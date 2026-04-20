# Specialized Graph Algorithms (Part A: Domination, Chordal, Bayesian, Planar)

NetworkX provides algorithms for domination problems, chordal graphs, Bayesian networks, and planarity.

## Dominating Sets

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5), (4, 5)])

# Find a dominating set
ds = nx.dominating_set(G)
print(ds)  # e.g., {1, 5}
# Every node is either in the set or adjacent to one

# Check if a set is dominating
is_dom = nx.is_dominating_set(G, {1, 5})
print(is_dom)  # True

# A dominating set covers all nodes
for node in G.nodes():
    assert node in ds or any(node in G[nbr] for nbr in ds)
```

## Dominance Frontiers (Compiler/Control Flow)

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

# Dominance frontiers (for SSA form in compilers)
frontiers = nx.dominance_frontiers(DG)
print(frontiers)
# Dict mapping each node to its dominance frontier set

# Immediate dominators
idoms = nx.immediate_dominators(DG, entry=1)
print(idoms)
# Dict mapping each node to its immediate dominator (parent in dominator tree)
```

## Edge Covers

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Check if a set of edges covers all vertices
edge_set = {(1, 2), (3, 4)}
is_cover = nx.is_edge_cover(G, edge_set)
print(is_cover)  # True (every node incident to at least one edge)

# Find minimum edge cover
min_cover = nx.min_edge_cover(G)
print(min_cover)  # e.g., {(1, 2), (3, 4)}
```

## Maximal Independent Set

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5)])

# Find a maximal independent set (greedy)
mis = nx.maximal_independent_set(G)
print(mis)  # e.g., {1, 4, 5}
# No two nodes are adjacent, and no more can be added

# For bipartite graphs (more efficient)
BG = nx.complete_bipartite_graph(3, 3)
bipartite_mis = nx.bipartite.independent_set(BG)
```

## Chordal Graphs

A chordal graph has no induced cycle of length > 3 (every cycle of 4+ nodes has a chord).

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])  # Cycle without chord

# Check if chordal
is_chordal = nx.is_chordal(G)
print(is_chordal)  # False (C4 has no chord)

# G with chord
G.add_edge(1, 3)
is_chordal = nx.is_chordal(G)
print(is_chordal)  # True

# Find chordal graph cliques (maximal cliques in chordal graphs have special structure)
cliques = nx.chordal_graph_cliques(G)
print(cliques)  # {{1, 2, 3}, {1, 3, 4}}

# Treewidth of chordal graph
tw = nx.chordal_graph_treewidth(G)
print(tw)

# Complete a graph to chordal (add minimum edges)
G_chordal = nx.complete_to_chordal_graph(G.copy())
assert nx.is_chordal(G_chordal)

# Find induced nodes (nodes whose neighborhood forms a clique)
induced = nx.find_induced_nodes(G, [1, 2, 3])
```

## D-Separation (Bayesian Networks)

D-separation determines conditional independence in Bayesian networks.

```python
import networkx as nx

# Create a Bayesian network (DAG)
# X1 -> X2 -> X3
#   \         /
#    -> X4 <-/
DG = nx.DiGraph()
DG.add_edges_from([("X1", "X2"), ("X2", "X3"), ("X1", "X4"), ("X4", "X3")])

# Check if X3 is d-separated from X2 given X1
is_dsep = nx.is_d_separator(DG, {"X1"}, {"X2"}, {"X3"})
print(is_dsep)  # True (X1 blocks the path X2 <- X1 -> X4 -> X3)

# Check if a set is a minimal d-separator
is_minimal = nx.is_minimal_d_separator(DG, {"X1"}, {"X2"}, {"X3"})

# Find a minimal d-separator
min_sep = nx.find_minimal_d_separator(DG, {"X2"}, {"X3"})
print(min_sep)  # e.g., {'X1', 'X4'}
```

**D-separation rules:**
- **Sequential**: A → B → C is blocked by conditioning on B
- **Diverging**: A ← B → C is blocked by conditioning on B
- **Converging**: A → B ← C is NOT blocked by conditioning on B (creates dependence)

## Moral Graph

Converts a Bayesian network to an undirected graph for inference.

```python
DG = nx.DiGraph()
DG.add_edges_from([("X1", "X2"), ("X1", "X3"), ("X2", "X4"), ("X3", "X4")])

# Moral graph: connect all parents of same child, then undirect edges
moral = nx.moral_graph(DG)
print(list(moral.edges()))
# Adds edge (X2, X3) since both are parents of X4
```

## Flow Hierarchy

Measures hierarchical structure in directed networks.

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5)])

# Flow hierarchy index
h = nx.flow_hierarchy(DG)
print(h)
# Measures how hierarchical the flow is (0 = no hierarchy, 1 = perfect hierarchy)
```

## KL-Connected Subgraphs

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Check if graph is k-Laplacian-connected
is_kl = nx.is_kl_connected(G, k=2)

# Find maximum KL-connected subgraph
kl_sub = nx.kl_connected_subgraph(G, k=2)
```

## Threshold Graphs

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (1, 4)])  # Star graph is threshold

# Check if threshold graph
is_threshold = nx.is_threshold_graph(G)
print(is_threshold)  # True

# Find threshold graph from degree sequence
threshold = nx.find_threshold_graph([3, 1, 1, 1])
```

## Bipartite Networks (Comprehensive)

### Basic Operations

```python
from networkx.algorithms import bipartite

BG = nx.Graph()
BG.add_nodes_from(["A", "B", "C"], bipartite=0)
BG.add_nodes_from(["X", "Y"], bipartite=1)
BG.add_edges_from([("A", "X"), ("A", "Y"), ("B", "X"), ("C", "Y")])

# Check if bipartite
is_bip = nx.is_bipartite(BG)

# Get the two partitions
set1, set2 = nx.bipartite.sets(BG)
print(set1)  # {A, B, C}
print(set2)  # {X, Y}

# Color nodes by partition
colors = nx.bipartite.color(BG)

# Degrees in bipartite graph
degrees = nx.bipartite.degrees(BG, weight=None)

# Density
density = nx.bipartite.density(BG)

# Check if node set is a valid partition
is_valid = nx.bipartite.is_bipartite_node_set(BG, {"A", "B", "C"})
```

### Bipartite Generators

```python
# Complete bipartite graph K_{m,n}
K = nx.bipartite.complete_bipartite_graph(3, 4)

# Havel-Hakimi bipartite graph from degree sequences
H = nx.bipartite.havel_hakimi_graph([3, 2, 2], [3, 2])

# Alternating Havel-Hakimi
H_alt = nx.bipartite.alternating_havel_hakimi_graph([3, 2, 2], [3, 2])

# Reverse Havel-Hakimi
H_rev = nx.bipartite.reverse_havel_hakimi_graph([3, 2, 2], [3, 2])

# Configuration model for bipartite
CM = nx.bipartite.configuration_model([3, 2, 2], [3, 2])

# GNMK random bipartite graph
G_nmk = nx.bipartite.gnmk_random_graph(5, 4, 8)

# Preferential attachment for bipartite
PA = nx.bipartite.preferential_attachment_graph([3, 2, 2], 0.5)

# Random bipartite graph
R = nx.bipartite.random_graph(rng=None, seed=None)
```

### Bipartite Projections

```python
# Project to one-mode graph (co-occurrence)
proj1 = nx.bipartite.projected_graph(BG, {"A", "B", "C"})
print(list(proj1.edges()))  # Pairs of U-nodes sharing V-neighbors

# Weighted projection
wp = nx.bipartite.weighted_projected_graph(BG, {"A", "B", "C"})

# Overlap weighted projection
owp = nx.bipartite.overlap_weighted_projected_graph(BG, {"A", "B", "C"})

# Collaboration weighted projection
cwp = nx.bipartite.collaboration_weighted_projected_graph(BG, {"A", "B", "C"})

# Generic weighted projection
gwp = nx.bipartite.generic_weighted_projected_graph(BG, {"A", "B", "C"}, weight_func)
```

### Bipartite Matching

```python
# Maximum matching
matching = nx.bipartite.maximum_matching(BG, top_nodes={"A", "B", "C"})
# Returns dict with both directions

# Hopcroft-Karp algorithm (fastest for bipartite)
hk = nx.bipartite.hopcroft_karp_matching(BG, top_nodes={"A", "B", "C"})

# Eppstein's matching
ep = nx.bipartite.eppstein_matching(BG, top_nodes={"A", "B", "C"})

# Minimum weight full matching
mwm = nx.bipartite.minimum_weight_full_matching(BG, top_nodes={"A", "B", "C"}, weight="weight")

# Convert matching to vertex cover
vc = nx.bipartite.vertex_cover(BG, top_nodes={"A", "B", "C"})

# Maximum independent set
mis = nx.bipartite.independent_set(BG, top_nodes={"A", "B", "C"})

# Minimum edge cover
mec = nx.bipartite.min_edge_cover(BG)
```

### Bipartite Matrix Operations

```python
# Biadjacency matrix (rows = one set, cols = other set)
bimatrix = nx.bipartite.biadjacency_matrix(BG, row_order=["A", "B", "C"], column_order=["X", "Y"])

# From biadjacency matrix
BG2 = nx.bipartite.from_biadjacency_matrix(bimatrix)
```

### Bipartite Centrality

```python
# Betweenness centrality (bipartite-specific)
bcb = nx.bipartite.betweenness_centrality(BG, weight=None, normalized=True)

# Closeness centrality (bipartite-specific)
bcc = nx.bipartite.closeness_centrality(BG)

# Degree centrality (bipartite-specific)
bdc = nx.bipartite.degree_centrality(BG)
```

### Bipartite Clustering

```python
# Local clustering coefficient
lcc = nx.bipartite.clustering(BG)

# Average clustering
avg_cc = nx.bipartite.average_clustering(BG)

# Latapy's clustering (optimized for bipartite)
lcc_latapy = nx.bipartite.latapy_clustering(BG)

# Robins-Alexander clustering
rac = nx.bipartite.robins_alexander_clustering(BG)
```

### Bipartite Other Measures

```python
# Redundancy (fraction of neighbors that are connected)
redund = nx.bipartite.node_redundancy(BG, "A")

# Spectral bipartivity (how bipartite the graph is, 0-1)
sb = nx.bipartite.spectral_bipartivity(BG)

# Extendability (can node be added?)
ext = nx.bipartite.extendability.maximal_extendability(BG, "new_node", {"A", "B", "C"})

# Birank (bipartite ranking)
br = nx.bipartite.link_analysis.birank(BG, target_nodes={"X"}, damping=0.85)

# Edge list operations (import/export for bipartite)
lines = nx.bipartite.edgelist.generate_edgelist(BG)
nx.bipartite.edgelist.write_edgelist(BG, "bipartite.edgelist")
BG_read = nx.bipartite.edgelist.read_edgelist("bipartite.edgelist")
```

### Assortativity Measures

```python
# Degree assortativity coefficient (-1 to 1)
degree_assort = nx.degree_assortativity_coefficient(G)

# Attribute assortativity
attr_assort = nx.attribute_assortativity_coefficient(G, "color")

# Numeric assortativity (for continuous node attributes)
num_assort = nx.numeric_assortativity_coefficient(G, attribute="weight")

# Degree mixing matrix (degree distribution of neighbors)
deg_mix = nx.degree_mixing_matrix(G)

# Attribute mixing matrix
attr_mix = nx.attribute_mixing_matrix(G, "color")

# Mixing dict (aggregated mixing)
mix_dict = nx.mixing_dict(G, method="default")

# Average degree connectivity
avg_deg_conn = nx.average_degree_connectivity(G)

# Average neighbor degree by degree
avg_neighbor = nx.average_neighbor_degree(G)

# Node attribute/degree cross-measures
node_attr = nx.node_attribute_xy(G, "color")
node_deg = nx.node_degree_xy(G)
```

## Summary (Part A)

| Function | Description |
|----------|-------------|
| `nx.dominating_set(G)` | Greedy dominating set |
| `nx.is_dominating_set()` | Check if set dominates all nodes |
| `nx.dominance_frontiers(DG)` | Dominance frontiers for SSA |
| `nx.immediate_dominators()` | Immediate dominator tree |
| `nx.min_edge_cover(G)` | Minimum edge cover |
| `nx.is_edge_cover()` | Check edge cover validity |
| `nx.maximal_independent_set()` | Greedy maximal independent set |
| `nx.is_chordal(G)` | Test chordality |
| `nx.chordal_graph_cliques()` | Clique decomposition of chordal graph |
| `nx.chordal_graph_treewidth()` | Treewidth via chordal completion |
| `nx.complete_to_chordal_graph()` | Add edges to make chordal |
| `nx.is_d_separator()` | D-separation in Bayesian networks |
| `nx.find_minimal_d_separator()` | Find minimal d-separator |
| `nx.moral_graph(DG)` | Moralize a DAG |
| `nx.flow_hierarchy()` | Hierarchy measure for directed graphs |
| `nx.is_threshold_graph()` | Test if threshold graph |
| `nx.find_threshold_graph()` | Create threshold from degree seq |
