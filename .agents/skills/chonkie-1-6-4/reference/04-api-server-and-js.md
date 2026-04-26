# API Server and JavaScript SDK

## Self-Hosted REST API

Run Chonkie as a self-hosted REST API for language-agnostic text chunking. No auth, no billing, no data leaving your infrastructure.

### Installation

```bash
pip install "chonkie[api,semantic,code,openai]"
```

The `api` extra includes FastAPI and uvicorn. Add `semantic` for the semantic chunker and `code` for the code chunker.

### Starting the Server

```bash
# Default (port 8000)
chonkie serve

# Custom port with auto-reload
chonkie serve --port 3000 --reload

# Debug logging
chonkie serve --log-level debug

# Direct uvicorn
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000
```

**Server options:**

- `--host` — Bind address. Default: `0.0.0.0`.
- `--port` — Port number. Default: `8000`.
- `--reload` — Auto-reload on file changes (development only).
- `--log-level` — Verbosity: `debug`, `info`, `warning`, `error`.

Visit `http://localhost:8000/docs` for Swagger UI or `/redoc` for ReDoc.

### API Endpoints

**Chunking endpoints:**

- `POST /v1/chunk/token` — Fixed-size token windows
- `POST /v1/chunk/sentence` — Sentence-boundary splitting
- `POST /v1/chunk/recursive` — Structural/hierarchical splitting
- `POST /v1/chunk/semantic` — Embedding-based semantic splitting
- `POST /v1/chunk/code` — AST-aware code splitting

**Refinery endpoints:**

- `POST /v1/refine/overlap` — Add overlap context to chunks
- `POST /v1/refine/embeddings` — Attach embeddings to chunks

**Pipeline management:**

- `POST /v1/pipelines` — Create a reusable pipeline
- `GET /v1/pipelines` — List all pipelines
- `GET /v1/pipelines/{id}` — Get a pipeline by ID
- `PUT /v1/pipelines/{id}` — Update a pipeline
- `DELETE /v1/pipelines/{id}` — Delete a pipeline
- `POST /v1/pipelines/{id}/execute` — Execute a pipeline on text

**Health:**

- `GET /health` — Health check
- `GET /` — API info and available endpoints

### Example Requests

**Token chunking:**

```bash
curl -X POST http://localhost:8000/v1/chunk/token \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Chonkie makes chunking easy. It splits text into manageable pieces.",
    "chunk_size": 20
  }'
```

**Response:**

```json
[
  {
    "text": "Chonkie makes chunking easy.",
    "start_index": 0,
    "end_index": 28,
    "token_count": 5
  },
  {
    "text": "It splits text into manageable pieces.",
    "start_index": 29,
    "end_index": 66,
    "token_count": 8
  }
]
```

**Semantic chunking:**

```bash
curl -X POST http://localhost:8000/v1/chunk/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dogs are loyal pets. Cats are independent. Quantum physics studies particles.",
    "embedding_model": "minishlab/potion-base-8M",
    "threshold": 0.5
  }'
```

**Recursive with recipe:**

```bash
curl -X POST http://localhost:8000/v1/chunk/recursive \
  -H "Content-Type: application/json" \
  -d '{
    "text": "# Heading\n\nParagraph one.\n\nParagraph two.",
    "chunk_size": 256,
    "recipe": "markdown"
  }'
```

**Batch processing** — Submit a list of strings instead of a single string to get back a list of lists (one inner list per input document).

### Pipeline Management via API

Create a reusable pipeline:

```bash
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag-chunker",
    "description": "Semantic chunking with embeddings for RAG",
    "steps": [
      {"type": "chunk", "chunker": "semantic", "config": {"chunk_size": 512, "threshold": 0.5}},
      {"type": "refine", "refinery": "embeddings", "config": {"embedding_model": "text-embedding-3-small"}}
    ]
  }'
```

Execute a pipeline:

```bash
curl -X POST http://localhost:8000/v1/pipelines/{pipeline_id}/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text here..."}'
```

Pipelines are stored in a local SQLite database.

### Docker Deployment

Quick start:

```bash
docker compose up
```

**docker-compose.yml:**

```yaml
services:
  chonkie-api:
    build:
      context: .
      dockerfile: Dockerfile
    image: chonkie-oss-api:latest
    container_name: chonkie-api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      LOG_LEVEL: "${LOG_LEVEL:-INFO}"
      CORS_ORIGINS: "${CORS_ORIGINS:-*}"
      DATABASE_URL: "sqlite+aiosqlite:////app/data/chonkie.db"
      OPENAI_API_KEY: "${OPENAI_API_KEY:-}"
      COHERE_API_KEY: "${COHERE_API_KEY:-}"
      VOYAGE_API_KEY: "${VOYAGE_API_KEY:-}"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
```

**Environment variables:**

- `LOG_LEVEL` — Log verbosity. Default: `INFO`.
- `CORS_ORIGINS` — Comma-separated allowed origins. Default: `*`.
- `DATABASE_URL` — SQLite database path. Default: `sqlite+aiosqlite:///./data/chonkie.db`.
- `OPENAI_API_KEY`, `COHERE_API_KEY`, `VOYAGE_API_KEY`, `MISTRAL_API_KEY` — API keys for embedding providers.

**Production tips:**
- Restrict CORS in production (replace `*` with actual domains)
- Add reverse proxy (Nginx/Caddy) for TLS termination
- Scale horizontally with multiple replicas behind a load balancer
- Send warm-up request after startup to avoid cold-start latency on SemanticChunker

## JavaScript SDK

Chonkie provides JavaScript packages for local chunking and API access.

### Installation

```bash
# Local chunking (Token, Sentence, Recursive, Fast, Table, Semantic, Code)
npm install @chonkiejs/core

# API client for cloud chunking
npm install @chonkiejs/cloud

# Custom tokenizers
npm install @chonkiejs/token
```

### Usage

```javascript
import { RecursiveChunker, TokenChunker, FastChunker } from "@chonkiejs/core";

// Recursive chunking
const chunker = await RecursiveChunker.create({
  chunkSize: 512,
  minCharactersPerChunk: 24,
});

const chunks = await chunker.chunk("Your text here...");

for (const chunk of chunks) {
  console.log(chunk.text);
  console.log(`Tokens: ${chunk.tokenCount}`);
}

// Token chunking with custom tokenizer
const tokenChunker = await TokenChunker.create({
  tokenizer: "gpt2",
  chunkSize: 1024,
  chunkOverlap: 128,
});

// Fast chunking (byte-based)
const fastChunker = await FastChunker.create({
  chunkSize: 4096,
  delimiters: "\n.?",
});

// Batch processing
const batchChunks = await chunker.chunkBatch(["Text 1", "Text 2"]);
```

### JavaScript Chunk Availability

**`@chonkiejs/core`** supports: TokenChunker, SentenceChunker, RecursiveChunker, FastChunker, TableChunker, SemanticChunker, CodeChunker.

**Not available locally in JS**: LateChunker, NeuralChunker, SlumberChunker (use API instead).

### Chunk Object (JavaScript)

```javascript
class Chunk {
  text: string;           // The chunk text
  startIndex: number;     // Starting index in original text
  endIndex: number;       // Ending index in original text
  tokenCount: number;     // Number of tokens
  embedding?: number[];   // Optional embedding vector
  toString(): string;     // String representation
}
```
