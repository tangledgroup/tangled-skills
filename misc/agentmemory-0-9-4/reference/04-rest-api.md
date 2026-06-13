# REST API

agentmemory exposes 107 REST endpoints on port `3111` (default). The server binds to `127.0.0.1` by default. Protected endpoints require `Authorization: Bearer <secret>` when `AGENTMEMORY_SECRET` is set.

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agentmemory/health` | Health check (always public) |
| `POST` | `/agentmemory/session/start` | Start session + get context |
| `POST` | `/agentmemory/session/end` | End session |
| `POST` | `/agentmemory/observe` | Capture observation |
| `POST` | `/agentmemory/smart-search` | Hybrid search |
| `POST` | `/agentmemory/context` | Generate context |
| `POST` | `/agentmemory/remember` | Save to long-term memory |
| `POST` | `/agentmemory/forget` | Delete observations |
| `GET` | `/agentmemory/sessions` | List sessions |
| `GET` | `/agentmemory/profile` | Project profile |
| `GET` | `/agentmemory/memories` | List memories |
| `POST` | `/agentmemory/consolidate` | Trigger consolidation |
| `POST` | `/agentmemory/graph/extract` | Manual graph extraction |
| `GET` | `/agentmemory/graph/stats` | Graph statistics |
| `GET` | `/agentmemory/config/flags` | Feature flag states (v0.9.3+) |
| `GET` | `/agentmemory/audit` | Audit trail entries |
| `POST` | `/agentmemory/export` | Export all data |
| `GET` | `/agentmemory/viewer` | Real-time viewer (CSP-protected) |

## New in v0.9.x

- **`GET /agentmemory/config/flags`** — Returns `{ version, provider, embeddingProvider, flags[] }` with per-flag details including `key`, `label`, `enabled`, `default`, `affects`, `needsLlm`, `description`, `enableHow`, `docsHref`. Used by viewer banner system and CLI status/doctor.
- **Structured error responses** — Feature-not-enabled errors now return `{ error, flag, enableHow, docsHref }` instead of bare error strings.
- **`GET /agentmemory/audit`** — Returns `{ entries, success }` shape (was bare array in earlier versions).

## Authentication

When `AGENTMEMORY_SECRET` is set, include the bearer token:

```bash
curl -H "Authorization: Bearer your-secret" http://localhost:3111/agentmemory/health
```

Mesh sync endpoints require `AGENTMEMORY_SECRET` on both peers.

## WebSocket Stream

The iii-engine exposes a WebSocket stream on port `3112` (default) for real-time event monitoring. The viewer connects to this stream for live updates. The iii console can also monitor these streams.

## CSP Headers

The `/agentmemory/viewer` endpoint uses per-response script nonces and disables inline handler attributes (`script-src-attr 'none'`).
