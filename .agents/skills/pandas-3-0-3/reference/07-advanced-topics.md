# Advanced Topics

## Contents
- Copy-on-Write Semantics
- PyArrow Backend
- Windowing Operations
- Visualization and Styler
- Performance Tuning
- Categorical Data
- Missing Data (NA / NaT)
- Nullable Integer and Boolean
- Sparse Arrays
- User-Defined Functions (UDFs)

## Copy-on-Write Semantics

pandas 3.0 enforces consistent copy/view behavior. Every indexing operation or method returning a new DataFrame/Series *behaves as if* it were a copy.

### Key Rules

1. Indexing results never modify the source when mutated
2. Only direct assignment to the original object mutates it
3. `SettingWithCopyWarning` is removed
4. Defensive `.copy()` calls are no longer needed

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# This modifies df — direct assignment
df["c"] = df["a"] + df["b"]

# This does NOT modify df
subset = df.loc[df["a"] > 1]
subset["b"] = 99

# Correct pattern: assign back to original
df.loc[df["a"] > 1, "b"] = 99
```

### Patterns to Avoid

```python
# Chained assignment — does NOT work
df[df["a"] > 0]["b"] = 1    # modifies a temporary copy

# Instead use .loc
df.loc[df["a"] > 0, "b"] = 1
```

## PyArrow Backend

PyArrow provides extended dtypes, better performance, and interoperability.

### Using PyArrow dtypes

```python
# Explicit PyArrow-backed column
s = pd.Series([1, 2, None], dtype="int64[pyarrow]")
s = pd.Series(["a", "b"], dtype="string[pyarrow]")

# Check backend
s.dtype.storage  # 'pyarrow' or 'python'
```

### Arrow PyCapsule Interoperability

```python
# Import from any Arrow-compatible library
df = pd.DataFrame.from_arrow(polars_df)
df = pd.DataFrame.from_arrow(cudf_table)

# Export
stream = df.__arrow_c_stream__()
```

## Windowing Operations

Perform aggregations over sliding partitions of data.

### Rolling Window

```python
s = pd.Series([1, 2, 3, 4, 5])

s.rolling(window=3).sum()       # [NaN, NaN, 6, 9, 12]
s.rolling(window=3, min_periods=1).mean()
s.rolling(window="30D").mean()  # time-based window
```

### Expanding Window

Cumulative aggregation from the start:

```python
s.expanding().mean()    # cumulative mean
s.expanding().sum()     # cumulative sum
```

### Exponentially Weighted Window

```python
s.ewm(span=5).mean()    # exponential moving average
s.ewm(halflife=3).mean()
```

### Weighted Window

```python
s.rolling(window=3).apply(lambda x: np.dot(x, [0.2, 0.3, 0.5]))
```

## Visualization and Styler

### Basic Plotting (via Matplotlib)

```python
df["value"].plot(kind="line")
df.plot.bar(x="category", y="value")
df.plot.scatter(x="x", y="y")
df["value"].plot.hist(bins=20)
df.boxplot(column=["a", "b"])
```

### Styler for HTML Table Formatting

```python
styled = df.style.highlight_max(subset=["score"])
styled = df.style.bar(subset=["revenue"], color="steelblue")
styled = df.style.format({"score": "{:.1f}", "date": "{:%Y-%m-%d}"})

# Export
styled.to_html("report.html")
styled.to_excel("report.xlsx")
```

## Performance Tuning

### Prefer Vectorized Operations

```python
# Slow — Python loop
for i in range(len(df)):
    df.loc[i, "c"] = df.loc[i, "a"] + df.loc[i, "b"]

# Fast — vectorized
df["c"] = df["a"] + df["b"]
```

### Use eval() for Complex Expressions

```python
df["result"] = pd.eval("df.a + df.b * df.c / df.d")
```

### Numba JIT Compilation

```python
from numba import njit

@njit
def fast_compute(arr):
    result = np.empty(len(arr))
    for i in range(len(arr)):
        result[i] = arr[i] ** 2 + np.sin(arr[i])
    return result

df["computed"] = fast_compute(df["value"].values)
```

### Use Efficient dtypes

```python
# Reduce memory with smaller integer types
df["id"] = df["id"].astype("int32")

# Categorical for repeated string values
df["category"] = df["category"].astype("category")
```

## Categorical Data

Fixed-set of possible values. Memory-efficient and supports ordering.

```python
# Create categorical
s = pd.Series(["low", "medium", "high"], dtype="category")

# Ordered categories
s = pd.Series(
    ["low", "medium", "high"],
    dtype=pd.CategoricalDtype(
        categories=["low", "medium", "high"],
        ordered=True,
    ),
)

# Operations respecting order
s.sort_values()  # respects category order
(s == "medium").any()

# Modify categories
s.cat.add_categories(["extra"])
s.cat.remove_categories(["low"])
s.cat.rename_categories({"low": "L", "medium": "M", "high": "H"})
```

## Missing Data (NA / NaT)

### Missing Value Sentinels

| sentinel | usage |
|----------|-------|
| `np.nan` | Default missing value for `str`, `float64` columns |
| `pd.NA` | Missing value for nullable dtypes (`Int64`, `boolean`, `string`) |
| `pd.NaT` | Missing value for datetime/timedelta columns |

### Handling Missing Data

```python
# Detect
df.isna()        # boolean DataFrame
df.isna().any()  # columns with any missing values

# Drop
df.dropna()                      # drop rows with any NaN
df.dropna(subset=["col1"])       # drop rows where col1 is NaN
df.dropna(thresh=3)              # keep rows with at least 3 non-NaN

# Fill
df.fillna(0)                     # fill all NaN with 0
df.fillna({"a": 0, "b": "unknown"})  # column-specific
df.ffill()                       # forward fill
df.bfill()                       # backward fill
df["col"].fillna(df["col"].mean())

# Replace specific values with NA
df.replace(-999, pd.NA)
```

## Nullable Integer and Boolean

Use nullable types when data has missing values but you need integer/boolean semantics:

```python
# Nullable integer — preserves integer type with NaN
s = pd.Series([1, 2, None], dtype="Int64")
s.sum()     # 3 (ignores NA)
s.mean()    # 1.5

# Nullable boolean — three-valued logic (Kleene)
s = pd.Series([True, False, None], dtype="boolean")
s & True    # [True, False, <NA>]
s | False   # [True, False, <NA>]
```

## Sparse Arrays

Efficient storage for data with many repeated values (typically zeros):

```python
s = pd.Series(pd.arrays.SparseArray([0, 0, 1, 0, 0, 2, 0]))
s.sparse.density    # fraction of non-fill values

# Sparse DataFrame column
df["sparse_col"] = df["col"].astype("Sparse[int64]")
```

## User-Defined Functions (UDFs)

### apply() — Row or Column-Wise

```python
# Apply to each column
df.apply(np.sum)

# Apply to each row
df.apply(lambda row: row["a"] + row["b"], axis=1)

# Apply to a Series
df["score"].apply(lambda x: "pass" if x >= 60 else "fail")
```

### Preferred Alternatives

Vectorized operations are faster than UDFs. Prefer these when possible:

| instead of apply/lambda | use |
|------------------------|-----|
| `df.apply(lambda r: r["a"] + r["b"], axis=1)` | `df["a"] + df["b"]` or `pd.col("a") + pd.col("b")` |
| `s.apply(len)` | `s.str.len()` |
| `s.apply(lambda x: x.upper())` | `s.str.upper()` |
| `df.groupby("x").apply(func)` | `df.groupby("x").agg(func)` |
