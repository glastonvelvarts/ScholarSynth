"""Milvus client utilities."""

import logging

from pymilvus import (
    connections,
    Collection,
    utility
)

from papercontext.vectorstore.schema import (
    COLLECTION_NAME,
    SCHEMA,
    INDEX_PARAMS
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def connect_to_milvus():

    try:

        connections.connect(
            alias="default",
            host="localhost",
            port="19530"
        )

        logger.info(
            "Connected to Milvus"
        )

    except Exception:

        logger.exception(
            "Failed to connect to Milvus"
        )

        raise


def create_collection_if_not_exists():

    connect_to_milvus()

    if utility.has_collection(
        COLLECTION_NAME
    ):

        logger.info(
            "Collection '%s' already exists",
            COLLECTION_NAME
        )

        return Collection(
            COLLECTION_NAME
        )

    collection = Collection(
        name=COLLECTION_NAME,
        schema=SCHEMA
    )

    collection.create_index(
        field_name="embedding",
        index_params=INDEX_PARAMS
    )

    logger.info(
        "Created collection '%s'",
        COLLECTION_NAME
    )

    return collection


def get_collection():

    connect_to_milvus()

    if not utility.has_collection(
        COLLECTION_NAME
    ):

        return create_collection_if_not_exists()

    collection = Collection(
        COLLECTION_NAME
    )

    collection.load()

    return collection


if __name__ == "__main__":

    collection = (
        create_collection_if_not_exists()
    )

    logger.info(
        "Collection ready: %s",
        collection.name
    )