import json
import logging
import os

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
):
    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text)
        )

        chunks.append({
            "text": text[start:end],
            "start_char": start,
            "end_char": end
        })

        start += chunk_size - overlap

    return chunks


def chunk_document(document: dict):
    chunks = []

    document_name = document["document_name"]

    document_id = (
        document_name
        .replace(" ", "_")
        .replace(".pdf", "")
    )

    for page_data in document["pages"]:

        page_number = page_data["page"]
        page_text = page_data["text"]

        if not page_text.strip():
            continue

        page_chunks = chunk_text(page_text)

        for idx, chunk_data in enumerate(page_chunks):

            chunks.append(
                {
                    "chunk_id": f"{document_id}_{page_number}_{idx}",
                    "document_name": document_name,
                    "page": page_number,
                    "chunk_index": idx,
                    "start_char": chunk_data["start_char"],
                    "end_char": chunk_data["end_char"],
                    "section": None,
                    "text": chunk_data["text"],
                }
            )

    logger.info(
        "Created %d chunks from %s",
        len(chunks),
        document_name
    )

    return chunks


def save_chunks(
    chunks,
    output_file="chunked.json"
):
    os.makedirs(
        "chunked_data",
        exist_ok=True
    )

    output_path = os.path.join(
        "chunked_data",
        output_file
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            chunks,
            f,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Saved %d chunks to %s",
        len(chunks),
        output_path
    )

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    with open(
        "outputs/Automating_Customer_Service_Using_Langchain.pdf.json",
        "r",
        encoding="utf-8"
    ) as f:
        document = json.load(f)

    chunks = chunk_document(document)

    save_chunks(chunks)

    logger.info(
        "First chunk:\n%s",
        chunks[0]["text"][:300]
    )