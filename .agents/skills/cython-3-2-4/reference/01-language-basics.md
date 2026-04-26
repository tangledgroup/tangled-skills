# Language Basics

## Declaring Data Types

Cython enables early binding — declaring static types for variables and parameters — to avoid Python's runtime type dispatch overhead. Typing is optional; optimize where needed.

**Three ways to declare C variables:**

1. `cdef` statement (Cython syntax, `.pyx`)
2. PEP-484/526 type annotations with `cython.*` types (Pure Python, `.py`)
3. `cython.declare()` function (works in both modes for module-level)

```cython
# Cython syntax (.pyx)
cdef int a_global_variable = 42

def func():
    cdef int i = 10
    cdef float f = 2.5
    cdef int[4] g = [1, 2, 3, 4]
    cdef float *h
```

```python
# Pure Python mode (.py)
import cython

a_global_variable = cython.declare(cython.int, 42)

def func():
    i: cython.int = 10
    f: cython.float = 2.5
    g: cython.int[4] = [1, 2, 3, 4]
    h: cython.p_float
```

**Important:** Type annotations only affect local variables and class attributes — they are ignored at module level (since annotations are not Cython-specific). Use `cython.declare()` for global C variables in Pure Python mode.

## C Types

Standard C types are available:

- Integers: `char`, `short`, `int`, `long`, `long long` (and `unsigned` variants)
- Floating point: `float`, `double`, `long double`
- Complex: `float complex`, `double complex`, `long double complex`
- Special: `bint` (C boolean), `Py_ssize_t` (container sizes), `size_t`
- Pointers: `int *`, `char **` (Cython syntax) or `cython.p_int`, `cython.pp_char` (Pure Python)
- Arrays: `int[10]`, `double[5][5]` (compile-time known size for stack allocation)

**Pure Python pointer naming scheme:**

- `cython.p_int` = `int *`
- `cython.pp_int` = `int **`
- `cython.pointer[cython.int]` = generic pointer construction

## Structs, Unions, Enums

```cython
# Cython syntax
cdef struct Grail:
    int group_number
    int size
    char kind[134]

cdef enum CheeseState:
    hard = 1
    soft = 2
    runny = 3

# Packed struct (matches NumPy structured arrays)
cdef packed struct StructArray:
    int[4] spam
    signed char[5] eggs
```

```python
# Pure Python mode
import cython

Grail = cython.struct(
    group_number=cython.int,
    size=cython.int,
    kind=cython.char[134]
)
```

Refer to types without the keyword: `cdef Grail *gp` (not `cdef struct Grail *gp`).

## Type Aliases

```cython
ctypedef unsigned long ULong
ctypedef int* IntPtr
```

```python
ULong = cython.typedef(cython.ulong)
IntPtr = cython.typedef(cython.p_int)
```

## C Arrays

Java-style declaration is recommended (consistent with memoryviews):

```cython
cdef int[4] g = [1, 2, 3, 4]   # OK, Java style (recommended)
cdef int g[4]                   # OK but soft-deprecated
cdef int g[4] = [1, 2, 3, 4]   # ERROR — C style doesn't support init
```

## Function Types

**`def` — Python function:**

Takes and returns Python objects. Callable from both Python and Cython code. This is how you "export" functions from a Cython module.

```cython
def spam(int i, char *s):
    # i is converted from Python int to C int
    # s is converted from Python str to C char*
    pass
```

**`cdef` — C function:**

Fastest calling convention within Cython. Not visible from Python. Can use any C type for parameters and return values.

```cython
cdef int eggs(unsigned long l, float f):
    return <int>(l * f)
```

```python
# Pure Python equivalent
@cython.cfunc
def eggs(l: cython.ulong, f: cython.float) -> cython.int:
    return <int>(l * f)
```

**`cpdef` — Hybrid function:**

Callable from both Python and C. Uses fast C calling when called from Cython code, Python calling from Python. Small overhead vs pure `cdef`.

```cython
cpdef int hybrid_func(int x):
    return x * 2
```

```python
# Pure Python equivalent
@cython.ccall
def hybrid_func(x: cython.int) -> cython.int:
    return x * 2
```

## Python Objects as Types

When no type is specified, parameters default to Python objects (not C `int` as in C). Use `object` explicitly when needed:

```cython
cdef spamobjs(x, y):          # both are Python objects
cdef object ftang(object int): # explicit — parameter named 'int'
```

For borrowed references (no refcount management):

```cython
cdef void process(PyObject *obj):
    # No Py_INCREF/DECREF — be careful with lifetime
    pass
```

## Optional Arguments in C Functions

Unlike pure C, `cdef` and `cpdef` functions support default arguments:

```cython
cdef int compute(int x, int y=10):
    return x + y
```

Default values are specified in the implementation (`.pyx`), not the declaration (`.pxd`).

## C Name Specifications

Resolve naming conflicts between Python and C names:

```cython
cdef extern from "myheader.h":
    void c_yield "yield" (float speed)  # Cython name: c_yield, C name: yield
```

## Grouping Declarations

```cython
cdef:
    int a
    double b
    char *c
```
