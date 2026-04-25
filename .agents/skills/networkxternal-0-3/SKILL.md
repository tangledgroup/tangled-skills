---
name: networkxternal-0-3
description: NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, MongoDB, Neo4J). Use when working with Terabyte-Petabyte graphs that won't fit into RAM, needing multi-edge support with key/label-based edge identity, or building graph applications requiring database-backed storage without changing application code.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - graph
  - database
  - networkx
  - sqlite
  - postgresql
  - mysql
  - mongodb
  - neo4j
  - persistent-storage
category: databases
external_references:
  - https://github.com/ashvardanian/NetworkXternal
  - https://docs.sqlalchemy.org/
  - https://github.com/ashvardanian/NetworkXternal/blob/main/networkxternal/base_api.py
  - https://networkx.github.io/documentation/stable/reference/classes/generated/networkx.Graph.html
  - https://networkx.github.io/documentation/stable/reference/classes/multidigraph.html
  - https://networkx.github.io/
---
## Overview
**NetworkXternal** is a NetworkX-like interface for external memory graphs persisted in various databases. It lets you upscale from Megabyte-Gigabyte graphs to Terabyte-Petabyte graphs (that won't fit into RAM) without changing your code.

The library provides **partial** compatibility with [NetworkX](https://networkx.github.io/) `MultiDiGraph` API, supporting multi-edges (multiple edges between the same node pair) with key/label-based edge identity. Graph data is stored in:

- **SQLite** - Fastest for tiny databases under 20 MB
- **PostgreSQL** - Feature-rich open-source relational DB
- **MySQL** - Most commonly-used relational DB
- **MongoDB** - Modern distributed document DB
- **Neo4J** - Native graph database (with performance caveats)

## When to Use
Use NetworkXternal when:

- **Graph exceeds RAM**: Your graph is too large to fit in memory (GBs to TBs of edges)
- **Persistence required**: You need graphs to survive application restarts
- **NetworkX compatibility**: You want to migrate from NetworkX with minimal code changes
- **Multi-process access**: Multiple processes need to read/write the same graph
- **Database already in use**: Your stack already uses one of the supported databases

**Don't use when:**
- Graph fits comfortably in RAM (use NetworkX directly for better performance)
- You need advanced graph algorithms (NetworkXternal focuses on storage, not algorithms)
- Sub-millisecond latency is required (database I/O adds overhead)

## Core Concepts
### External Memory Graphs

Traditional graph libraries like NetworkX store all nodes and edges in RAM. NetworkXternal stores them in a database, allowing:

- **Unbounded size**: Limited only by storage capacity, not RAM
- **Persistence**: Graph survives application restarts automatically
- **Concurrency**: Multiple processes can access the same graph
- **Crash safety**: Database ACID properties protect against data loss

### MultiDiGraph Compatibility

NetworkXternal is designed as a partial `MultiDiGraph` replacement. It stores **directed weighted multigraphs** by default, with configurable options:

| Feature | Supported | Notes |
|---------|-----------|-------|
| Directed graphs | ✅ | `directed=True` (default) |
| Undirected graphs | ✅ | `directed=False` in constructor |
| Weighted edges | ✅ | Float weights, default 1.0 |
| Multi-edges | ✅ | `multigraph=True` (default); multiple edges between same nodes |
| Edge keys/labels | ✅ | `key` parameter maps to edge `label` (int) |
| Node attributes | ✅ | Stored as JSON payload dict |
| Edge attributes | ✅ | Stored as JSON payload dict; `key` is special-cased |
| Integer node IDs | ✅ | Native support, fastest path |
| Non-integer node IDs | ✅ | Hashed to integers via Python's `hash()` |
| Edge identity | ✅ | Cantor-style hash: `(first+second)*(first+second+1)//2 + second` mod 2³¹ |

**Key deviation from NetworkX API:**
- `has_edge(u, v)` returns a **list of Edge objects** (not a `bool`). Returns empty list `[]` if no edges found.
- `number_of_edges()` accepts optional `u`, `v`, `key` parameters for filtering (like NetworkX's `MultiDiGraph.number_of_edges()`).
- `get_edge_data(u, v)` returns a dict of edge attributes or `default`; not actively used internally.

**Edge uniqueness strategy:**
When no explicit `_id` is provided, edges are identified by hashing their endpoints using a Cantor-style pairing function. This means `(u, v)` and `(v, u)` produce different IDs for directed graphs. For undirected graphs, the same hash applies regardless of direction.

### Constructor Parameters

All backends accept these parameters in `__init__`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directed` | `bool` | `True` | Whether the graph is directed (MultiDiGraph) or undirected (MultiGraph) |
| `weighted` | `bool` | `True` | Whether edges carry float weights |
| `multigraph` | `bool` | `True` | Whether multiple edges between same nodes are allowed |
| `url` | `str` | varies by backend | Database connection string (SQL backends and MongoDB) |
| `enterprise_edition` | `bool` | `False` | Neo4J only: enables edge uniqueness constraints |

### Node Model

**Nodes** have:
- `_id`: Integer identifier (auto-generated or provided; non-integers are hashed)
- `weight`: Float value (default: 1.0)
- `label`: Integer label (default: -1)
- `payload`: Dict of custom attributes (stored as JSON)

If the original node name was non-integer, it is stored in `payload["_id"]`.

### Edge Model

**Edges** have:
- `_id`: Integer identifier (auto-generated via Cantor hash from endpoints if not provided)
- `first`: Source node ID (integer)
- `second`: Target node ID (integer)
- `is_directed`: Boolean flag
- `weight`: Float value (default: 1.0)
- `label`: Integer label (derived from the `key` parameter, default: -1)
- `payload`: Dict of custom attributes (stored as JSON; `key` is stored here too)

Edges support tuple-like indexing: `edge[0]` returns `first`, `edge[1]` returns `second` (for NetworkX compatibility).

### Edge ID Hashing

NetworkXternal uses a Cantor-style pairing function for deterministic edge IDs:

```python
def identify_by_members(first: int, second: int) -> int:
    _id = (first + second) * (first + second + 1) // 2 + second
    _id = _id % (2**31)
    return _id
```

This ensures:
- **Order-dependent**: `identify_by_members(10, 20) != identify_by_members(20, 10)` — critical for directed graphs
- **Deterministic**: Same node pair always produces the same ID
- **Bounded**: Result fits in signed 31-bit integer

**Note:** Some databases (SQLite default) use smaller integer sizes. Use `BigInteger` type in SQLAlchemy models to avoid overflow on large graphs.

## Installation / Setup
### From Source (Current Version)

NetworkXternal is not yet published to PyPI. Install from GitHub:

```bash
# Using pip
pip install git+https://github.com/ashvardanian/NetworkXternal.git@main

# Using uv (recommended for speed)
uv add "git+https://github.com/ashvardanian/NetworkXternal.git@main"
```

### Dependencies

The package requires:

- **Core**: `networkx`, `sqlalchemy`
- **Optional backends**:
  - `neo4j` - For Neo4J support
  - `pymongo` - For MongoDB support
  - Database-specific drivers for SQLAlchemy (e.g., `psycopg2` for PostgreSQL)

### Quick Start Example

```python
from networkxternal.sqlite import SQLite

# Create an in-memory SQLite graph
graph = SQLite(url="sqlite:///:memory:", directed=True, weighted=True)

# Add nodes and edges
graph.add_node(1, weight=2.5, category="source")
graph.add_node(2, weight=1.0, category="target")
graph.add_edge(1, 2, weight=3.5, label="connects_to")

# Query the graph
print(f"Nodes: {graph.number_of_nodes()}")  # 2
print(f"Edges: {graph.number_of_edges()}")  # 1
print(f"Neighbors of 1: {list(graph.neighbors(1))}")  # [2]

# Check for edge existence
edges = graph.has_edge(1, 2)
print(f"Edge exists: {edges is not None}")  # True
```

## Advanced Topics
## Advanced Topics

- [Database Backends](reference/01-database-backends.md)
- [Api Reference](reference/02-api-reference.md)
- [Performance Benchmarks](reference/03-performance-benchmarks.md)
- [Migration From Networkx](reference/04-migration-from-networkx.md)
- [Advanced Patterns](reference/05-advanced-patterns.md)
- [Multidigraph Usage Patterns](reference/06-multidigraph-usage-patterns.md)
- [Database Backends](reference/07-database-backends.md)
- [Basic Operations](reference/08-basic-operations.md)
- [Performance Considerations](reference/09-performance-considerations.md)
- [Troubleshooting](reference/10-troubleshooting.md)

