# Ahead-of-Time Compilation

## Overview

Numba's `numba.pycc` module provides Ahead-of-Time (AOT) compilation, producing compiled extension modules that do not depend on Numba at runtime. Note: this module is pending deprecation.

### Benefits

1. Distributed modules work on machines without Numba installed (NumPy is still required)
2. No runtime compilation overhead
3. No import overhead for Numba

### Limitations

1. Only regular functions supported, not ufuncs
2. Function signatures must be specified explicitly
3. Each exported function has only one signature
4. No runtime type checking of arguments
5. Produces generic code for CPU architecture family (not optimized for specific CPU model like JIT)

## Usage

### Standalone Example

```python
from numba.pycc import CC

cc = CC('my_module')
# cc.verbose = True  # print compilation steps

@cc.export('multf', 'f8(f8, f8)')
@cc.export('multi', 'i4(i4, i4)')
def mult(a, b):
    return a * b

@cc.export('square', 'f8(f8)')
def square(a):
    return a ** 2

if __name__ == "__main__":
    cc.compile()
```

Running this script generates an extension module (`my_module.so`, `my_module.pyd`, etc.):

```python
>>> import my_module
>>> my_module.multi(3, 4)
12
>>> my_module.square(1.414)
1.9993959999993999
```

### Distutils Integration

Integrate compilation into `setup.py`:

```python
from distutils.core import setup
from source_module import cc

setup(...,
      ext_modules=[cc.distutils_extension()])
```

Extensions compiled this way are included in build files for distribution as wheels or Conda packages. For conda, use compilers available in the Anaconda distribution.

## Signature Syntax

Same syntax as `@jit` decorator:

```python
@cc.export('centdiff_1d', 'f8[:](f8[:], f8)')
def centdiff_1d(u, dx):
    D = np.empty_like(u)
    D[0] = 0
    D[-1] = 0
    for i in range(1, len(D) - 1):
        D[i] = (u[i+1] - 2 * u[i] + u[i-1]) / dx**2
    return D
```

Omit the return type for inference: `'(f8[:], f8)'` instead of `'f8[:](f8[:], f8)'`.

## Alternative: JIT Cache

For many use cases, `@jit(cache=True)` provides similar benefits without AOT limitations — compiled functions are cached to disk and loaded on subsequent runs, with full JIT optimization including CPU-specific code generation.
