---
name: numpy-2-4-4
description: Complete toolkit for NumPy 2.4.4, the fundamental package for scientific computing with Python, providing powerful n-dimensional arrays, comprehensive mathematical functions, linear algebra routines, Fourier transforms, random number generation, and high-performance numerical operations with support for modern Python typing and Array API standard compatibility.
license: MIT
author: Generated from NumPy 2.4.4 Documentation
version: "2.4.4"
tags:
  - numpy
  - arrays
  - scientific-computing
  - linear-algebra
  - numerical-analysis
  - python
category: data-science
external_references:
  - https://numpy.org/
  - https://numpy.org/doc/stable/
  - https://github.com/numpy/numpy/tree/v2.4.4
---

# NumPy 2.4.4

## Overview

NumPy is the fundamental package for scientific computing with Python, providing:

- **Powerful n-dimensional arrays** (`ndarray`) with vectorization, indexing, and broadcasting
- **Comprehensive mathematical functions** including trigonometric, statistical, and linear algebra operations
- **High-performance computation** via optimized C code with minimal Python overhead
- **Random number generation** with modern Generator API (PCG64, Philox, SFC64)
- **Fourier transforms** and polynomial operations
- **File I/O** for reading/writing array data in various formats
- **Array API standard compatibility** for interoperability with other libraries

NumPy 2.4.4 includes significant improvements from the NumPy 2.0 release, including updated type promotion rules (NEP 50), cleaned namespace, improved error messages, and better performance across all operations.

## When to Use

Use this skill when:

- Creating or manipulating multi-dimensional numerical arrays in Python
- Performing vectorized mathematical operations without explicit loops
- Implementing linear algebra algorithms (matrix multiplication, decomposition, eigenvalues)
- Generating random samples from various probability distributions
- Reading/writing numerical data from files (CSV, binary, text)
- Working with scientific/numerical libraries that depend on NumPy (SciPy, pandas, scikit-learn)
- Optimizing numerical code for performance using broadcasting and ufuncs
- Migrating code to NumPy 2.0+ compatibility

## Core Concepts

### The ndarray Object

NumPy's fundamental data structure is the `ndarray` (n-dimensional array):

```python
import numpy as np

# Create arrays
arr = np.array([1, 2, 3, 4, 5])           # 1D array
matrix = np.array([[1, 2], [3, 4]])       # 2D array
tensor = np.zeros((3, 4, 5))              # 3D array

# Key attributes
arr.ndim        # Number of dimensions (axes)
arr.shape       # Tuple of dimensions (e.g., (3, 4))
arr.size        # Total number of elements
arr.dtype       # Data type (e.g., np.float64, np.int32)
arr.itemsize    # Size in bytes of each element
```

### Data Types (dtypes)

NumPy provides explicit data types for memory efficiency:

```python
# Integer types
np.int8, np.int16, np.int32, np.int64     # Signed integers
np.uint8, np.uint16, np.uint32, np.uint64 # Unsigned integers

# Floating point types
np.float32, np.float64, np.longdouble     # Floats

# Complex numbers
np.complex64, np.complex128               # Complex (real + imaginary)

# Boolean and string
np.bool_, np.str_, np.bytes_

# Specify dtype on creation
arr = np.array([1, 2, 3], dtype=np.float32)
```

### Broadcasting

Broadcasting allows operations on arrays of different shapes:

```python
# Add scalar to array (scalar broadcasts to all elements)
arr = np.array([1, 2, 3])
result = arr + 10  # [11, 12, 13]

# Add 1D array to 2D array (broadcasts across rows)
matrix = np.array([[1, 2, 3], [4, 5, 6]])
offset = np.array([10, 20, 30])
result = matrix + offset  # [[11, 22, 33], [14, 25, 36]]

# Broadcasting rules:
# 1. Align shapes from the right
# 2. Dimensions match if equal or one is 1
# 3. Missing dimensions treated as size 1
```

### Vectorization

Replace Python loops with vectorized operations for performance:

```python
# Slow: Python loop
result = [x**2 for x in arr]

# Fast: Vectorized operation
result = arr ** 2

# Vectorized ufuncs (universal functions)
np.sin(arr), np.exp(arr), np.log(arr)
np.add(arr1, arr2), np.multiply(arr1, arr2)
```

## Installation

```bash
# Using pip
pip install numpy==2.4.4

# Using uv (recommended for speed)
uv add numpy==2.4.4

# Using conda
conda install numpy=2.4.4

# Verify installation
python -c "import numpy; print(numpy.__version__)"
```

## Usage Examples

### Array Creation

See [Array Creation](references/01-array-creation.md) for comprehensive examples.

```python
import numpy as np

# From Python sequences
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# Pre-filled arrays
zeros = np.zeros((3, 4))           # All zeros
ones = np.ones((2, 3))             # All ones
empty = np.empty((2, 2))           # Uninitialized (fast)

# Sequences
range_arr = np.arange(0, 10, 2)    # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)    # [0.  , 0.25, 0.5 , 0.75, 1.  ]

# Identity and diagonal
identity = np.eye(3)               # 3x3 identity matrix
diag = np.diag([1, 2, 3])          # Diagonal matrix

# Random arrays (modern API)
rng = np.random.default_rng(42)    # Create generator with seed
random_arr = rng.random((3, 3))    # Uniform [0, 1)
normal_arr = rng.normal(0, 1, (3, 3))  # Gaussian distribution
integers = rng.integers(0, 10, (5,))   # Integers in [0, 10)
```

### Indexing and Slicing

See [Indexing and Slicing](references/02-indexing-slicing.md) for advanced techniques.

```python
arr = np.arange(20).reshape(4, 5)

# Basic indexing
arr[0]           # First row
arr[0, 1]        # Element at row 0, column 1

# Slicing
arr[0:2, 1:4]    # Rows 0-1, columns 1-3
arr[:, ::2]      # All rows, every other column

# Boolean indexing
mask = arr > 10
filtered = arr[mask]

# Fancy indexing (integer arrays)
indices = [0, 2, 3]
selected = arr[indices]
```

### Array Manipulation

See [Array Manipulation](references/03-array-manipulation.md) for reshaping and combining.

```python
arr = np.arange(12)

# Reshaping
reshaped = arr.reshape(3, 4)       # 3x4 array
flattened = arr.ravel()            # Flatten to 1D
transposed = matrix.T              # Transpose

# Changing dimensions
expanded = np.expand_dims(arr, axis=0)  # Add new axis
squeezed = np.squeeze(expanded)         # Remove size-1 dimensions

# Combining arrays
hstack = np.hstack([arr1, arr2])   # Horizontal stack
vstack = np.vstack([arr1, arr2])   # Vertical stack
concat = np.concatenate([arr1, arr2], axis=0)

# Splitting arrays
split = np.split(arr, 3)           # Split into 3 parts
hsplit = np.hsplit(matrix, 2)      # Horizontal split
```

### Mathematical Operations

See [Mathematical Functions](references/04-mathematical-functions.md) for complete reference.

```python
arr = np.array([1, 2, 3, 4, 5])

# Arithmetic
np.add(arr, 10), np.subtract(arr, 5)
np.multiply(arr, 2), np.divide(arr, 2)
np.power(arr, 2), np.mod(arr, 2)

# Trigonometric
angles = np.deg2rad([0, 30, 45, 60, 90])
np.sin(angles), np.cos(angles), np.tan(angles)

# Exponential and logarithmic
np.exp(arr), np.log(arr), np.log10(arr), np.sqrt(arr)

# Statistical operations
np.mean(arr), np.std(arr), np.var(arr)
np.min(arr), np.max(arr), np.argmin(arr), np.argmax(arr)
np.sum(arr), np.cumsum(arr), np.prod(arr)

# Rounding
np.floor(3.7), np.ceil(3.2), np.round(3.5)
```

### Linear Algebra

See [Linear Algebra](references/05-linear-algebra.md) for advanced operations.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication
C = A @ B              # Using @ operator
D = np.dot(A, B)       # Using dot function
E = np.matmul(A, B)    # Using matmul function

# Decompositions
U, S, Vh = np.linalg.svd(A)        # Singular value decomposition
L, U = np.linalg.lu(A)             # LU decomposition (via scipy)
eigenvalues, eigenvectors = np.linalg.eig(A)  # Eigenvalues/vectors

# Solving linear systems
b = np.array([1, 2])
x = np.linalg.solve(A, b)          # Solve Ax = b

# Matrix properties
det = np.linalg.det(A)             # Determinant
trace = np.linalg.trace(A)         # Trace
rank = np.linalg.matrix_rank(A)    # Rank
inv = np.linalg.inv(A)             # Inverse (use solve instead when possible)
norm = np.linalg.norm(A)           # Matrix norm
```

### File I/O

```python
import numpy as np

# Save and load arrays
arr = np.arange(100).reshape(10, 10)
np.save('data.npy', arr)           # Binary format (fast)
loaded = np.load('data.npy')

# Multiple arrays
np.savez('data.npz', a=arr1, b=arr2)
data = np.load('data.npz')
arr1 = data['a'], arr2 = data['b']

# Text files (CSV)
np.savetxt('data.csv', arr, delimiter=',')
loaded = np.loadtxt('data.csv', delimiter=',')

# With headers
np.savetxt('data.csv', arr, delimiter=',', 
           header='col1,col2,col3', comments='')
```

### Random Number Generation

See [Random Number Generation](references/06-random-generation.md) for comprehensive guide.

```python
import numpy as np

# Modern Generator API (recommended)
rng = np.random.default_rng(42)  # Seed for reproducibility

# Basic distributions
uniform = rng.random((3, 3))              # Uniform [0, 1)
normal = rng.normal(loc=0, scale=1, size=(3, 3))  # Gaussian
integers = rng.integers(low=0, high=10, size=(5,))  # Discrete uniform

# More distributions
exponential = rng.exponential(scale=1.0, size=10)
gamma = rng.gamma(shape=2.0, scale=1.0, size=10)
beta = rng.beta(alpha=2, beta=5, size=10)
chi_square = rng.chisquare(df=2, size=10)

# Sampling
choices = rng.choice([1, 3, 5, 7, 9], size=10)  # With replacement
permutation = rng.permutation(10)               # Shuffle
shuffle = rng.shuffle(arr)                      # Shuffle in-place

# Legacy API (for compatibility)
np.random.seed(42)
np.random.rand(3, 3)     # Use Generator instead
```

## Advanced Topics

### NumPy 2.0 Migration

See [NumPy 2.0 Migration](references/07-numpy2-migration.md) for upgrade guide.

Key changes in NumPy 2.0+:

1. **Type promotion** (NEP 50): Scalars preserve precision
   ```python
   # Now returns float32, not float64
   result = np.float32(3) + 3.0
   ```

2. **Cleaned namespace**: ~100 members removed/moved
   ```python
   # Use np.all instead of np.alltrue
   # Use np.isin instead of np.in1d
   # Use np.trapezoid instead of np.trapz
   ```

3. **Private namespaces**: `np.core` → `np._core`

4. **Default integer**: Now 64-bit on all 64-bit systems (was C `long`)

### Performance Optimization

See [Performance Tips](references/08-performance-tips.md) for advanced techniques.

```python
# Use vectorized operations instead of loops
result = np.sum(arr * weights)  # Not: sum(a*w for a,w in zip(arr, weights))

# Pre-allocate arrays instead of growing
arr = np.empty(n)
for i in range(n):
    arr[i] = compute_value(i)  # Not: arr = np.append(arr, value)

# Use appropriate dtypes to save memory
arr = np.array(data, dtype=np.float32)  # Half the memory of float64

# In-place operations when possible
np.add(arr1, arr2, out=arr1)  # Not: arr1 = arr1 + arr2
```

### Array API Standard

NumPy 2.x implements the [Array API standard](https://data-apis.org/array-api/) for interoperability:

```python
import numpy as np

# Use np.array_api namespace for standard-compliant code
import numpy.array_api as xp

x = xp.asarray([1, 2, 3])
y = xp.add(x, 1)
```

## Troubleshooting

### Common Issues

**"Cannot cast ufunc output" error**: Occurs when result type doesn't fit destination dtype.
```python
# Problem
arr = np.array([1, 2, 3], dtype=np.int32)
arr += arr * 0.5  # Error: can't convert float to int

# Solution
arr = arr.astype(np.float64)
arr += arr * 0.5
```

**"IndexError: index out of bounds"**: Check array dimensions.
```python
arr = np.array([1, 2, 3])
print(arr[3])  # Error: only indices 0, 1, 2 exist
```

**Broadcasting errors**: Shapes must be compatible.
```python
# Problem
arr1 = np.zeros((3, 4))
arr2 = np.zeros((5,))
result = arr1 + arr2  # Error: incompatible shapes

# Solution: make shapes broadcastable
arr2 = np.zeros((3, 1))  # Now broadcasts to (3, 4)
```

**Memory errors with large arrays**: Use appropriate dtypes or chunking.
```python
# Use float32 instead of float64 if precision allows
arr = np.zeros(10_000_000, dtype=np.float32)  # 40 MB vs 80 MB

# Process in chunks for very large files
for chunk in np.memmap('large_file.dat', dtype='float32', mode='r', shape=(1000000,)):
    process(chunk[:1000])
```

## References

- **Official Documentation**: https://numpy.org/doc/stable/
- **GitHub Repository**: https://github.com/numpy/numpy
- **NumPy 2.0 Migration Guide**: https://numpy.org/doc/stable/numpy_2_0_migration_guide.html
- **NEP 50 (Type Promotion)**: https://numpy.org/neps/nep-0050-new-type-promotion.html
- **NEP 52 (Namespace Cleanup)**: https://numpy.org/neps/nep-0052-public-naming.html
- **Array API Standard**: https://data-apis.org/array-api/
- **Random Number Generation Guide**: https://numpy.org/doc/stable/reference/random/index.html

### Reference Files

- [Array Creation](references/01-array-creation.md) - Comprehensive array creation methods
- [Indexing and Slicing](references/02-indexing-slicing.md) - Accessing array elements
- [Array Manipulation](references/03-array-manipulation.md) - Reshaping, stacking, splitting
- [Mathematical Functions](references/04-mathematical-functions.md) - Ufuncs and mathematical operations
- [Linear Algebra](references/05-linear-algebra.md) - Matrix operations and decompositions
- [Random Number Generation](references/06-random-generation.md) - Modern Generator API
- [NumPy 2.0 Migration](references/07-numpy2-migration.md) - Upgrade guide from NumPy 1.x
- [Performance Tips](references/08-performance-tips.md) - Optimization techniques

## Best Practices

1. **Always use the modern random API**: `np.random.default_rng()` instead of legacy functions
2. **Be explicit about dtypes**: Specify dtype when creating arrays to avoid surprises
3. **Use vectorized operations**: Avoid Python loops for numerical computations
4. **Check array shapes**: Use `.shape` and `.ndim` to debug broadcasting issues
5. **Prefer `np.linalg.solve` over `np.linalg.inv`**: More stable and faster for solving linear systems
6. **Use `np.einsum` for complex tensor operations**: Often faster and clearer than multiple reshapes
7. **Leverage NumPy's broadcasting**: Write cleaner code without explicit loops
8. **Read the migration guide when upgrading**: NumPy 2.0 has breaking changes
