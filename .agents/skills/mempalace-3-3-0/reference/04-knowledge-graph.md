# Knowledge Graph

## Overview

MemPalace's knowledge graph is a temporal entity-relationship system stored in SQLite. It tracks facts with validity windows — knowing not just what is true, but when it became true and when it stopped being true.

Storage: `~/.mempalace/knowledge_graph.sqlite3` (local, no external dependencies).

## Schema

Three tables:

**entities** — Node storage
- `id` — slugified name (e.g., `alice_obrien`)
- `name` — display name
- `type` — entity category (person, project, tool, concept)
- `properties` — JSON string of additional attributes

**triples** — Relationship edges
- `subject`, `predicate`, `object` — the triple
- `valid_from`, `valid_to` — temporal validity window
- `confidence` — float (default 1.0)
- `source_closet`, `source_file` — provenance links back to verbatim memory

**attributes** — Entity key-value pairs
- `entity_id`, `key`, `value`
- `valid_from`, `valid_to` — temporal validity

Indexes on triples: subject, object, predicate, and (valid_from, valid_to) for temporal queries.

## Python API

```python
from mempalace.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
# Custom path:
kg = KnowledgeGraph(db_path="/path/to/kg.sqlite3")
```

### Adding Entities and Relationships

```python
# Add entity explicitly
kg.add_entity("Kai", entity_type="person", properties={"role": "engineer"})

# Add triple — auto-creates entities if they don't exist
kg.add_triple(
    "Kai", "works_on", "Orion",
    valid_from="2025-06-01"
)
kg.add_triple(
    "Maya", "assigned_to", "auth-migration",
    valid_from="2026-01-15"
)
```

### Invalidating Facts

When something stops being true, set `valid_to`:

```python
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")
```

Current queries won't return Orion for Kai. Historical queries still will.

### Querying

```python
# Everything about an entity
kg.query_entity("Kai")
# → [Kai → works_on → Orion (current), Kai → recommended → Clerk (2026-01)]

# What was true at a specific time?
kg.query_entity("Maya", as_of="2026-01-20")
# → [Maya → assigned_to → auth-migration (active)]

# Direction: "outgoing", "incoming", or "both"
kg.query_entity("Alice", direction="both")

# All triples of a relationship type
kg.query_relationship("works_on")

# Chronological timeline
kg.timeline("Orion")
```

Query results include `current` (True if `valid_to IS NULL`) and `source_closet` for provenance.

## Fact Checker (Experimental)

The `fact_checker.py` module checks assertions against entity facts in the knowledge graph:

```
Input:  "Soren finished the auth migration"
Output: 🔴 AUTH-MIGRATION: attribution conflict — Maya was assigned, not Soren

Input:  "Kai has been here 2 years"
Output: 🟡 KAI: wrong_tenure — records show 3 years (started 2023-04)
```

Facts checked against the knowledge graph. Ages, dates, and tenures calculated dynamically. Note: this is a separate utility not automatically wired into KG operations as of v3.3.0.

## Entity Detection

The `entity_detector.py` module auto-detects people, projects, and tools from content using regex patterns and keyword matching. Results are confirmed interactively during `mempalace init`. The `entity_registry.py` manages entity storage and disambiguation by DOB, ID, or context.

## Limitations

- Entity ID normalization is naive slugification (`alice_obrien`) — no sophisticated entity resolution
- No contradiction detection in the core KG (the fact checker is a separate module)
- Flat triple lookup — no multi-hop graph traversal
- String date comparison requires consistent ISO formatting
