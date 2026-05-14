# C Interoperability

## The @cfunc Decorator

`@cfunc` creates a compiled function callable from foreign C code. Unlike `@jit`, a single explicit signature is mandatory — it determines the visible C callback signature.

### Basic Usage

```python
from numba import cfunc

@cfunc("float64(float64, float64)")
def add(x, y):
    return x + y

# Access the compiled callback via ctypes
print(add.ctypes(4.0, 5.0))  # prints 9.0
```

The C function object exposes:
- `address` — Memory address of the compiled callback (pass to any C/C++ library)
- `ctypes` — A ctypes callback object, also callable from Python for testing

### Example with scipy.integrate.quad

```python
import numpy as np
from numba import cfunc
import scipy.integrate as si

def integrand(t):
    return np.exp(-t) / t**2

nb_integrand = cfunc("float64(float64)")(integrand)

# Pass the ctypes callback to quad
result = si.quad(nb_integrand.ctypes, 1, np.inf)
```

This avoids Python interpreter overhead on each integrand evaluation, achieving significant speedup (18x in the documented example).

## Working with Pointers and Arrays

C callbacks often receive raw pointers. Use `numba.carray` to create array views:

```python
from numba import cfunc, types, carray

c_sig = types.void(types.CPointer(types.double),
                   types.CPointer(types.double),
                   types.intc, types.intc)

@cfunc(c_sig)
def my_callback(in_, out, m, n):
    in_array = carray(in_, (m, n))
    out_array = carray(out, (m, n))
    for i in range(m):
        for j in range(n):
            out_array[i, j] = 2 * in_array[i, j]
```

Use `numba.farray` instead of `carray` if data is laid out in Fortran order.

## Handling C Structures

### With CFFI

Convert CFFI types to Numba Record types:

```python
from cffi import FFI
from numba.core.typing import cffi_utils
from numba import cfunc, carray

src = """
typedef struct my_struct {
   int    i1;
   float  f2;
   double d3;
   float  af4[7];
} my_struct;

typedef double (*my_func)(my_struct*, size_t);
"""

ffi = FFI()
ffi.cdef(src)

sig = cffi_utils.map_type(ffi.typeof('my_func'), use_record_dtype=True)

@cfunc(sig)
def foo(ptr, n):
    base = carray(ptr, n)
    tmp = 0
    for i in range(n):
        tmp += base[i].i1 * base[i].f2 / base[i].d3
        tmp += base[i].af4.sum()
    return tmp
```

Note: `use_record_dtype=True` is required, otherwise pointers to C structures are returned as void pointers.

### With Record.make_c_struct

Create Numba Record types manually:

```python
from numba import types

my_struct = types.Record.make_c_struct([
    ('i1', types.int32),
    ('f2', types.float32),
    ('d3', types.float64),
    ('af4', types.NestedArray(dtype=types.float32, shape=(7,))),
])
```

Due to ABI limitations, pass structures as pointers: `types.CPointer(my_struct)`.

## Signature Specification for C Functions

Limit signatures to scalar types (`int8`, `float64`), pointers to scalars (`types.CPointer(types.int8)`), or pointers to Record types. Complex Numba types do not map cleanly to C ABI.

## ctypes and CFFI Support in JIT Code

Beyond creating callbacks, Numba supports calling C functions from within JIT-compiled code:

- **CFFI** — Calling CFFI functions is supported in nopython mode
- **ctypes** — Calling ctypes-wrapped functions is supported in nopython mode
- **Cython** — Cython-exported functions are callable from Numba
