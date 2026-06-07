import json
import logging
import os

from pymilvus import Collection

from papercontext.vectorstore.client import get_collection

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


def prepare_data(chunks):

    return [
        [c["chunk_id"] for c in chunks],
        [c["document_name"] for c in chunks],
        [c["page"] for c in chunks],
        [c["text"] for c in chunks],
        [c["embedding"] for c in chunks]
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