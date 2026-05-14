# Multi-Agent Coordination

agentmemory provides primitives for coordinating work across multiple AI agents sharing the same memory store. All agents connect to the same server instance via MCP or REST API.

## Actions & Frontier

Actions are work items with dependencies, statuses, and priority ranking.

**Creating actions:**

```
memory_action_create(title: "Fix N+1 query in user loader",
                     description: "Add include: [posts] to User.findAll()",
                     dependsOn: ["mem-auth-fix"])
```

**Finding what to work on next:**

- `memory_frontier` — Returns unblocked actions ranked by priority (dependencies satisfied)
- `memory_next` — Returns the single most important next action

Actions support status updates via `memory_action_update(actionId, status)`.

## Leases

Exclusive leases prevent multiple agents from working on the same action simultaneously. A lease is time-bounded and auto-expires.

```
memory_lease(actionId: "act-001", agentId: "claude-code-1", ttl: 3600)
```

Leases use keyed mutex locking (`withKeyedLock`) for race safety. When one agent holds a lease, others see the action as blocked in `memory_frontier`.

## Signals

Inter-agent messaging with delivery receipts. Agents can send structured signals to coordinate workflow.

```
memory_signal_send(targetAgent: "cursor-1",
                   signal: "auth-module-complete",
                   payload: { filesModified: ["src/auth.ts"] })
```

Read received signals:

```
memory_signal_read(agentId: "cursor-1")
```

## Routines

Routines are reusable workflow templates that can be instantiated with parameters. They define a sequence of actions with dependencies.

```
memory_routine_run(routineName: "add-endpoint",
                   params: { path: "/api/rate-limit", method: "POST" })
```

## Checkpoints

External condition gates for workflow synchronization. Agents wait at checkpoints until conditions are met.

```
memory_checkpoint(name: "database-migration-complete", value: true)
```

## Mesh Sync

P2P synchronization between agentmemory instances across machines or networks. Requires `AGENTMEMORY_SECRET` configured on both peers for authentication (hardened in v0.8.2).

```
memory_mesh_sync(remoteUrl: "http://remote-machine:3111")
```

Mesh sync pushes and pulls memory state between instances, enabling distributed teams to share context.

## Sentinels

Event-driven watchers that trigger actions when conditions are met. Created with a condition specification and can be fired externally.

```
memory_sentinel_create(name: "watch-for-auth-errors",
                       condition: { hookType: "post_tool_failure", pattern: "auth" })
```

Trigger externally:

```
memory_sentinel_trigger(sentinelId: "sent-001")
```

## Sketches & Crystallization

Sketches are ephemeral action graphs for exploratory work — lightweight plans that can be promoted to permanent memory.

```
memory_sketch_create(title: "API redesign exploration",
                     actions: [{title: "Audit endpoints"}, {title: "Design new schema"}])
```

Promote to permanent memory when validated:

```
memory_sketch_promote(sketchId: "sketch-001")
```

Crystallize compacts action chains into consolidated memories:

```
memory_crystallize(actionChainId: "chain-001")
```

## Team Memory

Namespaced shared and private memory across team members. Requires `TEAM_ID` and `USER_ID` configuration.

- **Private mode** — Each member has isolated memory within the team namespace
- **Shared mode** — Memories are visible to all team members

Share specific memories:

```
memory_team_share(memoryId: "mem-001", teamIds: "team-alpha")
```

View shared feed:

```
memory_team_feed(limit: 20)
```

## Claude Bridge

Bi-directional sync with CLAUDE.md / MEMORY.md for Claude Code compatibility. When enabled (`CLAUDE_MEMORY_BRIDGE=true`), agentmemory writes structured summaries to the traditional memory file, allowing agents that read CLAUDE.md to access agentmemory's indexed context.

Sync manually:

```
memory_claude_bridge_sync()
```
