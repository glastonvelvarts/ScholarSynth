from pymilvus import (
    CollectionSchema,
    FieldSchema,
    DataType
)

from scholarsynth.vectorstore.constants import COLLECTION_NAME, EMBEDDING_DIM

__all__ = [
    "COLLECTION_NAME",
    "EMBEDDING_DIM",
    "FIELDS",
    "SCHEMA",
    "INDEX_PARAMS",
    "SEARCH_PARAMS",
]

FIELDS = [
    FieldSchema(
        name="chunk_id",
        dtype=DataType.VARCHAR,
        max_length=256,
        is_primary=True
    ),

    FieldSchema(
        name="document_name",
        dtype=DataType.VARCHAR,
        max_length=512
    ),

    FieldSchema(
        name="page",
        dtype=DataType.INT64
    ),

    FieldSchema(
        name="page_end",
        dtype=DataType.INT64
    ),

    FieldSchema(
        name="section",
        dtype=DataType.VARCHAR,
        max_length=512
    ),

    FieldSchema(
        name="chunk_type",
        dtype=DataType.VARCHAR,
        max_length=32
    ),

    FieldSchema(
        name="text",
        dtype=DataType.VARCHAR,
        max_length=16384
    ),

    FieldSchema(
        name="citations",
        dtype=DataType.VARCHAR,
        max_length=4096
    ),

    FieldSchema(
        name="table_markdown",
        dtype=DataType.VARCHAR,
        max_length=16384
    ),

    FieldSchema(
        name="embedding",
        dtype=DataType.FLOAT_VECTOR,
        dim=EMBEDDING_DIM
    )
]

SCHEMA = CollectionSchema(
    fields=FIELDS,
    description="PaperSynth Research Paper Chunks"
)

INDEX_PARAMS = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {
        "M": 16,
        "efConstruction": 200
    }
}

SEARCH_PARAMS = {
    "metric_type": "COSINE",
    "params": {
        "ef": 64
    }
}