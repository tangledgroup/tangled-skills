# Mathematical Functions in NumPy 2.4.4

## Overview

NumPy provides comprehensive mathematical functions organized into:

- **Universal functions (ufuncs)**: Element-wise operations on arrays
- **Aggregation functions**: Sum, mean, std across axes
- **Mathematical categories**: Trigonometric, exponential, statistical, etc.
- **Floating-point control**: Error handling and precision

## Universal Functions (Ufuncs)

### Basic Arithmetic

```python
import numpy as np

arr1 = np.array([1, 2, 3, 4])
arr2 = np.array([5, 6, 7, 8])

# Addition
result = np.add(arr1, arr2)      # [6, 8, 10, 12]
result = arr1 + arr2             # Same using operator

# Subtraction
result = np.subtract(arr1, arr2) # [-4, -4, -4, -4]
result = arr1 - arr2

# Multiplication (element-wise)
result = np.multiply(arr1, arr2) # [5, 12, 21, 32]
result = arr1 * arr2

# Division
result = np.divide(arr1, arr2)   # [0.2, 0.333..., 0.428..., 0.5]
result = arr1 / arr2

# Integer division
result = np.floor_divide(arr2, arr1)  # [5, 3, 2, 2]
result = arr2 // arr1

# Remainder (modulo)
result = np.mod(arr2, arr1)      # [0, 0, 1, 0]
result = arr2 % arr1

# Exponentiation
result = np.power(arr1, 2)       # [1, 4, 9, 16]
result = arr1 ** 2

# Negative
result = np.negative(arr1)       # [-1, -2, -3, -4]
result = -arr1

# Absolute value
result = np.abs([-1, 2, -3, 4])  # [1, 2, 3, 4]
result = np.absolute([-1, 2, -3, 4])
```

### Trigonometric Functions

```python
angles_deg = np.array([0, 30, 45, 60, 90])
angles_rad = np.deg2rad(angles_deg)  # Convert to radians

# Basic trig functions
sin_vals = np.sin(angles_rad)       # [0, 0.5, 0.707..., 0.866..., 1]
cos_vals = np.cos(angles_rad)       # [1, 0.866..., 0.707..., 0.5, 0]
tan_vals = np.tan(angles_rad)       # [0, 0.577..., 1, 1.732..., inf]

# Inverse trig functions (return radians)
asin = np.arcsin(0.5)               # π/6 ≈ 0.524
acos = np.arccos(0.5)               # π/3 ≈ 1.047
atan = np.arctan(1.0)               # π/4 ≈ 0.785

# atan2(y, x) - angle from coordinates
angle = np.arctan2(1, 1)            # π/4 (first quadrant)

# Hyperbolic functions
sinh = np.sinh(angles_rad)
cosh = np.cosh(angles_rad)
tanh = np.tanh(angles_rad)

# Inverse hyperbolic
asinh = np.arcsinh(1.0)
acosh = np.arccosh(2.0)
atanh = np.arctanh(0.5)

# Degree-radian conversion
rad_to_deg = np.rad2deg(np.pi)      # 180.0
deg_to_rad = np.deg2rad(180)        # π
```

### Exponential and Logarithmic

```python
arr = np.array([1, 2, 3, 4])

# Exponential
exp_vals = np.exp(arr)              # [e^1, e^2, e^3, e^4]
exp2_vals = np.exp2(arr)            # [2^1, 2^2, 2^3, 2^4]
expm1_vals = np.expm1(arr)          # e^x - 1 (more accurate for small x)

# Natural logarithm
log_vals = np.log(arr)              # ln(x)
log10_vals = np.log10(arr)          # log base 10
log2_vals = np.log2(arr)            # log base 2

# Log with offset (more accurate for small x)
logp1_vals = np.log1p(arr - 1)      # ln(x + 1)

# Power and roots
sqrt_vals = np.sqrt(arr)            # [1, 1.414..., 1.732..., 2]
cbrt_vals = np.cbrt([8, 27, 64])    # [2, 3, 4]

# Square
squared = np.square(arr)            # [1, 4, 9, 16]
```

### Rounding and Remainders

```python
arr = np.array([1.2, 1.5, 1.7, 2.3, 2.5, 2.7])

# Floor (round down)
floored = np.floor(arr)             # [1, 1, 1, 2, 2, 2]

# Ceiling (round up)
ceiled = np.ceil(arr)               # [2, 2, 2, 3, 3, 3]

# Round to nearest integer
rounded = np.round(arr)             # [1, 2, 2, 2, 2, 3]
# Note: 1.5 → 2 (rounds to even), 2.5 → 2 (rounds to even)

# Round to decimal places
rounded_1 = np.round([1.234, 5.678], 1)  # [1.2, 5.7]

# Truncate toward zero
truncated = np.trunc([1.9, -1.9])   # [1.0, -1.0]

# Modf (integer and fractional parts)
frac, whole = np.modf([1.2, 2.7])   # frac: [0.2, 0.7], whole: [1.0, 2.0]

# Remainder after division
remainder = np.remainder([7, 8, 9], 3)  # [1, 2, 0]
```

### Sign and Comparison

```python
arr = np.array([-3, -1, 0, 2, 4])

# Sign of elements
signs = np.sign(arr)                # [-1, -1, 0, 1, 1]

# Maximum and minimum
max_val = np.maximum(arr, 0)        # [0, 0, 0, 2, 4]
min_val = np.minimum(arr, 2)        # [-3, -1, 0, 2, 2]

# Element-wise max/min of two arrays
arr1 = np.array([1, 5, 3])
arr2 = np.array([2, 4, 4])
elem_max = np.maximum(arr1, arr2)   # [2, 5, 4]
elem_min = np.minimum(arr1, arr2)   # [1, 4, 3]

# Clip values to range
clipped = np.clip(arr, -1, 3)       # [-1, -1, 0, 2, 3]

# Absolute difference
diff = np.absdiff([1, 2, 3], [2, 2, 2])  # [1, 0, 1] (NumPy 2.0+)
```

## Aggregation Functions

### Sum and Product

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Sum all elements
total = np.sum(arr)                 # 21

# Sum along axis
col_sum = np.sum(arr, axis=0)       # [5, 7, 9] - sum of each column
row_sum = np.sum(arr, axis=1)       # [6, 15] - sum of each row

# Cumulative sum
cumsum = np.cumsum(arr)             # [1, 3, 6, 10, 15, 21] (flattened)
cumsum_axis0 = np.cumsum(arr, axis=0)  # [[1, 2, 3], [5, 7, 9]]

# Product of all elements
product = np.prod(arr)              # 720

# Cumulative product
cumprod = np.cumprod(arr)           # [1, 2, 6, 24, 120, 720]

# Sum with initial value
sum_init = np.sum([1, 2, 3], initial=10)  # 16 (NumPy 1.25+)
```

### Mean and Variance

```python
arr = np.array([1, 2, 3, 4, 5])

# Arithmetic mean
mean_val = np.mean(arr)             # 3.0

# Weighted average
values = np.array([1, 2, 3, 4])
weights = np.array([4, 3, 2, 1])
weighted_mean = np.average(values, weights=weights)  # 1.667

# Geometric mean
geo_mean = np.geometric_mean([1, 2, 3, 4])  # 2.213 (NumPy 1.22+)

# Harmonic mean
harm_mean = np.harmonic_mean([1, 2, 4])     # 1.714 (NumPy 1.22+)

# Variance
var_pop = np.var(arr)               # Population variance: 2.0
var_samp = np.var(arr, ddof=1)      # Sample variance: 2.5

# Standard deviation
std_pop = np.std(arr)               # Population std: 1.414
std_samp = np.std(arr, ddof=1)      # Sample std: 1.581

# Multi-dimensional with axis
matrix = np.array([[1, 2, 3], [4, 5, 6]])
row_means = np.mean(matrix, axis=1) # [2.0, 5.0]
col_means = np.mean(matrix, axis=0) # [2.5, 3.5, 4.5]
```

### Min and Max

```python
arr = np.array([[1, 5, 3], [4, 2, 6]])

# Global min/max
min_val = np.min(arr)               # 1
max_val = np.max(arr)               # 6

# Axis-wise min/max
row_min = np.min(arr, axis=1)       # [1, 2]
col_max = np.max(arr, axis=0)       # [4, 5, 6]

# Indices of min/max
min_idx = np.argmin(arr)            # 0 (flat index)
max_idx = np.argmax(arr)            # 5 (flat index)
row_min_idx = np.argmin(arr, axis=1) # [0, 1] - min index in each row

# ptp (peak-to-peak: max - min)
range_val = np.ptp(arr)             # 5
row_ptp = np.ptp(arr, axis=1)       # [4, 4]

# Partition (k smallest/largest without full sort)
arr = np.array([3, 1, 4, 1, 5, 9, 2])
three_smallest = np.partition(arr, 3)[:3]  # [1, 1, 2] (unsorted)
```

### Counting and Checking

```python
arr = np.array([0, 1, 0, 2, 0, 3])

# Count non-zero elements
nonzero_count = np.count_nonzero(arr)  # 3

# Check if any/all are True/non-zero
has_nonzero = np.any(arr)              # True
all_nonzero = np.all(arr)              # False

# With condition
any_positive = np.any(arr > 1)         # True
all_positive = np.all(arr > 0)         # False

# Count along axis
matrix = np.array([[1, 0, 2], [0, 0, 3]])
col_nonzero = np.count_nonzero(matrix, axis=0)  # [1, 0, 2]
```

### Cumulative Operations

```python
arr = np.array([1, 2, 3, 4])

# Cumulative sum
cumsum = np.cumsum(arr)                # [1, 3, 6, 10]

# Cumulative product
cumprod = np.cumprod(arr)              # [1, 2, 6, 24]

# Cumulative max/min
cummax = np.cummax([1, 3, 2, 5])       # [1, 3, 3, 5] (NumPy 1.22+)
cummin = np.cummin([5, 3, 4, 1])       # [5, 3, 3, 1] (NumPy 1.22+)

# Cumulative sum with axis
matrix = np.array([[1, 2], [3, 4]])
cumsum_rows = np.cumsum(matrix, axis=1)  # [[1, 3], [3, 7]]
```

## Statistical Functions

### Sorting and Ordering

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])

# Sort array
sorted_arr = np.sort(arr)             # [1, 1, 2, 3, 4, 5, 6, 9]

# Argsort (indices that would sort)
sort_indices = np.argsort(arr)        # [1, 3, 6, 0, 2, 4, 7, 5]
sorted_via_argsort = arr[sort_indices]  # [1, 1, 2, 3, 4, 5, 6, 9]

# Lexicographic sort (multi-key)
names = np.array(['Alice', 'Bob', 'Alice'])
scores = np.array([85, 90, 85])
sorted_idx = np.lexsort((scores, names))  # Sort by names, then scores

# Partition (partial sort)
k_smallest = np.partition(arr, 3)[:4]   # 4 smallest (unsorted)

# Multi-dimensional sort
matrix = np.array([[3, 1, 2], [6, 4, 5]])
row_sorted = np.sort(matrix, axis=1)    # Sort each row
```

### Percentiles and Quantiles

```python
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Percentile
median = np.percentile(arr, 50)        # 5.5
p25, p75 = np.percentile(arr, [25, 75])  # 3.25, 7.75

# Quantile (0 to 1 scale)
q_median = np.quantile(arr, 0.5)       # 5.5
quartiles = np.quantile(arr, [0.25, 0.5, 0.75])  # Q1, median, Q3

# With axis
matrix = np.array([[1, 2, 3], [4, 5, 6]])
col_median = np.median(matrix, axis=0)  # [2.5, 3.5, 4.5]
```

### Correlation and Covariance

```python
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 1, 3, 5])

# Correlation coefficient
corr_coef = np.corrcoef(x, y)[0, 1]    # Single correlation value

# Full correlation matrix
corr_matrix = np.corrcoef(x, y)
# [[1.      , 0.436...]
#  [0.436..., 1.     ]]

# Covariance
cov_matrix = np.cov(x, y)
# [[1.25, 0.75]
#  [0.75, 1.7]]

# Dot product and inner products
dot_prod = np.dot(x, y)                # Scalar dot product
inner_prod = np.inner(x, y)            # Same for 1D
outer_prod = np.outer(x, y)            # Outer product (matrix)
```

## Linear Algebra Functions

See [Linear Algebra](05-linear-algebra.md) for comprehensive coverage.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])

# Basic operations via np.linalg
det = np.linalg.det(A)                 # Determinant: -2.0
trace = np.linalg.trace(A)             # Trace: 5
rank = np.linalg.matrix_rank(A)        # Rank: 2

# Matrix multiplication (also use @ operator)
B = np.array([[5, 6], [7, 8]])
C = A @ B                              # [[19, 22], [43, 50]]
```

## Floating-Point Control

### Error Handling

```python
import numpy as np

# Check current error settings
print(np.geterr())

# Temporary error handling context
with np.errstate(divide='ignore', invalid='warn'):
    result = np.array([1, 0]) / np.array([0, 1])  # No error on division by zero

# Set global error behavior
np.seterr(all='raise')     # Raise exception on any floating-point error
np.seterr(divide='warn')   # Warning on division by zero
np.seterr(over='ignore')   # Ignore overflow
```

### Special Values

```python
import numpy as np

# Infinity
inf = np.inf
neg_inf = -np.inf

# NaN (Not a Number)
nan = np.nan

# Check for special values
arr = np.array([1, np.inf, -np.inf, np.nan, 5])
is_finite = np.isfinite(arr)    # [True, False, False, False, True]
is_inf = np.isinf(arr)          # [False, True, True, False, False]
is_nan = np.isnan(arr)          # [False, False, False, True, False]

# Replace NaN with value
clean_arr = np.nan_to_num(arr, nan=0.0)  # Replace NaN with 0

# NaN-aware operations
nan_mean = np.nanmean([1, 2, np.nan, 4])  # 2.333 (ignores NaN)
nan_sum = np.nansum([1, 2, np.nan, 4])    # 7.0
```

## Ufunc Features

### Out Parameter (In-Place Operations)

```python
arr1 = np.array([1, 2, 3])
arr2 = np.array([4, 5, 6])

# Create output array once
output = np.empty(3)
np.add(arr1, arr2, out=output)     # Saves memory allocation

# In-place modification
np.multiply(arr1, 2, out=arr1)     # arr1 is modified directly

# Multiple outputs
divmod_out = [np.empty(3), np.empty(3)]
np.divmod([7, 8, 9], 3, out=divmod_out)
# divmod_out[0]: [2, 2, 3] (quotient)
# divmod_out[1]: [1, 2, 0] (remainder)
```

### Where Parameter (Conditional Operations)

```python
arr = np.array([1, 2, 3, 4, 5])
mask = arr > 2

# Only modify where mask is True
np.negative(arr, where=mask, out=arr)
# arr: [1, 2, -3, -4, -5]

# Combine with initial value
result = np.zeros(5)
np.add(arr, 10, where=mask, out=result)
# result: [0, 0, 13, 14, 15]
```

### Reduce and Accumulate

```python
arr = np.array([1, 2, 3, 4])

# Reduce (apply ufunc cumulatively, return single value)
total = np.add.reduce(arr)          # 10 (same as sum)
product = np.multiply.reduce(arr)   # 24 (same as prod)

# Accumulate (return all intermediate results)
cumsum = np.add.accumulate(arr)     # [1, 3, 6, 10] (same as cumsum)
cumprod = np.multiply.accumulate(arr)  # [1, 2, 6, 24]

# Reduceat (strided reduce)
arr = np.array([0, 10, 20, 30, 40, 50])
indices = [0, 2, 4]
result = np.add.reduceat(arr, indices)  # [10, 50, 90]
# Sums: arr[0:2], arr[2:4], arr[4:]
```

## Common Patterns

```python
# Normalize array to [0, 1] range
def normalize(arr):
    return (arr - arr.min()) / (arr.max() - arr.min())

# Z-score normalization
def zscore(arr):
    return (arr - np.mean(arr)) / np.std(arr)

# Clip outliers to percentiles
def clip_outliers(arr, low_pct=1, high_pct=99):
    low, high = np.percentile(arr, [low_pct, high_pct])
    return np.clip(arr, low, high)

# Safe division (avoid divide by zero)
def safe_divide(a, b):
    with np.errstate(divide='ignore', invalid='ignore'):
        result = a / b
        result[np.isinf(result)] = 0
        result[np.isnan(result)] = 0
    return result

# Moving average
def moving_average(arr, window_size=3):
    cumsum = np.cumsum(np.insert(arr, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size
```

## Performance Tips

1. **Use ufuncs over Python loops** - Vectorized operations are much faster
2. **Avoid unnecessary copies** - Use `out` parameter for in-place operations
3. **Choose appropriate dtype** - float32 is faster than float64 on some hardware
4. **Use cumulative operations** - cumsum, cumprod instead of manual accumulation
5. **Leverage broadcasting** - Avoid explicit loops with shape-compatible arrays
