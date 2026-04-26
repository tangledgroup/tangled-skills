# Virtual Tables and Extensions

## Virtual Table Mechanism

Virtual tables are objects registered with an open SQLite database connection. From SQL's perspective, they look like regular tables — but behind the scenes, queries invoke callback methods of the virtual table object instead of reading from disk.

Key characteristics:
- Cannot create triggers on virtual tables
- Cannot create additional indexes (indexes must be built into the implementation)
- Cannot use `ALTER TABLE ... ADD COLUMN`
- Individual implementations may impose additional constraints (read-only, etc.)

### Types of Virtual Tables

**Regular virtual tables** — Created with `CREATE VIRTUAL TABLE`:
```sql
CREATE VIRTUAL TABLE search USING fts5(content);
```

**Eponymous virtual tables** — Accessed by name without explicit creation:
```sql
SELECT * FROM sqlite_schema;
SELECT * FROM sqlite_master;
```

**Table-valued functions** — Called with function syntax:
```sql
SELECT * FROM json_each('{"a":1,"b":2}');
SELECT * FROM generate_series(1, 10);
```

## Loadable Extensions

Run-time loadable extensions are shared libraries (`.so` on Linux, `.dll` on Windows, `.dylib` on macOS) that register new virtual tables, functions, or other capabilities.

Enable at compile time with `-DSQLITE_ENABLE_LOAD_EXTENSION=1`. At runtime:

```sql
-- Enable loading extensions
PRAGMA legacy_file_format = OFF;
SELECT load_extension('/path/to/extension.so');

-- Or via CLI
.load /path/to/extension.so
```

Security note: Loadable extensions can execute arbitrary code. Use `--safe` mode in the CLI to prevent extension loading, or disable with `-DSQLITE_OMIT_LOAD_EXTENSION`.

## Built-in Extensions

### CSV Virtual Table

Read RFC 4180 formatted CSV files directly as tables:

```sql
CREATE VIRTUAL TABLE csv_data USING csv(filename '/path/to/data.csv');
SELECT * FROM csv_data;
```

Options:
- `filename` — Path to the CSV file
- `cols=N` — Number of columns
- `sep=CHAR` — Column separator (default: comma)
- `has_headers=YES|NO` — First row contains headers

Read-only. Compile with `-DSQLITE_ENABLE_CSV=1`.

### DBSTAT Virtual Table

Reports on the sizes and geometries of tables in a database:

```sql
CREATE VIRTUAL TABLE dbstat USING dbstat(main);
SELECT name, path, pgoffset, pgsize, nnullfilter FROM dbstat;
```

Columns include `name` (table/index name), `path` (B-tree path), `pgoffset` (page offset), `pgsize` (page size), `nnullfilter` (number of null-filtered entries). Used by the `sqlite3_analyzer` utility.

### generate_series

Table-valued function that generates a sequence of integers:

```sql
-- Simple range
SELECT * FROM generate_series(1, 10);

-- With step
SELECT * FROM generate_series(0, 100, 10);

-- Cross join for date ranges
SELECT date('2024-01-01', '+' || value || ' days') AS day
FROM generate_series(0, 364);
```

### CARRAY

Table-valued function that exposes a C-language array as a SQL table:

```sql
-- Used primarily from the C API to pass arrays into SQL
SELECT * FROM carray('my_array', 5);
```

Takes an array pointer and length, returns one row per element with columns `key` (index) and `value`.

### Spellfix1

Spelling correction for full-text search:

```sql
CREATE VIRTUAL TABLE spellfix USING spellfix1(word TEXT);

-- Find corrections for a misspelled word
SELECT word, distance FROM spellfix
WHERE word MATCH 'recieve'
ORDER BY distance LIMIT 5;
```

The `distance` column shows the edit distance (number of character changes). Best used in conjunction with FTS3/FTS4.

### Zipfile

Read and write ZIP archives as database tables:

```sql
-- Open a ZIP file as a virtual table
CREATE VIRTUAL TABLE zf USING zipfile('/path/to/archive.zip');

-- List contents
SELECT name, size, mtime FROM zf;

-- Extract data
SELECT data FROM zf WHERE name = 'document.txt';

-- Write to ZIP
INSERT INTO zf(name, data) VALUES ('newfile.txt', X'48656C6C6F');
```

Compile with `-DSQLITE_ENABLE_ZIPFILE=1`.

### Percentile Extension

Aggregate functions for percentile calculations:

- `median(X)` — Median value
- `percentile(X, P)` — Value at percentile P (0-100)
- `percentile_cont(X, P)` — Continuous percentile (interpolated)
- `percentile_disc(X, P)` — Discrete percentile

```sql
SELECT
    median(salary) AS median_salary,
    percentile(salary, 25) AS q1,
    percentile(salary, 75) AS q3,
    percentile_cont(salary, 90) AS p90
FROM employees;
```

## Creating Custom Virtual Tables

The virtual table interface consists of callback methods implemented in C:

- `xCreate` — Create a new virtual table instance
- `xConnect` — Connect to an existing virtual table
- `xBestIndex` — Determine the best query plan (inputs: constraints and ORDER BY; outputs: index number and cost estimate)
- `xDisconnect` / `xDestroy` — Cleanup
- `xOpen` — Open a cursor for iterating results
- `xClose` — Close a cursor
- `xEof` — Check if cursor is at end of results
- `xFilter` — Start a search with given constraints
- `xNext` — Advance cursor to next row
- `xColumn` — Extract a column value from the current row
- `xRowid` — Get the rowid of the current row
- `xUpdate` — Insert/update/delete rows
- `xFindFunction` — Lookup built-in functions
- `xBegin`, `xSync`, `xCommit`, `xRollback` — Transaction support
- `xRename` — Handle table rename
- `xSavepoint`, `xRelease`, `xRollbackTo` — Savepoint support

Register with `sqlite3_create_module(db, "module_name", &module, NULL)`.
