import torch
import logging
import os
from sentence_transformers import SentenceTransformer
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MODEL_NAME = "BAAI/bge-m3"
CHUNKED_DATA_PATH = "chunked_data/chunked.json"

def load_chunks():
    file_path=CHUNKED_DATA_PATH
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON: {file_path}")
        return []


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(
        f"CUDA Available: {torch.cuda.is_available()}"
    )

    if torch.cuda.is_available():
        logger.info(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

    logger.info(
        f"Loading model {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
        device=device
    )

    logger.info(
        f"Loaded model on {device}"
    )

    return model
def embed_chunks(chunks,model):
    texts=[chunk["text"] for chunk in chunks]
    try:
        logger.info("text encoding started....")
        embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    except Exception as e:
        logger.error(f"Error embedding chunks: {e}")
        return []
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"]=embedding.tolist()
    return chunks

    # return embeddings

def save_embeddings(
    embedded_chunks,
    output_file
):

    os.makedirs(
        "embedded_data",
        exist_ok=True
    )

    output_path = os.path.join(
        "embedded_data",
        output_file
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            embedded_chunks,
            f,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Saved embeddings to %s",
        output_path
    )


if __name__ == "__main__":

    chunk_file = os.path.join(
        "chunked_data",
        "chunked.json"
    )

    chunks = load_chunks()

    model = load_model()

    embedded_chunks = embed_chunks(
        chunks,
        model
    )

    save_embeddings(
        embedded_chunks,
        "embedded_chunks.json"
    )

    logger.info(
        "Embedded %d chunks",
        len(embedded_chunks)
    )

    logger.info(
        "Embedding Dimension: %d",
        len(
            embedded_chunks[0]["embedding"]
        )
    )