# Algorithms Reference

NetworkX 3.6.1 provides 70+ algorithm modules organized into major categories.

## Centrality

Measures of node importance in a network:

```python
nx.degree_centrality(G)
nx.betweenness_centrality(G)
nx.closeness_centrality(G)
nx.eigenvector_centrality(G)
nx.pagerank(G)
nx.katz_centrality(G)
nx.harmonic_centrality(G)
nx.current_flow_betweenness_centrality(G)
nx.load_centrality(G)
nx.voterank_centrality(G)
```

## Shortest Paths

Unweighted and weighted shortest path algorithms:

```python
# Single-source
paths = nx.single_source_shortest_path(G, source)
lengths = nx.single_source_shortest_path_length(G, source)

# All-pairs
all_lengths = nx.all_pairs_shortest_path_length(G)

# Specific pair
path = nx.shortest_path(G, "A", "D", weight="weight")
length = nx.shortest_path_length(G, "A", "D", weight="weight")

# Dijkstra, Bellman-Ford, A*, BFS
nx.dijkstra_path(G, source, target, weight="weight")
nx.bellman_ford_path(G, source, target, weight="weight")
nx.astar_path(G, source, target, heuristic=h, weight="weight")
nx.bidirectional_dijkstra(G, source, target)
```

## Community Detection

Identify communities and clusters within networks:

```python
# Louvain (fast, modularity-based)
communities = nx.community.louvain_communities(G)

# Leiden
communities = nx.community.leiden_communities(G)

# Label propagation
communities = list(nx.community.label_propagation_communities(G))

# Girvan-Newman (hierarchical, based on betweenness)
communities = list(nx.community.girvan_newman(G, k=3))

# K-clique
communities = list(nx.community.k_clique_communities(G, k=3))

# Modularity measurement
q = nx.community.modularity(G, partition)
```

## Flow and Connectivity

Maximum flow, minimum cut, and connectivity algorithms:

```python
# Max flow
flow_value = nx.maximum_flow_value(G, "s", "t", capacity="capacity")
flow_dict = nx.maximum_flow(G, "s", "t", capacity="capacity")

# Min cut
cut_value, partition = nx.minimum_cut(G, "s", "t", capacity="capacity")

# Connectivity
k_node = nx.node_connectivity(G)
k_edge = nx.edge_connectivity(G)

# Connected components
components = list(nx.connected_components(G))
is_connected = nx.is_connected(G)
largest_cc = max(nx.connected_components(G), key=len)

# Strong components (directed graphs)
sccs = list(nx.strongly_connected_components(DG))
```

## Graph Traversal

```python
# BFS
bfs_nodes = list(nx.bfs_tree(G, source))
bfs_edges = list(nx.bfs_edges(G, source))

# DFS
dfs_nodes = list(nx.dfs_tree(G, source))
dfs_edges = list(nx.dfs_edges(G, source))
```

## Directed Acyclic Graphs (DAG)

```python
nx.is_directed_acyclic_graph(DG)
topo_order = list(nx.topological_sort(DG))
all_topo = list(nx.all_topological_sorts(DG))
ancestors = nx.ancestors(DG, node)
descendants = nx.descendants(DG, node)
longest = nx.dag_longest_path(DAG)
length = nx.dag_longest_path_length(DAG)
transitive = nx.transitive_closure(DAG)
reduced = nx.transitive_reduction(DAG)
```

## Bipartite Graphs

```python
is_bipartite = nx.is_bipartite(G)
top_nodes = nx.bipartite.sets(G)[0]
projection = nx.bipartite.projected_graph(G, top_nodes)
matching = nx.bipartite.maximum_matching(G)
```

## Clustering and Triangles

```python
clustering = nx.clustering(G)
avg_clustering = nx.average_clustering(G)
transitivity = nx.transitivity(G)
triangles = nx.triangles(G)
```

## Matching

```python
matching = nx.max_weight_matching(G, maxcardinality=True)
nx.is_matching(G, matching)
nx.is_perfect_matching(G, matching)
```

## Isomorphism

```python
nx.is_isomorphic(G1, G2)
nm = nx.algorithms.isomorphism.GraphMatcher(G1, G2)
if nm.is_isomorphic():
    mapping = nm.mapping
```

## Cycles

```python
basis = nx.cycle_basis(G)
cycles = list(nx.simple_cycles(DG))
girth = nx.girth(G)
chordless = list(nx.chordless_cycles(G))
```

## Planarity

```python
is_planar = nx.check_planarity(G)
nx.planar_embedding(G)
```

## Link Analysis

```python
pr = nx.pagerank(G, alpha=0.85)
hits_hubs, hits_authority = nx.hits(G)
```

## Link Prediction

```python
nx.common_neighbor_centrality(G)
nx.resource_allocation_index(G)
nx.adamic_adar_index(G)
nx.preferential_attachment(G)
nx.jaccard_coefficient(G)
```

## Approximations

```python
nx.approximation.travelling_salesman_problem(G, weight="weight")
nx.approximation.vertex_cover(G)
nx.approximation.dominating_set(G)
nx.approximation.treewidth(G)
nx.approximation.clique.max_clique(G)
```

## Distance Measures

```python
diameter = nx.diameter(G)
radius = nx.radius(G)
center = nx.center(G)
periphery = nx.periphery(G)
eccentricity = nx.eccentricity(G)
barycenter = nx.barycenter(G, weight="weight")
```

## Eulerian Graphs

```python
nx.is_eulerian(G)
circuit = list(nx.eulerian_circuit(G))
eulerized = nx.eulerize(G)
```

## Assortativity

```python
corr = nx.degree_assortativity_coefficient(G)
avg = nx.average_neighbor_degree(G)
```

## Rich Club

```python
coefficients = nx.rich_club_coefficient(G, normalized=True)
```

## Structural Holes and Constraint

```python
constraint = nx.structural_constraint(G)
effective_size = nx.effective_size(G)
```

## Tree Algorithms

```python
nx.is_tree(G)
spanning_tree = nx.minimum_spanning_tree(G, weight="weight")
nx.number_of_spanning_trees(G)
```

## Clustering Coefficient by Node Type

```python
generalized = nx.generalized_degree(G)
square_clust = nx.square_clustering(G)
```
