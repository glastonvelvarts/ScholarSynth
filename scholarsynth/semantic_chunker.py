"""Semantic text chunking using sentence embeddings and similarity breakpoints."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MAX_CHUNK_CHARS = 1500
DEFAULT_MIN_CHUNK_CHARS = 200
DEFAULT_BREAKPOINT_PERCENTILE = 90.0
DEFAULT_MODEL_NAME = "BAAI/bge-m3"

_MAX_HEADING_LENGTH = 80

_NAMED_SECTION = re.compile(
    r"^("
    r"abstract|introduction|background|related\s+work|"
    r"motivation|preliminaries|problem\s+statement|"
    r"methodology|methods?|approach|materials?|"
    r"experiments?|experimental\s+setup|evaluation|setup|"
    r"results?|findings|discussion|analysis|ablation|"
    r"limitations?|conclusion|conclusions|future\s+work|"
    r"references|bibliography|acknowledgments?|appendix"
    r")\s*$",
    re.IGNORECASE,
)

# "I. INTRODUCTION", "IV. RESULTS", "1. INTRODUCTION",
# "A. EVALUATION", "3.1 METHODS", "3.1. METHODS"
_PREFIXED_CAPS_HEADING = re.compile(
    r"^(?:"
    r"[IVX]{1,5}\."          # roman numeral + dot
    r"|[A-Z]\."              # single letter + dot
    r"|\d{1,2}\.\d{1,2}\.?"  # nested number, optional trailing dot
    r"|\d{1,2}\."            # single number + dot
    r")\s+[A-Z][A-Z0-9\s\-&'/]+\s*$"
)

# Bare ALL CAPS heading: "RESULTS", "BACKGROUND AND RELATED WORK"
_BARE_CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9\s\-&'/]{2,}\s*$")

_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?…])\s+(?=[A-Z\"'(\[])"
    r"|(?<=[.!?…])\s*\n\s*(?=[A-Z\"'(\[])"
)


def is_section_heading(paragraph: str) -> bool:
    """
    Return True only for clear section headings.

    A heading must be a single short line with no question mark, and either:
    - a well-known named section (Abstract, Introduction, References, ...), or
    - a prefixed ALL CAPS heading (I. INTRODUCTION, A. EVALUATION, 3. METHODS), or
    - a bare ALL CAPS heading.

    This rejects FAQ items like "5. Name the annual" or "3. What is IEEE?".
    """
    if "\n" in paragraph:
        return False
    text = paragraph.strip()
    if not text or "?" in text:
        return False
    if len(text) > _MAX_HEADING_LENGTH or len(text) < 3:
        return False

    if _NAMED_SECTION.match(text):
        return True
    if _PREFIXED_CAPS_HEADING.match(text):
        return True
    if _BARE_CAPS_HEADING.match(text):
        return True
    return False


@dataclass(frozen=True)
class SentenceSpan:
    text: str
    page: int
    section: Optional[str]
    paragraph_break_after: bool = False


@dataclass(frozen=True)
class TextChunk:
    text: str
    page: int
    page_end: int
    section: Optional[str]
    sentence_count: int


def split_sentences(text: str, page: int, section: Optional[str]) -> list[SentenceSpan]:
    """Split page text into sentences while preserving paragraph boundaries."""
    paragraphs = re.split(r"\n\n+", text.strip())
    spans: list[SentenceSpan] = []

    for para_idx, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if is_section_heading(paragraph):
            section = paragraph
            spans.append(
                SentenceSpan(
                    text=paragraph,
                    page=page,
                    section=section,
                    paragraph_break_after=para_idx < len(paragraphs) - 1,
                )
            )
            continue

        parts = _SENTENCE_BOUNDARY.split(paragraph)
        parts = [part.strip() for part in parts if part.strip()]

        for sent_idx, sentence in enumerate(parts):
            is_last_in_para = sent_idx == len(parts) - 1
            spans.append(
                SentenceSpan(
                    text=sentence,
                    page=page,
                    section=section,
                    paragraph_break_after=is_last_in_para and para_idx < len(paragraphs) - 1,
                )
            )

    return spans


def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(1.0 - np.dot(a, b))


def _find_breakpoints(distances: list[float], percentile: float) -> set[int]:
    """Return indices AFTER which a new chunk should start."""
    if len(distances) <= 1:
        return set()

    threshold = float(np.percentile(distances, percentile))
    return {idx + 1 for idx, distance in enumerate(distances) if distance >= threshold}


def _group_sentences(
    sentences: list[SentenceSpan],
    breakpoints: set[int],
    max_chunk_chars: int,
    min_chunk_chars: int,
) -> list[tuple[int, int]]:
    """Return (start, end) sentence index ranges respecting size limits."""
    if not sentences:
        return []

    hard_breaks: set[int] = {
        idx + 1 for idx, sent in enumerate(sentences[:-1]) if sent.paragraph_break_after
    }
    all_breaks = sorted(breakpoints | hard_breaks)

    ranges: list[tuple[int, int]] = []
    start = 0

    for break_at in all_breaks + [len(sentences)]:
        if break_at <= start:
            continue

        chunk_text = " ".join(s.text for s in sentences[start:break_at])
        if len(chunk_text) > max_chunk_chars and break_at - start > 1:
            sub_ranges = _split_oversized_range(
                sentences,
                start,
                break_at,
                max_chunk_chars,
            )
            ranges.extend(sub_ranges)
            start = break_at
            continue

        ranges.append((start, break_at))
        start = break_at

    return _merge_small_ranges(sentences, ranges, min_chunk_chars, max_chunk_chars)


def _split_oversized_range(
    sentences: list[SentenceSpan],
    start: int,
    end: int,
    max_chunk_chars: int,
) -> list[tuple[int, int]]:
    """Split a sentence range that exceeds max_chunk_chars."""
    ranges: list[tuple[int, int]] = []
    cursor = start

    while cursor < end:
        best_end = cursor + 1
        accumulated = sentences[cursor].text

        while best_end < end:
            candidate = f"{accumulated} {sentences[best_end].text}"
            if len(candidate) > max_chunk_chars:
                break
            accumulated = candidate
            best_end += 1

        if best_end == cursor + 1 and best_end < end:
            best_end += 1

        ranges.append((cursor, best_end))
        cursor = best_end

    return ranges


def _merge_small_ranges(
    sentences: list[SentenceSpan],
    ranges: list[tuple[int, int]],
    min_chunk_chars: int,
    max_chunk_chars: int,
) -> list[tuple[int, int]]:
    if not ranges:
        return []

    merged: list[tuple[int, int]] = []
    idx = 0

    while idx < len(ranges):
        start, end = ranges[idx]
        text = " ".join(s.text for s in sentences[start:end])

        while len(text) < min_chunk_chars and idx + 1 < len(ranges):
            next_start, next_end = ranges[idx + 1]
            combined = f"{text} {' '.join(s.text for s in sentences[next_start:next_end])}"
            if len(combined) > max_chunk_chars:
                break
            end = next_end
            text = combined
            idx += 1

        merged.append((start, end))
        idx += 1

    return merged


def semantic_chunk_sentences(
    sentences: list[SentenceSpan],
    embed_fn: Callable[[list[str]], np.ndarray],
    *,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS,
    breakpoint_percentile: float = DEFAULT_BREAKPOINT_PERCENTILE,
) -> list[TextChunk]:
    """
    Group sentences into semantically coherent chunks.

    Uses embedding similarity between consecutive sentences to find natural
    breakpoints, with hard splits at paragraph boundaries and size caps.
    """
    if not sentences:
        return []

    texts = [sentence.text for sentence in sentences]
    embeddings = embed_fn(texts)

    distances: list[float] = []
    for idx in range(len(sentences) - 1):
        if sentences[idx].paragraph_break_after:
            distances.append(1.0)
        else:
            distances.append(_cosine_distance(embeddings[idx], embeddings[idx + 1]))

    breakpoints = _find_breakpoints(distances, breakpoint_percentile)
    ranges = _group_sentences(
        sentences,
        breakpoints,
        max_chunk_chars,
        min_chunk_chars,
    )

    chunks: list[TextChunk] = []
    for start, end in ranges:
        group = sentences[start:end]
        text = " ".join(s.text for s in group)
        chunks.append(
            TextChunk(
                text=text,
                page=group[0].page,
                page_end=group[-1].page,
                section=group[0].section,
                sentence_count=len(group),
            )
        )

    logger.info(
        "Semantic chunking produced %d chunks from %d sentences",
        len(chunks),
        len(sentences),
    )

    return chunks
