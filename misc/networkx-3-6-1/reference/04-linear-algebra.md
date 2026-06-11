# Linear Algebra

NetworkX provides functions for converting graphs to matrix representations and computing spectral properties.

## Adjacency Matrix

```python
import numpy as np

# Graph to adjacency matrix
A = nx.adjacency_matrix(G)           # SciPy sparse array
A_dense = nx.to_numpy_array(G)       # NumPy dense array

# With nodelist for specific ordering
A = nx.adjacency_matrix(G, nodelist=node_order)

# Incidence matrix
B = nx.incidence_matrix(G)
```

## Laplacian Matrix

All Laplacian calculations use out-degree. For in-degree Laplacians, reverse the graph first:

```python
# Unnormalized (combinatorial) Laplacian
L = nx.laplacian_matrix(G)

# Normalized Laplacian
L_norm = nx.normalized_laplacian_matrix(G)

# Directed Laplacian
L_dir = nx.directed_laplacian_matrix(G)

# Directed combinatorial Laplacian
L_dir_comb = nx.directed_combinatorial_laplacian_matrix(G)
```

## Bethe Hessian Matrix

The deformed Laplacian used for community detection:

```python
B = nx.bethe_hessian_matrix(G, r)  # r is the deformation parameter
```

## Algebraic Connectivity

Fiedler vector and spectral bisection:

```python
# Algebraic connectivity (Fiedler value)
ac = nx.algebraic_connectivity(G)

# Fiedler vector
fv = nx.fiedler_vector(G)

# Spectral ordering
ordering = nx.spectral_ordering(G)

# Spectral bisection
partition = nx.spectral_bisection(G)
```

## Modularity Matrix

Used for modularity-based community detection:

```python
M = nx.modularity_matrix(G)
M_dir = nx.directed_modularity_matrix(G)
```

## Attribute Matrices

Construct matrices from node or edge attributes:

```python
# Dense attribute matrix
attr_mat = nx.attr_matrix(G, edge_attr="weight", node_attr="id")

# Sparse attribute matrix
attr_sparse = nx.attr_sparse_matrix(G, edge_attr="weight")
```

## Spectrum Analysis

Compute eigenvalue spectra of graph matrices:

```python
# Adjacency spectrum
eigenvalues = nx.adjacency_spectrum(G)

# Laplacian spectrum
lap_eigs = nx.laplacian_spectrum(G)

# Normalized Laplacian spectrum
norm_lap_eigs = nx.normalized_laplacian_spectrum(G)

# Modularity spectrum
mod_eigs = nx.modularity_spectrum(G)

# Bethe Hessian spectrum
bethe_eigs = nx.bethe_hessian_spectrum(G, r=2)
```

## Converting to/from Other Formats

### NumPy Arrays

```python
# Graph -> NumPy
A = nx.to_numpy_array(G, weight="weight", dtype=float)

# NumPy -> Graph
G = nx.from_numpy_array(A, create_using=nx.Graph)
DG = nx.from_numpy_array(A, create_using=nx.DiGraph)
```

### SciPy Sparse Arrays

```python
# Graph -> SciPy sparse
sparse_A = nx.to_scipy_sparse_array(G, weight="weight")

# SciPy sparse -> Graph
G = nx.from_scipy_sparse_array(sparse_A)
```

### Pandas DataFrames

```python
# Adjacency DataFrame
adj_df = nx.to_pandas_adjacency(G, weight="weight")
G = nx.from_pandas_adjacency(adj_df)

# Edge list DataFrame
edge_df = nx.to_pandas_edgelist(G, source="src", target="dst", edge_attr="weight")
G = nx.from_pandas_edgelist(edge_df, source="src", target="dst", edge_attr="weight")
```

### Dictionaries

```python
# Dict of dicts
dod = nx.to_dict_of_dicts(G)
G = nx.from_dict_of_dicts(dod)

# Dict of lists
dol = nx.to_dict_of_lists(G)
G = nx.from_dict_of_lists(dol)
```

### Edge Lists

```python
el = nx.to_edgelist(G, data=True)
G = nx.from_edgelist(el)
```
