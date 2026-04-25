# Isomorphism, Matching, Coloring, and Specialized Algorithms

NetworkX provides algorithms for graph isomorphism, matching, graph coloring, and other specialized structural analysis.

## Graph Isomorphism

### Subgraph Isomorphism

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

H = nx.Graph()
H.add_edges_from([(a, b), (b, c), (c, d), (d, a)])

# Check if two graphs are isomorphic
is_iso = nx.is_isomorphic(G, H)
print(is_iso)  # True

# Fast isomorphism check (pre-filtering)
can_be = nx.algorithms.isomorphism.could_be_isomorphic(G, H)
fast_can_be = nx.algorithms.isomorphism.fast_could_be_isomorphic(G, H)
faster_can_be = nx.algorithms.isomorphism.faster_could_be_isomorphic(G, H)

# Get actual isomorphism mapping
GM = nx.algorithms.isomorphism.GraphMatcher(G, H)
if GM.is_isomorphic():
    mapping = GM.mapping
    print(mapping)  # e.g., {1: a, 2: b, 3: c, 4: d}

# Find all isomorphisms
all_iso = list(nx.algorithms.isomorphism.vf2pp_all_isomorphisms(G, H))
print(all_iso)

# Subgraph isomorphism
subgraph = nx.Graph()
subgraph.add_edges_from([(1, 2), (2, 3)])

sub_GM = nx.algorithms.isomorphism.GraphMatcher(G, subgraph)
is_sub = sub_GM.subgraph_is_isomorphic()
print(is_sub)  # True

# Find all subgraph matches
for match in sub_GM.subgraph_isomorphisms_iter():
    print(match)

# Edge-labeled subgraph isomorphism
GM_edge = nx.algorithms.isomorphism.GraphMatcher(
    G, H,
    node_match=lambda n1, n2: n1 == n2,
    edge_match=lambda e1, e2: e1.get("weight") == e2.get("weight")
)

# Tree isomorphism (faster for trees)
T1 = nx.balanced_tree(2, 3)
T2 = nx.balanced_tree(2, 3)
tree_iso = nx.algorithms.isomorphism.tree_isomorphism(T1, T2)
rooted_iso = nx.algorithms.isomorphism.tree_isomorphism(T1, T2, rooted=True)
```

### VF2++ Algorithm

```python
# VF2++ is the recommended default (fastest for most graphs)
GM = nx.algorithms.isomorphism.vf2pp_graph_matcher(G, H)

# All isomorphisms via VF2++
all_iso = nx.algorithms.isomorphism.vf2pp_all_isomorphisms(G, H)

# Subgraph isomorphism via VF2++
is_sub = nx.algorithms.isomorphism.vf2pp_subgraph_isomorphic(G, H)
```

## Graph Matching

### Maximum Matching

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)])

# Maximum cardinality matching
matching = nx.max_weight_matching(G, maxcardinality=True)
print(matching)  # e.g., {1: 2, 3: 4}

# Maximum weight matching
G.add_edge(1, 2, weight=10)
G.add_edge(3, 4, weight=1)
max_w = nx.max_weight_matching(G, weight="weight")
print(max_w)

# Minimum weight matching
min_w = nx.min_weight_matching(G, weight="weight")

# Maximum bipartite matching (faster for bipartite graphs)
BG = nx.Graph()
BG.add_nodes_from([1, 2, 3], bipartite=0)
BG.add_nodes_from([4, 5, 6], bipartite=1)
BG.add_edges_from([(1, 4), (1, 5), (2, 5), (2, 6), (3, 6)])

top_nodes = {1, 2, 3}
bipartite_matching = nx.bipartite.maximum_matching(BG, top_nodes=top_nodes)
print(bipartite_matching)

# Maximum matching via flow
from networkx.algorithms import bipartite
max_match = nx.max_weight_matching(G)

# Check if a set of edges is a matching
edge_set = {(1, 2), (3, 4)}
is_matching = nx.is_matching(G, edge_set)

# Check if matching is maximal (cannot add more edges)
is_maximal = nx.is_maximal_matching(G, edge_set)

# Check if matching is perfect (covers all nodes)
is_perfect = nx.is_perfect_matching(G, edge_set)
```

### Bipartite Matching Applications

```python
from networkx.algorithms import bipartite

BG = nx.Graph()
BG.add_nodes_from(["Alice", "Bob", "Carol"], bipartite=0)
BG.add_nodes_from(["Task1", "Task2", "Task3"], bipartite=1)
BG.add_edges_from([
    ("Alice", "Task1"), ("Alice", "Task2"),
    ("Bob", "Task2"), ("Bob", "Task3"),
    ("Carol", "Task1"), ("Carol", "Task3"),
])

top_nodes = {"Alice", "Bob", "Carol"}

# Maximum matching
matching = bipartite.maximum_matching(BG, top_nodes=top_nodes)

# Minimum node cover (Konig's theorem: |max matching| = |min vertex cover| for bipartite)
vertex_cover = bipartite.vertex_cover(BG, top_nodes=top_nodes)
print(vertex_cover)  # e.g., {"Alice", "Task2"}

# Maximum independent set
independent_set = bipartite.independent_set(BG, top_nodes=top_nodes)
print(independent_set)

# Minimum edge cover
edge_cover = bipartite.min_edge_cover(BG)
print(edge_cover)

# Check if perfect matching exists
is_perfect_match = bipartite.is_matching(BG, matching.items())
```

## Graph Coloring

### Coloring Strategies

NetworkX provides 7 greedy coloring strategies. Each produces different color counts.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Greedy coloring with various strategies
strategies = {
    'connected_sequential': nx.algorithms.coloring.strategy_connected_sequential,
    'connected_sequential_bfs': nx.algorithms.coloring.strategy_connected_sequential_bfs,
    'connected_sequential_dfs': nx.algorithms.coloring.strategy_connected_sequential_dfs,
    'largest_first': nx.algorithms.coloring.strategy_largest_first,
    'random_sequential': nx.algorithms.coloring.strategy_random_sequential,
    'saturation_largest_first': nx.algorithms.coloring.strategy_saturation_largest_first,
    'independent_set': nx.algorithms.coloring.strategy_independent_set,
    'smallest_last': nx.algorithms.coloring.strategy_smallest_last,
}

for name, strategy in strategies.items():
    coloring = nx.greedy_color(G, strategy=strategy)
    n_colors = max(coloring.values()) + 1
    print(f"{name}: {n_colors} colors")

# Equitable coloring (balanced color classes)
equitable = nx.equitable_color(G, k=3)
```

### Coloring Function Reference

| Function | Description |
|----------|-------------|
| `greedy_color(G, strategy=None, mapping=None, sequence=None)` | Greedy vertex coloring |
| `equitable_color(G, k)` | Equitable coloring with k colors |
| `strategy_connected_sequential(G, vertices=None, edges=None)` | BFS-based sequential coloring |
| `strategy_connected_sequential_bfs(G, ...)` | BFS order for sequential coloring |
| `strategy_connected_sequential_dfs(G, ...)` | DFS order for sequential coloring |
| `strategy_largest_first(G, ...)` | Sort by degree descending |
| `strategy_random_sequential(G, ...)` | Random node order |
| `strategy_saturation_largest_first(G, ...)` | Most constrained first |
| `strategy_independent_set(G, ...)` | Independent set ordering |
| `strategy_smallest_last(G, ...)` | Smallest-last ordering |coloring = nx.greedy_color(G)
print(coloring)  # e.g., {1: 0, 2: 1, 3: 2, 4: 0, 5: 0}

# Different coloring strategies
strategies = [
    nx.algorithms.coloring.strategy_connected_sequential,
    nx.algorithms.coloring.strategy_connected_sequential_bfs,
    nx.algorithms.coloring.strategy_connected_sequential_dfs,
    nx.algorithms.coloring.strategy_largest_first,
    nx.algorithms.coloring.strategy_random_sequential,
    nx.algorithms.coloring.strategy_saturation_largest_first,
    nx.algorithms.coloring.strategy_independent_set,
    nx.algorithms.coloring.strategy_smallest_last,
]

# Use specific strategy
coloring = nx.greedy_color(G, strategy=nx.algorithms.coloring.strategy_smallest_last)
n_colors = max(coloring.values()) + 1
print(f"Colors used: {n_colors}")

# Equitable coloring (balanced color classes)
equitable = nx.equitable_color(G, k=3)
print(equitable)  # e.g., {1: 0, 2: 1, 3: 2, 4: 0, 5: 1}
```

## Graph Colorings for Bipartite

```python
BG = nx.complete_bipartite_graph(3, 4)

# Check if bipartite
is_bip = nx.is_bipartite(BG)
print(is_bip)  # True

# Get the two partitions
partitions = nx.bipartite.sets(BG)
print(partitions)  # ({0, 1, 2}, {3, 4, 5, 6})

# Color the bipartite graph (2 colors)
colors = nx.bipartite.color(BG)
print(colors)  # {0: 0, 1: 1, 2: 0, 3: 1, ...}

# Check if node set is one partition
is_valid = nx.bipartite.is_bipartite_node_set(BG, {0, 1, 2})
print(is_valid)

# Bipartite density
density = nx.bipartite.density(BG)
print(density)

# Degree of nodes in bipartite graph
degrees = nx.bipartite.degrees(BG, weight=None)
```

## Specialized Algorithm Categories

### Triads (Directed 3-Node Subgraphs)

```python
DG = nx.DiGraph()
DG.add_edges_from([(0, 1), (1, 2)])  # Mutual, asymmetric, directed triad

# Check if a triple forms a specific triad type
is_triad = nx.is_triad(DG, [0, 1, 2])
triad_type = nx.triad_type(DG, [0, 1, 2])
print(triad_type)  # e.g., "300", "030T", etc.

# Triadic census (count all triads by type)
census = nx.triadic_census(DG)
print(census)  # e.g., {'300': 2, '030T': 1, ...}

# All triads in the graph
all_triads = nx.all_triads(DG)
triads_by_type = nx.triads_by_type(DG)

# Triad-based measures
for triad_type, count in census.items():
    print(f"{triad_type}: {count}")
```

### Reciprocity

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 1), (2, 3), (3, 4)])

# Overall reciprocity (fraction of mutual edges)
overall_recip = nx.overall_reciprocity(DG)
print(overall_recip)  # 0.5 (1 out of 2 edges is reciprocal)

# Per-node reciprocity
recip = nx.reciprocity(DG)
print(recip)  # {1: 1.0, 2: 0.5, 3: 0.0, ...}
```

### Assortativity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Degree assortativity (-1 to 1)
# Positive = similar degrees connect, negative = dissimilar
assortativity = nx.degree_assortativity_coefficient(G)
print(assortivity)

# Other assortativity measures
x_assort = nx.attribute_assortativity_coefficient(G, "color")
weight_assort = nx.weighted_degree_assortativity_coefficient(G)
```

### Rich Club

```python
G = nx.Graph()
# Create a rich-club structure (high-degree nodes well connected)
hub_nodes = [1, 2, 3, 4, 5]
for i in range(len(hub_nodes)):
    for j in range(i + 1, len(hub_nodes)):
        G.add_edge(hub_nodes[i], hub_nodes[j])

# Rich club coefficient
rc = nx.rich_club_coefficient(G, normalized=False, seed=42)
print(rc)  # [(k, phi_k), ...] where k = threshold, phi = rich club coefficient

# With normalization
rc_normalized = nx.rich_club_coefficient(G, normalized=True)
```

### Structural Holes

```python
G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (1, 4),  # Node 1 connects clusters {2}, {3,5}, {4}
    (3, 5), (4, 6),
])

# Constraint (structural holes measure)
constraint = nx.constraint(G, 1)
print(constraint)  # 0-1, lower = more structural holes

# Effective size
effective_size = nx.effective_size(G, 1)
print(effective_size)  # Number of non-redundant contacts

# Local constraint
local_constraint = nx.local_constraint(G, 1)
```

### Graph Edit Distance

```python
G1 = nx.Graph()
G1.add_edges_from([(1, 2), (2, 3)])

G2 = nx.Graph()
G2.add_edges_from([(a, b), (b, c), (c, d)])

# Compute graph edit distance
ged = nx.graph_edit_distance(G1, G2)
print(ged)  # Minimum operations to transform G1 into G2

# Optimal edit paths
opt_paths = nx.optimize_graph_edit_distance(G1, G2)
print(opt_paths)

# Similarity (0-1, higher = more similar)
similarity = nx.panther_similarity(G1, G2)
vector_sim = nx.panther_vector_similarity(G1, G2)

# SimRank similarity (based on random walks)
sr = nx.simrank_similarity(G, source=[1])
```

### Graph Hashing

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Weisfeiler-Lehman graph hash
wh_hash = nx.weisfeiler_lehman_graph_hash(G)
print(wh_hash)  # Unique hash for the graph structure

# Subgraph hashes
sub_hashes = nx.weisfeiler_lehman_subgraph_hashes(G)
print(sub_hashes)  # Per-node hashes
```

### Swap Operations

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (3, 4), (2, 3)])

# Double edge swap (preserves degree sequence)
G_swapped = nx.double_edge_swap(G, nswap=1, max_tries=100)

# Connected double edge swap
G_connected = nx.connected_double_edge_swap(G, nswap=1, max_tries=100)

# Directed edge swap
DG = nx.DiGraph([(1, 2), (3, 4)])
DG_swapped = nx.directed_edge_swap(DG, nswap=1, max_tries=100)
```

## Additional Matching Functions

```python
# Is matching (valid matching?)
is_match = nx.is_matching(G, {(1, 2), (3, 4)})

# Is maximal matching (can't add edges)
is_maximal = nx.is_maximal_matching(G, {(1, 2), (3, 4)})

# Is perfect matching (all nodes covered)
is_perfect = nx.is_perfect_matching(G, {(1, 2), (3, 4)})

# Maximum matching (cardinality)
max_match = nx.maximal_matching(G)

# Minimum weight matching
min_wt = nx.min_weight_matching(G, weight="weight")
```

## Complete Isomorphism Function Reference

| Function | Description |
|----------|-------------|
| `is_isomorphic(G, H)` | Quick isomorphism check |
| `could_be_isomorphic(G, H)` | Pre-filter (degree sequence) |
| `fast_could_be_isomorphic(G, H)` | Faster pre-filter |
| `faster_could_be_isomorphic(G, H)` | Fastest pre-filter |
| `GraphMatcher(G, H)` | Full isomorphism toolkit |
| `tree_isomorphism(T1, T2, rooted=False)` | Tree-specific isomorphism |
| `rooted_tree_isomorphism(T1, T2)` | Rooted tree isomorphism |
| `vf2pp_graph_matcher(G, H)` | VF2++ matcher factory |
| `vf2pp_all_isomorphisms(G, H)` | All isomorphisms via VF2++ |
| `vf2pp_subgraph_isomorphic(G, H)` | Subgraph iso via VF2++ |

## Complete Matching Function Reference

| Function | Description |
|----------|-------------|
| `max_weight_matching(G, weight=None, maxcardinality=False)` | Max cardinality/weight matching |
| `minimal_matching(G)` | Minimal matching (empty) |
| `maximal_matching(G)` | Greedy maximal matching |
| `min_weight_matching(G, weight=None)` | Min weight matching |
| `is_matching(G, edge_set)` | Validate matching |
| `is_maximal_matching(G, edge_set)` | Check maximality |
| `is_perfect_matching(G, edge_set)` | Check perfection |

## Summary

| Algorithm | Function | Description |
|-----------|----------|-------------|
| Isomorphism check | `nx.is_isomorphic()` | Are G and H isomorphic? |
| GraphMatcher | `nx.algorithms.isomorphism.GraphMatcher()` | Full isomorphism toolkit |
| VF2++ all isos | `vf2pp_all_isomorphisms()` | Find all isomorphisms |
| Tree isomorphism | `nx.algorithms.isomorphism.tree_isomorphism()` | Fast tree comparison |
| Max matching | `nx.max_weight_matching()` | Maximum cardinality/weight |
| Bipartite matching | `bipartite.maximum_matching()` | Fast bipartite matching |
| Vertex cover | `bipartite.vertex_cover()` | Minimum vertex cover (bipartite) |
| Greedy coloring | `nx.greedy_color()` | Graph coloring with 8 strategies |
| Equitable coloring | `nx.equitable_color(G, k)` | Balanced color classes |
| Triadic census | `nx.triadic_census()` | Count directed triads by type |
| Reciprocity | `nx.reciprocity()` | Mutual edge ratio |
| Assortativity | `nx.degree_assortativity_coefficient()` | Degree correlation |
| Rich club | `nx.rich_club_coefficient()` | High-degree connectivity |
| Constraint | `nx.constraint()` | Structural holes measure |
| Graph edit distance | `nx.graph_edit_distance()` | Minimum edit ops between graphs |
| WL hash | `nx.weisfeiler_lehman_graph_hash()` | Graph fingerprint |
