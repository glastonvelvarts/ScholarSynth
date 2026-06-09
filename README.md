# scholarsynth

scholarsynth is a research paper RAG (Retrieval-Augmented Generation) system that enables users to upload one or more research papers, generate embeddings, store them in a vector database, and perform semantic retrieval over the uploaded documents.

## Current Pipeline

```text
PDF
 ↓
pdf_reader.py
 ↓
chunker.py
 ↓
embedder.py (BGE-M3)
 ↓
Milvus
 ↓
Semantic Search
```

## Features

* PDF Extraction using PyMuPDF
* Custom Chunking Pipeline
* BGE-M3 Embeddings
* Milvus Vector Database
* HNSW Indexing
* Cosine Similarity Search
* GPU Acceleration (CUDA)
* Docker-based Deployment

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
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
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

### 🚧 Next Steps

* Semantic Retrieval
* Query Embeddings
* Top-K Search
* Multi-PDF Comparison
* Session-Based Isolation
* Reranking
* LLM Integration
* Citation Generation

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
