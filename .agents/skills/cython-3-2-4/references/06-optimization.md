# Optimization and Performance Tuning

## Profiling Before Optimizing

### Using cProfile

```python
# In your Cython code
# cython: profile=True, linetrace=True

def my_function():
    # ... code to profile
    pass
```

Build and profile:
```bash
python -m cProfile -o profile.out script.py
python -m pstats profile.out
(pstats) sort_calls  # Sort by cumulative time
(pstats) stats 10    # Show top 10 functions
```

### Using cython's annotate

```bash
# Generate annotated HTML
cython -a module.pyx

# Open module.html in browser
# Yellow = Python code, White = C code
# Darker yellow = more Python overhead
```

## Compiler Directives

### Performance-Critical Directives

```python
# File-wide optimization
# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

def fast_loop(int[:] arr):
    cdef int i, total = 0
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

**Key directives:**

| Directive | Default | Performance Impact | Safety Impact |
|-----------|---------|-------------------|---------------|
| `boundscheck` | True | High (10-50%) | Critical - segfault risk |
| `wraparound` | True | Medium (5-20%) | High - negative indices broken |
| `cdivision` | False | Low (1-5%) | Medium - no ZeroDivisionError |
| `embedsignature` | False | None | None - just signature display |
| `auto_cpdef` | False | Medium | None - changes calling convention |

### Local Directive Overrides

```python
# File-wide: unsafe for speed
# cython: boundscheck=False, wraparound=False

def unsafe_fast(int[:] arr, int i):
    return arr[i]  # No bounds check!

@cython.boundscheck(True)
def safe_access(int[:] arr, int i):
    return arr[i]  # Bounds checked despite file default
```

## Type Optimization Strategies

### Static Typing Everywhere

**Slow - Dynamic typing:**
```python
def slow_sum(arr):
    total = 0  # Python object
    for x in arr:  # Python iteration
        total += x  # Python addition
    return total
```

**Fast - Static typing:**
```python
def fast_sum(int[:] arr):
    cdef int total = 0, i  # C integers
    for i in range(arr.shape[0]):  # C loop
        total += arr[i]  # C addition
    return total
```

**Typical speedup:** 10-100x for tight loops

### Function Return Types

```python
# Infer return type (may be Python object)
def unclear_return(int x):
    return x * 2

# Explicit return type (C int)
cdef int typed_return(int x):
    return x * 2

# For public functions
cpdef int cpdef_typed(int x):
    return x * 2
```

### Local Variable Optimization

```python
def optimized_locals(double[:] arr):
    # Pre-declare all locals with types
    cdef Py_ssize_t i, n = arr.shape[0]
    cdef double total = 0.0, temp
    
    # Reuse variables instead of creating new ones
    for i in range(n):
        temp = arr[i] * 2.0
        total += temp
    
    return total
```

## Memory Access Patterns

### Contiguous Memoryviews

**Faster - Contiguous:**
```python
def contiguous_sum(double[::1] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

**Slower - Strided:**
```python
def strided_sum(double[:] arr):  # May be non-contiguous
    # Same code, but potentially slower due to cache misses
    pass
```

### Loop Ordering for Cache

**Bad - Cache unfriendly:**
```python
def bad_order(double[:,:] matrix):
    cdef Py_ssize_t i, j
    for j in range(matrix.shape[1]):  # Outer loop over columns
        for i in range(matrix.shape[0]):  # Inner loop over rows
            matrix[i, j] *= 2.0  # Jumping between rows
```

**Good - Cache friendly:**
```python
def good_order(double[:,:] matrix):
    cdef Py_ssize_t i, j
    for i in range(matrix.shape[0]):  # Outer loop over rows
        for j in range(matrix.shape[1]):  # Inner loop over columns
            matrix[i, j] *= 2.0  # Sequential memory access
```

### Loop Unrolling

Cython can auto-unroll small loops:

```python
# Small fixed-size loop (may be unrolled)
cdef int sum_small(int[:] arr):
    cdef int total = 0, i
    for i in range(4):  # Likely to be unrolled
        total += arr[i]
    return total
```

For larger loops, manual unrolling:

```python
cdef int unrolled_sum(int[:] arr):
    cdef int total = 0, i, n = arr.shape[0]
    
    # Process 4 elements at a time
    for i in range(0, n - 3, 4):
        total += arr[i] + arr[i+1] + arr[i+2] + arr[i+3]
    
    # Handle remainder
    for i in range(n - 3, n):
        total += arr[i]
    
    return total
```

## Avoiding Python Overhead

### Minimizing Python API Calls

**Slow - Many Python calls:**
```python
def slow_python_calls(list items):
    result = []
    for item in items:
        result.append(str(item))  # Python method call each iteration
    return result
```

**Fast - Pre-allocate and use C:**
```python
def fast_c_operations(int[:] input, int[:] output):
    cdef Py_ssize_t i, n = input.shape[0]
    for i in range(n):
        output[i] = input[i] * 2  # No Python calls
```

### String Operations

**Slow - String concatenation:**
```python
def slow_concat(list parts):
    result = ""
    for part in parts:
        result += str(part)  # Creates new string each time!
    return result
```

**Fast - Join or buffer:**
```python
from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_FromStringAndSize

def fast_concat(int[:] data):
    # Use memory operations for binary data
    cdef char *buffer = <char *>malloc(data.shape[0])
    memcpy(buffer, &data[0], data.shape[0])
    # ... process buffer
```

### Attribute Access

**Slow - Repeated attribute access:**
```python
def slow_attr_access(object obj, int n):
    total = 0
    for i in range(n):
        total += obj.value  # Attribute lookup each time
        obj.counter += 1
    return total
```

**Fast - Cache attributes:**
```python
def fast_attr_access(MyClass obj, int n):
    cdef int total = 0, i
    cdef int *value_ptr = &obj.value
    cdef int *counter_ptr = &obj.counter
    
    for i in range(n):
        total += obj.value  # Still Python access but less lookups
        obj.counter += 1
    return total
```

## Algorithm Optimization

### Early Exit Patterns

```python
def find_if_matches(int[:] arr, int target):
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        if arr[i] == target:
            return i  # Early exit - don't process rest
    
    return -1  # Not found
```

### Branch Prediction

```python
# Good - predictable branch
def filter_positive(int[:] arr, int[:] output):
    cdef Py_ssize_t i, out_idx = 0
    
    for i in range(arr.shape[0]):
        if arr[i] > 0:  # Predictable if data is sorted
            output[out_idx] = arr[i]
            out_idx += 1
    
    return out_idx
```

### Avoiding Branches (Branchless Code)

```python
# With branch
cdef int abs_with_branch(int x):
    if x < 0:
        return -x
    return x

# Branchless (may be faster on some CPUs)
cdef int abs_branchless(int x):
    cdef int mask = x >> 31  # All 1s if negative, 0s if positive
    return (x + mask) ^ mask
```

## Parallelism Optimization

See [Parallelism Reference](04-parallelism.md) for details. Key points:

```python
from cython.parallel import prange

def optimized_parallel(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i, n = arr.shape[0]
    
    # Only parallelize if worth it
    for i in prange(n, nogil=True, 
                   use_threads_if=n > 10000,
                   schedule='static'):
        total += expensive_computation(arr[i])
    
    return total
```

## Memory Optimization

### Avoiding Temporary Arrays

**Slow - Creates temporaries:**
```python
import numpy as np

def slow_temporaries(np.ndarray arr):
    return np.sum(arr * 2.0 + 1.0)  # Two temporary arrays!
```

**Fast - Single pass:**
```python
def fast_single_pass(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    for i in range(arr.shape[0]):
        total += arr[i] * 2.0 + 1.0
    
    return total
```

### Reusing Memory

```python
cdef class MemoryPool:
    cdef double[:] buffer
    cdef int size
    
    def __init__(self, int initial_size):
        self.size = initial_size
        self.buffer = [0.0] * initial_size
    
    def process(self, double[:] input):
        # Reuse existing buffer instead of allocating new
        cdef Py_ssize_t i
        for i in range(input.shape[0]):
            self.buffer[i] = input[i] * 2.0
        
        return self.buffer[:input.shape[0]]
```

## Fused Types for Generic Code

```python
ctypedef fused real_types:
    float
    double

ctypedef fused int_types:
    short
    int
    long

# Generates specialized versions for each type
cpdef real_types squared(real_types x):
    return x * x

cpdef int_types absolute(int_types x):
    if x < 0:
        return -x
    return x
```

**Benefits:**
- Single code path for multiple types
- Each specialization is fully optimized
- No runtime type checking overhead

## Common Pitfalls

### Unnecessary Object Creation

```python
# Bad - creates Python object each iteration
def bad_object_creation(int n):
    total = 0
    for i in range(n):
        total += int(i * 2)  # Creates Python int object
    
    return total

# Good - stays in C land
def good_c_arithmetic(int n):
    cdef int total = 0, i, temp
    for i in range(n):
        temp = i * 2  # C arithmetic
        total += temp
    
    return total
```

### Inefficient Loop Patterns

```python
# Bad - Python-range iteration
def bad_loop(int n):
    total = 0
    for i in range(n):  # 'i' is Python object
        total += i
    
    return total

# Good - typed loop variable
def good_loop(int n):
    cdef int total = 0, i
    for i in range(n):  # 'i' inferred as C int if declared
        total += i
    
    return total
```

### Missing Compiler Optimizations

```python
# May not be optimized without hints
cdef int compute(int x):
    return x * (2 + 2)  # Could be x * 4

# Help the compiler
cdef const int FACTOR = 4

cdef int optimized_compute(int x):
    return x * FACTOR  # Compiler can optimize better
```

## Benchmarking

### Simple Timing

```python
import time

def benchmark(func, *args, n_iter=1000):
    start = time.perf_counter()
    
    for _ in range(n_iter):
        func(*args)
    
    end = time.perf_counter()
    return (end - start) / n_iter

# Usage
avg_time = benchmark(slow_sum, large_array)
print(f"Average: {avg_time*1000:.3f} ms")
```

### Timeit Module

```python
import timeit

# Compare implementations
time_cython = timeit.timeit(
    'fast_sum(arr)',
    setup='from __main__ import fast_sum, arr',
    number=1000
)

time_python = timeit.timeit(
    'slow_sum(arr)',
    setup='from __main__ import slow_sum, arr',
    number=1000
)

print(f"Speedup: {time_python/time_cython:.2f}x")
```

See [SKILL.md](../SKILL.md) for overview and [Troubleshooting Guide](10-troubleshooting.md) for debugging slow code.
