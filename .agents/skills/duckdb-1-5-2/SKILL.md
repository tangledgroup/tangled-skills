---
name: duckdb-1-5-2
description: High-performance analytical SQL database with support for nested types, vectorized execution, and seamless integration with Python, R, Java, Node.js, and WebAssembly. Use when building data analytics applications, performing ad-hoc queries on CSV/Parquet/JSON files, working with DataFrames (pandas, Polars), or needing an embedded OLAP database without server infrastructure.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.5.2"
tags:
  - analytics
  - olap
  - embedded-database
  - sql
  - data-science
  - dataframe
  - parquet
  - json
category: database
external_references:
  - https://duckdb.org/docs/current/
  - https://duckdb.org/docs/current/clients/python/overview
  - https://duckdb.org/docs/current/sql/introduction
  - https://github.com/duckdb/duckdb
  - https://github.com/duckdb/duckdb/tree/v1.5.2
---

# DuckDB 1.5.2

## Overview

DuckDB is a high-performance analytical database system designed to be fast, reliable, portable, and easy to use. It provides a rich SQL dialect with support far beyond basic SQL including arbitrary and nested correlated subqueries, window functions, collations, complex types (arrays, structs, maps), and extensions designed to make SQL easier to use.

DuckDB is an **in-process** database — it runs embedded within your application process rather than as a separate server. This makes it ideal for analytical workloads, data science pipelines, ETL processes, and ad-hoc querying without any infrastructure overhead.

Key characteristics:

- **Embedded architecture** — no server to install or configure, runs in-process
- **Columnar storage** — optimized for analytical (OLAP) queries with vectorized execution
- **Zero-copy data access** — query data directly from files, DataFrames, and cloud storage without loading
- **Rich SQL dialect** — supports complex types, window functions, CTEs, QUALIFY, and more
- **Multi-language clients** — Python, R, Java (JDBC), Node.js, Go, C/C++, Rust, Wasm, ODBC, ADBC
- **Deep DataFrame integration** — query pandas and Polars DataFrames directly with SQL
- **Extension ecosystem** — HTTP/S3 access, spatial data, full-text search, Delta/Iceberg/Lakehouse formats

## When to Use

Use DuckDB when:

- Performing analytical queries on CSV, Parquet, or JSON files without loading into a database
- Running SQL over pandas DataFrames or Polars DataFrames in Python
- Building embedded analytics into applications without database server infrastructure
- Needing fast ad-hoc data exploration and summarization
- Processing large datasets that fit in memory with columnar execution patterns
- Integrating SQL capabilities into data science pipelines (Python, R)
- Querying data directly from cloud storage (S3, GCS, HTTP)
- Building lightweight ETL/ELT transformations with SQL
- Needing an SQLite-like embedded database but for analytical (OLAP) rather than transactional (OLTP) workloads

Do not use DuckDB when:

- You need high-concurrency OLTP workloads (use PostgreSQL or SQLite instead)
- You need a client-server database architecture with multiple concurrent writers
- You need ACID transaction guarantees across multiple processes

## Core Concepts

**In-process execution**: DuckDB runs inside your application process. There is no separate server daemon. Connections are lightweight and share the same memory space as the host application.

**Columnar storage**: Data is stored in column-oriented format optimized for analytical queries that scan many rows but few columns. This provides superior compression and cache efficiency for analytics compared to row-based storage.

**Vectorized execution**: DuckDB processes data in vectors (batches of ~1024 rows) rather than row-by-row, enabling SIMD instructions and reducing interpreter overhead. This makes analytical queries significantly faster than traditional row-oriented databases.

**Zero-copy file access**: DuckDB can query CSV, Parquet, and JSON files directly by referencing them in SQL without explicit import. For Parquet files especially, this means near-zero overhead as the on-disk format is columnar.

**Nested types**: Unlike most SQL databases, DuckDB natively supports arrays, structs, maps, and unions as first-class data types. This makes it ideal for working with semi-structured data from JSON APIs and NoSQL sources.

**Friendly SQL**: DuckDB includes quality-of-life SQL features like automatic type coercion, lenient CSV parsing, implicit casting in comparisons, and order preservation to reduce common friction points.

## Installation / Setup

Install the Python package:

```bash
pip install duckdb==1.5.2
```

Other language clients are available via their respective package managers (npm for Node.js, CRAN for R, Maven for Java, etc.).

## Usage Examples

**Basic query from a file:**

```python
import duckdb

# Query CSV directly without loading
result = duckdb.sql("SELECT * FROM 'data.csv' LIMIT 10")
print(result)

# Query Parquet (zero-copy columnar access)
result = duckdb.sql("SELECT country, COUNT(*) FROM 'sales.parquet' GROUP BY country")
```

**In-memory database:**

```python
import duckdb

con = duckdb.connect()  # in-memory database

# Create table and insert data
con.execute("CREATE TABLE users (id INTEGER, name VARCHAR, score DOUBLE)")
con.execute("INSERT INTO users VALUES (1, 'Alice', 95.5), (2, 'Bob', 87.3)")

# Query
result = con.execute("SELECT * FROM users WHERE score > 90").fetchall()
print(result)  # [(1, 'Alice', 95.5)]
```

**SQL on pandas DataFrames:**

```python
import duckdb
import pandas as pd

df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'], 'score': [95, 87, 92]})

# Query DataFrame directly with SQL
result = duckdb.sql("SELECT * FROM df WHERE score > 90")
print(result)

# Or use the relational API
rel = duckdb.relational(df)
filtered = rel.filter("score > 90")
```

**Persisting to disk:**

```python
import duckdb

# Connect to a file-based database
con = duckdb.connect('my_database.db')
con.execute("CREATE TABLE data (x INTEGER, y VARCHAR)")
con.execute("INSERT INTO data VALUES (1, 'hello'), (2, 'world')")
con.close()

# Reconnect — data persists
con = duckdb.connect('my_database.db')
result = con.execute("SELECT * FROM data").fetchall()
print(result)  # [(1, 'hello'), (2, 'world')]
```

**Reading multiple files with glob:**

```python
import duckdb

# Read all CSV files in a directory
result = duckdb.sql("SELECT * FROM 'data/*.csv'")

# Read partitioned Parquet files
result = duckdb.sql("SELECT * FROM 's3://bucket/data/year=2024/*.parquet'")
```

## Advanced Topics

**Python API Reference**: Connection management, execution methods, result handling, DB-API 2.0 compliance → See [Python Client API](reference/01-python-api.md)

**SQL Dialect and Query Syntax**: DuckDB's SQL extensions, data types, expressions, functions, window functions, QUALIFY, PIVOT, and query patterns → See [SQL Reference](reference/02-sql-reference.md)

**Data Import and File Formats**: Reading/writing CSV, Parquet, JSON, Excel; cloud storage access (S3, GCS, HTTP); auto-detection; partitioned data → See [Data Import and Export](reference/03-data-import-export.md)

**Extensions and Configuration**: Core extensions (httpfs, spatial, full-text search, iceberg, delta), extension installation, pragmas, secrets manager → See [Extensions and Configuration](reference/04-extensions-config.md)
