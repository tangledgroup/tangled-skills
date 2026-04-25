# Linear Algebra in NumPy 2.4.4

## Overview

NumPy's `linalg` module provides comprehensive linear algebra operations:

- **Matrix multiplication and products**
- **Decompositions**: SVD, eigenvalues, Cholesky, LU (via SciPy)
- **Solving linear systems**
- **Matrix properties**: determinant, rank, norm, condition number
- **Tensor contractions and advanced products**

## Matrix Multiplication

### Basic Operations

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication using @ operator (Python 3.5+)
C = A @ B
# [[19, 22]
#  [43, 50]]

# Using np.dot() - works for matrices and vectors
C = np.dot(A, B)

# Using np.matmul() - strictly matrix multiplication
C = np.matmul(A, B)

# Method form
C = A.dot(B)
```

### Vector Products

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Dot product (scalar result)
dot = np.dot(a, b)          # 32 (1*4 + 2*5 + 3*6)
dot = a @ b                 # Same using @ operator

# Outer product (matrix result)
outer = np.outer(a, b)
# [[ 4,  5,  6]
#  [ 8, 10, 12]
#  [12, 15, 18]]

# Inner product (generalized dot product)
inner = np.inner(a, b)      # 32 (same as dot for 1D)
```

### Batch Matrix Multiplication

```python
# Stack of matrices: (batch_size, rows, cols)
A_batch = np.random.rand(3, 4, 5)  # 3 matrices of shape (4, 5)
B_batch = np.random.rand(3, 5, 2)  # 3 matrices of shape (5, 2)

# Batch matrix multiply: result is (3, 4, 2)
C_batch = np.matmul(A_batch, B_batch)
C_batch = A_batch @ B_batch  # Same
```

## Solving Linear Systems

### solve() - Ax = b

```python
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])

# Solve for x in Ax = b
x = np.linalg.solve(A, b)
# x: [1., 4.] (verify: A @ x == b)

# Multiple right-hand sides
B = np.array([[9, 1], [8, 2]])
X = np.linalg.solve(A, B)  # Solve Ax1 = b1 and Ax2 = b2 simultaneously

# Requirements:
# - A must be square and full rank
# - Faster and more stable than computing inverse
```

### lstsq() - Least Squares

```python
A = np.array([[1, 1], [1, 1], [1, 1]])  # Overdetermined system
b = np.array([1, 2, 3])

# Find x that minimizes ||Ax - b||^2
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

# For underdetermined systems (more variables than equations)
A = np.array([[1, 2, 3]])
b = np.array([6])
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
# Returns minimum norm solution
```

### Tensor Contractions

```python
# Einstein summation notation (most flexible)
A = np.random.rand(2, 3, 4)
B = np.random.rand(4, 3, 2)

# Contract last axis of A with first axis of B
C = np.einsum('ijk,kjl->ijl', A, B)

# Matrix multiplication using einsum
A = np.random.rand(3, 4)
B = np.random.rand(4, 5)
C = np.einsum('ij,jk->ik', A, B)  # Same as A @ B

# Trace (sum of diagonal)
A = np.random.rand(3, 3)
trace = np.einsum('ii->', A)  # Sum over repeated index

# Tensordot (explicit axis specification)
C = np.tensordot(A, B, axes=([2], [0]))  # Contract axis 2 of A with axis 0 of B
```

## Matrix Decompositions

### Eigenvalues and Eigenvectors

```python
A = np.array([[4, -2], [1, 1]])

# Standard eigenvalue problem: Av = λv
eigenvalues, eigenvectors = np.linalg.eig(A)
# eigenvalues: [3., 2.]
# eigenvectors: columns are eigenvectors

# Verify: A @ v ≈ λ * v
for i in range(len(eigenvalues)):
    v = eigenvectors[:, i]
    lam = eigenvalues[i]
    assert np.allclose(A @ v, lam * v)

# For symmetric matrices (more stable)
A_sym = np.array([[4, 2], [2, 3]])
eigenvalues, eigenvectors = np.linalg.eigh(A_sym)
# Eigenvalues are real and sorted in ascending order
```

### Singular Value Decomposition (SVD)

```python
A = np.random.rand(4, 5)

# Full SVD: A = U @ diag(S) @ Vh
U, S, Vh = np.linalg.svd(A, full_matrices=False)

# Reconstruct A
A_reconstructed = U @ np.diag(S) @ Vh
assert np.allclose(A, A_reconstructed)

# S contains singular values (sorted descending)
print(f"Singular values: {S}")

# Truncated SVD for low-rank approximation
k = 2  # Keep top k singular values
A_approx = U[:, :k] @ np.diag(S[:k]) @ Vh[:k, :]

# Full_matrices=True gives complete U and Vh matrices
U_full, S, Vh_full = np.linalg.svd(A, full_matrices=True)
```

### QR Decomposition

```python
A = np.random.rand(4, 3)

# QR decomposition: A = Q @ R
Q, R = np.linalg.qr(A)

# Verify reconstruction
assert np.allclose(A, Q @ R)

# Q is orthogonal (Q.T @ Q = I)
assert np.allclose(Q.T @ Q, np.eye(3))

# R is upper triangular
print(R)  # Upper triangular matrix

# 'complete' vs 'reduced' mode
Q_full, R_full = np.linalg.qr(A, mode='complete')
Q_econ, R_econ = np.linalg.qr(A, mode='reduced')  # Default
```

### Cholesky Decomposition

```python
# Requires symmetric positive-definite matrix
A = np.array([[4, 2], [2, 3]])
A_spd = A @ A.T  # Make positive definite

# Cholesky: A = L @ L.T where L is lower triangular
L = np.linalg.cholesky(A_spd)

# Verify reconstruction
assert np.allclose(A_spd, L @ L.T)

# Useful for solving Ax = b when A is positive definite
b = np.array([1, 2])
x = np.linalg.solve(L.T, np.linalg.solve(L, b))  # More stable than direct solve
```

## Matrix Properties

### Determinant

```python
A = np.array([[1, 2], [3, 4]])

# Determinant
det = np.linalg.det(A)  # -2.0

# For larger matrices (can be numerically unstable)
A_large = np.random.rand(10, 10)
det_large = np.linalg.det(A_large)

# Log determinant (more stable for large matrices)
sign, logdet = np.linalg.slogdet(A_large)
det_stable = sign * np.exp(logdet)
```

### Rank

```python
A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Matrix rank (number of linearly independent rows/columns)
rank = np.linalg.matrix_rank(A)  # 2 (rows are dependent)

# With tolerance
rank_tol = np.linalg.matrix_rank(A, tol=1e-10)

# Full rank matrix
A_full = np.array([[1, 0], [0, 1]])
rank_full = np.linalg.matrix_rank(A_full)  # 2
```

### Norms

```python
v = np.array([3, 4])
A = np.array([[1, 2], [3, 4]])

# Vector norms
norm2 = np.linalg.norm(v)           # L2 norm: 5.0
norm1 = np.linalg.norm(v, ord=1)    # L1 norm: 7.0
norm_inf = np.linalg.norm(v, ord=np.inf)  # Infinity norm: 4.0

# Matrix norms
frobenius = np.linalg.norm(A)       # Frobenius norm (default)
max_abs = np.linalg.norm(A, np.inf) # Max row sum
col_sum = np.linalg.norm(A, ord=1)  # Max column sum

# Nuclear norm (sum of singular values)
S = np.linalg.svd(A, compute_uv=False)
nuclear_norm = np.sum(S)
```

### Condition Number

```python
A = np.array([[1, 2], [3, 4]])

# Condition number (measure of sensitivity to numerical errors)
cond_2 = np.linalg.cond(A)          # 2-norm condition number (default)
cond_1 = np.linalg.cond(A, p=1)     # 1-norm
cond_inf = np.linalg.cond(A, np.inf)  # Infinity norm

# Large condition number → ill-conditioned matrix
# Small condition number → well-conditioned matrix

# Condition number of identity is 1 (perfectly conditioned)
I = np.eye(3)
cond_I = np.linalg.cond(I)  # 1.0
```

### Trace

```python
A = np.array([[1, 2], [3, 4]])

# Sum of diagonal elements
trace = np.linalg.trace(A)  # 5 (1 + 4)

# Works for any array (sums last two axes)
tensor = np.arange(24).reshape(2, 3, 4)
trace_tensor = np.trace(tensor)  # Sum of diagonals in each 3x4 slice
```

## Matrix Inversion and Pseudoinverse

### inv() - Matrix Inverse

```python
A = np.array([[1, 2], [3, 4]])

# Compute inverse
A_inv = np.linalg.inv(A)

# Verify: A @ A_inv = I
assert np.allclose(A @ A_inv, np.eye(2))

# WARNING: Avoid computing inverse when possible
# Use solve() instead for Ax = b
```

### pinv() - Moore-Penrose Pseudoinverse

```python
A = np.array([[1, 2, 3], [4, 5, 6]])  # Non-square matrix

# Pseudoinverse (works for non-square and singular matrices)
A_pinv = np.linalg.pinv(A)

# Verify properties
assert np.allclose(A @ A_pinv @ A, A)
assert np.allclose(A_pinv @ A @ A_pinv, A_pinv)

# Solve least squares using pseudoinverse
b = np.array([1, 2])
x = A_pinv @ b  # Minimum norm solution
```

## Advanced Operations

### Matrix Exponential and Logarithm

```python
from scipy.linalg import expm, logm  # NumPy doesn't have these

A = np.array([[0, 1], [-1, 0]])

# Matrix exponential
exp_A = expm(A)

# Matrix logarithm
log_exp_A = logm(exp_A)
assert np.allclose(log_exp_A, A)
```

### Sign Decomposition

```python
A = np.random.rand(4, 4)

# Symmetric part
A_sym = (A + A.T) / 2

# Skew-symmetric part  
A_skew = (A - A.T) / 2

# Verify: A = A_sym + A_skew
assert np.allclose(A, A_sym + A_skew)
```

### Hessenberg and Schur Forms

```python
from scipy.linalg import hessenberg, schur

A = np.random.rand(4, 4)

# Upper Hessenberg form (nearly triangular)
H, P = hessenberg(A)  # H = P.T @ A @ P

# Schur decomposition: A = Q @ T @ Q.T
T, Q = schur(A)
assert np.allclose(A, Q @ T @ Q.conj().T)
```

## Common Patterns

```python
# Projection matrix onto column space of A
def projection_matrix(A):
    return A @ np.linalg.inv(A.T @ A) @ A.T

# Orthogonalize columns (Gram-Schmidt via QR)
def orthogonalize(A):
    Q, R = np.linalg.qr(A)
    return Q

# Check if matrix is symmetric
def is_symmetric(A, tol=1e-10):
    return np.allclose(A, A.T, atol=tol)

# Check if matrix is positive definite
def is_positive_definite(A):
    try:
        np.linalg.cholesky(A)
        return True
    except np.linalg.LinAlgError:
        return False

# Solve multiple systems with same A efficiently
def solve_multiple(A, B):
    """Solve Ax = b for multiple b vectors (columns of B)"""
    return np.linalg.solve(A, B)  # Optimized for this case

# Low-rank approximation using SVD
def low_rank_approx(A, k):
    U, S, Vh = np.linalg.svd(A, full_matrices=False)
    return U[:, :k] @ np.diag(S[:k]) @ Vh[:k, :]
```

## Performance Tips

1. **Use `solve()` instead of `inv()`** - More stable and faster for Ax = b
2. **Exploit matrix structure** - Use `eigh()` for symmetric matrices
3. **Batch operations when possible** - Process multiple matrices at once
4. **Use appropriate decomposition** - Cholesky for positive definite, QR for least squares
5. **Avoid full SVD when not needed** - Use `full_matrices=False`

## Troubleshooting

**LinAlgError: Singular matrix**: Matrix is not invertible.
```python
# Check condition number
cond = np.linalg.cond(A)
if cond > 1e10:
    print("Matrix is nearly singular")
    # Use pinv() instead of inv()
```

**LinAlgError: Last 2 dimensions must be square**: Trying to compute determinant/inverse of non-square matrix.
```python
# Check shape
assert A.shape[0] == A.shape[1], "Matrix must be square"
```

**Shape mismatch in multiplication**: Inner dimensions must match.
```python
A = np.random.rand(3, 4)
B = np.random.rand(4, 5)
C = A @ B  # OK: (3, 4) @ (4, 5) → (3, 5)
```
