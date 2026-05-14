# MCP Tools Reference

agentmemory exposes 43 MCP tools through the stdio transport. By default, only 7 core tools are visible. Set `AGENTMEMORY_TOOLS=all` to expose all 43.

## Core Tools (always available)

### memory_recall

Search past observations using keyword matching.

```
memory_recall(query: string, limit?: number)
```

### memory_save

Save an insight, decision, or pattern to long-term memory. Accepts `concepts` and `files` as arrays or comma-separated strings.

```
memory_save(title: string, content: string, type?: string, concepts?: string|string[], files?: string|string[])
```

### memory_smart_search

Hybrid semantic + keyword search combining BM25, vector, and graph signals with RRF fusion. In standalone MCP mode, falls back to substring filter since BM25/vector/graph require the full engine.

```
memory_smart_search(query: string, limit?: number)
```

### memory_file_history

Past observations about specific files.

```
memory_file_history(file: string, limit?: number)
```

### memory_sessions

List recent sessions. Honors a `limit` argument (default 20).

```
memory_sessions(limit?: number)
```

### memory_profile

Project profile containing top concepts, files, and patterns.

```
memory_profile()
```

### memory_export

Export all memory data as JSON.

```
memory_export()
```

## Extended Tools (AGENTMEMORY_TOOLS=all)

### Pattern Detection

**memory_patterns** — Detect recurring patterns across sessions.

```
memory_patterns(limit?: number)
```

### Timeline & Relations

**memory_timeline** — Chronological observations within a session or across sessions.

```
memory_timeline(sessionId?: string, limit?: number)
```

**memory_relations** — Query the relationship graph between memories.

```
memory_relations(memoryId: string)
```

**memory_graph_query** — Knowledge graph traversal via entity matching.

```
memory_graph_query(entity: string, depth?: number)
```

### Consolidation & Sync

**memory_consolidate** — Run the 4-tier consolidation pipeline manually.

```
memory_consolidate()
```

**memory_claude_bridge_sync** — Bi-directional sync with CLAUDE.md / MEMORY.md.

```
memory_claude_bridge_sync()
```

### Team Memory

**memory_team_share** — Share a memory with team members (requires TEAM_ID + USER_ID).

```
memory_team_share(memoryId: string, teamIds?: string)
```

**memory_team_feed** — Recent shared items from team members.

```
memory_team_feed(limit?: number)
```

### Governance & Audit

**memory_audit** — Audit trail of all memory operations.

```
memory_audit(limit?: number)
```

**memory_governance_delete** — Delete memories with audit trail. Accepts `memoryIds` as array or comma-separated string, returns `{deleted, requested, reason}`.

```
memory_governance_delete(memoryIds: string|string[])
```

### Snapshots

**memory_snapshot_create** — Create a git-versioned snapshot of memory state for rollback and diff.

```
memory_snapshot_create(label?: string)
```

### Actions & Frontier

**memory_action_create** — Create work items with dependencies.

```
memory_action_create(title: string, description: string, dependsOn?: string[])
```

**memory_action_update** — Update action status.

```
memory_action_update(actionId: string, status: string)
```

**memory_frontier** — Unblocked actions ranked by priority.

```
memory_frontier(limit?: number)
```

**memory_next** — Single most important next action.

```
memory_next()
```

### Multi-Agent Coordination

**memory_lease** — Exclusive action leases for multi-agent coordination.

```
memory_lease(actionId: string, agentId: string, ttl?: number)
```

**memory_routine_run** — Instantiate workflow routines.

```
memory_routine_run(routineName: string, params?: object)
```

**memory_signal_send** — Inter-agent messaging with receipts.

```
memory_signal_send(targetAgent: string, signal: string, payload?: object)
```

**memory_signal_read** — Read messages from other agents.

```
memory_signal_read(agentId?: string)
```

**memory_checkpoint** — External condition gates for workflow synchronization.

```
memory_checkpoint(name: string, value?: unknown)
```

### Mesh Sync & Sentinels

**memory_mesh_sync** — P2P sync between agentmemory instances (requires AGENTMEMORY_SECRET on both peers).

```
memory_mesh_sync(remoteUrl: string)
```

**memory_sentinel_create** — Event-driven watchers that trigger on conditions.

```
memory_sentinel_create(name: string, condition: object)
```

**memory_sentinel_trigger** — Fire sentinels externally.

```
memory_sentinel_trigger(sentinelId: string)
```

### Sketches & Crystallization

**memory_sketch_create** — Ephemeral action graphs for exploratory work.

```
memory_sketch_create(title: string, actions: object[])
```

**memory_sketch_promote** — Promote a sketch to permanent memory.

```
memory_sketch_promote(sketchId: string)
```

**memory_crystallize** — Compact action chains into consolidated memories.

```
memory_crystallize(actionChainId: string)
```

### Health & Diagnostics

**memory_diagnose** — Health checks and system diagnostics.

```
memory_diagnose()
```

**memory_heal** — Auto-fix stuck states (circuit breaker reset, index rebuild).

```
memory_heal()
```

### Facets & Verification

**memory_facet_tag** — Add dimension:value tags to memories.

```
memory_facet_tag(memoryId: string, facet: string)
```

**memory_facet_query** — Query memories by facet tags.

```
memory_facet_query(facet: string)
```

**memory_verify** — Trace provenance of any memory back to source observations.

```
memory_verify(memoryId: string)
```

## MCP Resources

Six read-only resources available to agents:

- `agentmemory://status` — Health, session count, memory count
- `agentmemory://project/{name}/profile` — Per-project intelligence
- `agentmemory://memories/latest` — Latest 10 active memories
- `agentmemory://graph/stats` — Knowledge graph statistics

## MCP Prompts

Three predefined prompts for structured agent interactions:

- **recall_context** — Search + return context messages
- **session_handoff** — Handoff data between agents
- **detect_patterns** — Analyze recurring patterns

## Claude Code Skills

Four skills available in the Claude Code plugin (rewritten as pure prompts in v0.8.9 to avoid sandbox issues):

- `/recall` — Search memory
- `/remember` — Save to long-term memory
- `/session-history` — Recent session summaries
- `/forget` — Delete observations/sessions

## Standalone MCP Notes

The standalone MCP shim (`@agentmemory/mcp`) runs without the full iii-engine. As of v0.8.9 it ships 7 tools: `memory_save`, `memory_recall`, `memory_sessions`, `memory_export`, `memory_audit`, `memory_smart_search` (substring fallback), and `memory_governance_delete`. Data persists to `~/.agentmemory/standalone.json` immediately after every save (survives SIGKILL since v0.8.4).
