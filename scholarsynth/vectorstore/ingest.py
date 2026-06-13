import json
import logging
import os

from scholarsynth.vectorstore.client import get_collection

logger = logging.getLogger(__name__)

EMBEDDED_DATA_PATH = (
    "embedded_data/embedded_chunks.json"
)


def load_embedded_chunks():

    try:
        with open(
            EMBEDDED_DATA_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except FileNotFoundError:

        logger.error(
            "Embedded chunk file not found"
        )

        return []


def _serialize_citations(citations) -> str:
    if not citations:
        return "[]"
    if isinstance(citations, str):
        return citations
    return json.dumps(citations, ensure_ascii=False)


_TEXT_MAX_CHARS = 16000
_MARKDOWN_MAX_CHARS = 16000
_SECTION_MAX_CHARS = 500
_CITATIONS_MAX_CHARS = 4000


def _truncate(value: str, max_chars: int) -> str:
    if value is None:
        return ""
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3] + "..."


def prepare_data(chunks):
    return [
        [c["chunk_id"] for c in chunks],
        [c["document_name"] for c in chunks],
        [c["page"] for c in chunks],
        [c.get("page_end", c["page"]) for c in chunks],
        [_truncate(c.get("section") or "", _SECTION_MAX_CHARS) for c in chunks],
        [c.get("chunk_type", "prose") for c in chunks],
        [_truncate(c["text"], _TEXT_MAX_CHARS) for c in chunks],
        [
            _truncate(_serialize_citations(c.get("citations", [])), _CITATIONS_MAX_CHARS)
            for c in chunks
        ],
        [_truncate(c.get("table_markdown") or "", _MARKDOWN_MAX_CHARS) for c in chunks],
        [c["embedding"] for c in chunks],
    ]


def ingest_chunks():

    chunks = load_embedded_chunks()

    if not chunks:

        logger.error(
            "No chunks found for ingestion"
        )

        return

    collection = get_collection()

    data = prepare_data(
        chunks
    )

    logger.info(
        "Inserting %d chunks",
        len(chunks)
    )

    collection.insert(
        data
    )

    collection.flush()

    logger.info(
        "Inserted %d chunks successfully",
        len(chunks)
    )

    logger.info(
        "Collection now contains %d entities",
        collection.num_entities
    )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    ingest_chunks()