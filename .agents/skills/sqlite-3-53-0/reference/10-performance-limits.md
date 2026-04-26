# Performance and Limits

## Key Pragmas

Pragmas modify SQLite operation or query internal state. They are SQLite-specific and not portable to other databases.

**Journaling:**
```sql
PRAGMA journal_mode;           -- Query current mode
PRAGMA journal_mode=WAL;       -- Set WAL mode
PRAGMA journal_size_limit=134217728;  -- Max journal size (bytes)
PRAGMA wal_autocheckpoint=1000;       -- Auto-checkpoint page count
```

**Performance tuning:**
```sql
PRAGMA synchronous=NORMAL;     -- Balance safety and speed (OFF, NORMAL, FULL)
PRAGMA cache_size=-64000;      -- Cache size in KB (negative = KB, positive = pages)
PRAGMA temp_store=MEMORY;      -- Store temp tables in memory (DEFAULT, FILE, MEMORY)
PRAGMA mmap_size=268435456;    -- Max memory-mapped I/O size (bytes)
PRAGMA page_size=4096;         -- Database page size (must be set before any data)
PRAGMA busy_timeout=5000;      -- Milliseconds to wait on locked database
```

**Integrity and security:**
```sql
PRAGMA integrity_check;        -- Verify database integrity
PRAGMA foreign_keys=ON;        -- Enable foreign key enforcement
PRAGMA case_sensitive_like=ON; -- Make LIKE case-sensitive
PRAGMA user_version=N;         -- Set user-defined version number
PRAGMA application_id=N;       -- Set application ID in database header
```

**Querying pragmas as table-valued functions:**
```sql
SELECT * FROM pragma_table_info('users');
SELECT * FROM pragma_index_list('users');
SELECT * FROM pragma_foreign_key_list('orders');
```

## Compile-Time Options

Key compile-time options that affect behavior:

- `-DSQLITE_ENABLE_MATH_FUNCTIONS` — Enable math functions
- `-DSQLITE_ENABLE_FTS5` — Enable FTS5 full-text search
- `-DSQLITE_ENABLE_RTREE` — Enable R-Tree module
- `-DSQLITE_ENABLE_SESSION` — Enable Sessions extension
- `-DSQLITE_ENABLE_LOAD_EXTENSION` — Enable loadable extensions
- `-DSQLITE_ENABLE_JSON1` — JSON functions (default in 3.38+, use `-DSQLITE_OMIT_JSON` to disable)
- `-DSQLITE_THREADSAFE=0|1|2` — Threading mode (0=single-thread, 1=multi-thread, 2=serialized)
- `-DSQLITE_DEFAULT_CACHE_SIZE=N` — Default cache size in pages
- `-DSQLITE_DEFAULT_JOURNAL_SIZE_LIMIT=N` — Default journal size limit
- `-DSQLITE_MAX_VARIABLE_NUMBER=N` — Maximum number of variables in a statement
- `-DSQLITE_MAX_EXPR_DEPTH=N` — Maximum expression tree depth

## Implementation Limits

SQLite has well-defined limits, many configurable at compile-time and some at run-time:

- **Maximum string or BLOB length:** 1,000,000,000 bytes (default). Configurable via `SQLITE_MAX_LENGTH`.
- **Maximum database size:** 281 TB (exabytes with large pages). Configurable via `SQLITE_MAX_MMAP_SIZE`.
- **Maximum number of columns in a table:** 2000 (default). Configurable via `SQLITE_MAX_COLUMN`.
- **Maximum number of terms in a compound SELECT:** 500 (default).
- **Maximum number of attachments:** 10 (default). Configurable via `SQLITE_MAX_ATTACHED`.
- **Maximum SQL statement length:** 1,000,000,000 bytes (default).
- **Maximum index depth:** 50,000 levels.
- **Maximum index entries:** 4,741,982,696.
- **Maximum number of variables in prepared statement:** 32,766 (default). Configurable via `SQLITE_MAX_VARIABLE_NUMBER`.
- **Maximum recursion depth:** 1000 (default). Configurable via `SQLITE_MAX_EXPR_DEPTH`.

Run-time limits can be adjusted per-connection:
```c
sqlite3_limit(db, SQLITE_LIMIT_LENGTH, new_value);
sqlite3_limit(db, SQLITE_LIMIT_COLUMN, new_value);
sqlite3_limit(db, SQLITE_LIMIT_VARIABLE_NUMBER, new_value);
```

## Performance Optimization

### Indexing Strategies

- Create indexes on columns used in WHERE, JOIN, ORDER BY, and GROUP BY
- Use partial indexes for frequently queried subsets:
  ```sql
  CREATE INDEX idx_active ON users(email) WHERE active = 1;
  ```
- Composite indexes should list most-selective columns first
- Expression indexes for computed lookups:
  ```sql
  CREATE INDEX idx_lower_email ON users(LOWER(email));
  ```

### Batch Operations

Wrap multiple inserts/updates in a single transaction:
```sql
BEGIN TRANSACTION;
INSERT INTO data VALUES (...);
INSERT INTO data VALUES (...);
-- ... many more inserts
COMMIT;
```

Without an explicit transaction, SQLite auto-commits after each statement, which is very slow.

### WAL Mode for Concurrent Workloads

WAL mode allows concurrent readers and writers:
```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-64000;
```

### Analyze the Query Plan

Use `EXPLAIN QUERY PLAN` to understand how SQLite executes queries:
```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'alice@example.com';
```

Run `ANALYZE` after significant data changes to update query planner statistics:
```sql
ANALYZE;              -- All tables
ANALYZE users;        -- Specific table
```

### Vacuum for Space Reclamation

After large deletes, reclaim space:
```sql
VACUUM;               -- Rebuild the entire database
VACUUM INTO 'new.db'; -- Write to a new file
```

In WAL mode, the main database file does not shrink automatically. Periodic checkpointing and vacuuming are needed to manage file size.

### Memory Configuration

Tune memory usage for your workload:
```sql
PRAGMA cache_size=-64000;     -- 64 MB page cache
PRAGMA mmap_size=268435456;   -- 256 MB memory-mapped I/O
PRAGMA temp_store=MEMORY;     -- Temp tables in RAM
```

## Database File Format

SQLite stores data in a single cross-platform file with the following structure:
- 100-byte header describing the database format
- Pages of configurable size (default 4096 bytes, must be a power of 2 from 512 to 65536)
- B-tree pages for tables and indexes
- Overflow pages for large values
- Free pages for reclaimed space

The file format is stable across versions — databases created by old SQLite versions work with new ones.

## Security Considerations

- Use parameterized queries (bound parameters) to prevent SQL injection
- Enable `PRAGMA foreign_keys=ON` for referential integrity
- Use `--safe` mode in CLI to restrict dangerous operations
- Set appropriate file permissions on database files
- Use WAL mode with `PRAGMA wal_checkpoint=PASSIVE` for better concurrency under load
- Be aware that SQLite does not provide built-in encryption — use SQLCipher or similar for encrypted storage
