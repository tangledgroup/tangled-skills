# External C/C++ Code

## Referencing C Header Files

The primary way to interface with external C code is `cdef extern from`:

```cython
cdef extern from "spam.h":
    int spam_counter
    void order_spam(int tons)
    struct Bunny:
        int vorpalness
```

This does three things:
1. Places `#include "spam.h"` in the generated C code
2. Prevents Cython from generating C declarations for the block contents
3. Treats all declarations as `extern`

**Important:** Cython does not parse the header file itself — you must provide Cython-compatible declarations manually.

## Header File Adaptation

When declaring external headers, adapt as needed:

- Omit platform-specific extensions like `__declspec()`
- Declare only the struct members you need (C compiler uses the full definition from the header)
- For unused structs, use `pass`:
  ```cython
  cdef extern from "foo.h":
      struct spam:
          pass
  ```
- Replace C `typedef` names with `ctypedef`:
  ```cython
  ctypedef int word  # whatever the platform defines 'word' as
  ```
- Translate C macro constants into enum or variable declarations
- Declare macro functions as ordinary functions

## Include Variations

```cython
# System header
cdef extern from "<sysheader.h>":
    ...

# No specific header (already included elsewhere)
cdef extern from "*":
    ...

# Include only, no declarations
cdef extern from "spam.h":
    pass
```

## Verbatim C Code

Embed raw C code as a docstring in an `extern from` block:

```cython
cdef extern from "*":
    """
    long c_square(long x) {
        return x * x;
    }
    """
    long c_square(long x)
```

Use raw strings (`r"""..."""`) when character escapes must pass through to C:

```cython
cdef extern from "*":
    r"""
    #define MY_PATH "C:\\path\\to\\file"
    """
    ...
```

## Platform-Specific Adaptation

```cython
cdef extern from "*":
    """
    #ifdef _WIN32
    #define PLATFORM "windows"
    #else
    #define PLATFORM "unix"
    #endif
    """
    const char* PLATFORM
```

## Implementing Functions in C

Compile C code directly as part of the Cython module:

```cython
# In .pyx file
cdef extern from "helper.c":
    void helper_func(int tons)

# Tell distutils to include the source
# distutils: sources = helper.c
```

The function in `helper.c` must be `static` to match Cython's expectations.

## Pointers

Pass pointers using `&` for address-of and `[0]` for dereferencing:

```cython
cdef extern from "my_lib.h":
    void increase_by_one(int *my_var)

cdef int some_int = 42
increase_by_one(&some_int)
# Or with an intermediate variable
cdef int *ptr = &some_int
increase_by_one(ptr)
```

Dereference pointers using array access (`ptr[0]`), not `*ptr`.

## Python/C API Access

Access Python C API routines:

```cython
cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *s, Py_ssize_t len)
```

Cython provides ready-made declarations in `cpython.*` modules. Always use submodules:

```cython
from cpython.object cimport PyObject
from cpython.list cimport PyList_Append
```

## Resolving Naming Conflicts

Put extern declarations in `.pxd` files to separate namespaces:

```cython
# decl.pxd
cdef extern from "myheader.h":
    void eject_tomato(float speed)
```

```cython
# module.pyx
from decl cimport eject_tomato as c_eject_tomato

def eject_tomato(speed):
    c_eject_tomato(speed)
```

Or use the module prefix:

```cython
cimport decl

def eject_tomato(speed):
    decl.eject_tomato(speed)
```

## Public Declarations

Make C declarations available to external C code by generating a header file:

```cython
cdef public struct Bunny:
    int vorpalness

cdef public int spam
cdef public void grail(Bunny *)
```

This generates `modulename.h` with equivalent C declarations.

## C API Declarations

Export functions dynamically via the Python import mechanism:

```cython
cdef api void exported_func(int x):
    ...
```

Generates `modulename_api.h` and `import_modulename()` function. External C code calls `import_modulename()` before using exported functions.

## Struct Declaration Styles

Match the Cython declaration to the C header style:

- `typedef struct { ... } Foo;` → `ctypedef struct Foo: ...`
- `struct Foo { ... };` → `cdef struct Foo: ...`
- `typedef struct foo { ... } Foo;` → `cdef struct foo: ...` or `ctypedef struct Foo: ...`

## Windows Calling Conventions

```cython
cdef extern int __stdcall FrobnicateWindow(long handle)
cdef void (__stdcall *callback)(void *)
```
