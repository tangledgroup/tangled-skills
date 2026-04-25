# Clustering, Core Decomposition, and Cycles

NetworkX provides algorithms for measuring local clustering, decomposing graphs into k-cores/k-trusses, and finding cycles.

## Graph Clustering

### Local Clustering Coefficient

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Local clustering coefficient for a node
# Measures the fraction of pairs of neighbors that are connected
local_cc = nx.clustering(G, 1)
print(local_cc)  # 1.0 (neighbors 2 and 3 are connected)

# Clustering coefficient for all nodes
all_cc = nx.clustering(G)
print(all_cc)  # {1: 1.0, 2: 0.333, ...}

# For directed graphs, there are three variants
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (1, 3)])
directed_cc = nx.clustering(DG)

# Weighted clustering (edge weights as similarity)
weighted_cc = nx.clustering(G, weight="weight")

# Triangles incident to each node
triangles = nx.triangles(G, 1)
print(triangles)  # Number of triangles containing node 1
```

### Average Clustering and Transitivity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Average clustering coefficient
avg_cc = nx.average_clustering(G)
print(avg_cc)

# Transitivity (clustering coefficient of the whole graph)
transitivity = nx.transitivity(G)
print(transitivity)
# Transitivity = 3 × triangles / connections
# Measures "how close to being a clique" the graph is

# All triangles in the graph
all_triangles = nx.triangles(G)  # Total number of triangles
print(all_triangles)

# Squared clustering (for degree-correlated networks)
sq_clustering = nx.square_clustering(G)
print(sq_clustering)  # {node: squared_clustering_coefficient}

# Generalized degree distribution
gen_degree = nx.generalized_degree(G)
print(gen_degree)  # {degree: count_of_nodes_with_that_degree}
```

### k-Clique and Clique Percolation

```python
G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4),  # K4: {1,2,3,4}
    (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)   # K4: {4,5,6,7}
])

# Find all maximal cliques
cliques = list(nx.find_cliques(G))
print(cliques)  # [{1, 2, 3, 4}, {4, 5, 6, 7}]

# Recursive variant (returns iterator, useful for iterative processing)
cliques_iter = nx.find_cliques_recursive(G)
for clique in cliques_iter:
    print(f"Clique: {clique}")

# Find all cliques of any size
all_cliques = list(nx.enumerate_all_cliques(G))

# Find all cliques of any size
all_cliques = list(nx.enumerate_all_cliques(G))

# Maximum weight clique (weighted graph)
G.add_edge(1, 2, weight=10)
max_w_clique = nx.max_weight_clique(G, weight="weight")
print(max_w_clique)

# Number of cliques of each size
n_cliques = nx.number_of_cliques(G)
print(n_cliques)  # {3: 1, 4: 2, ...}

# Number of k-cliques for specific k
k3_cliques = n_cliques.get(3, 0)
k4_cliques = n_cliques.get(4, 0)

# Clique number (size of largest clique)
clique_num = max(nx.find_cliques(G), key=len)
print(len(clique_num))

# Node clique number (largest clique containing each node)
node_cq = nx.node_clique_number(G)
print(node_cq)  # {1: 4, 2: 4, 3: 4, 4: 4, ...}

# Convert between clique graph and original
clique_graph = nx.make_max_clique_graph(G)
bipartite = nx.make_clique_bipartite(G)
```

## Core Decomposition

### k-Core, k-Shell, k-Crust, k-Truss

```python
G = nx.Graph()
# Create a graph with clear core structure
G.add_edges_from([
    (1, 2), (1, 3), (1, 4), (1, 5),  # Hub node 1
    (2, 3), (2, 4), (2, 5),           # Dense core
    (3, 4), (3, 5),
    (4, 5),
    (6, 7), (6, 8), (7, 8),          # Smaller dense group
    (1, 6),                           # Bridge
])

# Core number of each node
core_number = nx.core_number(G)
print(core_number)  # {1: 4, 2: 3, 3: 3, ...}

# k-core subgraph (maximal subgraph with min degree k)
k2_core = nx.k_core(G, k=2)
k3_core = nx.k_core(G, k=3)
print(f"Nodes in 3-core: {list(k3_core.nodes())}")

# k-shell (nodes with core number exactly k)
k1_shell = nx.k_shell(G, k=1)
k2_shell = nx.k_shell(G, k=2)

# k-crust (subgraph of nodes with core number <= k)
k1_crust = nx.k_crust(G, k=1)

# k-corona (nodes whose neighbors are all within the corona)
k1_corona = nx.k_corona(G, k=1)

# K-truss (each edge in at least k-2 triangles)
k2_truss = nx.k_truss(G, k=2)
k3_truss = nx.k_truss(G, k=3)

# Onion layers (iterative peeling order)
layers = list(nx.onion_layers(G))
print(layers)  # [[outer_nodes], [inner_nodes], ...]
```

### Core Decomposition Analysis

```python
# Plot core number distribution
core_numbers = dict(nx.core_number(G))
max_core = max(core_numbers.values())

for k in range(max_core + 1):
    core_subgraph = nx.k_core(G, k=k)
    print(f"k={k}: {len(core_subgraph.nodes())} nodes, {len(core_subgraph.edges())} edges")

# Identify core-periphery structure
core_nodes = [n for n, c in core_numbers.items() if c >= max_core * 0.7]
periphery_nodes = [n for n, c in core_numbers.items() if c < max_core * 0.3]
print(f"Core nodes: {core_nodes}")
print(f"Periphery nodes: {periphery_nodes}")
```

## Cycle Detection

### Finding Cycles

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])

# Find a cycle in the graph
cycle = nx.find_cycle(G)
print(cycle)  # [(1, 2), (2, 3), (3, 1)]

# Cycle basis (fundamental set of cycles)
basis = nx.cycle_basis(G)
print(basis)  # [[1, 2, 3]]

# All chordless cycles (induced cycles, no chords)
chordless = list(nx.chordless_cycles(G))
print(chordless)

# Girth (length of shortest cycle)
girth = nx.girth(G)
print(girth)  # 3

# Minimum cycle basis (cycles with minimum total weight)
G.add_edge(1, 2, weight=1)
G.add_edge(2, 3, weight=1)
G.add_edge(1, 3, weight=10)
min_basis = nx.minimum_cycle_basis(G, weight="weight")
print(min_basis)

# For directed graphs: find simple cycles
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 3)])

# Simple cycles in directed graph
simple_cycles = list(nx.simple_cycles(DG))
print(simple_cycles)  # [[1, 2, 3], [3, 4]]

# Recursive simple cycles
recursive = list(nx.recursive_simple_cycles(DG))
```

### Directed Graph Cycles

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Find cycle (directed)
cycle = nx.find_cycle(DG)
print(cycle)  # [(1, 2), (2, 3), (3, 1)]

# Simple cycles in directed graph
for cycle in nx.simple_cycles(DG):
    print(f"Cycle: {cycle}")

# Chordless cycles
chordless = list(nx.chordless_cycles(DG))
```

## Eulerian Paths and Circuits

```python
G = nx.Graph()
# Eulerian circuit exists iff all vertices have even degree
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 3)])

# Check if Eulerian
is_eulerian = nx.is_eulerian(G)
print(is_eulerian)  # True if all nodes have even degree

# Check if semi-Eulerian (has Eulerian path but not circuit)
is_semieulerian = nx.is_semieulerian(G)
print(is_semieulerian)

# Find Eulerian circuit
if is_eulerian:
    eulerian_circuit = list(nx.eulerian_circuit(G))
    print(eulerian_circuit)

# Find Eulerian path
has_path = nx.has_eulerian_path(G)
if has_path:
    eulerian_path = list(nx.eulerian_path(G))
    print(eulerian_path)

# Make graph Eulerian by adding minimum edges
G_eulerian = nx.eulerize(G)
```

## Cycle and Path Metrics

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])

# Number of walks of length k
walks_2 = nx.number_of_walks(G, 2)
print(walks_2)

# Walk-based measures
for node in G.nodes():
    for k in range(1, 5):
        n_walks = nx.number_of_walks(G, k, source=node)
        print(f"Walks of length {k} from {node}: {n_walks}")
```

## Practical Applications

### Community Detection via Clique Percolation

```python
# Use k-clique percolation for overlapping community detection
G = nx.Graph()
# Create two overlapping cliques
G.add_edges_from([
    (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4),  # Clique {1,2,3,4}
    (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)   # Clique {4,5,6,7}
])

# Find maximal cliques
cliques = list(nx.find_cliques(G))
print(f"Maximal cliques: {cliques}")

# k-clique percolation communities (overlapping communities)
from networkx.algorithms.community import greedy_communities
communities = list(greedy_communities(G, similarity="cn_soundarajan_hopcroft"))
print(f"Communities: {communities}")
```

### Core-Periphery Analysis

```python
# Identify core-periphery structure in social networks
G = nx.karate_club_graph()

# Get core numbers
core_numbers = nx.core_number(G)
max_core = max(core_numbers.values())

# Define thresholds
core_threshold = max_core * 0.7
periphery_threshold = max_core * 0.3

core_members = {n for n, c in core_numbers.items() if c >= core_threshold}
periphery_members = {n for n, c in core_numbers.items() if c <= periphery_threshold}
middle = set(G.nodes()) - core_members - periphery_members

print(f"Core: {len(core_members)}, Middle: {len(middle)}, Periphery: {len(periphery_members)}")

# Analyze density of each group
core_subgraph = G.subgraph(core_members)
periphery_subgraph = G.subgraph(periphery_members)
print(f"Core density: {nx.density(core_subgraph):.3f}")
print(f"Periphery density: {nx.density(periphery_subgraph):.3f}")
```

### Cycle Analysis in Dependency Graphs

```python
# Detect circular dependencies
DG = nx.DiGraph()
DG.add_edges_from([
    ("A", "B"), ("B", "C"), ("C", "A"),  # Circular: A->B->C->A
    ("D", "E"), ("E", "F"), ("F", "D"),  # Another cycle
])

# Find all simple cycles
cycles = list(nx.simple_cycles(DG))
print(f"Found {len(cycles)} cycles:")
for cycle in cycles:
    print(f"  {' -> '.join(cycle)}")

# Find chordless cycles (minimal feedback vertex sets)
chordless = list(nx.chordless_cycles(DG))
print(f"Chordless cycles: {chordless}")
```

## Additional Clustering Functions

```python
# All triangles in graph (total count)
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
all_tri = nx.all_triangles(G)  # Total number of triangles

# Squared clustering (for degree-correlated networks)
sq_clustering = nx.square_clustering(G)

# Generalized degree (degree → count mapping)
gen_degree = nx.generalized_degree(G)

# Edge cover
is_cover = nx.is_edge_cover(G, {(1, 2), (2, 3)})
min_cover = nx.min_edge_cover(G)
```

## Additional Cycle Functions Reference

| Function | Description |
|----------|-------------|
| `all_triangles(G)` | Total number of triangles in graph |
| `square_clustering(G)` | Squared clustering coefficient |
| `generalized_degree(G)` | Degree → count mapping |
| `chordless_cycles(G)` | All induced (chordless) cycles |
| `minimum_cycle_basis(G, weight=None)` | Weighted minimum cycle basis |
| `recursive_simple_cycles(DG)` | Recursive simple cycles (directed) |

## Complete Clustering/Core/Cycle Function Reference

| Category | Function | Description |
|----------|----------|-------------|
| Clustering | `clustering(G, n=None, weight=None)` | Local or per-node clustering coefficient |
| Clustering | `average_clustering(G, weight=None)` | Mean of local coefficients |
| Clustering | `transitivity(G)` | 3×triangles/connections (global) |
| Clustering | `triangles(G, n=None)` | Triangle count at node or total |
| Clustering | `all_triangles(G)` | Total triangle count |
| Clustering | `square_clustering(G)` | Squared clustering per node |
| Clustering | `generalized_degree(G)` | Degree distribution mapping |
| Core | `core_number(G)` | Max k-core containing each node |
| Core | `k_core(G, k=None)` | Subgraph with min degree ≥ k |
| Core | `k_shell(G, k=None)` | Nodes with core number = k |
| Core | `k_crust(G, k=None)` | Nodes with core number ≤ k |
| Core | `k_corona(G, k=None)` | k-corona subgraph |
| Core | `k_truss(G, k=None)` | Edges in ≥ k-2 triangles |
| Core | `onion_layers(G)` | Iterative peeling order |
| Cycles | `cycle_basis(G, root=None)` | Fundamental cycle basis |
| Cycles | `find_cycle(G, source=None, orientation=None)` | Single cycle found |
| Cycles | `chordless_cycles(G)` | Induced (chordless) cycles |
| Cycles | `girth(G)` | Shortest cycle length |
| Cycles | `minimum_cycle_basis(G, weight=None)` | Min-weight cycle basis |
| Cycles | `simple_cycles(DG)` | All directed simple cycles |
| Cycles | `recursive_simple_cycles(DG)` | Recursive variant |
| Eulerian | `is_eulerian(G)` | All even degrees? |
| Eulerian | `is_semieulerian(G)` | Exactly 0 or 2 odd-degree nodes? |
| Eulerian | `has_eulerian_path(G, s=None)` | Exists Eulerian path? |
| Eulerian | `eulerian_circuit(G, source=None)` | Eulerian circuit edges |
| Eulerian | `eulerian_path(G, source=None)` | Eulerian path edges |
| Eulerian | `eulerize(G)` | Add edges to make Eulerian |

## Summary

| Algorithm | Function | Description |
|-----------|----------|-------------|
| Local clustering | `nx.clustering(G, n)` | Fraction of connected neighbor pairs |
| Average clustering | `nx.average_clustering(G)` | Mean clustering coefficient |
| Transitivity | `nx.transitivity(G)` | Global clustering (3×triangles/connections) |
| Triangles | `nx.triangles(G, n)` | Number of triangles at node n |
| Maximal cliques | `nx.find_cliques(G)` | All maximal complete subgraphs |
| Max weight clique | `nx.max_weight_clique(G)` | Heaviest clique by weight |
| k-core | `nx.k_core(G, k)` | Subgraph with min degree k |
| k-shell | `nx.k_shell(G, k)` | Nodes with core number exactly k |
| k-truss | `nx.k_truss(G, k)` | Subgraph where each edge in ≥k-2 triangles |
| Core number | `nx.core_number(G)` | Max k such that node is in k-core |
| Cycle basis | `nx.cycle_basis(G)` | Fundamental cycle set |
| Find cycle | `nx.find_cycle(G)` | Single cycle (directed/undirected) |
| Simple cycles (directed) | `nx.simple_cycles(DG)` | All directed simple cycles |
| Girth | `nx.girth(G)` | Length of shortest cycle |
| Eulerian circuit | `nx.eulerian_circuit(G)` | Eulerian tour through all edges |
| Eulerian path | `nx.eulerian_path(G)` | Eulerian walk (not necessarily closed) |
