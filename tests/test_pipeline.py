"""Tests for the RAG pipeline serialization."""

from scholarsynth.rag.pipeline import RAGResponse, SourceChunk, rag_response_to_dict
from scholarsynth.retrieval.retriever import RetrievalConfig


def test_rag_response_to_dict_maps_citations():
    response = RAGResponse(
        query="what is the f1 score?",
        answer="The model achieved 92.1% F1.",
        sources=[
            SourceChunk(
                chunk_id="doc_p3_0",
                document_name="Paper.pdf",
                page=3,
                page_end=4,
                section="RESULTS",
                chunk_type="prose",
                text="The model achieved 92.1% F1 on the benchmark.",
                score=0.81,
            )
        ],
        confident=True,
        retrieval_score=0.81,
        config=RetrievalConfig(),
    )

    payload = rag_response_to_dict(response)
    assert payload["answer"] == "The model achieved 92.1% F1."
    assert payload["confident"] is True
    assert len(payload["citations"]) == 1
    cite = payload["citations"][0]
    assert cite["paper_title"] == "Paper"
    assert cite["page_number"] == 3
    assert cite["page_end"] == 4
    assert cite["relevance_score"] == 0.81
