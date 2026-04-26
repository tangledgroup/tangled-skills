# Module Preparation

## cdef() Syntax

`ffi.cdecl()` declares C types, functions, constants, and global variables. The syntax follows C declaration rules with some CFFI-specific extensions.

### Supported Declarations

**Functions:**

```python
ffi.cdef("""
    int printf(const char *format, ...);
    void *malloc(size_t size);
    double sin(double x);
""")
```

**Structures:**

```python
ffi.cdef("""
    struct point {
        int x;
        int y;
    };

    // Partial struct — C compiler fills in unknown fields
    struct passwd {
        char *pw_name;
        ...;
    };
""")

**Unions:**

```python
ffi.cdef("""
    union value {
        int ival;
        double dval;
        char *sval;
    };
""")
```

**Enums:**

```python
ffi.cdef("""
    enum color { RED, GREEN, BLUE };

    // Unknown values — compiler resolves
    enum flags { A, B, C, ... };
    // Or partial known values
    enum status { OK=0, ERROR=..., TIMEOUT=... };
""")
```

**Typedefs:**

```python
ffi.cdef("""
    typedef unsigned long size_t;

    // Opaque type — useful for handles
    typedef ... foo_t;
    typedef ... *foo_p;
""")
```

Note: `typedef ... foo_t` declares an opaque struct-like type only. You cannot use it to declare integer or float types. For unknown integer types, use `typedef int... my_type;`.

**Constants:**

```python
ffi.cdef("""
    #define MAX_PATH 260
    static const int VERSION = 42;
    static const char *const PROGRAM_NAME;
""")
```

For macros with unknown integer values:

```python
ffi.cdef("#define FOO_SIZE ...")
# Access as lib.FOO_SIZE — compiler resolves the value
```

**Global Variables:**

```python
ffi.cdef("""
    extern int errno;
    extern FILE *stdout;
    FILE *const stdin;  // read-only global
""")
```

### What cdef() Does Not Support

- `#include` or `#ifdef` preprocessor directives
- `__attribute__` or `#pragma pack(n)`
- Vector types, special-size floating point
- `__restrict__` or `__restrict` (but plain `restrict` is accepted and ignored)
- C++ declarations

### Multiple cdef() Calls

You can call `cdef()` multiple times on the same FFI instance to split declarations across files:

```python
ffi.cdef("int foo(int);")
ffi.cdef("void bar(void);")
# Both declarations are available
```

Each call is validated against previous ones — mismatched declarations raise errors.

## set_source() Parameters

`ffibuilder.set_source(module_name, c_source, **kwargs)` configures the out-of-line module build:

### Module Name

The name of the generated extension module. Use `_` prefix convention:

```python
ffibuilder.set_source("_mylib", ...)
# Generates _mylib.so / _mylib.pyd
```

For packages, use dotted notation:

```python
ffibuilder.set_source("mypackage._mylib", ...)
# Generates mypackage/_mylib.so
```

### C Source Code

- **String**: C code (with `#include` directives) to include in the generated file. This is where you reference header files and can define helper functions.
- **None**: ABI mode — no C compilation, declarations only.

```python
ffibuilder.set_source("_mylib",
    r"""
        #include <stdlib.h>
        #include "my_custom_header.h"

        // Helper function available to Python
        static int my_helper(int x) {
            return x * 42;
        }
    """)
```

### Compiler Keywords

All standard distutils/setuptools keywords are supported:

```python
ffibuilder.set_source("_mylib",
    r"#include <math.h>",
    libraries=["m"],           # link libm
    include_dirs=["/usr/local/include"],
    library_dirs=["/usr/local/lib"],
    sources=["extra_code.c"],  # additional C source files
    define_macros=[("DEBUG", "1")],
    extra_compile_args=["-O2"],
    extra_link_args=["-Wl,-rpath,/opt/lib"],
    )
```

### API vs ABI in set_source()

CFFI selects the mode based on whether `c_source` is `None` or not:

- `set_source("_mod", None)` → out-of-line ABI mode (generates `.py`)
- `set_source("_mod", "#include <foo.h>")` → out-of-line API mode (generates `.c` then compiles)

## Compiling Modules

### ffibuilder.compile()

```python
if __name__ == "__main__":
    ffibuilder.compile(tmpdir=".", verbose=True, debug=False)
```

- `tmpdir`: output directory for generated files
- `verbose`: print compiler commands
- `debug`: compile with debug symbols (defaults to `sys.flags.debug`)

### Emitting Without Compiling

```python
ffibuilder.emit_c_code("my_module.c")     # generate C source only
ffibuilder.emit_python_code("my_module.py")  # generate Python wrapper (ABI mode)
```

Since v1.17.1, these accept file-like objects (e.g., `io.StringIO`).

### Setuptools Integration

In `setup.py`:

```python
from setuptools import setup

setup(
    name="my_package",
    version="1.0",
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["my_lib_build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
)
```

The `cffi_modules` parameter takes `"path/to/build_script.py:variable_name"` where the variable is an FFI instance or a function returning one.

For distutils-based builds:

```python
ext = ffibuilder.distutils_extension(tmpdir="build", verbose=True)
setup(ext_modules=[ext])
```

## dlopen() in ABI Mode

`ffi.dlopen(name)` loads a shared library and returns a `FFILibrary` object:

```python
lib = ffi.dlopen(None)           # standard C library (Unix)
lib = ffi.dlopen("libfoo.so")    # specific library
lib = ffi.dlopen("/usr/lib/libbar.so.1")  # full path
```

On Windows, use `ctypes.util.find_library()` for name resolution:

```python
import ctypes.util
path = ctypes.util.find_library("msvcrt")
lib = ffi.dlopen(path)
```

In out-of-line ABI mode, `dlopen()` does not perform automatic library discovery — it passes the name directly to the platform's loader.

### Closing Libraries

Since v1.14.3:

```python
lib = ffi.dlopen("libfoo.so")
# ... use lib ...
ffi.dlclose(lib)  # explicitly close
```

## Combining Interfaces with include()

`ffi.include(other_ffi)` imports typedefs, structs, unions, enums, and constants from another FFI instance:

```python
# In build script A
ffi_a = FFI()
ffi_a.cdef("typedef struct { int x; } point_t;")

# In build script B
ffi_b = FFI()
ffi_b.include(ffi_a)
ffi_b.cdef("""
    void draw_point(point_t *p);  // can use point_t from ffi_a
""")
```

This is the cdef-level equivalent of `#include` in C. Use it for large projects where one interface depends on types from another.

## Debugging dlopen'ed Libraries

Environment variables for debugging dynamic loading issues on Linux:

```bash
export LD_TRACE_LOADED_OBJECTS=all  # verbose linker info
export LD_VERBOSE=1                 # symbol versioning info
export LD_WARN=1                    # warn about unresolved symbols
```

## cdef() Limitations Summary

- All ANSI C89 declarations supported, some C99
- No preprocessor (`#include`, `#ifdef`)
- No `__attribute__` or `#pragma pack`
- Complex numbers (`float _Complex`, `double _Complex`) supported in data but not as function arguments in ABI mode
- `int field[]` in structs = variable-length array
- `int field[...]` in structs = compiler-determined length
- Thread-local variables (`__thread`) supported since v1.2
- Dynamic macro variables (`#define myvar (*fetchme())`) supported since v1.2

## Deprecated: ffi.verify()

`ffi.verify()` is the old inline API mode, deprecated in favor of `set_source()`. It compiles and loads a module on-the-fly:

```python
lib = ffi.verify("const int mysize = sizeof(THE_TYPE);")
print(lib.mysize)
```

Use cases remaining: quick type size inspection during development. The out-of-line `set_source()` approach is preferred for all production use.
