# Basic Operations

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
