---
name: agentmemory-0-8-9
description: Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 + vector + knowledge graph), and multi-agent coordination via MCP server with 43 tools. Works with Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, OpenClaw, and any MCP client without external database dependencies.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.8.9"
tags:
  - ai-agents
  - memory
  - mcp-server
  - persistent-context
  - vector-search
category: ai-agent-tools
external_references:
  - https://github.com/rohitg00/agentmemory/tree/v0.8.9
  - https://arxiv.org/abs/2410.10813
  - https://github.com/rohitg00/agentmemory/blob/v0.8.9/CHANGELOG.md
  - https://iii.dev/docs
---
## Overview
**agentmemory** is a persistent memory engine for AI coding agents that automatically captures every tool use, compresses it into searchable memory, and injects relevant context when sessions start. It eliminates the need to re-explain architecture, re-discover bugs, or re-teach preferences across sessions.

**Key capabilities:**
- **Automatic capture**: 12 lifecycle hooks record observations with zero manual effort
- **95.2% retrieval accuracy** on LongMemEval-S benchmark (ICLR 2025)
- **Hybrid search**: BM25 + vector embeddings + knowledge graph with Reciprocal Rank Fusion
- **43 MCP tools**: Complete toolkit for memory operations, multi-agent coordination, and governance
- **Zero external dependencies**: SQLite + iii-engine, no Postgres/Redis/Qdrant required
- **92% fewer tokens** vs pasting full context (~$10/year vs ~$500)
- **Cross-agent compatible**: Same memory server works for Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, OpenClaw, and 32+ other agents

## When to Use
Load this skill when:
- Setting up persistent memory for AI coding agents (Claude Code, Cursor, Gemini CLI, etc.)
- Configuring MCP server for multi-agent memory sharing
- Implementing automatic context capture via lifecycle hooks
- Needing semantic search across past agent sessions
- Building multi-agent coordination with leases, signals, and mesh sync
- Troubleshooting memory retrieval or token efficiency issues
- Integrating with specific agents (Hermes, OpenClaw, Claude Code plugin)
- Configuring embedding providers (local, OpenAI, Gemini, Voyage AI, Cohere)

## Core Concepts
### Memory Tiers (4-Tier Consolidation)

Inspired by human memory consolidation:

| Tier | What it stores | Analogy |
|------|----------------|---------|
| **Working** | Raw tool observations | Short-term memory |
| **Episodic** | Compressed session summaries | "What happened" |
| **Semantic** | Extracted facts and patterns | "What I know" |
| **Procedural** | Workflows and decision patterns | "How to do it" |

### Memory Lifecycle

```
PostToolUse hook fires
  → SHA-256 dedup (5min window)
  → Privacy filter (strip secrets, API keys)
  → Store raw observation
  → Synthetic compression (zero LLM calls by default)
  → Vector embedding (6 providers + local)
  → Index in BM25 + vector + knowledge graph

SessionStart hook fires
  → Load project profile (top concepts, files, patterns)
  → Hybrid search (BM25 + vector + graph)
  → Token budget (default: 2000 tokens)
  → Inject into conversation
```

### Capture Hooks

| Hook | Captures |
|------|----------|
| `SessionStart` | Project path, session ID |
| `UserPromptSubmit` | User prompts (privacy-filtered) |
| `PreToolUse` | File access patterns + enriched context |
| `PostToolUse` | Tool name, input, output |
| `PostToolUseFailure` | Error context |
| `PreCompact` | Re-injects memory before compaction |
| `SubagentStart/Stop` | Sub-agent lifecycle |
| `Stop` | End-of-session summary |
| `SessionEnd` | Session complete marker |

### Search Architecture

Triple-stream retrieval with Reciprocal Rank Fusion (RRF, k=60):

1. **BM25**: Stemmed keyword matching with synonym expansion (always on)
2. **Vector**: Cosine similarity over dense embeddings (`all-MiniLM-L6-v2` local or API providers)
3. **Graph**: Knowledge graph traversal via entity matching

Session-diversified results (max 3 per session).

## Installation / Setup
### Basic Installation (30 seconds)

```bash
# Terminal 1: start the memory server
npx @agentmemory/agentmemory

# Terminal 2: test with demo data
npx @agentmemory/agentmemory demo
```

The `demo` command seeds 3 realistic sessions (JWT auth, N+1 query fix, rate limiting) and runs semantic searches. Open `http://localhost:3113` to watch the real-time viewer.

### Claude Code Integration

Paste this block into Claude Code:

```
Install agentmemory: run `npx @agentmemory/agentmemory` in a separate terminal to start the memory server. Then run `/plugin marketplace add rohitg00/agentmemory` and `/plugin install agentmemory` — the plugin registers all 12 hooks, 4 skills, AND auto-wires the `@agentmemory/mcp` stdio server via its `.mcp.json`, so you get 43 MCP tools (memory_smart_search, memory_save, memory_sessions, memory_governance_delete, etc.) without any extra config step. Verify with `curl http://localhost:3111/agentmemory/health`. The real-time viewer is at http://localhost:3113.
```

### MCP Server Setup (Any Agent)

Start the server:
```bash
npx @agentmemory/agentmemory
```

Add to your agent's MCP config (example for Cursor, Claude Desktop, Cline):
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/mcp"]
    }
  }
}
```

Agent-specific configs:
- **Cursor**: `~/.cursor/mcp.json`
- **Gemini CLI**: `gemini mcp add agentmemory -- npx -y @agentmemory/mcp`
- **OpenCode**: See [OpenClaw/OpenCode Config](reference/02-agent-integrations.md)
- **Hermes**: See [Hermes Integration](reference/02-agent-integrations.md)

### From Source

```bash
git clone https://github.com/rohitg00/agentmemory.git && cd agentmemory
npm install && npm run build && npm start
```

Requires Node.js >= 20 and either [iii-engine](https://iii.dev/docs) or Docker.

## Configuration
### Environment Variables

Create `~/.agentmemory/.env`:

```env
# LLM provider (pick one, or leave empty for Claude subscription)
# ANTHROPIC_API_KEY=sk-ant-...
# GEMINI_API_KEY=...
# OPENROUTER_API_KEY=...

# Embedding provider (auto-detected, or override)
# EMBEDDING_PROVIDER=local
# VOYAGE_API_KEY=...

# Search tuning
# BM25_WEIGHT=0.4
# VECTOR_WEIGHT=0.6
# TOKEN_BUDGET=2000

# Auth for protected endpoints
# AGENTMEMORY_SECRET=your-secret

# Ports (defaults: 3111 API, 3113 viewer)
# III_REST_PORT=3111

# Features
# AGENTMEMORY_AUTO_COMPRESS=false  # OFF by default (#138). When on,
                                   # every PostToolUse hook calls your
                                   # LLM provider to compress the
                                   # observation — expect significant
                                   # token spend on active sessions.
# GRAPH_EXTRACTION_ENABLED=false
# CONSOLIDATION_ENABLED=true
# LESSON_DECAY_ENABLED=true
# OBSIDIAN_AUTO_EXPORT=false
# AGENTMEMORY_EXPORT_ROOT=~/.agentmemory
# CLAUDE_MEMORY_BRIDGE=false

# Team memory (multi-user)
# TEAM_ID=your-team
# USER_ID=your-username
# TEAM_MODE=private

# Tool visibility: "core" (7 tools) or "all" (43 tools)
# AGENTMEMORY_TOOLS=core
```

### Embedding Providers

| Provider | Model | Cost | Install |
|----------|-------|------|---------|
| **Local (recommended)** | `all-MiniLM-L6-v2` | Free | `npm install @xenova/transformers` |
| Gemini | `text-embedding-004` | Free tier | `GEMINI_API_KEY=...` |
| OpenAI | `text-embedding-3-small` | $0.02/1M | `OPENAI_API_KEY=...` |
| Voyage AI | `voyage-code-3` | Paid | `VOYAGE_API_KEY=...` |
| Cohere | `embed-english-v3.0` | Free trial | `COHERE_API_KEY=...` |

Local embeddings provide +8pp recall over BM25-only with zero API costs.

## MCP Tools (43 Total)
### Core Tools (Always Available)

| Tool | Description |
|------|-------------|
| `memory_recall` | Search past observations |
| `memory_save` | Save an insight, decision, or pattern |
| `memory_smart_search` | Hybrid semantic + keyword search |
| `memory_file_history` | Past observations about specific files |
| `memory_sessions` | List recent sessions |
| `memory_profile` | Project profile (concepts, files, patterns) |
| `memory_export` | Export all memory data |

### Extended Tools (Set `AGENTMEMORY_TOOLS=all`)

See [Extended MCP Tools](reference/03-mcp-tools.md) for the complete 43-tool reference including:
- Pattern detection (`memory_patterns`, `memory_timeline`)
- Knowledge graph queries (`memory_graph_query`, `memory_relations`)
- Multi-agent coordination (`memory_lease`, `memory_signal_send`, `memory_mesh_sync`)
- Governance (`memory_governance_delete`, `memory_audit`, `memory_snapshot_create`)
- Actions and routines (`memory_action_create`, `memory_routine_run`, `memory_next`)

### Resources, Prompts, Skills

| Type | Name | Description |
|------|------|-------------|
| Resource | `agentmemory://status` | Health, session count, memory count |
| Resource | `agentmemory://project/{name}/profile` | Per-project intelligence |
| Prompt | `recall_context` | Search + return context messages |
| Skill | `/recall` | Search memory |
| Skill | `/remember` | Save to long-term memory |
| Skill | `/session-history` | Recent session summaries |
| Skill | `/forget` | Delete observations/sessions |

## REST API
109 endpoints on port `3111`. Protected endpoints require `Authorization: Bearer <secret>` when `AGENTMEMORY_SECRET` is set.

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/agentmemory/health` | Health check (always public) |
| `POST` | `/agentmemory/session/start` | Start session + get context |
| `POST` | `/agentmemory/session/end` | End session |
| `POST` | `/agentmemory/observe` | Capture observation |
| `POST` | `/agentmemory/smart-search` | Hybrid search |
| `POST` | `/agentmemory/context` | Generate context |
| `POST` | `/agentmemory/remember` | Save to long-term memory |
| `POST` | `/agentmemory/forget` | Delete observations |
| `GET` | `/agentmemory/profile` | Project profile |
| `GET` | `/agentmemory/export` | Export all data |

See [REST API Reference](reference/04-api-reference.md) for complete endpoint documentation.

## Real-Time Viewer
Auto-starts on port `3113`. Features:
- Live observation stream
- Session explorer
- Memory browser
- Knowledge graph visualization
- Health dashboard
- Token savings calculator

```bash
open http://localhost:3113
```

The viewer binds to `127.0.0.1` by default with CSP nonces and no inline handlers (security fix in v0.8.2).

## Security Features
**v0.8.2+ security hardening:**
- Default localhost binding (`127.0.0.1`) instead of `0.0.0.0`
- Viewer CSP with per-response nonces, `script-src-attr 'none'`
- Mesh sync requires `AGENTMEMORY_SECRET` on both peers
- Privacy filtering strips API keys, secrets, `<private>` tags before storage
- Path traversal protection in Obsidian export

**Privacy filter covers:**
- `sk-`, `sk-proj-` (OpenAI, Anthropic)
- `ghp_`, `ghs_`, `ghu_` (GitHub tokens)
- AWS access keys
- Bearer tokens
- Custom `<private>` tags

## Troubleshooting
See [Troubleshooting Guide](reference/05-troubleshooting.md) for:
- "Connection refused on port 3111"
- "No memories returned"
- Windows setup (iii-engine installation)
- Docker fallback issues
- Search quality improvements
- Token usage concerns

## Benchmarks
### Retrieval Accuracy (LongMemEval-S, ICLR 2025)

| System | R@5 | R@10 | MRR |
|--------|-----|------|-----|
| **agentmemory** (BM25 + Vector) | **95.2%** | **98.6%** | **88.2%** |
| agentmemory (BM25-only) | 86.2% | 94.6% | 71.5% |

### Token Efficiency

| Approach | Tokens/year | Cost/year |
|----------|-------------|-----------|
| Paste full history | 19.5M+ | Impossible (exceeds window) |
| LLM-summarized | ~650K | ~$500 |
| **agentmemory** (API embeddings) | **~170K** | **~$10** |
| **agentmemory** (local embeddings) | **~170K** | **$0** |

See [Benchmark Comparison](reference/06-benchmarks.md) for detailed comparison vs mem0, Letta, Khoj, claude-mem, Hippo.

## Advanced Topics
## Advanced Topics

- [Agent Integrations](reference/02-agent-integrations.md)
- [Mcp Tools](reference/03-mcp-tools.md)
- [Api Reference](reference/04-api-reference.md)
- [Troubleshooting](reference/05-troubleshooting.md)
- [Benchmarks](reference/06-benchmarks.md)

