# JIT Compilation

## The @jit Decorator

The `@jit` decorator is Numba's central feature for marking functions for optimization. It translates Python bytecode combined with argument type information into optimized machine code via LLVM.

### Lazy Compilation

The recommended approach — let Numba decide when and how to optimize:

```python
from numba import jit

@jit
def f(x, y):
    return x + y
```

Compilation is deferred until the first call. Numba infers argument types at call time and generates specialized code for each type combination:

```python
>>> f(1, 2)      # compiles int64(int64, int64)
3
>>> f(1j, 2)     # compiles complex128(complex128, int64)
(2+1j)
```

### Eager Compilation

Specify an explicit signature to compile at decoration time:

```python
from numba import jit, int32

@jit(int32(int32, int32))
def f(x, y):
    return x + y
```

This compiles the single specialization immediately. No other specializations are allowed. Useful for fine-grained type control (e.g., forcing single-precision floats).

Omit the return type to let Numba infer it: `(int32, int32)` instead of `int32(int32, int32)`.

Signatures can also be strings: `"float64(float64, float64)"` or shorthand `"f8(f8, f8)"`. Multiple signatures can be passed as a list.

### @njit — Nopython Mode Alias

`@njit` is an alias for `@jit(nopython=True)`. Since Numba 0.59, nopython mode is the default for `@jit`, making `@njit` equivalent to plain `@jit`. However, `@njit` remains common in existing code as an explicit signal that the function must compile in nopython mode.

## Compilation Options

### nopython

Controls compilation mode. Default since 0.59:

```python
@jit  # same as @jit(nopython=True) or @njit
def f(x, y):
    return x + y
```

Nopython mode produces much faster code but has limitations on supported Python features. If compilation fails in nopython mode, Numba raises an error (no silent fallback to object mode).

### nogil

Releases the GIL when entering compiled functions that operate on native types:

```python
@jit(nogil=True)
def f(x, y):
    return x + y
```

Allows concurrent execution with other threads. Be aware of multi-threading pitfalls (race conditions, synchronization).

### cache

Persist compiled functions to disk to avoid recompilation:

```python
@jit(cache=True)
def f(x, y):
    return x + y
```

Limitations:
- Caching is per-main function, not per-called function
- Changes in imported modules may not invalidate the cache
- Global variables are treated as constants at compilation time

### parallel

Enable automatic parallelization of supported operations:

```python
@jit(nopython=True, parallel=True)
def f(x, y):
    return x + y
```

Must be used with `nopython=True`. See [Parallel Execution](reference/04-parallel-execution.md) for details.

### fastmath

Relax IEEE 754 compliance for additional performance:

```python
@njit(fastmath=True)
def compute(A):
    acc = 0.0
    for x in A:
        acc += np.sqrt(x)
    return acc
```

Can also accept a set of specific LLVM fast-math flags: `fastmath={'reassoc', 'nsz'}`.

### boundscheck

Enable array bounds checking (adds runtime overhead):

```python
@jit(boundscheck=True)
def f(arr):
    return arr[1000]  # raises IndexError if out of bounds
```

## Calling and Inlining Other Functions

Numba-compiled functions can call other compiled functions. Calls may be inlined at LLVM's discretion:

```python
@jit
def square(x):
    return x ** 2

@jit
def hypot(x, y):
    return math.sqrt(square(x) + square(y))
```

The `@jit` decorator must be added to any called library function, otherwise Numba generates much slower code.

## Signature Specification

Common type symbols for signatures:

- `void` — functions returning nothing
- `intp`, `uintp` — pointer-sized integers
- `intc`, `uintc` — C int-sized integers
- `int8`–`int64`, `uint8`–`uint64` — fixed-width integers
- `float32`, `float64` — single and double precision floats
- `complex64`, `complex128` — complex numbers
- Array types: `float32[:]` (1D), `int8[:, :]` (2D)
