---
name: cffi-2-0-0
description: Python C Foreign Function Interface for calling C libraries from Python
  with C-like declarations. Use when interfacing with C code, wrapping C libraries,
  creating Python extensions, embedding Python in C applications, or needing high-performance
  C integration without writing traditional C extension modules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: 2.0.0
tags:
- cffi
- c-integration
- ffi
- foreign-function-interface
- python-c-bindings
- c-libraries
category: language-tools
external_references:
- https://cffi.readthedocs.io/en/stable/
- https://py-free-threading.github.io/
- https://pypi.org/project/cffi/
- https://sourceware.org/libffi/
- https://github.com/python-cffi/cffi/tree/v2.0.0
---

# CFFI 2.0.0

## Overview

CFFI (C Foreign Function Interface) is a Python library for calling C code from Python using C-like declarations that can often be copy-pasted directly from header files. Based on LuaJIT's FFI design, it requires users to know only C and Python — no third-party DSL or complex API to learn.

CFFI supports both CPython (3.9–3.14) and PyPy. It is the recommended way to interface with C libraries on PyPy due to minimal JIT overhead. On CPython, it outperforms ctypes in core speed with better import times when using out-of-line modules.

The library has two operational modes:
- **ABI mode** — works at the binary level using libffi, like ctypes. No C compiler needed at runtime but more fragile across platforms.
- **API mode** — compiles a C wrapper that directly invokes target functions. Requires a C compiler at build time but is faster and more portable.

CFFI 2.0.0 adds support for free-threaded CPython (3.14t+), Python 3.14, and drops Python 3.8. It depends on libffi (bundled for Windows) and pycparser >= 2.06.

## When to Use

- Wrapping existing C libraries for use from Python without writing traditional `Python.h` extension modules
- Calling system C APIs (`getpwuid`, `printf`, libc functions) from Python
- Creating high-performance numerical or computational code by writing hot paths in C and calling them from Python
- Embedding Python inside a C/C++ application to expose Python logic as a native shared library
- Building plugins for existing C/C++ programs that load `.so`/`.dll` modules
- Replacing ctypes bindings when better performance or API-mode portability is needed
- Working with C structs, unions, enums, and global variables from Python
- Implementing callbacks from C into Python (via `extern "Python"` or `ffi.callback()`)

## Core Concepts

**Two Modes of Operation:**

- **ABI mode** uses `ffi.dlopen()` to load a compiled shared library. The CFFI layer calls functions through libffi at runtime. No C compiler is needed, but struct layouts must be declared exactly — and on non-Windows platforms, C libraries typically document an API, not a stable ABI.

- **API mode** uses `ffibuilder.set_source()` to compile a C extension module. The C compiler validates declarations and links symbols. This is faster at runtime and more portable because the C compiler fills in struct layout details (using `...` placeholders).

**The cdef() Declaration:**

All C types, functions, constants, and global variables are declared using `ffi.cdef()` with C-like syntax:

```python
ffi.cdef("""
    int printf(const char *format, ...);
    struct passwd {
        char *pw_name;
        ...;
    };
    struct passwd *getpwuid(int uid);
""")
```

The `...` (dot-dot-dot) syntax tells CFFI to let the C compiler fill in unknown details — available only in API mode.

**The ffi and lib Objects:**

- `ffi` — the FFI interface object providing methods like `ffi.new()`, `ffi.cast()`, `ffi.string()`, `ffi.sizeof()`
- `lib` — the library object (from `ffi.dlopen()` or imported from an out-of-line module) exposing declared C functions, constants, and global variables as attributes

**cdata Objects:**

All C values in Python are wrapped as `<cdata>` objects. These represent C integers, pointers, structs, arrays, and function pointers with proper type checking and conversion between Python and C types.

**Embedding Mode:**

CFFI can generate a shared library (`.so`/`.dll`) that embeds the Python interpreter. C applications load this library without knowing it contains Python. The `ffibuilder.embedding_api()` declares exported functions, and `@ffi.def_extern()` attaches Python implementations to them.

## Installation / Setup

Install via pip:

```bash
pip install cffi
```

On non-Windows platforms, you need:
- A C compiler (gcc, clang)
- `libffi-dev` package (to compile CFFI itself)
- `python3-dev` or equivalent headers
- `pkg-config` (for libffi detection on Linux)

On macOS with Homebrew:
```bash
brew install pkg-config libffi
PKG_CONFIG_PATH=$(brew --prefix libffi)/lib/pkgconfig pip install cffi
```

CFFI is distributed bundled with PyPy. Python 3.9–3.14 are supported (2.0.0 drops 3.8). For free-threaded CPython, use 3.14t+ only (3.13t is not yet supported due to sync primitive differences).

## Usage Examples

**Quick ABI mode — calling libc printf:**

```python
import cffi

ffi = cffi.FFI()
ffi.cdef("int printf(const char *format, ...);")
lib = ffi.dlopen(None)  # load standard C library on Unix
lib.printf(b"Hello from CFFI! Number %d\n", 42)
```

**Allocating and using C structs:**

```python
ffi.cdef("""
    struct point { int x; int y; };
    int distance(struct point *p);
""")
lib = ffi.dlopen("libgeom.so")

p = ffi.new("struct point *", {"x": 3, "y": 4})
result = lib.distance(p)
```

**Out-of-line API mode build script:**

```python
# my_lib_build.py
from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""
    struct passwd {
        char *pw_name;
        ...;
    };
    struct passwd *getpwuid(int uid);
""")
ffibuilder.set_source("my_lib",
    r"""
        #include <pwd.h>
    """)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

Then in your application:

```python
from my_lib import ffi, lib

p = lib.getpwuid(0)
print(ffi.string(p.pw_name))  # b'root'
```

**Callbacks with extern "Python":**

```python
# In build script cdef():
ffibuilder.cdef("""
    extern "Python" int my_callback(int, int);
    void library_function(int(*callback)(int, int));
""")

# In application code:
from my_lib import ffi, lib

@ffi.def_extern()
def my_callback(x, y):
    return x + y

lib.library_function(lib.my_callback)
```

## Advanced Topics

**ABI vs API Mode**: Detailed comparison of the two operational modes, when to choose each, and the `...` ellipsis syntax → See [ABI vs API Mode](reference/01-abi-vs-api-mode.md)

**Working with Pointers, Structs, and Arrays**: Memory allocation with `ffi.new()`, casting, buffer access, pointer arithmetic, struct field access, array slicing, and FILE* handling → See [Pointers, Structs & Arrays](reference/02-pointers-structs-arrays.md)

**Callbacks and extern "Python"**: New-style callbacks with `extern "Python"` / `@ffi.def_extern()`, old-style `ffi.callback()`, void* userdata patterns, error handling with `onerror`, and Windows calling conventions → See [Callbacks](reference/03-callbacks.md)

**Preparing and Distributing Modules**: `cdef()` syntax details, `set_source()` parameters, `dlopen()`, setuptools integration, combining interfaces with `include()`, and cdef limitations → See [Module Preparation](reference/04-module-preparation.md)

**Embedding Python in C Applications**: Creating shared libraries from Python code, `embedding_api()`, `embedding_init_code()`, multithreading, multiple DLLs, testing, and troubleshooting → See [Embedding](reference/05-embedding.md)

**FFI API Reference**: Complete reference for `ffi.new()`, `ffi.cast()`, `ffi.string()`, `ffi.buffer()`, `ffi.from_buffer()`, `ffi.gc()`, `ffi.sizeof()`, `ffi.typeof()`, `ffi.addressof()`, `ffi.new_allocator()`, `ffi.release()`, `ffi.init_once()`, type conversions, and thread safety → See [FFI API Reference](reference/06-ffi-api-reference.md)

**v2.0.0 Changes**: Free-threaded CPython support, Python 3.14 compatibility, dropped 3.8 support, and migration notes → See [What's New in 2.0.0](reference/07-whats-new-2-0-0.md)
