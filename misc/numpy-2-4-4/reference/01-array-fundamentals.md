# Array Fundamentals

## ndarray Creation

### From Python Sequences

```python
import numpy as np

# 1-D from list
a = np.array([1, 2, 3, 4])

# 2-D from nested lists
b = np.array([[1, 2, 3], [4, 5, 6]])

# Specify dtype explicitly
c = np.array([1, 2, 3], dtype=np.float32)

# copy parameter (NumPy 2.x): 'never' (default), 'always', 'if_needed'
d = np.array(b, copy=False)   # may return a view
```

### From Shape and Value

| Function | Description |
|----------|-------------|
| `np.zeros(shape)` | Array filled with zeros |
| `np.ones(shape)` | Array filled with ones |
| `np.empty(shape)` | Uninitialized array (fastest) |
| `np.full(shape, fill_value)` | Array filled with a scalar |
| `np.eye(N[, M, k])` | Identity-like matrix with 1s on diagonal k |
| `np.identity(n)` | Square identity matrix |
| `np.zeros_like(a)` | Zeros matching shape/dtype of a |
| `np.ones_like(a)` | Ones matching shape/dtype of a |
| `np.full_like(a, fill_value)` | Full array matching shape/dtype of a |

```python
# All accept dtype= and order='C'|'F' parameters
z = np.zeros((3, 4), dtype=np.float32, order='F')  # Fortran-contiguous
```

### Numerical Ranges

```python
np.arange(10)           # [0, 1, ..., 9]
np.arange(2, 10, 2)     # [2, 4, 6, 8]
np.linspace(0, 1, 5)    # [0., 0.25, 0.5, 0.75, 1.]
np.logspace(0, 2, 3)    # [1., 10., 100.] (base 10)
np.geomspace(1, 1000, 4) # [1, 10, 100, 1000]
```

### From Functions and Iterators

```python
# From a function applied to indices
f = np.fromfunction(lambda i, j: i + j, (3, 3), dtype=int)

# From an iterator
g = np.fromiter((x**2 for x in range(10)), dtype=int)

# From raw bytes
b = np.frombuffer(b'\x00\x01\x02\x03', dtype=np.uint8)
```

## Array Attributes

Every ndarray has these key attributes:

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

a.ndim       # 2 — number of dimensions
a.shape      # (2, 3) — tuple of axis lengths
a.size       # 6 — total element count
a.dtype      # dtype('int64') — data type object
a.itemsize   # 8 — bytes per element
a.nbytes     # 48 — total memory consumption

# Memory layout
a.flags['C_CONTIGUOUS']  # True if C-order (row-major)
a.flags['F_CONTIGUOUS']  # True if Fortran-order (column-major)

# Strides and data pointer
a.strides    # tuple of bytes to step along each axis
a.data       # memoryview of underlying buffer
```

## Indexing

### Basic Indexing and Slicing

```python
a = np.arange(12).reshape(3, 4)

# Single element
a[1, 2]        # 6

# Row/column slices
a[0]           # first row → array([0, 1, 2, 3])
a[:, 1]        # second column → array([1, 5, 9])
a[1:, :2]      # rows 1+, cols 0-1

# Step slicing
a[::2, ::2]    # every other row and column

# Reversing
a[::-1]        # reverse row order
```

### Fancy Indexing

Fancy indexing uses integer arrays or boolean arrays and always returns a copy (not a view).

```python
a = np.arange(10)

# Integer array indexing
a[[0, 3, 6]]           # [0, 3, 6]
a[np.array([[0, 1], [5, 6]])]  # 2-D result

# Boolean (mask) indexing
mask = a % 2 == 0
a[mask]                 # all even elements

# Combining conditions
(a > 2) & (a < 8)       # boolean array
a[(a > 2) & (a < 8)]    # elements in range (2, 8)
```

### The np.ix_ Helper

Constructs an open mesh from multiple sequences for fancy indexing:

```python
a = np.arange(12).reshape(3, 4)
rows = [0, 2]
cols = [1, 3]
a[np.ix_(rows, cols)]   # elements at intersections
```

## Views vs Copies

Understanding when operations return views (shared memory) vs copies (new memory) is critical for performance and correctness.

### Operations that return views

```python
a = np.arange(10)

b = a[3:7]        # slice → view
c = a.reshape(2, 5)  # reshape → view (when possible)
d = a.T            # transpose → view
e = a + 0          # NO — this is a copy
```

Modifying a view modifies the original:

```python
b[0] = 99
print(a[3])  # 99 — changed through the view
```

### Operations that return copies

```python
a = np.arange(10)

b = a[[0, 2, 4]]       # fancy indexing → copy
c = a[a > 5]           # boolean indexing → copy
d = np.sort(a)         # sort → copy
e = a.copy()           # explicit copy
```

### Checking View Relationships

```python
np.shares_memory(a, b)   # True if a and b share memory
b.base is a              # True if b is a view of a
```

## Reshaping and Transposing

```python
a = np.arange(12)

# Reshape — returns view when strides allow
b = a.reshape(3, 4)
c = a.reshape(-1, 4)    # -1 infers the dimension → (3, 4)

# Flatten operations
d = a.ravel()            # flatten to 1-D, view when possible
e = a.flatten()          # always returns a copy
f = a.reshape(-1)        # equivalent to ravel()

# Transpose
g = b.T                  # swap axes
h = np.transpose(b, (1, 0))  # explicit axis order

# Swap specific axes
i = np.swapaxes(b, 0, 1)
```

## Structured Arrays

Structured arrays store records with named fields of different types:

```python
# Define a structured dtype
dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('weight', 'f8')])

# Create array
people = np.array([
    ('Alice', 30, 55.5),
    ('Bob', 25, 72.0),
    ('Charlie', 35, 68.3)
], dtype=dt)

# Access fields
people['name']      # array(['Alice', 'Bob', 'Charlie'], dtype='<U10')
people['age']       # array([30, 25, 35], dtype=int32)
people[0]['weight'] # 55.5
```

## Copies and Views — Detailed Rules

When slicing returns a view, the resulting array references the same underlying data buffer. This means:

1. Modifications through the view affect the original
2. Memory is not duplicated
3. The view cannot outlive the original (if the original is deleted, the view becomes invalid)

Use `np.ascontiguousarray()` to ensure C-contiguous memory layout, or `np.asfortranarray()` for Fortran-contiguous layout. These return views if the array already has the requested layout.

## Stride Tricks

Advanced memory manipulation via strides (use with caution):

```python
from numpy.lib.stride_tricks import sliding_window_view

a = np.arange(10)
windows = sliding_window_view(a, window_shape=3)
# array([[0,1,2], [1,2,3], [2,3,4], ..., [7,8,9]])
```
