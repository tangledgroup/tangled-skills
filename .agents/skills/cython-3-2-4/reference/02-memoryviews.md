# Typed Memoryviews

## Overview

Typed memoryviews provide efficient, zero-overhead access to memory buffers (NumPy arrays, C arrays, Cython arrays) without Python object creation. They are the preferred way to work with NumPy data in Cython — faster and more feature-rich than the older buffer syntax (`np.ndarray[np.float64_t, ndim=2]`).

Memoryviews work with any object exposing the PEP 3118 buffer interface and do not usually require the GIL.

## Syntax

```cython
# Cython syntax
cdef int[:] view1d = some_array        # 1D
cdef int[:,:] view2d = some_array      # 2D
cdef double[:,:,:] view3d = some_array # 3D
```

```python
# Pure Python mode
view1d: cython.int[:] = some_array
view2d: cython.int[:,:] = some_array
view3d: cython.double[:,:,:] = some_array
```

## Basic Usage

Memoryviews as function parameters reject incompatible buffers automatically (e.g., wrong dimensionality raises `ValueError`):

```cython
def process_3d(int[:,:,:] view not None):
    cdef int total = 0
    for i in range(view.shape[0]):
        for j in range(view.shape[1]):
            for k in range(view.shape[2]):
                total += view[i, j, k]
    return total
```

The `not None` declaration rejects `None` input. In Pure Python mode, `None` is rejected by default unless the type is declared as `Optional`.

## Indexing and Slicing

Index access translates directly to memory addresses:

```cython
cdef int[:,:] buf = exporting_object
print(buf[1, 2])       # direct C-level access
print(buf[-1, -2])     # negative indices count from end
```

Slicing produces new views (no data copy):

```cython
row_view = buf[5, :]        # 1D view of row 5
col_view = buf[:, 3]        # 1D view of column 3
sub_view = buf[1:10, 2:8]   # 2D sub-view
```

Ellipsis works for unspecified dimensions:

```cython
slice1 = buf[..., 0]    # all but last dim, index 0 on last
```

## Copying and Transposing

```cython
# In-place copy
dest[:] = src

# C-contiguous copy
cdef int[:, :, ::1] c_copy = myview.copy()

# Fortran-contiguous copy
cdef int[::1, :, :] f_copy = myview.copy_fortran()

# Transpose
transposed = buf.T
```

## Newaxis

Introduce new axes with `None` indexing (like NumPy):

```cython
myslice: cython.double[:] = np.linspace(0, 10, num=50)
as_2d_row = myslice[None, :]      # shape (1, 50)
as_2d_col = myslice[:, None]      # shape (50, 1)
```

## Read-Only Views

Declare item type as `const` for read-only buffers:

```cython
cdef const double[:] readonly_view = read_only_array
```

This accepts both read-only and writable buffers. Normal (non-const) views reject read-only buffers at runtime.

## Memory Layout

**Default layout** — strided, direct access (no pointers):

```cython
cdef int[:,:,:] default_layout  # strided in all dimensions
```

**C-contiguous** — `::1` on the last dimension:

```cython
cdef int[:, :, ::1] c_contig    # C-contiguous 3D
```

**Fortran-contiguous** — `::1` on the first dimension:

```cython
cdef int[::1, :, :] f_contig    # Fortran-contiguous 3D
```

Passing a non-matching layout raises `ValueError` at runtime. Use `.copy()` or `.copy_fortran()` to convert layouts.

## Custom Structured Arrays

For NumPy arrays with custom dtypes, declare a matching packed struct:

```cython
cdef packed struct Particle:
    double x
    double y
    double z
    double mass

cdef Particle[:] particles = np_array_with_structured_dtype
```

Pure Python mode does not support packed structs.

## Comparison with Old Buffer Syntax

Memoryviews are preferred because:

- Cleaner syntax
- Do not usually need the GIL
- Significantly faster (even without `nogil`)
- Support more buffer sources (C arrays, Cython arrays)

Old equivalent of a 3D sum:

```cython
# Old buffer syntax (slower, needs GIL)
cdef int old_sum3d(np.ndarray[np.int_t, ndim=3] arr):
    ...
```

New memoryview version (faster, can use `nogil`):

```cython
# Memoryview syntax
cdef int sum3d(int[:,:,:] arr) noexcept nogil:
    ...
```

## Cython Arrays

Cython provides its own array type that works with memoryviews:

```cython
from cython.view cimport array as cvarray
from cython.view cimport ndarray

# Create a Cython array
cdef int[100] c_array
cdef int[:] view = c_array

# Cython view array (heap-allocated)
arr = cvarray(shape=(100,), itemsize=sizeof(int), format="i")
cdef int[:] arr_view = arr.data
```
