# Usage Examples

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
