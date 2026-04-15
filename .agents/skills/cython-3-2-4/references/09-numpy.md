# NumPy Integration

## Basic Setup

### Importing NumPy in Cython

```python
# In .pyx file
import numpy as np
cimport numpy as np

# Or with minimum version requirement
cimport numpy as np
np.import_array()  # Required for older NumPy versions (<1.23)
```

### Compilation with NumPy Headers

```python
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

ext = Extension(
    "numpy_module",
    ["numpy_module.pyx"],
    include_dirs=[np.get_include()]  # Critical: NumPy headers
)

setup(ext_modules=cythonize([ext]))
```

## Array Types

### Declaring NumPy Arrays

**Method 1: Using memoryviews (recommended):**
```python
def process_array(double[:] arr):
    """Works with any buffer, including NumPy"""
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        arr[i] *= 2.0
```

**Method 2: Using numpy.ndarray declaration:**
```python
def process_array_typed(np.ndarray[double, ndim=1] arr):
    """Strictly typed to 1D double array"""
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        arr[i] *= 2.0
```

### Multi-dimensional Arrays

```python
# 2D array with memoryview
def matrix_operation(double[:,:] matrix):
    cdef Py_ssize_t rows = matrix.shape[0]
    cdef Py_ssize_t cols = matrix.shape[1]
    
    for i in range(rows):
        for j in range(cols):
            matrix[i, j] += 1.0

# 2D array with numpy declaration
def matrix_operation_typed(np.ndarray[float, ndim=2, mode='c'] matrix):
    """C-contiguous 2D float array"""
    cdef Py_ssize_t i, j
    
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            matrix[i, j] *= 2.0
```

### Array Flags and Modes

```python
# C-contiguous (row-major)
np.ndarray[double, ndim=2, mode='c'] arr_c

# Fortran-contiguous (column-major)
np.ndarray[double, ndim=2, mode='f'] arr_f

# Strided (any layout)
np.ndarray[double, ndim=2, mode='strided'] arr_any

# With memoryviews - specify contiguity in declaration
def needs_c_contiguous(double[::1, :] arr):  # First dimension contiguous
    pass

def needs_fortran_contiguous(double[:, ::1] arr):  # Last dimension contiguous
    pass
```

## Creating NumPy Arrays

### From Python Lists

```python
import numpy as np
cimport numpy as np

def create_from_list(list data):
    """Create NumPy array from Python list"""
    cdef Py_ssize_t n = len(data)
    cdef np.ndarray[double, ndim=1] arr = np.empty(n, dtype=np.float64)
    
    cdef Py_ssize_t i
    for i in range(n):
        arr[i] = data[i]
    
    return arr
```

### Pre-allocated Arrays

```python
def create_zeros(int rows, int cols):
    """Create zero-initialized 2D array"""
    cdef np.ndarray[double, ndim=2] result = \
        np.zeros((rows, cols), dtype=np.float64)
    
    return result

def create_random(int size):
    """Create array with random values"""
    cdef np.ndarray[double, ndim=1] result = \
        np.random.randn(size).astype(np.float64)
    
    return result
```

### From C Arrays

```python
def from_c_array():
    """Convert C array to NumPy array"""
    cdef double c_data[100]
    cdef Py_ssize_t i
    
    for i in range(100):
        c_data[i] = i * 2.0
    
    # Create NumPy array viewing the C data
    cdef np.ndarray[double, ndim=1] arr = \
        np.PyArray_SimpleNewFromData(
            1,  # ndim
            &c_data.shape[0],  # shape
            np.NPY_FLOAT64,  # dtype
            <char *>c_data  # data pointer
        )
    
    return arr
```

## Array Operations

### Element-wise Operations

```python
def elementwise_add(double[:] a, double[:] b):
    """Add two arrays element-wise"""
    cdef Py_ssize_t n = a.shape[0]
    cdef double[:] result = np.empty(n, dtype=np.float64)
    
    cdef Py_ssize_t i
    for i in range(n):
        result[i] = a[i] + b[i]
    
    return result

def elementwise_multiply(double[:] arr, double scalar):
    """Multiply array by scalar"""
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        arr[i] *= scalar
```

### Matrix Multiplication

```python
def matrix_multiply(double[:,:] a, double[:,:] b):
    """Manual matrix multiplication"""
    cdef Py_ssize_t rows_a = a.shape[0]
    cdef Py_ssize_t cols_a = a.shape[1]
    cdef Py_ssize_t cols_b = b.shape[1]
    
    cdef double[:,:] result = np.zeros((rows_a, cols_b), dtype=np.float64)
    cdef Py_ssize_t i, j, k
    
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i, j] += a[i, k] * b[k, j]
    
    return result

# Or use NumPy's optimized version
def matrix_multiply_np(np.ndarray a, np.ndarray b):
    return np.matmul(a, b)
```

### Reductions

```python
def array_sum(double[:] arr):
    """Sum all elements"""
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    for i in range(arr.shape[0]):
        total += arr[i]
    
    return total

def array_max(double[:] arr):
    """Find maximum element"""
    cdef double max_val = arr[0]
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(1, n):
        if arr[i] > max_val:
            max_val = arr[i]
    
    return max_val

def array_stats(double[:] arr):
    """Compute multiple statistics"""
    cdef double min_val = arr[0], max_val = arr[0], total = 0.0
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        if arr[i] < min_val:
            min_val = arr[i]
        if arr[i] > max_val:
            max_val = arr[i]
        total += arr[i]
    
    return {
        'min': min_val,
        'max': max_val,
        'mean': total / n,
        'sum': total
    }
```

## Advanced Indexing

### Slicing

```python
def slice_array(double[:] arr):
    """Create sub-arrays via slicing"""
    cdef double[:] first_half = arr[:arr.shape[0]//2]
    cdef double[:] last_quarter = arr[arr.shape[0]//4:]
    cdef double[:] every_other = arr[::2]
    
    return first_half, last_quarter, every_other

def slice_2d(double[:,:] matrix):
    """2D slicing"""
    cdef double[:] row = matrix[5, :]  # Row 5
    cdef double[:] col = matrix[:, 3]  # Column 3
    cdef double[:,:] submatrix = matrix[10:20, 5:15]  # Submatrix
    
    return row, col, submatrix
```

### Boolean Masking

```python
def apply_mask(double[:] arr, double threshold):
    """Count elements above threshold"""
    cdef Py_ssize_t count = 0, i, n = arr.shape[0]
    
    for i in range(n):
        if arr[i] > threshold:
            count += 1
    
    return count

def mask_operation(double[:] arr, double[:] mask, double value):
    """Apply value where mask is True"""
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        if mask[i] > 0.5:  # Treat as boolean
            arr[i] = value
```

## Working with Different Dtypes

### Integer Arrays

```python
def process_integers(int[:] arr):
    """Process integer array"""
    cdef Py_ssize_t i, n = arr.shape[0]
    
    for i in range(n):
        arr[i] = arr[i] * 2 + 1
```

### Complex Numbers

```python
from libc.cmath cimport carg, cabs

def complex_operation(complex[:] arr):
    """Process complex array"""
    cdef Py_ssize_t i, n = arr.shape[0]
    cdef double total_magnitude = 0.0
    
    for i in range(n):
        total_magnitude += cabs(arr[i])
    
    return total_magnitude
```

### Structured Arrays

```python
# Define matching struct
cdef packed struct Point3D:
    double x
    double y
    double z

def process_points(Point3D[:] points):
    """Process array of 3D points"""
    cdef Py_ssize_t i, n = points.shape[0]
    cdef double total_distance = 0.0
    
    for i in range(n):
        total_distance += (points[i].x**2 + 
                          points[i].y**2 + 
                          points[i].z**2) ** 0.5
    
    return total_distance

# Usage from Python:
# dtype = np.dtype([('x', 'f8'), ('y', 'f8'), ('z', 'f8')])
# points = np.zeros(100, dtype=dtype)
```

## NumPy UFuncs

### Creating Custom UFuncs

```python
cdef extern from "numpy/arrayobject.h":
    void PyUFunc_GetOuterLoop(...)

def custom_addufunc(np.ndarray[double, ndim=1] in1, 
                   np.ndarray[double, ndim=1] in2,
                   np.ndarray[double, ndim=1] out):
    """Custom ufunc-like operation"""
    cdef Py_ssize_t i, n = in1.shape[0]
    
    for i in range(n):
        out[i] = in1[i] + in2[i] + 1.0  # Custom formula

# Register as ufunc (advanced)
# See NumPy C-API documentation for full details
```

### Using Existing UFuncs

```python
import numpy as np

def use_numpy_ufuncs(np.ndarray arr):
    """Leverage NumPy's optimized ufuncs"""
    squared = np.square(arr)
    sqrt_arr = np.sqrt(arr)
    exp_arr = np.exp(arr)
    log_arr = np.log(arr)
    
    return squared, sqrt_arr, exp_arr, log_arr
```

## Performance Tips

### Memory Layout Matters

```python
# Good - sequential access in C-contiguous array
def row_traversal(double[::1, :] arr):
    cdef Py_ssize_t i, j
    
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i, j] *= 2.0  # Fast: sequential memory

# Bad - strided access
def column_traversal(double[:,:] arr):
    cdef Py_ssize_t i, j
    
    for j in range(arr.shape[1]):
        for i in range(arr.shape[0]):
            arr[i, j] *= 2.0  # Slow: jumping between rows
```

### Avoid Python Overhead in Loops

```python
# Bad - Python objects in loop
def slow_numpy(np.ndarray arr):
    total = 0
    for val in arr.flat:  # Python iteration
        total += val * 2  # Python arithmetic
    return total

# Good - C-level operations
def fast_numpy(double[:] arr):
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    for i in range(arr.shape[0]):
        total += arr[i] * 2.0  # C arithmetic
    return total
```

### Use Broadcasting Carefully

```python
# Manual broadcasting (fast)
def manual_broadcast(double[:] vector, double[:,:] matrix):
    cdef Py_ssize_t i, j, rows = matrix.shape[0]
    
    for i in range(rows):
        for j in range(matrix.shape[1]):
            matrix[i, j] += vector[j]  # Add vector to each row

# NumPy broadcasting (convenient but may copy)
def numpy_broadcast(np.ndarray vector, np.ndarray matrix):
    return matrix + vector  # NumPy handles broadcasting
```

See [SKILL.md](../SKILL.md) for overview and [Memoryviews](03-memoryviews.md) for buffer access patterns.
