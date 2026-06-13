"""Tests for citation extraction and stripping."""

from scholarsynth.citations import extract_citations, strip_citations


def test_extract_bracket_citations():
    text = "The model [1] outperforms prior work [2, 3] and [4-6]."
    assert extract_citations(text) == ["[1]", "[2, 3]", "[4-6]"]


def test_extract_author_year_citations():
    text = "Prior studies (Smith, 2020) and (Jones et al., 2019) show gains."
    citations = extract_citations(text)
    assert "(Smith, 2020)" in citations
    assert "(Jones et al., 2019)" in citations


def test_strip_citations_preserves_prose():
    text = "Transformers [1] improve retrieval (Smith, 2020)."
    result = strip_citations(text)

    assert "[1]" not in result.cleaned
    assert "(Smith, 2020)" not in result.cleaned
    assert "Transformers improve retrieval." in result.cleaned
    assert result.original == text
    assert "[1]" in result.citations


def test_strip_citations_deduplicates():
    text = "As shown [1], the approach [1] works."
    result = strip_citations(text)
    assert result.citations == ["[1]"]
