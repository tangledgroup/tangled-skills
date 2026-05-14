# Usage Examples

## Creating Graphs

### SQLite (in-memory)

```python
from networkxternal.sqlite import SQLiteMem

g = SQLiteMem(directed=True, weighted=True)
g.add_node(1, label="start")
g.add_edge(1, 2, weight=3.5)
g.add_edge(2, 3, weight=1.0)

print(g.number_of_nodes())   # 3
print(g.number_of_edges())   # 2
```

### SQLite (file-based)

```python
from networkxternal.sqlite import SQLite

g = SQLite("sqlite:///my_graph.db", directed=True)
g.add_edge(1, 2, weight=1.0)
g.add_edge(2, 3, weight=2.0)
```

### PostgreSQL

```python
from networkxternal.postgres import PostgreSQL

g = PostgreSQL("postgresql://user:pass@localhost:5432/graph_db")
g.add_edge(1, 2, weight=1.0)
```

### MySQL

```python
from networkxternal.mysql import MySQL

g = MySQL("mysql+pymysql://user:pass@localhost:3306/graph_db")
g.add_edge(1, 2, weight=1.0)
```

### MongoDB

```python
from networkxternal.mongodb import MongoDB

g = MongoDB("mongodb://localhost:27017/my_graph", directed=True)
g.add_edge(1, 2, weight=1.0)
```

### Neo4J

```python
from networkxternal.neo4j import Neo4J

g = Neo4J("bolt://user:pass@localhost:7687/graph_db")
g.add_edge(1, 2, weight=1.0)
```

## Common Operations

### Adding data

```python
# Single node with attributes
g.add_node(42, label="special", custom_attr="value")

# Single edge
g.add_edge(1, 2, weight=5.0, label=10)

# Bulk add using Edge objects
from networkxternal.helpers.edge import Edge
edges = [
    Edge(first=1, second=2, weight=1.0),
    Edge(first=2, second=3, weight=2.0),
]
g.add(edges)
```

### Querying the graph

```python
# Check if node exists
node = g.has_node(1)

# Find edges between two nodes
edges = g.has_edge(1, 2)

# Get neighbors
neighbors = g.neighbors(1)

# Directed graph: successors and predecessors
successors = g.successors(1)
predecessors = g.predecessors(1)

# Two-hop neighborhood
two_hop = g.neighbors_of_neighbors(1)
```

### Bulk import from adjacency list

```python
# Stream of (first, second, weight) tuples
stream = [
    (1, 2, 1.0),
    (2, 3, 2.0),
    (3, 4, 0.5),
]
g.add_stream(stream)
```

### Graph metadata

```python
# Node and edge counts
print(g.order())              # number of nodes
print(g.number_of_edges())    # number of edges

# Reduction (count + sum of weights)
node_stats = g.reduce_nodes()
edge_stats = g.reduce_edges()
print(f"Nodes: {node_stats.count}, total weight: {node_stats.weight}")

# Largest edge ID
max_id = g.biggest_edge_id()
```

### Removing data

```python
# Remove a single node (and its edges)
g.remove_node(1)

# Remove a specific edge
from networkxternal.helpers.edge import Edge
g.remove(Edge(first=2, second=3))

# Clear everything
g.clear()
```

## Multi-Graph Patterns

NetworkXternal supports multi-edges by default. Multiple edges can connect the same node pair:

```python
g = SQLiteMem(multigraph=True)
g.add_edge(1, 2, weight=1.0, label=0)
g.add_edge(1, 2, weight=5.0, label=1)

# Both edges are returned
edges = g.has_edge(1, 2)
print(len(edges))  # 2

# Filter by label
edges_l0 = g.has_edge(1, 2, key=0)
```

## Undirected Graphs

```python
g = SQLiteMem(directed=False)
g.add_edge(1, 2, weight=1.0)

# neighbors() returns nodes connected in either direction
n = g.neighbors(1)
```

## Placeholder Backends

The library includes placeholder classes for planned backends:

- `Cayley` — RDF-focused graph database (Go-based, via pyley bindings)
- `BlazingSQL` — GPU-accelerated analytics engine (Rapids.ai, NVIDIA GPUs only)

These are not yet implemented.
