"""Structured document models for extracted PDF content."""

from __future__ import annotations

from typing import TypedDict


class Page(TypedDict):
    page: int
    text: str


class DocumentMetadata(TypedDict):
    source_path: str
    page_count: int
    total_characters: int
    cleaned: bool


class Document(TypedDict):
    document_name: str
    metadata: DocumentMetadata
    pages: list[Page]
