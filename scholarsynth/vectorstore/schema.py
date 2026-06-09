from pymilvus import (
    CollectionSchema,
    FieldSchema,
    DataType
)

COLLECTION_NAME = "papersynth"

EMBEDDING_DIM = 1024

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
        name="text",
        dtype=DataType.VARCHAR,
        max_length=8192
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