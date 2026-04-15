# scipy.sparse - Sparse Matrices and Linear Algebra

The `scipy.sparse` module provides data structures and algorithms for efficiently working with sparse matrices (matrices containing mostly zero values). This is essential for large-scale linear algebra, graph algorithms, and scientific computing.

## Sparse Matrix Formats

### Creating Sparse Matrices

```python
from scipy import sparse
import numpy as np

# From dense matrix
dense = np.array([[0, 0, 3], [0, 4, 0], [5, 0, 0]])
sparse_csr = sparse.csr_matrix(dense)  # Compressed Sparse Row

# From COO format (efficient for construction)
row = np.array([0, 1, 2])
col = np.array([2, 1, 0])
data = np.array([3, 4, 5])
sparse_coo = sparse.coo_matrix((data, (row, col)), shape=(3, 3))

# From diagonal
diagonal = np.array([1, 2, 3, 4])
sparse_diag = sparse.diags(diagonal)

# Identity matrix
sparse_eye = sparse.eye(5)  # 5x5 identity

# Random sparse matrix
sparse_rand = sparse.random(100, 100, density=0.1)  # 10% non-zero
```

### Format Comparison

| Format | Best For | Row Slicing | Column Slicing | Math Operations |
|--------|----------|-------------|----------------|-----------------|
| `CSR` | Arithmetic, row access | ✅ Fast | ❌ Slow | ✅ Excellent |
| `CSC` | Arithmetic, column access | ❌ Slow | ✅ Fast | ✅ Excellent |
| `COO` | Construction, I/O | ❌ Slow | ❌ Slow | ❌ Convert first |
| `LIL` | Incremental construction | ✅ Fast | ✅ Fast | ⚠️ Moderate |
| `DIA` | Diagonal matrices | ✅ Fast | ✅ Fast | ✅ Good |

### Converting Between Formats

```python
from scipy import sparse

# Start with COO (efficient for building)
coo = sparse.coo_matrix((data, (row, col)), shape=(100, 100))

# Convert to CSR for arithmetic
csr = coo.tocsr()

# Convert to CSC for column operations
csc = coo.tocsc()

# Convert to LIL for incremental modification
lil = coo.tolil()

# Back to dense (use carefully - can be memory-intensive!)
dense = csr.toarray()
```

## Sparse Matrix Operations

### Basic Arithmetic

```python
from scipy import sparse
import numpy as np

A = sparse.random(100, 100, density=0.1, format='csr')
B = sparse.random(100, 100, density=0.1, format='csr')

# Addition (preserves sparsity)
C_add = A + B

# Subtraction
C_sub = A - B

# Multiplication (sparse @ sparse)
C_mul = A @ B

# Element-wise multiplication (Hadamard product)
C_hadamard = A.multiply(B)

# Scalar multiplication
C_scalar = 2.0 * A

# Transpose
A_T = A.T  # or A.transpose()
```

### Matrix-Vector Operations

```python
from scipy import sparse

A = sparse.random(1000, 1000, density=0.01, format='csr')
x = np.random.rand(1000)

# Sparse matrix-vector multiplication (very efficient)
y = A @ x

# Transpose times vector
y_T = A.T @ x

# Element-wise operations
x_sparse = sparse.csr_matrix(x.reshape(-1, 1))
```

### Slicing and Indexing

```python
from scipy import sparse

A = sparse.random(50, 50, density=0.2, format='csr')

# Row slicing (efficient in CSR)
rows_10_20 = A[10:20, :]

# Column slicing (efficient in CSC)
A_csc = A.tocsc()
cols_10_20 = A_csc[:, 10:20]

# Element access
value = A[5, 10]  # Returns scalar

# Boolean indexing
mask = np.random.rand(50) > 0.5
rows_masked = A[mask, :]

# Fancy indexing
indices = [0, 5, 10, 15]
rows_fancy = A[indices, :]
```

## Sparse Linear Algebra (scipy.sparse.linalg)

### Iterative Solvers

#### Conjugate Gradient (Symmetric Positive Definite)

```python
from scipy.sparse import linalg as spla
import numpy as np

# Create symmetric positive definite matrix
A = sparse.random(1000, 1000, density=0.01, format='csr')
A = A @ A.T + sparse.eye(1000) * 0.1  # Make SPD

b = np.random.rand(1000)

# Solve Ax = b using conjugate gradient
x, info = spla.cg(A, b, tol=1e-6, maxiter=1000)

if info == 0:
    print("Converged successfully")
else:
    print(f"Did not converge (info={info})")
```

#### GMRES (General Case)

```python
from scipy.sparse import linalg as spla

# For non-symmetric or indefinite matrices
A = sparse.random(1000, 1000, density=0.01, format='csr')
b = np.random.rand(1000)

# GMRES solver
x, info = spla.gmres(A, b, tol=1e-6, restart=100)

# With preconditioning (see below)
M = spla.spilu(A).solve  # ILU preconditioner
x, info = spla.gmres(A, b, M=M)
```

#### BiCGSTAB and Other Methods

```python
from scipy.sparse import linalg as spla

# Biconjugate gradient stabilized
x, info = spla.bicgstab(A, b, tol=1e-6)

# TFQMR (Terminated Fast QR Multistep)
x, info = spla.tfqmr(A, b)

# CG for normal equations (non-symmetric systems)
x, info = spla.cgs(A, b)
```

### Eigenvalue Problems

#### Largest Eigenvalues

```python
from scipy.sparse import linalg as spla

A = sparse.random(1000, 1000, density=0.01, format='csr')

# Compute k largest eigenvalues (by magnitude)
k = 10
eigenvalues, eigenvectors = spla.eigs(A, k=k, which='LM')

# Other options for 'which':
# 'LA': Largest algebraic (for symmetric)
# 'SA': Smallest algebraic
# 'LR': Largest real part
# 'SR': Smallest real part
# 'LI': Largest imaginary part
# 'SI': Smallest imaginary part
```

#### Symmetric Eigenvalue Problems

```python
from scipy.sparse import linalg as spla

# Create symmetric matrix
A = sparse.random(1000, 1000, density=0.01)
A = (A + A.T) / 2  # Make symmetric

# Use eigsh for symmetric matrices (faster and more stable)
eigenvalues, eigenvectors = spla.eigsh(A, k=10, which='LM')

# Smallest eigenvalues
eigenvalues_small, _ = spla.eigsh(A, k=10, which='SA')
```

#### Shift-Invert Mode (Interior Eigenvalues)

```python
from scipy.sparse import linalg as spla

# Find eigenvalues near a specific value sigma
sigma = 5.0
eigenvalues, eigenvectors = spla.eigs(A, k=10, sigma=sigma, which='LM')

# This finds eigenvalues closest to sigma
```

### Sparse Matrix Factorization

#### LU Factorization (UMFPACK)

```python
from scipy.sparse import linalg as spla

A = sparse.random(500, 500, density=0.1, format='csc')

# Compute LU factorization
lu = spla.splu(A, diag_pivot_thresh=0.0, permc_spec='COLMIN')

# Solve using factorization
b = np.random.rand(500)
x = lu.solve(b)
```

#### Cholesky Factorization (Symmetric Positive Definite)

```python
from scipy.sparse import linalg as spla

# Create SPD matrix
A = sparse.random(500, 500, density=0.1)
A = A @ A.T + sparse.eye(500) * 0.1

# Cholesky factorization
chol = spla.splu(A, symmetric_mode=True)

# Or use CHOLMOD (if available)
from scikits.cholmod import cholesky  # Separate package
```

#### Incomplete LU (Preconditioning)

```python
from scipy.sparse import linalg as spla

A = sparse.random(1000, 1000, density=0.01, format='csc')

# Incomplete LU factorization (for preconditioning)
ilu = spla.spilu(A, fill_factor=10, drop_tol=1e-3)

# Use as preconditioner in iterative solver
def M(x):
    return ilu.solve(x)

b = np.random.rand(1000)
x, info = spla.gmres(A, b, M=M)
```

## Graph Algorithms (scipy.sparse.csgraph)

### Connected Components

```python
from scipy.sparse import csgraph
import numpy as np

# Create adjacency matrix (undirected graph)
adj = sparse.random(100, 100, density=0.1, format='csr')
adj = adj + adj.T  # Make symmetric
adj.data = 1  # Unweighted

# Find connected components
n_components, component_labels = csgraph.connected_components(adj, directed=False)

print(f"Number of components: {n_components}")
```

### Shortest Paths

#### Single-Source Shortest Path (Dijkstra)

```python
from scipy.sparse import csgraph

# Weighted graph (adjacency matrix with weights)
adj_weighted = sparse.random(100, 100, density=0.1, format='csr')
adj_weighted.data = np.random.rand(len(adj_weighted.data)) * 10  # Random weights

# Shortest paths from node 0
distances, predecessors = csgraph.dijkstra(adj_weighted, directed=True, 
                                           indices=0, return_predecessors=True)

# Reconstruct path to node k
k = 50
path = []
node = k
while node is not None:
    path.append(node)
    node = predecessors[node]
path.reverse()
```

#### All-Pairs Shortest Path (Floyd-Warshall)

```python
from scipy.sparse import csgraph

# All-pairs shortest paths
distances_all, predecessors_all = csgraph.floyd_warshall(adj_weighted, 
                                                         directed=True, 
                                                         return_predecessors=True)

# Distance from node i to node j
dist_ij = distances_all[i, j]
```

### Minimum Spanning Tree

```python
from scipy.sparse import csgraph

# Compute minimum spanning tree
mst = csgraph.minimum_spanning_tree(adj_weighted)

# Number of edges in MST
n_edges_mst = mst.nnz  # For undirected graph, divide by 2

# Kruskal's algorithm (alternative)
mst_kruskal = csgraph.minimum_spanning_tree(adj_weighted, 
                                            algorithm='kruskal')
```

### Random Walks and PageRank

```python
from scipy.sparse import csgraph

# PageRank computation
adj_graph = sparse.random(100, 100, density=0.1, format='csr')
adj_graph.data = 1  # Unweighted

pagerank_scores, damping = csgraph.laplacian(adj_graph, normalized=True)
```

## Sparse Matrix Utilities

### Creating Special Matrices

```python
from scipy import sparse

# Diagonal matrix with offsets
diagonals = [np.ones(5), np.ones(4)*2, np.ones(4)*3]
offsets = [0, 1, -1]  # Main diagonal, upper, lower
diag_matrix = sparse.diags(diagonals, offsets, shape=(5, 5))

# Block diagonal matrix
blocks = [sparse.eye(3), sparse.eye(4), sparse.eye(2)]
block_diag = sparse.block_diag(blocks, format='csr')

# Triangular matrices
tri_upper = sparse.triu(sparse.random(10, 10, density=0.3))
tri_lower = sparse.tril(sparse.random(10, 10, density=0.3))
```

### Matrix Properties and Analysis

```python
from scipy import sparse

A = sparse.random(100, 100, density=0.1, format='csr')

# Number of stored elements
n_stored = A.nnz

# Density (fraction of non-zero elements)
density = A.nnz / (A.shape[0] * A.shape[1])

# Sparsity pattern
rows, cols = A.nonzero()

# Convert to different formats
A_csc = A.tocsc()
A_lil = A.tolil()

# Check if matrix is structured
is_csr = sparse.isspmatrix_csr(A)
is_csc = sparse.isspmatrix_csc(A)
```

### Efficient Construction Patterns

```python
from scipy import sparse
import numpy as np

# Pattern 1: Build with COO, convert to CSR
n_rows, n_cols = 1000, 1000
data_list, row_list, col_list = [], [], []

for i in range(100):
    r = np.random.randint(0, n_rows)
    c = np.random.randint(0, n_cols)
    data_list.append(np.random.rand())
    row_list.append(r)
    col_list.append(c)

coo = sparse.coo_matrix((data_list, (row_list, col_list)), 
                        shape=(n_rows, n_cols))
csr = coo.tocsr()  # Convert for arithmetic

# Pattern 2: Use LIL for incremental updates
lil = sparse.lil_matrix((n_rows, n_cols))
for i in range(100):
    lil[i, np.random.randint(0, n_cols)] = np.random.rand()

csr = lil.tocsr()  # Convert when done modifying

# Pattern 3: Use diags for banded matrices
main_diag = np.ones(100)
upper_diag = np.ones(99) * 0.5
lower_diag = np.ones(99) * 0.5
banded = sparse.diags([lower_diag, main_diag, upper_diag], 
                      offsets=[-1, 0, 1])
```

## Troubleshooting

### Memory Issues

```python
# Check memory usage before converting to dense
A = sparse.random(10000, 10000, density=0.001)
print(f"Sparse nnz: {A.nnz}")
print(f"Dense size: {A.shape[0] * A.shape[1] * 8 / 1e6:.1f} MB")

# Use iterative solvers instead of direct methods for large problems
x, info = spla.gmres(A, b)  # Instead of splu(A).solve(b)
```

### Format Selection Issues

```python
# CSR is best for most operations
A_csr = A.tocsr()

# Use CSC for column operations
A_csc = A.tocsc()

# Convert before arithmetic operations
result = A_csr @ B_csr  # Not COO @ COO
```

### Convergence Issues in Iterative Solvers

```python
# Use preconditioning
M = spla.spilu(A, drop_tol=1e-4).solve
x, info = spla.gmres(A, b, M=M, maxiter=2000)

# Try different methods
for method in ['cg', 'gcg', 'gmres', 'bicgstab']:
    x, info = spla.cg(A, b) if method == 'cg' else spla.gmres(A, b)
    print(f"{method}: info={info}")
```

## See Also

- [`scipy.linalg`](references/04-linalg.md) - Dense linear algebra
- [`networkx`](https://networkx.org/) - Graph algorithms and analysis
- [`pyamg`](https://github.com/pyamg/pyamg) - Algebraic multigrid for preconditioning
