# Mem0 Platform Features

Advanced features available in the managed Mem0 Platform including graph memory, webhooks, MCP integration, and exports.

## Graph Memory

Track relationships between entities for more intelligent recall.

### What is Graph Memory?

Graph memory stores not just individual facts, but also relationships between entities (people, places, concepts). This enables queries like "Who are Alice's colleagues?" or "What projects has the team worked on?"

### Enable Graph Memory

```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Add memory with graph extraction enabled
result = client.add(
    messages=[
        {"role": "user", "content": "I work with Bob at Acme Corp on the Titan project"}
    ],
    user_id="alice",
    enable_graph=True  # Extract relationships
)
```

### Query Relationships

```python
# Search for relationship-based information
results = client.search(
    query="Who does Alice work with?",
    filters={"user_id": "alice"},
    include_graph=True  # Include graph data in results
)

print(results)
# {
#   "results": [...],
#   "graph": {
#     "nodes": [
#       {"id": "alice", "type": "person"},
#       {"id": "bob", "type": "person"},
#       {"id": "acme_corp", "type": "organization"},
#       {"id": "titan_project", "type": "project"}
#     ],
#     "edges": [
#       {"from": "alice", "to": "bob", "relation": "colleague_of"},
#       {"from": "alice", "to": "acme_corp", "relation": "works_at"},
#       {"from": "alice", "to": "titan_project", "relation": "works_on"}
#     ]
#   }
# }
```

### Graph Configuration

```python
# Configure graph extraction thresholds
result = client.add(
    messages=[...],
    user_id="alice",
    enable_graph=True,
    graph_config={
        "threshold": 0.7,  # Confidence threshold for relationships
        "max_entities": 10,  # Max entities to extract per message
        "entity_types": ["person", "organization", "project"]  # Filter entity types
    }
)
```

## Webhooks

Receive real-time notifications when memories change.

### Create Webhook

```python
# Create webhook via API
import requests

response = requests.post(
    "https://api.mem0.ai/v1/webhooks",
    headers={
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "url": "https://your-server.com/webhook/mem0",
        "events": ["memory.created", "memory.updated", "memory.deleted"],
        "secret": "your-webhook-secret"  # For signature verification
    }
)

webhook = response.json()
print(f"Webhook ID: {webhook['id']}")
```

### Handle Webhook Events

```python
from fastapi import FastAPI, Header, HTTPException
import hmac
import hashlib

app = FastAPI()

@app.post("/webhook/mem0")
async def handle_webhook(
    payload: dict,
    x_mem0_signature: str = Header(None),
    x_mem0_event: str = Header(None)
):
    # Verify signature
    secret = "your-webhook-secret"
    expected_signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_mem0_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Handle event
    event_type = x_mem0_event
    
    if event_type == "memory.created":
        await handle_memory_created(payload)
    elif event_type == "memory.updated":
        await handle_memory_updated(payload)
    elif event_type == "memory.deleted":
        await handle_memory_deleted(payload)
    
    return {"status": "received"}

async def handle_memory_created(payload: dict):
    """Handle new memory creation."""
    memory_id = payload["memory"]["id"]
    user_id = payload["memory"]["user_id"]
    content = payload["memory"]["memory"]
    
    # Trigger downstream actions
    await notify_user(user_id, f"New memory: {content}")
    await update_search_index(memory_id, content)
```

### Webhook Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `memory.created` | New memory added | Memory object with full details |
| `memory.updated` | Memory content changed | Old and new memory objects |
| `memory.deleted` | Memory removed | Memory ID and user_id |
| `graph.edge.created` | New relationship extracted | Edge object with nodes |

## MCP (Model Context Protocol) Integration

Enable AI agents to manage their own memories automatically.

### What is MCP?

Mem0 MCP provides a standardized protocol for AI clients (Claude Code, Cursor, etc.) to interact with memory without custom integration code.

### Configure MCP Server

```json
// claude-code config
{
  "mcpServers": {
    "mem0": {
      "command": "npx",
      "args": ["-y", "@mem0/mcp"],
      "env": {
        "MEM0_API_KEY": "your-api-key"
      }
    }
  }
}
```

### AI Agent Auto-Memory

Once configured, AI agents can:

1. **Auto-add memories** - Save important facts during conversations
2. **Auto-search** - Retrieve context when needed
3. **Self-manage** - Decide what to remember without prompts

Example interaction:

```
User: "I'm planning a trip to Japan next spring"

[Agent automatically saves: "User planning trip to Japan in spring"]

User (next session): "What should I pack for my trip?"

[Agent automatically searches memories]
Agent: "For your Japan trip in spring, you should pack..."
```

### Custom MCP Tools

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Mem0")

@mcp.tool()
async def get_user_context(user_id: str) -> str:
    """Get relevant user memories for context."""
    client = MemoryClient(api_key="your-api-key")
    results = await client.search(
        query="preferences and history",
        filters={"user_id": user_id},
        limit=5
    )
    return "\n".join([r["memory"] for r in results["results"]])

@mcp.tool()
async def save_insight(user_id: str, insight: str) -> dict:
    """Save an important insight or fact."""
    client = MemoryClient(api_key="your-api-key")
    result = await client.add(
        messages=[{"role": "user", "content": insight}],
        user_id=user_id
    )
    return result

@mcp.resource("mem0://memories/{user_id}")
async def list_memories(user_id: str) -> list[dict]:
    """List all memories for a user."""
    client = MemoryClient(api_key="your-api-key")
    results = await client.get_all(filters={"user_id": user_id})
    return results["memories"]
```

## Memory Exports

Export memories for backup, migration, or analysis.

### Create Export

```python
# Platform API export
import requests

response = requests.post(
    "https://api.mem0.ai/v1/exports",
    headers={
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "filters": {"user_id": "alice"},  # Optional: filter by user
        "format": "json",  # or "csv"
        "include_metadata": True
    }
)

export_job = response.json()
export_id = export_job["id"]
print(f"Export job created: {export_id}")
```

### Check Export Status

```python
response = requests.get(
    f"https://api.mem0.ai/v1/exports/{export_id}",
    headers={"Authorization": f"Token {API_KEY}"}
)

export_status = response.json()

if export_status["status"] == "completed":
    download_url = export_status["download_url"]
    print(f"Download ready: {download_url}")
```

### Download Export

```python
response = requests.get(
    export_status["download_url"],
    headers={"Authorization": f"Token {API_KEY}"}
)

memories = response.json()

# Process exported memories
for memory in memories["memories"]:
    print(f"{memory['id']}: {memory['memory']}")
```

### Export Formats

**JSON (default):**
```json
{
  "exported_at": "2025-01-15T10:30:00Z",
  "total_count": 42,
  "memories": [
    {
      "id": "mem_abc123",
      "memory": "User prefers vegetarian food",
      "user_id": "alice",
      "categories": ["diet"],
      "created_at": "2025-01-10T08:00:00Z",
      "updated_at": "2025-01-12T14:30:00Z"
    }
  ]
}
```

**CSV:**
```csv
id,memory,user_id,categories,created_at,updated_at
mem_abc123,"User prefers vegetarian food",alice,"diet",2025-01-10T08:00:00Z,2025-01-12T14:30:00Z
```

## Direct Import

Import memories from external sources.

### Bulk Import

```python
import requests

memories_to_import = [
    {
        "memory": "User works as a software engineer",
        "user_id": "alice",
        "categories": ["professional"]
    },
    {
        "memory": "User lives in San Francisco",
        "user_id": "alice",
        "categories": ["location"]
    }
]

response = requests.post(
    "https://api.mem0.ai/v1/memories/import",
    headers={
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "memories": memories_to_import,
        "upsert": True  # Update if memory_id exists
    }
)

import_result = response.json()
print(f"Imported {import_result['count']} memories")
```

### Import from File

```python
def import_from_json_file(filepath: str, api_key: str):
    """Import memories from a JSON file."""
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    memories = [
        {
            "memory": m["memory"],
            "user_id": m["user_id"],
            "categories": m.get("categories", [])
        }
        for m in data["memories"]
    ]
    
    response = requests.post(
        "https://api.mem0.ai/v1/memories/import",
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        },
        json={"memories": memories}
    )
    
    return response.json()

# Usage
result = import_from_json_file("backup.json", "your-api-key")
```

## Custom Categories

Organize memories with custom taxonomy.

### Add with Categories

```python
result = client.add(
    messages=[{"role": "user", "content": "I love Italian cuisine"}],
    user_id="alice",
    metadata={
        "category": "food_preferences"  # Custom category
    }
)
```

### Search by Category

```python
results = client.search(
    query="food preferences",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"categories": {"contains": "food_preferences"}}
        ]
    }
)
```

### Category Management

```python
# List all categories for a user
def get_user_categories(client, user_id: str) -> set[str]:
    all_memories = client.get_all(filters={"user_id": user_id})
    
    categories = set()
    for memory in all_memories["memories"]:
        categories.update(memory.get("categories", []))
    
    return categories

# Usage
categories = get_user_categories(client, "alice")
print(f"User has {len(categories)} categories: {categories}")
```

## Custom Instructions

Provide context-specific guidance for memory extraction.

### Set Custom Instructions

```python
result = client.add(
    messages=[...],
    user_id="alice",
    custom_instructions="""Focus on extracting:
- Technical preferences (programming languages, tools)
- Project constraints (deadlines, budgets)
- Team member roles and responsibilities

Ignore casual conversation and small talk."""
)
```

### Use Cases for Custom Instructions

**Healthcare:**
```
Extract medical history, symptoms, medications, allergies.
Use precise medical terminology.
Flag any urgent concerns.
```

**Customer Support:**
```
Extract product issues, error messages, troubleshooting steps.
Note customer sentiment and urgency level.
Track resolution status.
```

**Education:**
```
Extract learning goals, current skill level, preferred learning styles.
Track progress on specific topics.
Note areas of confusion or difficulty.
```

## Expiration Date

Set automatic expiration for temporary memories.

### Add with Expiration

```python
result = client.add(
    messages=[{"role": "user", "content": "I need this report by Friday"}],
    user_id="alice",
    metadata={
        "expiration_date": "2025-01-20T23:59:59Z"  # ISO 8601 format
    }
)
```

### Query with Expiration Filter

```python
from datetime import datetime, timedelta

# Get memories that haven't expired
cutoff = datetime.utcnow().isoformat()

results = client.search(
    query="urgent tasks",
    filters={
        "AND": [
            {"user_id": "alice"},
            {"expiration_date": {"gte": cutoff}}  # Not yet expired
        ]
    }
)
```

### Auto-Cleanup Expired Memories

```python
def cleanup_expired_memories(client: MemoryClient, user_id: str):
    """Delete all expired memories for a user."""
    
    cutoff = datetime.utcnow().isoformat()
    all_memories = client.get_all(filters={"user_id": user_id})
    
    deleted_count = 0
    for memory in all_memories["memories"]:
        expiration = memory.get("metadata", {}).get("expiration_date")
        
        if expiration and expiration < cutoff:
            client.delete(memory_id=memory["id"])
            deleted_count += 1
    
    print(f"Deleted {deleted_count} expired memories")
```

## Feedback Mechanism

Collect user feedback to improve memory quality.

### Provide Feedback

```python
# Rate a memory's relevance
result = client.feedback(
    memory_id="mem_abc123",
    score=0.9,  # 0.0 to 1.0
    reason="Highly relevant to current context"
)

# Mark as incorrect
result = client.feedback(
    memory_id="mem_xyz789",
    score=0.0,
    reason="Outdated information, user moved cities"
)
```

### Use Feedback for Filtering

```python
# Get highly-rated memories
results = client.search(
    query="preferences",
    filters={"user_id": "alice"},
    min_feedback_score=0.7  # Only memories with good feedback
)
```

## CLI Tools

Manage memories from the command line.

### Installation

```bash
pip install mem0ai-cli
```

### Authentication

```bash
mem0 init --api-key "your-api-key"
```

### Basic Operations

```bash
# Add memory
mem0 add "I prefer dark mode" --user-id alice

# Search memories
mem0 search "UI preferences" --user-id alice

# List all memories for user
mem0 list --user-id alice

# Delete specific memory
mem0 delete mem_abc123

# Export memories
mem0 export --user-id alice --output backups/alice.json
```

### Batch Operations

```bash
# Import from file
mem0 import --file memories.json

# Delete all for user (dangerous!)
mem0 delete-all --user-id alice --confirm
```

## Platform vs OSS Feature Comparison

| Feature | Platform | Open Source |
|---------|----------|-------------|
| Graph memory | ✅ Managed Neo4j/Memgraph | ⚠️ Self-host required |
| Webhooks | ✅ Built-in | ❌ Not available |
| MCP integration | ✅ Official server | ⚠️ Community implementations |
| Memory exports | ✅ One-click UI + API | ⚠️ Manual extraction |
| Direct import | ✅ Bulk API | ⚠️ Custom scripts |
| Custom categories | ✅ Native support | ✅ Via metadata |
| Expiration dates | ✅ Automatic cleanup | ✅ Manual implementation |
| Feedback mechanism | ✅ Built-in tracking | ❌ Not available |
| CLI tool | ✅ Full-featured | ✅ Basic operations |
| Dashboard UI | ✅ Visual management | ❌ Self-host or custom |

## Best Practices

1. **Use graph memory for relationship-heavy domains** - Social networks, organizational charts
2. **Set up webhooks for real-time sync** - Keep external systems in sync with memory changes
3. **Enable MCP for AI agent workflows** - Let agents self-manage memory
4. **Schedule regular exports** - Backup memories for compliance and disaster recovery
5. **Implement custom categories** - Organize by domain-specific taxonomy
6. **Set expiration dates for temporary data** - Auto-clean session-specific memories
7. **Collect feedback iteratively** - Improve extraction quality over time
