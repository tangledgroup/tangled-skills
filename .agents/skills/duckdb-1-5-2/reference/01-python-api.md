# Python Client API

## Connection Management

### Creating Connections

```python
import duckdb

# In-memory database (default)
con = duckdb.connect()

# Persistent file-based database
con = duckdb.connect('my_database.db')

# Read-only connection
con = duckdb.connect('my_database.db', read_only=True)

# With configuration options
con = duckdb.connect(config={'threads': '4', 'memory_limit': '2GB'})
```

### Module-level Functions

The `duckdb` module provides convenience functions that use an implicit default connection:

```python
import duckdb

# Execute and return results as DataFrame
df = duckdb.query("SELECT 1 as x").fetchdf()

# Execute SQL string directly
result = duckdb.sql("SELECT * FROM 'data.csv'")

# Get version
print(duckdb.__version__)
```

### Connection Methods

```python
con = duckdb.connect()

# Execute SQL (returns cursor)
cursor = con.execute("SELECT 1 as x")

# Execute without returning results
con.executescript("""
    CREATE TABLE t1 (a INTEGER);
    INSERT INTO t1 VALUES (1), (2), (3);
""")

# Close connection
con.close()
```

## Execution and Results

### Cursor Interface (DB-API 2.0)

DuckDB's Python client implements Python DB-API 2.0 (PEP 249):

```python
import duckdb

con = duckdb.connect()
cur = con.cursor()

# Execute query
cur.execute("SELECT 1 as a, 2 as b")

# Fetch results
row = cur.fetchone()       # First row: (1, 2)
rows = cur.fetchall()      # All remaining rows
sample = cur.fetchmany(5)  # Next 5 rows

# Column description
print(cur.description)     # List of (name, type_code, ...) tuples
print(cur.rowcount)        # Number of rows returned
```

### Result Formats

Convert query results to various formats:

```python
result = con.execute("SELECT name, score FROM users")

# As list of tuples (default)
rows = result.fetchall()
# [('Alice', 95), ('Bob', 87)]

# As list of dictionaries
dicts = result.fetchall()
# Use fetchdf() for dict-like access

# As pandas DataFrame
df = result.fetchdf()

# As PyArrow Table
table = result.fetch_arrow_table()

# As PyArrow record batch
batch = result.fetch_arrow_batch()

# As numpy arrays
arrays = result.fetchnumpy()
```

### Arrow-based Results (Zero-copy)

DuckDB uses Apache Arrow as its internal format. Fetching Arrow results is zero-copy:

```python
import duckdb

con = duckdb.connect()
result = con.execute("SELECT * FROM large_table")

# Zero-copy to PyArrow Table
arrow_table = result.fetch_arrow_table()

# Zero-copy to pandas (Arrow-backed)
df = result.fetchdf()
```

## Relational API

The relational API provides a programmatic, composable interface for building queries:

```python
import duckdb

# Create relation from various sources
rel = duckdb.table('my_table')           # From database table
rel = duckdb.from_arrow(arrow_table)     # From PyArrow
rel = duckdb.from_csv_auto('data.csv')   # Auto-detect CSV schema
rel = duckdb.from_parquet('data.parquet') # From Parquet

# Composable transformations
result = (rel
    .filter("score > 90")
    .project("name, score")
    .order("score DESC")
    .limit(10))

# Execute and convert
df = result.fetchdf()
```

### Relational Operations

```python
# Filter
rel.filter("age > 25 AND city = 'NYC'")

# Project (select columns with expressions)
rel.project("name, score * 2 as double_score")

# Aggregate
rel.aggregate("COUNT(*), AVG(score), SUM(revenue)")

# Group by
rel.group_by("department").aggregate("AVG(salary), COUNT(*)")

# Join
orders = duckdb.table('orders')
customers = duckdb.table('customers')
joined = orders.join(customers, "orders.customer_id = customers.id")

# Order and limit
rel.order("created_at DESC").limit(100)

# Union
rel1.union(rel2)
```

## Data Ingestion

### From CSV

```python
import duckdb

# Auto-detect schema
df = duckdb.from_csv_auto('data.csv').fetchdf()

# With options
df = duckdb.from_csv_auto('data.csv',
    read_options={'delimiter': ';', 'header': True})

# Multiple files
df = duckdb.from_csv_auto('data/*.csv').fetchdf()
```

### From Parquet

```python
# Single file
table = duckdb.from_parquet('data.parquet')

# Multiple files / glob
table = duckdb.from_parquet('data/*.parquet')

# With row groups (for partial reads)
table = duckdb.from_parquet('data.parquet',
    read_options={'row_groups': '[0, 2]'})
```

### From JSON

```python
# Auto-detect schema
table = duckdb.from_json_auto('data.json')

# Multiple files
table = duckdb.from_json_auto('data/*.json')
```

### From Pandas / PyArrow

```python
import pandas as pd
import pyarrow as pa
import duckdb

# Register pandas DataFrame
df = pd.DataFrame({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})
result = duckdb.sql("SELECT * FROM df")

# Register PyArrow table
arrow_table = pa.table({'x': [1, 2, 3]})
result = duckdb.sql("SELECT * FROM arrow_table")

# Create table from DataFrame
con = duckdb.connect()
con.execute("CREATE TABLE my_table AS SELECT * FROM df")
```

## Function API

Register custom Python functions as SQL scalar or aggregate functions:

```python
import duckdb

con = duckdb.connect()

# Scalar function
def my_upper(s):
    return s.upper() if s else None

con.create_function('my_upper', my_upper, ['VARCHAR'], 'VARCHAR')
result = con.execute("SELECT my_upper('hello')").fetchone()
# ('HELLO',)

# Vectorized scalar function (receives numpy arrays)
import numpy as np

def vectorized_double(arr):
    return arr * 2

con.create_function('double_val', vectorized_double, ['INTEGER'], 'INTEGER',
                    type='native')
```

## Type Conversion

DuckDB automatically converts between Python types and SQL types:

| DuckDB Type | Python Type |
|---|---|
| INTEGER / BIGINT | int |
| FLOAT / DOUBLE | float |
| VARCHAR | str |
| BOOLEAN | bool |
| DATE | datetime.date |
| TIMESTAMP | datetime.datetime |
| INTERVAL | duckdb.Interval |
| BLOB | bytes |
| ARRAY | list |
| STRUCT | dict |
| MAP | dict |
| NULL | None |

## Spark API

DuckDB provides a PySpark-compatible API for running Spark-like code locally:

```python
from duckdb import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet('data.parquet')
df.createOrReplaceTempView('my_data')
result = spark.sql("SELECT * FROM my_data WHERE score > 90")
result.show()
```
