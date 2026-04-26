---
name: cython-3-2-4
description: A skill for using Cython 3.2.4, an optimizing Python compiler that makes
  writing C extensions as easy as Python itself by translating Python code to C/C++
  with support for calling C functions and declaring C types on variables and class
  attributes. Use when building high-performance Python extensions, wrapping C/C++
  libraries, creating optimized numerical code with NumPy integration, implementing
  parallel algorithms with OpenMP, or needing fine-grained manual tuning from broad
  to low-level C optimizations.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: 3.2.4
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

# Cython 3.2.4

## Overview

Cython is a compiler that translates Python-like code into optimized C or C++ extensions. It supports the full Python language plus optional static typing, C-level function calls, and direct access to C library APIs. Code runs within the Python runtime environment but compiles to native machine code instead of interpreted bytecode.

Cython's two syntax variants — **Cython syntax** (`.pyx` files with `cdef`, `cimport`) and **Pure Python mode** (`.py` files with `cython.*` annotations and decorators) — let you start with plain Python and incrementally add performance optimizations where needed.

Key capabilities:

- Static type declarations for variables, function parameters, and return values
- Direct C/C++ function calls with zero Python overhead
- Typed memoryviews for efficient NumPy array access
- Fused types for generic programming (like C++ templates)
- OpenMP-based parallelism via `prange`
- GIL release for true multi-threaded execution
- Wrapping existing C and C++ libraries

## When to Use

- Building high-performance Python extensions where loops and numerical operations dominate runtime
- Wrapping C or C++ libraries for use from Python
- Optimizing hot paths in existing Python code with incremental typing
- Creating typed NumPy operations that outperform pure NumPy vectorization
- Implementing parallel algorithms using OpenMP (`prange`)
- Needing fine-grained control from broad Python-level optimization down to manual C tuning

## Core Concepts

**Two compilation stages:** A `.pyx` or `.py` file is first compiled by Cython into a `.c` or `.cpp` file, then compiled by a C/C++ compiler into a platform-specific shared library (`.so` on Linux, `.pyd` on Windows).

**Two syntax variants:**

- **Cython syntax** (`.pyx`): Uses `cdef`, `cimport`, `cpdef` keywords. Not valid Python.
- **Pure Python mode** (`.py`): Uses PEP-484 type annotations with `cython.*` types and `@cython.*` decorators. Valid Python that also compiles with Cython.

**Three function types:**

- `def` — Python-callable function, always goes through Python calling convention
- `cdef` / `@cython.cfunc` — C-only function, fastest calls within Cython code, not visible from Python
- `cpdef` / `@cython.ccall` — Hybrid: callable from both Python and C, uses fast C calling when called from Cython

**Extension types:** Declared with `cdef class` or `@cython.cclass`, these are like Python classes but with faster attribute access for `cdef` members. They compile to C structs.

## Installation / Setup

Install Cython via pip:

```bash
pip install "Cython==3.2.4"
```

A C compiler is required (gcc, clang, or MSVC). For NumPy integration, also install numpy.

Basic `setup.py` for compiling a `.pyx` file:

```python
# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("example.pyx")
)
```

Build with:

```bash
python setup.py build_ext --inplace
```

For `pyproject.toml` builds (PEP 518):

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "Cython"]
build-backend = "setuptools.build_meta"
```

Command-line compilation:

```bash
cythonize -i example.pyx    # compile to C and build extension in-place
cython -a example.pyx       # generate annotated HTML showing Python/C boundaries
```

## Usage Examples

**Basic typed function (Cython syntax):**

```cython
# math_ops.pyx
def fast_sum(int[:] arr):
    cdef double total = 0.0
    cdef int i
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

**Same function in Pure Python mode:**

```python
# math_ops.py
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def fast_sum(arr: cython.double[:]) -> cython.double:
    total: cython.double = 0.0
    i: cython.Py_ssize_t
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

**Wrapping a C library:**

```cython
# lib_wrapper.pyx
cdef extern from "math.h":
    double sin(double x)
    double cos(double x)

def compute_angle(double x, double y):
    return atan2(y, x)
```

## Advanced Topics

**Language Basics**: Data types, `cdef`/`cpdef`, structs, unions, enums, pointers, ctuples → See [Language Basics](reference/01-language-basics.md)

**Typed Memoryviews**: Efficient NumPy array access without GIL, slicing, strides, C/Fortran contiguity → See [Typed Memoryviews](reference/02-memoryviews.md)

**External C/C++ Code**: Wrapping C libraries, `cdef extern from`, header files, verbatim C, public/API declarations → See [External C/C++ Code](reference/03-external-c-code.md)

**C++ Support**: `cppclass`, templates, STL containers, operator overloading, exception handling → See [Using C++ in Cython](reference/04-cpp-support.md)

**Fused Types**: Generic programming with type specializations, indexing, memoryview fused types → See [Fused Types](reference/05-fused-types.md)

**Parallelism and GIL**: `prange`, OpenMP schedules, releasing the GIL, `nogil` functions, thread-local buffers → See [Parallelism and GIL](reference/06-parallelism-gil.md)

**Compilation and Directives**: setup.py patterns, distutils comments, compiler directives, annotations, shared utility modules → See [Compilation and Directives](reference/07-compilation-directives.md)
