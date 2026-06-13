# scholarsynth

scholarsynth is a research paper RAG (Retrieval-Augmented Generation) system that enables users to upload one or more research papers, generate embeddings, store them in a vector database, and perform semantic retrieval over the uploaded documents.

## Current Pipeline

```text
PDF
 ↓
pdf_reader.py            # column-aware text + table extraction (PyMuPDF)
 ↓
chunker.py               # semantic chunking + typed chunks
                         #   prose | table | reference | metadata
                         # citations preserved separately
 ↓
embedder.py (BGE-M3)     # embeds citation-stripped text
 ↓
Milvus (HNSW, COSINE)    # vector store + typed metadata
 ↓
retrieval/retriever.py   # dense ANN -> CrossEncoder rerank
                         #   + chunk-type filter
                         #   + low-confidence gating
```

## Features

* Column-aware PDF extraction with table detection (markdown output)
* Semantic sentence-boundary chunking, not fixed character windows
* Typed chunks: prose / table / reference / metadata
* Citation extraction — embeddings use clean text, originals kept for display
* BGE-M3 dense embeddings (multilingual, 1024-dim, normalized)
* Optional BGE-Reranker-v2-m3 cross-encoder rerank
* Low-confidence threshold returns "no match" instead of misleading top hits
* Configurable query instruction prefix (for E5 / jina / older BGE models)
* Milvus 2.5 (HNSW, COSINE) with strict schema
* GPU acceleration when CUDA is available

---

## Project Structure

```text
scholarsynth/
│
├── chunked_data/
│   └── chunked.json
│
├── embedded_data/
│   └── embedded_chunks.json
│
├── outputs/
│
├── scholarsynth/
│   ├── pdf_reader.py
│   ├── page_extractor.py
│   ├── text_cleaner.py
│   ├── chunker.py
│   ├── embedder.py
│   │
│   └── vectorstore/
│       ├── client.py
│       ├── schema.py
│       └── ingest.py
│
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<username>/scholarsynth.git
cd scholarsynth
```

### Install Dependencies

```bash
uv sync
```

Or install packages manually:

```bash
uv add pymupdf
uv add sentence-transformers
uv add pymilvus
uv add torch
```

---

## PDF Extraction

Run the PDF reader:

```bash
uv run python -m scholarsynth.pdf_reader <pdf_file>
```

Example:

```bash
uv run python -m scholarsynth.pdf_reader Automating_Customer_Service_Using_Langchain.pdf
```

Output:

```text
outputs/
└── Automating_Customer_Service_Using_Langchain.pdf.json
```

---

## Chunk Documents

Generate chunks from extracted documents:

```bash
uv run python -m scholarsynth.chunker
```

Output:

```text
chunked_data/
└── chunked.json
```

Default Configuration:

```python
DEFAULT_MAX_CHUNK_CHARS = 1500     # hard cap per chunk
DEFAULT_MIN_CHUNK_CHARS = 200      # merge small chunks under this
DEFAULT_BREAKPOINT_PERCENTILE = 90 # split where embedding distance is in the top 10%
```

Each chunk also stores:

```python
{
  "chunk_type": "prose" | "table" | "reference" | "metadata",
  "text":            "...",           # original text (for display)
  "text_clean":      "...",           # citation-stripped (for embedding)
  "citations":       ["[1]", "(Smith, 2020)"],
  "table_markdown":  "| Model | F1 |\n| ...",  # only for tables
  "section":         "IV. RESULTS",
  "page": 3, "page_end": 4
}
```

---

## Generate Embeddings

Embedding Model:

```text
BAAI/bge-m3
```

Generate embeddings:

```bash
uv run python -m scholarsynth.embedder
```

Output:

```text
embedded_data/
└── embedded_chunks.json
```

GPU acceleration is automatically enabled when CUDA is available.

---

## Start Milvus

Launch Milvus using Docker Compose:

```bash
docker compose up -d
```

Verify running containers:

```bash
docker ps
```

Expected containers:

```text
milvus-standalone
milvus-etcd
milvus-minio
```

---

## Ingest Embeddings into Milvus

Insert generated embeddings into the vector database:

```bash
uv run python -m scholarsynth.vectorstore.ingest
```

Example Output:

```text
Connected to Milvus
Created collection 'papersynth'
Inserted 18 chunks successfully
Collection now contains 18 entities
```

---

## Milvus Configuration

### Collection

```text
papersynth
```

### Schema

```text
chunk_id
document_name
page
text
embedding
```

### Embedding Dimension

```text
1024
```

### Similarity Metric

```text
COSINE
```

### Index Type

```text
HNSW
```

---

## Current Status

### ✅ Completed

* PDF Extraction
* Document Chunking
* Embedding Generation
* Milvus Integration
* Vector Ingestion

### ✅ Recently Added

* Table-aware PDF extraction
* Semantic sentence-boundary chunking
* Typed chunks (prose / table / reference / metadata)
* Citation extraction and preservation
* CrossEncoder reranking
* Low-confidence gating

### 🚧 Next Steps

* Hybrid retrieval (BM25 + dense fusion)
* Multi-PDF comparison and session isolation
* LLM answer synthesis with citation attribution
* Reference resolution: `[1]` → full bibliographic entry
* Migrate Milvus stack to single-node Qdrant for simpler ops

## Retrieval Configuration

```python
from scholarsynth.retrieval.retriever import retrieve, RetrievalConfig

response = retrieve(
    query="how were the models evaluated?",
    config=RetrievalConfig(
        top_k=5,
        candidate_k=20,             # candidates fetched before rerank
        score_threshold=0.45,       # dense score under this -> "no match"
        rerank=True,                # BGE-reranker-v2-m3 cross-encoder
        exclude_chunk_types=("metadata",),
        document_filter=None,       # or "Some_Paper.pdf"
    ),
)

if not response.confident:
    print(response.message)        # honest "not found" instead of garbage
for chunk in response.results:
    print(chunk.chunk_type, chunk.page, chunk.text[:120])
```

Environment overrides:

```bash
export SCHOLARSYNTH_MILVUS_URI=http://localhost:19530
export SCHOLARSYNTH_QUERY_PREFIX=""           # set for E5/jina models
export SCHOLARSYNTH_SCORE_THRESHOLD=0.45
export SCHOLARSYNTH_RERANK=1                  # 0 to disable
```

## Resetting the Index

The Milvus schema changed (new `chunk_type`, `table_markdown`, `page_end`,
`section` fields). After pulling these changes:

```bash
uv run python -m scholarsynth.vectorstore.drop_collection
docker compose restart milvus-standalone     # optional, only if cache is stale
uv run python -m scholarsynth.pdf_reader <pdf>
uv run python -m scholarsynth.chunker
uv run python -m scholarsynth.embedder
uv run python -m scholarsynth.vectorstore.ingest
```

---

## Technology Stack

* Python
* PyMuPDF
* Sentence Transformers
* BAAI BGE-M3
* Milvus
* Docker
* PyTorch
* UV Package Manager

---

## License

This project is licensed under the MIT License.
