# What's New in 2.0.0

## v2.0.0

### Free-Threaded CPython Support

CFFI 2.0.0 adds support for free-threaded CPython builds (3.14t and later). This enables CFFI to work with Python's no-GIL mode introduced in PEP 703.

**Important limitations:**
- Free-threaded build does not yet support building extensions with the limited API
- You must set `py_limited_api=False` when building extensions for the free-threaded build
- CPython 3.13t is **not** currently supported due to differences in synchronization primitive behavior from 3.14t that result in segfaults

### Python 3.14 Support

Added compatibility with Python 3.14 standard builds.

### Dropped Python 3.8 Support

Python 3.8 reached end-of-life and is no longer supported. CFFI 2.0.0 requires Python 3.9+.

## Recent Version History

### v1.17.1
- Fixed failing `distutils.msvc9compiler` imports under Windows
- `ffibuilder.emit_python_code()` and `emit_c_code()` accept file-like objects
- `ffiplatform` calls bypassed by emit methods

### v1.17.0
- In API mode, `lib.myfunc` (the special performance-optimized object) can now be passed in many places where CFFI expects a regular `<cdata>`: as a callback to a C function call, inside a struct field of pointer-to-function type, or with `ffi.cast()` / `ffi.typeof()`. Previously you needed `ffi.addressof(lib, "myfunc")` to get a real cdata.

### v1.16.0
- Python 3.12 support (with setuptools as required build dependency due to distutils removal)
- Dropped Python 2.7, 3.6, 3.7
- PEP 517 build support
- Project hosting moved from Heptapod to GitHub

### v1.15.x
- CPython 3.10 support with wheels
- macOS arm64 (Apple Silicon) support
- Initial Windows arm64 support
- Updated libffi to 3.4.2 for Windows/arm64

### v1.14.x
- Linux wheel builds using gcc default ISA for libffi
- `sys.unraisablehook()` support on Python 3.8+
- Minor memory leak fixes
- IRC channel moved to irc.libera.chat

## Migration Notes

### From CFFI 1.x to 2.0

- If targeting Python 3.8, pin to `cffi<2.0`
- For free-threaded Python (3.14t+), set `py_limited_api=False` in build configuration
- No API changes for standard usage patterns

### From ctypes to CFFI

- Replace `CDLL()` / `PyDLL()` with `ffi.dlopen()`
- Replace `c_int()`, `c_char_p()` etc. with `ffi.new()` and `ffi.cast()`
- Struct definitions become cdef declarations (often copy-paste from headers)
- Use API mode (`set_source()`) for better performance and portability

### From CFFI 0.9 to 1.0+

If using the old `ffi.verify()` inline API mode, migrate to out-of-line with `set_source()`:

```python
# Old (deprecated)
lib = ffi.verify("#include <foo.h>")

# New (recommended)
# In build script:
ffibuilder.set_source("_mymod", "#include <foo.h>")
ffibuilder.compile()

# In application:
from _mymod import ffi, lib
```
