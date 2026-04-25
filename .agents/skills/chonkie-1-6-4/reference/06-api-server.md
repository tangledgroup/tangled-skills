# API Server

> **Source:** https://docs.chonkie.ai/oss/api/overview
> **Loaded from:** SKILL.md (via progressive disclosure)

Chonkie can run as a self-hosted REST API server built on FastAPI. No auth, no billing, no data leaving your infrastructure.

## Quick Start

```bash
# Install with API dependencies
pip install "chonkie[api,semantic,code,catsu]"

# Start the server
chonkie serve

# Custom options
chonkie serve --port 3000 --reload --log-level debug

# Or directly with uvicorn
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000
```

Interactive Swagger UI available at `http://localhost:8000/docs`.

## Docker Deployment

```bash
docker compose up
```

## Available Endpoints

### Chunkers

- `POST /v1/chunk/token` — Fixed-size token windows
- `POST /v1/chunk/sentence` — Sentence-boundary splitting
- `POST /v1/chunk/recursive` — Structural/hierarchical splitting
- `POST /v1/chunk/semantic` — Embedding-based semantic splitting
- `POST /v1/chunk/code` — AST-aware code splitting

### Refineries

- `POST /v1/refine/overlap` — Add overlap context to chunks
- `POST /v1/refine/embeddings` — Attach embeddings to chunks

### Pipelines

- `POST /v1/pipelines` — Create a reusable pipeline
- `GET /v1/pipelines` — List all pipelines
- `GET /v1/pipelines/{id}` — Get pipeline by ID
- `PUT /v1/pipelines/{id}` — Update a pipeline
- `DELETE /v1/pipelines/{id}` — Delete a pipeline
- `POST /v1/pipelines/{id}/execute` — Execute pipeline on text

### Utilities

- `GET /health` — Health check
- `GET /` — API info and available endpoints

## Usage Examples

### Token Chunking

```bash
curl -X POST http://localhost:8000/v1/chunk/token \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here...",
    "chunk_size": 512,
    "chunk_overlap": 50
  }'
```

### Recursive Chunking

```bash
curl -X POST http://localhost:8000/v1/chunk/recursive \
  -H "Content-Type: application/json" \
  -d '{
    "text": "# Heading\n\nParagraph one.\n\nParagraph two.",
    "chunk_size": 256,
    "recipe": "markdown"
  }'
```

### Semantic Chunking

```bash
curl -X POST http://localhost:8000/v1/chunk/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dogs are loyal pets. Cats are independent. Quantum physics studies particles.",
    "embedding_model": "minishlab/potion-base-8M",
    "threshold": 0.5
  }'
```

### Batch Processing

Submit a list of strings instead of a single string to get back a list of lists — one inner list per input document:

```bash
curl -X POST http://localhost:8000/v1/chunk/token \
  -H "Content-Type: application/json" \
  -d '{
    "text": ["First document...", "Second document..."],
    "chunk_size": 512
  }'
```

### Create A Pipeline

```bash
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag-chunker",
    "steps": [
      {"type": "chunk", "chunker": "semantic", "config": {"chunk_size": 512}},
      {"type": "refine", "refinery": "embeddings", "config": {"embedding_model": "text-embedding-3-small"}}
    ]
  }'
```

### Execute A Pipeline

```bash
curl -X POST http://localhost:8000/v1/pipelines/rag-chunker/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "Document to process..."}'
```

## Response Format

All chunking endpoints return a list of chunk objects:

```json
[
  {
    "text": "chunk content",
    "start_index": 0,
    "end_index": 42,
    "token_count": 8
  }
]
```

## Why Use The API

- **Language-agnostic**: Call from JavaScript, Go, Ruby, or any HTTP client
- **Self-hosted**: Data never leaves your infrastructure
- **Full feature parity**: All Chonkie chunkers and refineries over HTTP
- **Batch support**: Chunk multiple documents in a single request
- **No auth required**: Run it and chunk away
- **Reusable pipelines**: Save workflows in SQLite, execute by ID
