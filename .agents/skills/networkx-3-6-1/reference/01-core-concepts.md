# Core Concepts and Graph Classes

Foundational NetworkX concepts: graph types, nodes/edges, attributes, views, and core API.

## Which Graph Class Should I Use?

| Need | Class |
|------|-------|
| Simple undirected | `Graph` |
| Directed relationships | `DiGraph` |
| Multiple edges between same pair | `MultiGraph` / `MultiDiGraph` |
| Self-loops allowed | All classes (default) or use `strict=True` in `nx.path_graph(..., create_using=nx.Graph())` |

```python
import networkx as nx

G = nx.Graph()          # Undirected, no parallel edges
DG = nx.DiGraph()       # Directed, no parallel edges
MG = nx.MultiGraph()    # Undirected, parallel edges allowed
MDG = nx.MultiDiGraph() # Directed, parallel edges allowed
```

## Graph Creation Methods

### From Scratch

```python
G = nx.Graph()

# Nodes
G.add_node(1)
G.add_nodes_from([2, 3, 4])
G.add_node("a", color="blue")  # with attributes

# Edges
G.add_edge(1, 2, weight=2.5)
G.add_edges_from([(2, 3), (3, 4)])

# Bulk operations
G.add_nodes_from([(i, {"index": i}) for i in range(10)])
G.add_edges_from([(i, i+1) for i in range(9)])
```

### From Data Sources

```python
import networkx as nx

# From adjacency matrix (numpy)
import numpy as np
adj = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
G = nx.from_numpy_array(adj)

# From dict of dicts
dod = {1: {2: {"weight": 1.0}}, 2: {1: {"weight": 1.0}}}
G = nx.DiGraph(dod)

# From dict of lists
dol = {1: [2, 3], 2: [1, 3]}
G = nx.Graph(dol)

# From edge list
edges = [(0, 1), (1, 2), (2, 3)]
G = nx.Graph(edges)

# From scipy sparse
import scipy.sparse as sp
sparse = sp.csr_matrix(adj)
G = nx.from_scipy_sparse_array(sparse)

# From pandas DataFrame
import pandas as pd
df = pd.DataFrame([(0, 1), (1, 2)], columns=['u', 'v'])
G = nx.from_pandas_edgelist(df, source='u', target='v')
```

### Using `create_using` Parameter

```python
# Create a DiGraph from a generator
G = nx.path_graph(5, create_using=nx.DiGraph)

# Create an empty MultiGraph
MG = nx.Graph(create_using=nx.MultiGraph)
```

## Nodes and Edges

### Node Operations

```python
G = nx.Graph()
G.add_node("Alice", age=30, role="manager")
G.add_nodes_from([("Bob", {"age": 25}), ("Carol", {"role": "dev"})])

# Query
print(G.nodes)              # NodeView with attributes
print(G.number_of_nodes())  # count
print("Alice" in G)         # True (membership test)
print(G.nodes["Alice"])     # {'age': 30, 'role': 'manager'}

# Remove
G.remove_node("Bob")
G.remove_nodes_from(["Carol"])
```

### Edge Operations

```python
G = nx.Graph()
G.add_edge(1, 2, weight=0.8, since="2020")
G.add_edges_from([(2, 3), (3, 4)])

# Query
print(G.edges)              # EdgeView with attributes
print(G.number_of_edges())  # count
print(G[1][2])              # {'weight': 0.8, 'since': '2020'}
print(G.get_edge_data(1, 2))  # same as above

# Remove
G.remove_edge(1, 2)
G.remove_edges_from([(2, 3)])
```

### Access Patterns

```python
# Adjacency dict-like access (O(1) lookup)
neighbors = G[1]           # dict of {neighbor: edge_data}
print(neighbors[2])        # {'weight': 0.8, 'since': '2020'}

# Using .edges() for iteration with data
for u, v, data in G.edges(data=True):
    print(f"{u}-{v}: weight={data.get('weight', 1)}")

# Using .nodes() for iteration with data
for n, data in G.nodes(data=True):
    print(f"{n}: {data}")

# Degree
print(G.degree(1))          # number of edges incident to node 1
print(dict(G.degree()))     # {node: degree, ...}

# Neighbors
print(list(G.neighbors(1)))  # [2]
```

## Graph Attributes

```python
G = nx.Graph()
G.graph["name"] = "my_network"
G.graph["version"] = "1.0"

print(G.graph)  # {'name': 'my_network', 'version': '1.0'}

# Node attributes (set/get)
G.add_node(1, color="red")
nx.set_node_attributes(G, {1: {"color": "blue"}}, "color")
nx.set_node_attributes(G, {"age": 30})

print(G.nodes[1])        # {'color': 'blue', 'age': 30}
print(nx.get_node_attributes(G, "age"))  # {1: 30}

# Edge attributes
G.add_edge(1, 2, weight=5.0)
nx.set_edge_attributes(G, {(1, 2): {"weight": 10.0}})
nx.set_edge_attributes(G, {"capacity": 100})

print(G.edges[1, 2])     # {'weight': 10.0, 'capacity': 100}
print(nx.get_edge_attributes(G, "weight"))  # {(1, 2): 10.0}
```

## Graph Views

Views provide **zero-copy** access to subsets of a graph:

```python
G = nx.complete_graph(5)

# Subgraph view (shares data with original)
sub = G.subgraph([0, 1, 2])
print(list(sub.edges()))  # [(0, 1), (0, 2), (1, 2)]
# Modifying sub does NOT modify G

# Filtered views
all_edges = G.edges()                    # EdgeView
no_filter = nx.empty_filter              # always True
hide_0 = nx.hide_nodes(G, [0])           # view without node 0
show_only = nx.show_nodes(G, [1, 2])     # view with only nodes 1, 2

# Graph transformation views
DG = G.to_directed()          # DiGraph view
UG = DG.to_undirected()       # back to undirected
RG = DG.reverse()             # reverse all edges
```

### CoreViews (Specialized View Types)

| Class | Description |
|-------|-------------|
| `AtlasView` | Read-only dict-like view of node/edge attributes |
| `AdjacencyView` | Read-only dict-like view of adjacency (neighbors → edge data) |
| `MultiAdjacencyView` | Same but for MultiGraph (list of edge dicts per neighbor) |
| `UnionAtlas` | Concatenated read-only view of multiple attribute dicts |
| `UnionAdjacency` | Concatenated view of multiple adjacency dicts |
| `FilterAtlas` | Filtered subset of attributes by key |
| `FilterAdjacency` | Filtered subset of neighbors by node/edge criteria |

```python
from networkx.classes import coreviews

# Access internal views
adj = G.adj           # AdjacencyView
nodes = G.nodes       # NodeView (dict-like)
edges = G.edges       # EdgeView (iterable of tuples)
degree = G.degree     # DegreeView (node → degree mapping)
```

### Filter Functions

```python
from networkx.classes.filters import hide_nodes, show_nodes, hide_edges, show_edges, no_filter

# Create filtered views
G = nx.path_graph(5)

view1 = nx.subgraph_view(G, filter_node=lambda n: n % 2 == 0)
view2 = nx.subgraph_view(G, filter_edge=lambda u, v: G[u][v].get("weight", 1) > 0.5)

# Combine filters
combined = nx.subgraph_view(
    G,
    filter_node=no_filter,
    filter_edge=hide_edges([0, 1])
)

# Unfilter (restore original)
original = view1.restore()
```

## Graph Operations

### Set Operations

```python
G1 = nx.Graph([(1, 2), (2, 3)])
G2 = nx.Graph([(2, 3), (3, 4)])

union = G1 | G2           # Union (all nodes/edges from both)
intersection = G1 & G2    # Intersection (shared nodes/edges)
difference = G1 - G2      # Nodes/edges in G1 but not G2
symmetric_diff = G1 ^ G2  # Nodes/edges in exactly one graph
```

### Graph Composition and Products

```python
G1 = nx.path_graph(3)
G2 = nx.path_graph(3)

# Composition (union with shared nodes merged)
composed = nx.compose(G1, G2)

# Disjoint union (no shared nodes)
disjoint = nx.disjoint_union(G1, G2)

# Graph products
cartesian = nx.cartesian_product(G1, G2)
tensor = nx.tensor_product(G1, G2)
strong = nx.strong_product(G1, G2)
lexicographic = nx.lexicographic_product(G1, G2)

# Complement (edges where there were none and vice versa)
comp = nx.complement(G1)

# Subgraph / induced subgraph
sub = G1.subgraph([0, 1])
induced = G1.induced_subgraph([0, 1])
```

### Relabeling Nodes

```python
G = nx.Graph([(0, 1), (1, 2)])

# Map function
H = nx.relabel_nodes(G, {0: "a", 1: "b", 2: "c"})

# Convert to integer labels
H = nx.convert_node_labels_to_integers(G, ordering="increasing")
H = nx.convert_node_labels_to_integers(G, ordering="decreasing")
H = nx.convert_node_labels_to_integers(G, ordering="increasing_degree")

# In-place relabeling
nx.relabel_nodes(G, {0: "a"}, copy=False)
```

## Graph Properties and Reporting

```python
G = nx.Graph([(1, 2), (2, 3), (3, 4)])

# Basic properties
print(G.number_of_nodes())      # 4
print(G.number_of_edges())      # 3
print(G.order())                # same as number_of_nodes
print(G.size())                 # same as number_of_edges

# Density: ratio of edges to max possible edges
print(nx.density(G))

# Degree statistics
degrees = dict(G.degree())
print(degrees)                  # {1: 1, 2: 2, 3: 2, 4: 1}
print(max(dict(G.degree()).values()))  # max degree

# Connectivity
print(nx.is_connected(G))       # True (undirected)
print(nx.is_directed(G))        # False
print(G.is_directed())          # same

# Weighted check
print(nx.is_weighted(G))
print(nx.is_negatively_weighted(G))

# Path check
print(nx.is_path(G, [1, 2, 3]))   # True
print(nx.path_weight(G, [1, 2, 3]))  # sum of edge weights

# Self-loops
G.add_edge(1, 1)
print(G.number_of_selfloops())
print(G.nodes_with_selfloops())
print(G.selfloop_edges())
```

## Frozen Graphs

Prevent modification of a graph:

```python
G = nx.Graph([(1, 2), (2, 3)])
G.freeze()

# Now raises NetworkXError on any modification attempt
G.add_node(4)  # NetworkXError: Frozen graph can't be modified
```

## Path Weight Calculation

```python
G = nx.Graph()
G.add_edge(1, 2, weight=5.0)
G.add_edge(2, 3, weight=3.0)

print(nx.path_weight(G, [1, 2, 3]))  # 8.0
print(nx.is_path(G, [1, 2, 3]))      # True
```

## Non-Edges

Find pairs of nodes that are NOT connected:

```python
G = nx.complete_graph(3)  # 0-1, 1-2, 0-2
print(list(nx.non_edges(G)))  # [] (all pairs connected in K3)

G2 = nx.Graph([(0, 1)])
print(list(nx.non_edges(G2)))  # [(0, 2), (1, 2)] if nodes include 2
```

## Key Module Paths

| Topic | Module |
|-------|--------|
| Graph classes | `networkx.classes` |
| Graph views/filters | `networkx.classes.graphviews`, `networkx.classes.filters` |
| CoreViews | `networkx.classes.coreviews` |
| Exceptions | `networkx.exception` |
| Conversion | `networkx.convert` |
| Relabeling | `networkx.relabel` |
| Randomness utils | `networkx.randomization` / `networkx.utils.randomness` |
| Configuration | `networkx.configs` |

## References

- [NetworkX Introduction](https://networkx.org/documentation/stable/reference/introduction.html)
- [Graph Classes Reference](https://networkx.org/documentation/stable/reference/classes/index.html)
- [Graph Views & Filters](https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.Graph.subgraph_view.html)
- [CoreViews Documentation](https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.coreviews.AtlasView.html)
- [Conversion Functions](https://networkx.org/documentation/stable/reference/convert.html)
- [Relabeling](https://networkx.org/documentation/stable/reference/relabel.html)
