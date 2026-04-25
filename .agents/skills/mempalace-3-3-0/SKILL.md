---
name: mempalace-3-3-0
description: Local AI memory system that mines projects and conversations into a searchable palace using ChromaDB for vector search and SQLite for knowledge graph storage. Achieves 96.6% LongMemEval recall without API keys or cloud dependencies. Use when building AI agents requiring persistent memory across sessions, mining conversation exports for decisions, creating searchable indexes of codebases, implementing local RAG, needing temporal knowledge graphs, or migrating from paid memory systems to self-hosted alternatives.
license: MIT
author: Tangled <noreply@tangledgroup.com>
category: ai-memory
version: "3.3.0"
tags:
  - ai-memory
  - rag
  - chromadb
  - local-ai
  - mcp-server
  - knowledge-graph
external_references:
  - https://github.com/MemPalace/mempalace/tree/v3.3.0
  - https://github.com/MemPalace/mempalace
  - https://github.com/MemPalace/mempalace/issues
  - https://github.com/MemPalace/mempalace/tree/v3.3.0/benchmarks
  - https://github.com/MemPalace/mempalace/tree/v3.3.0/docs
  - https://raw.githubusercontent.com/lhl/agentic-memory/10ade6b92a1d54f896f56cd2be386ef54e288a0c/ANALYSIS-mempalace.md
---
## Overview
MemPalace is a local AI memory system that mines projects and conversations into a searchable "palace" using ChromaDB for vector search and SQLite for knowledge graph storage. It achieves **96.6% recall on LongMemEval** without API keys or cloud dependencies, storing verbatim content organized into wings (projects/people), halls (memory types), rooms (topics), closets (index pointers), and drawers (verbatim files).

Key features:
- **Raw verbatim storage** — No summarization loss; stores exact exchanges in ChromaDB
- **Palace structure** — Wings, halls, rooms, tunnels provide 34% retrieval improvement over flat search
- **MCP server** — 29 tools for AI agents (Claude Code, Cursor, Gemini CLI) to query memory automatically
- **Knowledge graph** — Temporal entity-relationship triples in SQLite with validity windows
- **AAAK dialect** — Experimental lossy compression for repeated entities at scale
- **Local & free** — Zero API calls, everything runs on your machine

## When to Use
Use MemPalace when:
- Building AI agents that need persistent memory across sessions
- Mining conversation exports (Claude, ChatGPT, Slack) for decisions and context
- Creating searchable indexes of codebases, docs, and project files
- Implementing local RAG without cloud dependencies or API costs
- Needing temporal knowledge graphs with entity relationships
- Building specialist agents with domain-specific diaries
- Migrating from paid memory systems (Zep, Mem0, Mastra) to local alternatives

## Core Concepts
### The Palace Architecture

```
WING: Project/Person
├── HALLS (memory types, same across all wings)
│   ├── hall_facts — decisions made, choices locked in
│   ├── hall_events — sessions, milestones, debugging
│   ├── hall_discoveries — breakthroughs, new insights
│   ├── hall_preferences — habits, likes, opinions
│   └── hall_advice — recommendations and solutions
├── ROOMS (topics specific to this wing)
│   ├── auth-migration
│   ├── graphql-switch
│   └── ci-pipeline
├── CLOSETS (index pointers, ~1500 chars each)
│   └── points to drawers via "→drawer_id_a,drawer_id_b"
└── DRAWERS (verbatim content, ~800 chars each)
    └── exact words from source files
```

**Tunnels** connect rooms across different wings (e.g., `auth-migration` in both `wing_kai` and `wing_driftwood`).

### Memory Stack Layers

| Layer | Content | Size | When Loaded |
|-------|---------|------|-------------|
| L0 | Identity — who is this AI? | ~50 tokens | Always |
| L1 | Critical facts — team, projects, preferences | ~120-900 tokens | Always |
| L2 | Room recall — recent sessions, current project | Variable | On demand |
| L3 | Deep search — semantic query across all closets | Variable | On demand |

### Mining Modes

- **`projects`** — Code files, documentation, notes (default)
- **`convos`** — Conversation exports (Claude JSONL, ChatGPT, Slack)
- **`general`** — Auto-classifies into decisions, milestones, problems, emotional context

## Installation / Setup
### Install

```bash
pip install mempalace
```

**Dependencies:**
- Python >= 3.9
- chromadb >= 0.5.0
- pyyaml >= 6.0, < 7

### Initialize a Palace

```bash
# Create palace at ~/.mempalace/palace (default) or custom path
mempalace init ~/projects/myapp --palace ~/.mempalace/palace

# Auto-detects entities (people, projects) from file content
# Detects rooms from folder structure
```

### Mine Content

```bash
# Mine project files (code, docs, notes)
mempalace mine ~/projects/myapp --wing myapp

# Mine conversation exports
mempalace mine ~/chats/claude-sessions --mode convos --wing personal
mempalace mine ~/exports/slack --mode convos --wing team

# Auto-classify general content into memory types
mempalace mine ~/notes/ --mode general --wing knowledge

# Split concatenated mega-files first (if needed)
mempalace split ~/chats/ --dry-run              # preview
mempalace split ~/chats/ --min-sessions 3       # only files with 3+ sessions
```

### Search

```bash
# Global search across all wings
mempalace search "why did we switch to GraphQL"

# Within a specific wing
mempalace search "auth decisions" --wing myapp

# Within a specific room
mempalace search "pricing" --room costs

# Limit results
mempalace search "bugs" --results 5
```

### Wake-Up Context

Load critical facts into AI context:

```bash
# Full wake-up (L0 + L1)
mempalace wake-up > context.txt

# For a specific project
mempalace wake-up --wing myapp > context.txt

# Paste context.txt into your AI's system prompt
```

## Advanced Topics
## Advanced Topics

- [Independent Analysis](reference/01-independent-analysis.md)
- [Usage Examples](reference/02-usage-examples.md)
- [Troubleshooting](reference/03-troubleshooting.md)
- [Benchmarks](reference/04-benchmarks.md)
- [Comparison With Alternatives](reference/05-comparison-with-alternatives.md)

