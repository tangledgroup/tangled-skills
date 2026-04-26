# Supported Features

## Python Language Support

### Supported Constructs

- Conditionals: `if`..`elif`..`else`
- Loops: `while`, `for`..`in`, `break`, `continue`
- Generators: `yield`
- Assertions: `assert`
- Function calls with positional, named arguments, defaults, and `*args` (tuple only)

### Partially Supported

- Exceptions: `try`..`except`, `raise`, `else`, `finally`
  - `raise SomeException` or `raise SomeException(args)` supported
  - Re-raising exceptions is not supported
  - Only bare `except` or `except Exception:` are supported
  - Exception objects cannot be stored in variables
- Context managers: only `numba.objmode()`
- List comprehension (limited)

### Unsupported

- Async features: `async with`, `async for`, `async def`
- Class definition (except `@jitclass`)
- Set, dict, and generator comprehensions
- `yield from`
- `del` statements
- Explicit `**kwargs`

## Built-in Types

### Numbers

- `int`, `bool` — Full arithmetic support
- `float`, `complex` — Full arithmetic and math operations
- String (`str`) — Limited support in nopython mode (comparison, concatenation with `+`, formatting with `%`)
- `bytes`, `bytearray`, `memoryview` — Basic support

### Collections

- **tuple** — Homogeneous and heterogeneous tuples supported
- **list** — Standard Python lists have limited support; use `numba.typed.List` for full functionality in nopython mode
- **set** — Limited support; use `numba.typed.Set`
- **Typed Dict** (`numba.typed.Dict`) — Full dict-like operations with homogeneous key/value types
- **Heterogeneous Literal String Key Dictionary** — Dict with literal string keys and heterogeneous value types
- **None** — Supported as a value

## Built-in Functions

- `abs()`, `bool()`, `complex()`, `float()`, `int()`, `len()`, `max()`, `min()`, `pow()`, `round()`, `sum()`
- Hashing: `hash()` for supported types

## Standard Library Modules

- **math** — Most functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `floor`, `ceil`, `fabs`, `isnan`, `isinf`, etc.
- **cmath** — Complex math functions
- **operator** — Most operators: `add`, `sub`, `mul`, `truediv`, `floordiv`, `mod`, `pow`, `and_`, `or_`, `xor`, `eq`, `ne`, `lt`, `le`, `gt`, `ge`, etc.
- **functools** — `reduce`
- **random** — Selected functions: `random`, `randint`, `uniform`, `gauss`, `normalvariate`, `shuffle`, etc.
- **heapq** — `heappush`, `heappop`, `heapify`, `nlargest`, `nsmallest`
- **array** — Basic array module support
- **collections** — `namedtuple`
- **enum** — `Enum` classes
- **ctypes** — Calling ctypes-wrapped C functions

## Third-party Modules

- **cffi** — Calling CFFI-defined functions in nopython mode

## Supported NumPy Features

### Scalar Types

All standard NumPy scalar types: `int8`–`int64`, `uint8`–`uint64`, `float16`/`float32`/`float64`, `complex64`/`complex128`, `bool_`.

### Array Operations

- Indexing and slicing (including negative indices)
- Boolean indexing
- Integer array indexing
- Structured array access
- Attributes: `.shape`, `.ndim`, `.size`, `.dtype`, `.itemsize`, `.T`, `.flat`
- Calculations: `.sum()`, `.mean()`, `.var()`, `.std()`, `.min()`, `.max()`, `.argmin()`, `.argmax()`, `.dot()`, `.flatten()`, `.ravel()`, `.reshape()`, `.copy()`, `.astype()`
- Methods: `.sort()`, `.argsort()`, `.compress()`, `.repeat()`, `.searchsorted()`

### NumPy Functions

- **Linear algebra**: `np.dot`, `np.vdot`, `np.inner`, `np.outer`, `np.matmul`, `np.linalg.solve`, `np.linalg.inv`, `np.linalg.det`, `np.linalg.eig`, `np.linalg.norm`, `np.linalg.svd` (requires scipy)
- **Reductions**: `np.sum`, `np.prod`, `np.min`, `np.max`, `np.argmin`, `np.argmax`, `np.mean`, `np.var`, `np.std`, `np.any`, `np.all`
- **Array creation**: `np.zeros`, `np.ones`, `np.empty`, `np.full`, `np.arange`, `np.linspace`, `np.eye`, `np.identity`, `np.diag`, `np.tile`, `np.repeat`
- **Manipulation**: `np.concatenate`, `np.stack`, `np.hstack`, `np.vstack`, `np.reshape`, `np.transpose`, `np.swapaxes`
- **Random**: `np.random.rand`, `np.random.randn`, `np.random.randint`, `np.random.uniform`, `np.random.normal`, `np.random.exponential`, etc.
- **Polynomials**: `np.polyval`, `np.polyder`

### Standard Ufuncs

Math operations (`add`, `subtract`, `multiply`, `divide`, `floor_divide`, `power`, `remainder`, `mod`), trigonometric (`sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`, etc.), bit-twiddling (`bitwise_and`, `bitwise_or`, `bitwise_xor`, `invert`, `left_shift`, `right_shift`), comparison (`less`, `greater`, `equal`, `not_equal`, etc.), floating-point (`isnan`, `isinf`, `signbit`, `copysign`, `floor`, `ceil`, `trunc`), datetime operations.

Limitation: Only broadcasting and reduce features of ufuncs are supported in compiled code.

## Deviations from Python Semantics

- **Bounds checking** — Disabled by default; enable with `boundscheck=True`
- **Exceptions** — `KeyboardInterrupt` and `SystemExit` are masked during compiled execution
- **Integer width** — Uses C-style fixed-width integers (not arbitrary precision)
- **Boolean inversion** — `~True` is `-2` (bitwise NOT), not `False` as in Python
- **Global/closure variables** — Captured at compilation time as constants; changes may not be reflected
- **Zero initialization** — Local variables are not zero-initialized (contain garbage until assigned)
