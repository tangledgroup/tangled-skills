# Linear Algebra and Fourier Transforms

## Linear Algebra Overview

NumPy's `linalg` module relies on BLAS and LAPACK libraries for efficient implementations. When available, optimized libraries like OpenBLAS, Intel MKL, or ATLAS are preferred over NumPy's bundled reference implementations. These libraries are multithreaded — use `threadpoolctl` to control thread count if needed.

```python
import numpy as np
from numpy import linalg as LA
```

## Matrix and Vector Products

### The @ Operator

Introduced in NumPy 1.10, the `@` operator calls `np.matmul` and is preferred for matrix multiplication:

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

C = A @ B           # matrix product
# [[19, 22], [43, 50]]
```

### Product Functions

```python
# Dot product of two vectors
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
np.dot(v1, v2)      # 32
np.vdot(v1, v2)     # 32 (conjugate for complex)

# Inner product
np.inner(v1, v2)    # 32

# Outer product
np.outer(v1, v2)
# [[4, 5, 6], [8, 10, 12], [12, 15, 18]]

# Matrix multiplication
np.matmul(A, B)     # same as A @ B

# Tensor dot product along specific axes
np.tensordot(A, B, axes=1)

# Einstein summation (most flexible)
np.einsum('ij,jk->ik', A, B)  # matrix multiply
np.einsum('ii', A)             # trace (diagonal sum)
np.einsum('ij,ij', A, B)       # element-wise product then sum (Frobenius inner product)

# Kronecker product
np.kron(A, B)

# Cross product of 3-element vectors
np.cross([1, 2, 3], [4, 5, 6])  # [-3, 6, -3]
```

### multi_dot for Chain Products

Automatically finds the fastest evaluation order:

```python
A = np.random.rand(100, 2)
B = np.random.rand(2, 1000)
C = np.random.rand(1000, 5)

# Computes (A @ B) @ C or A @ (B @ C), whichever is faster
result = np.linalg.multi_dot([A, B, C])
```

## Matrix Decompositions

### Cholesky Decomposition

For symmetric positive-definite matrices:

```python
A = np.array([[4, 2], [2, 3]])
L = np.linalg.cholesky(A)
# L @ L.T == A
```

### QR Decomposition

```python
Q, R = np.linalg.qr(A)
# A = Q @ R, where Q is orthogonal and R is upper triangular
```

### Singular Value Decomposition (SVD)

```python
U, s, Vt = np.linalg.svd(A)
# A = U @ diag(s) @ Vt

# SVD without computing U and V (faster for large matrices)
s = np.linalg.svdvals(A)
```

## Eigenvalues and Eigenvectors

### General Matrices

```python
eigenvalues, eigenvectors = np.linalg.eig(A)
# A @ eigenvectors[:, i] = eigenvalues[i] * eigenvectors[:, i]

# Eigenvalues only (faster)
vals = np.linalg.eigvals(A)
```

### Symmetric/Hermitian Matrices

Use `eigh` for better numerical stability:

```python
eigenvalues, eigenvectors = np.linalg.eigh(A)
# eigenvalues are sorted in ascending order
vals = np.linalg.eigvalsh(A)  # values only
```

## Norms and Matrix Properties

```python
# Vector norms
v = np.array([3, 4])
np.linalg.norm(v)           # L2 norm → 5.0
np.linalg.norm(v, ord=1)    # L1 norm → 7.0
np.linalg.norm(v, ord=np.inf)  # max norm → 4.0

# Matrix norms
np.linalg.norm(A)           # Frobenius norm (default for 2-D)
np.linalg.norm(A, ord='fro')  # explicit Frobenius
np.linalg.norm(A, ord=2)    # spectral norm (largest singular value)

# Matrix-specific norm functions (Array API compatible)
np.linalg.matrix_norm(A, ord='fro')
np.linalg.vector_norm(v, ord=2)

# Condition number
np.linalg.cond(A)           # ratio of largest to smallest singular value

# Determinant
np.linalg.det(A)            # determinant
np.linalg.slogdet(A)        # sign and log(det) — more numerically stable

# Rank
np.linalg.matrix_rank(A)    # rank using SVD with tolerance

# Trace
np.trace(A)                 # sum of diagonal elements
```

## Solving Linear Systems

### Direct Solve

```python
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)   # x = [2, 3]
# Solves Ax = b efficiently using LU decomposition
```

### Least Squares

```python
A = np.array([[1, 1], [2, 1], [3, 1]])
b = np.array([1, 2, 3])
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
# Finds x that minimizes ||Ax - b||^2
```

### Matrix Inverse and Pseudoinverse

```python
A_inv = np.linalg.inv(A)         # inverse (use solve instead when possible)
A_pinv = np.linalg.pinv(A)       # Moore-Penrose pseudoinverse (works for singular matrices)
```

## Tensor Operations

```python
# Solve tensor equation a x = b
np.linalg.tensorsolve(a, b)

# Inverse of tensor
np.linalg.tensorinv(a)

# Matrix power
np.linalg.matrix_power(A, 3)  # A @ A @ A
```

## Discrete Fourier Transform (DFT)

NumPy's FFT module provides fast Fourier transform operations:

```python
import numpy as np

# 1-D FFT
signal = np.array([1, 2, 3, 4, 5, 6, 7, 8])
fft_result = np.fft.fft(signal)

# Inverse FFT
recovered = np.fft.ifft(fft_result)

# FFT frequency components
freqs = np.fft.fftfreq(len(signal), d=1.0)

# 2-D FFT (for images)
image_fft = np.fft.fft2(image_array)
shifted = np.fft.fftshift(image_fft)  # center zero-frequency

# Real-input FFT (faster, exploits symmetry)
rfft_result = np.fft.rfft(signal)

# FFT of specific length (zero-pads or truncates)
np.fft.fft(signal, n=16)
```

### FFT-Related Functions

```python
np.fft.ifft2      # 2-D inverse FFT
np.fft.rfft2     # 2-D real-input FFT
np.fft.irfft     # Inverse real-input FFT
np.fft.fftshift  # Shift zero-frequency to center
np.fft.ifftshift # Inverse of fftshift
np.fft.rfftfreq  # Frequencies for rfft output
```

## NumPy vs SciPy Linear Algebra

NumPy's `linalg` covers core operations. For advanced functionality, use `scipy.linalg`:

- LU decomposition (`scipy.linalg.lu`)
- Schur decomposition
- Matrix functions (expm, logm, sqrtm)
- Generalized eigenvalue problems
- Sparse linear algebra

NumPy's advantage: some functions like `np.linalg.solve` support stacked (batched) arrays, while SciPy typically accepts single matrices.
