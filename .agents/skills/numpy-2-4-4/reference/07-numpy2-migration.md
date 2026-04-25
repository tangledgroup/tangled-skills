# NumPy 2.0 Migration Guide

## Overview

NumPy 2.0 introduces breaking changes to improve consistency, performance, and maintainability. This guide covers migration from NumPy 1.x to 2.4.4.

Key changes:
- **Type promotion** (NEP 50): More consistent scalar/array interactions
- **Namespace cleanup** (NEP 52): ~100 members removed/moved
- **Private namespaces**: `np.core` → `np._core`
- **Default integer**: Now 64-bit on all 64-bit systems
- **Copy keyword behavior**: Changed in `asarray`, `array`, `__array__`

## Type Promotion Changes (NEP 50)

### Scalar Precision Preserved

```python
import numpy as np

# NumPy 1.x: float32 + float → float64
# NumPy 2.x: float32 + float → float32 (scalar precision preserved)

arr = np.array([1.0, 2.0], dtype=np.float32)

# Old behavior (NumPy 1.x)
result = arr + 3.0  # Was: float64 array

# New behavior (NumPy 2.x)  
result = arr + 3.0  # Now: float32 array (precision of arr preserved)

# If you need float64, be explicit
result = arr + np.float64(3.0)  # Explicitly float64
```

### Integer Overflow Behavior

```python
# NumPy 1.x: Often promoted to larger type
# NumPy 2.x: May overflow or error depending on context

arr = np.array([100, 200], dtype=np.int8)

# This may now overflow or raise error
result = arr * 2  # int8 * Python int → depends on promotion state

# Be explicit about dtypes to avoid surprises
result = arr.astype(np.int16) * 2  # Safe: promotes to int16 first
```

### Migration Strategy

```python
# Enable warnings during migration
np._set_promotion_state("weak_and_warn")

# Your code here - will warn about changed behavior
result = np.float32(3) + 3.0

# Review warnings and update code as needed
np._set_promotion_state("jax")  # Reset to default (NumPy 2.x standard)
```

## Namespace Cleanup (NEP 52)

### Removed from Main Namespace

Many members have been removed or moved. Here are common replacements:

```python
# Deprecated/removed → Replacement

# Boolean operations
np.alltrue(x)      → np.all(x)
np.sometrue(x)     → np.any(x)

# Array creation/manipulation  
np.asfarray(x)     → np.asarray(x, dtype=float)
np.row_stack(xs)   → np.vstack(xs)

# Mathematical functions
np.cumproduct(x)   → np.cumprod(x)
np.product(x)      → np.prod(x)
np.trapz(y, x)     → np.trapezoid(y, x)

# Type aliases (use explicit dtypes)
np.float_          → np.float64
np.complex_        → np.complex128
np.int_            → np.int64 (or platform intp)
np.str_            → np.str_ (still available)
np.bool_           → np.bool_ (still available)

# Constants
np.Inf, np.inf     → np.inf (lowercase preferred)
np.PINF            → np.inf
np.NINF            → -np.inf
np.NaN, np.nan     → np.nan (lowercase preferred)
np.Infinity        → np.inf

# Type checking
np.issubsctype(a, b) → np.issubdtype(a, b)
np.issctype(x)      → issubclass(x, np.generic)

# Array operations
np.find_common_type() → np.promote_types() or np.result_type()
```

### Moved Members

Some members moved to submodules:

```python
# np.lib namespace cleanup
np.lib.some_function  → np.some_function (main namespace)

# Still in np.lib (specialized)
np.lib.stride_tricks.sliding_window_view
np.lib.array_utils.byte_bounds
np.lib.scimath  # Complex-safe math functions

# C-API related (now private)
np.core.some_api    → np._core.some_api (private, don't use directly)
```

### Private Namespaces

```python
# NumPy 1.x: np.core was semi-public
from numpy.core import ndarray  # Works in 1.x

# NumPy 2.x: np.core is private alias to np._core
from numpy._core import ndarray  # Correct but not recommended

# Preferred: use public API
import numpy as np
arr = np.array([1, 2, 3])  # Use main namespace
```

## Default Integer Changes

### Windows Default Integer

```python
# NumPy 1.x on Windows: default int was 32-bit (C long)
# NumPy 2.x on all platforms: default int is 64-bit (np.intp)

arr = np.array([1, 2, 3])
print(arr.dtype)  # Was: int32 on Windows, Now: int64 everywhere (on 64-bit systems)

# For C API compatibility, be explicit
arr_long = np.array([1, 2, 3], dtype='long')  # Matches C long
arr_intp = np.array([1, 2, 3], dtype=np.intp)  # Pointer-sized integer
```

### Migration Tips

```python
# If your code depends on specific integer size, be explicit
# Instead of relying on default:
arr = np.arange(100)  # Default int (now int64 on 64-bit systems)

# Use explicit dtype for portability
arr = np.arange(100, dtype=np.int32)  # Always 32-bit
arr = np.arange(100, dtype='long')    # Matches C long on platform
```

## Copy Keyword Changes

### asarray() and array()

```python
# NumPy 1.x: copy=False meant "don't copy if possible"
# NumPy 2.x: copy=False means "raise if copy needed"

arr = np.array([1, 2, 3])

# Old code that might break:
result = np.array(arr, copy=False)  # In 2.x: raises if copy needed

# Migration options:
result = np.asarray(arr)  # Copy only if needed (recommended)
result = np.array(arr, copy=None)  # Explicit "copy if needed"
result = np.array(arr, copy=True)  # Always copy
```

### __array__ Protocol

```python
class CustomArray:
    # NumPy 2.x requires these parameters
    def __array__(self, dtype=None, copy=None):
        if copy is False:
            # Must return view or raise ValueError
            raise ValueError("Cannot avoid copy")
        elif copy is True:
            # Must return copy
            return np.array(self.data, dtype=dtype, copy=True)
        else:  # copy=None
            # Copy only if needed (e.g., for dtype conversion)
            return np.asarray(self.data, dtype=dtype)
```

## C-API Changes

### PyArray_Descr Struct

```c
// NumPy 1.x: Direct struct access
int elsize = descr->elsize;

// NumPy 2.x: Use accessor functions
npy_intp elsize = PyDataType_ELSIZE(descr);

// For compatibility with both versions:
#include "numpy/npy_2_compat.h"

// Or define fallback macros:
#if NPY_API_VERSION < 0x02000000
#define PyDataType_ELSIZE(descr) ((descr)->elsize)
#endif
```

### Complex Types

```c
// NumPy 1.x: Direct field access
npy_cfloat c;
double real = c.real;
double imag = c.imag;

// NumPy 2.x: Use accessor functions (C99 complex)
npy_cfloat c;
double real = npy_creal(&c);
double imag = npy_cimag(&c);

// For setting values:
npy_csetreal(&c, 1.0);
npy_csetimag(&c, 2.0);
```

### Maximum Dimensions

```c
// NumPy 1.x: NPY_MAXDIMS was 32
// NumPy 2.x: Increased to 64

// Old code using NPY_MAXDIMS as "None" for axis:
axis = NPY_MAXDIMS;  // Meant "all axes"

// New code:
axis = NPY_RAVEL_AXIS;  // Use this constant instead
```

## Using Ruff for Automated Migration

Ruff rule `NPY201` can automatically detect and fix many issues:

```bash
# Install ruff
pip install ruff>=0.4.8

# Check for NumPy 2.0 issues
ruff check path/to/code/ --select NPY201

# Auto-fix where possible
ruff check path/to/code/ --select NPY201 --fix

# Add to pyproject.toml for ongoing checks:
[tool.ruff.lint]
select = ["NPY201"]
```

## Testing Migration

### Version-Dependent Code

```python
import numpy as np

# Check NumPy version
if np.lib.NumpyVersion(np.__version__) >= '2.0.0':
    # NumPy 2.x code path
    from numpy.exceptions import AxisError
else:
    # NumPy 1.x code path  
    from numpy import AxisError

# Or use try/except for cleaner code
try:
    from numpy.exceptions import AxisError
except ImportError:
    from numpy import AxisError
```

### Compatibility Layer

```python
import numpy as np

def compatible_asarray(arr, dtype=None):
    """asarray that works with NumPy 1.x and 2.x"""
    if np.lib.NumpyVersion(np.__version__) >= '2.0.0':
        return np.asarray(arr, dtype=dtype)
    else:
        return np.array(arr, dtype=dtype, copy=False)

def compatible_trapz(y, x=None):
    """trapezoidal integration compatible with both versions"""
    if hasattr(np, 'trapezoid'):
        return np.trapezoid(y, x=x)
    else:
        return np.trapz(y, x=x)
```

## Common Migration Issues

### Issue 1: Type Promotion Surprises

```python
# Problem: Code relying on implicit upcasting
arr = np.array([1, 2, 3], dtype=np.float32)
result = arr + 3.0  # Was float64, now float32

# Solution: Be explicit about desired precision
result = (arr.astype(np.float64) + 3.0)  # Force float64
# Or accept float32 if sufficient for your use case
```

### Issue 2: Removed Functions

```python
# Problem: Using deprecated function
result = np.alltrue(arr)  # AttributeError in NumPy 2.x

# Solution: Use replacement
result = np.all(arr)  # Same functionality
```

### Issue 3: Copy Behavior Changes

```python
# Problem: copy=False raises when it shouldn't
arr_subclass = MyCustomArray([1, 2, 3])
result = np.array(arr_subclass, copy=False)  # May raise in 2.x

# Solution: Use asarray for "copy if needed"
result = np.asarray(arr_subclass)
```

### Issue 4: Private API Access

```python
# Problem: Using private API
from numpy.core.umath import some_function  # Broken in 2.x

# Solution: Use public API or _core with understanding it's private
from numpy._core.umath import some_function  # Works but not recommended
# Better: find public equivalent in main namespace
```

## Best Practices for NumPy 2.x

1. **Specify dtypes explicitly** - Don't rely on defaults
2. **Use modern random API** - `default_rng()` instead of legacy functions
3. **Prefer `asarray` over `array(copy=False)`** - Clearer intent
4. **Avoid private namespaces** - Use public API only
5. **Test with promotion warnings** - `np._set_promotion_state("weak_and_warn")`
6. **Use Ruff NPY201 rule** - Catch issues automatically
7. **Update dependencies** - Ensure all packages support NumPy 2.x

## Checking Package Compatibility

```bash
# Check if your packages support NumPy 2.x
pip list | grep -E "(numpy|scipy|pandas|sklearn)"

# Test with NumPy 2.x in isolated environment
python -m venv numpy2_test
source numpy2_test/bin/activate
pip install "numpy>=2.0"
pip install your-package
python -c "import your_package; print('OK')"
```

## Resources

- **NEP 50 (Type Promotion)**: https://numpy.org/neps/nep-0050-new-type-promotion.html
- **NEP 52 (Namespace Cleanup)**: https://numpy.org/neps/nep-0052-public-naming.html
- **NumPy 2.0 Release Notes**: https://numpy.org/devdocs/release/2.0.0-notes.html
- **Ruff NPY201 Rules**: https://docs.astral.sh/ruff/rules/#numpy2-deprecation-npy201
