# API Server and JavaScript SDK

## Self-Hosted REST API

Chonkie can run as a self-hosted REST API server, providing endpoints for all chunkers, refineries, and pipelines. Pipeline configurations are persisted in a local SQLite database.

### Installation

```bash
pip install "chonkie[api,semantic,code,catsu]"
```

The `catsu` extra provides multi-provider embedding support for the API server.

### Starting the Server

Via CLI:

```bash
# Default settings
chonkie serve

# Custom options
chonkie serve --port 3000 --reload --log-level debug
```

Via uvicorn directly:

```bash
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
docker compose up
```

The repository includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

### API Endpoints

**Chunking**: POST requests to chunk text using any supported chunker.

```bash
# Chunk with recursive chunker
curl -X POST http://localhost:8000/v1/chunk/recursive \
  -H "Content-Type: application/json"
  -d '{"text": "Your document text here...", "chunk_size": 512}'
```

**Pipelines**: Create, list, and execute reusable pipeline configurations stored in SQLite.

```bash
# Create a reusable pipeline
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json"
  -d '{
    "name": "rag-chunker",
    "steps": [
      {"type": "chunk", "chunker": "semantic", "config": {"chunk_size": 512}},
      {"type": "refine", "refinery": "embeddings", "config": {"embedding_model": "text-embedding-3-small"}}
    ]
  }'

# List pipelines
curl http://localhost:8000/v1/pipelines
```

Interactive Swagger/OpenAPI documentation is available at `/docs` when the server is running.

Full API documentation: [docs.chonkie.ai/api](https://docs.chonkie.ai/api)

## JavaScript SDK

Chonkie provides JavaScript packages for local chunking and cloud API access.

### @chonkiejs/core

Local chunking with TokenChunker and RecursiveChunker support.

```bash
npm install @chonkiejs/core
```

```javascript
import { RecursiveChunker } from "@chonkiejs/core";

// Create a chunker
const chunker = await RecursiveChunker.create({
  chunkSize: 512,
  minCharactersPerChunk: 24,
});

// Chunk text
const chunks = await chunker.chunk("Your document text here...");

for (const chunk of chunks) {
  console.log(chunk.text);
  console.log(`Tokens: ${chunk.tokenCount}`);
}
```

**Chunk type in JavaScript**:

```javascript
class Chunk {
  text: string;
  startIndex: number;
  endIndex: number;
  tokenCount: number;
  embedding?: number[];
  toString(): string;
}
```

### @chonkiejs/token

Custom tokenizer support for JavaScript.

```bash
npm install @chonkiejs/token
```

```javascript
import { TokenChunker } from "@chonkiejs/core";

const chunker = await TokenChunker.create({
  tokenizer: "gpt2",
  chunkSize: 2048,
  chunkOverlap: 512
});
```

### @chonkiejs/cloud

Client for the Chonkie cloud API.

```bash
npm install @chonkiejs/cloud
```

Use this package to access all chunkers (including semantic, code, neural) through the Chonkie API when local installation is not feasible.

## CLI

Chonkie includes a command-line interface for serving and managing the API server:

```bash
chonkie serve                    # Start API server
chonkie serve --port 3000        # Custom port
chonkie serve --reload           # Auto-reload on code changes
chonkie serve --log-level debug  # Debug logging
```

## Performance Benchmarks

Chonkie benchmarks against LangChain and LlamaIndex on 100K Wikipedia articles (Google Colab A100):

**Token Chunking**: Chonkie 58s vs LangChain 70s vs LlamaIndex 50 min (33x faster than slowest)

**Sentence Chunking**: Chonkie 59s vs LlamaIndex 239s (4x faster)

**Recursive Chunking**: Chonkie 79s vs LangChain 165s (2x faster)

**Semantic Chunking**: Chonkie 839s default settings vs LangChain 3693s vs LlamaIndex 4875s

**Package Size**: Chonkie 15 MB base install vs LangChain 80 MB vs LlamaIndex 171 MB (5–11x lighter)

With semantic features: Chonkie 62 MB vs LangChain 625 MB vs LlamaIndex 678 MB (10–11x lighter)
