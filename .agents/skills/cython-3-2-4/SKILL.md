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

# Cython 3.2.4

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

## Quick Start

### Installation

```bash
pip install Cython
```

If you need a C compiler (required for building extensions):

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python3-dev
```

**macOS:**
```bash
xcode-select --install
```

**Windows:**
Install Visual Studio Build Tools with "Desktop development with C++"

### Hello World

Create `helloworld.py`:
```python
print("Hello World")
```

Create `setup.py`:
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("helloworld.py")
)
```

Build and run:
```bash
python setup.py build_ext --inplace
python -c "import helloworld"
# Output: Hello World
```

This produces `helloworld.so` (Linux/macOS) or `helloworld.pyd` (Windows).

### First Typed Function

Create `fibonacci.pyx`:
```python
def fib(int n):
    """Fibonacci sequence with typed parameter"""
    cdef int a = 0, b = 1, i, temp
    
    for i in range(n):
        temp = a + b
        a = b
        b = temp
        print(a)
```

Update `setup.py`:
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("fibonacci.pyx")
)
```

Build and test:
```bash
python setup.py build_ext --inplace
python
>>> import fibonacci
>>> fib(10)
1 1 2 3 5 8 13 21 34 55
```

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

See [Extension Types Reference](references/02-extension-types.md) for advanced patterns.

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

See [Memoryviews Reference](references/03-memoryviews.md) for complete guide.

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

See [Parallelism Reference](references/04-parallelism.md) for scheduling and optimization.

## Compilation Methods

### Command Line Tools

**cythonize** (translate + compile):
```bash
# Generate C file and compile to extension module
cythonize -i yourmod.pyx

# Generate annotated HTML for debugging
cythonize -a -i yourmod.pyx

# Parallel compilation
cythonize -j 4 yourmod.pyx

# C++ mode
cythonize --cplus -i yourmod.pyx
```

**cython** (translate only):
```bash
# Generate C file only
cython yourmod.pyx

# With debug symbols
cython --gdb yourmod.pyx

# Show line numbers in generated C
cython --line-directives=none yourmod.pyx
```

### setup.py with setuptools

**Basic setup:**
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("module.pyx")
)
```

Build:
```bash
python setup.py build_ext --inplace
```

**With compiler directives:**
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True
        }
    )
)
```

**With NumPy:**
```python
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

ext = Extension(
    "numpy_module",
    ["numpy_module.pyx"],
    include_dirs=[np.get_include()]
)

setup(ext_modules=cythonize([ext]))
```

**With C++:**
```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "cpp_module",
    ["cpp_module.pyx", "external.cpp"],
    language="c++",
    extra_compile_args=["-std=c++17"]
)

setup(ext_modules=cythonize([ext]))
```

### pyproject.toml (Modern Approach)

```toml
[build-system]
requires = ["setuptools>=61", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-cython-package"
version = "0.1.0"

[tool.setuptools.ext-modules]
ext-modules = [
  {name = "mymodule", sources = ["mymodule.pyx"]}
]
```

Build with:
```bash
python -m build
```

See [Compilation Reference](references/05-compilation.md) for advanced configuration.

## Optimization Techniques

### Compiler Directives

Control code generation behavior:

```python
# File-wide directive
# cython: language_level=3, boundscheck=False, wraparound=False

def fast_loop(int[:] arr):
    # ... optimized code
    pass

# Local directive (overrides file-wide)
@cython.boundscheck(True)
def safe_access(int[:] arr, int index):
    return arr[index]
```

**Common directives:**

| Directive | Default | Effect when False/True |
|-----------|---------|------------------------|
| `boundscheck` | True | Skip array bounds checking (faster, unsafe) |
| `wraparound` | True | Disable negative index support (faster) |
| `cdivision` | False | Use C division (no ZeroError, true modulo) |
| `embedsignature` | False | Embed Cython signature in Python signature |
| `auto_cpdef` | False | Treat all def functions as cpdef |
| `language_level` | 2 | Python 2 vs 3 semantics |

### Performance Tips

1. **Type everything in hot paths:**
   ```python
   # Slow - all Python objects
   def slow_sum(arr):
       total = 0
       for x in arr:
           total += x
       return total
   
   # Fast - C integers
   def fast_sum(int[:] arr):
       cdef int total = 0, i
       for i in range(arr.shape[0]):
           total += arr[i]
       return total
   ```

2. **Use memoryviews for NumPy:**
   ```python
   # Slow - Python API calls
   def slow_numpy(np.ndarray arr):
       return np.sum(arr)
   
   # Fast - direct memory access
   def fast_numpy(double[:] arr):
       cdef double total = 0.0
       for i in range(arr.shape[0]):
           total += arr[i]
       return total
   ```

3. **Release GIL for CPU-bound work:**
   ```python
   def cpu_bound(int n) nogil:
       cdef int i, result = 0
       for i in range(n):
           result += expensive_calc(i)
       return result
   ```

4. **Use fused types for generic code:**
   ```python
   ctypedef fused real_types:
       float
       double
   
   cpdef squared(real_types x):
       return x * x
   ```

See [Optimization Reference](references/06-optimization.md) for detailed strategies.

## Debugging

### Annotated HTML

Generate visual performance analysis:

```bash
cythonize -a yourmod.pyx
# Opens yourmod.html in browser showing:
# - Which lines are Python vs C
# - Color-coded by "Cyness" (how optimized)
```

### GDB Debugging

Build with debug symbols:
```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("module", ["module.pyx"])
setup(ext_modules=cythonize([ext], gdb_debug=True))
```

Compile and debug:
```bash
python setup.py build_ext --inplace
cygdb
(gdb) cy break my_function
(gdb) cy run
(gdb) cy step
(gdb) cy next
```

### Runtime Debugging

Enable runtime checks:
```python
# In setup.py
setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'boundscheck': True,
            'initializedcheck': True,
            'nonecheck': True
        }
    )
)
```

## Common Patterns

### Wrapping C Libraries

See [C Library Wrapping](references/07-c-libraries.md) for complete guide.

Basic pattern:
```python
# mylib.pxd
cdef extern from "mylib.h":
    int c_function(int x, float y)
    void c_void_function(char *str)

# mylib.pyx
from mylib cimport c_function

def python_wrapper(int x, float y):
    return c_function(x, y)
```

### Wrapping C++ Libraries

See [C++ Library Wrapping](references/08-cpp-libraries.md) for complete guide.

Basic pattern:
```python
# mylib.pxd
cdef extern from "MyClass.h" namespace "myns":
    cdef cppclass MyClass:
        MyClass() except +
        int get_value()
        void set_value(int v)

# mylib.pyx
from mylib cimport MyClass

def use_cpp():
    cdef MyClass obj
    obj.set_value(42)
    return obj.get_value()
```

### NumPy Integration

See [NumPy Tutorial](references/09-numpy.md) for complete guide.

Basic pattern:
```python
# distutils: language = c
import numpy as np
cimport numpy as np

def process_array(np.ndarray[double, ndim=1] arr):
    cdef int i
    cdef double total = 0.0
    
    for i in range(arr.shape[0]):
        total += arr[i]
    
    return total
```

## Troubleshooting

### AttributeError on cdef Attributes

**Problem:** `AttributeError: 'Counter' object has no attribute 'count'`

**Cause:** `cdef` attributes are not accessible from Python by default.

**Solution:** Declare as `public` or `readonly`:
```python
cdef class Counter:
    cdef public int count  # Now accessible from Python
```

### Module Import Errors

**Problem:** `ModuleNotFoundError: No module named 'mymodule'`

**Cause:** Extension not built in correct location.

**Solution:** Use `--inplace` flag:
```bash
python setup.py build_ext --inplace
```

### Type Inference Issues

**Problem:** Code doesn't compile or is slower than expected.

**Cause:** Cython can't infer types at module level.

**Solution:** Explicitly declare global variables:
```python
# Instead of:
global_var = Counter()  # Treated as Python object

# Use:
cdef Counter global_var
global_var = Counter()
```

See [Troubleshooting Guide](references/10-troubleshooting.md) for more issues.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
