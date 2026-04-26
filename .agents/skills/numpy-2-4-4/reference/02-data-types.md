# Data Types and Type Promotion

## dtype Object

A `numpy.dtype` describes how bytes in memory should be interpreted as array elements. It specifies the data type, size, byte order, and for structured types, field names and layouts.

### Creating dtypes

```python
import numpy as np

# From type objects
dt = np.dtype(np.int32)
dt = np.dtype(np.float64)
dt = np.dtype(np.complex128)

# From string codes
dt = np.dtype('i4')    # int32
dt = np.dtype('f8')    # float64
dt = np.dtype('c16')   # complex128

# With byte order
dt = np.dtype('>i4')   # big-endian int32
dt = np.dtype('<f4')   # little-endian float32
dt = np.dtype('|b1')   # bool (byte order irrelevant)
```

### dtype Attributes

```python
dt = np.dtype('float64')
dt.name       # 'float64'
dt.kind       # 'f' — type category letter
dt.char       # 'd' — single character code
dt.itemsize   # 8 — bytes per element
dt.type       # <class 'numpy.float64'> — corresponding Python type
dt.str        # '<f8' — string representation
dt.num        # 12 — internal type number
```

### Type Kind Characters

| Kind | Category | Examples |
|------|----------|----------|
| `b` | Boolean | `bool_` |
| `i` | Signed integer | `int8`, `int16`, `int32`, `int64` |
| `u` | Unsigned integer | `uint8`, `uint16`, `uint32`, `uint64` |
| `f` | Floating-point | `float16`, `float32`, `float64` |
| `c` | Complex floating | `complex64`, `complex128` |
| `m` | Timedelta | `timedelta64` |
| `M` | Datetime | `datetime64` |
| `O` | Object | Python objects |
| `U` | Unicode string | `str_` |
| `S` | Byte string | `bytes_` |
| `V` | Void (structured) | structured dtypes |

## Scalar Type Hierarchy

NumPy scalars form a class hierarchy rooted at `numpy.generic`:

```
generic
├── number
│   ├── integer
│   │   └── signedinteger: byte, short, intc, int_, longlong
│   │   └── unsignedinteger: ubyte, ushort, uintc, uint, ulonglong
│   ├── floating: half, float_, double, longdouble
│   └── complexfloating: cfloat, cdouble, clongdouble
├── flexible
│   ├── character: bytes_, str_
│   └── void
├── bool_
├── datetime64
└── timedelta64
```

Additional types `intp` and `uintp` are pointer-sized integers used for indexing. Since NumPy 2.0, the default integer is `intp`.

### Built-in Scalar Equivalents

| NumPy scalar | Python type | Inherits? |
|-------------|-------------|-----------|
| `double` (float64) | `float` | yes |
| `cdouble` (complex128) | `complex` | yes |
| `bytes_` | `bytes` | yes |
| `str_` | `str` | yes |
| `int_` (int64 on 64-bit) | `int` | **no** |
| `bool_` | `bool` | **no** |

The default data type in NumPy is `double` (`float64`).

## Structured dtypes

Structured dtypes define records with named fields:

```python
# From a list of (name, dtype) pairs
dt = np.dtype([('x', 'f4'), ('y', 'f4')])

# With sub-arrays
dt = np.dtype([('name', 'U16'), ('grades', 'f8', (2,))])

# Nested structures
dt = np.dtype([('point', [('x', 'f4'), ('y', 'f4')]), ('label', 'U10')])

# Create an array
arr = np.array([((1.0, 2.0), 'A'), ((3.0, 4.0), 'B')], dtype=dt)
arr['point']['x']   # array([1., 3.])
```

## Type Promotion Rules (NEP 50)

NumPy 2.0 changed type promotion rules per NEP 50. The key change: **scalar precision is now preserved consistently**.

### Key Changes

```python
# Before NumPy 2.0:
np.float32(3) + 3.0           # → float64 (Python float wins)
np.array([3], dtype=np.float32) + np.float64(3)  # → float32

# NumPy 2.0+:
np.float32(3) + 3.0           # → float32 (NumPy scalar precision preserved)
np.array([3], dtype=np.float32) + np.float64(3)  # → float64 (higher precision scalar not ignored)
```

### Promotion Categories

NumPy uses a category-based promotion system:

1. **Exact promotion** — same kind, wider type wins (e.g., `int32` + `int64` → `int64`)
2. **Python scalar promotion** — Python `int`, `float`, `complex` promote to the "default" types (`int_`, `float64`, `complex128`)
3. **NumPy scalar promotion** — NumPy scalars preserve their precision in NumPy 2.x
4. **Array + scalar** — array dtype is used as base, scalar may widen

### Casting Modes

Ufuncs and `astype` support casting modes:

- `'no'` — no casting allowed
- `'equiv'` — only byte-order changes
- `'safe'` — only safe casts (no data loss)
- `'same_kind'` — same type kind (e.g., float32 → float64)
- `'unsafe'` — any cast allowed

```python
a = np.array([1.5, 2.7], dtype=np.float64)
b = a.astype(np.int32, casting='truncating')  # explicit truncation

# In ufuncs:
np.add(a, b, casting='safe')  # may reject unsafe casts
```

### Detecting Promotion Changes

During migration to NumPy 2.x, use:

```python
np._set_promotion_state("weak_and_warn")  # warn on changed behavior
# Use with warnings.simplefilter("error") for tracebacks during testing
```

## Type Conversion Functions

```python
# result_type — determine output type of an operation
np.result_type(np.float32(1), np.int64(2))  # dtype('float64')

# promote_types — find smallest dtype that can hold both
np.promote_types(np.int32, np.float32)  # dtype('float32')

# can_cast — check if casting is possible
np.can_cast(np.int32, np.int64, casting='safe')  # True
np.can_cast(np.float64, np.int32, casting='safe')  # False
```

## NumPy 2.0 Default Integer Change

On Windows (and all 64-bit systems), the default integer is now 64-bit (`np.intp`). Previously on Windows it was 32-bit (C `long`). This affects:

- `np.array([1, 2, 3]).dtype` → now `int64` on all 64-bit platforms
- Operations that previously produced 32-bit integers on Windows

If interfacing with compiled code expecting `long`, explicitly cast:

```python
arr = arr.astype("long", copy=False)
```
