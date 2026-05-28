# Expressions

## Contents

- Expression basics
- Contexts (select, with_columns, filter, group_by)
- Arithmetic and comparisons
- Conditionals
- Expression expansion
- Aggregation expressions
- Folds
- User-defined functions

## Expression Basics

An expression is a reusable computation description that only executes inside a context. All column operations use `pl.col()`:

```python
import polars as pl

# Reference columns
pl.col("price")
pl.col("price", "cost")  # multiple columns

# Literal values
pl.lit(42)
pl.lit("hello")
pl.lit([1, 2, 3])

# Column arithmetic
pl.col("a") + pl.col("b")
pl.col("x") * 2
pl.col("y") ** 2

# Aliasing
pl.col("price").alias("unit_price")
```

## Contexts

Expressions evaluate inside one of four primary contexts:

### select — produce new columns

Each expression maps to one output column. Original columns not referenced are dropped.

```python
df.select(
    pl.col("name"),
    (pl.col("weight") / pl.col("height") ** 2).alias("bmi"),
)
```

### with_columns — add to existing

New columns are appended; existing columns are preserved.

```python
df.with_columns(
    (pl.col("price") * pl.col("quantity")).alias("total"),
    pl.col("price").round(2).alias("rounded_price"),
)
```

### filter — row predicate

Expression must produce Boolean output. Rows where expression is `True` are kept.

```python
df.filter(
    (pl.col("age") >= 18) & (pl.col("status") == "active")
)
```

### group_by — aggregation per group

Expressions compute one value per group. Use named arguments for clean output column names.

```python
df.group_by("department").agg(
    pl.col("salary").mean().alias("avg_salary"),
    pl.col("employee_id").count().alias("headcount"),
)
```

## Arithmetic and Comparisons

Standard operators work on expressions:

```python
# Arithmetic
pl.col("a") + pl.col("b")
pl.col("a") - pl.col("b")
pl.col("a") * pl.col("b")
pl.col("a") / pl.col("b")
pl.col("a") % pl.col("b")

# Comparisons
pl.col("a") > 10
pl.col("a") == pl.col("b")
pl.col("a").is_between(0, 100)

# Boolean
(pl.col("a") > 0) & (pl.col("b") < 5)
(pl.col("a") > 0) | (pl.col("b") < 5)
~pl.col("flag")
```

## Conditionals

`pl.when().then().otherwise()` for conditional logic:

```python
df.with_columns(
    pl.when(pl.col("score") >= 90)
    .then(pl.lit("A"))
    .when(pl.col("score") >= 80)
    .then(pl.lit("B"))
    .otherwise(pl.lit("C"))
    .alias("grade"),
)
```

`pl.replace()` and `pl.replace_strict()` for value mapping:

```python
df.with_columns(
    pl.col("status").replace(
        {"active": 1, "inactive": 0}, default=-1
    ).alias("status_code"),
)
```

## Expression Expansion

Expressions can expand to multiple columns using selectors:

```python
# By name pattern
df.select(pl.col("*_price"))           # all columns ending in _price
df.select(pl.col("a", "b", "c"))       # explicit list

# By dtype
df.select(pl.all().matches(r".*int.*"))
df.select(pl.exclude("name"))

# Selectors module
from polars import selectors as s
df.select(s.numeric())
df.select(s.string() | s.temporal())
```

## Aggregation Expressions

Common aggregation functions:

```python
pl.col("x").sum()
pl.col("x").mean()
pl.col("x").median()
pl.col("x").min()
pl.col("x").max()
pl.col("x").std()
pl.col("x").var()
pl.col("x").count()
pl.col("x").n_unique()
pl.col("x").first()
pl.col("x").last()
pl.col("x").quantile(0.95)
pl.col("x").implode()          # collect into list
```

Horizontal aggregations (across columns per row):

```python
pl.sum_horizontal("col_a", "col_b", "col_c")
pl.max_horizontal("col_a", "col_b")
pl.mean_horizontal(pl.all().matches(r".*_score$"))
```

## Folds

`pl.fold()` and `pl.reduce()` iterate across columns, accumulating a single value per row:

```python
# Row-wise mean of selected columns
pl.fold(acc=pl.lit(0), f=lambda a, b: a + b, exprs=pl.all().numeric()) / pl.count()

# Check if any column in a set is null
pl.reduce(
    acc=pl.lit(False),
    f=lambda a, b: a | b.is_null(),
    exprs=pl.col("a", "b", "c"),
)
```

## User-Defined Functions

`.map_elements()` applies a Python function element-wise (slowest option — use only when built-in expressions cannot express the logic):

```python
df.with_columns(
    pl.col("value").map_elements(lambda x: x ** 2 if x > 0 else 0, return_dtype=pl.Float64).alias("squared"),
)
```

`.map_batches()` applies a function to entire column chunks (faster than `map_elements`):

```python
df.with_columns(
    pl.col("value").map_batches(lambda s: s.to_numpy() ** 2).alias("squared"),
)
```

Prefer built-in expressions over UDFs. Order of preference: built-in expression → `map_batches` → `map_elements`.
