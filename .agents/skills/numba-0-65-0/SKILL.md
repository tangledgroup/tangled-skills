---
name: numba-0-65-0
description: Just-in-time compiler for Python that translates numerical and array-oriented code into optimized machine code using LLVM. Supports @jit, @njit, @vectorize, @guvectorize, @stencil, @jitclass, and @cfunc decorators with CPU parallelization (prange), SIMD vectorization, NVIDIA CUDA GPU targets, typed containers, C interoperability via ctypes/CFFI, and ahead-of-time compilation. Use when accelerating Python numerical loops, creating NumPy-compatible ufuncs, parallelizing array operations, compiling classes for performance, generating C callbacks, or targeting GPU execution from pure Python.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.65.0"
tags:
  - jit
  - compiler
  - llvm
  - numba
  - numpy
  - performance
  - parallelization
  - gpu
  - cuda
category: compiler
external_references:
  - https://github.com/numba/numba/tree/0.65.0
  - https://github.com/numba/numba
  - https://gitter.im/numba/numba
  - https://numba.discourse.group
  - https://numba.pydata.org
  - https://numba.readthedocs.io/en/stable/
  - https://numba.readthedocs.io/en/stable/index.html
---

# Numba 0.65.0

## Overview

Numba is an open-source just-in-time (JIT) compiler that translates a subset of Python and NumPy code into fast machine code. It uses the LLVM compiler infrastructure to generate optimized native code at runtime, achieving performance comparable to C, C++, or Fortran without switching languages or interpreters.

Key capabilities:

- **JIT compilation** — On-the-fly code generation at import time or runtime via decorators
- **Native CPU code** — Code tailored to specific CPU capabilities (SSE, AVX, AVX-512)
- **GPU acceleration** — NVIDIA CUDA support for parallel GPU algorithms from pure Python
- **NumPy integration** — Deep support for NumPy arrays, ufuncs, and broadcasting
- **Parallel execution** — Automatic multi-core parallelization with `parallel=True` and explicit `prange` loops
- **SIMD vectorization** — Automatic translation of loops into vector instructions

Numba works best on code that uses NumPy arrays, mathematical operations, and loops. It is not suited for code heavy in pandas, string manipulation, or general-purpose Python features.

## When to Use

- Accelerating performance-critical numerical loops in Python
- Creating high-performance NumPy-compatible universal functions (ufuncs)
- Parallelizing array computations across multiple CPU cores
- Writing stencil operations for image processing, PDE solving, and spatial computations
- Compiling Python classes with typed fields for use in JIT-compiled code
- Generating C callbacks for interfacing with native libraries
- Targeting NVIDIA CUDA GPUs from pure Python
- Building ahead-of-time compiled extension modules

## Core Concepts

### Compilation Modes

Numba operates in two compilation modes:

- **Nopython mode** — The default and recommended mode. Compiles the function to run entirely without the Python interpreter, producing the fastest code. Use `@njit` (alias for `@jit(nopython=True)`) or plain `@jit`.
- **Object mode** — Falls back to running code through the Python interpreter when nopython compilation fails. Use only when necessary; it provides minimal speedup and adds overhead.

### Type System

Numba uses a fine-grained type system rather than Python's dynamic types. Types are inferred from argument types at call time. Key numeric types include `int8`–`int64`, `uint8`–`uint64`, `float32`, `float64`, `complex64`, `complex128`, and boolean. Array types use subscript notation: `float64[:]` for 1D, `float64[:, :]` for 2D.

### Lazy vs Eager Compilation

- **Lazy compilation** (default) — Compilation is deferred until the first function call with specific argument types. Separate specializations are generated for different input types.
- **Eager compilation** — Specify an explicit signature at decoration time to compile immediately: `@jit(float64(float64, float64))`.

### Performance Measurement

Always account for compilation time when benchmarking. The first call includes JIT compilation overhead. Use `timeit` or call the function once before timing to measure post-compilation performance.

## Installation / Setup

Numba is available via conda or pip:

- Conda: `conda install numba`
- Pip: `pip install numba`

Optional dependencies for additional functionality:

- `scipy` — enables `numpy.linalg` function compilation
- `colorama` — color highlighting in error messages
- `pyyaml` — YAML configuration file support (`.numba_config.yaml`)
- `intel-cmplr-lib-rt` — Intel SVML high-performance math library (x86_64)
- `tbb` — Intel TBB threading layer for parallel execution

Supported platforms: x86, x86_64, POWER8/9, ARM (including Apple M1), NVIDIA GPUs. Operating systems: Windows, macOS, Linux. Python versions: 3.9–3.12.

## Usage Examples

### Basic JIT Compilation

```python
from numba import njit
import numpy as np

@njit
def sum_array(arr):
    total = 0.0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            total += arr[i, j]
    return total

x = np.arange(100).reshape(10, 10)
print(sum_array(x))
```

### Parallel Loops with prange

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

### Creating a ufunc with @vectorize

```python
from numba import vectorize, float64

@vectorize([float64(float64, float64)])
def add(x, y):
    return x + y

# Works like a NumPy ufunc with reduce, accumulate, broadcasting
result = add.reduce(some_array, axis=0)
```

### Stencil Operations

```python
from numba import stencil
import numpy as np

@stencil
def average_neighbors(a):
    return 0.25 * (a[0, 1] + a[1, 0] + a[0, -1] + a[-1, 0])

input_arr = np.arange(100).reshape((10, 10))
output = average_neighbors(input_arr)
```

### JIT-Compiled Class

```python
import numpy as np
from numba import int32, float32
from numba.experimental import jitclass

spec = [
    ('value', int32),
    ('array', float32[:]),
]

@jitclass(spec)
class Bag:
    def __init__(self, value):
        self.value = value
        self.array = np.zeros(value, dtype=np.float32)

    @property
    def size(self):
        return self.array.size

    def increment(self, val):
        for i in range(self.size):
            self.array[i] += val
        return self.array

mybag = Bag(10)
```

### C Callback with @cfunc

```python
from numba import cfunc

@cfunc("float64(float64, float64)")
def add(x, y):
    return x + y

# Access the ctypes callback
print(add.ctypes(4.0, 5.0))  # prints 9.0
```

## Advanced Topics

**JIT Compilation Details**: `@jit` decorator options, signatures, lazy vs eager compilation, caching → See [JIT Compilation](reference/01-jit-compilation.md)

**Vectorize and Guvectorize**: Creating NumPy ufuncs and generalized ufuncs with multiple targets (cpu, parallel, cuda) → See [Universal Functions](reference/02-universal-functions.md)

**jitclass**: Compiling Python classes with typed fields, type inference from annotations, dunder methods → See [JIT Classes](reference/03-jit-classes.md)

**Parallel Execution**: `parallel=True`, `prange`, supported operations, reduction patterns, threading layers (tbb, omp, workqueue) → See [Parallel Execution](reference/04-parallel-execution.md)

**Stencil Operations**: Kernel definition, neighborhood specification, border handling, standard indexing → See [Stencil Operations](reference/05-stencil-operations.md)

**C Interoperability**: `@cfunc` callbacks, `carray`, C structures via CFFI and `Record.make_c_struct` → See [C Interoperability](reference/06-c-interoperability.md)

**Ahead-of-Time Compilation**: `numba.pycc` module, extension module generation, signature syntax → See [AOT Compilation](reference/07-aot-compilation.md)

**Types and Signatures**: Numba type system, numeric types, array layouts, function types, first-class functions → See [Types and Signatures](reference/08-types-and-signatures.md)

**Performance Tuning**: nopython mode, fastmath, SIMD vectorization, Intel SVML, parallel optimization tips → See [Performance Tips](reference/09-performance-tips.md)

**Supported Features**: Python language support, built-in types, standard library modules, NumPy features, deviations from Python semantics → See [Supported Features](reference/10-supported-features.md)

**Environment Variables and Debugging**: Configuration via `.numba_config.yaml`, JIT flags, debugging tools, GDB integration → See [Configuration and Debugging](reference/11-configuration-debugging.md)
