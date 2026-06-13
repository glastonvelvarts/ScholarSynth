"""Tests for retriever pure-logic helpers (no Milvus or model loading)."""

import numpy as np

from scholarsynth.retrieval import retriever as r


def test_parse_citations_handles_json_string():
    assert r._parse_citations('["[1]", "[2]"]') == ["[1]", "[2]"]
    assert r._parse_citations(None) == []
    assert r._parse_citations([]) == []
    assert r._parse_citations(["[1]"]) == ["[1]"]


def test_build_filter_expr_combines_exclusions_and_doc_filter():
    expr = r._build_filter_expr(("reference", "metadata"), "Paper.pdf")
    assert 'chunk_type not in ["reference", "metadata"]' in expr
    assert 'document_name == "Paper.pdf"' in expr
    assert " and " in expr


def test_build_filter_expr_returns_none_when_empty():
    assert r._build_filter_expr((), None) is None


def test_hits_to_chunks_maps_fields():
    hits = [
        {
            "distance": 0.72,
            "entity": {
                "chunk_id": "doc_1",
                "document_name": "Paper.pdf",
                "page": 3,
                "page_end": 4,
                "section": "RESULTS",
                "chunk_type": "table",
                "text": "TABLE I\n\n| Model | F1 |",
                "citations": '["[1]"]',
                "table_markdown": "| Model | F1 |",
            },
        }
    ]
    chunks = r._hits_to_chunks(hits)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.chunk_id == "doc_1"
    assert chunk.page == 3
    assert chunk.page_end == 4
    assert chunk.chunk_type == "table"
    assert chunk.citations == ["[1]"]
    assert chunk.table_markdown == "| Model | F1 |"
    assert chunk.score == 0.72


def test_retrieve_low_confidence_message(monkeypatch):
    def fake_embed(query, prefix=""):
        return np.array([1.0, 0.0])

    def fake_search(query_embedding, limit, filter_expr):
        return [
            {
                "distance": 0.30,
                "entity": {
                    "chunk_id": "weak_match",
                    "document_name": "Paper.pdf",
                    "page": 1,
                    "page_end": 1,
                    "section": None,
                    "chunk_type": "prose",
                    "text": "Unrelated content about something else.",
                    "citations": "[]",
                    "table_markdown": "",
                },
            }
        ]

    monkeypatch.setattr(r, "embed_query", fake_embed)
    monkeypatch.setattr(r, "_search", fake_search)

    response = r.retrieve(
        "what is the f1 score",
        config=r.RetrievalConfig(rerank=False, score_threshold=0.45),
    )

    assert response.confident is False
    assert response.message is not None
    assert response.top_score < 0.45
    assert len(response.results) == 1
