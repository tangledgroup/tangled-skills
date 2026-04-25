# Performance Considerations

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
