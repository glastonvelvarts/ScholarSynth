"""Drop the papersynth Milvus collection."""

from __future__ import annotations

import logging
import sys

from pymilvus import MilvusClient, MilvusException

logger = logging.getLogger(__name__)

COLLECTION_NAME = "papersynth"
MILVUS_URI = "http://localhost:19530"


def drop_collection(collection_name: str = COLLECTION_NAME) -> None:
    client = MilvusClient(uri=MILVUS_URI)

    if not client.has_collection(collection_name):
        logger.info("Collection '%s' does not exist; nothing to drop.", collection_name)
        return

    client.drop_collection(collection_name)
    logger.info("Dropped collection '%s'.", collection_name)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    try:
        drop_collection()
    except MilvusException as exc:
        logger.error("Failed to drop collection: %s", exc)
        logger.error(
            "Milvus cluster metadata is likely out of sync. Reset it with:\n"
            "  docker compose down\n"
            "  docker compose up -d\n"
            "Then retry. If it still fails, wipe volumes (deletes all Milvus data):\n"
            "  docker compose down -v\n"
            "  docker compose up -d"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
