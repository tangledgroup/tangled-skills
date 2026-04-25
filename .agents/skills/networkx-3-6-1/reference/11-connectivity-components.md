# Connectivity and Components

NetworkX provides algorithms for analyzing connected components, bridges, articulation points, and various forms of graph connectivity.

## Connected Components (Undirected)

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (4, 5)])
# Two components: {1,2,3} and {4,5}

# Get all connected components (sets of nodes)
components = list(nx.connected_components(G))
print(components)  # [{1, 2, 3}, {4, 5}]

# Number of connected components
n_components = nx.number_connected_components(G)
print(n_components)  # 2

# Check if graph is connected
is_connected = nx.is_connected(G)
print(is_connected)  # False

# Get component membership for each node
component_id = dict(nx.connected_components(G))
# Note: use a different approach:
node_to_comp = {}
for i, comp in enumerate(nx.connected_components(G)):
    for node in comp:
        node_to_comp[node] = i

# Largest connected component
largest = max(nx.connected_components(G), key=len)
G_largest = G.subgraph(largest)
```

## Strongly Connected Components (Directed)

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1), (4, 5)])
# SCCs: {1,2,3} and {4} and {5}

# Get all strongly connected components
sccs = list(nx.strongly_connected_components(DG))
print(sccs)  # [{1, 2, 3}, {4}, {5}]

# Number of SCCs
n_scc = nx.number_strongly_connected_components(DG)
print(n_scc)  # 3

# Check if strongly connected
is_strong = nx.is_strongly_connected(DG)
print(is_strong)  # False

# Weakly connected components (treat as undirected)
wccs = list(nx.weakly_connected_components(DG))
is_weak = nx.is_weakly_connected(DG)

# Condensation: contract each SCC to a single node
condensation = nx.condensation(DG)
# condensation is a DiGraph where each node represents one SCC
# Original node -> SCC mapping via condensation.node['contracted_node']
```

## Attracting Components

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 1), (2, 3), (3, 4), (4, 3)])

# Attracting components: SCCs with no outgoing edges to other SCCs
attracting = list(nx.attracting_components(DG))
print(attracting)  # [{1, 2}, {3, 4}]

# Check if a subgraph is an attracting component
is_attracting = nx.is_attracting_component(DG, {1, 2})
```

## Biconnected Components and Articulation Points

```python
G = nx.Graph()
# Create a graph with articulation points
# 1--2--3
#     |
#     4
G.add_edges_from([(1, 2), (2, 3), (2, 4)])

# Find biconnected components (maximal subgraphs without articulation points)
biconnected = list(nx.biconnected_components(G))
print(biconnected)  # [{1, 2}, {2, 3}, {2, 4}]

# Get edges of biconnected component
biconnected_edges = list(nx.biconnected_component_edges(G))
print(biconnected_edges)

# Find articulation points (cut vertices)
articulation_pts = list(nx.articulation_points(G))
print(articulation_pts)  # [2]

# Check if graph is biconnected
is_biconnected = nx.is_biconnected(G)
print(is_biconnected)  # False

# Biconnected components using DFS
for comp in nx.biconnected_components(G):
    subgraph = G.subgraph(comp)
    print(f"Component: {comp}, edges: {list(subgraph.edges())}")
```

## Edge and Node Connectivity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)])

# Global edge connectivity (min edges to disconnect)
edge_conn = nx.edge_connectivity(G)
print(edge_conn)  # 2

# Local edge connectivity between two nodes
local_edge = nx.local_edge_connectivity(G, 1, 4)
print(local_edge)  # 2

# Global node connectivity (min nodes to disconnect)
node_conn = nx.node_connectivity(G)
print(node_conn)  # 2

# Local node connectivity
local_node = nx.local_node_connectivity(G, 1, 4)
print(local_node)  # 2

# Minimum edge cut
min_cut_edges = nx.minimum_edge_cut(G, 1, 4)
print(min_cut_edges)  # e.g., {(2, 4), (3, 4)}

# Minimum node cut
min_cut_nodes = nx.minimum_node_cut(G, 1, 4)
print(min_cut_nodes)  # e.g., {2, 3}

# Edge-disjoint paths
edge_paths = list(nx.edge_disjoint_paths(G, "1", "4"))
print(edge_paths)

# Node-disjoint paths
node_paths = list(nx.node_disjoint_paths(G, "1", "4"))
print(node_paths)
```

## k-Edge Connectivity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])

# Check if k-edge-connected
is_2_edge = nx.is_k_edge_connected(G, k=2)
print(is_2_edge)  # True

# Find edge connectivity via min-cut
# Uses max-flow algorithm internally
conn = nx.edge_connectivity(G, sources=None, targets=None)

# For directed graphs
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 3)])

# Edge connectivity for directed graphs
dc = nx.edge_connectivity(DG, "1", "4")
```

## Bridges and Local Bridges

```python
G = nx.Graph()
# Bridge: edge whose removal disconnects the graph
# 1--2--3
#     |
#     4
G.add_edges_from([(1, 2), (2, 3), (2, 4)])

# Find all bridges
bridges = list(nx.bridges(G))
print(bridges)  # [(1, 2), (2, 3), (2, 4)]

# Check if specific edge is a bridge
is_bridge = nx.has_bridges(G)
bridge_list = list(nx.bridges(G))

# Local bridges (low-betweenness edges, may not disconnect but are weak)
local_bridges = list(nx.local_bridges(G, weight=None))
print(local_bridges)

# With weight penalty
weighted_local = list(nx.local_bridges(G, weight="weight", weight_penalty=2.0))
```

## Node and Edge Boundaries

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5)])

# Node boundary: nodes outside S connected to nodes in S
S = {1, 2}
node_boundary = nx.node_boundary(G, S)
print(node_boundary)  # {3, 4}

# Edge boundary: edges between S and V\S
edge_boundary = nx.edge_boundary(G, S)
print(edge_boundary)  # {(2, 4), (1, 3)}
```

## Isolated Nodes

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (3, 4)])
G.add_node(5)  # Isolated node

# Find isolated nodes
isolates = list(nx.isolates(G))
print(isolates)  # [5]

# Number of isolated nodes
n_isolates = nx.number_of_isolates(G)
print(n_isolates)  # 1

# Check if specific node is isolated
is_iso = nx.is_isolate(G, 5)
print(is_iso)  # True
```

## Semiconnected Graphs

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3)])

# A directed graph is semiconnected if for every pair (u,v),
# there's a path from u to v or from v to u
is_semiconnected = nx.is_semiconnected(DG)
print(is_semiconnected)  # True

# Another example (not semiconnected)
DG2 = nx.DiGraph()
DG2.add_edges_from([(1, 2), (3, 4)])
print(nx.is_semiconnected(DG2))  # False
```

## k-Edge Augmentation

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Check if graph is k-edge-connected
is_2_edge = nx.is_k_edge_connected(G, k=2)
print(is_2_edge)  # False (triangle is only 2-edge-connected if we count correctly)

# For directed graphs
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 1)])
is_locally = nx.is_locally_k_edge_connected(DG, k=1, s=1, t=2)

# k-edge augmentation (add minimum edges to make graph k-edge-connected)
augmented = nx.k_edge_augmentation(G, k=2)
print(f"Edges added: {list(augmented.edges())}")
```

## Stoer-Wagner Min-Cut (Undirected)

Global minimum cut algorithm for undirected graphs. O(V³ + VE) or better.

```python
G = nx.Graph()
G.add_edge(1, 2, capacity=3)
G.add_edge(2, 3, capacity=2)
G.add_edge(3, 4, capacity=5)

# Stoer-Wagner algorithm (global min-cut, no source/target needed)
cut_value, partition = nx.stoer_wagner(G)
print(f"Global min cut: {cut_value}")
# partition = (set1, set2) dividing graph into two parts
```

## All Node Cuts

Find all minimal sets of nodes whose removal disconnects the graph.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

# All node cuts between two nodes
all_cuts = nx.all_node_cuts(G, 1, 4)
for cut in all_cuts:
    print(f"Cut: {cut}")
# e.g., {{2}, {3}} — removing either 2 or 3 disconnects 1 from 4
```

## k-Components

Maximal subgraphs that are k-connected (need at least k nodes removed to disconnect).

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (6, 4)])

# Find k-edge components
edge_comps = nx.k_edge_components(G, k=2)
print(edge_comps)  # List of node sets

# k-edge subgraphs
subgraphs = nx.k_edge_subgraphs(G, k=2)

# Bridge components (1-edge components)
bridge_comps = nx.bridge_components(G)

# Find k-components (node connectivity version)
k_comps = nx.k_components(G, k=2)
print(k_comps)  # Nodes in 2-connected component
```

## Average Node Connectivity

Expected node connectivity between random pairs.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

avg_conn = nx.average_node_connectivity(G)
print(f"Average node connectivity: {avg_conn:.2f}")
# Expected value of local node connectivity over all pairs

# All-pairs node connectivity
all_pair_conn = nx.all_pairs_node_connectivity(G)
print(all_pair_conn)  # {(1, 2): 2, (1, 3): 2, ...}
```

## Additional Connectivity Functions Reference

| Function | Description |
|----------|-------------|
| `is_semiconnected(DG)` | Check if directed graph is semiconnected |
| `stoer_wagner(G)` | Global min-cut (undirected, weighted) |
| `k_edge_components(G, k)` | k-edge-connected components |
| `k_edge_subgraphs(G, k)` | All k-edge-connected subgraphs |
| `bridge_components(G)` | Components separated by bridges |
| `k_components(G, k=2)` | Nodes in k-connected component |
| `all_node_cuts(G, s, t)` | All minimal node cuts between s and t |
| `is_locally_k_edge_connected(DG, k, s, t)` | Local k-edge-connectivity check |
| `k_edge_augmentation(G, k)` | Add edges to achieve k-edge-connectivity |
| `average_node_connectivity(G)` | Expected connectivity over all pairs |
| `all_pairs_node_connectivity(G)` | Pairwise node connectivity matrix |

## Summary

| Concept | Function | Description |
|---------|----------|-------------|
| Connected components | `nx.connected_components()` | Maximal connected subgraphs (undirected) |
| Strongly connected | `nx.strongly_connected_components()` | SCCs (directed) |
| Weakly connected | `nx.weakly_connected_components()` | Components treating edges as undirected |
| Is connected | `nx.is_connected()` | Single component check (undirected) |
| Is strongly connected | `nx.is_strongly_connected()` | Single SCC check (directed) |
| Articulation points | `nx.articulation_points()` | Cut vertices |
| Biconnected components | `nx.biconnected_components()` | Maximal 2-connected subgraphs |
| Bridges | `nx.bridges()` | Critical edges |
| Edge connectivity | `nx.edge_connectivity()` | Min edges to disconnect |
| Node connectivity | `nx.node_connectivity()` | Min nodes to disconnect |
| Condensation | `nx.condensation()` | SCCs contracted to single nodes |
| Isolated nodes | `nx.isolates()` | Nodes with no edges |
| Stoer-Wagner min-cut | `nx.stoer_wagner()` | Global min-cut (undirected) |
| k-components | `nx.k_components()` | Nodes in k-connected component |
| All node cuts | `nx.all_node_cuts(G, s, t)` | All minimal node cuts between s,t |
| Average connectivity | `nx.average_node_connectivity()` | Expected pairwise connectivity |

## Practical Applications

### Finding Weak Points in Infrastructure Networks

```python
# Find critical nodes whose removal disconnects the network
G = nx.Graph()
# Simulate a road/network graph
edges = [
    (1, 2), (1, 3), (2, 4), (2, 5), (3, 5), (3, 6),
    (4, 7), (5, 7), (5, 8), (6, 8), (7, 9), (8, 9)
]
G.add_edges_from(edges)

# Find articulation points
critical_nodes = list(nx.articulation_points(G))
print(f"Critical nodes: {critical_nodes}")

# Find bridges
weak_links = list(nx.bridges(G))
print(f"Weak links (bridges): {weak_links}")

# Compute connectivity
edge_conn = nx.edge_connectivity(G)
node_conn = nx.node_connectivity(G)
print(f"Edge connectivity: {edge_conn}, Node connectivity: {node_conn}")
```

### SCC Analysis for Dependency Graphs

```python
# Detect circular dependencies in a project
DG = nx.DiGraph()
DG.add_edges_from([
    ("module_a", "module_b"),
    ("module_b", "module_c"),
    ("module_c", "module_a"),  # Circular!
    ("module_d", "module_e"),
])

# Find circular dependencies (SCCs with > 1 node)
sccs = list(nx.strongly_connected_components(DG))
circular_deps = [scc for scc in sccs if len(scc) > 1]
print(f"Circular dependencies: {circular_deps}")

# Condense to DAG
condensed = nx.condensation(DG)
# Now condensed is a DAG of dependency groups
```

## Summary

| Concept | Function | Description |
|---------|----------|-------------|
| Connected components | `nx.connected_components()` | Maximal connected subgraphs (undirected) |
| Strongly connected | `nx.strongly_connected_components()` | SCCs (directed) |
| Weakly connected | `nx.weakly_connected_components()` | Components treating edges as undirected |
| Is connected | `nx.is_connected()` | Single component check (undirected) |
| Is strongly connected | `nx.is_strongly_connected()` | Single SCC check (directed) |
| Articulation points | `nx.articulation_points()` | Cut vertices |
| Biconnected components | `nx.biconnected_components()` | Maximal 2-connected subgraphs |
| Bridges | `nx.bridges()` | Critical edges |
| Edge connectivity | `nx.edge_connectivity()` | Min edges to disconnect |
| Node connectivity | `nx.node_connectivity()` | Min nodes to disconnect |
| Condensation | `nx.condensation()` | SCCs contracted to single nodes |
| Isolated nodes | `nx.isolates()` | Nodes with no edges |
