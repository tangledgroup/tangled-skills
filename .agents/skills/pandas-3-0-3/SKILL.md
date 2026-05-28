---
name: pandas-3-0-3
description: >-
  Complete toolkit for pandas 3.0.3 providing DataFrame and Series data structures,
  tabular data manipulation, groupby aggregations, merging/joining, reshaping,
  time series analysis, I/O for CSV/JSON/Parquet/Excel/SQL/Iceberg,
  PyArrow integration, Copy-on-Write semantics, and the new default string dtype.
  Use when building Python programs that require data wrangling, exploratory analysis,
  ETL pipelines, statistical summaries, or any workflow centered on labeled tabular data.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pandas
  - dataframe
  - data-analysis
  - tabular-data
  - python
  - pyarrow
  - etl
category: library
external_references:
  - https://github.com/pandas-dev/pandas/tree/v3.0.3
  - https://pandas.pydata.org/docs/
---

# pandas 3.0.3

## Overview

pandas is the standard Python library for data manipulation and analysis. It provides two core data structures — `Series` (1D labeled array) and `DataFrame` (2D labeled table) — along with tools for reading/writing data, filtering, grouping, reshaping, merging, time series operations, and statistical summaries.

pandas 3.0 introduces three major changes:

1. **Dedicated string dtype by default** — String columns are now inferred as `str` (backed by PyArrow when available), replacing the legacy `object` dtype.
2. **Copy-on-Write (CoW)** — All indexing and method results behave as copies. Chained assignment no longer works, and `SettingWithCopyWarning` is removed.
3. **`pd.col()` expressions** — Column references without lambda functions in `assign()`, `loc[]`, and similar methods.

## When to Use

- Reading, cleaning, transforming, or writing tabular data (CSV, JSON, Parquet, Excel, SQL)
- Grouping data and computing aggregations (split-apply-combine)
- Merging or joining multiple tables on keys
- Reshaping data with pivot tables, melt, stack/unstack
- Time series analysis with resampling, rolling windows, or timezone handling
- Vectorized string operations on text columns
- Any Python data pipeline that operates on labeled rows and columns

## Core Concepts

### Data Structures

- **`DataFrame`** — 2D labeled table with named columns and an index. The primary workhorse.
- **`Series`** — 1D labeled array. A single column from a DataFrame is a Series.
- **`Index`** — Immutable axis labels. Supports `RangeIndex`, `DatetimeIndex`, `MultiIndex`, etc.

### Key dtypes (pandas 3.0)

| dtype | description |
|-------|-------------|
| `str` | Default string type (PyArrow-backed if available). Missing value is `NaN`. |
| `int64`, `float64`, `bool` | Standard NumPy types. |
| `Int64`, `boolean` | Nullable variants using `pd.NA`. |
| `datetime64[ns]` | Timestamps. Use `DatetimeIndex` for time-indexed data. |
| `timedelta64[ns]` | Time durations. |
| `category` | Fixed-set categorical data. Memory-efficient for repeated values. |

### Copy-on-Write (CoW)

Every indexing operation or method returning a new DataFrame/Series *behaves as if* it were a copy. Modifying a subset never modifies the original. Direct assignment to the object itself is the only way to mutate it:

```python
df["new_col"] = df["a"] + df["b"]  # OK — modifies df directly
subset = df[df["a"] > 0]
subset["b"] = 99  # Does NOT modify df (CoW semantics)
```

### `pd.col()` Expressions

Reference columns without lambda wrappers:

```python
df.assign(total=pd.col("price") * pd.col("qty"))
df.loc[pd.col("status") == "active", "flag"] = 1
```

## Usage Examples

### Create and inspect a DataFrame

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "score": [88.5, 92.0, 78.3],
})
print(df.dtypes)
# name     str
# age      int64
# score   float64
```

### Read CSV, filter, group, and write Parquet

```python
df = pd.read_csv("data.csv")
filtered = df.loc[df["revenue"] > 0]
summary = filtered.groupby("region").agg(
    total=("revenue", "sum"),
    avg=("score", "mean"),
    count=("id", "count"),
)
summary.to_parquet("output.parquet")
```

### Merge two DataFrames

```python
merged = pd.merge(orders, customers, on="customer_id", how="left")
```

### Reshape with pivot table

```python
pivot = df.pivot_table(values="sales", index="month", columns="category", aggfunc="sum")
```

### Time series resampling

```python
ts = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date")
daily = ts["price"].resample("D").mean()
```

## Advanced Topics

**Data Structures**: Series, DataFrame construction, attributes, dtypes, pandas 3.0 `str` default → [Data Structures](reference/01-data-structures.md)

**Indexing and Selection**: `.loc`/`.iloc`, boolean indexing, `query()`, slicing, `isin()` → [Indexing and Selection](reference/02-indexing-selection.md)

**Data Manipulation**: groupby, merge/join/concat, pivot/melt/stack, `pd.col()` expressions → [Data Manipulation](reference/03-data-manipulation.md)

**I/O Operations**: CSV, JSON, Parquet, Excel, SQL, Iceberg, ORC, Arrow PyCapsule Interface → [I/O Operations](reference/04-io-operations.md)

**Time Series**: Timestamps, DatetimeIndex, resampling, timezones, DateOffset, `date_range()` → [Time Series](reference/05-timeseries.md)

**Text and Strings**: `.str` accessor, `StringDtype` variants, pandas 3.0 string migration → [Text and Strings](reference/06-text-and-strings.md)

**Advanced Topics**: Copy-on-Write, PyArrow backend, windowing, visualization/Styler, performance, categorical data, missing data, UDFs → [Advanced Topics](reference/07-advanced-topics.md)
