---
name: polars-0-53-0
description: "Complete toolkit for Polars 0.53.0 providing high-performance DataFrame computing with lazy evaluation, expression-based API, streaming engine, GPU acceleration, and SQL interface. Covers data types, expressions, transformations (joins, pivots, window functions), IO (CSV, Parquet, JSON, Excel, databases, cloud storage), LazyFrame optimization, and streaming. Use when building Python data pipelines, ETL workflows, analytics queries, or migrating from pandas/Spark to Polars."
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - polars
  - dataframe
  - lazy-evaluation
  - expressions
  - streaming
  - gpu
  - etl
category: library
external_references:
  - https://github.com/pola-rs/polars/tree/rs-0.53.0
  - https://docs.pola.rs/api/python/stable/reference/index.html
  - https://docs.pola.rs/#example
---

# Polars 0.53.0

## Overview

Polars is a fast, multi-language DataFrame library built on Apache Arrow columnar format with a Rust core. It provides an expression-based API for data manipulation, lazy evaluation with automatic query optimization, streaming mode for out-of-core processing, GPU acceleration via RAPIDS cuDF, and SQL query support. Polars supports Python and Rust, with primary focus on the Python API.

Key differentiators from pandas: expressions are first-class (not column operations), lazy evaluation defers computation until `.collect()`, and the streaming engine handles datasets larger than RAM.

## When to Use

- Building data pipelines that require high-performance DataFrame operations
- Working with large datasets that exceed available memory (streaming mode)
- Migrating from pandas or Spark to a faster, expression-based alternative
- Needing SQL queries over in-memory DataFrames
- GPU-accelerated data processing on NVIDIA hardware
- ETL workflows involving CSV, Parquet, JSON, Excel, or database I/O
- Time-series analysis with rolling windows, resampling, and dynamic grouping

## Installation / Setup

```bash
# Core installation
pip install polars

# With optional features
pip install 'polars[numpy,pandas,pyarrow]'   # Interoperability
pip install 'polars[excel]'                   # Excel support
pip install 'polars[database]'                # Database I/O (ADBC, ConnectorX, SQLAlchemy)
pip install 'polars[fsspec]'                  # Cloud storage (S3, GCS, Azure Blob)
pip install 'polars[gpu]'                     # GPU acceleration (NVIDIA, CUDA 12+)
pip install 'polars[async]'                   # Async LazyFrame collection
pip install 'polars[all]'                     # All optional dependencies

# Big index (>4.3 billion rows)
pip install 'polars[rt64]'

# Legacy CPU without AVX2
pip install 'polars[rtcompat]'
```

Import convention:

```python
import polars as pl
```

## Core Concepts

### Expressions and Contexts

Expressions are the core abstraction in Polars. An expression describes a computation abstractly — it only materializes when evaluated inside a *context*:

```python
# Expression: abstract computation
expr = pl.col("weight") / (pl.col("height") ** 2)

# Contexts that evaluate expressions:
df.select(expr.alias("bmi"))              # select: produce new columns
df.with_columns(expr.alias("bmi"))        # with_columns: add to existing
df.filter(pl.col("age") > 30)             # filter: row predicate
df.group_by("city").agg(pl.col("age").mean())  # group_by: aggregation per group
```

### Eager vs Lazy API

- **Eager (`DataFrame`)**: operations execute immediately. Simple and intuitive for small datasets.
- **Lazy (`LazyFrame`)**: operations build a query plan that is optimized and executed on `.collect()`. Enables predicate pushdown, projection pushdown, slice pushdown, common subplan elimination, and other optimizations.

```python
# Eager
df = pl.read_csv("data.csv").filter(pl.col("x") > 10).select(["a", "b"])

# Lazy (preferred for complex queries)
lf = pl.scan_csv("data.csv").filter(pl.col("x") > 10).select(["a", "b"])
df = lf.collect()
```

### Streaming Mode

Process datasets larger than RAM by passing `engine="streaming"` to `.collect()`. Falls back to in-memory for unsupported operations.

```python
lf = pl.scan_parquet("large-data/*.parquet")
result = lf.group_by("category").agg(pl.col("value").mean()).collect(engine="streaming")
```

## Usage Examples

### Create and inspect a DataFrame

```python
import polars as pl
import datetime as dt

df = pl.DataFrame({
    "name": ["Alice", "Ben", "Chloe"],
    "age": [30, 25, 35],
    "score": [88.5, 92.1, 78.3],
})

print(df.schema)   # {'name': String, 'age': Int64, 'score': Float64}
print(df.shape)    # (3, 3)
df.glimpse()       # compact column overview
```

### Filter, select, and compute derived columns

```python
result = df.filter(pl.col("age") >= 28).select(
    pl.col("name"),
    (pl.col("score") * 1.1).alias("adjusted_score"),
)
```

### Group-by aggregation

```python
summary = (
    df.group_by("department")
    .agg(
        pl.col("salary").mean().alias("avg_salary"),
        pl.col("salary").sum().alias("total_salary"),
        pl.col("employee_id").count().alias("headcount"),
    )
    .sort("total_salary", descending=True)
)
```

### Join two DataFrames

```python
orders = pl.DataFrame({"order_id": [1, 2, 3], "customer_id": [10, 20, 10]})
customers = pl.DataFrame({"customer_id": [10, 20], "name": ["Alice", "Ben"]})

joined = orders.join(customers, on="customer_id", how="left")
```

### Read and write Parquet (recommended format)

```python
# Read
df = pl.read_parquet("data.parquet")

# Scan lazily (lazy API preferred for large files)
lf = pl.scan_parquet("data/*.parquet")

# Write
df.write_parquet("output.parquet", compression="zstd")
```

## Advanced Topics

**Data Types and Schema**: Full type system including physical/logical types, Struct, List, Array, Categorical, Enum → [Data Types](reference/01-data-types.md)

**Expressions Deep Dive**: Expression syntax, contexts, expansion, conditionals, folds, user-defined functions → [Expressions](reference/02-expressions.md)

**DataFrame API Reference**: Construction, manipulation, selection, aggregation, export methods → [DataFrame API](reference/03-dataframe-api.md)

**LazyFrame and Lazy API**: Lazy evaluation, query plan inspection, optimizations, schema inference, execution control → [LazyFrame and Lazy API](reference/04-lazyframe-and-lazy-api.md)

**Input/Output Operations**: CSV, Parquet, JSON, Excel, databases, cloud storage, Arrow IPC, multiple file scanning → [IO](reference/05-io.md)

**Data Transformations**: Joins (inner, left, right, full, semi, anti, asof), concatenation, pivots, unpivots, melt, explode → [Transformations](reference/06-transformations.md)

**SQL and Advanced Queries**: SQLContext, SQL queries over DataFrames, CTEs, window functions, rolling/dynamic group-by → [SQL and Advanced Queries](reference/07-sql-and-advanced-queries.md)

**Streaming, GPU, and Performance**: Streaming engine, GPU acceleration via cuDF, multiprocessing, profiling, optimization flags → [Streaming and Performance](reference/08-streaming-and-performance.md)
