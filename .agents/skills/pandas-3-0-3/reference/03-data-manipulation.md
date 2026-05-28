# Data Manipulation

## Contents
- GroupBy (Split-Apply-Combine)
- Merge and Join
- Concatenate
- Reshape: Pivot, Melt, Stack/Unstack
- pd.col() Expressions
- Sorting

## GroupBy (Split-Apply-Combine)

Group data by one or more columns, then apply an aggregation, transformation, or filter.

```python
# Basic groupby + aggregation
df.groupby("region").agg(
    total_revenue=("revenue", "sum"),
    avg_score=("score", "mean"),
    n_customers=("id", "count"),
)

# Multiple grouping columns
df.groupby(["region", "category"]).size()

# Aggregation with named aggregations
df.groupby("date").agg(
    min_val=pd.NamedAgg(column="value", aggfunc="min"),
    max_val=pd.NamedAgg(column="value", aggfunc="max"),
)

# Transformation — broadcast group result back to original shape
df["group_mean"] = df.groupby("category")["score"].transform("mean")

# Filtration — drop groups not meeting condition
df.groupby("category").filter(lambda g: len(g) > 5)

# Iterating over groups
for name, group in df.groupby("region"):
    ...

# nsmallest / nlargest per group
df.groupby("region")["revenue"].nlargest(3)
```

### Common Aggregation Functions

| function | description |
|----------|-------------|
| `sum`, `mean`, `median`, `std`, `var` | numeric summaries |
| `min`, `max`, `count`, `first`, `last` | general reductions |
| `nunique` | count of unique values |
| `quantile(q)` | quantile at probability q |
| `agg([f1, f2])` | multiple functions at once |

## Merge and Join

Combine DataFrames on common keys (like SQL JOIN).

```python
# Inner join on common column
merged = pd.merge(left, right, on="key")

# Left outer join
merged = pd.merge(left, right, on="key", how="left")

# Different column names
merged = pd.merge(left, right, left_on="lkey", right_on="rkey")

# Cross join (cartesian product)
merged = pd.merge(left, right, how="cross")

# Merge with suffixes for overlapping columns
merged = pd.merge(left, right, on="id", suffixes=("_left", "_right"))

# DataFrame.join — merge on index
df1.join(df2, lsuffix="_l", rsuffix="_r")
```

### Join Types

| how | description |
|-----|-------------|
| `"inner"` | only matching keys (default) |
| `"left"` | all keys from left |
| `"right"` | all keys from right |
| `"outer"` | all keys from both |
| `"cross"` | cartesian product |

## Concatenate

Stack DataFrames row-wise or column-wise.

```python
# Row-wise (append rows)
combined = pd.concat([df1, df2], axis=0)

# Column-wise
combined = pd.concat([df1, df2], axis=1)

# With new index
combined = pd.concat([df1, df2], ignore_index=True)

# With group keys
combined = pd.concat([df1, df2], keys=["source_a", "source_b"])
```

## Reshape: Pivot, Melt, Stack/Unstack

### Pivot Table

Create a spreadsheet-style pivot table:

```python
pivot = df.pivot_table(
    values="sales",
    index="month",
    columns="category",
    aggfunc="sum",
    fill_value=0,
)
```

### Melt (Wide to Long)

```python
long_df = pd.melt(
    df,
    id_vars=["id", "date"],
    value_vars=["q1", "q2", "q3"],
    var_name="quarter",
    value_name="sales",
)
```

### Stack / Unstack

```python
# Columns → index levels (wide to long)
stacked = df.stack()

# Index levels → columns (long to wide)
unstacked = stacked.unstack()
```

### Explode

Expand list-like cells into separate rows:

```python
df = pd.DataFrame({"name": ["Alice", "Bob"], "tags": [["a", "b"], ["c"]]})
exploded = df.explode("tags")
```

## pd.col() Expressions

pandas 3.0 introduces `pd.col()` for column references without lambda wrappers:

```python
# Instead of lambda in assign
df.assign(total=pd.col("price") * pd.col("qty"))
# Old way
df.assign(total=lambda d: d["price"] * d["qty"])

# In .loc with boolean condition
df.loc[pd.col("status") == "active", "flag"] = 1

# Chaining expressions
df.assign(
    profit=pd.col("revenue") - pd.col("cost"),
    margin=(pd.col("revenue") - pd.col("cost")) / pd.col("revenue"),
)
```

`pd.col()` supports all standard operators and Series methods:
```python
pd.col("name").str.upper()
pd.col("score").rank()
```

## Sorting

```python
# Sort by one column
df.sort_values("age")

# Sort by multiple columns
df.sort_values(["region", "score"], ascending=[True, False])

# Sort by index
df.sort_index()
```
