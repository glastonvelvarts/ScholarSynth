"""Text normalization and repeated header/footer removal."""

from __future__ import annotations

import re
from collections import Counter

# Lines that repeat on most pages (conference headers, page numbers, etc.)
_DEFAULT_MIN_PAGE_RATIO = 0.6
_DEFAULT_MIN_LINE_LENGTH = 10
_PAGE_NUMBER_PATTERN = re.compile(r"^\d{1,4}$")
_HYPHENATED_BREAK_PATTERN = re.compile(r"(\w+)-\n(\w+)")


def find_repeated_lines(
    page_texts: list[str],
    *,
    min_page_ratio: float = _DEFAULT_MIN_PAGE_RATIO,
    min_line_length: int = _DEFAULT_MIN_LINE_LENGTH,
) -> frozenset[str]:
    """Return lines that appear on most pages and are likely headers or footers."""
    if len(page_texts) < 2:
        return frozenset()

    threshold = max(2, int(len(page_texts) * min_page_ratio))
    counts: Counter[str] = Counter()

    for text in page_texts:
        unique_lines = {
            line.strip()
            for line in text.splitlines()
            if _is_candidate_repeated_line(line.strip(), min_line_length)
        }
        for line in unique_lines:
            counts[line] += 1

    return frozenset(line for line, count in counts.items() if count >= threshold)


def _is_candidate_repeated_line(line: str, min_line_length: int) -> bool:
    if len(line) < min_line_length and not _PAGE_NUMBER_PATTERN.match(line):
        return False
    return bool(line)


def remove_lines(text: str, lines_to_remove: frozenset[str]) -> str:
    """Drop exact line matches from text."""
    if not lines_to_remove:
        return text

    kept = [line for line in text.splitlines() if line.strip() not in lines_to_remove]
    return "\n".join(kept)


def fix_hyphenated_line_breaks(text: str) -> str:
    """Join words split across lines with a hyphen (e.g. 'custom-\\ner' -> 'customer')."""

    def _replace(match: re.Match[str]) -> str:
        left, right = match.group(1), match.group(2)
        # Short suffixes are usually syllable breaks; longer segments are compound words.
        if len(right) <= 4:
            return left + right
        return f"{left}-{right}"

    return _HYPHENATED_BREAK_PATTERN.sub(_replace, text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize PDF extraction artifacts:
    - fix hyphenated line breaks
    - collapse inline whitespace
    - preserve paragraph breaks (blank lines)
    """
    text = fix_hyphenated_line_breaks(text)

    paragraphs: list[str] = []
    buffer: list[str] = []

    for line in text.splitlines():
        stripped = " ".join(line.split())
        if not stripped:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(stripped)

    if buffer:
        paragraphs.append(" ".join(buffer))

    return "\n\n".join(paragraphs)


def clean_page_texts(raw_page_texts: list[str]) -> list[str]:
    """Remove repeated headers/footers and normalize whitespace for all pages."""
    repeated = find_repeated_lines(raw_page_texts)
    return [normalize_whitespace(remove_lines(text, repeated)) for text in raw_page_texts]
