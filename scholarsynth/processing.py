"""End-to-end PDF processing: extract, chunk, embed, and ingest into Milvus."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Optional

from scholarsynth.chunker import chunk_document
from scholarsynth.embedder import embed_chunks, load_model
from scholarsynth.pdf_reader import read_pdf
from scholarsynth.vectorstore.client import get_collection
from scholarsynth.vectorstore.ingest import prepare_data

logger = logging.getLogger(__name__)

StatusCallback = Callable[[str], None]

UPLOAD_DIR = Path(os.environ.get("SCHOLARSYNTH_UPLOAD_DIR", "uploads"))

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = load_model()
    return _embedding_model


def ingest_chunks(chunks: list[dict]) -> int:
    if not chunks:
        return 0

    collection = get_collection()
    data = prepare_data(chunks)
    collection.insert(data)
    collection.flush()
    logger.info("Ingested %d chunks into Milvus", len(chunks))
    return len(chunks)


def process_pdf(
    pdf_path: Path,
    *,
    on_status: Optional[StatusCallback] = None,
) -> dict:
    """Run the full pipeline on a single PDF file."""
    def _status(step: str) -> None:
        if on_status:
            on_status(step)

    _status("uploading")
    _status("reading")
    document = read_pdf(pdf_path)

    _status("cleaning")
    _status("chunking")
    chunks = chunk_document(document)
    if not chunks:
        raise ValueError(f"No chunks produced from {pdf_path.name}")

    _status("embedding")
    model = get_embedding_model()
    embedded = embed_chunks(chunks, model)
    if not embedded:
        raise ValueError(f"Embedding failed for {pdf_path.name}")

    _status("indexing")
    chunk_count = ingest_chunks(embedded)
    _status("ready")

    meta = document["metadata"]
    return {
        "id": document["document_name"],
        "title": document["document_name"].removesuffix(".pdf"),
        "document_name": document["document_name"],
        "page_count": meta["page_count"],
        "chunk_count": chunk_count,
        "source_path": str(pdf_path),
    }


def list_indexed_documents() -> list[dict]:
    """Return unique documents currently indexed in Milvus."""
    try:
        collection = get_collection()
        rows = collection.query(
            expr='chunk_id != ""',
            output_fields=["document_name"],
            limit=16384,
        )
    except Exception:
        logger.exception("Failed to list documents from Milvus")
        return []

    seen: dict[str, dict] = {}
    for row in rows:
        name = row.get("document_name", "")
        if name and name not in seen:
            seen[name] = {
                "id": name,
                "title": name.removesuffix(".pdf"),
                "document_name": name,
            }
    return list(seen.values())
