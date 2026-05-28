# Streaming, GPU, and Performance

## Contents

- Streaming engine
- GPU acceleration
- Multiprocessing
- Profiling and debugging
- Optimization flags

## Streaming Engine

Process datasets larger than RAM by executing queries in batches. Activate with `engine="streaming"`:

```python
lf = pl.scan_parquet("large-dataset/*.parquet")

result = (
    lf
    .filter(pl.col("status") == "active")
    .group_by("category")
    .agg(pl.col("amount").mean())
    .collect(engine="streaming")
)
```

The streaming engine is also more performant than in-memory for many operations. It processes data in chunks, keeping memory usage bounded regardless of dataset size.

### Inspecting streaming execution

Some operations are inherently non-streaming and will fall back to in-memory. Inspect the physical plan to see which nodes run in streaming mode:

```python
lf.show_graph()  # visual graph showing streaming vs in-memory nodes
```

### Chunk size configuration

```python
with pl.Config() as cfg:
    cfg.set_streaming_chunk_size(4_000_000)  # rows per chunk
```

## GPU Acceleration

Polars supports NVIDIA GPU execution via RAPIDS cuDF (Open Beta). Only available in the Lazy API.

### Requirements

- NVIDIA GPU with compute capability 7.0+ (Volta or higher)
- CUDA 12 (CUDA 11 support ends with RAPIDS v25.06)
- Linux or WSL2

### Installation and usage

```bash
pip install polars[gpu]
```

```python
import polars as pl

lf = pl.scan_parquet("data/*.parquet")

# Basic GPU execution
result = lf.filter(pl.col("x") > 10).collect(engine="gpu")

# Specify GPU device on multi-GPU systems
result = lf.collect(engine=pl.GPUEngine(device=1))
```

### Supported on GPU

- LazyFrame API operations
- SQL queries
- I/O from CSV, Parquet, NDJSON
- Numeric, logical, string, and datetime types
- String processing
- Aggregations (grouped and rolling)
- Joins, filters, concatenation
- Missing data handling

### Not supported on GPU

- Eager DataFrame API
- Streaming mode
- Date, Categorical, Enum, Time, Array, Binary, Object types
- Datetime with timezone, List types
- Time-series resampling
- Folds
- User-defined functions
- Excel and database I/O

### CPU fallback

By default, unsupported queries fall back to CPU execution with a `PerformanceWarning` in verbose mode:

```python
with pl.Config() as cfg:
    cfg.set_verbose(True)
    result = lf.collect(engine="gpu")
```

Disable fallback to raise on unsupported operations:

```python
result = lf.collect(engine=pl.GPUEngine(raise_on_fail=True))
```

### When to use GPU

GPU acceleration provides the most benefit for workflows dominated by grouped aggregations and joins. I/O-bound queries show similar performance. GPUs typically have less memory than CPU systems — datasets of 50–100 GiB fit well on GPUs with 80 GiB VRAM.

## Multiprocessing

Polars uses a thread pool for parallel execution by default:

```python
# Default: uses all available cores
df = lf.collect()

# Control via environment variable
import os
os.environ["POLARS_MAX_THREADS"] = "8"
```

Streaming mode automatically parallelizes across chunks.

## Profiling and Debugging

### Query profiling

Measure time spent in each operation:

```python
df, profile = lf.profile()
print(profile)
# Shows operation name, start time, end time, duration
```

### Explaining the plan

```python
# Logical plan (before optimization)
print(lf.explain(optimized=False))

# Physical plan (after optimization)
print(lf.explain(optimized=True))
```

### Inspect intermediate results

```python
lf.inspect()  # prints DataFrame at this point in the chain
```

## Optimization Flags

Fine-tune query optimizations:

```python
from polars import QueryOptFlags

flags = QueryOptFlags()

# Disable specific optimizations
flags = flags.with_predicate_pushdown(False)
flags = flags.with_projection_pushdown(False)
flags = flags.with_slice_pushdown(False)
flags = flags.with_common_subplan_elimination(False)

df = lf.collect(optimization_toggle=flags)
```

### Cache repeated subqueries

Mark a LazyFrame for caching to avoid recomputation:

```python
base = pl.scan_parquet("data.parquet").cache()

result1 = base.filter(pl.col("x") > 0).select(["a"])
result2 = base.filter(pl.col("y") < 100).select(["b"])
```

### Collect batches

Iterate over results in batches instead of collecting all at once:

```python
query_result = lf.collect_batches()
for batch_df in query_result:
    process(batch_df)
```
