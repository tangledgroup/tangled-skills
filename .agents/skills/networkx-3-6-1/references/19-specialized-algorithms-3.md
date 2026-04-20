# Specialized Graph Algorithms (Part C: Efficiency, Tournament, Chemical Indices, Classification)

NetworkX provides algorithms for efficiency measures, tournaments, chemical graph indices, node classification, and more.

## Efficiency Measures

Measures how efficiently information flows through a network.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)])

# Local efficiency (clustering of neighbors)
local_eff = nx.local_efficiency(G)
print(local_eff)  # How well connected are each node's neighbors

# Global efficiency (inverse of average shortest path in complement)
global_eff = nx.global_efficiency(G)
print(global_eff)  # Overall network efficiency

# Individual node efficiency
eff = nx.efficiency(G)
print(eff)  # Dict: node -> local efficiency

# Interpretation:
# - Global efficiency ≈ 1 for fully connected, → 0 as graph disconnects
# - High global efficiency = fast information flow
# - Used in transportation, communication, and brain network analysis
```

## Non-Randomness Measure

Quantifies how far a graph is from a random graph with same degree sequence.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4)])

# Non-randomness measure
nr = nx.non_randomness(G)
print(nr)  # Higher = more structured, lower = more random-like

# Used to detect community structure, modular organization
```

## Time-Dependent Centrality

Centrality measures that account for temporal dynamics.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# CD index (communicability-based diffusion centrality)
cd = nx.cd_index(G, source=1)
print(cd)  # How quickly information from node 1 reaches all others

# Useful for temporal networks, epidemic spreading analysis
```

## Tournament Graphs

A tournament is a directed graph where every pair of nodes has exactly one directed edge.

```python
import networkx as nx

# Create a random tournament
T = nx.random_tournament(10)
print(list(T.edges())[:10])

# Check if a graph is a tournament
is_tournament = nx.is_tournament(T)
print(is_tournament)  # True

# Score sequence (out-degrees, sorted)
scores = nx.score_sequence(T)
print(scores)  # e.g., [0, 1, 1, 2, 2, 3, 3, 3, 4, 5]

# Hamiltonian path (exists in every tournament)
hamiltonian = nx.hamiltonian_path(T)
print(hamiltonian)  # A path visiting all nodes exactly once

# Check reachability in tournament
is_reachable = nx.is_reachable(T, 1, 5)
print(is_reachable)  # True if there's a directed path from 1 to 5

# Strongly connected tournament
is_strong = nx.is_strongly_connected(T)

# Tournament matrix (adjacency matrix for tournaments)
matrix = nx.tournament_matrix(T)
```

**Landau's Theorem**: A sequence of non-negative integers is a tournament score sequence iff it satisfies certain conditions (sum of k smallest scores ≥ C(k,2) for all k).

## Voronoi Cells

Partition nodes based on proximity to seed nodes.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5), (4, 5)])

# Seeds for Voronoi partitioning
seeds = {0: "cluster_A", 4: "cluster_B"}

# Voronoi cells based on shortest path distance
cells = nx.voronoi_cells(G, seeds)
print(cells)
# Dict mapping seed -> set of nodes closest to that seed

# Used for clustering, facility location, territory partitioning
```

## Walks and Path Counting

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Number of walks of length k between nodes
walks_2 = nx.number_of_walks(G, 2)
print(walks_2)
# walks_2[u][v] = number of walks of length 2 from u to v

# Walk counts from a specific source
walks_from_1 = nx.number_of_walks(G, 3, source=1)
print(walks_from_1)
# Dict: target -> number of walks of length 3 from node 1

# Walks are useful for:
# - Random walk simulations
# - Counting paths in DAGs (via dynamic programming)
# - Estimating connectivity
```

## Chemical Graph Indices (Wiener Family)

Topological indices used in cheminformatics to correlate molecular structure with properties.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])  # Path graph = pentane

# Wiener index (sum of all pairwise shortest path distances)
wiener = nx.wiener_index(G)
print(wiener)
# Used to predict boiling point, stability of alkanes

# Schultz index (weighted by degree)
schultz = nx.schultz_index(G)
print(schultz)

# Gutman index (another degree-weighted distance sum)
gutman = nx.gutman_index(G)
print(gutman)

# Hyper-Wiener index (includes squared distances)
hyper_wiener = nx.hyper_wiener_index(G)
print(hyper_wiener)

# These indices are used in QSAR/QSPR studies:
# - Predicting chemical properties from structure
# - Drug design and molecular similarity
# - Material science (nanotubes, polymers)
```

## Random Path Generation

Generate random paths for Monte Carlo analysis and sampling.

```python
import networkx as nx
from networkx.algorithms import similarity

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])

# Generate random paths between source and target
paths = list(similarity.generate_random_paths(G, source=1, target=5, length=3))
for path in paths:
    print(path)  # e.g., [1, 3, 4, 5]

# Useful for:
# - Monte Carlo estimation of connectivity
# - Random walk betweenness centrality
# - Sampling paths in large graphs
```

## Communicability

Measures how easily information/contagion spreads through a network.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Communicability between all pairs (based on graph adjacency eigenvalues)
comm = nx.communicability(G)
print(comm)
# comm[u][v] = Σ λᵏ/k! for walks from u to v
# Higher = more paths (of all lengths) between nodes

# Communicability exponential (more computationally efficient)
comm_exp = nx.communicability_exp(G)
print(comm_exp)

# Used for:
# - Social network analysis (information spread)
# - Biological networks (protein interaction)
# - Web link analysis
```

## Chain Decomposition

Decompose a graph into cycles and paths.

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])

# Find chain decomposition
chains = nx.chain_decomposition(G)
print(chains)
# List of cycles and paths that decompose the graph

# Useful for:
# - Understanding cycle structure
# - Network robustness analysis
# - Graph factorization
```

## Node Classification

Label propagation and harmonic function methods for classifying unlabeled nodes.

```python
import networkx as nx

G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (2, 3),  # Cluster A
    (4, 5), (4, 6), (5, 6),  # Cluster B
    (3, 4),                    # Bridge
])

# Label some nodes
labeled_nodes = {1: "A", 2: "A", 4: "B", 5: "B"}
unlabeled = set(G.nodes()) - set(labeled_nodes.keys())

# Harmonic function method (solves Laplacian system)
labels_harmonic = nx.harmonic_function(G, labeled_nodes, unlabeled)
print(labels_harmonic)
# {3: 'A', 6: 'B'} - propagated labels

# Local and global consistency (combines local smoothness with global structure)
labels_lgc = nx.local_and_global_consistency(
    G,
    labeled_nodes,
    unlabeled,
    gamma=1.0,
    n_iterations=10
)
print(labels_lgc)

# Used for:
# - Semi-supervised learning on graphs
# - Social network analysis (predicting group membership)
# - Biological networks (protein function prediction)
```

## Approximation Algorithms

Approximate solutions for NP-hard problems.

```python
import networkx as nx
from networkx.algorithms import approximation

G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (1, 4),
    (2, 3), (2, 4),
    (3, 4),
    (4, 5), (4, 6),
    (5, 6),
])

# === Clique Problems ===
# Approximate maximum clique (greedy)
approx_clique = nx.approximation.clique.max_clique(G)
print(approx_clique)

# Clique removal algorithm (iteratively remove max clique)
cliques_removed = list(nx.approximation.clique.clique_removal(G))

# Large clique size (approximate upper bound)
large = nx.approximation.clique.large_clique_size(G)

# Approximate maximum independent set
approx_mis = nx.approximation.clique.maximum_independent_set(G)

# Approximate average clustering (faster for large graphs)
avg_cc = nx.approximation.clustering_coefficient.average_clustering(G)

# === Connectivity ===
# Approximate all-pairs node connectivity
all_conn = nx.approximation.connectivity.all_pairs_node_connectivity(G)

# Approximate local node connectivity
local_conn = nx.approximation.connectivity.local_node_connectivity(G, 1, 4)

# === Densest Subgraph ===
# Find subgraph with maximum density (edges/nodes)
densest_nodes = nx.approximation.density.densest_subgraph(G)
print(densest_nodes)  # Nodes in densest subgraph

# === Dominating Set ===
# Minimum edge dominating set
min_ed = nx.approximation.dominating_set.min_edge_dominating_set(G)

# Minimum weighted dominating set
min_wd = nx.approximation.dominating_set.min_weighted_dominating_set(G, weight="weight")

# === Vertex Cover ===
# Approximate minimum vertex cover
vc = nx.approximation.vertex_cover.min_weighted_vertex_cover(G, weight="weight")

# === Matching ===
# Min-maximal matching (minimum maximal matching)
min_max = nx.approximation.matching.min_maximal_matching(G)

# === Max Cut ===
# One-exchange local search
max_cut_edges = nx.approximation.maxcut.one_exchange(G, weight="weight", max_iter=100)

# Randomized partitioning
max_cut_random = nx.approximation.maxcut.randomized_partitioning(G, weight="weight")

# === Steiner Tree ===
# Steiner tree in metric closure
steiner = nx.approximation.steinertree.steiner_tree(G, {1, 4, 5}, weight="weight")

# Metric closure (all-pairs shortest paths on subset)
mclosure = nx.approximation.steinertree.metric_closure(G, {1, 4, 5})

# === Traveling Salesperson Problem ===
# Christofides algorithm (1.5-approximation for metric TSP)
tsp_christofides = nx.approximation.traveling_salesman.christofides(G, weight="weight")

# Asadpour ATSP (Asymmetric TSP, 2(1+ln(3/2))-approximation)
tsp_asadpour = nx.approximation.traveling_salesman.asadpour_atsp(G, weight="weight")

# Greedy TSP (nearest neighbor)
tsp_greedy = nx.approximation.traveling_salesman.greedy_tsp(G, weight="weight", cycle=False)

# Simulated annealing TSP
tsp_sa = nx.approximation.traveling_salesman.simulated_annealing_tsp(G, weight="weight")

# Threshold accepting TSP
tsp_ta = nx.approximation.traveling_salesman.threshold_accepting_tsp(G, weight="weight")

# General TSP solver
TSP = nx.approximation.traveling_salesman.traveling_salesman_problem(G, weight="weight")

# === Treewidth ===
# Treewidth via minimum degree heuristic
tw_min_deg = nx.approximation.treewidth.treewidth_min_degree(G)
print(tw_min_deg)  # (width, elimination_order)

# Treewidth via minimum fill-in heuristic
tw_min_fill = nx.approximation.treewidth.treewidth_min_fill_in(G)

# === Approximate k-Components ===
k_comps = nx.approximation.kcomponents.k_components(G)
```

## Asteroidal Triples

Detect asteroidal triples (three nodes where each pair has a path avoiding neighbors of the third).

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)])

# Find an asteroidal triple
at = nx.find_asteroidal_triple(G)
print(at)  # e.g., [1, 3, 5] or None

# Check if graph is AT-free (no asteroidal triples)
is_at_free = nx.is_at_free(G)
print(is_at_free)

# AT-free graphs include:
# - Interval graphs
# - Permutation graphs
# - Comparability graphs
```

## Complete Approximation Algorithm Reference

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

## Tournament Functions Reference

| Function | Description |
|----------|-------------|
| `is_tournament(DG)` | Check if directed graph is a tournament |
| `random_tournament(n, seed=None)` | Generate random tournament on n nodes |
| `score_sequence(DG)` | Out-degree sequence (sorted) |
| `hamiltonian_path(DG)` | Find Hamiltonian path (exists in every tournament) |
| `is_reachable(DG, u, v)` | Check reachability in tournament |
| `is_strongly_connected(DG)` | Check if strongly connected |
| `tournament_matrix(DG)` | Adjacency matrix for tournament |

## Complete Efficiency Measures Reference

| Function | Description |
|----------|-------------|
| `local_efficiency(G)` | Mean of local node efficiencies |
| `global_efficiency(G)` | Inverse of harmonic mean of distances |
| `efficiency(G)` | Per-node local efficiency |

## Complete Communicability Reference

| Function | Description |
|----------|-------------|
| `communicability(G)` | Walk-based connectivity (eigenvalue formula) |
| `communicability_exp(G)` | Exponential variant (faster) |

## Summary (Part C)

| Function | Description | Domain |
|----------|-------------|--------|
| `nx.local_efficiency()` | Clustering of neighbors | Transportation, brain networks |
| `nx.global_efficiency()` | Inverse avg shortest path | Communication networks |
| `nx.non_randomness()` | Structure vs randomness | Community detection |
| `nx.cd_index()` | Communicability diffusion | Temporal networks |
| `nx.is_tournament()` | Test tournament graph | Voting, competition |
| `nx.hamiltonian_path()` | Hamiltonian path in tournament | Scheduling |
| `nx.score_sequence()` | Out-degree sequence | Tournament analysis |
| `nx.voronoi_cells()` | Distance-based partitioning | Facility location |
| `nx.number_of_walks()` | Walk counting (matrix powers) | Random walks, connectivity |
| `nx.wiener_index()` | Sum of all pairwise distances | Cheminformatics (alkanes) |
| `nx.schultz/gutman_index()` | Degree-weighted distance sums | QSPR studies |
| `nx.hyper_wiener_index()` | Squared-distance Wiener index | Molecular properties |
| `nx.communicability()` | Walk-based connectivity | Social/bio networks |
| `nx.chain_decomposition()` | Cycle/path decomposition | Graph factorization |
| `nx.harmonic_function()` | Label propagation via Laplacian | Semi-supervised learning |
| `nx.max_clique()` | Approximate max clique | Heuristic optimization |
| `nx.clique_removal()` | Greedy clique decomposition | Graph coloring |
| `nx.is_at_free()` | Test for asteroidal triples | Interval/permutation graphs |
