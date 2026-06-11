# LazyFrame and Lazy API

## Contents

- Lazy evaluation model
- Scanning vs reading
- Query optimizations
- Inspecting the query plan
- Schema inference
- Execution control
- Sources and sinks

## Lazy Evaluation Model

The Lazy API defers computation until `.collect()` is called. Operations build a logical query plan that Polars optimizes before execution:

```python
import polars as pl

# Build query plan (no data loaded yet)
lf = (
    pl.scan_csv("large_file.csv")
    .filter(pl.col("status") == "active")
    .select(["user_id", "amount"])
    .group_by("user_id")
    .agg(pl.col("amount").sum())
    .sort("amount", descending=True)
    .head(100)
)

# Execute optimized plan
df = lf.collect()
```

## Scanning vs Reading

Use *scan* functions for lazy loading. They read metadata only and defer full data access:

| Eager (immediate) | Lazy (deferred) |
| --- | --- |
| `pl.read_csv()` | `pl.scan_csv()` |
| `pl.read_parquet()` | `pl.scan_parquet()` |
| `pl.read_json()` | `pl.scan_ndjson()` |
| `pl.read_excel()` | — (use eager read, then `.lazy()`) |

Scanning supports glob patterns for multi-file operations:

```python
lf = pl.scan_parquet("data/2024-*/part-*.parquet")
```

## Query Optimizations

Polars automatically applies these optimizations to lazy queries:

| Optimization | Description |
| --- | --- |
| **Predicate pushdown** | Filters applied at scan level, before other operations |
| **Projection pushdown** | Only needed columns read from source |
| **Slice pushdown** | `head()`/`tail()` pushed to scan level |
| **Common subplan elimination** | Shared subqueries cached and reused |
| **Simplify expressions** | Constant folding, expensive-to-cheap replacements |
| **Join ordering** | Reorders join branches to minimize intermediate size |
| **Type coercion** | Minimal memory type selection for operations |
| **Cardinality estimation** | Determines optimal group-by strategy |

Control optimizations with `collect()`:

```python
df = lf.collect(
    optimization_toggle=pl.QueryOptFlags().with_predicate_pushdown(False),
)
```

## Inspecting the Query Plan

```python
lf = pl.scan_csv("data.csv").filter(pl.col("x") > 10).select(["a", "b"])

# Text representation of logical plan
print(lf.explain())

# Optimized physical plan
print(lf.explain(optimized=True))

# Visualize as graph (requires 'graph' feature)
lf.show_graph()
```

## Schema Inference

LazyFrames infer schema without executing the full query:

```python
lf = pl.scan_parquet("data/*.parquet")
print(lf.collect_schema())
# {'id': Int64, 'name': String, 'created_at': Datetime('us', None)}

# DataType expressions for conditional column selection
lf.select(pl.col_by_dtype(pl.Int64))
lf.select(pl.col_by_dtype(pl.Temporal))
```

## Execution Control

### Collect options

```python
df = lf.collect(
    streaming=False,           # in-memory execution (default)
    background=False,          # return immediately with InProcessQuery
    optimize=True,             # run optimizations (default)
    engine="cpu",              # "cpu" | "streaming" | "gpu"
)

# Async collection (requires 'async' feature)
df = lf.collect_async()
```

### Multiprocessing

```python
# Use all available cores (default)
df = lf.collect()

# Limit parallelism
df = lf.collect(
    optimization_toggle=pl.QueryOptFlags(),
)

# Set global thread pool size
pl.Config().set_streaming_chunk_size(4_000_000)
```

### Profiling

```python
df, profile = lf.profile()

# Print timing for each operation in the query plan
print(profile)
```

## Sources and Sinks

Directly write query results to disk without materializing in memory:

```python
# Sink to Parquet
lf.sink_parquet("output/part-*.parquet")

# Sink to CSV
lf.sink_csv("output.csv")

# Sink to JSON
lf.sink_ndjson("output.jsonl")

# Sink to database (requires 'database' feature)
lf.sink_database(
    table="my_table",
    connection="postgresql://user:pass@host/db",
)
```

## With Context

Reference other LazyFrames within a query without joining:

```python
orders = pl.scan_csv("orders.csv")
products = pl.scan_csv("products.csv")

result = (
    orders
    .with_context([products])
    .select(
        pl.col("order_id"),
        pl.col("product_name"),  # from products context
    )
)
```
