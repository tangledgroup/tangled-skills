# SQL and Advanced Queries

## Contents

- SQLContext
- Executing SQL queries
- Common Table Expressions (CTEs)
- Window functions
- Rolling and dynamic group-by
- Time-series operations

## SQLContext

Polars translates SQL into expressions executed by its native engine. There is no separate SQL engine — performance matches the expression API.

```python
import polars as pl

# Create context
ctx = pl.SQLContext()

# Register DataFrames
df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
ctx.register("my_table", df)

# Or register all from global namespace
ctx = pl.SQLContext(register_globals=True)

# Or via dict
ctx = pl.SQLContext(frames={"orders": orders_df, "customers": cust_df})
```

## Executing SQL Queries

```python
result = ctx.execute("""
    SELECT a, b
    FROM my_table
    WHERE a > 1
    ORDER BY a DESC
""")

# Returns LazyFrame — call .collect() for DataFrame
df = result.collect()

# Chained queries in same context
ctx.execute("CREATE TABLE filtered AS SELECT * FROM my_table WHERE a > 1")
result = ctx.execute("SELECT * FROM filtered")
```

### Supported SQL features

- `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`
- `JOIN` (inner, left, right, full, cross)
- `GROUP BY` with aggregate functions
- `UNION`, `INTERSECT`, `EXCEPT`
- Subqueries in `FROM` and `WHERE`
- `CASE WHEN` expressions

## Common Table Expressions (CTEs)

```python
result = ctx.execute("""
    WITH active_users AS (
        SELECT user_id, COUNT(*) as order_count
        FROM orders
        WHERE status = 'active'
        GROUP BY user_id
    )
    SELECT u.name, au.order_count
    FROM users u
    JOIN active_users au ON u.id = au.user_id
    WHERE au.order_count > 5
""")
```

## Window Functions

Window functions compute aggregations within groups while preserving row-level granularity. Use `.over()` to define the window:

```python
df = pl.DataFrame({
    "department": ["A", "A", "B", "B", "A"],
    "salary": [50, 60, 70, 80, 55],
    "name": ["Alice", "Ben", "Chloe", "Dan", "Eve"],
})

# Aggregation per group, mapped to each row
result = df.with_columns(
    pl.col("salary").mean().over("department").alias("dept_avg"),
    pl.col("salary").rank().over("department").alias("salary_rank"),
    pl.col("name").first().over("department").alias("top_earner"),
)
```

### Common window expressions

```python
# Running total within group
pl.col("amount").sum().over("user_id")

# Row number within partition
pl.col("value").rank(method="ordinal").over("category")

# Difference from group mean
(pl.col("score") - pl.col("score").mean().over("class")).alias("deviation")

# Lead/lag
pl.col("price").shift(1).over("symbol").alias("prev_price")
pl.col("price").shift(-1).over("symbol").alias("next_price")
```

### Mapping window results

Window functions produce per-row results. To collapse back to one row per group, combine with `group_by`:

```python
# Window: keeps all rows
df.with_columns(pl.col("x").mean().over("g"))

# Group-by: one row per group
df.group_by("g").agg(pl.col("x").mean())
```

## Rolling and Dynamic Group-By

### group_by_dynamic — fixed time windows

Group rows into calendar-aligned time buckets:

```python
df = pl.read_csv("stock_prices.csv", try_parse_dates=True).sort("Date")

annual_avg = (
    df.group_by_dynamic(index_column="Date", every="1y")
    .agg(pl.col("Close").mean().alias("avg_close"))
)

# Other intervals: "1d", "1w", "1mo", "6mo", "1h"
daily = df.group_by_dynamic("Date", every="1d", period="7d").agg(
    pl.col("Close").mean()
)
```

Parameters:
- `every`: window recurrence interval
- `period`: window size (how far back to look)
- `offset`: shift window boundaries
- `truncate`: align output timestamps to interval boundaries
- `include_boundaries`: add `_lower` and `_upper` boundary columns

### Rolling windows

Sliding window over ordered data:

```python
df.with_columns(
    pl.col("value").rolling_mean("timestamp", window_size="7d").alias("7d_avg"),
    pl.col("value").rolling_sum("timestamp", window_size="30d").alias("30d_sum"),
)
```

### Upsampling

Fill missing time periods:

```python
df.upsample(time_column="Date", every="1D").forward_fill()
```

## Time-Series Operations

### Parsing dates from strings

```python
df.with_columns(
    pl.col("date_str").str.strptime(pl.Date, "%Y-%m-%d"),
    pl.col("ts").str.strptime(pl.Datetime("us"), "%Y-%m-%d %H:%M:%S.%f"),
)
```

### Timezone handling

```python
df.with_columns(
    pl.col("ts").dt.replace_time_zone("UTC"),
    pl.col("ts").dt.convert_time_zone("America/New_York"),
)
```

### Filtering by time range

```python
df.filter(
    pl.col("timestamp").is_between(
        datetime(2024, 1, 1),
        datetime(2024, 12, 31),
    )
)
```

### Resampling

```python
df.group_by_dynamic("timestamp", every="1h").agg(
    pl.col("value").mean(),
    pl.col("value").max(),
).set_sorted("timestamp")
```
