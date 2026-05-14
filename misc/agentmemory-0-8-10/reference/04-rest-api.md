# REST API

109 endpoints on port 3111 (configurable via `III_REST_PORT`). Binds to `127.0.0.1` by default. Protected endpoints require `Authorization: Bearer <secret>` when `AGENTMEMORY_SECRET` is set.

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agentmemory/health` | Health check (always public) |
| `POST` | `/agentmemory/session/start` | Start session + get context |
| `POST` | `/agentmemory/session/end` | End session |
| `POST` | `/agentmemory/observe` | Capture observation |
| `POST` | `/agentmemory/smart-search` | Hybrid search |
| `POST` | `/agentmemory/context` | Generate context block |
| `POST` | `/agentmemory/remember` | Save to long-term memory |
| `POST` | `/agentmemory/forget` | Delete observations |
| `POST` | `/agentmemory/enrich` | File context + memories + bugs |
| `GET` | `/agentmemory/profile` | Project profile |
| `GET` | `/agentmemory/export` | Export all data |
| `POST` | `/agentmemory/import` | Import from JSON |
| `POST` | `/agentmemory/graph/query` | Knowledge graph query |
| `POST` | `/agentmemory/team/share` | Share with team |
| `GET` | `/agentmemory/audit` | Audit trail |

## MCP Endpoint

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agentmemory/mcp/tools` | List available MCP tools |
| `POST` | `/agentmemory/mcp/tools` | Call an MCP tool by name |

## Authentication

When `AGENTMEMORY_SECRET` is set, all protected endpoints require:

```
Authorization: Bearer <AGENTMEMORY_SECRET>
```

Timing-safe comparison is used to prevent timing attacks on the secret. Mesh sync endpoints require `AGENTMEMORY_SECRET` on both peers.

## Example Requests

### Start a session

```bash
curl -X POST http://localhost:3111/agentmemory/session/start \
  -H "Content-Type: application/json" \
  -d '{"project": "my-app", "cwd": "/path/to/project"}'
```

### Smart search

```bash
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -d '{"query": "JWT authentication setup"}'
```

### Capture observation

```bash
curl -X POST http://localhost:3111/agentmemory/observe \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "sess_abc123",
    "hookType": "post_tool_use",
    "toolName": "Edit",
    "toolInput": {"file_path": "src/auth.ts"},
    "toolOutput": "Added JWT middleware..."
  }'
```

### Get project profile

```bash
curl http://localhost:3111/agentmemory/profile \
  -H "Content-Type: application/json"
```

## Real-Time Viewer

Auto-starts on port 3113. Features:
- Live observation stream via WebSocket
- Session explorer with filtering
- Memory browser with search
- Knowledge graph visualization
- Health dashboard
- Token savings card (dollar cost saved)

CSP headers use per-response script nonce and disable inline handler attributes (`script-src-attr 'none'`).

## Streams

WebSocket streams on port 3112 (configurable via `III_STREAMS_PORT`):
- `mem-live` — live observation stream, grouped by session ID
- `viewer` — real-time viewer updates

## Security

- Default binding is `127.0.0.1` (localhost only)
- Mesh sync validates peer IPs against private IP ranges
- Obsidian export confined to `AGENTMEMORY_EXPORT_ROOT`
- Viewer CSP prevents XSS via nonce-based script loading
- Secret redaction covers 15+ token patterns
