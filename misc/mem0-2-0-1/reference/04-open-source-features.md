# Open Source Features

## Self-Hosted Server

The self-hosted bundle ships the REST API and a web dashboard together via Docker Compose.

### Bootstrap

```bash
cd server && make bootstrap   # stack + admin + first API key in one command
```

Or manual setup:

```bash
cd server && docker compose up -d    # http://localhost:3000
```

### Environment Variables

Copy `server/.env.example` to `server/.env` and fill required values:

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Default LLM and embedder provider |
| `JWT_SECRET` | Yes | Signs access and refresh tokens. Missing = 500 on auth endpoints |
| `ADMIN_API_KEY` | Optional | Legacy shared admin key. Prefer per-user keys for new setups |
| `AUTH_DISABLED` | Optional | `true` turns off auth for local dev only. Never in production |

### Auth (Default On)

Auth is on by default in v2. Pre-auth builds that relied on `ADMIN_API_KEY` or open endpoints will return 401 until you either set `ADMIN_API_KEY`, register an admin through the wizard, or set `AUTH_DISABLED=true` for local development.

## Enhanced Metadata Filtering

Filter by custom metadata fields in self-hosted deployments:

```python
m.add(messages, user_id="alice", metadata={"department": "engineering", "level": "senior"})

results = m.search(
    "expertise",
    filters={
        "user_id": "alice",
        "metadata": {
            "department": "engineering",
            "level": {"$gte": "senior"}
        }
    }
)
```

## Reranker-Enhanced Search

Improve OSS search quality with a reranker:

```python
config = {
    "llm": {"provider": "openai", "config": {"model": "gpt-5-mini"}},
    "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
    "reranker": {"provider": "cohere", "config": {"model": "rerank-english-v3.0"}},
}
memory = Memory.from_config(config)

results = memory.search("query", filters={"user_id": "alice"}, rerank=True)
```

## Async Memory

Non-blocking I/O for self-hosted apps:

```python
import asyncio
from mem0 import AsyncMemory

async def main():
    memory = AsyncMemory()

    await memory.add(
        [{"role": "user", "content": "I prefer dark mode"}],
        user_id="alice"
    )

    results = await memory.search("preferences", filters={"user_id": "alice"})
    print(results)

asyncio.run(main())
```

## Multimodal Support (OSS)

Handle images and PDFs in self-hosted deployments:

```python
m.add(
    [
        {"role": "user", "content": [{"type": "text", "text": "Here's my document"}]},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "https://example.com/receipt.png"}}]}
    ],
    user_id="alice"
)
```

## Custom Instructions (OSS)

Tailor extraction prompts in self-hosted mode:

```python
m.add(
    messages,
    user_id="alice",
    instructions="Focus on medical information only. Ignore casual conversation."
)
```

## REST API Server (OSS)

Expose self-hosted Mem0 as a FastAPI service:

```bash
cd server && docker compose up -d
# API at http://localhost:8888
# Dashboard at http://localhost:3000
```

The OSS server provides the same REST endpoints as the Platform for memory CRUD operations.

## OpenAI Compatibility

Hit an OpenAI-compatible endpoint with self-hosted Mem0:

```bash
curl http://localhost:8888/v1/chat/completions \
  -H "Authorization: Bearer $MEM0_API_KEY" \
  -d '{
    "model": "mem0-memory",
    "messages": [{"role": "user", "content": "What do you know about me?"}],
    "user_id": "alice"
  }'
```

## Quick Recovery

- **Qdrant connection errors** — Confirm port 6333 is exposed and API key matches.
- **Empty search results** — Verify the embedder model name; a mismatch causes dimension errors.
- **Unknown reranker** — Update the SDK (`pip install --upgrade mem0ai`).
- **spaCy model not found** — Run `python -m spacy download en_core_web_sm`.
- **Entity store collection creation fails** — Check vector store connectivity and permissions.
- **Score values different from before** — v2 uses multi-signal scoring (semantic + BM25 + entity). Scores are not directly comparable with v1.
