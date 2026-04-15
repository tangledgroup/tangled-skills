# Graph Generators

NetworkX provides extensive graph generators for creating classic graphs, random networks, and specialized topologies.

## Classic Graphs

Basic graph structures used as building blocks or test cases.

```python
import networkx as nx

# Complete graph (every node connected to every other)
G = nx.complete_graph(6)           # K₆ - 6 nodes
# All pairs have edges, n*(n-1)/2 edges total

# Cycle graph
G = nx.cycle_graph(10)             # C₁₀ - 10 nodes in a cycle

# Path graph
G = nx.path_graph(10)              # P₁₀ - 10 nodes in a line

# Star graph
G = nx.star_graph(10)              # Center node + 10 leaves

# Wheel graph
G = nx.wheel_graph(10)             # Center connected to 9-node cycle

# Ladder graph
G = nx.ladder_graph(6)             # Two paths of 6 with rungs

# Circular ladder (prism graph)
G = nx.circular_ladder_graph(6)

# Barbell graph (two complete graphs connected by path)
G = nx.barbell_graph(5, 3)         # Two K₅ connected by 3-node path

# Binomial tree
G = nx.binomial_tree(4)            # Depth-4 binomial tree

# Balanced tree
G = nx.balanced_tree(2, 3)         # 2-ary tree of depth 3

# Full k-ary tree
G = nx.full_rary_tree(2, 9)        # Complete binary tree with 9 nodes

# Null graph (no nodes)
G = nx.null_graph()

# Trivial graph (single node)
G = nx.trivial_graph()

# Empty graph (n nodes, no edges)
G = nx.empty_graph(10)

# Petersen graph (famous small graph)
G = nx.petersen_graph()

# Dorogovtsev-Goltsev-Mendes graph
G = nx.dorogovtsev_goltsev_mendes_graph(5)

# House graph
G = nx.house_graph()

# Complete multipartite graph
G = nx.complete_multipartite_graph(2, 3, 4)  # K₂,₃,₄

# Turan graph
G = nx.turan_graph(10, 3)          # 10 nodes, no K₄

# Circulant graph
G = nx.circulant_graph(10, [2, 5])

# Kneser graph
G = kneser_graph(5, 2)             # K(5,2) - intersection of 2-element subsets
```

## Geometric Graphs

Graphs based on geometric properties and spatial arrangements.

```python
# Grid graphs
G = nx.grid_2d_graph(5, 5)         # 5x5 2D grid
G = nx.grid_graph([5, 5, 5])       # 5x5x5 3D grid

# Hexagonal lattice
G = nx.hexagonal_lattice_graph(5, 5)

# Triangular lattice
G = nx.triangular_lattice_graph(5, 5)

# Hypercube graph
G = nx.hypercube_graph(4)          # 4-dimensional hypercube (16 nodes)

# Random geometric graph
G = nx.random_geometric_graph(50, radius=0.1)  # 50 nodes, connection radius 0.1

# Geographical threshold graph
G = nx.geographical_threshold_graph(50, 0.1)

# Waxman graph (network topology model)
G = nx.waxman_graph(50, 1.0, 0.5, pos=None)

# Navigable small world
G = nx.navigable_small_world_graph(10, alpha=2, L=[10, 10])

# Soft random geometric graph
G = nx.soft_random_geometric_graph(50, 0.1)
```

## Random Graphs

### Erdős-Rényi Models

```python
# G(n, p) - each edge exists with probability p
G = nx.erdos_renyi_graph(100, 0.1)
G = nx.gnp_random_graph(100, 0.1)     # Same as above
G = nx.binomial_graph(100, 0.1)       # Also same

# Fast version for large graphs
G = nx.fast_gnp_random_graph(1000, 0.01)

# G(n, m) - graph with n nodes and m edges
G = nx.gnm_random_graph(100, 200)     # 100 nodes, 200 edges
G = nx.dense_gnm_random_graph(100, 200)  # Faster for dense graphs
```

### Small-World Networks

```python
# Watts-Strogatz small-world model
G = nx.watts_strogatz_graph(100, 4, 0.1)  # 100 nodes, k=4, rewiring p=0.1

# Connected Watts-Strogatz (guaranteed connected)
G = nx.connected_watts_strogatz_graph(100, 4, 0.1)

# Newman-Watts-Strogatz (adds edges instead of rewiring)
G = nx.newman_watts_strogatz_graph(100, 2, 0.1)
```

### Scale-Free Networks

```python
# Barabási-Albert preferential attachment
G = nx.barabasi_albert_graph(100, 3)     # 100 nodes, m=3 edges per new node

# Dual Barabási-Albert
G = nx.dual_barabasi_albert_graph(10, 2)

# Extended Barabási-Albert (with initial random graph)
G = nx.extended_barabasi_albert_graph(100, 3, 1)

# Powerlaw cluster graph
G = nx.powerlaw_cluster_graph(100, 3, 0.5)
```

### Random Regular Graphs

```python
# Random k-regular graph (every node has degree k)
G = nx.random_regular_graph(3, 50)       # 3-regular graph with 50 nodes

# Must have n*k even (handshaking lemma)
```

### Other Random Models

```python
# Random tree
G = nx.random_tree(100)

# Random powerlaw tree
G = nx.random_powerlaw_tree(100)

# Random lobster (tree with paths attached)
G = nx.random_lobster(100, 0.3, 0.7)

# Random shell graph
nlist = [50, 50]  # Two shells of 50 nodes each
parray = [0.1, 0.02, 0.02]  # Connection probabilities
G = nx.random_shell_graph(nlist, parray)

# Random kernel graph
def kernel(x, y): return x * y
G = nx.random_kernel_graph(100, kernel)

# Configuration model (from degree sequence)
degree_sequence = [3, 3, 3, 3, 2, 2, 2, 2]
G = nx.configuration_model(degree_sequence)

# Directed configuration model
in_degrees = [2, 2, 1, 1]
out_degrees = [1, 1, 2, 2]
G = nx.directed_configuration_model(in_degrees, out_degrees)

# Havel-Hakimi algorithm (realizes degree sequence without self-loops/multi-edges)
G = nx.havel_hakimi_graph(degree_sequence)
```

## Directed Graphs

```python
# Gn, GnR, Gnc models (directed random graphs)
G = nx.gn_graph(10, 0.5)              # Each directed edge with probability p
G = nx.gnr_graph(10, 20)              # 10 nodes, 20 directed edges
G = nx.gnc_graph(10, 20)              # Connected directed graph

# Random k-out graph (each node has out-degree k)
G = nx.random_k_out_graph(10, 2)      # 10 nodes, each with 2 outgoing edges

# Scale-free directed graph
G = nx.scale_free_graph(100)
```

## Internet and AS Graphs

```python
# Random Internet AS (Autonomous System) graph
G = nx.random_internet_as_graph(100, 3, 1, 0.5, 0.2)
```

## Social Network Models

```python
# Various social network generators
from networkx.generators import social

# Dolphin social network (real data)
G = nx.dolphins()

# Florentine families (real historical data)
G = nx.florentine_families()

# Kentucky high school athletes
G = nx.karate_club_graph()

# Jazz musicians collaboration network
G = nx.jazz()

# American political books
G = nx.polbooks()

# Metro transit networks
G = nx.metro_petersburg()  # St. Petersburg metro
```

## Intersection Graphs

```python
# Random intersection graphs
G = nx.uniform_random_intersection_graph(100, 50, 0.1)
G = nx.k_random_intersection_graph(100, 50, 3)
G = nx.general_random_intersection_graph(100, 50, p_func)
```

## Line Graphs

```python
# Line graph (edges become nodes, adjacency preserved)
G = nx.path_graph(5)
L = nx.line_graph(G)  # L(G) has 4 nodes (the edges of G)

# Inverse line graph (if it exists)
G_original = nx.inverse_line_graph(L)
```

## Ego Networks

```python
# Ego network (node and its neighbors)
G = nx.erdos_renyi_graph(100, 0.1)
ego_G = nx.ego_graph(G, "node42", radius=2)  # Node and neighbors up to distance 2

# Number of nodes in ego network
n_ego = nx.number_of_edges(nx.ego_graph(G, "node42"))
```

## Duplication-Divergence Models

Models for biological network evolution.

```python
# Duplication-divergence graph
G = nx.duplication_divergence_graph(10, 0.5)  # 10 duplications, p=0.5 retention

# Partial duplication graph
G = nx.partial_duplication_graph(10, 0.5)
```

## Stochastic Graphs

```python
# From stochastic matrix (Markov chain)
import numpy as np
P = np.array([[0.7, 0.3], [0.2, 0.8]])  # Transition matrix
G = nx.stochastic_graph(P)
```

## Atlas

Small graph atlas (1334 graphs with up to 7 nodes).

```python
# Get all graphs in atlas
atlas = nx.graph_atlas_g()

# Find a specific graph by index
G = atlas[273]  # Petersen graph is at index 273 (actually needs 10 nodes)

# Search for graphs with properties
for i, G in enumerate(atlas):
    if nx.number_of_nodes(G) == 6 and nx.is_complete_graph(G):
        print(f"Complete graph K₆ at index {i}")
```

## Chordal Graphs

```python
# Generate chordal graphs (every cycle > 3 has a chord)
G = nx.chordal_graph(10)
```

## Expanders

```python
# Margulis-Gabber-Galil expander graph
G = nx.margulis_gabber_galil_graph(4)

# Chordal cycle expander
G = nx.chordal_cycle_graph(10)

# Paley graph (quadratic residue graph)
G = nx.paley_graph(17)  # Must be prime ≡ 1 (mod 4)

# Random regular expander
G = nx.random_regular_expander_graph(4, 100)  # 4-regular, 100 nodes

# Check if graph is expander
is_expander = nx.is_regular_expander(G)
```

## Specialized Graphs

### Small Named Graphs

```python
# Platonic solids
G = nx.tetrahedral_graph()    # 4 nodes (K₄)
G = nx.octahedral_graph()     # 6 nodes
G = nx.icosahedral_graph()    # 12 nodes
G = nx.dodecahedral_graph()   # 20 nodes

# Famous graphs
G = nx.cubical_graph()        # Cube (8 nodes)
G = nx.heawood_graph()        # 14 nodes, girth 6
G = nx.hoffman_singleton_graph()  # 50 nodes, strongly regular
G = nx.desargues_graph()      # 20 nodes
G = nx.moebius_kantor_graph() # 16 nodes
G = nx.frucht_graph()         # 12 nodes, smallest cubic asymmetric
G = nx.sedgewick_maze_graph() # 24 nodes
G = nx.tutte_graph()          # 46 nodes, smallest snark

# Other named graphs
G = nx.bull_graph()           # 5 nodes
G = nx.diamond_graph()        # 4 nodes
G = nx.chvatal_graph()        # 12 nodes
G = nx.krackhardt_kite_graph()  # 10 nodes
G = nx.pappus_graph()         # 18 nodes

# Generalized Petersen graphs
G = nx.generalized_petersen_graph(10, 2)  # P(10, 2)
```

### Truncated Polyhedra

```python
G = nx.truncated_tetrahedron_graph()
G = nx.truncated_cube_graph()
```

### LCF Graphs

List of Cordial Form notation for cubic graphs.

```python
# From LCF notation
G = nx.LCF_graph([3, -3], 4)  # Cube graph
```

## Generator Parameters

Most generators accept these common parameters:

```python
# create_using: Specify graph type
G = nx.erdos_renyi_graph(100, 0.1, create_using=nx.DiGraph())
G = nx.complete_graph(10, create_using=nx.MultiGraph())

# seed: Random seed for reproducibility
G1 = nx.erdos_renyi_graph(100, 0.1, seed=42)
G2 = nx.erdos_renyi_graph(100, 0.1, seed=42)
assert G1 == G2  # Same graph

# name: Graph name (stored as attribute)
G = nx.complete_graph(5, name="K5")
print(G.graph['name'])  # "K5"
```

## Creating Custom Generators

```python
def my_custom_graph(n):
    """Create a custom graph with n nodes."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    # Add edges based on custom rule
    for i in range(n):
        for j in range(i + 1, n):
            if (i + j) % 2 == 0:  # Connect if sum is even
                G.add_edge(i, j)
    
    return G

# Usage
G = my_custom_graph(10)
```

## Generator Selection Guide

| Use Case | Recommended Generator |
|----------|----------------------|
| Test algorithms on known structure | Classic graphs (cycle, path, complete) |
| Random baseline | `erdos_renyi_graph` or `gnp_random_graph` |
| Social networks | `watts_strogatz_graph` or `barabasi_albert_graph` |
| Biological networks | `duplication_divergence_graph` |
| Spatial networks | `random_geometric_graph` or grid graphs |
| Scale-free networks | `barabasi_albert_graph` |
| Regular networks | `random_regular_graph` |
| Small test cases | `graph_atlas_g()` |
