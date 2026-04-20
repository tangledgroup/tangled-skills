# Exceptions and Fundamental Concepts

NetworkX provides a hierarchy of exceptions for error handling, plus fundamental graph concepts used throughout the library.

## Exception Hierarchy

```
NetworkXException
├── NetworkXError              # Generic error
├── NetworkXAlgorithmError     # Algorithm failed
│   └── NetworkXUnfeasible     # Operation not feasible
│       ├── NetworkXNoPath     # No path exists
│       └── NetworkXNoCycle    # No cycle exists
├── NodeNotFound               # Node doesn't exist in graph
├── AmbiguousSolution          # Multiple valid solutions found
├── ExceededMaxIterations      # Algorithm exceeded max iterations
├── PowerIterationFailedConvergence  # Power iteration didn't converge
├── HasACycle                  # Cycle detected (expected acyclic)
└── NetworkXPointlessConcept   # Concept not applicable
    └── NetworkXNotImplemented # Feature not implemented
```

## Using Exceptions

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (3, 4)])  # Disconnected

# NetworkXNoPath: No path between disconnected components
try:
    path = nx.shortest_path(G, 1, 3)
except nx.NetworkXNoPath as e:
    print(f"No path: {e}")

# NodeNotFound: Node doesn't exist
try:
    G.remove_node(99)
except nx.NodeNotFound as e:
    print(f"Node not found: {e}")

# NetworkXUnfeasible: Operation not possible
try:
    nx.bellman_ford_path(G, 1, 3)  # No path exists
except nx.NetworkXUnfeasible as e:
    print(f"Not feasible: {e}")

# HasACycle: Expected DAG but found cycle
DG = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
try:
    nx.topological_sort(DG)
except nx.HasACycle as e:
    print(f"Cycle detected: {e}")

# ExceededMaxIterations: Algorithm didn't converge
try:
    nx.pagerank(G, max_iter=2)  # Very few iterations
except nx.ExceededMaxIterations as e:
    print(f"Max iterations exceeded: {e}")

# PowerIterationFailedConvergence: PageRank/HITS didn't converge
try:
    nx.pagerank(G, tol=1e-15, max_iter=2)
except nx.PowerIterationFailedConvergence as e:
    print(f"Convergence failed: {e}")

# AmbiguousSolution: Multiple valid solutions
# (e.g., multiple maximum matchings of same size)
try:
    # This might raise AmbiguousSolution in edge cases
    pass
except nx.AmbiguousSolution as e:
    print(f"Ambiguous solution: {e}")

# NetworkXNotImplemented: Feature not implemented for this graph type
try:
    nx.betweenness_centrality(nx.MultiGraph())  # May not be implemented
except nx.NetworkXNotImplemented as e:
    print(f"Not implemented: {e}")

# NetworkXPointlessConcept: Concept doesn't apply
# E.g., trying to compute diameter of disconnected graph
try:
    nx.diameter(G)  # Fails for disconnected graphs
except nx.NetworkXPointlessConcept as e:
    print(f"Pointless concept: {e}")
```

## Fundamental Graph Concepts

### Graph Types

```python
# Four main graph classes in NetworkX

G = nx.Graph()        # Undirected, no self-loops, no parallel edges
DG = nx.DiGraph()     # Directed, no self-loops, no parallel edges
MG = nx.MultiGraph()  # Undirected, allows self-loops and parallel edges
MDG = nx.MultiDiGraph()  # Directed, allows self-loops and parallel edges
```

### Frozen Graphs (Read-Only)

```python
# Frozen graphs are immutable and faster for iteration
FG = nx.freeze(G)
print(nx.is_frozen(FG))  # True

# Cannot modify frozen graphs
try:
    FG.add_node(99)
except nx.NetworkXError as e:
    print(f"Cannot modify frozen graph: {e}")

# Create empty copy (same type, no data)
empty = nx.create_empty_copy(G)
```

### Graph Views vs Copies

```python
# Views share data with original (zero copy overhead)
subview = nx.subgraph_view(G, filter_node=lambda n: n < 10)
rev_view = nx.reverse_view(DG)

# Restricted view (remove specific edges/nodes from view only)
rv = nx.restricted_view(G, 1, 2)  # Edge (1,2) hidden in view
rv2 = nx.restricted_view(G, 1)     # Node 1 and edges hidden

# Copies are independent
G_copy = G.copy()
G_deep = nx.Graph(G)  # Shallow copy
```

### Graph Filters

```python
from networkx.classes import filters

# Filter functions for graph views
hide_nodes = filters.hide_nodes([1, 2, 3])
show_edges = filters.show_edges([(1, 2), (2, 3)])
no_filter = filters.no_filter  # Always returns True

# Use with subgraph_view
filtered = nx.subgraph_view(G, filter_node=hide_nodes)
```

### Simple Graph Concepts

```python
# NetworkXPointlessConcept enum values
# Used when a concept doesn't apply to the graph type

# E.g., diameter of disconnected graph
G = nx.Graph()
G.add_edges_from([(1, 2), (3, 4)])

try:
    d = nx.diameter(G)
except nx.NetworkXPointlessConcept:
    print("Cannot compute diameter of disconnected graph")

# Use average_shortest_path_length instead
avg = nx.average_shortest_path_length(G)
```

## Error Handling Best Practices

```python
# 1. Check connectivity before shortest path
if nx.has_path(G, source, target):
    path = nx.shortest_path(G, source, target)
else:
    print(f"No path from {source} to {target}")

# 2. Use try/except for algorithms that may not converge
try:
    pr = nx.pagerank(G, tol=1e-6, max_iter=1000)
except nx.PowerIterationFailedConvergence as e:
    print(f"PageRank didn't converge: {e}")
    pr = nx.pagerank(G, tol=0.01)  # Relax tolerance

# 3. Validate input before processing
if not nx.is_connected(G):
    raise nx.NetworkXError("Graph must be connected")

# 4. Handle empty graphs
if G.number_of_nodes() == 0:
    print("Empty graph")

# 5. Check for self-loops in algorithms that don't support them
if G.selfloop_edges():
    G.remove_edges_from(G.selfloop_edges())
```

## Summary

| Exception | When Raised |
|-----------|-------------|
| `NetworkXError` | Generic NetworkX error |
| `NetworkXAlgorithmError` | Algorithm failed to produce valid result |
| `NetworkXUnfeasible` | Operation not mathematically feasible |
| `NetworkXNoPath` | No path exists between nodes |
| `NetworkXNoCycle` | No cycle exists in graph |
| `NodeNotFound` | Referenced node doesn't exist |
| `AmbiguousSolution` | Multiple valid solutions found |
| `ExceededMaxIterations` | Iterative algorithm hit iteration limit |
| `PowerIterationFailedConvergence` | Power iteration didn't converge |
| `HasACycle` | Expected acyclic but cycle found |
| `NetworkXNotImplemented` | Feature not implemented for graph type |
| `NetworkXPointlessConcept` | Concept doesn't apply to this graph |
