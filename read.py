"""
This script reads a PDF file and extracts the text.
"""
import pymupdf as fitz
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)

logger=logging.getLogger(__name__)


def read_pdf(pdf_path):
    """Read a PDF and return a structured document with per-page text."""
    document = {
        "document_name": os.path.basename(pdf_path),
        "pages": [],
    }
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            document["pages"].append({
                "page": page_num,
                "text": page.get_text("text"),
            })
    return document


def main():
    parser = argparse.ArgumentParser(description="Read a PDF file and extract the text.")
    parser.add_argument("pdf_path", type=str, help="The path to the PDF file.")
    args = parser.parse_args()
    document = read_pdf(args.pdf_path)
    char_count = sum(len(p["text"]) for p in document["pages"])
    logger.info(
        "Extracted %d characters across %d pages from %s",
        char_count,
        len(document["pages"]),
        document["document_name"],
    )
    return document

if __name__ == "__main__":
    main()
