# scipy.linalg - Linear Algebra and Matrix Operations

The `scipy.linalg` module provides comprehensive linear algebra routines, including matrix decompositions, eigenvalue problems, matrix equations, and special matrix operations. It builds on BLAS and LAPACK for high performance.

## Matrix Factorizations

### LU Decomposition

```python
from scipy import linalg
import numpy as np

A = np.array([[3, -2, 3], [2, 1, 0], [2, -3, 4]], dtype=float)

# LU decomposition with pivoting
P, L, U = linalg.lu(A)

# Verify: A = P @ L @ U
assert np.allclose(A, P @ L @ U)

# Solve linear system using LU
b = np.array([1, 2, 3])
x = linalg.lu_solve((L, U, P[0]), b)
```

### QR Decomposition

```python
A = np.random.rand(5, 3)

# Full QR decomposition
Q, R = linalg.qr(A, mode='full')  # Q: (m, m), R: (m, n)

# Reduced QR decomposition
Q, R = linalg.qr(A, mode='reduced')  # Q: (m, n), R: (n, n)

# Economy QR (same as reduced)
Q, R = linalg.qr(A, mode='economic')

# Verify: A = Q @ R
assert np.allclose(A, Q @ R)
```

### Cholesky Decomposition

```python
# Must be symmetric positive definite
A = np.array([[4, 2], [2, 5]], dtype=float)

# Lower triangular Cholesky factor
L = linalg.cholesky(A, lower=True)

# Upper triangular (default)
U = linalg.cholesky(A, lower=False)

# Verify: A = L @ L.T or A = U.T @ U
assert np.allclose(A, L @ L.T)

# Solve using Cholesky (faster than general solve for SPD matrices)
b = np.array([1, 2])
x = linalg.cho_solve((L, True), b)
```

### Singular Value Decomposition (SVD)

```python
A = np.random.rand(4, 3)

# Full SVD
U, s, Vh = linalg.svd(A, full_matrices=True)

# Economy SVD (default)
U, s, Vh = linalg.svd(A, full_matrices=False)

# Verify: A = U @ diag(s) @ Vh
A_reconstructed = U @ np.diag(s) @ Vh
assert np.allclose(A, A_reconstructed)

# Compute pseudo-inverse using SVD
A_pinv = Vh.T @ np.diag(1/s) @ U.T
```

### Eigenvalue Decomposition

```python
A = np.array([[4, 2], [1, 3]], dtype=float)

# Eigenvalues and eigenvectors (general case)
eigenvalues, eigenvectors = linalg.eig(A)

# Verify: A @ v = λ * v for each eigenvalue/eigenvector pair
assert np.allclose(A @ eigenvectors[:, 0], eigenvalues[0] * eigenvectors[:, 0])

# For symmetric matrices (more stable, real eigenvalues)
A_sym = np.array([[4, 2], [2, 3]], dtype=float)
eigenvalues, eigenvectors = linalg.eigh(A_sym)

# Upper triangular stored in lower part
A_up = np.array([[4, 2], [0, 3]], dtype=float)
eigenvalues, eigenvectors = linalg.eigh(A_up, UPLO='U')
```

## Solving Linear Systems

### Direct Methods

```python
A = np.array([[3, -2, 3], [2, 1, 0], [2, -3, 4]], dtype=float)
b = np.array([1, 2, 3])

# General solve (uses LU decomposition internally)
x = linalg.solve(A, b)

# Solve multiple right-hand sides
B = np.array([[1, 4], [2, 5], [3, 6]])
X = linalg.solve(A, B)

# Using Cholesky for symmetric positive definite
A_spd = np.array([[4, 2], [2, 5]], dtype=float)
b = np.array([1, 2])
x = linalg.cho_solve(linalg.cho_factor(A_spd), b)
```

### Least Squares Solutions

```python
# Overdetermined system (more equations than unknowns)
A = np.array([[1, 2], [3, 4], [5, 6], [7, 8]], dtype=float)
b = np.array([1, 2, 3, 4])

# Solve in least squares sense
x, residuals, rank, s = linalg.lstsq(A, b)

# Alternative using pseudo-inverse
A_pinv = linalg.pinv(A)
x_alt = A_pinv @ b
```

### Matrix Inversion (Use Sparingly)

```python
A = np.array([[3, -2, 3], [2, 1, 0], [2, -3, 4]], dtype=float)

# Compute inverse
A_inv = linalg.inv(A)

# Better: solve directly instead of inverting
b = np.array([1, 2, 3])
x = linalg.solve(A, b)  # Preferred over A_inv @ b

# Pseudo-inverse for singular or non-square matrices
A_pinv = linalg.pinv(A)
```

## Matrix Properties

### Determinant and Trace

```python
A = np.array([[3, -2, 3], [2, 1, 0], [2, -3, 4]], dtype=float)

# Determinant
det_A = linalg.det(A)

# Logarithm of absolute determinant (more stable for large matrices)
sign, logdet = linalg.slogdet(A)
det_A_stable = sign * np.exp(logdet)

# Trace
tr_A = linalg.trace(A)
```

### Rank and Norms

```python
A = np.random.rand(4, 3)

# Matrix rank (with tolerance)
rank = linalg.matrix_rank(A, tol=None)

# Various norms
norm_F = linalg.norm(A, 'fro')  # Frobenius norm
norm_2 = linalg.norm(A, 2)     # Spectral norm (largest singular value)
norm_inf = linalg.norm(A, np.inf)  # Max row sum
norm_1 = linalg.norm(A, 1)       # Max column sum

# Vector norms
v = np.array([1, 2, 3])
norm_v2 = linalg.norm(v, 2)  # Euclidean norm
norm_v1 = linalg.norm(v, 1)  # Sum of absolute values
```

### Condition Number

```python
A = np.array([[1, 2], [3, 4]], dtype=float)

# Condition number (2-norm, using singular values)
cond_A = linalg.cond(A, 2)

# Other norms
cond_A_1 = linalg.cond(A, 1)    # 1-norm condition number
cond_A_inf = linalg.cond(A, np.inf)  # Infinity norm

# Large condition number indicates ill-conditioned matrix
if cond_A > 1e10:
    print("Warning: Matrix is nearly singular")
```

## Special Matrix Operations

### Matrix Exponential and Logarithm

```python
A = np.array([[0, 1], [-1, 0]], dtype=float)

# Matrix exponential
exp_A = linalg.expm(A)

# Matrix logarithm
log_exp_A = linalg.logm(exp_A)
assert np.allclose(A, log_exp_A)

# Matrix square root
sqrt_A = linalg.sqrtm(A)
assert np.allclose(A, sqrt_A @ sqrt_A)
```

### Kronecker Product and Other Operations

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[0, 1], [1, 0]])

# Kronecker product (tensor product)
K = linalg.kron(A, B)

# Matrix power
A_squared = linalg.matrix_power(A, 2)
A_inv3 = linalg.matrix_power(A, -3)  # (A^-1)^3

# Sign and absolute value of matrix
sign_A, abs_A = linalg.signm(A)
```

### Solving Matrix Equations

#### Sylvester Equation: AX + XB = C

```python
A = np.array([[1, 2], [3, 4]], dtype=float)
B = np.array([[5, 6], [7, 8]], dtype=float)
C = np.array([[9, 10], [11, 12]], dtype=float)

# Solve AX + XB = C for X
X = linalg.solve_sylvester(A, B, C)
```

#### Lyapunov Equation: AX + XA* = B

```python
A = np.array([[1, 2], [3, 4]], dtype=float)
B = np.array([[5, 6], [7, 8]], dtype=float)

# Solve AX + XA* = B for X (where A* is conjugate transpose)
X = linalg.solve_lyapunov(A, B)
```

#### Continuous-time Algebraic Riccati Equation

```python
A = np.array([[1, 2], [3, 4]], dtype=float)
B = np.array([[5, 6], [7, 8]], dtype=float)
Q = np.array([[9, 10], [11, 12]], dtype=float)

# Solve ARE for control theory applications
X = linalg.solve_continuous_are(A, B, Q)
```

## BLAS and LAPACK Wrappers (Low-Level Access)

### Direct BLAS Calls

```python
from scipy.linalg import blas

# Matrix-matrix multiplication: C = alpha * op(A) * op(B) + beta * C
A = np.random.rand(10, 5)
B = np.random.rand(5, 8)
C = np.zeros((10, 8))

# dgemm for double precision general matrix multiply
C = blas.dgemm(A, B, C)
```

### Direct LAPACK Calls

```python
from scipy.linalg import lapack

# Solve triangular system
A = np.array([[3, 2], [0, 4]], dtype=float)
b = np.array([1, 2])

# dtrtrs for double precision triangular solve
x, info = lapack.dtrtrs(A, b, lower=False)
```

## Sparse Linear Algebra (Use scipy.sparse.linalg Instead)

For sparse matrices, use `scipy.sparse.linalg`:

```python
from scipy import sparse
from scipy.sparse import linalg as spla

# Create sparse matrix
A_sparse = sparse.random(1000, 1000, density=0.01)

# Iterative solvers (use for large sparse systems)
b = np.random.rand(1000)
x, info = spla.cg(A_sparse, b)  # Conjugate gradient (symmetric positive definite)
x, info = spla.gmres(A_sparse, b)  # GMRES (general case)

# Sparse eigenvalue problems
eigenvalues, eigenvectors = spla.eigs(A_sparse, k=5)  # 5 largest eigenvalues
```

## Troubleshooting

### Singular Matrix Errors

```python
try:
    x = linalg.solve(A, b)
except linalg.LinAlgError:
    print("Matrix is singular or nearly singular")
    # Use pseudo-inverse instead
    x = linalg.pinv(A) @ b
```

### Numerical Stability Issues

```python
# Use log determinant for large matrices
sign, logdet = linalg.slogdet(A)

# Check condition number before inverting
cond = linalg.cond(A)
if cond > 1e10:
    print("Warning: Matrix is ill-conditioned")

# Use appropriate tolerance for rank computation
rank = linalg.matrix_rank(A, tol=1e-10)
```

### Memory Issues with Large Matrices

```python
# Use sparse matrices for large problems
from scipy import sparse
A_sparse = sparse.csr_matrix(A_dense)

# Use out-of-place operations to avoid temporary arrays
linalg.solve(A, b, overwrite_b=True)  # Modifies b in place

# Process in chunks if necessary
for chunk in chunks(B):
    X_chunk = linalg.solve(A, chunk)
```

## See Also

- [`scipy.sparse.linalg`](references/09-sparse.md) - Sparse linear algebra
- [`numpy.linalg`](https://numpy.org/doc/stable/reference/routines.linalg.html) - Basic linear algebra in NumPy
- [`sklearn.decomposition`](https://scikit-learn.org/stable/modules/decomposition.html) - Dimensionality reduction
