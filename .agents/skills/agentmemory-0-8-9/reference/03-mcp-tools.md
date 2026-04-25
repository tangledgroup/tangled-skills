# Extended MCP Tools Reference

Complete reference for all 43 MCP tools available in agentmemory. Set `AGENTMEMORY_TOOLS=all` to enable extended tools beyond the core 7.

## Core Tools (Always Available)

### memory_recall

Search past observations by keyword or semantic similarity.

**Input:**
```typescript
{
  query: string,           // Search query
  limit?: number,          // Max results (default: 10)
  sessionId?: string       // Filter by session
}
```

**Output:**
```typescript
{
  results: Array<{
    id: string,
    type: 'working' | 'episodic' | 'semantic' | 'procedural',
    title: string,
    narrative: string,
    score: number,
    sessionId: string,
    createdAt: string
  }>
}
```

**Example:**
```typescript
await memory_recall({
  query: "JWT authentication setup",
  limit: 5
});
```

---

### memory_save

Save an insight, decision, or pattern to long-term memory.

**Input:**
```typescript
{
  type: 'insight' | 'decision' | 'pattern' | 'bugfix' | 'config',
  title: string,
  narrative: string,
  concepts?: string[],      // or comma-separated string
  files?: string[],         // or comma-separated string
  sessionId?: string
}
```

**Output:**
```typescript
{
  id: string,
  savedAt: string,
  type: string
}
```

**Example:**
```typescript
await memory_save({
  type: 'decision',
  title: 'Chose jose over jsonwebtoken',
  narrative: 'Selected jose library for JWT handling due to Edge compatibility requirements. jsonwebtoken has native Node.js dependencies that prevent Edge deployment.',
  concepts: ['JWT', 'authentication', 'Edge functions'],
  files: ['src/middleware/auth.ts']
});
```

---

### memory_smart_search

Hybrid semantic + keyword search with BM25, vector, and knowledge graph fusion.

**Input:**
```typescript
{
  query: string,
  budget?: number,          // Token budget (default: 2000)
  minConfidence?: number,   // Min score threshold (default: 0.5)
  sessionId?: string
}
```

**Output:**
```typescript
{
  results: Array<{
    id: string,
    content: string,
    score: number,
    source: 'bm25' | 'vector' | 'graph',
    citations: Array<{
      observationId: string,
      sessionId: string
    }>
  }>,
  tokenCount: number
}
```

**Example:**
```typescript
await memory_smart_search({
  query: "database performance optimization",
  budget: 3000
});
// Finds "N+1 query fix" even though query doesn't contain those keywords
```

---

### memory_file_history

Get past observations about specific files.

**Input:**
```typescript
{
  filePath: string,         // e.g., 'src/middleware/auth.ts'
  limit?: number
}
```

**Output:**
```typescript
{
  observations: Array<{
    id: string,
    tool: string,
    input: string,
    output: string,
    timestamp: string
  }>
}
```

**Example:**
```typescript
await memory_file_history({
  filePath: 'src/utils/auth.ts',
  limit: 10
});
```

---

### memory_sessions

List recent sessions with summaries.

**Input:**
```typescript
{
  limit?: number,           // Default: 20
  projectId?: string
}
```

**Output:**
```typescript
{
  sessions: Array<{
    id: string,
    project: string,
    startedAt: string,
    endedAt: string,
    observationCount: number,
    summary?: string
  }>
}
```

**Example:**
```typescript
await memory_sessions({ limit: 5 });
```

---

### memory_profile

Get project profile with top concepts, files, and patterns.

**Input:**
```typescript
{
  projectId?: string
}
```

**Output:**
```typescript
{
  project: string,
  topConcepts: Array<{ concept: string, count: number }>,
  topFiles: Array<{ file: string, accessCount: number }>,
  patterns: Array<{
    type: string,
    title: string,
    description: string
  }>,
  totalObservations: number,
  totalSessions: number
}
```

**Example:**
```typescript
await memory_profile();
```

---

### memory_export

Export all memory data for backup or migration.

**Input:**
```typescript
{
  format?: 'json' | 'obsidian',
  includeObservations?: boolean,  // Default: true
  includeMemories?: boolean,      // Default: true
  vaultDir?: string               // For Obsidian format
}
```

**Output:**
```typescript
{
  exportedAt: string,
  path: string,                   // For Obsidian
  data: object                    // For JSON format
}
```

**Example:**
```typescript
await memory_export({
  format: 'json',
  includeObservations: true
});
```

---

## Extended Tools (Set `AGENTMEMORY_TOOLS=all`)

### Pattern Detection

#### memory_patterns

Detect recurring patterns across sessions.

**Input:**
```typescript
{
  minOccurrences?: number,   // Default: 3
  timeframe?: string         // e.g., '7d', '30d'
}
```

**Output:**
```typescript
{
  patterns: Array<{
    type: string,
    title: string,
    occurrences: number,
    examples: Array<string>,
    firstSeen: string,
    lastSeen: string
  }>
}
```

---

#### memory_timeline

Get chronological observations.

**Input:**
```typescript
{
  startTime?: string,        // ISO 8601
  endTime?: string,          // ISO 8601
  sessionId?: string,
  limit?: number
}
```

**Output:**
```typescript
{
  observations: Array<{
    id: string,
    timestamp: string,
    type: string,
    title: string,
    sessionId: string
  }>
}
```

---

### Knowledge Graph

#### memory_relations

Query relationship graph between entities.

**Input:**
```typescript
{
  entity: string,            // Entity name to query
  depth?: number             // BFS depth (default: 2)
}
```

**Output:**
```typescript
{
  entity: string,
  relations: Array<{
    relatedEntity: string,
    relationType: string,
    strength: number,
    path: Array<string>
  }>
}
```

---

#### memory_graph_query

Traverse knowledge graph with BFS.

**Input:**
```typescript
{
  startEntity: string,
  maxDepth?: number,
  relationFilter?: string[]
}
```

**Output:**
```typescript
{
  nodes: Array<{
    entity: string,
    type: string,
    connections: number
  }>,
  edges: Array<{
    source: string,
    target: string,
    relation: string
  }>
}
```

---

### Consolidation and Governance

#### memory_consolidate

Run 4-tier memory consolidation manually.

**Input:**
```typescript
{
  sessionId?: string,        // Optional: specific session
  force?: boolean            // Force even if recent
}
```

**Output:**
```typescript
{
  consolidated: number,      // Count of memories consolidated
  tiers: {
    working: number,
    episodic: number,
    semantic: number,
    procedural: number
  }
}
```

---

#### memory_claude_bridge_sync

Sync with Claude Code's MEMORY.md.

**Input:**
```typescript
{
  direction: 'to-claude' | 'from-claude' | 'bidirectional'
}
```

**Output:**
```typescript
{
  synced: number,            // Count of items synced
  direction: string,
  timestamp: string
}
```

---

#### memory_governance_delete

Delete memories with audit trail.

**Input:**
```typescript
{
  memoryIds: string[] | string,  // Array or comma-separated string
  reason: string                 // Required for audit
}
```

**Output:**
```typescript
{
  deleted: Array<string>,        // Successfully deleted IDs
  requested: Array<string>,      // All requested IDs
  reason: string,
  timestamp: string
}
```

---

#### memory_audit

Get audit trail of operations.

**Input:**
```typescript
{
  operationType?: string,   // 'create', 'update', 'delete'
  startTime?: string,
  endTime?: string,
  limit?: number
}
```

**Output:**
```typescript
{
  entries: Array<{
    timestamp: string,
    operation: string,
    entityId: string,
    actor: string,
    details: object
  }>
}
```

---

#### memory_snapshot_create

Create git-versioned memory snapshot.

**Input:**
```typescript
{
  name: string,
  message?: string
}
```

**Output:**
```typescript
{
  snapshotId: string,
  name: string,
  createdAt: string,
  memoryCount: number
}
```

---

### Team Memory

#### memory_team_share

Share memories with team members.

**Input:**
```typescript
{
  memoryIds: string[],
  teamId: string,
  visibility: 'team' | 'public'
}
```

**Output:**
```typescript
{
  shared: Array<string>,
  teamId: string,
  timestamp: string
}
```

---

#### memory_team_feed

Get recent shared items from team.

**Input:**
```typescript
{
  teamId: string,
  limit?: number,
  userId?: string             // Filter by user
}
```

**Output:**
```typescript
{
  items: Array<{
    id: string,
    title: string,
    sharedBy: string,
    sharedAt: string,
    visibility: string
  }>
}
```

---

### Actions and Coordination

#### memory_action_create

Create work items with dependencies.

**Input:**
```typescript
{
  title: string,
  description: string,
  dependencies?: string[],    // Action IDs
  priority?: number,          // 1-10
  estimatedTokens?: number
}
```

**Output:**
```typescript
{
  actionId: string,
  status: 'pending' | 'blocked' | 'ready',
  createdAt: string
}
```

---

#### memory_action_update

Update action status.

**Input:**
```typescript
{
  actionId: string,
  status: 'pending' | 'in-progress' | 'completed' | 'blocked',
  notes?: string
}
```

**Output:**
```typescript
{
  actionId: string,
  status: string,
  updatedAt: string
}
```

---

#### memory_frontier

Get unblocked actions ranked by priority.

**Input:**
```typescript
{
  limit?: number,
  includeBlocked?: boolean
}
```

**Output:**
```typescript
{
  actions: Array<{
    id: string,
    title: string,
    priority: number,
    status: string,
    dependencies: Array<string>
  }>
}
```

---

#### memory_next

Get single most important next action.

**Input:**
```typescript
{}
```

**Output:**
```typescript
{
  action: {
    id: string,
    title: string,
    description: string,
    priority: number,
    whyNow: string
  } | null
}
```

---

### Multi-Agent Coordination

#### memory_lease

Claim exclusive lease on an action (multi-agent coordination).

**Input:**
```typescript
{
  actionId: string,
  agentId: string,
  duration?: number          // Seconds (default: 300)
}
```

**Output:**
```typescript
{
  leaseId: string,
  actionId: string,
  agentId: string,
  expiresAt: string,
  granted: boolean           // False if already leased
}
```

---

#### memory_signal_send

Send threaded messages between agents.

**Input:**
```typescript
{
  targetAgentId: string,
  channel: string,           // e.g., 'auth-work', 'database'
  message: string,
  parentId?: string          // For threading
}
```

**Output:**
```typescript
{
  signalId: string,
  sentAt: string,
  deliveryStatus: 'sent' | 'delivered' | 'read'
}
```

---

#### memory_signal_read

Read messages with read receipts.

**Input:**
```typescript
{
  agentId: string,           // Read messages for this agent
  channel?: string,
  unreadOnly?: boolean
}
```

**Output:**
```typescript
{
  messages: Array<{
    id: string,
    fromAgentId: string,
    channel: string,
    message: string,
    sentAt: string,
    readAt: string | null,
    parentId: string | null
  }>
}
```

---

#### memory_checkpoint

Create external condition gates.

**Input:**
```typescript
{
  name: string,
  condition: string,         // e.g., 'tests-passing', 'deployed'
  actionId?: string          // Optional: gate specific action
}
```

**Output:**
```typescript
{
  checkpointId: string,
  name: string,
  status: 'pending' | 'satisfied',
  createdAt: string
}
```

---

#### memory_mesh_sync

P2P sync between agentmemory instances.

**Input:**
```typescript
{
  remoteUrl: string,         // Remote instance URL
  secret: string,            // Required for auth
  direction: 'push' | 'pull' | 'bidirectional'
}
```

**Output:**
```typescript
{
  synced: number,            // Count of items synced
  remoteUrl: string,
  direction: string,
  timestamp: string
}
```

---

### Routines and Automation

#### memory_routine_run

Instantiate workflow routines.

**Input:**
```typescript
{
  routineName: string,       // e.g., 'add-auth', 'setup-database'
  parameters?: object
}
```

**Output:**
```typescript
{
  instanceId: string,
  routineName: string,
  steps: Array<{
    id: string,
    title: string,
    order: number
  }>,
  startedAt: string
}
```

---

#### memory_sentinel_create

Create event-driven watchers.

**Input:**
```typescript
{
  name: string,
  condition: string,         // e.g., 'file-modified:src/auth.ts'
  action: string             // e.g., 'notify', 'run-routine'
}
```

**Output:**
```typescript
{
  sentinelId: string,
  name: string,
  active: boolean,
  createdAt: string
}
```

---

#### memory_sentinel_trigger

Fire sentinels externally.

**Input:**
```typescript
{
  sentinelId: string,
  event: object
}
```

**Output:**
```typescript
{
  triggered: boolean,
  sentinelId: string,
  timestamp: string
}
```

---

### Ephemeral Memory

#### memory_sketch_create

Create ephemeral action graphs.

**Input:**
```typescript
{
  title: string,
  nodes: Array<{
    id: string,
    type: string,
    data: object
  }>,
  edges: Array<{
    from: string,
    to: string
  }>
}
```

**Output:**
```typescript
{
  sketchId: string,
  title: string,
  ttl: number,               // Seconds until expiry
  createdAt: string
}
```

---

#### memory_sketch_promote

Promote sketch to permanent memory.

**Input:**
```typescript
{
  sketchId: string
}
```

**Output:**
```typescript
{
  promoted: boolean,
  memoryIds: Array<string>,
  timestamp: string
}
```

---

### Advanced Operations

#### memory_crystallize

Compact action chains into procedural memory.

**Input:**
```typescript
{
  actionChainIds: string[],
  title?: string
}
```

**Output:**
```typescript
{
  crystallizedId: string,
  type: 'procedural',
  stepCount: number,
  timestamp: string
}
```

---

#### memory_diagnose

Run health checks and diagnostics.

**Input:**
```typescript
{}
```

**Output:**
```typescript
{
  status: 'healthy' | 'degraded' | 'unhealthy',
  checks: Array<{
    name: string,
    status: 'pass' | 'fail' | 'warn',
    message: string
  }>,
  recommendations: Array<string>
}
```

---

#### memory_heal

Auto-fix stuck state.

**Input:**
```typescript
{
  force?: boolean
}
```

**Output:**
```typescript
{
  healed: boolean,
  actions: Array<string>,    // What was fixed
  timestamp: string
}
```

---

#### memory_facet_tag

Add dimension:value tags to memories.

**Input:**
```typescript
{
  memoryId: string,
  facets: Array<{
    dimension: string,       // e.g., 'auth', 'database'
    value: string            // e.g., 'JWT', 'PostgreSQL'
  }>
}
```

**Output:**
```typescript
{
  memoryId: string,
  tagged: number,            // Count of facets added
  timestamp: string
}
```

---

#### memory_facet_query

Query by facet tags.

**Input:**
```typescript
{
  facets: Array<{
    dimension: string,
    value: string
  }>,
  operator?: 'AND' | 'OR'    // Default: 'AND'
}
```

**Output:**
```typescript
{
  results: Array<{
    id: string,
    title: string,
    facets: Array<string>
  }>
}
```

---

#### memory_verify

Trace provenance of a memory.

**Input:**
```typescript
{
  memoryId: string
}
```

**Output:**
```typescript
{
  memoryId: string,
  sourceObservations: Array<{
    id: string,
    sessionId: string,
    timestamp: string
  }>,
  transformations: Array<{
    type: string,
    timestamp: string,
    details: object
  }>
}
```

---

## Tool Usage Examples

### Complete Workflow Example

```typescript
// Session start: get context
const context = await memory_smart_search({
  query: "current project state",
  budget: 2000
});

// During work: save important decisions
await memory_save({
  type: 'decision',
  title: 'Selected PostgreSQL over SQLite',
  narrative: 'Chose PostgreSQL for production due to concurrent write requirements and JSONB support for flexible metadata storage.',
  concepts: ['database', 'PostgreSQL', 'production'],
  files: ['prisma/schema.prisma']
});

// Track file changes
const history = await memory_file_history({
  filePath: 'src/api/auth.ts'
});

// Session end: consolidate
await memory_consolidate({ sessionId: currentSessionId });
```

### Multi-Agent Coordination Example

```typescript
// Agent A claims exclusive work
const lease = await memory_lease({
  actionId: 'fix-auth-bug',
  agentId: 'agent-a',
  duration: 600  // 10 minutes
});

if (lease.granted) {
  // Do the work...
  
  // Notify other agents
  await memory_signal_send({
    targetAgentId: 'agent-b',
    channel: 'auth-work',
    message: 'Fixed JWT validation bug, tests passing'
  });
  
  // Complete the action
  await memory_action_update({
    actionId: 'fix-auth-bug',
    status: 'completed'
  });
}
```

### Team Collaboration Example

```typescript
// Share key findings with team
await memory_team_share({
  memoryIds: ['mem-123', 'mem-456'],
  teamId: 'backend-team',
  visibility: 'team'
});

// Check what others have shared
const feed = await memory_team_feed({
  teamId: 'backend-team',
  limit: 10
});
```

## Tool Visibility Control

Control which tools are exposed to agents:

```env
# Only core 7 tools (safe default)
AGENTMEMORY_TOOLS=core

# All 43 tools (advanced users)
AGENTMEMORY_TOOLS=all
```

Core tools are sufficient for most use cases. Extended tools provide advanced capabilities for multi-agent coordination, team collaboration, and workflow automation.
