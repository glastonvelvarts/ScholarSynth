"""Tests for PDF path validation."""

import pytest

from papercontext.exceptions import PDFNotFoundError, PDFValidationError
from papercontext.pdf_reader import _validate_pdf_path


def test_validate_pdf_path_missing_file(tmp_path):
    missing = tmp_path / "missing.pdf"
    with pytest.raises(PDFNotFoundError):
        _validate_pdf_path(missing)


def test_validate_pdf_path_wrong_extension(tmp_path):
    wrong = tmp_path / "document.txt"
    wrong.write_text("not a pdf", encoding="utf-8")
    with pytest.raises(PDFValidationError, match="Expected a .pdf"):
        _validate_pdf_path(wrong)


def test_validate_pdf_path_directory(tmp_path):
    with pytest.raises(PDFValidationError, match="Expected a file"):
        _validate_pdf_path(tmp_path)
