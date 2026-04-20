# Graph Class Methods and Operations

NetworkX graphs support a rich API for creating, modifying, and combining graphs.

## Core Graph Methods

### Adding/Removing Nodes

```python
import networkx as nx

G = nx.Graph()

# Add single node
G.add_node(1)
G.add_node("A", color="red", size=10)  # with attributes
G.add_node((0, 0), label="origin")     # hashable objects work as nodes

# Add multiple nodes
G.add_nodes_from([2, 3, 4])
G.add_nodes_from([(5, {"color": "blue"}), (6, {"color": "green"})])

# Remove single node (also removes its edges)
G.remove_node(1)

# Remove multiple nodes
G.remove_nodes_from([2, 3])

# Check if node exists
has_one = 1 in G
print(has_one)  # False after removal

# Get number of nodes
n = G.number_of_nodes()

# Iterate over nodes
for node in G.nodes():
    print(node, G.nodes[node])  # node and its attributes dict

# Get node data
data = G.nodes[1, data=True]  # (node, {attr_dict})
```

### Adding/Removing Edges

```python
G = nx.Graph()

# Add single edge
G.add_edge(1, 2)
G.add_edge("A", "B", weight=0.5)  # with attributes

# Add multiple edges
G.add_edges_from([(1, 2), (2, 3), (3, 4)])
G.add_edges_from([(5, 6, {"weight": 1.0}), (6, 7, {"weight": 2.0})])

# Remove single edge
G.remove_edge(1, 2)

# Remove multiple edges
G.remove_edges_from([(3, 4), (4, 5)])

# Check if edge exists
has_edge = G.has_edge(1, 2)
has_edge2 = 1 in G[2]           # alternative check
print(has_edge)  # False after removal

# Get number of edges
n = G.number_of_edges()

# Iterate over edges
for u, v in G.edges():
    print(u, v)

for u, v, data in G.edges(data=True):
    print(u, v, data)

for u, v, w in G.edges(data="weight", default=1.0):
    print(u, v, w)
```

### Accessing Neighbors and Degree

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Get neighbors of a node
neighbors = list(G.neighbors(1))   # [2, 3]
print(neighbors)

# Check if a specific neighbor
is_neighbor = 2 in G[1]
print(is_neighbor)  # True

# Get degree (number of edges connected to node)
deg = G.degree(1)
print(deg)  # 2

for n, d in G.degree():
    print(f"{n}: {d}")

# Degree as view (iterable)
degrees = dict(G.degree())
print(degrees)  # {1: 2, 2: 3, 3: 2, 4: 1}

# Get all neighbor degrees
for n, nbrs in G.adjacency():
    print(f"{n}: {[(nbr, d.get('weight', 1)) for nbr, d in nbrs.items()]}")
```

### Subgraphs and Views

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)])

# Create subgraph view (shares data with original)
sub = G.subgraph([1, 2, 3])
print(list(sub.edges()))  # [(1, 2), (1, 3), (2, 3)]

# Create induced subgraph (includes all edges between selected nodes)
induced = G.subgraph([1, 2, 4])

# Edge-induced subgraph (only edges in list and their endpoints)
edge_sub = G.edge_subgraph([(1, 2), (2, 3)])

# Create a copy (independent graph)
G_copy = G.copy()
G_digraph = nx.DiGraph(G)  # Convert to directed

# Make frozen copy (no modifications allowed, faster)
G_frozen = nx.freeze(G)
try:
    G_frozen.add_node(99)
except nx.NetworkXError as e:
    print(e)  # Frozen graph can only be iterated over

is_frozen = nx.is_frozen(G_frozen)
print(is_frozen)  # True

# Create empty copy (same type, no edges/nodes)
G_empty = nx.create_empty_copy(G)
```

### Directed Graph Specific Methods

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Reverse direction
RDG = DG.reverse()  # Returns reversed DiGraph
print(list(RDG.edges()))  # [(2, 1), (3, 2), (3, 1)]

# In-neighbors and out-neighbors
in_neighbors = list(DG.predecessors(3))  # [1, 2]
out_neighbors = list(DG.successors(1))   # [2, 3]

# In-degree and out-degree
in_deg = DG.in_degree(3)
out_deg = DG.out_degree(1)

# For DiGraph, degree() returns total (in + out)
total_deg = DG.degree(3)
```

### Graph Conversion

```python
G = nx.Graph()
G.add_edges_from([(1, 2, {"weight": 0.5}), (2, 3, {"weight": 1.0})])

# To directed
DG = G.to_directed()
print(list(DG.edges()))  # [(1, 2), (2, 1), (2, 3), (3, 2)]

# To undirected
G2 = DG.to_undirected()

# To multigraph
MG = nx.MultiGraph(G)

# From dict of dicts
data = {1: {2: {"weight": 0.5}}, 2: {1: {"weight": 0.5}}}
G_from_dict = nx.from_dict_of_dicts(data)

# From dict of lists
data = {1: [2, 3], 2: [1, 3]}
G_from_dol = nx.from_dict_of_lists(data)

# From edgelist
edges = [(1, 2), (2, 3), (3, 4)]
G_from_edges = nx.from_edgelist(edges)

# To dict of dicts
dod = nx.to_dict_of_dicts(G)

# To dict of lists
dol = nx.to_dict_of_lists(G)

# To edgelist
edges = list(nx.to_edgelist(G))
```

## Graph Operators (Combining Graphs)

### Binary Operations

```python
import networkx as nx
from networkx.algorithms import operators

G1 = nx.Graph()
G1.add_edges_from([(1, 2), (2, 3)])

G2 = nx.Graph()
G2.add_edges_from([(2, 3), (3, 4), (4, 5)])

# Union: combine all nodes and edges
G_union = nx.disjoint_union(G1, G2)  # Relabels to avoid conflicts
print(list(G_union.edges()))

# Composition: merge common nodes/edges
G_comp = nx.compose(G1, G2)
print(list(G_comp.edges()))  # [(1, 2), (2, 3), (3, 4), (4, 5)]

# Intersection: only edges in both graphs
G_inter = nx.intersection(G1, G2)
print(list(G_inter.edges()))  # [(2, 3)]

# Difference: edges in G1 but not in G2
G_diff = nx.difference(G1, G2)
print(list(G_diff.edges()))  # [(1, 2)]

# Symmetric difference: edges in exactly one graph
G_symdiff = nx.symmetric_difference(G1, G2)
print(list(G_symdiff.edges()))  # [(1, 2), (3, 4), (4, 5)]

# Full join: union plus all edges between node sets
G_fulljoin = nx.full_join(G1, G2)
```

### Graph Products

```python
G1 = nx.complete_graph(3)  # K3
G2 = nx.path_graph(3)      # P3

# Cartesian product
G_cart = nx.cartesian_product(G1, G2)

# Tensor (direct/Kronecker) product
G_tensor = nx.tensor_product(G1, G2)

# Strong product
G_strong = nx.strong_product(G1, G2)

# Lexicographic product
G_lex = nx.lexicographic_product(G1, G2)

# Rooted product
G_root = nx.rooted_product(G1, G2, 1)  # root node 1 of G1

# Modular product
G_modular = nx.modular_product(G1, G2)

# Corona product
G_corona = nx.corona_product(G1, G2, 0)

# Power of graph
G_power = nx.power(G1, 2)  # Nodes connected if distance <= 2
```

### Unary Operations

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Complement: all edges NOT in G
G_comp = nx.complement(G)
print(list(G_comp.edges()))  # Non-edges of G

# Reverse (directed graphs only)
DG = nx.DiGraph([(1, 2), (2, 3)])
RDG = nx.reverse(DG)

# Minors
G_minors = nx.contracted_nodes(G, 1, 2)  # Merge node 1 into node 2
G_quotient = nx.quotient_graph(G, [set([1, 2]), set([3])])

# Contract specific edge
G_contracted = nx.contracted_edge(G, (1, 2), self_loop=False)

# Identify nodes (merge with attribute tracking)
G_identified = nx.identified_nodes(G, [1, 2], label="group")

# Equivalence classes of nodes
eq_classes = nx.equivalence_classes(G, lambda n: n % 2 == 0)
print(eq_classes)  # [{even_nodes}, {odd_nodes}]
```

## Batch Graph Operators

Apply binary operators to lists of graphs at once.

```python
from networkx.algorithms.operators.all import *

G1 = nx.path_graph(3)
G2 = nx.path_graph(4)
G3 = nx.path_graph(5)
graph_list = [G1, G2, G3]

# Union all graphs in a list
all_union = union_all(graph_list)
print(f"Union has {all_union.number_of_nodes()} nodes")

# Disjoint union all (auto-relabels to avoid conflicts)
disjoint = disjoint_union_all(graph_list)
print(f"Disjoint union: {disjoint.number_of_nodes()} nodes")

# Intersection of all graphs
all_inter = intersection_all(graph_list)
print(f"Common edges: {all_inter.number_of_edges()}")

# Compose all (merge common nodes/edges)
all_compose = compose_all(graph_list)
print(f"Composed: {all_compose.number_of_nodes()} nodes")
```

## Attribute Management

```python
G = nx.Graph()
G.add_node(1, color="red")
G.add_edge(1, 2, weight=0.5)

# Get node attributes
color = G.nodes[1]["color"]
weight = G.edges[1, 2].get("weight", 1.0)

# Set single attribute
G.add_node(1, size=10)
G.add_edge(1, 2, label="edge1")

# Set multiple node attributes
nx.set_node_attributes(G, {"1": "red", "2": "blue"}, "color")
G.nodes[1]["color"]  # "red"

# Set edge attributes
nx.set_edge_attributes(G, {(1, 2): 0.5, (2, 3): 1.0}, "weight")
G.edges[(1, 2)]["weight"]  # 0.5

# Get all attributes as dict
node_attrs = nx.get_node_attributes(G, "color")
edge_attrs = nx.get_edge_attributes(G, "weight")

# Remove attribute
del G.nodes[1]["color"]
G.edges[(1, 2)].pop("weight", None)

# Check if edge is negatively weighted
is_neg = nx.is_negatively_weighted(G, 1, 2, weight="weight")
```

## Non-edges and Self-loops

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (3, 4)])

# Find non-edges (pairs not connected)
non_edges = list(nx.non_edges(G))
print(non_edges)  # [(1, 3), (1, 4), (2, 3), ...]

# Find self-loops
G.add_edge(1, 1)
self_loops = list(G.selfloop_edges())
n_selfloops = G.number_of_selfloops()
nodes_with_selfloops = list(nx.nodes_with_selfloops(G))

# Common neighbors
common = list(nx.common_neighbors(G, 1, 3))
print(common)  # Nodes connected to both 1 and 3
```

## Graph Properties and Checks

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Basic properties
is_directed = nx.is_directed(G)  # False for Graph
is_empty = G.number_of_nodes() == 0
n_nodes = G.number_of_nodes()
n_edges = G.number_of_edges()
density = nx.density(G)

# Edge list from specific source
edges_from_1 = list(G.edges(1))  # Edges with 1 as first node

# All neighbors (for both directions in DiGraph)
all_neighbors = list(nx.all_neighbors(G, 1))

# Non-neighbors of a node
non_neighbors = list(nx.non_neighbors(G, 1))
```

## Frozen Graphs (Read-Only Views)

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3)])

# Create frozen graph (immutable, faster iteration)
FG = nx.freeze(G)

# Frozen graphs can only be iterated over
for node in FG.nodes():
    print(node)

# Cannot modify
try:
    FG.add_node(4)
except nx.NetworkXError:
    pass

# Check if frozen
print(nx.is_frozen(FG))  # True

# Create empty copy (same type, no data)
empty = nx.create_empty_copy(G)
```

## Graph Views and Filtering

```python
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5], category=lambda n: "A" if n <= 2 else "B")
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5)])

# Subgraph view (lightweight, shares data)
subview = nx.subgraph_view(G, filter_node=lambda n: n <= 3)
print(list(subview.nodes()))  # [1, 2, 3]

# Reverse view (for directed graphs)
DG = nx.DiGraph([(1, 2), (2, 3)])
rev = nx.reverse_view(DG)

# Restricted view (hide nodes/edges matching criteria)
rv = nx.restricted_view(G, 1, 2)  # Remove edge (1,2)
rv2 = nx.restricted_view(G, 1)     # Remove node 1 and its edges

# Edge subgraph (only specified edges and their endpoints)
es = G.edge_subgraph([(1, 2), (2, 3)])
```

## Summary of Key Methods

| Method | Description |
|--------|-------------|
| `add_node(n, **attr)` | Add single node with attributes |
| `add_nodes_from(nodes)` | Add multiple nodes |
| `remove_node(n)` | Remove node and its edges |
| `add_edge(u, v, **attr)` | Add single edge with attributes |
| `add_edges_from(edges)` | Add multiple edges |
| `remove_edge(u, v)` | Remove single edge |
| `has_node(n)` / `n in G` | Check if node exists |
| `has_edge(u, v)` / `v in G[u]` | Check if edge exists |
| `nodes()` / `G.nodes` | Node view (iterable) |
| `edges()` / `G.edges` | Edge view (iterable) |
| `neighbors(n)` / `G[n]` | Neighbor view |
| `degree(n)` | Degree of node n |
| `subgraph(nodes)` | Subgraph view |
| `copy()` | Independent copy |
| `reverse()` | Reverse directed graph |
| `to_directed()` | Convert to DiGraph |
| `to_undirected()` | Convert to Graph |
| `freeze()` | Immutable read-only copy |
| `relabel_nodes(mapping)` | Relabel nodes |
