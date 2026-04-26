# API Reference

## Platform REST API

Base URL: `https://api.mem0.ai`

All endpoints use `/v1/` prefix. Authentication via `Authorization: Token <API_KEY>` header.

### Core Memory Endpoints

- `POST /v1/memories/` — Add memories
- `GET /v1/memories/` — Get all memories (with pagination and filtering)
- `POST /v1/memories/search/` — Search memories
- `GET /v1/memories/{memory_id}/` — Get single memory by ID
- `PUT /v1/memories/{memory_id}/` — Update memory
- `DELETE /v1/memories/{memory_id}/` — Delete memory
- `GET /v1/memories/{memory_id}/history/` — Memory change history
- `PUT /v1/batch/` — Batch update memories
- `DELETE /v1/batch/` — Batch delete memories
- `DELETE /v1/memories/` — Delete all matching criteria

### V2 Endpoints

- `POST /v2/memories/` — Add memories (v2 format)
- `POST /v2/memories/search/` — Search memories (v2 format)
- `GET /v2/entities/{entity_type}/{entity_id}/` — Get entity memories
- `DELETE /v2/entities/{entity_type}/{entity_id}/` — Delete entity and memories

### Events

- `GET /v1/events/` — List async memory operation events
- `GET /v1/event/{event_id}/` — Get specific event details
- `GET /v1/memories/events/` — Memory-specific events

### Entities

- `GET /v1/entities/` — List all entities (users, agents, apps)
- `GET /v1/entities/filters/` — Available filter options
- `POST /v1/users/` — Create user
- `POST /v1/agents/` — Create agent
- `POST /v1/apps/` — Create app
- `DELETE /v1/entities/{entity_type}/{entity_id}/` — Delete entity

### Runs

- `POST /v1/runs/` — Create a run (session)

### Exports

- `POST /v1/exports/` — Create export job with schema
- `POST /v1/exports/get` — Export data based on filters

### Feedback

- `POST /v1/feedback/` — Submit memory quality feedback

### Statistics

- `GET /v1/stats/` — Memory-related statistics

### Organizations & Projects

- `GET /api/v1/orgs/organizations/` — List organizations
- `POST /api/v1/orgs/organizations/` — Create organization
- `GET /api/v1/orgs/organizations/{org_id}/` — Get organization
- `DELETE /api/v1/orgs/organizations/{org_id}/` — Delete organization
- `GET /api/v1/orgs/organizations/{org_id}/members/` — List members
- `POST /api/v1/orgs/organizations/{org_id}/members/` — Add member
- `PUT /api/v1/orgs/organizations/{org_id}/members/` — Update member role
- `DELETE /api/v1/orgs/organizations/{org_id}/members/` — Remove member
- `GET /api/v1/orgs/organizations/{org_id}/projects/` — List projects
- `POST /api/v1/orgs/organizations/{org_id}/projects/` — Create project
- `GET /api/v1/orgs/organizations/{org_id}/projects/{project_id}/` — Get project
- `PATCH /api/v1/orgs/organizations/{org_id}/projects/{project_id}/` — Update project
- `DELETE /api/v1/orgs/organizations/{org_id}/projects/{project_id}/` — Delete project
- `GET /api/v1/orgs/organizations/{org_id}/projects/{project_id}/members/` — Project members
- `POST /api/v1/orgs/organizations/{org_id}/projects/{project_id}/members/` — Add project member
- `PUT /api/v1/orgs/organizations/{org_id}/projects/{project_id}/members/` — Update project member
- `DELETE /api/v1/orgs/organizations/{org_id}/projects/{project_id}/members/` — Delete project member

### Webhooks

- `GET /api/v1/webhooks/projects/{project_id}/` — List webhooks
- `POST /api/v1/webhooks/projects/{project_id}/` — Create webhook
- `PUT /api/v1/webhooks/{webhook_id}/` — Update webhook
- `DELETE /api/v1/webhooks/{webhook_id}/` — Delete webhook

### cURL Examples

```bash
# Add memory
curl -X POST https://api.mem0.ai/v1/memories/ \
  -H "Authorization: Token $MEM0_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Im a vegetarian and allergic to nuts."}
    ],
    "user_id": "user123"
  }'

# Search memories
curl -X POST https://api.mem0.ai/v1/memories/search/ \
  -H "Authorization: Token $MEM0_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my dietary restrictions?",
    "filters": {"user_id": "user123"}
  }'

# Get all memories
curl -X GET "https://api.mem0.ai/v1/memories/?user_id=user123" \
  -H "Authorization: Token $MEM0_API_KEY"
```

## Open Source REST API

Base URL: `http://localhost:8000` (or your deployment URL)

No `/v1/` prefix. Optional authentication via `X-API-Key` header.

### Endpoints

- `POST /memories` — Add memories
- `GET /memories` — List all memories
- `GET /memories/{memory_id}` — Get single memory
- `PUT /memories/{memory_id}` — Update memory
- `DELETE /memories/{memory_id}` — Delete memory
- `POST /memories/search` — Search memories
- `GET /` — Health check / redirect to docs
- `/docs` — Interactive OpenAPI explorer
- `/openapi.json` — OpenAPI schema

```bash
# Add memory (OSS)
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "I prefer dark mode."}
    ],
    "user_id": "alice"
  }'

# Search memories (OSS)
curl -X POST http://localhost:8000/memories/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "UI preferences",
    "user_id": "alice"
  }'
```

## SDK Method Reference

### MemoryClient (Platform, Synchronous)

| Method | Description |
|--------|-------------|
| `add(messages, ...)` | Add memories from conversation |
| `search(query, filters=...)` | Search memories with filters |
| `get_all(filters=...)` | Get all memories (requires filters) |
| `get(memory_id)` | Get single memory by ID |
| `update(memory_id, text=..., metadata=...)` | Update memory |
| `delete(memory_id)` | Delete single memory |
| `batch_update(memories)` | Batch update (up to 1000) |
| `batch_delete(memories)` | Batch delete (up to 1000) |
| `delete_all(user_id=..., agent_id=...)` | Delete by filter |
| `history(memory_id)` | Get memory change history |
| `create_webhook(...)` | Create webhook |
| `get_webhooks(project_id)` | List webhooks |
| `project.get(fields=...)` | Get project details |
| `project.update(...)` | Update project settings |

### AsyncMemoryClient (Platform, Asynchronous)

Same methods as `MemoryClient`, all prefixed with `await`.

### Memory (Open Source, Synchronous)

| Method | Description |
|--------|-------------|
| `add(messages, user_id=..., infer=True)` | Add memories |
| `search(query, user_id=..., limit=3, rerank=False)` | Search memories |
| `get_all(user_id=...)` | Get all memories |
| `get(memory_id)` | Get single memory |
| `update(memory_id, data=...)` | Update memory |
| `delete(memory_id, user_id=...)` | Delete memory |
| `delete_all(user_id=...)` | Delete by user |
| `history(memory_id, user_id=...)` | Memory history |

### AsyncMemory (Open Source, Asynchronous)

Same methods as `Memory`, all prefixed with `await`.
