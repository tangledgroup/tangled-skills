# MCP Tools Reference

agentmemory exposes 51 MCP tools through the `@agentmemory/mcp` package. Core tools (8) are always available; extended tools require `AGENTMEMORY_TOOLS=all`.

## Core Tools (always available)

| Tool | Description |
|------|-------------|
| `memory_recall` | Search past observations |
| `memory_compress_file` | Compress markdown files while preserving structure |
| `memory_save` | Save an insight, decision, or pattern |
| `memory_patterns` | Detect recurring patterns |
| `memory_smart_search` | Hybrid semantic + keyword search |
| `memory_file_history` | Past observations about specific files |
| `memory_sessions` | List recent sessions |
| `memory_profile` | Project profile (concepts, files, patterns) |

## Extended Tools (set AGENTMEMORY_TOOLS=all)

| Tool | Description |
|------|-------------|
| `memory_timeline` | Chronological observations |
| `memory_relations` | Query relationship graph |
| `memory_graph_query` | Knowledge graph traversal |
| `memory_consolidate` | Run 4-tier consolidation |
| `memory_claude_bridge_sync` | Sync with MEMORY.md |
| `memory_team_share` | Share with team members |
| `memory_team_feed` | Recent shared items |
| `memory_audit` | Audit trail of operations |
| `memory_governance_delete` | Delete with audit trail |
| `memory_snapshot_create` | Git-versioned snapshot |
| `memory_action_create` | Create work items with dependencies |
| `memory_action_update` | Update action status |
| `memory_frontier` | Unblocked actions ranked by priority |
| `memory_next` | Single most important next action |
| `memory_lease` | Exclusive action leases (multi-agent) |
| `memory_routine_run` | Instantiate workflow routines |
| `memory_signal_send` | Inter-agent messaging |
| `memory_signal_read` | Read messages with receipts |
| `memory_checkpoint` | External condition gates |
| `memory_mesh_sync` | P2P sync between instances |
| `memory_sentinel_create` | Event-driven watchers |
| `memory_sentinel_trigger` | Fire sentinels externally |
| `memory_sketch_create` | Ephemeral action graphs |
| `memory_sketch_promote` | Promote to permanent |
| `memory_crystallize` | Compact action chains |
| `memory_diagnose` | Health checks |
| `memory_heal` | Auto-fix stuck state |
| `memory_facet_tag` | Dimension:value tags |
| `memory_facet_query` | Query by facet tags |
| `memory_verify` | Trace provenance |
| `memory_export` | Export all memory data |

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

## MCP Skills (Claude Code)

| Skill | Description |
|-------|-------------|
| `/recall` | Search memory |
| `/remember` | Save to long-term memory |
| `/session-history` | Recent session summaries |
| `/forget` | Delete observations/sessions |

## Standalone MCP Server

The `@agentmemory/mcp` package is a standalone MCP server that proxies to the running agentmemory server. This ensures hooks and the viewer stay in sync. Start it via:

```bash
npx -y @agentmemory/mcp
```

Or inline in agent config as shown in the main SKILL.md.
