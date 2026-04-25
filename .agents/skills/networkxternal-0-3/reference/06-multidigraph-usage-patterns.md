# MultiDiGraph Usage Patterns

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
