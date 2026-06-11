# MongoDB Implementation

## Overview

MongoDB implements `BaseAPI` directly rather than through `BaseSQL`. It uses PyMongo's aggregation pipelines for analytical queries and `bulk_write()` for batch upserts.

## Connection and Setup

```python
from networkxternal.mongodb import MongoDB

graph = MongoDB(url="mongodb://localhost:27017/graph")
```

The URL path determines the database name (defaults to `graph`). Two collections are created: `edges` and `nodes`.

### Indexes

On initialization, sparse indexes are created on:

- `first` — source node ID
- `second` — target node ID
- `is_directed` — direction flag

These enable efficient neighbor lookups and directed/undirected filtering.

## Aggregation Pipeline Queries

MongoDB uses aggregation pipelines for edge queries rather than simple `find()`. The pipeline pattern is:

```python
[
    pipe_match_edge_members(u, v),  # optional $match stage
    pipe_match_label(key),           # optional $match stage
    pipe_compute_degree(),            # $group stage for count/sum
]
```

Each stage returns `None` if the filter parameter is -1 (meaning "any"), and the pipeline filters out `None` stages before execution.

### Pipeline Helpers

- `pipe_match_edge_members(u, v)` — builds `$match` for node membership, respecting directed/undirected mode
- `pipe_match_label(key)` — builds `$match` for label filtering
- `pipe_compute_degree()` — builds `$group` stage that returns `count` and `weight` sum

## Batch Operations

### Upsert Mode

Uses `bulk_write()` with `UpdateOne` operations and `ordered=False` for parallel execution:

```python
ops = [UpdateOne(
    filter={"_id": o._id},
    update={"$set": o.__dict__},
    upsert=True
) for o in objects]
result = collection.bulk_write(requests=ops, ordered=False)
```

Returns `nUpserted + nInserted` from the bulk API result. Catches `BulkWriteError` and prints details.

### Insert-Only Mode

Uses `insert_many()` with `ordered=False`. Returns count of inserted IDs.

## Reading Operations

### Node Retrieval

```python
@property
def nodes(self) -> Sequence[Node]:
    return [Node(**as_dict) for as_dict in self.nodes_collection.find()]
```

All documents are deserialized into `Node` dataclasses. Same pattern for edges.

### Edge Retrieval with Filters

`has_edge(u, v, key)` uses aggregation pipeline with match stages for members and label, returning all matching edges as `Edge` objects.

### Neighbor Queries

`neighbors_of_group(vs)` uses `$or` filter on `first` and `second` fields with `$in` operator, projecting only the node IDs needed. Results are deduplicated against the input set.

### Mentioned Node IDs

Due to MongoDB's 16 MB BSON response limit, `distinct()` cannot be used directly on large collections. Instead, `mentioned_nodes_ids()` iterates through edges projecting only `first` or `second` fields separately, collecting into a Python set.

## Batch Size

`__max_batch_size__` is set to 10,000. MongoDB's write command batch limit increased from 1,000 (pre-version 2.6) to 100,000, but practical improvement diminishes beyond 10,000 depending on document size and available RAM.
