"""PDF text + table extraction with validation and optional cleaning."""

from __future__ import annotations

import logging
from pathlib import Path

import pymupdf as fitz

from scholarsynth.exceptions import PDFNotFoundError, PDFReadError, PDFValidationError
from scholarsynth.models import Document, Page, TableBlock
from scholarsynth.page_extractor import extract_page_content
from scholarsynth.text_cleaner import clean_page_texts

logger = logging.getLogger(__name__)


def _validate_pdf_path(pdf_path: str | Path) -> Path:
    path = Path(pdf_path).expanduser().resolve()

    if not path.exists():
        raise PDFNotFoundError(f"PDF not found: {path}")
    if not path.is_file():
        raise PDFValidationError(f"Expected a file, got directory: {path}")
    if path.suffix.lower() != ".pdf":
        raise PDFValidationError(f"Expected a .pdf file, got: {path.suffix!r}")

    return path


def _extract_raw_pages(doc: fitz.Document) -> list[dict]:
    return [extract_page_content(page) for page in doc]


def read_pdf(pdf_path: str | Path, *, clean: bool = True) -> Document:
    """
    Read a PDF and return a structured document with per-page prose and tables.

    Args:
        pdf_path: Path to the PDF file.
        clean: When True, remove repeated headers/footers and normalize whitespace
            for the prose stream. Tables are kept verbatim either way.

    Returns:
        Document dict with document_name, metadata, and pages.
    """
    path = _validate_pdf_path(pdf_path)

    try:
        with fitz.open(path) as doc:
            if doc.page_count == 0:
                raise PDFReadError(f"PDF has no pages: {path}")

            raw_pages = _extract_raw_pages(doc)
            raw_texts = [item["text"] for item in raw_pages]
            page_texts = clean_page_texts(raw_texts) if clean else raw_texts

            pages: list[Page] = []
            for page_num, (text, raw) in enumerate(zip(page_texts, raw_pages), start=1):
                tables: list[TableBlock] = raw.get("tables", [])
                pages.append(
                    {
                        "page": page_num,
                        "text": text,
                        "tables": tables,
                    }
                )
    except (PDFNotFoundError, PDFValidationError, PDFReadError):
        raise
    except fitz.FileDataError as exc:
        raise PDFReadError(f"Failed to read PDF: {path}") from exc
    except Exception as exc:
        raise PDFReadError(f"Unexpected error reading PDF: {path}") from exc

    total_characters = sum(len(page["text"]) for page in pages)
    total_tables = sum(len(page.get("tables", [])) for page in pages)

    document: Document = {
        "document_name": path.name,
        "metadata": {
            "source_path": str(path),
            "page_count": len(pages),
            "total_characters": total_characters,
            "cleaned": clean,
        },
        "pages": pages,
    }

    logger.info(
        "Extracted %d characters and %d tables across %d pages from %s (cleaned=%s)",
        total_characters,
        total_tables,
        len(pages),
        document["document_name"],
        clean,
    )

    return document
