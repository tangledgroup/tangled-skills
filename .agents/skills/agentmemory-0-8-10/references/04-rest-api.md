# agentmemory REST API Reference

All 109 REST endpoints exposed on `http://localhost:3111/agentmemory/*`. Most require Bearer token authentication when `AGENTMEMORY_SECRET` is set.

## Authentication

```bash
export AGENTMEMORY_SECRET="your-secret-key"

# Include in all requests
curl -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  http://localhost:3111/agentmemory/endpoint
```

## Core Endpoints

### Search and Recall

#### POST /search

Search observations with hybrid search (BM25 + vector + graph).

**Request:**
```json
{
  "query": "JWT authentication",
  "project": "/home/user/my-project",
  "limit": 10,
  "offset": 0,
  "sessionId": "session_xyz",  // Optional: filter by session
  "types": ["file_write", "decision"],  // Optional: filter by type
  "expandIds": ["obs_abc123"]  // Optional: expand specific results
}
```

**Response:**
```json
{
  "results": [
    {
      "observation": {
        "id": "obs_abc123",
        "sessionId": "session_xyz",
        "title": "Added JWT middleware",
        "type": "file_write",
        "facts": ["HS256 algorithm", "24h expiry"],
        "narrative": "Implemented authentication...",
        "concepts": ["jwt", "auth"],
        "files": ["src/middleware/auth.ts"]
      },
      "score": 0.92,
      "bm25Score": 0.85,
      "vectorScore": 0.94,
      "graphScore": 0.88
    }
  ],
  "totalMatches": 47,
  "queryTimeMs": 23
}
```

---

#### POST /smart-search

Progressive disclosure search (compact results first, expand on demand).

**Request:**
```json
{
  "query": "database migration",
  "limit": 10,
  "expandIds": ["obs_abc123", "obs_def456"]
}
```

**Response:**
```json
{
  "results": [
    {
      "obsId": "obs_abc123",
      "sessionId": "session_xyz",
      "title": "Added PostgreSQL migration",
      "type": "file_write",
      "score": 0.94,
      "timestamp": "2024-01-12T09:15:00Z",
      "expanded": {
        "narrative": "Created initial schema...",
        "facts": ["PostgreSQL 15", "Prisma ORM"],
        "files": ["prisma/schema.prisma"]
      }
    },
    {
      "obsId": "obs_def456",
      "title": "Updated user model",
      "score": 0.87,
      "timestamp": "2024-01-12T10:30:00Z"
      // Not expanded (not in expandIds)
    }
  ],
  "totalMatches": 23
}
```

---

### Memory Management

#### POST /remember

Explicitly save a memory.

**Request:**
```json
{
  "content": "Use jose for JWT auth instead of jsonwebtoken (Edge compatibility)",
  "type": "preference",
  "concepts": ["jwt", "auth", "edge-functions"],
  "files": ["src/middleware/auth.ts"]
}
```

**Response:**
```json
{
  "success": true,
  "memoryId": "mem_abc123",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

---

#### GET /memories

List all memories.

**Query Parameters:**
- `type` — Filter by type (pattern, preference, architecture, bug, workflow, fact)
- `project` — Filter by project path
- `limit` — Max results (default 50)
- `offset` — Pagination offset

**Response:**
```json
{
  "memories": [
    {
      "id": "mem_abc123",
      "type": "preference",
      "title": "Use jose for JWT",
      "content": "Use jose instead of jsonwebtoken...",
      "concepts": ["jwt", "auth"],
      "files": ["src/middleware/auth.ts"],
      "strength": 0.92,
      "version": 1,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 47
}
```

---

#### GET /memories/:id

Get a specific memory.

**Response:**
```json
{
  "id": "mem_abc123",
  "type": "preference",
  "title": "Use jose for JWT",
  "content": "Full memory content...",
  "concepts": ["jwt", "auth", "edge-functions"],
  "files": ["src/middleware/auth.ts"],
  "sessionIds": ["session_xyz", "session_abc"],
  "strength": 0.92,
  "version": 1,
  "relatedIds": ["mem_def456"],
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

---

#### DELETE /memories/:id

Delete a memory.

**Request:**
```json
{
  "reason": "Outdated information",
  "archive": true  // Optional: archive instead of delete
}
```

---

### Session Management

#### GET /sessions

List all sessions.

**Query Parameters:**
- `status` — Filter by status (active, completed, abandoned)
- `project` — Filter by project path
- `limit` — Max results (default 20)

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_abc123",
      "project": "/home/user/my-project",
      "cwd": "/home/user/my-project",
      "startedAt": "2024-01-15T10:30:00Z",
      "endedAt": "2024-01-15T11:45:00Z",
      "status": "completed",
      "observationCount": 47,
      "model": "claude-sonnet-4-20250514"
    }
  ],
  "total": 23
}
```

---

#### GET /sessions/:id

Get session details.

**Response:**
```json
{
  "session": {
    "id": "session_abc123",
    "project": "/home/user/my-project",
    "startedAt": "2024-01-15T10:30:00Z",
    "endedAt": "2024-01-15T11:45:00Z",
    "status": "completed",
    "observationCount": 47
  },
  "observations": [...],
  "summary": {
    "title": "Implemented JWT authentication",
    "narrative": "Added middleware for...",
    "keyDecisions": ["Use jose library", "HS256 algorithm"],
    "filesModified": ["src/middleware/auth.ts"]
  }
}
```

---

#### POST /sessions/:id/summarize

Summarize a session with LLM.

**Request:**
```json
{
  "includeDecisions": true,
  "includePatterns": true,
  "maxTokens": 1000
}
```

---

### File Context

#### POST /file-context

Get observations for specific files.

**Request:**
```json
{
  "files": ["src/middleware/auth.ts", "src/utils/jwt.ts"],
  "sessionId": "session_current_123",  // Exclude current session
  "limit": 10
}
```

**Response:**
```json
{
  "context": "## File History\n\n### src/middleware/auth.ts\n- Session 2024-01-15: Added JWT validation middleware\n- Session 2024-01-10: Refactored to use jose library\n- Session 2024-01-05: Initial implementation\n\n### src/utils/jwt.ts\n- Session 2024-01-12: Added token refresh logic",
  "observations": [
    {
      "file": "src/middleware/auth.ts",
      "obsId": "obs_abc123",
      "title": "Added JWT validation",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Project Profile

#### POST /profile

Get or regenerate project profile.

**Request:**
```json
{
  "project": "/home/user/my-project",
  "refresh": false  // Set to true to force rebuild
}
```

**Response:**
```json
{
  "project": "/home/user/my-project",
  "updatedAt": "2024-01-15T12:00:00Z",
  "topConcepts": [
    {"concept": "authentication", "frequency": 34},
    {"concept": "postgresql", "frequency": 28}
  ],
  "topFiles": [
    {"file": "src/middleware/auth.ts", "frequency": 12},
    {"file": "prisma/schema.prisma", "frequency": 9}
  ],
  "conventions": [
    "TypeScript interfaces before implementation",
    "Tests alongside features"
  ],
  "commonErrors": [
    "JWT token expiry handling"
  ],
  "recentActivity": [
    "2024-01-15: Added rate limiting",
    "2024-01-14: Refactored auth middleware"
  ],
  "sessionCount": 23,
  "totalObservations": 1247
}
```

---

### Timeline

#### POST /timeline

Get chronological observations around an anchor point.

**Request:**
```json
{
  "anchor": "2024-01-15T10:00:00Z",  // ISO date or keyword
  "project": "/home/user/my-project",
  "before": 5,
  "after": 5
}
```

**Response:**
```json
{
  "anchor": "2024-01-15T10:00:00Z",
  "entries": [
    {
      "observation": {
        "id": "obs_abc123",
        "title": "Refactored auth middleware",
        "type": "file_edit"
      },
      "sessionId": "session_xyz",
      "relativePosition": -2,  // 2 observations before anchor
      "timestamp": "2024-01-15T09:30:00Z"
    },
    {
      "observation": {
        "id": "obs_def456",
        "title": "Added JWT validation",
        "type": "file_write"
      },
      "relativePosition": 1,
      "timestamp": "2024-01-15T10:15:00Z"
    }
  ]
}
```

---

### Knowledge Graph

#### POST /graph-query

Query the knowledge graph.

**Request:**
```json
{
  "startNodeId": "mem_abc123",
  "maxHops": 2,
  "minConfidence": 0.7,
  "nodeTypes": ["file", "concept"],  // Optional filter
  "relationTypes": ["extends", "related"]  // Optional filter
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "mem_abc123",
      "type": "memory",
      "title": "JWT with jose",
      "concepts": ["jwt", "auth"]
    },
    {
      "id": "file_auth-ts",
      "type": "file",
      "path": "src/middleware/auth.ts"
    }
  ],
  "edges": [
    {
      "source": "mem_abc123",
      "target": "file_auth-ts",
      "type": "references",
      "confidence": 0.95
    },
    {
      "source": "mem_abc123",
      "target": "mem_def456",
      "type": "extends",
      "confidence": 0.87
    }
  ]
}
```

---

#### GET /graph/nodes

List all graph nodes.

**Query Parameters:**
- `type` — Filter by node type (memory, file, concept)
- `limit` — Max results

---

#### GET /graph/edges

List all graph edges.

**Query Parameters:**
- `source` — Filter by source node
- `target` — Filter by target node
- `type` — Filter by edge type (supersedes, extends, derives, contradicts, related)
- `minConfidence` — Minimum confidence score

---

### Context Injection

#### POST /context

Build context for session injection.

**Request:**
```json
{
  "project": "/home/user/my-project",
  "tokenBudget": 2000,
  "include": ["summaries", "memories", "recent-observations"],
  "excludeSessionId": "session_current_123"
}
```

**Response:**
```json
{
  "contextBlocks": [
    {
      "type": "summary",
      "content": "## Recent Session Summary\n\nLast session focused on...",
      "tokens": 342,
      "recency": 0.95,
      "sourceIds": ["session_xyz"]
    },
    {
      "type": "memory",
      "content": "## Preference: JWT Library\n\nUse jose instead of jsonwebtoken...",
      "tokens": 128,
      "recency": 0.78,
      "sourceIds": ["mem_abc123"]
    }
  ],
  "totalTokens": 1456,
  "budgetUsed": 0.73
}
```

---

### Export/Import

#### POST /export

Export all memory data.

**Request:**
```json
{
  "format": "json",  // or "obsidian"
  "includeObservations": true,
  "includeGraph": true,
  "sessionId": "session_xyz"  // Optional: export single session
}
```

**Response:**
```json
{
  "version": "0.8.10",
  "exportedAt": "2024-01-15T12:00:00Z",
  "sessions": [...],
  "observations": [...],
  "memories": [...],
  "summaries": [...],
  "profiles": [...],
  "graphNodes": [...],
  "graphEdges": [...],
  "config": {...}
}
```

---

#### POST /import

Import data from export or other systems.

**Request:**
```json
{
  "data": {...},  // Export JSON object
  "source": "agentmemory",  // or "claude-mem", "mem0", etc.
  "merge": true,  // Merge with existing or replace
  "dryRun": false  // Validate without importing
}
```

---

### Consolidation

#### POST /consolidate

Consolidate related memories.

**Request:**
```json
{
  "memoryIds": ["mem_abc123", "mem_def456", "mem_ghi789"],
  "strategy": "merge"  // or "supersede"
}
```

**Response:**
```json
{
  "success": true,
  "consolidatedMemoryId": "mem_new123",
  "supersededIds": ["mem_abc123", "mem_def456", "mem_ghi789"],
  "newTitle": "JWT Authentication Best Practices"
}
```

---

### Maintenance

#### POST /rebuild-index

Rebuild BM25 and vector indexes.

**Request:**
```json
{
  "force": false,  // Force rebuild even if index is fresh
  "verbose": true  // Log progress
}
```

---

#### POST /evict

Remove low-retention memories.

**Request:**
```json
{
  "minRetentionScore": 0.1,
  "dryRun": true,  // Show what would be evicted
  "archive": false  // Archive instead of delete
}
```

**Response:**
```json
{
  "evictedIds": ["mem_old123", "mem_old456"],
  "archivedIds": [],
  "freedTokens": 1234,
  "dryRun": true
}
```

---

#### POST /diagnostics

Run system diagnostics.

**Request:**
```json
{
  "checkEmbeddings": true,
  "checkIndex": true,
  "checkGraph": true,
  "verbose": true
}
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "embeddings": {
      "status": "ok",
      "provider": "openai",
      "dimensions": 1536,
      "latencyMs": 45
    },
    "index": {
      "status": "ok",
      "bm25DocCount": 1247,
      "vectorCount": 1247
    },
    "graph": {
      "status": "ok",
      "nodeCount": 534,
      "edgeCount": 892
    }
  },
  "alerts": [],
  "recommendations": [
    "Consider consolidating memories (47 similar pairs detected)"
  ]
}
```

---

### Health and Metrics

#### GET /health

Get system health status.

**Response:**
```json
{
  "status": "healthy",
  "connectionState": "connected",
  "workers": [
    {
      "id": "worker_1",
      "name": "agentmemory",
      "status": "running"
    }
  ],
  "memory": {
    "heapUsed": 45678901,
    "heapTotal": 67890123,
    "rss": 89012345
  },
  "cpu": {
    "percent": 12.5
  },
  "eventLoopLagMs": 2.3,
  "uptimeSeconds": 86400,
  "kvConnectivity": {
    "status": "ok",
    "latencyMs": 1.2
  },
  "alerts": []
}
```

---

#### GET /metrics

Get function metrics.

**Response:**
```json
{
  "functions": [
    {
      "functionId": "mem::compress",
      "totalCalls": 1247,
      "successCount": 1235,
      "failureCount": 12,
      "avgLatencyMs": 1234,
      "avgQualityScore": 0.92
    },
    {
      "functionId": "mem::search",
      "totalCalls": 892,
      "successCount": 892,
      "failureCount": 0,
      "avgLatencyMs": 23,
      "avgQualityScore": 0.95
    }
  ],
  "tokenSavings": {
    "totalTokensSaved": 1834567,
    "estimatedCostSaved": 89.23
  }
}
```

---

### Configuration

#### GET /config

Get current configuration.

**Response:**
```json
{
  "engineUrl": "ws://localhost:49134",
  "restPort": 3111,
  "streamsPort": 3112,
  "provider": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
  },
  "tokenBudget": 2000,
  "maxObservationsPerSession": 500,
  "embeddingProvider": "openai",
  "bm25Weight": 0.4,
  "vectorWeight": 0.6,
  "dataDir": "/home/user/.agentmemory"
}
```

---

#### POST /config-update

Update runtime configuration.

**Request:**
```json
{
  "tokenBudget": 4000,
  "bm25Weight": 0.5,
  "vectorWeight": 0.35
}
```

**Note:** Most config changes require restart. Only search weights and token budget can be updated at runtime.

---

### Team Collaboration

#### POST /team/create

Create a new team.

**Request:**
```json
{
  "teamId": "backend-team",
  "name": "Backend Development Team",
  "description": "Shared memories for backend developers"
}
```

---

#### POST /team/share

Share memories with a team.

**Request:**
```json
{
  "teamId": "backend-team",
  "memoryIds": ["mem_abc123", "mem_def456"]
}
```

---

#### POST /team/sync

Sync shared memories from team.

**Request:**
```json
{
  "teamId": "backend-team"
}
```

**Response:**
```json
{
  "syncedMemories": [
    {
      "id": "mem_shared123",
      "title": "API design patterns",
      "sharedBy": "alice",
      "sharedAt": "2024-01-15T10:00:00Z"
    }
  ],
  "totalSynced": 12
}
```

---

### Advanced Features

#### POST /snapshot

Create a point-in-time snapshot.

**Request:**
```json
{
  "label": "Before major refactor",
  "includeObservations": true,
  "includeGraph": true
}
```

---

#### POST /enrich

Enrich observations with related context.

**Request:**
```json
{
  "observationIds": ["obs_abc123", "obs_def456"],
  "includeRelations": true,
  "maxHops": 2
}
```

---

#### POST /patterns

Detect recurring patterns.

**Request:**
```json
{
  "project": "/home/user/my-project",
  "minFrequency": 3,
  "types": ["file_write", "command_run"]
}
```

---

### WebSocket Streams

Connect to `ws://localhost:3112` for real-time observation streams.

**Subscribe to session:**
```json
{
  "type": "subscribe",
  "sessionId": "session_abc123",
  "group": "session_abc123"
}
```

**Receive observations:**
```json
{
  "type": "observation",
  "sessionId": "session_abc123",
  "data": {
    "id": "obs_new123",
    "hookType": "post_tool_use",
    "toolName": "write",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

### Error Responses

All endpoints return standard error format on failure:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Query is required",
    "details": {
      "field": "query",
      "reason": "missing_required_field"
    }
  }
}
```

**HTTP Status Codes:**
- `200` — Success
- `400` — Bad request (validation error)
- `401` — Unauthorized (missing/invalid token)
- `404` — Not found
- `500` — Internal server error
