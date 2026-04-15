# CFFI Modes - Complete Guide

## Overview

CFFI provides multiple modes of operation that control how Python code interacts with C libraries. Understanding these modes is crucial for choosing the right approach for your use case.

## Mode Dimensions

CFFI modes can be understood along two independent dimensions:

### 1. ABI vs API Level

**ABI (Application Binary Interface) Level**
- Works at the binary level with compiled shared libraries
- Uses libffi to make function calls
- No C compiler needed at runtime
- Must know exact struct layouts (field order, sizes, padding)
- Risk of crashes if declarations don't match actual binary layout

**API (Application Programming Interface) Level**
- Works at the source code level with C headers/sources
- Compiles C wrapper code around your declarations
- Requires C compiler during build
- More portable across platforms
- C compiler validates your declarations
- Can use `...` in struct declarations to skip unknown fields

### 2. In-Line vs Out-of-Line

**In-Line Mode**
- Declarations and usage in the same Python file
- Simple for scripts and prototypes
- Slower import times (parses declarations on each import)
- Not ideal for distribution

**Out-of-Line Mode**
- Separates build script from runtime code
- Build script generates C extension module
- Runtime code imports pre-compiled module
- Faster import times
- Better for package distribution
- Supports setuptools integration

## Mode Combinations

### ABI + In-Line (Most Common for Simple Use)

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    int printf(const char *format, ...);
    char *getenv(const char *name);
""")

lib = ffi.dlopen(None)  # Load C library
lib.printf(b"Hello!\n")

home = lib.getenv(b"HOME")
print(ffi.string(home).decode())
```

**When to use:**
- Quick scripts and prototypes
- Calling system libraries without distribution
- Development and testing
- When you don't have a C compiler available

**Pros:**
- Simplest to use
- No build step required
- Works immediately after installing CFFI

**Cons:**
- Slower (uses libffi for all calls)
- Must know exact struct layouts
- Crashes possible if declarations are wrong
- Declarations parsed on every import

### API + Out-of-Line (Recommended for Production)

Build script (`build_cffi.py`):
```python
from cffi import FFI

ffibuilder = FFI()

# Declare types and functions
ffibuilder.cdef("""
    struct passwd {
        char *pw_name;
        char *pw_passwd;
        int pw_uid;
        int pw_gid;
        // ... can skip fields we don't need
    };
    struct passwd *getpwuid(int uid);
    void endpwent(void);
""")

# Specify C source/includes (can be empty string for system libs)
ffibuilder.set_source(
    "_passwd_wrapper",  # Output module name
    "",  # No additional C source needed
    libraries=["c"]  # Link with standard C library
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

Runtime code (`use_passwd.py`):
```python
from _passwd_wrapper import ffi, lib

pw = lib.getpwuid(0)  # Get root user
print(f"Username: {ffi.string(pw.pw_name).decode()}")
```

**When to use:**
- Production applications
- Distributable packages
- When performance matters
- Working with complex struct layouts
- Cross-platform projects

**Pros:**
- Fast (direct C calls, no libffi overhead)
- Portable (C compiler handles platform differences)
- Safe (compile-time validation of declarations)
- Can use `...` in structs to skip unknown fields
- Fast import times (declarations compiled once)

**Cons:**
- Requires C compiler for build step
- More complex setup
- Build artifacts need to be managed

### ABI + Out-of-Line (Hybrid Approach)

Build script (`build_abi.py`):
```python
from cffi import FFI

ffibuilder = FFI()

# Set source to None for ABI mode
ffibuilder.set_source("_mylib", None)

ffibuilder.cdef("""
    int my_function(int x, int y);
    void *my_malloc(size_t size);
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

Runtime code:
```python
from _mylib import ffi

# Still need to dlopen at runtime
lib = ffi.dlopen("libmylib.so")  # Must use full filename
result = lib.my_function(5, 10)
```

**When to use:**
- Large C header files (parsing is slow in in-line mode)
- When you need fast imports but can't use API mode
- Version-specific declarations (can generate different modules per version)
- Binary-only libraries without headers

**Pros:**
- Fast import times (declarations compiled to Python module)
- No C compiler needed at runtime
- Can do complex build-time logic for declarations

**Cons:**
- Still uses libffi (slower than API mode)
- Must know exact struct layouts
- `dlopen()` path handling is platform-specific

### API + In-Line (Deprecated)

```python
from cffi import FFI

ffi = FFI()
lib = ffi.verify("""
    int add(int x, int y) {
        return x + y;
    }
""")

result = lib.add(5, 10)
```

**Status:** Long deprecated in favor of API + Out-of-Line

**Why avoid:**
- Slower than out-of-line variant
- More problematic as projects grow
- Same benefits as out-of-line without the drawbacks

## Mode Selection Guide

### Decision Tree

```
Do you need to distribute the package?
├─ Yes → Use API + Out-of-Line
│         (setuptools integration, wheels)
│
└─ No → Is performance critical?
         ├─ Yes → Use API + Out-of-Line
         │          (faster than ABI mode)
         │
         └─ No → Do you have C headers/sources?
                  ├─ Yes → Use API + Out-of-Line
                  │         (safer, more portable)
                  │
                  └─ No → Use ABI + In-Line
                           (simplest for quick scripts)
```

### Specific Scenarios

**Wrapping system libraries (e.g., libc, libssl):**
- Use API + Out-of-Line if you have headers
- Use ABI + Out-of-Line for fast imports with many declarations
- Use ABI + In-Line for simple scripts

**Calling custom compiled libraries:**
- If you control the build: API + Out-of-Line
- If binary-only: ABI mode (in-line or out-of-line)

**Embedding Python in C:**
- Always use out-of-line mode
- See [06-embedding.md](06-embedding.md) for details

**Performance-critical code:**
- API mode is essential (2-10x faster than ABI)
- Consider implementing hot paths in C directly via `set_source()`

**Cross-platform libraries:**
- API mode handles platform differences automatically
- Use `...` in struct declarations to ignore platform-specific fields

## Setuptools Integration

For distributable packages, integrate with setuptools:

`setup.py`:
```python
from setuptools import setup

setup(
    name="my-cffi-package",
    version="1.0.0",
    # Build-time dependency for generating C extension
    setup_requires=["cffi>=1.0.0"],
    # Runtime dependency
    install_requires=["cffi>=1.0.0"],
    # CFFI build scripts
    cffi_modules=["build_cffi.py:ffibuilder"],
)
```

Then users can install with:
```bash
pip install .
```

The C extension will be built automatically during installation.

## Performance Comparison

| Mode | Import Time | Call Overhead | Best For |
|------|-------------|---------------|----------|
| ABI + In-Line | Slow (parse declarations) | High (libffi) | Quick scripts |
| ABI + Out-of-Line | Fast | High (libffi) | Large headers, binary-only libs |
| API + Out-of-Line | Fast | Low (direct C) | Production, performance |
| API + In-Line | Slow (compile on import) | Low (direct C) | Deprecated |

## Common Pitfalls

### ABI Mode Struct Layout Issues

```python
# WRONG: Assuming struct layout without verification
ffi.cdef("""
    struct mystuct {
        int a;
        double b;  # Might have padding before this!
        char c;
    };
""")

# RIGHT: Use API mode or verify with compiler
ffibuilder.set_source("mymodule", """
    #include "mystuct.h"  // Let compiler handle layout
""")
```

### Path Handling in dlopen()

```python
# WRONG on most systems
lib = ffi.dlopen("foo")  # Won't find libfoo.so

# RIGHT: Use full filename or ctypes helper
lib = ffi.dlopen("libfoo.so")  # Linux/macOS
lib = ffi.dlopen(ctypes.util.find_library("foo"))  # Cross-platform
```

### Forgetting to Convert Strings

```python
# WRONG: Treating C string as Python string
pw = lib.getpwuid(0)
print(pw.pw_name)  # <cdata 'char *'> not usable as string

# RIGHT: Convert with ffi.string()
username = ffi.string(pw.pw_name).decode('utf-8')
print(username)  # "root"
```

## Migration Guide

### From ABI In-Line to API Out-of-Line

**Before (ABI in-line):**
```python
from cffi import FFI

ffi = FFI()
ffi.cdef("int foo(int x);")
lib = ffi.dlopen("libfoo.so")
```

**After (API out-of-line):**

Build script:
```python
from cffi import FFI
ffibuilder = FFI()
ffibuilder.cdef("int foo(int x);")
ffibuilder.set_source("_foo", "", libraries=["foo"])
if __name__ == "__main__":
    ffibuilder.compile()
```

Runtime:
```python
from _foo import lib
result = lib.foo(42)
```

### From ctypes to CFFI

**Before (ctypes):**
```python
import ctypes
lib = ctypes.CDLL("libfoo.so")
lib.foo.argtypes = [ctypes.c_int]
lib.foo.restype = ctypes.c_int
result = lib.foo(42)
```

**After (CFFI):**
```python
from cffi import FFI
ffi = FFI()
ffi.cdef("int foo(int x);")
lib = ffi.dlopen("libfoo.so")
result = lib.foo(42)  # Type checking automatic
```

## References

- [Official CFFI Documentation - Overview](https://cffi.readthedocs.io/en/stable/overview.html)
- [Using the ffi/lib objects](https://cffi.readthedocs.io/en/stable/using.html)
- [Preparing and Distributing modules](https://cffi.readthedocs.io/en/stable/cdef.html)
