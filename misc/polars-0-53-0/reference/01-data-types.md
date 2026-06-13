# Data Types and Schema

## Contents

- Primitive types
- Logical and physical types
- Struct, List, Array
- Categorical and Enum
- Schema inspection and manipulation
- Type casting

## Primitive Types

Polars supports a comprehensive type system backed by Apache Arrow:

| Category | Types |
| --- | --- |
| Boolean | `Boolean` |
| Integer (signed) | `Int8`, `Int16`, `Int32`, `Int64`, `Int128` |
| Integer (unsigned) | `UInt8`, `UInt16`, `UInt32`, `UInt64` |
| Float | `Float32`, `Float64` |
| String | `String` (UTF-8) |
| Binary | `Binary` |

## Logical and Physical Types

Polars distinguishes between *physical* storage and *logical* interpretation. Date/time types store values as integers but expose datetime semantics:

| Logical Type | Physical Storage |
| --- | --- |
| `Date` | `Int32` (days since Unix epoch) |
| `Datetime(time_unit, timezone?)` | `Int64` (time unit: `us`, `ms`, `ns`) |
| `Duration(time_unit)` | `Int64` |
| `Time` | `Int64` (nanoseconds since midnight) |

```python
import polars as pl
import datetime as dt

df = pl.DataFrame({
    "event_date": [dt.date(2024, 1, 15), dt.date(2024, 6, 30)],
    "timestamp": [
        dt.datetime(2024, 1, 15, 10, 30, 0),
        dt.datetime(2024, 6, 30, 14, 45, 0),
    ],
})

print(df.schema)
# {'event_date': Date, 'timestamp': Datetime('us', None)}
```

Access temporal components via the `dt` namespace:

```python
df.select(
    pl.col("timestamp").dt.year().alias("year"),
    pl.col("timestamp").dt.month().alias("month"),
    pl.col("timestamp").dt.hour().alias("hour"),
    pl.col("event_date").dt.day_of_week().alias("dow"),
)
```

## Struct, List, Array

**Struct**: nested named fields within a single column.

```python
df = pl.DataFrame({
    "x": [1, 2, 3],
    "y": ["a", "b", "c"],
}).select(pl.struct(["x", "y"]).alias("point"))

print(df.schema)
# {'point': Struct([Field('x', Int64), Field('y', String)])}

# Access struct fields
df.select(pl.col("point").struct.field("x"))
```

**List**: variable-length arrays per row.

```python
df = pl.DataFrame({"groups": [[1, 2], [3], [4, 5, 6]]})
print(df.schema)
# {'groups': List(Int64)}

# List namespace operations
df.select(
    pl.col("groups").list.len().alias("length"),
    pl.col("groups").list.first().alias("first_elem"),
    pl.col("groups").list.contains(3),
)
```

**Array**: fixed-length arrays per row (different from List).

```python
df = pl.DataFrame({"coords": [[1.0, 2.0], [3.0, 4.0]]}).select(
    pl.col("coords").list.to_array(2)
)
print(df.schema)
# {'coords': Array(Float64, 2)}
```

## Categorical and Enum

**Categorical**: string-backed type optimized for low-cardinality data. Stores integer indices internally.

```python
df = pl.DataFrame({"category": ["low", "medium", "high", "low"]}).with_columns(
    pl.col("category").cast(pl.Categorical)
)
print(df.schema)
# {'category': Categorical}
```

**Enum**: predefined set of valid string values. Enforces membership at construction time.

```python
priority_enum = pl.Enum(["low", "medium", "high"])
df = pl.DataFrame({"priority": ["low", "high"]}).with_columns(
    pl.col("priority").cast(priority_enum)
)
```

Use Enum when the set of valid values is known and fixed. Use Categorical when categories are open-ended but cardinality is low.

## Schema Inspection and Manipulation

```python
df = pl.DataFrame({"a": [1], "b": ["x"], "c": [1.5]})

# Inspect
print(df.schema)     # {'a': Int64, 'b': String, 'c': Float64}
print(df.dtypes)     # [Int64, String, Float64]
print(df.columns)    # ['a', 'b', 'c']

# LazyFrame schema inference (without executing query)
lf = pl.scan_csv("data.csv").filter(pl.col("x") > 0).select(["a", "b"])
print(lf.collect_schema())

# Match schema to another frame
df.match_to_schema(other_df)
```

## Type Casting

Use `.cast()` for explicit type conversion:

```python
df = df.with_columns(
    pl.col("price").cast(pl.Float64),
    pl.col("date_str").str.strptime(pl.Date, "%Y-%m-%d"),
    pl.col("category").cast(pl.Categorical),
)

# Shrink types to minimal memory representation
df = df.select(pl.all().shrink_dtype())
```

String parsing to datetime:

```python
df.with_columns(
    pl.col("ts").str.strptime(pl.Datetime("us"), "%Y-%m-%d %H:%M:%S.%f"),
    pl.col("date").str.to_date("%Y-%m-%d"),
)
```
