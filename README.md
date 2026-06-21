# ScholarSynth

ScholarSynth is a full-stack research assistant: upload PDFs or import open-access papers from Semantic Scholar, index them in Milvus, and ask questions with **grounded answers and page-level citations** powered by dense retrieval + Modal-hosted vLLM.

```text
┌─────────────┐     /api/*      ┌──────────────────┐     Milvus      ┌─────────────┐
│  Frontend   │ ──────────────► │  FastAPI (8080)  │ ◄──────────────►│  Vector DB  │
│  Vite/React │                 │  scholarsynth.api│                 │  BGE-M3     │
└─────────────┘                 └────────┬─────────┘                 └─────────────┘
                                         │
                                         │  /v1/chat/completions
                                         ▼
                                ┌──────────────────┐
                                │  Modal + vLLM    │
                                │  Qwen2.5-Coder   │
                                │  (L40S GPU)      │
                                └──────────────────┘
```

---

## Features

### Ingestion
- Column-aware PDF extraction with table detection (PyMuPDF)
- Semantic sentence-boundary chunking (not fixed character windows)
- Typed chunks: `prose` | `table` | `reference` | `metadata`
- Citation extraction — embeddings use clean text; originals kept for display
- BGE-M3 dense embeddings (1024-dim, COSINE, HNSW in Milvus)
- Upload up to 10 PDFs via the web UI or API

### Retrieval
- Dense ANN search → BGE-Reranker-v2-m3 cross-encoder rerank
- Chunk-type filtering (metadata excluded by default)
- **Vectorless broad retrieval** for general synthesis queries (see below)
- Confidence score is informational — **never blocks LLM generation** when context exists

### Generation (RAG)
- Retrieved excerpts + user question sent to vLLM on Modal
- Separate system prompts for pinpoint Q&A vs cross-paper synthesis
- Inline citations as `[DocumentName, p.X]`
- Low-confidence retrieval still generates an answer from available context

### Paper Discovery
- Semantic Scholar search (`query.py` / `/api/search`)
- Import open-access PDFs directly into the workspace (`/api/papers/import`)
- Only downloads papers the user selects that have an available PDF

### Frontend
- React + Vite + Tailwind workspace UI
- Upload modal with live processing steps
- Chat panel with citation explorer
- Paper search page with filters (year, open-access)

---

## RAG Pipeline

```text
User question
     ↓
query_router.py          # general vs specific query?
     ↓
┌────────────────────────────────────────────────────────────┐
│  Specific query (e.g. "What F1 score was reported?")       │
│    → Milvus dense search (top_k=5, candidate_k=20)         │
│    → BGE reranker                                          │
├────────────────────────────────────────────────────────────┤
│  General query (e.g. "Summarize all uploaded papers")      │
│    → Milvus dense search (top_k=10, candidate_k=30)        │
│    → Vectorless broad retrieval (retrieve_broad)           │
│         samples early prose chunks from each document       │
│         without relying on query↔chunk similarity           │
│    → merge + dedupe chunks                                 │
└────────────────────────────────────────────────────────────┘
     ↓
generator.py             # build context prompt + call Modal vLLM
     ↓
Answer with citations
```

### Vectorless retrieval

General questions like *"Summarize all uploaded papers"* or *"Compare methodologies"* don't align well with dense vector similarity — the query is meta-level, not semantically close to any single chunk. ScholarSynth handles this with **`retrieve_broad()`** in `scholarsynth/retrieval/retriever.py`:

1. **`query_router.py`** detects general queries via keyword patterns (`summarize`, `compare`, `all papers`, `overview`, etc.).
2. **`retrieve_broad()`** fetches the first N prose chunks per indexed document ordered by page — no embedding search involved.
3. Broad chunks are **merged** with dense-retrieval results (deduped by `chunk_id`).
4. vLLM receives a wider, document-representative context and uses the **synthesis system prompt** (`RAG_SYNTHESIS_PROMPT`).

Confidence gating (`score_threshold=0.45`) still runs for logging and the `confident` API field, but **does not skip generation**. vLLM is only skipped when the index is completely empty.

### CLI

```bash
uv run python -m scholarsynth.rag.pipeline "Summarize all uploaded papers"
```

---

## Modal (vLLM)

Generation runs on **Modal** using **vLLM** with an OpenAI-compatible API.

| Setting | Default |
|---|---|
| App name | `scholarsynth-vllm` |
| GPU | NVIDIA L40S |
| HF model | `Qwen/Qwen2.5-Coder-7B-Instruct` |
| Served name | `qwen-coder-7b` |
| Port | 8000 (proxied by Modal web server) |

### Auth

Modal reads `~/.modal.toml`, not `.env`:

```bash
modal token set --token-id <MODAL_TOKEN_ID> --token-secret <MODAL_TOKEN_SECRET>
```

On WSL, if you see `\r` errors in headers, fix Windows line endings: `dos2unix .env`

### Deploy (persistent URL)

```bash
uv run modal deploy model.py
```

Output example:

```text
https://<workspace>--scholarsynth-vllm-serve.modal.run
```

Set in `.env`:

```bash
SCHOLARSYNTH_VLLM_BASE_URL=https://<workspace>--scholarsynth-vllm-serve.modal.run/v1
```

**Important:** the URL must include your workspace prefix (`<workspace>--`). A bare `scholarsynth-vllm-serve.modal.run` URL will 404.

### Dev (ephemeral URL)

```bash
uv run modal serve model.py
```

Updates `.env` with the printed URL each session.

### Stop / restart

```bash
uv run modal app list
uv run modal app stop scholarsynth-vllm      # stop containers
uv run modal deploy model.py               # redeploy
uv run modal app logs scholarsynth-vllm    # tail logs
```

First request after idle triggers a **cold start** (GPU spin-up + model load) and can take several minutes.

Override the HF model for research-focused Q&A:

```bash
export SCHOLARSYNTH_VLLM_HF_MODEL=Qwen/Qwen3-8B
export SCHOLARSYNTH_VLLM_SERVED_MODEL=qwen3-8b
uv run modal deploy model.py
```

---

## Quick Start (full stack)

### 1. Install

```bash
git clone https://github.com/<username>/scholarsynth.git
cd scholarsynth
uv sync
cd Frontend && npm install && cd ..
```

### 2. Environment

Create `.env` in the project root:

```bash
SCHOLAR_API_KEY=<your-semantic-scholar-key>
SCHOLARSYNTH_VLLM_BASE_URL=https://<workspace>--scholarsynth-vllm-serve.modal.run/v1
```

Optional:

```bash
SCHOLARSYNTH_MILVUS_URI=http://localhost:19530
SCHOLARSYNTH_SCORE_THRESHOLD=0.45
SCHOLARSYNTH_RERANK=1
SCHOLARSYNTH_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SCHOLARSYNTH_API_PORT=8080
```

### 3. Milvus

```bash
docker compose up -d
```

### 4. Modal vLLM

```bash
uv run modal deploy model.py
```

### 5. Run (two terminals)

**Terminal 1 — API:**

```bash
uv run python -m scholarsynth.api
# → http://0.0.0.0:8080
```

**Terminal 2 — Frontend:**

```bash
cd Frontend
npm run dev
# → http://localhost:5173  (proxies /api → :8080)
```

Open `http://localhost:5173`. Upload PDFs or search Semantic Scholar, then chat.

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/query` | RAG Q&A over indexed papers |
| `POST` | `/api/search` | Semantic Scholar paper search |
| `POST` | `/api/papers/upload` | Upload PDFs (multipart, max 10) |
| `POST` | `/api/papers/import` | Download + index open-access papers by ID |
| `GET` | `/api/papers` | List indexed documents |
| `GET` | `/api/jobs/{job_id}` | Poll upload/import processing status |

### Example: query

```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize all uploaded papers", "top_k": 5}'
```

### Example: search

```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Vision Transformers", "limit": 20, "years_back": 10}'
```

### Example: import paper

```bash
curl -X POST http://localhost:8080/api/papers/import \
  -H "Content-Type: application/json" \
  -d '{"paper_ids": ["<semantic-scholar-paper-id>"]}'
```

Upload/import jobs run in the background. Poll `/api/jobs/{job_id}` until `status` is `completed`.

---

## Offline / CLI Pipeline

For batch processing without the web UI:

```text
PDF
 ↓  pdf_reader.py
JSON document
 ↓  chunker.py
chunked_data/chunked.json
 ↓  embedder.py (BGE-M3)
embedded_data/embedded_chunks.json
 ↓  vectorstore/ingest.py
Milvus collection "papersynth"
```

```bash
uv run python read.py path/to/paper.pdf
uv run python -m scholarsynth.chunker
uv run python -m scholarsynth.embedder
uv run python -m scholarsynth.vectorstore.ingest
```

Semantic Scholar CSV export:

```bash
uv run python query.py "voice conversion using AI" --limit 100 -o results.csv
```

---

## Project Structure

```text
ScholarSynth/
├── Frontend/                  # React + Vite UI
│   └── src/
│       ├── components/        # Landing, Search, Workspace
│       └── lib/api.ts         # API client
├── scholarsynth/
│   ├── api.py                 # FastAPI server
│   ├── processing.py          # PDF → chunk → embed → ingest
│   ├── semantic_search.py     # Semantic Scholar search + PDF download
│   ├── jobs.py                # Background job tracker
│   ├── pdf_reader.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── rag/
│   │   ├── pipeline.py        # RAG orchestration
│   │   ├── generator.py       # vLLM answer synthesis
│   │   ├── query_router.py    # General vs specific query detection
│   │   ├── milvus_retriever.py
│   │   └── prompts.py
│   ├── retrieval/
│   │   └── retriever.py       # Dense + rerank + retrieve_broad (vectorless)
│   └── vectorstore/
├── model.py                   # Modal vLLM deployment
├── query.py                   # Semantic Scholar CLI
├── docker-compose.yml         # Milvus stack
├── pyproject.toml
└── .env
```

---

## Retrieval Configuration

```python
from scholarsynth.retrieval.retriever import retrieve, retrieve_broad, RetrievalConfig

# Specific factual query
response = retrieve(
    "how were the models evaluated?",
    config=RetrievalConfig(
        top_k=5,
        candidate_k=20,
        score_threshold=0.45,
        rerank=True,
        exclude_chunk_types=("metadata",),
    ),
)

# Vectorless broad sampling (used automatically for general queries)
broad = retrieve_broad(chunks_per_doc=3, max_total=12)
```

Environment overrides:

```bash
export SCHOLARSYNTH_MILVUS_URI=http://localhost:19530
export SCHOLARSYNTH_QUERY_PREFIX=""
export SCHOLARSYNTH_SCORE_THRESHOLD=0.45
export SCHOLARSYNTH_RERANK=1
export SCHOLARSYNTH_VLLM_SERVED_MODEL=qwen-coder-7b
export SCHOLARSYNTH_VLLM_TIMEOUT=120
```

---

## Milvus

| Setting | Value |
|---|---|
| Collection | `papersynth` |
| Metric | COSINE |
| Index | HNSW |
| Embedding dim | 1024 |

Schema fields: `chunk_id`, `document_name`, `page`, `page_end`, `section`, `chunk_type`, `text`, `citations`, `table_markdown`, `embedding`

### Reset index

```bash
uv run python tests/drop_collection.py
docker compose restart milvus-standalone
uv run python read.py <pdf>
uv run python -m scholarsynth.chunker
uv run python -m scholarsynth.embedder
uv run python -m scholarsynth.vectorstore.ingest
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Vite `ECONNREFUSED` on `/api/*` | Start the API: `uv run python -m scholarsynth.api` |
| `\r` in header / API key error | `.strip()` is applied in code; also run `dos2unix .env` |
| Modal 404 / invalid function call | URL missing workspace prefix — redeploy and copy full URL |
| Chat timeout on first query | Modal cold start — wait 2–5 min, retry |
| "No indexed documents" | Upload papers or run ingest pipeline; ensure Milvus is up |
| Import fails "No open-access PDF" | Paper is paywalled — upload the PDF manually instead |

---

## Technology Stack

| Layer | Tech |
|---|---|
| Frontend | React, Vite, Tailwind, Framer Motion |
| API | FastAPI, Uvicorn, python-multipart |
| Extraction | PyMuPDF |
| Embeddings | Sentence Transformers, BAAI/bge-m3 |
| Reranker | BAAI/bge-reranker-v2-m3 |
| Vector DB | Milvus 2.5 (Docker) |
| LLM serving | Modal, vLLM, Qwen2.5-Coder-7B-Instruct |
| RAG framework | LlamaIndex (retriever + OpenAILike LLM) |
| Paper search | Semantic Scholar API |
| Package manager | UV |

---

## License

MIT License
