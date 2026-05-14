# Performance Tips

## Nopython Mode

The default and most important optimization. Always aim for nopython mode:

```python
from numba import njit  # @njit = @jit(nopython=True)

@njit
def compute(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2
```

Since Numba 0.59, `@jit` defaults to nopython mode. Prior to that, `@njit` or `@jit(nopython=True)` was required.

## Loops

Numba handles explicit loops as well as vectorized NumPy operations:

```python
@njit
def ident_np(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2

@njit
def ident_loops(x):
    r = np.empty_like(x)
    n = len(x)
    for i in range(n):
        r[i] = np.cos(x[i]) ** 2 + np.sin(x[i]) ** 2
    return r
```

Both run at nearly identical speeds with `@njit`. Without the decorator, the vectorized version is orders of magnitude faster.

## Fastmath

Relax IEEE 754 compliance for performance gains (can be 2x speedup):

```python
@njit(fastmath=True)
def do_sum_fast(A):
    acc = 0.0
    for x in A:
        acc += np.sqrt(x)
    return acc
```

Select specific optimizations: `fastmath={'reassoc', 'nsz'}`. Note that fastmath can change results with infinity and NaN values.

## Parallel=True

Enable automatic parallelization for supported array operations:

```python
@njit(parallel=True)
def ident_parallel(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2
```

Combine with `prange` for explicit parallel loops:

```python
@njit(parallel=True, fastmath=True)
def do_sum_parallel_fast(A):
    n = len(A)
    acc = 0.0
    for i in prange(n):
        acc += np.sqrt(A[i])
    return acc
```

## Intel SVML

When `intel-cmplr-lib-rt` is present, Numba automatically uses Intel's Short Vector Math Library for optimized transcendental functions. With `fastmath=True`, lower-accuracy (but faster) versions are used. High accuracy (default) is within 1 ULP; low accuracy is within 4 ULP.

## Linear Algebra

With `scipy` installed, Numba compiles `numpy.linalg` functions. For best performance with BLAS/LAPACK operations, ensure an optimized BLAS library is available in the environment.

## General Tips

- **Profile first** — Use real data to guide optimization
- **Compile only critical paths** — Factor performance-critical code into separate functions
- **Use explicit types when needed** — Eager compilation with signatures avoids runtime type inference overhead
- **Cache compiled functions** — `@jit(cache=True)` eliminates recompilation on restart
- **Avoid object mode** — It adds overhead with minimal speedup
- **Watch for type unification failures** — All code paths must return compatible types
