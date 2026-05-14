---
name: agentmemory-0-8-9
description: Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 + vector + knowledge graph), and multi-agent coordination via MCP server with 43 tools. Works with Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, OpenClaw, and any MCP client without external database dependencies. Use when building AI coding agent workflows requiring persistent memory, semantic recall across sessions, or multi-agent coordination with shared context.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ai-agents
  - memory
  - mcp-server
  - persistent-context
  - vector-search
  - hybrid-search
  - knowledge-graph
  - multi-agent
category: ai-agent-tools
external_references:
  - https://github.com/rohitg00/agentmemory/tree/v0.8.9
  - https://arxiv.org/abs/2410.10813
  - https://github.com/rohitg00/agentmemory/blob/v0.8.9/CHANGELOG.md
  - https://iii.dev/docs
---

# agentmemory v0.8.9

## Overview

agentmemory is a persistent memory system for AI coding agents. It runs as a background service that silently captures every tool use, file edit, and decision your agent makes — compresses it into searchable structured memory — and injects the right context when the next session starts. One command. Works across all major agents. No external databases required.

Built on [iii-engine](https://iii.dev)'s three primitives (Worker/Function/Trigger), agentmemory replaces the traditional Express + Postgres + Redis stack with a single native binary that provides HTTP triggers, KV state, WebSocket streams, and worker management. The codebase is 118 TypeScript source files (~21,800 LOC) with 715 passing tests.

**Key metrics:**
- 95.2% retrieval recall at R@5 on LongMemEval-S (ICLR 2025 benchmark, 500 questions)
- 92% fewer tokens vs. pasting full context into conversation
- 43 MCP tools for memory operations
- 12 auto-capture hooks (zero manual effort)
- 0 external database dependencies (SQLite + in-memory vector index via iii-engine)

## When to Use

- Building or operating AI coding agents that need persistent cross-session memory
- Setting up Claude Code, Cursor, Gemini CLI, OpenCode, Hermes, OpenClaw, Codex CLI, Cline, Goose, Kilo Code, Aider, Claude Desktop, Windsurf, Roo Code, or Claude SDK with memory
- Replacing built-in agent memory (CLAUDE.md, .cursorrules) that caps at ~200 lines
- Implementing hybrid semantic search (BM25 + vector embeddings + knowledge graph) for code context
- Coordinating memory across multiple AI agents working on the same project
- Needing real-time observability of agent memory via the built-in viewer (port 3113)
- Migrating from cloud-dependent memory systems (mem0, Letta, Hippo) to self-hosted alternatives

## Core Concepts

### The Memory Problem

Every AI coding agent forgets everything when the session ends. You waste the first 5 minutes of every session re-explaining your stack, architecture decisions, and bug fixes. Built-in memory files (CLAUDE.md, .cursorrules) cap out at ~200 lines and go stale. agentmemory solves this by running as a background service that captures, compresses, indexes, and retrieves context automatically.

### How It Works — The Memory Pipeline

1. **Capture** — 12 hooks fire on every agent event (tool use, file edit, session start/end, errors)
2. **Dedup** — SHA-256 deduplication with a 5-minute window prevents duplicate observations
3. **Privacy Filter** — API keys, secrets, and `<private>` tags are stripped before storage
4. **Compress** — Observations are compressed into structured facts, concepts, and narrative (LLM-powered or zero-token synthetic)
5. **Embed** — Dense vector embeddings generated via 6 supported providers (local, Gemini, OpenAI, Voyage AI, Cohere, OpenRouter)
6. **Index** — Triple-stream indexing: BM25 keyword index + vector index + knowledge graph
7. **Retrieve** — At session start, hybrid search (BM25 + vector + graph) with RRF fusion injects relevant context within a token budget

### 4-Tier Memory Consolidation

Inspired by human sleep consolidation, memories progress through four tiers:

- **Working** — Raw observations from tool use (short-term memory)
- **Episodic** — Compressed session summaries ("what happened")
- **Semantic** — Extracted facts and patterns ("what I know")
- **Procedural** — Workflows and decision patterns ("how to do it")

Memories decay over time following the Ebbinghaus forgetting curve. Frequently accessed memories strengthen through reinforcement scoring. Stale memories auto-evict. Contradictions are detected and resolved.

### Agent Compatibility

agentmemory works with any agent that supports hooks, MCP, or REST API. All agents share the same memory server instance:

- **Claude Code** — 12 hooks + MCP + skills (first-class integration)
- **OpenClaw** — MCP + gateway plugin with 4 lifecycle hooks
- **Hermes** — MCP + memory provider plugin with 6 hooks
- **Cursor, Gemini CLI, OpenCode, Codex CLI, Cline, Goose, Kilo Code, Claude Desktop, Windsurf, Roo Code** — MCP server
- **Aider** — REST API (109 endpoints on port 3111)
- **Claude SDK** — AgentSDKProvider integration
- **Any agent** — REST API or `npx skillkit install agentmemory`

## Installation / Setup

### Quick Start

Start the memory server:

```bash
npx @agentmemory/agentmemory
```

This auto-starts a local iii-engine if `iii` is already installed, or falls back to Docker Compose if Docker is available. REST API binds to `127.0.0.1:3111`, streams to port 3112, and the real-time viewer to port 3113.

### Demo

Seed sample data and see recall in action:

```bash
npx @agentmemory/agentmemory demo
```

This seeds 3 realistic sessions (JWT auth, N+1 query fix, rate limiting) and runs semantic searches against them. You'll see it find "N+1 query fix" when you search "database performance optimization" — the kind of result keyword matching alone cannot produce.

### Prerequisites

- Node.js >= 20
- iii-engine runtime (native binary) or Docker

Install iii-engine:

- **macOS / Linux:** `curl -fsSL https://install.iii.dev/iii/main/install.sh | sh`
- **Windows:** Download `iii-x86_64-pc-windows-msvc.zip` from [iii-hq/iii releases](https://github.com/iii-hq/iii/releases/latest), extract `iii.exe` to PATH
- **Docker:** The bundled `docker-compose.yml` pulls `iiidev/iii:latest`

### Configuration

Create `~/.agentmemory/.env`:

```env
# LLM provider (auto-detected from Claude subscription, or override)
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

# Auth
# AGENTMEMORY_SECRET=your-secret

# Features
# AGENTMEMORY_AUTO_COMPRESS=false  # OFF by default since v0.8.8
# GRAPH_EXTRACTION_ENABLED=false
# CONSOLIDATION_ENABLED=true
# LESSON_DECAY_ENABLED=true
# CLAUDE_MEMORY_BRIDGE=false
# SNAPSHOT_ENABLED=false
```

### Standalone MCP (no engine required)

For agents that only need MCP tools without the full server:

```bash
npx -y @agentmemory/agentmemory mcp   # canonical
npx -y @agentmemory/mcp                # shim package alias
```

Add to your agent's MCP config (most agents):

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

## Advanced Topics

**Memory Pipeline and Architecture**: Deep dive into the capture-compress-index-retrieve pipeline, iii-engine primitives, and system architecture → [Memory Pipeline & Architecture](reference/01-memory-pipeline.md)

**MCP Tools Reference**: All 43 MCP tools with parameters, behavior, and usage patterns → [MCP Tools Reference](reference/02-mcp-tools.md)

**REST API Reference**: 109 REST endpoints for programmatic memory access → [REST API Reference](reference/03-rest-api.md)

**Configuration and Embedding Providers**: LLM providers, embedding backends, environment variables, and search tuning → [Configuration & Providers](reference/04-configuration.md)

**Multi-Agent Coordination**: Leases, signals, actions, routines, checkpoints, mesh sync, sentinels, and team memory → [Multi-Agent Coordination](reference/05-multi-agent.md)

**Memory Governance**: Auto-forgetting, retention scoring, decay curves, consolidation pipeline, and citation provenance → [Memory Governance](reference/06-governance.md)
