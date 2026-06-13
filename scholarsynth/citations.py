"""Extract and strip inline citations from academic paper text."""

from __future__ import annotations

import re
from typing import NamedTuple

# Numeric bracket refs: [1], [1, 2], [1-3], [1, 2-4]
_BRACKET_NUMERIC = re.compile(
    r"\[(?:\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)\]"
)

# Author-year parenthetical refs: (Smith, 2020), (Jones et al., 2019)
_AUTHOR_YEAR = re.compile(
    r"\("
    r"[A-Z][A-Za-z\-]+"
    r"(?:\s+et\s+al\.)?"
    r"(?:\s+(?:&|and)\s+[A-Z][A-Za-z\-]+)?"
    r"\s*,\s*\d{4}"
    r"\)"
)

_CITATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    _BRACKET_NUMERIC,
    _AUTHOR_YEAR,
)


class CitationResult(NamedTuple):
    """Original text, cleaned text, and citations found (deduplicated, order preserved)."""

    original: str
    cleaned: str
    citations: list[str]


def extract_citations(text: str) -> list[str]:
    """Return citation strings found in text, in document order, deduplicated."""
    seen: set[str] = set()
    citations: list[str] = []

    for pattern in _CITATION_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(0)
            if token not in seen:
                seen.add(token)
                citations.append(token)

    return citations


def strip_citations(text: str) -> CitationResult:
    """
    Remove inline citations from text for embedding while preserving originals.

    The cleaned text keeps readable prose; citation tokens are replaced with
    a single space and whitespace is normalized.
    """
    citations = extract_citations(text)
    cleaned = text

    for pattern in _CITATION_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)

    cleaned = re.sub(r"  +", " ", cleaned)
    cleaned = re.sub(r" ([,.;:!?])", r"\1", cleaned)

    return CitationResult(
        original=text,
        cleaned=cleaned.strip(),
        citations=citations,
    )
