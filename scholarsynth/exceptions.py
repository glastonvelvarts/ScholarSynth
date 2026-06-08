"""Domain-specific exceptions for PaperContext."""


class PaperContextError(Exception):
    """Base exception for PaperContext operations."""


class PDFNotFoundError(PaperContextError, FileNotFoundError):
    """Raised when the requested PDF path does not exist."""


class PDFValidationError(PaperContextError, ValueError):
    """Raised when the path is not a valid PDF file."""


class PDFReadError(PaperContextError):
    """Raised when PDF parsing fails."""
