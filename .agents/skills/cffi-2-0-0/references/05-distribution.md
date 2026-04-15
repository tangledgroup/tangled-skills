# CFFI Distribution - Complete Guide

## Overview

Distributing CFFI-based packages requires understanding the build process, setuptools integration, and platform-specific considerations. This guide covers creating distributable packages with CFFI.

## Setuptools Integration

### Basic Setup.py Configuration

```python
# setup.py
from setuptools import setup

setup(
    name="my-cffi-package",
    version="1.0.0",
    description="Package using CFFI to wrap C libraries",
    author="Your Name",
    author_email="you@example.com",
    packages=["mypackage"],
    
    # Runtime dependency
    install_requires=[
        "cffi>=1.0.0",
    ],
    
    # Build-time dependency (for generating C extension)
    setup_requires=[
        "cffi>=1.0.0",
    ],
    
    # CFFI build scripts - format: "file.py:variable_name"
    cffi_modules=[
        "build_mod1.py:ffibuilder",
        "build_mod2.py:ffibuilder",
    ],
)
```

### Build Script Structure

```python
# build_mod1.py
from cffi import FFI

ffibuilder = FFI()

# Declare C interface
ffibuilder.cdef("""
    int my_function(int x, int y);
    const char *get_version(void);
    
    struct config {
        int max_size;
        char *path;
    };
    struct config *create_config(void);
    void free_config(struct config *cfg);
""")

# Specify source and dependencies
ffibuilder.set_source(
    "_mod1",  # Output module name (must start with underscore)
    
    # C source code (can include headers, define functions)
    """
    #include "mylib.h"
    
    // Can also define helper functions here
    static int helper(int x) {
        return x * 2;
    }
    """,
    
    # Libraries to link against
    libraries=["mylib", "m"],  # -lmylib -lm
    
    # Additional options (same as Extension)
    include_dirs=["/usr/include/mylib"],
    library_dirs=["/usr/lib"],
    extra_compile_args=["-O2"],
    extra_link_args=[],
    runtime_library_dirs=["/usr/lib"],  # RPATH
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

### Package Structure

```
my-cffi-package/
├── setup.py
├── build_mod1.py           # CFFI build script
├── mypackage/
│   ├── __init__.py
│   └── wrapper.py          # Python wrapper code
├── mylib.h                 # C header (optional)
├── README.md
└── tests/
    └── test_wrapper.py
```

### Python Wrapper Code

```python
# mypackage/wrapper.py
from _mod1 import ffi, lib

def add(x, y):
    """Add two integers using C library."""
    return lib.my_function(x, y)

def get_version():
    """Get library version string."""
    c_str = lib.get_version()
    return ffi.string(c_str).decode('utf-8')

class Config:
    """Context manager for config objects."""
    
    def __init__(self):
        self._cfg = lib.create_config()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cfg:
            lib.free_config(self._cfg)
            self._cfg = None
    
    @property
    def max_size(self):
        return self._cfg.max_size
    
    @max_size.setter
    def max_size(self, value):
        self._cfg.max_size = value
    
    @property
    def path(self):
        return ffi.string(self._cfg.path).decode('utf-8')
```

## Platform-Specific Configuration

### Cross-Platform Library Names

```python
# build_script.py
import sys
from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef("int pthread_create(...);")

if sys.platform == "win32":
    # Windows
    ffibuilder.set_source(
        "_threads",
        "",
        libraries=["pthreadVC2"],  # Or find via ctypes.util.find_library()
        define_macros=[("_WIN32", None)]
    )
elif sys.platform == "darwin":
    # macOS
    ffibuilder.set_source(
        "_threads",
        "",
        libraries=["c"]  # pthreads in libc on macOS
    )
else:
    # Linux and others
    ffibuilder.set_source(
        "_threads",
        "",
        libraries=["pthread"]
    )

if __name__ == "__main__":
    ffibuilder.compile()
```

### Platform-Specific Headers

```python
import os
import sys
from cffi import FFI

ffibuilder = FFI()

# Detect platform and adjust declarations
if sys.platform == "win32":
    ffibuilder.cdef("""
        int __stdcall GetVersionExA(void *lpVersionInfo);
        typedef struct {
            DWORD dwOSVersionInfoSize;
            DWORD dwMajorVersion;
            DWORD dwMinorVersion;
        } OSVERSIONINFOA;
    """)
else:
    ffibuilder.cdef("""
        int uname(struct utsname *buf);
        struct utsname {
            char sysname[65];
            char release[65];
            char version[65];
            char machine[65];
        };
    """)

if __name__ == "__main__":
    ffibuilder.compile()
```

## Conditional Compilation

### Feature Detection

```python
# build_script.py
import subprocess
from cffi import FFI

ffibuilder = FFI()

# Test if a header exists
def has_header(header_name):
    test_code = f"#include <{header_name}>"
    result = subprocess.run(
        ["gcc", "-E", "-x", "c", "-", "/dev/null"],
        input=test_code.encode(),
        capture_output=True
    )
    return result.returncode == 0

# Conditionally declare based on availability
if has_header("ssl.h"):
    ffibuilder.cdef("""
        void SSL_library_init(void);
        void OpenSSL_add_all_algorithms(void);
    """)
    libraries = ["ssl", "crypto"]
else:
    # Fallback declarations
    ffibuilder.cdef("int no_ssl_available(void);")
    libraries = []

ffibuilder.set_source("_crypto", "", libraries=libraries)

if __name__ == "__main__":
    ffibuilder.compile()
```

### Version-Specific Declarations

```python
import subprocess
import re
from cffi import FFI

ffibuilder = FFI()

# Get library version
def get_library_version(library, pkg_config_name):
    result = subprocess.run(
        ["pkg-config", "--modversion", pkg_config_name],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return tuple(map(int, result.stdout.strip().split(".")))
    return (0, 0)

lib_version = get_library_version("mylib", "mylib")

if lib_version >= (2, 0):
    ffibuilder.cdef("""
        int new_function_added_in_2_0(int x);
        void deprecated_function(void);
    """)
else:
    ffibuilder.cdef("""
        int old_function(int x);
    """)

if __name__ == "__main__":
    ffibuilder.compile()
```

## Building Wheels

### Local Wheel Build

```bash
# Install build dependencies
pip install build twine

# Build wheel and source distribution
python -m build

# Outputs:
# dist/my_cffi_package-1.0.0-cp38-cp38-linux_x86_64.whl
# dist/my_cffi_package-1.0.0.tar.gz
```

### ManyLinux Wheels for Linux

For maximum compatibility, build manyLinux wheels:

```bash
# Using Docker
docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2014_x86_64 \
    /opt/python/cp38-cp38/bin/pip wheel /io --no-deps --wheel-dir /io/dist

# Or use cibuildwheel in CI/CD
```

### Cross-Platform Build Matrix

Use GitHub Actions or similar:

```yaml
# .github/workflows/build_wheels.yml
name: Build Wheels

on:
  release:
    types: [published]

jobs:
  build_wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build wheels
        uses: pypa/cibuildwheel@v2.12
        env:
          CIBW_BUILD: "cp${{ matrix.python }}-*"
      
      - name: Upload wheels
        uses: actions/upload-artifact@v3
        with:
          name: wheels
          path: wheelhouse/
```

## ABI Mode Distribution

### Pre-Generated Python Module

For ABI mode, you can distribute the generated Python file:

```python
# build_abi_module.py
from cffi import FFI

ffibuilder = FFI()

# Set source to None for ABI mode
ffibuilder.set_source("_mylib_abi", None)

ffibuilder.cdef("""
    int my_function(int x);
    const char *get_string(void);
""")

if __name__ == "__main__":
    # This generates _mylib_abi.py instead of .so
    ffibuilder.compile()
```

Then include `_mylib_abi.py` in your package:

```python
# setup.py
setup(
    name="my-abi-package",
    packages=["mypackage"],
    package_data={
        "mypackage": ["_mylib_abi.py"],
    },
    install_requires=["cffi>=1.0.0"],
    # No cffi_modules needed - module is pre-generated
)
```

**Advantages:**
- No C compiler needed by end users
- Pure Python wheel (easier distribution)
- Works on any platform with the target library

**Disadvantages:**
- Slower than API mode (uses libffi)
- Must know exact struct layouts
- Library must be present on user's system

## Testing Built Packages

### Unit Tests with CFFI

```python
# tests/test_wrapper.py
import pytest
from mypackage.wrapper import add, get_version, Config

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_version():
    version = get_version()
    assert isinstance(version, str)
    assert len(version) > 0

def test_config_context_manager():
    with Config() as cfg:
        cfg.max_size = 1024
        assert cfg.max_size == 1024
    
    # Config should be freed after context

def test_config_path():
    with Config() as cfg:
        path = cfg.path
        assert isinstance(path, str)
```

### Integration Tests

```python
# tests/test_integration.py
from mypackage import ffi, lib

def test_ffi_types():
    # Test that types are correctly declared
    assert ffi.sizeof("int") >= 4
    assert ffi.sizeof("long") >= 4

def test_library_functions():
    # Test actual C library calls
    result = lib.my_function(10, 20)
    assert result == 30

def test_memory_management():
    # Test that memory is properly managed
    ptr = lib.create_object()
    assert ptr != ffi.NULL
    
    lib.free_object(ptr)
    # No memory leak should occur
```

## Debugging Build Issues

### Verbose Build Output

```bash
# Enable verbose compilation
python build_script.py

# Or with setup.py
python setup.py build --verbose

# For even more detail
CFLAGS="-v" python setup.py build
```

### Common Build Errors

**"No C compiler found"**
```bash
# Install build tools
# Ubuntu/Debian:
sudo apt install build-essential

# macOS:
xcode-select --install

# Fedora:
sudo dnf install gcc gcc-c++
```

**"Header not found"**
```bash
# Install development packages
# Ubuntu/Debian:
sudo apt install libmylib-dev

# Specify include directory in set_source()
ffibuilder.set_source(
    "_mod",
    "",
    include_dirs=["/usr/local/include"]
)
```

**"Library not found"**
```bash
# Install library
sudo apt install libmylib0

# Specify library directory
ffibuilder.set_source(
    "_mod",
    "",
    libraries=["mylib"],
    library_dirs=["/usr/local/lib"]
)
```

## Publishing to PyPI

### Twine Upload

```bash
# Build distributions
python -m build

# Upload to PyPI
twine upload dist/*

# Or upload to TestPyPI first
twine upload --repository testpypi dist/*
```

### pyproject.toml Configuration

```toml
[build-system]
requires = ["setuptools>=61.0", "cffi>=1.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-cffi-package"
version = "1.0.0"
description = "CFFI-based C library wrapper"
requires-python = ">=3.8"
dependencies = [
    "cffi>=1.0.0",
]

[tool.setuptools]
packages = ["mypackage"]

[tool.setuptools.cffi]
cffi-modules = [
    "build_mod1.py:ffibuilder",
]
```

## Best Practices

1. **Use API mode for production**: Better performance and portability
2. **Test on target platforms**: Build and test wheels on all supported platforms
3. **Document system dependencies**: List required system libraries in README
4. **Provide pure Python fallbacks**: When possible, offer slower but more portable alternatives
5. **Use manyLinux for Linux**: Maximizes wheel compatibility
6. **Pin CFFI version carefully**: Major versions may have ABI changes
7. **Include test suite**: Verify CFFI bindings work correctly
8. **Provide build instructions**: Document how to build from source

## References

- [CFFI Documentation - Preparing and Distributing](https://cffi.readthedocs.io/en/stable/cdef.html)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [cibuildwheel Documentation](https://cibuildwheel.pypa.io/)
