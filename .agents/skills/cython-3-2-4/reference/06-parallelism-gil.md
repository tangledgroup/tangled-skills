# Parallelism and GIL

## The GIL

Python's Global Interpreter Lock (GIL) ensures thread safety for Python objects. In Cython, releasing the GIL is useful for:

1. Using `prange` parallel loops (requires `nogil`)
2. Allowing other Python threads to run during long computations
3. Avoiding deadlocks in multi-threaded applications

**Important:** Releasing the GIL alone does not speed up single-threaded code. The speedup comes from writing efficient C-level code that happens to not need the GIL.

## Marking Functions as `nogil`

```cython
# Cython syntax
cdef void some_func() noexcept nogil:
    ...

# Pure Python mode
@cython.nogil
@cython.cfunc
@cython.noexcept
def some_func() -> None:
    ...
```

This marks the function as safe to call without the GIL but does not release it at the call site. The caller must be in a `nogil` context for parallelism to occur.

## Releasing the GIL

```cython
# Cython syntax
with nogil:
    ...  # runs without GIL
    with gil:
        ...  # temporarily reacquire GIL
    ...  # back to nogil

# Pure Python mode
with cython.nogil:
    ...
    with cython.gil:
        ...
```

**Conditionally releasing the GIL** (useful with fused types):

```cython
with nogil(some_type is not object):
    ...  # runs without GIL unless processing Python objects
```

## `prange` — Parallel Range

The `prange` function distributes loop iterations across threads using OpenMP:

```cython
from cython.parallel import prange

@cython.boundscheck(False)
@cython.wraparound(False)
def parallel_sum(double[:] arr):
    cdef double total = 0
    cdef Py_ssize_t i
    for i in prange(arr.shape[0], nogil=True, schedule='static'):
        total += arr[i]
    return total
```

**Parameters:**

- `nogil` — If `True`, wraps the loop in a `nogil` block automatically
- `schedule` — OpenMP scheduling: `'static'`, `'dynamic'`, `'guided'`, `'runtime'`
- `chunksize` — Chunk size for static/dynamic/guided scheduling
- `num_threads` — Number of threads (defaults to OpenMP default, typically CPU count)
- `use_threads_if` — Condition for parallel execution; falls back to sequential if false

**Variable semantics in `prange`:**

- Assignment (`x = ...`) → `lastprivate` (value from last iteration)
- In-place operator (`x += ...`) → reduction (thread-local values combined after loop)
- Loop index → always `lastprivate`

## Examples

**Reduction:**

```cython
from cython.parallel import prange

def sum_array(double[:] arr):
    cdef double total = 0
    cdef Py_ssize_t i
    for i in prange(len(arr), nogil=True):
        total += arr[i]   # automatic reduction with +=
    return total
```

**Memoryview with parallelism:**

```cython
from cython.parallel import prange

def process_2d(double[:,:] arr):
    cdef Py_ssize_t i, j
    for i in prange(arr.shape[0], nogil=True, schedule='static'):
        for j in range(arr.shape[1]):
            arr[i, j] *= 2.0
```

**Conditional parallelism:**

```cython
def smart_parallel(double[:] arr):
    cdef Py_ssize_t i
    # Only use threads if array is large enough
    for i in prange(len(arr), nogil=True, use_threads_if=len(arr) > 10000):
        arr[i] += 1.0
```

## `parallel` Context Manager

For thread-local buffer setup:

```cython
from cython.parallel import parallel, threadid

def with_thread_buffers():
    with parallel(num_threads=4):
        cdef double local_buf = 0
        # Variables assigned here are private to each thread
        cdef Py_ssize_t tid = threadid()
        ...
```

## OpenMP Functions

Access OpenMP runtime functions:

```cython
# Cython syntax
from openmp cimport omp_get_num_threads, omp_get_thread_num

# Pure Python mode
from cython.parallel cimport omp_get_num_threads, omp_get_thread_num
```

## Compiling with OpenMP

In `setup.py`:

```python
from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "my_module", ["my_module.pyx"],
        extra_compile_args=["-fopenmp"],
        extra_link_args=["-fopenmp"],
    )
]

setup(ext_modules=cythonize(extensions))
```

For MSVC (Windows), use `'/openmp'` for compile args and no link args.

In source file:

```cython
# distutils: extra_compile_args=-fopenmp
# distutils: extra_link_args=-fopenmp
```

In Jupyter notebook:

```python
%%cython --force
# distutils: extra_compile_args=-fopenmp
# distutils: extra_link_args=-fopenmp
```

## Breaking Out of Parallel Loops

`break`, `continue`, and `return` are supported in `prange` but with best-effort semantics:

```cython
for i in prange(n, nogil=True):
    if condition(i):
        break  # skips remaining iterations (order is undefined)
```

It is undefined which value is returned if multiple threads may return different values.

## `with gil` Functions

Ensure a function acquires the GIL on entry:

```cython
cdef int some_func() with gil:
    ...

# In a nogil context:
with nogil:
    some_func()  # internally acquires GIL
```

```python
# Pure Python mode
@cython.with_gil
@cython.cfunc
def some_func() -> cython.int:
    ...
```

## `noexcept` and Exception Handling

In `nogil` blocks, exceptions are handled efficiently:

- Functions with specific exception specs (`except +`, `except ValueError`) check error state without acquiring GIL unless an error occurs
- Functions with `except *` (catch-all) must acquire the GIL after every call to check — use `noexcept` or `@cython.exceptval(check=False)` to avoid this

```cython
# Mark helper as noexcept to avoid GIL acquisition in nogil loops
cdef my_type clip(my_type a, my_type lo, my_type hi) noexcept nogil:
    return min(max(a, lo), hi)
```

## Don't Use the GIL as a Lock

The GIL is for interpreter safety, not application-level synchronization. Use `threading.Lock` or similar for reliable locking. The GIL can be released unexpectedly (e.g., during `__del__` calls).
