# Array API Standard and Interoperability

## Array API Standard

NumPy 2.3.0+ main namespace is compatible with the **2024.12** version of the Python Array API Standard. This standard defines a common interface for array libraries, enabling backend-agnostic code that works with NumPy, CuPy, JAX, PyTorch, and others.

### Entry Point Discovery

NumPy registers an entry point for array API discovery:

```python
from importlib.metadata import entry_points

eps = entry_points(group='array_api', name='numpy')
# EntryPoint(name='numpy', value='numpy', group='array_api')
```

### Inspection Utilities

NumPy implements the `__array_namespace_info__()` function for runtime inspection:

```python
info = np.__array_namespace_info__()

# Get capabilities
info.capabilities()
# {'boolean indexing': True, 'data-dependent output shape': True, ...}

# Get all standard functions
info.all_functions()

# Get standard data types
info.default_device()   # 'cpu'
info.devices()          # ['cpu']
```

## Duck Array Protocols

NumPy supports several protocols for interoperability with other array libraries:

### `__array__` Protocol

Returns a NumPy array view or copy. Most basic protocol:

```python
class MyArray:
    def __array__(self, dtype=None):
        return np.array([1, 2, 3], dtype=dtype)

# NumPy functions automatically call __array__
np.sum(MyArray())  # 6
```

### `__array_function__` Protocol (NEP 18 / NEP 35)

Allows overriding high-level NumPy functions:

```python
class MyArray:
    def __array_function__(self, func, types, args, kwargs):
        if func is np.sum:
            return custom_sum(self)
        return NotImplemented

# NumPy dispatches to __array_function__
np.sum(MyArray())  # calls custom_sum
```

### `__array_ufunc__` Protocol (NEP 13)

Allows overriding ufunc operations:

```python
class MyArray:
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if ufunc is np.add and method == '__call__':
            return custom_add(self, inputs[1])
        return NotImplemented

# Ufuncs dispatch to __array_ufunc__
MyArray() + np.array([1, 2, 3])
```

### `__dlpack__` Protocol

Zero-copy exchange with other libraries:

```python
# Create NumPy array from dlpack-compatible object
arr = np.from_dlpack(cupy_array)

# NumPy arrays implement __dlpack__ for export
cupy_arr = cupy.fromDlpack(numpy_arr.__dlpack__())
```

## Array API Strict Testing

The `array-api-strict` package tests whether code only uses standard-compliant features:

```python
import array_api_strict as xp

# Use xp instead of np for standard-compliant code
x = xp.array([1, 2, 3])
y = xp.matmul(x, x)
```

## Backend-Agnostic Code Pattern

Write code that works with any Array API implementation:

```python
def process_data(xp, data):
    """Process data using the given array library."""
    # Standard-compliant operations
    normalized = (data - xp.mean(data)) / xp.std(data)
    result = xp.matmul(normalized.T, normalized)
    return xp.linalg.eigvalsh(result)

# Works with any backend
import numpy as np
result_np = process_data(np, data_np)

import cupy as cp
result_cp = process_data(cp, data_cp)
```

## NumPy-Specific vs Standard Features

### Array API Standard Functions

These follow the standard and work across backends:
- `xp.matmul`, `xp.linalg.solve`, `xp.linalg.eigvalsh`
- `xp.concat`, `xp.stack`, `xp.reshape`
- `xp.sum`, `xp.mean`, `xp.std`
- `xp.abs`, `xp.exp`, `xp.log`
- `xp.argsort`, `xp.sort`

### NumPy-Specific Features (Not in Standard)

These are NumPy-specific and may not work with other backends:
- Structured arrays
- `np.broadcast_to`, `np.ravel`
- `np.einsum`, `np.kron`
- `np.pad`, `np.clip`
- `np.lib.stride_tricks`
- Masked arrays (`np.ma`)
- Matrix class (`np.matrix`)
- FFT module (`np.fft`)
- Random module (`np.random`)
- File I/O (`np.save`, `np.load`)

## Interoperability with Other Libraries

### Dask — Distributed Computing

Dask provides NumPy-compatible distributed arrays:

```python
import dask.array as da
x = da.from_array(np_array, chunks=(1000, 1000))
result = x.mean()  # lazy computation
result.compute()   # trigger execution
```

### CuPy — GPU Acceleration

CuPy is a drop-in NumPy replacement for NVIDIA GPUs:

```python
import cupy as cp
x_gpu = cp.array([1, 2, 3])
y_gpu = cp.matmul(x_gpu, x_gpu.T)
result_cpu = cp.asnumpy(y_gpu)  # transfer back to CPU
```

### JAX — Automatic Differentiation

JAX provides NumPy-compatible arrays with transformation capabilities:

```python
import jax.numpy as jnp
from jax import grad

def loss(x):
    return jnp.sum(jnp.square(x))

grad_loss = grad(loss)
x = jnp.array([1.0, 2.0, 3.0])
print(grad_loss(x))  # [2., 4., 6.]
```

## Typing Support

NumPy provides type annotations via `numpy.typing`:

```python
from typing import Literal
import numpy as np
from numpy.typing import NDArray, ArrayLike, DTypeLike

def process(data: ArrayLike, dtype: DTypeLike = np.float64) -> NDArray[np.float64]:
    arr = np.asarray(data, dtype=dtype)
    return arr / arr.sum()

# Type aliases for common dtypes
from numpy.typing import _GenericAlias
NDArray[np.int32]   # 32-bit integer array
NDArray[np.bool_]   # boolean array
```

NumPy 2.4 improves runtime signature introspection for type checkers, enabling better IDE autocomplete and static analysis with mypy, pyright, and other tools.
