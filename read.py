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
    """Read a PDF file and extract the text."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text+=page.get_text("text")
    return text

def main():
    parser=argparse.ArgumentParser(description="Read a PDF file and extract the text.")
    parser.add_argument("pdf_path", type=str, help="The path to the PDF file.")
    args=parser.parse_args()
    text=read_pdf(args.pdf_path)
    logger.info(f"Extracted {len(text)} characters from {args.pdf_path}")
    return text

if __name__ == "__main__":
    main()
