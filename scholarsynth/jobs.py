"""In-memory job tracker for async paper processing."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PaperJobItem:
    id: str
    title: str
    status: str = "pending"
    error: Optional[str] = None
    page_count: Optional[int] = None
    source: str = "upload"


@dataclass
class ProcessingJob:
    id: str
    status: str = "pending"
    step: str = "idle"
    papers: list[PaperJobItem] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


_lock = threading.Lock()
_jobs: dict[str, ProcessingJob] = {}


def create_job(paper_titles: list[tuple[str, str, str]]) -> ProcessingJob:
    """Create a job. Each item is (id, title, source)."""
    job_id = uuid.uuid4().hex
    items = [PaperJobItem(id=pid, title=title, source=source) for pid, title, source in paper_titles]
    job = ProcessingJob(id=job_id, papers=items)
    with _lock:
        _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Optional[ProcessingJob]:
    with _lock:
        return _jobs.get(job_id)


def update_job_step(job_id: str, step: str) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job:
            job.step = step
            job.status = "processing"


def update_paper_status(
    job_id: str,
    paper_id: str,
    *,
    status: str,
    error: Optional[str] = None,
    page_count: Optional[int] = None,
) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        for paper in job.papers:
            if paper.id == paper_id:
                paper.status = status
                paper.error = error
                if page_count is not None:
                    paper.page_count = page_count
                break


def finish_job(job_id: str, *, error: Optional[str] = None) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.status = "error" if error else "completed"
        job.step = "ready" if not error else "error"
        job.error = error


def job_to_dict(job: ProcessingJob) -> dict:
    return {
        "id": job.id,
        "status": job.status,
        "step": job.step,
        "error": job.error,
        "papers": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "error": p.error,
                "page_count": p.page_count,
                "source": p.source,
            }
            for p in job.papers
        ],
    }
