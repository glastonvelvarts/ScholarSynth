"""Tests for chunk classification (no model loading)."""

from scholarsynth.chunker import _classify_prose


def test_classify_reference_section():
    assert _classify_prose("Some bibliographic entry text.", "REFERENCES", False) == "reference"
    assert _classify_prose("Some text.", "Bibliography", False) == "reference"


def test_classify_bracket_reference_start():
    assert _classify_prose("[1] Smith et al. 2020. A paper.", None, False) == "reference"


def test_classify_metadata_first_chunk_with_email():
    text = "John Doe john@example.edu University of X"
    assert _classify_prose(text, None, True) == "metadata"


def test_classify_metadata_not_first_chunk():
    text = "John Doe john@example.edu University of X"
    assert _classify_prose(text, None, False) == "prose"


def test_classify_default_prose():
    text = "This paper proposes a new approach to retrieval."
    assert _classify_prose(text, "I. INTRODUCTION", False) == "prose"
