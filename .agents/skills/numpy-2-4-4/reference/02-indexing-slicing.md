# Indexing and Slicing in NumPy 2.4.4

## Overview

NumPy provides powerful indexing and slicing mechanisms for accessing and modifying array elements:

- **Basic indexing**: Python-style lists and slices
- **Advanced indexing**: Integer arrays, boolean masks, fancy indexing
- **Slicing**: Ranges with step, ellipsis, newaxis
- **Broadcasting in indexing**: Using arrays to select elements

## Basic Indexing

### 1D Arrays

```python
import numpy as np

arr = np.array([10, 20, 30, 40, 50])

# Single element
first = arr[0]      # 10
last = arr[-1]      # 50 (negative index from end)
third = arr[2]      # 30

# Assignment
arr[0] = 100        # Modify single element
arr[-1] = 500       # Modify last element
```

### 2D Arrays

```python
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

# Single element: row, column
element = matrix[0, 0]    # 1 (top-left)
element = matrix[1, 2]    # 6 (row 1, col 2)
element = matrix[-1, -1]  # 9 (bottom-right)

# Assignment
matrix[0, 0] = 99         # Change top-left to 99
```

### ND Arrays

```python
tensor = np.arange(24).reshape(2, 3, 4)

# Access element: dimension1, dimension2, dimension3
element = tensor[0, 1, 2]  # Element at [0, 1, 2]

# Number of indices must match ndim
tensor.shape  # (2, 3, 4) - need 3 indices
```

## Slicing

### Basic Slices

```python
arr = np.arange(10)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Slice syntax: start:stop:step
first_five = arr[:5]       # [0, 1, 2, 3, 4]
last_five = arr[5:]        # [5, 6, 7, 8, 9]
middle = arr[2:7]          # [2, 3, 4, 5, 6]

# With step
every_other = arr[::2]     # [0, 2, 4, 6, 8]
reverse = arr[::-1]        # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
backwards_step = arr[9:2:-1]  # [9, 8, 7, 6, 5, 4, 3]

# Negative indices in slices
almost_all = arr[1:-1]     # [1, 2, 3, 4, 5, 6, 7, 8]
```

### Multi-dimensional Slicing

```python
matrix = np.arange(20).reshape(4, 5)
# [[ 0  1  2  3  4]
#  [ 5  6  7  8  9]
#  [10 11 12 13 14]
#  [15 16 17 18 19]]

# Slice rows and columns independently
first_two_rows = matrix[:2, :]      # First 2 rows, all columns
last_two_cols = matrix[:, -2:]      # All rows, last 2 columns
submatrix = matrix[1:3, 2:4]        # Rows 1-2, cols 2-3

# Combine with step
every_other_row = matrix[::2, :]    # Rows 0 and 2
every_other_both = matrix[::2, ::2] # Every other row and column

# Assignment to slices (modifies original)
matrix[:2, :] = 0                   # Set first two rows to 0
```

### Slices Create Views

```python
arr = np.arange(10)
slice_view = arr[2:7]    # View, not copy!

# Modifying view affects original
slice_view[0] = 999
print(arr[2])            # 999 - original is changed!

# To create a copy:
slice_copy = arr[2:7].copy()
```

## Advanced Indexing

### Integer Array Indexing

```python
arr = np.arange(10)

# Select specific indices
indices = [0, 2, 4, 6]
selected = arr[indices]      # [0, 2, 4, 6]

# Indices can be in any order
reordered = arr[[9, 7, 5, 3, 1]]  # [9, 7, 5, 3, 1]

# Repetition allowed
with_repeat = arr[[1, 1, 2, 2, 2]]  # [1, 1, 2, 2, 2]

# Multi-dimensional
matrix = np.arange(20).reshape(4, 5)
rows = [0, 2, 3]
cols = [1, 3, 4]
selected = matrix[rows, cols]  # [1, 13, 18] - pairs (0,1), (2,3), (3,4)
```

### Boolean (Mask) Indexing

```python
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Create boolean mask
mask = arr > 5              # [False, False, ..., True, True]
filtered = arr[mask]        # [6, 7, 8, 9, 10]

# Complex conditions
mask = (arr > 3) & (arr < 8)   # [4, 5, 6, 7]
mask = (arr % 2 == 0)          # Even numbers: [2, 4, 6, 8, 10]

# Multiple conditions with np.logical
mask = np.logical_and(arr > 3, arr < 8)
mask = np.logical_or(arr < 3, arr > 8)

# Count True values
count = np.sum(arr > 5)        # 5 elements greater than 5

# Assignment with mask
arr[arr > 5] = 0               # Set all values > 5 to 0
arr[(arr > 2) & (arr < 8)] = -1  # Set 3-7 to -1
```

### Boolean Indexing in Multi-dimensional Arrays

```python
matrix = np.arange(20).reshape(4, 5)

# Apply mask to one dimension
row_mask = matrix[0, :] > 2
first_row_filtered = matrix[0, row_mask]  # [3, 4] from first row

# Element-wise mask (flattened view)
mask = matrix > 10
high_values = matrix[mask]    # All values > 10: [11, 12, ..., 19]

# Set values with mask
matrix[matrix < 5] = 0        # Set all values < 5 to 0
```

### Combining Indexing Types

```python
arr = np.arange(20).reshape(4, 5)

# Integer array + slice
selected = arr[[0, 2], 1:4]   # Rows 0 and 2, columns 1-3

# Boolean + integer
mask = arr[0, :] > 2
selected = arr[0, mask]       # First row where value > 2

# Slice + boolean
rows_of_interest = arr[:2, arr[0, :] > 2]
```

## Special Indexing Tools

### Ellipsis (...)

```python
tensor = np.arange(24).reshape(2, 3, 4)

# Use ... to represent "all remaining dimensions"
first_slice = tensor[:, :, 0]    # All of dim 0,1, first of dim 2
with_ellipsis = tensor[..., 0]   # Same as above

# Useful for high-dimensional arrays
arr_5d = np.zeros((2, 3, 4, 5, 6))
first_two_dims = arr_5d[:, :, ..., 0]  # Equivalent to [:, :, :, :, 0]

# Multiple ellipses not allowed - use slices instead
```

### np.newaxis (or None)

```python
arr = np.array([1, 2, 3])       # Shape: (3,)

# Add new dimension
column = arr[:, np.newaxis]     # Shape: (3, 1)
row = arr[np.newaxis, :]        # Shape: (1, 3)

# Equivalent using None
column = arr[:, None]           # Same as above
row = arr[None, :]              # Same as above

# Useful for broadcasting
matrix = np.zeros((3, 4))
result = matrix + arr[:, np.newaxis]  # Add column vector to each column
```

### np.ix_ - Open Meshgrid

```python
arr = np.arange(20).reshape(4, 5)

# Select specific rows AND columns (all combinations)
rows = [0, 2]
cols = [1, 3]

# Using ix_ creates open meshgrid
submatrix = arr[np.ix_(rows, cols)]
# Returns 2x2 matrix: all combinations of rows [0,2] and cols [1,3]
# [[ 1  3]
#  [11 13]]

# Without ix_, you get element-wise pairing:
paired = arr[rows, cols]  # [1, 13] - pairs (0,1) and (2,3)
```

## Fancy Indexing Details

### Assignment with Fancy Indexing

```python
arr = np.arange(10)

# Fancy indexing creates a copy, not a view!
indices = [1, 3, 5, 7]
selected = arr[indices]
selected[0] = 999              # Modifies copy only
print(arr[1])                  # Still 1, not 999

# For assignment to work:
arr[indices] = [10, 30, 50, 70]  # Direct assignment works
```

### Repeated Indices in Assignment

```python
arr = np.zeros(10)
indices = [1, 1, 2, 2]
values = [10, 20, 30, 40]

# Each index gets last value assigned
arr[indices] = values
print(arr[1])  # 20 (last value for index 1)
print(arr[2])  # 40 (last value for index 2)

# Use np.add.at for accumulation
arr = np.zeros(10)
np.add.at(arr, indices, values)
print(arr[1])  # 30 (10 + 20)
print(arr[2])  # 70 (30 + 40)
```

## Conditional Operations

### np.where()

```python
arr = np.array([1, 2, 3, 4, 5])

# Simple condition
result = np.where(arr > 3, arr, 0)
# [0, 0, 0, 4, 5] - values > 3 kept, others set to 0

# Return indices where condition is True
indices = np.where(arr > 3)      # (array([3, 4]),)
values = arr[np.where(arr > 3)]  # [4, 5]

# Multi-dimensional
matrix = np.arange(12).reshape(3, 4)
rows, cols = np.where(matrix > 5)
# rows: [1, 1, 1, 2, 2, 2], cols: [1, 2, 3, 0, 1, 2, 3]

# Replace values based on condition
arr = np.where(arr < 3, 0, arr)  # Values < 3 become 0
```

### np.select()

```python
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Multiple conditions
conditions = [
    arr < 3,
    (arr >= 3) & (arr <= 7),
    arr > 7
]
choices = ['low', 'medium', 'high']

result = np.select(conditions, choices, default='unknown')
# ['low', 'low', 'medium', ..., 'high', 'high']
```

## Searching and Finding

### Finding Elements

```python
arr = np.array([1, 2, 3, 2, 4, 2, 5])

# Find where condition is True
indices = np.where(arr == 2)         # (array([1, 3, 5]),)

# Find first occurrence
first_idx = np.argmax(arr == 2)      # 1

# Find non-zero elements
nonzero = np.nonzero(arr)            # Same as where for boolean

# argmin/argmax
arr = np.array([3, 1, 4, 1, 5, 9])
min_idx = np.argmin(arr)             # 1 (first occurrence of min)
max_idx = np.argmax(arr)             # 5 (index of max value)

# Multi-dimensional with axis
matrix = np.array([[3, 1, 4], [2, 5, 1]])
row_min_idx = np.argmin(matrix, axis=1)  # [1, 0] - min index in each row
```

### Searchsorted (Binary Search)

```python
arr = np.array([1, 2, 2, 3, 4, 5])

# Find where to insert values to maintain sorted order
indices = np.searchsorted(arr, [2, 3.5])  # [1, 4]

# 'left' vs 'right' for duplicates
left_idx = np.searchsorted(arr, 2, side='left')   # 1 (first position)
right_idx = np.searchsorted(arr, 2, side='right') # 3 (after all 2s)

# Useful for binning data
bins = [0, 10, 20, 30]
data = [5, 15, 25, 35]
bin_indices = np.searchsorted(bins, data)  # [1, 2, 2, 3]
```

## Performance Tips

1. **Use slicing for contiguous ranges** (faster than fancy indexing)
2. **Boolean masks are efficient** for filtering large arrays
3. **Avoid repeated fancy indexing** - creates copies each time
4. **Use views when possible** to save memory (slices create views)
5. **Pre-filter with argmax/argmin** instead of where for single values

## Common Patterns

```python
# Get indices of top N values
arr = np.random.rand(100)
top_n_indices = np.argsort(arr)[-10:][::-1]  # Indices of 10 largest

# Remove NaN values
clean_arr = arr[~np.isnan(arr)]

# Get unique values with counts
unique, counts = np.unique(arr, return_counts=True)

# Mask out specific rows/cols
mask = np.ones_like(matrix, dtype=bool)
mask[[1, 3], :] = False  # Exclude rows 1 and 3
filtered = matrix[mask]

# Index with broadcasting
rows = np.array([0, 2])[:, np.newaxis]  # Column vector
cols = np.array([1, 3, 5])              # Row vector
selected = matrix[rows, cols]           # (2, 3) array of all combinations
```

## Troubleshooting

**"IndexError: index out of bounds"**: Check that indices are within range.
```python
arr = np.array([1, 2, 3])
arr[3]  # Error! Valid indices: 0, 1, 2
```

**"Shape mismatch in assignment"**: Ensure shapes are broadcastable.
```python
matrix = np.zeros((3, 4))
matrix[:, 0] = [1, 2]  # Error: need 3 values, got 2
matrix[:, 0] = [1, 2, 3]  # OK
```

**"Boolean index is wrong shape"**: Boolean mask must match array shape.
```python
arr = np.zeros((3, 4))
mask = np.array([True, False])  # Wrong shape!
mask = arr > 0  # Correct: same shape as arr
```
