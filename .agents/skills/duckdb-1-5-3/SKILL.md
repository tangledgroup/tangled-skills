---
name: duckdb-1-5-3
description: Complete toolkit for DuckDB 1.5.3, an in-process SQL OLAP database management system. Covers SQL queries, data import/export (CSV, JSON, Parquet), Python API (Relations, UDFs, DB-API), nested types, window functions, and extensions. Use when writing SQL queries against local files or embedded databases, performing analytical data processing in Python, ingesting data from CSV/JSON/Parquet, or building data pipelines with DuckDB.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - duckdb
  - sql
  - database
  - olap
  - python-api
  - data-analytics
  - parquet
category: database
external_references:
  - https://github.com/duckdb/duckdb/tree/v1.5.3
  - https://duckdb.org/docs/current/
  - https://duckdb.org/docs/current/clients/python/overview
---

# DuckDB 1.5.3

## Overview

DuckDB is an in-process SQL OLAP database management system designed for analytical queries. It runs embedded within applications — no server process required. DuckDB reads directly from files (CSV, JSON, Parquet) and in-memory data structures (Pandas DataFrames, Polars DataFrames, PyArrow tables), making it ideal for data analysis, ETL pipelines, and local data exploration.

Key capabilities:
- **SQL-first**: PostgreSQL-compatible SQL dialect with extensions for analytical workloads
- **Zero-copy data ingestion**: Query files directly without loading into memory
- **Nested data types**: ARRAY, LIST, MAP, STRUCT, UNION, VARIANT
- **Multi-language API**: Python, R, Java, Go, Node.js, Rust, C/C++, CLI
- **Extension ecosystem**: httpfs, spatial, json, arrow, and community extensions

## When to Use

- Writing analytical SQL queries against local files (CSV, JSON, Parquet) without a database server
- Processing Pandas/Polars/Arrow data with SQL in Python
- Building ETL pipelines that read/write CSV, JSON, or Parquet files
- Creating user-defined functions (UDFs) bridging Python libraries and SQL
- Performing window functions, QUALIFY clauses, or CTE-based analytical queries
- Working with nested/semi-structured data (JSON, structs, arrays)
- Setting up persistent embedded databases with `duckdb.connect("file.db")`

## Core Concepts

### In-Process Architecture

DuckDB runs inside the application process. No network connection or server daemon is needed. Queries execute on data that lives in the same process or on local disk.

### Lazy Evaluation with Relations

The Python API returns `Relation` objects — symbolic representations of queries. No data is fetched until an output method (`.fetchall()`, `.df()`, `.show()`) is called.

```python
import duckdb

# Query is not executed yet
rel = duckdb.sql("SELECT * FROM 'large_file.parquet' WHERE value > 100")
# Data is fetched here
result = rel.fetchall()
```

### Direct File Queries

DuckDB queries files directly without explicit import:

```python
duckdb.sql("SELECT * FROM 'data.csv'")
duckdb.sql("SELECT * FROM 'data.parquet'")
duckdb.sql("SELECT * FROM read_json('data.json')")
```

### Connection Modes

| Mode | Usage | Persistence |
|------|-------|-------------|
| `duckdb.sql()` | Global in-memory database | None (ephemeral) |
| `duckdb.connect()` | New in-memory connection | None (ephemeral) |
| `duckdb.connect("file.db")` | Persistent file-based database | Stored on disk |

For production packages, always create explicit connections instead of using `duckdb.sql()` to avoid shared global state issues across threads.

### Thread Safety

`duckdb.sql()` and the global connection are **not thread-safe**. Each thread must create its own connection:

```python
# Safe — each thread gets its own connection
con = duckdb.connect()
con.sql("SELECT 1").fetchall()

# Unsafe — uses shared global connection
duckdb.sql("SELECT 1").fetchall()
```

## Installation / Setup

### Python

```bash
pip install duckdb
```

Requires Python 3.9+. Also available via conda:

```bash
conda install python-duckdb -c conda-forge
```

### CLI

See [DuckDB installation page](https://duckdb.org/install/) for platform-specific instructions.

## Usage Examples

### Basic Query with File Input

```python
import duckdb

# Query a CSV file directly
result = duckdb.sql("SELECT name, AVG(score) AS avg_score FROM 'students.csv' GROUP BY name")
result.show()
```

### Working with Pandas DataFrames

```python
import duckdb
import pandas as pd

df = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 82]})
result = duckdb.sql("SELECT * FROM df WHERE score > 80").df()
```

### Persistent Database with Schema

```python
import duckdb

with duckdb.connect("analytics.db") as con:
    con.sql("CREATE TABLE events (id INTEGER, type VARCHAR, ts TIMESTAMP)")
    con.sql("INSERT INTO events VALUES (1, 'click', CURRENT_TIMESTAMP)")
    con.sql("SELECT * FROM events").show()
```

### User-Defined Function

```python
import duckdb
from duckdb.sqltypes import VARCHAR

def uppercase_name(name):
    return name.upper()

duckdb.create_function("upper_name", uppercase_name, [VARCHAR], VARCHAR)
duckdb.sql("SELECT upper_name('alice')").fetchall()
# [('ALICE',)]
```

### Writing Results to Disk

```python
import duckdb

duckdb.sql("SELECT * FROM 'input.csv' WHERE active = true").write_parquet("output.parquet")
```

## Advanced Topics

**SQL Fundamentals**: SQL statements for DDL, DML, data manipulation, and schema management → [SQL Fundamentals](reference/01-sql-fundamentals.md)

**Data Types**: Scalar types, nested/composite types (ARRAY, LIST, MAP, STRUCT, UNION, VARIANT), typecasting rules → [Data Types](reference/02-data-types.md)

**Python API Deep Dive**: Connection management, Relations, DB-API compliance, UDFs with Arrow batches, type conversion rules → [Python API](reference/03-python-api.md)

**Data Import and Export**: Reading CSV/JSON/Parquet files, writing results, appender API, INSERT patterns → [Data Import and Export](reference/04-data-import-export.md)

**Query Patterns**: FROM/JOIN clauses, WHERE filtering, GROUP BY aggregation, WINDOW functions, QUALIFY, CTEs, subqueries → [Query Patterns](reference/05-query-patterns.md)

**Extensions and Configuration**: Extension installation/loading, autoloading, configuration options, secrets management → [Extensions and Configuration](reference/06-extensions-and-config.md)
