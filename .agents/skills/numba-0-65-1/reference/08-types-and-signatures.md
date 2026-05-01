# Types and Signatures

## Rationale

Numba needs precise types to generate efficient machine code. Python's standard types are not precise enough, so Numba uses its own fine-grained type system. You encounter Numba types mainly during debugging or educational purposes, but must use them explicitly for AOT compilation.

## Signatures

A signature specifies a function's types. Example: `"f8(i4, i4)"` or equivalently `"float64(int32, int32)"` — a function taking two 32-bit integers and returning a double-precision float.

String shorthand aliases follow NumPy conventions (e.g., `f8` for `float64`, `i4` for `int32`).

## Basic Types

### Numbers

- `boolean` / `b1` — represented as a byte
- `uint8`/`byte` (`u1`), `uint16` (`u2`), `uint32` (`u4`), `uint64` (`u8`)
- `int8`/`char` (`i1`), `int16` (`i2`), `int32` (`i4`), `int64` (`i8`)
- `intc`, `uintc` — C int-sized integers
- `intp`, `uintp` — pointer-sized integers
- `ssize_t`, `size_t` — C standard types
- `float32` (`f4`) — single-precision float
- `float64`/`double` (`f8`) — double-precision float
- `complex64` (`c8`) — single-precision complex
- `complex128` (`c16`) — double-precision complex

### Arrays

Subscript an elementary type by dimension count:

```python
>>> numba.float32[:]          # array(float32, 1d, A)
>>> numba.float32[:, :, :]    # array(float32, 3d, A)
```

Specify contiguity with `::1`:

```python
>>> numba.float32[::1]         # array(float32, 1d, C) — C-contiguous
>>> numba.float32[:, :, ::1]   # array(float32, 3d, C)
>>> numba.float32[::1, :, :]   # array(float32, 3d, F) — Fortran-contiguous
```

This syntax works within compiled functions for declaring typed container types:

```python
from numba import njit, types, typed

@njit
def example():
    return typed.List.empty_list(types.float64[:, ::1])
```

### Functions

Numba supports first-class function objects — JIT-compiled functions and `cfunc`-compiled functions can be passed as arguments, called, used as items in sequences, and returned.

Restrictions: non-CPU targets, Python generators, functions with Omitted arguments or Optional return values do not support first-class functions. Disable with `no_cfunc_wrapper=True`.

Example of function composition with first-class functions:

```python
@numba.njit
def composition(funcs, x):
    r = x
    for f in funcs[::-1]:
        r = f(r)
    return r

@numba.cfunc("double(double)")
def a(x):
    return x + 1.0

@numba.njit
def b(x):
    return x * x

composition((a, b), 0.5)  # 1.25
```

### Wrapper Address Protocol (WAP)

Any Python object can become a first-class function for Numba by implementing:

- `__wrapper_address__(self) -> int` — Returns the memory address of the compiled function
- `signature(self) -> numba.typing.Signature` — Returns the function signature

Optionally implement `__call__` for object mode support.

## Advanced Types

### Inference

Numba infers types from usage context. Explicit signatures override inference.

### NumPy Scalars

NumPy scalar types map to corresponding Numba types (e.g., `np.int32` → `int32`).

### Optional Types

`types.OptionalType` wraps another type to allow None values. Used internally; rarely needed explicitly.

### Python Types

`types.none`, `types.unicode_type` (for strings), and `types.python` for Python object mode references.
