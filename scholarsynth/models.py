"""Structured document and chunk models."""

from __future__ import annotations

from typing import Literal, Optional, TypedDict


ChunkType = Literal["prose", "table", "reference", "metadata"]


class TableBlock(TypedDict):
    """A table extracted from a PDF page."""

    rows: list[list[str]]
    markdown: str
    caption: Optional[str]
    bbox: tuple[float, float, float, float]


class Page(TypedDict, total=False):
    page: int
    text: str
    tables: list[TableBlock]


class DocumentMetadata(TypedDict):
    source_path: str
    page_count: int
    total_characters: int
    cleaned: bool


class Document(TypedDict):
    document_name: str
    metadata: DocumentMetadata
    pages: list[Page]


class Chunk(TypedDict, total=False):
    chunk_id: str
    document_name: str
    page: int
    page_end: int
    chunk_index: int
    section: Optional[str]
    chunk_type: ChunkType
    sentence_count: int
    text: str
    text_clean: str
    citations: list[str]
    table_markdown: Optional[str]
    embedding: list[float]
