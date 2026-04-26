# ABI vs API Mode

## Overview

CFFI operates at two distinct levels: ABI (Application Binary Interface) and API (Application Programming Interface). The choice between them affects performance, portability, build requirements, and how you declare C types.

## ABI Mode

ABI mode works at the binary level. You declare C types and functions, then use `ffi.dlopen()` to load a compiled shared library. Function calls go through libffi, which handles the calling convention translation at runtime.

### How It Works

```python
import cffi

ffi = cffi.FFI()
ffi.cdef("""
    int printf(const char *format, ...);
""")
lib = ffi.dlopen(None)  # None = standard C library on Unix
lib.printf(b"Hello %d\n", 42)
```

For specific libraries:

```python
lib = ffi.dlopen("libfoo.so")     # Linux
lib = ffi.dlopen("libfoo.dylib")  # macOS
# On Windows, use ctypes.util.find_library() for discovery:
import ctypes.util
lib = ffi.dlopen(ctypes.util.find_library("msvcrt"))
```

### Advantages

- No C compiler needed at runtime or build time
- Simplest setup — just declare and load
- Good for quick prototyping

### Disadvantages

- Slower function calls (goes through libffi indirection)
- Struct layouts must be declared exactly — no `...` ellipsis support
- On non-Windows platforms, C libraries typically document an API but not a stable ABI
- More fragile across platform differences
- libffi may crash on less common architectures for callbacks

### When to Use

- Quick one-off calls to well-known system libraries
- Prototyping before committing to API mode
- Parsing binary file formats (declaring struct layouts without linking)
- When a C compiler is not available

## API Mode

API mode compiles a C wrapper that directly invokes target functions. The C compiler validates declarations, resolves symbols through the linker, and fills in struct layout details from header files.

### How It Works

Create a build script:

```python
# example_build.py
from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef("""
    struct passwd {
        char *pw_name;
        ...;     // literally dot-dot-dot — C compiler fills this in
    };
    struct passwd *getpwuid(int uid);
""")

ffibuilder.set_source("_example",
    r"""
        #include <pwd.h>
    """,
    libraries=["c"])  # link libc explicitly if needed

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

Run the build script once to generate `_example.c` and compile it to `_example.so` (or `.pyd` on Windows):

```bash
python example_build.py
```

Then use in your application:

```python
from _example import ffi, lib

p = lib.getpwuid(0)
print(ffi.string(p.pw_name))  # b'root'
```

### The Ellipsis (`...`) Syntax

In API mode, `...` tells CFFI to let the C compiler fill in unknown details:

```python
# Unknown struct fields — compiler determines layout
struct passwd {
    char *pw_name;
    ...;
};

# Unknown enum values — compiler determines actual integers
enum foo { A, B, C, ... };

# Unknown macro value — compiler resolves it
#define FOO_SIZE ...

# Unknown array length in struct field or global
extern int n[...];

# Unknown integer type size
typedef int... my_int_type;
```

### Advantages

- Faster function calls (direct invocation, no libffi overhead)
- More portable — C compiler validates everything
- Can use `...` for unknown struct fields, enum values, macro constants
- Works with complex types that libffi cannot handle (complex numbers as arguments)
- Generates code independent of platform/Python version

### Disadvantages

- Requires a C compiler at build time
- Build step adds complexity to distribution
- Generated `.so` depends on `_cffi_backend` module

### When to Use

- Production libraries where performance matters
- Wrapping complex C APIs with structs whose layouts vary by platform
- When you need the safety of C compiler validation
- Distributing precompiled extension modules

## Out-of-Line ABI Mode

A hybrid approach: use `set_source()` with `None` to pre-generate the declarations, then call `ffi.dlopen()` at runtime. This reduces import time for large declaration sets while keeping ABI mode flexibility.

```python
# build script
from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_source("_simple_example", None)  # None = ABI mode
ffibuilder.cdef("""
    int printf(const char *format, ...);
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

```python
# application
from _simple_example import ffi
lib = ffi.dlopen(None)  # Unix: open standard C library
lib.printf(b"hi there\n")
```

Note: the out-of-line `ffi.dlopen()` does not perform automatic library name resolution — you must provide a path as required by the platform's `dlopen()` or `LoadLibrary()`.

## Performance Comparison

API mode is significantly faster than ABI mode for function calls because it generates direct C calls rather than going through libffi's generic calling mechanism. The difference is most noticeable in tight loops calling small C functions.

Import time: in-line ABI mode parses declarations on every import. Out-of-line modes (both API and ABI) pre-compile declarations, resulting in much faster imports.

## Migration from ctypes

If migrating from ctypes, prefer API mode for production use. The declaration syntax is similar to ctypes but closer to actual C header files. Use `...` for any struct fields you don't need to access — the C compiler will handle them correctly.
