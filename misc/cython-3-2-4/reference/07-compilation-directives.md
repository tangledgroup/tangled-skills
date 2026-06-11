# Compilation and Directives

## Build Methods

**Command line:**

```bash
cython example.pyx              # generates example.c
cythonize -i example.pyx        # generates .c and builds extension in-place
cythonize -a example.pyx        # also generates annotated HTML
cythonize -j 4 **/*.pyx         # parallel build with 4 jobs
```

**setuptools (preferred for packages):**

```python
# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("package/*.pyx")
)
```

Build: `python setup.py build_ext --inplace`

**pyproject.toml (PEP 518):**

```toml
[build-system]
requires = ["setuptools", "Cython"]
build-backend = "setuptools.build_meta"
```

**setuptools 74.1.0+ extensions in pyproject.toml:**

```toml
[tool.setuptools]
ext-modules = [
  {name = "example", sources = ["example.pyx"]}
]
```

Build: `python -m build`

## Configuring the C Build

**Extension options:**

```python
extensions = [
    Extension(
        "my_module", ["my_module.pyx"],
        include_dirs=["/usr/local/include"],  # header search paths
        libraries=["m", "mylib"],              # libraries to link
        library_dirs=["/usr/local/lib"],       # library search paths
        language="c++",                        # C or c++
    )
]
```

**Distutils comments in source files:**

```cython
# distutils: libraries = m mylib
# distutils: include_dirs = /opt/include
# distutils: sources = helper.c another_helper.c
# distutils: language = c++
```

These are merged across `cimport`ed `.pxd` files.

**NumPy include path:**

```python
Extension("*", ["*.pyx"], include_dirs=[numpy.get_include()])
```

Only needed when using `cimport numpy`. Memoryviews and `import numpy` do not require it.

**Suppressing NumPy deprecation warnings (Cython 3.0+):**

```python
define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
```

Or in source:

```cython
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
```

## `cythonize()` Arguments

```python
cythonize(
    extensions,
    language_level=3,        # Python 3 syntax (default in Cython 3.x)
    annotate=True,           # generate annotated HTML
    optimize=True,           # enable optimizations
    nthreads=4,              # parallel compilation jobs
    include_path=["/path"],  # search path for .pxd files
    force=True,              # recompile even if not outdated
    quiet=True,              # suppress output
)
```

## Compiler Directives

Directives control Cython's code generation. Set globally, per-file, or per-function.

**Common directives:**

- `boundscheck` — Enable array bounds checking (default: `True`). Set to `False` for performance when indices are known safe.
- `wraparound` — Enable negative index wraparound (default: `True`). Set to `False` when using only non-negative indices.
- `cdivision` — Use C-style division (no ZeroDivisionError, allows `//` on floats). Default: `False`.
- `initializedcheck` — Check that variables are initialized before use. Default: `True`.
- `infer_types` — Infer C types for untyped variables from assignment context. Default: `False`.
- `language_level` — Python version compatibility (`2`, `3`, or `None`). Default: `3` in Cython 3.x.
- `cpp_locals` — Initialize C++ class attributes lazily on first assignment instead of at declaration. Avoids requiring default constructors.

**Setting directives:**

Globally (in `setup.py` or `.pyxcfg`):

```python
from Cython.Compiler import Options
Options.boundscheck = False
Options.wraparound = False
```

Per-file (as comment at top of `.pyx`):

```cython
# cython: boundscheck=False, wraparound=False
```

Per-function (decorator):

```python
@cython.boundscheck(False)
@cython.wraparound(False)
def fast_function():
    ...
```

In `cythonize()`:

```python
cythonize("*.pyx", compiler_directives={
    "boundscheck": False,
    "wraparound": False,
})
```

## Annotated HTML

Generate a color-coded HTML file showing Python vs C boundaries:

```bash
cython -a example.pyx           # generates example.html
```

In `setup.py`:

```python
cythonize("*.pyx", annotate=True)
```

Yellow lines indicate Python interaction (slow). White lines are pure C (fast). The goal is to minimize yellow in hot paths.

## `pyximport`

For development without explicit rebuilds:

```python
import pyximport
pyximport.install()
import my_cython_module  # compiled automatically on first import
```

## Jupyter Notebook

Use the `%%cython` cell magic:

```python
%%cython
# distutils: language = c++
import numpy as np

def fast_sum(double[:] arr):
    cdef double total = 0.0
    cdef int i
    for i in range(arr.shape[0]):
        total += arr[i]
    return total
```

## Distributing Cython Modules

**Recommended (PEP 518):** Ship `.pyx` sources, require Cython at build time:

```toml
[build-system]
requires = ["setuptools", "Cython"]
build-backend = "setuptools.build_meta"
```

**Optional Cython compilation:**

```python
USE_CYTHON = True  # or detect via try/except

ext = '.pyx' if USE_CYTHON else '.c'
extensions = [Extension("example", ["example" + ext])]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)
```

**Sharing `.pxd` files:**

```python
setup(
    package_data={
        'my_package': ['*.pxd'],
        'my_package.sub': ['*.pxd'],
    },
)
```

## Shared Utility Module

For projects with multiple Cython modules, extract common utility code:

```bash
cython --generate-shared=mypkg/shared/_cyutility.c
cython --shared=mypkg.shared._cyutility module.pyx
```

Or via `cythonize()`:

```python
extensions = [
    Extension("*", ["**/*.pyx"]),
    Extension("mypkg.shared._cyutility", sources=["mypkg/shared/_cyutility.c"]),
]

cythonize(extensions, shared_utility_qualified_name='mypkg.shared._cyutility')
```

## Multiple Modules in a Package

```python
# Compile all .pyx files in a package
setup(ext_modules=cythonize("package/*.pyx"))

# Or with glob patterns
extensions = [Extension("*", ["*.pyx"])]
setup(ext_modules=cythonize(extensions))
```

## Custom Extension Creation

Provide a `create_extension` function to customize `Extension` objects after Cython processes them:

```python
from Cython.Build.Dependencies import default_create_extension

def my_create_extension(template, kwds):
    libs = list(kwds.get('libraries', [])) + ["mylib"]
    kwds['libraries'] = libs
    return default_create_extension(template, kwds)

cythonize(..., create_extension=my_create_extension)
```

Note: The function must be pickleable when using `nthreads > 1` (no lambdas).

## Integrating Multiple Modules into One Binary

For embedding Python in another application:

```c
// In C code
#if PY_MAJOR_VERSION < 3
#define MODINIT(name)  init ## name
#else
#define MODINIT(name)  PyInit_ ## name
#endif

PyMODINIT_FUNC MODINIT(my_module)(void);

int main() {
    PyImport_AppendInittab("my_module", MODINIT(my_module));
    Py_Initialize();
    // ... use my_module ...
    Py_Finalize();
}
```

Hide init symbols during compilation with `CYTHON_NO_PYINIT_EXPORT` macro.
