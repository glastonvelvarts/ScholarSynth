"""Produce typed chunks (prose / table / reference / metadata) from a document."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional

from scholarsynth.citations import strip_citations
from scholarsynth.models import Chunk, ChunkType
from scholarsynth.semantic_chunker import (
    DEFAULT_BREAKPOINT_PERCENTILE,
    DEFAULT_MAX_CHUNK_CHARS,
    DEFAULT_MIN_CHUNK_CHARS,
    DEFAULT_MODEL_NAME,
    SentenceSpan,
    semantic_chunk_sentences,
    split_sentences,
)

logger = logging.getLogger(__name__)

CHUNK_SIZE = DEFAULT_MAX_CHUNK_CHARS
CHUNK_OVERLAP = 0

_MODEL: Optional[Any] = None

_REFERENCE_SECTION = re.compile(
    r"references|bibliography|acknowledgments?", re.IGNORECASE
)
_BRACKET_REF_START = re.compile(r"^\s*\[\d+\]\s+")
_EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


def _get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    global _MODEL

    if _MODEL is None:
        import torch
        from sentence_transformers import SentenceTransformer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _MODEL = SentenceTransformer(model_name, trust_remote_code=True, device=device)
        logger.info("Loaded chunking model %s on %s", model_name, device)

    return _MODEL


def _make_embed_fn(model):
    def embed(texts: list[str]):
        import numpy as np

        clean_texts = [strip_citations(text).cleaned for text in texts]
        vectors = model.encode(
            clean_texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(vectors)

    return embed


def collect_sentences(document: dict) -> list[SentenceSpan]:
    """Flatten prose pages into ordered sentences with page and section metadata."""
    sentences: list[SentenceSpan] = []
    current_section: Optional[str] = None

    for page_data in document["pages"]:
        page_number = page_data["page"]
        page_text = page_data.get("text", "")

        if not page_text.strip():
            continue

        page_sentences = split_sentences(page_text, page_number, current_section)
        for span in page_sentences:
            if span.section:
                current_section = span.section
            sentences.append(span)

    return sentences


def _section_by_page(sentences: list[SentenceSpan]) -> dict[int, Optional[str]]:
    """Determine the active section at the start of each page."""
    seen: dict[int, Optional[str]] = {}
    current: Optional[str] = None
    for span in sentences:
        if span.section:
            current = span.section
        if span.page not in seen:
            seen[span.page] = current
    return seen


def _collect_table_chunks(
    document: dict,
    section_by_page: dict[int, Optional[str]],
) -> list[dict]:
    """One chunk per table, embedding caption + markdown for searchability."""
    out: list[dict] = []
    for page_data in document["pages"]:
        page = page_data["page"]
        for table in page_data.get("tables", []):
            caption = (table.get("caption") or "").strip()
            markdown = table["markdown"]
            text = f"{caption}\n\n{markdown}" if caption else markdown
            out.append(
                {
                    "page": page,
                    "section": section_by_page.get(page),
                    "text": text,
                    "markdown": markdown,
                    "caption": caption or None,
                }
            )
    return out


def _classify_prose(text: str, section: Optional[str], is_first: bool) -> ChunkType:
    if section and _REFERENCE_SECTION.search(section):
        return "reference"
    if _BRACKET_REF_START.match(text):
        return "reference"
    if is_first and section is None and _EMAIL_PATTERN.search(text):
        return "metadata"
    return "prose"


def chunk_document(
    document: dict,
    *,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS,
    breakpoint_percentile: float = DEFAULT_BREAKPOINT_PERCENTILE,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[Chunk]:
    """
    Build typed semantic chunks from a Document.

    For each chunk we store:
      - text: original (for display, includes citations)
      - text_clean: citation-stripped (for embedding)
      - citations: extracted refs preserved for lookup
      - chunk_type: "prose" | "table" | "reference" | "metadata"
      - table_markdown: present only for table chunks
    """
    document_name = document["document_name"]
    document_id = document_name.replace(" ", "_").replace(".pdf", "")

    sentences = collect_sentences(document)
    section_by_page = _section_by_page(sentences)
    table_records = _collect_table_chunks(document, section_by_page)

    prose_chunks: list = []
    if sentences:
        model = _get_embedding_model(model_name)
        embed_fn = _make_embed_fn(model)
        prose_chunks = semantic_chunk_sentences(
            sentences,
            embed_fn,
            max_chunk_chars=max_chunk_chars,
            min_chunk_chars=min_chunk_chars,
            breakpoint_percentile=breakpoint_percentile,
        )

    items: list[tuple[int, int, str, object]] = []
    for order_idx, tc in enumerate(prose_chunks):
        items.append((tc.page, 0, "prose", tc))
    for order_idx, tab in enumerate(table_records):
        items.append((tab["page"], 1, "table", tab))

    items.sort(key=lambda item: (item[0], item[1]))

    chunks: list[Chunk] = []
    for idx, (_, _, kind, payload) in enumerate(items):
        if kind == "prose":
            tc = payload  # TextChunk
            citation_result = strip_citations(tc.text)
            chunk_type = _classify_prose(
                citation_result.original,
                tc.section,
                is_first=idx == 0,
            )
            chunks.append(
                {
                    "chunk_id": f"{document_id}_{idx}",
                    "document_name": document_name,
                    "page": tc.page,
                    "page_end": tc.page_end,
                    "chunk_index": idx,
                    "section": tc.section,
                    "chunk_type": chunk_type,
                    "sentence_count": tc.sentence_count,
                    "text": citation_result.original,
                    "text_clean": citation_result.cleaned,
                    "citations": citation_result.citations,
                    "table_markdown": None,
                }
            )
        else:
            tab = payload
            chunks.append(
                {
                    "chunk_id": f"{document_id}_{idx}",
                    "document_name": document_name,
                    "page": tab["page"],
                    "page_end": tab["page"],
                    "chunk_index": idx,
                    "section": tab.get("section"),
                    "chunk_type": "table",
                    "sentence_count": 0,
                    "text": tab["text"],
                    "text_clean": tab["text"],
                    "citations": [],
                    "table_markdown": tab["markdown"],
                }
            )

    type_counts = {ct: 0 for ct in ("prose", "table", "reference", "metadata")}
    for chunk in chunks:
        type_counts[chunk["chunk_type"]] += 1

    logger.info(
        "Created %d chunks from %s (prose=%d, table=%d, reference=%d, metadata=%d)",
        len(chunks),
        document_name,
        type_counts["prose"],
        type_counts["table"],
        type_counts["reference"],
        type_counts["metadata"],
    )

    return chunks


def save_chunks(chunks: list[Chunk], output_file: str = "chunked.json") -> str:
    os.makedirs("chunked_data", exist_ok=True)
    output_path = os.path.join("chunked_data", output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    logger.info("Saved %d chunks to %s", len(chunks), output_path)
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open(
        "outputs/Automating_Customer_Service_Using_Langchain.pdf.json",
        "r",
        encoding="utf-8",
    ) as f:
        document = json.load(f)

    chunks = chunk_document(document)
    save_chunks(chunks)

    if chunks:
        first = chunks[0]
        logger.info("First chunk (%s):\n%s", first["chunk_type"], first["text_clean"][:300])
        logger.info("Citations in first chunk: %s", first["citations"])
