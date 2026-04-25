# Data Import and Export

## Overview

DuckDB provides multiple methods for importing and exporting data, optimized for analytical workloads. The best method depends on your data format, size, and use case.

## File-Based Import

### CSV Files

#### Basic CSV Loading

```sql
-- Simplest method: query file directly
SELECT * FROM 'data.csv';

-- With header row detection
SELECT * FROM read_csv('data.csv', header = true);

-- Specify delimiter
SELECT * FROM read_csv('data.csv', delimiter = ';');

-- Skip rows
SELECT * FROM read_csv('data.csv', skip = 5);
```

#### Advanced CSV Options

```sql
-- Full control with read_csv()
SELECT * FROM read_csv('data.csv', 
    header = true,              -- First row is header
    delimiter = ',',            -- Field separator
    quote = '"',                -- Quote character
    escape = '\\',              -- Escape character
    skip = 0,                   -- Rows to skip
    columns = {                 -- Explicit schema
        'id': INTEGER,
        'name': VARCHAR,
        'amount': DOUBLE,
        'created': TIMESTAMP
    },
    dateformat = '%Y-%m-%d',    -- Date format
    timestampformat = '%Y-%m-%d %H:%M:%S',  -- Timestamp format
    nullstr = ['NULL', 'NA', '']  -- Strings to treat as NULL
);

-- Auto-detect schema (sample first 1000 rows)
SELECT * FROM read_csv_auto('data.csv');

-- Multiple files with wildcard
SELECT * FROM read_csv_auto('data_*.csv');

-- Add filename column
SELECT *, _filename FROM read_csv_auto('data_*.csv');
```

#### CSV Loading Best Practices

```sql
-- For bulk loading into table: use COPY
COPY users FROM 'users.csv' (
    HEADER true,
    DELIMITER ',',
    NULL_VALUE 'NULL',
    AUTO_DETECT false
);

-- With error handling
COPY orders FROM 'orders.csv' (
    HEADER true,
    ERROR_ON_INVALID_DATA false,  -- Skip bad rows
    WARN_ON_TRAILING_DATA true    -- Warn about extra data
);
```

**Common CSV Issues:**

| Issue | Solution |
|-------|----------|
| Wrong delimiter | Specify `delimiter = ';'` or other character |
| Date parsing fails | Use `dateformat = '%d/%m/%Y'` to match format |
| Mixed types in column | Explicitly define schema with `columns` parameter |
| Quoted fields with quotes | Set `escape = '\\'` or change `quote` character |

### Parquet Files

#### Basic Parquet Loading

```sql
-- Query directly by filename
SELECT * FROM 'data.parquet';

-- Using read_parquet()
SELECT * FROM read_parquet('data.parquet');

-- Multiple files
SELECT * FROM read_parquet('data_*.parquet');
SELECT * FROM read_parquet(['file1.parquet', 'file2.parquet']);
```

#### Advanced Parquet Options

```sql
-- Column filtering (only read needed columns)
SELECT * FROM read_parquet('data.parquet', 
    column_filter = ['id', 'name', 'amount']
);

-- Push down filters to reader
SELECT * FROM read_parquet('data.parquet',
    pushdown_filters = true
)
WHERE amount > 1000 AND status = 'active';

-- Row filtering at reader level
SELECT * FROM read_parquet('data.parquet',
    row_filter = 'amount > 1000'
);

-- Skip metadata
SELECT * FROM read_parquet('data.parquet',
    skip_metadata = true
);
```

#### Parquet Best Practices

```sql
-- Write optimized Parquet files
COPY (SELECT * FROM large_table) TO 'output.parquet' (
    COMPRESSION SNAPPY,        -- or ZSTD, GZIP, LZ4
    ROW_GROUP_SIZE 100000,     -- Optimal for most workloads
    PAGE_SIZE 65536,
    DICTIONARY_ENCODING true   -- For low-cardinality columns
);

-- Partitioned Parquet (for large datasets)
COPY (SELECT * FROM sales) TO 'sales_output/' (
    PARTITION_BY region, year, month
);

-- Result: sales_output(region=us/year=2024/month=01/data.parquet)
```

**Parquet Advantages:**
- Columnar storage (fast analytics)
- Built-in compression
- Schema preservation
- Predicate pushdown support
- Native DuckDB format

### JSON Files

#### Basic JSON Loading

```sql
-- Auto-detect JSON structure
SELECT * FROM read_json_auto('data.json');

-- Array of objects
SELECT * FROM read_json('[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]');

-- Nested JSON (flattened)
SELECT * FROM read_json('{
    "user": {"id": 1, "name": "Alice"},
    "orders": [{"id": 101, "amount": 99.99}]
}');

-- Multiple JSON files
SELECT * FROM read_json_auto('data_*.json');
```

#### Advanced JSON Options

```sql
-- Specify path within JSON document
SELECT * FROM read_json('data.json', 
    json_path = '$.users[*]'
);

-- With explicit schema
SELECT * FROM read_json('data.json',
    columns = {
        'id': BIGINT,
        'name': VARCHAR,
        'email': VARCHAR
    }
);

-- Handle nested structures
SELECT 
    user.id,
    user.name,
    orders[1].amount AS first_order_amount
FROM read_json('data.json');
```

#### JSON Best Practices

```sql
-- Write JSON output
COPY (SELECT * FROM users) TO 'users.json' (FORMAT JSON);

-- Pretty-printed JSON
COPY (SELECT * FROM config) TO 'config.json' (
    FORMAT JSON,
    PRETTY true
);

-- JSON lines (one object per line)
COPY (SELECT * FROM events) TO 'events.jsonl' (
    FORMAT JSON,
    ARRAY true  -- Each row as JSON array element
);
```

### Excel Files

#### Reading Excel

```sql
-- Requires excel extension
INSTALL excel;
LOAD excel;

-- Read entire workbook (first sheet)
SELECT * FROM 'data.xlsx';

-- Specific sheet
SELECT * FROM read_excel('data.xlsx', sheet = 'Sales');

-- By sheet index (0-based)
SELECT * FROM read_excel('data.xlsx', sheet_index = 1);

-- With options
SELECT * FROM read_excel('data.xlsx', 
    sheet = 'Data',
    header = true,
    skip = 0,
    range = 'A2:D100'  -- Excel range notation
);
```

#### Writing Excel

```sql
-- Write to Excel file
COPY (SELECT * FROM report) TO 'report.xlsx' (FORMAT EXCEL);

-- Specific sheet name
COPY (SELECT * FROM summary) TO 'summary.xlsx' (
    FORMAT EXCEL,
    SHEET 'Summary Data'
);
```

### Other File Formats

#### Avro Files

```sql
INSTALL avro;
LOAD avro;

SELECT * FROM read_avro('data.avro');
SELECT * FROM 'data.avro';  -- Shorthand
```

#### Feather Files

```sql
-- Arrow Feather format (fast, uncompressed)
SELECT * FROM read_feather('data.feather');

-- Write Feather
COPY (SELECT * FROM dataframe) TO 'output.feather';
```

#### HDF5 Files

```sql
-- Hierarchical Data Format
SELECT * FROM read_hdf5('data.h5', dataset = '/path/to/data');
```

## DataFrame Integration

### Pandas Integration

#### Reading DataFrames

```python
import duckdb
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'amount': [100.50, 200.75, 300.25]
})

# Query directly (read-only)
duckdb.sql("SELECT * FROM df WHERE amount > 150").show()

# Register with custom name
duckdb.register('my_data', df)
duckdb.sql("SELECT * FROM my_data").show()

# Multiple DataFrames in one query
df1 = pd.DataFrame({'key': [1, 2, 3], 'val1': ['a', 'b', 'c']})
df2 = pd.DataFrame({'key': [1, 2, 3], 'val2': [10, 20, 30]})

result = duckdb.sql("""
    SELECT df1.key, df1.val1, df2.val2
    FROM df1
    JOIN df2 ON df1.key = df2.key
""").df()
```

#### Writing to DataFrames

```python
import duckdb
import pandas as pd

# Query to Pandas DataFrame
result_df = duckdb.sql("SELECT * FROM users WHERE age > 18").df()

# With Polars
result_pl = duckdb.sql("SELECT * FROM users").pl()

# To PyArrow
result_arrow = duckdb.sql("SELECT * FROM users").arrow()

# To NumPy
result_numpy = duckdb.sql("SELECT * FROM users").fetchnumpy()

# To Python lists
result_list = duckdb.sql("SELECT * FROM users").fetchall()
result_dict = duckdb.sql("SELECT * FROM users").fetchdf().to_dict('records')
```

#### Performance Tips

```python
# Good: Let DuckDB filter, then convert
filtered_df = duckdb.sql("""
    SELECT id, name, amount 
    FROM large_dataframe 
    WHERE amount > 1000 AND status = 'active'
""").df()

# Bad: Load everything, then filter in Pandas
all_df = duckdb.sql("SELECT * FROM large_dataframe").df()
filtered_df = all_df[all_df['amount'] > 1000]
```

### Polars Integration

```python
import duckdb
import polars as pl

# Create Polars DataFrame
polars_df = pl.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie']
})

# Query directly
duckdb.sql("SELECT * FROM polars_df").show()

# Convert query result to Polars
result_pl = duckdb.sql("SELECT * FROM users").pl()

# Lazy evaluation with Polars
lazy_result = (
    pl.scan_parquet('data.parquet')
    .filter(pl.col('amount') > 1000)
    .collect()
)
duckdb.sql("SELECT * FROM lazy_result").show()
```

### PyArrow Integration

```python
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

# Read Parquet with PyArrow
arrow_table = pq.read_table('data.parquet')

# Query with DuckDB
duckdb.sql("SELECT * FROM arrow_table WHERE amount > 1000").show()

# Convert DuckDB result to Arrow
result_arrow = duckdb.sql("SELECT * FROM users").arrow()

# Write to Parquet
result_arrow.write_parquet('output.parquet')
```

## Database Import/Export

### Import from Other Databases

#### SQLite

```sql
INSTALL sqlite;
LOAD sqlite;

-- Query SQLite database directly
SELECT * FROM sqlite_scan('/path/to/database.sqlite', 'table_name');

-- With schema specification
SELECT * FROM sqlite_scan('/path/to/database.sqlite', 'main', 'users');

-- Copy into DuckDB table
CREATE TABLE users AS 
SELECT * FROM sqlite_scan('/path/to/legacy.db', 'users');
```

#### PostgreSQL

```sql
INSTALL postgres;
LOAD postgres;

-- Create connection secret
CREATE SECRET (
    TYPE POSTGRESQL,
    KEY_ID 'pg_source',
    HOST 'localhost',
    PORT 5432,
    DATABASE 'source_db',
    USERNAME 'user',
    PASSWORD 'password'
);

-- Query PostgreSQL tables
SELECT * FROM postgres_scan('pg_source', 'public', 'users');

-- Bulk import
CREATE TABLE duckdb_users AS
SELECT * FROM postgres_scan('pg_source', 'public', 'users');
```

#### MySQL

```sql
INSTALL mysql;
LOAD mysql;

-- Create connection
CREATE SECRET (
    TYPE MYSQL,
    KEY_ID 'mysql_source',
    HOST 'localhost',
    PORT 3306,
    DATABASE 'source_db',
    USERNAME 'user',
    PASSWORD 'password'
);

-- Query MySQL tables
SELECT * FROM mysql_scan('mysql_source', 'users');
```

#### ODBC

```sql
INSTALL odbc;
LOAD odbc;

-- Create ODBC connection
CREATE SECRET (
    TYPE ODBC,
    KEY_ID 'my_odbc',
    DSN 'MyDataSource'
);

-- Execute query through ODBC
SELECT * FROM odbc_scan('my_odbc', 'SELECT * FROM remote_table');
```

### Export to Other Formats

#### SQL Dump

```sql
-- Generate CREATE and INSERT statements
.dump  -- In CLI, outputs to stdout

-- Or use .output to file
.output backup.sql
.dump
.output stdout
```

#### Backup/Restore

```sql
-- Backup database
.backup 'backup.db'

-- Restore (replace entire database)
.restore 'backup.db'
```

## Cloud Storage Integration

### AWS S3

```sql
INSTALL httpfs;
LOAD httpfs;

-- Configure credentials (or use environment variables)
SET s3_region = 'us-east-1';
SET s3_access_key_id = 'your-key';
SET s3_secret_access_key = 'your-secret';

-- Query files directly
SELECT * FROM 's3://my-bucket/data/*.parquet';

-- With specific path
SELECT * FROM 's3://my-bucket/folder/subfolder/data.parquet';

-- Write to S3
COPY (SELECT * FROM report) TO 's3://my-bucket/reports/report.parquet';

-- Partitioned write to S3
COPY (SELECT * FROM sales) TO 's3://my-bucket/sales/' (
    PARTITION_BY region, year
);
```

### Azure Blob Storage

```sql
INSTALL httpfs;
LOAD httpfs;

-- Configure Azure credentials
SET azure_storage_account_name = 'mystorage';
SET azure_storage_sas_token = '?sv=2021-...';

-- Query Azure Blob Storage
SELECT * FROM 'az://container/data.parquet';

-- Write to Azure
COPY (SELECT * FROM data) TO 'az://container/output.parquet';
```

### Google Cloud Storage

```sql
INSTALL httpfs;
LOAD httpfs;

-- Configure GCS credentials
SET gcs_project_id = 'my-project';
-- Or use service account JSON key file

-- Query GCS
SELECT * FROM 'gs://bucket/data.parquet';

-- Write to GCS
COPY (SELECT * FROM data) TO 'gs://bucket/output.parquet';
```

## Data Transformation During Import

### Schema Transformation

```sql
-- Transform during import
CREATE TABLE cleaned_data AS
SELECT 
    id,
    TRIM(name) AS name,
    CAST(amount AS DOUBLE) AS amount,
    STRFTIME('%Y-%m-%d', created_at) AS created_date,
    CASE 
        WHEN status = 'A' THEN 'active'
        WHEN status = 'I' THEN 'inactive'
        ELSE 'unknown'
    END AS status_clean
FROM read_csv('raw_data.csv');
```

### Data Validation

```sql
-- Import with validation checks
CREATE TABLE validated_orders AS
SELECT 
    id,
    customer_id,
    amount,
    order_date
FROM read_csv('orders.csv')
WHERE 
    id IS NOT NULL
    AND customer_id > 0
    AND amount >= 0
    AND order_date <= CURRENT_DATE;

-- Check for invalid rows
SELECT * FROM read_csv('orders.csv')
WHERE 
    id IS NULL
    OR customer_id <= 0
    OR amount < 0;
```

### Incremental Loading

```python
import duckdb

con = duckdb.connect('mydb.db')

# Get last processed timestamp
last_id = con.sql("SELECT COALESCE(MAX(id), 0) FROM users").fetchone()[0]

# Load only new data
new_users = con.sql(f"""
    SELECT * FROM read_csv('users.csv')
    WHERE id > {last_id}
""")

# Insert new rows
con.execute("INSERT INTO users SELECT * FROM new_users")
```

## Best Practices Summary

### Format Selection

| Use Case | Recommended Format |
|----------|-------------------|
| Analytics workloads | Parquet |
| Interoperability | CSV |
| Semi-structured data | JSON |
| Excel reports | XLSX |
| Large-scale cloud storage | Parquet + S3/Azure/GCS |
| DataFrame operations | Native (pandas/Polars/Arrow) |

### Performance Guidelines

1. **Use Parquet for large datasets**: Better compression, faster queries
2. **Batch CSV imports**: Use COPY instead of row-by-row INSERT
3. **Filter early**: Let DuckDB filter during import, not after
4. **Partition large datasets**: By date, region, or other high-cardinality columns
5. **Use appropriate compression**: SNAPPY for balance, ZSTD for size
6. **Leverage predicate pushdown**: Especially with Parquet and cloud storage

### Error Handling

```sql
-- Import with error tolerance
COPY users FROM 'users.csv' (
    HEADER true,
    ERROR_ON_INVALID_DATA false,  -- Skip bad rows
    LOG_ERRORS true               -- Log to stderr
);

-- Check for import issues
SELECT * FROM duckdb_csv_errors();  -- View parsing errors
```
