# Graph Generators

NetworkX provides extensive graph generation capabilities organized into categories.

## Classic Graphs

Basic graph structures used throughout graph theory:

```python
nx.empty_graph(n)                          # n isolated nodes, no edges
nx.null_graph()                            # no nodes, no edges
nx.trivial_graph()                         # single node, no edges
nx.complete_graph(n)                       # K_n — all pairs connected
nx.complete_multipartite_graph(*sizes)     # complete multipartite
nx.path_graph(n)                           # P_n — linear chain
nx.cycle_graph(n)                          # C_n — ring
nx.star_graph(n)                           # one center, n leaves
nx.barbell_graph(m1, m2)                   # two K_m1 connected by P_m2
nx.lollipop_graph(m, n)                    # K_m connected to P_n
nx.tadpole_graph(m, n)                     # C_m connected to P_n
nx.wheel_graph(n)                          # center connected to C_n
nx.circulant_graph(n, offsets)            # circulant graph
nx.circular_ladder_graph(n)               # prism graph
nx.ladder_graph(n)                         # P_n x P_2
nx.turan_graph(n, r)                       # Turan graph
nx.balanced_tree(r, h)                     # balanced r-ary tree of height h
nx.full_rary_tree(r, n)                    # full r-ary tree with n nodes
nx.binomial_tree(n)                        # binomial tree of order n
```

## Named Small Graphs

Famous graphs from graph theory literature:

```python
nx.petersen_graph()
nx.tutte_graph()
nx.sedgewick_maze_graph()
nx.tetrahedral_graph()
nx.dodecahedral_graph()
nx.icoshahedron_graph()
nx.hexahedron_graph()
nx.okamoto_ashikawa_graph()
nx.mcgregor_maidenhead_graph()
nx.flower_snark(k)
nx.lcf_graph(n, shift_list, repeats)
```

## Random Graphs

Probabilistic graph models:

```python
# Erdos-Renyi (G(n, p))
G = nx.erdos_renyi_graph(n, p)

# G(n, m) — random graph with n nodes and m edges
G = nx.gnm_random_graph(n, m)

# Barabasi-Albert (preferential attachment)
G = nx.barabasi_albert_graph(n, m)

# Configuration model (given degree sequence)
G = nx.configuration_model(deg_sequence)

# Watts-Strogatz (small-world)
G = nx.watts_strogatz_graph(n, k, p)

# Random regular graph
G = nx.random_regular_graph(d, n)

# Directed random graphs
G = nx.directed_erdos_renyi_graph(n, p)
G = nx.random_k_out_graph(n, k, creation_type="pair")
```

## Lattice and Grid Graphs

Regular grid structures:

```python
nx.grid_2d_graph(m, n)                    # 2D grid m x n
nx.grid_graph(dim)                         # n-dimensional grid
nx.triangular_lattice_graph(m, n)         # triangular tiling
nx.hexagonal_lattice_graph(m, n)          # hexagonal tiling
nx.hypercube_graph(n)                     # n-dimensional hypercube
```

## Expander Graphs

Explicit constructions of expander graphs:

```python
nx.margulis_gabber_galil_graph(n)
nx.chordal_cycle_graph(p)
nx.paley_graph(p)
nx.random_regular_expander_graph(n, d)
nx.is_regular_expander(G, epsilon)
```

## Social Networks

Classic sociological network datasets:

```python
nx.davis_southern_women_graph()
nx.karate_club_graph()
nx.flights_graph()
nx.les_miserables_graph()
nx.davis_racquetball_graph()
nx.edges_of_triangle_with_2_paths_of_length_n(n)
```

## Community Graphs

Graphs with known community structure for testing:

```python
nx.random_partition_graph(cluster_sizes, p_in, p_out)
nx.connected_caveman_graph(L, k)          # L cliques of size k
nx.caveman_graph(L, k)                    # disconnected L cliques of size k
nx.gaussian_random_partition_graph(...)
nx.power_law_cluster_graph(m, n)
```

## Trees

```python
nx.random_tree(n, seed)
nx.balanced_tree(r, h)
nx.full_rary_tree(r, n)
nx.preferential_attachment_tree(n)
```

## Geometric Graphs

Graphs based on geometric proximity:

```python
nx.random_geometric_graph(n, radius)
nx.navigable_small_world_graph(dims, p=2)
nx.geographical_threshold_graph(n, beta)
nx.soft_random_geometric_graph(n, radius)
```

## Directed Graph Generators

```python
nx.random_digraph(n, p)
nx.directed_configuration_model(in_deg, out_deg)
nx.scale_free_graph(n)
nx.directed_erdos_renyi_graph(n, p)
```

## Degree Sequence Graphs

Generate graphs matching a specific degree sequence:

```python
nx.havel_hakimi_graph(sequence)
nx.configuration_model(sequence)
nx.directed_configuration_model(in_seq, out_seq)
nx.random_degree_sequence_graph(sequence)
```

## Atlas

The graph atlas contains all non-isomorphic graphs with up to 7 nodes:

```python
G = nx.graph_atlas(i)        # i-th graph from the atlas
all_graphs = nx.graph_atlas_g()  # list of all atlas graphs
```
