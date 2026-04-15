# Array Manipulation in NumPy 2.4.4

## Overview

NumPy provides extensive functions for reshaping, resizing, combining, and splitting arrays:

- **Reshaping**: Change array shape without changing data
- **Transposing**: Rearrange axes order
- **Flattening**: Convert to 1D array
- **Stacking**: Combine arrays along new or existing axes
- **Splitting**: Divide arrays into multiple smaller arrays
- **Adding/Removing dimensions**: Expand or squeeze axes

## Reshaping Arrays

### reshape()

```python
import numpy as np

arr = np.arange(12)  # [0, 1, 2, ..., 11]

# Reshape to different dimensions
reshaped = arr.reshape(3, 4)     # 3 rows, 4 columns
reshaped = arr.reshape(2, 6)     # 2 rows, 6 columns
reshaped = arr.reshape(2, 2, 3)  # 3D: 2x2x3

# Infer one dimension with -1
reshaped = arr.reshape(3, -1)    # (3, 4) - NumPy calculates 4
reshaped = arr.reshape(-1, 2)    # (6, 2) - NumPy calculates 6

# Reshape preserves data order (row-major by default)
matrix = np.arange(6).reshape(2, 3)
# [[0, 1, 2]
#  [3, 4, 5]]
```

### resize()

```python
arr = np.array([[1, 2], [3, 4]])

# Resize with repetition if needed
resized = np.resize(arr, (3, 3))
# [[1, 2, 3]
#  [4, 1, 2]
#  [3, 4, 1]]

# Note: resize flattens, repeats, then reshapes
# Use reshape when size matches exactly
```

### Array.reshape Method

```python
arr = np.arange(12)

# Method form (returns view when possible)
reshaped = arr.reshape(3, 4)

# Modify in-place with resize method
arr.resize(3, 4)  # Modifies arr directly
```

## Changing Array Order

### ravel() vs flatten()

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])

# ravel() - returns view when possible (faster, less memory)
flat_view = matrix.ravel()
flat_view[0] = 99
print(matrix[0, 0])  # 99 - original changed!

# flatten() - always returns copy
flat_copy = matrix.flatten()
flat_copy[0] = 99
print(matrix[0, 0])  # 1 - original unchanged

# Specify order
row_major = matrix.ravel(order='C')  # Row-major (default)
col_major = matrix.ravel(order='F')  # Column-major (Fortran)
```

### flatten() with Axis

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])

# Flatten specific axis (NumPy 2.0+)
flat_axis0 = matrix.flatten(axis=0)  # Column-wise flattening
flat_axis1 = matrix.flatten(axis=1)  # Row-wise flattening
```

## Transposing Arrays

### Basic Transpose

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
# [[1, 2, 3]
#  [4, 5, 6]]

# Using .T attribute (reverses axes)
transposed = matrix.T
# [[1, 4]
#  [2, 5]
#  [3, 6]]

# For 1D arrays, .T has no effect
arr = np.array([1, 2, 3])
arr.T  # Still [1, 2, 3] - need reshape to get column vector
```

### transpose() with Axis Reordering

```python
tensor = np.arange(24).reshape(2, 3, 4)

# Reverse all axes
reversed_axes = tensor.transpose()  # Same as tensor.T

# Specify axis order explicitly
reordered = tensor.transpose(2, 0, 1)  # Move last axis to first

# Swap specific axes
swapped = tensor.transpose(1, 0, 2)  # Swap first two axes

# Use ... for remaining axes
partial = tensor.transpose(0, 2, 1)  # Equivalent to transpose(0, 2, 1)
```

### swapaxes()

```python
tensor = np.arange(24).reshape(2, 3, 4)

# Swap two specific axes
swapped = np.swapaxes(tensor, 0, 1)  # Swap axis 0 and 1
# Shape changes from (2, 3, 4) to (3, 2, 4)

# Method form
swapped = tensor.swapaxes(1, 2)  # Swap axis 1 and 2
```

### moveaxis()

```python
tensor = np.arange(24).reshape(2, 3, 4)

# Move axis from source to destination
moved = np.moveaxis(tensor, -1, 0)  # Move last axis to first
# Shape: (4, 2, 3)

# Move multiple axes
moved = np.moveaxis(tensor, [0, 1], [1, 2])  # (2,3,4) -> (4,2,3)
```

## Adding and Removing Dimensions

### expand_dims()

```python
arr = np.array([1, 2, 3])         # Shape: (3,)

# Add dimension at specific position
at_start = np.expand_dims(arr, axis=0)  # Shape: (1, 3) - row vector
at_end = np.expand_dims(arr, axis=1)    # Shape: (3, 1) - column vector

# Multiple dimensions
arr_2d = np.array([[1, 2], [3, 4]])  # Shape: (2, 2)
expanded = np.expand_dims(arr_2d, axis=0)  # Shape: (1, 2, 2)
```

### squeeze()

```python
arr = np.zeros((1, 3, 1, 5, 1))

# Remove all size-1 dimensions
squeezed = np.squeeze(arr)  # Shape: (3, 5)

# Remove specific axis
partial_squeeze = np.squeeze(arr, axis=0)  # Shape: (3, 1, 5, 1)
```

### Using newaxis/None

```python
arr = np.array([1, 2, 3])       # Shape: (3,)

# Add dimensions using None or np.newaxis
row = arr[np.newaxis, :]        # Shape: (1, 3)
col = arr[:, np.newaxis]        # Shape: (3, 1)

# Multiple new axes
expanded = arr[np.newaxis, :, np.newaxis]  # Shape: (1, 3, 1)
```

## Stacking Arrays

### hstack() - Horizontal Stack

```python
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

# 1D arrays: concatenate
hstacked = np.hstack([arr1, arr2])  # [1, 2, 3, 4, 5, 6]

# 2D arrays: stack columns
matrix1 = np.array([[1], [2]])
matrix2 = np.array([[3], [4]])
hstacked = np.hstack([matrix1, matrix2])
# [[1, 3]
#  [2, 4]]
```

### vstack() - Vertical Stack

```python
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

# 1D arrays: stack as rows
vstacked = np.vstack([arr1, arr2])
# [[1, 2, 3]
#  [4, 5, 6]]

# 2D arrays: stack rows
matrix1 = np.array([[1, 2]])
matrix2 = np.array([[3, 4]])
vstacked = np.vstack([matrix1, matrix2])
# [[1, 2]
#  [3, 4]]
```

### dstack() - Depth Stack

```python
arr1 = np.array([[1, 2]])
arr2 = np.array([[3, 4]])

# Stack along third axis
dstacked = np.dstack([arr1, arr2])  # Shape: (1, 2, 2)
```

### column_stack() and row_stack()

```python
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

# Stack as columns (like hstack for 1D)
cols = np.column_stack([arr1, arr2])
# [[1, 4]
#  [2, 5]
#  [3, 6]]

# Stack as rows (alias for vstack)
rows = np.row_stack([arr1, arr2])
# [[1, 2, 3]
#  [4, 5, 6]]
```

### stack() - Create New Axis

```python
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

# Stack along new axis (default axis=0)
stacked = np.stack([arr1, arr2])
# [[1, 2, 3]
#  [4, 5, 6]]  Shape: (2, 3)

# Specify axis position
axis1 = np.stack([arr1, arr2], axis=1)
# [[1, 4]
#  [2, 5]
#  [3, 6]]  Shape: (3, 2)
```

### concatenate() - Join Along Existing Axis

```python
arr1 = np.array([[1, 2], [3, 4]])
arr2 = np.array([[5, 6], [7, 8]])

# Concatenate along rows (axis=0)
concat_rows = np.concatenate([arr1, arr2], axis=0)
# [[1, 2]
#  [3, 4]
#  [5, 6]
#  [7, 8]]

# Concatenate along columns (axis=1)
concat_cols = np.concatenate([arr1, arr2], axis=1)
# [[1, 2, 5, 6]
#  [3, 4, 7, 8]]

# Multiple arrays
concat_all = np.concatenate([arr1, arr2, arr3], axis=0)
```

## Splitting Arrays

### split() - Equal Chunks

```python
arr = np.arange(12)

# Split into 3 equal parts
parts = np.split(arr, 3)
# [array([0, 1, 2, 3]), array([4, 5, 6, 7]), array([8, 9, 10, 11])]

# Multi-dimensional
matrix = np.arange(16).reshape(4, 4)
row_splits = np.split(matrix, 2, axis=0)  # Split rows into 2
col_splits = np.split(matrix, 2, axis=1)  # Split columns into 2
```

### array_split() - Unequal Chunks

```python
arr = np.arange(10)

# Split at specific indices (may be unequal)
parts = np.array_split(arr, 3)
# [array([0, 1, 2]), array([3, 4, 5]), array([6, 7, 8, 9])]

# Specify split positions
parts = np.array_split(arr, [3, 7])
# [array([0, 1, 2]), array([3, 4, 5, 6]), array([7, 8, 9])]
```

### hsplit(), vsplit(), dsplt()

```python
matrix = np.arange(20).reshape(4, 5)

# Horizontal split (along columns)
left, right = np.hsplit(matrix, [3])  # Split after column 3

# Vertical split (along rows)
top, bottom = np.vsplit(matrix, [2])  # Split after row 2

# Depth split (along third axis)
# Requires 3D array
tensor = np.arange(24).reshape(2, 3, 4)
front, back = np.dsplit(tensor, [2])
```

## Repeating and Tiling

### repeat()

```python
arr = np.array([1, 2, 3])

# Repeat each element
repeated = arr.repeat(2)        # [1, 1, 2, 2, 3, 3]
repeated = arr.repeat([1, 2, 3])  # [1, 2, 2, 3, 3, 3]

# Multi-dimensional with axis
matrix = np.array([[1, 2], [3, 4]])
row_repeat = np.repeat(matrix, 2, axis=0)  # Repeat each row
col_repeat = np.repeat(matrix, 2, axis=1)  # Repeat each column
```

### tile()

```python
arr = np.array([1, 2, 3])

# Tile entire array
tiled = np.tile(arr, 2)         # [1, 2, 3, 1, 2, 3]
tiled = np.tile(arr, (3,))      # Same as above

# Multi-dimensional tiling
tiled_2d = np.tile(arr, (3, 1))
# [[1, 2, 3]
#  [1, 2, 3]
#  [1, 2, 3]]

# Tile 2D array
matrix = np.array([[1, 2]])
tiled = np.tile(matrix, (2, 3))
# [[1, 2, 1, 2, 1, 2]
#  [1, 2, 1, 2, 1, 2]]
```

## Inserting and Deleting

### insert()

```python
arr = np.array([1, 2, 3, 4, 5])

# Insert scalar at position
inserted = np.insert(arr, 2, 99)      # [1, 2, 99, 3, 4, 5]

# Insert multiple values
inserted = np.insert(arr, [1, 3], [10, 20])  # [1, 10, 2, 20, 3, 4, 5]

# Multi-dimensional
matrix = np.array([[1, 2], [3, 4]])
row_inserted = np.insert(matrix, 1, [99, 99], axis=0)  # Insert row
col_inserted = np.insert(matrix, 1, [[99], [99]], axis=1)  # Insert column
```

### delete()

```python
arr = np.array([1, 2, 3, 4, 5])

# Delete by index
deleted = np.delete(arr, 2)        # [1, 2, 4, 5]
deleted = np.delete(arr, [1, 3])   # [1, 3, 5]

# Delete by slice
deleted = np.delete(arr, slice(1, 4))  # [1, 5]

# Multi-dimensional
matrix = np.array([[1, 2, 3], [4, 5, 6]])
row_deleted = np.delete(matrix, 0, axis=0)  # Delete first row
col_deleted = np.delete(matrix, 1, axis=1)  # Delete second column
```

### append()

```python
arr = np.array([1, 2, 3])

# Append values (creates new array)
appended = np.append(arr, [4, 5, 6])  # [1, 2, 3, 4, 5, 6]

# Multi-dimensional (flattens by default)
matrix = np.array([[1, 2], [3, 4]])
appended = np.append(matrix, [5, 6])  # [1, 2, 3, 4, 5, 6]

# Specify axis to preserve shape
appended = np.append(matrix, [[5, 6]], axis=0)
# [[1, 2]
#  [3, 4]
#  [5, 6]]
```

## Unique Values and Set Operations

### unique()

```python
arr = np.array([1, 2, 2, 3, 3, 3, 4])

# Get unique values (sorted)
uniques = np.unique(arr)  # [1, 2, 3, 4]

# Get indices of first occurrence
uniques, indices = np.unique(arr, return_index=True)
# indices: [0, 1, 3, 6]

# Get counts
uniques, counts = np.unique(arr, return_counts=True)
# counts: [1, 2, 3, 1]

# Multi-dimensional (operates on flattened array)
matrix = np.array([[1, 2], [2, 3]])
uniques = np.unique(matrix)  # [1, 2, 3]
```

### Set Operations

```python
arr1 = np.array([1, 2, 3, 4])
arr2 = np.array([3, 4, 5, 6])

# Union (all unique elements)
union = np.union1d(arr1, arr2)      # [1, 2, 3, 4, 5, 6]

# Intersection (common elements)
intersection = np.intersect1d(arr1, arr2)  # [3, 4]

# Difference (in arr1 but not arr2)
difference = np.setdiff1d(arr1, arr2)  # [1, 2]

# Set membership
in_arr2 = np.in1d(arr1, arr2)       # [False, False, True, True]
# Or use isin (preferred in NumPy 2.0+)
in_arr2 = np.isin(arr1, arr2)       # [False, False, True, True]
```

## Padding Arrays

### pad()

```python
arr = np.array([1, 2, 3, 4, 5])

# Pad with zeros
padded = np.pad(arr, (2, 3), 'constant')  # [0, 0, 1, 2, 3, 4, 5, 0, 0, 0]

# Pad with edge values
padded = np.pad(arr, 2, 'edge')           # [1, 1, 1, 2, 3, 4, 5, 5, 5]

# Pad with reflection
padded = np.pad(arr, 2, 'reflect')        # [3, 2, 1, 2, 3, 4, 5, 4, 3]

# Pad with wrap-around
padded = np.pad(arr, 2, 'wrap')           # [4, 5, 1, 2, 3, 4, 5, 1, 2]

# Custom constant values
padded = np.pad(arr, 2, 'constant', 
                constant_values=(-99, 99))  # [-99, -99, ..., 99, 99]

# Multi-dimensional with different padding per axis
matrix = np.array([[1, 2], [3, 4]])
padded = np.pad(matrix, ((1, 2), (2, 1)), 'constant')
# Pad: (top=1, bottom=2), (left=2, right=1)
```

## Common Patterns

```python
# Convert 1D to column vector
col = arr[:, np.newaxis]

# Convert 1D to row vector
row = arr[np.newaxis, :]

# Flatten while preserving data
flat = arr.ravel()

# Reshape with automatic dimension calculation
reshaped = arr.reshape(-1, 3)  # Last dim is 3, first calculated

# Stack list of arrays along new axis
stacked = np.stack(list_of_arrays, axis=0)

# Concatenate list of arrays
concatenated = np.concatenate(list_of_arrays, axis=0)

# Remove NaN rows
clean_matrix = matrix[~np.any(np.isnan(matrix), axis=1)]

# Get unique rows
unique_rows = np.unique(matrix, axis=0)
```

## Performance Tips

1. **Use reshape over resize** when total size matches (no data copying)
2. **Prefer views over copies**: ravel() vs flatten(), slices vs fancy indexing
3. **Use concatenate for large arrays** instead of repeated append
4. **Specify axis explicitly** to avoid unexpected behavior
5. **Use in-place operations** when possible to save memory
