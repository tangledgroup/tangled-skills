# Additional SQLite Extensions

Comprehensive guide to SQLite's built-in and loadable extensions beyond FTS5 and JSON.

## R-Tree Spatial Indexing

R-Tree extension provides efficient multi-dimensional spatial indexing.

### Creating R-Tree Tables

```sql
-- Basic R-Tree for 2D rectangles
CREATE VIRTUAL TABLE buildings USING rtree(
    id,                -- Integer primary key
    x0, y0,            -- Minimum x and y coordinates
    x1, y1             -- Maximum x and y coordinates
);

-- R-Tree with external content (data stored separately)
CREATE VIRTUAL TABLE geo_features USING rtree(
    id,
    minx, miny,        -- Bounding box minimum
    maxx, maxy,        -- Bounding box maximum
    data              -- Reference to external table
);

-- Create external content table
CREATE TABLE feature_data (
    id INTEGER PRIMARY KEY,
    name TEXT,
    geometry TEXT,
    attributes JSON
);
```

### Inserting Spatial Data

```sql
-- Insert rectangles (x0, y0 is bottom-left; x1, y1 is top-right)
INSERT INTO buildings VALUES (1, 0.0, 0.0, 10.0, 20.0);
INSERT INTO buildings VALUES (2, 5.0, 5.0, 15.0, 25.0);
INSERT INTO buildings VALUES (3, 20.0, 0.0, 30.0, 10.0);

-- With external content
INSERT INTO geo_features VALUES (1, -74.0, 40.6, -73.9, 40.8, 1);
INSERT INTO feature_data VALUES (1, 'Manhattan', 'POLYGON(...)', '{"population": 1600000}');
```

### Spatial Queries

```sql
-- Find all rectangles containing a point (x=7, y=10)
SELECT * FROM buildings 
WHERE 7 >= x0 AND 7 <= x1 AND 10 >= y0 AND 10 <= y1;

-- Find all rectangles overlapping a region
SELECT * FROM buildings 
WHERE x0 < 20 AND x1 > 5 AND y0 < 30 AND y1 > 0;

-- Join with external content
SELECT f.name, f.attributes
FROM geo_features g
JOIN feature_data f ON g.id = f.id
WHERE g.minx < -73.9 AND g.maxx > -74.0 
  AND g.miny < 40.8 AND g.maxy > 40.6;

-- Find nearest neighbors (requires additional logic)
SELECT *, 
    (x0 - 7) * (x0 - 7) + (y0 - 10) * (y0 - 10) AS distance_sq
FROM buildings
WHERE 7 >= x0 AND 7 <= x1 AND 10 >= y0 AND 10 <= y1
ORDER BY distance_sq
LIMIT 5;
```

### R-Tree Options

```sql
-- Create R-Tree with custom options
CREATE VIRTUAL TABLE spatial USING rtree(
    id,
    minx, maxx,
    miny, maxy,
    minz, maxz,     -- 3D support
    interleave=0,   -- Use Hilbert curve for better locality
    sparse=1        -- Allow NULL values in dimensions
);
```

## Sessions Extension

The Sessions extension tracks changes to a database for undo/redo and synchronization.

### Creating and Using Sessions

```sql
-- Load the session extension (if not compiled in)
LOAD EXTENSION 'libsqlite3session.so';

-- Create a session
CREATE SESSION my_session;

-- Attach tables to track
ATTACH TABLE users TO my_session;
ATTACH TABLE orders TO my_session;

-- Make some changes
UPDATE users SET name = 'Alice Smith' WHERE id = 1;
DELETE FROM orders WHERE id = 100;
INSERT INTO logs (message) VALUES ('Session started');

-- Get changelog as SQL
SELECT * FROM my_session_changes;

-- Export changes to a blob
SELECT session_changes(my_session, 0, 0, 0);

-- Apply changes to another database
-- (In receiving database)
SELECT session_attach('my_session', :changes_blob);
SELECT session_pull(my_session);

-- Undo changes
SELECT session_revert(my_session);

-- Drop session
DROP SESSION my_session;
```

### Change Tracking Options

```sql
-- Track only specific tables
ATTACH TABLE users TO my_session;
-- orders table changes are not tracked

-- Exclude columns from tracking
CREATE SESSION partial_session;
ATTACH TABLE users EXCLUDE (updated_at, version) TO partial_session;

-- Get change statistics
SELECT * FROM my_session_stats;
```

### Undo/Redo Implementation

```sql
-- Enable undo support
PRAGMA session.undo_log = ON;

-- Make changes
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- Undo last change
SELECT session_revert(my_session);

-- Redo (if saved)
SELECT session_apply(my_session, :saved_changes);
```

## CSV Virtual Table

Query CSV files directly as if they were tables.

### Creating CSV Virtual Tables

```sql
-- Load CSV module (if not compiled in)
LOAD EXTENSION 'libsqlite3csv.so';

-- Create virtual table pointing to CSV file
CREATE VIRTUAL TABLE sales_data USING csv(
    filename '/data/sales.csv',
    has_headers 1,
    separator ','
);

-- Query the CSV directly
SELECT * FROM sales_data WHERE amount > 1000;
SELECT product, SUM(amount) AS total 
FROM sales_data 
GROUP BY product;

-- Join CSV with regular tables
SELECT s.product, c.category_name, SUM(s.amount)
FROM sales_data s
JOIN categories c ON s.category_id = c.id
GROUP BY s.product, c.category_name;
```

### CSV Options

```sql
-- Custom separator
CREATE VIRTUAL TABLE tab_data USING csv(
    filename '/data/tabular.tsv',
    separator '\t'
);

-- No headers (provide schema)
CREATE VIRTUAL TABLE raw_data(id INTEGER, name TEXT, value REAL) 
USING csv(filename '/data/raw.csv', has_headers 0);

-- Quote character
CREATE VIRTUAL TABLE quoted USING csv(
    filename '/data/quoted.csv',
    quotechar '"'
);

-- Skip rows
CREATE VIRTUAL TABLE skip_header USING csv(
    filename '/data/skip.csv',
    skip 2  -- Skip first 2 rows
);
```

### Writing CSV Files

```sql
-- Export query results to CSV
.output /output/results.csv
.mode csv
.headers on
SELECT * FROM users WHERE active = 1;
.output stdout
```

## Spellfix1 Extension

Spelling correction for full-text search.

### Creating Spellfix Tables

```sql
-- Create spellfix virtual table
CREATE VIRTUAL TABLE dictionary USING spellfix1(
    word,              -- Word column
    langtable          -- Language statistics table
);

-- Populate with known words
INSERT INTO dictionary(word) VALUES ('hello');
INSERT INTO dictionary(word) VALUES ('world');
INSERT INTO dictionary(word) VALUES ('sqlite');
INSERT INTO dictionary(word) VALUES ('database');

-- Train on corpus (optional, for better suggestions)
INSERT INTO dictionary(langtable) 
SELECT word, freq FROM word_frequency_corpus;
```

### Finding Spelling Corrections

```sql
-- Find corrections for misspelled word
SELECT * FROM dictionary 
WHERE dictionary MATCH spellfix_query('helo');
-- Returns: hello

-- Get multiple suggestions
SELECT * FROM dictionary 
WHERE dictionary MATCH spellfix_query('sqllite');
-- Returns: sqlite

-- Limit results
SELECT * FROM dictionary 
WHERE dictionary MATCH spellfix_query('databse')
LIMIT 3;
```

### Integration with FTS5

```sql
-- Create FTS5 table for search
CREATE VIRTUAL TABLE documents USING fts5(content, title);

-- Create spellfix for corrections
CREATE VIRTUAL TABLE spelling USING spellfix1(word);

-- Search with auto-correction
SELECT d.*
FROM documents d
WHERE d MATCH :query
UNION ALL
SELECT d.*
FROM documents d, spelling s
WHERE s MATCH spellfix_query(:query)
  AND d MATCH s.word
LIMIT 10;
```

## Percentile Extension

Aggregate functions for calculating percentiles and medians.

### Using Percentile Functions

```sql
-- Calculate median
SELECT percentile_median(salary) AS median_salary
FROM employees;

-- Calculate specific percentile
SELECT percentile(salary, 0.25) AS q1,
       percentile(salary, 0.50) AS median,
       percentile(salary, 0.75) AS q3
FROM employees;

-- Percentile by department
SELECT department,
       percentile_median(salary) AS median_salary,
       percentile(salary, 0.90) AS p90_salary
FROM employees
GROUP BY department;
```

### Advanced Percentile Functions

```sql
-- Continuous percentile (interpolation)
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY salary)
FROM employees;

-- Discrete percentile (exact value)
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY salary)
FROM employees;

-- Multiple percentiles in one query
SELECT 
    percentile(salary, 0.10) AS p10,
    percentile(salary, 0.25) AS q1,
    percentile(salary, 0.50) AS median,
    percentile(salary, 0.75) AS q3,
    percentile(salary, 0.90) AS p90
FROM employees;
```

## DBSTAT Virtual Table

Database statistics and analysis.

### Querying Database Statistics

```sql
-- View table and index sizes
SELECT * FROM dbstat;

-- Get size of specific table
SELECT name, SUM(pages) * page_size AS size_bytes
FROM dbstat
WHERE rootpage IN (SELECT rootpage FROM sqlite_master WHERE name = 'users')
GROUP BY name;

-- Analyze index usage
SELECT 
    m.name AS table_name,
    s.name AS index_name,
    s.level,
    s.pages * (SELECT page_size FROM pragma_page_size) AS size_bytes
FROM dbstat s
JOIN sqlite_master m ON s.rootpage = m.rootpage;

-- Find largest tables
SELECT 
    name,
    type,
    SUM(pages) * (SELECT page_size FROM pragma_page_size) AS size_bytes
FROM dbstat d
JOIN sqlite_master m ON d.rootpage = m.rootpage
GROUP BY name, type
ORDER BY size_bytes DESC;
```

### Using sqlite3_analyzer

```bash
# Generate HTML analysis report
sqlite3_analyzer database.db > analysis.html

# Check in CLI
SELECT * FROM dbstat ORDER BY pages DESC;
```

## Generate Series (Table-Valued Function)

Generate sequences of values.

### Creating Series

```sql
-- Load series module if needed
LOAD EXTENSION 'libsqlite3series.so';

-- Generate simple sequence
SELECT * FROM generate_series(1, 10);
-- Returns: 1, 2, 3, ..., 10

-- With step
SELECT * FROM generate_series(0, 100, 10);
-- Returns: 0, 10, 20, ..., 100

-- Generate dates
SELECT date('2024-01-01', '+' || value || ' days') AS day
FROM generate_series(0, 30);

-- Create calendar table
CREATE TABLE calendar AS
SELECT 
    value AS day_number,
    date('2024-01-01', '+' || value || ' days') AS date,
    strftime('%w', date('2024-01-01', '+' || value || ' days')) AS weekday
FROM generate_series(0, 365);
```

### Practical Applications

```sql
-- Fill gaps in time series
SELECT 
    COALESCE(t.date, g.date) AS date,
    COALESCE(t.value, 0) AS value
FROM generate_series(1, 31) g
LEFT JOIN (
    SELECT date('2024-01-01', '+' || (value - 1) || ' days') AS date, 
           SUM(amount) AS value
    FROM transactions
    GROUP BY date
) t ON g.value = strftime('%d', t.date)
ORDER BY g.date;

-- Create test data
INSERT INTO benchmark_data (id, value)
SELECT 
    value,
    random() % 1000
FROM generate_series(1, 10000);
```

## CARRAY Extension

Use C-language arrays in SQL queries.

### Creating and Using CARRAY

```sql
-- Load carray extension
LOAD EXTENSION 'libsqlite3carray.so';

-- Create array from values
SELECT * FROM carray(1, 2, 3, 4, 5);

-- Access array elements (0-indexed)
SELECT value FROM carray(10, 20, 30, 40, 50) WHERE key = 2;
-- Returns: 30

-- Iterate over array
SELECT key AS index, value 
FROM carray('a', 'b', 'c', 'd', 'e');

-- Use in queries
SELECT * FROM products
WHERE category_id IN (
    SELECT value FROM carray(1, 3, 5, 7)
);
```

## Zipfile Virtual Table

Read and write ZIP archives as databases.

### Reading ZIP Files

```sql
-- Load zipfile extension
LOAD EXTENSION 'libsqlite3zipfile.so';

-- Create virtual table for ZIP
CREATE VIRTUAL TABLE my_archive USING zipfile('/path/to/archive.zip');

-- List contents
SELECT * FROM my_archive;

-- Extract file content
SELECT payload FROM my_archive WHERE name = 'document.txt';

-- Query multiple files in archive
SELECT name, size, mtime 
FROM my_archive 
WHERE name LIKE '%.json';
```

### Writing ZIP Files

```sql
-- Create new ZIP archive
CREATE VIRTUAL TABLE output USING zipfile('/output/archive.zip', 'w');

-- Add files to archive
INSERT INTO output(name, payload, mtime) 
VALUES ('readme.txt', X'526561646D65', strftime('%s', 'now'));

-- Add from query results
INSERT INTO output(name, payload)
SELECT name || '.txt', content
FROM documents
WHERE category = 'export';
```

## Loading Extensions

### Compile-Time vs Run-Time Extensions

```sql
-- Check compiled-in extensions
SELECT * FROM pragma_compile_options LIKE '%EXT%';

-- Load run-time extension (Unix)
LOAD EXTENSION '/usr/lib/sqlite3/libsqlite3fts5.so';

-- Load run-time extension (Windows)
LOAD EXTENSION 'C:\Program Files\SQLite\extensions\fts5.dll';

-- Load from relative path
LOAD EXTENSION './lib/custom_extension.so';
```

### Security Considerations

```sql
-- Enable load extension (disabled by default in many builds)
PRAGMA load_extension = 1;

-- Load only from trusted directories
-- Set SQLITE_EXTENSION_DIR environment variable

-- Disable after loading needed extensions
PRAGMA load_extension = 0;
```

## Extension Discovery

```sql
-- List all available virtual table modules
SELECT name, rootpage 
FROM sqlite_master 
WHERE type = 'module';

-- Check for compiled-in extensions
SELECT 
    'JSON1' AS extension,
    json_valid('{"test": true}') IS NOT NULL AS available
UNION ALL
SELECT 
    'FTS5',
    EXISTS (SELECT 1 FROM sqlite_master WHERE type = 'module' AND name = 'fts5');

-- Test extension availability
SELECT 
    CASE 
        WHEN json_extract('{"key": "value"}', '$.key') = 'value' 
        THEN 'JSON1 available' 
        ELSE 'JSON1 not available' 
    END AS status;
```

## Best Practices

1. **Check availability** - Test if extension is compiled in before using
2. **Load once** - Extensions loaded at connection start
3. **Security first** - Only load from trusted sources
4. **Document dependencies** - List required extensions in schema docs
5. **Test portability** - Some extensions may not be available in all builds
6. **Use virtual tables** - Prefer built-in modules when possible

## Related Documentation

- [Virtual Tables](06-virtual-tables.md) - Creating custom virtual tables
- [FTS5](05-fts5.md) - Full-text search extension details
- [JSON Functions](04-json-jsonb.md) - JSON1 extension reference
- [C API](02-c-api.md) - Programmatic extension loading
