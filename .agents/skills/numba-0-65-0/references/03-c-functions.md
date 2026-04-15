# C Callback Functions with Numba

## Overview

The `@cfunc` decorator creates compiled functions callable from foreign C/C++ code. This is essential for:
- Providing callbacks to native libraries
- Interfacing with C APIs that require function pointers
- Creating high-performance callback handlers
- Integrating Python logic with C ecosystems

## Basic Usage

### Simple C Callback

```python
from numba import cfunc

@cfunc("float64(float64, float64)")
def add(x, y):
    """Add two floats - callable from C code."""
    return x + y

# Get the C function address
print(add.address)  # Memory address of compiled C function

# Call via ctypes wrapper (for testing)
print(add.ctypes(4.0, 5.0))  # Prints "9.0"
```

### Signature Requirements

The signature is **mandatory** for `@cfunc`:

```python
from numba import cfunc
from numba import types

# Using string signature
@cfunc("float64(float64, float64)")
def func1(x, y):
    return x + y

# Using types (more flexible)
sig = types.float64(types.float64, types.float64)

@cfunc(sig)
def func2(x, y):
    return x + y
```

## Type Signatures

### Basic Types

| C Type | Numba Type String | Numba Type Object |
|--------|-------------------|-------------------|
| `void` | `"void"` | `types.void` |
| `char` | `"int8"` | `types.int8` |
| `short` | `"int16"` | `types.int16` |
| `int` | `"int32"` | `types.int32` |
| `long` | `"int64"` | `types.int64` |
| `float` | `"float32"` | `types.float32` |
| `double` | `"float64"` | `types.float64` |
| `char*` | `"unicode_type"` | `types.unicode_type` |

### Pointer Types

```python
from numba import cfunc, types

# Function taking a pointer and size
sig = types.void(
    types.CPointer(types.float64),  # double*
    types.intc                       # int (size)
)

@cfunc(sig)
def scale_array(ptr, n):
    """Scale array elements in place."""
    for i in range(n):
        ptr[i] *= 2.0
```

### Function Pointers

```python
from numba import cfunc, types

# Callback type: double (*)(double)
callback_type = types.float64(types.float64)

@cfunc(callback_type)
def my_callback(x):
    return x * 2.0 + 1.0
```

## Working with Arrays

### Using carray for C Pointers

Convert C pointers to NumPy-like arrays:

```python
from numba import cfunc, types, carray
import numpy as np

c_sig = types.void(
    types.CPointer(types.double),  # input array
    types.CPointer(types.double),  # output array
    types.intc,                     # rows
    types.intc                      # columns
)

@cfunc(c_sig)
def matrix_scale(in_ptr, out_ptr, m, n):
    """Scale 2D matrix elements."""
    in_array = carray(in_ptr, (m, n))
    out_array = carray(out_ptr, (m, n))
    
    for i in range(m):
        for j in range(n):
            out_array[i, j] = 2.0 * in_array[i, j]

# Usage with ctypes
import ctypes

m, n = 100, 100
input_data = np.random.rand(m, n).ctypes.data_as(ctypes.POINTER(ctypes.c_double))
output_data = np.zeros((m, n), dtype=np.float64).ctypes.data_as(ctypes.POINTER(ctypes.c_double))

matrix_scale.ctypes(input_data, output_data, m, n)
```

### Fortran-Ordered Arrays

Use `farray` for Fortran-order (column-major) arrays:

```python
from numba import cfunc, types, farray

@cfunc(types.void(types.CPointer(types.double), types.intc))
def process_fortran_array(ptr, n):
    """Process Fortran-ordered array."""
    arr = farray(ptr, (n,))
    for i in range(n):
        arr[i] *= 2.0
```

## C Structure Interoperability

### Using CFFI

Map C structures to Numba types via CFFI:

```python
from cffi import FFI
from numba.core.typing import cffi_utils
from numba import cfunc, carray

# Define C structure
ffi = FFI()
ffi.cdef("""
    typedef struct {
        int i1;
        float f2;
        double d3;
        float af4[7];
    } my_struct;
    
    typedef double (*my_func)(my_struct*, size_t);
""")

# Map C type to Numba type
sig = cffi_utils.map_type(ffi.typeof('my_func'), use_record_dtype=True)

@cfunc(sig)
def process_structs(ptr, n):
    """Process array of C structures."""
    base = carray(ptr, n)  # View as array of structs
    total = 0.0
    
    for i in range(n):
        total += base[i].i1 * base[i].f2 / base[i].d3
        total += base[i].af4.sum()  # Nested arrays work like NumPy arrays
    
    return total
```

### Manual Structure Definition

Define structures using `types.Record.make_c_struct`:

```python
from numba import cfunc, types, carray

# Define C-compatible structure
my_struct = types.Record.make_c_struct([
    ('i1', types.int32),
    ('f2', types.float32),
    ('d3', types.float64),
    ('af4', types.NestedArray(dtype=types.float32, shape=(7,))),
])

# Callback taking pointer to struct array
sig = types.float64(types.CPointer(my_struct), types.intc)

@cfunc(sig)
def process_manual_structs(ptr, n):
    """Process manually defined structures."""
    base = carray(ptr, n)
    total = 0.0
    
    for i in range(n):
        total += base[i].i1 * base[i].f2
    
    return total
```

## Real-World Example: SciPy Integration

Use Numba callbacks with `scipy.integrate.quad`:

```python
from numba import cfunc
import numpy as np
import scipy.integrate as si

# Define integrand as Python function
def python_integrand(t):
    return np.exp(-t) / t**2

# Compile as C callback
@cfunc("float64(float64)")
def numba_integrand(t):
    return np.exp(-t) / t**2

# Integration function
def integrate_func(func):
    """Integrate from 1.0 to infinity."""
    return si.quad(func, 1, np.inf)

# Compare performance
python_result = integrate_func(python_integrand)
numba_result = integrate_func(numba_integrand.ctypes)

print(f"Python: {python_result[0]:.10f}")
print(f"Numba:  {numba_result[0]:.10f}")

# Numba callback is ~18x faster!
```

## Callback with State

Pass state through void pointers:

```python
from numba import cfunc, types, carray
import ctypes

# State structure
state_struct = types.Record.make_c_struct([
    ('offset', types.float64),
    ('scale', types.float64),
])

# Callback with state pointer
sig = types.float64(types.CPointer(types.float64), types.CPointer(state_struct))

@cfunc(sig)
def transform_with_state(x_ptr, state_ptr):
    """Transform value using state."""
    x = x_ptr[0]
    state = state_ptr[0]  # Access struct
    return (x + state.offset) * state.scale

# Usage
state_data = np.zeros(1, dtype=[('offset', 'f8'), ('scale', 'f8')])
state_data['offset'][0] = 10.0
state_data['scale'][0] = 2.0

input_val = np.array([5.0], dtype=np.float64)
result = transform_with_state.ctypes(
    input_val.ctypes.data,
    state_data.ctypes.data
)
```

## Error Handling

### Returning Error Codes

```python
from numba import cfunc, types

@cfunc(types.intc(types.CPointer(types.double), types.intc))
def safe_divide(arr, n):
    """Return error code if division by zero detected."""
    for i in range(n):
        if arr[i] == 0.0:
            return -1  # Error: division by zero
    
    for i in range(n):
        arr[i] = 1.0 / arr[i]
    
    return 0  # Success
```

### Output Parameters

Use pointers for multiple return values:

```python
from numba import cfunc, types

sig = types.intc(  # Return error code
    types.float64,           # Input x
    types.CPointer(types.float64),  # Output result
    types.CPointer(types.intc)      # Output status
)

@cfunc(sig)
def safe_log(x, result_ptr, status_ptr):
    """Compute log with error handling."""
    if x <= 0:
        status_ptr[0] = -1  # Invalid input
        return -1
    
    result_ptr[0] = np.log(x)
    status_ptr[0] = 0  # Success
    return 0
```

## Integration with ctypes

### Passing Callbacks to C Libraries

```python
from numba import cfunc
import ctypes

@cfunc("void(int)")
def print_callback(value):
    """Callback that prints a value."""
    print(f"Received: {value}")

# Create ctypes callback type
CB_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_int)

# Get ctypes wrapper
ctypes_callback = CB_FUNC(print_callback.ctypes)

# Pass to C library function
# library.my_function(ctypes_callback, ...)
```

### Callback Arrays

```python
from numba import cfunc, types
import numpy as np
import ctypes

# Define callback type
cb_type = types.float64(types.float64)

# Create multiple callbacks
@cfunc(cb_type)
def callback1(x):
    return x + 1.0

@cfunc(cb_type)
def callback2(x):
    return x * 2.0

@cfunc(cb_type)
def callback3(x):
    return x ** 2.0

# Store in array
callbacks = np.array([
    callback1.address,
    callback2.address,
    callback3.address,
], dtype=np.uintp)

# Call via index
from ctypes import cast, CFUNCTYPE
FuncPtr = CFUNCTYPE(ctypes.c_double, ctypes.c_double)

for i in range(len(callbacks)):
    func = cast(callbacks[i], FuncPtr)
    print(f"Callback {i}: {func(5.0)}")
```

## Best Practices

### Always Validate Signatures

Ensure C signatures match exactly:

```python
from numba import cfunc, types

# Good: Explicit signature matching C expectation
@cfunc(types.intc(types.CPointer(types.uint8), types.size_t))
def process_buffer(buf, size):
    """Process byte buffer."""
    return 0

# Bad: Wrong pointer type
@cfunc(types.intc(types.CPointer(types.int8), types.size_t))  # int8 vs uint8!
def wrong_signature(buf, size):
    return 0
```

### Document C API Contract

Clearly document the expected C interface:

```python
from numba import cfunc, types

@cfunc(types.void(types.CPointer(types.double), types.intc))
def normalize_array(data, n):
    """
    Normalize array to unit norm.
    
    C signature: void normalize_array(double* data, int n)
    
    Parameters:
        data: Pointer to array of n doubles (modified in place)
        n: Number of elements in array
    
    Behavior:
        Scales data so that sum(data[i]^2) = 1.0
    """
    norm = 0.0
    for i in range(n):
        norm += data[i] ** 2
    norm = np.sqrt(norm)
    
    if norm > 0:
        for i in range(n):
            data[i] /= norm
```

### Test with ctypes First

Always test callbacks via ctypes before C integration:

```python
from numba import cfunc, types
import numpy as np

@cfunc(types.float64(types.float64, types.float64))
def add(x, y):
    return x + y

# Test via ctypes
assert add.ctypes(2.0, 3.0) == 5.0
assert add.ctypes(-1.0, 1.0) == 0.0

# Now safe to use with C libraries
```

## Troubleshooting

### Signature Mismatch

If you get "Signature mismatch" errors:

```python
from numba import cfunc, types

# Problem: Python int vs C int32
@cfunc(types.int64(types.intc))  # intc is usually int32
def bad_func(x):
    return x * 2  # Might overflow if x is large int32

# Solution: Use appropriate type
@cfunc(types.int64(types.int64))
def good_func(x):
    return x * 2
```

### Memory Layout Issues

Ensure arrays match expected layout:

```python
from numba import cfunc, types, carray
import numpy as np

@cfunc(types.void(types.CPointer(types.double), types.intc))
def expect_c_order(ptr, n):
    """Expects C-contiguous data."""
    arr = carray(ptr, (n,))
    for i in range(n):
        arr[i] *= 2.0

# Good: C-contiguous
arr_c = np.ascontiguousarray(np.random.rand(100))
expect_c_order.ctypes(arr_c.ctypes.data, 100)

# Bad: Fortran-contiguous might have issues
arr_f = np.asfortranarray(np.random.rand(100))
# expect_c_order.ctypes(arr_f.ctypes.data, 100)  # Potential issue!
```
