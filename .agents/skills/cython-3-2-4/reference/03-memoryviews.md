# Typed Memoryviews

## Introduction

Typed memoryviews provide zero-copy access to memory buffers, including NumPy arrays, Python arrays, and C arrays. They're faster than the older NumPy array declaration syntax and more flexible.

**Key benefits:**
- No data copying when accessing buffers
- Works with NumPy arrays, Python arrays, bytes, and custom buffer providers
- Cleaner syntax than `np.ndarray[np.float64_t, ndim=2]`
- Supports Fortran-order (column-major) arrays
- Can be used as function arguments, return values, and class attributes

## Basic Syntax

### 1D Memoryview

```python
def sum_array(double[:] arr):
    """Sum elements of a 1D array"""
    cdef double total = 0.0
    cdef Py_ssize_t i
    
    for i in range(arr.shape[0]):
        total += arr[i]
    
    return total
```

### Multi-dimensional Memoryviews

```python
def matrix_multiply(double[:,:] a, double[:,:] b, double[:,:] result):
    """Multiply two 2D matrices"""
    cdef Py_ssize_t i, j, k
    cdef Py_ssize_t rows_a = a.shape[0]
    cdef Py_ssize_t cols_a = a.shape[1]
    cdef Py_ssize_t cols_b = b.shape[1]
    
    for i in range(rows_a):
        for j in range(cols_b):
            result[i, j] = 0.0
            for k in range(cols_a):
                result[i, j] += a[i, k] * b[k, j]
```

### Memoryview Declaration Forms

```python
# Complete view (can be None by default)
cdef double[:] view1

# View that cannot be None
cdef double[:] view2 not None

# 2D view
cdef int[:,:] matrix

# 3D view
cdef float[:,:,:] tensor

# Fortran-order (column-major)
cdef double[::1] contiguous_view

# Strided view (can handle non-contiguous)
cdef double[::,:] strided_2d
```

## Creating Memoryviews

### From NumPy Arrays

```python
import numpy as np

def process_numpy_array(np.ndarray[double, ndim=2] input_arr):
    # Create memoryview from NumPy array
    cdef double[:,:] view = input_arr
    
    # Use the view (no copy made!)
    for i in range(view.shape[0]):
        for j in range(view.shape[1]):
            view[i, j] *= 2.0
    
    # Changes reflect in original array
```

### From Python Lists

```python
def list_to_memoryview(list data):
    cdef double[:] view = data  # Creates a copy!
    return view
```

**Note:** Converting Python lists to memoryviews copies the data. For zero-copy, use NumPy arrays or other buffer providers.

### From C Arrays

```python
def process_c_array():
    cdef double c_arr[100]
    cdef double[:] view = c_arr
    
    for i in range(100):
        view[i] = i * 2.0
    
    return view[50]  # 100.0
```

### From Bytes Objects

```python
def process_bytes(bytes data):
    cdef unsigned char[:] view = data
    
    for i in range(view.shape[0]):
        print(view[i])  # Print each byte
```

## Memoryview Attributes

```python
def inspect_memoryview(double[:,:] arr):
    cdef Py_ssize_t ndim = arr.ndim        # Number of dimensions (2)
    cdef Py_ssize_t shape0 = arr.shape[0]  # First dimension size
    cdef Py_ssize_t shape1 = arr.shape[1]  # Second dimension size
    
    cdef Py_ssize_t strides0 = arr.strides[0]  # Bytes between rows
    cdef Py_ssize_t strides1 = arr.strides[1]  # Bytes between columns
    
    print(f"Shape: {arr.shape}")
    print(f"Strides: {arr.strides}")
```

## Slicing and Views

### Creating Subviews

```python
def create_subview(double[:,:] matrix):
    # Row slice (creates view, no copy)
    cdef double[:] row_view = matrix[5, :]
    
    # Column slice (creates view, no copy)
    cdef double[:] col_view = matrix[:, 3]
    
    # 2D submatrix (creates view, no copy)
    cdef double[:,:] submatrix = matrix[10:20, 5:15]
    
    return row_view, col_view, submatrix
```

### Strided Slicing

```python
def strided_access(double[:] arr):
    # Every other element
    cdef double[:] every_other = arr[::2]
    
    # Every third element starting from index 1
    cdef double[:] strided = arr[1::3]
```

## Contiguous Memoryviews

Contiguous memoryviews are faster for certain operations:

```python
# C-contiguous (row-major, default for NumPy)
cdef double[::1] c_contiguous

# Fortran-contiguous (column-major)
cdef double[:, ::1] fortran_contiguous_2d

def requires_contiguous(double[::1] arr):
    """Only accepts C-contiguous arrays"""
    # Fast sequential access
    pass
```

**Performance tip:** Use `np.ascontiguousarray()` to ensure NumPy arrays are contiguous:

```python
import numpy as np

arr = np.random.rand(100, 100)
contiguous_arr = np.ascontiguousarray(arr)
result = requires_contiguous(contiguous_arr)
```

## Memoryview vs NumPy Array Declaration

### Old Style (NumPy-specific)

```python
import numpy as np
cimport numpy as np

def old_style(np.ndarray[double, ndim=2, mode='strided'] arr):
    cdef Py_ssize_t i, j
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i, j] *= 2.0
```

### New Style (Memoryviews)

```python
def new_style(double[:,:] arr):
    cdef Py_ssize_t i, j
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            arr[i, j] *= 2.0
```

**Advantages of memoryviews:**
- No need to `cimport numpy`
- Works with non-NumPy buffers
- Cleaner syntax
- Better performance in many cases

## Custom Data Types with Memoryviews

### Using Packed Structs

```python
# Define a struct matching NumPy dtype
cdef packed struct Point3D:
    double x
    double y
    double z

def process_points(Point3D[:] points):
    cdef Py_ssize_t i
    cdef double total_distance = 0.0
    
    for i in range(points.shape[0]):
        total_distance += (points[i].x**2 + 
                          points[i].y**2 + 
                          points[i].z**2) ** 0.5
    
    return total_distance
```

**Usage with NumPy:**
```python
import numpy as np

# Create matching dtype
point_dtype = np.dtype([('x', 'f8'), ('y', 'f8'), ('z', 'f8')])
points = np.zeros(100, dtype=point_dtype)

points['x'] = range(100)
points['y'] = range(100, 200)
points['z'] = range(200, 300)

result = process_points(points)
```

## Returning Memoryviews

```python
def create_identity_matrix(int n):
    # Create and return a new memoryview
    cdef double[:,:] result = [[0.0] * n for _ in range(n)]
    
    cdef Py_ssize_t i
    for i in range(n):
        result[i, i] = 1.0
    
    return result
```

**Note:** The returned memoryview owns the data. When it goes out of scope in Python, the data is freed.

## Memoryviews in Extension Types

```python
cdef class ImageProcessor:
    cdef double[:,:] image_data
    cdef readonly int width
    cdef readonly int height
    
    def __init__(self, double[:,:] initial_data):
        self.image_data = initial_data
        self.height = initial_data.shape[0]
        self.width = initial_data.shape[1]
    
    def apply_grayscale(self):
        """Convert to grayscale (in-place)"""
        cdef Py_ssize_t i, j
        
        # Simple averaging (assuming RGB in separate arrays)
        for i in range(self.height):
            for j in range(self.width):
                # Grayscale formula
                self.image_data[i, j] = 0.299 * self.image_data[i, j] + \
                                        0.587 * self.image_data[i, j] + \
                                        0.114 * self.image_data[i, j]
    
    def get_row(self, int row_index) -> double[:]:
        """Return a view of a single row"""
        return self.image_data[row_index, :]
```

## Performance Considerations

### When Memoryviews Are Fast

1. **Large arrays** - Avoids Python object creation overhead
2. **Tight loops** - Direct memory access without bounds checking
3. **In-place operations** - No temporary arrays created
4. **Contiguous data** - Sequential memory access patterns

### When They're Not

1. **Small arrays** - Overhead may dominate
2. **Highly strided access** - Cache misses
3. **Frequent shape changes** - Memoryview must be recreated

### Optimization Tips

```python
# cython: boundscheck=False, wraparound=False

def optimized_sum(double[::1] arr):
    """Fast sum with optimizations"""
    cdef double total = 0.0
    cdef Py_ssize_t i, n = arr.shape[0]
    
    # Disable bounds checking for speed
    for i in range(n):
        total += arr[i]
    
    return total
```

## Common Patterns

### Element-wise Operations

```python
def elementwise_add(double[:] a, double[:] b, double[:] result):
    cdef Py_ssize_t i, n = a.shape[0]
    
    for i in range(n):
        result[i] = a[i] + b[i]
```

### Reductions

```python
def find_max(double[:] arr):
    cdef Py_ssize_t i, n = arr.shape[0]
    cdef double max_val = arr[0]
    
    for i in range(1, n):
        if arr[i] > max_val:
            max_val = arr[i]
    
    return max_val
```

### Matrix Operations

```python
def matrix_transpose(double[:,:] input, double[:,:] output):
    cdef Py_ssize_t i, j
    cdef Py_ssize_t rows = input.shape[0]
    cdef Py_ssize_t cols = input.shape[1]
    
    for i in range(rows):
        for j in range(cols):
            output[j, i] = input[i, j]
```

### Image Processing

```python
def convolution_3x3(double[:,:] image, double[:,:] kernel, double[:,:] output):
    cdef Py_ssize_t i, j, ki, kj
    cdef Py_ssize_t height = image.shape[0]
    cdef Py_ssize_t width = image.shape[1]
    
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            output[i, j] = 0.0
            for ki in range(-1, 2):
                for kj in range(-1, 2):
                    output[i, j] += image[i + ki, j + kj] * kernel[ki + 1, kj + 1]
```

## Error Handling

### Checking for None

```python
def safe_process(double[:] arr not None):
    """arr cannot be None"""
    # No need to check for None
    pass

def optional_process(double[:] arr):
    """arr can be None"""
    if arr is None:
        raise ValueError("Array cannot be None")
    
    # Process array
    pass
```

### Shape Validation

```python
def validate_shape(double[:,:] arr, int expected_rows, int expected_cols):
    if arr.shape[0] != expected_rows or arr.shape[1] != expected_cols:
        raise ValueError(f"Expected shape ({expected_rows}, {expected_cols}), "
                        f"got {arr.shape}")
```

See [SKILL.md](../SKILL.md) for overview and [NumPy Integration](09-numpy.md) for NumPy-specific patterns.
