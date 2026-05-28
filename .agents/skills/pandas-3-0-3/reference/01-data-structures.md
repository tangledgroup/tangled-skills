# Data Structures

## Contents
- Series
- DataFrame
- Index Objects
- Data Types (dtypes)
- pandas 3.0 String Default

## Series

A one-dimensional labeled array holding any data type. The axis labels are collectively called the **index**.

```python
import pandas as pd
import numpy as np

# From list — auto RangeIndex
s = pd.Series([10, 20, 30])

# With explicit index
s = pd.Series([10, 20, 30], index=["a", "b", "c"])

# From dict
s = pd.Series({"x": 1, "y": 2, "z": 3})

# Key attributes
s.values    # underlying numpy/pyarrow array
s.index     # Index object
s.name      # label (optional)
```

## DataFrame

A two-dimensional labeled table with named columns and an index. Columns can have different dtypes.

```python
# From dict of lists
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30],
})

# From dict of Series (index alignment is automatic)
df = pd.DataFrame({
    "a": pd.Series([1, 2, 3]),
    "b": pd.Series([4, 5]),  # misaligned → NaN at index 2
})

# With explicit index and columns
df = pd.DataFrame(
    np.random.randn(6, 4),
    index=pd.date_range("2024-01-01", periods=6),
    columns=["A", "B", "C", "D"],
)
```

### Key Attributes

| attribute | description |
|-----------|-------------|
| `df.shape` | `(rows, cols)` tuple |
| `df.columns` | column labels (Index) |
| `df.index` | row labels (Index) |
| `df.dtypes` | dtype per column |
| `df.values` | underlying 2D array |
| `df.info()` | summary of columns, dtypes, memory |

### Key Methods

| method | description |
|--------|-------------|
| `df.head(n)` / `df.tail(n)` | first/last n rows (default 5) |
| `df.describe()` | descriptive statistics per column |
| `df.T` | transpose |
| `df.sort_values("col")` | sort by column values |
| `df.sort_index()` | sort by index labels |
| `df.rename(columns={...})` | rename columns |

## Index Objects

Index is the immutable axis label container. Common variants:

- **`RangeIndex`** — default integer index (0, 1, 2, …)
- **`Index`** — generic immutable array of labels
- **`DatetimeIndex`** — timezone-aware timestamps
- **`TimedeltaIndex`** — time durations
- **`PeriodIndex`** — fixed-frequency time periods
- **`MultiIndex`** — hierarchical (multi-level) index
- **`CategoricalIndex`** — categorical labels
- **`IntervalIndex`** — intervals/bins

```python
# Set/reset index
df = df.set_index("name")
df = df.reset_index()

# MultiIndex from multiple columns
df = df.set_index(["region", "category"])
```

## Data Types (dtypes)

pandas supports a wide range of dtypes. Each column has exactly one dtype.

### Standard NumPy dtypes

| dtype | description |
|-------|-------------|
| `int64`, `int32`, etc. | Fixed-width integers |
| `float64`, `float32` | Floating-point numbers |
| `bool` | Boolean values |
| `datetime64[ns]` | Timestamps (nanosecond precision) |
| `timedelta64[ns]` | Time durations |

### Nullable dtypes

Use `pd.NA` as missing value sentinel (three-valued logic):

```python
# Nullable integer — allows NaN without converting to float
s = pd.Series([1, 2, None], dtype="Int64")

# Nullable boolean
s = pd.Series([True, False, None], dtype="boolean")
```

### Selecting columns by dtype

```python
df.select_dtypes(include=["number"])    # numeric columns only
df.select_dtypes(exclude=["str"])       # non-string columns
```

## pandas 3.0 String Default

In pandas 3.0, string data is inferred as `str` dtype by default (previously `object`).

```python
# pandas 3.0 — str dtype by default
s = pd.Series(["a", "b", None])
print(s.dtype)  # str

# Missing value is NaN (not pd.NA)
pd.isna(s[2])   # True

# Explicit specification
s = pd.Series(["a", "b"], dtype="str")
```

**Key differences from `object`:**
- Only strings and missing values allowed (non-string setitem raises error)
- Missing value sentinel is `np.nan` (consistent with other default dtypes)
- PyArrow-backed when `pyarrow` is installed (better memory and performance)
- Falls back to NumPy `object` storage when PyArrow is not available

**Migration from pandas < 3.0:** Code that checks `.dtype == "object"` to detect string columns will need updating. Use `pd.api.types.is_string_dtype()` instead.
