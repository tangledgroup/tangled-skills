# Extensions and Configuration

## Extension System

DuckDB extends its functionality through a modular extension system. Extensions can be installed and loaded on demand.

### Installing and Loading Extensions

```sql
-- Install from default repository
INSTALL httpfs;

-- Load into current session
LOAD httpfs;

-- Auto-load on first use (recommended)
SET autoinstall_known_extensions=true;
SET autoload_known_extensions=true;

-- With these settings, extensions load automatically when you use their features
SELECT * FROM read_parquet('s3://bucket/data.parquet');  -- auto-loads httpfs
```

### Extension Repository

Extensions are downloaded from the DuckDB extension repository. Custom repositories can be configured:

```sql
-- Set custom extension repository
SET custom_extension_repository='https://my-extensions.example.com';

-- Install specific version
INSTALL httpfs FROM 'https://extensions.duckdb.org/...';
```

## Core Extensions

### httpfs — HTTP(S) and Cloud Storage Access

Provides access to files over HTTP/HTTPS and cloud storage (S3, GCS, Azure Blob, Cloudflare R2).

```sql
LOAD httpfs;

-- S3 access
SELECT * FROM read_parquet('s3://bucket/data.parquet');

-- Set credentials
SET s3_region='us-east-1';
SET s3_access_key_id='AKIA...';
SET s3_secret_access_key='secret...';

-- HTTPS
SELECT * FROM read_csv_auto('https://example.com/data.csv');

-- Google Cloud Storage
SELECT * FROM read_parquet('gs://bucket/data.parquet');
```

### Spatial — Geospatial Data Support

Provides PostGIS-compatible spatial functions and types.

```sql
LOAD spatial;

-- Create geometry
SELECT ST_Point(-73.97, 40.77);
SELECT ST_GeomFromText('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))');

-- Spatial functions
SELECT ST_Distance(
    ST_Point(-73.97, 40.77),
    ST_Point(-74.00, 40.71)
);

-- R-Tree indexes for spatial queries
CREATE INDEX idx_geom ON locations USING RTREE (geom);
```

### Full-Text Search

Provides full-text search capabilities with tokenization and ranking.

```sql
LOAD full_text_search;

-- Create FTS index
CREATE FULLTEXT SEARCH INDEX fts_idx ON articles (title, body);

-- Search
SELECT * FROM articles WHERE to_tsquery('database AND sql') @@ (title, body);

-- With ranking
SELECT title, ts_rank(to_tsquery('database'), body) as rank
FROM articles
WHERE to_tsquery('database') @@ body
ORDER BY rank DESC;
```

### Iceberg — Apache Iceberg Table Format

Read and write Apache Iceberg tables.

```sql
LOAD iceberg;

-- Query Iceberg table
SELECT * FROM iceberg_scan('s3://bucket/iceberg-table/');

-- With catalog
SELECT * FROM iceberg_scan('s3://bucket/table/',
    catalog='rest',
    options={
        'uri': 'https://catalog.example.com',
        'warehouse': 's3://bucket/'
    }
);
```

### Delta — Delta Lake Format

Read Delta Lake tables.

```sql
LOAD delta;

-- Query Delta table
SELECT * FROM delta_scan('s3://bucket/delta-table/');
```

### Excel — Microsoft Excel Support

Read and write Excel files (.xlsx, .xls).

```sql
LOAD excel;

SELECT * FROM read_excel('report.xlsx');
SELECT * FROM read_excel('report.xlsx', sheet_name='Q1');
COPY (SELECT * FROM data) TO 'output.xlsx' (FORMAT EXCEL);
```

### Other Core Extensions

- **autocomplete** — CLI auto-completion
- **aws** — AWS-specific functionality
- **azure** — Azure cloud storage
- **encodings** — Additional compression codecs (zstd, lz4)
- **httpfs** — HTTP/S3/GCS access
- **icu** — International Components for Unicode (advanced collation)
- **inet** — IP address type and functions
- **jemalloc** — Alternative memory allocator
- **lance** — Lance columnar data format
- **mysql** — MySQL database connector
- **odbc** — ODBC driver
- **postgres** — PostgreSQL database connector
- **spatial** — Geospatial functions
- **sqlite** — SQLite database connector
- **tpcds / tpch** — Benchmark data generators
- **vortex** — Vortex vectorized format

## Configuration

### Pragmas and Settings

```sql
-- View all settings
SELECT * FROM duckdb_settings();

-- Thread count
SET threads=4;

-- Memory limit
SET memory_limit='4GB';

-- Temporary directory
SET temp_directory='/tmp/duckdb';

-- Preserve insertion order
SET preserve_insertion_order=true;

-- Allow unsigned types
SET allow_unsigned_int_types=true;

-- Query timeout
SET query_timeout=30000;  -- milliseconds
```

### Python Configuration

```python
import duckdb

# Pass config at connection time
con = duckdb.connect(
    'my.db',
    config={
        'threads': '4',
        'memory_limit': '4GB',
        'preserve_insertion_order': 'true',
        'temp_directory': '/tmp/duckdb'
    }
)
```

### Secrets Manager

Manage cloud credentials securely:

```sql
-- Create secret for S3
CREATE SECRET (
    TYPE S3,
    PROVIDER CREDENTIAL_CHAIN
);

-- Create secret with explicit credentials
CREATE SECRET my_s3 (
    TYPE S3,
    KEY_ID 'AKIA...',
    SECRET 'secret...',
    REGION 'us-east-1'
);

-- List secrets
SHOW SECRETS;

-- Drop secret
DROP SECRET my_s3;
```

## Performance Tuning

### Key Settings for Performance

```sql
-- Increase threads for parallel execution
SET threads=(SELECT COUNT(*) FROM range(16));  -- match CPU cores

-- Memory management
SET memory_limit='8GB';
SET mmap=true;

-- For large imports
SET temp_directory='/fast-disk/tmp';
SET max_temp_directory_size='50GB';

-- Parquet optimization
SET parquet_read_parallelism=true;
```

### Query Profiling

```sql
-- Explain query plan
EXPLAIN SELECT COUNT(*) FROM large_table GROUP BY category;

-- Profile with execution statistics
EXPLAIN ANALYZE SELECT * FROM large_table WHERE x > 100;

-- Physical plan details
EXPLAIN (COSTS OFF, FORMAT TEXT)
SELECT * FROM large_table WHERE x > 100;
```

### Database Size Management

```sql
-- Check database size
SELECT * FROM duckdb_database_size();

-- Vacuum to reclaim space
VACUUM;
VACUUM table_name;

-- Check table sizes
SELECT * FROM scan('my.db');
```

## Concurrency Model

DuckDB uses a shared-worker model:

- Multiple connections share the same database and worker threads
- Read queries can execute concurrently
- Write operations are serialized within a single process
- For multi-process access, use `ATTACH` with read-only mode

```python
# Multiple connections sharing workers
con1 = duckdb.connect('shared.db')
con2 = duckdb.connect('shared.db')

# Both share the same in-memory cache and workers
con1.execute("CREATE TABLE t AS SELECT range as x FROM range(1000000)")
con2.execute("SELECT COUNT(*) FROM t")  # Sees con1's table
```
