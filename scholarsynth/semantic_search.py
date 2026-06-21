"""Semantic Scholar paper search and open-access PDF download."""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper"
DEFAULT_FIELDS = (
    "paperId,title,abstract,year,authors,venue,citationCount,"
    "externalIds,url,openAccessPdf,isOpenAccess"
)


@dataclass
class PaperSearchResult:
    id: str
    title: str
    authors: list[str]
    abstract: str
    publication_venue: Optional[str]
    year: Optional[int]
    citation_count: int
    relevance_score: float
    is_open_access: bool
    pdf_url: Optional[str]
    url: Optional[str]
    doi: Optional[str]


def _api_key() -> str:
    key = (os.getenv("SCHOLAR_API_KEY") or "").strip()
    if not key:
        raise ValueError("SCHOLAR_API_KEY not configured")
    return key


def _headers() -> dict[str, str]:
    return {"x-api-key": _api_key()}


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    while True:
        response = requests.request(method, url, headers=_headers(), timeout=30, **kwargs)
        if response.status_code == 429:
            logger.warning("Semantic Scholar rate limit — waiting 5s")
            time.sleep(5)
            continue
        response.raise_for_status()
        return response


def _safe_filename(title: str, paper_id: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title or "paper").strip().replace(" ", "_")
    slug = slug[:80] or "paper"
    return f"{slug}_{paper_id[:8]}.pdf"


def search_papers(
    query: str,
    *,
    limit: int = 20,
    offset: int = 0,
    years_back: int = 10,
) -> list[PaperSearchResult]:
    """Search Semantic Scholar and return deduplicated, ranked results."""
    current_year = datetime.now().year
    min_year = current_year - years_back

    params = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset,
        "fields": DEFAULT_FIELDS,
    }

    response = _request_with_retry("GET", SEARCH_URL, params=params)
    raw = response.json().get("data", [])

    seen_titles: set[str] = set()
    results: list[PaperSearchResult] = []

    for idx, paper in enumerate(raw):
        year = paper.get("year")
        if year is not None and year < min_year:
            continue

        title = (paper.get("title") or "").strip()
        if not title:
            continue

        norm_title = title.lower()
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)

        authors = [
            a.get("name", "")
            for a in paper.get("authors") or []
            if a.get("name")
        ]

        oa = paper.get("openAccessPdf") or {}
        pdf_url = oa.get("url")
        doi = None
        if paper.get("externalIds"):
            doi = paper["externalIds"].get("DOI")

        results.append(
            PaperSearchResult(
                id=paper.get("paperId", ""),
                title=title,
                authors=authors,
                abstract=(paper.get("abstract") or "").strip(),
                publication_venue=paper.get("venue"),
                year=year,
                citation_count=int(paper.get("citationCount") or 0),
                relevance_score=max(0.55, 0.97 - idx * 0.04),
                is_open_access=bool(paper.get("isOpenAccess") or pdf_url),
                pdf_url=pdf_url,
                url=paper.get("url"),
                doi=doi,
            )
        )

    return results[:limit]


def fetch_paper_pdf_url(paper_id: str) -> Optional[str]:
    """Resolve an open-access PDF URL for a paper ID."""
    response = _request_with_retry(
        "GET",
        f"{PAPER_URL}/{paper_id}",
        params={"fields": "openAccessPdf,isOpenAccess"},
    )
    data = response.json()
    oa = data.get("openAccessPdf") or {}
    return oa.get("url")


def download_paper_pdf(paper_id: str, dest_dir: Path, *, title: str = "") -> Path:
    """
    Download an open-access PDF for the given paper.

    Raises ValueError when no PDF is available.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    pdf_url = fetch_paper_pdf_url(paper_id)
    if not pdf_url:
        raise ValueError(f"No open-access PDF available for paper {paper_id}")

    dest_path = dest_dir / _safe_filename(title, paper_id)

    response = requests.get(pdf_url, timeout=60, stream=True)
    response.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info("Downloaded %s -> %s", paper_id, dest_path.name)
    return dest_path


def paper_search_to_dict(result: PaperSearchResult) -> dict:
    tags: list[str] = []
    if result.publication_venue:
        tags.append(result.publication_venue)
    if result.is_open_access:
        tags.append("Open Access")

    return {
        "id": result.id,
        "title": result.title,
        "authors": result.authors,
        "abstract": result.abstract,
        "publication_venue": result.publication_venue,
        "year": result.year,
        "tags": tags[:4],
        "relevance_score": round(result.relevance_score, 3),
        "is_open_access": result.is_open_access,
        "pdf_url": result.pdf_url,
        "url": result.url,
        "citation_count": result.citation_count,
    }
