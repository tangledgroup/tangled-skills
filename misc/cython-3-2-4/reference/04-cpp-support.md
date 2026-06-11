# Using C++ in Cython

## Overview

Cython has native support for most C++ features:

- Dynamic allocation with `new`/`del`
- Stack allocation of C++ objects
- `cppclass` declarations
- Templates (classes and functions)
- Function overloading
- Operator overloading

## Declaring C++ Classes

Use `cdef cppclass` inside an `extern from` block:

```cython
cdef extern from "Rectangle.h" namespace "shapes":
    cdef cppclass Rectangle:
        Rectangle(double x0, double y0, double x1, double y1) except +
        double get_area()
        void move(double dx, double dy)
        double x0, y0, x1, y1
```

The `except +` on the constructor lets Cython convert C++ exceptions to Python exceptions.

## Enabling C++ Mode

Add to `.pyx` file:

```cython
# distutils: language = c++
```

Or in `setup.py`:

```python
Extension("module", ["module.pyx"], language="c++")
```

This tells Cython to generate `.cpp` instead of `.c`.

## Using C++ Objects

**Heap allocation:**

```cython
cdef Rectangle *rect_ptr = new Rectangle(1, 2, 3, 4)
print(rect_ptr[0].get_area())   # dereference with [0]
del rect_ptr
```

**Stack allocation** (requires default constructor):

```cython
cdef extern from "Foo.h":
    cdef cppclass Foo:
        Foo()

def func():
    cdef Foo foo  # stack-allocated, auto-destructed
    ...
```

## Creating Python Wrapper Classes

Pattern: extension type holds a C++ instance with forwarding methods:

```cython
# rect.pyx
from Rectangle cimport Rectangle

cdef class PyRectangle:
    cdef Rectangle *thisptr

    def __cinit__(self, double x0, double y0, double x1, double y1):
        self.thisptr = new Rectangle(x0, y0, x1, y1)

    def __dealloc__(self):
        del self.thisptr

    cpdef double get_area(self):
        return self.thisptr[0].get_area()

    cpdef void move(self, double dx, double dy):
        self.thisptr[0].move(dx, dy)
```

**Simplified wrapping with default constructor:**

When the C++ class has a nullary constructor, you can store an instance directly (no pointer needed):

```cython
cdef class PyVector:
    cdef cppclass Vector:
        Vector()
        void push_back(int x)

    cdef Vector _vec  # auto-constructed and destructed
```

## Operator Overloading

Use C++ operator names in declarations:

```cython
cdef extern from "foo.h":
    cdef cppclass Foo:
        Foo()
        Foo operator+(Foo)
        Foo operator-(Foo)
        int operator*(Foo)
        int operator[](int)

cdef Foo foo = new Foo()
foo2 = foo + foo
x = foo[0]
del foo
```

For pointers, dereference first: `ptr[0] + ptr[0]` (not `ptr + ptr`).

## Operators Not Compatible with Python Syntax

Use `cython.operator` module:

```cython
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from cython.operator cimport address

cdef Foo *ptr = new Foo()
deref(ptr)         # produces *(ptr)
preinc(some_var)   # produces ++(some_var)
address(obj)       # produces &(obj), same as &obj
```

Also available: `predecrement`, `postincrement`, `postdecrement`, `comma`.

## Templates

**Class templates:**

```cython
cdef extern from "<vector>" namespace "std":
    cdef cppclass vector[T]:
        cppclass iterator:
            T operator*()
            iterator operator++()
            bint operator==(iterator)
            bint operator!=(iterator)
        vector() except +
        void push_back(T &)
        T operator[](cython.size_t)
        T &at(cython.size_t)
        iterator begin()
        iterator end()
        cython.size_t size()
```

Instantiate with bracket syntax: `vector[double]`, `vector[int]`.

Multiple template parameters: `[T, U, V]` or `[int, bool, char]`.

Optional template parameters: `[T, U, V=*]`.

**Function templates:**

```cython
cdef extern from "algo.h":
    T my_max[T](T a, T b)

result = my_max[double](1.0, 2.0)
```

## STL Containers

Cython provides `.pxd` declarations for common STL containers in `libcpp`:

- `libcpp.vector`, `libcpp.list`, `libcpp.deque`
- `libcpp.map`, `libcpp.unordered_map`
- `libcpp.set`, `libcpp.unordered_set`
- `libcpp.stack`, `libcpp.queue`, `libcpp.pair`

```cython
from libcpp.vector cimport vector

def process():
    cdef vector[double] v
    v.push_back(1.0)
    v.push_back(2.0)
    return list(v)  # automatic conversion to Python list
```

**Automatic conversions between Python and C++ types:**

- `bytes` ↔ `std::string`
- `iterable` ↔ `std::vector`, `std::list`
- `iterable` ↔ `std::set`, `std::unordered_set`
- `mapping` ↔ `std::map`, `std::unordered_map`
- `iterable (len 2)` ↔ `std::pair`
- `complex` ↔ `std::complex`

Conversions copy data and recursively convert nested containers.

## Iteration

Iterate over STL containers with `for .. in`:

```cython
from libcpp.vector cimport vector

cdef vector[int] v = ...
for item in v:
    print(item)
```

Requires `begin()`/`end()` returning iterators supporting increment, dereference, and comparison.

## C++ Exception Handling

Declare functions as potentially throwing C++ exceptions:

```cython
cdef extern from "some_file.h":
    cdef int foo() except +
    cdef int bar() except +MemoryError
```

Cython maps standard C++ exceptions to Python exceptions:

- `bad_alloc` → `MemoryError`
- `bad_cast`, `bad_typeid` → `TypeError`
- `domain_error`, `invalid_argument` → `ValueError`
- `out_of_range` → `IndexError`
- `overflow_error` → `OverflowError`
- `range_error`, `underflow_error` → `ArithmeticError`
- All others → `RuntimeError`

Custom exception handlers are possible:

```cython
cdef int raise_py_error()
cdef int something_dangerous() except +raise_py_error
```

## Nested Classes

```cython
cdef extern from "Outer.h":
    cdef cppclass Outer:
        cppclass Inner:
            int value
        Inner get_inner()
```

## C++ Public Declarations and `extern "C"`

When compiling as C++, public functions default to C++ API. For plain C API:

```python
Extension(
    "module", ["module.pyx"],
    define_macros=[("CYTHON_EXTERN_C", 'extern "C"')],
    language="c++",
)
```
