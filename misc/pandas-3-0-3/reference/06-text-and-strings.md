# Text and Strings

## Contents
- String Data Types
- .str Accessor Methods
- Splitting and Replacing
- Concatenation
- Pattern Matching and Extraction
- pandas 3.0 String Migration

## String Data Types

pandas 3.0 uses `str` dtype by default for string data (PyArrow-backed when available).

```python
# Inferred as str in pandas 3.0
s = pd.Series(["hello", "world", None])
print(s.dtype)  # str

# Explicit specification
s = pd.Series(["a", "b"], dtype="str")
```

### Four StringDtype Variants

| variant | storage | NA value |
|---------|---------|----------|
| `str` (default in 3.0) | PyArrow or object | `NaN` |
| `string` | object | `pd.NA` |
| `string[pyarrow]` | PyArrow | `pd.NA` |
| `string[python]` | object | `pd.NA` |

```python
# Explicit variant
s = pd.Series(["a", "b"], dtype="string[pyarrow]")
```

## .str Accessor Methods

The `.str` accessor provides vectorized string operations on Series:

```python
s = pd.Series(["Hello World", "foo bar", None])

s.str.lower()              # ["hello world", "foo bar", NaN]
s.str.upper()
s.str.strip()
s.str.len()                # [11, 7, NaN]
s.str.cat(sep=", ")        # single string: "Hello World, foo bar"
```

## Splitting and Replacing

```python
# Split into list
s.str.split(" ")

# Split with expand → DataFrame
s.str.split(" ", n=1, expand=True)

# Replace
s.str.replace("foo", "bar")
s.str.replace(r"\d+", "", regex=True)

# Extract groups
s.str.extract(r"(\w+) (\w+)")   # returns DataFrame
```

## Concatenation

```python
df["full_name"] = df["first"] + " " + df["last"]
df["full_name"] = df["first"].str.cat(df["last"], sep=" ")
```

## Pattern Matching and Extraction

```python
# Test for pattern
s.str.contains("pattern")
s.str.startswith("Hello")
s.str.endswith("World")
s.str.match(r"^\d{3}-\d{4}$")   # full match

# Extract
s.str.extract(r"(\d{4})-(\d{2})")    # named groups
s.str.extractall(r"(\w+)")           # all matches

# Find
s.str.find("pattern")      # first occurrence index
s.str.rfind("pattern")     # last occurrence
```

## Creating Indicator Variables

```python
# One-hot encoding from strings
pd.get_dummies(s.str.split(",", expand=True).stack())
```

## pandas 3.0 String Migration

When upgrading from pandas < 3.0, be aware of these changes:

### What Changed

- String columns are now `str` dtype instead of `object`
- Missing value is `np.nan` (not `pd.NA`)
- Non-string values cannot be stored in `str` columns (raises error on setitem)

### Common Issues and Fixes

```python
# OLD: Check for object dtype to find string columns
if df["col"].dtype == "object":  # breaks in 3.0
    ...

# NEW: Use type-checking function
import pandas.api.types as pat
if pat.is_string_dtype(df["col"]):
    ...

# OLD: Mixed types silently stored in object column
s = pd.Series(["a", 1, "b"])  # object dtype — allowed
s[1] = 42                      # silently stores int

# NEW: str dtype rejects non-strings
s = pd.Series(["a", "b"], dtype="str")
s[0] = 42                      # raises TypeError

# OLD: Check for pd.NA in string columns
if val is pd.NA: ...

# NEW: Use pd.isna() which works with NaN
if pd.isna(val): ...
```

### Testing Before Upgrade

Enable the new behavior in pandas 2.3 to test compatibility:

```python
pd.options.future.infer_string = True
```
