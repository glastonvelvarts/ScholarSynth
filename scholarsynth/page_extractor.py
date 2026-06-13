"""Block-based page text extraction with table awareness and two-column support."""

from __future__ import annotations

import logging
from typing import Any

import pymupdf as fitz

from scholarsynth.models import TableBlock

logger = logging.getLogger(__name__)

# A text block whose bbox is mostly inside a table bbox is part of that table
# and must be excluded from prose to avoid duplicate, jumbled content.
_TABLE_OVERLAP_THRESHOLD = 0.6


def extract_page_content(page: fitz.Page) -> dict[str, Any]:
    """
    Extract prose text and structured tables from a page.

    Returns a dict with:
        - "text": prose text with table regions removed
        - "tables": list of TableBlock dicts
    """
    tables = _extract_tables(page)
    table_bboxes = [tab["bbox"] for tab in tables]

    text = _extract_prose_text(page, exclude_bboxes=table_bboxes)
    return {"text": text, "tables": tables}


def extract_page_text(page: fitz.Page) -> str:
    """Backward-compatible prose-only extractor used by older callers and tests."""
    return _extract_prose_text(page, exclude_bboxes=[])


def _extract_tables(page: fitz.Page) -> list[TableBlock]:
    """Find tables on the page and convert each to markdown."""
    finder = getattr(page, "find_tables", None)
    if finder is None:
        return []

    try:
        found = finder()
    except Exception as exc:
        logger.debug("Table detection failed on page %s: %s", page.number, exc)
        return []

    tables: list[TableBlock] = []
    for table in getattr(found, "tables", []) or []:
        try:
            rows = table.extract() or []
        except Exception as exc:
            logger.debug("Table extract failed: %s", exc)
            continue

        normalized = _normalize_rows(rows)
        if not _is_meaningful_table(normalized):
            continue

        markdown = _rows_to_markdown(normalized)
        caption = _find_caption(page, tuple(table.bbox))

        tables.append(
            TableBlock(
                rows=normalized,
                markdown=markdown,
                caption=caption,
                bbox=tuple(float(v) for v in table.bbox),
            )
        )

    return tables


def _normalize_rows(rows: list[list[Any]]) -> list[list[str]]:
    cleaned: list[list[str]] = []
    for row in rows:
        cleaned_row = [
            (cell if cell is not None else "").strip().replace("\n", " ")
            for cell in row
        ]
        if any(cell for cell in cleaned_row):
            cleaned.append(cleaned_row)
    return cleaned


def _is_meaningful_table(rows: list[list[str]]) -> bool:
    """Reject 1-cell or empty tables that find_tables sometimes reports."""
    if len(rows) < 2:
        return False
    if max(len(row) for row in rows) < 2:
        return False
    total_chars = sum(len(cell) for row in rows for cell in row)
    return total_chars >= 20


def _rows_to_markdown(rows: list[list[str]]) -> str:
    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]

    header = padded[0]
    body = padded[1:] if len(padded) > 1 else []

    header_line = "| " + " | ".join(header) + " |"
    divider_line = "| " + " | ".join(["---"] * width) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in body]

    return "\n".join([header_line, divider_line, *body_lines])


def _find_caption(page: fitz.Page, table_bbox: tuple[float, float, float, float]) -> str | None:
    """Look for a 'TABLE N.' caption immediately above the table."""
    x0, y0, x1, _ = table_bbox
    search_rect = fitz.Rect(x0, max(y0 - 60, 0), x1, y0)
    try:
        nearby = page.get_text("text", clip=search_rect)
    except Exception:
        return None

    for line in reversed(nearby.splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if upper.startswith("TABLE") or upper.startswith("TBL"):
            return stripped
        return None
    return None


def _extract_prose_text(
    page: fitz.Page,
    *,
    exclude_bboxes: list[tuple[float, float, float, float]],
) -> str:
    blocks = page.get_text("blocks")
    text_blocks = [block for block in blocks if block[6] == 0 and block[4].strip()]

    if exclude_bboxes:
        text_blocks = [
            block for block in text_blocks
            if not _block_overlaps_any(block, exclude_bboxes)
        ]

    if not text_blocks:
        return ""

    if _is_two_column_layout(text_blocks, page.rect.width):
        return _extract_two_column_text(text_blocks, page.rect.width)

    text_blocks.sort(key=lambda block: (block[1], block[0]))
    return "\n\n".join(block[4].strip() for block in text_blocks)


def _block_overlaps_any(
    block: tuple,
    bboxes: list[tuple[float, float, float, float]],
) -> bool:
    bx0, by0, bx1, by1 = block[0], block[1], block[2], block[3]
    block_area = max((bx1 - bx0) * (by1 - by0), 1e-6)

    for tx0, ty0, tx1, ty1 in bboxes:
        ix0 = max(bx0, tx0)
        iy0 = max(by0, ty0)
        ix1 = min(bx1, tx1)
        iy1 = min(by1, ty1)

        if ix1 <= ix0 or iy1 <= iy0:
            continue

        intersection = (ix1 - ix0) * (iy1 - iy0)
        if intersection / block_area >= _TABLE_OVERLAP_THRESHOLD:
            return True

    return False


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
