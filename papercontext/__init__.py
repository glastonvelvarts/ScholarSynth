"""PaperContext — production PDF extraction for research papers."""

from papercontext.exceptions import (
    PDFNotFoundError,
    PDFReadError,
    PDFValidationError,
    PaperContextError,
)
from papercontext.models import Document, DocumentMetadata, Page
from papercontext.pdf_reader import read_pdf
from papercontext.writer import default_output_path, save_document

__all__ = [
    "Document",
    "DocumentMetadata",
    "Page",
    "PaperContextError",
    "PDFNotFoundError",
    "PDFReadError",
    "PDFValidationError",
    "default_output_path",
    "read_pdf",
    "save_document",
]
