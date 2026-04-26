# Graph Classes and Views

## Basic Graph Types

NetworkX provides four core graph classes. All accept any hashable Python object as nodes and any Python object as edge attributes.

### Graph — Undirected, Simple

```python
G = nx.Graph()
G.add_edge(1, 2)
# G.edges contains (1, 2) only — undirected means no duplicate (2, 1)
```

Allows self-loops. Does not allow parallel edges (multiple edges between same pair).

### DiGraph — Directed, Simple

```python
DG = nx.DiGraph()
DG.add_edge(1, 2)
# Only (1, 2) exists, not (2, 1)
list(DG.successors(1))   # [2]
list(DG.predecessors(1)) # [] unless someone points to 1
```

Provides directed-specific methods: `out_edges`, `in_degree`, `predecessors()`, `successors()`. The `degree()` method reports the sum of in-degree and out-degree.

### MultiGraph — Undirected, Parallel Edges

```python
MG = nx.MultiGraph()
MG.add_edge(1, 2, weight=0.5)
MG.add_edge(1, 2, weight=0.75)
# Two edges between nodes 1 and 2, each with different attributes
```

Allows multiple edges between the same node pair, distinguished by a key. Edge access uses `MG[u][v][key]`.

### MultiDiGraph — Directed, Parallel Edges

```python
MDG = nx.MultiDiGraph()
MDG.add_edge(1, 2, weight=0.5)
MDG.add_edge(1, 2, weight=0.75)
```

Combines direction with parallel edges.

## Graph Views

Views provide read-only access to modified graph structure without copying data. Useful for algorithms that need temporary morphing.

### Subgraph View

```python
# Node-induced subgraph — O(1) creation, no copy
view = nx.subgraph_view(G, filter_node=lambda n: n % 2 == 0)
# Or using the graph method
view = G.subgraph([1, 2, 3])  # returns a SubGraph view
```

### Reverse View (DiGraph only)

```python
reversed_G = nx.reverse_view(DG)
# All edge directions flipped, original unchanged
```

### Generic Graph View

```python
# Cast to another graph type without copying
undirected_view = nx.generic_graph_view(DG, create_using=nx.Graph)
```

### Filter Functions

Filters control which nodes and edges appear in a view:

```python
from networkx.classes.filters import hide_nodes, show_nodes, hide_edges

# Hide specific nodes
hidden_view = nx.subgraph_view(G, filter_node=hide_nodes({1, 2}))

# Show only specific nodes
shown_view = nx.subgraph_view(G, filter_node=show_nodes({3, 4, 5}))

# Hide specific edges
edge_hidden = nx.subgraph_view(G, filter_edge=hide_edges([(1, 2)]))
```

Available filters: `no_filter`, `hide_nodes`, `show_nodes`, `hide_edges`, `show_edges`, `hide_diedges`, `show_diedges`, `hide_multiedges`, `show_multiedges`, `hide_multidiedges`, `show_multidiedges`.

### View Chain Warning

Views-of-views-of-views become slow after about 15 nesting levels. For common subgraph chains, NetworkX short-circuits by returning a subgraph of the original directly. When in doubt, use `.copy()` to materialize.

## Core Views

Core views provide read-only access to internal data structures:

- **AtlasView** — Read-only Mapping of Mappings (node attribute dict)
- **AdjacencyView** — Read-only Map of Maps of Maps (adjacency for Graph/DiGraph)
- **MultiAdjacencyView** — Read-only Map of Maps of Maps of Maps (adjacency for Multi*)

## Graph Properties and Reporting

Four primary views provide read-only access to graph structure:

- `G.nodes` — NodeView, set-like and dict-like
- `G.edges` — EdgeDataView, set-like and dict-like
- `G.adj` — AdjacencyView (neighbors)
- `G.degree` — DegreeView

```python
list(G.nodes)              # all nodes
list(G.nodes.data("color")) # nodes with color attribute
list(G.edges)              # all edges
list(G.edges.data())       # edges with attributes
G.adj[1]                   # neighbors of node 1
G.degree[1]                # degree of node 1

# nbunch — filter to subset of nodes
G.edges([2, "m"])          # edges incident to nodes 2 and "m"
G.degree([2, 3])           # degrees of nodes 2 and 3
```

Access patterns: use attribute form `G.nodes[node]` for setting/modifying data, callable form `G.nodes()` for iteration.

## Graph Operations

### Subgraph

```python
H = G.subgraph([1, 2, 3])       # induced subgraph on nodes [1, 2, 3]
H = nx.induced_subgraph(G, nbunch)  # returns a SubGraph view
H = nx.edge_subgraph(G, edges)      # subgraph induced by specified edges
```

### Union and Composition

```python
U = nx.union(G1, G2, rename=("G1_", "G2_"))   # disjoint union with renamed nodes
DU = nx.disjoint_union(G1, G2)                 # disjoint union, auto-renamed
C = nx.compose(G1, G2)                         # combine overlapping nodes/edges
```

### Product Graphs

```python
P = nx.cartesian_product(G, H)  # Cartesian product of G and H
```

### Complement

```python
C = nx.complement(G)  # all edges NOT in G (among same nodes)
```

### Conversion Between Types

```python
undirected = nx.to_undirected(DG)   # drop direction
directed = nx.to_directed(G)        # add bidirectional edges
empty = nx.create_empty_copy(G)     # same nodes, no edges
```

## Freezing Graph Structure

Prevent further modification to a graph:

```python
nx.freeze(G)
nx.is_frozen(G)  # True
# G.add_edge(1, 2) now raises NetworkXError
```
