# Built-in Functions

## Core Scalar Functions

Always available by default:

**String functions:**
- `length(X)` — Number of characters in X
- `lower(X)`, `upper(X)` — Case conversion
- `ltrim(X)`, `rtrim(X)`, `trim(X,Y)` — Remove whitespace or characters
- `replace(X,Y,Z)` — Replace occurrences of Y with Z in X
- `substr(X,Y,Z)` — Extract substring starting at position Y, length Z
- `instr(X,Y)` — Byte index of first occurrence of Y in X
- `like(X,Y)`, `glob(X,Y)` — Pattern matching (`%` and `_` for LIKE; `*` and `?` for GLOB)
- `regexp(Y,X)` — Regular expression match (not enabled by default, requires application-defined function)

**Numeric functions:**
- `abs(X)` — Absolute value
- `max(X,Y,...)`, `min(X,Y,...)` — Maximum/minimum of arguments (scalar form)
- `round(X,Y)` — Round X to Y decimal places
- `ceil(X)`, `floor(X)`, `trunc(X)` — Ceiling, floor, truncate
- `change_count()` — Number of rows changed by the most recent statement
- `last_insert_rowid()` — Rowid of the last INSERT

**NULL handling:**
- `coalesce(X,Y,...)` — Return first non-NULL argument
- `ifnull(X,Y)` — Same as coalesce with two arguments
- `nullif(X,Y)` — Return NULL if X equals Y, otherwise return X
- `isnull(X)`, `notnull(X)` — Test for NULL

**Type inspection:**
- `typeof(X)` — Returns "text", "real", "integer", "blob", or "null"
- `unicode(X)` — Unicode code point of first character
- `char(X,...)` — Character from one or more unicode code points

**Other:**
- `hex(X)`, `unhex(X)` — Hexadecimal encoding/decoding
- `printf(FORMAT,...)` — C-style formatted output
- `random()` — Random integer between -2^63 and 2^63-1
- `randomblob(N)` — N bytes of random data
- `sqlite_version()`, `sqlite_source_id()` — Version information
- `total_changes()` — Total rows changed since connection opened

## Date and Time Functions

Seven built-in functions for date/time manipulation:

```sql
date(time-value, modifier, ...)
time(time-value, modifier, ...)
datetime(time-value, modifier, ...)
julianday(time-value, modifier, ...)
unixepoch(time-value, modifier, ...)
strftime(format, time-value, modifier, ...)
timediff(time-value-1, time-value-2)
```

Time values can be in these formats:
- `YYYY-MM-DD` or `YYYY-MM-DD HH:MM` or `YYYY-MM-DD HH:MM:SS.SSS`
- `HH:MM:SS.SSS` (time only, defaults to 2000-01-01)
- Unix timestamp: `unixepoch(N)`
- Julian day number: `julianday(N)`
- `now` — Current date and time
- `start`, `current`, `today`, `tomorrow`, `yesterday`

Common modifiers:
- `+NN days/hours/minutes/seconds`
- `-NN days/hours/minutes/seconds`
- `start of month/year/day`
- `weekday N` (0=Sunday, 1=Monday, etc.)
- `localtime`, `utc`

Examples:

```sql
-- Current timestamp
SELECT datetime('now');

-- Days between two dates
SELECT julianday('2025-12-31') - julianday('2025-01-01');

-- First day of next month
SELECT date('now', 'start of month', '+1 month');

-- Format with strftime
SELECT strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime');
```

## Aggregate Functions

Operate over a group of rows:

- `count(X)` — Number of non-NULL values (or `COUNT(*)` for all rows)
- `sum(X)` — Sum of values
- `avg(X)` — Average of values
- `min(X)`, `max(X)` — Minimum/maximum value
- `group_concat(X, separator)` — Concatenate values with optional separator
- `total(X)` — Like sum but returns 0.0 for empty groups (not NULL)
- `stddev(X)`, `variance(X)` — Standard deviation and variance

With FILTER clause:

```sql
SELECT
    count(*) AS total,
    avg(price) FILTER (WHERE price > 0) AS avg_positive_price,
    sum(quantity) FILTER (WHERE status = 'shipped') AS shipped_qty
FROM orders;
```

## Math Functions

Available when compiled with `-DSQLITE_ENABLE_MATH_FUNCTIONS`. Includes:

- `acos(X)`, `asin(X)`, `atan(X)`, `atan2(Y,X)` — Inverse trigonometric
- `cos(X)`, `sin(X)`, `tan(X)` — Trigonometric
- `cosh(X)`, `sinh(X)`, `tanh(X)` — Hyperbolic
- `exp(X)`, `log(X)` (natural log), `log10(X)`, `log2(X)`
- `power(Y,X)` — Y raised to the power X
- `sqrt(X)` — Square root
- `pi()` — Value of pi
- `trunc(X)` — Truncate to integer

## Window Functions

Window functions operate over a sliding window of rows using the `OVER` clause:

```sql
SELECT name, salary, department,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank_in_dept,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    LAG(salary) OVER (ORDER BY hire_date) AS prev_hire_salary
FROM employees;
```

Built-in window functions:
- `ROW_NUMBER()` — Sequential row number within partition
- `RANK()`, `DENSE_RANK()` — Ranking with/without gaps
- `NTILE(N)` — Divide rows into N buckets
- `PERCENT_RANK()`, `CUME_DIST()` — Distribution statistics
- `LAG(X,N)`, `LEAD(X,N)` — Access previous/next row values
- `FIRST_VALUE(X)`, `LAST_VALUE(X)` — First/last value in window frame
- Any aggregate function with OVER clause

Frame specifications:
- `ROWS BETWEEN ... AND ...` — Physical row boundaries
- `RANGE BETWEEN ... AND ...` — Logical value boundaries
- `GROUPS BETWEEN ... AND ...` — Peer group boundaries
- Boundaries: `UNBOUNDED PRECEDING`, `N PRECEDING`, `CURRENT ROW`, `N FOLLOWING`, `UNBOUNDED FOLLOWING`

## JSON Functions

Built-in since SQLite 3.38.0 (opt-out with `-DSQLITE_OMIT_JSON`).

**Core functions:**
- `json(X)` — Canonicalize JSON input, returns well-formed JSON
- `jsonb(X)` — Like json but removes all whitespace (binary compact form)
- `json_valid(X)` — Test if text is valid JSON
- `json_quote(X)` — Quote a value for use in JSON

**Construction:**
- `json_array(X,...)` — Create a JSON array from values
- `json_object(K,V,...)` — Create a JSON object from key-value pairs

**Extraction:**
- `json_extract(JSON, PATH,...)` — Extract values at JSON path
- `JSON -> PATH` — Same as json_extract (operator form)
- `JSON ->> PATH` — Like -> but unquotes the result

**Modification:**
- `json_insert(JSON, PATH, VALUE,...)` — Insert without replacing existing
- `json_replace(JSON, PATH, VALUE,...)` — Replace existing only
- `json_set(JSON, PATH, VALUE,...)` — Insert or replace
- `json_remove(JSON, PATH,...)` — Remove values at path
- `json_patch(JSON1, JSON2)` — Apply JSON Patch

**Querying:**
- `json_type(JSON)` or `json_type(JSON, PATH)` — Type of value
- `json_array_length(JSON)` or `json_array_length(JSON, PATH)` — Array length

**Table-valued functions for decomposition:**
- `json_each(JSON)` — Iterate over array elements
- `json_tree(JSON)` — Recursively iterate entire JSON structure

```sql
-- Extract nested values
SELECT json_extract(data, '$.user.name') AS name FROM events;

-- Using operator shorthand
SELECT data -> '$.user.name' AS name FROM events;

-- Decompose a JSON array
SELECT value FROM json_each('["a","b","c"]');

-- Recursive tree walk
SELECT key, value, type, path
FROM json_tree('{"a": [1,2,{"b":"c"}]}');
```

**JSON paths** use the `$` root indicator with dot notation for object keys and bracket notation for array indices:
- `$.name` — Object key "name"
- `$.items[0]` — First element of items array
- `$.items[*]` — All elements of items array
- `$..id` — Recursive descent for all "id" keys

**JSONB support:** Every JSON function has a `jsonb_` variant that produces compact output with no whitespace. JSONB values are stored as text but without formatting whitespace, saving storage space.

## Aggregate Functions (JSON)

- `json_group_array(X)` — Collect values into a JSON array
- `json_group_object(K,V)` — Collect key-value pairs into a JSON object

```sql
SELECT department,
    json_group_array(name) AS members
FROM employees
GROUP BY department;
```
