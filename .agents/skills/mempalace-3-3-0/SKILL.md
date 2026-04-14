---
name: mempalace-3-3-0
description: Local AI memory system that mines projects and conversations into a searchable palace using ChromaDB for vector search and SQLite for knowledge graph storage. Achieves 96.6% LongMemEval recall without API keys or cloud dependencies. Use when building AI agents requiring persistent memory across sessions, mining conversation exports for decisions, creating searchable indexes of codebases, implementing local RAG, needing temporal knowledge graphs, or migrating from paid memory systems to self-hosted alternatives.
license: MIT
author: MemPalace Team
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
---

# MemPalace 3.3.0

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

## Usage Examples

### MCP Integration (Recommended for AI Agents)

#### Claude Code

```bash
# Via plugin (recommended)
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace

# Or manually via MCP
mempalace mcp
# Outputs: claude mcp add mempalace -- python -m mempalace.mcp_server
```

After setup, the AI automatically has 29 tools available. Ask questions like:

> "What did we decide about auth last month?"

The AI calls `mempalace_search` automatically — you never type CLI commands manually.

#### Cursor / Gemini CLI / Other MCP Hosts

```bash
# Generic MCP setup
claude mcp add mempalace -- python -m mempalace.mcp_server

# With custom palace path
python -m mempalace.mcp_server --palace /path/to/palace
```

### Python API

#### Search

```python
from mempalace.searcher import search_memories, search

# Basic search
results = search_memories("auth decisions", palace_path="~/.mempalace/palace")

# With filters
results = search(
    query="GraphQL migration",
    palace_path="~/.mempalace/palace",
    wing="myapp",
    room="api-refactor",
    n_results=10
)
```

#### Knowledge Graph

```python
from mempalace.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# Add temporal triples
kg.add_triple("Kai", "works_on", "Orion", valid_from="2025-06-01")
kg.add_triple("Maya", "assigned_to", "auth-migration", valid_from="2026-01-15")
kg.add_triple("Maya", "completed", "auth-migration", valid_from="2026-02-01")

# Query entity relationships
kg.query_entity("Kai")
# → [Kai → works_on → Orion (current), Kai → recommended → Clerk (2026-01)]

# Temporal query: what was true in January?
kg.query_entity("Maya", as_of="2026-01-20")
# → [Maya → assigned_to → auth-migration (active)]

# Timeline of a project
kg.timeline("Orion")

# Invalidate a fact (mark as ended)
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")
```

#### Palace Navigation

```python
from mempalace.palace import Palace

palace = Palace(palace_path="~/.mempalace/palace")

# List wings and rooms
palace.list_wings()
palace.list_rooms(wing="myapp")

# Get full taxonomy tree
taxonomy = palace.get_taxonomy()

# Traverse across wings via tunnels
palace.traverse(wing="kai", room="auth-migration")

# Find tunnels between two wings
palace.find_tunnels(wing1="kai", wing2="driftwood")
```

### Specialist Agents

Create domain-focused agents with their own diaries:

```bash
# Create agent configs in ~/.mempalace/agents/
cat > ~/.mempalace/agents/reviewer.json << 'EOF'
{
  "name": "reviewer",
  "focus": "code quality, patterns, bugs",
  "diary_path": "~/.mempalace/diaries/reviewer.aaak"
}
EOF

cat > ~/.mempalace/agents/architect.json << 'EOF'
{
  "name": "architect",
  "focus": "design decisions, tradeoffs",
  "diary_path": "~/.mempalace/diaries/architect.aaak"
}
EOF
```

Agents write to their diaries in AAAK format:

```bash
# Via CLI
mempalace_diary_write("reviewer", "PR#42|auth.bypass.found|missing.middleware.check|pattern:3rd.time.this.quarter|★★★★")

# Via MCP tool (AI calls this automatically)
mempalace_diary_write(agent="architect", entry="decision.graphql.over.rest|reason:type.safety+single.query|→drawer_x1y2z3")
```

### Auto-Save Hooks (Claude Code)

Configure hooks to save memories during work:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/mempalace/hooks/mempal_save_hook.sh"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
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

**Save Hook:** Every 15 messages, triggers structured save (topics, decisions, quotes, code changes) + regenerates critical facts layer.

**PreCompact Hook:** Fires before context compression for emergency saves.

**Optional auto-ingest:** Set `MEMPAL_DIR` environment variable to auto-run `mempalace mine` on that directory during each save trigger.

## Advanced Topics

See [Independent Analysis](references/01-independent-analysis.md) for an external code review covering:
- Claims vs. implementation reality check
- Architecture deep dive (storage, KG, palace graph)
- Write/read path internals
- Benchmark methodology assessment
- Comparison with other memory systems (ENGRAM, Memoria, Mnemosyne, etc.)
- Design takeaways and red flags

### AAAK Dialect (Experimental)

AAAK is a lossy abbreviation system using entity codes and structural markers to compress repeated entities at scale.

**Honest status (v3.3.0):**
- Lossy compression, not lossless (uses regex-based abbreviation)
- Does NOT save tokens at small scales (overhead costs more on short text)
- Can save tokens at scale with many repeated entities
- Currently regresses LongMemEval vs raw mode (84.2% R@5 vs 96.6%)
- **Default storage is RAW verbatim** — AAAK is optional compression layer

Compress a wing:

```bash
mempalace compress --wing myapp [--config entities.json]
```

### Closet Architecture

Closets are index pointers that enable fast search:

```
CLOSET: "built auth system|Ben;Igor|→drawer_api_auth_a1b2c3"
         ↑ topic          ↑ entities  ↑ points to this drawer
```

**Search flow:**
1. Query `mempalace_closets` collection (fast, small docs)
2. Parse `→drawer_id_a,drawer_id_b` pointers from hits
3. Fetch exactly those drawers from `mempalace_drawers` (verbatim content)
4. Apply `max_distance` filter
5. Return chunk-level results with `matched_via: "closet"`

**Limits:**
- Max closet size: 1,500 chars
- Source content scanned: 5,000 chars
- Max topics per file: 12
- Max quotes per file: 3
- Max entities per pointer: 5

### Knowledge Graph Details

Temporal entity-relationship triples with SQLite storage:

```python
# Triples have validity windows
kg.add_triple(
    subject="Maya",
    predicate="assigned_to",
    obj="auth-migration",
    valid_from="2026-01-15",
    valid_to=None,  # Still active
    confidence=1.0,
    source_closet="closet_id_abc123",
    source_file="/path/to/source.txt"
)

# Invalidate (mark as ended)
kg.invalidate("Maya", "assigned_to", "auth-migration", ended="2026-02-01")
```

**Tables:**
- `entities` — Node metadata (id, name, type, properties)
- `triples` — Relationships with temporal validity (subject, predicate, object, valid_from, valid_to, confidence, source refs)

### MCP Tools Reference

**Palace (read):**
- `mempalace_status` — Palace overview + AAAK spec + memory protocol
- `mempalace_list_wings` — Wings with counts
- `mempalace_list_rooms` — Rooms within a wing
- `mempalace_get_taxonomy` — Full wing → room → count tree
- `mempalace_search` — Semantic search with wing/room filters
- `mempalace_check_duplicate` — Check before filing
- `mempalace_get_aaak_spec` — AAAK dialect reference

**Palace (write):**
- `mempalace_add_drawer` — File verbatim content
- `mempalace_delete_drawer` — Remove by ID

**Knowledge Graph:**
- `mempalace_kg_query` — Entity relationships with time filtering
- `mempalace_kg_add` — Add facts
- `mempalace_kg_invalidate` — Mark facts as ended
- `mempalace_kg_timeline` — Chronological entity story
- `mempalace_kg_stats` — Graph overview

**Navigation:**
- `mempalace_traverse` — Walk the graph from a room across wings
- `mempalace_find_tunnels` — Find rooms bridging two wings
- `mempalace_graph_stats` — Graph connectivity overview
- `mempalace_create_tunnel` — Create explicit cross-wing link
- `mempalace_list_tunnels` — List all explicit tunnels
- `mempalace_delete_tunnel` — Remove a tunnel by ID
- `mempalace_follow_tunnels` — Follow tunnels from a room

**Drawer Management:**
- `mempalace_get_drawer` — Fetch single drawer by ID
- `mempalace_list_drawers` — Paginated drawer listing
- `mempalace_update_drawer` — Update content or metadata

**Agent Diary:**
- `mempalace_diary_write` — Write AAAK diary entry
- `mempalace_diary_read` — Read recent diary entries

**System:**
- `mempalace_hook_settings` — Get/set hook behavior (silent save, toast)
- `mempalace_memories_filed_away` — Check if recent checkpoint was saved
- `mempalace_reconnect` — Force DB reconnect after external writes

## Troubleshooting

### Palace Not Found

```bash
# Initialize first
mempalace init ~/projects/myapp

# Or specify palace path explicitly
mempalace mine ~/projects/myapp --palace ~/.mempalace/palace
```

### ChromaDB Version Mismatch

```bash
# Check current version
mempalace status

# Migrate if needed
mempalace migrate --dry-run        # preview changes
mempalace migrate --yes            # apply migration
```

### Rebuild Palace Index

```bash
# Repair vector index from SQLite metadata
mempalace repair --yes

# Creates backup at ~/.mempalace/palace.backup
```

### Split Concatenated Transcripts

Some exports concatenate multiple sessions:

```bash
# Preview split
mempalace split ~/chats/ --dry-run

# Split files with 3+ sessions
mempalace split ~/chats/ --min-sessions 3

# Custom output directory
mempalace split ~/chats/ --output-dir ~/chats-split/
```

### No Closets Created

Closets are only created for project mining (not conversation mode yet):

```bash
# Mine as project to create closets
mempalace mine ~/projects/myapp  # creates closets

# Conversations use direct drawer search (fallback path)
mempalace mine ~/chats/ --mode convos  # no closets yet
```

## Benchmarks

| Benchmark | Mode | Score | API Calls |
|-----------|------|-------|-----------|
| LongMemEval R@5 | Raw (ChromaDB only) | **96.6%** | Zero |
| LongMemEval R@5 | Hybrid + Haiku rerank | **100%** (500/500) | ~500 |
| LoCoMo R@10 | Raw, session level | 60.3% | Zero |
| Personal palace R@10 | Heuristic bench | 85% | Zero |
| Palace structure impact | Wing+room filtering | **+34%** R@10 | Zero |

**Structure improvement:**
- Search all closets: 60.9% R@10
- Search within wing: 73.1% (+12%)
- Search wing + hall: 84.8% (+24%)
- Search wing + room: 94.8% (+34%)

## References

- **GitHub repository:** https://github.com/MemPalace/mempalace
- **Version v3.3.0:** https://github.com/MemPalace/mempalace/tree/v3.3.0
- **Documentation:** https://github.com/MemPalace/mempalace/tree/v3.3.0/docs
- **Benchmarks:** https://github.com/MemPalace/mempalace/tree/v3.3.0/benchmarks
- **Issue tracker:** https://github.com/MemPalace/mempalace/issues
- **Independent analysis:** [lhl/agentic-memory ANALYSIS-mempalace.md](https://raw.githubusercontent.com/lhl/agentic-memory/10ade6b92a1d54f896f56cd2be386ef54e288a0c/ANALYSIS-mempalace.md) — code review, claims verification, architecture deep dive (see [references/01-independent-analysis.md](references/01-independent-analysis.md))

## Comparison with Alternatives

| Feature | MemPalace | Zep (Graphiti) | Mem0 | Mastra |
|---------|-----------|----------------|------|--------|
| Storage | SQLite + ChromaDB | Neo4j (cloud) | Proprietary | GPT API |
| Cost | Free | $25/mo+ | $19-249/mo | API costs |
| Temporal KG | Yes | Yes | No | No |
| Self-hosted | Always | Enterprise only | No | No |
| LongMemEval R@5 | 96.6% (raw) | ~85% | ~85% | 94.87% |
| API Required | No | Yes | Yes | Yes |
