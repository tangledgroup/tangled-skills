# Compilation and Build Systems

## Overview

Cython compilation involves two stages:
1. **Translation:** `.pyx` → `.c` or `.cpp` (Cython compiler)
2. **Compilation:** `.c`/`.cpp` → `.so`/`.pyd` (C/C++ compiler)

This guide covers all build methods from simple command-line to complex multi-platform setups.

## Command-Line Tools

### cythonize Command

The `cythonize` command handles both translation and compilation:

```bash
# Basic usage - translate only
cythonize module.pyx

# Translate and compile in-place
cythonize -i module.pyx

# Generate annotated HTML for debugging
cythonize -a module.pyx

# Both annotate and compile
cythonize -a -i module.pyx

# Parallel compilation (4 jobs)
cythonize -j 4 module.pyx

# C++ mode
cythonize --cplus -i module.pyx

# Multiple files with glob patterns
cythonize -i src/**/*.pyx
```

**Common options:**
- `-i, --inplace` - Build extension modules in place
- `-a, --annotate` - Produce annotated HTML
- `-j N` - Parallel build with N jobs
- `--cplus` - Compile as C++
- `--embed` - Embed Python interpreter
- `-X directive=value` - Set compiler directive

### cython Command

The `cython` command only translates (no compilation):

```bash
# Basic translation
cython module.pyx  # Produces module.c

# With debug symbols for GDB
cython --gdb module.pyx

# C++ output
cython --cplus module.pyx  # Produces module.cpp

# No line directives (smaller C files)
cython --line-directives=none module.pyx

# Show language level
cython --version
```

## setuptools Integration

### Basic setup.py

```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="my_package",
    version="0.1.0",
    ext_modules=cythonize("module.pyx")
)
```

Build:
```bash
python setup.py build_ext --inplace
```

Install:
```bash
pip install .
```

### Multiple Extensions

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("module1", ["module1.pyx"]),
    Extension("module2", ["module2.pyx"]),
    Extension("module3", ["src/module3.pyx"]),
]

setup(
    name="my_package",
    version="0.1.0",
    ext_modules=cythonize(extensions)
)
```

### Compiler Directives in setup.py

```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'language_level': 3,           # Python 3 semantics
            'boundscheck': False,          # Disable bounds checking
            'wraparound': False,           # Disable negative indexing
            'cdivision': True,             # Use C division
            'embedsignature': True,        # Embed Cython signatures
            'profile': False,              # Disable profiling
            'linetrace': False,            # Disable line tracing
        }
    )
)
```

### Include Paths

```python
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

ext = Extension(
    "numpy_module",
    ["numpy_module.pyx"],
    include_dirs=[
        np.get_include(),  # NumPy headers
        "/usr/include/custom"  # Custom headers
    ]
)

setup(ext_modules=cythonize([ext]))
```

### Library Linking

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "custom_module",
    ["custom_module.pyx"],
    libraries=["m"],           # Link with libm (math library)
    library_dirs=["/usr/local/lib"],
    runtime_library_dirs=["/usr/local/lib"]
)

setup(ext_modules=cythonize([ext]))
```

### C++ Compilation

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "cpp_module",
    ["cpp_module.pyx", "external.cpp"],  # Include C++ source files
    language="c++",
    extra_compile_args=["-std=c++17", "-O3"],
    extra_link_args=["-lpthread"]
)

setup(ext_modules=cythonize([ext]))
```

### OpenMP Support

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "parallel_module",
    ["parallel_module.pyx"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"]
)

setup(ext_modules=cythonize([ext], compiler_directives={'language_level': 3}))
```

**For Windows (MSVC):**
```python
extra_compile_args=["/openmp"],
# No extra_link_args needed for MSVC
```

## pyproject.toml Configuration

### Modern Build System (PEP 517/518)

```toml
[build-system]
requires = ["setuptools>=61", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-cython-package"
version = "0.1.0"
description = "A Cython package"
requires-python = ">=3.8"

[tool.setuptools.ext-modules]
ext-modules = [
  {name = "mymodule", sources = ["mymodule.pyx"]},
  {name = "another", sources = ["src/another.pyx"]}
]
```

Build with:
```bash
python -m build
```

### With NumPy Dependency

```toml
[build-system]
requires = [
    "setuptools>=61",
    "Cython>=3.0",
    "numpy>=1.21"  # Needed at build time for headers
]
build-backend = "setuptools.build_meta"

[project]
name = "numpy-cython-package"
version = "0.1.0"
dependencies = ["numpy>=1.21"]

[tool.cythonize]
modules = ["mymodule.pyx"]
# Additional options can be specified here
```

### Advanced pyproject.toml

```toml
[build-system]
requires = ["setuptools", "wheel", "Cython"]
build-backend = "setuptools.build_meta"

[project]
name = "advanced-cython"
version = "1.0.0"

[tool.setuptools]
packages = ["mypackage"]

[tool.setuptools.ext-modules]
ext-modules = [
    {name = "mypackage.core", sources = ["mypackage/core.pyx"], 
     include-dirs = ["include"], language = "c++"}
]

[tool.cython]
directives = {language_level = 3, boundscheck = false}
```

## Environment Variables

### Build-Time Configuration

```bash
# Disable optimizations for faster development builds
export CFLAGS="-O0 -ggdb"

# Enable all warnings
export CFLAGS="-Wall -Wextra -Werror"

# Set optimization level
export CFLAGS="-O3 -march=native"

# OpenMP thread count
export OMP_NUM_THREADS=4

# OpenMP scheduling
export OMP_SCHEDULE="dynamic,10"
```

### Platform-Specific Variables

**Linux/macOS:**
```bash
export CFLAGS="-O3 -Wall"
export LDFLAGS="-L/usr/local/lib"
export CPPFLAGS="-I/usr/local/include"
```

**Windows (cmd.exe):**
```cmd
set CFLAGS=/O2
set LDFLAGS=/LIBPATH:C:\lib
```

## Debug Builds

### GDB Debug Symbols

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension("debug_module", ["debug_module.pyx"])

setup(
    ext_modules=cythonize(
        [ext], 
        gdb_debug=True  # Generate GDB debug info
    )
)
```

Build and debug:
```bash
python setup.py build_ext --inplace
cygdb ./debug_module.so
```

### Debug Directives

```python
setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'boundscheck': True,       # Enable bounds checking
            'initializedcheck': True,  # Check for uninitialized vars
            'nonecheck': True,         # Check for None values
            'profile': True,           # Enable cProfile
            'linetrace': True          # Enable line-by-line tracing
        }
    )
)
```

## Cross-Compilation

### Manylinux Wheels

For distributing binary wheels:

```python
# Use cibuildwheel or similar tool
# pyproject.toml:
[tool.cibuildwheel]
build = "cp38-* cp39-* cp310-* cp311-*"
skip = "*-win32 pp*"

environment = {CFLAGS="-O3"}
```

### Platform-Specific Flags

```python
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize

extra_compile_args = []
if sys.platform == 'darwin':
    extra_compile_args = ['-stdlib=libc++', '-mmacosx-version-min=10.9']
elif sys.platform == 'win32':
    extra_compile_args = ['/std:c++17']
else:  # Linux
    extra_compile_args = ['-std=c++17', '-fPIC']

ext = Extension(
    "platform_module",
    ["platform_module.pyx"],
    extra_compile_args=extra_compile_args,
    language="c++"
)

setup(ext_modules=cythonize([ext]))
```

## Advanced Topics

### Custom Build Commands

```python
from setuptools import setup, Command
from Cython.Build import cythonize

class DevelopCommand(Command):
    """Custom command for development"""
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        print("Running custom development setup")
        # Custom logic here

setup(
    ext_modules=cythonize("module.pyx"),
    cmdclass={'develop': DevelopCommand}
)
```

### Conditional Compilation

```python
import os
from setuptools import setup, Extension
from Cython.Build import cythonize

# Check for optional dependencies
try:
    import numpy
    use_numpy = True
except ImportError:
    use_numpy = False

ext = Extension(
    "conditional_module",
    ["conditional_module.pyx"],
    define_macros=[('HAVE_NUMPY', 1)] if use_numpy else [],
    include_dirs=[numpy.get_include()] if use_numpy else []
)

setup(ext_modules=cythonize([ext]))
```

### Subpackage Structure

```python
# Package structure:
# mypackage/
#   __init__.py
#   core.pyx
#   utils/
#     __init__.py
#     helpers.pyx

from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="mypackage",
    packages=find_packages(),
    ext_modules=cythonize([
        "mypackage/core.pyx",
        "mypackage/utils/helpers.pyx"
    ])
)
```

### Cleaning Build Artifacts

```python
# setup.py clean command handles:
python setup.py clean --all

# Or manually:
find . -name "*.c" -delete
find . -name "*.so" -delete
find . -name "*.html" -delete  # Annotated HTML
find . -name "__pycache__" -type d -exec rm -rf {} +
rm -rf build/ dist/ *.egg-info
```

## Troubleshooting Compilation

### Common Errors

**Error: "No C compiler found"**
```bash
# Install build tools
sudo apt-get install build-essential  # Debian/Ubuntu
brew install gcc                      # macOS
# Windows: Install Visual Studio Build Tools
```

**Error: "Python.h not found"**
```bash
sudo apt-get install python3-dev  # Debian/Ubuntu
brew install python               # macOS (includes headers)
```

**Error: "numpy/arrayobject.h not found"**
```bash
pip install numpy  # Must be installed before building
```

### Verbose Build Output

```bash
# See exact compilation commands
python setup.py build_ext --inplace -v

# Even more verbose
python setup.py build_ext --inplace -vvv
```

See [SKILL.md](../SKILL.md) for overview and [Troubleshooting Guide](10-troubleshooting.md) for common issues.
