"""Domain-specific exceptions for scholarsynth."""


class scholarsynthError(Exception):
    """Base exception for scholarsynth operations."""


class PDFNotFoundError(scholarsynthError, FileNotFoundError):
    """Raised when the requested PDF path does not exist."""


class PDFValidationError(scholarsynthError, ValueError):
    """Raised when the path is not a valid PDF file."""


class PDFReadError(scholarsynthError):
    """Raised when PDF parsing fails."""
