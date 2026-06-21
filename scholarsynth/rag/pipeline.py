"""End-to-end RAG pipeline: Milvus retrieval then vLLM generation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

from dotenv import load_dotenv
from llama_index.core.schema import NodeWithScore
from llama_index.llms.openai_like import OpenAILike

from scholarsynth.rag.generator import build_llm, generate_answer
from scholarsynth.rag.milvus_retriever import MilvusRetriever, retrieval_response_to_nodes
from scholarsynth.rag.query_router import is_general_query
from scholarsynth.retrieval.retriever import RetrievalConfig, retrieve_broad

load_dotenv()


@dataclass
class SourceChunk:
    chunk_id: str
    document_name: str
    page: int
    page_end: int
    section: Optional[str]
    chunk_type: str
    text: str
    score: float


@dataclass
class RAGResponse:
    query: str
    answer: str
    sources: List[SourceChunk]
    confident: bool
    retrieval_message: Optional[str] = None
    retrieval_score: float = 0.0
    config: RetrievalConfig = field(default_factory=RetrievalConfig)


def _node_to_source(node: NodeWithScore) -> SourceChunk:
    meta = node.node.metadata
    page = int(meta.get("page", 0) or 0)
    page_end = int(meta.get("page_end", page) or page)
    return SourceChunk(
        chunk_id=str(meta.get("chunk_id", node.node.id_ or "")),
        document_name=str(meta.get("document_name", "")),
        page=page,
        page_end=page_end,
        section=meta.get("section") or None,
        chunk_type=str(meta.get("chunk_type", "prose")),
        text=node.node.get_content(),
        score=float(node.score or 0.0),
    )


def _nodes_to_sources(nodes: list[NodeWithScore]) -> list[SourceChunk]:
    return [_node_to_source(node) for node in nodes]


def _merge_nodes(
    primary: list[NodeWithScore],
    extra: list[NodeWithScore],
    *,
    max_nodes: int = 12,
) -> list[NodeWithScore]:
    seen: set[str] = set()
    merged: list[NodeWithScore] = []
    for node in primary + extra:
        cid = node.node.id_ or ""
        if cid in seen:
            continue
        seen.add(cid)
        merged.append(node)
        if len(merged) >= max_nodes:
            break
    return merged


def default_retrieval_config(
    *,
    document_filter: Optional[str] = None,
    top_k: int = 5,
    general: bool = False,
) -> RetrievalConfig:
    if general:
        return RetrievalConfig(
            top_k=max(top_k, 10),
            candidate_k=30,
            rerank=os.environ.get("SCHOLARSYNTH_RERANK", "1") == "1",
            exclude_chunk_types=("metadata",),
            score_threshold=float(os.environ.get("SCHOLARSYNTH_SCORE_THRESHOLD", "0.45")),
            document_filter=document_filter,
        )
    return RetrievalConfig(
        top_k=top_k,
        candidate_k=20,
        rerank=os.environ.get("SCHOLARSYNTH_RERANK", "1") == "1",
        exclude_chunk_types=("metadata",),
        score_threshold=float(os.environ.get("SCHOLARSYNTH_SCORE_THRESHOLD", "0.45")),
        document_filter=document_filter,
    )


def run_rag(
    query: str,
    *,
    retrieval_config: Optional[RetrievalConfig] = None,
    llm: Optional[OpenAILike] = None,
) -> RAGResponse:
    """
    ScholarSynth RAG pipeline:
        1. Dense retrieval (+ vectorless broad sampling for general queries)
        2. Always generate via vLLM when any context is available
        3. Confidence score is informational only — never blocks the LLM
    """
    general = is_general_query(query)
    cfg = retrieval_config or default_retrieval_config(general=general)

    retriever = MilvusRetriever(config=cfg)
    retrieval_response, nodes = retriever.retrieve_with_response(query)

    if general:
        broad = retrieve_broad(cfg, chunks_per_doc=3, max_total=cfg.top_k)
        nodes = _merge_nodes(nodes, retrieval_response_to_nodes(broad), max_nodes=cfg.top_k)

    sources = _nodes_to_sources(nodes)

    if not nodes:
        return RAGResponse(
            query=query,
            answer=(
                "No indexed documents found. Upload papers to your workspace first, "
                "then ask your question again."
            ),
            sources=[],
            confident=False,
            retrieval_message=retrieval_response.message,
            retrieval_score=retrieval_response.top_score,
            config=cfg,
        )

    answer = generate_answer(
        query,
        nodes,
        llm=llm or build_llm(),
        synthesis=general,
    )
    return RAGResponse(
        query=query,
        answer=answer,
        sources=sources,
        confident=retrieval_response.confident or general,
        retrieval_message=retrieval_response.message if not retrieval_response.confident and not general else None,
        retrieval_score=retrieval_response.top_score,
        config=cfg,
    )


def rag_response_to_dict(response: RAGResponse) -> dict[str, Any]:
    """Serialize for API / frontend consumption."""
    return {
        "query": response.query,
        "answer": response.answer,
        "confident": response.confident,
        "retrieval_score": response.retrieval_score,
        "retrieval_message": response.retrieval_message,
        "citations": [
            {
                "id": source.chunk_id,
                "paper_id": source.document_name,
                "paper_title": source.document_name.removesuffix(".pdf"),
                "text": source.text[:500],
                "page_number": source.page,
                "page_end": source.page_end,
                "section": source.section,
                "chunk_type": source.chunk_type,
                "relevance_score": source.score,
            }
            for source in response.sources
        ],
    }


def _print_response(response: RAGResponse) -> None:
    if response.retrieval_message and not response.confident:
        print(f"\n[low-confidence] {response.retrieval_message}\n")

    print(response.answer)
    print("\n--- Sources ---")
    for idx, source in enumerate(response.sources, start=1):
        page = (
            str(source.page)
            if source.page == source.page_end
            else f"{source.page}-{source.page_end}"
        )
        print(
            f"{idx}. {source.document_name} p.{page} "
            f"({source.chunk_type}, score={source.score:.3f})"
        )


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    question = " ".join(sys.argv[1:]).strip() or input("\nQuestion: ").strip()
    if not question:
        raise SystemExit("Empty query.")

    result = run_rag(question)
    _print_response(result)
