---
name: scipy-1-17-1
description: Complete SciPy 1.17 toolkit for scientific computing covering optimization, integration, interpolation, eigenvalue problems, algebraic equations, differential equations, statistics, signal processing, linear algebra, FFT, sparse arrays, spatial data structures, special functions, image processing, and more. Use when building Python programs that require numerical computations, scientific analysis, engineering calculations, statistical modeling, or mathematical operations built on NumPy with highly-optimized Fortran/C/C++ backends.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.17.1"
tags:
  - scipy
  - scientific-computing
  - optimization
  - integration
  - statistics
  - linear-algebra
  - signal-processing
  - interpolation
  - fft
  - sparse-arrays
category: scientific-computing
external_references:
  - https://scipy.org/
  - https://docs.scipy.org/doc/scipy/
  - https://docs.scipy.org/doc/scipy/reference/
  - https://docs.scipy.org/doc/scipy/tutorial/
  - https://github.com/scipy/scipy
---

# SciPy 1.17

## Overview

SciPy (pronounced "Sigh Pie") is an open-source library of mathematical algorithms and convenience functions built on NumPy. It extends NumPy with significant power for mathematics, science, and engineering by providing high-level commands and classes for manipulating and visualizing data. SciPy wraps highly-optimized implementations written in Fortran, C, and C++, giving Python the flexibility of a scripting language with the speed of compiled code.

SciPy is organized into subpackages covering different scientific computing domains. The library is distributed under a liberal BSD license and developed publicly on GitHub by a vibrant, responsive community.

**Version 1.17.1** is a bug-fix release (February 2026) for the 1.17 series. It requires Python 3.11-3.14 and NumPy 1.26.4+. Key highlights of the 1.17 series include native batching support for N-dimensional arrays across many functions, ARPACK/PROPACK ported from Fortran77 to C with external PRNG support, COO sparse array indexing in nD, Rotation/RigidTransform extended to N-D arrays, new matrix_t and Logistic distributions in stats, and initial ILP64 (64-bit integer) BLAS/LAPACK support.

## When to Use

- Solving optimization problems (unconstrained, constrained, least-squares, linear programming)
- Numerical integration of functions and solving ordinary differential equations
- Interpolating data in 1D, 2D, or N-D (splines, grid interpolation, radial basis functions)
- Statistical analysis (probability distributions, hypothesis tests, descriptive statistics, QMC sampling)
- Linear algebra operations (matrix factorization, eigenvalue problems, solving linear systems)
- Signal processing (filter design, filtering, spectral analysis, B-spline transforms)
- Fourier transforms (DFT, FFT, DCT, DST, Hankel transform)
- Sparse matrix computations and graph algorithms on sparse data
- Spatial data structures (Delaunay triangulation, Voronoi diagrams, k-D trees, convex hulls)
- Special mathematical functions (Bessel, gamma, elliptic, hypergeometric, etc.)
- Multi-dimensional image processing (filtering, morphology, interpolation, object measurement)
- Clustering algorithms (vector quantization, hierarchical clustering)
- Physical and mathematical constants lookup

## Core Concepts

**Subpackage organization**: SciPy is organized into focused subpackages. Each subpackage covers a specific domain of scientific computing and should be as self-contained as possible with minimal cross-dependencies. A dependency on NumPy is always assumed.

**Import convention**: Use namespace imports rather than direct function imports:

```python
import scipy
result = scipy.optimize.curve_fit(...)
# or
from scipy import optimize
result = optimize.curve_fit(...)
```

For `scipy.io`, prefer `import scipy` because `io` conflicts with the Python stdlib module of the same name.

**Lazy loading**: SciPy uses lazy loading — modules are only loaded into memory when first accessed. This means `import scipy` is fast; submodules load on demand.

**Public API**: Names starting with underscore `_` are private. Submodules listed in the API reference are public and stable across releases. When a submodule defines `__all__`, that authoritatively defines its public interface.

**NumPy foundation**: All SciPy routines expect NumPy arrays as input and return NumPy arrays (or compatible array types). The library builds on NumPy's n-dimensional array computing capabilities.

**Array API standard**: Many SciPy functions now support the Python Array API standard, enabling dispatch to different backends including GPU arrays.

## Installation / Setup

SciPy is installed via pip or conda:

```bash
pip install scipy==1.17.1
# or
conda install scipy=1.17.1
```

Requires Python 3.11-3.14 and NumPy 1.26.4+. Pre-built binaries are available for most platforms. When building from source, Meson is used as the build system (replacing the legacy setup.py).

## Usage Examples

```python
import numpy as np
from scipy import optimize, integrate, stats, linalg

# Optimization: minimize the Rosenbrock function
def rosen(x):
    return sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)

x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
result = optimize.minimize(rosen, x0, method='BFGS')
print(result.x)  # [1. 1. 1. 1. 1.]

# Integration: integrate a Bessel function
from scipy import special
value, error = integrate.quad(lambda x: special.jv(2.5, x), 0, 4.5)
print(value)  # ~1.1178

# Statistics: fit a normal distribution to data
data = np.random.randn(1000)
loc, scale = stats.norm.fit(data)

# Linear algebra: solve Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = linalg.solve(A, b)
```

## Advanced Topics

**Optimization**: Local and global minimization, root finding, least-squares, linear programming → [Optimization](reference/01-optimize.md)

**Integration & ODEs**: Numerical quadrature, multiple integration, initial value problems, boundary value problems → [Integration](reference/02-integrate.md)

**Interpolation**: 1D splines, N-D grid interpolation, scattered data, radial basis functions → [Interpolation](reference/03-interpolate.md)

**Statistics**: Probability distributions, hypothesis tests, descriptive statistics, QMC sampling, KDE → [Statistics](reference/04-stats.md)

**Linear Algebra**: Matrix factorizations, eigenvalue problems, BLAS/LAPACK access → [Linear Algebra](reference/05-linalg.md)

**Signal Processing**: Filter design, filtering, spectral analysis, B-splines → [Signal Processing](reference/06-signal.md)

**Fourier Transforms**: FFT, DCT, DST, Hankel transform → [Fourier Transforms](reference/07-fft.md)

**Sparse Arrays**: Sparse formats, sparse linear algebra, compressed sparse graphs → [Sparse Arrays](reference/08-sparse.md)

**Spatial Data Structures**: Delaunay triangulation, Voronoi diagrams, k-D trees, rotations → [Spatial](reference/09-spatial.md)

**Special Functions**: Bessel, gamma, elliptic, hypergeometric, and more → [Special Functions](reference/10-special.md)

**Additional Subpackages**: FFTPack (legacy), Image Processing (ndimage), File I/O (io), Clustering, Constants, Differentiation, ODR, Datasets → [Additional Modules](reference/11-additional-modules.md)
