---
name: agentmemory-0-8-10
description: Persistent memory engine for AI coding agents with cross-session context capture, hybrid search (BM25 + vector + knowledge graph), and multi-agent coordination via MCP server. Works with Claude Code, Cursor, Gemini CLI, and any MCP client without external databases. Use when building AI coding agent workflows requiring persistent memory or semantic recall.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ai-agent
  - persistent-memory
  - mcp-server
  - hybrid-search
  - knowledge-graph
  - multi-agent
category: ai-agent-infrastructure
external_references:
  - https://github.com/rohitg00/agentmemory/tree/v0.8.10
  - https://github.com/rohitg00/agentmemory/blob/v0.8.10/benchmark/COMPARISON.md
  - https://github.com/rohitg00/agentmemory/blob/v0.8.10/benchmark/LONGMEMEVAL.md
  - https://www.npmjs.com/package/@agentmemory/agentmemory
---

# agentmemory v0.8.10

## Overview

agentmemory is a persistent memory system for AI coding agents that eliminates the need to re-explain architecture, rediscover bugs, or re-teach preferences across sessions. It runs as a background server powered by [iii-engine](https://iii.dev) and provides 43 MCP tools, 109 REST endpoints, and a real-time viewer on port 3113.

Built on iii-engine's three primitives (Worker/Function/Trigger), agentmemory replaces the traditional Express + Postgres + Redis stack with a single lightweight runtime. State is stored in file-based SQLite via iii-engine's StateModule, with an in-memory vector index for semantic search and a knowledge graph for entity relationships.

Key statistics:
- **95.2% retrieval recall at R@5** on LongMemEval-S (500 questions, ~115K tokens each)
- **~170K tokens/year** vs 19.5M+ for full-history pasting (92% fewer tokens, ~$10/yr vs impossible)
- **43 MCP tools** across core memory, governance, multi-agent coordination, and diagnostics
- **12 lifecycle hooks** for automatic capture with zero manual effort
- **Zero external database dependencies** — SQLite + in-memory vector index + local embeddings

## When to Use

- Setting up persistent memory for any AI coding agent (Claude Code, Cursor, Gemini CLI, OpenCode, Codex, Cline, Goose, Windsurf, Roo Code, Claude Desktop, Aider, Hermes, OpenClaw, Kilo Code)
- Implementing cross-session recall of coding decisions, architecture patterns, and bug fixes
- Building multi-agent workflows that share memory through leases, signals, and routines
- Reducing token costs by replacing full-history context injection with targeted memory retrieval
- Enabling semantic search over coding history when keyword matching is insufficient
- Setting up team memory with namespaced shared and private memories across team members

## Core Concepts

**Observations** are raw captures of agent activity (tool uses, file edits, command outputs) recorded via lifecycle hooks. They flow through SHA-256 deduplication (5-minute window), privacy filtering (strips API keys, secrets, `<private>` tags), and synthetic or LLM-powered compression into structured facts, concepts, and narratives.

**Memories** are the compressed, long-term form of observations — typed as pattern, preference, architecture, bug, workflow, or fact. They carry strength scores (1-10), version chains with Jaccard-based supersession, relationship graphs, and TTL-based auto-forgetting.

**Hybrid Search** combines three retrieval streams: BM25 keyword matching with Porter stemming, vector cosine similarity over dense embeddings (6 providers including local `all-MiniLM-L6-v2`), and knowledge graph traversal via entity extraction. Results are fused with Reciprocal Rank Fusion (RRF, k=60) and session-diversified (max 3 results per session).

**4-Tier Memory Consolidation** mirrors human memory processing: working (raw observations), episodic (compressed session summaries), semantic (extracted facts and patterns), and procedural (workflows and decision patterns). Memories decay over time following the Ebbinghaus curve, frequently accessed memories strengthen, and stale memories auto-evict.

## Installation / Setup

### Quick Start

```bash
# Terminal 1: start the server
npx @agentmemory/agentmemory

# Terminal 2: seed sample data and see recall in action
npx @agentmemory/agentmemory demo
```

Open `http://localhost:3113` for the real-time viewer.

### Prerequisites

- Node.js >= 20
- iii-engine runtime (separate native binary) or Docker

Install iii-engine:

- **macOS / Linux:** `curl -fsSL https://install.iii.dev/iii/main/install.sh | sh`
- **Windows:** Download `iii-x86_64-pc-windows-msvc.zip` from [iii-hq/iii releases](https://github.com/iii-hq/iii/releases/latest), extract `iii.exe` to PATH
- **Docker fallback:** agentmemory auto-starts bundled `docker-compose.yml` if Docker is available

### Standalone MCP (no engine required)

For agents that only need MCP tools without the full server, viewer, or cron jobs:

```bash
npx -y @agentmemory/agentmemory mcp
# or via the shim package:
npx -y @agentmemory/mcp
```

### Agent Configuration

Add to your agent's MCP config:

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

### Environment Configuration

Create `~/.agentmemory/.env`:

```env
# LLM provider (pick one, or leave empty for Claude subscription default)
# ANTHROPIC_API_KEY=sk-ant-...
# GEMINI_API_KEY=...
# OPENROUTER_API_KEY=...

# Embedding provider (auto-detected, or force local)
# EMBEDDING_PROVIDER=local

# Search tuning (default: BM25 0.4, Vector 0.6)
# BM25_WEIGHT=0.4
# VECTOR_WEIGHT=0.6
# TOKEN_BUDGET=2000

# Auth
# AGENTMEMORY_SECRET=your-secret

# Feature flags (all OFF by default in 0.8.10)
# AGENTMEMORY_AUTO_COMPRESS=false   # LLM compression per observation
# AGENTMEMORY_INJECT_CONTEXT=false  # Context injection into conversation
# GRAPH_EXTRACTION_ENABLED=false    # Knowledge graph extraction
# CONSOLIDATION_ENABLED=true        # 4-tier consolidation pipeline
```

## Advanced Topics

**Memory Pipeline and Hooks**: The observation lifecycle from capture to retrieval → [Memory Pipeline](reference/01-memory-pipeline.md)

**Hybrid Search Architecture**: Triple-stream retrieval with BM25, vector, and knowledge graph → [Hybrid Search](reference/02-hybrid-search.md)

**MCP Tools Reference**: All 43 tools organized by category → [MCP Tools](reference/03-mcp-tools.md)

**REST API Endpoints**: 109 endpoints for programmatic access → [REST API](reference/04-rest-api.md)

**Configuration and Providers**: LLM providers, embedding providers, environment variables → [Configuration](reference/05-configuration.md)

**Multi-Agent Coordination**: Leases, signals, routines, checkpoints, mesh sync → [Multi-Agent](reference/06-multi-agent.md)

**Benchmarks and Comparison**: LongMemEval results vs competitors → [Benchmarks](reference/07-benchmarks.md)
