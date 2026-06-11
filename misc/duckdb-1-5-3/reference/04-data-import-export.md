# Data Import and Export

## Contents
- Reading CSV Files
- Reading JSON Files
- Reading Parquet Files
- Direct File Queries
- Writing to Disk
- COPY Statement
- Appender API
- INSERT Statements

## Reading CSV Files

### Basic Read

```sql
SELECT * FROM 'data.csv';
```

DuckDB auto-detects delimiter, header, and column types.

### Explicit Options

```sql
SELECT *
FROM read_csv_auto('data.csv',
    sep = ',',
    header = true,
    columns = {id: 'INTEGER', name: 'VARCHAR', score: 'DOUBLE'});
```

### Python API

```python
import duckdb

duckdb.read_csv("example.csv")              # Returns Relation
duckdb.sql("SELECT * FROM 'example.csv'")   # Direct query
```

### Multi-File Reads

Glob patterns for reading multiple files:

```sql
SELECT * FROM read_csv_auto('data/*.csv');
```

The `filename` virtual column identifies the source file (available since v1.3.0):

```sql
SELECT filename, * FROM read_csv_auto('data/*.csv');
```

## Reading JSON Files

JSON support requires the `json` extension (auto-loaded in most distributions).

### Basic Read

```sql
SELECT * FROM 'todos.json';
```

### With Custom Schema

```sql
SELECT *
FROM read_json('todos.json',
    format = 'array',
    columns = {userId: 'UBIGINT', id: 'UBIGINT', title: 'VARCHAR', completed: 'BOOLEAN'});
```

### JSON Extraction

DuckDB supports JSONPath and JSON Pointer syntax via the `->` operator:

```sql
-- Extract field using JSONPath
SELECT data->'$.name' FROM json_data;

-- Extract array element (0-based indexing for JSON)
SELECT data->'$[0]' FROM json_data;
```

> JSON arrays use **0-based indexing**, while DuckDB ARRAY and LIST types use **1-based indexing**.

### Loading JSON into a Table

```sql
CREATE TABLE todos AS SELECT * FROM 'todos.json';
-- Or with explicit schema
COPY todos FROM 'todos.json' (AUTO_DETECT true);
```

## Reading Parquet Files

Parquet is DuckDB's native high-performance format.

### Basic Read

```sql
SELECT * FROM 'data.parquet';
```

### Python API

```python
duckdb.read_parquet("example.parquet")
duckdb.sql("SELECT * FROM 'example.parquet'")
```

### Partitioned Parquet

Read partitioned datasets (Hive-style partitioning):

```sql
SELECT *
FROM read_parquet('s3://bucket/data/year=2024/month=*/*.parquet');
```

### Multi-File with Filename Column

```sql
SELECT filename, * FROM 'data/*.parquet';
```

## Direct File Queries

DuckDB queries files directly without explicit import — the file extension determines the reader:

```python
import duckdb

duckdb.sql("SELECT * FROM 'data.csv'")
duckdb.sql("SELECT * FROM 'data.parquet'")
duckdb.sql("SELECT * FROM read_json('data.json')")
```

Remote files via httpfs extension (auto-loaded):

```sql
SELECT * FROM 'https://example.com/data.parquet';
```

S3/Azure/GCS with credentials:

```sql
SELECT * FROM 's3://bucket/path/file.parquet';
```

## Writing to Disk

### Python API Methods

```python
import duckdb

duckdb.sql("SELECT * FROM data WHERE active").write_parquet("output.parquet")
duckdb.sql("SELECT * FROM data WHERE active").write_csv("output.csv")
```

### COPY Statement

```sql
COPY (SELECT * FROM users) TO 'users.csv' (HEADER true);
COPY events TO 'events.parquet' (COMPRESSION 'zstd');
```

Supported output formats: CSV, Parquet, JSON.

## COPY Statement

Import data into tables:

```sql
COPY users FROM 'users.csv' (AUTO_DETECT true, HEADER true);
COPY events FROM 'events.parquet';
COPY data FROM 'data.json' (AUTO_DETECT true);
```

Export tables:

```sql
COPY users TO 'users_backup.parquet';
COPY (SELECT name, COUNT(*) FROM events GROUP BY name) TO 'summary.csv' (HEADER true);
```

## Appender API

The Appender provides high-performance row-by-row or batch insertion:

```python
import duckdb

con = duckdb.connect()
con.sql("CREATE TABLE logs (id INTEGER, message VARCHAR, ts TIMESTAMP)")

appender = con.appender("logs")
appender.append_row(1, "started", "2024-01-01 00:00:00")
appender.append_row(2, "completed", "2024-01-01 00:05:00")
appender.close()
```

For batch insertion, use `INSERT` with multiple values or `COPY FROM`.

## INSERT Statements

Single-row insert:

```sql
INSERT INTO users VALUES (1, 'Alice', CURRENT_TIMESTAMP);
```

Multi-row insert:

```sql
INSERT INTO users VALUES
    (2, 'Bob', '2024-01-15'),
    (3, 'Carol', '2024-02-20');
```

Insert from query:

```sql
INSERT INTO summary
SELECT name, COUNT(*) AS total FROM events GROUP BY name;
```
