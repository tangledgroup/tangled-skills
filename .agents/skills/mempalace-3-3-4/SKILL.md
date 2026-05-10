---
name: mempalace-3-3-4
description: Local AI memory system that mines projects and conversations into a searchable index using ChromaDB for vector search and SQLite for knowledge graph storage. No API keys or cloud dependencies required. Use when building AI agents requiring persistent memory, mining conversation exports, creating searchable codebase indexes, implementing local RAG, or needing temporal knowledge graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ai-memory
  - local-rag
  - chromadb
  - knowledge-graph
  - mcp
  - agent-memory
  - verbatim-storage
category: ai-tooling
external_references:
  - https://github.com/MemPalace/mempalace/tree/v3.3.4
  - https://github.com/MemPalace/mempalace/releases
  - https://mempalaceofficial.com
  - https://raw.githubusercontent.com/lhl/agentic-memory/10ade6b92a1d54f896f56cd2be386ef54e288a0c/ANALYSIS-mempalace.md
---

# MemPalace 3.3.4

## Overview

MemPalace is a local-first AI memory system that stores conversation transcripts and project files verbatim in ChromaDB, organized by a spatial metaphor inspired by the ancient method of loci. It provides semantic search, a temporal knowledge graph (SQLite), and an MCP server for integration with Claude Code, Gemini CLI, Codex, and other MCP-compatible agents.

The core philosophy: **store everything, then make it findable.** No LLM is required to extract, summarize, or curate memories. Raw verbatim text with ChromaDB's default embeddings achieves 96.6% R@5 on LongMemEval — the highest published score requiring zero API keys.

**Dependencies:** Python 3.9+, ChromaDB (>=1.5.4, <2), PyYAML. No external APIs required for core operations.

**v3.3.4 highlights:** `mempalace init` now prompts to mine the same directory with `--auto-mine` flag for non-interactive paths; cross-wing topic tunnels auto-link shared themes across wings; context-aware corpus detection (Pass 0) identifies AI-dialogue records and agent personas before entity classification; LLM-assisted refinement runs by default (graceful fallback if no LLM available); HNSW bloat guard reduces 30 GB palaces to 376 MB; hybrid BM25 + cosine search in CLI; `max-seq-id` repair mode; graceful Ctrl-C during mine; idempotent re-runs of `init`.

## When to Use

- Building AI agents that need persistent memory across sessions without cloud dependencies
- Mining conversation exports (Claude, ChatGPT, Slack) into a searchable knowledge base
- Creating verbatim indexes of codebases, documentation, or notes
- Implementing local RAG pipelines with hybrid BM25 + vector search
- Replacing paid memory systems (Mem0, Letta, Zep) with self-hosted alternatives
- Temporal entity-relationship tracking with SQLite-based knowledge graphs

## Core Concepts

**Palace Architecture** — The spatial organization: Wings (people/projects) contain Rooms (topics/days), which contain Drawers (verbatim text chunks). Closets are compact searchable indexes that point to drawers. Halls connect rooms within a wing; tunnels cross-reference the same topic across wings.

**Verbatim Storage** — Original text is stored in ChromaDB drawers (~800 chars per chunk, 100 char overlap). Nothing is summarized or paraphrased. The 96.6% benchmark score comes from this raw mode.

**Closets** — A compact index layer created during mining. Each closet line contains a topic description, entity names, and pointers to drawer IDs. Search queries closets first (fast scan of short text), then opens referenced drawers for full verbatim content. Closets are a ranking signal, never a gate — direct drawer search always runs as the baseline.

**Knowledge Graph** — Temporal entity-relationship triples stored in SQLite with validity windows (`valid_from` / `valid_to`). Facts can be invalidated when they change, and queried with time filtering.

**4-Layer Memory Stack** — Progressive loading: L0 (identity, ~50 tokens), L1 (essential story from palace, ~500-800 tokens), L2 (on-demand wing/room retrieval, ~200-500 tokens), L3 (deep semantic search, unlimited). Wake-up cost is ~600-900 tokens.

**AAAK Dialect** — An experimental lossy abbreviation system for packing repeated entities into fewer tokens. Readable by any text-capable LLM. Not the storage default — raw verbatim text is the primary format. AAAK currently regresses LongMemEval vs raw mode (84.2% vs 96.6%).

**Cross-Wing Topic Tunnels** (v3.3.4) — When two wings share confirmed `TOPIC` labels (from LLM-refine bucket in `init --llm`), the miner creates symmetric tunnels between them at mine time. Configurable via `MEMPALACE_TOPIC_TUNNEL_MIN_COUNT` env var or `topic_tunnel_min_count` in config (default 1).

**Context-Aware Corpus Detection** (v3.3.4) — Pass 0 runs before entity detection during `init`, identifying whether a corpus is an AI-dialogue record and which platform/persona names are present. Tier 1 uses free regex heuristics; Tier 2 uses LLM (~$0.01 with Anthropic Haiku, free with local Ollama). Results persist to `<palace>/.mempalace/origin.json`.

## Installation / Setup

```bash
pip install mempalace

# Initialize a palace (now prompts to mine immediately)
mempalace init ~/projects/myapp

# Non-interactive: init + auto-mine
mempalace init --auto-mine ~/projects/myapp

# Mine project files (code, docs, notes)
mempalace mine ~/projects/myapp

# Mine conversation exports
mempalace mine ~/.claude/projects/ --mode convos

# Re-detect corpus origin after corpus grows
mempalace mine --redetect-origin ~/projects/myapp

# Search (now uses hybrid BM25 + cosine)
mempalace search "why did we switch to GraphQL"

# Check status
mempalace status
```

## Advanced Topics

**Palace Architecture**: Wings, rooms, halls, tunnels, closets, drawers — the spatial metaphor explained → [Palace Architecture](reference/01-palace-architecture.md)

**Mining and Ingestion**: Project mining, conversation mining, mega-file splitting, entity detection, corpus-origin detection, LLM-assisted refinement → [Mining and Ingestion](reference/02-mining-and-ingestion.md)

**Search and Retrieval**: Hybrid BM25 + vector search, closet-first retrieval, memory layers → [Search and Retrieval](reference/03-search-and-retrieval.md)

**Knowledge Graph**: Temporal triples, entity management, timeline queries → [Knowledge Graph](reference/04-knowledge-graph.md)

**MCP Server and Integration**: 29+ tools, Claude Code plugin, Gemini CLI hooks, local model support → [MCP Server and Integration](reference/05-mcp-and-integration.md)

**AAAK Dialect**: The experimental compression format, emotion codes, flags → [AAAK Dialect](reference/06-aaak-dialect.md)

**Benchmarks**: LongMemEval, ConvoMem, LoCoMo results and methodology → [Benchmarks](reference/07-benchmarks.md)
