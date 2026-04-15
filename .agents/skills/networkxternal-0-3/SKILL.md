---
name: networkxternal-0-3
description: NetworkX-compatible interface for external memory graphs persisted in databases (SQLite, PostgreSQL, MySQL, MongoDB, Neo4J). Use when working with Terabyte-Petabyte graphs that won't fit into RAM, migrating from NetworkX to persistent storage, or building graph applications requiring database-backed storage without changing application code.
license: MIT
author: Generated from ashvardanian/NetworkXternal v0.3.0
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
  - https://networkx.github.io/
---

# NetworkXternal 0.3

## Overview

**NetworkXternal** is a NetworkX-like interface for external memory graphs persisted in various databases. It lets you upscale from Megabyte-Gigabyte graphs to Terabyte-Petabyte graphs (that won't fit into RAM) without changing your code.

The library provides drop-in compatibility with [NetworkX](https://networkx.github.io/) `MultiDiGraph` API while storing graph data in:

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

### NetworkX Compatibility

NetworkXternal implements a subset of the NetworkX `MultiDiGraph` API:

| Feature | Supported | Notes |
|---------|-----------|-------|
| Directed/undirected graphs | ✅ | Configurable per instance |
| Weighted edges | ✅ | Float weights supported |
| Multi-edges | ✅ | Multiple edges between same nodes |
| Node/edge attributes | ✅ | Stored as JSON payload |
| Integer node IDs | ✅ | Non-integers are hashed to integers |
| Edge uniqueness | ⚠️ | Use edge ID hashing for uniqueness |

### Data Model

**Nodes** have:
- `_id`: Integer identifier (auto-generated or provided)
- `weight`: Float value (default: 1.0)
- `label`: Integer label (default: -1)
- `payload`: Dict of custom attributes (stored as JSON)

**Edges** have:
- `_id`: Integer identifier (auto-generated or computed from endpoints)
- `first`: Source node ID
- `second`: Target node ID
- `is_directed`: Boolean flag
- `weight`: Float value (default: 1.0)
- `label`: Integer label (default: -1)
- `payload`: Dict of custom attributes (stored as JSON)

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
    enterprise_edition=False  # Set True for edge constraints
)

# WARNING: Neo4J has known issues:
# - High CPU usage (10-20x other DBs)
# - Java heap space crashes on large imports
# - Edge indexing only in Enterprise edition
# - Unstable with datasets > small size
```

**Best for**: Small graphs where native graph queries are needed, NOT recommended for large-scale use

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
edge_count = graph.number_of_edges()

# Check if node exists
node = graph.has_node(1)  # Returns Node object or None

# Check if edge exists
edges = graph.has_edge(1, 2)  # Returns list of Edge objects or None

# Get neighbors (undirected)
neighbors = graph.neighbors(1)  # Set of node IDs

# Get successors/predecessors (directed)
successors = graph.successors(1)  # Nodes reachable from 1
predecessors = graph.predecessors(1)  # Nodes that point to 1

# Get all nodes/edges (can be expensive!)
all_nodes = list(graph.nodes)
all_edges = list(graph.edges)
```

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

## Common Patterns

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
- **Solution**: Reduce batch size to 1,000 or use a different backend

**Issue**: Slow imports with SQLite
- **Solution**: Ensure WAL mode is enabled (automatic on first launch)

**Issue**: Edge not found after adding
- **Solution**: Check if node IDs are integers; strings are hashed

**Issue**: Memory usage still high
- **Solution**: Use streaming (`for edge in graph.edges`) instead of loading all at once

### Backend Selection Guide

| Requirement | Recommended Backend |
|-------------|-------------------|
| < 20 MB graph, single process | SQLiteMem or SQLite |
| Multi-process access | PostgreSQL |
| Existing MongoDB infra | MongoDB |
| Existing MySQL infra | MySQL |
| Native graph queries (small) | Neo4J (use with caution) |
| Production, large scale | PostgreSQL |

## References

- **GitHub Repository**: https://github.com/ashvardanian/NetworkXternal
- **NetworkX Documentation**: https://networkx.github.io/documentation/stable/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/

## See Also

For detailed information on specific topics, see:

- [Database Backends](references/01-database-backends.md) - Complete backend configuration and optimization
- [API Reference](references/02-api-reference.md) - Full method signatures and parameters
- [Performance Benchmarks](references/03-performance-benchmarks.md) - Detailed performance analysis and tuning
- [Migration from NetworkX](references/04-migration-from-networkx.md) - Step-by-step migration guide
- [Advanced Patterns](references/05-advanced-patterns.md) - Bulk operations, streaming, edge cases
