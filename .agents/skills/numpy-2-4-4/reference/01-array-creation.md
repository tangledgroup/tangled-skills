# Array Creation in NumPy 2.4.4

## Overview

NumPy provides numerous methods for creating arrays, categorized into:

1. Conversion from Python sequences (lists, tuples)
2. Intrinsic creation functions (zeros, ones, arange, etc.)
3. Replicating or mutating existing arrays
4. Reading from disk files
5. Creating from raw bytes/buffers
6. Special library functions (random, linear algebra)

## From Python Sequences

### Using np.array()

```python
import numpy as np

# 1D array from list
arr1d = np.array([1, 2, 3, 4, 5])

# 2D array from list of lists
arr2d = np.array([[1, 2, 3], [4, 5, 6]])

# 3D array from nested lists
arr3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

# From tuples (converted to list internally)
from_tuple = np.array((1, 2, 3))

# Specify dtype explicitly
int_arr = np.array([1, 2, 3], dtype=np.int32)
float_arr = np.array([1, 2, 3], dtype=np.float64)
complex_arr = np.array([1, 2, 3], dtype=complex)
```

### Important Parameters

```python
# Copy controls whether data is copied
arr = np.array([1, 2, 3], copy=True)   # Always copy
arr = np.array([1, 2, 3], copy=False)  # Never copy (raise if needed)
arr = np.array([1, 2, 3], copy=None)   # Copy only if necessary (default in NumPy 2.0+)

# Order controls memory layout
c_order = np.array([[1, 2], [3, 4]], order='C')  # Row-major (default)
f_order = np.array([[1, 2], [3, 4]], order='F')  # Column-major (Fortran)

# Subok preserves subclasses
subclass_arr = np.array(some_matrix, subok=True)  # Keep subclass type
```

### Common Pitfalls

```python
# WRONG: Multiple arguments instead of single sequence
arr = np.array(1, 2, 3, 4)  # TypeError!

# RIGHT: Single sequence argument
arr = np.array([1, 2, 3, 4])  # Correct

# Overflow with small dtypes
arr = np.array([127, 128, 129], dtype=np.int8)  # OverflowError in NumPy 2.0+
# Use larger dtype or allow wrapping
arr = np.array([127, 128, 129], dtype=np.int16)
```

## Intrinsic Creation Functions

### Empty Arrays (Uninitialized)

```python
# Fast but contains garbage values
empty_1d = np.empty(5)
empty_2d = np.empty((3, 4))
empty_float = np.empty((2, 3), dtype=np.float32)

# Use when you'll overwrite all values immediately
arr = np.empty(1000)
for i in range(1000):
    arr[i] = compute_value(i)  # Much faster than starting with zeros
```

### Zero-Filled Arrays

```python
# All elements are 0.0 (float by default)
zeros_1d = np.zeros(5)
zeros_2d = np.zeros((3, 4))
zeros_int = np.zeros((2, 3), dtype=np.int64)

# Like existing array
arr = np.array([1, 2, 3, 4])
zeros_like = np.zeros_like(arr)  # Same shape and dtype as arr

# With custom dtype
zeros_float32 = np.zeros(10, dtype=np.float32)
```

### One-Filled Arrays

```python
# All elements are 1.0
ones_1d = np.ones(5)
ones_2d = np.ones((3, 4))
ones_int = np.ones((2, 3), dtype=np.int32)

# Like existing array
arr = np.array([5, 6, 7])
ones_like = np.ones_like(arr)
```

### Full Arrays (Custom Value)

```python
# Fill with any value
full_10 = np.full(5, 10)           # [10, 10, 10, 10, 10]
full_2d = np.full((3, 3), -1)      # 3x3 array of -1s
full_pi = np.full((2, 3), np.pi)   # Fill with π

# Like existing array
arr = np.array([1, 2, 3])
full_like = np.full_like(arr, 99)  # [99, 99, 99]
```

### Numeric Ranges

#### arange() - Like Python range()

```python
# Basic usage
arr = np.arange(10)           # [0, 1, 2, ..., 9]
arr = np.arange(5, 10)        # [5, 6, 7, 8, 9]
arr = np.arange(0, 10, 2)     # [0, 2, 4, 6, 8]

# With float step (use carefully due to floating point errors)
arr = np.arange(0, 1, 0.3)    # [0.  , 0.3 , 0.6 , 0.9 ]

# Specify dtype
int_arr = np.arange(5, dtype=np.int32)
float_arr = np.arange(0, 1, 0.1, dtype=np.float64)

# WARNING: Floating point step can give unexpected number of elements
# Prefer linspace for precise control over element count
```

#### linspace() - Fixed Number of Elements

```python
# 50 points from 0 to 1 (inclusive by default)
arr = np.linspace(0, 1, 50)

# Exclude endpoint
arr = np.linspace(0, 1, 50, endpoint=False)

# Different dtypes
int_arr = np.linspace(0, 10, 5, dtype=int)  # [0, 2, 4, 6, 8]

# Logarithmic spacing
logspace = np.logspace(0, 2, 5)  # 10^0 to 10^2: [1, 10, 100, 1000, 10000]
geomspace = np.geomspace(1, 1000, 4)  # [1, 10, 100, 1000]
```

### Identity and Special Matrices

#### Eye - Identity Matrix

```python
# Square identity matrix
I3 = np.eye(3)
# [[1. 0. 0.]
#  [0. 1. 0.]
#  [0. 0. 1.]]

# Rectangular
I_rect = np.eye(3, 5)  # 3 rows, 5 columns

# Offset diagonal
k1 = np.eye(3, k=1)    # Diagonal above main
k_1 = np.eye(3, k=-1)  # Diagonal below main

# Custom value on diagonal
I_custom = np.eye(3, k=0, dtype=int) * 5
```

#### Diag - Diagonal Matrix/Extraction

```python
# Create diagonal matrix from 1D array
d = np.diag([1, 2, 3])
# [[1 0 0]
#  [0 2 0]
#  [0 0 3]]

# Extract diagonal from 2D array
arr = np.array([[1, 2], [3, 4]])
diag_vals = np.diag(arr)  # [1, 4]

# Offset diagonal
d_up = np.diag([1, 2, 3], k=1)   # Above main diagonal
d_down = np.diag([1, 2, 3], k=-1) # Below main diagonal
```

#### Tri - Lower/Upper Triangular

```python
# Create lower triangular matrix
m = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
lower = np.tril(m)      # Keep lower triangle, zero upper
upper = np.triu(m)      # Keep upper triangle, zero lower

# With offset
lower_k1 = np.tril(m, k=1)   # Include first diagonal above main
```

### Random Arrays

See [Random Number Generation](06-random-generation.md) for comprehensive guide.

```python
import numpy as np

# Modern Generator API (recommended)
rng = np.random.default_rng(42)  # Seed for reproducibility

# Uniform random in [0, 1)
uniform = rng.random((3, 3))

# Normal distribution (Gaussian)
normal = rng.normal(loc=0, scale=1, size=(3, 3))

# Integers in range [low, high)
integers = rng.integers(low=0, high=10, size=(5,))

# Other distributions
exponential = rng.exponential(scale=1.0, size=10)
gamma = rng.gamma(shape=2, scale=1, size=10)
```

## From Existing Arrays

### Array Methods

```python
arr = np.array([1, 2, 3])

# Copy array
copy = arr.copy()

# Cast to different dtype
float_arr = arr.astype(np.float64)

# Change shape (returns view when possible)
reshaped = arr.reshape(3, 1)
flattened = arr.ravel()      # Flatten to 1D
flat = arr.flatten()         # Always returns copy

# Transpose
matrix = np.array([[1, 2], [3, 4]])
transposed = matrix.T        # Or matrix.transpose()
```

### Repeat and Tile

```python
arr = np.array([1, 2, 3])

# Repeat elements
repeated = np.repeat(arr, 2)      # [1, 1, 2, 2, 3, 3]
repeated_var = np.repeat(arr, [1, 2, 3])  # [1, 2, 2, 3, 3, 3]

# Tile array (replicate whole array)
tiled = np.tile(arr, 2)           # [1, 2, 3, 1, 2, 3]
tiled_2d = np.tile(arr, (3, 1))   # 3 rows of [1, 2, 3]
```

### From Function

```python
# Create array by applying function to index grid
def f(x, y):
    return np.sqrt(x**2 + y**2)

x = np.arange(5)
y = np.arange(5)
xx, yy = np.meshgrid(x, y)
result = np.fromfunction(f, (5, 5), dtype=int)
```

## From Files

### Binary Format (.npy, .npz)

```python
import numpy as np

# Save single array
arr = np.arange(100).reshape(10, 10)
np.save('data.npy', arr)

# Load
loaded = np.load('data.npy')

# Save multiple arrays
np.savez('data.npz', a=arr1, b=arr2, c=arr3)

# Load compressed
np.savez_compressed('data.npz', a=arr1, b=arr2)

# Load as dictionary-like object
data = np.load('data.npz')
arr1 = data['a']
arr2 = data['b']

# List contents without loading
with np.load('data.npz', allow_pickle=False) as data:
    print(data.files)  # ['a', 'b', 'c']
```

### Text Files (CSV, TSV)

```python
import numpy as np

# Save to CSV
arr = np.arange(20).reshape(4, 5)
np.savetxt('data.csv', arr, delimiter=',')

# With headers
np.savetxt('data.csv', arr, delimiter=',',
           header='col1,col2,col3,col4,col5',
           comments='')  # No '#' prefix

# Load from CSV
loaded = np.loadtxt('data.csv', delimiter=',')

# With missing values
loaded = np.loadtxt('data.csv', delimiter=',', 
                    dtype=float, 
                    filling_value=np.nan)

# Genfromtxt (more flexible, handles missing data)
loaded = np.genfromtxt('data.csv', delimiter=',', 
                       names=True,  # First row is column names
                       dtype=None)  # Auto-detect types
```

### Memmap - Large Arrays

```python
# Memory-map large file (access without loading into RAM)
filename = 'large_array.dat'
fp = np.memmap(filename, dtype='float32', mode='w+', 
               shape=(1000000, 1000))

# Use like regular array (operations are lazy)
fp[0:100, :] = some_data
del fp  # Flushes to disk

# Read mode
fp_read = np.memmap(filename, dtype='float32', mode='r', 
                    shape=(1000000, 1000))
data = fp_read[0:1000, :]  # Only loads needed portion
```

## Special Creation Methods

### Structured Arrays

```python
# Define dtype with named fields
dtype = np.dtype([('name', 'U10'),  # Unicode string, max 10 chars
                  ('age', 'i4'),     # 32-bit integer
                  ('weight', 'f8')]) # 64-bit float

# Create array
arr = np.array([('Alice', 30, 70.5), 
                ('Bob', 25, 80.2)], dtype=dtype)

# Access fields
names = arr['name']      # ['Alice', 'Bob']
ages = arr['age']        # [30, 25]
```

### Record Arrays

```python
# Structured array with object interface
dtype = np.dtype([('x', float), ('y', float)])
arr = np.array([(1.0, 2.0), (3.0, 4.0)], dtype=dtype)
rec_arr = arr.view(np.recarray)

# Access fields as attributes
x_vals = rec_arr.x
y_vals = rec_arr.y
```

### Void Arrays (Raw Bytes)

```python
# Create array of raw bytes
data = b'\x00\x01\x02\x03'
arr = np.frombuffer(data, dtype=np.uint8)  # [0, 1, 2, 3]

# View as different type
arr_int16 = arr.view(np.int16)  # Interpret bytes as int16
```

## Best Practices

1. **Prefer `np.zeros`/`np.ones` over loops** for initialization
2. **Use `np.empty` only when you'll overwrite all values** (faster but uninitialized)
3. **Specify dtype explicitly** to avoid unexpected type promotion
4. **Use `linspace` instead of `arange` with floats** for precise element count
5. **For large arrays, consider `memmap`** to avoid loading everything into RAM
6. **Use `.npy` format for single arrays** (fast, preserves dtype)
7. **Use `.npz` for multiple arrays** (convenient archive format)
8. **Be careful with `copy` parameter** in NumPy 2.0+ (changed default behavior)

## Common Patterns

```python
# Initialize accumulator
total = np.zeros_like(data)
for chunk in data_chunks:
    total += chunk

# Create mask for filtering
mask = (arr > 0) & (arr < 100)
filtered = arr[mask]

# Build array from loop (pre-allocate)
n = 1000
result = np.empty(n)
for i in range(n):
    result[i] = expensive_computation(i)  # Much faster than np.append

# Create diagonal weighting matrix
weights = np.array([1, 2, 3, 4])
W = np.diag(weights)
```
