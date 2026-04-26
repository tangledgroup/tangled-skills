# Universal Functions and Broadcasting

## Ufunc Basics

A universal function (ufunc) operates on ndarrays element-by-element, supporting broadcasting, type casting, and multiple outputs. Ufuncs are implemented in C for performance.

### Common Mathematical Ufuncs

```python
import numpy as np

a = np.array([1, 4, 9, 16])
np.sqrt(a)       # [1., 2., 3., 4.]
np.exp(a)        # exponential
np.log(a)        # natural log
np.sin(a)        # sine
np.cos(a)        # cosine
np.abs(a)        # absolute value
np.ceil(a)       # ceiling
np.floor(a)      # floor
np.trunc(a)      # truncate to integer
```

### Arithmetic Ufuncs

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

np.add(a, b)       # [5, 7, 9]
np.subtract(a, b)  # [-3, -3, -3]
np.multiply(a, b)  # [4, 10, 18]
np.divide(a, b)    # [0.25, 0.4, 0.5]
np.power(a, b)     # [1, 32, 729]
np.mod(a, b)       # element-wise modulo
np.negative(a)     # [-1, -2, -3]
```

### Comparison Ufuncs

```python
a = np.array([1, 5, 3])
b = np.array([2, 3, 3])

np.greater(a, b)       # [False, True, False]
np.less(a, b)          # [True, False, False]
np.equal(a, b)         # [False, False, True]
np.not_equal(a, b)     # [True, True, False]
np.greater_equal(a, b) # [False, True, True]
np.less_equal(a, b)    # [True, False, True]
```

### Logical Ufuncs

```python
a = np.array([True, False, True])
b = np.array([True, True, False])

np.logical_and(a, b)   # [True, False, False]
np.logical_or(a, b)    # [True, True, True]
np.logical_not(a)      # [False, True, False]
```

## Ufunc Methods

Every ufunc has built-in methods for reduced operations:

```python
a = np.array([1, 2, 3, 4])

# reduce — apply cumulatively along an axis
np.add.reduce(a)        # 10 (sum)
np.multiply.reduce(a)   # 24 (product)
np.maximum.reduce(a)    # 4

# accumulate — return intermediate results
np.add.accumulate(a)    # [1, 3, 6, 10]

# reduceat — partial reduces at indices
np.add.reduceat(a, [0, 2, 0])  # [3, 7, 10]

# outer — outer product
np.multiply.outer([1, 2], [3, 4])  # [[3,4],[6,8]]

# at — in-place operation
np.add.at(a, [0, 2], 10)  # a becomes [11, 2, 13, 4]
```

## Ufunc Keyword Arguments

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# out — write result to pre-allocated array
result = np.empty(3)
np.add(a, b, out=result)

# where — boolean mask for conditional application
mask = np.array([True, False, True])
output = np.zeros(3)
np.add(a, b, out=output, where=mask)  # [5, 0., 9]

# dtype — override computation precision
np.multiply(a, b, dtype=np.float64)

# casting — control type casting policy
np.add(a, b, casting='safe')
```

## Broadcasting Rules

Broadcasting determines how arrays of different shapes interact in element-wise operations.

### The Rules

1. Arrays are aligned by their **trailing** (rightmost) dimensions
2. Two dimensions are compatible when they are **equal** or **one of them is 1**
3. Missing leading dimensions are treated as size 1
4. If any pair of dimensions is incompatible, a `ValueError` is raised

### Examples

```python
# Scalar + array
np.array([1, 2, 3]) + 10        # [11, 12, 13]

# 1-D + 2-D (column broadcast)
a = np.array([[0, 0, 0],
              [10, 10, 10],
              [20, 20, 20]])
b = np.array([1, 2, 3])
a + b  # [[1,2,3], [11,12,13], [21,22,23]]

# 2-D with size-1 dimension
x = np.array([[1], [2], [3]])    # shape (3, 1)
y = np.array([10, 20, 30])       # shape (3,)
x + y  # [[11, 21, 31], [12, 22, 32], [13, 23, 33]]

# Outer product via broadcasting
a = np.array([0, 10, 20, 30])
b = np.array([1, 2, 3])
a[:, np.newaxis] + b
# [[1, 2, 3], [11, 12, 13], [21, 22, 23], [31, 32, 33]]
```

### Shape Compatibility Reference

```
Image (3d):  256 x 256 x 3
Scale (1d):           3
Result:      256 x 256 x 3    ✓

A (4d):  8 x 1 x 6 x 1
B (3d):     7 x 1 x 5
Result:  8 x 7 x 6 x 5        ✓

A (1d):  3
B (1d):  4
Result:  ValueError            ✗ trailing dims mismatch

A (2d):    2 x 1
B (3d):  8 x 4 x 3
Result:  ValueError            ✗ second-to-last dims mismatch
```

### np.broadcast_to and np.broadcast_arrays

```python
# Expand an array to a new shape via broadcasting (returns a view)
a = np.array([1, 2, 3])
b = np.broadcast_to(a, (4, 3))
# [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]]

# Broadcast multiple arrays to a common shape
x, y = np.broadcast_arrays(a, np.array([[0], [0], [0], [0]]))
```

## Generalized Ufuncs

Generalized ufuncs operate on sub-arrays rather than scalars, specified by a signature:

```python
# matmul has signature (n,k),(k,m)->(n,m) — operates on 2-D matrices
np.matmul(A, B)

# inner has signature (i),(i)->() — dot product of 1-D vectors
np.inner(a, b)

# check ufunc signature
np.add.signature    # None (standard ufunc)
np.matmul.signature # '(n,k),(k,m)->(n,m)'
```

### Common Generalized Ufuncs

- `np.matmul` / `@` — matrix multiplication, signature `(n,k),(k,m)->(n,m)`
- `np.tensordot` — tensor dot product along specified axes
- `np.einsum` — Einstein summation (most flexible, not a gufunc but similar concept)

## Performance Considerations

Ufuncs are implemented in C and execute much faster than Python loops. Key optimization strategies:

1. **Use ufuncs instead of loops** — `a + b` is faster than `[x+y for x,y in zip(a,b)]`
2. **Use the `out` parameter** to avoid temporary allocations
3. **Chain operations** rather than creating intermediates
4. **Use `np.where`** for vectorized conditional logic instead of Python if/else

```python
# Slow: Python loop
result = []
for x in a:
    result.append(x * 2 + 1)

# Fast: ufunc composition
result = np.add(np.multiply(a, 2), 1)
# Or simply:
result = a * 2 + 1  # NumPy overloads operators to use ufuncs
```
