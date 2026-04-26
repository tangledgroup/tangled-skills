---
name: numpy-2-4-4
description: Complete toolkit for NumPy 2.4.4, the fundamental package for scientific computing with Python, providing powerful n-dimensional arrays, comprehensive mathematical functions, random number generators, linear algebra routines, Fourier transforms, and more with support for modern Python typing and Array API standard compatibility. Use when building Python programs that require numerical array computing, scientific data processing, matrix operations, statistical analysis, or high-performance vectorized computation replacing Python loops.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.4.4"
tags:
  - numpy
  - arrays
  - scientific-computing
  - linear-algebra
  - data-science
  - numerical-computing
category: library
external_references:
  - https://numpy.org/
  - https://data-apis.org/array-api/
  - https://github.com/numpy/numpy
  - https://numpy.org/doc/stable/numpy_2_0_migration_guide.html
  - https://numpy.org/doc/stable/reference/random/index.html
  - https://numpy.org/neps/nep-0050-new-type-promotion.html
  - https://numpy.org/neps/nep-0052-public-naming.html
  - https://numpy.org/doc/stable/
  - https://github.com/numpy/numpy/tree/v2.4.4
---

# NumPy 2.4.4

## Overview

NumPy (Numerical Python) is the fundamental package for scientific computing in Python. It provides a powerful n-dimensional array object (`ndarray`), derived objects (masked arrays, matrices), and an assortment of routines for fast operations on arrays including mathematical, logical, shape manipulation, sorting, selecting, I/O, discrete Fourier transforms, basic linear algebra, basic statistical operations, random simulation, and much more.

NumPy 2.4.4 is part of the NumPy 2.x series (released June 2024 as a major breaking-change release). It supports Python 3.11 through 3.14, implements the Array API standard 2024.12 compatibility in its main namespace, and continues work on free-threaded Python support, user dtypes, and annotation improvements.

Key features of NumPy 2.x:
- New type promotion rules (NEP 50) preserving scalar precision consistently
- Cleaned Python API namespace (NEP 52) with ~100 members moved or removed
- Default integer is now 64-bit on all 64-bit systems (`np.intp` equivalent)
- Array API standard compatibility in the main namespace
- C-API changes including opaque `PyArray_Descr` struct and increased max dimensions to 64
- SIMD optimizations via CPU dispatch
- Multi-phase C extension initialization (PEP 489)

## When to Use

- Building numerical computing applications requiring n-dimensional array operations
- Performing matrix algebra, linear system solving, eigenvalue decomposition, or SVD
- Implementing vectorized computations to replace slow Python loops
- Working with scientific data: signal processing, image analysis, statistics
- Generating random numbers from various probability distributions
- Reading/writing binary and text data in array format
- Building foundations for data science pipelines (pandas, scikit-learn, etc. depend on NumPy)
- Interfacing with GPU/distributed array libraries (CuPy, Dask, JAX use NumPy-compatible APIs)
- Implementing Array API standard-compatible code for backend-agnostic array computing

## Core Concepts

### The ndarray — N-dimensional Array

The `ndarray` is the central data structure in NumPy. It represents a homogeneous, rectangular grid of values with fixed size and uniform data type. Key attributes:

- `ndim` — number of dimensions (axes)
- `shape` — tuple of sizes along each axis
- `size` — total number of elements
- `dtype` — data type of elements
- `itemsize` — size in bytes of each element

```python
import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
a.ndim    # 2
a.shape   # (2, 3)
a.size    # 6
a.dtype   # dtype('int64')
```

### Broadcasting

Broadcasting describes how NumPy handles arrays of different shapes in arithmetic operations. The smaller array is conceptually "stretched" across the larger one. Rules: dimensions are compared from trailing to leading; they are compatible if equal or one is 1. Missing leading dimensions are treated as size 1.

```python
a = np.array([[0, 0, 0], [10, 10, 10]])
b = np.array([1, 2, 3])
a + b  # array([[1, 2, 3], [11, 12, 13]])
```

### Universal Functions (ufuncs)

Ufuncs operate element-by-element on arrays, supporting broadcasting, type casting, and multiple outputs. Examples: `np.add`, `np.multiply`, `np.sin`, `np.exp`. They support keyword arguments like `out` (output buffer), `where` (boolean mask), and `dtype` (computation precision).

### Data Types (dtype)

NumPy supports 24 fundamental scalar types organized in a hierarchy: `generic` → `number` → `integer`/`floating`/`complexfloating`. Common types: `int8`-`int64`, `uint8`-`uint64`, `float16`/`float32`/`float64`, `complex64`/`complex128`, `bool_`, `str_`, `bytes_`, `datetime64`, `timedelta64`. Structured dtypes allow C-like records with named fields.

## Usage Examples

### Array Creation

```python
import numpy as np

# From Python sequences
a = np.array([1, 2, 3, 4])
b = np.array([[1, 2], [3, 4]])

# From shape/value
zeros = np.zeros((3, 4))
ones = np.ones((2, 2), dtype=np.int32)
empty = np.empty((5,))        # uninitialized — fastest
full = np.full((3, 3), 7.5)
identity = np.eye(4)

# Ranges
seq = np.arange(0, 10, 2)     # [0, 2, 4, 6, 8]
spaced = np.linspace(0, 1, 5) # [0., 0.25, 0.5, 0.75, 1.]
log_spaced = np.logspace(0, 2, 3)  # [1., 10., 100.]
```

### Indexing and Slicing

```python
a = np.arange(12).reshape(3, 4)

# Basic indexing
a[0]          # first row
a[1, 2]       # element at row 1, col 2 → 6
a[:, ::2]     # every other column

# Fancy indexing
a[[0, 2], [1, 3]]   # elements (0,1) and (2,3)

# Boolean indexing
mask = a > 5
a[mask]              # all elements > 5
```

### Linear Algebra

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])

# Matrix multiplication via @ operator
C = A @ A.T

# Solve Ax = b
x = np.linalg.solve(A, b)

# Eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

# SVD
U, s, Vt = np.linalg.svd(A)
```

### Random Number Generation

```python
import numpy as np

rng = np.random.default_rng(seed=42)

uniform = rng.random((3, 3))                    # [0, 1) uniform
normal = rng.standard_normal(1000)              # standard normal
integers = rng.integers(low=0, high=10, size=5) # random integers
choice = rng.choice([10, 20, 30], size=3, replace=False)
```

## Advanced Topics

**Array Fundamentals**: Deep dive into ndarray creation, indexing patterns, views vs copies, structured arrays, and memory layout → See [Array Fundamentals](reference/01-array-fundamentals.md)

**Data Types and Type Promotion**: Complete dtype hierarchy, structured dtypes, NEP 50 type promotion rules, casting modes, and NumPy 2.0 changes → See [Data Types and Type Promotion](reference/02-data-types.md)

**Universal Functions and Broadcasting**: Ufunc internals, generalized ufuncs, output buffers, where masks, broadcasting rules with examples → See [Universal Functions and Broadcasting](reference/03-ufuncs-and-broadcasting.md)

**Linear Algebra and Fourier Transforms**: BLAS/LAPACK-backed routines, matrix decompositions, eigenvalue problems, norm computation, DFT operations → See [Linear Algebra and Fourier Transforms](reference/04-linear-algebra.md)

**Random Number Generation**: Generator API, bit generators (PCG64, MT19937), seeding strategies, parallel generation, distribution methods → See [Random Number Generation](reference/05-random.md)

**I/O and Memory Mapping**: Binary formats (.npy/.npz), text file I/O, memory-mapped arrays, string formatting → See [I/O and Memory Mapping](reference/06-io.md)

**Array API Standard and Interoperability**: Array API 2024.12 compliance, `__array_namespace_info__`, entry points, duck array protocols → See [Array API Standard and Interoperability](reference/07-array-api.md)

**NumPy 2.x Migration Guide**: NEP 50 type promotion changes, NEP 52 namespace cleanup, C-API changes, default integer on Windows, Ruff NPY201 rule → See [NumPy 2.x Migration Guide](reference/08-migration.md)
