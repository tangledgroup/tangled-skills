# Troubleshooting and Debugging

## Common Errors

### AttributeError on cdef Attributes

**Error:**
```
AttributeError: 'MyClass' object has no attribute 'my_attr'
```

**Cause:** `cdef` attributes are not accessible from Python by default.

**Solution 1 - Make public:**
```python
# Before (private)
cdef class MyClass:
    cdef int my_attr

# After (public)
cdef class MyClass:
    cdef public int my_attr
```

**Solution 2 - Add property:**
```python
cdef class MyClass:
    cdef int my_attr
    
    @property
    def my_attr(self):
        return self.my_attr
    
    @my_attr.setter
    def my_attr(self, int value):
        self.my_attr = value
```

### Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'mymodule'
```

**Cause:** Extension not built or not in Python path.

**Solution 1 - Build in-place:**
```bash
python setup.py build_ext --inplace
```

**Solution 2 - Check extension location:**
```bash
# Find the .so or .pyd file
find . -name "mymodule*.so" -o -name "mymodule*.pyd"

# Add directory to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:/path/to/build"
```

**Solution 3 - Verify extension compiled:**
```bash
python -c "import mymodule; print(mymodule.__file__)"
```

### Type Inference Issues

**Error:**
```
Cannot convert Python object to C type 'int'
```

**Cause:** Cython can't infer types at module level or in complex expressions.

**Solution - Explicit declarations:**
```python
# Module-level variables need explicit declaration
cdef int global_counter = 0  # Not: global_counter = 0

# Function parameters should be typed
def process(int x, float y):  # Not: def process(x, y):
    return x + int(y)

# Local variables in performance-critical code
def compute():
    cdef int total = 0  # Declare type explicitly
    cdef int i
    
    for i in range(100):
        total += i
```

### Compilation Errors

**Error:** "No C compiler found"

**Solution - Install build tools:**

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential python3-dev
```

**macOS:**
```bash
xcode-select --install
```

**Windows:**
Install Visual Studio Build Tools with "Desktop development with C++" workload.

**Error:** "Python.h not found"

**Solution:**
```bash
sudo apt-get install python3-dev  # Debian/Ubuntu
# macOS: brew install python (includes headers)
```

**Error:** "numpy/arrayobject.h not found"

**Solution:**
```bash
pip install numpy  # Must be installed before building Cython extensions
```

## Debugging Techniques

### Annotated HTML Output

Generate visual performance analysis:

```bash
cython -a module.pyx
# Opens module.html in browser
```

**Reading the output:**
- **White lines:** Translated to C code (fast)
- **Yellow lines:** Still use Python API (slower)
- **Darker yellow:** More Python overhead
- **Click on line numbers:** See generated C code

### GDB Debugging

**Step 1 - Build with debug symbols:**
```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("module", ["module.pyx"])
setup(ext_modules=cythonize([ext], gdb_debug=True))
```

**Step 2 - Compile:**
```bash
python setup.py build_ext --inplace
```

**Step 3 - Run GDB:**
```bash
cygdb
(gdb) cy break my_function
(gdb) cy run
(gdb) cy step
(gdb) cy next
(gdb) cy print variable_name
```

**GDB commands:**
- `cy break func` - Set breakpoint on Cython function
- `cy break :15` - Break at line 15
- `cy step` - Step into functions
- `cy next` - Step over functions
- `cy run` - Start program
- `cy cont` - Continue execution
- `cy up/down` - Navigate stack frames

### Runtime Debugging Directives

Enable checks for development:

```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'boundscheck': True,       # Check array bounds
            'initializedcheck': True,  # Catch uninitialized variables
            'nonecheck': True,         # Check for None in typed variables
            'wraparound': True         # Support negative indices
        }
    )
)
```

### Print Debugging

**C-style printf:**
```python
from libc.stdio cimport printf

def debug_function(int x):
    cdef int y = x * 2
    printf("x=%d, y=%d\n", x, y)
    return y
```

**Python print with types:**
```python
def debug_with_types(double[:] arr):
    print(f"Array shape: {arr.shape}")
    print(f"First element: {arr[0]}")
    print(f"Type: {type(arr)}")
```

### Logging

```python
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def tracked_function(int x):
    log.debug(f"Called with x={x}")
    
    cdef int result = x * 2
    log.debug(f"Result: {result}")
    
    return result
```

## Performance Debugging

### Profiling with cProfile

**Enable profiling:**
```python
# In setup.py
setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={'profile': True, 'linetrace': True}
    )
)
```

**Run profiler:**
```bash
python -m cProfile -o profile.out script.py
python -m pstats profile.out
(pstats) sort_cum
(pstats) stats 10
```

### Identifying Hot Spots

**Use timeit for micro-benchmarks:**
```python
import timeit

# Compare implementations
time_python = timeit.timeit(
    'slow_function(data)',
    setup='from __main__ import slow_function, data',
    number=1000
)

time_cython = timeit.timeit(
    'fast_function(data)',
    setup='from __main__ import fast_function, data',
    number=1000
)

print(f"Speedup: {time_python/time_cython:.2f}x")
```

### Memory Profiling

**Check for memory leaks:**
```python
import gc
import tracemalloc

def check_memory():
    tracemalloc.start()
    
    # Run code that might leak
    result = memory_intensive_operation()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()
    return result
```

## Common Pitfalls and Solutions

### Segmentation Faults

**Cause 1 - Uninitialized variables:**
```python
# Bad
def bug():
    cdef int value
    # value is uninitialized!
    return value + 1  # Undefined behavior

# Good
def fixed():
    cdef int value = 0  # Initialize
    return value + 1
```

**Cause 2 - Out of bounds access:**
```python
# Bad (with boundscheck=False)
def out_of_bounds(int[:] arr, int index):
    return arr[index]  # May segfault if index invalid

# Good
def safe_access(int[:] arr, int index):
    if index < 0 or index >= arr.shape[0]:
        raise IndexError(f"Index {index} out of bounds")
    return arr[index]
```

**Cause 3 - Double free:**
```python
# Bad
def double_free_bug():
    cdef char *ptr = malloc(100)
    free(ptr)
    free(ptr)  # Double free!

# Good
def safe_free():
    cdef char *ptr = malloc(100)
    try:
        # Use ptr...
        pass
    finally:
        if ptr != NULL:
            free(ptr)
            ptr = NULL  # Prevent double free
```

### Memory Leaks

**Problem - C++ objects not deleted:**
```python
# Bad - memory leak
def leak_example():
    cdef MyClass *obj = new MyClass()
    # Function returns, obj never deleted!

# Good - use try/finally
def no_leak():
    cdef MyClass *obj = new MyClass()
    try:
        return obj.get_value()
    finally:
        del obj
```

**Better - use wrapper class:**
```python
cdef class ManagedObject:
    cdef MyClass *ptr
    
    def __init__(self):
        self.ptr = new MyClass()
    
    def __del__(self):
        del self.ptr  # Automatic cleanup
```

### GIL Issues

**Problem - Deadlock when holding GIL:**
```python
# Bad - may deadlock
def deadlock_risk():
    with nogil:
        # Can't call Python functions here!
        python_function()  # Error!

# Good - release and reacquire GIL properly
def safe_nogil():
    with nogil:
        c_computation()
    
    with gil:
        python_function()  # Safe
```

### Type Conversion Issues

**Problem - Implicit conversions:**
```python
# May lose precision
cdef float f = some_double_value  # Truncation

# Explicit is better
cdef float f = <float>some_double_value  # Intentional
```

**Problem - String encoding:**
```python
# Bad - assumes ASCII
cdef char *c_str = python_string  # May fail with Unicode

# Good - explicit encoding
cdef char *c_str = python_string.encode('utf-8')
```

## Testing Strategies

### Unit Tests for Cython Code

```python
# test_module.py
import unittest
from mymodule import fast_function, MyClass

class TestCythonFunctions(unittest.TestCase):
    def test_fast_function(self):
        result = fast_function(10)
        self.assertEqual(result, 20)
    
    def test_class_initialization(self):
        obj = MyClass(42)
        self.assertEqual(obj.value, 42)

if __name__ == '__main__':
    unittest.main()
```

Run with:
```bash
python -m pytest test_module.py -v
# or
python test_module.py
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=1000))
def test_always_positive(n):
    result = absolute_value(n)
    assert result >= 0
```

## Getting Help

### Official Resources

- **Cython Documentation:** https://cython.readthedocs.io/
- **GitHub Issues:** https://github.com/cython/cython/issues
- **Cython Mailing List:** https://groups.google.com/group/cython
- **Stack Overflow:** Tag with [cython]

### Debugging Checklist

1. ✅ Check annotated HTML for Python vs C code
2. ✅ Enable boundscheck and initializedcheck
3. ✅ Verify all variables are initialized
4. ✅ Check array bounds in loops
5. ✅ Ensure proper memory management (no leaks, no double-free)
6. ✅ Verify GIL is held when calling Python
7. ✅ Check type declarations match usage
8. ✅ Review generated C code for clues

See [SKILL.md](../SKILL.md) for overview and [Optimization Reference](06-optimization.md) for performance tuning.
