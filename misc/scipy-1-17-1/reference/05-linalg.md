# Linear Algebra (scipy.linalg)

## Overview

`scipy.linalg` contains all functions from `numpy.linalg` plus additional advanced routines. It is always compiled with BLAS/LAPACK support, making it faster than `numpy.linalg` in most cases. Prefer `scipy.linalg` unless you want to avoid the SciPy dependency.

```python
from scipy import linalg
import numpy as np
```

## Matrix Operations

### Solving Linear Systems

```python
# Solve Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = linalg.solve(A, b)

# Batched solve (multiple right-hand sides)
B = np.array([[9, 1], [8, 2]])
X = linalg.solve(A, B)
```

### Matrix Inversion

`linalg.inv` in 1.17 has significant improvements:

```python
# Automatic structure detection with assume_a keyword
inv_A = linalg.inv(A, assume_a='gen')  # general
inv_A = linalg.inv(A, assume_a='sym')  # symmetric
inv_A = linalg.inv(A, assume_a='pos')  # positive definite

# For symmetric matrices, specify which triangle to use
inv_A = linalg.inv(A, assume_a='sym', lower=True)

# Emits LinAlgWarning for ill-conditioned inputs
```

### Matrix Factorizations

```python
# LU decomposition
lu, piv = linalg.lu_factor(A)
x = linalg.lu_solve((lu, piv), b)

# Cholesky decomposition (positive definite matrices)
L = linalg.cholesky(A, lower=True)

# QR decomposition
Q, R = linalg.qr(A)

# SVD
U, s, Vt = linalg.svd(A)

# Schur decomposition
T, Z = linalg.schur(A)
```

## Eigenvalue Problems

```python
# General eigenvalues and eigenvectors
eigenvalues, eigenvectors = linalg.eig(A)

# Symmetric/Hermitian eigenvalues (more efficient)
eigenvalues, eigenvectors = linalg.eigh(A)

# Generalized eigenvalue problem Ax = lambda*Bx
eigenvalues = linalg.eig(A, B)

# Eigenvalues only (faster)
eigenvalues = linalg.eigvals(A)
```

## Special Decompositions

```python
# Pseudo-inverse
pinv_A = linalg.pinv(A)

# Matrix square root
sqrt_A = linalg.sqrtm(A)

# Matrix sign function
sign_A = linalg.signm(A)

# Matrix exponential
exp_A = linalg.expm(A)

# Matrix logarithm
log_A = linalg.logm(A)

# Triangular solve
x = linalg.solve_triangular(U, b, lower=False)
```

## BLAS and LAPACK Access

Direct access to low-level BLAS/LAPACK routines:

```python
from scipy.linalg import blas, lapack

# BLAS level 2: matrix-vector operations
y = blas.gemv(1.0, A, x)

# BLAS level 3: matrix-matrix operations
C = blas.gemm(1.0, A, B, 0.0, C)

# LAPACK routines
result = lapack.potrf(A, lower=True)  # Cholesky
```

## Interpolative Decomposition

```python
from scipy.linalg import interpolative

# Compute interpolative decomposition
tp, ip, c = interpolative.ilp_d(A)
```

## Batched Operations

In 1.17, `linalg.inv`, `linalg.solve`, and `linalg.fiedler` have improved performance for batched inputs (N-D arrays where last two dimensions are the matrix).

## Array API Support

Many linalg functions support the Python Array API standard, enabling GPU array backends.
