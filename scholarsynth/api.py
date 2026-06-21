"""FastAPI server exposing the ScholarSynth RAG pipeline."""

from __future__ import annotations

import logging
import os
import shutil
import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scholarsynth.jobs import (
    create_job,
    finish_job,
    get_job,
    job_to_dict,
    update_job_step,
    update_paper_status,
)
from scholarsynth.processing import UPLOAD_DIR, list_indexed_documents, process_pdf
from scholarsynth.rag.pipeline import default_retrieval_config, rag_response_to_dict, run_rag
from scholarsynth.semantic_search import (
    download_paper_pdf,
    paper_search_to_dict,
    search_papers,
)

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="ScholarSynth API", version="0.1.0")

_cors_origins = os.environ.get(
    "SCHOLARSYNTH_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Request / response models ────────────────────────────────────────────────


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    document_filter: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    query: str
    answer: str
    confident: bool
    retrieval_score: float
    retrieval_message: Optional[str] = None
    citations: list[dict]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    years_back: int = Field(default=10, ge=1, le=50)


class ImportPapersRequest(BaseModel):
    paper_ids: list[str] = Field(min_length=1, max_length=10)
    titles: Optional[dict[str, str]] = None


# ── Background processing ─────────────────────────────────────────────────────


def _run_upload_job(job_id: str, saved_paths: list[tuple[str, str, Path]]) -> None:
    """Process uploaded PDFs. saved_paths: (paper_id, title, path)."""
    try:
        for paper_id, title, path in saved_paths:
            update_paper_status(job_id, paper_id, status="processing")

            def on_status(step: str) -> None:
                update_job_step(job_id, step)

            try:
                result = process_pdf(path, on_status=on_status)
                update_paper_status(
                    job_id,
                    paper_id,
                    status="ready",
                    page_count=result["page_count"],
                )
            except Exception as exc:
                logger.exception("Failed to process %s", path.name)
                update_paper_status(job_id, paper_id, status="error", error=str(exc))
    except Exception as exc:
        logger.exception("Upload job failed")
        finish_job(job_id, error=str(exc))
        return

    finish_job(job_id)


def _run_import_job(
    job_id: str,
    items: list[tuple[str, str]],
) -> None:
    """Download and process papers from Semantic Scholar. items: (paper_id, title)."""
    download_dir = UPLOAD_DIR / "imports"
    download_dir.mkdir(parents=True, exist_ok=True)

    try:
        for paper_id, title in items:
            update_paper_status(job_id, paper_id, status="processing")
            update_job_step(job_id, "uploading")

            try:
                pdf_path = download_paper_pdf(paper_id, download_dir, title=title)

                def on_status(step: str) -> None:
                    update_job_step(job_id, step)

                result = process_pdf(pdf_path, on_status=on_status)
                update_paper_status(
                    job_id,
                    paper_id,
                    status="ready",
                    page_count=result["page_count"],
                )
            except ValueError as exc:
                logger.warning("Import skipped for %s: %s", paper_id, exc)
                update_paper_status(job_id, paper_id, status="error", error=str(exc))
            except Exception as exc:
                logger.exception("Import failed for %s", paper_id)
                update_paper_status(job_id, paper_id, status="error", error=str(exc))
    except Exception as exc:
        logger.exception("Import job failed")
        finish_job(job_id, error=str(exc))
        return

    finish_job(job_id)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/query", response_model=QueryResponse)
def query_documents(body: QueryRequest) -> QueryResponse:
    try:
        config = default_retrieval_config(
            document_filter=body.document_filter,
            top_k=body.top_k,
        )
        result = run_rag(body.query.strip(), retrieval_config=config)
        payload = rag_response_to_dict(result)
        return QueryResponse(**payload)
    except Exception as exc:
        logger.exception("RAG query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/search")
def search(body: SearchRequest) -> dict:
    try:
        results = search_papers(
            body.query.strip(),
            limit=body.limit,
            offset=body.offset,
            years_back=body.years_back,
        )
        return {
            "query": body.query,
            "count": len(results),
            "results": [paper_search_to_dict(r) for r in results],
        }
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/papers")
def list_papers() -> dict:
    try:
        docs = list_indexed_documents()
        return {"papers": docs, "count": len(docs)}
    except Exception as exc:
        logger.exception("List papers failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/papers/upload")
async def upload_papers(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per upload")

    saved: list[tuple[str, str, Path]] = []
    job_items: list[tuple[str, str, str]] = []

    for upload in files:
        if not upload.filename or not upload.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Only PDF files accepted: {upload.filename}")

        safe_name = Path(upload.filename).name
        dest = UPLOAD_DIR / safe_name
        if dest.exists():
            stem = dest.stem
            suffix = dest.suffix
            counter = 1
            while dest.exists():
                dest = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
                counter += 1

        with open(dest, "wb") as out:
            shutil.copyfileobj(upload.file, out)

        paper_id = dest.name
        title = dest.stem
        saved.append((paper_id, title, dest))
        job_items.append((paper_id, title, "upload"))

    job = create_job(job_items)
    background_tasks.add_task(_run_upload_job, job.id, saved)

    return {"job_id": job.id, **job_to_dict(job)}


@app.post("/api/papers/import")
def import_papers(body: ImportPapersRequest, background_tasks: BackgroundTasks) -> dict:
    titles = body.titles or {}
    items: list[tuple[str, str]] = []
    job_items: list[tuple[str, str, str]] = []

    for paper_id in body.paper_ids:
        title = titles.get(paper_id, paper_id)
        items.append((paper_id, title))
        job_items.append((paper_id, title, "search"))

    job = create_job(job_items)
    thread = threading.Thread(target=_run_import_job, args=(job.id, items), daemon=True)
    thread.start()

    return {"job_id": job.id, **job_to_dict(job)}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job)


def main() -> None:
    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    host = os.environ.get("SCHOLARSYNTH_API_HOST", "0.0.0.0")
    port = int(os.environ.get("SCHOLARSYNTH_API_PORT", "8080"))
    uvicorn.run("scholarsynth.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
