# Data Transformations

## Contents

- Joins (equi, non-equi, asof)
- Concatenation
- Pivots and unpivots
- Melt and explode
- Reshaping operations

## Joins

### Equi Joins

Match rows by key equality. Use `.join()` with `on` for shared key names or `left_on`/`right_on` for different names:

```python
orders = pl.DataFrame({
    "order_id": [1, 2, 3, 4],
    "customer_id": [10, 20, 10, 30],
    "amount": [100, 200, 150, 300],
})

customers = pl.DataFrame({
    "customer_id": [10, 20],
    "name": ["Alice", "Ben"],
})

# Inner join — only matching rows from both sides
result = orders.join(customers, on="customer_id", how="inner")

# Left join — all left rows, matched right data (NULL if no match)
result = orders.join(customers, on="customer_id", how="left")

# Right join — all right rows
result = orders.join(customers, on="customer_id", how="right")

# Full (outer) join — all rows from both sides
result = orders.join(customers, on="customer_id", how="full")
```

### Semi and Anti Joins

```python
# Semi join — keep left rows that have a match in right (no columns from right)
result = orders.join(customers, on="customer_id", how="semi")

# Anti join — keep left rows that have NO match in right
result = orders.join(customers, on="customer_id", how="anti")
```

### Different key column names

```python
orders.join(pricing, left_on="product_code", right_on="code", how="left")
```

### Multiple key joins

```python
df1.join(df2, on=["year", "month", "region"], how="inner")
```

### Non-Equi Joins

Match rows using inequality conditions instead of equality:

```python
result = orders.join_where(
    customers,
    (pl.col("amount") > pl.col("threshold")),
)
```

### Asof Join

Match by nearest key value (useful for time-series alignment):

```python
trades = pl.DataFrame({
    "time": [1, 5, 10, 15],
    "price": [10.5, 10.8, 11.2, 10.9],
})

quotes = pl.DataFrame({
    "time": [2, 8, 12],
    "bid": [10.4, 10.7, 11.1],
})

result = trades.join_asof(quotes, on="time", strategy="backward")
```

Strategies: `"backward"` (nearest key ≤ left), `"forward"` (nearest key ≥ left), `"nearest"`.

### Cartesian Product

```python
result = orders.join(customers, how="cross")
```

## Concatenation

### Vertical (row-wise)

```python
# Same schema
combined = pl.concat([df1, df2], how="vertical")

# Lazy concatenation
combined_lf = pl.concat([lf1, lf2])
```

### Horizontal (column-wise)

```python
# Side-by-side (same number of rows required)
combined = pl.concat([df1, df2], how="horizontal")
```

### Diagonal (relaxed schema)

Merges frames with different schemas, filling missing columns with nulls:

```python
combined = pl.concat([df1, df2], how="diagonal")
```

## Pivots

Convert rows to columns:

```python
sales = pl.DataFrame({
    "year": [2023, 2023, 2024, 2024],
    "product": ["A", "B", "A", "B"],
    "revenue": [100, 200, 150, 250],
})

pivoted = sales.pivot(
    on="product",
    index="year",
    values="revenue",
    aggregate_function="sum",
)
# Result: year | A   | B
#        2023 | 100 | 200
#        2024 | 150 | 250
```

## Unpivot

Convert columns to rows (inverse of pivot):

```python
unpivoted = pivoted.unpivot(
    on=["A", "B"],
    index="year",
    variable_name="product",
    value_name="revenue",
)
```

## Melt

Long-form reshaping (similar to unpivot but with different semantics):

```python
melted = df.melt(
    id_vars="name",
    value_vars=["math", "science", "english"],
    variable_name="subject",
    value_name="score",
)
```

## Explode

Expand list columns into separate rows:

```python
df = pl.DataFrame({
    "name": ["Alice", "Ben"],
    "tags": [["python", "rust"], ["java"]],
})

exploded = df.explode("tags")
# name  | tags
# Alice | python
# Alice | rust
# Ben   | java
```
