---
name: pyarrow-24-0-0
description: "Complete toolkit for PyArrow 24.0.0 providing columnar in-memory data structures, vectorized compute functions, Parquet/CSV/ORC/JSON file I/O, Pandas and NumPy zero-copy integration, IPC serialization, tabular datasets, and Arrow Flight RPC. Use when building Python data pipelines, converting between Pandas/NumPy/Arrow formats, reading or writing Parquet files, performing vectorized array computations, serializing data via IPC, or working with partitioned datasets."
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - pyarrow
  - arrow
  - columnar
  - parquet
  - data-pipeline
  - numpy
  - pandas
category: library
external_references:
  - https://github.com/apache/arrow/tree/apache-arrow-24.0.0/python
  - https://arrow.apache.org/docs/python/
  - https://arrow.apache.org/cookbook/py/
---

# PyArrow 24.0.0

## Overview

PyArrow is the Python binding for Apache Arrow, a cross-language development platform for in-memory columnar data. It provides zero-copy memory sharing between processes and languages, high-performance file I/O (Parquet, CSV, JSON, ORC, Feather), vectorized compute functions, and seamless integration with Pandas, NumPy, and the broader Python data ecosystem.

PyArrow 24.0.0 supports Python 3.10 through 3.14. Install with `pip install pyarrow` or `conda install -c conda-forge pyarrow`.

## When to Use

- Creating columnar in-memory data structures (Arrays, Tables, RecordBatches)
- Reading or writing Parquet, CSV, JSON, ORC, or Feather files
- Converting between Pandas DataFrames and Arrow Tables with zero-copy semantics
- Performing vectorized computations on arrays (aggregations, filtering, string ops)
- Serializing data via Arrow IPC format for cross-process or cross-language exchange
- Working with large partitioned datasets using the `pyarrow.dataset` API
- Building or consuming Arrow Flight RPC services

## Core Concepts

### Columnar Memory Layout

Arrow stores data in contiguous columnar buffers. Each column is a single type, enabling cache-efficient vectorized operations. Data is immutable — slices and views share memory without copying.

### Key Abstractions

| Class | Description |
|---|---|
| `pyarrow.Array` | Atomic, contiguous columnar data of a single type |
| `pyarrow.ChunkedArray` | Logical column composed of multiple Array chunks (from batched reads) |
| `pyarrow.RecordBatch` | Collection of equal-length Arrays with a Schema (one row chunk) |
| `pyarrow.Table` | Logical table where each column is a ChunkedArray (multiple batches) |
| `pyarrow.Schema` | Named collection of types defining Table/RecordBatch structure |

### Type System

Arrow defines language-agnostic data types created via factory functions:

- **Primitive**: `pa.int8()`, `pa.int16()`, `pa.int32()`, `pa.int64()`, `pa.uint*()`, `pa.float16()`, `pa.float32()`, `pa.float64()`, `pa.bool_()`
- **Temporal**: `pa.date32()`, `pa.date64()`, `pa.time32()`, `pa.time64()`, `pa.timestamp('ms')`, `pa.duration('s')`
- **Binary/String**: `pa.binary()`, `pa.string()` (alias `pa.utf8()`), `pa.large_binary()`, `pa.large_string()`
- **Decimal**: `pa.decimal128(precision, scale)`, `pa.decimal256(10, 2)`
- **Nested**: `pa.list_(value_type)`, `pa.struct(fields)`, `pa.map_(key_type, item_type)`
- **Dictionary**: `pa.dictionary(index_type, value_type)` for categorical data

### Zero-Copy Philosophy

Arrow enables zero-copy data exchange. Slicing arrays, converting between Pandas and Arrow (when types align), and IPC deserialization all share underlying buffers without copying.

## Usage Examples

### Creating Arrays and Tables

```python
import pyarrow as pa

# Create an array (type inferred)
arr = pa.array([1, 2, None, 3])  # Int64Array with 1 null

# Explicit type
arr = pa.array([1, 2], type=pa.uint16())

# Create a table from named columns
table = pa.table({
    "name": ["Alice", "Bob", "Eve"],
    "age": [30, 25, 35],
})

# Create a table from arrays with explicit names
days = pa.array([1, 12, 17], type=pa.int8())
months = pa.array([1, 3, 5], type=pa.int8())
table = pa.table([days, months], names=["days", "months"])
```

### Converting with Pandas

```python
import pandas as pd
import pyarrow as pa

# Pandas DataFrame -> Arrow Table (zero-copy when possible)
df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
table = pa.Table.from_pandas(df)

# Arrow Table -> Pandas DataFrame
df_back = table.to_pandas()

# Control index preservation
table_no_index = pa.Table.from_pandas(df, preserve_index=False)
```

### Reading and Writing Parquet

```python
import pyarrow.parquet as pq

# Write a table to Parquet
pq.write_table(table, "data.parquet")

# Read back (full table)
table = pq.read_table("data.parquet")

# Read specific columns only
table = pq.read_table("data.parquet", columns=["name", "age"])

# Read with predicate pushdown filter
import pyarrow.compute as pc
table = pq.read_table("data.parquet",
                      filter=pc.field("age") > 25)
```

### Compute Functions

```python
import pyarrow.compute as pc

# Aggregate
pc.sum(pa.array([1, 2, 3, 4]))  # Int64Scalar: 10

# Element-wise
pc.multiply(pa.array([1, 2]), pa.array([10, 20]))  # [10, 40]

# String operations
pc.upper(pa.array(["hello", "world"]))  # ["HELLO", "WORLD"]

# Value counts
pc.value_counts(pa.array(["a", "a", "b"]))
```

## Advanced Topics

**Data Model**: Arrays, ChunkedArrays, Tables, RecordBatches, Schemas, and nested types → [Data Model](reference/01-data-model.md)

**Compute Functions**: Vectorized compute API, function catalog, grouped aggregations, joins → [Compute Functions](reference/02-compute-functions.md)

**File Formats**: Parquet, CSV, JSON, ORC, Feather read/write with options → [File Formats](reference/03-file-formats.md)

**Integration**: NumPy, Pandas, DLPack, and Dataframe Interchange Protocol → [Integration](reference/04-integration.md)

**IPC and Memory**: Serialization, streaming, memory pools, buffer management → [IPC and Memory](reference/05-ipc-and-memory.md)

**Datasets**: TabularDataset API, partitioned data, filesystems (S3, GCS, HDFS) → [Datasets](reference/06-datasets.md)

**Advanced Topics**: Arrow Flight RPC, extension types, CUDA, C++/Cython interop → [Advanced Topics](reference/07-advanced-topics.md)
