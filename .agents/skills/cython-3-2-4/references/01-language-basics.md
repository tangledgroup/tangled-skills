# Cython Language Basics

## Type System Fundamentals

### C Data Types in Cython

Cython supports all standard C types:

```python
cdef int i = 42                    # Signed integer
cdef unsigned int u = 42           # Unsigned integer
cdef long l = 1000000              # Long integer
cdef float f = 3.14                # Single precision
cdef double d = 3.14159265359      # Double precision
cdef char c = 'A'                  # Character
cdef bstring s = b"bytes"          # Byte string
cdef unicode u = "text"            # Unicode string
cdef void *ptr = NULL              # Void pointer
cdef double complex z = 1 + 2j     # Complex number
```

### Type Modifiers

```python
cdef const int value = 10          # Constant (compile-time)
cdef volatile int flag             # Volatile (no optimization)
cdef signed char sc                # Explicit signed
cdef unsigned long ul              # Unsigned long
```

### Arrays and Pointers

**Fixed-size arrays:**
```python
cdef int arr[10]                   # Array of 10 ints
cdef double matrix[3][4]           # 2D array (3x4)

# Initialization
cdef int numbers[4] = [1, 2, 3, 4]
```

**Pointers:**
```python
cdef int *ptr                      # Pointer to int
cdef int **pptr                    # Pointer to pointer
cdef int *arr_ptr = &arr[0]        # Pointer to array element

# Pointer arithmetic
cdef int value = arr_ptr[2]        # Access via pointer
```

### Creating Type Aliases

```python
# Using ctypedef
ctypedef unsigned int uint
ctypedef double real
ctypedef int point_t[3]            # Array type alias

# Using cython.typedef() in pure Python mode
UInt = cython.typedef(cython.uint)
Real = cython.typedef(cython.double)
```

## Function Declaration Patterns

### def Functions (Python API)

Always accessible from Python, use Python calling convention:

```python
def python_func(int x, float y):
    """Called from Python and Cython via Python API"""
    cdef int result = x
    return result + y
```

**Characteristics:**
- Can be called from Python code
- Arguments converted to/from Python objects
- Supports default arguments, *args, **kwargs
- Slower but more flexible

### cdef Functions (C API Only)

Internal functions, not accessible from Python:

```python
cdef int fast_helper(int x):
    """Called only from Cython code"""
    return x * 2

def public_api(int n):
    return fast_helper(n) + fast_helper(n + 1)
```

**Characteristics:**
- Cannot be called from Python
- No argument conversion overhead
- Can use C types exclusively
- Fastest calling convention

### cpdef Functions (Hybrid)

Best of both worlds - fast from Cython, accessible from Python:

```python
cpdef int hybrid_func(int x):
    """Fast from Cython, callable from Python"""
    return x ** 2

# From Cython (fast C call)
cdef int result = hybrid_func(5)

# From Python (slower but works)
result = hybrid_func(5)
```

**Use cases:**
- Functions you might want to override in Python subclasses
- Performance-critical functions that need Python accessibility
- Library APIs where both speed and flexibility matter

### Function Signatures with Defaults

```python
# Python-style defaults (def only)
def func_with_defaults(int x, int y=10):
    return x + y

# cpdef with defaults (uses * for unspecified)
cpdef int cpdef_defaults(int x, int y=*):
    if y == 0:  # Check for default
        y = 10
    return x + y
```

## Variable Scoping Rules

### Module-Level Variables

```python
# Global C variable (not visible to Python)
cdef int global_counter = 0

# Global Python object (visible as module attribute)
python_global = "I'm a Python object"

# Using cython.declare() for typed globals in .py files
counter = cython.declare(cython.int, 0)
```

**Important:** Type annotations at module level are ignored in pure Python mode. Use `cython.declare()` instead:

```python
# In .py file
MY_CONSTANT = cython.declare(cython.int, 42)

def func():
    x: cython.int = 10  # This works for locals
```

### Local Variables

```python
def example():
    # C-local variables (fast, not visible to Python)
    cdef int i = 0
    cdef float total = 0.0
    
    # Python locals (slower, full Python semantics)
    python_list = []
    
    for i in range(10):
        total += i
        python_list.append(i)
    
    return total, python_list
```

### Type Inference

Cython can infer types in some contexts:

```python
def inferred_types():
    # Cython infers 'counter' is int from assignment
    counter = 0  # Actually Python object!
    
    # Explicit declaration needed for C type
    cdef int explicit_counter = 0
    
    # Type inference works with 'for' loops over ranges
    for i in range(10):
        # 'i' is inferred as Python object, not C int
        pass
    
    # Use typed memoryview or declare explicitly
    cdef int j
    for j in range(10):
        # 'j' is now C int
        pass
```

**Rule of thumb:** Always declare types explicitly for performance-critical code.

## Control Flow Optimization

### Bounds Checking

By default, Cython checks array bounds:

```python
# cython: boundscheck=True  (default)

def safe_access(int[:] arr, int index):
    return arr[index]  # Raises IndexError if out of bounds
```

Disable for performance (unsafe):

```python
# cython: boundscheck=False

def unsafe_access(int[:] arr, int index):
    return arr[index]  # No bounds check - faster but can segfault
```

### Negative Index Handling

Python allows negative indices (`arr[-1]`):

```python
# cython: wraparound=True  (default)

def with_negative_index(int[:] arr):
    return arr[-1]  # Last element
```

Disable if you never use negative indices:

```python
# cython: wraparound=False

def no_negative_index(int[:] arr, int i):
    return arr[i]  # Faster, but arr[-1] won't work
```

### Division Behavior

Python vs C division:

```python
# cython: cdivision=False  (default - Python semantics)

def python_division():
    return 1 / 0  # Raises ZeroDivisionError

# cython: cdivision=True  (C semantics)

def c_division():
    return 1.0 / 0.0  # Returns inf (infinity), no exception
```

## Special Cython Types

### fused Types (Templates)

Define functions that work with multiple types:

```python
ctypedef fused number_types:
    int
    float
    double

cpdef squared(number_types x):
    """Works with int, float, or double"""
    return x * x

# Usage - generates specialized versions
result1 = squared(5)        # Uses int version
result2 = squared(3.14)     # Uses double version
```

**Advanced fused types:**

```python
ctypedef fused int_types:
    char
    short
    int
    long

cpdef int_types max_val(int_types a, int_types b):
    return a if a > b else b
```

### Optional Types

```python
from typing import Optional

def process_optional(Optional[int] value):
    if value is None:
        return 0
    return value * 2
```

### Cython-Specific Types

```python
cdef Py_ssize_t index          # Python's index type (signed)
cdef size_t count              # C size type (unsigned)
cdef ssize_t offset            # Signed size
cdef bytearray ba              # Python bytearray
cdef bytes b                   # Python bytes object
```

## Memory Management

### Stack vs Heap Allocation

**Stack allocation (fast, limited size):**
```python
def stack_arrays():
    cdef int fixed_arr[100]     # On stack, max 100 elements
    cdef double matrix[10][10]  # 2D array on stack
    
    fixed_arr[0] = 42
    return fixed_arr[0]
```

**Heap allocation (dynamic size):**
```python
from libc.stdlib cimport malloc, free

def heap_array(int size):
    cdef int *arr = <int *>malloc(size * sizeof(int))
    if arr == NULL:
        raise MemoryError("Failed to allocate")
    
    try:
        for i in range(size):
            arr[i] = i * 2
        return sum(arr[i] for i in range(size))
    finally:
        free(arr)
```

### Automatic Memory Management

Cython handles Python object reference counting automatically:

```python
def ref_count_example():
    # All these are Python objects with automatic ref counting
    lst = [1, 2, 3]
    dct = {"key": "value"}
    obj = SomeClass()
    
    # When they go out of scope, refs are decremented
    # and objects freed if refcount reaches 0
    pass
```

**C types don't have automatic cleanup:**

```python
def c_memory_example():
    cdef char *buffer = <char *>malloc(1024)
    
    # Must manually free!
    try:
        # Use buffer...
        pass
    finally:
        free(buffer)  # Required!
```

## Common Pitfalls

### Uninitialized Variables

```python
def uninitialized_bug():
    cdef int counter
    # counter = ?  # Uninitialized!
    
    if some_condition():
        counter = 10
    
    return counter  # Undefined behavior if condition was False
```

**Fix:** Always initialize:

```python
def initialized_ok():
    cdef int counter = 0  # Initialize to default
    
    if some_condition():
        counter = 10
    
    return counter  # Safe
```

### Type Mismatches

```python
def type_mismatch():
    cdef int x = 5
    cdef float y = 3.7
    
    # Implicit conversion (int to float)
    cdef double result = x + y  # OK: result = 8.7
    
    # Explicit conversion needed for precision
    cdef int truncated = <int>y  # truncated = 3
```

### Python vs C Semantics

```python
def python_vs_c():
    cdef int a = 5, b = 0
    
    # Python division (raises exception)
    # result = a / b  # ZeroDivisionError!
    
    # C division (undefined behavior, often inf or crash)
    # result = a / b  # Don't do this!
    
    # Safe approach
    if b != 0:
        result = a / b
    else:
        result = 0  # Or handle appropriately
```

See [SKILL.md](../SKILL.md) for overview and [Optimization Reference](06-optimization.md) for performance tuning.
