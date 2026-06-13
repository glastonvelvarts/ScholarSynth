"""Tests for column-aware page extraction and table formatting."""

from scholarsynth.page_extractor import (
    _block_overlaps_any,
    _is_meaningful_table,
    _is_two_column_layout,
    _normalize_rows,
    _rows_to_markdown,
)


def test_is_two_column_layout_detects_split_columns():
    blocks = [
        (50, 100, 250, 120, "Left column paragraph one with enough text.", 0, 0),
        (50, 140, 250, 160, "Left column paragraph two with enough text.", 0, 0),
        (320, 100, 520, 120, "Right column paragraph one with enough text.", 0, 0),
        (320, 140, 520, 160, "Right column paragraph two with enough text.", 0, 0),
    ]
    assert _is_two_column_layout(blocks, page_width=595.0) is True


def test_is_two_column_layout_rejects_single_column():
    blocks = [
        (50, 100, 500, 120, "Single wide paragraph with enough text here.", 0, 0),
        (50, 140, 500, 160, "Another wide paragraph with enough text here.", 0, 0),
    ]
    assert _is_two_column_layout(blocks, page_width=595.0) is False


def test_normalize_rows_strips_whitespace_and_newlines():
    rows = [
        [" Model ", "F1 ", "Recall\nscore"],
        ["FLAN-T5-XXL", "0.91", "0.93"],
        [None, "", ""],
    ]
    normalized = _normalize_rows(rows)
    assert normalized == [
        ["Model", "F1", "Recall score"],
        ["FLAN-T5-XXL", "0.91", "0.93"],
    ]


def test_rows_to_markdown_produces_valid_table():
    rows = [
        ["Model", "F1", "Recall"],
        ["FLAN-T5-XXL", "0.91", "0.93"],
        ["FLAN-T5-BASE", "0.74", "0.78"],
    ]
    md = _rows_to_markdown(rows)
    lines = md.split("\n")
    assert lines[0] == "| Model | F1 | Recall |"
    assert lines[1] == "| --- | --- | --- |"
    assert lines[2] == "| FLAN-T5-XXL | 0.91 | 0.93 |"
    assert lines[3] == "| FLAN-T5-BASE | 0.74 | 0.78 |"


def test_is_meaningful_table_rejects_trivial():
    assert not _is_meaningful_table([])
    assert not _is_meaningful_table([["single cell"]])
    assert not _is_meaningful_table([["a", "b"]])  # only one row
    assert _is_meaningful_table([["Model", "Score"], ["FLAN-T5-XXL", "0.91"]])


def test_block_overlaps_any_detects_table_region():
    table_bboxes = [(100.0, 200.0, 400.0, 400.0)]
    block_inside = (110.0, 210.0, 390.0, 390.0, "text", 0, 0)
    block_outside = (10.0, 10.0, 90.0, 90.0, "text", 0, 0)
    assert _block_overlaps_any(block_inside, table_bboxes) is True
    assert _block_overlaps_any(block_outside, table_bboxes) is False
