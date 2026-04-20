# Linear Algebra, Matrix Conversion, and Graph Relabeling

NetworkX provides functions for converting between graph and matrix representations, computing spectral properties, and relabeling nodes.

## Matrix Representations

### Adjacency Matrix

```python
import networkx as nx
import numpy as np
from scipy import sparse

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Dense adjacency matrix
adj = nx.adjacency_matrix(G).toarray()
print(adj)

# With weights
G.add_edge(1, 2, weight=0.5)
weighted_adj = nx.weighted_adjacency_matrix(G, weight="weight").toarray()

# Convert to numpy array directly
np_adj = nx.to_numpy_array(G)
np_weighted = nx.to_numpy_array(G, weight="weight")

# With node ordering
np_ordered = nx.to_numpy_array(G, nodelist=[1, 2, 3])

# To scipy sparse matrix (memory efficient for large graphs)
sparse_adj = nx.adjacency_matrix(G)
print(type(sparse_adj))  # <class 'scipy.sparse._csr.csr_matrix'>

# To pandas DataFrame
import pandas as pd
pd_adj = nx.to_pandas_adjacency(G)
```

### Laplacian Matrix

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])

# Combinatorial Laplacian: L = D - A
laplacian = nx.laplacian_matrix(G).toarray()
print(laplacian)

# Normalized Laplacian: L_norm = I - D^(-1/2)AD^(-1/2)
norm_laplacian = nx.normalized_laplacian_matrix(G).toarray()

# Directed combinatorial Laplacian
DG = nx.DiGraph([(1, 2), (2, 3)])
directed_lap = nx.directed_combinatorial_laplacian_matrix(DG).toarray()
```

### Incidence Matrix

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Incidence matrix (nodes × edges)
incidence = nx.incidence_matrix(G).toarray()
print(incidence)
# Each column has +1 and -1 for the two endpoints of an edge
```

### Bethe Hessian Matrix

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Bethe Hessian matrix (for community detection)
d = 2.0  # Average degree parameter
bethe = nx.bethe_hessian_matrix(G, r=d).toarray()
print(bethe)
```

### Modularity Matrix

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Undirected modularity matrix
mod_matrix = nx.modularity_matrix(G)
print(mod_matrix.toarray())

# Directed modularity matrix
DG = nx.DiGraph([(1, 2), (2, 3)])
directed_mod = nx.directed_modularity_matrix(DG)
```

### Attribute Matrices

Matrices based on node/edge attributes.

```python
G = nx.Graph()
G.add_nodes_from([1, 2, 3], color=[1, 0, 0])
G.add_nodes_from([2, 3], size=[10, 20])
G.add_edge(1, 2, weight=0.5)

# Node attribute matrix (one column per unique attribute value)
attr_mat = nx.attr_matrix(G, nodelist=[1, 2, 3])
print(attr_mat)

# With edge attributes
edge_attr_mat = nx.attr_matrix(G, edges=[(1, 2)], edge_attr="weight")

# Sparse version (memory efficient)
sparse_attr = nx.attr_sparse_matrix(G, nodelist=[1, 2, 3])
```

## Matrix Conversions

### From Various Formats to NetworkX

```python
import numpy as np
import pandas as pd
from scipy import sparse
import networkx as nx

# From numpy array
np_matrix = np.array([[0, 1, 1], [1, 0, 0], [1, 0, 0]])
G = nx.from_numpy_array(np_matrix)

# With directed graph
DG = nx.from_numpy_array(np_matrix, create_using=nx.DiGraph)

# From weighted numpy array
weighted_matrix = np.array([[0, 1.5, 0.3], [1.5, 0, 0], [0.3, 0, 0]])
G_w = nx.from_numpy_array(weighted_matrix, edge_attr="weight")

# From scipy sparse matrix
sparse_mat = nx.adjacency_matrix(nx.path_graph(5))
G_sparse = nx.from_scipy_sparse_array(sparse_mat)

# From pandas DataFrame (adjacency)
pd_df = pd.DataFrame(np_matrix, index=[1, 2, 3], columns=[1, 2, 3])
G_pd = nx.from_pandas_adjacency(pd_df)

# From pandas edgelist
df = pd.DataFrame({
    'source': [1, 2, 3],
    'target': [2, 3, 1],
    'weight': [0.5, 1.0, 0.3]
})
G_edgelist = nx.from_pandas_edgelist(df, source='source', target='target', edge_attr='weight')

# From dict of dicts
dod = {1: {2: {"weight": 0.5}}, 2: {1: {"weight": 0.5}}}
G_dod = nx.from_dict_of_dicts(dod)

# From dict of lists
dol = {1: [2, 3], 2: [1, 3]}
G_dol = nx.from_dict_of_lists(dol)

# From edgelist
edges = [(1, 2), (2, 3)]
G_el = nx.from_edgelist(edges)

# Create from any Python object
G = nx.to_networkx_graph([(1, 2), (2, 3)])
G_from_dict = nx.to_networkx_graph({1: {2: {}, 3: {}}})
```

### To Various Formats

```python
G = nx.Graph()
G.add_edges_from([(1, 2, {"weight": 0.5}), (2, 3, {"weight": 1.0})])

# To numpy array
np_arr = nx.to_numpy_array(G)
np_weighted = nx.to_numpy_array(G, weight="weight")

# To scipy sparse
sparse_mat = nx.to_scipy_sparse_array(G)

# To pandas adjacency
pd_adj = nx.to_pandas_adjacency(G)

# To pandas edgelist
pd_edges = nx.to_pandas_edgelist(G)

# To dict of dicts
dod = nx.to_dict_of_dicts(G)
print(dod)  # {1: {2: {}}, 2: {1: {}, 3: {}}, 3: {2: {}}}

# To dict of lists
dol = nx.to_dict_of_lists(G)
print(dol)  # {1: [2], 2: [1, 3], 3: [2]}

# To edgelist
edges = list(nx.to_edgelist(G))
print(edges)  # [(1, 2, {}), (2, 3, {})]

# Write to Matrix Market format
from scipy import sparse
sparse_mat = nx.adjacency_matrix(G)
nx.write_matrix_market(sparse_mat, "graph.mtx")

# Read from Matrix Market
loaded_mat = nx.read_matrix_market("graph.mtx")
G_loaded = nx.from_scipy_sparse_array(loaded_mat)
```

## Spectral Properties

### Eigenvalue Spectrum

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4)])

# Adjacency spectrum
eigenvalues = nx.adjacency_spectrum(G)
print(eigenvalues)

# Laplacian spectrum
lap_spectrum = nx.laplacian_spectrum(G)
print(lap_spectrum)

# Normalized Laplacian spectrum
norm_spectrum = nx.normalized_laplacian_spectrum(G)

# Bethe Hessian spectrum
bethe_spectrum = nx.bethe_hessian_spectrum(G, r=2.0)

# Modularity spectrum
mod_spectrum = nx.modularity_spectrum(G)
```

### Algebraic Connectivity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (1, 4)])

# Algebraic connectivity (smallest non-zero Laplacian eigenvalue)
alg_conn = nx.algebraic_connectivity(G)
print(alg_conn)

# Fiedler vector (eigenvector corresponding to algebraic connectivity)
fiedler = nx.fiedler_vector(G)
print(fiedler)

# Spectral bisection (using Fiedler vector)
partition = nx.spectral_bisection(G, fiedler)
print(partition)  # Partition of nodes

# Spectral ordering (reorder nodes by Fiedler vector)
ordered = nx.spectral_ordering(G)
print(ordered)
```

### Visibility Graph

```python
# Convert time series to graph (for network analysis of signals)
time_series = [1, 3, 2, 5, 4, 6]
G_vis = nx.visibility_graph(time_series)
print(list(G_vis.edges()))

# Horizontal visibility
G_hvis = nx.horizontal_visibility_graph(time_series)
```

## Graph Relabeling

### Convert Node Labels to Integers

```python
G = nx.Graph()
G.add_edges_from([("Alice", "Bob"), ("Bob", "Charlie")])

# Convert all node labels to integers
G_int = nx.convert_node_labels_to_integers(G)
print(list(G_int.nodes()))  # [0, 1, 2]

# With starting index
G_start = nx.convert_node_labels_to_integers(G, first_label=10)
print(list(G_start.nodes()))  # [10, 11, 12]

# With ordering (sorted by degree)
G_sorted = nx.convert_node_labels_to_integers(
    G,
    ordering="increasing_degree",
    first_label=0
)

# Other ordering options:
# "decreasing_degree" - highest degree first
# "increasing_label" - alphabetical/numerical order
# "decreasing_label" - reverse alphabetical/numerical order
```

### Relabel Nodes with Custom Mapping

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3)])

# Relabel with custom mapping
mapping = {1: "A", 2: "B", 3: "C"}
G_relabel = nx.relabel_nodes(G, mapping)
print(list(G_relabel.edges()))  # [('A', 'B'), ('B', 'C')]

# Using a function
G_func = nx.relabel_nodes(G, lambda x: f"node_{x}")
print(list(G_func.edges()))  # [('node_1', 'node_2'), ...]

# Partial relabeling (only specified nodes)
partial_mapping = {1: "X"}
G_partial = nx.relabel_nodes(G, partial_mapping)
# Node 2 and 3 keep their original labels
```

### GEXF Relabeling

```python
# When reading GEXF files, node IDs may need relabeling
G = nx.read_gexf("graph.gexf", node_type=int)
# Or relabel after loading
G = nx.relabel_nodes(G, {old_id: new_id for old_id, new_id in enumerate(G.nodes())})
```

## Practical Applications

### Adjacency-Based Clustering

```python
import numpy as np
from sklearn.cluster import SpectralClustering

G = nx.Graph()
G.add_edges_from([
    (1, 2), (1, 3), (2, 3),  # Cluster 1
    (4, 5), (4, 6), (5, 6),  # Cluster 2
    (1, 4),                   # Bridge
])

# Get adjacency matrix
adj = nx.to_numpy_array(G)

# Spectral clustering using Laplacian
lap = nx.laplacian_matrix(G).toarray()
sc = SpectralClustering(n_clusters=2, affinity='precomputed')
labels = sc.fit_predict(-adj)  # Negative because similar = connected
print(labels)
```

### Fiedler Vector for Graph Partitioning

```python
G = nx.Graph()
# Create a graph with two dense clusters connected by a bridge
G.add_edges_from([
    (1, 2), (1, 3), (2, 3),  # Cluster A
    (4, 5), (4, 6), (5, 6),  # Cluster B
    (3, 4),                   # Bridge
])

# Compute Fiedler vector
fiedler = nx.fiedler_vector(G)
print(fiedler)

# Positive values in one cluster, negative in the other
positive = [n for n, v in zip(G.nodes(), fiedler) if v > 0]
negative = [n for n, v in zip(G.nodes(), fiedler) if v <= 0]
print(f"Cluster A: {positive}")
print(f"Cluster B: {negative}")
```

### Matrix-Based Graph Analysis

```python
# Compute path counts via matrix powers
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (1, 3)])

adj = nx.to_numpy_array(G)
two_step_paths = np.linalg.matrix_power(adj, 2)
print(two_step_paths)
# two_step_paths[i][j] = number of paths of length 2 between i and j

# PageRank via power iteration
n = G.number_of_nodes()
A = nx.to_numpy_array(G).T
damping = 0.85
D_inv = np.diag(1.0 / A.sum(axis=1))
M = damping * D_inv @ A + (1 - damping) / n * np.ones((n, n))

# Power iteration
v = np.ones(n) / n
for _ in range(100):
    v = M @ v
    v /= v.sum()
print(v)
```

## Additional Matrix Functions

```python
# Convert to numpy edgelist (source, target, weight)
np_edgelist = nx.to_numpy_edgelist(G)

# Read/write attribute matrices
attr_mat = nx.attr_matrix(G, nodelist=[1, 2, 3])
sparse_attr = nx.attr_sparse_matrix(G, nodelist=[1, 2, 3])
```

## Complete Linalg/Conversion Function Reference

| Category | Function | Description |
|----------|----------|-------------|
| Adjacency | `adjacency_matrix(G)` | Sparse CSR matrix |
| Adjacency | `to_numpy_array(G, weight=None)` | Dense numpy array |
| Adjacency | `to_pandas_adjacency(G)` | DataFrame |
| Adjacency | `to_numpy_edgelist(G)` | (src, tgt, w) array |
| Adjacency | `weighted_adjacency_matrix(G, weight)` | Weighted sparse |
| Laplacian | `laplacian_matrix(G)` | D - A |
| Laplacian | `normalized_laplacian_matrix(G)` | I - D^(-1/2)AD^(-1/2) |
| Laplacian | `directed_combinatorial_laplacian_matrix(DG)` | Directed L |
| Incidence | `incidence_matrix(G)` | Nodes × edges |
| Bethe Hessian | `bethe_hessian_matrix(G, r=avg_degree)` | Community detection |
| Modularity | `modularity_matrix(G)` | Undirected B = A - dd^T/2m |
| Modularity | `directed_modularity_matrix(DG)` | Directed modularity |
| Attribute | `attr_matrix(G, nodelist, edge_attr=None)` | Dense attribute matrix |
| Attribute | `attr_sparse_matrix(G, nodelist, ...)` | Sparse attribute matrix |
| Spectrum | `adjacency_spectrum(G)` | Eigenvalues of A |
| Spectrum | `laplacian_spectrum(G)` | Eigenvalues of L |
| Spectrum | `normalized_laplacian_spectrum(G)` | Normalized Lap eigenvalues |
| Spectrum | `bethe_hessian_spectrum(G, r)` | Bethe Hessian eigenvalues |
| Spectrum | `modularity_spectrum(G)` | Modularity matrix eigenvalues |
| Connectivity | `algebraic_connectivity(G)` | 2nd smallest Laplacian eig |
| Fiedler | `fiedler_vector(G)` | Eigenvector for alg. connectivity |
| Spectral | `spectral_bisection(G, fiedler_vec)` | Partition via Fiedler |
| Spectral | `spectral_ordering(G)` | Node ordering by Fiedler |
| Visibility | `visibility_graph(time_series)` | Time series → graph |
| Conversion | `to_numpy_edgelist(G)` | (src, tgt, w) array |
| From numpy | `from_numpy_array(A, create_using=None)` | Matrix → Graph |
| From scipy | `from_scipy_sparse_array(A)` | Sparse → Graph |
| From pandas | `from_pandas_adjacency(df)` | DataFrame → Graph |
| From pandas | `from_pandas_edgelist(df, ...)` | Edgelist DF → Graph |
| To scipy | `to_scipy_sparse_array(G)` | Graph → sparse |
| Relabel | `relabel_nodes(G, mapping, copy=True)` | Custom node mapping |
| Relabel | `convert_node_labels_to_integers(G, ...)` | Convert to 0..n-1 |
| General | `to_networkx_graph(data, create_using=None)` | Any input → Graph |

## Summary

| Operation | Function | Description |
|-----------|----------|-------------|
| Adjacency matrix | `nx.adjacency_matrix()` | Sparse CSR matrix |
| Numpy adjacency | `nx.to_numpy_array()` | Dense numpy array |
| Laplacian matrix | `nx.laplacian_matrix()` | D - A |
| Normalized Laplacian | `nx.normalized_laplacian_matrix()` | I - D^(-1/2)AD^(-1/2) |
| Incidence matrix | `nx.incidence_matrix()` | Nodes × edges |
| Bethe Hessian | `nx.bethe_hessian_matrix()` | For community detection |
| Modularity matrix | `nx.modularity_matrix()` | B = A - (dd^T)/2m |
| Attribute matrix | `nx.attr_matrix(G, nodelist)` | Node attribute matrix |
| Adjacency spectrum | `nx.adjacency_spectrum()` | Eigenvalues of A |
| Laplacian spectrum | `nx.laplacian_spectrum()` | Eigenvalues of L |
| Algebraic connectivity | `nx.algebraic_connectivity()` | 2nd smallest Laplacian eigenvalue |
| Fiedler vector | `nx.fiedler_vector()` | Eigenvector for algebraic connectivity |
| Spectral bisection | `nx.spectral_bisection()` | Partition via Fiedler vector |
| From numpy array | `nx.from_numpy_array()` | Matrix → Graph |
| From scipy sparse | `nx.from_scipy_sparse_array()` | Sparse matrix → Graph |
| From pandas | `nx.from_pandas_edgelist()` | DataFrame → Graph |
| Relabel nodes | `nx.relabel_nodes()` | Custom node mapping |
| Integer labels | `nx.convert_node_labels_to_integers()` | Convert to 0, 1, 2, ... |
