# Graph Traversal and Tree Algorithms

NetworkX provides comprehensive traversal algorithms (BFS, DFS, beam search) and tree operations (branchings, arborescences, Prufer sequences).

## Breadth-First Search (BFS)

### BFS Tree and Edges

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (2, 5)])

# BFS tree rooted at a node
bfs_tree = nx.bfs_tree(G, source=1)
print(list(bfs_tree.edges()))
# [(1, 2), (1, 3), (2, 4), (2, 5)]

# BFS edges (generator yielding edges in BFS order)
bfs_edges = list(nx.bfs_edges(G, source=1))
print(bfs_edges)
# [(1, 2), (1, 3), (2, 4), (2, 5)]

# BFS with labeled edges (tree, back, forward, cross)
bfs_labeled = list(nx.bfs_labeled_edges(G, source=1))
print(bfs_labeled)
# [(1, 2, 'tree'), (1, 3, 'tree'), (2, 4, 'tree'), (2, 5, 'tree')]

# BFS successors (node -> list of children in BFS tree)
bfs_succ = nx.bfs_successors(G, source=1)
print(list(bfs_succ))
# [(1, [2, 3]), (2, [4, 5])]

# BFS predecessors
bfs_pred = nx.bfs_predecessors(G, source=1)
print(dict(bfs_pred))
# {2: 1, 3: 1, 4: 2, 5: 2}

# BFS layers (list of lists, one per level)
layers = list(nx.bfs_layers(G, sources=[1]))
print(layers)
# [[1], [2, 3], [4, 5]]

# BFS edges (generic, with callback)
def custom_callback(G, u, v:
    print(f"Visiting edge ({u}, {v})")

bfs_gen = nx.algorithms.traversal.breadth_first_search.generic_bfs_edges(
    G, source=1, cycle_check=False
)

# Descendants at specific distance
desc_d1 = nx.descendants_at_distance(G, 1, 1)  # Immediate neighbors
desc_d2 = nx.descendants_at_distance(G, 1, 2)  # Nodes at distance 2
print(desc_d2)  # {4, 5}
```

### BFS for Directed Graphs

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (1, 3)])

# BFS respects edge direction
bfs_tree = nx.bfs_tree(DG, source=1)
print(list(bfs_tree.edges()))  # [(1, 2), (2, 3), (1, 3)]

# BFS from multiple sources
multi_sources = nx.bfs_layers(DG, sources=[1, 4])
print(list(multi_sources))

# BFS with depth limit
for node in nx.bfs_tree(DG, source=1, depth_limit=2):
    print(node)
```

## Depth-First Search (DFS)

### DFS Tree and Traversals

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (2, 4), (3, 5)])

# DFS tree rooted at a node
dfs_tree = nx.dfs_tree(G, source=1)
print(list(dfs_tree.edges()))
# [(1, 2), (2, 3), (3, 5)]  # or [(1, 2), (2, 4), (4, ...)]

# DFS edges (generator yielding edges in DFS order)
dfs_edges = list(nx.dfs_edges(G, source=1))
print(dfs_edges)

# DFS with labeled edges (tree, back, forward, cross)
dfs_labeled = list(nx.dfs_labeled_edges(G, source=1))
print(dfs_labeled)
# [(1, 2, 'tree'), (2, 3, 'tree'), (3, 5, 'back'/'tree'), ...]

# DFS predecessors
dfs_pred = nx.dfs_predecessors(G, source=1)
print(dict(dfs_pred))

# DFS successors
dfs_succ = nx.dfs_successors(G, source=1)
print(dict(dfs_succ))

# Preorder traversal (visit node before children)
preorder = list(nx.dfs_preorder_nodes(G, source=1))
print(preorder)  # e.g., [1, 2, 3, 5, 4]

# Postorder traversal (visit children before node)
postorder = list(nx.dfs_postorder_nodes(G, source=1))
print(postorder)  # e.g., [5, 3, 4, 2, 1]
```

### DFS for Directed Graphs

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4)])

# DFS on directed graph identifies back edges (cycles)
dfs_labeled = list(nx.dfs_labeled_edges(DG, source=1))
for u, v, edge_type in dfs_labeled:
    if edge_type == 'back':
        print(f"Back edge ({u}, {v}) indicates a cycle")

# DFS forest for disconnected graph
forest = list(nx.dfs_edges(DG))  # Starts from first node, then others
```

## Beam Search

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)])

# BFS with beam width (limits frontier size)
beam_edges = list(nx.bfs_beam_edges(G, source=1, width=2))
print(beam_edges)
# Explores at most 2 nodes per level simultaneously

# Beam search is useful for large graphs where full BFS/DFS is too expensive
# It trades completeness for memory efficiency
```

## Edge-Based Traversal

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Edge-based BFS (iterates over edges, not nodes)
edge_bfs = list(nx.edge_bfs(G, source=1))
print(edge_bfs)
# [(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)]
# Yields both directions for undirected graphs

# Edge-based DFS
edge_dfs = list(nx.edge_dfs(G, source=1))
print(edge_dfs)
```

## Tree Algorithms

### Spanning Trees and Arborescences

```python
import networkx as nx
from networkx.algorithms import tree

G = nx.Graph()
G.add_edges_from([
    (1, 2, {"weight": 4}),
    (1, 3, {"weight": 2}),
    (2, 3, {"weight": 1}),
    (2, 4, {"weight": 5}),
    (3, 4, {"weight": 3}),
])

# Minimum spanning tree (Kruskal's/Prim's)
mst = nx.minimum_spanning_tree(G)
print(list(mst.edges(data=True)))

# Maximum spanning tree
mxt = nx.maximum_spanning_tree(G)

# Minimum spanning forest (for disconnected graphs)
msf = nx.minimum_spanning_forest(G)

# Using specific algorithm
mst_prim = nx.minimum_spanning_tree(G, algorithm='prim')
mst_kruskal = nx.minimum_spanning_tree(G, algorithm='kruskal')
mst_boruvka = nx.minimum_spanning_tree(G, algorithm='boruvka')

# Weight of spanning tree
weight = nx.boundary_weight(mst, weight="weight")
```

### Arborescences (Directed Spanning Trees)

```python
DG = nx.DiGraph()
DG.add_edges_from([
    (1, 2, {"weight": 4}),
    (1, 3, {"weight": 2}),
    (2, 3, {"weight": 1}),
    (2, 4, {"weight": 5}),
    (3, 4, {"weight": 3}),
])

# Minimum spanning arborescence (directed)
min_arb = nx.minimum_spanning_arborescence(DG, root=1)
print(list(min_arb.edges()))

# Maximum spanning arborescence
max_arb = nx.maximum_spanning_arborescence(DG, root=1)

# Minimum/maximum branching (for graphs without guaranteed arborescence)
min_branch = nx.minimum_branching(DG)
max_branch = nx.maximum_branching(DG)

# Greedy branching (fast approximation)
greedy_br = nx.greedy_branching(DG)

# Weight of branching
br_weight = nx.branching_weight(min_arb, weight="weight")

# Arborescence iterator (enumerate all arborescences)
for arb in nx.ArborescenceIterator(DG, root=1):
    print(list(arb.edges()))
```

### Prufer Sequences

```python
# Convert tree to Prufer sequence (unique encoding)
T = nx.balanced_tree(2, 2)  # A small tree
prufer = nx.to_prufer_sequence(T)
print(prufer)  # e.g., [0, 0, 1]

# Reconstruct tree from Prufer sequence
T_reconstructed = nx.from_prufer_sequence(prufer)
assert nx.is_isomorphic(T, T_reconstructed)

# For labeled trees with specific node labels
T2 = nx.Graph()
T2.add_edges_from([("A", "B"), ("B", "C")])
prufer2 = nx.to_prufer_sequence(T2, label_mapping=str)
T2_back = nx.from_prufer_sequence(prufer2, reverse_label_mapping=str)
```

### Nested Tuple Representation

```python
# Convert tree to nested tuple (hierarchical representation)
T = nx.balanced_tree(2, 2)
nested = nx.to_nested_tuple(T, source=0)
print(nested)
# ((1, (3, (4,), (5,))), 2)

# Reconstruct tree from nested tuple
T_reconstructed = nx.from_nested_tuple(nested, create_using=nx.Graph)

# Error handling for non-tree graphs
try:
    G = nx.cycle_graph(4)  # Not a tree!
    nx.to_nested_tuple(G, source=0)
except nx.NotATree as e:
    print(f"Not a tree: {e}")
```

### Junction Trees (Tree Decomposition)

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Junction tree for probabilistic inference
JT = nx.junction_tree(G)
print(list(JT.nodes()))  # Cliques of the original graph
print(list(JT.edges()))  # Connections between cliques

# Junction tree has treewidth = max clique size - 1
```

## Tree Properties and Analysis

```python
T = nx.balanced_tree(3, 4)

# Check if a graph is a tree
is_tree = nx.is_tree(T)
print(is_tree)  # True

# For directed graphs, check if it's an arborescence
is_arborescence = nx.is_arborescence(DG, root=1)

# Tree diameter
diam = nx.diameter(T)

# Height (longest path from root to leaf)
height = nx.height(T, source=0)

# Number of leaves
leaves = [n for n, d in T.degree() if d == 1]
print(len(leaves))
```

## Practical Applications

### Finding Spanning Trees in Network Reliability

```python
# Find minimum cost spanning tree for network infrastructure
G = nx.Graph()
cities = ["A", "B", "C", "D", "E"]
G.add_nodes_from(cities)
G.add_edges_from([
    ("A", "B", {"cost": 10}),
    ("A", "C", {"cost": 15}),
    ("B", "C", {"cost": 5}),
    ("B", "D", {"cost": 20}),
    ("C", "D", {"cost": 8}),
    ("C", "E", {"cost": 12}),
    ("D", "E", {"cost": 7}),
])

# Minimum cost to connect all cities
mst = nx.minimum_spanning_tree(G)
total_cost = sum(d["cost"] for _, _, d in mst.edges(data=True))
print(f"Minimum total cost: {total_cost}")

# Compare different algorithms
for algo in ["prim", "kruskal", "boruvka"]:
    t = nx.minimum_spanning_tree(G, algorithm=algo)
    cost = sum(d["cost"] for _, _, d in t.edges(data=True))
    print(f"{algo}: {cost}")
```

### Tree Encoding/Decoding

```python
# Prufer sequences are useful for:
# 1. Generating random labeled trees
# 2. Counting trees (Cayley's formula: n^(n-2) trees on n nodes)
# 3. Efficient tree storage/transmission

import random

def generate_random_tree(n):
    """Generate a random labeled tree using Prufer sequence."""
    # Cayley's formula: there are n^(n-2) labeled trees
    prufer = [random.randint(1, n) for _ in range(n - 2)]
    return nx.from_prufer_sequence(prufer)

T = generate_random_tree(10)
print(f"Random tree: {T.number_of_nodes()} nodes, {T.number_of_edges()} edges")
```

### Tree Decomposition for Constraint Satisfaction

```python
# Junction trees enable exact inference in Bayesian networks
G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (2, 4), (2, 5), (3, 5), (3, 6)
])

# Create junction tree for message passing
JT = nx.junction_tree(G)

# Each node in JT is a clique from G
for clique in JT.nodes():
    print(f"Clique: {clique}")

# Edges connect overlapping cliques
for u, v in JT.edges():
    overlap = set(u).intersection(set(v))
    print(f"Edge between {u} and {v}, separator = {overlap}")
```

## Additional Traversal Functions Reference

| Function | Description |
|----------|-------------|
| `bfs_edges(G, source=None)` | BFS edge generator |
| `bfs_labeled_edges(G, source=None)` | BFS with edge type labels |
| `bfs_layers(G, sources)` | Iterator over layers |
| `bfs_successors(G, source)` | (node, children_list) pairs |
| `bfs_predecessors(G, source)` | (node, parent) pairs |
| `descendants_at_distance(G, source, distance)` | Nodes at exact distance |
| `dfs_edges(G, source=None)` | DFS edge generator |
| `dfs_labeled_edges(G, source=None)` | DFS with edge type labels |
| `dfs_preorder_nodes(G, source=None)` | Pre-order traversal |
| `dfs_postorder_nodes(G, source=None)` | Post-order traversal |
| `dfs_successors(G, source)` | (node, children_list) pairs |
| `dfs_predecessors(G, source)` | (node, parent) pairs |
| `edge_bfs(G, source=None)` | Edge-based BFS |
| `edge_dfs(G, source=None)` | Edge-based DFS |
| `bfs_beam_edges(G, source, width)` | Beam-limited BFS |

## Additional Tree Functions Reference

| Function | Description |
|----------|-------------|
| `minimum_spanning_tree(G, algorithm='kruskal')` | MST (Kruskal/Prim/Boruvka) |
| `maximum_spanning_tree(G, algorithm='kruskal')` | Maximum weight spanning tree |
| `minimum_spanning_forest(G, algorithm='kruskal')` | MST for disconnected graphs |
| `maximum_spanning_edges(G, algorithm, weight)` | Edges of max spanning tree |
| `minimum_spanning_edges(G, algorithm, weight)` | Edges of min spanning tree |
| `number_of_spanning_trees(G)` | Count spanning trees (Kirchhoff) |
| `random_spanning_tree(G, root=None, seed=None)` | Random spanning tree |
| `minimum_spanning_arborescence(DG, root, weight)` | Directed MST from root |
| `maximum_spanning_arborescence(DG, root, weight)` | Max directed spanning tree |
| `minimum_branching(DG, weight)` | Max weight branching (directed) |
| `maximum_branching(DG, weight)` | Max weight branching |
| `greedy_branching(DG, weight, reverse=False)` | Greedy branching approximation |
| `branching_weight(B, weight=None)` | Total weight of branching |
| `is_arborescence(DG, root=None)` | Check directed spanning tree |
| `is_branching(DG, reverse=False)` | Check if branching |
| `is_forest(G)` | Check if forest (no cycles) |
| `is_tree(G)` | Check if tree |
| `join_trees(T1, T2)` | Join two trees with single edge |
| `centroid(G, root=None)` | Tree centroid(s) |

## Complete Traversal/Tree Function Reference

| Category | Function | Description |
|----------|----------|-------------|
| BFS | `bfs_tree(G, source, depth_limit)` | BFS spanning tree |
| BFS | `bfs_edges(G, source)` | Edge generator (iter) |
| BFS | `bfs_labeled_edges(G, source)` | With type labels |
| BFS | `bfs_layers(G, sources)` | Layer iterator |
| BFS | `bfs_successors(G, source)` | (node, children) pairs |
| BFS | `bfs_predecessors(G, source)` | (node, parent) pairs |
| BFS | `descendants_at_distance(G, s, k)` | Nodes at distance k |
| DFS | `dfs_tree(G, source, depth_limit)` | DFS spanning tree |
| DFS | `dfs_edges(G, source)` | Edge generator (iter) |
| DFS | `dfs_labeled_edges(G, source)` | With type labels |
| DFS | `dfs_preorder_nodes(G, source)` | Pre-order traversal |
| DFS | `dfs_postorder_nodes(G, source)` | Post-order traversal |
| DFS | `dfs_successors(G, source)` | (node, children) pairs |
| DFS | `dfs_predecessors(G, source)` | (node, parent) pairs |
| Edge | `edge_bfs(G, source)` | BFS over edges |
| Edge | `edge_dfs(G, source)` | DFS over edges |
| Beam | `bfs_beam_edges(G, source, width)` | Limited frontier BFS |
| MST | `minimum_spanning_tree(G, algorithm)` | Kruskal/Prim/Boruvka |
| MST | `maximum_spanning_tree(G, algorithm)` | Max weight spanning tree |
| MST | `minimum_spanning_forest(G, algorithm)` | Forest version |
| MST | `minimum_spanning_edges(G, algorithm, weight)` | Edge iterator |
| MST | `maximum_spanning_edges(G, algorithm, weight)` | Edge iterator |
| MST | `number_of_spanning_trees(G)` | Kirchhoff count |
| MST | `random_spanning_tree(G, root, seed)` | Random spanning tree |
| Arborescence | `minimum_spanning_arborescence(DG, root)` | Directed MST |
| Arborescence | `maximum_spanning_arborescence(DG, root)` | Max directed MST |
| Branching | `minimum_branching(DG)` | Min weight branching |
| Branching | `maximum_branching(DG)` | Max weight branching |
| Branching | `greedy_branching(DG, reverse)` | Greedy approximation |
| Branching | `branching_weight(B, weight)` | Total weight |
| Recognition | `is_tree(G)` | Check tree |
| Recognition | `is_forest(G)` | Check forest |
| Recognition | `is_arborescence(DG, root)` | Check arborescence |
| Recognition | `is_branching(DG, reverse)` | Check branching |
| Encoding | `to_prufer_sequence(T, label_mapping)` | Tree → Prufer |
| Encoding | `from_prufer_sequence(seq, reverse_label_mapping)` | Prufer → Tree |
| Encoding | `to_nested_tuple(T, source)` | Tree → nested tuple |
| Encoding | `from_nested_tuple(nested, create_using)` | Nested tuple → Tree |
| Operations | `join_trees(T1, T2)` | Join two trees |
| Properties | `centroid(G, root)` | Tree centroid(s) |
| Decomposition | `junction_tree(G)` | Clique tree for inference |

## Summary

| Function | Description |
|----------|-------------|
| `nx.bfs_tree(G, source)` | BFS spanning tree |
| `nx.bfs_edges(G, source)` | BFS edge generator |
| `nx.bfs_labeled_edges()` | BFS with edge types (tree/back/forward/cross) |
| `nx.bfs_successors/predecessors()` | BFS tree structure |
| `nx.bfs_layers()` | Nodes grouped by distance from source |
| `nx.descendants_at_distance(G, n, k)` | Nodes at exactly distance k |
| `nx.dfs_tree(G, source)` | DFS spanning tree |
| `nx.dfs_edges(G, source)` | DFS edge generator |
| `nx.dfs_labeled_edges()` | DFS with edge types |
| `nx.dfs_preorder/postorder_nodes()` | Tree traversal orders |
| `nx.edge_bfs/dfs(G, source)` | Edge-based traversal |
| `nx.bfs_beam_edges(G, source, width)` | Memory-limited BFS |
| `nx.minimum_spanning_tree()` | MST (Kruskal/Prim/Boruvka) |
| `nx.maximum_spanning_tree()` | Maximum weight spanning tree |
| `nx.minimum_spanning_arborescence()` | Directed MST from root |
| `nx.minimum_branching()` | Max weight subgraph without cycles (directed) |
| `nx.to_prufer_sequence()` | Tree → Prufer encoding |
| `nx.from_prufer_sequence()` | Prufer → Tree decoding |
| `nx.to_nested_tuple()` | Tree → nested tuple |
| `nx.from_nested_tuple()` | Nested tuple → Tree |
| `nx.junction_tree()` | Clique tree for inference |
| `nx.is_tree()` | Check if graph is a tree |
| `nx.ArborescenceIterator()` | Enumerate all arborescences |
| `nx.number_of_spanning_trees()` | Count spanning trees (Kirchhoff) |
| `nx.random_spanning_tree()` | Random spanning tree |
| `nx.join_trees()` | Join two trees with single edge |
| `nx.centroid()` | Tree centroid(s) |
