"""scholarsynth — production PDF extraction for research papers."""

from scholarsynth.exceptions import (
    PDFNotFoundError,
    PDFReadError,
    PDFValidationError,
    scholarsynthError,
)
from scholarsynth.models import Document, DocumentMetadata, Page
from scholarsynth.pdf_reader import read_pdf
from scholarsynth.writer import default_output_path, save_document

__all__ = [
    "Document",
    "DocumentMetadata",
    "Page",
    "scholarsynthError",
    "PDFNotFoundError",
    "PDFReadError",
    "PDFValidationError",
    "default_output_path",
    "read_pdf",
    "save_document",
]
