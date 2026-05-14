# Neo4J Backend

## Overview

The `Neo4J` class implements `BaseAPI` using the official Neo4J Bolt driver with Cypher queries. Batch size is limited to 1,000 due to Java heap space constraints on typical hardware. Supports concurrent access.

### Connection URL

Format: `bolt://username:password@host:port/database_name`

Default: `bolt://localhost:7687/graph`

The username and password are extracted from the URL by the constructor. The database name is used to generate unique label prefixes.

### Labels and Namespacing

Neo4J cannot easily switch between databases on the same server. NetworkXternal uses node/relationship labels to namespace different graphs within a single Neo4J instance:

- Node label: `v<first_char_of_db_name>` (e.g., `vg` for database "graph")
- Edge label: `e<first_char_of_db_name>` (e.g., `eg` for database "graph")

All Cypher queries are generated with these labels substituted in, so multiple disjoint graphs can coexist in the same Neo4J instance.

### Known Limitations

1. **Space inefficiency**: Cannot overwrite native Neo4J node IDs, so vertices are indexed by an artificial `_id` property alongside native IDs.

2. **Edge indexing**: Indexing edge properties is only available in the Enterprise Edition. Querying edges by ID can be slower than searching by connected node IDs.

3. **Stability**: Neo4J is known to crash with Java heap space errors, especially on laptops. CPU utilization is 10-20x higher than other backends. Importing a 30 MB CSV file allocated 1.4 GB of RAM in testing.

4. **API version compatibility**: Issues between Neo4J API versions 3.5 and 4.x.

### Constructor Options

```python
Neo4J(
    url="bolt://localhost:7687/graph",
    enterprise_edition=False,
    import_directory="~/import",
    use_full_name_for_label=False,
    use_indexes_over_constraints=True,
    **kwargs
)
```

- `enterprise_edition`: Enables edge uniqueness constraints (Enterprise-only feature)
- `import_directory`: Directory for CSV file imports (must be Neo4J's import directory)
- `use_indexes_over_constraints`: When True, creates indexes instead of uniqueness constraints

### Index and Constraint Setup

On initialization, the backend checks existing indexes/constraints and creates missing ones:

```python
create_index_nodes()
```
Creates a named index on the `_id` property of nodes:
```cypher
CREATE INDEX indexVG FOR (v:VG) ON (v._id)
```

```python
create_constraint_nodes()
```
Creates a uniqueness constraint on node `_id`:
```cypher
CREATE CONSTRAINT constraintVG ON (v:VG) ASSERT (v._id) IS UNIQUE
```

```python
create_constraint_edges()
```
Enterprise-only. Creates uniqueness constraint on edge `_id`:
```cypher
CREATE CONSTRAINT uniqueEG ON ()-[e:EG]-() ASSERT (e._id) IS UNIQUE
```

## Cypher Query Patterns

### Edge Queries

```python
has_edge(first, second) -> List[Edge]
edges_from(v) -> List[Edge]
edges_to(v) -> List[Edge]
edges_related(v) -> List[Edge]
```

Uses `MATCH` patterns with directed (`->`) or undirected (`-`) relationship syntax depending on the graph's `directed` flag.

Example for directed graph:
```cypher
MATCH (first:VG {_id: 1})-[e:EG]->(second:VG {_id: 2})
RETURN first._id, second._id, e.weight
```

### Neighborhood Queries

```python
neighbors(v) -> Set[int]
neighbors_of_group(vs) -> Set[int]
neighbors_of_neighbors(v, include_related=False) -> Set[int]
```

Two-hop queries use chained relationship patterns:
```cypher
MATCH (v:VG {_id: 1})-[:EG]-(:VG)-[:EG]-(v_unrelated:VG)
WHERE NOT EXISTS { MATCH (v)-[e_banned:EG]-(v_unrelated) }
  AND NOT (v._id = v_unrelated._id)
RETURN v_unrelated._id as _id
```

### Metadata

```python
reduce_nodes() -> int
reduce_edges() -> int
degree_neighbors(v) -> (int, float)
degree_predecessors(v) -> (int, float)
degree_successors(v) -> (int, float)
biggest_edge_id() -> int
```

Degree methods return count and sum of weights for edges connected to a node.

### Shortest Path

```python
shortest_path(first, second) -> (List[int], float)
```

Uses Neo4J's `algo.shortestPath.stream` procedure:
```cypher
MATCH (first:VG {_id: 1}), (second:VG {_id: 2})
CALL algo.shortestPath.stream(first, second, "weight")
YIELD nodeId, weight
RETURN v_on_path._id AS _id, weight
```

Returns path as list of node IDs and total weight.

## Write Operations

### Single Edge Insert

```python
add(e: Edge) -> bool
insert_edge(e: Edge) -> bool
```

`add` uses `MERGE` (upsert — slow without indexes). `insert_edge` uses `CREATE` (faster, no upsert check):
```cypher
MERGE (first:VG {_id: 1})
MERGE (second:VG {_id: 2})
CREATE (first)-[:EG {_id: 100, weight: 1.0}]->(second)
```

### Bulk Insert

```python
insert_edges(es: List[Edge]) -> int
```

Builds a single Cypher statement with all node MERGEs followed by edge CREATEs. Processes in batches of `__max_batch_size__` (1,000).

### CSV Import

```python
add_from_csv(filepath, is_directed=True) -> int
insert_adjacency_list_in_parts(filepath, is_directed=True) -> int
```

Both copy the file to Neo4J's import directory and use `LOAD CSV WITH HEADERS`. The "in parts" variant separates node creation and edge creation into two passes with `USING PERIODIC COMMIT` for memory efficiency.

CSV format expected: columns `first`, `second`, `weight`.

### Remove

```python
remove(e: Edge) -> bool
remove_node(v: int)
```

Edge removal matches by `_id` if known, otherwise by endpoints. Node removal uses `DETACH DELETE` to remove the node and all its relationships.

### Clear

```python
clear()
```

Detaches and deletes all nodes with the graph's label, then drops indexes and constraints:
```cypher
MATCH (v:VG) DETACH DELETE v
DROP INDEX indexVG
DROP CONSTRAINT constraintVG
```
