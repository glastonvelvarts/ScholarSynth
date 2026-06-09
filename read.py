"""CLI entrypoint for PDF extraction."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from scholarsynth.exceptions import scholarsynthError
from scholarsynth.pdf_reader import read_pdf
from scholarsynth.writer import default_output_path, save_document

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract structured text from a PDF for scholarsynth.",
    )
    parser.add_argument("pdf_path", help="Path to the PDF file.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="outputs",
        help="Directory for JSON output (default: outputs).",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip header/footer removal and whitespace normalization.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(levelname)s:%(name)s:%(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)

    try:
        document = read_pdf(args.pdf_path, clean=not args.no_clean)
        output_path = default_output_path(document["document_name"], args.output_dir)
        save_document(document, output_path)
    except scholarsynthError as exc:
        logger.error("%s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
