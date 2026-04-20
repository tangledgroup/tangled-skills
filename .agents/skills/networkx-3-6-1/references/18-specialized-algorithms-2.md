# Specialized Graph Algorithms (Part B: Paths, LCA, Metrics, Polynomials)

NetworkX provides algorithms for simple paths, lowest common ancestors, graph metrics, and polynomials.

## Simple Paths

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])

# All simple paths between two nodes (no repeated nodes)
all_paths = list(nx.all_simple_paths(G, source=1, target=4))
print(all_paths)
# [[1, 2, 4], [1, 3, 4], [1, 2, 3, 4]]

# With length limit
short_paths = list(nx.all_simple_paths(G, source=1, target=4, cutoff=2))
print(short_paths)
# [[1, 2, 4], [1, 3, 4]]  # Only paths of length <= 2

# All simple edge paths (no repeated edges)
all_edge_paths = list(nx.all_simple_edge_paths(G, source=1, target=4))
print(all_edge_paths)

# Check if a path is simple
is_simple = nx.is_simple_path(G, [1, 2, 4])
print(is_simple)  # True

is_not_simple = nx.is_simple_path(G, [1, 2, 3, 2, 4])
print(is_not_simple)  # False (node 2 repeated)

# Shortest simple paths (k-shortest without repeating nodes)
k_shortest = list(nx.shortest_simple_paths(G, source=1, target=4))
first = k_shortest[0]  # Shortest simple path
second = k_shortest[1]  # Second shortest simple path
```

## Lowest Common Ancestor (LCA)

For rooted trees, finds the deepest node that is an ancestor of both given nodes.

```python
T = nx.balanced_tree(2, 3)  # Rooted binary tree

# LCA of two nodes
lca = nx.lowest_common_ancestor(T, 4, 5)
print(lca)  # The deepest common ancestor

# All pairs LCA in a tree
all_lca = dict(nx.all_pairs_lowest_common_ancestor(T))
print(all_lca[(4, 5)])  # Same as above

# Tree-specific all-pairs LCA (more efficient for large trees)
tree_lca = nx.tree_all_pairs_lowest_common_ancestor(T, root=0)
for node, ancestors in tree_lca.items():
    print(f"Node {node}: LCA with each other node = {ancestors}")

# Build LCA data structure for fast queries
class LCARoot:
    def __init__(self, tree, root):
        self.tree = tree
        self.root = root
        # Precompute depths and parents
        self.depth = nx.single_source_shortest_path_length(tree, root)
        self.parent = {}
        for node in nx.dfs_preorder_nodes(tree, source=root):
            for nbr in tree[node]:
                if nbr != [p for p, c in nx.dfs_edges(tree, source=root) if c == node][0] if [p for p, c in nx.dfs_edges(tree, source=root) if c == node] else None:
                    pass  # Simplified - use BFS from root
        # For actual use, rely on nx.lowest_common_ancestor
```

## Closeness Vitality

Measures how "central" a node is based on changes in average shortest path.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Closeness vitality of each node
vitality = nx.closeness_vitality(G)
print(vitality)
# Dict: node -> how much avg shortest path increases if node is removed
```

## Small-World Metrics

Quantify small-world properties (high clustering + short path lengths).

```python
G = nx.watts_strogatz_graph(100, 4, 0.1)

# Clustering coefficient
clustering = nx.average_clustering(G)

# Average shortest path
avg_path = nx.average_shortest_path_length(G)

# Small-worldness sigma (σ > 1 indicates small-world)
sigma = nx.sigma(G, num_paths=100)
print(f"Sigma: {sigma:.4f}")  # σ = C_random / C_actual × L_actual / L_random

# Omega (ω) - measures deviation from regular lattice
omega = nx.omega(G, num_paths=100)
print(f"Omega: {omega:.4f}")  # ω ≈ 0 for small-world, < 0 for regular, > 0 for random

# Random and lattice reference graphs
lattice_ref = nx.lattice_reference(G, k=4, p=0.1, n_trials=10)
random_ref = nx.random_reference(G, n_trials=10)
```

**Interpretation:**
- **σ > 1**: Small-world (higher clustering + shorter paths than random)
- **ω ≈ 0**: Small-world structure
- **ω < 0**: Closer to regular lattice
- **ω > 0**: Closer to random graph

## S-Metric (Network Robustness)

Measures network robustness against targeted attacks.

```python
G = nx.karate_club_graph()

# S-metric (higher = more robust to random failure, less robust to targeted)
s_metric = nx.s_metric(G)
print(s_metric)

# Interpretation: measures concentration of connections on high-degree nodes
# High s_metric = network concentrates edges on few hubs (fragile to hub removal)
```

## Spanners (Graph Sparsification)

Approximate distance-preserving subgraphs.

```python
G = nx.Graph()
G.add_edges_from([(1, 2, {"weight": 1}), (1, 3, {"weight": 3}),
                   (2, 3, {"weight": 2}), (2, 4, {"weight": 4}),
                   (3, 4, {"weight": 1})])

# t-spanner: subgraph preserving distances within factor t
spanner = nx.spanner(G, weight="weight", stretch=2)
print(list(spanner.edges(data=True)))
# Returns a sparse subgraph where dist_spanner(u,v) ≤ t × dist_G(u,v)
```

## Graph Summarization

Compress large graphs while preserving structure.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Dedensify: merge nodes with identical neighborhoods
G_dedensified = nx.dedensify(G)
print(list(G_dedensified.nodes()))

# Snap aggregation: aggregate nodes by structural similarity
G_snap = nx.snap_aggregation(G, aggregation_function="mean")
```

## Graph Edit Distance (Optimized)

Graph edit distance measures the minimum cost to transform one graph into another.

```python
import networkx as nx
from networkx.algorithms import similarity

G1 = nx.Graph()
G1.add_edges_from([(1, 2), (2, 3)])

G2 = nx.Graph()
G2.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Optimal edit paths (sequence of operations to transform G1 → G2)
paths = similarity.optimal_edit_paths(G1, G2)
for path, cost in paths:
    print(f"Cost: {cost}")
    for op in path:
        print(f"  {op}")

# Optimize graph edit distance (faster, approximate)
opt_cost = similarity.optimize_graph_edit_distance(G1, G2)
print(f"Optimized GED: {opt_cost}")

# Optimize edit paths (find near-optimal transformation)
opt_paths = similarity.optimize_edit_paths(G1, G2)
for path, cost in opt_paths:
    print(f"Cost: {cost}, Operations: {len(path)}")
```

**Edit operations:**
- Node insertion/deletion
- Edge insertion/deletion
- Node/edge label substitution
- Each operation has an associated cost

## Polynomial Invariants

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])  # Triangle

# Chromatic polynomial (evaluated at k gives number of valid k-colorings)
# P(G, k) = k(k-1)(k-2) for triangle
chromatic = nx.chromatic_polynomial(G)
print(chromatic)
# Returns a Poly1 object: can evaluate at any k
num_3_colorings = chromatic(3)  # Should be 6
num_4_colorings = chromatic(4)  # Should be 24

# Tutte polynomial (generalization of chromatic, reliability, flow polynomials)
tutte = nx.tutte_polynomial(G)
print(tutte)
# P(x, y) for triangle: x² + x + y
```

## Regular Graphs

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])

# Check if k-regular (every node has degree k)
is_2_regular = nx.is_k_regular(G, k=2)
print(is_2_regular)

# Check if regular (any k)
is_regular = nx.is_regular(G)
print(is_regular)

# Find k-factor (k-regular spanning subgraph)
k_factor = nx.k_factor(G, k=1)
if k_factor:
    print(f"1-factor found: {list(k_factor.edges())}")
```

## Distance-Regular Graphs

```python
# Check if distance-regular (all pairs at same distance have same local structure)
G = nx.petersen_graph()
is_dist_reg = nx.is_distance_regular(G)
print(is_dist_reg)  # True (Petersen graph is distance-regular)

# Intersection array (describes the distance structure)
if is_dist_reg:
    intersection = nx.intersection_array(G)
    print(intersection)  # (3, 2, 1; 1, 1, 3) for Petersen

# Global parameters
params = nx.global_parameters(3, 2, 1, 1, 1, 3)
print(params)

# Check strongly regular (special case of distance-regular with λ, μ)
is_strongly_reg = nx.is_strongly_regular(G)
```

## Additional Similarity Measures

```python
from networkx.algorithms import similarity

# Panther similarity (based on random walks)
panther_sim = similarity.panther_similarity(G1, G2)
print(panther_sim)  # Float between 0 and 1

# Panther vector similarity (feature-based)
panther_vec = similarity.panther_vector_similarity(G1, G2)
print(panther_vec)  # Similarity vector

# SimRank similarity (based on random walks with restarts)
sr = nx.simrank_similarity(G, source=[1], max_iter=100, epsilon=1e-6)
print(sr[(1, 2)])  # SimRank score between nodes 1 and 2
```

## Complete Structural Holes Reference

| Function | Description |
|----------|-------------|
| `constraint(G, nodes=None)` | Burt's constraint (structural holes) |
| `effective_size(G, nodes=None)` | Effective network size |
| `local_constraint(G, nodes=None)` | Local constraint measure |

## Complete Swap Operations Reference

| Function | Description |
|----------|-------------|
| `double_edge_swap(G, nswap, max_tries=100)` | Preserve degree sequence |
| `connected_double_edge_swap(G, nswap, max_tries=100)` | Connected result |
| `directed_edge_swap(DG, nswap, max_tries=100)` | Directed swap (preserve in/out degrees) |

## Summary (Part B)

| Function | Description |
|----------|-------------|
| `nx.all_simple_paths()` | All paths without repeated nodes |
| `nx.all_simple_edge_paths()` | All paths without repeated edges |
| `nx.is_simple_path()` | Check if path has no repeats |
| `nx.shortest_simple_paths()` | k-shortest simple paths |
| `nx.lowest_common_ancestor()` | LCA in rooted tree |
| `nx.all_pairs_lowest_common_ancestor()` | All-pairs LCA |
| `nx.tree_all_pairs_lowest_common_ancestor()` | Efficient all-pairs LCA for trees |
| `nx.closeness_vitality()` | Node importance via path disruption |
| `nx.sigma()` | Small-worldness σ metric |
| `nx.omega()` | Regular-to-random deviation ω |
| `nx.s_metric()` | Network robustness measure |
| `nx.spanner()` | Distance-preserving subgraph |
| `nx.dedensify()` | Merge identical-neighborhood nodes |
| `nx.snap_aggregation()` | Structural aggregation |
| `nx.chromatic_polynomial()` | Polynomial for graph coloring count |
| `nx.tutte_polynomial()` | General graph polynomial invariant |
| `nx.is_k_regular()` | Check k-regularity |
| `nx.k_factor()` | Find k-regular spanning subgraph |
| `nx.is_distance_regular()` | Test distance-regularity |
| `nx.intersection_array()` | Distance structure of distance-regular graphs |
