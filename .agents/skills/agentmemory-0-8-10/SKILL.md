---
name: agentmemory-0-8-10
description: Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 + vector + knowledge graph), and multi-agent coordination via MCP server with 43 tools. Works with Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, and any MCP client without external database dependencies.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.8.10"
tags:
  - ai-agents
  - memory
  - persistent-context
  - mcp-server
  - iii-engine
  - knowledge-graph
category: ai-agent-tooling
external_references:
  - https://github.com/rohitg00/agentmemory/tree/v0.8.10
  - https://github.com/rohitg00/agentmemory/blob/v0.8.10/benchmark/COMPARISON.md
  - https://github.com/rohitg00/agentmemory/blob/v0.8.10/benchmark/LONGMEMEVAL.md
  - https://github.com/rohitg00/iii-engine
  - https://www.npmjs.com/package/@agentmemory/agentmemory
---
## Overview
agentmemory is a persistent memory system for AI coding agents that silently captures what your agent does, compresses it into searchable memory, and injects the right context when the next session starts. Built on [iii-engine](https://github.com/rohitg00/iii-engine)'s three primitives (Worker/Function/Trigger), it provides 43 MCP tools, 109 REST endpoints, 12 auto-hooks, and a real-time viewer without external database dependencies.

**Key capabilities:**
- **Automatic observation capture**: Hooks into agent tool usage via 12 lifecycle events
- **LLM-powered compression**: Compresses raw observations into structured memories with facts, concepts, and narratives
- **Hybrid search**: Combines BM25 keyword search, vector embeddings (optional), and knowledge graph traversal
- **Multi-agent shared memory**: One server instance serves Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, and any MCP client
- **Zero external dependencies**: File-based SQLite via iii-engine's StateModule at `~/.agentmemory/state_store.db`

**Performance metrics:**
- 95.2% retrieval accuracy (R@5) on LongMemEval-S benchmark
- 92% fewer tokens vs full context paste (~170K tokens/yr vs 19.5M+)
- 654 tests passing, Apache-2.0 licensed

## When to Use
Load this skill when:
- Setting up agentmemory for the first time (installation, configuration, hooks)
- Integrating with specific agents (Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, Cline, etc.)
- Using MCP tools programmatically (`memory_recall`, `memory_save`, `memory_smart_search`, etc.)
- Configuring embedding providers (local transformers, OpenAI, Gemini, Voyage, Cohere)
- Troubleshooting memory capture, search accuracy, or viewer connectivity
- Implementing team collaboration features (shared memories, governance, snapshots)
- Extending agentmemory with custom functions or hooks

## Core Concepts
### Memory Lifecycle

1. **Observation**: Raw hook events captured from agent interactions (tool calls, prompts, responses)
2. **Compression**: LLM summarizes observations into structured format (title, facts, narrative, concepts, files)
3. **Memory Storage**: Compressed memories stored in SQLite with BM25 index and optional vector embeddings
4. **Context Injection**: At session start, relevant context injected based on project path and recent activity
5. **Consolidation**: Periodic merging of related memories to reduce redundancy

### Hook Types (12 Auto-Hooks)

```typescript
type HookType =
  | "session_start"       // Capture initial context injection
  | "prompt_submit"       // User prompt submitted
  | "pre_tool_use"        // Before tool execution
  | "post_tool_use"       // After successful tool execution
  | "post_tool_failure"   // After failed tool execution
  | "pre_compact"         // Before context window compaction
  | "subagent_start"      // Subagent invocation begins
  | "subagent_stop"       // Subagent invocation ends
  | "notification"        // Agent notification events
  | "task_completed"      // Task completion markers
  | "stop"                // Agent stopping
  | "session_end"         // Session cleanup and finalization
```

### Memory Types

- **pattern**: Recurring code patterns or architectural decisions
- **preference**: User preferences (code style, tool choices, workflows)
- **architecture**: System architecture and design decisions
- **bug**: Known bugs and their fixes
- **workflow**: Multi-step workflows and procedures
- **fact**: Discrete facts about the codebase

### Hybrid Search Architecture

```
Query → [BM25 (40%)] + [Vector (35%)] + [Graph (25%)] → Combined Score → Results
         ↓              ↓                ↓
      Keyword       Embeddings      Relations
      matching      (optional)      traversal
```

**Configuration:**
- `BM25_WEIGHT`: 0.4 (default)
- `VECTOR_WEIGHT`: 0.6 (default, requires embedding provider)
- Graph score: derived from relation confidence and hop count

See [Architecture Details](reference/01-architecture.md) for deep dive into iii-engine integration and state management.

## Installation / Setup
### Quick Start

```bash
# Install via npm (requires Node.js >= 20)
npm install -g @agentmemory/agentmemory

# Start the memory server
agentmemory start
```

This starts:
- REST API on `http://localhost:3111/agentmemory/*`
- WebSocket streams on `ws://localhost:3112`
- iii-engine connection to `ws://localhost:49134`

### Docker Deployment

```bash
# Use provided docker-compose.yml
docker-compose up -d

# Services exposed:
# - agentmemory:3111 (REST API)
# - agentmemory:3112 (WebSocket streams)
# - iii-engine:49134 (internal engine)
```

### Data Directory

All data stored in `~/.agentmemory/`:
- `state_store.db` — SQLite database (sessions, observations, memories, indexes)
- `.env` — Environment configuration
- `viewer/` — Real-time viewer static files

See [Configuration Guide](reference/02-configuration.md) for environment variables and embedding setup.

## Usage Examples
### 1. Claude Code Integration

agentmemory ships with a Claude Code plugin that automatically captures observations and injects context.

**Installation:**
```bash
# Add to ~/.claude/plugins/agentmemory.json
{
  "name": "agentmemory",
  "version": "0.8.10",
  "skills": ["./skills/"]
}
```

**Automatic behavior:**
- Session start: Injects relevant context from past sessions
- Tool usage: Captures all read/write/edit operations
- Session end: Compresses observations into memories

**Manual memory save:**
```bash
# Via MCP tool call
agentmemory tool memory_save \
  --content "Use jose for JWT auth, not jsonwebtoken (Edge compatibility)" \
  --type preference \
  --concepts "jwt,auth,edge-functions" \
  --files "src/middleware/auth.ts"
```

### 2. MCP Client Setup (Cursor, Gemini CLI, OpenCode)

**MCP Server Configuration:**
```json
{
  "mcpServers": {
    "agentmemory": {
      "command": "agentmemory",
      "args": ["mcp"],
      "env": {
        "AGENTMEMORY_SECRET": "your-secret-key"
      }
    }
  }
}
```

**Available Tools (8 visible by default, 43 total):**
- `memory_recall` — Search past observations
- `memory_save` — Explicitly save insights
- `memory_file_history` — File-specific history
- `memory_patterns` — Detect recurring patterns
- `memory_sessions` — List recent sessions
- `memory_smart_search` — Hybrid semantic+keyword search
- `memory_timeline` — Chronological observations
- `memory_profile` — Project profile with concepts and files

Enable all tools: `AGENTMEMORY_TOOLS=all`

### 3. Programmatic REST API

```bash
# Recall context for a specific project
curl -X POST http://localhost:3111/agentmemory/search \
  -H "Authorization: Bearer your-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "JWT authentication middleware",
    "project": "/home/user/my-project",
    "limit": 5
  }'

# Save a memory explicitly
curl -X POST http://localhost:3111/agentmemory/remember \
  -H "Authorization: Bearer your-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Database migrations use Prisma with PostgreSQL",
    "type": "architecture",
    "concepts": ["database", "prisma", "postgresql"],
    "files": ["prisma/schema.prisma"]
  }'

# Get project profile
curl -X POST http://localhost:3111/agentmemory/profile \
  -H "Authorization: Bearer your-secret" \
  -d '{"project": "/home/user/my-project"}'
```

### 4. Smart Search with Progressive Disclosure

```bash
# Initial search (compact results)
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -d '{"query": "payment processing", "limit": 5}'

# Expand specific results for full details
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -d '{
    "query": "payment processing",
    "expandIds": ["obs_abc123", "obs_def456"]
  }'
```

### 5. Real-Time Viewer

```bash
# Start viewer (separate command)
agentmemory viewer

# Or access via REST API viewer endpoint
# http://localhost:3111/agentmemory/viewer
```

**Viewer features:**
- Live observation stream
- Memory graph visualization
- Session timeline
- Search interface
- Token savings dashboard

See [MCP Tools Reference](reference/03-mcp-tools.md) for all 43 tools and [REST API Reference](reference/04-rest-api.md) for endpoint details.

## Troubleshooting
### Memory Not Capturing

**Check hooks are installed:**
```bash
# For Claude Code
ls ~/.claude/plugins/agentmemory/hooks/

# Verify iii-engine is running
curl http://localhost:49134/health
```

**Manual hook trigger test:**
```bash
curl -X POST http://localhost:3111/agentmemory/hook-test \
  -d '{"hookType": "session_start", "project": "/test"}'
```

### Search Returning No Results

**Rebuild BM25 index:**
```bash
curl -X POST http://localhost:3111/agentmemory/rebuild-index
```

**Check observation count:**
```bash
curl http://localhost:3111/agentmemory/sessions
```

### Viewer Not Connecting

**Verify WebSocket port:**
```bash
# Check streams server
netstat -an | grep 3112

# Or restart with explicit port
III_STREAMS_PORT=3112 agentmemory start
```

See [Troubleshooting Guide](reference/06-troubleshooting.md) for comprehensive debugging steps.

## Advanced Topics
## Advanced Topics

- [Architecture](reference/01-architecture.md)
- [Configuration](reference/02-configuration.md)
- [Mcp Tools](reference/03-mcp-tools.md)
- [Rest Api](reference/04-rest-api.md)
- [Advanced Features](reference/05-advanced-features.md)
- [Troubleshooting](reference/06-troubleshooting.md)

