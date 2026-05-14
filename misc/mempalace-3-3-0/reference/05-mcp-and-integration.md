# MCP Server and Integration

## Overview

MemPalace provides an MCP (Model Context Protocol) server that exposes palace operations as tools for AI agents. It integrates with Claude Code, Gemini CLI, OpenAI Codex, and any MCP-compatible host.

## Starting the Server

```bash
# Default palace path
python -m mempalace.mcp_server

# Custom palace
python -m mempalace.mcp_server --palace /path/to/palace
```

The server uses JSON-RPC 2.0 over stdin/stdout (standard MCP transport). ChromaDB client is cached between calls and reconnects automatically if the database changes on disk (inode or mtime detection).

## Claude Code Integration

**Marketplace plugin (recommended):**

```bash
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace
```

Restart Claude Code, then type `/skills` to verify "mempalace" appears.

**Manual MCP setup:**

```bash
claude mcp add mempalace -- python -m mempalace.mcp_server
```

## Gemini CLI Integration

```bash
gemini mcp add mempalace /absolute/path/to/venv/bin/python3 \
  -m mempalace.mcp_server --scope user
```

Add a PreCompress hook to `~/.gemini/settings.json` for auto-saving before context compression:

```json
{
  "hooks": {
    "PreCompress": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/mempalace/hooks/mempal_precompact_hook.sh"
          }
        ]
      }
    ]
  }
}
```

## Hooks

Hooks enable automatic background saving without interrupting conversation:

- **Save Hook** (`mempal_save_hook.sh`): Saves new facts and decisions every 15 messages
- **PreCompact Hook** (`mempal_precompact_hook.sh`): Saves context before the AI's memory window fills up

Claude Code hook configuration in settings:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "./hooks/mempal_save_hook.sh"}]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "./hooks/mempal_precompact_hook.sh"}]
      }
    ]
  }
}
```

Hook settings configurable via `~/.mempalace/config.json`:

- `hooks.silent_save` — True: saves directly (default). False: blocks for MCP calls
- `hooks.desktop_toast` — Show desktop notification via `notify-send`

## Available MCP Tools

**Palace (read):**

- `mempalace_status` — Palace overview + AAAK spec + memory protocol
- `mempalace_list_wings` — Wings with drawer counts
- `mempalace_list_rooms` — Rooms within a wing
- `mempalace_get_taxonomy` — Full wing → room → count tree
- `mempalace_search` — Semantic search with wing/room filters
- `mempalace_check_duplicate` — Check before filing
- `mempalace_get_aaak_spec` — AAAK dialect reference

**Palace (write):**

- `mempalace_add_drawer` — File verbatim content
- `mempalace_delete_drawer` — Remove by ID
- `mempalace_get_drawer` — Get drawer by ID
- `mempalace_list_drawers` — List drawers with pagination
- `mempalace_update_drawer` — Update drawer content

**Knowledge Graph:**

- `mempalace_kg_query` — Entity relationships with time filtering
- `mempalace_kg_add` — Add facts
- `mempalace_kg_invalidate` — Mark facts as ended
- `mempalace_kg_timeline` — Chronological entity history
- `mempalace_kg_stats` — Graph statistics

**Navigation:**

- `mempalace_traverse` — Room traversal within wing
- `mempalace_find_tunnels` — Cross-wing connections
- `mempalace_graph_stats` — Palace graph statistics
- `mempalace_create_tunnel` — Create cross-wing link
- `mempalace_delete_tunnel` — Remove tunnel
- `mempalace_follow_tunnels` — Navigate tunnel network

**Agent Diary:**

- `mempalace_diary_write` — Write diary entry for an agent
- `mempalace_diary_read` — Read recent diary entries

**Maintenance:**

- `mempalace_reconnect` — Force cache invalidation and reconnect
- `mempalace_export` — Export palace data
- `mempalace_hook_settings` — Configure hook behavior

## Palace Protocol

The `status` tool embeds a `PALACE_PROTOCOL` string that instructs the AI agent:

1. On wake-up: call `mempalace_status` to load overview + AAAK spec
2. Before responding about any person/project/event: call `mempalace_kg_query` or `mempalace_search` first
3. If unsure about a fact: say "let me check" and query the palace
4. After each session: call `mempalace_diary_write` to record what happened
5. When facts change: invalidate old fact, add new one

## Local Model Support

Local models (Llama, Mistral) generally don't speak MCP yet. Two approaches:

**Wake-up command** — load world into context:

```bash
mempalace wake-up > context.txt
# Paste context.txt into local model's system prompt
```

**CLI search** — query on demand:

```bash
mempalace search "auth decisions" > results.txt
# Include results.txt in your prompt
```

**Python API:**

```python
from mempalace.searcher import search_memories
results = search_memories("auth decisions", palace_path="~/.mempalace/palace")
# Inject into local model's context
```

## Write-Ahead Log

Every write operation is logged to `~/.mempalace/wal/write_log.jsonl` before execution. Sensitive content (drawer text, queries) is redacted in the log. Provides an audit trail for detecting memory poisoning and enables review/rollback of writes.

## Specialist Agents

Create agents that focus on specific areas:

```
~/.mempalace/agents/
  ├── reviewer.json       # code quality, patterns, bugs
  ├── architect.json      # design decisions, tradeoffs
  └── ops.json            # deploys, incidents, infra
```

Each agent gets its own wing and diary. The AI discovers agents from the palace at runtime via `mempalace_list_agents`.
