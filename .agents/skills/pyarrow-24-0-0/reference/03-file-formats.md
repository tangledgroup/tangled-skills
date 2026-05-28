# File Formats

## Contents

- Parquet
- CSV
- JSON
- ORC
- Feather

## Parquet

Parquet is the primary columnar storage format for Arrow data. Import via `pyarrow.parquet` (conventionally as `pq`).

### Writing

```python
import pyarrow.parquet as pq
import pyarrow as pa

table = pa.table({"name": ["Alice", "Bob"], "age": [30, 25]})

# Basic write
pq.write_table(table, "data.parquet")

# With options
pq.write_table(table, "data.parquet",
    compression="snappy",        # snappy, gzip, zstd, none
    compression_level=6,
    use_dictionary=True,         # dictionary encode string columns
    write_statistics=True,       # write min/max/null_count stats
    row_group_size=128*1024,     # rows per row group
    data_page_size=1024*1024,    # ~1MB page size
    version="2.6",               # "1.0" for older readers
)
```

### Reading

```python
# Full read
table = pq.read_table("data.parquet")

# Read specific columns (skips unread columns on disk)
table = pq.read_table("data.parquet", columns=["name", "age"])

# Predicate pushdown filter (filters at row-group level)
import pyarrow.compute as pc
table = pq.read_table("data.parquet",
    filter=pc.field("age") > 25
)

# Memory map for large files
table = pq.read_table("data.parquet", memory_map=True)

# Read as Pandas (preserves index metadata)
df = pq.read_pandas("data.parquet", columns=["name"]).to_pandas()
```

### Fine-Grained Access

```python
# Inspect file metadata
pf = pq.ParquetFile("data.parquet")
pf.metadata           # FileMetaData: num_rows, num_row_groups, etc.
pf.schema             # ParquetSchema
pf.num_row_groups     # number of row groups

# Read individual row group
batch = pf.read_row_group(0)

# Read metadata only (no data decompression)
metadata = pq.read_metadata("data.parquet")

# Write multiple row groups
with pq.ParquetWriter("multi.parquet", table.schema) as writer:
    for batch in batches:
        writer.write_batch(batch)
```

### Partitioned Datasets

```python
# Write partitioned dataset
table = pa.table({
    "a": range(10),
    "part": ["x"] * 5 + ["y"] * 5,
})
pq.write_to_dataset(table, "partitioned_dir", partition_cols=["part"])

# Creates: partitioned_dir/part=x/*.parquet, partitioned_dir/part=y/*.parquet
```

## CSV

CSV support via `pyarrow.csv` module. Supports multi-threaded reading and automatic decompression (`.gz`, `.bz2`, etc.).

### Reading

```python
from pyarrow import csv

# Basic read (auto type inference)
table = csv.read_csv("data.csv")

# Compressed file (auto-detected by extension)
table = csv.read_csv("data.csv.gz")

# Custom parse options
table = csv.read_csv("data.csv",
    parse_options=csv.ParseOptions(
        delimiter=";",
        skip_rows_after_header=0,
        has_column_names=True,
    ),
    read_options=csv.ReadOptions(
        column_names=["a", "b", "c"],  # override header names
        skip_rows=1,                     # skip first row
    ),
    convert_options=csv.ConvertOptions(
        types={"a": pa.int32()},        # force column types
        include_columns=["a", "b"],     # select columns
        null_values=["NA", ""],         # additional null sentinels
    ),
)
```

### Writing

```python
# Basic write
csv.write_csv(table, "output.csv")

# Compressed output
with pa.CompressedOutputStream("output.csv.gz", "gzip") as out:
    csv.write_csv(table, out)

# Custom write options
csv.write_csv(table, "output.csv",
    write_options=csv.WriteOptions(
        delimiter=";",
        include_header=True,
    ),
)
```

## JSON

Reads line-delimited JSON (one JSON object per line). Import via `pyarrow.json`.

```python
from pyarrow import json

# Basic read (auto type inference)
table = json.read_json("data.json")

# With explicit schema
schema = pa.schema([("name", pa.string()), ("age", pa.int32())])
table = json.read_json("data.json", schema=schema)

# JSONLines format
table = json.read_json("data.jsonl")
```

## ORC

Apache ORC format support. Import via `pyarrow.orc`.

```python
import pyarrow.orc as orc

# Read ORC file
table = orc.read_orc("data.orc")

# Read specific columns
table = orc.read_orc("data.orc", columns=["name", "age"])

# Write ORC file
orc.write_orc(table, "output.orc")

# Inspect metadata
reader = orc.OrcReader("data.orc")
reader.schema
reader.num_rows
```

## Feather

Feather is Arrow's native binary format (IPC file format wrapped in a convenient API). Fastest read/write for Arrow data.

```python
import pyarrow.feather as feather

# Write
feather.write_feather(table, "data.feather",
    compression="lz4",     # lz4, zstd, or None
    compression_level=1,
)

# Read
table = feather.read_feather("data.feather")

# Read specific columns
table = feather.read_feather("data.feather", columns=["name"])

# Read specific rows
table = feather.read_feather("data.feather",
    use_threads=True,
)
```
