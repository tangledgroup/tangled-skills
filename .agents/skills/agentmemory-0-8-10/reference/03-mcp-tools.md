# MCP Tools Reference

43 tools exposed through the MCP server, organized by category. Tool visibility controlled by `AGENTMEMORY_TOOLS` env var: `core` (7 tools) or `all` (43 tools).

## Core Tools (always available)

| Tool | Description | Required Args |
|------|-------------|---------------|
| `memory_recall` | Search past observations | `query` (string), `limit` (number, default 10) |
| `memory_save` | Save an insight, decision, or pattern | `content` (string), `type`, `concepts`, `files` |
| `memory_smart_search` | Hybrid semantic + keyword search | `query` (string), `limit`, `expandIds` |
| `memory_file_history` | Past observations about specific files | `files` (comma-separated), `sessionId` |
| `memory_sessions` | List recent sessions | `limit` (default 20) |
| `memory_profile` | Project profile (concepts, files, patterns) | `project` (string), `refresh` |
| `memory_export` | Export all memory data | none |

## Extended Tools

### Pattern and Timeline Analysis

| Tool | Description |
|------|-------------|
| `memory_patterns` | Detect recurring patterns across sessions |
| `memory_timeline` | Chronological observations around an anchor point |
| `memory_relations` | Query relationship graph for a memory |
| `memory_graph_query` | Knowledge graph traversal (requires GRAPH_EXTRACTION_ENABLED) |

### Memory Management

| Tool | Description |
|------|-------------|
| `memory_consolidate` | Run 4-tier consolidation pipeline |
| `memory_claude_bridge_sync` | Sync with Claude Code MEMORY.md |
| `memory_governance_delete` | Delete memories with audit trail |
| `memory_snapshot_create` | Git-versioned memory snapshot |

### Multi-Agent Coordination

| Tool | Description |
|------|-------------|
| `memory_team_share` | Share memory items with team members |
| `memory_team_feed` | Recent shared items from team |
| `memory_action_create` | Create work items with dependencies |
| `memory_action_update` | Update action status and results |
| `memory_frontier` | Unblocked actions ranked by priority |
| `memory_next` | Single most important next action |
| `memory_lease` | Exclusive action leases (acquire/release/renew) |
| `memory_routine_run` | Instantiate workflow routines |
| `memory_signal_send` | Inter-agent messaging |
| `memory_signal_read` | Read messages with receipts |
| `memory_checkpoint` | External condition gates |
| `memory_mesh_sync` | P2P sync between instances |

### Advanced Features

| Tool | Description |
|------|-------------|
| `memory_sentinel_create` | Event-driven watchers |
| `memory_sentinel_trigger` | Fire sentinels externally |
| `memory_sketch_create` | Ephemeral action graphs |
| `memory_sketch_promote` | Promote sketch to permanent |
| `memory_crystallize` | Compact action chains |
| `memory_facet_tag` | Dimension:value tags on memories |
| `memory_facet_query` | Query by facet tags |
| `memory_verify` | Trace provenance of a memory |

### Diagnostics and Audit

| Tool | Description |
|------|-------------|
| `memory_audit` | Audit trail of operations |
| `memory_diagnose` | Health checks |
| `memory_heal` | Auto-fix stuck state |

## MCP Resources

| Resource | Description |
|----------|-------------|
| `agentmemory://status` | Health, session count, memory count |
| `agentmemory://project/{name}/profile` | Per-project intelligence |
| `agentmemory://memories/latest` | Latest 10 active memories |
| `agentmemory://graph/stats` | Knowledge graph statistics |

## MCP Prompts

| Prompt | Description |
|--------|-------------|
| `recall_context` | Search + return context messages |
| `session_handoff` | Handoff data between agents |
| `detect_patterns` | Analyze recurring patterns |

## Claude Code Skills (plugin)

| Skill | Description |
|-------|-------------|
| `/recall` | Search memory |
| `/remember` | Save to long-term memory |
| `/session-history` | Recent session summaries |
| `/forget` | Delete observations/sessions |

## Standalone MCP Server

The `@agentmemory/mcp` shim package provides a subset of tools without requiring iii-engine:

- `memory_save` — persists to `~/.agentmemory/standalone.json`
- `memory_recall` — substring filtering on stored memories
- `memory_smart_search` — same as recall (no BM25/vector/graph without engine)
- `memory_sessions` — lists sessions with limit support
- `memory_export` — exports all stored data
- `memory_audit` — audit trail
- `memory_governance_delete` — delete with reason tracking

Run standalone:

```bash
npx -y @agentmemory/agentmemory mcp
# or:
npx -y @agentmemory/mcp
```

## Tool Response Format

All MCP tools return responses in JSON-RPC format:

```json
{
  "content": [
    { "type": "text", "text": "{\"result\": ...}" }
  ]
}
```

Error responses include `isError: true` on the content item or a top-level `error` field with HTTP status code.
