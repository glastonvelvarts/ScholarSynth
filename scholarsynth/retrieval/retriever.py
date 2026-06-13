"""Dense retrieval with optional cross-encoder reranking and confidence gating."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Sequence

from scholarsynth.vectorstore.constants import COLLECTION_NAME

logger = logging.getLogger(__name__)

MILVUS_URI = os.environ.get("SCHOLARSYNTH_MILVUS_URI", "http://localhost:19530")

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"

# BGE-M3 was trained without a query instruction, so the default prefix is empty.
# For E5 / jina / older BGE checkpoints, override via SCHOLARSYNTH_QUERY_PREFIX.
QUERY_PREFIX = os.environ.get("SCHOLARSYNTH_QUERY_PREFIX", "")

DEFAULT_OUTPUT_FIELDS = (
    "chunk_id",
    "document_name",
    "page",
    "page_end",
    "section",
    "chunk_type",
    "text",
    "citations",
    "table_markdown",
)


@dataclass(frozen=True)
class RetrievalConfig:
    """Tunable retrieval behavior."""

    top_k: int = 5
    candidate_k: int = 20
    score_threshold: float = 0.45
    rerank: bool = True
    exclude_chunk_types: tuple[str, ...] = ()
    document_filter: Optional[str] = None


@dataclass
class RetrievedChunk:
    """One result returned to callers."""

    chunk_id: str
    document_name: str
    page: int
    page_end: int
    section: Optional[str]
    chunk_type: str
    text: str
    citations: List[str]
    table_markdown: Optional[str]
    score: float
    rerank_score: Optional[float] = None


@dataclass
class RetrievalResponse:
    """Wraps results so callers can react to low-confidence states."""

    query: str
    results: List[RetrievedChunk]
    top_score: float
    confident: bool
    message: Optional[str] = None
    config: RetrievalConfig = field(default_factory=RetrievalConfig)


_EMBED_MODEL: Optional[Any] = None
_RERANK_MODEL: Optional[Any] = None
_CLIENT: Optional[Any] = None
_LOADED_COLLECTIONS: set[str] = set()


def _get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        import torch
        from sentence_transformers import SentenceTransformer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _EMBED_MODEL = SentenceTransformer(
            EMBEDDING_MODEL_NAME,
            trust_remote_code=True,
            device=device,
        )
        logger.info("Loaded embedding model %s on %s", EMBEDDING_MODEL_NAME, device)
    return _EMBED_MODEL


def _get_rerank_model():
    global _RERANK_MODEL
    if _RERANK_MODEL is None:
        import torch
        from sentence_transformers import CrossEncoder

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _RERANK_MODEL = CrossEncoder(RERANKER_MODEL_NAME, device=device)
        logger.info("Loaded reranker %s on %s", RERANKER_MODEL_NAME, device)
    return _RERANK_MODEL


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        from pymilvus import MilvusClient

        _CLIENT = MilvusClient(uri=MILVUS_URI)
        logger.info("Connected to Milvus at %s", MILVUS_URI)
    return _CLIENT


def _ensure_collection_loaded(client, collection_name: str) -> None:
    """MilvusClient.search requires the collection to be loaded into memory first."""
    if collection_name in _LOADED_COLLECTIONS:
        return

    if not client.has_collection(collection_name):
        raise RuntimeError(
            f"Collection '{collection_name}' does not exist. "
            "Run the ingest pipeline first."
        )

    try:
        state = client.get_load_state(collection_name)
        already_loaded = (
            str(state).lower().find("loaded") != -1
            and str(state).lower().find("notload") == -1
        )
    except Exception:
        already_loaded = False

    if not already_loaded:
        logger.info("Loading collection %s into memory", collection_name)
        client.load_collection(collection_name)

    _LOADED_COLLECTIONS.add(collection_name)


def embed_query(query: str, prefix: str = QUERY_PREFIX):
    """Embed a query string with an optional model-specific instruction prefix."""
    model = _get_embed_model()
    text = f"{prefix}{query}" if prefix else query
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding


def _build_filter_expr(
    exclude_chunk_types: Sequence[str],
    document_filter: Optional[str],
) -> Optional[str]:
    parts: list[str] = []
    if exclude_chunk_types:
        excluded = ", ".join(f'"{ct}"' for ct in exclude_chunk_types)
        parts.append(f"chunk_type not in [{excluded}]")
    if document_filter:
        parts.append(f'document_name == "{document_filter}"')
    return " and ".join(parts) if parts else None


def _search(
    query_embedding,
    limit: int,
    filter_expr: Optional[str],
) -> list[dict]:
    client = _get_client()
    _ensure_collection_loaded(client, COLLECTION_NAME)
    hits = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_embedding.tolist()],
        anns_field="embedding",
        search_params={"metric_type": "COSINE", "params": {"ef": 64}},
        limit=limit,
        filter=filter_expr or "",
        output_fields=list(DEFAULT_OUTPUT_FIELDS),
    )
    return hits[0] if hits else []


def _parse_citations(raw) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [str(raw)]
    return parsed if isinstance(parsed, list) else [str(parsed)]


def _hits_to_chunks(hits: Iterable[dict]) -> List[RetrievedChunk]:
    results: List[RetrievedChunk] = []
    for hit in hits:
        entity = hit.get("entity", hit)
        page = entity.get("page", 0)
        results.append(
            RetrievedChunk(
                chunk_id=entity.get("chunk_id", ""),
                document_name=entity.get("document_name", ""),
                page=int(page),
                page_end=int(entity.get("page_end", page) or page),
                section=entity.get("section") or None,
                chunk_type=entity.get("chunk_type") or "prose",
                text=entity.get("text", ""),
                citations=_parse_citations(entity.get("citations")),
                table_markdown=entity.get("table_markdown") or None,
                score=float(hit.get("distance", 0.0)),
            )
        )
    return results


def _rerank(query: str, candidates: List[RetrievedChunk], top_k: int) -> List[RetrievedChunk]:
    if not candidates:
        return candidates

    model = _get_rerank_model()
    pairs = [(query, chunk.text) for chunk in candidates]
    scores = model.predict(pairs)

    for chunk, score in zip(candidates, scores):
        chunk.rerank_score = float(score)

    return sorted(candidates, key=lambda c: c.rerank_score or 0.0, reverse=True)[:top_k]


def retrieve(query: str, config: Optional[RetrievalConfig] = None) -> RetrievalResponse:
    """
    Run dense retrieval with optional reranking and confidence gating.

    Flow:
        embed query (with optional prefix)
          -> Milvus ANN search (top candidate_k)
          -> optional cross-encoder rerank to top_k
          -> confidence check vs score_threshold
    """
    cfg = config or RetrievalConfig()
    logger.info("Retrieving documents for query: %s", query)

    query_embedding = embed_query(query)
    filter_expr = _build_filter_expr(cfg.exclude_chunk_types, cfg.document_filter)
    candidate_limit = max(cfg.candidate_k if cfg.rerank else cfg.top_k, cfg.top_k)

    hits = _search(query_embedding, candidate_limit, filter_expr)
    candidates = _hits_to_chunks(hits)

    if cfg.rerank and candidates:
        try:
            results = _rerank(query, candidates, cfg.top_k)
        except Exception as exc:
            logger.warning("Reranker failed, falling back to dense scores: %s", exc)
            results = candidates[: cfg.top_k]
    else:
        results = candidates[: cfg.top_k]

    top_score = max(
        (
            r.rerank_score if r.rerank_score is not None else r.score
            for r in results
        ),
        default=0.0,
    )

    # Reranker logits are unbounded, so only gate on dense score when rerank is off.
    gate_score = top_score if not cfg.rerank else (
        max((r.score for r in results), default=0.0)
    )
    confident = gate_score >= cfg.score_threshold

    message = None
    if not confident:
        message = (
            "No high-confidence match found in the indexed documents. "
            "The query may reference content that is not present "
            f"(top similarity {gate_score:.3f} < threshold {cfg.score_threshold:.2f})."
        )
        logger.info(message)

    return RetrievalResponse(
        query=query,
        results=results,
        top_score=float(gate_score),
        confident=confident,
        message=message,
        config=cfg,
    )


def _format_page(chunk: RetrievedChunk) -> str:
    return (
        str(chunk.page)
        if chunk.page == chunk.page_end
        else f"{chunk.page}-{chunk.page_end}"
    )


def _print_response(response: RetrievalResponse) -> None:
    if response.message:
        print(f"\n[low-confidence] {response.message}\n")

    for idx, chunk in enumerate(response.results, start=1):
        print("=" * 100)
        print(f"Result {idx}  ({chunk.chunk_type})")
        score_line = f"Dense: {chunk.score:.4f}"
        if chunk.rerank_score is not None:
            score_line += f"  |  Rerank: {chunk.rerank_score:.4f}"
        print(score_line)
        print(f"Document: {chunk.document_name}")
        print(f"Page: {_format_page(chunk)}")
        if chunk.section:
            print(f"Section: {chunk.section}")
        if chunk.citations:
            print(f"Citations: {', '.join(chunk.citations)}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print()
        if chunk.chunk_type == "table" and chunk.table_markdown:
            print(chunk.table_markdown[:800])
        else:
            print(chunk.text[:600])
        print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    query = input("\nQuestion: ").strip()
    if not query:
        print("Empty query, exiting.")
        raise SystemExit(0)

    config = RetrievalConfig(
        top_k=5,
        candidate_k=20,
        rerank=os.environ.get("SCHOLARSYNTH_RERANK", "1") == "1",
        exclude_chunk_types=("metadata",),
        score_threshold=float(
            os.environ.get("SCHOLARSYNTH_SCORE_THRESHOLD", "0.45")
        ),
    )

    response = retrieve(query, config=config)
    _print_response(response)
