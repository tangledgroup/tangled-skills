# Compilation Methods

### Command Line Tools

**cythonize** (translate + compile):
```bash
# Generate C file and compile to extension module
cythonize -i yourmod.pyx

# Generate annotated HTML for debugging
cythonize -a -i yourmod.pyx

# Parallel compilation
cythonize -j 4 yourmod.pyx

# C++ mode
cythonize --cplus -i yourmod.pyx
```

**cython** (translate only):
```bash
# Generate C file only
cython yourmod.pyx

# With debug symbols
cython --gdb yourmod.pyx

# Show line numbers in generated C
cython --line-directives=none yourmod.pyx
```

### setup.py with setuptools

**Basic setup:**
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("module.pyx")
)
```

Build:
```bash
python setup.py build_ext --inplace
```

**With compiler directives:**
```python
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "module.pyx",
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True
        }
    )
)
```

**With NumPy:**
```python
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

ext = Extension(
    "numpy_module",
    ["numpy_module.pyx"],
    include_dirs=[np.get_include()]
)

setup(ext_modules=cythonize([ext]))
```

**With C++:**
```python
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "cpp_module",
    ["cpp_module.pyx", "external.cpp"],
    language="c++",
    extra_compile_args=["-std=c++17"]
)

setup(ext_modules=cythonize([ext]))
```

### pyproject.toml (Modern Approach)

```toml
[build-system]
requires = ["setuptools>=61", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-cython-package"
version = "0.1.0"

[tool.setuptools.ext-modules]
ext-modules = [
  {name = "mymodule", sources = ["mymodule.pyx"]}
]
```

Build with:
```bash
python -m build
```

See [Compilation Reference](reference/05-compilation.md) for advanced configuration.
