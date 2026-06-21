import os
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ---------------- CONFIG ----------------

load_dotenv()

SCHOLAR_API_KEY = os.getenv("SCHOLAR_API_KEY")

if not SCHOLAR_API_KEY:
    raise ValueError("SCHOLAR_API_KEY not found in .env file")

QUERY = '"voice conversion using AI"'
YEARS_BACK = 10
MAX_RESULTS = 1000          # Total papers to fetch
PAGE_SIZE = 100             # Max allowed by Semantic Scholar

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# ----------------------------------------

headers = {
    "x-api-key": SCHOLAR_API_KEY
}

current_year = datetime.now().year
min_year = current_year - YEARS_BACK

papers = []
offset = 0

while offset < MAX_RESULTS:

    params = {
        "query": QUERY,
        "limit": PAGE_SIZE,
        "offset": offset,
        "fields": (
            "title,"
            "abstract,"
            "year,"
            "authors,"
            "venue,"
            "citationCount,"
            "externalIds,"
            "url"
        )
    }

    # Retry on rate limiting
    while True:
        response = requests.get(
            BASE_URL,
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 429:
            print("Rate limit hit. Waiting 5 seconds...")
            time.sleep(5)
            continue

        response.raise_for_status()
        break

    results = response.json().get("data", [])

    if not results:
        print("No more papers found.")
        break

    for paper in results:
        year = paper.get("year")

        if year is None or year < min_year:
            continue

        authors = ", ".join(
            author.get("name", "")
            for author in paper.get("authors", [])
        )

        doi = None
        if paper.get("externalIds"):
            doi = paper["externalIds"].get("DOI")

        papers.append({
            "Title": paper.get("title"),
            "Year": year,
            "Authors": authors,
            "Venue": paper.get("venue"),
            "CitationCount": paper.get("citationCount", 0),
            "DOI": doi,
            "URL": paper.get("url"),
            "Abstract": paper.get("abstract"),
        })

    offset += PAGE_SIZE

    print(f"Fetched {len(papers)} papers so far...")

    # Respect Semantic Scholar API limit
    time.sleep(1)

# ---------------- CLEANUP ----------------

df = pd.DataFrame(papers)

# Prefer DOI deduplication
if "DOI" in df.columns:
    df = df.drop_duplicates(subset=["DOI"], keep="first")

# Fallback deduplication
df = df.drop_duplicates(subset=["Title"], keep="first")

# Sort by citations
df = df.sort_values(
    by="CitationCount",
    ascending=False,
    na_position="last"
)

df.reset_index(drop=True, inplace=True)

output_file = "semantic_scholar_results.csv"
df.to_csv(output_file, index=False)

print("=" * 50)
print(f"Saved {len(df)} papers to {output_file}")
print("=" * 50)