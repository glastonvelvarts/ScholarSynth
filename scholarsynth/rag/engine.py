"""LlamaIndex query engine: Milvus retrieval + vLLM synthesis."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.schema import NodeWithScore
from llama_index.llms.openai_like import OpenAILike

from scholarsynth.rag.milvus_retriever import MilvusRetriever
from scholarsynth.rag.prompts import RAG_SYSTEM_PROMPT, TEXT_QA_TEMPLATE
from scholarsynth.retrieval.retriever import RetrievalConfig, RetrievalResponse

logger = logging.getLogger(__name__)

VLLM_BASE_URL = os.environ.get("SCHOLARSYNTH_VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL = os.environ.get("SCHOLARSYNTH_VLLM_SERVED_MODEL", "qwen-coder-7b")
VLLM_API_KEY = os.environ.get("SCHOLARSYNTH_VLLM_API_KEY", "not-needed")
VLLM_TIMEOUT = float(os.environ.get("SCHOLARSYNTH_VLLM_TIMEOUT", "120"))


@dataclass
class RAGResponse:
    """End-to-end RAG output."""

    query: str
    answer: str
    sources: List[NodeWithScore]
    confident: bool
    retrieval_message: Optional[str] = None
    retrieval_score: float = 0.0
    config: RetrievalConfig = field(default_factory=RetrievalConfig)


def build_llm(
    *,
    api_base: str = VLLM_BASE_URL,
    model: str = VLLM_MODEL,
    api_key: str = VLLM_API_KEY,
    timeout: float = VLLM_TIMEOUT,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> OpenAILike:
    """OpenAI-compatible client for Modal-hosted vLLM."""
    return OpenAILike(
        model=model,
        api_base=api_base,
        api_key=api_key,
        is_chat_model=True,
        is_function_calling_model=False,
        timeout=timeout,
        temperature=temperature,
        max_tokens=max_tokens,
        additional_kwargs={
            "top_p": 0.9,
        },
    )


def build_query_engine(
    *,
    retrieval_config: Optional[RetrievalConfig] = None,
    llm: Optional[OpenAILike] = None,
) -> RetrieverQueryEngine:
    """Wire Milvus retriever to vLLM via LlamaIndex."""
    retriever = MilvusRetriever(config=retrieval_config)
    synthesizer = get_response_synthesizer(
        llm=llm or build_llm(),
        text_qa_template=TEXT_QA_TEMPLATE,
        response_mode="compact",
    )
    return RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        node_postprocessors=[],
    )


def _format_context_header(node: NodeWithScore) -> str:
    meta = node.node.metadata
    doc = meta.get("document_name", "unknown")
    page = meta.get("page_label") or meta.get("page", "?")
    section = meta.get("section") or ""
    chunk_type = meta.get("chunk_type", "prose")
    header = f"[{doc}, p.{page}] ({chunk_type})"
    if section:
        header += f" — {section}"
    return header


def ask(
    query: str,
    *,
    retrieval_config: Optional[RetrievalConfig] = None,
    llm: Optional[OpenAILike] = None,
    skip_generation_on_low_confidence: bool = True,
) -> RAGResponse:
    """
    Full RAG: retrieve from Milvus, synthesize answer via vLLM.

    When retrieval is below the confidence threshold, returns the retrieval
    message without calling the LLM (unless skip_generation_on_low_confidence=False).
    """
    cfg = retrieval_config or RetrievalConfig(exclude_chunk_types=("metadata",))
    retriever = MilvusRetriever(config=cfg)
    retrieval_response, nodes = retriever.retrieve_with_response(query)

    if skip_generation_on_low_confidence and not retrieval_response.confident:
        return RAGResponse(
            query=query,
            answer=retrieval_response.message or "No confident matches found.",
            sources=nodes,
            confident=False,
            retrieval_message=retrieval_response.message,
            retrieval_score=retrieval_response.top_score,
            config=cfg,
        )

    llm_client = llm or build_llm()
    context_blocks = [
        f"{_format_context_header(node)}\n{node.node.get_content()}"
        for node in nodes
    ]
    context_str = "\n\n".join(context_blocks)

    prompt = (
        f"{RAG_SYSTEM_PROMPT.strip()}\n\n"
        f"{TEXT_QA_TEMPLATE.format(context_str=context_str, query_str=query)}"
    )

    logger.info("Querying vLLM at %s model=%s", VLLM_BASE_URL, VLLM_MODEL)
    completion = llm_client.complete(prompt)
    answer = str(completion).strip()

    return RAGResponse(
        query=query,
        answer=answer,
        sources=nodes,
        confident=retrieval_response.confident,
        retrieval_message=retrieval_response.message,
        retrieval_score=retrieval_response.top_score,
        config=cfg,
    )


def _print_response(response: RAGResponse) -> None:
    if response.retrieval_message and not response.confident:
        print(f"\n[low-confidence] {response.retrieval_message}\n")

    print(response.answer)
    print("\n--- Sources ---")
    for idx, node in enumerate(response.sources, start=1):
        meta: dict[str, Any] = node.node.metadata
        print(
            f"{idx}. {meta.get('document_name')} p.{meta.get('page_label')} "
            f"({meta.get('chunk_type')}, score={node.score:.3f})"
        )


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    question = " ".join(sys.argv[1:]).strip() or input("\nQuestion: ").strip()
    if not question:
        raise SystemExit("Empty query.")

    config = RetrievalConfig(
        top_k=5,
        candidate_k=20,
        rerank=os.environ.get("SCHOLARSYNTH_RERANK", "1") == "1",
        exclude_chunk_types=("metadata",),
        score_threshold=float(os.environ.get("SCHOLARSYNTH_SCORE_THRESHOLD", "0.45")),
    )

    result = ask(question, retrieval_config=config)
    _print_response(result)
