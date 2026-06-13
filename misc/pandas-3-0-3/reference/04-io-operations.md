# I/O Operations

## Contents
- CSV and Text Files
- JSON
- Parquet
- Excel
- SQL
- Other Formats (Iceberg, ORC, Feather, HDF5)
- Arrow PyCapsule Interface

pandas provides `read_*` functions to load data and `to_*` methods to write it.

## CSV and Text Files

```python
# Read CSV
df = pd.read_csv("data.csv")

# Common options
df = pd.read_csv(
    "data.csv",
    sep=";",                 # delimiter
    header=0,                # row number for column names
    index_col="id",          # column to use as index
    dtype={"name": "str"},   # explicit dtypes
    parse_dates=["date"],    # auto-parse date columns
    na_values=["NA", ""],    # additional NA markers
    usecols=["a", "b"],      # only read specific columns
)

# Write CSV
df.to_csv("out.csv", index=False)

# Float formatting
df.to_csv("out.csv", float_format="{:.2f}")
```

### Chunked Reading for Large Files

```python
for chunk in pd.read_csv("large.csv", chunksize=100_000):
    process(chunk)
```

## JSON

```python
# Read JSON (records format by default)
df = pd.read_json("data.json")

# Lines-delimited JSON
df = pd.read_json("data.jsonl", lines=True)

# Write JSON
df.to_json("out.json", orient="records")
df.to_json("out.jsonl", orient="records", lines=True)
```

## Parquet

Parquet is the recommended format for efficient storage and interchange. Requires `pyarrow` or `fastparquet`.

```python
# Read Parquet
df = pd.read_parquet("data.parquet")

# With PyArrow conversion options
df = pd.read_parquet("data.parquet", to_pandas_kwargs={"maps_as_pydicts": True})

# Write Parquet
df.to_parquet("data.parquet", engine="pyarrow")
```

## Excel

Requires `openpyxl` (`.xlsx`) or `xlrd` (`.xls`).

```python
# Read Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# Multiple sheets
sheets = pd.read_excel("data.xlsx", sheet_name=None)  # dict of DataFrames

# Write Excel
df.to_excel("out.xlsx", index=False, merge_cells="columns")

# With autofilter
df.to_excel("out.xlsx", autofilter=True)
```

## SQL

Works with any SQLAlchemy-compatible database.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data.db")

# Read SQL query
df = pd.read_sql("SELECT * FROM table WHERE active = 1", engine)

# Read table
df = pd.read_sql_table("my_table", engine)

# Write to SQL
df.to_sql("my_table", engine, if_exists="append", index=False)

# Replace all rows
df.to_sql("my_table", engine, if_exists="delete_rows", index=False)
```

## Other Formats

### Iceberg

```python
df = pd.read_iceberg("s3://bucket/table")
df.to_iceberg("s3://bucket/table")
```

### ORC

```python
df = pd.read_orc("data.orc")
df.to_orc("data.orc")
```

### Feather

```python
df.to_feather("data.feather")
df = pd.read_feather("data.feather")
```

### HDF5 (PyTables)

```python
df.to_hdf("data.h5", key="df")
df = pd.read_hdf("data.h5", key="df")
```

### Pickle / msgpack

```python
df.to_pickle("data.pkl")
df = pd.read_pickle("data.pkl")
```

## Arrow PyCapsule Interface

pandas 3.0 supports the Arrow PyCapsule Interface for zero-copy data exchange with other Arrow-compatible libraries (polars, cuDF, etc.).

```python
# Import from any Arrow-compatible object
df = pd.DataFrame.from_arrow(pyarrow_table)
s = pd.Series.from_arrow(pyarrow_array)

# Export via __arrow_c_stream__
arrow_obj = df.__arrow_c_stream__()
```

This enables seamless interoperability between pandas and other DataFrame libraries without serialization overhead.
