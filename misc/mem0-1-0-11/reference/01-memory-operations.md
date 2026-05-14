# Memory Operations

## Add Memory

Adding memory captures useful details from conversations for later retrieval. Mem0 extracts structured facts via an LLM (default `infer=True`) or stores raw messages (`infer=False`).

### Platform API

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

messages = [
    {"role": "user", "content": "I'm planning a trip to Tokyo next month."},
    {"role": "assistant", "content": "Great! I'll remember that for future suggestions."}
]

result = client.add(messages, user_id="alice")
```

### Open Source

```python
from mem0 import Memory

m = Memory()

# Store inferred memories (default)
result = m.add(messages, user_id="alice", metadata={"category": "travel"})

# Store raw messages without inference
result = m.add(messages, user_id="alice", infer=False)
```

### JavaScript SDK

```javascript
import { MemoryClient } from "mem0ai";

const client = new MemoryClient({ apiKey: "your-api-key" });

await client.add(messages, { user_id: "alice" });
```

### Key Parameters

- `messages` — Ordered list of `{role, content}` turns (string or dict or list accepted)
- `user_id` — Scope memory to a specific user
- `agent_id` — Scope memory to a specific agent
- `app_id` — Scope memory to a specific application
- `run_id` / `session_id` — Scope to a session or run
- `metadata` — Optional key-value filters for retrieval
- `infer` — Whether to extract structured memories (default `True`). Set `False` for raw storage.
- `enable_graph` — Enable graph relationship extraction (Platform)
- `async_mode` — Process asynchronously (default `True` in v1.0+)

### Important Notes

- Duplicate protection only runs during conflict resolution when `infer=True`. Raw inserts (`infer=False`) skip this check.
- Mixing `infer=True` and `infer=False` for the same fact will save it twice.
- Platform writes with both `user_id` and `agent_id` persist as separate records per entity — each record carries exactly one primary entity.

## Search Memory

Search converts natural language queries into vector embeddings, finds similar memories, ranks by similarity score, and optionally reranks.

### Platform API

```python
results = client.search(
    "What do you know about me?",
    filters={"user_id": "alice"}
)

# With advanced retrieval options
results = client.search(
    query="What foods should I avoid?",
    keyword_search=True,   # Expand to include exact keyword matches
    rerank=True,            # Reorder by semantic relevance
    user_id="alice"
)
```

### Open Source

```python
# Simple search
results = m.search("What do you know about me?", user_id="alice")

# Search with filters
results = m.search(
    "food preferences",
    user_id="alice",
    filters={"categories": {"contains": "diet"}}
)

# Search with reranking
results = m.search(
    "travel plans",
    user_id="alice",
    limit=5,
    rerank=True
)
```

### Response Format

```json
{
  "results": [
    {
      "id": "mem_123abc",
      "memory": "Name is Alex. Enjoys basketball and gaming.",
      "user_id": "alex",
      "categories": ["personal_info"],
      "created_at": "2025-10-22T04:40:22.864647-07:00",
      "score": 0.89
    }
  ]
}
```

When graph memory is enabled, results include a `relations` array with related entities.

### Search Parameters

- `query` — Natural language question or statement
- `filters` — JSON logic with AND/OR operators (Platform) or field filters (OSS)
- `limit` / `top_k` — Maximum number of results
- `threshold` — Minimum similarity score
- `rerank` — Enable reranker pass for better precision
- `keyword_search` — Expand to include exact keyword matches

### Platform vs OSS Search Differences

- **Platform**: Filters use logical operators (`AND`, `OR`, comparisons) with field-level access. Reranking via `rerank=True`.
- **OSS**: Basic field filters, extendable via Python hooks. Reranking requires configuring a reranker provider.

## Update Memory

Update modifies existing memory content or metadata without deleting the record.

### Platform API

```python
# Single update
client.update(
    memory_id="your_memory_id",
    text="Updated memory content about the user",
    metadata={"category": "profile-update"},
    timestamp="2025-01-15T12:00:00Z"
)

# Batch update (up to 1000 memories)
update_memories = [
    {"memory_id": "id1", "text": "Watches football"},
    {"memory_id": "id2", "text": "Likes to travel"}
]
response = client.batch_update(update_memories)
```

### Open Source

```python
memory.update(
    memory_id="mem_123",
    data="Alex now prefers decaf coffee"
)
```

### Notes

- Update both `text` and `metadata` together to keep filters accurate.
- Immutable memories must be deleted and re-added instead of updated.
- OSS JavaScript SDK does not expose `update` yet — use REST API or Python SDK.

## Delete Memory

Delete removes memories individually, in bulk, or by filter.

### Platform API

```python
# Single delete
client.delete(memory_id="your_memory_id")

# Batch delete (up to 1000)
delete_memories = [
    {"memory_id": "id1"},
    {"memory_id": "id2"}
]
response = client.batch_delete(delete_memories)

# Delete by filter
client.delete_all(user_id="alice")
client.delete_all(agent_id="support-bot")
client.delete_all(run_id="session-xyz")

# Wildcard: delete all memories across every user
client.delete_all(user_id="*")
```

### Open Source

```python
# Single delete
m.delete(memory_id="mem_123", user_id="alice")

# Delete all for a user
m.delete_all(user_id="alice")
```

### Breaking Change (v1.0)

`delete_all` now **raises an error** if called with no filters. Previously it wiped all project memories. Use `"*"` wildcards for intentional bulk deletion.

## Get All Memories

Retrieve all memories, optionally filtered by entity identifiers.

### Platform API

```python
# Requires filters in v1.0+
all_memories = client.get_all(filters={"user_id": "alice"})
```

### Open Source

```python
all_memories = m.get_all(user_id="alice")
```

## Memory History

Track changes to individual memories for auditing.

```python
# Platform
history = client.history(memory_id="mem_123")

# OSS
history = m.history(memory_id="mem_123", user_id="alice")
```
