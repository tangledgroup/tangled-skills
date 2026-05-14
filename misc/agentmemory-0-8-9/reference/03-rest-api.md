# REST API Reference

109 endpoints on port 3111. The REST API binds to `127.0.0.1` by default (security hardening since v0.8.2). Protected endpoints require `Authorization: Bearer <secret>` when `AGENTMEMORY_SECRET` is set. Mesh sync endpoints require the secret on both peers.

## Authentication

When `AGENTMEMORY_SECRET` is configured, include it as a bearer token:

```bash
curl -H "Authorization: Bearer your-secret" http://localhost:3111/agentmemory/health
```

## Key Endpoints

### Health & Status

**GET /agentmemory/health** — Health check (always public, no auth required).

```bash
curl http://localhost:3111/agentmemory/health
```

### Session Management

**POST /agentmemory/session/start** — Start a new session and get initial context.

```json
{
  "project": "my-api",
  "cwd": "/path/to/project"
}
```

**POST /agentmemory/session/end** — End the current session, triggering summary generation.

### Observations

**POST /agentmemory/observe** — Capture a raw observation (typically called by hooks).

```json
{
  "sessionId": "sess-abc123",
  "hookType": "post_tool_use",
  "toolName": "Write",
  "toolInput": { "path": "src/auth.ts" },
  "toolOutput": "..."
}
```

### Search

**POST /agentmemory/smart-search** — Hybrid search combining BM25, vector, and graph signals.

```json
{
  "query": "JWT authentication middleware",
  "limit": 10
}
```

### Context Generation

**POST /agentmemory/context** — Generate context block for injection into agent conversation. Respects token budget (default: 2000 tokens).

```json
{
  "sessionId": "sess-abc123",
  "project": "my-api",
  "budget": 2000
}
```

### Long-Term Memory

**POST /agentmemory/remember** — Save to long-term memory.

```json
{
  "title": "Auth uses jose for Edge compatibility",
  "content": "JWT middleware in src/middleware/auth.ts uses jose instead of jsonwebtoken...",
  "type": "architecture"
}
```

**POST /agentmemory/forget** — Delete observations by ID.

```json
{
  "memoryIds": ["mem-001", "mem-002"]
}
```

### File Context

**POST /agentmemory/enrich** — Get file context + related memories + known bugs for a specific file.

```json
{
  "filePath": "src/middleware/auth.ts"
}
```

### Project Profile

**GET /agentmemory/profile** — Project profile with top concepts, files, and patterns.

```bash
curl http://localhost:3111/agentmemory/profile
```

### Data Portability

**GET /agentmemory/export** — Export all memory data as JSON (includes access log since v0.8.3).

**POST /agentmemory/import** — Import from previously exported JSON.

### Knowledge Graph

**POST /agentmemory/graph/query** — Query the knowledge graph by entity.

```json
{
  "entity": "authentication",
  "depth": 2
}
```

### Team Memory

**POST /agentmemory/team/share** — Share memory with team members (requires TEAM_ID).

### Audit Trail

**GET /agentmemory/audit** — Full audit trail of memory operations.

## Real-Time Viewer

The real-time viewer auto-starts on port 3113 and provides:

- Live observation stream
- Session explorer
- Memory browser
- Knowledge graph visualization
- Health dashboard
- Token savings dashboard (cumulative tokens saved + dollar cost saved at $0.30/1K tokens)

```bash
open http://localhost:3113
```

The viewer uses CSP nonces and `script-src-attr 'none'` for security (hardened in v0.8.2).

## WebSocket Streams

Real-time event streams available on port 3112 via iii-engine's Stream worker. Used by the viewer for live observation updates.
