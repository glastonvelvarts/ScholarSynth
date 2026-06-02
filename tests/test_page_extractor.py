"""Tests for column-aware page extraction."""

from papercontext.page_extractor import _is_two_column_layout


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
