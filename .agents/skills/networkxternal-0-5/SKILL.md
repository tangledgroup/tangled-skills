---
name: networkxternal-0-5
description: NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, MongoDB, Neo4J). Use when working with Terabyte-Petabyte graphs that won't fit into RAM, needing multi-edge support with key/label-based edge identity, or building graph applications requiring database-backed storage without changing application code.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - graph
  - database
  - networkx
  - external-memory
  - sql
  - mongodb
  - neo4j
category: data
external_references:
  - https://github.com/ashvardanian/NetworkXternal
---

# NetworkXternal 0.5

## Overview

NetworkXternal provides a [NetworkX](https://networkx.org/)-compatible `MultiDiGraph` interface for graphs persisted in external databases. This lets you scale from Megabyte-Gigabyte in-memory graphs to Terabyte-Petabyte graphs that won't fit into RAM, without changing your application code.

The trade-off is performance — database-backed operations are slower than in-memory equivalents — but it enables graph workloads impossible with pure NetworkX.

## When to Use

- Graphs too large for RAM (Terabyte-Petabyte scale)
- Need persistent graph storage across sessions
- Building graph applications with existing database infrastructure
- Multi-edge directed/undirected graphs with edge keys and labels
- Migrating from in-memory NetworkX to database-backed storage with minimal code changes

## Supported Databases

- **SQLite** — fastest for tiny databases under 20 MB, embedded single-file
- **PostgreSQL** — most feature-rich open-source relational DB, optimized upserts
- **MySQL** — commonly-used relational DB with CSV import support
- **MongoDB** — distributed document store with aggregation pipeline queries
- **Neo4J** — native graph database using Cypher DSL and Bolt protocol

## Core Architecture

The library uses a class hierarchy with `BaseAPI` as the abstract root:

- `BaseAPI` — abstract graph API (shared by all backends)
- `BaseSQL(BaseAPI)` — SQL-compatible layer using SQLAlchemy ORM
- `SQLite(BaseSQL)` — SQLite with performance pragmas
- `SQLiteMem(BaseSQL)` — in-memory SQLite
- `PostgreSQL(BaseSQL)` — PostgreSQL with ON CONFLICT upserts
- `MySQL(BaseSQL)` — MySQL with session-level tuning
- `MongoDB(BaseAPI)` — MongoDB with aggregation pipelines
- `Neo4J(BaseAPI)` — Neo4J with Cypher queries via Bolt protocol

## Installation

```bash
pip install networkxternal
```

Dependencies: `networkx`, `sqlalchemy`, `neo4j`, `pymongo`.

## Usage Examples

### SQLite (file-based)

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///my_graph.db")
graph.add_node(1, label="start")
graph.add_node(2, label="end")
graph.add_edge(1, 2, weight=5.0)

print(graph.number_of_nodes())  # 2
print(graph.number_of_edges())  # 1
```

### SQLite (in-memory)

```python
from networkxternal.sqlite import SQLiteMem

graph = SQLiteMem()
graph.add_edge(1, 2, weight=3.0)
graph.add_edge(2, 3, weight=7.0)
print(graph.neighbors(2))  # {1, 3}
```

### PostgreSQL

```python
from networkxternal.postgres import PostgreSQL

graph = PostgreSQL(url="postgresql://user:pass@localhost/graph_db")
graph.add_edge("alice", "bob", weight=1.0, label="friend")
graph.add_edge("bob", "charlie", weight=2.0, label="colleague")
print(graph.successors("alice"))  # [hashed_id_of_bob]
```

### MongoDB

```python
from networkxternal.mongodb import MongoDB

graph = MongoDB(url="mongodb://localhost:27017/graph")
graph.add_edge(1, 2, weight=4.0)
graph.add_edge(2, 3, weight=6.0)
print(graph.number_of_edges())  # 2
```

### Neo4J

```python
from networkxternal.neo4j import Neo4J

graph = Neo4J(url="bolt://user:pass@localhost:7687/graph")
graph.add_edge(1, 2, weight=3.0)
path, total_weight = graph.shortest_path(1, 3)
```

## API Compatibility

NetworkXternal targets `MultiDiGraph` compatibility from NetworkX. Supported methods:

- **Metadata**: `number_of_nodes()`, `number_of_edges()`, `order()`, `is_directed()`, `is_multigraph()`
- **Node operations**: `add_node()`, `has_node()`, `remove_node()`
- **Edge operations**: `add_edge()`, `has_edge()`, `get_edge_data()`
- **Neighbor queries**: `neighbors()`, `successors()`, `predecessors()`, `neighbors_of_group()`, `neighbors_of_neighbors()`
- **Bulk operations**: `add()`, `remove()`, `clear()`, `clear_edges()`, `add_stream()`
- **Iteration**: `__iter__()`, `__len__()`, `__contains__()`
- **Properties**: `.nodes`, `.edges`, `.out_edges`, `.in_edges`, `.mentioned_nodes_ids`

Non-integer node IDs are hashed. Edge attributes include `_id`, `weight`, `label`, and `directed`. Node attributes include `_id`, `weight`, and `label`.

## Advanced Topics

**Database Backends**: Detailed comparison of SQLite, PostgreSQL, MySQL, MongoDB, and Neo4J implementations → [Database Backends](reference/01-database-backends.md)

**SQL Architecture**: BaseSQL layer, SQLAlchemy ORM models, bulk import patterns → [SQL Architecture](reference/02-sql-architecture.md)

**MongoDB Implementation**: Aggregation pipelines, batch operations, index strategy → [MongoDB Implementation](reference/03-mongodb-implementation.md)

**Neo4J Implementation**: Cypher queries, Bolt protocol, CSV imports, known limitations → [Neo4J Implementation](reference/04-neo4j-implementation.md)
