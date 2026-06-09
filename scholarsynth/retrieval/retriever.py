import logging
from typing import List, Dict, Optional

import torch
from pymilvus import Collection
from sentence_transformers import SentenceTransformer

from scholarsynth.vectorstore.client import (
    connect_to_milvus
)

logger = logging.getLogger(__name__)

MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "papersynth"

_MODEL = None


def load_model() -> SentenceTransformer:
    """
    Loads the embedding model.
    """

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
        "Loaded model %s on %s",
        MODEL_NAME,
        device
    )

    return model


def get_model() -> SentenceTransformer:
    """
    Singleton model loader.
    Prevents reloading the model
    for every query.
    """

    global _MODEL

    if _MODEL is None:
        _MODEL = load_model()

    return _MODEL


def embed_query(
    query: str
):
    """
    Converts a query into
    a dense vector embedding.
    """

    model = get_model()

    embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    return embedding


def search_collection(
    query_embedding,
    top_k: int = 5,
    expr: Optional[str] = None
):
    """
    Searches Milvus for
    the most relevant chunks.
    """

    connect_to_milvus()

    collection = Collection(
        COLLECTION_NAME
    )

    collection.load()

    logger.info(
        "Searching collection %s",
        COLLECTION_NAME
    )

    search_params = {
        "metric_type": "COSINE",
        "params": {
            "ef": 64
        }
    }

    results = collection.search(
        data=[
            query_embedding.tolist()
        ],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=expr,
        output_fields=[
            "chunk_id",
            "document_name",
            "page",
            "text"
        ]
    )

    logger.info(
        "Retrieved %d results",
        len(results[0])
    )

    return results


def format_results(
    results
) -> List[Dict]:
    """
    Converts Milvus search hits
    into plain Python dictionaries.
    """

    formatted_results = []

    for hit in results[0]:

        formatted_results.append(
            {
                "score": float(
                    hit.distance
                ),
                "chunk_id": hit.entity.get(
                    "chunk_id"
                ),
                "document_name":
                hit.entity.get(
                    "document_name"
                ),
                "page":
                hit.entity.get(
                    "page"
                ),
                "text":
                hit.entity.get(
                    "text"
                )
            }
        )

    return formatted_results


def retrieve(
    query: str,
    top_k: int = 5,
    expr: Optional[str] = None
) -> List[Dict]:
    """
    Main retrieval function.

    Flow:
        Query
          ↓
        Embedding
          ↓
        Milvus Search
          ↓
        Structured Results
    """

    logger.info(
        "Retrieving documents for query: %s",
        query
    )

    query_embedding = embed_query(
        query
    )

    results = search_collection(
        query_embedding=query_embedding,
        top_k=top_k,
        expr=expr
    )

    return format_results(
        results
    )


if __name__ == "__main__":

   
    query = input(
        "\nQuestion: "
    )
    logging.basicConfig(
        level=logging.INFO
    )

    results = retrieve(
        query=query,
        top_k=5
    )

    print("\n")

    for idx, result in enumerate(
        results,
        start=1
    ):

        print("=" * 100)

        print(
            f"Result {idx}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            f"Document: "
            f"{result['document_name']}"
        )

        print(
            f"Page: "
            f"{result['page']}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print()

        print(
            result["text"][:500]
        )

        print()