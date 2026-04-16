---
name: numba-0-65-0
description: Just-in-time compiler for numerical Python using LLVM, providing @jit, @vectorize, @guvectorize, @stencil, @jitclass, and @cfunc decorators for CPU/GPU acceleration with automatic parallelization support.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.65.0"
tags:
  - jit
  - compiler
  - numpy
  - performance
  - gpu
  - cuda
category: compilation
external_references:
  - https://github.com/numba/numba/tree/0.65.0
  - https://numba.readthedocs.io/en/stable/index.html
---

# Numba 0.65.0

## Overview

Numba is an open-source, NumPy-aware optimizing compiler for Python that uses the LLVM compiler project to generate machine code from Python syntax. It can compile a large subset of numerically-focused Python, including many NumPy functions, and provides support for automatic parallelization of loops, GPU-accelerated code generation, and creation of ufuncs and C callbacks.

**Key capabilities:**
- Just-in-time (JIT) compilation with `@jit` and `@njit` decorators
- Universal function creation with `@vectorize` and `@guvectorize`
- CUDA GPU acceleration with `@cuda.jit`
- Stencil computations for finite difference operations
- Compiled Python classes with `@jitclass`
- C callback functions with `@cfunc`
- Automatic parallelization across CPU cores
- Ahead-of-time (AOT) compilation with `pycc`

## When to Use

Use Numba when:
- **Numerical code needs acceleration**: Functions using NumPy arrays, mathematical operations, and loops
- **Loop-heavy computations**: Code with nested loops over numerical data that would benefit from native machine code execution
- **Array operations**: Element-wise operations, reductions, and array transformations on large datasets
- **GPU acceleration needed**: CUDA-enabled code for massive parallelization on NVIDIA GPUs (compute capability 5.0+)
- **C interoperability**: Creating callbacks for C/C++ libraries or interfacing with native code
- **Performance-critical paths**: Hot loops in scientific computing, data analysis, or machine learning pipelines

**Do NOT use Numba for:**
- Code heavily using pandas DataFrames (Numba doesn't understand pandas)
- General-purpose Python applications without numerical focus
- Code requiring extensive Python object manipulation
- Applications where compilation time is critical (first call includes JIT overhead)

## Core Concepts

### Compilation Modes

**Nopython mode** (default since 0.59.0): Compiles functions to run entirely without the Python interpreter, providing best performance. Use `@njit` or `@jit(nopython=True)`.

**Object mode**: Falls back to running code through the Python interpreter when nopython compilation fails. Slower but more permissive. Avoid for production code.

**Loop lifting**: With `@jit(forceobj=True, looplift=True)`, Numba attempts to compile loops in nopython mode while running other code in object mode.

### Type Inference

Numba uses static type inference to determine variable types at compile time. Functions are compiled for specific argument type signatures and cached for reuse. Subsequent calls with the same types use the cached compiled version.

### Supported Operations

- NumPy array operations (element-wise arithmetic, comparisons)
- NumPy ufuncs (`np.sin`, `np.cos`, `np.exp`, etc.)
- Array creation (`np.zeros`, `np.ones`, `np.arange`, `np.linspace`)
- Reductions (`np.sum`, `np.prod`, `np.min`, `np.max`, `np.mean`, `np.var`, `np.std`)
- Linear algebra operations (requires SciPy)
- Python builtins for numeric types
- Typed containers (`numba.typed.List`, `numba.typed.Dict`)

## Installation / Setup

### Conda Installation (Recommended)

```bash
# Basic installation
conda install numba

# With CUDA support (CUDA 12)
conda install -c conda-forge cuda-nvcc cuda-nvrtc "cuda-version>=12.0"

# With CUDA support (CUDA 11)
conda install -c conda-forge cudatoolkit "cuda-version>=11.2,<12.0"

# Optional: Intel SVML for faster math functions
conda install intel-cmplr-lib-rt
```

### Pip Installation

```bash
pip install numba
```

Binary wheels include bundled LLVM components; no separate LLVM installation needed.

### Platform Support

| Platform | Status |
|----------|--------|
| Linux x86_64 | ✅ Supported |
| Linux arm64/aarch64 | ✅ Supported |
| Windows 10+ (64-bit) | ✅ Supported |
| macOS 11.0+ (M1/Arm64) | ✅ Supported |
| NVIDIA GPUs (compute capability 5.0+) | ✅ Supported |
| BSD | ⚠️ Unofficial support |

## Usage Examples

### Basic JIT Compilation

```python
from numba import njit
import numpy as np

@njit
def sum_array(arr):
    """Sum all elements using a loop."""
    total = 0.0
    for i in range(arr.shape[0]):
        total += arr[i]
    return total

data = np.arange(1000000, dtype=np.float64)
result = sum_array(data)  # First call compiles, subsequent calls use cache
```

### Vectorized Operations

```python
from numba import vectorize
import numpy as np

@vectorize(['float64(float64, float64)', 'float32(float32, float32)'])
def add_elements(a, b):
    """Element-wise addition as a NumPy ufunc."""
    return a + b

arr1 = np.array([1.0, 2.0, 3.0])
arr2 = np.array([4.0, 5.0, 6.0])
result = add_elements(arr1, arr2)  # [5.0, 7.0, 9.0]

# Ufuncs support broadcasting and reduction
total = add_elements.reduce(arr1 + arr2)  # Sum all elements
```

### Parallel Execution

```python
from numba import njit, prange
import numpy as np

@njit(parallel=True)
def parallel_sum(arr):
    """Parallel array summation using prange."""
    total = 0.0
    for i in prange(arr.shape[0]):  # prange enables parallelization
        total += arr[i]
    return total

# Automatic parallelization (no prange needed)
@njit(parallel=True)
def auto_parallel(arr):
    """Numba auto-parallelizes array operations."""
    return np.sin(arr) ** 2 + np.cos(arr) ** 2
```

### GPU Computing with CUDA

```python
from numba import cuda
import numpy as np

@cuda.jit
def vector_add(x, y, result):
    """Add two vectors on GPU."""
    idx = cuda.grid(1)
    if idx < x.size:
        result[idx] = x[idx] + y[idx]

# Prepare data
x = np.arange(1000, dtype=np.float64)
y = np.ones(1000, dtype=np.float64)
result = np.zeros(1000, dtype=np.float64)

# Launch kernel
threads_per_block = 256
blocks_per_grid = (x.size + threads_per_block - 1) // threads_per_block
vector_add[blocks_per_grid, threads_per_block](x, y, result)
```

See [CUDA GPU Programming](references/04-cuda-programming.md) for comprehensive GPU guidance.

## Advanced Topics

### Stencil Computations

For finite difference operations and image processing:

```python
from numba import stencil
import numpy as np

@stencil
def laplacian_kernel(a):
    """2D Laplacian stencil."""
    return (a[0, 1] + a[0, -1] + a[1, 0] + a[-1, 0] - 4 * a[0, 0])

array = np.random.rand(100, 100)
result = laplacian_kernel(array)
```

### JIT Classes

Compile Python classes for performance:

```python
from numba import njit
from numba.experimental import jitclass
import numpy as np

spec = [
    ('center', np.float64),
    ('spread', np.float64),
]

@jitclass(spec)
class Gaussian1D:
    def __init__(self, center, spread):
        self.center = center
        self.spread = spread
    
    def pdf(self, x):
        from math import exp, pi, sqrt
        coef = 1.0 / (sqrt(2 * pi) * self.spread)
        return coef * exp(-0.5 * ((x - self.center) / self.spread) ** 2)

gaussian = Gaussian1D(0.0, 1.0)
```

### C Callbacks

Create functions callable from C/C++:

```python
from numba import cfunc
import numpy as np

@cfunc("float64(float64, float64)")
def add_callback(x, y):
    """C callback for use with native libraries."""
    return x + y

# Pass to C library via ctypes
handle = add_callback.ctypes
```

See [C Callback Functions](references/03-c-functions.md) for advanced patterns.

### Performance Optimization

- **Use nopython mode**: Always prefer `@njit` over `@jit` for production code
- **Enable fastmath**: Use `fastmath=True` when IEEE 754 compliance isn't required
- **Parallel execution**: Add `parallel=True` for multi-core CPU utilization
- **Intel SVML**: Install `intel-cmplr-lib-rt` for optimized transcendental functions
- **Profile first**: Use profiling to identify hot spots before optimization

See [Performance Tips](references/02-performance-tips.md) for detailed guidance.

## References

### Official Documentation

- **Numba Homepage**: https://numba.pydata.org
- **Documentation**: https://numba.readthedocs.io/en/stable/
- **GitHub Repository**: https://github.com/numba/numba
- **Discourse Forum**: https://numba.discourse.group
- **Gitter Chat**: https://gitter.im/numba/numba

### Reference Files

- [JIT Compilation Details](references/01-jit-compilation.md) - `@jit`, `@njit`, compilation modes, type inference
- [Performance Tips](references/02-performance-tips.md) - Optimization strategies, fastmath, parallelization, SVML
- [C Callback Functions](references/03-c-functions.md) - `@cfunc` decorator, C interoperability, ctypes integration
- [CUDA GPU Programming](references/04-cuda-programming.md) - GPU kernels, memory management, device functions
- [Advanced Features](references/05-advanced-features.md) - Stencils, jitclasses, vectorize, typed containers

### Related Skills

- `numpy-2-4-4` - NumPy array operations and mathematical functions
- `scipy-1-17-1` - Scientific computing with SciPy integration
