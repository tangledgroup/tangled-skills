# Stencil Operations

## Overview

Stencils are a computational pattern where array elements are updated according to a fixed neighborhood pattern. The `@stencil` decorator lets users define the kernel, and Numba generates the looping code to apply it across the input array.

## Basic Usage

```python
from numba import stencil
import numpy as np

@stencil
def average_neighbors(a):
    return 0.25 * (a[0, 1] + a[1, 0] + a[0, -1] + a[-1, 0])

input_arr = np.arange(100).reshape((10, 10))
output_arr = average_neighbors(input_arr)
```

The kernel function uses relative indexing — `a[0, 0]` refers to the current element, `a[-1, 1]` refers to one row up and one column right. The output array has the same shape as the input.

Border elements where the kernel would access out-of-bounds indices are set to zero by default.

## Stencil Parameters

The first argument must be an array (determines output size and shape). Additional arguments can be scalars or arrays (arrays must be at least as large as the first argument in each dimension). All array arguments use relative indexing.

## Kernel Shape Inference

Numba analyzes the kernel to determine its size automatically. For example, indices `-1` to `+1` in both dimensions produce a 3×3 kernel with a border of size 1. Non-symmetric and non-square kernels are handled correctly.

In parallel mode, Numba can infer kernel indices from simple expressions:

```python
@njit(parallel=True)
def stencil_test(A):
    c = 2
    B = stencil(lambda a, c: 0.3 * (a[-c+1] + a[0] + a[c-1]))(A, c)
    return B
```

## Decorator Options

### neighborhood

Specify index ranges explicitly instead of relying on inference:

```python
@stencil(neighborhood=((−29, 0),))
def moving_average(a):
    cumul = 0
    for i in range(-29, 1):
        cumul += a[i]
    return cumul / 30
```

The neighborhood is a tuple of tuples, one per dimension, each containing (min_offset, max_offset). Accessing outside the specified neighborhood produces undefined behavior.

### func_or_mode

Controls border handling. Currently only `"constant"` is supported — kernel is not applied where it would access out-of-bounds indices, and those output elements are set to `cval`.

### cval

The constant value for border elements (default: 0). Must match the kernel's return type.

```python
@stencil(func_or_mode="constant", cval=-1.0)
def kernel(a):
    return a[0] + a[1]
```

### standard_indexing

Some parameters may use standard Python indexing instead of relative indexing:

```python
@stencil(standard_indexing=("b",))
def weighted_kernel(a, b):
    return a[-1] * b[0] + a[0] + b[1]
```

Array `a` uses relative indexing; array `b` uses standard indexing.

## StencilFunc

The decorator returns a `StencilFunc` object. Its `neighborhood` attribute holds the computed or specified neighborhood, useful for verification:

```python
print(average_neighbors.neighborhood)
```

## Invocation Options

### out

Provide a pre-allocated output array:

```python
output_arr = np.full(input_arr.shape, 0.0)
average_neighbors(input_arr, out=output_arr)
```

The output array's element type must be safely castable from the kernel's return type following NumPy ufunc casting rules.

## Stencil with Parallel Execution

Stencils work with `parallel=True` for higher performance:

```python
@njit(parallel=True)
def apply_stencil(A):
    return stencil(lambda a: 0.25 * (a[0, 1] + a[1, 0] + a[0, -1] + a[-1, 0]))(A)
```
