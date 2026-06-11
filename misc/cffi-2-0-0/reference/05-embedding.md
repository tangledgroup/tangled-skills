# Embedding

## Overview

CFFI's embedding mode generates a shared library (`.so`/`.dll`/`.dylib`) that embeds the Python interpreter. A C application loads this library without knowing it contains Python. The first C function call automatically initializes Python and executes frozen initialization code.

This is entirely independent from the CPython C API — no `Py_Initialize()`, `PyRun_SimpleString()`, or `PyObject`. It works identically on CPython and PyPy.

## Use Cases

- Exposing a Python library directly to C/C++ programs
- Creating a plugin for an existing C/C++ program that loads `.so`/`.dll` modules
- Implementing part of a larger C/C++ application in Python (with static linking)
- Writing a C wrapper around Python to hide its implementation details

## Basic Example

**Header file (`plugin.h`):**

```c
typedef struct { int x, y; } point_t;
extern int do_stuff(point_t *);
```

**Build script (`plugin_build.py`):**

```python
import cffi
ffibuilder = cffi.FFI()

# Declare the C API (read from header, stripping # directives)
with open('plugin.h') as f:
    data = ''.join(line for line in f if not line.startswith('#'))
    ffibuilder.embedding_api(data)

# Include the header for the generated C code
ffibuilder.set_source("my_plugin",
    r'''
        #include "plugin.h"
    ''')

# Frozen Python initialization code
ffibuilder.embedding_init_code("""
    from my_plugin import ffi

    @ffi.def_extern()
    def do_stuff(p):
        print("adding %d and %d" % (p.x, p.y))
        return p.x + p.y
""")

# Compile to plugin-1.5.so / .dll / .dylib
ffibuilder.compile(target="plugin-1.5.*", verbose=True)
```

Running this produces a shared library with the declared C API. The C application links or `dlopen()`s it normally.

## Key Methods

### ffibuilder.embedding_api(source)

Parses C source declaring functions, types, constants, and global variables to be exported by the DLL. Functions are automatically implemented to initialize Python on first call and invoke the attached Python function.

Global variables must be defined explicitly in `set_source()`.

### ffibuilder.embedding_init_code(python_code)

Specifies initialization-time Python source code that is frozen inside the DLL. This code runs when the DLL is first initialized, after Python itself is initialized.

The init code has access to a magical built-in module named after the first argument to `set_source()`:

```python
from my_plugin import ffi, lib
# 'my_plugin' comes from set_source("my_plugin", ...)
# This represents "the caller's C world" from Python's perspective
```

Every function declared in `embedding_api()` must have a corresponding `@ffi.def_extern()` in the init code or its imports.

### ffibuilder.set_source(module_name, c_code)

Sets the module name (used in the frozen import) and provides additional C code for the generated file. The macro `CFFI_DLLEXPORT` is available:

```python
# In embedding_api(): "extern int my_glob;"
# In set_source():
ffibuilder.set_source("my_plugin",
    r'''
        CFFI_DLLEXPORT int my_glob = 42;
    ''')
```

### ffibuilder.compile(target=..., verbose=True)

Generates and compiles the shared library. The `target` parameter controls the output filename:

- Default: `module_name.so` / `.dll` / `.dylib`
- `target="foo.*"`: produces `foo.so`, `foo.dll`, or `foo.dylib` depending on platform
- Use `ffibuilder.emit_c_code("foo.c")` instead to get C source for external compilation

## Windows DLL Export Handling

For Windows compatibility, use a conditional macro in the header:

```c
#ifndef CFFI_DLLEXPORT
#  if defined(_MSC_VER)
#    define CFFI_DLLEXPORT  extern __declspec(dllimport)
#  else
#    define CFFI_DLLEXPORT  extern
#  endif
#endif

CFFI_DLLEXPORT int do_stuff(point_t *);
```

In the build script, strip `#` directives and replace `CFFI_DLLEXPORT`:

```python
with open('plugin.h') as f:
    data = ''.join(line for line in f if not line.startswith('#'))
    data = data.replace('CFFI_DLLEXPORT', '')
    ffibuilder.embedding_api(data)
```

## Multithreading

Multithreading works based on Python's Global Interpreter Lock:

- If two threads call C functions before Python is initialized, one proceeds with initialization while the other blocks
- For different CFFI-made DLLs, Python initialization is serialized but init code for each DLL runs independently
- After initialization, the GIL controls concurrent execution

## Using Multiple CFFI-Made DLLs

Multiple CFFI-generated shared libraries can coexist in the same process. They share a single Python interpreter, similar to how unrelated Python packages share the interpreter in a large application.

## Testing

For testing, import the CFFI-made DLL as a regular Python extension module:

```python
# On Windows, rename from .dll to .pyd or use a symlink
from my_plugin import ffi, lib

# Call C functions directly
result = lib.do_stuff(...)
```

The frozen init code executes on the first function call.

## Embedding and Extending Together

You can combine embedding (`embedding_api()`) and extending (`cdef()`):

```python
ffibuilder.embedding_api("int exported_func(int);")  # exported to C
ffibuilder.cdef("""
    extern "Python" int mycb(int);  # callback from internal C code
""")

ffibuilder.set_source("my_plugin",
    r"""
        static int mycb(int);

        CFFI_DLLEXPORT int myfunc(int a, int b) {
            int product = a * b;
            return mycb(product);  // calls Python via callback
        }
    """)
```

The `myfunc` is a pure C function exported from the DLL. It calls `mycb()` which triggers Python initialization if needed, then invokes the `@ffi.def_extern()` decorated Python function.

## Manual Python Initialization

From C code within `set_source()`, force Python initialization:

```c
// In set_source() C code:
int ok = cffi_start_python();
// Returns 0 on success, -1 on failure
// Note: cffi_start_python() is static — wrap it in a non-static function
// if calling from other source files
```

## Troubleshooting

**"unknown version 0x2701"**: The running Python has CFFI < 1.5 installed. Install CFFI 1.5+ in the target Python.

**PyPy "lib-python and lib_pypy not found"**: The `libpypy-c.so` was found but the standard library is not at the expected location. Keep `libpypy-c.so` inside PyPy's `bin/` directory and symlink from `/usr/lib/`.

**Library path issues**: Use `-Wl,-rpath=` to hard-code paths in the shared library:

```python
ffibuilder.set_source("my_plugin", "",
    extra_link_args=['-Wl,-rpath=$ORIGIN/../venv/bin'])
```

Check embedded paths with `ldd libmy_plugin.so`.

**Debian/Ubuntu `undefined symbol` with `RTLD_LOCAL`**: Work around by loading libpython first:

```c
dlopen("libpython3.X.so", RTLD_LAZY | RTLD_GLOBAL);
```

## Distribution Notes

The generated `.so` does not contain the Python interpreter or standard library. The target system must have Python available. Options:

- Bundle a Python installation alongside the shared library
- Rely on system Python (check version compatibility)
- Use `$ORIGIN` rpath to locate Python relative to the library
