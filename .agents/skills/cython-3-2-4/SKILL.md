---
name: cython-3-2-4
description: A skill for using Cython 3.2.4, an optimizing Python compiler that makes writing C extensions as easy as Python itself by translating Python code to C/C++ with support for calling C functions and declaring C types on variables and class attributes. Use when building high-performance Python extensions, wrapping C/C++ libraries, creating optimized numerical code with NumPy integration, implementing parallel algorithms with OpenMP, or needing fine-grained manual tuning from broad to low-level C optimizations.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.2.4"
tags:
  - python
  - compiler
  - c-extension
  - performance
  - optimization
  - numpy
  - parallelism
category: programming-languages
external_references:
  - https://github.com/cython/cython/tree/3.2.4
  - https://github.com/cython/cython/wiki
  - https://groups.google.com/group/cython
  - https://cython.readthedocs.io/en/latest/
---
## Overview
Cython is an optimizing Python compiler that makes writing C extensions for Python as easy as Python itself. It translates Python code to C/C++ code, but additionally supports calling C functions and declaring C types on variables and class attributes. This allows broad to fine-grained manual tuning that lets the compiler generate very efficient C code from Cython code.

**Key capabilities:**
- Compile Python-like code to optimized C/C++ extensions
- Declare C data types on variables, function parameters, and class attributes
- Wrap external C and C++ libraries with minimal boilerplate
- Integrate seamlessly with NumPy arrays using typed memoryviews
- Implement parallel algorithms using OpenMP with `prange`
- Release the GIL for true multi-threaded execution
- Support both `.pyx` (Cython syntax) and `.py` (pure Python mode) files

**Performance characteristics:**
- 70+ million downloads per month on PyPI
- Typical speedups: 20-50% for pure Python, 10-100x with C typing
- For-loop style programs can gain orders of magnitude with proper typing
- "Generate once, compile everywhere" C code generation for reproducible results

## When to Use
Use Cython when:

| Scenario | Benefit |
|----------|---------|
| **Performance-critical loops** | 10-100x speedup with static typing on loop variables |
| **Wrapping C/C++ libraries** | Direct C API access without Python overhead |
| **NumPy array processing** | Zero-copy memoryviews eliminate buffer overhead |
| **Parallel computation** | OpenMP `prange` for multi-core utilization |
| **Long-running computations** | Release GIL to allow other Python threads to run |
| **Extension modules** | Create `.so`/`.pyd` files importable from Python |
| **Gradual optimization** | Start with pure Python, add types incrementally |

**Don't use Cython when:**
- You need JIT compilation with runtime optimizations (consider PyPy or Numba)
- Your code is I/O bound rather than CPU bound
- You require full language compliance without any C knowledge
- Dynamic features are essential throughout the codebase

## Core Concepts
### Two Syntax Variants

Cython supports two ways to write typed code:

**1. Cython-specific syntax (.pyx files):**
```python
cdef int counter = 0
cdef float rate = 3.14

def process(int x, float y):
    cdef int result
    result = x * int(y)
    return result
```

**2. Pure Python mode (.py files with type hints):**
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import cython

def process(x: cython.int, y: cython.float) -> cython.int:
    result: cython.int
    result = x * int(y)
    return result
```

**Key differences:**
- `.pyx` files require Cython to run (cannot be interpreted)
- `.py` files can run with or without compilation
- Pure Python mode keeps debugging/linting tools compatible
- Use pure Python mode when no external C library interaction is needed

### Type Declarations

Three ways to declare C types:

**1. Using `cdef` (Cython syntax):**
```python
cdef int i = 10
cdef float f = 2.5
cdef int[4] arr = [1, 2, 3, 4]
cdef float *ptr = &f
```

**2. Using type annotations (Pure Python):**
```python
def func():
    i: cython.int = 10
    f: cython.float = 2.5
    arr: cython.int[4] = [1, 2, 3, 4]
```

**3. Using `cython.declare()` (Pure Python):**
```python
# Module-level (type annotations ignored at module level)
global_var = cython.declare(cython.int, 42)

def func():
    local_var = cython.declare(cython.int)
```

### Function Types

| Type | Declaration | Called from Python | Called from Cython | Use case |
|------|-------------|-------------------|-------------------|----------|
| `def` | `def foo():` | Yes | Yes (Python API) | Public API |
| `cdef` | `cdef foo():` | No | Yes (C API) | Internal functions |
| `cpdef` | `cpdef foo():` | Yes | Yes (C API) | Hybrid functions |

**Example:**
```python
# Public function callable from Python
def public_api(int x):
    return _helper(x) + 1

# Internal C function (faster, not exposed to Python)
cdef int _helper(int x):
    return x * 2

# Hybrid: fast from Cython, accessible from Python
cpdef int hybrid_func(int x):
    return x ** 2
```

### Extension Types

Create efficient Python types with C data structures:

```python
cdef class Counter:
    """Extension type with C attributes"""
    
    cdef int count
    cdef public string name  # Accessible from Python
    
    def __init__(self, string name):
        self.count = 0
        self.name = name
    
    cdef void _increment(self):
        """Internal C method"""
        self.count += 1
    
    def increment(self):
        """Public Python method"""
        self._increment()
    
    def get_count(self) -> int:
        return self.count
```

**Usage:**
```python
counter = Counter("my_counter")
counter.increment()
print(counter.get_count())  # 1
print(counter.name)         # "my_counter"
# counter.count             # AttributeError! (not public)
```

See [Extension Types Reference](reference/02-extension-types.md) for advanced patterns.

### Memoryviews

Zero-copy access to NumPy arrays and buffers:

```python
import numpy as np

def sum_array(double[:] arr):
    """Sum array elements using memoryview"""
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    for i in range(arr.shape[0]):
        total += arr[i]
    
    return total

# Usage
arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
result = sum_array(arr)  # 15.0
```

**Memoryview syntax:**
- `double[:]` - 1D array of doubles
- `double[:,:]` - 2D array
- `int[:, :, :]` - 3D array
- `double[::1]` - contiguous memory (faster)
- `double[:] not None` - reject None values

See [Memoryviews Reference](reference/03-memoryviews.md) for complete guide.

### Parallelism with OpenMP

Parallel loops using `prange`:

```python
from cython.parallel import prange, parallel

def parallel_sum(double[:] arr):
    """Sum array in parallel"""
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    # Automatically releases GIL and parallelizes
    for i in prange(arr.shape[0], nogil=True, num_threads=4):
        total += arr[i]  # Automatic reduction
    
    return total
```

**Compilation with OpenMP:**
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

See [Parallelism Reference](reference/04-parallelism.md) for scheduling and optimization.

## Advanced Topics
## Advanced Topics

- [Language Basics](reference/01-language-basics.md)
- [Extension Types](reference/02-extension-types.md)
- [Memoryviews](reference/03-memoryviews.md)
- [Parallelism](reference/04-parallelism.md)
- [Compilation](reference/05-compilation.md)
- [Optimization](reference/06-optimization.md)
- [C Libraries](reference/07-c-libraries.md)
- [Cpp Libraries](reference/08-cpp-libraries.md)
- [Numpy](reference/09-numpy.md)
- [Troubleshooting](reference/10-troubleshooting.md)
- [Quick Start](reference/11-quick-start.md)
- [Compilation Methods](reference/12-compilation-methods.md)
- [Optimization Techniques](reference/13-optimization-techniques.md)
- [Debugging](reference/14-debugging.md)
- [Common Patterns](reference/15-common-patterns.md)
- [Troubleshooting](reference/16-troubleshooting.md)

