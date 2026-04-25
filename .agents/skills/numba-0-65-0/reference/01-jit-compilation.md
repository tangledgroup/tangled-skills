# JIT Compilation with Numba

## The `@jit` Decorator

The `@jit` decorator is Numba's primary mechanism for just-in-time compilation. It compiles Python functions to machine code when first called, caching the compiled version for subsequent calls.

### Basic Usage

```python
from numba import jit
import numpy as np

@jit
def compute(a):
    trace = 0.0
    for i in range(a.shape[0]):
        trace += np.tanh(a[i, i])
    return a + trace

x = np.arange(100).reshape(10, 10)
result = compute(x)  # First call: compile + execute
result2 = compute(x) # Subsequent calls: execute from cache
```

### The `@njit` Alias

`@njit` is an alias for `@jit(nopython=True)` and is the recommended decorator for production code:

```python
from numba import njit

@njit  # Equivalent to @jit(nopython=True)
def fast_compute(a):
    return np.sin(a) ** 2 + np.cos(a) ** 2
```

## Compilation Modes

### Nopython Mode (Recommended)

In nopython mode, Numba compiles the function to run entirely without the Python interpreter:

```python
@jit(nopython=True)
def nopython_func(arr):
    total = 0.0
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

**Benefits:**
- Best performance (10-100x speedup typical)
- Static type inference
- No Python interpreter overhead
- Deterministic behavior

**Limitations:**
- Must use supported operations
- No dynamic Python features
- Type signatures must be inferable

### Object Mode (Fallback)

Object mode runs code through the Python interpreter with Numba overhead:

```python
@jit(forceobj=True)
def object_func(df):
    # Falls back to interpreter for unsupported operations
    return df.sum()
```

**When it's used:**
- When nopython compilation fails (pre-0.59.0 default behavior)
- When explicitly requested with `forceobj=True`
- For debugging and development

**Warning:** Object mode is slower than pure Python due to Numba overhead. Avoid in production code.

### Loop Lifting

Loop lifting attempts to compile loops in nopython mode while running other code in object mode:

```python
@jit(forceobj=True, looplift=True)
def mixed_func(arr):
    # This part runs in object mode
    processed = preprocess(arr)  # Unsupported operation
    
    # This loop runs in nopython mode
    total = 0.0
    for i in range(processed.shape[0]):
        total += processed[i]
    
    return total
```

## Type Inference and Signatures

### Automatic Type Inference

Numba infers types from function arguments at compile time:

```python
@njit
def typed_func(x, y):
    return x + y

result1 = typed_func(1, 2)      # Compiled for int64
result2 = typed_func(1.0, 2.0)  # Compiled for float64 (separate cache entry)
```

### Explicit Signatures

You can specify explicit type signatures:

```python
from numba import types
from numba.extending import overload

@njit(types.float64(types.float64, types.float64))
def explicit_add(x, y):
    return x + y
```

### Type Inspection

Use `numba.typeof` to inspect Numba types:

```python
from numba import typeof, njit
import numpy as np

arr = np.array([1.0, 2.0, 3.0])
print(typeof(arr))  # array(float64, 1d, C)

@njit
def inspect_types(x, y):
    print(type(x))  # Shows Numba type
    return x + y
```

## Performance Measurement

### Compilation Overhead

Always account for compilation time when benchmarking:

```python
import time
from numba import njit
import numpy as np

@njit
def benchmark_func(arr):
    return np.sum(arr ** 2)

data = np.arange(1000000, dtype=np.float64)

# WRONG: Includes compilation time
start = time.perf_counter()
benchmark_func(data)
end = time.perf_counter()
print(f"Wrong timing: {end - start}")

# CORRECT: Warm up first, then time
benchmark_func(data)  # Warm-up (compilation)
start = time.perf_counter()
benchmark_func(data)  # Timed execution (from cache)
end = time.perf_counter()
print(f"Correct timing: {end - start}")
```

### Using timeit

The `timeit` module handles compilation overhead automatically:

```python
import timeit
from numba import njit
import numpy as np

@njit
def func(arr):
    return np.sum(arr ** 2)

data = np.arange(10000, dtype=np.float64)

# timeit.repeat runs multiple iterations
times = timeit.repeat(
    'func(data)',
    globals=globals(),
    repeat=5,
    number=10
)
print(f"Best time: {min(times) / 10:.6f} seconds")
```

## Caching Compiled Functions

### Disk Cache

Enable persistent caching to avoid recompilation across sessions:

```python
@njit(cache=True)
def cached_func(arr):
    return np.sum(arr ** 2)
```

Cache directory locations:
- Linux: `~/.cache/numba/`
- Windows: `%LOCALAPPDATA%\numba\`
- macOS: `~/Library/Caches/numba/`

Configure with environment variable:
```bash
export NUMBA_CACHE_DIR=/custom/path/to/cache
```

### Cache Configuration

```python
import os
os.environ['NUMBA_DISABLE_JIT'] = '0'  # Enable JIT (default)
os.environ['NUMBA_ENABLE_CGCOMPILER'] = '1'  # Enable CG compiler
os.environ['NUMBA_DEBUG'] = '1'  # Enable debug output
```

## Supported Operations

### NumPy Functions

Most NumPy ufuncs are supported in nopython mode:

```python
@njit
def numpy_ops(arr):
    # Element-wise operations
    result = np.sin(arr) + np.cos(arr)
    result = np.exp(result) * np.log(np.abs(arr) + 1)
    
    # Reductions
    total = np.sum(arr)
    mean_val = np.mean(arr)
    min_val = np.min(arr)
    max_val = np.max(arr)
    
    return result, total, mean_val, min_val, max_val
```

### Array Creation

```python
@njit
def create_arrays(n):
    zeros_arr = np.zeros(n)
    ones_arr = np.ones(n)
    arange_arr = np.arange(n)
    linspace_arr = np.linspace(0, 1, n)
    
    return zeros_arr, ones_arr, arange_arr, linspace_arr
```

### Linear Algebra (requires SciPy)

```python
@njit
def linear_algebra(A, b):
    from numpy import linalg
    
    # Solve Ax = b
    x = linalg.solve(A, b)
    
    # Matrix multiplication
    C = np.dot(A, A.T)
    
    # Eigenvalues
    eigenvalues = linalg.eigvals(C)
    
    return x, C, eigenvalues
```

## Troubleshooting

### Common Errors

**TypingError: Cannot infer type**

```python
# Problem: Uninitialized variable
@njit
def bad_func(x):
    if x > 0:
        result = x * 2  # result not defined in else branch
    return result  # Error!

# Solution: Initialize before conditional
@njit
def good_func(x):
    result = 0.0  # Initialize
    if x > 0:
        result = x * 2
    return result
```

**TypingError: Unsupported operation**

```python
# Problem: Using unsupported Python feature
@njit
def bad_func():
    lst = [1, 2, 3]
    lst.append(4)  # Error: list.append not supported

# Solution: Use numba.typed.List
from numba import typed

@njit
def good_func():
    lst = typed.List()
    lst.extend([1, 2, 3])
    lst.append(4)  # OK
```

### Debugging Tips

Enable verbose error messages:

```bash
export NUMBA_DEBUG=1
export NUMBA_DUMP_IR=1  # Dump LLVM IR
export NUMBA_DUMP_TYPEINFER=1  # Dump type inference
```

Force object mode to isolate compilation issues:

```python
@jit(forceobj=True)
def debug_func(arr):
    # Runs in interpreter, helps identify unsupported operations
    return np.sum(arr)
```

### Getting Help

- Check error messages carefully - Numba provides detailed type information
- Use `@njit` to ensure nopython mode is being used
- Simplify code incrementally to isolate problematic operations
- Consult the [Numba Discourse Forum](https://numba.discourse.group) for community help
