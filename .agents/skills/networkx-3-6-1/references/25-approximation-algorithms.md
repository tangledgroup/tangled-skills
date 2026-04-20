# Approximation Algorithms

NetworkX provides approximation algorithms for NP-hard optimization problems, including clique, independent set, vertex cover, Steiner tree, TSP, max cut, densest subgraph, dominating set, and treewidth.

## Clique and Independent Set

```python
from networkx.algorithms import approximation

G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (1, 4),
    (2, 3), (2, 4),
    (3, 4),
    (4, 5), (4, 6),
    (5, 6),
])

# Approximate maximum clique (greedy)
approx_clique = approximation.clique.max_clique(G)
print(approx_clique)

# Clique removal (iteratively remove max clique, useful for graph coloring)
cliques_removed = list(approximation.clique.clique_removal(G))
print(cliques_removed)  # List of cliques, largest first

# Large clique size (upper bound, faster than exact)
large = approximation.clique.large_clique_size(G)
print(large)

# Approximate maximum independent set
approx_mis = approximation.clique.maximum_independent_set(G)
print(approx_mis)  # Largest set of non-adjacent nodes
```

## Densest Subgraph

Find the subgraph with maximum density (edges/nodes ratio). This can be solved exactly using max-flow.

```python
# Find densest subgraph
densest_nodes = approximation.density.densest_subgraph(G, weight="weight")
print(densest_nodes)  # Set of nodes in densest subgraph

# With edge weights
G.add_edge(1, 2, weight=10)
dense_heavy = approximation.density.densest_subgraph(G, weight="weight")
```

## Dominating Set

```python
# Minimum edge dominating set (each edge adjacent to at least one in set)
min_ed = approximation.dominating_set.min_edge_dominating_set(G)

# Minimum weighted dominating set
G.add_nodes_from([1, 2, 3], weight={1: 5, 2: 3, 3: 4})
min_wd = approximation.dominating_set.min_weighted_dominating_set(
    G, weight="weight"
)
```

## Vertex Cover

Approximate minimum vertex cover (smallest set of nodes touching all edges).

```python
# Approximate minimum weighted vertex cover (2-approximation)
vc = approximation.vertex_cover.min_weighted_vertex_cover(G, weight="weight")
print(vc)  # Set of vertices covering all edges
```

## Matching

```python
# Minimum maximal matching (smallest set of non-adjacent edges)
min_max = approximation.matching.min_maximal_matching(G)
print(min_max)  # Minimal (not maximum) matching
```

## Max Cut

Partition nodes into two sets to maximize crossing edges.

```python
# One-exchange local search (0.5-approximation)
max_cut_edges = approximation.maxcut.one_exchange(
    G, weight="weight", max_iter=100, seed=42
)
print(max_cut_edges)  # Set of edges in the cut

# Randomized partitioning (also 0.5-approximation)
max_cut_random = approximation.maxcut.randomized_partitioning(
    G, weight="weight", seed=42
)
```

## Steiner Tree

Find minimum-cost tree connecting a subset of terminal nodes.

```python
# Build weighted graph
G = nx.Graph()
G.add_edges_from([
    (1, 2, {"weight": 1}), (1, 3, {"weight": 4}),
    (2, 3, {"weight": 2}), (2, 4, {"weight": 5}),
    (3, 4, {"weight": 3}), (3, 5, {"weight": 2}),
    (4, 5, {"weight": 1}),
])

terminals = {1, 4, 5}

# Steiner tree in metric closure (2-approximation for metric case)
steiner_tree = approximation.steinertree.steiner_tree(G, terminals, weight="weight")
print(list(steiner_tree.edges(data=True)))

# Metric closure (all-pairs shortest paths on terminal subset)
mclosure = approximation.steinertree.metric_closure(G, terminals, weight="weight")
```

## Traveling Salesperson Problem

```python
# Christofides algorithm (1.5-approximation for metric TSP)
tsp_christofides = approximation.traveling_salesman.christofides(
    G, weight="weight"
)
print(tsp_christofides)  # List of nodes in tour order

# Asadpour ATSP (Asymmetric TSP, 2(1+ln(3/2))-approximation)
DG = nx.DiGraph(G)  # Convert to directed
tsp_asadpour = approximation.traveling_salesman.asadpour_atsp(
    DG, weight="weight"
)

# Greedy TSP (nearest neighbor heuristic)
tsp_greedy = approximation.traveling_salesman.greedy_tsp(
    G, weight="weight", cycle=False
)

# Simulated annealing TSP
tsp_sa = approximation.traveling_salesman.simulated_annealing_tsp(
    G, weight="weight", temperature=2.0, max_iterations=1000
)

# Threshold accepting TSP
tsp_ta = approximation.traveling_salesman.threshold_accepting_tsp(
    G, weight="weight"
)

# General TSP solver (chooses best method)
TSP_result = approximation.traveling_salesman.traveling_salesman_problem(
    G, weight="weight", method="christofides"
)
```

## Treewidth

Treewidth measures how "tree-like" a graph is. Computing exact treewidth is NP-hard; these are heuristics.

```python
# Treewidth via minimum degree elimination ordering
tw_min_deg = approximation.treewidth.treewidth_min_degree(G)
print(tw_min_deg)  # (width, elimination_order)

# Treewidth via minimum fill-in heuristic
tw_min_fill = approximation.treewidth.treewidth_min_fill_in(G)
print(tw_min_fill)  # (width, elimination_order)
```

## Approximate Connectivity

```python
# All-pairs approximate node connectivity
all_conn = approximation.connectivity.all_pairs_node_connectivity(G)

# Local approximate node connectivity
local_conn = approximation.connectivity.local_node_connectivity(G, 1, 4)

# Approximate k-components
k_comps = approximation.kcomponents.k_components(G)
```

## Summary

| Problem | Function | Approximation Ratio |
|---------|----------|-------------------|
| Max clique | `approximation.clique.max_clique()` | O(n/log²n) |
| Clique removal | `approximation.clique.clique_removal()` | Greedy |
| Large clique size | `approximation.clique.large_clique_size()` | Upper bound |
| Max independent set | `approximation.clique.maximum_independent_set()` | O(Δ/log Δ) |
| Densest subgraph | `approximation.density.densest_subgraph()` | Exact (fractional) |
| Min edge dominating set | `approximation.dominating_set.min_edge_dominating_set()` | 2-approx |
| Min weighted DS | `approximation.dominating_set.min_weighted_dominating_set()` | ln(Δ)-approx |
| Min vertex cover | `approximation.vertex_cover.min_weighted_vertex_cover()` | 2-approx |
| Min-maximal matching | `approximation.matching.min_maximal_matching()` | Greedy |
| Max cut (local search) | `approximation.maxcut.one_exchange()` | 0.5-approx |
| Max cut (randomized) | `approximation.maxcut.randomized_partitioning()` | 0.5-approx |
| Steiner tree | `approximation.steinertree.steiner_tree()` | 2-approx (metric) |
| TSP (Christofides) | `approximation.traveling_salesman.christofides()` | 1.5-approx |
| ATSP (Asadpour) | `approximation.traveling_salesman.asadpour_atsp()` | 2(1+ln(3/2))-approx |
| TSP (greedy) | `approximation.traveling_salesman.greedy_tsp()` | O(log n) |
| Treewidth (min degree) | `approximation.treewidth.treewidth_min_degree()` | Heuristic |
| Treewidth (min fill-in) | `approximation.treewidth.treewidth_min_fill_in()` | Heuristic |
