# agentmemory MCP Tools Reference

All 43 MCP tools available via the `mcp::tools::call` endpoint. By default, only 8 core tools are visible (`AGENTMEMORY_TOOLS=all` enables all).

## Core Tools (Always Visible)

### memory_recall

Search past session observations for relevant context.

**Description:** Use when you need to recall what happened in previous sessions, find past decisions, or look up how a file was modified before.

**Input Schema:**
```json
{
  "query": {
    "type": "string",
    "description": "Search query (keywords, file names, concepts)",
    "required": true
  },
  "limit": {
    "type": "number",
    "description": "Max results to return (default 10)"
  }
}
```

**Example:**
```json
{
  "name": "memory_recall",
  "arguments": {
    "query": "JWT authentication middleware implementation",
    "limit": 5
  }
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
        "title": "Added JWT middleware using jose",
        "type": "file_write",
        "facts": ["JWT uses HS256", "Token expiry: 24h"],
        "files": ["src/middleware/auth.ts"]
      },
      "score": 0.92,
      "sessionId": "session_xyz"
    }
  ],
  "totalMatches": 17
}
```

---

### memory_save

Explicitly save an important insight, decision, or pattern to long-term memory.

**Input Schema:**
```json
{
  "content": {
    "type": "string",
    "description": "The insight or decision to remember",
    "required": true
  },
  "type": {
    "type": "string",
    "description": "Memory type: pattern, preference, architecture, bug, workflow, or fact"
  },
  "concepts": {
    "type": "string",
    "description": "Comma-separated key concepts"
  },
  "files": {
    "type": "string",
    "description": "Comma-separated relevant file paths"
  }
}
```

**Example:**
```json
{
  "name": "memory_save",
  "arguments": {
    "content": "Use jose for JWT auth instead of jsonwebtoken for Edge compatibility",
    "type": "preference",
    "concepts": "jwt,auth,edge-functions,vercel",
    "files": "src/middleware/auth.ts,src/utils/jwt.ts"
  }
}
```

---

### memory_file_history

Get past observations about specific files.

**Input Schema:**
```json
{
  "files": {
    "type": "string",
    "description": "Comma-separated file paths",
    "required": true
  },
  "sessionId": {
    "type": "string",
    "description": "Current session ID to exclude"
  }
}
```

**Example:**
```json
{
  "name": "memory_file_history",
  "arguments": {
    "files": "src/api/users.ts,src/services/user-service.ts",
    "sessionId": "session_current_123"
  }
}
```

**Response:**
```json
{
  "context": "## File History\n\n### src/api/users.ts\n- Session 2024-01-15: Added rate limiting middleware (10 req/min)\n- Session 2024-01-10: Refactored to use UserRepository\n- Session 2024-01-05: Initial implementation with Express\n\n### src/services/user-service.ts\n- Session 2024-01-12: Added pagination support\n- Session 2024-01-08: Implemented caching with Redis"
}
```

---

### memory_patterns

Detect recurring patterns across sessions.

**Input Schema:**
```json
{
  "project": {
    "type": "string",
    "description": "Project path to analyze"
  }
}
```

**Example:**
```json
{
  "name": "memory_patterns",
  "arguments": {
    "project": "/home/user/my-project"
  }
}
```

**Response:**
```json
{
  "patterns": [
    {
      "type": "file_write",
      "frequency": 23,
      "description": "Adding TypeScript interfaces before implementation",
      "files": ["src/types/*.ts"],
      "concepts": ["typescript", "interfaces", "type-safety"]
    },
    {
      "type": "command_run",
      "frequency": 15,
      "description": "Running tests after each feature completion",
      "commands": ["npm test", "pnpm test"],
      "concepts": ["testing", "tdd", "quality-assurance"]
    }
  ],
  "totalPatterns": 8
}
```

---

### memory_sessions

List recent sessions with their status and observation counts.

**Input Schema:**
```json
{}
```

**Example:**
```json
{
  "name": "memory_sessions",
  "arguments": {}
}
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_abc123",
      "project": "/home/user/my-project",
      "startedAt": "2024-01-15T10:30:00Z",
      "endedAt": "2024-01-15T11:45:00Z",
      "status": "completed",
      "observationCount": 47,
      "model": "claude-sonnet-4-20250514"
    },
    {
      "id": "session_def456",
      "project": "/home/user/my-project",
      "startedAt": "2024-01-14T14:20:00Z",
      "endedAt": "2024-01-14T16:00:00Z",
      "status": "completed",
      "observationCount": 62
    }
  ],
  "totalSessions": 23
}
```

---

### memory_smart_search

Hybrid semantic+keyword search with progressive disclosure.

**Input Schema:**
```json
{
  "query": {
    "type": "string",
    "description": "Search query",
    "required": true
  },
  "expandIds": {
    "type": "string",
    "description": "Comma-separated observation IDs to expand"
  },
  "limit": {
    "type": "number",
    "description": "Max results (default 10)"
  }
}
```

**Example (compact):**
```json
{
  "name": "memory_smart_search",
  "arguments": {
    "query": "database migration postgresql",
    "limit": 5
  }
}
```

**Example (with expansion):**
```json
{
  "name": "memory_smart_search",
  "arguments": {
    "query": "database migration postgresql",
    "expandIds": "obs_abc123,obs_def456",
    "limit": 5
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "obsId": "obs_abc123",
      "title": "Added PostgreSQL migration for users table",
      "type": "file_write",
      "score": 0.94,
      "timestamp": "2024-01-12T09:15:00Z",
      "expanded": {
        "narrative": "Created initial database schema using Prisma...",
        "facts": ["PostgreSQL 15", "Prisma ORM", "UUID primary keys"],
        "files": ["prisma/schema.prisma"]
      }
    }
  ],
  "totalMatches": 12
}
```

---

### memory_timeline

Chronological observations around an anchor point.

**Input Schema:**
```json
{
  "anchor": {
    "type": "string",
    "description": "Anchor point: ISO date or keyword",
    "required": true
  },
  "project": {
    "type": "string",
    "description": "Filter by project path"
  },
  "before": {
    "type": "number",
    "description": "Observations before anchor (default 5)"
  },
  "after": {
    "type": "number",
    "description": "Observations after anchor (default 5)"
  }
}
```

**Example (date anchor):**
```json
{
  "name": "memory_timeline",
  "arguments": {
    "anchor": "2024-01-15T10:00:00Z",
    "project": "/home/user/my-project",
    "before": 3,
    "after": 3
  }
}
```

**Example (keyword anchor):**
```json
{
  "name": "memory_timeline",
  "arguments": {
    "anchor": "authentication implementation",
    "before": 5,
    "after": 5
  }
}
```

---

### memory_profile

User/project profile with top concepts and file patterns.

**Input Schema:**
```json
{
  "project": {
    "type": "string",
    "description": "Project path",
    "required": true
  },
  "refresh": {
    "type": "string",
    "description": "Set to 'true' to force rebuild"
  }
}
```

**Example:**
```json
{
  "name": "memory_profile",
  "arguments": {
    "project": "/home/user/my-project",
    "refresh": "false"
  }
}
```

**Response:**
```json
{
  "project": "/home/user/my-project",
  "updatedAt": "2024-01-15T12:00:00Z",
  "topConcepts": [
    {"concept": "authentication", "frequency": 34},
    {"concept": "postgresql", "frequency": 28},
    {"concept": "typescript", "frequency": 56}
  ],
  "topFiles": [
    {"file": "src/middleware/auth.ts", "frequency": 12},
    {"file": "prisma/schema.prisma", "frequency": 9}
  ],
  "conventions": [
    "TypeScript interfaces before implementation",
    "Tests written alongside features",
    "Prisma for database access"
  ],
  "commonErrors": [
    "JWT token expiry handling",
    "Database connection pooling"
  ],
  "sessionCount": 23,
  "totalObservations": 1247
}
```

---

### memory_export

Export all memory data as JSON.

**Input Schema:**
```json
{}
```

**Example:**
```json
{
  "name": "memory_export",
  "arguments": {}
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
  "graphEdges": [...]
}
```

---

### memory_relations

Query the memory relationship graph.

**Input Schema:**
```json
{
  "memoryId": {
    "type": "string",
    "description": "Memory ID to find relations for",
    "required": true
  },
  "maxHops": {
    "type": "number",
    "description": "Max traversal depth (default 2)"
  },
  "minConfidence": {
    "type": "number",
    "description": "Min confidence (0-1, default 0)"
  }
}
```

**Example:**
```json
{
  "name": "memory_relations",
  "arguments": {
    "memoryId": "mem_abc123",
    "maxHops": 2,
    "minConfidence": 0.7
  }
}
```

**Response:**
```json
{
  "centerNode": {
    "id": "mem_abc123",
    "title": "JWT authentication with jose",
    "type": "preference"
  },
  "relations": [
    {
      "type": "extends",
      "target": {
        "id": "mem_def456",
        "title": "Authentication middleware pattern",
        "confidence": 0.89
      }
    },
    {
      "type": "related",
      "target": {
        "id": "mem_ghi789",
        "title": "Edge functions deployment",
        "confidence": 0.76
      }
    }
  ]
}
```

---

## Extended Tools (AGENTMEMORY_TOOLS=all)

### v0.40+ Tools

#### memory_claude_bridge_sync

Sync memory state to/from Claude Code's native MEMORY.md file.

```json
{
  "name": "memory_claude_bridge_sync",
  "arguments": {
    "direction": "write"  // or "read"
  }
}
```

#### memory_graph_query

Query the knowledge graph for entities and relationships.

```json
{
  "name": "memory_graph_query",
  "arguments": {
    "startNodeId": "mem_abc123",
    "nodeType": "file",
    "maxDepth": 3
  }
}
```

#### memory_consolidate

Consolidate related memories to reduce redundancy.

```json
{
  "name": "memory_consolidate",
  "arguments": {
    "memoryIds": "mem_abc123,mem_def456,mem_ghi789"
  }
}
```

#### memory_summarize

Summarize a session or set of observations.

```json
{
  "name": "memory_summarize",
  "arguments": {
    "sessionId": "session_xyz",
    "includeDecisions": true
  }
}
```

#### memory_evict

Remove memories below retention threshold.

```json
{
  "name": "memory_evict",
  "arguments": {
    "minRetentionScore": 0.1,
    "dryRun": true
  }
}
```

#### memory_enrich

Enrich observations with additional context from related memories.

```json
{
  "name": "memory_enrich",
  "arguments": {
    "observationIds": "obs_abc123,obs_def456"
  }
}
```

### Team Tools

#### memory_team_create

Create a new team for shared memories.

```json
{
  "name": "memory_team_create",
  "arguments": {
    "teamId": "backend-team",
    "name": "Backend Development Team"
  }
}
```

#### memory_team_share

Share memories with a team.

```json
{
  "name": "memory_team_share",
  "arguments": {
    "teamId": "backend-team",
    "memoryIds": "mem_abc123,mem_def456"
  }
}
```

#### memory_team_sync

Sync shared memories from team.

```json
{
  "name": "memory_team_sync",
  "arguments": {
    "teamId": "backend-team"
  }
}
```

### Advanced Tools

#### memory_snapshot

Create a point-in-time snapshot of memory state.

```json
{
  "name": "memory_snapshot",
  "arguments": {
    "label": "Before major refactor",
    "includeObservations": true
  }
}
```

#### memory_migrate

Migrate data from older versions or other systems.

```json
{
  "name": "memory_migrate",
  "arguments": {
    "source": "claude-mem",
    "filePath": "/path/to/export.json"
  }
}
```

#### memory_diagnostics

Run system diagnostics and health checks.

```json
{
  "name": "memory_diagnostics",
  "arguments": {
    "checkEmbeddings": true,
    "checkIndex": true
  }
}
```

#### memory_rebuild_index

Rebuild BM25 and vector indexes.

```json
{
  "name": "memory_rebuild_index",
  "arguments": {}
}
```

### Utility Tools

Complete list of remaining tools (18 more):

- `memory_actions` — Query action history
- `memory_checkpoints` — Manage session checkpoints
- `memory_crystallize` — Extract crystallized insights
- `memory_facets` — Multi-dimensional memory view
- `memory_frontier` — Explore knowledge frontiers
- `memory_lessons` — Extract lessons learned
- `memory_mesh` — Mesh network operations
- `memory_obsidian_export` — Export to Obsidian format
- `memory_reflect` — Reflective analysis
- `memory_retention` — Retention score management
- `memory_routines` — Routine pattern detection
- `memory_signals` — Signal-based triggers
- `memory_sketches` — Temporary memory sketches
- `memory_sliding_window` — Time-windowed queries
- `memory_temporal_graph` — Temporal graph traversal
- `memory_verify` — Memory verification
- `memory_working_memory` — Working memory operations
- `memory_skill_extract` — Extract skills from observations

## MCP Server Configuration

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "agentmemory",
      "args": ["mcp"],
      "env": {
        "AGENTMEMORY_SECRET": "your-secret"
      }
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/mcp.json`:

```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/agentmemory@0.8.10", "mcp"]
    }
  }
}
```

### Claude Desktop

Add to `~/.claude-desktop/mcp-config.json`:

```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "agentmemory",
      "args": ["mcp"]
    }
  }
}
```

### Custom MCP Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const client = new Client(
  { name: "my-agent", version: "1.0.0" },
  { url: "http://localhost:3111/agentmemory/mcp" }
);

await client.connect();

// List available tools
const tools = await client.listTools();

// Call a tool
const result = await client.callTool({
  name: "memory_recall",
  arguments: { query: "JWT auth", limit: 5 }
});
```
