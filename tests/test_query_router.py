"""Tests for query routing."""

from scholarsynth.rag.query_router import is_general_query


def test_general_query_detects_summarize():
    assert is_general_query("Summarize all uploaded papers") is True


def test_general_query_detects_compare():
    assert is_general_query("Compare the methodologies across papers") is True


def test_specific_query_not_general():
    assert is_general_query("What F1 score did the model achieve on CIFAR-10?") is False
