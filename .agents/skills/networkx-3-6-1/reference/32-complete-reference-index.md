# Complete Reference Index

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
