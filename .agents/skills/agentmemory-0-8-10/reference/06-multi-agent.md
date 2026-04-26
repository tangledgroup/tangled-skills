# Multi-Agent Coordination

agentmemory supports multi-agent workflows through a shared memory server with coordination primitives. All agents connect to the same instance via MCP or REST API.

## Leases

Exclusive action leases prevent multiple agents from working on the same task simultaneously:

```typescript
// Acquire lease
memory_lease({
  actionId: "action_abc123",
  agentId: "agent-1",
  operation: "acquire",
  ttlMs: 300000  // 5 minutes
})

// Renew lease before expiry
memory_lease({
  actionId: "action_abc123",
  agentId: "agent-1",
  operation: "renew",
  ttlMs: 300000
})

// Release lease with result
memory_lease({
  actionId: "action_abc123",
  agentId: "agent-1",
  operation: "release",
  result: "Completed auth middleware"
})
```

Leases use keyed mutex for race-safe acquisition. Expired leases auto-release.

## Actions and Frontier

Actions are work items with dependencies, priorities, and status tracking:

```typescript
// Create action with dependencies
memory_action_create({
  title: "Implement rate limiting",
  description: "Add express-rate-limit to API routes",
  priority: "high",
  project: "my-app",
  tags: ["security", "api"],
  requires: "action_auth,action_db"  // comma-separated action IDs
})

// Get unblocked actions ranked by priority
memory_frontier({
  project: "my-app",
  agentId: "agent-1",
  limit: 5
})

// Get single most important next action
memory_next({
  project: "my-app",
  agentId: "agent-1"
})
```

Action edges define `requires` relationships. The frontier returns actions whose dependencies are all completed, sorted by priority.

## Signals

Inter-agent messaging with delivery receipts:

```typescript
// Send signal
memory_signal_send({
  from: "agent-1",
  to: "agent-2",       // optional, omit for broadcast
  content: "Auth middleware complete, proceed with rate limiting",
  type: "status-update"
})

// Read signals
memory_signal_read({
  agentId: "agent-2",
  limit: 10
})
```

## Routines

Reusable workflow templates that instantiate as action chains:

```typescript
memory_routine_run({
  routineId: "security-audit",
  project: "my-app",
  initiatedBy: "agent-1"
})
```

Routines define sequences of actions with dependencies. Running a routine creates all its actions and edges in one transaction.

## Checkpoints

External condition gates that block action progress until conditions are met:

```typescript
memory_checkpoint({
  // Create or check checkpoint conditions
  // Actions can wait on checkpoints before proceeding
})
```

## Mesh Sync

P2P synchronization between agentmemory instances across machines:

- Requires `AGENTMEMORY_SECRET` on both peers
- Syncs memories, actions, semantic/procedural memories, relations, and graph data
- Uses Last-Writer-Wins (LWW) merge for conflict resolution
- Validates peer URLs against private IP ranges for security
- Default shared scopes: memories, actions, semantic, procedural, relations, graph:nodes, graph:edges

## Team Memory

Namespaced shared and private memories across team members:

```env
TEAM_ID=my-team
USER_ID=alice
TEAM_MODE=shared  # or "private"
```

- `memory_team_share` — share a memory item with the team
- `memory_team_feed` — recent items shared by team members
- Team data stored in separate KV namespaces: `mem:team:<teamId>:shared`, `mem:team:<teamId>:users:<userId>`

## Sentinels

Event-driven watchers that trigger on conditions:

```typescript
memory_sentinel_create({
  // Define event-driven watcher
})
memory_sentinel_trigger({
  // Fire sentinels externally
})
```

## Sketches

Ephemeral action graphs for exploratory work:

```typescript
memory_sketch_create({
  // Create temporary action graph
})
memory_sketch_promote({
  // Promote sketch to permanent actions
})
```

Sketches are temporary by default. `promote` makes them permanent in the action system.

## Crystallization

Compact action chains into consolidated memories:

```typescript
memory_crystallize({
  // Compact completed action chains into procedural memory
})
```
