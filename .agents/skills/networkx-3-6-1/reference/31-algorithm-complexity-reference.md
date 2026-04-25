# Algorithm Complexity Reference

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
