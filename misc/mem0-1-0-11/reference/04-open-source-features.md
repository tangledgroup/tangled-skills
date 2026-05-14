# Open Source Features

## Overview

Mem0 OSS delivers the same adaptive memory engine as the platform, packaged for teams that need full infrastructure control. Key differentiators:

- **Full control**: Tune every component — LLMs, vector stores, embedders, rerankers
- **Offline ready**: Keep memory on your own network
- **Extendable codebase**: Fork, add providers, ship custom automations
- **No vendor lock-in**: Own your data, providers, and pipelines

## Graph Memory (Self-Hosted)

Graph Memory persists nodes and edges alongside embeddings. On retrieval, vector search narrows candidates while the graph returns related context in the `relations` array.

### Supported Graph Backends

- Neo4j (including Neo4j Aura free tier)
- Memgraph
- Neptune Analytics
- Kuzu
- Apache AGE

### Quickstart with Neo4j

```bash
pip install "mem0ai[graph]"
```

```python
import os
from mem0 import Memory

config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": os.environ["NEO4J_URL"],
            "username": os.environ["NEO4J_USERNAME"],
            "password": os.environ["NEO4J_PASSWORD"],
            "database": "neo4j",
        }
    }
}

memory = Memory.from_config(config)

conversation = [
    {"role": "user", "content": "Alice met Bob at GraphConf 2025 in San Francisco."},
    {"role": "assistant", "content": "Great! Logging that connection."},
]

memory.add(conversation, user_id="demo-user")

results = memory.search(
    "Who did Alice meet at GraphConf?",
    user_id="demo-user",
    limit=3,
    rerank=True,
)

for hit in results["results"]:
    print(hit["memory"])
```

## Async Memory

`AsyncMemory` provides non-blocking memory operations for Python async applications (FastAPI, background workers, asyncio workflows).

```python
import asyncio
from mem0 import AsyncMemory

memory = AsyncMemory()

# Add memories concurrently
async def batch_operations():
    tasks = [
        memory.add(
            messages=[{"role": "user", "content": f"Message {i}"}],
            user_id=f"user_{i}"
        )
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Method parity with synchronous API
await memory.add(messages, user_id="alice")
await memory.search("query", user_id="alice")
await memory.get_all(user_id="alice")
await memory.get(memory_id="mem_123")
await memory.update(memory_id="mem_123", data="updated content")
await memory.delete(memory_id="mem_123")
await memory.delete_all(user_id="alice")
await memory.history(memory_id="mem_123")
```

### Lifecycle Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_memory():
    memory = AsyncMemory()
    try:
        yield memory
    finally:
        pass  # Clean up resources if needed

async def safe_usage():
    async with get_memory() as memory:
        return await memory.search("test", user_id="alice")
```

## REST API Server

Mem0 OSS exposes a FastAPI-powered REST layer for language-agnostic access.

### Run with Docker Compose

```bash
cd server
docker compose up
```

API available at `http://localhost:8888`. OpenAPI docs at `/docs`.

### Run with Docker

```bash
docker pull mem0/mem0-api-server
docker run -p 8000:8000 --env-file .env mem0-api-server
```

### Run Directly

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Authentication

Set `ADMIN_API_KEY` in `.env` to require `X-API-Key` header on all endpoints.

| `ADMIN_API_KEY` | Behavior |
|---|---|
| Not set / empty | All endpoints open (no auth) |
| Non-empty string | Requests must include `X-API-Key: <key>` |

### Key Endpoints

- `POST /memories` — Add memories
- `GET /memories` — List memories
- `POST /memories/search` — Search memories
- `PUT /memories/{memory_id}` — Update memory
- `DELETE /memories/{memory_id}` — Delete memory

**Note**: OSS server does **not** use `/v1/` prefix. Platform API uses `/v1/memories/`.

## Metadata Filtering

Filter memories using custom metadata fields attached during `add`.

```python
# Add with metadata
m.add(messages, user_id="alice", metadata={"category": "travel", "priority": "high"})

# Search with filters
results = m.search(
    "vacation plans",
    user_id="alice",
    filters={"categories": {"contains": "travel"}}
)
```

## Multimodal Support (OSS)

Same as Platform — add images via URLs or base64-encoded local files. Images processed through vision model, extracted facts stored as standard searchable memories.

```python
from mem0 import Memory

client = Memory()

messages = [
    {"role": "user", "content": "Hi, my name is Alice."},
    {
        "role": "user",
        "content": {
            "type": "image_url",
            "image_url": {"url": "https://example.com/menu.jpg"}
        }
    }
]

client.add(messages, user_id="alice")
```

## Custom Fact Extraction Prompt

Tailor how Mem0 extracts information from conversations.

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.1
        }
    },
    "custom_extraction_prompt": """Extract key facts about user preferences,
    focusing on dietary restrictions and medical conditions."""
}

memory = Memory.from_config(config)
```

## Custom Update Memory Prompt

Customize how memories are updated and merged when new information arrives.

```python
config = {
    "custom_update_memory_prompt": """When updating memories, always preserve
    the most recent version of conflicting facts. Merge complementary
    information rather than replacing."""
}

memory = Memory.from_config(config)
```

## OpenAI Compatibility

Seamless integration with OpenAI-compatible APIs. Configure any OpenAI-compatible endpoint:

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": "your-key",
            "base_url": "http://localhost:8080/v1",  # Custom endpoint
            "model": "your-model"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": "your-key",
            "base_url": "http://localhost:8080/v1",
            "model": "your-embedding-model"
        }
    }
}

memory = Memory.from_config(config)
```

## Reranker-Enhanced Search (OSS)

Add a second scoring pass after vector retrieval for better precision.

```python
from mem0 import Memory

config = {
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "api_key": "your-cohere-api-key"
        }
    }
}

m = Memory.from_config(config)

# Search with reranking enabled
results = m.search("travel plans", user_id="alice", rerank=True)
```

Confirm `results["results"][0]["score"]` reflects the reranker output — if missing, the reranker was not applied.
