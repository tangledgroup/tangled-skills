# Python API

## Contents
- Module-Level vs Connection API
- Connection Management
- Relations and Lazy Evaluation
- DB-API (PEP 249) Compliance
- Type Conversion Rules
- User-Defined Functions (UDFs)
- Relational API

## Module-Level vs Connection API

The `duckdb` module and connection objects support the same methods. The module uses a shared global in-memory database; connections create isolated instances.

```python
import duckdb

# Module-level — uses global in-memory database
duckdb.sql("SELECT 42").show()

# Connection-level — isolated instance (recommended for libraries)
con = duckdb.connect()
con.sql("SELECT 42").show()
```

> For packages used by others, always create explicit connections. The global database causes hard-to-debug issues when multiple packages share state.

## Connection Management

### In-Memory Connections

```python
con = duckdb.connect()  # in-memory, ephemeral
```

### Persistent Database

```python
con = duckdb.connect("analytics.db")  # persists to disk
con.sql("CREATE TABLE events (id INTEGER)")
con.close()
# Reconnect to access persisted data
con2 = duckdb.connect("analytics.db")
```

### Context Manager

```python
with duckdb.connect("file.db") as con:
    con.sql("CREATE TABLE test (i INTEGER)")
    con.sql("INSERT INTO test VALUES (42)")
# Connection closed automatically
```

### Configuration at Connect Time

```python
con = duckdb.connect(
    config={
        'threads': 1,
        'memory_limit': '2GB',
        'access_mode': 'READ_ONLY'
    }
)
```

### Community Extensions

```python
con.install_extension("h3", repository="community")
con.load_extension("h3")
```

### Unsigned Extensions

```python
con = duckdb.connect(config={"allow_unsigned_extensions": "true"})
```

> Only load unsigned extensions from trusted sources. Avoid loading over HTTP.

## Relations and Lazy Evaluation

`Relation` objects are symbolic query representations — no data is fetched until an output method is called.

```python
rel = duckdb.sql("SELECT * FROM 'large.parquet' WHERE value > 100")
# Nothing executed yet
rel.show()       # Fetches first 10K rows for display
rel.fetchall()   # Fetches all rows as Python tuples
```

### Chaining Relations

```python
r1 = duckdb.sql("SELECT 42 AS i")
duckdb.sql("SELECT i * 2 AS k FROM r1").show()
```

### Output Methods

| Method | Returns |
|--------|---------|
| `.fetchall()` | List of Python tuples |
| `.fetchone()` | Single tuple |
| `.df()` | Pandas DataFrame |
| `.pl()` | Polars DataFrame |
| `.arrow()` | PyArrow Table |
| `.fetchnumpy()` | Dict of NumPy arrays |
| `.show()` | Print to console (first 10K rows) |
| `.write_parquet(path)` | Write to Parquet file |
| `.write_csv(path)` | Write to CSV file |

## DB-API (PEP 249) Compliance

DuckDB supports the Python Database API Specification 2.0:

```python
import duckdb

con = duckdb.connect()
cur = con.cursor()

cur.execute("CREATE TABLE data (x INTEGER, y VARCHAR)")
cur.execute("INSERT INTO data VALUES (?, ?)", (1, "hello"))
cur.execute("SELECT * FROM data")
print(cur.fetchall())

# Parameterized queries with named parameters
cur.execute("SELECT * FROM data WHERE x > :threshold", {"threshold": 0})
```

> Cursors from the same connection share the underlying connection — they cannot run concurrent queries.

## Type Conversion Rules

### Python Object → DuckDB

| Python Type | DuckDB Type |
|-------------|-------------|
| `None` | `NULL` |
| `bool` | `BOOLEAN` |
| `str` | `VARCHAR` |
| `bytearray`, `memoryview` | `BLOB` |
| `datetime.datetime` | `TIMESTAMP` or `TIMESTAMPTZ` (with tzinfo) |
| `datetime.date` | `DATE` |
| `datetime.time` | `TIME` or `TIMETZ` (with tzinfo) |
| `datetime.timedelta` | `INTERVAL` |
| `decimal.Decimal` | `DECIMAL` / `DOUBLE` |
| `uuid.UUID` | `UUID` |
| `int` | `BIGINT` → `INTEGER` → `UBIGINT` → `UINTEGER` → `DOUBLE` (tried in order) |
| `float` | `DOUBLE` → `FLOAT` (tried in order) |

### DuckDB Result → Python

```python
result = duckdb.sql("SELECT 42 AS i, 'hello' AS s, CURRENT_DATE AS d")
rows = result.fetchall()
# [(42, 'hello', datetime.date(2024, 1, 15))]
```

Conversion to DataFrames:

```python
duckdb.sql("SELECT * FROM data").df()     # Pandas
duckdb.sql("SELECT * FROM data").pl()     # Polars
duckdb.sql("SELECT * FROM data").arrow()  # PyArrow
```

## User-Defined Functions (UDFs)

Register Python functions for use in SQL:

```python
import duckdb
from duckdb.sqltypes import VARCHAR, INTEGER

def add_one(x):
    return x + 1

# Register scalar UDF
duckdb.create_function("add_one", add_one, [INTEGER], INTEGER)
duckdb.sql("SELECT add_one(41)").fetchall()  # [(42,)]
```

### Arrow UDFs (Batch Processing)

For performance, use Arrow UDFs that operate on entire batches:

```python
import duckdb
from duckdb.sqltypes import VARCHAR
import pyarrow as pa

def process_names(arr):
    return pa.array([name.upper() for name in arr.to_pylist()])

duckdb.create_function(
    "upper_name",
    process_names,
    [VARCHAR],
    VARCHAR,
    type='arrow'  # Arrow batch mode — much faster than native
)
```

### UDF Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Unique function name in catalog |
| `function` | Python callable |
| `parameters` | List of input column types |
| `return_type` | Return type of the function |
| `type` | `'native'` (default) or `'arrow'` for batch processing |
| `null_handling` | `'standard'` (default, NULL-in NULL-out) or `'special'` |
| `exception_handling` | `'raise'` (default) or `'return_null'` |
| `side_effects` | `False` (default) or `True` for non-deterministic functions |

Remove a UDF:

```python
con.remove_function("upper_name")
```

## Relational API

The Relational API provides method chaining for incremental query construction:

```python
import duckdb

con = duckdb.connect()
rel = con.sql("SELECT * FROM 'data.csv'")
filtered = rel.filter("score > 80")
aggregated = filtered.aggregate("AVG(score)")
aggregated.show()
```

Key relation methods:
- `.filter(expr)` — Apply WHERE condition
- `.project(expr)` — Select columns/expressions
- `.aggregate(expr)` — Aggregate with GROUP BY
- `.order(expr)` — ORDER BY
- `.limit(n)` — LIMIT n rows
- `.join(other, on, how='inner')` — Join with another relation

Relations support lazy evaluation — the query plan is built incrementally and executed only when output is requested.
