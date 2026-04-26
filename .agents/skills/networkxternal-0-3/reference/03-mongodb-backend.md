# MongoDB Backend

## Overview

The `MongoDB` class implements `BaseAPI` directly using PyMongo. It stores nodes and edges as separate collections with BSON documents. Batch size is limited to 10,000 (MongoDB's write command batch limit). Supports concurrent access.

### Connection URL

Format: `mongodb://host:port/database_name`

Default: `mongodb://localhost:27017/graph`

The database name is extracted from the URL path. Username and password can be included in the URL.

### Collections

- `nodes`: Stores Node documents with fields `_id`, `weight`, `label`, `payload`
- `edges`: Stores Edge documents with fields `_id`, `first`, `second`, `weight`, `label`, `is_directed`, `payload`

### Indexes

Created on first initialization via `create_index()`:
- `edges.first` — sparse index for source node lookups
- `edges.second` — sparse index for target node lookups
- `edges.is_directed` — sparse index for directed/undirected filtering

Indexes can be created in background mode (`background=True`) to avoid blocking.

## Aggregation Pipeline Helpers

MongoDB uses aggregation pipelines for most queries. The following pipeline stage builders are provided:

```python
pipe_compute_degree() -> dict
```
Returns a `$group` stage that computes count and sum of weights:
```json
{ "$group": { "_id": None, "count": { "$sum": 1 }, "weight": { "$sum": "$weight" } } }
```

```python
pipe_match_edge_members(u, v) -> dict | None
```
Returns a `$match` stage filtering edges by source/target endpoints. Logic mirrors the SQL `filter_edges_members`:
- Both endpoints: matches `first=u AND second=v` (directed) or either direction (undirected)
- Single endpoint: matches only that role
- Self-loop: matches edges where node appears in either role

```python
pipe_match_label(key) -> dict | None
```
Returns `$match` stage for edge label filtering. Returns `None` when key is None/negative (no filter applied).

## Method Details

### Metadata

```python
reduce_nodes() -> GraphDegree
reduce_edges(u=None, v=None, key=None) -> GraphDegree
biggest_edge_id() -> int
```

Uses aggregation pipelines. `biggest_edge_id` sorts by `_id` descending with limit 1.

### Bulk Reads

```python
nodes -> Sequence[Node]
edges -> Sequence[Edge]
out_edges -> Sequence[Edge]
mentioned_nodes_ids -> Sequence[int]
```

`out_edges` filters by `is_directed: True`. `mentioned_nodes_ids` iterates edges projecting only `first` and `second` fields to avoid the 16 MB BSON document size limit (using `.distinct()` on large collections can exceed this limit).

### Random Reads

```python
has_node(n) -> Optional[Node]
has_edge(u, v, key=None) -> Sequence[Edge]
neighbors_of_group(vs: Sequence[int]) -> Set[int]
```

`has_edge` uses aggregation pipeline with match stages. `neighbors_of_group` uses `$or` filter on `first` and `second` fields with `$in` operator.

### Random Writes

```python
add(obj, upsert=True) -> int
remove(obj) -> int
```

Single items use `update_one` (upsert) or `insert_one`. Bulk operations use `bulk_write` with `UpdateOne` requests for upsert, or `insert_many` for insert-only. Bulk write is unordered (`ordered=False`) for parallelism. Returns count of inserted/upserted documents.

```python
remove_node(n) -> int
```
Removes the node document and deletes all edges where `n` appears as `first` or `second`.

### Bulk Operations

```python
clear_edges()
clear()
```

Uses `collection.drop()` to remove collections entirely. `clear` drops both edges and nodes.
