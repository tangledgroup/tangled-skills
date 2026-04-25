---
name: networkx-3-6-1
description: A comprehensive toolkit for NetworkX 3.6.1, the Python package for creating, manipulating, and studying complex networks. Use when building graph analysis applications, implementing network algorithms, generating random or classic graphs, computing centrality measures, finding shortest paths, detecting communities, analyzing bipartite networks, drawing visualizations, or reading/writing graphs in various formats.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.0.0"
tags:
  - graph-theory
  - network-analysis
  - complex-networks
  - algorithms
  - data-science
category: data-science
external_references:
  - https://networkx.org/documentation/stable/reference/index.html
  - http://conference.scipy.org.s3-website-us-east-1.amazonaws.com/proceedings/scipy2008/paper_2/full_text.pdf
  - https://discord.com/invite/vur45CbwMz
  - https://github.com/networkx/networkx
  - https://github.com/networkx/networkx/discussions
  - https://groups.google.com/forum/#!forum/networkx-discuss
  - https://networkx.org/documentation/stable/
  - https://networkx.org/documentation/stable/reference/
  - https://networkx.org/documentation/stable/tutorial.html
  - https://github.com/networkx/networkx/tree/networkx-3.6.1
  - https://networkx.org/en/
---

# NetworkX 3.6.1

## Overview

NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks. It provides tools for analyzing social, biological, and infrastructure networks, along with a standard programming interface and graph implementation suitable for many applications.

With NetworkX you can:
- Load and store networks in standard and nonstandard data formats
- Generate random and classic network models
- Analyze network structure using advanced algorithms
- Build network models and design new algorithms
- Draw and visualize networks
- Interface with numerical algorithms and code written in C, C++, and FORTRAN

## When to Use

Use this skill when:
- **Building graph analysis applications** - Social networks, biological pathways, infrastructure systems
- **Implementing network algorithms** - Shortest paths, centrality measures, community detection, flow optimization, DAG scheduling, matching, isomorphism
- **Generating test networks** - Random graphs (Erdős-Rényi, Barabási-Albert), classic graphs (Petersen, grid), geometric graphs, social models
- **Analyzing network structure** - Connectivity, clustering, k-core decomposition, cycles, bridges, articulation points, planarity
- **Working with graph data** - Import/export in 15+ formats (GraphML, GEXF, GML, JSON, edge lists, adjacency matrices, Pajek, LEDA, DOT, Matrix Market)
- **Converting between representations** - Graph ↔ numpy arrays, scipy sparse matrices, pandas DataFrames, dict of dicts/lists
- **Visualizing networks** - Layout algorithms (15+), matplotlib integration, Graphviz, LaTeX/TikZ export, iplotx
- **Graph manipulation** - Union, intersection, difference, composition, graph products, relabeling, freezing, subgraph views
- **Optimization** - Max flow/min-cut, min-cost flow, maximum matching, graph coloring, minimum vertex cover
- **Research and education** - Prototyping graph algorithms, teaching graph theory concepts, spectral graph analysis

## Core Concepts

### Graph Types

NetworkX provides four main graph classes:

| Class | Type | Self-loops | Parallel edges |
|-------|------|------------|----------------|
| `Graph` | Undirected | Yes | No |
| `DiGraph` | Directed | Yes | No |
| `MultiGraph` | Undirected | Yes | Yes |
| `MultiDiGraph` | Directed | Yes | Yes |

```python
import networkx as nx

# Create different graph types
G = nx.Graph()              # Undirected simple graph
DG = nx.DiGraph()           # Directed simple graph
MG = nx.MultiGraph()        # Undirected multigraph
MDG = nx.MultiDiGraph()     # Directed multigraph
```

### Nodes and Edges

- **Nodes** can be any hashable Python object (strings, integers, tuples, custom objects)
- **Edges** connect pairs of nodes and can have arbitrary attributes
- **Attributes** are stored as key-value pairs on graphs, nodes, and edges

```python
G = nx.Graph()

# Add nodes with attributes
G.add_node("Alice", age=30, role="manager")
G.add_node("Bob", age=25, role="developer")

# Add edges with attributes
G.add_edge("Alice", "Bob", weight=0.8, since="2020")

# Access attributes
print(G.nodes["Alice"]["age"])      # 30
print(G.edges["Alice", "Bob"]["weight"])  # 0.8
```

### Graph Views

NetworkX uses views for efficient access to nodes, edges, and neighbors without copying data:

```python
G = nx.complete_graph(5)

# Views (not copies)
nodes = G.nodes()           # NodeView
edges = G.edges()           # EdgeView
neighbors = G.neighbors("node")  # NeighborView

# Subgraph views (lightweight, share data with original)
subview = nx.subgraph_view(G, filter_node=lambda n: n % 2 == 0)
```

## Installation

### Basic Installation

```bash
pip install networkx
```

### With Optional Dependencies

```bash
# Recommended for full functionality
pip install networkx[default]

# For all optional features (visualization, etc.)
pip install networkx[all]
```

### Development Installation

```bash
git clone https://github.com/networkx/networkx.git
cd networkx
pip install -e ".[default]"
```

## Usage Examples

### Creating Graphs

```python
import networkx as nx

# From scratch
G = nx.Graph()
G.add_node(1)
G.add_edge(1, 2, weight=2.5)
G.add_edges_from([(2, 3), (3, 4)])

# From edge list
edge_list = [(1, 2), (2, 3), (3, 4), (4, 1)]
G = nx.Graph(edge_list)

# Using generators
G = nx.erdos_renyi_graph(n=100, p=0.1)      # Random graph
G = nx.barabasi_albert_graph(n=100, m=3)    # Scale-free network
G = nx.watts_strogatz_graph(n=100, k=4, p=0.1)  # Small-world
G = nx.complete_graph(10)                   # Complete graph K₁₀
G = nx.cycle_graph(10)                      # Cycle graph C₁₀
G = nx.path_graph(10)                       # Path graph P₁₀
```

### Basic Analysis

```python
# Graph properties
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
print(f"Density: {nx.density(G)}")
print(f"Diameter: {nx.diameter(G)}")

# Degree statistics
degrees = [d for n, d in G.degree()]
print(f"Average degree: {sum(degrees) / len(degrees)}")
print(f"Max degree: {max(degrees)}")

# Connectivity
print(f"Is connected: {nx.is_connected(G)}")
print(f"Number of components: {nx.number_connected_components(G)}")
```

### Core Graph Operations

See [Core Concepts and Graph Classes](references/01-core-concepts.md) for graph types, views, attributes, set operations, and relabeling.

```python
import networkx as nx

# Graph creation from scratch
g = nx.Graph()
g.add_node(1)
g.add_edges_from([(1, 2), (2, 3)])

# Set operations
G1 | G2   # union
G1 & G2   # intersection
G1 - G2   # difference

# Relabeling
H = nx.relabel_nodes(G, {1: "a", 2: "b"})

# Frozen graphs
g.freeze()  # prevents modification
```

### Shortest Paths

See [Shortest Path Algorithms](references/02-shortest-paths.md) for comprehensive coverage.

```python
# Single shortest path
path = nx.shortest_path(G, source="A", target="D")
length = nx.shortest_path_length(G, "A", "D")

# Weighted shortest paths
path = nx.shortest_path(G, source="A", target="D", weight="weight")

# All pairs shortest paths
lengths = dict(nx.all_pairs_shortest_path_length(G))

# Single-source shortest paths
paths = nx.single_source_shortest_path(G, "A")
```

### Centrality Measures

See [Centrality and Importance](references/03-centrality.md) for detailed explanations.

```python
# Degree centrality (normalized degree)
dc = nx.degree_centrality(G)

# Betweenness centrality (how often node lies on shortest paths)
bc = nx.betweenness_centrality(G)

# Closeness centrality (average distance to all other nodes)
cc = nx.closeness_centrality(G)

# Eigenvector centrality (importance based on neighbors' importance)
ec = nx.eigenvector_centrality(G)

# PageRank (variant of eigenvector centrality)
pr = nx.pagerank(G)
```

### Community Detection

See [Community Detection](references/04-community-detection.md) for algorithms and examples.

```python
from networkx.algorithms import community

# Louvain method (modularity optimization)
louvain_communities = list(community.louvain_communities(G))

# Label propagation
lp_communities = list(community.label_propagation_communities(G))

# Girvan-Newman (edge betweenness-based)
gn_communities = list(community.girvan_newman(G))

# Check modularity (quality of partition)
mod = community.modularity(G, louvain_communities)
```

### Graph Drawing

See [Visualization](references/05-visualization.md) for layout algorithms and styling.

```python
import matplotlib.pyplot as plt

# Basic drawing
nx.draw(G, with_labels=True, node_color="lightblue", edge_color="gray")
plt.show()

# Different layouts
pos = nx.spring_layout(G)      # Force-directed layout
pos = nx.circular_layout(G)    # Circular arrangement
pos = nx.planar_layout(G)      # Planar embedding (if planar)
pos = nx.spectral_layout(G)    # Spectral embedding
pos = nx.kamada_kawai_layout(G)  # Kamada-Kawai force-directed

# Custom drawing
nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue")
nx.draw_networkx_edges(G, pos, edge_color="gray", width=2)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
plt.axis("off")
plt.show()
```

### Reading and Writing Graphs

See [File Formats](references/06-file-formats.md) for format-specific details.

```python
# GraphML (XML-based, preserves attributes)
nx.write_graphml(G, "graph.graphml")
G = nx.read_graphml("graph.graphml")

# GEXF (Gephi format)
nx.write_gexf(G, "graph.gexf")

# GML (Graph Description Language)
nx.write_gml(G, "graph.gml")

# Edge list
nx.write_edgelist(G, "graph.edgelist", delimiter=",")
G = nx.read_edgelist("graph.edgelist")

# Adjacency list
nx.write_adjlist(G, "graph.adjlist")

# JSON (with Python objects)
import json
data = nx.node_link_data(G)
with open("graph.json", "w") as f:
    json.dump(data, f)
G = nx.node_link_graph(json.load(open("graph.json")))
```

## Advanced Topics

- [Core Concepts and Graph Classes](references/01-core-concepts.md) - Graph types, nodes/edges, attributes, views, CoreViews, filters, set operations, products, relabeling, frozen graphs, non-edges
- [Shortest Path Algorithms](references/02-shortest-paths.md) - BFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson
- [Centrality and Importance](references/03-centrality.md) - Degree, betweenness, closeness, eigenvector, PageRank, and 15+ other measures
- [Community Detection](references/04-community-detection.md) - Louvain, label propagation, Girvan-Newman, spectral clustering
- [Visualization](references/05-visualization.md) - Layout algorithms, matplotlib integration, graphviz, styling options
- [File Formats](references/06-file-formats.md) - GraphML, GEXF, GML, JSON (node-link/tree/adjacency/cytoscape), edge lists, adjacency lists, Matrix Market, LEDA, Graph6/Sparse6, text export
- [Graph Generators](references/07-generators.md) - Random graphs, classic graphs, small-world, scale-free, expanders, atlas, geometric, community, degree sequence generators
- [Backends and Performance](references/08-backends.md) - GPU acceleration, parallel processing, third-party backends
- [Graph Class Methods and Operations](references/09-graph-operations.md) - add_node, remove_edge, subgraph, copy, reverse, freeze, CoreViews (AtlasView, AdjacencyView, FilterAtlas, etc.), filter functions, node/edge queries (all_neighbors, non_neighbors, common_neighbors), graph operators (union, intersection, product), attribute management
- [DAG Algorithms and Network Flow](references/10-dag-and-flow.md) - Topological sort, longest path, transitive closure, max flow (Edmonds-Karp, Boykov-Kolmogorov), min-cut, min-cost flow, Gomory-Hu tree
- [Connectivity and Components](references/11-connectivity-components.md) - Connected components, strongly connected, articulation points, bridges, edge/node connectivity, condensation
- [Clustering, Core Decomposition, Cycles](references/12-clustering-core-cycles.md) - Clustering coefficient, transitivity, k-core/k-shell/k-truss, clique percolation, cycle basis, recursive_simple_cycles, Eulerian paths
- [Isomorphism, Matching, Coloring](references/13-isomorphism-matching-coloring.md) - VF2++, subgraph isomorphism, maximum matching, bipartite matching, graph coloring, triadic census, reciprocity, assortativity, structural holes
- [Linear Algebra and Matrix Conversion](references/14-linalg-conversion.md) - Adjacency/Laplacian/Modularity/Attribute matrices, spectrum (5 types), algebraic connectivity, Fiedler vector, spectral bisection/ordering, to_networkx_graph(), numpy/scipy/pandas/dict conversion, graph relabeling
- [Graph Traversal and Trees](references/15-traversal-and-trees.md) - BFS, DFS, beam search, edge traversal, spanning trees, arborescences, Prufer sequences, nested tuples, junction trees
- [Link Prediction and Analysis](references/16-link-prediction-and-analysis.md) - Jaccard, Adamic-Adar, resource allocation, preferential attachment, HITS, PageRank google_matrix
- [Specialized Algorithms A](references/17-specialized-algorithms.md) - Dominating sets, dominance frontiers, edge covers, chordal graphs, D-separation (Bayesian networks), moral graphs, flow hierarchy, threshold graphs
- [Specialized Algorithms B](references/18-specialized-algorithms-2.md) - Simple paths, lowest common ancestor, closeness vitality, small-world metrics (σ/ω), s-metric, spanners, graph summarization, chromatic/Tutte polynomials, regular graphs, distance-regular graphs
- [Specialized Algorithms C](references/19-specialized-algorithms-3.md) - Efficiency measures, non-randomness, time-dependent centrality, tournaments, Voronoi cells, walk counting, chemical indices (Wiener/Schultz/Gutman), communicability, chain decomposition, node classification, approximation algorithms
- [Niche Algorithms](references/20-niche-algorithms.md) - Configuration, random utilities, Sparse6/Graph6 formats, text export, Graphviz DOT, broadcast trees, perfect graphs, planar embeddings, non-randomness measure
- [Graphical Degree Sequences](references/21-graphical-and-sequence.md) - Erdős–Gallai, Havel-Hakimi, graph type validation (simple/directed/multigraph/pseudograph)
- [Bipartite Networks](references/22-bipartite-networks.md) - Bipartite generators, projections (weighted/overlap/collaboration), matching (Hopcroft-Karp/Eppstein), biadjacency matrices, bipartite centrality/clustering, BiRANK ranking
- [Planarity and Embeddings](references/23-planarity-and-embeddings.md) - Planarity testing, PlanarEmbedding (cyclic edge order), combinatorial embedding to 2D positions
- [Graph Polynomials and Perfect Graphs](references/24-graph-polynomials-and-perfect.md) - Chromatic polynomial P(G,k), Tutte polynomial T(G;x,y), perfect graph property
- [Approximation Algorithms](references/25-approximation-algorithms.md) - NP-hard approximations: max clique, independent set, vertex cover, Steiner tree, TSP (Christofides/Asadpour/greedy/SA), max cut, densest subgraph, dominating set, treewidth
- [Graph Similarity and Edit Distance](references/26-similarity-and-edit-distance.md) - Graph edit distance (optimal paths), Panther similarity, SimRank random walk similarity, random path generation
- [Utils, Randomness, Configuration](references/27-utils-randomness-config.md) - Random permutations, power-law sequences, reservoir sampling, backend config, decorator utilities (argmap, nodes_or_number, np_random_state, py_random_state, open_file, creation), misc utilities (flatten, pairwise, groups, dict_to_numpy_array), UnionFind data structure
- [Complete Drawing and Layouts](references/28-drawing-layouts-complete.md) - All 46+ layout functions (spring, kamada-kawai, ARF, ForceAtlas2, BFS, multipartite, spiral), drawing primitives, LaTeX/TikZ export, Graphviz integration (pygraphviz + pydot), DOT read/write
- [Exceptions and Concepts](references/29-exceptions-and-concepts.md) - Full exception hierarchy (13 exceptions), frozen graphs, graph views vs copies, filter functions, fundamental graph concepts

## Algorithm Complexity Reference

### Shortest Paths

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| BFS shortest path | O(V + E) | Unweighted graphs, fewest hops |
| Dijkstra | O((V + E) log V) | Weighted graphs, non-negative weights |
| Bellman-Ford | O(VE) | Graphs with negative weights |
| Floyd-Warshall | O(V³) | All-pairs shortest paths, dense graphs |
| Johnson | O(V(V + E) log V) | All-pairs with negative weights |

### Centrality and Analysis

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| Degree centrality | O(V + E) | Direct neighbor count |
| Betweenness centrality | O(VE) | Node importance via shortest paths |
| Closeness centrality | O(V(V + E)) | Average distance to all nodes |
| Eigenvector centrality | O(k(V + E)) | k iterations, importance propagation |
| PageRank | O(kV) | k iterations, web-like networks |

### Connectivity and Components

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| Connected components (BFS/DFS) | O(V + E) | Undirected graph components |
| Strongly connected (Tarjan/Kosaraju) | O(V + E) | Directed graph SCCs |
| Articulation points | O(V + E) | Cut vertices in undirected graphs |
| Bridges | O(V + E) | Critical edges |
| Edge connectivity | O(V·max_flow) | Min edges to disconnect |
| Node connectivity | O(V·max_flow) | Min nodes to disconnect |

### DAG and Flow

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| Topological sort | O(V + E) | Linear ordering of DAG |
| Longest path in DAG | O(V + E) | Critical path method |
| Transitive closure | O(V·(V + E)) | Reachability matrix |
| Max flow (Edmonds-Karp) | O(VE²) | Network capacity optimization |
| Min-cost flow | O(VE × f) | Flow with cost constraints |

### Community and Clustering

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| Louvain community detection | O(kE) | k iterations, modularity optimization |
| Label propagation | O(kE) | k iterations, very fast |
| Girvan-Newman | O(VE²) | Hierarchical edge removal |
| Average clustering | O(V + E) | Local triangle density |
| Transitivity | O(V + E) | Global clustering coefficient |

### Matching and Isomorphism

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| Maximum matching | O(E√V) | Bipartite/weighted matching |
| Max weight clique | O(3^(V/3)) | NP-hard, exact for small graphs |
| Graph isomorphism (VF2++) | O(2^V) worst case | Practical: fast for most graphs |
| Subgraph isomorphism | O(2^V) | NP-complete |

### Core Decomposition and Cycles

| Algorithm | Time Complexity | Use Case |
|-----------|----------------|----------|
| k-core decomposition | O(V + E) | Peeling by minimum degree |
| Cycle basis | O(V²E) | Fundamental cycle set |
| Simple cycles (directed) | O(E·C) | C = number of simple cycles |
| Girth | O(VE) | Shortest cycle length |

Where V = number of nodes, E = number of edges, k = iterations, f = flow value.

## Complete Reference Index

### Core API
- Graph types: `Graph`, `DiGraph`, `MultiGraph`, `MultiDiGraph`
- Node/edge methods: `add_node()`, `remove_node()`, `add_edge()`, `remove_edge()`
- Views: `.nodes`, `.edges`, `.neighbors`, `.degree()`, `.subgraph()`
- Conversion: `.copy()`, `.reverse()`, `.to_directed()`, `.to_undirected()`, `.freeze()`
- Attributes: `set_node_attributes()`, `get_node_attributes()`, `set_edge_attributes()`, `get_edge_attributes()`
- Node queries: `all_neighbors()`, `non_neighbors()`, `common_neighbors()`
- Edge queries: `selfloop_edges()`, `number_of_selfloops()`, `nodes_with_selfloops()`, `non_edges()`
- Properties: `is_directed()`, `is_empty()`, `density()`, `is_weighted()`, `is_negatively_weighted()`, `is_path()`, `path_weight()`
- Subgraph views: `subgraph()`, `induced_subgraph()`, `edge_subgraph()`, `restricted_view()`, `subgraph_view()`
- CoreViews: `AtlasView`, `AdjacencyView`, `MultiAdjacencyView`, `UnionAtlas`, `UnionAdjacency`, `UnionMultiInner`, `UnionMultiAdjacency`, `FilterAtlas`, `FilterAdjacency`, `FilterMultiInner`
- Filters: `no_filter`, `hide_nodes`, `show_nodes`, `show_edges`, `hide_edges`, `show_multiedges`, `hide_multiedges`

### Algorithms by Category
- **Shortest paths**: BFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson, k-shortest paths
- **Centrality**: Degree, betweenness, closeness, eigenvector, PageRank, Katz, current flow, harmonic, load, subgraph, group centrality, dispersion, Laplacian, VoteRank
- **Community detection**: Louvain, label propagation, Girvan-Newman, spectral clustering, Walktrap, leading eigenvector, asyn_fluid, edge cluster
- **DAG algorithms**: Topological sort, all_topological_sorts, lexicographical topological sort, longest path, transitive closure, transitive_closure_dag, reduction, ancestors/descendants, antichains
- **Network flow**: Maximum flow (Edmonds-Karp, Boykov-Kolmogorov, Dinitz), min-cut, min-cost flow, capacity scaling, Gomory-Hu tree
- **Connectivity**: Connected components, strongly connected, weakly connected, biconnected components, articulation points, bridges, edge/node connectivity
- **Clustering**: Local clustering coefficient, average clustering, transitivity, triangles, k-clique percolation, modularity matrix
- **Core decomposition**: k-core, k-shell, k-crust, k-truss, core number, onion layers
- **Cycles**: Cycle basis, find cycle, simple cycles (directed), chordless cycles, girth, Eulerian paths/circuits
- **Graph operations**: Union, intersection, difference, composition, disjoint union, cartesian/tensor/strong/lexicographic products, complement, contraction, batch operators (union_all, compose_all, intersection_all, disjoint_union_all)
- **Isomorphism**: VF2++, ISMAGS, subgraph isomorphism, tree isomorphism, graph hashing (Weisfeiler-Lehman)
- **Matching**: Maximum cardinality matching, maximum weight matching, bipartite matching, vertex cover, independent set
- **Coloring**: Greedy coloring with 7+ strategies, equitable coloring
- **Bipartite**: `is_bipartite`, bipartite sets/color, projections, bipartite centrality
- **Link prediction**: Jaccard coefficient, Adamic-Adar index, cn_soundarajan_hopcroft, preferential attachment, resource allocation, RA index, common neighbor centrality
- **Trees**: Spanning trees, branchings, arborescences (max/min), Prufer sequences, nested tuples, junction trees
- **Planarity**: `is_planar()`, `check_planarity()`, PlanarEmbedding, planar drawing
- **Cliques**: `find_cliques()`, `find_cliques_recursive()`, max weight clique, enumerate all cliques, clique number
- **Distance measures**: Eccentricity, center, periphery, radius, diameter, resistance distance, effective graph resistance, harmonic diameter, Kemeny constant, barycenter
- **Simple paths**: All simple paths, all simple edge paths, shortest simple paths
- **Structural holes**: Constraint, effective size, local constraint
- **Triads**: Triadic census, triad types (300, 030T, etc.), all triads
- **Reciprocity**: Overall reciprocity, per-node reciprocity
- **Assortativity**: Degree assortativity, attribute assortativity, weighted degree assortativity
- **Rich club**: Rich club coefficient (normalized/unnormalized)
- **Swap operations**: Double edge swap, connected double edge swap, directed edge swap
- **Minors**: Contracted edges/nodes, quotient graph, identified nodes, equivalence classes
- **Graph hashing**: Weisfeiler-Lehman graph hash, subgraph hashes
- **Graph edit distance**: Optimal edit paths, optimized GED, random path generation
- **Graphical degree sequences**: Erdős–Gallai, Havel-Hakimi, is_graphical, is_digraphical, is_multigraphical, is_pseudographical, sequence validation
- **Graph cuts**: Conductance, volume, edge/node expansion, cut_size, boundary_expansion, mixing_expansion, normalized_cut_size
- **Matching (bipartite)**: Maximum matching, minimum vertex cover, maximum independent set, minimum edge cover
- **Bridges/boundaries**: Bridges, local bridges, node boundary, edge boundary
- **Coloring**: Graph coloring with greedy strategies
- **Eulerian**: Eulerian circuit, Eulerian path, eulerize()
- **Percolation centrality**
- **Trophic levels** (directed networks)
- **Graph generators**: 50+ generators including classic, random, geometric, social, lattice, tree, duplication-divergence
- **Matrix representations**: Adjacency, Laplacian, normalized Laplacian, directed Laplacian, combinatorial Laplacian, incidence, Bethe Hessian, modularity (directed), attribute matrices (dense/sparse)
- **Spectral properties**: Adjacency/Laplacian/Bethe/Modularity spectrum, algebraic connectivity, Fiedler vector, spectral bisection/ordering
- **Relabeling**: `relabel_nodes()`, `convert_node_labels_to_integers()`
- **Conversion**: to_networkx_graph(), to/from numpy arrays, scipy sparse, pandas DataFrames, dict of dicts/lists, dict of weighted dicts, edgelists
- **Backends**: cuGraph (GPU), nx-parallel (multi-core CPU), GraphBLAS, Rustworkx
- **Traversal**: BFS, DFS, beam search, edge-based traversal, labeled edges (tree/back/forward/cross), predecessors/successors/layers
- **Link analysis**: HITS (hubs/authorities), google_matrix, personalized PageRank
- **Domination**: Dominating sets, dominance frontiers, immediate dominators, edge covers, maximal independent set
- **Chordal graphs**: is_chordal, chordal_graph_cliques, treewidth, complete_to_chordal, induced nodes
- **Bayesian networks**: D-separation, minimal d-separators, moral graph, flow hierarchy
- **Polynomials**: Chromatic polynomial, Tutte polynomial
- **Perfect graphs**: is_perfect_graph (chromatic number = clique number for all induced subgraphs)
- **Lowest common ancestor**: LCA, all_pairs_lca, tree_all_pairs_lca
- **Small-world metrics**: sigma (σ), omega (ω), lattice/random reference graphs
- **S-metric**: Network robustness measure
- **Spanners**: t-spanner (distance-preserving subgraph)
- **Summarization**: dedensify, snap_aggregation
- **Efficiency measures**: local/global/individual efficiency
- **Non-randomness**: Non-randomness measure
- **Time-dependent**: CD index (communicability diffusion)
- **Tournaments**: is_tournament, hamiltonian_path, score_sequence, random_tournament, tournament_matrix
- **Voronoi cells**: Distance-based node partitioning
- **Walks**: number_of_walks (walk counting via matrix powers)
- **Chemical indices**: Wiener, Schultz, Gutman, hyper-Wiener indices
- **Communicability**: communicability, communicability_exp (graph eigenvalue-based)
- **Chain decomposition**: Cycle/path decomposition
- **Node classification**: harmonic_function, local_and_global_consistency (semi-supervised learning)
- **Approximation**: max_clique, clique_removal, large_clique_size, maximum_independent_set
- **Asteroidal triples**: find_asteroidal_triple, is_at_free
- **Distance-regular**: is_distance_regular, intersection_array, global_parameters
- **Regular graphs**: is_k_regular, k_factor
- **Threshold graphs**: is_threshold_graph, find_threshold_graph
- **Configuration**: backend_priority (algos/generators/classes), fallback_to_nx, cache_converted_graphs, drawing.element_limit, drawing.np_float_weighted
- **Randomness**: random_permutation, arbitrary_element, random_sample, powerlaw_sequence, reservoir sampling, random_node, random_edge
- **Decorators**: @argmap, @nodes_or_number, @not_implemented_for, @np_random_state, @py_random_state, @open_file, @creation
- **Misc utilities**: flatten, make_list_of_ints, dict_to_numpy_array, pairwise, groups, create_py_random_state, create_random_state
- **UnionFind**: union(), find(), same_set(), size(), equivalence classes
- **File formats**: GraphML, GEXF, GML, JSON (node-link/tree/adjacency/cytoscape), edge lists, adjacency lists, multiline adjacency lists, Pajek, LEDA, DOT/Graphviz (pygraphviz + pydot), Matrix Market, CSV via pandas, Graph6, Sparse6, text export

### File Formats
- GraphML, GEXF, GML, JSON (node-link/tree/adjacency/cytoscape), edge lists, adjacency lists, multiline adjacency lists, Pajek, LEDA, DOT/Graphviz, Matrix Market, CSV via pandas, Graph6, Sparse6, text export

### Visualization
- Matplotlib: `draw()`, `draw_networkx_*`, layouts (spring, circular, spectral, Kamada-Kawai, shell, planar, BFS, spiral, ARF, ForceAtlas2, multipartite)
- Graphviz: pygraphviz and pydot integration
- LaTeX/TikZ export via `to_latex()`
- iplotx for interactive web visualization

### Exceptions
`NetworkXException`, `NetworkXError`, `NetworkXAlgorithmError`, `NetworkXNoPath`, `NetworkXNoCycle`, `NetworkXUnfeasible`, `NetworkXNotImplemented`, `NodeNotFound`, `AmbiguousSolution`, `ExceededMaxIterations`, `PowerIterationFailedConvergence`, `HasACycle`, `NetworkXPointlessConcept`

