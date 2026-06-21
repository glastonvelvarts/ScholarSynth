"""Tests for LlamaIndex Milvus retriever adapter."""

from scholarsynth.rag.milvus_retriever import chunk_to_node, retrieval_response_to_nodes
from scholarsynth.retrieval.retriever import (
    RetrievedChunk,
    RetrievalConfig,
    RetrievalResponse,
)


def _sample_chunk(**overrides) -> RetrievedChunk:
    defaults = {
        "chunk_id": "doc_p3_0",
        "document_name": "Paper.pdf",
        "page": 3,
        "page_end": 4,
        "section": "RESULTS",
        "chunk_type": "prose",
        "text": "The model achieved 92.1% F1 on the benchmark.",
        "citations": ["[1]"],
        "table_markdown": None,
        "score": 0.81,
        "rerank_score": 1.42,
    }
    defaults.update(overrides)
    return RetrievedChunk(**defaults)


def test_chunk_to_node_maps_metadata_and_prefers_rerank_score():
    node = chunk_to_node(_sample_chunk())
    assert node.score == 1.42
    assert node.node.metadata["document_name"] == "Paper.pdf"
    assert node.node.metadata["page_label"] == "3-4"
    assert node.node.metadata["citations"] == ["[1]"]
    assert "92.1%" in node.node.get_content()


def test_chunk_to_node_uses_table_markdown_for_tables():
    node = chunk_to_node(
        _sample_chunk(
            chunk_type="table",
            text="TABLE I",
            table_markdown="| Model | F1 |\n| --- | --- |\n| Ours | 92.1 |",
        )
    )
    assert "| Model | F1 |" in node.node.get_content()
    assert node.node.metadata["chunk_type"] == "table"


def test_retrieval_response_to_nodes_preserves_order():
    response = RetrievalResponse(
        query="f1 score",
        results=[_sample_chunk(chunk_id="a"), _sample_chunk(chunk_id="b")],
        top_score=0.81,
        confident=True,
        config=RetrievalConfig(),
    )
    nodes = retrieval_response_to_nodes(response)
    assert [n.node.id_ for n in nodes] == ["a", "b"]
