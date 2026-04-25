# agentmemory Advanced Features

## Team Collaboration

### Shared Memories

Teams can share memories across members while maintaining personal observation history.

**Create a team:**
```bash
curl -X POST http://localhost:3111/agentmemory/team/create \
  -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  -d '{
    "teamId": "backend-team",
    "name": "Backend Development Team",
    "description": "Shared architecture decisions and patterns"
  }'
```

**Share specific memories:**
```bash
curl -X POST http://localhost:3111/agentmemory/team/share \
  -d '{
    "teamId": "backend-team",
    "memoryIds": ["mem_arch_decision_123", "mem_api_pattern_456"]
  }'
```

**Sync from team:**
```bash
# Pull shared memories from team
curl -X POST http://localhost:3111/agentmemory/team/sync \
  -d '{"teamId": "backend-team"}'
```

**Team profile:**
```bash
# Get aggregated team knowledge
curl -X POST http://localhost:3111/agentmemory/team/profile \
  -d '{"teamId": "backend-team"}'
```

### Governance

Control who can share what with teams.

```bash
# Set governance policies
curl -X POST http://localhost:3111/agentmemory/governance/set \
  -d '{
    "teamId": "backend-team",
    "policies": {
      "requireApproval": false,
      "allowedTypes": ["architecture", "pattern", "workflow"],
      "maxMemoriesPerUser": 50,
      "retentionDays": 365
    }
  }'
```

## Snapshots

Point-in-time memory state for rollback or comparison.

### Create Snapshot

```bash
curl -X POST http://localhost:3111/agentmemory/snapshot/create \
  -d '{
    "label": "Before authentication refactor",
    "description": "Baseline before implementing OAuth2",
    "includeObservations": true,
    "includeGraph": true,
    "tags": ["auth", "refactor", "baseline"]
  }'
```

### List Snapshots

```bash
curl http://localhost:3111/agentmemory/snapshot/list
```

### Compare Snapshots

```bash
curl -X POST http://localhost:3111/agentmemory/snapshot/compare \
  -d '{
    "snapshotId1": "snap_before_refactor",
    "snapshotId2": "snap_after_refactor"
  }'
```

**Response:**
```json
{
  "addedMemories": 12,
  "removedMemories": 3,
  "modifiedMemories": 5,
  "newConcepts": ["oauth2", "openid-connect"],
  "removedConcepts": ["basic-auth"]
}
```

### Restore from Snapshot

```bash
curl -X POST http://localhost:3111/agentmemory/snapshot/restore \
  -d '{
    "snapshotId": "snap_before_refactor",
    "merge": true,  // Merge with current or replace
    "dryRun": false
  }'
```

## Mesh Network

Distributed memory synchronization across multiple agentmemory instances.

### Configure Mesh Node

```bash
# Set mesh configuration
curl -X POST http://localhost:3111/agentmemory/mesh/configure \
  -d '{
    "nodeId": "alice-laptop",
    "nodeName": "Alice Development Machine",
    "peers": [
      {
        "nodeId": "bob-desktop",
        "url": "http://bob-desktop:3111/agentmemory"
      },
      {
        "nodeId": "ci-runner",
        "url": "http://ci-server:3111/agentmemory"
      }
    ],
    "syncIntervalMs": 60000,
    "authToken": "mesh-auth-token"
  }'
```

### Mesh Operations

**Sync with peers:**
```bash
curl -X POST http://localhost:3111/agentmemory/mesh/sync
```

**Broadcast memory:**
```bash
curl -X POST http://localhost:3111/agentmemory/mesh/broadcast \
  -d '{"memoryId": "mem_abc123"}'
```

**Get mesh status:**
```bash
curl http://localhost:3111/agentmemory/mesh/status
```

## Actions and Routines

### Action History

Track agent actions for pattern detection.

```bash
# Get action history
curl -X POST http://localhost:3111/agentmemory/actions/query \
  -d '{
    "sessionId": "session_abc123",
    "actionTypes": ["file_write", "command_run"],
    "limit": 50
  }'
```

### Routine Detection

Identify recurring multi-step workflows.

```bash
curl -X POST http://localhost:3111/agentmemory/routines/detect \
  -d '{
    "project": "/home/user/my-project",
    "minOccurrences": 3,
    "maxSteps": 10
  }'
```

**Response:**
```json
{
  "routines": [
    {
      "id": "routine_123",
      "name": "Add new API endpoint",
      "steps": [
        {"action": "file_write", "pattern": "src/api/*.ts"},
        {"action": "file_write", "pattern": "src/services/*.ts"},
        {"action": "command_run", "pattern": "npm test"}
      ],
      "occurrences": 12,
      "avgDurationMs": 345000
    }
  ]
}
```

### Routine Execution

Trigger automated routine execution.

```bash
curl -X POST http://localhost:3111/agentmemory/routines/run \
  -d '{
    "routineId": "routine_123",
    "parameters": {
      "endpointName": "users",
      "method": "GET"
    }
  }'
```

## Checkpoints

Save and restore agent state at key points.

### Create Checkpoint

```bash
curl -X POST http://localhost:3111/agentmemory/checkpoint/create \
  -d '{
    "label": "Before complex refactoring",
    "sessionId": "session_abc123",
    "includeWorkingMemory": true
  }'
```

### List Checkpoints

```bash
curl http://localhost:3111/agentmemory/checkpoint/list \
  ?sessionId=session_abc123
```

### Restore Checkpoint

```bash
curl -X POST http://localhost:3111/agentmemory/checkpoint/restore \
  -d '{"checkpointId": "ckpt_123"}'
```

## Sentinels

Automated monitoring and alerting on memory patterns.

### Create Sentinel

```bash
curl -X POST http://localhost:3111/agentmemory/sentinels/create \
  -d '{
    "name": "Detect authentication issues",
    "condition": {
      "type": "pattern_match",
      "query": "authentication error OR login failed",
      "threshold": 3,
      "windowMinutes": 60
    },
    "action": {
      "type": "alert",
      "channel": "webhook",
      "url": "https://hooks.slack.com/services/xxx"
    }
  }'
```

### Sentinel Types

- **pattern_match** — Trigger on search query matches
- **frequency_threshold** — Trigger on observation frequency
- **retention_drop** — Trigger when retention scores drop
- **graph_change** — Trigger on knowledge graph modifications

## Crystallization

Extract high-confidence insights from memories.

### Crystallize Memories

```bash
curl -X POST http://localhost:3111/agentmemory/crystallize \
  -d '{
    "project": "/home/user/my-project",
    "minConfidence": 0.8,
    "types": ["architecture", "pattern"]
  }'
```

**Response:**
```json
{
  "crystals": [
    {
      "id": "crystal_123",
      "title": "Authentication Architecture",
      "content": "This project uses JWT with jose library for Edge compatibility...",
      "confidence": 0.94,
      "sourceMemories": ["mem_abc123", "mem_def456"],
      "concepts": ["jwt", "auth", "edge-functions"]
    }
  ]
}
```

## Lessons Learned

Extract and track lessons from past work.

### Add Lesson

```bash
curl -X POST http://localhost:3111/agentmemory/lessons/add \
  -d '{
    "title": "Database connection pooling",
    "content": "Always set max connections based on CPU cores * 2",
    "category": "performance",
    "tags": ["database", "postgresql", "connections"],
    "lessonType": "mistake-avoided"
  }'
```

### Query Lessons

```bash
curl -X POST http://localhost:3111/agentmemory/lessons/query \
  -d '{
    "query": "database performance",
    "category": "performance"
  }'
```

## Reflection

LLM-powered reflection on agent behavior.

### Trigger Reflection

```bash
curl -X POST http://localhost:3111/agentmemory/reflect \
  -d '{
    "sessionId": "session_abc123",
    "focus": ["tool_usage", "decision_quality"],
    "maxTokens": 2000
  }'
```

**Response:**
```json
{
  "reflection": {
    "strengths": [
      "Consistent use of TypeScript interfaces",
      "Good test coverage for critical paths"
    ],
    "improvements": [
      "Consider adding integration tests for API endpoints",
      "Document error handling patterns"
    ],
    "patterns": [
      "Tends to implement before writing tests",
      "Prefers functional programming style"
    ]
  }
}
```

## Working Memory

Short-term context for active sessions.

### Set Working Memory

```bash
curl -X POST http://localhost:3111/agentmemory/working-memory/set \
  -d '{
    "sessionId": "session_abc123",
    "items": [
      {"key": "current-task", "value": "Implementing OAuth2"},
      {"key": "blockers", "value": "Need API keys from team"}
    ]
  }'
```

### Get Working Memory

```bash
curl http://localhost:3111/agentmemory/working-memory/get \
  ?sessionId=session_abc123
```

## Frontier Exploration

Identify knowledge gaps and exploration opportunities.

### Analyze Frontiers

```bash
curl -X POST http://localhost:3111/agentmemory/frontier/analyze \
  -d '{
    "project": "/home/user/my-project",
    "excludeConcepts": ["jwt", "auth", "postgresql"]
  }'
```

**Response:**
```json
{
  "frontiers": [
    {
      "concept": "caching",
      "relevance": 0.87,
      "reasoning": "High traffic endpoints detected, no caching strategy observed"
    },
    {
      "concept": "rate-limiting",
      "relevance": 0.76,
      "reasoning": "Public API endpoints without rate limiting"
    }
  ]
}
```

## Facets

Multi-dimensional memory views.

### Query by Facet

```bash
curl -X POST http://localhost:3111/agentmemory/facets/query \
  -d '{
    "facets": {
      "type": ["architecture", "pattern"],
      "concepts": ["jwt", "auth"],
      "files": ["src/middleware/*"]
    },
    "operator": "AND"  // or "OR"
  }'
```

## Temporal Graph

Time-aware knowledge graph traversal.

### Query Temporal Relations

```bash
curl -X POST http://localhost:3111/agentmemory/temporal-graph/query \
  -d '{
    "nodeId": "mem_abc123",
    "startTime": "2024-01-01T00:00:00Z",
    "endTime": "2024-01-31T23:59:59Z"
  }'
```

**Response:**
```json
{
  "temporalEdges": [
    {
      "source": "mem_abc123",
      "target": "mem_def456",
      "type": "supersedes",
      "validFrom": "2024-01-15T10:00:00Z",
      "validTo": null  // Still valid
    }
  ]
}
```

## Retention Management

### View Retention Scores

```bash
curl -X POST http://localhost:3111/agentmemory/retention/scores \
  -d '{
    "project": "/home/user/my-project",
    "minScore": 0.5
  }'
```

### Adjust Retention

```bash
curl -X POST http://localhost:3111/agentmemory/retention/adjust \
  -d '{
    "memoryId": "mem_abc123",
    "score": 0.9,
    "reason": "Critical architecture decision"
  }'
```

### Auto-Forget Configuration

```bash
curl -X POST http://localhost:3111/agentmemory/auto-forget/configure \
  -d '{
    "minRetentionScore": 0.1,
    "maxAgeDays": 365,
    "excludeTypes": ["architecture"],
    "dryRun": false
  }'
```

## Skill Extraction

Extract reusable skills from observations.

### Extract Skills

```bash
curl -X POST http://localhost:3111/agentmemory/skill-extract \
  -d '{
    "sessionId": "session_abc123",
    "minConfidence": 0.7
  }'
```

**Response:**
```json
{
  "skills": [
    {
      "name": "implement-jwt-authentication",
      "description": "Add JWT-based authentication using jose library",
      "steps": [
        "Install jose dependency",
        "Create auth middleware",
        "Add token validation",
        "Implement refresh logic"
      ],
      "confidence": 0.89
    }
  ]
}
```

## Query Expansion

Automatic query rewriting for better recall.

### Enable Query Expansion

```bash
curl -X POST http://localhost:3111/agentmemory/query-expansion/enable \
  -d '{
    "maxExpansions": 3,
    "minConfidence": 0.6
  }'
```

**Example:**
- Original query: "JWT auth"
- Expanded queries: ["JWT authentication", "token-based auth", "jose library"]

## Sliding Window Queries

Time-windowed observation queries.

### Query with Window

```bash
curl -X POST http://localhost:3111/agentmemory/sliding-window/query \
  -d '{
    "anchor": "2024-01-15T10:00:00Z",
    "windowBeforeMinutes": 60,
    "windowAfterMinutes": 30,
    "project": "/home/user/my-project"
  }'
```

## Signals

Event-based triggers for automated actions.

### Create Signal

```bash
curl -X POST http://localhost:3111/agentmemory/signals/create \
  -d '{
    "name": "High-frequency file edits",
    "trigger": {
      "type": "observation_rate",
      "threshold": 10,
      "windowMinutes": 5
    },
    "action": {
      "type": "summarize",
      "target": "current_session"
    }
  }'
```

## Sketches

Temporary memory for exploration.

### Create Sketch

```bash
curl -X POST http://localhost:3111/agentmemory/sketches/create \
  -d '{
    "title": "Exploring caching strategies",
    "content": "Redis vs Memcached comparison notes...",
    "ttlMinutes": 60,
    "promoteToMemory": false
  }'
```

### Promote Sketch to Memory

```bash
curl -X POST http://localhost:3111/agentmemory/sketches/promote \
  -d '{"sketchId": "sketch_123"}'
```
