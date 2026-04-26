# Data Import and Export

## CSV Files

### Reading CSV

```sql
-- Auto-detect schema (recommended)
SELECT * FROM read_csv_auto('data.csv');

-- With glob patterns
SELECT * FROM read_csv_auto('data/*.csv');

-- Explicit options
SELECT * FROM read_csv('data.csv',
    columns={name: 'VARCHAR', age: 'INTEGER'},
    delim=',',
    header=true,
    null_str='NA'
);

-- Auto-detect with sampling control
SELECT * FROM read_csv_auto('large.csv', samples=10, max_line_size=8192);
```

### Writing CSV

```sql
-- Export query results to CSV
COPY (SELECT * FROM users WHERE active) TO 'output.csv' (WITH HEADER);

-- Options
COPY (SELECT * FROM data) TO 'output.csv' (
    DELIM ',',
    QUOTE '"',
    WITH HEADER,
    NULL 'NA'
);
```

### Reading Faulty CSV

DuckDB handles common CSV issues gracefully:

```sql
-- Auto-detect with error tolerance
SELECT * FROM read_csv_auto('messy.csv',
    allow_quoted_newlines=true,
    auto_detect=true,
    max_errors=100
);
```

## Parquet Files

### Reading Parquet

```sql
-- Direct query (zero-copy columnar access)
SELECT * FROM 'data.parquet';

-- Multiple files
SELECT * FROM read_parquet('data/*.parquet');

-- With filename metadata
SELECT *, file_name FROM read_parquet('data/*.parquet');

-- Cloud storage
SELECT * FROM read_parquet('s3://bucket/data/*.parquet');
SELECT * FROM read_parquet('https://example.com/data.parquet');

-- Specific columns (projection pushdown)
SELECT name, score FROM read_parquet('large.parquet');

-- Row group filtering
SELECT * FROM read_parquet('data.parquet', row_groups=[0, 2, 4]);
```

### Writing Parquet

```sql
-- Export to single file
COPY (SELECT * FROM data) TO 'output.parquet' (FORMAT PARQUET);

-- Partitioned output
COPY (SELECT * FROM events) TO 'output/' (
    FORMAT PARQUET,
    PARTITION_BY date
);

-- With compression
COPY (SELECT * FROM data) TO 'output.parquet' (
    FORMAT PARQUET,
    COMPRESSION 'ZSTD'
);

-- Per-thread output files
COPY (SELECT * FROM large_data) TO 'output/*.parquet' (FORMAT PARQUET);
```

### Parquet Metadata

```sql
-- View parquet file metadata
SELECT * FROM parquet_metadata('data.parquet');

-- View parquet schema
DESCRIBE SELECT * FROM 'data.parquet';
```

## JSON Files

### Reading JSON

```sql
-- Auto-detect schema
SELECT * FROM read_json_auto('data.json');

-- Multiple files
SELECT * FROM read_json_auto('data/*.json');

-- Newline-delimited JSON (JSONL)
SELECT * FROM read_json_auto('events.jsonl');

-- With explicit schema
SELECT * FROM read_json('data.json',
    columns={name: 'VARCHAR', score: 'INTEGER'}
);
```

### Writing JSON

```sql
-- Export as JSON array
COPY (SELECT * FROM users) TO 'output.json' (FORMAT JSON);

-- Newline-delimited JSON
COPY (SELECT * FROM users) TO 'output.jsonl' (
    FORMAT JSON,
    ARRAY FALSE
);
```

## Excel Files

Requires the `excel` extension:

```sql
INSTALL excel;
LOAD excel;

-- Read Excel file
SELECT * FROM read_excel('data.xlsx');

-- Specific sheet
SELECT * FROM read_excel('data.xlsx', sheet_name='Sales');

-- Write to Excel
COPY (SELECT * FROM report) TO 'output.xlsx' (FORMAT EXCEL);
```

## Cloud Storage Access

### S3 / AWS

Requires the `httpfs` extension:

```sql
INSTALL httpfs;
LOAD httpfs;

-- Read from S3
SELECT * FROM read_parquet('s3://bucket/data/*.parquet');

-- With credentials
SET s3_region='us-west-2';
SET s3_access_key_id='AKIA...';
SET s3_secret_access_key='secret...';

-- Or use IAM role / instance profile (automatic)
SELECT * FROM read_parquet('s3://bucket/data.parquet');
```

### Google Cloud Storage

```sql
-- GCS access via httpfs
SELECT * FROM read_parquet('gs://bucket/data/*.parquet');
```

### HTTP / HTTPS

```sql
-- Read directly from URL
SELECT * FROM read_csv_auto('https://example.com/data.csv');
SELECT * FROM read_parquet('https://example.com/data.parquet');
```

## Database Integration

### Importing from SQLite

```sql
INSTALL sqlite;
LOAD sqlite;

-- Query SQLite database directly
SELECT * FROM sqlite_scan('sqlite.db', 'users');

-- Copy to DuckDB table
CREATE TABLE users AS SELECT * FROM sqlite_scan('sqlite.db', 'users');
```

### Importing from PostgreSQL

```sql
INSTALL postgres;
LOAD postgres;

-- Connect to PostgreSQL
CALL postgres_attach('dbname=mydb host=localhost user=postgres password=xxx', 'pg_data');

-- Query PostgreSQL tables
SELECT * FROM pg_data.public.users;
```

### Importing from MySQL

```sql
INSTALL mysql;
LOAD mysql;

-- Connect to MySQL
CALL mysql_attach('mydb', 'localhost', {'user': 'root', 'password': 'xxx'}, 'mysql_data');

-- Query MySQL tables
SELECT * FROM mysql_data.mydb.users;
```

## Data Summarization

DuckDB provides automatic data summarization:

```sql
-- Summarize entire table
SUMMARIZE users;

-- Summarize query results
SUMMARIZE (SELECT * FROM events WHERE date > '2024-01-01');

-- Returns statistics: min, max, median, distinct count, nulls, type
```

## Hive Partitioning

Read partitioned data directories automatically:

```sql
-- Auto-detect Hive partitioning
SELECT * FROM read_parquet('s3://bucket/data/year=*/month=*/day=*.parquet');

-- Manual partition columns
SELECT * FROM read_parquet('data/*.parquet', hive_partitioning=true);
```

## COPY Statement

General-purpose data import/export:

```sql
-- Import
COPY users FROM 'users.csv' (AUTO_DETECT TRUE);
COPY users FROM 'users.parquet' (FORMAT PARQUET);
COPY users FROM 'users.json' (FORMAT JSON, AUTO_DETECT TRUE);

-- Export
COPY users TO 'users.csv' (WITH HEADER);
COPY users TO 'users.parquet' (FORMAT PARQUET);
COPY users TO 'users.json' (FORMAT JSON);
```

## Appender API (Python)

High-performance bulk data loading:

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE data (id INTEGER, name VARCHAR, score DOUBLE)")

appender = con.appender('data')
appender.append_row(1, 'Alice', 95.5)
appender.append_row(2, 'Bob', 87.3)

# Or append batches
appender.append_rows([(3, 'Charlie', 92.1), (4, 'Diana', 88.7)])
appender.close()
```
