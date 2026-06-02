"""Tests for text normalization and header/footer removal."""

from papercontext.text_cleaner import (
    clean_page_texts,
    find_repeated_lines,
    fix_hyphenated_line_breaks,
    normalize_whitespace,
    remove_lines,
)


def test_fix_hyphenated_line_breaks():
    raw = "This is a custom-\ner service platform."
    assert fix_hyphenated_line_breaks(raw) == "This is a customer service platform."


def test_fix_hyphenated_line_breaks_keeps_compound_words():
    raw = "a dynamic and customer-\ncentric ecosystem."
    assert fix_hyphenated_line_breaks(raw) == "a dynamic and customer-centric ecosystem."


def test_normalize_whitespace_collapses_wrapped_lines():
    raw = "Abstract\nIn the digital age,\nthe dynamics evolve."
    result = normalize_whitespace(raw)
    assert result == "Abstract In the digital age, the dynamics evolve."


def test_normalize_whitespace_preserves_paragraph_breaks():
    raw = "Section I\n\nSection II"
    result = normalize_whitespace(raw)
    assert result == "Section I\n\nSection II"


def test_find_repeated_lines_detects_conference_header():
    header = "Submitted to the 3rd International Conference on Women in Science"
    pages = [
        f"{header}\nPage one content.",
        f"{header}\nPage two content.",
        f"{header}\nPage three content.",
    ]
    repeated = find_repeated_lines(pages, min_page_ratio=0.6)
    assert header in repeated


def test_remove_lines_strips_header():
    header = "Repeated conference header line here"
    text = f"{header}\nActual body text."
    result = remove_lines(text, frozenset({header}))
    assert result == "Actual body text."


def test_clean_page_texts_removes_repeated_header_and_normalizes():
    header = "Submitted to the 3rd International Conference on Women in Science"
    pages = [
        f"{header}\nAbstract\nIn the digital age,",
        f"{header}\nIII. METHODOLOGY\nThis section covers",
    ]
    cleaned = clean_page_texts(pages)
    assert header not in cleaned[0]
    assert header not in cleaned[1]
    assert "Abstract In the digital age," in cleaned[0]
    assert "III. METHODOLOGY This section covers" in cleaned[1]
