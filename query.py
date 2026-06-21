"""CLI wrapper — search Semantic Scholar and export results to CSV."""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from scholarsynth.semantic_search import paper_search_to_dict, search_papers

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Semantic Scholar and save results to CSV.")
    parser.add_argument("query", nargs="?", default='"voice conversion using AI"')
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--years-back", type=int, default=10)
    parser.add_argument("-o", "--output", default="semantic_scholar_results.csv")
    args = parser.parse_args()

    results = search_papers(args.query, limit=args.limit, years_back=args.years_back)
    rows = [
        {
            "Title": r.title,
            "Year": r.year,
            "Authors": ", ".join(r.authors),
            "Venue": r.publication_venue,
            "CitationCount": r.citation_count,
            "DOI": r.doi,
            "URL": r.url,
            "Abstract": r.abstract,
            "OpenAccess": r.is_open_access,
        }
        for r in results
    ]

    df = pd.DataFrame(rows)
    if "DOI" in df.columns:
        df = df.drop_duplicates(subset=["DOI"], keep="first")
    df = df.drop_duplicates(subset=["Title"], keep="first")
    df = df.sort_values(by="CitationCount", ascending=False, na_position="last")
    df.reset_index(drop=True, inplace=True)
    df.to_csv(args.output, index=False)

    logger.info("Saved %d papers to %s", len(df), args.output)
    if results:
        logger.info("Top result: %s", paper_search_to_dict(results[0])["title"])


if __name__ == "__main__":
    main()
