import logging
import torch

from pymilvus import Collection
from sentence_transformers import SentenceTransformer

from scholarsynth.vectorstore.client import (
    connect_to_milvus
)

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "papersynth"

def load_model():

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
        device=device
    )

    logger.info(
        "Loaded %s on %s",
        MODEL_NAME,
        device
    )

    return model


def embed_query(
    query: str,
    model
):

    return model.encode(
        query,
        normalize_embeddings=True
    )


def search_collection(
    query_embedding,
    top_k=5
):

    connect_to_milvus()

    collection = Collection(
        COLLECTION_NAME
    )

    collection.load()

    results = collection.search(
        data=[
            query_embedding.tolist()
        ],
        anns_field="embedding",
        param={
            "metric_type": "COSINE",
            "params": {
                "ef": 64
            }
        },
        limit=top_k,
        output_fields=[
            "chunk_id",
            "document_name",
            "page",
            "text"
        ]
    )

    return results