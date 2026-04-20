# Bipartite Networks

Bipartite graphs have nodes partitioned into two sets U and V where every edge connects a node in U to one in V. NetworkX provides extensive support for bipartite graph analysis, generation, projection, and matching.

## Basic Operations

```python
import networkx as nx
from networkx.algorithms import bipartite

BG = nx.Graph()
BG.add_nodes_from(["A", "B", "C"], bipartite=0)  # Set U
BG.add_nodes_from(["X", "Y"], bipartite=1)        # Set V
BG.add_edges_from([("A", "X"), ("A", "Y"), ("B", "X"), ("C", "Y")])

# Check if bipartite
is_bip = nx.is_bipartite(BG)

# Get the two partitions
set1, set2 = nx.bipartite.sets(BG)

# Color nodes by partition
colors = nx.bipartite.color(BG)

# Degrees in bipartite graph
degrees = nx.bipartite.degrees(BG, weight=None)

# Density
density = nx.bipartite.density(BG)

# Check if node set is a valid partition
is_valid = nx.bipartite.is_bipartite_node_set(BG, {"A", "B", "C"})
```

## Bipartite Generators

```python
from networkx.algorithms import bipartite

# Complete bipartite graph K_{m,n}
K = nx.complete_bipartite_graph(3, 4)

# Havel-Hakimi bipartite graph from degree sequences
H = bipartite.havel_hakimi_graph([3, 2, 2], [3, 2])

# Alternating Havel-Hakimi
H_alt = bipartite.alternating_havel_hakimi_graph([3, 2, 2], [3, 2])

# Reverse Havel-Hakimi
H_rev = bipartite.reverse_havel_hakimi_graph([3, 2, 2], [3, 2])

# Configuration model for bipartite
CM = bipartite.configuration_model([3, 2, 2], [3, 2])

# GNMK random bipartite graph
G_nmk = bipartite.gnmk_random_graph(5, 4, 8)

# Preferential attachment for bipartite
PA = bipartite.preferential_attachment_graph([3, 2, 2], 0.5)

# Random bipartite graph
R = bipartite.random_graph(seed=None)
```

## Bipartite Projections (One-Mode Conversion)

Projection maps a bipartite graph to a one-mode graph on one partition, where two nodes are connected if they share a neighbor in the other set.

```python
# Project to U-nodes (co-occurrence of A,B,C via X,Y)
proj_U = nx.bipartite.projected_graph(BG, {"A", "B", "C"})

# Weighted projection (weight = number of shared neighbors)
wp = nx.bipartite.weighted_projected_graph(BG, {"A", "B", "C"})

# Overlap weighted projection
owp = nx.bipartite.overlap_weighted_projected_graph(BG, {"A", "B", "C"})

# Collaboration weighted projection (inverse of shared neighbors)
cwp = nx.bipartite.collaboration_weighted_projected_graph(BG, {"A", "B", "C"})

# Generic weighted projection with custom function
def weight_func(common_neighbors):
    return 1.0 / len(common_neighbors) if common_neighbors else 0
gwp = nx.bipartite.generic_weighted_projected_graph(
    BG, {"A", "B", "C"}, weight_func=weight_func
)
```

## Bipartite Matching

```python
# Maximum matching (returns dict with both directions)
matching = bipartite.maximum_matching(BG, top_nodes={"A", "B", "C"})

# Hopcroft-Karp algorithm (fastest for bipartite graphs)
hk = bipartite.hopcroft_karp_matching(BG, top_nodes={"A", "B", "C"})

# Eppstein's matching algorithm
ep = bipartite.eppstein_matching(BG, top_nodes={"A", "B", "C"})

# Minimum weight full matching
mwm = bipartite.minimum_weight_full_matching(
    BG, top_nodes={"A", "B", "C"}, weight="weight"
)

# Convert maximum matching to minimum vertex cover (Konig's theorem)
vc = bipartite.vertex_cover(BG, top_nodes={"A", "B", "C"})

# Maximum independent set
mis = bipartite.independent_set(BG, top_nodes={"A", "B", "C"})

# Minimum edge cover
mec = bipartite.min_edge_cover(BG)
```

## Bipartite Matrix Operations

```python
# Biadjacency matrix (rows = U-set, cols = V-set)
bimatrix = nx.bipartite.biadjacency_matrix(
    BG, row_order=["A", "B", "C"], column_order=["X", "Y"]
)

# From biadjacency matrix to graph
BG2 = nx.bipartite.from_biadjacency_matrix(bimatrix)
```

## Bipartite Centrality

```python
# Betweenness centrality (bipartite-specific algorithm)
bcb = bipartite.betweenness_centrality(BG, weight=None, normalized=True)

# Closeness centrality (bipartite-specific)
bcc = bipartite.closeness_centrality(BG)

# Degree centrality (bipartite-specific)
bdc = bipartite.degree_centrality(BG)
```

## Bipartite Clustering

```python
# Local clustering coefficient
lcc = bipartite.clustering(BG)

# Average clustering
avg_cc = bipartite.average_clustering(BG)

# Latapy's clustering (optimized for bipartite, O(m) instead of O(n³))
lcc_latapy = bipartite.latapy_clustering(BG)

# Robins-Alexander clustering
rac = bipartite.robins_alexander_clustering(BG)
```

## Bipartite Link Analysis & Ranking

```python
# BiRANK (bipartite ranking algorithm)
br = bipartite.link_analysis.birank(
    BG, target_nodes={"X"}, damping=0.85, max_iter=100
)

# Extending BiRANK for classification
extended = bipartite.link_analysis.birank(
    BG, target_nodes={"X"}, unlabeled_nodes={"A", "B", "C"},
    alpha=0.5, damping=0.85
)
```

## Bipartite Other Measures

```python
# Redundancy (fraction of a node's neighbors that are connected to each other)
redund = bipartite.node_redundancy(BG, "A")

# Spectral bipartivity (how bipartite the graph is, 0-1 scale)
sb = bipartite.spectral_bipartivity(BG)

# Maximal extendability (can a node be added while preserving bipartiteness?)
max_ext = bipartite.extendability.maximal_extendability(
    BG, "new_node", {"A", "B", "C"}
)

# Edge list operations for bipartite graphs
lines = bipartite.edgelist.generate_edgelist(BG)
bipartite.edgelist.write_edgelist(BG, "bipartite.edgelist")
BG_read = bipartite.edgelist.read_edgelist("bipartite.edgelist")
```

## Practical Applications

### Recommendation Systems via Projection

```python
# User-item bipartite graph
users = [f"user_{i}" for i in range(10)]
items = [f"item_{i}" for i in range(20)]
G = nx.Graph()
G.add_nodes_from(users, bipartite=0)
G.add_nodes_from(items, bipartite=1)

# Known interactions (user liked item)
interactions = [
    ("user_0", "item_0"), ("user_0", "item_1"), ("user_0", "item_3"),
    ("user_1", "item_1"), ("user_1", "item_2"),
    ("user_2", "item_0"), ("user_2", "item_3"),
]
G.add_edges_from(interactions)

# User-item projection (users who liked same items are connected)
user_proj = bipartite.projected_graph(G, users)

# Weighted user projection (weight = shared items)
user_wp = bipartite.weighted_projected_graph(G, users)

# Predict items for user_0 using weighted projection
candidates = [(u, v, w) for u, v, w in user_wp.edges(data=True, weight='weight')
              if u == "user_0" and not G.has_edge("user_0", v)]
recommended = sorted(candidates, key=lambda x: x[2], reverse=True)[:5]
```

### Citation Networks via Bipartite Projection

```python
# Papers × Topics bipartite graph
papers = ["P1", "P2", "P3", "P4"]
topics = ["ML", "DL", "NLP", "CV"]
G = nx.Graph()
G.add_nodes_from(papers, bipartite=0)
G.add_nodes_from(topics, bipartite=1)
G.add_edges_from([
    ("P1", "ML"), ("P1", "DL"),
    ("P2", "DL"), ("P2", "NLP"),
    ("P3", "ML"), ("P3", "CV"),
    ("P4", "NLP"), ("P4", "CV"),
])

# Paper-paper projection (papers sharing topics are connected)
paper_proj = bipartite.weighted_projected_graph(G, papers)
print(list(paper_proj.edges(data=True)))
# Shows which papers share topics and how many
```

## Summary

| Function | Description |
|----------|-------------|
| `is_bipartite(G)` | Check if graph is bipartite |
| `bipartite.sets(G)` | Get two node partitions |
| `bipartite.color(G)` | Node → partition color mapping |
| `complete_bipartite_graph(m, n)` | K_{m,n} generator |
| `projected_graph(G, nodes)` | One-mode projection |
| `weighted_projected_graph(G, nodes)` | Weighted co-occurrence projection |
| `maximum_matching(G, top_nodes)` | Maximum cardinality matching |
| `hopcroft_karp_matching(G, top_nodes)` | Fastest bipartite matching |
| `vertex_cover(G, top_nodes)` | Minimum vertex cover (bipartite) |
| `independent_set(G, top_nodes)` | Maximum independent set |
| `biadjacency_matrix(G, row_order, column_order)` | Biadjacency matrix |
| `from_biadjacency_matrix(matrix)` | Matrix → bipartite graph |
| `betweenness_centrality(G, top_nodes)` | Bipartite betweenness |
| `spectral_bipartivity(G)` | How bipartite is the graph (0-1) |
