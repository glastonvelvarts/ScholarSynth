"""Block-based page text extraction with two-column support."""

from __future__ import annotations

import pymupdf as fitz


def extract_page_text(page: fitz.Page) -> str:
    """
    Extract page text preserving reading order.

    Academic PDFs often use two columns. PyMuPDF's sort=True can interleave
    columns incorrectly, so we read blocks left-to-right when a two-column
    layout is detected; otherwise we fall back to natural block order.
    """
    blocks = page.get_text("blocks")
    text_blocks = [
        block for block in blocks if block[6] == 0 and block[4].strip()
    ]

    if not text_blocks:
        return ""

    if _is_two_column_layout(text_blocks, page.rect.width):
        return _extract_two_column_text(text_blocks, page.rect.width)

    text_blocks.sort(key=lambda block: (block[1], block[0]))
    return "\n\n".join(block[4].strip() for block in text_blocks)


def _is_two_column_layout(blocks: list[tuple], page_width: float) -> bool:
    """Heuristic: meaningful text on both halves of the page."""
    midpoint = page_width / 2
    margin = page_width * 0.08

    left = 0
    right = 0

    for block in blocks:
        x0, _, x1, _, text, *_rest = block
        if len(text.strip()) < 20:
            continue
        center = (x0 + x1) / 2
        if center < midpoint - margin:
            left += 1
        elif center > midpoint + margin:
            right += 1

    return left >= 2 and right >= 2


def _extract_two_column_text(blocks: list[tuple], page_width: float) -> str:
    """Read down the left column, then down the right column."""
    midpoint = page_width / 2
    left_blocks: list[tuple] = []
    right_blocks: list[tuple] = []

    for block in blocks:
        x0, y0, x1, _y1, text, *_rest = block
        center = (x0 + x1) / 2
        cleaned = text.strip()
        if center <= midpoint:
            left_blocks.append((y0, cleaned))
        else:
            right_blocks.append((y0, cleaned))

    left_blocks.sort(key=lambda item: item[0])
    right_blocks.sort(key=lambda item: item[0])

    ordered = [text for _, text in left_blocks] + [text for _, text in right_blocks]
    return "\n\n".join(ordered)
