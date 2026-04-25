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

# NetworkXternal 0.3

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

## MultiDiGraph Usage Patterns

### Basic Directed Multigraph

```python
from networkxternal.sqlite import SQLite

# Create a directed multigraph (MultiDiGraph)
graph = SQLite(url="sqlite:///multigraph.db", directed=True, multigraph=True)

# Add multiple edges between same nodes using key/label parameter
graph.add_edge(1, 2, key=1, weight=1.0, relation="friend")    # label=1
graph.add_edge(1, 2, key=2, weight=2.0, relation="colleague")  # label=2
graph.add_edge(1, 2, key=3, weight=3.0, relation="family")     # label=3

# has_edge returns a LIST of Edge objects (not bool!)
edges = graph.has_edge(1, 2)
print(f"Found {len(edges)} edges between 1 and 2")  # 3

# Query by key/label
edge_key_1 = graph.has_edge(1, 2, key=1)
print(f"Friend edge: {edge_key_1[0].payload}")  # {'key': 1, 'relation': 'friend'}

# Count edges with filtering
all_edges = graph.number_of_edges()           # Total edges
from_1_to_2 = graph.number_of_edges(u=1, v=2) # Specific direction
by_key = graph.number_of_edges(u=1, v=2, key=1)  # Specific label
```

### Undirected Multigraph (MultiGraph)

```python
from networkxternal.sqlite import SQLite

# Create an undirected multigraph
graph = SQLite(url="sqlite:///undirected.db", directed=False, multigraph=True)

# Edges work bidirectionally
graph.add_edge(1, 2, key=1, weight=5.0)
graph.add_edge(1, 2, key=2, weight=3.0)

# neighbors() returns all connected nodes (both directions for undirected)
print(graph.neighbors(1))  # {2}

# successors/predecessors are the same in undirected mode
print(graph.successors(1))   # {2}
print(graph.predecessors(1)) # {2}
```

### Using Edge Objects Directly

```python
from networkxternal.helpers.edge import Edge
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///graph.db")

# Create edges with explicit IDs and labels
edge_a = Edge(_id=-1, first=1, second=2, weight=1.0, label=1, is_directed=True)
edge_b = Edge(_id=-1, first=1, second=2, weight=2.0, label=2, is_directed=True)

# Adding edges auto-computes _id via Cantor hash if _id < 0
graph.add([edge_a, edge_b])
print(f"Edge A ID: {edge_a._id}")  # Computed from (1, 2)
print(f"Edge B ID: {edge_b._id}")  # Same computed ID (same endpoints!)

# The label distinguishes them in has_edge() queries
```

### Non-Integer Node IDs

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///string_nodes.db")

# String node IDs are hashed to integers
graph.add_node("alice", role="user")   # Stored with hash(id("alice"))
graph.add_node("bob", role="user")     # Stored with hash(id("bob"))
graph.add_edge("alice", "bob", weight=10.0)

# The original string is preserved in node payload
node = graph.has_node(hash("alice"))
print(node.payload["_id"])  # "alice"
print(node.payload["role"]) # "user"
```

### In-Memory Quick Prototyping

```python
from networkxternal.sqlite import SQLiteMem

# Fastest option, single-process only (no concurrency)
graph = SQLiteMem(directed=True, weighted=True, multigraph=True)

graph.add_node(1, category="A")
graph.add_edge(1, 2, weight=3.5, label="connects_to")

# All operations are in-memory — no disk I/O
print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")
```

## Installation

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

## Database Backends

### SQLite (Fastest for Small Graphs)

```python
from networkxternal.sqlite import SQLite, SQLiteMem

# In-memory (fastest, but volatile)
graph = SQLiteMem(directed=True)

# Persistent file-based storage
graph = SQLite(url="sqlite:///path/to/graph.db", directed=True)

# SQLite is optimized with pragmas:
# - page_size=4096
# - journal_mode=WAL
# - synchronous=ON
# - cache_size=10000
```

**Best for**: Graphs under 20 MB, single-process access, quick prototyping

### PostgreSQL (Feature-Rich)

```python
from networkxternal.postgres import PostgreSQL

graph = PostgreSQL(
    url="postgresql://user:password@localhost:5432/graph_db",
    directed=True
)

# PostgreSQL supports:
# - Concurrent reads/writes
# - JSON payload querying
# - Advanced indexing
```

**Best for**: Multi-process access, large graphs (GBs), production environments

### MySQL

```python
from networkxternal.mysql import MySQL

graph = MySQL(
    url="mysql://user:password@localhost:3306/graph_db",
    directed=True
)

# MySQL is optimized with:
# - local_infile=1 (for CSV imports)
# - innodb_file_per_table=1
# - tmp_table_size=16MB
```

**Best for**: Existing MySQL infrastructure, moderate-sized graphs

### MongoDB (Document-Based)

```python
from networkxternal.mongodb import MongoDB

graph = MongoDB(
    url="mongodb://localhost:27017/graph",
    directed=True
)

# MongoDB stores:
# - Nodes in 'nodes' collection
# - Edges in 'edges' collection
# - Uses aggregation pipelines for queries
```

**Best for**: Distributed deployments, existing MongoDB infrastructure, flexible schemas

### Neo4J (Native Graph DB)

```python
from networkxternal.neo4j import Neo4J

graph = Neo4J(
    url="bolt://user:password@localhost:7687/graph",
    directed=True,
    enterprise_edition=False  # Set True for edge uniqueness constraints
)

# Neo4J-specific methods:
path, weight = graph.shortest_path(first_node, second_node)  # Returns (node_ids, total_weight)
degree_count, degree_weight = graph.degree_neighbors(v)       # Count + total weight of edges
degree_count, degree_weight = graph.degree_successors(v)      # Out-degree stats
degree_count, degree_weight = graph.degree_predecessors(v)    # In-degree stats

# Neo4J uses Cypher queries with labels: v<name> for nodes, e<name> for edges
```

**⚠️ CRITICAL WARNING: Neo4J is the least stable backend:**
- **High CPU usage**: 10-20x higher than other backends
- **Java heap space crashes**: Frequently crashes on large imports (30 MB CSV → 1.4 GB RAM)
- **Edge indexing**: Only available in Enterprise edition; free version has poor edge lookup performance
- **Unstable**: Reports of stack overflow errors, inconsistent query profiler results
- **Small batch size recommended**: Max 1,000 edges per batch (vs 1M+ for SQL backends)
- **Not recommended for production** with large datasets

**Best for**: Small graphs (< 10K edges) where native Cypher graph queries are needed. Use other backends for anything larger.

## Basic Operations

### Adding Data

```python
from networkxternal.helpers.edge import Edge
from networkxternal.helpers.node import Node
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///graph.db")

# Add single node
graph.add_node(1, weight=2.0, category="A")

# Add single edge
graph.add_edge(1, 2, weight=3.5, label="connects")

# Add using Edge/Node objects
edge = Edge(first=1, second=2, weight=4.0, is_directed=True)
graph.add(edge)

# Batch add multiple edges
edges = [
    Edge(first=i, second=i+1, weight=float(i))
    for i in range(100)
]
graph.add(edges)  # Returns count of added edges
```

### Querying Data

```python
# Count nodes and edges
node_count = graph.number_of_nodes()
edge_count = graph.number_of_edges()  # Optional: u, v, key filters

# Check if node exists
node = graph.has_node(1)  # Returns Node object or None

# Check if edge exists — RETURNS LIST (not bool like NetworkX!)
edges = graph.has_edge(1, 2)  # Returns list of Edge objects (empty [] if none)
if edges:  # Not empty
    for edge in edges:
        print(f"Edge {edge._id}: {edge.first} -> {edge.second}, weight={edge.weight}")

# Query specific key/label
edges_by_key = graph.has_edge(1, 2, key=1)  # Edges with label == 1 between 1 and 2

# Get neighbors (both directions for undirected)
neighbors = graph.neighbors(1)  # Set of node IDs

# Get successors/predecessors (directed only)
successors = graph.successors(1)  # Nodes reachable FROM 1 (out-neighbors)
predecessors = graph.predecessors(1)  # Nodes that point TO 1 (in-neighbors)

# out_edges and in_edges properties
out_edges = graph.out_edges   # All directed edges where is_directed=True
in_edges = graph.in_edges     # Inverted copy of out_edges (not stored separately!)

# Get all nodes/edges (can be expensive on large graphs!)
all_nodes = list(graph.nodes)  # Returns Sequence[Node]
all_edges = list(graph.edges)  # Returns Sequence[Edge]

# Filter edges by endpoint using reduce_edges
edges_to_node_1 = graph.reduce_edges(v=1)  # GraphDegree(count, weight)
edges_from_node_1 = graph.reduce_edges(u=1)
```

**Important API deviations from NetworkX MultiDiGraph:**

| NetworkX Method | NetworkXternal Equivalent | Difference |
|----------------|--------------------------|------------|
| `G.has_edge(u, v)` | `G.has_edge(u, v)` | Returns `list[Edge]` (not `bool`) |
| `G.number_of_edges()` | `G.number_of_edges(u, v, key)` | Accepts filter params |
| `G.get_edge_data(u, v, key)` | `G.get_edge_data(u, v, key)` | Returns dict; not actively used |
| `G.successors(v)` | `G.successors(v)` | Same semantics |
| `G.predecessors(v)` | `G.predecessors(v)` | Same semantics |
| `G.neighbors(v)` | `G.neighbors(v)` | Same semantics |
| `G.edges` | `G.edges` | Returns `Sequence[Edge]` |
| `G.out_edges` | `G.out_edges` | Directed edges only |
| `G.in_edges` | `G.in_edges` | Inverted copy of out_edges (computed, not stored) |
| `G.__len__()` | `len(G)` | Returns node count |
| `G.order()` | `G.order()` | Returns node count |
| `G.is_directed()` | `G.is_directed()` | Same |
| `G.is_multigraph()` | `G.is_multigraph()` | Same |

### Removing Data

```python
# Remove single edge
graph.remove(edge)

# Remove node and all connected edges
graph.remove_node(1)

# Remove batch of edges
graph.remove(edges)

# Clear all edges but keep nodes
graph.clear_edges()

# Clear entire graph
graph.clear()
```

## Performance Considerations

NetworkXternal has performance tradeoffs compared to in-memory graphs:

| Operation | NetworkX | NetworkXternal | Notes |
|-----------|----------|----------------|-------|
| Add edge | ~1 μs | ~100-1000 μs | Database I/O overhead |
| Find edge | ~1 μs | ~10-100 μs | Index lookups help |
| Get neighbors | ~1 μs | ~100-1000 μs | Depends on node degree |
| Import 1M edges | ~1 sec | ~10-60 sec | Batch size matters |

**Batch size recommendations by backend:**

| Backend | Optimal Batch Size | Max Recommended |
|---------|-------------------|-----------------|
| SQLiteMem | 5,000,000 | 5,000,000 |
| SQLite | 1,000,000 | 1,000,000 |
| PostgreSQL | 100,000 | 1,000,000 |
| MySQL | 100,000 | 1,000,000 |
| MongoDB | 10,000 | 100,000 |
| Neo4J | 1,000 | 10,000 |

### Ensuring Node Existence (add_missing_nodes)

When adding edges, nodes are not automatically created. Use `add_missing_nodes()` to ensure all nodes referenced by edges exist:

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///graph.db")

# Add edges without pre-creating nodes
graph.add_edge(1, 2, weight=5.0)
graph.add_edge(2, 3, weight=3.0)

# Nodes 1, 2, 3 may not exist as registered nodes!
# Verify and fix:
graph.add_missing_nodes()  # Creates Node objects for any edge-referenced IDs missing from nodes table

# This is automatically called at the end of add_stream()
```

**How it works:**
1. Collects all node IDs mentioned in edges (`mentioned_nodes_ids`)
2. Compares against registered nodes in the nodes table
3. Creates `Node` objects for any missing IDs
4. Bulk-inserts them into the database

### Getting All Edges Touching a Node (edges_related)

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///graph.db")

# Get all edges connected to node 1 (both directions, undirected semantics)
related_edges = graph.edges_related(1)  # Returns list of Edge objects

# In directed mode: first == 1 OR second == 1
# In undirected mode: same behavior (edges are bidirectional)
```

### Common Patterns

### Importing from CSV

```python
from networkxternal.helpers.parsing import import_graph

# CSV format: first,second,weight (with header row)
count = import_graph(graph, "path/to/edges.csv")
print(f"Imported {count} edges")
```

### Streaming Edges

```python
# Process edges in batches to avoid memory issues
for edge in graph.edges:
    process(edge)  # Your processing logic

# Or use streaming for large graphs
from networkxternal.helpers.algorithms import chunks

for batch in chunks(graph.edges, 1000):
    process_batch(batch)
```

### Graph Statistics

```python
# Get degree statistics (count and total weight)
node_stats = graph.reduce_nodes()
print(f"Nodes: {node_stats.count}, Total weight: {node_stats.weight}")

edge_stats = graph.reduce_edges()
print(f"Edges: {edge_stats.count}, Total weight: {edge_stats.weight}")

# Filter edges by endpoint
edges_to_node_1 = graph.reduce_edges(v=1)
edges_from_node_1 = graph.reduce_edges(u=1)
```

## Troubleshooting

### Common Issues

**Issue**: "Java heap space" error with Neo4J
- **Solution**: Reduce batch size to 1,000 or use a different backend (SQLite/PostgreSQL)

**Issue**: Slow imports with SQLite
- **Solution**: Ensure WAL mode is enabled (automatic on first launch); increase `page_size` pragma

**Issue**: Edge not found after adding
- **Solution**: Check if node IDs are integers; non-integers are hashed via Python's `hash()`. Use `graph.has_edge(u, v)` and check the returned list (not truthiness).

**Issue**: Memory usage still high
- **Solution**: Use streaming (`for edge in graph.edges`) instead of loading all at once. Avoid `list(graph.edges)` on large graphs.

**Issue**: `has_edge()` returns empty list but I expected a boolean
- **Solution**: NetworkXternal deviates from NetworkX here — `has_edge()` returns `list[Edge]`. Check with `if graph.has_edge(u, v):` or `len(graph.has_edge(u, v)) > 0`.

**Issue**: Multiple edges between same nodes all return the same ID
- **Solution**: Use the `key` parameter in `add_edge()` to assign different labels. Edges with the same `(first, second)` but different `label` are distinct.

**Issue**: Integer overflow on edge IDs in large graphs
- **Solution**: Edge IDs use 31-bit signed integers. For very large graphs, ensure your database uses `BigInteger` type (SQLAlchemy does this by default).

**Issue**: `in_edges` returns unexpected results
- **Solution**: `in_edges` is computed as an inverted copy of `out_edges` — it's not stored separately. It swaps `first` and `second` for all directed edges.

### Backend Selection Guide

| Requirement | Recommended Backend |
|-------------|-------------------|
| < 20 MB graph, single process | SQLiteMem or SQLite |
| Multi-process access | PostgreSQL |
| Existing MongoDB infra | MongoDB |
| Existing MySQL infra | MySQL |
| Native graph queries (small) | Neo4J (use with caution) |
| Production, large scale | PostgreSQL |

## See Also

For detailed information on specific topics, see:

- [Database Backends](references/01-database-backends.md) - Complete backend configuration and optimization
- [API Reference](references/02-api-reference.md) - Full method signatures and parameters
- [Performance Benchmarks](references/03-performance-benchmarks.md) - Detailed performance analysis and tuning
- [Migration from NetworkX](references/04-migration-from-networkx.md) - Step-by-step migration guide
- [Advanced Patterns](references/05-advanced-patterns.md) - Bulk operations, streaming, edge cases

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
