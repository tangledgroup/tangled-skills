# NumPy 2.x Migration Guide

## Overview

NumPy 2.0 (released June 2024) introduced breaking changes to both Python and C APIs. NumPy 2.4 continues this trajectory with additional deprecations and cleanups. This guide covers migration from NumPy 1.x to NumPy 2.x.

## Ruff NPY201 Rule

The Ruff linter provides an automated migration rule for many NumPy 2.0 changes:

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["NPY201"]
```

```bash
ruff check path/to/code/ --select NPY201
```

This catches most namespace and API changes automatically.

## Python API Changes (NEP 52)

### Removed Members

About 100 members were removed from the main `np` namespace. Key removals:

| Removed | Replacement |
|---------|-------------|
| `np.alltrue` | `np.all` |
| `np.anytrue` / `np.sometrue` | `np.any` |
| `np.cumproduct` | `np.cumprod` |
| `np.product` | `np.prod` |
| `np.in1d` | `np.isin` |
| `np.row_stack` | `np.vstack` |
| `np.trapz` | `np.trapezoid` or `scipy.integrate` |
| `np.recfromcsv` | `np.genfromtxt(delimiter=',')` |
| `np.recfromtxt` | `np.genfromtxt` |
| `np.round_` | `np.round` |
| `np.cfloat` | `np.complex128` |
| `np.float_` | `np.float64` |
| `np.complex_` | `np.complex128` |
| `np.longfloat` | `np.longdouble` |
| `np.longcomplex` | `np.clongdouble` |
| `np.string_` | `np.bytes_` |
| `np.unicode_` | `np.str_` |
| `np.Inf` / `np.Infinity` / `np.infty` | `np.inf` |
| `np.NINF` | `-np.inf` |
| `np.PINF` | `np.inf` |
| `np.NaN` | `np.nan` |
| `np.geterrobj` / `np.seterrobj` | `np.errstate` context manager |
| `np.safe_eval` | `ast.literal_eval` |
| `np.find_common_type` | `np.promote_types` or `np.result_type` |
| `np.mat` | `np.asmatrix` |
| `np.nbytes` | `np.dtype(<type>).itemsize` |
| `np.issubclass_` | built-in `issubclass` |
| `np.issubsctype` | `np.issubdtype` |
| `np.sctype2char` | `np.dtype(obj).char` |
| `np.obj2sctype` | `np.dtype(obj).type` |
| `np.set_string_function` | `np.set_printoptions(formatter=...)` |
| `np.disp` | custom printing function |
| `np.who` | IDE variable explorer or `locals()` |
| `np.compat` | no replacement (Python 2 no longer supported) |
| `np.lookfor` | search NumPy documentation directly |
| `np.source` | `inspect.getsource` |
| `np.maximum_sctype` | use specific dtype explicitly |

### Moved Members

These are still available but moved to submodules:

| Old Location | New Location |
|-------------|-------------|
| `np.add_docstring` | `np.lib.add_docstring` |
| `np.add_newdoc` | `np.lib.add_newdoc` |
| `np.char.chararray` | still at `np.char.chararray` |
| `np.DataSource` | `np.lib.npyio.DataSource` |
| `np.tracemalloc_domain` | `np.lib.tracemalloc_domain` |
| `np.format_parser` | `np.rec.format_parser` |
| `np.byte_bounds` | `np.lib.array_utils.byte_bounds` |

### Deprecated Members (Will Be Removed)

| Deprecated | Replacement |
|------------|-------------|
| `np.in1d` | `np.isin` |
| `np.row_stack` | `np.vstack` |
| `np.trapz` | `np.trapezoid` |
| `np.fix` | `np.trunc` (pending deprecation in 2.4) |

## NumPy 2.4 Specific Changes

### Expired Deprecations

- `np.in1d` — removed, use `np.isin`
- `np.trapz` — removed, use `np.trapezoid`
- `np.ndindex.ndincr()` — removed, use `next(ndindex)`
- `interpolation` parameter in `np.quantile`/`np.percentile` — removed, use `method`
- `np.linalg.linalg` and `np.fft.helper` — moved to private modules
- `np.save(fix_imports=...)` — parameter removed
- `np.reshape(newshape=...)` — parameter removed, use `shape=` or positional
- `np.array2string(style=...)` — parameter removed
- `np.sum(generator)` — now raises TypeError, use `np.sum(np.fromiter(gen))`
- `np.ma.mrecords.fromtextfile(delimitor=...)` — removed, use `delimiter`
- Converting array with ndim > 0 to scalar — now raises TypeError

### New Deprecations in 2.4

- Setting `ndarray.strides` attribute — use `np.lib.stride_tricks.as_strided` or `strided_window_view`
- Positional `out` argument to `np.maximum`/`np.minimum` — use keyword form `np.maximum(a, b, out=c)`
- `align=` must be boolean in `np.dtype()` — use keyword `align=True`
- `np.testing.assert_warns` and `np.testing.suppress_warnings` — use `warnings.catch_warnings` or `pytest.warns`
- In-place modification of `ndarray.shape` — use `np.reshape` instead

### Compatibility Notes

- `np.round` now always returns a copy (was view for integer inputs with decimals >= 0)
- C extensions use multi-phase initialization (PEP 489) — deleting numpy from `sys.modules` and re-importing will fail
- `np.arange(start=...)` as keyword argument rejected by type checkers (runtime still works)

## Type Promotion Changes (NEP 50)

### Key Behavioral Changes

```python
# Scalar precision preserved in NumPy 2.x:
np.float32(3) + 3.0
# NumPy 1.x: float64(3.0)
# NumPy 2.x: float32(3.0)

# Higher-precision scalar not ignored:
np.array([3], dtype=np.float32) + np.float64(3)
# NumPy 1.x: float32 array
# NumPy 2.x: float64 array
```

### Migration Strategy

1. Run with `np._set_promotion_state("weak_and_warn")` to detect changes
2. For explicit control, cast with `arr.astype(target_dtype)`
3. Use Python scalars via `int()`, `float()` for predictable promotion
4. Extract scalars from arrays with `.item()` before mixing

## Windows Default Integer Change

On 64-bit Windows, the default integer is now `int64` (was `int32`):

```python
np.array([1, 2, 3]).dtype
# NumPy 1.x on Windows: int32
# NumPy 2.x on Windows: int64

# To maintain old behavior when interfacing with C code:
arr = arr.astype("long", copy=False)
```

## C-API Changes

### PyArray_Descr Struct is Now Opaque

Direct field access to `->elsize` requires accessor functions:

```c
// NumPy 1.x (direct access)
int size = descr->elsize;

// NumPy 2.x (use accessor)
npy_intp size = PyDataType_ELSIZE(descr);
PyDataType_SET_ELSIZE(descr, new_size);

// Other new accessors
PyDataType_ALIGNMENT(descr)
PyDataType_FIELDS(descr)
PyDataType_NAMES(descr)
PyDataType_SUBARRAY(descr)
PyDataType_C_METADATA(descr)
```

For compatibility with both 1.x and 2.x, use `npy_2_compat.h`:

```c
#include "numpy/npy_2_compat.h"

// NPY_DEFAULT_INT evaluates to NPY_LONG on 1.x, NPY_INTP on 2.x
// NPY_RAVEL_AXIS maps to 32 on 1.x, min int on 2.x
```

### Increased Maximum Dimensions

`NPY_MAXDIMS` and `NPY_MAXARGS` increased from 32 to 64. Code using these macros for `axis=None` should use `NPY_RAVEL_AXIS` instead.

### Complex Types Use C99 Native Types

Direct field access (`c.real`, `c.imag`) no longer works. Use:

```c
double real = npy_creal(c);
double imag = npy_cimag(c);
npy_csetreal(&c, value);
npy_csetimag(&c, value);
```

In Cython, use native typedefs (`cfloat_t`, `cdouble_t`) instead of NumPy types.

### import_array() Required for More Functions

Functions previously available from `ndarraytypes.h` now require `ndarrayobject.h` and `import_array()`. Use `PyArray_ImportNumPyAPI()` as a lightweight alternative.

## Migration Checklist

1. Run `ruff check --select NPY201` to auto-detect namespace changes
2. Review type promotion behavior with `np._set_promotion_state("weak_and_warn")`
3. Update C extensions to use accessor functions for `PyArray_Descr`
4. Test on Windows if the default integer change affects your code
5. Replace deprecated functions (`in1d` → `isin`, `trapz` → `trapezoid`)
6. Use `np.random.default_rng()` instead of `np.random.RandomState`
7. For C extensions, vendor `npy_2_compat.h` for dual 1.x/2.x support
8. Check `PyArray_RUNTIME_VERSION >= NPY_2_0_API_VERSION` for runtime version detection
