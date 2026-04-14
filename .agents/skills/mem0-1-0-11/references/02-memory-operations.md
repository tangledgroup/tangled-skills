# Mem0 Memory Operations

Complete guide to CRUD operations for memories including add, search, update, delete, and history tracking.

## Add Memory

Store conversation context or facts for later retrieval.

### Basic Usage

```python
from mem0 import Memory

memory = Memory()

messages = [
    {"role": "user", "content": "I'm planning a trip to Tokyo next month."},
    {"role": "assistant", "content": "Great! I'll remember that for future suggestions."}
]

# Add with automatic fact extraction (default)
result = memory.add(messages, user_id="alice")
print(result)  # {'memory_id': 'mem_abc123', ...}
```

### With Metadata

```python
result = memory.add(
    messages=messages,
    user_id="alice",
    agent_id="travel-assistant",
    metadata={"category": "travel_plans"}
)
```

### Platform API vs OSS Differences

| Parameter | Platform API | Open Source |
|-----------|--------------|-------------|
| User scoping | `filters={"user_id": "alice"}` | `user_id="alice"` parameter |
| Authentication | `MemoryClient(api_key=...)` | Environment variables |

```python
# Platform API
from mem0 import MemoryClient
client = MemoryClient(api_key="your-api-key")
client.add(messages, user_id="alice")  # Same interface

# OSS
from mem0 import Memory
memory = Memory()
memory.add(messages, user_id="alice")
```

### Inference Control

**Automatic extraction (default):**
```python
result = memory.add(messages, user_id="alice", infer=True)
# Mem0 extracts structured facts from conversation
```

**Raw storage (no inference):**
```python
result = memory.add(messages, user_id="alice", infer=False)
# Stores messages exactly as provided
```

<Warning>
Using `infer=False` skips conflict resolution. The same fact stored with `infer=True` later will create a duplicate memory instead of updating the existing one.
</Warning>

### Batch Add

```python
async def batch_add_memories(memory, conversations):
    tasks = [
        memory.add(conv["messages"], user_id=conv["user_id"])
        for conv in conversations
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Search Memory

Retrieve relevant memories using semantic search.

### Basic Search

```python
results = memory.search(
    query="Where is Alice traveling?",
    user_id="alice"
)

print(results)
# {
#   "results": [
#     {
#       "id": "mem_abc123",
#       "memory": "Alice is planning a trip to Tokyo next month",
#       "user_id": "alice",
#       "score": 0.89,
#       "created_at": "2025-01-15T10:30:00Z"
#     }
#   ]
# }
```

### With Filters

**OSS (parameter-based):**
```python
results = memory.search(
    query="What are Alice's preferences?",
    user_id="alice",
    agent_id="diet-assistant",
    run_id="session-123"
)
```

**Platform API (logical filters):**
```python
results = client.search(
    query="preferences",
    filters={
        "OR": [
            {"user_id": "alice"},
            {"agent_id": {"in": ["diet-assistant", "health-coach"]}}
        ]
    }
)
```

### Advanced Filters (Platform API)

**Date range filtering:**
```python
results = client.search(
    query="recent preferences",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"created_at": {"gte": "2024-01-01T00:00:00Z"}}
        ]
    }
)
```

**Category filtering:**
```python
results = client.search(
    query="food preferences",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"categories": {"contains": "diet"}}
        ]
    }
)
```

### Search Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | 10 | Number of results to return |
| `threshold` | 0.0 | Minimum similarity score (0-1) |
| `rerank` | True | Enable reranker if configured |
| `filters` | None | Filter expressions |

```python
results = memory.search(
    query="travel plans",
    user_id="alice",
    top_k=5,              # Return top 5 results
    threshold=0.7         # Minimum 70% similarity
)
```

### Context-Aware Search

```python
def get_relevant_context(memory, query, user_id, conversation_history):
    """Search with conversation context for better relevance."""
    
    # Enrich query with recent conversation
    enriched_query = f"{query}\n\nRecent context: {conversation_history[-3:]}"
    
    results = memory.search(
        query=enriched_query,
        user_id=user_id,
        top_k=3
    )
    
    return results["results"]
```

## Get All Memories

List all memories with optional scoping.

### Basic Listing

```python
# All memories for a user
all_memories = memory.get_all(user_id="alice")

print(all_memories)
# {
#   "memories": [
#     {"id": "...", "memory": "...", "user_id": "alice"},
#     ...
#   ]
# }
```

### Scoped Listing

```python
# By user and agent
agent_memories = memory.get_all(
    user_id="alice",
    agent_id="travel-assistant"
)

# By session (run_id)
session_memories = memory.get_all(
    user_id="alice",
    run_id="consultation-001"
)

# All three scopes
specific_memories = memory.get_all(
    user_id="alice",
    agent_id="travel-assistant",
    run_id="consultation-001"
)
```

### Pagination (Platform API)

```python
results = client.get_all(
    filters={"user_id": "alice"},
    limit=20,
    offset=0
)

# Paginate through results
offset = 0
all_memories = []
while True:
    batch = client.get_all(
        filters={"user_id": "alice"},
        limit=100,
        offset=offset
    )
    if not batch["memories"]:
        break
    all_memories.extend(batch["memories"])
    offset += 100
```

## Get Single Memory

Retrieve a specific memory by ID.

```python
memory_doc = memory.get(memory_id="mem_abc123")

print(memory_doc)
# {
#   "id": "mem_abc123",
#   "memory": "Alice prefers vegetarian food",
#   "user_id": "alice",
#   "categories": ["diet"],
#   "created_at": "2025-01-15T10:30:00Z",
#   "updated_at": "2025-01-20T14:22:00Z"
# }
```

Error handling:
```python
try:
    memory_doc = memory.get(memory_id="non-existent-id")
except ValueError as e:
    print(f"Memory not found: {e}")
```

## Update Memory

Modify existing memory content.

### Direct Update

```python
updated = memory.update(
    memory_id="mem_abc123",
    data="Alice prefers vegetarian food and is allergic to peanuts"
)

print(updated)
# {"id": "mem_abc123", "memory": "...", "updated_at": "..."}
```

### Conditional Update

```python
def update_if_relevant(memory, memory_id, new_content, threshold=0.8):
    """Update only if content is significantly different."""
    
    current = memory.get(memory_id=memory_id)
    current_embedding = memory._embed(current["memory"])
    new_embedding = memory._embed(new_content)
    
    similarity = cosine_similarity(current_embedding, new_embedding)
    
    if similarity < threshold:
        return memory.update(memory_id=memory_id, data=new_content)
    else:
        print("Content too similar, skipping update")
        return current
```

## Delete Memory

Remove memories individually or in bulk.

### Single Deletion

```python
result = memory.delete(memory_id="mem_abc123")
print(result)  # {"status": "deleted", "memory_id": "mem_abc123"}
```

### Bulk Deletion by Scope

```python
# Delete all memories for a user
result = memory.delete_all(user_id="alice")

# Delete all memories for an agent
result = memory.delete_all(agent_id="travel-assistant")

# Delete all memories from a session
result = memory.delete_all(run_id="session-123")

# Combined scope (most specific)
result = memory.delete_all(
    user_id="alice",
    agent_id="travel-assistant"
)
```

<Warning>
`delete_all` requires at least one scope filter (`user_id`, `agent_id`, or `run_id`). Calling without filters will raise an error.
</Warning>

### Conditional Deletion

```python
def delete_old_memories(memory, user_id, cutoff_date):
    """Delete memories older than a specific date."""
    
    all_memories = memory.get_all(user_id=user_id)
    
    for mem in all_memories["memories"]:
        if mem["created_at"] < cutoff_date:
            memory.delete(memory_id=mem["id"])
            
    print(f"Deleted old memories for {user_id}")
```

## Memory History

Audit trail of memory changes.

### Get History

```python
history = memory.history(memory_id="mem_abc123")

print(history)
# {
#   "memory_id": "mem_abc123",
#   "changes": [
#     {
#       "timestamp": "2025-01-15T10:30:00Z",
#       "action": "created",
#       "content": "Alice prefers vegetarian food"
#     },
#     {
#       "timestamp": "2025-01-20T14:22:00Z",
#       "action": "updated",
#       "old_content": "Alice prefers vegetarian food",
#       "new_content": "Alice prefers vegetarian food and is allergic to peanuts"
#     }
#   ]
# }
```

### Compliance Use Case

```python
def generate_audit_report(memory, user_id, start_date, end_date):
    """Generate compliance report for memory changes."""
    
    all_memories = memory.get_all(user_id=user_id)
    report = []
    
    for mem in all_memories["memories"]:
        if start_date <= mem["created_at"] <= end_date:
            history = memory.history(memory_id=mem["id"])
            report.append({
                "memory_id": mem["id"],
                "current_content": mem["memory"],
                "change_history": history["changes"]
            })
    
    return report
```

## Error Handling

### Common Errors

```python
from mem0 import Memory

memory = Memory()

# Handle invalid memory ID
try:
    memory.get(memory_id="invalid-id")
except ValueError as e:
    print(f"Memory not found: {e}")

# Handle empty search query
try:
    memory.search(query="", user_id="alice")
except ValueError as e:
    print(f"Invalid query: {e}")

# Handle delete_all without scope
try:
    memory.delete_all()  # Missing required filter
except ValueError as e:
    print(f"Scope required: {e}")
```

### Retry Logic for Operations

```python
import asyncio
from functools import wraps

def retry_memory_operation(max_retries=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

@retry_memory_operation(max_retries=3)
async def robust_add(memory, messages, user_id):
    return await memory.add(messages, user_id=user_id)
```

## Best Practices

1. **Always scope with user_id** - Prevents cross-user memory contamination
2. **Use metadata for categorization** - Enables better filtering later
3. **Keep inference enabled** - Automatic extraction prevents duplicates
4. **Set appropriate top_k** - Don't fetch more memories than needed
5. **Use history for debugging** - Track why memories changed
6. **Batch operations when possible** - Reduce API calls with asyncio.gather

## Performance Tips

- **Index by scope** - Vector stores perform better with scoped queries
- **Cache frequent searches** - Memoize results for repeated queries
- **Tune similarity threshold** - Higher threshold = fewer but more relevant results
- **Use rerankers selectively** - Reranking adds latency but improves precision
- **Batch deletes carefully** - Delete in chunks to avoid timeouts
