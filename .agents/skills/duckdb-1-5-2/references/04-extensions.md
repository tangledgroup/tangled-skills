# Extensions

## Extension Overview

DuckDB uses an **extension system** to add functionality beyond the core database engine. Extensions are modular packages that can be installed and loaded on-demand, keeping the core binary small while providing extensibility.

### Extension Types

| Type | Description | Examples |
|------|-------------|----------|
| **Core Extensions** | Maintained by DuckDB team, shipped with releases | httpfs, parquet, json, icu |
| **Community Extensions** | Third-party maintained, peer-reviewed | Various specialized tools |
| **Custom Extensions** | User-created for specific needs | Proprietary functions, connectors |

### Extension Lifecycle

```
INSTALL  → Download extension from repository
LOAD     → Load extension into current session
UNLOAD   → Remove from current session (keeps installed)
```

## Core Extensions Reference

### httpfs (Primary)

**Purpose**: Read/write files over HTTP(S) and cloud storage (S3, Azure, GCS).

```sql
INSTALL httpfs;
LOAD httpfs;

-- S3 (AWS)
SELECT * FROM 's3://bucket/path/file.parquet';
SELECT * FROM 's3://bucket/path/*.parquet';  -- Wildcard

-- Azure Blob Storage
SELECT * FROM 'az://container/path/file.parquet';

-- Google Cloud Storage
SELECT * FROM 'gs://bucket/path/file.parquet';

-- HTTP/HTTPS URLs
SELECT * FROM 'https://example.com/data.csv';
```

**Configuration**:

```sql
-- AWS credentials (various methods)
SET s3_region = 'us-east-1';
SET s3_access_key_id = 'your-key';
SET s3_secret_access_key = 'your-secret';

-- Or use environment variables
-- export AWS_ACCESS_KEY_ID=...
-- export AWS_SECRET_ACCESS_KEY=...

-- Azure credentials
SET azure_storage_account_name = 'account';
SET azure_storage_sas_token = 'token';

-- Anonymous access (public buckets)
SET s3_anonymous = true;
```

**See**: [httpfs Documentation](https://duckdb.org/docs/current/core_extensions/httpfs/overview)

### parquet (Primary)

**Purpose**: Read and write Apache Parquet files (columnar storage format).

```sql
-- Automatically loaded in most builds, but can be explicit:
INSTALL parquet;
LOAD parquet;

-- Read Parquet files
SELECT * FROM 'data.parquet';
SELECT * FROM read_parquet('data.parquet');

-- Read with options
SELECT * FROM read_parquet('data.parquet', 
    column_filter = 'col1, col2',  -- Only read specific columns
    pushdown_filters = true        -- Push filters to reader
);

-- Write Parquet files
COPY (SELECT * FROM my_table) TO 'output.parquet';
COPY (SELECT * FROM my_table) TO 'output.parquet' (
    COMPRESSION SNAPPY,
    ROW_GROUP_SIZE 100000
);

-- Partitioned Parquet
COPY (SELECT * FROM sales) TO 'sales_output/' (
    PARTITION_BY region, year
);
```

**See**: [Parquet Documentation](https://duckdb.org/docs/current/data/parquet/overview)

### json (Primary)

**Purpose**: JSON parsing, generation, and querying.

```sql
INSTALL json;
LOAD json;

-- Read JSON files
SELECT * FROM 'data.json';
SELECT * FROM read_json_auto('data.json');  -- Auto-detect schema

-- JSON functions
SELECT 
    json_extract('{"name": "Alice", "age": 30}', '$.name') AS name,
    json_extract_string('{"name": "Alice"}', '$.name') AS name_str,
    json_extract_int('{"age": 30}', '$.age') AS age_int;

-- Parse JSON strings
SELECT * FROM read_json('[{"a": 1}, {"a": 2}]');

-- Write JSON
COPY (SELECT * FROM users) TO 'users.json' (FORMAT JSON);
```

**See**: [JSON Documentation](https://duckdb.org/docs/current/data/json/overview)

### icu (Primary)

**Purpose**: International Components for Unicode - time zones, collations, locale-aware operations.

```sql
INSTALL icu;
LOAD icu;

-- Time zone conversions
SELECT 
    CONVERT_TZ('2024-01-15 12:00:00', 'America/New_York', 'Europe/London') AS converted;

-- Locale-aware collation
SET collation = 'de_DE';  -- German collation
SELECT * FROM products ORDER BY name COLLATE "de_DE";

-- Unicode normalization
SELECT 
    UNICODE_NORMALIZE('café', 'NFD') AS normalized;
```

### aws (Secondary)

**Purpose**: AWS SDK integration for enhanced cloud functionality.

```sql
INSTALL aws;
LOAD aws;

-- Enhanced S3 operations with AWS SDK
-- Supports IAM roles, temporary credentials, etc.
```

### azure (Secondary)

**Purpose**: Azure blob storage abstraction.

```sql
INSTALL azure;
LOAD azure;

-- Azure-specific operations
```

### delta (Secondary)

**Purpose**: Delta Lake table format support.

```sql
INSTALL delta;
LOAD delta;

-- Read Delta tables
SELECT * FROM 's3://bucket/delta-table/';

-- Write Delta tables
CALL DELTA_CREATE_TABLE('my_table', '(id INTEGER, name VARCHAR)', 's3://bucket/my-delta-table/');

-- Update Delta tables
CALL DELTA_UPDATE_TABLE('s3://bucket/my-delta-table/', 'name = ''updated''', 'id > 100');

-- Vacuum (cleanup)
CALL DELTA_VACUUM('s3://bucket/my-delta-table/', RETENTION 168);
```

**See**: [Delta Lake Documentation](https://duckdb.org/docs/current/core_extensions/delta)

### iceberg (Secondary)

**Purpose**: Apache Iceberg table format support.

```sql
INSTALL iceberg;
LOAD iceberg;

-- Read Iceberg tables
SELECT * FROM iceberg_scan('s3://bucket/iceberg-table/');

-- Iceberg REST catalogs
SET 'iceberg.rest_catalog.uri' = 'https://catalog.example.com';
SELECT * FROM iceberg_rest_scan('namespace.table');
```

**See**: [Iceberg Documentation](https://duckdb.org/docs/current/core_extensions/iceberg/overview)

### lance (Secondary)

**Purpose**: Lance columnar data format support.

```sql
INSTALL lance;
LOAD lance;

-- Read Lance tables
SELECT * FROM 'data.lance';
```

### vss (Secondary)

**Purpose**: Vector Similarity Search for embeddings and ANN queries.

```sql
INSTALL vss;
LOAD vss;

-- Create vector index
CREATE INDEX vec_idx ON embeddings USING HNSW (vector) 
WITH (distance_metric = 'cosine');

-- Vector search
SELECT * FROM embeddings 
ORDER BY vector <-> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;

-- Approximate nearest neighbors
SELECT * FROM embeddings 
WHERE vector <#> '[0.1, 0.2, 0.3, ...]' < 0.85;
```

### fts (Secondary)

**Purpose**: Full-Text Search with inverted indexes.

```sql
INSTALL fts;
LOAD fts;

-- Create FTS index
CREATE INDEX fts_idx ON documents USING FTSTOKENIZER(content, 'en');

-- Full-text search
SELECT * FROM documents 
WHERE content MATCH 'search query terms';

-- Phrase search
SELECT * FROM documents 
WHERE content MATCH '"exact phrase"';
```

**See**: [Full-Text Search Documentation](https://duckdb.org/docs/current/core_extensions/full_text_search)

### spatial (Secondary)

**Purpose**: Geospatial data types and functions.

```sql
INSTALL spatial;
LOAD spatial;

-- Geometry types
SELECT ST_GeomFromText('POINT(-122.4 37.8)') AS location;

-- Spatial functions
SELECT 
    ST_Distance(geom1, geom2) AS distance_meters,
    ST_Contains(polygon, point) AS is_inside,
    ST_Intersects(geom1, geom2) AS intersects;

-- GIS data import
SELECT * FROM st_read('data.shp');  -- Shapefile
```

### mysql_scanner (Secondary)

**Purpose**: Read from MySQL databases.

```sql
INSTALL mysql;
LOAD mysql;

-- Create MySQL connection
CREATE SECRET mysql_secret (
    TYPE MYSQL,
    KEY_ID 'my_mysql',
    HOST 'localhost',
    PORT 3306,
    DATABASE 'mydb',
    USERNAME 'user',
    PASSWORD 'password'
);

-- Query MySQL tables
SELECT * FROM mysql_scan('my_mysql', 'database', 'table');
```

### postgres_scanner (Secondary)

**Purpose**: Read from PostgreSQL databases.

```sql
INSTALL postgres;
LOAD postgres;

-- Create PostgreSQL connection
CREATE SECRET pg_secret (
    TYPE POSTGRESQL,
    KEY_ID 'my_postgres',
    HOST 'localhost',
    PORT 5432,
    DATABASE 'mydb',
    USERNAME 'user',
    PASSWORD 'password'
);

-- Query PostgreSQL tables
SELECT * FROM postgres_scan('my_postgres', 'public', 'users');
```

### sqlite_scanner (Secondary)

**Purpose**: Read from SQLite database files.

```sql
INSTALL sqlite;
LOAD sqlite;

-- Query SQLite databases
SELECT * FROM sqlite_scan('/path/to/database.sqlite', 'table_name');

-- Multiple tables
SELECT * FROM sqlite_scan('/path/to/database.sqlite', 'schema', 'table');
```

### odbc_scanner (Secondary)

**Purpose**: ODBC connectivity to external databases.

```sql
INSTALL odbc;
LOAD odbc;

-- Create ODBC connection
CREATE SECRET odbc_secret (
    TYPE ODBC,
    KEY_ID 'my_odbc',
    DSN 'MyDataSource'
);

-- Query via ODBC
SELECT * FROM odbc_scan('my_odbc', 'SELECT * FROM table');
```

### excel (Secondary)

**Purpose**: Read and write Excel files.

```sql
INSTALL excel;
LOAD excel;

-- Read Excel files
SELECT * FROM 'data.xlsx';
SELECT * FROM read_excel('data.xlsx', sheet = 'Sheet1');

-- Write Excel files
COPY (SELECT * FROM report) TO 'report.xlsx' (FORMAT EXCEL);
```

### avro (Secondary)

**Purpose**: Read Apache Avro files.

```sql
INSTALL avro;
LOAD avro;

-- Read Avro files
SELECT * FROM 'data.avro';
SELECT * FROM read_avro('data.avro');
```

### inet (Secondary)

**Purpose**: IP address and network functions.

```sql
INSTALL inet;
LOAD inet;

-- IP address operations
SELECT 
    '192.168.1.1'::INET AS ip,
    '10.0.0.0/8'::CIDR AS network,
    '192.168.1.1'::INET >>= '10.0.0.0/8'::CIDR;  -- IP in network

-- Network functions
SELECT 
    NETWORK('192.168.1.1/24') AS network_addr,
    BROADCAST('192.168.1.1/24') AS broadcast_addr;
```

### autocomplete (Secondary)

**Purpose**: Enhanced autocomplete in DuckDB CLI shell.

```sql
INSTALL autocomplete;
LOAD autocomplete;

-- Automatically enhances CLI experience
-- No additional configuration needed
```

### encodings (Secondary)

**Purpose**: Character encoding support from ICU data repository.

```sql
INSTALL encodings;
LOAD encodings;

-- Encoding conversions
SELECT CONVERT('text' USING 'UTF8', 'ISO-8859-1');
```

### jemalloc (Secondary)

**Purpose**: Replace system allocator with jemalloc for performance.

```sql
INSTALL jemalloc;
LOAD jemalloc;

-- Automatic memory allocation optimization
-- No configuration needed
```

### tpcds / tpch (Secondary)

**Purpose**: TPC-DS and TPC-H benchmark data generation.

```sql
INSTALL tpch;
LOAD tpch;

-- Generate TPC-H data (scale factor 1)
CALL DBGEN(1);

-- Query generated tables
SELECT * FROM customer LIMIT 10;
SELECT * FROM orders LIMIT 10;

-- Run benchmark queries
SELECT * FROM tpch.q1;
```

## Extension Management

### Installation Methods

#### From Repository (Recommended)

```sql
-- Install from official repository
INSTALL extension_name;

-- Load into current session
LOAD extension_name;

-- Combine in one statement
INSTALL httpfs;
LOAD httpfs;
```

#### From Local File

```sql
-- Install from local .duckdb_extension file
INSTALL 'file:///path/to/extension.duckdb_extension';
LOAD extension_name;
```

#### From URL

```sql
-- Install from custom URL
INSTALL 'https://example.com/extensions/extension.duckdb_extension';
LOAD extension_name;
```

### Session vs Persistent

```sql
-- Extensions loaded in session are not persistent
-- To make permanent, add to .duckdbrc or install script:

-- ~/.duckdb/.duckdbrc (CLI)
INSTALL httpfs;
LOAD httpfs;
INSTALL parquet;
LOAD parquet;
```

### Unload Extensions

```sql
-- Remove from current session only
UNLOAD httpfs;

-- Extension remains installed, can be reloaded
LOAD httpfs;
```

### Check Installed Extensions

```sql
-- List all installed extensions
SELECT * FROM duckdb_extensions();

-- List loaded extensions
SELECT * FROM duckdb_loaded_extensions();

-- Check extension status
SELECT 
    name,
    version,
    installed,
    loaded
FROM duckdb_extensions()
WHERE name IN ('httpfs', 'parquet', 'json');
```

## Secrets Manager

DuckDB 1.0+ includes a built-in secrets manager for secure credential storage:

```sql
-- Create secret (stored in memory by default)
CREATE SECRET (
    TYPE S3,
    KEY_ID 'my_s3',
    REGION 'us-east-1',
    ACCESS_KEY_ID 'your-key',
    SECRET_ACCESS_KEY 'your-secret'
);

-- Create secret with persistence
CREATE SECRET (
    TYPE S3,
    STORAGE 'FILE',  -- Store in file
    KEY_PATH '/path/to/credentials.json'
);

-- List secrets
SHOW SECRETS;

-- Drop secret
DROP SECRET my_s3;
```

## Extension Best Practices

### Performance Considerations

1. **Load only needed extensions**: Each extension adds memory overhead
2. **Use core extensions when possible**: Better tested and optimized
3. **Unload unused extensions**: Free resources when done

### Security Considerations

1. **Store secrets securely**: Use environment variables or secret managers
2. **Validate extension sources**: Only install from trusted repositories
3. **Review permissions**: Some extensions require network access

### Development Workflow

```sql
-- Standard setup script for data science workflow
INSTALL httpfs;
LOAD httpfs;
INSTALL parquet;
LOAD parquet;
INSTALL json;
LOAD json;
INSTALL icu;
LOAD icu;

-- Set common configuration
SET s3_region = 'us-east-1';
SET threads = 4;
SET memory_limit = '4GB';
```

## Troubleshooting Extensions

### Common Issues

| Issue | Solution |
|-------|----------|
| Extension not found | Check spelling, ensure repository access |
| Load fails | Verify compatible DuckDB version |
| Network errors | Check internet connection, proxy settings |
| Permission denied | Verify file permissions for local installs |

### Debug Commands

```sql
-- Check extension repository
SELECT * FROM duckdb_extension_types();

-- Get detailed error info
PRAGMA show_versions;

-- Check loaded extensions
SELECT current_setting('extension_directory');
```

## Third-Party Extensions

DuckDB supports community-maintained extensions:

### motherduck (Third Party)

**Purpose**: Connect to MotherDuck cloud service.

```sql
INSTALL 'https://motherduck.com/duckdb/extensions/motherduck.duckdb_extension';
LOAD motherduck;

-- Connect to MotherDuck
ATTACH 'md:database_name' AS md_db;
USE md_db;
```

### ui (Third Party)

**Purpose**: Local web UI for DuckDB.

```sql
INSTALL 'https://extensions.duckdb.org/ui.duckdb_extension';
LOAD ui;

-- Start UI server
CALL ui_start();
```

### unity_catalog (Third Party)

**Purpose**: Databricks Unity Catalog integration.

```sql
INSTALL unity_catalog;
LOAD unity_catalog;

-- Connect to Unity Catalog
SELECT * FROM unity_catalog_scan('catalog.schema.table');
```

## Extension Development

For creating custom extensions, see the [DuckDB Extension SDK](https://duckdb.org/docs/developing/extension_setup).

Key components:
- C++ implementation of functions/operators
- Build configuration (CMake)
- Metadata files (manifest.json)
- Testing framework
