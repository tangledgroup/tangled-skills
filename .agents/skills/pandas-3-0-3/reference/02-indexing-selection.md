# Indexing and Selection

## Contents
- Label-Based Indexing (.loc)
- Position-Based Indexing (.iloc)
- Scalar Access (.at / .iat)
- Boolean Indexing
- Slicing
- query() Method
- isin() and where()
- Setting Values

## Label-Based Indexing (.loc)

`.loc` selects by **label**. Both start and stop labels are **inclusive**.

```python
df = pd.DataFrame(
    {"a": [1, 2, 3], "b": [4, 5, 6]},
    index=["x", "y", "z"],
)

# Single row by label
df.loc["x"]              # Series

# Multiple rows
df.loc[["x", "z"]]       # DataFrame

# Row and column
df.loc["x", "a"]         # scalar: 1

# Label slice (inclusive on both ends)
df.loc["x":"y"]          # rows x through y

# All rows, specific columns
df.loc[:, ["a", "b"]]
```

## Position-Based Indexing (.iloc)

`.iloc` selects by **integer position** (0-based). Standard Python slice semantics (stop exclusive).

```python
# First row
df.iloc[0]               # Series

# Rows 0 and 2
df.iloc[[0, 2]]          # DataFrame

# Row 0, column 1
df.iloc[0, 1]            # scalar

# Slice rows (stop exclusive)
df.iloc[0:2]             # rows 0 and 1

# All rows, first two columns
df.iloc[:, :2]
```

## Scalar Access (.at / .iat)

Fast single-value access by label or position:

```python
df.at["x", "a"]          # by label — faster than .loc for single value
df.iat[0, 1]             # by position — faster than .iloc for single value
```

## Boolean Indexing

Filter rows using boolean conditions. Always vectorized — never use Python loops or `if` on a Series.

```python
# Single condition
df.loc[df["age"] > 30]

# Multiple conditions (use & | ~, not and/or/not)
df.loc[(df["age"] > 30) & (df["score"] > 80)]

# Negation
df.loc[~df["name"].isin(["Alice", "Bob"])]

# Check if ANY condition is true
if (df["age"] > 30).any():
    ...

# Check if ALL conditions are true
if (df["score"] >= 0).all():
    ...
```

**Never use `if df["col"] > 5`** — this raises `ValueError` because a Series has no single truth value.

## Slicing

```python
# By position
df.iloc[1:4]             # rows at positions 1, 2, 3

# By label (inclusive)
df.loc["start":"end"]    # includes both "start" and "end" if in index

# Step slicing
df.iloc[::2]             # every other row
```

## query() Method

Evaluate a string expression against column names. Clean syntax for complex filters:

```python
df.query("age > 30 and score > 80")
df.query("name == @variable")     # @ prefix for external variables
df.query("region in @regions")
```

## isin() and where()

```python
# Filter rows where column value is in a set
df.loc[df["category"].isin(["A", "B"])]

# Replace values conditionally (like SQL CASE WHEN)
df["score"].where(df["score"] > 50, other=0)  # values <= 50 become 0
```

## Setting Values

Under Copy-on-Write, always assign directly to the target object:

```python
# Direct column assignment — modifies df
df["new_col"] = df["a"] + df["b"]

# Assignment via .loc on the original object
df.loc[df["age"] > 30, "flag"] = True

# Chained assignment does NOT work under CoW
subset = df.loc[df["age"] > 30]
subset["flag"] = True    # modifies subset, NOT df
```

## Cross-Reference

- For MultiIndex (hierarchical indexing), see [Advanced Topics](reference/07-advanced-topics.md)
- For `pd.col()` expressions in selection, see [Data Manipulation](reference/03-data-manipulation.md)
