# Performance Tips for NumPy 2.4.4

## Overview

NumPy performance depends on:

- **Vectorization**: Avoid Python loops, use ufuncs
- **Memory layout**: Contiguous arrays are faster
- **Data types**: Choose appropriate precision
- **Algorithm choice**: Some operations have faster alternatives
- **Caching and reusing**: Minimize allocations

## Vectorization

### Replace Loops with Ufuncs

```python
import numpy as np
import timeit

# SLOW: Python loop
def slow_sum_squares(arr):
    result = 0
    for x in arr:
        result += x * x
    return result

# FAST: Vectorized operation
def fast_sum_squares(arr):
    return np.sum(arr ** 2)

# Even faster: single ufunc call
def fastest_sum_squares(arr):
    return np.dot(arr, arr)

arr = np.random.rand(1000000)
print(timeit.timeit(lambda: slow_sum_squares(arr), number=10))   # ~2-3 seconds
print(timeit.timeit(lambda: fast_sum_squares(arr), number=1000)) # ~0.1 seconds
print(timeit.timeit(lambda: fastest_sum_squares(arr), number=1000))  # ~0.05 seconds
```

### Element-wise Operations

```python
# SLOW: Loop with conditionals
def slow_threshold(arr, threshold=0.5):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        if arr[i] > threshold:
            result[i] = 1
        else:
            result[i] = 0
    return result

# FAST: Boolean indexing
def fast_threshold(arr, threshold=0.5):
    result = np.zeros_like(arr)
    result[arr > threshold] = 1
    return result

# FASTEST: Use ufunc directly
def fastest_threshold(arr, threshold=0.5):
    return (arr > threshold).astype(np.int32)
```

### Avoid Python Callable in Ufuncs

```python
# SLOW: Using Python function with np.vectorize
@np.vectorize
def slow_func(x):
    return x * 2 + 1

result = slow_func(arr)  # Slow! vectorize is just a convenience wrapper

# FAST: Use ufunc directly
result = arr * 2 + 1  # Vectorized automatically

# For custom operations, use numba or cython instead of np.vectorize
```

## Memory Layout and Access Patterns

### Contiguous Arrays

```python
import numpy as np

# Create contiguous array (default, fastest)
contiguous = np.array([[1, 2, 3], [4, 5, 6]])
print(contiguous.flags['C_CONTIGUOUS'])  # True

# Non-contiguous array (slower access)
strided = contiguous[:, ::2]  # Every other column
print(strided.flags['C_CONTIGUOUS'])  # False

# Make contiguous (if needed for performance)
contiguous_copy = np.ascontiguousarray(strided)
```

### Row vs Column Access

```python
import numpy as np
import timeit

matrix = np.random.rand(1000, 1000)

# FAST: Row access (C-contiguous, memory order)
row_access = timeit.timeit(lambda: matrix[500, :], number=10000)

# SLOWER: Column access (strided)
col_access = timeit.timeit(lambda: matrix[:, 500], number=10000)

# For column-heavy operations, use Fortran order
matrix_f = np.asfortranarray(matrix)
col_access_fast = timeit.timeit(lambda: matrix_f[:, 500], number=10000)
```

### Memory Order in Operations

```python
# Specify order based on access pattern
row_major = np.zeros((1000, 1000), order='C')   # Optimize for row access
col_major = np.zeros((1000, 1000), order='F')   # Optimize for column access

# Matrix multiplication is optimized regardless of layout
A = np.random.rand(1000, 1000)
B = np.random.rand(1000, 1000)
C = A @ B  # NumPy chooses optimal algorithm
```

## Data Type Optimization

### Choose Appropriate Precision

```python
import numpy as np

# float64 (default) - 8 bytes per element
arr64 = np.random.rand(1000000).astype(np.float64)
print(arr64.nbytes / 1024 / 1024)  # ~8 MB

# float32 - 4 bytes per element (often sufficient)
arr32 = np.random.rand(1000000).astype(np.float32)
print(arr32.nbytes / 1024 / 1024)  # ~4 MB (50% memory savings)

# int8 for categorical data instead of int64
categories = np.array([0, 1, 2, 3] * 250000, dtype=np.int8)  # 1 MB vs 8 MB
```

### Avoid Unnecessary Type Promotion

```python
# SLOW: Implicit promotion to object dtype
arr_mixed = np.array([1, 2.5, '3'])  # dtype=object (slow!)

# FAST: Keep homogeneous types
arr_int = np.array([1, 2, 3], dtype=np.int64)
arr_float = np.array([1.0, 2.5, 3.0], dtype=np.float64)

# Be explicit in operations to avoid promotion
result = np.add(arr32, arr32, dtype=np.float32)  # Stay in float32
```

### Use Structured Arrays for Records

```python
# SLOW: List of dicts or objects
records_obj = [{'x': 1.0, 'y': 2.0}, {'x': 3.0, 'y': 4.0}]

# FAST: Structured array
dtype = [('x', np.float64), ('y', np.float64)]
records_struct = np.array([(1.0, 2.0), (3.0, 4.0)], dtype=dtype)

# Access is fast and vectorized
x_coords = records_struct['x']  # Fast array access
```

## Pre-allocation and Reuse

### Pre-allocate Arrays

```python
# SLOW: Growing array with append
def slow_accumulate(n):
    result = np.array([])
    for i in range(n):
        result = np.append(result, compute_value(i))
    return result

# FAST: Pre-allocate and fill
def fast_accumulate(n):
    result = np.empty(n)
    for i in range(n):
        result[i] = compute_value(i)
    return result

# Even faster: vectorize the computation
def fastest_accumulate(n):
    indices = np.arange(n)
    return vectorized_compute(indices)
```

### Reuse Memory with out Parameter

```python
import numpy as np

# Creates new array each time (memory allocation overhead)
result1 = np.add(arr1, arr2)
result2 = np.multiply(result1, arr3)
result3 = np.subtract(result2, arr4)

# Reuses pre-allocated memory
output = np.empty_like(arr1)
np.add(arr1, arr2, out=output)
np.multiply(output, arr3, out=output)
np.subtract(output, arr4, out=output)

# For complex expressions, use multiple outputs
out1, out2 = np.empty_like(arr1), np.empty_like(arr1)
np.add(arr1, arr2, out=out1)
np.multiply(out1, arr3, out=out2)
```

### In-place Operations

```python
# Creates temporary arrays
result = (arr1 + arr2) * (arr3 - arr4)

# In-place operations (less memory)
temp = arr1.copy()
np.add(temp, arr2, out=temp)
np.subtract(arr3, arr4, out=temp2)
np.multiply(temp, temp2, out=result)

# For simple cases, use augmented assignment
arr += other_arr  # In-place addition
arr *= scalar     # In-place multiplication
```

## Broadcasting Optimization

### Use Broadcasting Instead of Replication

```python
# SLOW: Explicit replication
matrix = np.random.rand(1000, 1000)
vector = np.random.rand(1000)
replicated = np.tile(vector, (1000, 1))  # Creates 1000x copy!
result = matrix + replicated

# FAST: Broadcasting
result = matrix + vector[np.newaxis, :]  # No memory overhead

# Even more explicit with reshape
result = matrix + vector.reshape(1, -1)
```

### Optimize Broadcast Shapes

```python
# Less efficient broadcasting (more dimensions to align)
A = np.random.rand(1, 100, 1)
B = np.random.rand(100, 1)
result = A + B  # Works but creates (1, 100, 100) intermediate

# More efficient (reduce dimensions first if possible)
A_flat = A.squeeze()  # Shape (100,)
B_flat = B.squeeze()  # Shape (100,)
result = (A_flat[:, np.newaxis] + B_flat).reshape(1, 100, 100)
```

## Algorithm Choice

### Use Built-in Functions Over Manual Implementation

```python
import numpy as np

# SLOW: Manual convolution
def slow_convolve(signal, kernel):
    result = np.zeros(len(signal) + len(kernel) - 1)
    for k in range(len(kernel)):
        for s in range(len(signal)):
            result[k + s] += signal[s] * kernel[k]
    return result

# FAST: Use FFT-based convolution
result = np.convolve(signal, kernel)  # Uses optimized algorithms

# For large arrays, FFT is even faster
result = np.fft.irfft(np.fft.rfft(signal, n=n) * np.fft.rfft(kernel, n=n))
```

### Choose Right Sorting Algorithm

```python
arr = np.random.rand(10000)

# Default: Quicksort (fast average, O(n²) worst case)
sorted1 = np.sort(arr)

# For guaranteed O(n log n): Mergesort
sorted2 = np.sort(arr, kind='mergesort')

# For partially sorted data: Timsort
sorted3 = np.sort(arr, kind='timsort')

# For just k smallest/largest: Use partition
k_smallest = np.partition(arr, k)[:k]  # O(n) average vs O(n log n) for full sort
```

### Matrix Operations Optimization

```python
import numpy as np

A = np.random.rand(1000, 1000)
x = np.random.rand(1000)

# SLOW: Explicit inverse
x_sol = np.linalg.inv(A) @ b  # Computes full inverse (expensive!)

# FAST: Direct solve
x_sol = np.linalg.solve(A, b)  # Uses LU decomposition (faster, more stable)

# For multiple right-hand sides, solve is even better
B = np.random.rand(1000, 10)
X = np.linalg.solve(A, B)  # Solve all at once (optimized)
```

## Advanced Techniques

### Using numba for Complex Loops

```python
from numba import njit
import numpy as np

@njit
def fast_elementwise(arr):
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = complex_computation(arr[i])
    return result

# Compiles to machine code, runs at C speed
```

### Using Cython for Performance-Critical Code

```python
# In .pyx file
import numpy as np
cimport numpy as cnp

def cython_sum(cnp.ndarray[cnp.float64_t, ndim=1] arr):
    cdef double total = 0.0
    cdef int i
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

### Memory-Mapped Arrays for Large Data

```python
import numpy as np

# For arrays larger than RAM
filename = 'large_array.dat'
mm = np.memmap(filename, dtype='float32', mode='w+', shape=(1000000, 1000000))

# Process in chunks
chunk_size = 10000
for i in range(0, mm.shape[0], chunk_size):
    chunk = mm[i:i+chunk_size]
    process(chunk)

del mm  # Flushes to disk
```

### Using stride_tricks for Zero-Copy Views

```python
from numpy.lib.stride_tricks import sliding_window_view

arr = np.arange(10)
window_size = 3

# Create sliding window view (zero-copy!)
windows = sliding_window_view(arr, window_size)
# windows: [[0, 1, 2], [1, 2, 3], ..., [7, 8, 9]]

# Much faster than loop-based approach
sums = windows.sum(axis=1)  # Vectorized sum over all windows
```

## Profiling and Debugging

### Finding Performance Bottlenecks

```python
import numpy as np
from timeit import timeit

# Simple timing
def my_function(arr):
    return np.sum(arr ** 2)

arr = np.random.rand(1000000)
time = timeit(lambda: my_function(arr), number=1000)
print(f"Average time: {time/1000*1000:.2f} ms")

# Use cProfile for detailed profiling
import cProfile
cProfile.run('my_function(arr)')

# Use line_profiler for line-by-line analysis
# Install: pip install line_profiler
# Decorate function: @profile
```

### Memory Profiling

```python
import numpy as np
import tracemalloc

tracemalloc.start()

arr = np.random.rand(1000000)
result = arr ** 2 + np.sin(arr)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

## Common Performance Anti-patterns

### Anti-pattern 1: Converting to Python Lists

```python
# SLOW: Convert to list, process, convert back
arr = np.random.rand(1000000)
result = np.array([x**2 for x in arr.tolist()])

# FAST: Stay in NumPy
result = arr ** 2
```

### Anti-pattern 2: Using object dtype

```python
# SLOW: Object array (loses all NumPy optimizations)
arr_obj = np.array([1, 2, 3], dtype=object)
result = arr_obj * 2  # Uses Python multiplication

# FAST: Use numeric dtype
arr_num = np.array([1, 2, 3], dtype=np.int64)
result = arr_num * 2  # Uses vectorized ufunc
```

### Anti-pattern 3: Repeated concatenation

```python
# SLOW: Concatenate in loop
result = np.array([])
for i in range(1000):
    result = np.concatenate([result, new_data])

# FAST: Collect and concatenate once
results = []
for i in range(1000):
    results.append(new_data)
result = np.concatenate(results)

# BEST: Pre-allocate if total size known
result = np.empty(total_size)
for i, idx in enumerate(indices):
    result[idx] = new_data
```

## Summary Checklist

- ✅ **Vectorize**: Replace loops with ufuncs
- ✅ **Pre-allocate**: Avoid growing arrays
- ✅ **Reuse memory**: Use `out` parameter
- ✅ **Choose dtypes**: Use float32 when possible
- ✅ **Contiguous arrays**: Ensure C-contiguous for row access
- ✅ **Broadcasting**: Instead of explicit replication
- ✅ **Built-in functions**: Over manual implementations
- ✅ **solve() over inv()**: For linear systems
- ✅ **Partition over sort**: For top-k operations
- ✅ **Profile first**: Find actual bottlenecks

## Tools and Resources

- **numba**: JIT compilation for Python loops
- **Cython**: Compile Python to C extensions
- **line_profiler**: Line-by-line profiling
- **memory_profiler**: Memory usage analysis
- **py-spy**: Sampling profiler for production
- **NumPy benchmarks**: https://github.com/numpy/numpy/tree/main/benchmarks
