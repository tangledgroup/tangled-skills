# Data Model

## Contents

- Arrays
- ChunkedArrays
- Record Batches
- Tables
- Schemas and Fields
- Nested Types
- Dictionary (Categorical) Arrays
- Union Arrays

## Arrays

`pyarrow.Array` is the fundamental atomic data structure — a contiguous columnar buffer of a single type. Arrays are immutable.

```python
import pyarrow as pa

# Type inference from Python values
arr = pa.array([1, 2, None, 3])  # Int64Array, null_count=1

# Explicit type
arr = pa.array([1, 2], type=pa.uint16())

# With mask (True = null)
import numpy as np
arr = pa.array([1, 2, 3, 4, 5], mask=np.array([True, False, True, False, True]))
# [null, 2, null, 4, null]
```

Key properties: `arr.type`, `len(arr)`, `arr.null_count`. Indexing returns `pyarrow.Scalar` values. Slicing (`arr[1:3]`) is zero-copy.

## ChunkedArrays

A `ChunkedArray` represents a logical column composed of multiple Array chunks. This occurs when data is read in batches or concatenated from multiple sources.

```python
table = pa.Table.from_batches([
    pa.RecordBatch.from_arrays([pa.array([1, 2])], names=["x"]),
    pa.RecordBatch.from_arrays([pa.array([3, 4, 5])], names=["x"]),
])
col = table["x"]  # ChunkedArray with 2 chunks
col.num_chunks  # 2
col.chunk(0)    # First chunk: Int64Array [1, 2]
```

Compute functions operate on ChunkedArrays transparently — no manual concatenation needed. Use `col.combine_chunks()` to merge into a single Array if required (copies data).

## Record Batches

A `RecordBatch` is a collection of equal-length Arrays with a Schema. It represents one contiguous row chunk.

```python
batch = pa.RecordBatch.from_arrays(
    [pa.array([1, 2, 3]), pa.array(["a", "b", "c"])],
    names=["x", "y"]
)
batch.num_rows   # 3
batch.num_columns  # 2
batch.schema     # x: int64, y: string

# Access columns by index or name
batch[0]              # First column as Array
batch.column("y")     # Named column

# Zero-copy slice
sliced = batch.slice(1, 2)  # rows 1-2
```

Record Batches are the unit of IPC streaming and Parquet row groups.

## Tables

`pyarrow.Table` is a logical table where each column is a ChunkedArray (multiple batches). It is not part of the Arrow specification but is a PyArrow convenience for wrangling multi-batch data.

```python
# From dict
table = pa.table({"name": ["Alice", "Bob"], "age": [30, 25]})

# From record batches
batches = [batch1, batch2, batch3]
table = pa.Table.from_batches(batches)

# Key properties
table.num_rows       # total rows across all chunks
table.num_columns    # number of columns
table.schema         # Schema
table.column_names   # list of names

# Column access (returns ChunkedArray)
table["name"]        # by name
table.column(0)      # by index

# Filtering with boolean mask
mask = pc.field("age") > 25
filtered = table.filter(mask)

# Selecting columns
subset = table.select(["name"])

# Adding a column
new_col = pa.array([1, 2])
table = table.append_column("score", new_col)

# Replacing a column
table = table.set_column(0, "age", pa.array([31, 26]))

# Concatenating tables (schemas must match)
combined = pa.concat_tables([table1, table2])

# Grouping and aggregation
result = table.group_by("name").aggregate([
    ("age", "mean"),
    ("age", "max"),
])

# Sorting
sorted_table = table.sort_by([("age", "descending")])

# Joins
joined = table1.join(table2, keys="id", join_type="inner")
```

Supported join types: `left outer` (default), `right outer`, `inner`, `full outer`, `left semi`, `right semi`, `left anti`, `right anti`.

## Schemas and Fields

A `Schema` defines column names, types, and optional metadata. Schemas are immutable.

```python
# Create schema
schema = pa.schema([
    ("name", pa.string()),
    ("age", pa.int32()),
    ("scores", pa.list_(pa.float64())),
])

# Create a Field (named type with optional metadata)
field = pa.field("temperature", pa.float64(), nullable=True,
                 metadata={"unit": "celsius"})

# Modify schema (creates new schema, does not mutate)
updated = schema.set(1, pa.field("age", pa.int64()))

# Schema comparison
schema1.equals(schema2)           # exact match
pa.unify_schemas([schema1, schema2])  # find common superset
```

Schema and field metadata are key-value maps stored as bytes (`{b'key': b'value'}`). Metadata is preserved through IPC serialization.

```python
# Set schema-level metadata
table = table.replace_schema_metadata({b"source": b"api"})

# Set field-level metadata
field = table.schema.field("x").with_metadata({b"unit": b"meters"})
```

## Nested Types

Arrow supports nested data structures for complex data:

### List Arrays

```python
# Inferred from Python lists
arr = pa.array([[1, 2], None, [3], []])
print(arr.type)  # list<item: int64>

# Explicit type
arr = pa.array([[1, 2], [3]], type=pa.list_(pa.int32()))
```

### ListView Arrays

ListView arrays store both offsets and sizes buffers, allowing out-of-order element access:

```python
values = [1, 2, 3, 4, 5, 6]
offsets = [4, 2, 0]
sizes = [2, 2, 2]
arr = pa.ListViewArray.from_arrays(offsets, sizes, values)
# [[5,6], [3,4], [1,2]]
```

### Struct Arrays

```python
# From dicts (schema inferred)
arr = pa.array([{"x": 1, "y": True}, {"z": 3.4, "x": 4}])

# Explicit schema
ty = pa.struct([("x", pa.int8()), ("y", pa.bool_())])
arr = pa.array([{"x": 1, "y": True}], type=ty)

# From component arrays (zero-copy)
xs = pa.array([5, 6, 7], type=pa.int16())
ys = pa.array([False, True, True])
arr = pa.StructArray.from_arrays((xs, ys), names=("x", "y"))
```

### Map Arrays

```python
data = [[("x", 1), ("y", 0)], [("a", 2), ("b", 45)]]
ty = pa.map_(pa.string(), pa.int64())
arr = pa.array(data, type=ty)

# Access flattened keys and items
arr.keys   # ["x", "y", "a", "b"]
arr.items  # [1, 0, 2, 45]
```

## Dictionary (Categorical) Arrays

Dictionary encoding stores integer indices referencing a shared dictionary of distinct values. Saves memory for low-cardinality string columns.

```python
indices = pa.array([0, 1, 0, 1, 2, None])
dictionary = pa.array(["foo", "bar", "baz"])
dict_arr = pa.DictionaryArray.from_arrays(indices, dictionary)

print(dict_arr.type)  # dictionary<values=string, indices=int64>
dict_arr.dictionary   # The distinct values array
dict_arr.indices      # The index array

# Converts to pandas.Categorical
dict_arr.to_pandas()
```

## Union Arrays

Union types represent values that can be one of several possible types. Two storage modes:

```python
# Sparse union — each child array has full length
xs = pa.array([5, 6, 7])
ys = pa.array([False, False, True])
types = pa.array([0, 1, 1], type=pa.int8())
union = pa.UnionArray.from_sparse(types, [xs, ys])

# Dense union — includes value offsets for compact storage
types = pa.array([0, 1, 1, 0], type=pa.int8())
offsets = pa.array([0, 0, 1, 1], type=pa.int32())
union = pa.UnionArray.from_dense(types, offsets, [xs, ys])
```
