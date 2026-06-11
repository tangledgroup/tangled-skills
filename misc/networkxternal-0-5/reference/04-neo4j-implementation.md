# Neo4J Implementation

## Overview

Neo4J implements `BaseAPI` directly using the Bolt protocol and Cypher query language. It has the most significant limitations among supported backends due to Java VM overhead, heap management issues, and enterprise-edition feature gates.

## Connection and Setup

```python
from networkxternal.neo4j import Neo4J

graph = Neo4J(url="bolt://user:pass@localhost:7687/graph")
```

The URL provides scheme, host, port, username, password, and database name. Authentication credentials are parsed from the URL — Neo4J cannot resolve them automatically.

### Label System

Neo4J doesn't support easy switching between databases on the same server. The library uses label prefixes to isolate disjoint datasets:

- The last character of the database name becomes a suffix (e.g., `graph` → `_v` = `vh`, `_e` = `eh`)
- Nodes are labeled as `:{_v}` and edges as `:{_e}`
- All Cypher queries use these labels to scope operations to the correct dataset

## Indexes and Constraints

On initialization, the library checks for existing indexes/constraints and creates them if missing:

### Index Mode (default)

Creates a named index on node `_id`:
```cypher
CREATE INDEX indexVERTEX FOR (v:VERTEX) ON (v._id)
```

### Constraint Mode

When `use_indexes_over_constraints=False`, creates uniqueness constraints instead:
```cypher
CREATE CONSTRAINT constraintVERTEX ON (v:VERTEX) ASSERT (v._id) IS UNIQUE
```

Edge constraints are only available in Enterprise Edition. Without them, edge queries by ID require full scans.

## Cypher Query Patterns

### Edge Lookup

Directed:
```cypher
MATCH (first:VERTEX {_id: 1})-[e:EDGE]->(second:VERTEX {_id: 2})
RETURN first._id, second._id, e.weight
```

Undirected:
```cypher
MATCH (first:VERTEX {_id: 1})-[e:EDGE]-(second:VERTEX {_id: 2})
RETURN first._id, second._id, e.weight
```

### Neighbor Queries

`neighbors(v)` returns all connected node IDs:
```cypher
MATCH (:VERTEX {_id: %d})-[:EDGE]-(v_related:VERTEX)
RETURN v_related._id as _id
```

`neighbors_of_neighbors(v, include_related=False)` finds 2-hop neighbors, optionally excluding direct neighbors:
```cypher
MATCH (v:VERTEX {_id: %d})-[:EDGE]-(:VERTEX)-[:EDGE]-(v_unrelated:VERTEX)
WHERE NOT EXISTS { MATCH (v)-[e_banned:EDGE]-(v_unrelated) }
  AND NOT (v._id = v_unrelated._id)
RETURN v_unrelated._id as _id
```

### Shortest Path

Uses the APOC/Graph Data Science plugin's `algo.shortestPath.stream()`:
```cypher
MATCH (first:VERTEX {_id: %d}), (second:VERTEX {_id: %d})
CALL algo.shortestPath.stream(first, second, "weight")
YIELD nodeId, weight
MATCH (v_on_path:Loc) WHERE id(v_on_path) = nodeId
RETURN v_on_path._id AS _id, weight
```

## CSV Import

Two import methods are available:

### `add_from_csv(filepath, is_directed=True)`

Single-pass import using `LOAD CSV WITH HEADERS`. Creates nodes and edges in one query. Expected CSV format: `first,second,weight` with headers.

### `insert_adjacency_list_in_parts(filepath, is_directed=True)`

Two-pass import using `USING PERIODIC COMMIT`: first creates all nodes, then creates edges between matched nodes. More memory-efficient for large files.

Both methods copy the file to Neo4J's import directory before processing and clean up afterward.

## Known Limitations

1. **Space inefficiency**: Cannot overwrite native node IDs, so vertices are indexed by artificial `_id` property alongside internal Neo4J IDs.

2. **Edge indexing**: Indexing edge properties is Enterprise Edition only. Querying edges by ID can be slower than searching by connected node IDs.

3. **Java overhead**: CPU utilization is often 10-20x higher than other databases. Importing a 30 MB CSV allocated 1.4 GB of RAM.

4. **Stability issues**: Frequent crashes including:
   - `TransientError`: "not enough stack size"
   - `DatabaseError`: "Java heap space"
   - Inconsistent query profiler outputs

5. **Batch size**: Limited to 1,000 edges per batch on typical laptop hardware due to heap constraints.

## Cleanup

`clear()` removes all labeled nodes (with their edges via DETACH DELETE), then drops any indexes and constraints that were created:

```cypher
MATCH (v:{label}) DETACH DELETE v
DROP INDEX index{label}
```
