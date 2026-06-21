"""LlamaIndex retriever backed by the existing Milvus + BGE pipeline."""

from __future__ import annotations

from typing import Optional

from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

from scholarsynth.retrieval.retriever import (
    RetrievedChunk,
    RetrievalConfig,
    RetrievalResponse,
    retrieve,
)


def _format_page(chunk: RetrievedChunk) -> str:
    if chunk.page == chunk.page_end:
        return str(chunk.page)
    return f"{chunk.page}-{chunk.page_end}"


def chunk_to_node(chunk: RetrievedChunk) -> NodeWithScore:
    """Map a Milvus hit to a LlamaIndex node with citation metadata."""
    if chunk.chunk_type == "table" and chunk.table_markdown:
        text = chunk.table_markdown
    else:
        text = chunk.text

    metadata = {
        "chunk_id": chunk.chunk_id,
        "document_name": chunk.document_name,
        "page": chunk.page,
        "page_end": chunk.page_end,
        "page_label": _format_page(chunk),
        "section": chunk.section or "",
        "chunk_type": chunk.chunk_type,
        "citations": chunk.citations,
        "dense_score": chunk.score,
        "rerank_score": chunk.rerank_score,
    }
    node = TextNode(text=text, metadata=metadata, id_=chunk.chunk_id)
    score = chunk.rerank_score if chunk.rerank_score is not None else chunk.score
    return NodeWithScore(node=node, score=score)


def retrieval_response_to_nodes(response: RetrievalResponse) -> list[NodeWithScore]:
    return [chunk_to_node(chunk) for chunk in response.results]


class MilvusRetriever(BaseRetriever):
    """Expose ScholarSynth Milvus retrieval as a LlamaIndex retriever."""

    def __init__(self, config: Optional[RetrievalConfig] = None, **kwargs):
        self._config = config or RetrievalConfig(exclude_chunk_types=("metadata",))
        super().__init__(**kwargs)

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        response = retrieve(query_bundle.query_str, config=self._config)
        return retrieval_response_to_nodes(response)

    @property
    def config(self) -> RetrievalConfig:
        return self._config

    def retrieve_with_response(self, query: str) -> tuple[RetrievalResponse, list[NodeWithScore]]:
        response = retrieve(query, config=self._config)
        return response, retrieval_response_to_nodes(response)
