# Universal Functions

## The @vectorize Decorator

`@vectorize` compiles a pure Python function operating on scalars into a NumPy ufunc that operates over arrays at C-speed.

### Basic Usage with Signatures (Eager Compilation)

Pass one or more type signatures to build a standard NumPy ufunc:

```python
from numba import vectorize, float64

@vectorize([float64(float64, float64)])
def f(x, y):
    return x + y
```

Multiple signatures (most specific first):

```python
from numba import vectorize, int32, int64, float32, float64
import numpy as np

@vectorize([int32(int32, int32),
            int64(int64, int64),
            float32(float32, float32),
            float64(float64, float64)])
def f(x, y):
    return x + y
```

### Dynamic Universal Functions (Lazy Compilation)

Without signatures, `@vectorize` produces a `DUFunc` that dynamically compiles for new input types:

```python
from numba import vectorize

@vectorize
def f(x, y):
    return x + y
```

### Ufunc Features

NumPy ufuncs provide automatic features:

- **Broadcasting** — Arrays of different shapes work together
- **Reduce** — Accumulate along an axis
- **Accumulate** — Running accumulation
- **Outer** — Outer product operation

```python
a = np.arange(12).reshape(3, 4)
result1 = f.reduce(a, axis=0)       # [[12, 15, 18, 21]]
result2 = f.accumulate(a)           # running sum
```

Note: Only broadcasting and reduce are supported in compiled code (not from within JIT functions).

### Target Selection

The `target` parameter controls execution backend:

- `cpu` — Single-threaded CPU (default, best for small data < 1KB, low overhead)
- `parallel` — Multi-core CPU (best for medium data < 1MB, threading adds slight delay)
- `cuda` — CUDA GPU (best for large data > 1MB and high compute intensity, memory transfer overhead)

```python
@vectorize([float64(float64, float64)], target='parallel')
def parallel_add(x, y):
    return x + y
```

Starting in Numba 0.59, the `cpu` target supports ufunc attributes and methods in compiled code: `ufunc.nin`, `ufunc.nout`, `ufunc.nargs`, `ufunc.identity`, `ufunc.signature`, `ufunc.reduce()`.

## The @guvectorize Decorator

`@guvectorize` creates generalized ufuncs that operate on higher-dimensional arrays, taking and returning arrays of differing dimensions.

### Basic Usage

Unlike `@vectorize`, gufunc functions fill an output array argument rather than returning a value:

```python
from numba import guvectorize, int64
import numpy as np

@guvectorize([(int64[:], int64, int64[:])], '(n),()->(n)')
def g(x, y, res):
    for i in range(x.shape[0]):
        res[i] = x[i] + y
```

The signature `(n),()->(n)` tells NumPy the function takes an n-element 1D array and a scalar, producing an n-element 1D array.

### Broadcasting with Gufuncs

NumPy automatically dispatches over complex input shapes:

```python
a = np.arange(6).reshape(2, 3)
result1 = g(a, 10)                        # adds 10 to each row
result2 = g(a, np.array([10, 20]))        # adds different value per row
```

### Scalar Return Values

For gufuncs with scalar output, use the `()` output layout:

```python
@guvectorize([(float64[:], float64[:], float64[:])], '(n),(n)->()',
             identity=np.inf)
def my_min(x, y, res):
    for i in range(len(x)):
        if x[i] < y[i]:
            res[0] = x[i]
            return
    res[0] = np.inf
```

### Overwriting Input Values

Use `identity=0` to allow in-place operation:

```python
@guvectorize([(float64[:], float64[:])], '(n)->(n)', identity=0)
def square(x, result):
    for i in range(len(x)):
        result[i] = x[i] * x[i]
```

### Dynamic Generalized Universal Functions

Like `@vectorize`, omit signatures for lazy compilation producing a `DUFunc`:

```python
from numba import guvectorize

@guvectorize('(n),()->(n)')
def dynamic_gufunc(x, y, res):
    for i in range(x.shape[0]):
        res[i] = x[i] + y
```

Both `@vectorize` and `@guvectorize` support `nopython=True` for strict nopython mode compilation.
