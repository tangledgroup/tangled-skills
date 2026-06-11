# DataFrame API

## Contents

- Construction
- Inspection
- Column manipulation
- Row operations
- Sorting and sampling
- Null handling
- Export methods

## Construction

```python
import polars as pl

# From dict of lists
df = pl.DataFrame({
    "name": ["Alice", "Ben"],
    "age": [30, 25],
})

# From list of dicts (rows)
df = pl.DataFrame([
    {"name": "Alice", "age": 30},
    {"name": "Ben", "age": 25},
])

# From list of tuples with schema
df = pl.DataFrame(
    [("Alice", 30), ("Ben", 25)],
    schema=["name", "age"],
)

# Empty DataFrame with schema
df = pl.DataFrame(schema={"name": pl.String, "age": pl.Int64})
```

## Inspection

```python
df.shape          # (rows, columns)
df.height         # rows
df.width          # columns
df.columns        # ['name', 'age']
df.schema         # {'name': String, 'age': Int64}
df.dtypes         # [String, Int64]
df.flags          # column-level flags (sorted, etc.)

# Quick previews
df.head(5)
df.tail(3)
df.glimpse()      # compact column overview
df.describe()     # statistical summary
df.estimated_size(unit="mb")
```

## Column Manipulation

### Select and rename

```python
df.select(["name", "age"])
df.select(pl.col("name"), pl.col("age").alias("years"))
df.rename({"name": "full_name"})
```

### Add, drop, replace columns

```python
df.with_columns(
    (pl.col("age") * 365).alias("days_old"),
)

df.drop("temp_col")
df.drop_nulls(subset=["name"])

df.replace_column("age", pl.Series("age", [31, 26]))
df.insert_column(index=0, series=pl.Series("id", [1, 2]))
```

### Cast columns

```python
df.with_columns(pl.col("age").cast(pl.Int32))
df.select(pl.all().shrink_dtype())
```

## Row Operations

### Filtering

```python
df.filter(pl.col("age") > 25)
df.filter((pl.col("age") > 25) & (pl.col("name").str.starts_with("A")))
```

### Slicing and gathering

```python
df.slice(offset=5, length=10)
df.limit(10)
df.gather([0, 5, 10])              # by indices
df.gather_every(5)                 # every nth row
```

### Sorting and sampling

```python
df.sort("age", descending=True)
df.sort(["department", "salary"], descending=[False, True])
df.sample(fraction=0.1, seed=42)
df.sample(n=100, seed=42)
```

### Uniqueness and deduplication

```python
df.unique(subset=["name"])
df.unique(maintain_order=True)
df.is_duplicated()
df.is_unique(subset=["email"])
```

## Null Handling

```python
# Detect
df.null_count()
df.select(pl.col("x").is_null())
df.select(pl.col("x").is_not_null())

# Drop
df.drop_nulls()
df.drop_nulls(subset=["name", "email"])

# Fill
df.fill_null(strategy="forward")
df.fill_null(value=0)
df.with_columns(pl.col("category").fill_null("unknown"))

# NaN vs null: Polars distinguishes NaN (float only) from null
df.fill_nan(0)
df.drop_nans()
```

## Export Methods

```python
# To Python types
df.to_dict()           # dict of lists
df.to_dicts()          # list of dicts (one per row)
df.row(0)              # single row as tuple
df.rows()              # all rows as list of tuples
df.item(0, 0)          # single value

# To numpy / arrow
df.to_numpy()
df["col"].to_numpy()
df.to_arrow()

# To pandas
df.to_pandas()

# Interoperability
df.to_init_repr()      # reproducible Polars code
```

## Conversion to LazyFrame

```python
lf = df.lazy()    # convert eager DataFrame to LazyFrame for lazy evaluation
```
