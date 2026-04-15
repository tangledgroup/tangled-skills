# Parallelism with OpenMP

## Introduction

Cython supports parallel computation through OpenMP, allowing you to utilize multiple CPU cores for CPU-bound tasks. The primary mechanism is `prange` (parallel range), which automatically parallelizes loops.

**Key concepts:**
- `prange` - Parallel loop construct
- `nogil` - Release the Global Interpreter Lock
- Thread-local variables - Automatic handling
- Reductions - Automatic summing of partial results
- Scheduling strategies - Static, dynamic, guided, runtime

## Basic Parallel Loops

### Simple Parallel Sum

```python
from cython.parallel import prange

def parallel_sum(double[:] arr):
    """Sum array elements in parallel"""
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Automatic reduction (sum) and GIL release
    for i in prange(arr.shape[0], nogil=True):
        total += arr[i]
    
    return total
```

**Key points:**
- `nogil=True` is required - releases GIL so threads can run in parallel
- `total += arr[i]` is automatically detected as a reduction operation
- Each thread maintains its own copy of `total`, combined at the end

### Parallel Element-wise Operation

```python
def parallel_add(double[:] a, double[:] b, double[:] result):
    """Add two arrays in parallel"""
    cdef Py_ssize_t i, n = a.shape[0]
    
    for i in prange(n, nogil=True):
        result[i] = a[i] + b[i]
```

Each iteration is independent, making this ideal for parallelization.

## Compilation Requirements

OpenMP requires special compiler flags:

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "parallel_module",
    ["parallel_module.pyx"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"]
)

setup(ext_modules=cythonize([ext], compiler_directives={'language_level': 3}))
```

**For MSVC (Windows):**
```python
extra_compile_args=["/openmp"],
extra_link_args=[]  # OpenMP is built into MSVC
```

## Thread-Local Variables

### Last Private Variables

Variables assigned (not accumulated) in parallel loops are "last private":

```python
def find_last_value(int[:] arr):
    """Find the last non-zero value"""
    cdef int result = 0
    cdef Py_ssize_t i
    
    for i in prange(arr.shape[0], nogil=True):
        if arr[i] != 0:
            result = arr[i]  # Last private - final value from last iteration
    
    return result
```

**Warning:** The "last" iteration is not deterministic! Use only when order doesn't matter.

### Private Variables

Variables declared inside the loop are automatically thread-local:

```python
def parallel_compute(double[:] input, double[:] output):
    cdef Py_ssize_t i, n = input.shape[0]
    
    for i in prange(n, nogil=True):
        cdef double temp  # Private to each thread
        temp = input[i] * 2.0
        temp = temp ** 2
        output[i] = temp
```

## Reduction Operations

### Automatic Reductions

Cython detects common reduction patterns:

```python
def parallel_statistics(double[:] arr):
    cdef double sum_val = 0.0
    cdef double min_val = arr[0]
    cdef double max_val = arr[0]
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in prange(n, nogil=True):
        sum_val += arr[i]        # Reduction (sum)
        if arr[i] < min_val:     # Reduction (min)
            min_val = arr[i]
        if arr[i] > max_val:     # Reduction (max)
            max_val = arr[i]
    
    return sum_val / n, min_val, max_val
```

**Supported reductions:**
- `+=` (sum)
- `-=` (difference)
- `*=` (product)
- `&=`, `|=`, `^=` (bitwise)
- `&&=`, `||=` (logical)
- Min/max assignments

### Manual Reductions with OpenMP API

For custom reductions:

```python
from cython.parallel import parallel, single, master, num_threads

def parallel_with_custom_reduction(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i, n = arr.shape[0]
    
    with parallel(nogil=True):
        # Custom reduction logic here
        for i in prange(n):
            # Thread-local computation
            pass
    
    return total
```

## Scheduling Strategies

### Static Scheduling (Default)

Iterations divided evenly among threads:

```python
def static_schedule(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Equal chunks assigned upfront
    for i in prange(arr.shape[0], nogil=True, schedule='static'):
        total += expensive_computation(arr[i])
```

**Best for:** Uniform iteration costs

### Dynamic Scheduling

Threads request chunks as needed:

```python
def dynamic_schedule(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Threads get chunks as they finish
    for i in prange(arr.shape[0], nogil=True, 
                   schedule='dynamic', chunksize=10):
        total += variable_cost_computation(arr[i])
```

**Best for:** Varying iteration costs

### Guided Scheduling

Large chunks initially, decreasing to 1:

```python
def guided_schedule(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Large chunks first, smaller at end
    for i in prange(arr.shape[0], nogil=True, 
                   schedule='guided', chunksize=1):
        total += arr[i]
```

**Best for:** Unknown workload distribution

### Runtime Scheduling

Determined by environment variable:

```python
def runtime_schedule(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # OMP_SCHEDULE env var controls behavior
    for i in prange(arr.shape[0], nogil=True, schedule='runtime'):
        total += arr[i]
```

Set with: `export OMP_SCHEDULE="dynamic,10"`

## Thread Control

### Specifying Thread Count

```python
def fixed_threads(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Use exactly 4 threads
    for i in prange(arr.shape[0], nogil=True, num_threads=4):
        total += arr[i]
    
    return total
```

**Environment variable:** `OMP_NUM_THREADS=4`

### Conditional Parallelism

Only parallelize when beneficial:

```python
def conditional_parallel(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i, n = arr.shape[0]
    
    # Only use threads if array is large enough
    for i in prange(n, nogil=True, 
                   use_threads_if=n > 10000):
        total += arr[i]
    
    return total
```

## Parallel Matrix Operations

### Matrix Multiplication

```python
def parallel_matmul(double[:,:] a, double[:,:] b, double[:,:] result):
    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t rows_a = a.shape[0]
    cdef Py_ssize_t cols_a = a.shape[1]
    cdef Py_ssize_t cols_b = b.shape[1]
    
    # Parallelize over rows
    for i in prange(rows_a, nogil=True):
        for j in range(cols_b):
            result[i, j] = 0.0
            for k in range(cols_a):
                result[i, j] += a[i, k] * b[k, j]
```

### Nested Parallelism (Advanced)

```python
def nested_parallel(double[:,:] matrix):
    cdef Py_ssize_t i, j
    
    # Outer loop parallel
    for i in prange(matrix.shape[0], nogil=True):
        # Inner loop also parallel (use fewer threads)
        for j in prange(matrix.shape[1], num_threads=2):
            matrix[i, j] *= 2.0
```

**Warning:** Nested parallelism can cause thread oversubscription. Use carefully.

## GIL Management

### Understanding the GIL

Python's Global Interpreter Lock prevents true parallelism. Cython allows releasing it:

```python
def cpu_bound_work(int n) nogil:
    """Function that runs without GIL"""
    cdef int i, result = 0
    
    for i in range(n):
        result += expensive_calc(i)
    
    return result
```

### Reacquiring the GIL

Sometimes you need Python functionality inside a `nogil` block:

```python
def mixed_gil_nogil(int n):
    cdef int i, result = 0
    
    # Release GIL for computation
    with nogil:
        for i in range(n):
            result += compute(i)
        
        # Temporarily acquire GIL for Python call
        with gil:
            print(f"Progress: {i}/{n}")
    
    return result
```

### Functions That Require GIL

```python
@cython.with_gil
cdef int python_calling_function():
    """Ensures GIL is held"""
    return len(some_python_list())
```

## Performance Considerations

### When to Use Parallelism

**Good candidates:**
- CPU-bound computations
- Independent iterations
- Large data sets (>10,000 elements)
- Vector/matrix operations

**Poor candidates:**
- I/O bound operations
- Small arrays (overhead dominates)
- Dependent iterations
- Memory-bandwidth limited code

### Overhead Awareness

```python
def benchmark_parallel(double[:] arr):
    """Understand when parallel helps"""
    
    # Sequential version
    cdef double seq_total = 0.0
    cdef Py_ssize_t i
    for i in range(arr.shape[0]):
        seq_total += arr[i]
    
    # Parallel version
    cdef double par_total = 0.0
    for i in prange(arr.shape[0], nogil=True):
        par_total += arr[i]
    
    return seq_total, par_total
```

**Rule of thumb:** Parallel overhead ~1-2ms. Only parallelize if computation >10x overhead.

### False Sharing

Avoid having threads write to nearby memory:

```python
# Bad - threads may write to cache line together
cdef double[4] thread_results  # False sharing risk

# Good - pad to avoid false sharing
cdef double[64] thread_results  # Each thread gets separate cache line
```

## Debugging Parallel Code

### Thread Identification

```python
from cython.parallel import get_thread_id, num_threads

def debug_parallel(double[:] arr):
    cdef Py_ssize_t i, n = arr.shape[0]
    cdef int tid, nthreads
    
    with parallel(nogil=True):
        tid = get_thread_id()
        nthreads = num_threads()
        
        for i in prange(n):
            # Can log which thread processed which iteration
            pass
```

### Deterministic Testing

For testing, force single-threaded execution:

```python
# Set before running tests
import os
os.environ['OMP_NUM_THREADS'] = '1'
```

## Common Patterns

### Map Pattern

```python
def parallel_map(double[:] input, double[:] output):
    cdef Py_ssize_t i, n = input.shape[0]
    
    for i in prange(n, nogil=True):
        output[i] = transform(input[i])
```

### Reduce Pattern

```python
def parallel_reduce(double[:] arr):
    cdef double result = 0.0
    cdef Py_ssize_t i
    
    for i in prange(arr.shape[0], nogil=True):
        result += arr[i]
    
    return result
```

### Scan/Prefix Sum (Advanced)

```python
def parallel_prefix_sum(int[:] input, int[:] output):
    """Parallel prefix sum using block-based approach"""
    cdef Py_ssize_t i, block_size = 1024
    
    # Each thread does local prefix sum
    for i in prange(input.shape[0], nogil=True):
        if i == 0:
            output[i] = input[i]
        else:
            output[i] = input[i] + output[i - 1]
    
    # Note: This is sequential! True parallel prefix sum is complex
```

See [SKILL.md](../SKILL.md) for overview and [Optimization Reference](06-optimization.md) for performance tuning.
