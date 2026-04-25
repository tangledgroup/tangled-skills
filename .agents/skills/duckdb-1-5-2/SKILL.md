---
name: duckdb-1-5-2
description: High-performance analytical SQL database with support for nested types, vectorized execution, and seamless integration with Python/R/Java/Node.js. Use when building data analytics applications, performing ad-hoc queries on CSV/Parquet/JSON files, working with DataFrames (pandas/Polars), or needing an embedded OLAP database without server infrastructure.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.5.2"
tags:
  - sql
  - analytics
  - embedded-database
  - olap
  - data-science
category: database
external_references:
  - https://duckdb.org/docs/current/
  - https://duckdb.org/docs/current/clients/python/overview
  - https://duckdb.org/docs/current/sql/introduction
  - https://github.com/duckdb/duckdb
  - https://github.com/duckdb/duckdb/tree/v1.5.2
---
## Overview
DuckDB is a high-performance analytical database system designed to be fast, reliable, portable, and easy to use. It provides a rich SQL dialect with support far beyond basic SQL, including:

- Arbitrary and nested correlated subqueries
- Window functions
- Complex types (arrays, structs, maps)
- Vectorized query execution
- Columnar storage format
- Seamless DataFrame integration (pandas, Polars, PyArrow)

DuckDB operates as an **embedded database** - no server required. It's ideal for analytical workloads, data science pipelines, ETL processes, and applications requiring fast SQL analytics on local or cloud storage.

## When to Use
Use DuckDB when:

- **Analytical queries**: Running complex aggregations, window functions, or OLAP-style queries
- **File-based analytics**: Querying CSV, Parquet, JSON files directly without import
- **Data science workflows**: Integrating SQL with pandas/Polars/PyArrow DataFrames
- **Embedded analytics**: Needing a database without server infrastructure
- **Fast prototyping**: Rapidly exploring datasets with SQL
- **Edge computing**: Running analytics in resource-constrained environments
- **Data pipelines**: Transforming and aggregating data before loading to other systems

**Don't use DuckDB for:**
- High-concurrency OLTP workloads (use PostgreSQL, MySQL)
- Applications requiring frequent row-level updates/deletes
- Multi-user concurrent write scenarios
- Distributed query processing across multiple machines

## Core Concepts
### Architecture

- **Columnar Storage**: Data stored in column-oriented format for fast analytical queries
- **Vectorized Execution**: Processes data in batches for CPU cache efficiency
- **Embedded Model**: Library linked into applications, no separate server process
- **MPP Engine**: Massively Parallel Processing for query execution

### Data Types

DuckDB supports standard SQL types plus advanced nested types:

**Scalar Types:**
- `INTEGER`, `BIGINT`, `SMALLINT`, `TINYINT`
- `FLOAT`, `DOUBLE`, `DECIMAL(p,s)`
- `VARCHAR`, `CHAR(n)`, `BLOB`
- `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ`
- `BOOLEAN`, `BIT`, `UUID`

**Nested Types:**
- `ARRAY`: Lists of homogeneous elements
- `STRUCT`: Named fields with different types
- `MAP`: Key-value pairs

### In-Memory vs Persistent

```sql
-- In-memory database (default, volatile)
duckdb.connect()

-- Persistent database (file-based)
duckdb.connect('my_database.db')
```

## Installation / Setup
### Python Client

```bash
pip install duckdb==1.5.2
```

Or with conda:
```bash
conda install python-duckdb -c conda-forge
```

### CLI Tool

Download from [GitHub Releases](https://github.com/duckdb/duckdb/releases/tag/v1.5.2):

```bash
# macOS
brew install duckdb

# Linux (various packages available)
# See https://duckdb.org/docs/installation/

# Windows
# Download from GitHub releases or use chocolatey
choco install duckdb
```

### Other Languages

- **R**: `install.packages("duckdb")`
- **Java**: Add JDBC dependency from Maven Central
- **Node.js**: `npm install @duckdb/node-api`
- **Go**: `go get github.com/marcboeker/go-duckdb`
- **C/C++**: Link against DuckDB library

See [Client APIs](reference/02-client-apis.md) for detailed language-specific guides.

## Usage Examples
### Basic Queries

```python
import duckdb

# Simple query with in-memory database
result = duckdb.sql("SELECT 42 AS answer")
result.show()

# Query CSV files directly
duckdb.sql("SELECT * FROM 'sales.csv'").show()

# Query Parquet files
duckdb.sql("SELECT * FROM 'data.parquet' WHERE amount > 1000").show()
```

### Working with DataFrames

```python
import duckdb
import pandas as pd

# Create DataFrame
df = pd.DataFrame({'city': ['NYC', 'LA'], 'temp': [70, 85]})

# Query directly
duckdb.sql("SELECT * FROM df WHERE temp > 75").show()

# Convert query result to DataFrame
result_df = duckdb.sql("SELECT city, temp FROM df").df()
```

### Complex Analytics

```python
import duckdb

# Window functions
query = """
SELECT 
    product,
    sales,
    AVG(sales) OVER (PARTITION BY category) as avg_category_sales,
    RANK() OVER (ORDER BY sales DESC) as sales_rank
FROM sales_data
"""
duckdb.sql(query).show()

# Nested data operations
query = """
SELECT 
    customer_id,
    LIST(ORDER BY date DESC) as orders
FROM orders
GROUP BY customer_id
"""
```

See [SQL Reference](reference/03-sql-reference.md) for comprehensive SQL documentation.

## Quick Start Checklist
- [ ] Install DuckDB Python client: `pip install duckdb==1.5.2`
- [ ] Run first query: `python -c "import duckdb; duckdb.sql('SELECT 42').show()"`
- [ ] Query a CSV file: `duckdb.sql("SELECT * FROM 'file.csv'").show()`
- [ ] Connect to persistent database: `duckdb.connect('mydb.db')`
- [ ] Install extension: `INSTALL httpfs; LOAD httpfs;`
- [ ] Read cloud storage: `SELECT * FROM 's3://bucket/file.parquet'`

## Troubleshooting
Common issues and solutions:

| Issue | Solution |
|-------|----------|
| CSV parsing errors | Use `read_csv()` with explicit schema or options |
| Memory errors | Configure memory limits via `PRAGMA memory_limit` |
| Extension not found | Run `INSTALL extension_name; LOAD extension_name;` |
| S3 access denied | Configure AWS credentials and install httpfs extension |
| Slow queries | Use `EXPLAIN` to analyze query plan, consider Parquet format |

See [Performance Guide](reference/05-performance.md) for detailed troubleshooting.

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Client Apis](reference/02-client-apis.md)
- [Sql Reference](reference/03-sql-reference.md)
- [Extensions](reference/04-extensions.md)
- [Performance](reference/05-performance.md)
- [Data Import](reference/06-data-import.md)

