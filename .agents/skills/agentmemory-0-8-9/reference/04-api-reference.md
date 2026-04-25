# REST API Reference

Complete reference for all 109 REST API endpoints. The API binds to `127.0.0.1:3111` by default. Protected endpoints require `Authorization: Bearer <secret>` when `AGENTMEMORY_SECRET` is set.

## Authentication

```bash
# Health check (always public)
curl http://localhost:3111/agentmemory/health

# Protected endpoints require bearer token
curl -H "Authorization: Bearer your-secret" \
  http://localhost:3111/agentmemory/profile
```

## Session Management

### POST /agentmemory/session/start

Start a new session and get relevant context.

**Request:**
```json
{
  "project": "my-project",
  "budget": 2000
}
```

**Response:**
```json
{
  "sessionId": "sess-abc123",
  "project": "my-project",
  "context": {
    "profile": {
      "topConcepts": [...],
      "topFiles": [...],
      "patterns": [...]
    },
    "memories": [...],
    "tokenCount": 1850
  }
}
```

---

### POST /agentmemory/session/end

End a session and trigger summarization.

**Request:**
```json
{
  "sessionId": "sess-abc123"
}
```

**Response:**
```json
{
  "sessionId": "sess-abc123",
  "observationCount": 47,
  "summarized": true
}
```

---

## Observation Capture

### POST /agentmemory/observe

Capture a raw observation (tool use, user prompt, etc.).

**Request:**
```json
{
  "sessionId": "sess-abc123",
  "type": "post_tool_use",
  "tool": "Bash",
  "input": { "command": "npm install" },
  "output": "added 47 packages in 3s",
  "timestamp": "2026-04-14T10:30:00Z"
}
```

**Response:**
```json
{
  "observationId": "obs-xyz789",
  "sessionId": "sess-abc123",
  "stored": true
}
```

---

## Search and Retrieval

### POST /agentmemory/smart-search

Hybrid search with BM25, vector, and knowledge graph fusion.

**Request:**
```json
{
  "query": "JWT authentication setup",
  "sessionId": "sess-abc123",
  "budget": 2000,
  "minConfidence": 0.5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "mem-123",
      "content": "JWT middleware uses jose library...",
      "score": 0.89,
      "source": "vector",
      "citations": [
        {
          "observationId": "obs-456",
          "sessionId": "sess-previous"
        }
      ]
    }
  ],
  "tokenCount": 1240
}
```

---

### POST /agentmemory/search

BM25 keyword search only.

**Request:**
```json
{
  "query": "authentication middleware",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "mem-123",
      "title": "JWT Authentication Setup",
      "narrative": "...",
      "score": 0.76
    }
  ]
}
```

---

### POST /agentmemory/vector-search

Vector similarity search only.

**Request:**
```json
{
  "query": "database performance issues",
  "limit": 5,
  "threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "mem-456",
      "title": "N+1 Query Fix",
      "narrative": "...",
      "cosineSimilarity": 0.82
    }
  ]
}
```

---

### POST /agentmemory/graph-search

Knowledge graph traversal search.

**Request:**
```json
{
  "entity": "JWT",
  "maxDepth": 2
}
```

**Response:**
```json
{
  "nodes": [
    {
      "entity": "JWT",
      "type": "concept",
      "connections": 12
    },
    {
      "entity": "jose",
      "type": "library",
      "connections": 8
    }
  ],
  "edges": [
    {
      "source": "JWT",
      "target": "jose",
      "relation": "implements"
    }
  ]
}
```

---

## Context Generation

### POST /agentmemory/context

Generate token-budgeted context for a session.

**Request:**
```json
{
  "sessionId": "sess-abc123",
  "project": "my-project",
  "budget": 2000
}
```

**Response:**
```json
{
  "context": {
    "profile": "...",
    "recentMemories": "...",
    "relevantPatterns": "..."
  },
  "tokenCount": 1850,
  "memoriesIncluded": 7
}
```

---

## Memory Operations

### POST /agentmemory/remember

Save to long-term memory.

**Request:**
```json
{
  "type": "decision",
  "title": "Chose PostgreSQL over SQLite",
  "narrative": "Selected PostgreSQL for production...",
  "concepts": ["database", "PostgreSQL"],
  "files": ["prisma/schema.prisma"]
}
```

**Response:**
```json
{
  "memoryId": "mem-789",
  "savedAt": "2026-04-14T10:35:00Z"
}
```

---

### POST /agentmemory/forget

Delete observations or memories.

**Request:**
```json
{
  "ids": ["obs-123", "mem-456"],
  "reason": "Outdated information"
}
```

**Response:**
```json
{
  "deleted": ["obs-123", "mem-456"],
  "timestamp": "2026-04-14T10:40:00Z"
}
```

---

### POST /agentmemory/compress

Compress raw observations into structured memory.

**Request:**
```json
{
  "observationIds": ["obs-123", "obs-456"],
  "useLLM": false  // Use synthetic compression (zero tokens)
}
```

**Response:**
```json
{
  "compressed": 2,
  "memoryIds": ["mem-new-123"],
  "tokensUsed": 0
}
```

---

## File Context

### POST /agentmemory/enrich

Get file context with memories and known bugs.

**Request:**
```json
{
  "filePath": "src/middleware/auth.ts",
  "sessionId": "sess-abc123"
}
```

**Response:**
```json
{
  "fileHistory": [...],
  "relatedMemories": [...],
  "knownIssues": [
    {
      "type": "bug",
      "description": "JWT validation fails for expired tokens",
      "fixedIn": "obs-789"
    }
  ]
}
```

---

### GET /agentmemory/file-history/:filePath

Get observations for a specific file.

**Query Parameters:**
- `limit`: Max observations (default: 20)

**Response:**
```json
{
  "filePath": "src/middleware/auth.ts",
  "observations": [
    {
      "id": "obs-123",
      "tool": "Read",
      "timestamp": "2026-04-13T15:30:00Z"
    }
  ]
}
```

---

## Profile and Insights

### GET /agentmemory/profile

Get project profile.

**Query Parameters:**
- `project`: Project name (optional)

**Response:**
```json
{
  "project": "my-project",
  "topConcepts": [
    { "concept": "JWT", "count": 24 },
    { "concept": "PostgreSQL", "count": 18 }
  ],
  "topFiles": [
    { "file": "src/middleware/auth.ts", "accessCount": 47 }
  ],
  "patterns": [
    {
      "type": "decision",
      "title": "Use jose for JWT",
      "description": "...",
      "occurrences": 5
    }
  ],
  "totalObservations": 1247,
  "totalSessions": 34
}
```

---

### GET /agentmemory/status

Get health and statistics.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.8.9",
  "sessions": 34,
  "observations": 1247,
  "memories": 456,
  "tokenSavings": {
    "tokens": 1847293,
    "costDollars": 554.19
  }
}
```

---

## Sessions

### GET /agentmemory/sessions

List all sessions.

**Query Parameters:**
- `limit`: Max sessions (default: 20)
- `project`: Filter by project

**Response:**
```json
{
  "sessions": [
    {
      "id": "sess-abc123",
      "project": "my-project",
      "startedAt": "2026-04-14T09:00:00Z",
      "endedAt": "2026-04-14T10:30:00Z",
      "observationCount": 47,
      "summary": "Added JWT authentication..."
    }
  ]
}
```

---

### GET /agentmemory/sessions/:sessionId

Get session details.

**Response:**
```json
{
  "id": "sess-abc123",
  "project": "my-project",
  "startedAt": "2026-04-14T09:00:00Z",
  "endedAt": "2026-04-14T10:30:00Z",
  "observations": [...],
  "memories": [...],
  "summary": "..."
}
```

---

## Export and Import

### GET /agentmemory/export

Export all memory data.

**Query Parameters:**
- `format`: 'json' or 'obsidian' (default: 'json')
- `includeObservations`: true/false (default: true)
- `includeMemories`: true/false (default: true)

**Response (JSON format):**
```json
{
  "exportedAt": "2026-04-14T11:00:00Z",
  "version": "0.8.9",
  "data": {
    "sessions": [...],
    "observations": [...],
    "memories": [...],
    "accessLog": [...]
  }
}
```

---

### POST /agentmemory/import

Import memory data from JSON.

**Request:**
```json
{
  "data": {
    "sessions": [...],
    "observations": [...],
    "memories": [...]
  },
  "merge": true  // Merge with existing or replace
}
```

**Response:**
```json
{
  "importedAt": "2026-04-14T11:05:00Z",
  "sessionsImported": 12,
  "observationsImported": 456,
  "memoriesImported": 189
}
```

---

## Knowledge Graph

### POST /agentmemory/graph/query

Query knowledge graph.

**Request:**
```json
{
  "startEntity": "JWT",
  "maxDepth": 2,
  "relationFilter": ["implements", "uses"]
}
```

**Response:**
```json
{
  "nodes": [
    {
      "entity": "JWT",
      "type": "concept",
      "connections": 12
    }
  ],
  "edges": [
    {
      "source": "JWT",
      "target": "jose",
      "relation": "implements"
    }
  ]
}
```

---

### GET /agentmemory/graph/stats

Get knowledge graph statistics.

**Response:**
```json
{
  "totalEntities": 234,
  "totalRelations": 567,
  "topEntities": [
    { "entity": "JWT", "connections": 47 },
    { "entity": "PostgreSQL", "connections": 34 }
  ],
  "avgPathLength": 2.3
}
```

---

## Team Memory

### POST /agentmemory/team/share

Share memories with team.

**Request:**
```json
{
  "memoryIds": ["mem-123", "mem-456"],
  "teamId": "backend-team",
  "visibility": "team"
}
```

**Response:**
```json
{
  "shared": ["mem-123", "mem-456"],
  "teamId": "backend-team",
  "timestamp": "2026-04-14T11:10:00Z"
}
```

---

### GET /agentmemory/team/feed

Get team shared items.

**Query Parameters:**
- `teamId`: Team identifier (required)
- `limit`: Max items (default: 20)
- `userId`: Filter by user

**Response:**
```json
{
  "items": [
    {
      "id": "mem-123",
      "title": "JWT Setup Guide",
      "sharedBy": "alice",
      "sharedAt": "2026-04-14T10:00:00Z",
      "visibility": "team"
    }
  ]
}
```

---

## Audit and Governance

### GET /agentmemory/audit

Get audit trail.

**Query Parameters:**
- `operationType`: 'create', 'update', 'delete'
- `startTime`: ISO 8601 timestamp
- `endTime`: ISO 8601 timestamp
- `limit`: Max entries (default: 100)

**Response:**
```json
{
  "entries": [
    {
      "timestamp": "2026-04-14T11:15:00Z",
      "operation": "create",
      "entityId": "mem-789",
      "actor": "agent-a",
      "details": {
        "type": "decision",
        "title": "Chose PostgreSQL"
      }
    }
  ]
}
```

---

### POST /agentmemory/snapshot/create

Create memory snapshot.

**Request:**
```json
{
  "name": "before-refactor",
  "message": "Snapshot before major auth refactor"
}
```

**Response:**
```json
{
  "snapshotId": "snap-123",
  "name": "before-refactor",
  "createdAt": "2026-04-14T11:20:00Z",
  "memoryCount": 456
}
```

---

### GET /agentmemory/snapshots

List all snapshots.

**Response:**
```json
{
  "snapshots": [
    {
      "id": "snap-123",
      "name": "before-refactor",
      "createdAt": "2026-04-14T11:20:00Z",
      "memoryCount": 456
    }
  ]
}
```

---

## Actions and Coordination

### POST /agentmemory/actions/create

Create action item.

**Request:**
```json
{
  "title": "Fix JWT validation bug",
  "description": "Expired tokens not handled correctly",
  "dependencies": [],
  "priority": 8
}
```

**Response:**
```json
{
  "actionId": "act-123",
  "status": "ready",
  "createdAt": "2026-04-14T11:25:00Z"
}
```

---

### POST /agentmemory/actions/update

Update action status.

**Request:**
```json
{
  "actionId": "act-123",
  "status": "in-progress",
  "notes": "Started investigating token validation logic"
}
```

**Response:**
```json
{
  "actionId": "act-123",
  "status": "in-progress",
  "updatedAt": "2026-04-14T11:30:00Z"
}
```

---

### GET /agentmemory/actions/frontier

Get unblocked actions.

**Query Parameters:**
- `limit`: Max actions (default: 10)
- `includeBlocked`: true/false (default: false)

**Response:**
```json
{
  "actions": [
    {
      "id": "act-123",
      "title": "Fix JWT validation bug",
      "priority": 8,
      "status": "ready",
      "dependencies": []
    }
  ]
}
```

---

### GET /agentmemory/actions/next

Get next action.

**Response:**
```json
{
  "action": {
    "id": "act-123",
    "title": "Fix JWT validation bug",
    "description": "...",
    "priority": 8,
    "whyNow": "Highest priority unblocked action"
  }
}
```

---

## Multi-Agent Coordination

### POST /agentmemory/leases/create

Create lease.

**Request:**
```json
{
  "actionId": "act-123",
  "agentId": "agent-a",
  "duration": 600
}
```

**Response:**
```json
{
  "leaseId": "lease-456",
  "actionId": "act-123",
  "agentId": "agent-a",
  "expiresAt": "2026-04-14T12:30:00Z",
  "granted": true
}
```

---

### POST /agentmemory/signals/send

Send signal.

**Request:**
```json
{
  "targetAgentId": "agent-b",
  "channel": "auth-work",
  "message": "Fixed JWT validation bug",
  "parentId": null
}
```

**Response:**
```json
{
  "signalId": "sig-789",
  "sentAt": "2026-04-14T11:35:00Z",
  "deliveryStatus": "sent"
}
```

---

### GET /agentmemory/signals/read

Read signals.

**Query Parameters:**
- `agentId`: Read signals for this agent (required)
- `channel`: Filter by channel
- `unreadOnly`: true/false

**Response:**
```json
{
  "messages": [
    {
      "id": "sig-789",
      "fromAgentId": "agent-a",
      "channel": "auth-work",
      "message": "Fixed JWT validation bug",
      "sentAt": "2026-04-14T11:35:00Z",
      "readAt": null
    }
  ]
}
```

---

## Mesh Sync

### POST /agentmemory/mesh/push

Push memory to remote instance.

**Request:**
```json
{
  "remoteUrl": "http://remote-instance:3111",
  "secret": "shared-secret"
}
```

**Response:**
```json
{
  "synced": 47,
  "remoteUrl": "http://remote-instance:3111",
  "timestamp": "2026-04-14T11:40:00Z"
}
```

---

### POST /agentmemory/mesh/pull

Pull memory from remote instance.

**Request:**
```json
{
  "remoteUrl": "http://remote-instance:3111",
  "secret": "shared-secret"
}
```

**Response:**
```json
{
  "synced": 23,
  "remoteUrl": "http://remote-instance:3111",
  "timestamp": "2026-04-14T11:45:00Z"
}
```

---

## Diagnostics

### GET /agentmemory/diagnose

Run health checks.

**Response:**
```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "iii-engine",
      "status": "pass",
      "message": "Engine running"
    },
    {
      "name": "vector-index",
      "status": "pass",
      "message": "Index healthy"
    }
  ],
  "recommendations": []
}
```

---

### POST /agentmemory/heal

Auto-fix issues.

**Request:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "healed": true,
  "actions": [
    "Rebuilt vector index",
    "Cleared stale leases"
  ],
  "timestamp": "2026-04-14T11:50:00Z"
}
```

---

## Rate Limiting and Error Codes

### Rate Limits

- Search endpoints: 100 requests/minute
- Write endpoints: 50 requests/minute
- Mesh sync: 10 requests/minute

### Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid JSON, missing fields) |
| 401 | Unauthorized (missing or invalid bearer token) |
| 404 | Not found (session, memory, or action not found) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Error Response Format

```json
{
  "error": {
    "code": 404,
    "message": "Session not found",
    "details": {
      "sessionId": "sess-invalid"
    }
  }
}
```

---

## SDKs and Clients

### TypeScript/JavaScript

```typescript
const response = await fetch('http://localhost:3111/agentmemory/smart-search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-secret'
  },
  body: JSON.stringify({
    query: 'JWT authentication',
    budget: 2000
  })
});

const result = await response.json();
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:3111/agentmemory/smart-search',
    json={
        'query': 'JWT authentication',
        'budget': 2000
    },
    headers={
        'Authorization': 'Bearer your-secret'
    }
)

result = response.json()
```

### cURL

```bash
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret" \
  -d '{"query": "JWT authentication", "budget": 2000}'
```
