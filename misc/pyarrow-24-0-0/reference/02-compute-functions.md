# Compute Functions

## Contents

- API Overview
- Function Categories
- Execution Options
- Grouped Aggregations
- Table and Dataset Joins

## API Overview

The `pyarrow.compute` module (conventionally imported as `pc`) provides vectorized operations on Arrays, ChunkedArrays, Tables, and scalars. Functions accept both array and scalar inputs where applicable.

```python
import pyarrow.compute as pc
import pyarrow as pa

# Direct function call
a = pa.array([1, 1, 2, 3])
pc.sum(a)  # Int64Scalar: 7

# Element-wise with two arrays
b = pa.array([4, 1, 2, 8])
pc.equal(a, b)  # [false, true, true, false]

# Scalar inputs
pc.multiply(pa.scalar(7.8), pa.scalar(9.3))  # DoubleScalar: 72.54

# Multi-value return as StructScalar
result = pc.min_max(a)  # StructScalar: [('min', 1), ('max', 3)]
min_val, max_val = result.values()
```

Functions are accessed as named functions (`pc.sum`, `pc.filter`) rather than through a generic `call()` dispatcher.

## Function Categories

### Arithmetic

`pc.add`, `pc.subtract`, `pc.multiply`, `pc.divide`, `pc.power`, `pc.logarithm`, `pc.exp`, `pc.sqrt`, `pc.abs`, `pc.ceil`, `pc.floor`, `pc.round`, `pc.truncate`

### Comparison

`pc.equal`, `pc.not_equal`, `pc.greater`, `pc.greater_equal`, `pc.less`, `pc.less_equal`, `pc.is_in`, `pc.is_null`, `pc.is_nan`, `pc.if_else`, `pc.if_else.fill_null`

### Aggregation

`pc.sum`, `pc.min`, `pc.max`, `pc.min_max`, `pc.mean`, `pc.stdev`, `pc.variance`, `pc.median`, `pc.quantile`, `pc.count`, `pc.count_distinct`, `pc.all`, `pc.any`, `pc.product`, `pc.sum_checked`

### String Operations

`pc.upper`, `pc.lower`, `pc.replace`, `pc.replace_substring`, `pc.replace_regex`, `pc.match_substring`, `pc.match_like`, `pc.split_pattern`, `pc.replace_slice`, `pc.trim_whitespace`, `pc.trim_chars`, `pc.lpad`, `pc.rpad`, `pc.length`, `pc.substr`, `pc.capitalize`, `pc.leak`, `pc.utf8_normalize`

### Temporal

`pc.year`, `pc.month`, `pc.day`, `pc.hour`, `pc.minute`, `pc.second`, `pc.millisecond`, `pc.microsecond`, `pc.nanosecond`, `pc.date_part`, `pc.truncate`, `pc.make_date`, `pc.make_timestamp`, `pc.temporal_add`, `pc.temporal_subtract`

### Hash

`pc.hash_xxh3`, `pc.hash_xxh64`, `pc.md5`, `pc.sha256`, `pc.sha512`

### Set Operations

`pc.array_difference`, `pc.array_intersect`, `pc.array_union`, `pcarray_remove_duplicate`, `pc.value_counts`, `pc.mode`

### Sorting and Filtering

`pc.sort_indices`, `pc.array_sort_indices`, `pc.filter` (applies boolean mask array to target array)

### Casting

`pc.cast`, `pc.safe_cast`, `pc.try_cast` — convert between types. `safe_cast` raises on data loss, `try_cast` produces nulls for uncastable values.

## Execution Options

Most compute functions accept an options object for controlling behavior:

```python
# Memory pool for execution
result = pc.sum(arr, memory_pool=pa.default_memory_pool())

# Skip nulls in aggregation
pc.mean(arr, skip_nulls=True)  # default True

# Cast options
pc.cast(arr, pa.float64(), safe=True)  # raise on overflow
pc.try_cast(arr, pa.int32())           # produce nulls on overflow
```

## Grouped Aggregations

Use `Table.group_by()` for hash-based grouped aggregations. Returns a grouping declaration that accepts aggregation specifications.

```python
table = pa.table({
    "keys": ["a", "a", "b", "b", "c"],
    "values": [1, 2, 3, 4, 5],
})

# Single aggregation
result = table.group_by("keys").aggregate([
    ("values", "sum"),
])
# keys: ["a","b","c"], values_sum: [3,7,5]

# Multiple aggregations
result = table.group_by("keys").aggregate([
    ("values", "sum"),
    ("values", "mean"),
    ("keys", "count"),
])

# With options
table_with_nulls = pa.table({
    "keys": ["a", "a", "a"],
    "values": [1, None, None],
})
result = table_with_nulls.group_by(["keys"]).aggregate([
    ("values", "count", pc.CountOptions(mode="all")),       # counts nulls too
])
result = table_with_nulls.group_by(["keys"]).aggregate([
    ("values", "count", pc.CountOptions(mode="only_valid")), # valid only
])
```

Supported aggregation functions (use with or without `hash_` prefix):

| Function | Description |
|---|---|
| `count` / `count_all` / `count_distinct` | Count rows, non-nulls, or distinct values |
| `sum` / `mean` / `min` / `max` / `min_max` | Numeric aggregations |
| `stddev` / `variance` / `skew` / `kurtosis` | Statistical moments |
| `first` / `last` / `first_last` | First or last value per group |
| `all` / `any` | Boolean aggregation |
| `product` | Product of values |
| `list` | Collect all values into a list |
| `distinct` | Distinct values per group |
| `tdigest` | Approximate quantiles (TDigestOptions) |
| `approximate_median` | Approximate median |
| `pivot_wider` | Pivot values by key (PivotWiderOptions) |
| `one` | Get one arbitrary value from group |

## Table and Dataset Joins

Both `Table` and `Dataset` support join operations.

```python
table1 = pa.table({"id": [1, 2, 3], "year": [2020, 2022, 2019]})
table2 = pa.table({"id": [3, 4], "n_legs": [5, 100]})

# Basic join on common key
joined = table1.join(table2, keys="id")

# Specify join type
joined = table1.join(table2, keys="id", join_type="inner")

# Multiple keys
joined = table1.join(table2, keys=["id", "year"], join_type="left outer")

# Different key names on each side
joined = table1.join(table2, left_keys="id", right_keys="item_id")
```

Supported join types: `left outer` (default), `right outer`, `inner`, `full outer`, `left semi`, `right semi`, `left anti`, `right anti`.
