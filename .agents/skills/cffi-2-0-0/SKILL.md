---
name: cffi-2-0-0
description: Python C Foreign Function Interface for calling C libraries from Python with C-like declarations. Use when interfacing with C code, wrapping C libraries, creating Python extensions, embedding Python in C applications, or needing high-performance C integration without writing traditional C extension modules.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.0.0"
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
## Overview
CFFI (C Foreign Function Interface) is a library for calling C code from Python, based on C-like declarations that you can often copy-paste directly from header files or documentation. It provides two main modes: **ABI mode** (calling compiled shared libraries without recompilation) and **API mode** (compiling C wrapper code for better performance and portability).

CFFI 2.0.0 supports Python 3.8+ and includes full support for free-threaded Python 3.14+, with automatic GIL release when calling into C libraries.

## When to Use
Use CFFI when:
- You need to call functions from existing C libraries (system libraries, custom .so/.dll files)
- You want to wrap C code for use in Python without writing traditional C extension modules
- You need to embed Python in C applications (creating .so/.dll that export Python-implemented functions)
- You're working with binary file formats requiring precise struct layouts
- You need high-performance C integration but want Python-level development speed
- You want to compile custom C code alongside your FFI declarations for performance-critical sections

## Core Concepts
### Two Main Modes

**ABI Mode (Binary Level)**
- Calls existing compiled libraries directly using libffi
- No C compiler required at runtime
- Slower than API mode but more portable distribution
- Risk of crashes if struct layouts are misdeclared
- Use `ffi.dlopen()` to load libraries

**API Mode (Source Level)**
- Compiles C wrapper code around your declarations
- Requires C compiler during build, not at runtime
- Faster and more portable across platforms
- C compiler validates struct layouts and function signatures
- Use `FFI().set_source()` with actual C source/includes

### The ffi and lib Objects

```python
from cffi import FFI

ffi = FFI()  # Create FFI object for declarations

# Declare C types and functions
ffi.cdef("""
    int printf(const char *format, ...);
    struct passwd {
        char *pw_name;
        char *pw_passwd;
        int pw_uid;
        int pw_gid;
        // ... can use "..." to skip fields
    };
    struct passwd *getpwuid(int uid);
""")

# Load library (ABI mode)
lib = ffi.dlopen(None)  # None = standard C library on Unix

# Call functions
lib.printf(b"Hello %d!\n", 42)
```

### Out-of-Line vs In-Line

**In-Line Mode**: Declarations and usage in same file, good for simple scripts

**Out-of-Line Mode**: Separates build script from runtime code, better for distribution:
- Build script generates C extension module
- Runtime code imports the compiled module
- Supports setuptools integration for package distribution

## Installation / Setup
### Basic Installation

```bash
pip install cffi>=2.0.0
```

### System Dependencies

CFFI requires `libffi` development files:

**Debian/Ubuntu:**
```bash
sudo apt install libffi-dev
```

**Arch Linux:**
```bash
sudo pacman -S libffi
```

**macOS:**
```bash
brew install libffi
```

**Fedora/RHEL:**
```bash
sudo dnf install libffi-devel
```

### With C Compiler (for API mode)

For API mode usage, you also need a C compiler:

**Debian/Ubuntu:**
```bash
sudo apt install build-essential
```

**macOS:**
```bash
xcode-select --install
```

## Quick Start Examples
### Example 1: Simple C Library Call (ABI Mode)

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("int printf(const char *format, ...);")

lib = ffi.dlopen(None)  # Load standard C library
lib.printf(b"Hello from CFFI!\n")
```

### Example 2: Working with Structs

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    struct timespec {
        long tv_sec;
        long tv_nsec;
    };
    int clock_gettime(int clk_id, struct timespec *tp);
""")

lib = ffi.dlopen(None)

# Allocate struct
tp = ffi.new("struct timespec *")

# Call function
result = lib.clock_gettime(1, tp)  # CLOCK_REALTIME = 1

print(f"Seconds: {tp.tv_sec}, Nanoseconds: {tp.tv_nsec}")
```

### Example 3: String Handling

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("char *getpwuid(int uid);")

lib = ffi.dlopen(None)

# Get password entry for root (uid=0)
pw = lib.getpwuid(0)

# Convert C string to Python bytes
username = ffi.string(pw.pw_name)
print(f"Username: {username.decode('utf-8')}")
```

### Example 4: Arrays and Memory

```python
from cffi import FFI

ffi = FFI()
ffi.cdef("void qsort(void *base, size_t nmemb, size_t sizeof_elem, void *cmp);")

lib = ffi.dlopen(None)

# Create integer array
arr = ffi.new("int[]", [5, 2, 8, 1, 9])

# Comparison function for qsort
@ffi.callback("int(const void *, const void *)")
def compare_int(a, b):
    return a[0] - b[0]

# Sort array
lib.qsort(arr, 5, ffi.sizeof("int"), compare_int)

print([arr[i] for i in range(5)])  # [1, 2, 5, 8, 9]
```

## Advanced Topics
## Advanced Topics

- [Cffi Modes](reference/01-cffi-modes.md)
- [Type Declarations](reference/02-type-declarations.md)
- [Memory Management](reference/03-memory-management.md)
- [Callbacks](reference/04-callbacks.md)
- [Distribution](reference/05-distribution.md)
- [Embedding](reference/06-embedding.md)
- [Thread Safety](reference/07-thread-safety.md)
- [Advanced Topics](reference/08-advanced-topics.md)

## Troubleshooting
### Common Issues

**"No module named '_cffi_backend'"**
- CFFI not installed correctly: `pip install --force-reinstall cffi`
- Virtual environment issues: ensure correct Python interpreter

**"dlopen() failed: library not found"**
- Use full path: `ffi.dlopen("/usr/lib/libfoo.so")`
- On Windows: use `ctypes.util.find_library("foo")`
- Check library exists: `ldconfig | grep libfoo` (Linux) or `otool -L file` (macOS)

**Segmentation fault when calling C function**
- Check function signature matches exactly
- Verify struct field order and types
- Ensure pointers are properly initialized with `ffi.new()`
- Use API mode for better error messages during compilation

**"ffi.new() type not declared"**
- Type must be declared in `cdef()` before use
- For arrays: use `"int[]"` or `"int[10]"` syntax
- For structs: use `"struct name *"` or `"struct name[]"`

### Debugging Tips

```python
# Enable verbose compilation
ffibuilder.compile(verbose=True)

# Check declared types
print(ffi.typeof("int"))
print(ffi.sizeof("struct passwd"))
print(ffi.offsetof("struct passwd", "pw_name"))

# Inspect library symbols
lib = ffi.dlopen("/path/to/lib.so")
print(dir(lib))  # Shows available functions

# Use API mode for compile-time errors instead of runtime crashes
```

## Version-Specific Features (2.0.0)
- **Free-threaded Python 3.14+ support**: Full compatibility with Python's free-threaded build
- **Automatic GIL release**: CFFI releases GIL before calling C functions on GIL-enabled builds
- **Improved thread safety**: Better handling of multithreaded access to C libraries
- **Enhanced error messages**: More informative diagnostics for common mistakes
- **Performance improvements**: Optimized callback handling and memory management

## Best Practices
1. **Prefer API mode** for production code (better performance, portability)
2. **Use out-of-line** for distributable packages (separation of build/runtime)
3. **Declare complete struct layouts** when possible (avoid `...` in production)
4. **Always convert C strings** with `ffi.string()` before Python processing
5. **Manage memory carefully**: CFFI uses ref counting, but C-allocated memory needs explicit freeing
6. **Document thread safety** of wrapped libraries clearly
7. **Use type checking**: `ffi.cast()` for explicit type conversions
8. **Test on target platforms**: ABI mode can behave differently across systems

## Performance Considerations
- API mode is significantly faster than ABI mode (direct calls vs libffi)
- Out-of-line mode has faster import times than in-line
- Callbacks have overhead; minimize Python↔C crossing in hot paths
- Batch operations when possible to reduce function call overhead
- Use `ffi.release()` for large allocations in long-running programs

## Related Skills
- `cython-3-2-4` - Alternative Python-C integration with static typing
- `numpy-2-4-4` - For numerical C integration via NumPy C API
- `cryptography-46` - Uses CFFI internally for crypto operations

