# Integration

## Contents

- NumPy Integration
- Pandas Integration
- DLPack Protocol
- Dataframe Interchange Protocol
- PyCapsule Interface

## NumPy Integration

Arrow provides zero-copy conversion between NumPy arrays and Arrow Arrays when the data layout is compatible.

```python
import pyarrow as pa
import numpy as np

# NumPy -> Arrow (zero-copy for contiguous C/F-order arrays)
np_arr = np.array([1, 2, 3, 4], dtype=np.int64)
arr = pa.array(np_arr)

# Arrow -> NumPy
np_back = arr.to_numpy()

# Zero-copy check
np_back = arr.to_numpy(zero_copy_only=True)  # raises if copy needed

# From pandas Series
import pandas as pd
arr = pa.array(pd.Series([1, 2, 3]))
```

### Type Mapping (NumPy -> Arrow)

| NumPy dtype | Arrow type |
|---|---|
| `bool` | `bool_` |
| `int8/16/32/64` | `int8/16/32/64` |
| `uint8/16/32/64` | `uint8/16/32/64` |
| `float16/32/64` | `float16/32/64` |
| `datetime64[ns]` | `timestamp[ns]` |
| `timedelta64[ns]` | `duration[ns]` |
| `object` (strings) | `string` |
| `bytes` | `binary` |

Zero-copy works when the NumPy array is contiguous and the dtype maps directly. Multi-dimensional arrays require flattening or use `RecordBatch.to_tensor()` for column-major tensor conversion.

## Pandas Integration

Arrow Tables are the equivalent of Pandas DataFrames. Both consist of named columns of equal length, but Arrow additionally supports nested columns.

### Conversion

```python
import pyarrow as pa
import pandas as pd

# DataFrame -> Table
df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
table = pa.Table.from_pandas(df)

# Table -> DataFrame
df_back = table.to_pandas()

# Infer schema from pandas
schema = pa.Schema.from_pandas(df)
```

### Index Preservation

The `preserve_index` option controls how the pandas index is handled:

```python
# Default: RangeIndex stored as metadata, other indexes as data columns
table = pa.Table.from_pandas(df)

# Don't store index at all
table = pa.Table.from_pandas(df, preserve_index=False)

# Force all index data into physical columns
table = pa.Table.from_pandas(df, preserve_index=True)
```

### Type Mapping (Pandas -> Arrow)

| Pandas type | Arrow type |
|---|---|
| `bool` | `BOOL` |
| `(u)int{8,16,32,64}` | `(U)INT{8,16,32,64}` |
| `float32/64` | `FLOAT/DLDOUBLE` |
| `str` / `unicode` | `STRING` |
| `pd.Categorical` | `DICTIONARY` |
| `pd.Timestamp` | `TIMESTAMP(ns)` |
| `datetime.date` | `DATE` |

### to_pandas() Options

```python
# Custom type mapper for specific columns
df = table.to_pandas(types_mapper=pd.Int64Dtype)

# Date unit control
df = table.to_pandas(date_unit="s")  # seconds instead of nanoseconds

# Safe conversion (raise on data loss)
df = table.to_pandas(self_destruct=False)
```

### Series Conversion

```python
# Series -> Array
series = pd.Series([1, 2, None, 4])
arr = pa.Array.from_pandas(series)

# With explicit null mask
arr = pa.array([1, 2, 3, 4], mask=np.array([False, False, True, False]))
```

## DLPack Protocol

DLPack enables zero-copy tensor exchange between Arrow and GPU frameworks (CuPy, PyTorch, etc.).

```python
import pyarrow as pa

# RecordBatch -> DLPack tensor (column-major)
batch = pa.RecordBatch.from_arrays(
    [pa.array([1.0, 2.0, 3.0]), pa.array([4.0, 5.0, 6.0])],
    names=["x", "y"]
)
tensor = batch.to_tensor()

# DLPack tensor -> RecordBatch
batch_back = pa.RecordBatch.from_tensor(tensor, names=["x", "y"])
```

Only numeric types (integers and floats) are supported. Only column-major layout is available.

## Dataframe Interchange Protocol

Arrow Tables support the `__dataframe__` protocol, enabling interchange with any library implementing the protocol (Polars, cuDF, etc.).

```python
import pyarrow as pa

table = pa.table({"x": [1, 2, 3], "y": ["a", "b", "c"]})

# Export via interchange protocol
interchange = table.__dataframe__()

# Consume interchange protocol
import pyarrow.interchange as pai
table_from_interchange = pai.from_dataframe(other_lib_df)
```

## PyCapsule Interface

The Arrow PyCapsule Interface enables zero-copy data exchange between any Python libraries supporting the C Data Interface.

### Implementing the Protocol

```python
class MyArray:
    def __arrow_c_array__(self):
        # Return PyCapsule with Arrow array data
        ...

    def __arrow_c_stream__(self):
        # Return PyCapsule for chunked/streaming data
        ...
```

### Consuming with PyArrow

PyArrow constructors automatically detect and consume PyCapsule-compatible objects:

| Target | Constructor | Protocol |
|---|---|---|
| `Array` | `pa.array()` | `__arrow_c_array__` |
| `ChunkedArray` | `pa.chunked_array()` | `__arrow_c_array__`, `__arrow_c_stream__` |
| `RecordBatch` | `pa.record_batch()` | `__arrow_c_array__` |
| `Table` | `pa.table()` | `__arrow_c_array__`, `__arrow_c_stream__` |
| `Schema` | `pa.schema()` | `__arrow_c_schema__` |

### Legacy `__arrow_array__` Protocol

For simpler array conversion, implement `__arrow_array__`:

```python
class MyDuckArray:
    def __arrow_array__(self, type=None):
        return pa.array(self.data, type=type)
```

The `type` parameter is passed through from `pa.array()`. Return either an `Array` or `ChunkedArray`.
