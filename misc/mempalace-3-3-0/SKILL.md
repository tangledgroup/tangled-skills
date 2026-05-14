---
name: mempalace-3-3-0
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
  - https://github.com/MemPalace/mempalace/tree/v3.3.0
  - https://github.com/MemPalace/mempalace/issues
  - https://raw.githubusercontent.com/lhl/agentic-memory/10ade6b92a1d54f896f56cd2be386ef54e288a0c/ANALYSIS-mempalace.md
---

# MemPalace 3.3.0

## Overview

MemPalace is a local-first AI memory system that stores conversation transcripts and project files verbatim in ChromaDB, organized by a spatial metaphor inspired by the ancient method of loci. It provides semantic search, a temporal knowledge graph (SQLite), and an MCP server for integration with Claude Code, Gemini CLI, Codex, and other MCP-compatible agents.

The core philosophy: **store everything, then make it findable.** No LLM is required to extract, summarize, or curate memories. Raw verbatim text with ChromaDB's default embeddings achieves 96.6% R@5 on LongMemEval — the highest published score requiring zero API keys.

**Dependencies:** Python 3.9+, ChromaDB (>=0.5.0), PyYAML. No external APIs required for core operations.

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

## Installation / Setup

```bash
pip install mempalace

# Initialize a palace
mempalace init ~/projects/myapp

# Mine project files (code, docs, notes)
mempalace mine ~/projects/myapp

# Mine conversation exports
mempalace mine ~/chats/ --mode convos

# Search
mempalace search "why did we switch to GraphQL"

# Check status
mempalace status
```

## Advanced Topics

**Palace Architecture**: Wings, rooms, halls, tunnels, closets, drawers — the spatial metaphor explained → [Palace Architecture](reference/01-palace-architecture.md)

**Mining and Ingestion**: Project mining, conversation mining, mega-file splitting, entity detection → [Mining and Ingestion](reference/02-mining-and-ingestion.md)

**Search and Retrieval**: Hybrid BM25 + vector search, closet-first retrieval, memory layers → [Search and Retrieval](reference/03-search-and-retrieval.md)

**Knowledge Graph**: Temporal triples, entity management, timeline queries → [Knowledge Graph](reference/04-knowledge-graph.md)

**MCP Server and Integration**: 29+ tools, Claude Code plugin, Gemini CLI hooks, local model support → [MCP Server and Integration](reference/05-mcp-and-integration.md)

**AAAK Dialect**: The experimental compression format, emotion codes, flags → [AAAK Dialect](reference/06-aaak-dialect.md)

**Benchmarks**: LongMemEval, ConvoMem, LoCoMo results and methodology → [Benchmarks](reference/07-benchmarks.md)
