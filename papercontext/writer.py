"""JSON persistence for extracted documents."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from papercontext.models import Document

logger = logging.getLogger(__name__)


def save_document(document: Document, output_path: str | Path) -> Path:
    """
    Write a document to JSON.

    Args:
        document: Structured document from read_pdf.
        output_path: Destination file path.

    Returns:
        Resolved output path.
    """
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(document, file, indent=2, ensure_ascii=False)

    logger.info("Saved document to %s", path)
    return path


def default_output_path(document_name: str, output_dir: str | Path = "outputs") -> Path:
    """Build the default JSON output path for a document."""
    return Path(output_dir) / f"{document_name}.json"
