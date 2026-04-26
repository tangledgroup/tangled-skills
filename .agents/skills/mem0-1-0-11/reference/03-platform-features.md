# Platform Features

## Graph Memory

Graph Memory builds a network of interconnected entities for contextually relevant retrieval. It runs alongside vector search — vector returns top semantic matches, graph adds related entities in the `relations` array without reordering hits.

### Enable Graph Memory

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

messages = [
    {"role": "user", "content": "My name is Joseph"},
    {"role": "assistant", "content": "Hello Joseph!"},
    {"role": "user", "content": "I'm from Seattle and work as a software engineer"}
]

client.add(messages, user_id="joseph", enable_graph=True)
```

The response includes graph relations alongside vector results.

## Entity-Scoped Memory

Mem0 separates memories by entity identifiers to prevent cross-contamination between users, agents, apps, and sessions.

### Entity Dimensions

- `user_id` — Persistent persona or account (e.g., `"customer_6412"`)
- `agent_id` — Distinct agent persona (e.g., `"meal_planner"`)
- `app_id` — White-label app or product surface (e.g., `"ios_retail_demo"`)
- `run_id` — Short-lived flow or session (e.g., `"ticket-9241"`)

### Example

```python
messages = [
    {"role": "user", "content": "I teach ninth-grade algebra."},
    {"role": "assistant", "content": "I'll tailor study plans to algebra topics."}
]

client.add(
    messages,
    user_id="teacher_872",
    agent_id="study_planner",
    app_id="district_dashboard",
    run_id="prep-period-2025-09-02"
)
```

### Important: Implicit Null Scoping

When you create a memory with only `user_id="alice"`, the other fields default to `null`. Searching with `{"AND": [{"user_id": "alice"}, {"agent_id": "bot"}]}` returns nothing because no memory has `agent_id="bot"`. Use `OR` to combine scopes or search per-entity.

Platform writes with both `user_id` and `agent_id` persist as **separate records per entity** — each record carries exactly one primary entity for privacy boundaries.

## Async Client

`AsyncMemoryClient` provides non-blocking operations for high-concurrency Python applications.

```python
import os
from mem0 import AsyncMemoryClient

os.environ["MEM0_API_KEY"] = "your-api-key"
client = AsyncMemoryClient()

# Add asynchronously
messages = [
    {"role": "user", "content": "Alice loves playing badminton"},
    {"role": "assistant", "content": "That's great!"}
]
await client.add(messages, user_id="alice")

# Search asynchronously
results = await client.search("What is Alice's favorite sport?", user_id="alice")

# Get all (requires filters in v1.0+)
all_memories = await client.get_all(filters={"user_id": "alice"})
```

## Async Mode Default Change

In v1.0+, `async_mode` defaults to `True` for all `add` operations. This provides better performance for most use cases. Set `async_mode=False` only if you need synchronous processing guarantees.

```python
# Explicit async mode
client.add(messages, user_id="alice", async_mode=True)   # default
client.add(messages, user_id="alice", async_mode=False)  # synchronous
```

## Multimodal Support

Mem0 extracts facts from images alongside text. Supports JPEG, PNG, WebP, and GIF (max 20 MB).

### From URLs

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

### Local Images as Base64

```python
import base64

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

base64_image = encode_image("path/to/image.jpg")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
        ]
    }
]

client.add(messages, user_id="alice")
```

## Custom Categories

Replace default memory tags with domain-specific labels at the project level. Default catalog: `personal_details`, `family`, `professional_details`, `sports`, `travel`, `food`, `music`, `health`, `technology`, `hobbies`, `fashion`, `entertainment`, `milestones`, `user_preferences`, `misc`.

```python
from mem0 import MemoryClient

client = MemoryClient()

new_categories = [
    {"lifestyle_management_concerns": "Tracks daily routines, habits, hobbies"},
    {"seeking_structure": "Goals around creating routines and schedules"},
    {"personal_information": "Basic info including name, preferences"}
]

response = client.project.update(custom_categories=new_categories)

# Confirm active catalog
categories = client.project.get(fields=["custom_categories"])
```

## Advanced Retrieval

Enhance search beyond basic semantic similarity.

### Keyword Search

Expands results to include memories with specific terms, names, and technical keywords.

```python
results = client.search(
    query="What foods should I avoid?",
    keyword_search=True,
    user_id="user123"
)
```

- **Latency**: ~10ms additional
- **Recall**: Significantly increased
- **Precision**: Slightly decreased

### Reranking

Reorders results using deep semantic understanding.

```python
results = client.search(
    query="What are my upcoming travel plans?",
    rerank=True,
    user_id="user123"
)
```

- **Latency**: 150-200ms additional
- **Accuracy**: Significantly improved

## Webhooks

Real-time notifications for memory events, configured at the project level.

```python
# Create webhook
webhook = client.create_webhook(
    url="https://your-app.com/webhook",
    name="Memory Logger",
    project_id="proj_123",
    event_types=["memory_add", "memory_categorize"]
)

# Get webhooks
webhooks = client.get_webhooks(project_id="proj_123")
```

### Event Types

- `memory_add` — New memory created
- `memory_update` — Memory updated
- `memory_delete` — Memory deleted
- `memory_categorize` — Memory categorized

## Direct Import

Bulk import existing data into Mem0 memory.

```python
# Import memories in bulk
client.import_memories(
    memories=[
        {"text": "User prefers dark mode", "user_id": "alice"},
        {"text": "User is a vegetarian", "user_id": "alice"}
    ]
)
```

## Memory Export

Export memories in structured formats using Pydantic schemas.

```python
# Create export job
export_job = client.create_export(
    filters={"user_id": "alice"},
    schema="default"
)

# Retrieve exported data
exported_data = client.get_export(export_job["id"])
```

## Timestamp Support

Temporal memory management with time-based queries.

```python
# Add memory with timestamp
client.add(
    messages,
    user_id="alice",
    timestamp="2025-01-15T12:00:00Z"
)

# Search with time filters
results = client.search(
    query="recent preferences",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"created_at": {">": "2025-01-01T00:00:00Z"}}
        ]
    }
)
```

## Expiration Dates

Automatic memory cleanup with configurable expiration.

```python
# Set expiration when adding
client.add(
    messages,
    user_id="alice",
    expires_at="2025-12-31T23:59:59Z"
)
```

## Custom Instructions

Customize how Mem0 processes and stores information.

```python
# Set custom instructions at project level
client.project.update(
    custom_instructions="Focus on extracting dietary preferences and allergies."
)
```

## Contextual Add

Add memories with enhanced context awareness for better extraction quality.

```python
client.add(
    messages,
    user_id="alice",
    context="This conversation is about restaurant recommendations in Tokyo"
)
```

## Criteria-Based Retrieval

Targeted memory retrieval using custom criteria beyond semantic similarity.

```python
results = client.search(
    query="travel plans",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"categories": {"in": ["travel", "planning"]}}
        ]
    }
)
```

## V2 Memory Filters

Advanced filtering with logical operators and field-level access for precise memory queries.

```python
results = client.search(
    query="preferences",
    filters={
        "OR": [
            {"user_id": "alice"},
            {"agent_id": {"in": ["travel-assistant", "customer-support"]}}
        ],
        "AND": [
            {"created_at": {">": "2025-01-01"}}
        ]
    }
)
```

## Group Chat Support

Multi-conversation memory management for group interactions.

```python
client.add(
    messages,
    user_id="alice",
    run_id="group-session-xyz"
)
```

## Feedback Mechanism

Improve memory quality through user feedback signals.

```python
# Submit positive/negative feedback on a memory
client.feedback(
    memory_id="mem_123",
    rating="positive"  # or "negative"
)
```
