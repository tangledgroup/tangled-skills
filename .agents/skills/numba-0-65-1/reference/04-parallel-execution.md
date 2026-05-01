# Parallel Execution

## Automatic Parallelization

Setting `parallel=True` on `@jit` or `@njit` enables a transformation pass that automatically parallelizes supported operations. Numba identifies parallelizable operations and fuses adjacent ones into kernels that run in parallel across CPU cores (no GIL).

```python
from numba import njit
import numpy as np

@njit(parallel=True)
def logistic_regression(Y, X, w, iterations):
    for i in range(iterations):
        w -= np.dot(((1.0 / (1.0 + np.exp(-Y * np.dot(X, w))) - 1.0) * Y), X)
    return w
```

No code changes needed beyond the decorator option — Numba fuses array operations of matching dimensions into parallel kernels automatically.

## Supported Operations

### Element-wise Array Operations

All unary and binary operators (`+`, `-`, `*`, `/`, `%`, `|`, `&`, `^`, `<<`, `>>`, `**`, `//`, `==`, `!=`, `<`, `<=`, `>`, `>=`), NumPy ufuncs, and user-defined DUFuncs through `@vectorize`.

### Reduction Functions

`np.sum`, `np.prod`, `np.min`, `np.max`, `np.argmin`, `np.argmax`, and array methods `.mean()`, `.var()`, `.std()`.

### Array Creation

`np.zeros`, `np.ones`, `np.arange`, `np.linspace`, and several random functions.

### Dot Product

`np.dot` between matrix-vector or vector-vector. Other cases use Numba's default (non-parallel) implementation.

### Array Assignment

Slice and boolean array assignment where the target and value shapes are compatible.

### functools.reduce

Supported for parallel reductions on 1D NumPy arrays (initial value argument is mandatory).

## Explicit Parallel Loops with prange

Use `numba.prange` instead of `range` to mark loops for parallel execution:

```python
from numba import njit, prange
import numpy as np

@njit(parallel=True)
def parallel_sum(A):
    s = 0.0
    for i in prange(A.shape[0]):
        s += A[i]
    return s
```

### Reduction Support

Numba automatically infers reductions when a variable is updated using its previous value with supported operators: `+=`, `+`, `-=`, `-`, `*=`, `*`, `/=`, `/`, `max()`, `min()`.

For `max()` and `min()`, the reduction variable should hold the identity value before entering the prange loop.

### Induction Variable Type

With `parallel=True`, if the range is strictly positive, the induction variable is typed as `uint64` (vs `int64` for regular `range`). This can affect type coercion in mixed operations.

### Race Condition Pitfalls

The compiler may not detect all race conditions. Be careful when reducing into array slices or elements:

```python
# WRONG — race condition: multiple threads write to same element
@njit(parallel=True)
def wrong(x):
    n = x.shape[0]
    y = np.zeros(4)
    for i in prange(n):
        y[i % 4] += x[i]   # concurrent writes to same index
    return y

# OK — whole array reduction is safe
@njit(parallel=True)
def correct(x):
    n = x.shape[0]
    y = np.zeros(4)
    for i in prange(n):
        y += x[i]           # all threads reduce into whole array
    return y
```

Only prange loops with a single entry and single exit block can be parallelized. Exceptional control flow (assertions) in the loop can prevent parallelization.

## Threading Layers

Three threading backends are available:

- **tbb** — Intel TBB (fork-safe and thread-safe, requires `tbb` package)
- **omp** — OpenMP (requires OpenMP runtime)
- **workqueue** — Built-in work-sharing scheduler (always available)

### Setting the Threading Layer

Via environment variable:
```bash
NUMBA_THREADING_LAYER=tbb
```

Or programmatically (must be before any parallel compilation):
```python
from numba import config
config.THREADING_LAYER = 'tbb'
```

### Safe Parallel Execution Modes

- `default` — No specific safety guarantee (default)
- `safe` — Both fork-safe and thread-safe (requires TBB)
- `forksafe` — Fork-safe library
- `threadsafe` — Thread-safe library

### Threading Layer Priority

Change search order with `NUMBA_THREADING_LAYER_PRIORITY`:
```bash
NUMBA_THREADING_LAYER_PRIORITY="omp tbb workqueue"
```

Or programmatically:
```python
config.THREADING_LAYER_PRIORITY = ["omp", "tbb", "workqueue"]
```

### Thread Count

Control the number of threads:
```bash
OMP_NUM_THREADS=4          # for omp layer
TBB_NUM_THREADS=4          # for tbb layer
NUMBA_NUM_THREADS=4        # universal setting
```

Or programmatically:
```python
import numba.threading as thr
thr.set_num_threads(4)
```

### Getting Thread ID

```python
from numba import threading_layer, thread_id

@njit(parallel=True)
def show_thread_ids(n):
    ids = np.zeros(n, dtype=np.int64)
    for i in prange(n):
        ids[i] = thread_id()
    return ids
```

## Unsupported Operations in Parallel Contexts

- Mutating lists, sets, or dictionaries (not threadsafe)
- `//=` reduction operator (order-dependent)
- Exceptional control flow within prange loops
- Broadcasting between arrays of mixed dimensionality
- Reduction across selected dimensions
