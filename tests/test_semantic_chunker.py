"""Tests for semantic chunking helpers (no model loading)."""

import numpy as np

from scholarsynth.semantic_chunker import (
    SentenceSpan,
    is_section_heading,
    semantic_chunk_sentences,
    split_sentences,
)


def test_split_sentences_respects_paragraphs():
    text = "First sentence here. Second sentence here.\n\nAnother paragraph starts."
    spans = split_sentences(text, page=1, section=None)

    assert len(spans) == 3
    assert spans[0].paragraph_break_after is False
    assert spans[1].paragraph_break_after is True
    assert spans[2].paragraph_break_after is False


def test_split_sentences_detects_section_heading():
    text = "I. INTRODUCTION\n\nThis paper presents a system."
    spans = split_sentences(text, page=2, section=None)

    assert spans[0].text == "I. INTRODUCTION"
    assert spans[0].section == "I. INTRODUCTION"
    assert spans[1].section == "I. INTRODUCTION"


def test_is_section_heading_accepts_known_patterns():
    assert is_section_heading("I. INTRODUCTION")
    assert is_section_heading("IV. RESULTS")
    assert is_section_heading("V. CONCLUSION")
    assert is_section_heading("REFERENCES")
    assert is_section_heading("ACKNOWLEDGMENT")
    assert is_section_heading("Abstract")
    assert is_section_heading("Methodology")
    assert is_section_heading("A. EVALUATION")
    assert is_section_heading("3.1 METHODS")


def test_is_section_heading_rejects_faq_items():
    # These previously slipped through and broke section metadata.
    assert not is_section_heading("3. What is IEEE BVM?")
    assert not is_section_heading("4. What is TRS")
    assert not is_section_heading("5. Name the annual")
    assert not is_section_heading("1. What is BVM?")
    assert not is_section_heading("This is a regular sentence.")
    assert not is_section_heading("Tell me something about BVM")


def test_is_section_heading_rejects_long_or_multiline():
    long_text = "This is a long line that runs on and on and on and clearly is not a heading"
    assert not is_section_heading(long_text)
    assert not is_section_heading("HEADING\nWith a second line of content")


def test_semantic_chunk_sentences_splits_on_paragraphs():
    sentences = [
        SentenceSpan("Topic A sentence one.", 1, "Intro", paragraph_break_after=False),
        SentenceSpan("Topic A sentence two.", 1, "Intro", paragraph_break_after=True),
        SentenceSpan("Unrelated topic sentence.", 2, "Intro", paragraph_break_after=False),
    ]

    def embed_fn(texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            if text.startswith("Unrelated"):
                vectors.append(np.array([0.0, 1.0]))
            else:
                vectors.append(np.array([1.0, 0.0]))
        return np.asarray(vectors)

    chunks = semantic_chunk_sentences(
        sentences,
        embed_fn,
        max_chunk_chars=500,
        min_chunk_chars=10,
        breakpoint_percentile=50,
    )

    assert len(chunks) == 2
    assert "Topic A" in chunks[0].text
    assert chunks[0].page == 1
    assert chunks[1].text.startswith("Unrelated")
