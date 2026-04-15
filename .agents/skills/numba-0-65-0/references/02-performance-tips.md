# Performance Tips for Numba

## Nopython Mode is Essential

Always use nopython mode for best performance. Since Numba 0.59.0, this is the default for `@jit`, but be explicit with `@njit`:

```python
from numba import njit, jit
import numpy as np

# Recommended
@njit
def fast_func(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2

# Also fine (nopython is default since 0.59.0)
@jit
def also_fast(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2

# Avoid: explicit object mode fallback
@jit(nopython=False)
def slow_func(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2
```

## Loops vs Vectorization

Numba excels at compiling loops. Vectorized NumPy and explicit loops perform similarly when JIT-compiled:

```python
from numba import njit
import numpy as np

@njit
def vectorized_version(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2

@njit
def loop_version(x):
    r = np.empty_like(x)
    n = len(x)
    for i in range(n):
        r[i] = np.cos(x[i]) ** 2 + np.sin(x[i]) ** 2
    return r

# Both run at nearly identical speeds when compiled!
```

**Performance comparison (10M elements on Intel i7-4790):**

| Function | @njit | Execution time |
|----------|-------|----------------|
| `vectorized_version` | No | 5.81s |
| `vectorized_version` | Yes | 0.66s |
| `loop_version` | No | 25.2s |
| `loop_version` | Yes | 0.67s |

## Fast Math Optimizations

Relax IEEE 754 compliance for faster execution when exact precision isn't required:

```python
from numba import njit
import numpy as np

@njit(fastmath=False)
def strict_sum(A):
    acc = 0.0
    for x in A:
        acc += np.sqrt(x)
    return acc

@njit(fastmath=True)
def fast_sum(A):
    acc = 0.0
    for x in A:
        acc += np.sqrt(x)
    return acc

# fast_sum can be 2x faster but may have slight precision differences
```

### Fine-Grained Fast Math Flags

Select specific optimizations:

```python
@njit(fastmath={'reassoc'})
def allow_reassociation(x, y):
    # Allows (a + b) + c != a + (b + c) for performance
    return (x - y) + y

@njit(fastmath={'nsz'})
def allow_no_signed_zeros(x):
    # Allows -0.0 == 0.0 optimization
    return x * 0.0

@njit(fastmath={'arcp', 'contract', 'fast', 'nsz', 'noassociative', 'nornan', 'ninf', 'reassoc'})
def all_fastmath_ops(x):
    # All fast math optimizations enabled
    return np.arcsin(x)
```

**Fast math flags:**
- `arcp`: Approximate reciprocal
- `contract`: FMA (fused multiply-add) contraction
- `fast`: All fast math flags
- `nsz`: No signed zeros
- `noassociative`: Disable associativity
- `nornan`: No ordered NaN comparisons
- `ninf`: No signed infinities
- `reassoc`: Reassociation of operations

## Parallel Execution

### Automatic Parallelization

Enable automatic parallelization for supported operations:

```python
from numba import njit
import numpy as np

@njit(parallel=True)
def auto_parallel(x):
    # Numba automatically parallelizes array operations
    return np.cos(x) ** 2 + np.sin(x) ** 2

# ~5x faster than single-threaded on 4-core CPU
```

### Explicit Parallel Loops with prange

Use `prange` for explicit parallel loop declaration:

```python
from numba import njit, prange
import numpy as np

@njit(parallel=True)
def parallel_reduction(A):
    acc = 0.0
    for i in prange(len(A)):  # prange enables parallelization
        acc += np.sqrt(A[i])
    return acc

@njit(parallel=True, fastmath=True)
def parallel_reduction_fast(A):
    acc = 0.0
    for i in prange(len(A)):
        acc += np.sqrt(A[i])
    return acc

# parallel_reduction_fast can be 6-10x faster than serial version
```

### Supported Reductions

Numba automatically detects these reduction patterns:

```python
@njit(parallel=True)
def multiple_reductions(A):
    sum_val = 0.0
    prod_val = 1.0
    min_val = A[0]
    max_val = A[0]
    
    for i in prange(len(A)):
        sum_val += A[i]      # Sum reduction
        prod_val *= A[i]     # Product reduction
        min_val = min(min_val, A[i])  # Min reduction
        max_val = max(max_val, A[i])  # Max reduction
    
    return sum_val, prod_val, min_val, max_val
```

**Supported operators:** `+=`, `+`, `-=` , `-`, `*=`, `*`, `/=`, `/`, `max()`, `min()`

### Parallel Configuration

Control the number of threads:

```python
import os
os.environ['NUMBA_NUM_THREADS'] = '4'  # Use 4 threads

from numba import njit, prange
import numpy as np

@njit(parallel=True)
def threaded_func(A):
    return sum(np.sqrt(A[i]) for i in prange(len(A)))
```

## Intel SVML (Short Vector Math Library)

Intel's SVML provides optimized transcendental functions. Install via conda:

```bash
conda install intel-cmplr-lib-rt
```

**Performance comparison (100M elements):**

| @njit kwargs | SVML | Execution time |
|--------------|------|----------------|
| None | No | 5.95s |
| None | Yes | 2.26s |
| `fastmath=True` | No | 5.97s |
| `fastmath=True` | Yes | 1.8s |
| `parallel=True` | No | 1.36s |
| `parallel=True` | Yes | 0.624s |
| `parallel=True, fastmath=True` | No | 1.32s |
| `parallel=True, fastmath=True` | Yes | 0.576s |

SVML provides two accuracy modes:
- **High accuracy** (default): Within 1 ULP
- **Low accuracy** (with `fastmath=True`): Within 4 ULP

## Linear Algebra Optimization

Numba's linear algebra relies on SciPy's LAPACK/BLAS bindings. Use optimized builds:

```python
from numba import njit
import numpy as np

@njit
def linear_algebra_ops(A, b):
    from numpy import linalg
    
    # These use underlying BLAS/LAPACK
    x = linalg.solve(A, b)
    det = linalg.det(A)
    eigvals = linalg.eigvals(A)
    qr = linalg.qr(A)
    svd = linalg.svd(A)
    
    return x, det, eigvals, qr, svd
```

**Recommendation:** Use Anaconda's SciPy (built with Intel MKL) for best performance.

## Memory Layout and Access Patterns

### Contiguous Arrays

Ensure arrays are contiguous for optimal performance:

```python
from numba import njit
import numpy as np

@njit
def process_contiguous(arr):
    # Fast: sequential memory access
    total = 0.0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            total += arr[i, j]
    return total

# Create contiguous arrays
arr_c = np.ascontiguousarray(np.random.rand(1000, 1000))  # C-order
arr_f = np.asfortranarray(np.random.rand(1000, 1000))     # Fortran-order
```

### Avoid Strided Access

```python
from numba import njit
import numpy as np

@njit
def strided_access_bad(arr, stride):
    # Slow: non-contiguous memory access
    total = 0.0
    for i in range(0, arr.shape[0], stride):
        total += arr[i]
    return total

@njit
def strided_access_good(arr, stride):
    # Better: work on contiguous slice
    sliced = arr[::stride]
    return np.sum(sliced)
```

## Compilation Caching

Enable disk caching to avoid recompilation:

```python
from numba import njit

@njit(cache=True)
def cached_expensive_function(arr):
    # Complex computation that takes time to compile
    result = np.zeros_like(arr)
    for i in range(100):  # Many iterations
        result = np.sin(result + arr) * np.cos(arr)
    return result
```

Cache is automatically managed in:
- Linux: `~/.cache/numba/`
- Windows: `%LOCALAPPDATA%\numba\`
- macOS: `~/Library/Caches/numba/`

## Threading Layers

Numba supports multiple threading backends:

### OpenMP (default on Linux/Windows)

```python
from numba import njit, config

# Check threading layer
print(config.THREADING_LAYER)  # 'openmp', 'tbb', or 'workqueue'

@njit(parallel=True)
def openmp_parallel(arr):
    return np.sum(arr ** 2)
```

### TBB (Threading Building Blocks)

```python
import os
os.environ['NUMBA_THREADING_LAYER'] = 'tbb'

from numba import njit

@njit(parallel=True)
def tbb_parallel(arr):
    return np.sum(arr ** 2)
```

## Profiling and Benchmarking

### Use timeit for Accurate Timing

```python
import timeit
from numba import njit
import numpy as np

@njit
def func_to_benchmark(arr):
    return np.sin(arr) ** 2 + np.cos(arr) ** 2

data = np.arange(1000000, dtype=np.float64)

# Warm up compilation
func_to_benchmark(data)

# Benchmark with timeit
setup_code = "from __main__ import func_to_benchmark, data"
stmt = "func_to_benchmark(data)"

times = timeit.repeat(stmt, setup=setup_code, repeat=5, number=10)
print(f"Best time: {min(times) / 10:.6f} seconds")
```

### Profile with cProfile

```python
import cProfile
from numba import njit

@njit
def profiled_func(arr):
    return np.sum(arr ** 2)

profiler = cProfile.Profile()
profiler.enable()

for _ in range(100):
    profiled_func(np.arange(10000))

profiler.disable()
profiler.print_stats(sort='cumulative')
```

## Common Performance Pitfalls

### Object Mode Fallback

Always verify you're running in nopython mode:

```python
from numba import njit, typeof

@njit
def check_mode(arr):
    # If this compiles, you're in nopython mode
    return np.sum(arr)

# Force compilation and check
result = check_mode(np.array([1.0, 2.0, 3.0]))
print(f"Compiled successfully: {result}")
```

### Python Function Calls

Avoid calling Python functions from compiled code:

```python
from numba import njit

def python_helper(x):
    return x * 2

@njit
def bad_pattern(arr):
    total = 0.0
    for i in range(len(arr)):
        total += python_helper(arr[i])  # Slow: Python call overhead
    return total

@njit
def good_pattern(arr):
    total = 0.0
    for i in range(len(arr)):
        total += arr[i] * 2  # Fast: inline computation
    return total
```

### Dynamic Data Structures

Use typed containers instead of Python lists/dicts:

```python
from numba import njit, typed

@njit
def with_typed_list():
    lst = typed.List()
    for i in range(100):
        lst.append(i * 2.0)
    return sum(lst)

@njit
def with_typed_dict():
    d = typed.Dict()
    for i in range(100):
        d[i] = i * 2.0
    return sum(d.values())
```

## Environment Variables

Configure Numba behavior:

```bash
# Disable JIT compilation (for debugging)
export NUMBA_DISABLE_JIT=1

# Enable debug output
export NUMBA_DEBUG=1

# Dump LLVM IR
export NUMBA_DUMP_IR=1

# Dump type inference
export NUMBA_DUMP_TYPEINFER=1

# Set number of threads
export NUMBA_NUM_THREADS=4

# Set threading layer
export NUMBA_THREADING_LAYER=openmp  # or 'tbb' or 'workqueue'

# Enable cache
export NUMBA_CACHE_DIR=/path/to/cache

# Disable OpenMP/TBB backends at build time
export NUMBA_DISABLE_OPENMP=1
export NUMBA_DISABLE_TBB=1
```
