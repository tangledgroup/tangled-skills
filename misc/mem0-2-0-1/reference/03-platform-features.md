# Platform Features

## Essential Features

### V2 Memory Filters

Compound filters with AND/OR logic on metadata, entity, and time fields:

```python
results = client.search(
    "What does Alice like?",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"categories": {"in": ["preferences", "health"]}},
            {"created_at": {"$gte": "2025-01-01T00:00:00Z"}}
        ]
    }
)
```

### Entity-Scoped Memory

Partition memories by user, agent, app, or run:

```python
# User-scoped (long-lived)
client.add(messages, user_id="alice")

# Agent-scoped (per-agent persona)
client.add(messages, agent_id="travel-assistant")

# App-scoped (per product surface)
client.add(messages, app_id="mobile-app-v2")

# Run-scoped (short-lived session)
client.add(messages, user_id="alice", run_id="trip-planning-2025")
```

### Async Client

Non-blocking I/O for concurrent Mem0 calls:

```python
import asyncio
from mem0 import AsyncMemoryClient

client = AsyncMemoryClient(api_key="your-api-key")

async def main():
    await client.add(
        [{"role": "user", "content": "I love hiking"}],
        user_id="alice"
    )
    results = await client.search("hobbies", filters={"user_id": "alice"})
    print(results)

asyncio.run(main())
```

### Multimodal Support

Store images or PDFs as memory input alongside text:

```python
client.add(
    [
        {"role": "user", "content": [{"type": "text", "text": "Here's my receipt"}]},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "https://..."}}]}
    ],
    user_id="alice"
)
```

### Custom Categories

Define domain-specific memory categories beyond defaults:

```python
client.add(
    messages,
    user_id="alice",
    custom_categories=["medical_history", "medications", "allergies"]
)
```

## Advanced Retrieval

### Advanced Retrieval

Enable keyword search, reranking, and hybrid retrieval on Platform:

```python
results = client.search(
    "What medications does Alice take?",
    filters={"user_id": "alice"},
    enable_reranking=True,
    top_k=10
)
```

### Criteria-Based Retrieval

Target memories by custom criteria, not just semantic similarity:

```python
results = client.search(
    "recent travel plans",
    filters={
        "user_id": "alice",
        "categories": {"in": ["travel"]},
        "created_at": {"$gte": "2025-06-01T00:00:00Z"}
    }
)
```

### Contextual Add

Have `add()` consider the surrounding conversation, not just the latest turn:

```python
client.add(
    messages,
    user_id="alice",
    contextual=True  # considers full conversation context
)
```

### Custom Instructions

Tailor what Mem0 extracts and stores:

```python
client.add(
    messages,
    user_id="alice",
    instructions="Focus on medical information only. Ignore casual conversation."
)
```

## Data Management

### Direct Import

Seed a Mem0 project from existing data:

```python
client.import_memories(
    data=[
        {"memory": "Prefers vegetarian options", "user_id": "alice"},
        {"memory": "Allergic to shellfish", "user_id": "alice"},
    ]
)
```

### Memory Export

Export memories via a structured schema:

```python
export_job = client.create_export(user_id="alice")
results = client.get_export(export_job["id"])
```

### Timestamp Support

Temporal queries and time-based filtering:

```python
results = client.search(
    "preferences",
    filters={
        "user_id": "alice",
        "created_at": {
            "$gte": "2025-01-01T00:00:00Z",
            "$lte": "2025-12-31T23:59:59Z"
        }
    }
)
```

## Integration & Operations

### Webhooks

React to memory changes in real time:

```python
# Create a webhook
client.create_webhook(
    url="https://your-app.com/webhook",
    events=["memory.created", "memory.updated"]
)
```

### Feedback Mechanism

Capture user feedback to improve memory quality:

```python
client.feedback(memory_id="<id>", score=1.0, comment="Accurate memory")
```

### Group Chat Support

Handle conversations with multiple participants:

```python
client.add(
    messages,
    user_ids=["alice", "bob"],
    agent_id="group-chatbot"
)
```

### MCP Integration

Wire Mem0 into Claude Code, Cursor, and other MCP clients. The hosted MCP server is at `https://mcp.mem0.ai` and requires a Platform API key.

9 MCP tools available: `add_memory`, `search_memories`, `get_memories`, `get_memory`, `update_memory`, `delete_memory`, `delete_all_memories`, `delete_entities`, `list_entities`.

## Organizations & Projects (Platform)

Multi-tenant support with access control:

```python
# Create organization
client.create_organization(name="My Company")

# Create project within org
client.create_project(org_id="<org>", name="Customer Support Bot")

# Add members
client.add_member(project_id="<proj>", email="team@company.com", role="editor")
```
