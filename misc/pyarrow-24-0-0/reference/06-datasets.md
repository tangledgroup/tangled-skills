# Datasets

## Contents

- Dataset API Overview
- Reading Datasets
- Filtering and Projection
- Partitioned Datasets
- Writing Datasets
- Filesystems (Local, S3, GCS, HDFS)

## Dataset API Overview

The `pyarrow.dataset` module provides a unified interface for working with multi-file, potentially larger-than-memory tabular datasets. Supports Parquet, CSV, ORC, and Feather/Arrow IPC formats across local and cloud filesystems.

```python
import pyarrow.dataset as ds
import pyarrow as pa

# Create dataset from directory
dataset = ds.dataset("data_dir/", format="parquet")

# List files
dataset.files  # ['data_dir/part-0.parquet', ...]

# Schema (inferred from first file by default)
print(dataset.schema)

# Read entire dataset
table = dataset.to_table()

# Iterate in batches (memory efficient)
for batch in dataset.to_batches():
    process(batch)
```

## Reading Datasets

### Discovery

`ds.dataset()` accepts a directory path, single file, or list of files. It crawls the directory to find data files without reading their contents.

```python
# From directory
dataset = ds.dataset("data_dir/", format="parquet")

# From single file
dataset = ds.dataset("data.parquet", format="parquet")

# From file list
dataset = ds.dataset(["a.parquet", "b.parquet"], format="parquet")

# Custom file format options
parquet_format = ds.ParquetFileFormat(read_options={"dictionary_columns": ["col"]})
dataset = ds.dataset("data_dir/", format=parquet_format)
```

### Reading Different Formats

```python
ds.dataset("dir/", format="parquet")
ds.dataset("dir/", format="csv")
ds.dataset("dir/", format="orc")
ds.dataset("dir/", format="feather")
```

## Filtering and Projection

### Column Selection

```python
# Read specific columns
table = dataset.to_table(columns=["a", "b"])
```

### Row Filtering

Use `ds.field()` to build filter expressions. Filters are pushed down to the file level, skipping unread row groups.

```python
# Simple filter
table = dataset.to_table(filter=ds.field("age") >= 25)

# Set membership
table = dataset.to_table(filter=ds.field("status").isin(["active", "pending"]))

# Combined filters (use &, |, ~ — NOT and/or/not)
filter_expr = (ds.field("age") > 18) & (ds.field("country") == "US")
table = dataset.to_table(filter=filter_expr)

# Cross-column comparison
table = dataset.to_table(filter=ds.field("a") > ds.field("b"))
```

### Column Projection with Expressions

Derive new columns during scan:

```python
projection = {
    "a_renamed": ds.field("a"),
    "b_as_float32": ds.field("b").cast("float32"),
    "is_large": ds.field("b") > 1,
}
table = dataset.to_table(columns=projection)

# Include all existing columns plus derived
projection = {col: ds.field(col) for col in dataset.schema.names}
projection["b_squared"] = ds.field("b") * 2
table = dataset.to_table(columns=projection)
```

## Partitioned Datasets

Partitioning organizes data into subdirectories by key values, enabling efficient filtering by skipping entire partitions.

### Hive-Style Partitioning

Directory names encode key-value pairs: `year=2023/month=01/data.parquet`.

```python
# Read with automatic hive partition detection
dataset = ds.dataset("partitioned_dir/", format="parquet", partitioning="hive")

# Explicit partition schema
part = ds.partitioning(
    pa.schema([("year", pa.int16()), ("month", pa.int8())]),
    flavor="hive"
)
dataset = ds.dataset("partitioned_dir/", format="parquet", partitioning=part)

# Filter on partition keys (skips non-matching files entirely)
table = dataset.to_table(filter=ds.field("year") == 2023)
```

### Directory Partitioning

Path segments represent values without key names: `2023/01/data.parquet`.

```python
part = ds.partitioning(field_names=["year", "month"])
dataset = ds.dataset("dir/", format="parquet", partitioning=part)
```

### Writing Partitioned Datasets

```python
import pyarrow.dataset as ds
import pyarrow.parquet as pq

table = pa.table({
    "a": range(10),
    "part": ["x"] * 5 + ["y"] * 5,
})

# Using Parquet helper
pq.write_to_dataset(table, "partitioned_dir", partition_cols=["part"])

# Using dataset API
ds.write_dataset(table, "output_dir/", format="parquet",
    partitioning=ds.partitioning(
        pa.schema([table.schema.field("part")])
    )
)
```

## Filesystems

PyArrow's filesystem abstraction enables reading from local and cloud storage uniformly.

### Local

```python
from pyarrow import fs

local = fs.LocalFileSystem()
dataset = ds.dataset("data_dir/", format="parquet", filesystem=local)
```

### S3 / S3-Compatible

```python
s3 = fs.S3FileSystem(region="us-east-1")
dataset = ds.dataset("my-bucket/data/", format="parquet", filesystem=s3)

# Or via URI (filesystem inferred)
dataset = ds.dataset("s3://my-bucket/data/")
```

### Google Cloud Storage

```python
gcs = fs.GcsFileSystem(project="my-project")
dataset = ds.dataset("gs://my-bucket/data/", filesystem=gcs)
```

### HDFS

```python
hdfs = fs.HadoopFileSystem(host="namenode", port=8020)
dataset = ds.dataset("hdfs:///data/", filesystem=hdfs)
```

### Azure

```python
azure = fs.AzureFileSystem(account_name="myaccount")
dataset = ds.dataset("container/data/", filesystem=azure)
```

### URI Inference

```python
filesystem, path = fs.FileSystem.from_uri("s3://bucket/path")
# filesystem is S3FileSystem, path is "bucket/path"
```

### fsspec Integration

Use any fsspec-compatible filesystem:

```python
fsspec_fs = my_fsspec_filesystem()
arrow_fs = fs.PyFileSystem(fsspec_fs)
dataset = ds.dataset("path/", format="parquet", filesystem=arrow_fs)
```
