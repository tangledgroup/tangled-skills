# Memory Operations

## Add Memory

The `add()` operation stores information from conversations for later retrieval.

### How It Works (v2)

1. **Information extraction** — Mem0 sends messages through an LLM that pulls out key facts, decisions, or preferences in a single pass. No UPDATE/DELETE during extraction.
2. **Conflict resolution** — Existing memories are checked for duplicates or contradictions; latest truth wins.
3. **Storage** — Memories land in vector storage with entity embeddings for future retrieval.

### Parameters

- `messages` — Required. List of `{role, content}` dicts or a string. Cannot be None.
- `user_id` / `agent_id` / `app_id` — Entity identifiers passed as top-level kwargs on `add()`.
- `run_id` — Short-lived session identifier for temporary context.
- `metadata` — Optional dict for custom filters (e.g., `{"category": "movie_recommendations"}`).
- `infer` — Controls whether Mem0 extracts structured memories (`True`, default) or stores raw messages (`False`). With `infer=False`, duplicates will land since conflict resolution is skipped.

### Platform Example

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

messages = [
    {"role": "user", "content": "I'm planning a trip to Tokyo next month."},
    {"role": "assistant", "content": "Great! I'll remember that for future suggestions."}
]

result = client.add(messages, user_id="alice")
# Returns memory_id (or list of IDs)
```

### OSS Example

```python
from mem0 import Memory

m = Memory()

messages = [
    {"role": "user", "content": "I prefer boutique hotels."},
    {"role": "assistant", "content": "Noted!"}
]

result = m.add(messages, user_id="alex", run_id="trip-planning-2025")
```

### When to Add Memory

- After every meaningful conversation turn where new facts are revealed
- When user preferences, goals, or feedback are expressed
- Before generating responses that should inform future interactions
- Not on every single message — add when there is extractable information

## Search Memory

The `search()` operation retrieves relevant memories using multi-signal hybrid search.

### How It Works (v2)

1. **Query processing** — Natural-language query is cleaned and enriched.
2. **Multi-signal retrieval** — Semantic embeddings, BM25 keyword matching, and entity matching run in parallel.
3. **Filtering & reranking** — Logical filters narrow candidates; optional reranker fine-tunes ordering.
4. **Results delivery** — Formatted memories with metadata, timestamps, and categories return.

### Parameters (v2)

- `query` — Required. Natural-language question or statement.
- `filters` — Required for scoping. Dict with entity IDs: `{"user_id": "alice"}`. Top-level kwargs for entity IDs now raise `ValueError`.
- `top_k` — Number of results to return. Default changed from 100 to **20**. Pass `top_k=100` explicitly to restore old behavior.
- `threshold` — Minimum similarity score. Default changed from None (no filtering) to **0.1**. Must be in `[0, 1]`. Pass `threshold=0.0` for old behavior.
- `rerank` — Optional reranker pass. Default changed from `True` to **`False`**. Pass `rerank=True` to restore.

### Platform Example

```python
results = client.search(
    "What are Alice's hobbies?",
    filters={"user_id": "alice"},
    top_k=5,
    threshold=0.15
)

# Results format:
# {
#   "results": [
#     {
#       "id": "uuid",
#       "memory": "Allergic to nuts",
#       "user_id": "user123",
#       "categories": ["health"],
#       "created_at": "2025-10-22T04:40:22.864647-07:00",
#       "score": 0.30
#     }
#   ]
# }
```

### OSS Example

```python
results = m.search(
    "What does Alice like to do?",
    filters={"user_id": "alice"},
    top_k=3
)
```

### Filter Patterns

Always provide at least a `user_id` filter to scope searches. This prevents cross-contamination between users.

Platform supports compound logical filters:

```python
filters = {
    "OR": [
        {"user_id": "alice"},
        {"agent_id": {"in": ["travel-assistant", "customer-support"]}}
    ]
}
```

### Tips for Better Search

- Use natural language queries, not keywords alone — semantic matching works best with full sentences
- Keep `top_k` between 5-20 for most use cases
- Set a reasonable `threshold` (0.1-0.3) to filter low-relevance results
- Add metadata during `add()` to enable filtering during `search()`

## Get All Memories

Retrieve all memories for an entity.

```python
# Platform
all_memories = client.get_all(user_id="alice")

# OSS (v2: entity IDs inside filters)
all_memories = m.get_all(filters={"user_id": "alex"})
```

## Get Single Memory

Fetch one memory by ID.

```python
memory = client.get(memory_id="<id>")
# or
memory = m.get(memory_id="<id>")
```

## Update Memory

Modify existing memory content in place.

```python
client.update(memory_id="<id>", data="Alice loves mountain hiking")
m.update(memory_id="<id>", data="Updated fact here")
```

In v2, update is handled through the conflict resolution step during `add()` rather than as a separate extraction pass. The `update()` API remains available for direct edits.

## Delete Memory

Remove specific memories or batch delete operations.

```python
# Single delete
client.delete(memory_id="<id>")
m.delete(memory_id="<id>")

# Batch delete by entity
client.delete_all(user_id="alice")
m.delete_all(user_id="alex")
```

### When to Delete

- Outdated preferences that no longer apply
- User requests to forget specific information
- Privacy compliance (GDPR, data deletion requests)
- Cleaning up test or development data

## Platform vs OSS Differences

| Capability | Mem0 Platform | Mem0 OSS |
|---|---|---|
| Entity IDs on search/get_all | Inside `filters` dict | Inside `filters` dict (aligned in v2) |
| Filter syntax | Logical operators (AND/OR) | Basic filters + enhanced metadata filtering |
| Reranker | Built-in, no config needed | Optional, requires provider setup |
| Entity linking | Automatic | Requires NLP extras (`mem0ai[nlp]`) |
| BM25 keyword search | Built-in | Requires NLP extras |
| Dashboard | Yes (app.mem0.ai) | Yes (self-hosted at :3000) |
| Webhooks | Supported | Not available |
| Async client | `AsyncMemoryClient` | `AsyncMemory` |
