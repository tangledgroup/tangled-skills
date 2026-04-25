# API Server Guide

## Overview

Chonkie can run as a self-hosted REST API server, providing endpoints for all chunkers, refineries, and pipelines. The API is built on Catsu framework and supports multi-provider embeddings.

## Installation

```bash
# Install with API dependencies
pip install "chonkie[api,semantic,code,catsu]"

# Or minimal installation
pip install "chonkie[api]"
```

## Quick Start

### Using CLI

```bash
# Start the server with default settings
chonkie serve

# Custom port
chonkie serve --port 3000

# Enable auto-reload for development
chonkie serve --reload

# Set log level
chonkie serve --log-level debug

# All options combined
chonkie serve --host 0.0.0.0 --port 8000 --reload --log-level info
```

### Using Uvicorn Directly

```bash
# Basic uvicorn command
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000

# With reload for development
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000 --reload

# With workers for production
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Clone repository
git clone https://github.com/chonkie-inc/chonkie.git
cd chonkie

# Start with docker compose
docker compose up

# Server runs on http://localhost:8000
```

## API Endpoints

Interactive documentation is available at `/docs` (Swagger UI) when the server is running.

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.6.2"
}
```

### Chunking Endpoints

#### Token Chunker

```bash
curl -X POST http://localhost:8000/v1/chunk/token \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "tokenizer": "gpt2"
  }'
```

Response:
```json
{
  "chunks": [
    {
      "text": "First chunk of text...",
      "token_count": 480,
      "start_index": 0,
      "end_index": 312
    },
    {
      "text": "Second chunk with overlap...",
      "token_count": 450,
      "start_index": 262,
      "end_index": 598
    }
  ]
}
```

#### Recursive Chunker

```bash
curl -X POST http://localhost:8000/v1/chunk/recursive \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document...",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "tokenizer": "gpt2",
    "separators": ["\n\n", "\n", " ", ""]
  }'
```

#### Semantic Chunker

```bash
curl -X POST http://localhost:8000/v1/chunk/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document...",
    "chunk_size": 1024,
    "threshold": 0.8,
    "similarity_window": 3,
    "embedding_model": "minishlab/potion-base-32M"
  }'
```

#### Code Chunker

```bash
curl -X POST http://localhost:8000/v1/chunk/code \
  -H "Content-Type: application/json" \
  -d '{
    "text": "def hello():\n    print('Hello')",
    "language": "python",
    "chunk_size": 512,
    "chunk_overlap": 50
  }'
```

### Pipeline Endpoints

#### Create Pipeline

```bash
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag-chunker",
    "steps": [
      {
        "type": "chunk",
        "chunker": "semantic",
        "config": {
          "chunk_size": 512,
          "threshold": 0.8
        }
      },
      {
        "type": "refine",
        "refinery": "overlap",
        "config": {
          "context_size": 100
        }
      },
      {
        "type": "refine",
        "refinery": "embeddings",
        "config": {
          "embedding_model": "text-embedding-3-small"
        }
      }
    ]
  }'
```

Response:
```json
{
  "id": "pipeline_123",
  "name": "rag-chunker",
  "steps": [...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### List Pipelines

```bash
curl http://localhost:8000/v1/pipelines
```

Response:
```json
{
  "pipelines": [
    {
      "id": "pipeline_123",
      "name": "rag-chunker",
      "step_count": 3
    },
    {
      "id": "pipeline_456",
      "name": "code-processor",
      "step_count": 2
    }
  ]
}
```

#### Execute Pipeline

```bash
curl -X POST http://localhost:8000/v1/pipelines/pipeline_123/execute \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text..."
  }'
```

#### Delete Pipeline

```bash
curl -X DELETE http://localhost:8000/v1/pipelines/pipeline_123
```

### Embedding Endpoints

#### Generate Embeddings

```bash
curl -X POST http://localhost:8000/v1/embed \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "model": "minishlab/potion-base-32M"
  }'
```

Response:
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 512
}
```

#### Batch Embeddings

```bash
curl -X POST http://localhost:8000/v1/embed/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["text1", "text2", "text3"],
    "model": "minishlab/potion-base-32M"
  }'
```

Response:
```json
{
  "embeddings": [
    [0.123, -0.456, ...],
    [0.456, -0.789, ...],
    [0.789, -0.012, ...]
  ],
  "dimension": 512
}
```

### Available Chunkers via API

All chunkers available in Chonkie can be accessed via API:

| Endpoint | Chunker | Description |
|----------|---------|-------------|
| `/v1/chunk/token` | TokenChunker | Fixed-size token chunks |
| `/v1/chunk/fast` | FastChunker | SIMD-accelerated byte chunking |
| `/v1/chunk/sentence` | SentenceChunker | Sentence-level chunking |
| `/v1/chunk/recursive` | RecursiveChunker | Hierarchical chunking |
| `/v1/chunk/semantic` | SemanticChunker | Semantic similarity chunking |
| `/v1/chunk/late` | LateChunker | Late chunking algorithm |
| `/v1/chunk/code` | CodeChunker | AST-based code chunking |
| `/v1/chunk/neural` | NeuralChunker | BERT-based chunking |
| `/v1/chunk/slumber` | SlumberChunker | LLM-based agentic chunking |
| `/v1/chunk/table` | TableChunker | Markdown table chunking |

## Configuration

### Environment Variables

```bash
# Server configuration
export CHONKIE_API_HOST=0.0.0.0
export CHONKIE_API_PORT=8000
export CHONKIE_API_LOG_LEVEL=info  # debug, info, warning, error

# Embedding providers
export OPENAI_API_KEY=your-key
export COHERE_API_KEY=your-key
export JINA_API_KEY=your-key

# Vector databases (if using handshakes)
export QDRANT_URL=http://localhost:6333
export PINECONE_API_KEY=your-key
```

### Custom Configuration File

Create `chonkie_config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8000
  log_level: info
  workers: 4

embeddings:
  default_model: minishlab/potion-base-32M
  providers:
    openai:
      api_key: ${OPENAI_API_KEY}
      models:
        - text-embedding-3-small
        - text-embedding-3-large
    cohere:
      api_key: ${COHERE_API_KEY}
      models:
        - embed-english-v3.0

chunkers:
  default_chunk_size: 512
  default_overlap: 50
```

Start with config:
```bash
chonkie serve --config chonkie_config.yaml
```

## Python Client

Use the API from Python:

```python
import requests

# Chunk text
response = requests.post(
    "http://localhost:8000/v1/chunk/recursive",
    json={
        "text": "Your document...",
        "chunk_size": 512,
        "chunk_overlap": 50
    }
)
chunks = response.json()["chunks"]

# Create pipeline
response = requests.post(
    "http://localhost:8000/v1/pipelines",
    json={
        "name": "my-pipeline",
        "steps": [
            {
                "type": "chunk",
                "chunker": "semantic",
                "config": {"chunk_size": 512, "threshold": 0.8}
            }
        ]
    }
)
pipeline_id = response.json()["id"]

# Execute pipeline
response = requests.post(
    f"http://localhost:8000/v1/pipelines/{pipeline_id}/execute",
    json={"text": "Your document..."}
)
result = response.json()
```

## JavaScript/TypeScript Client

```javascript
// Chunk text
const response = await fetch("http://localhost:8000/v1/chunk/recursive", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    text: "Your document...",
    chunk_size: 512,
    chunk_overlap: 50
  })
});

const { chunks } = await response.json();
console.log(chunks);

// Create pipeline
const pipelineResponse = await fetch("http://localhost:8000/v1/pipelines", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    name: "my-pipeline",
    steps: [
      {
        type: "chunk",
        chunker: "semantic",
        config: { chunk_size: 512, threshold: 0.8 }
      }
    ]
  })
});

const { id: pipelineId } = await pipelineResponse.json();

// Execute pipeline
const executeResponse = await fetch(
  `http://localhost:8000/v1/pipelines/${pipelineId}/execute`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: "Your document..." })
  }
);

const result = await executeResponse.json();
```

## Production Deployment

### Using Docker Compose

```yaml
version: '3.8'

services:
  chonkie-api:
    image: chonkie-inc/chonkie:1.6.2
    ports:
      - "8000:8000"
    environment:
      - CHONKIE_API_HOST=0.0.0.0
      - CHONKIE_API_PORT=8000
      - CHONKIE_API_LOG_LEVEL=info
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./pipelines:/app/pipelines  # Persist pipelines
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage
    restart: unless-stopped
```

### Using Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chonkie-config
data:
  CHONKIE_API_HOST: "0.0.0.0"
  CHONKIE_API_PORT: "8000"
  CHONKIE_API_LOG_LEVEL: "info"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chonkie-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chonkie-api
  template:
    metadata:
      labels:
        app: chonkie-api
    spec:
      containers:
      - name: chonkie
        image: chonkie-inc/chonkie:1.6.2
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: chonkie-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: chonkie-api
spec:
  selector:
    app: chonkie-api
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## Rate Limiting

Configure rate limiting in production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute", "1000 per hour"]
)

@app.post("/v1/chunk/recursive")
@limiter.limit("50 per minute")
async def chunk_recursive(request: ChunkRequest):
    # Your chunking logic
    pass
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.6.2",
  "uptime_seconds": 3600,
  "requests_processed": 1234,
  "active_pipelines": 5
}
```

### Metrics Endpoint (Prometheus)

```bash
curl http://localhost:8000/metrics
```

## Troubleshooting

### Port Already in Use

```bash
# Change port
chonkie serve --port 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill
```

### Missing Dependencies

```bash
# Install all API dependencies
pip install "chonkie[api,semantic,code,catsu]"

# Verify installation
python -c "from chonkie.api.main import app; print('API ready')"
```

### Pipeline Not Found

Ensure pipeline was created successfully:

```bash
# List all pipelines
curl http://localhost:8000/v1/pipelines

# Create new pipeline if needed
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "steps": [{"type": "chunk", "chunker": "recursive", "config": {}}]}'
```

### Embedding Model Not Available

Install required dependencies:

```bash
# For Model2Vec
pip install "chonkie[semantic]"

# For OpenAI embeddings
pip install "chonkie[openai]"

# For SentenceTransformers
pip install "chonkie[st]"
```

## Best Practices

1. **Use pipelines for complex workflows**: Store reusable configurations in the database
2. **Enable rate limiting**: Prevent abuse in production
3. **Monitor health checks**: Use `/health` endpoint for load balancer health checks
4. **Persist pipelines**: Mount volume for pipeline storage in Docker
5. **Use environment variables**: Never hardcode API keys
6. **Enable logging**: Set appropriate log level for debugging
7. **Scale horizontally**: Use multiple workers or replicas for high throughput
