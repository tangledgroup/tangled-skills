# Sparse Arrays (scipy.sparse)

## Overview

Sparse arrays store only non-zero elements, saving memory and computation for arrays where most values are zero. SciPy provides multiple sparse formats with different tradeoffs between compression and functionality.

```python
import scipy.sparse as sp
import numpy as np
```

## Sparse Formats

| Format | Class | Best For |
|--------|-------|----------|
| COO | `coo_array` | Construction, conversion |
| CSR | `csr_array` | Arithmetic, row slicing, matrix-vector products |
| CSC | `csc_array` | Column slicing, linear algebra |
| BSR | `bsr_array` | Block-structured matrices |
| DIA | `dia_array` | Diagonal-dominant matrices |
| LIL | `lil_array` | Incremental construction |
| DOK | `dok_array` | Incremental construction by index |

### Format Conversion

```python
coo = sp.coo_array(dense)
csr = coo.tocsr()
csc = csr.tocsc()
dense = csr.toarray()
```

## Creating Sparse Arrays

```python
# From dense array
sparse = sp.coo_array(np.array([[1, 0, 0], [0, 4, 0], [0, 0, 5]]))

# From coordinates
row = np.array([0, 1, 2])
col = np.array([0, 1, 2])
data = np.array([1, 4, 5])
sparse = sp.coo_array((data, (row, col)), shape=(3, 3))

# Diagonal sparse array
diag = sp.diags([1, 2, 3], offsets=0)

# Identity
eye = sp.eye(5)

# Random sparse
rand_sparse = sp.random(1000, 1000, density=0.01)
```

## Operations

```python
# Arithmetic
result = A + B
result = A @ B  # matrix multiplication
result = A.dot(B)

# Reductions
print(sparse.max())      # maximum value
print(sparse.mean())     # mean (including zeros)
print(sparse.sum(axis=0))  # column sums

# Properties
print(sparse.nnz)        # number of stored elements
print(sparse.shape)      # array shape
# density = nnz / (shape[0] * shape[1])  # fraction of stored elements
```

### Indexing (New in 1.17)

`coo_array` now supports full indexing including integers, slices, arrays, `np.newaxis`, and `Ellipsis` in 1D, 2D, and nD:

```python
# COO indexing without format conversion
row_slice = coo[0:5, :]
element = csr[2, 3]
```

### Construction Functions (New in 1.17)

- `expand_dims`: Add new axis
- `swapaxes`: Swap axes
- `permute_dims`: Permute dimensions
- `kron`: Kronecker product with nD support

`dok_array` gained an `update` method for bulk updates from dict or iterable.

## Sparse Linear Algebra (scipy.sparse.linalg)

### Solving Sparse Systems

```python
from scipy.sparse import linalg as spla

# Direct solver (SuperLU)
x = spla.spsolve(A_sparse, b)

# Iterative solvers
x, info = spla.cg(A_sparse, b)          # Conjugate gradient
x, info = spla.gmres(A_sparse, b)       # GMRES
x, info = spla.bicgstab(A_sparse, b)    # Biconjugate gradient stabilized
```

### Sparse Eigenvalue Problems

```python
# Compute k smallest eigenvalues
eigenvalues, eigenvectors = spla.eigs(A_sparse, k=10, which='SM')

# Symmetric matrices (more efficient)
eigenvalues, eigenvectors = spla.eigsh(A_sparse, k=10, which='SM')

# New in 1.17: rng parameter for reproducible results
eigenvalues, eigenvectors = spla.eigs(A_sparse, k=10, rng=np.random.default_rng(42))
```

ARPACK and PROPACK were ported from Fortran77 to C in 1.17, enabling external PRNGs for reproducible runs.

### Linear Operator

For matrix-free operations:

```python
def matvec(v):
    return some_operation(v)  # define matrix-vector product

op = spla.LinearOperator((n, n), matvec=matvec)
x = spla.cg(op, b)[0]
```

### Matrix Functions

```python
# Sparse matrix exponential
exp_A = spla.expm(A_sparse)

# Krylov method for f(tA)b (new in 1.17)
y = spla.funm_multiply_krylov(f, t*A, b)
```

## Compressed Sparse Graph (scipy.sparse.csgraph)

Graph algorithms on sparse adjacency matrices:

```python
from scipy.sparse import csgraph

# Shortest path
dist_matrix, predecessors = csgraph.shortest_path(graph, method='D')

# Connected components
n_components, labels = csgraph.connected_components(graph, directed=False)

# Minimum spanning tree
mst = csgraph.minimum_spanning_tree(graph)

# Breadth-first/depth-first search
predecessor = csgraph.breadth_first_order(graph, 0)
```
