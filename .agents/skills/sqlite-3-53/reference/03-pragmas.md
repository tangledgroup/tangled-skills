# Pragma Configuration

Complete reference for SQLite pragmas - configuration commands that control database behavior, performance tuning, integrity checking, and SQLite customization.

## Overview

PRAGMA statements configure SQLite behavior at database or connection level:

```sql
-- Get current setting
PRAGMA journal_mode;

-- Set new value
PRAGMA journal_mode = WAL;

-- Combined get/set
PRAGMA count = 100;
```

## Journaling and Recovery

### journal_mode

Controls transaction journaling method:

```sql
-- DELETE (default) - Write-ahead log deleted after commit
PRAGMA journal_mode = DELETE;

-- TRUNCATE - Truncate journal file to zero bytes after commit
PRAGMA journal_mode = TRUNCATE;

-- PERSIST - Keep journal file, reuse across transactions
PRAGMA journal_mode = PERSIST;

-- OFF - No journal (fastest but unsafe)
PRAGMA journal_mode = OFF;

-- MEMORY - Journal in memory only
PRAGMA journal_mode = MEMORY;

-- WAL (Write-Ahead Log) - Best for concurrent access
PRAGMA journal_mode = WAL;

-- Check current mode
PRAGMA journal_mode;  -- Returns: wal
```

**Recommendations:**
- **WAL**: Multi-reader applications, better concurrency
- **DELETE**: Single-user applications, default behavior
- **MEMORY**: Testing, temporary databases
- **OFF**: Never use in production (data loss risk)

### synchronous

Controls flush timing for durability:

```sql
-- OFF - Never sync (fastest, highest risk)
PRAGMA synchronous = OFF;

-- NORMAL - Sync at critical points (good balance)
PRAGMA synchronous = NORMAL;

-- FULL - Always sync (safest, slowest)
PRAGMA synchronous = FULL;

-- Check current setting
PRAGMA synchronous;  -- Returns: 2 (FULL)
```

**Risk vs Performance:**
| Mode | Risk Level | Performance | Use Case |
|------|-----------|-------------|----------|
| OFF | Very High | Fastest | Temporary data |
| NORMAL | Low | Good | Most applications |
| FULL | None | Slowest | Critical data |

### Temp Store Location

```sql
-- Store temp tables on disk (default)
PRAGMA temp_store = DEFAULT;

-- Store temp tables in memory (faster)
PRAGMA temp_store = MEMORY;

-- Force disk storage
PRAGMA temp_store = FILE;

PRAGMA temp_store;  -- Check current setting
```

## WAL Mode Configuration

### wal_autocheckpoint

Automatic checkpoint interval (WAL mode):

```sql
-- Default: checkpoint every 1000 pages
PRAGMA wal_autocheckpoint = 1000;

-- Disable auto-checkpoint
PRAGMA wal_autocheckpoint = 0;

-- Checkpoint more frequently
PRAGMA wal_autocheckpoint = 100;

PRAGMA wal_autocheckpoint;  -- Check current value
```

### wal_checkpoint

Manual checkpoint control:

```sql
-- Synchronous checkpoint (blocks until complete)
PRAGMA wal_checkpoint(TRUNCATE);

-- Passive checkpoint (returns when possible)
PRAGMA wal_checkpoint(PASSIVE);

-- Full checkpoint (tries to complete all)
PRAGMA wal_checkpoint(FULL);

-- View checkpoint status
PRAGMA wal_checkpoint;
-- Returns: pages_checkpointed, pages_remaining, is_active
```

### wal_index_size

Size of WAL index file:

```sql
PRAGMA wal_index_size = 4;  -- Default: 4 pages
```

## Performance Tuning

### cache_size

Database cache size in pages or KB:

```sql
-- Set cache to 1000 pages
PRAGMA cache_size = 1000;

-- Set cache to 256 MB (negative value = KB)
PRAGMA cache_size = -262144;

-- Get current cache size (in pages)
PRAGMA cache_size;

-- Default is usually around 2000 pages (~2MB)
```

**Calculation:** `cache_size (KB) = pages * page_size / 1024`

### page_size

Database page size in bytes:

```sql
-- Must be set before creating tables
PRAGMA page_size = 4096;  -- Common sizes: 1024, 2048, 4096, 8192

-- Check current page size
PRAGMA page_size;

-- Note: Cannot change if database has content
```

**Page Size Selection:**
- **1024**: Small databases, embedded devices
- **4096**: Default, good for most applications
- **8192**: Large databases, better compression

### mmap_size

Memory-mapped I/O size:

```sql
-- Enable memory mapping (up to 256 MB)
PRAGMA mmap_size = 268435456;

-- Disable memory mapping
PRAGMA mmap_size = 0;

-- Check current setting
PRAGMA mmap_size;

-- Requires SQLite compiled with SQLITE_ENABLE_MEMORY_MANAGEMENT
```

### cache_autogrow

Allow cache to grow beyond cache_size:

```sql
-- Enable automatic cache growth (SQLite 3.39+)
PRAGMA cache_autogrow = ON;

-- Disable
PRAGMA cache_autogrow = OFF;
```

## Locking and Concurrency

### locking_mode

File locking behavior:

```sql
-- NORMAL - Lock database during transactions (default)
PRAGMA locking_mode = NORMAL;

-- EXCLUSIVE - Keep lock until connection closes
PRAGMA locking_mode = EXCLUSIVE;

-- CHECKPOINT - Lock only during checkpoint (WAL mode)
PRAGMA locking_mode = CHECKPOINT;

-- NONE - No locking (single-process use only)
PRAGMA locking_mode = NONE;

PRAGMA locking_mode;  -- Check current mode
```

### busy_timeout

Wait time for locked database (milliseconds):

```sql
-- Wait up to 5 seconds for lock
PRAGMA busy_timeout = 5000;

-- No waiting (default)
PRAGMA busy_timeout = 0;

-- Check current timeout
PRAGMA busy_timeout;
```

### busy_handler

Custom busy handler:

```c
// C code example
int busy_handler(void *param, int count) {
    if (count > 10) return 0;  // Give up after 10 retries
    usleep(100000);            // Wait 100ms
    return 1;                  // Try again
}

sqlite3_busy_handler(db, busy_handler, NULL);
```

## Integrity and Analysis

### integrity_check

Verify database integrity:

```sql
-- Full integrity check
PRAGMA integrity_check;

-- Check specific database (in ATTACH scenario)
PRAGMA main.integrity_check;
PRAGMA temp.integrity_check;

-- Quick check (only critical structures)
PRAGMA quick_check;

-- Expected output: "ok" if no problems found
```

### check_constraints

Verify CHECK constraints:

```sql
PRAGMA check_constraints;

-- Returns error if any constraint violated
```

### index_list

List indexes on a table:

```sql
-- List all indexes on table
PRAGMA index_list(users);

-- Returns: seq, name, unique, origin, partial

-- Get specific index info
PRAGMA index_info(idx_name);

-- Returns: seqno, cid, name
```

### table_info

Get table schema information:

```sql
PRAGMA table_info(users);

-- Returns: cid, name, type, notnull, dflt_value, pk

-- All tables
PRAGMA table_list;

-- Specific database
PRAGMA main.table_list;
```

### foreign_key_list

List foreign keys for a table:

```sql
PRAGMA foreign_key_list(users);

-- Returns: id, seq, table, from, to, on_update, on_delete, match
```

## Statistics and Optimization

### analyze

Update query planner statistics:

```sql
-- Analyze entire database
PRAGMA analyze;

-- Analyze specific table
PRAGMA analyze = users;

-- Or use ANALYZE statement
ANALYZE;
ANALYZE users;
```

### stats

View query planner statistics:

```sql
PRAGMA stats;

-- Shows: sample_size, row_estimates for each table/index
```

### optimize

Run automatic optimizations:

```sql
PRAGMA optimize;

-- Performs:
-- - Index rebuild if beneficial
-- - Statistics update
-- - Schema cleanup
```

## Foreign Keys

### foreign_keys

Enable/disable foreign key enforcement:

```sql
-- Enable foreign keys (must be done per connection)
PRAGMA foreign_keys = ON;

-- Disable foreign keys
PRAGMA foreign_keys = OFF;

-- Check current state (0 = off, 1 = on)
PRAGMA foreign_keys;

-- Always enable at connection start for production use
```

### foreign_key_check

Verify foreign key constraints:

```sql
PRAGMA foreign_key_check;

-- Returns rows with violations:
-- table, rowid, fk_id, parent

-- Empty result = no violations
```

## Virtual Tables

### module_list

List loaded virtual table modules:

```sql
PRAGMA module_list;

-- Shows: module_name, author, version
```

## Memory Management

### mem_debug

Enable memory debugging:

```sql
-- Enable memory allocation tracking
PRAGMA mem_debug = ON;

-- Disable
PRAGMA mem_debug = OFF;
```

### mem_usage

Get memory usage statistics:

```sql
PRAGMA mem_usage;

-- Returns total bytes allocated by SQLite
```

## Security Settings

### secure_delete

Secure file deletion:

```sql
-- Overwrite deleted pages with zeros
PRAGMA secure_delete = ON;

-- Normal deletion (faster)
PRAGMA secure_delete = OFF;

-- Check setting
PRAGMA secure_delete;
```

### user_version

Application version number:

```sql
-- Set application version
PRAGMA user_version = 3;

-- Get current version
PRAGMA user_version;

-- Useful for migration tracking
```

### application_id

Application identifier:

```sql
-- Set 4-byte application ID
PRAGMA application_id = 12345678;

-- Get current ID
PRAGMA application_id;
```

## Encryption (if compiled)

### cipher_type

Encryption algorithm (requires SQLCipher):

```sql
PRAGMA cipher_type = 'aes-256-cbc';
```

### key

Set encryption key (requires SQLCipher):

```sql
PRAGMA key = 'secret-password';

-- Rekey with new password
PRAGMA rekey = 'new-password';
```

## WAL-Specific Pragmas

### wal_checkpoint_tries

Number of checkpoint retry attempts:

```sql
PRAGMA wal_checkpoint_tries = 5000;  -- Default
```

### wal_checkpoint_retry

Retry delay in milliseconds:

```sql
PRAGMA wal_checkpoint_retry = 1000;  -- 1 second
```

## Temp Database Settings

### temp_store_directory

Directory for temporary files:

```sql
-- Use specific directory for temp files
PRAGMA temp_store_directory = '/tmp/sqlite';

-- Reset to default
PRAGMA temp_store_directory = '';
```

## Query Analysis

### explain

Show query execution plan:

```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Returns: id, parent,外侧, detail

-- Detailed explanation
EXPLAIN QUERY PLAN SELECT u.*, COUNT(o.id) 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id 
GROUP BY u.id;
```

### trace

Enable SQL statement tracing:

```c
// C code example
void trace_callback(void *param, const char *sql) {
    printf("Executing: %s\n", sql);
}

sqlite3_trace(db, trace_callback, NULL);
```

## Common Configuration Patterns

### Development Environment

```sql
-- Fast development settings
PRAGMA journal_mode = MEMORY;
PRAGMA synchronous = OFF;
PRAGMA foreign_keys = ON;
PRAGMA temp_store = MEMORY;
```

### Production (Single User)

```sql
-- Safe single-user configuration
PRAGMA journal_mode = DELETE;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -256000;  -- 256 MB
PRAGMA temp_store = MEMORY;
```

### Production (Multi-User)

```sql
-- Multi-user with WAL mode
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -128000;  -- 128 MB per connection
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 5000;
PRAGMA wal_autocheckpoint = 1000;
```

### High Performance (Acceptable Risk)

```sql
-- Maximum performance with some risk
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;  -- Still safe on crash
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -512000;  -- 512 MB
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;  -- 256 MB memory mapping
```

### Read-Only Optimization

```sql
-- Optimized for read-only access
PRAGMA journal_mode = WAL;
PRAGMA cache_size = -1024000;  -- 1 GB cache
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 2147483648;  -- 2 GB memory mapping
```

## Monitoring and Diagnostics

### Connection Information

```sql
-- Get SQLite version
SELECT sqlite_version();

-- Get compile options
PRAGMA compile_options;

-- Get database size
SELECT page_count * page_size AS size_bytes 
FROM pragma_page_count(), pragma_page_size();

-- Get free pages
PRAGMA freelist_count;
```

### Performance Monitoring

```sql
-- Create performance monitoring table
CREATE TABLE IF NOT EXISTS perf_stats (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    pragma_name TEXT,
    value TEXT
);

-- Record current settings
INSERT INTO perf_stats (pragma_name, value) 
SELECT 'cache_size', * FROM (PRAGMA cache_size);

INSERT INTO perf_stats (pragma_name, value) 
SELECT 'page_size', * FROM (PRAGMA page_size);

INSERT INTO perf_stats (pragma_name, value) 
SELECT 'free_pages', * FROM (PRAGMA freelist_count);
```

### Health Check Query

```sql
-- Comprehensive health check
SELECT 
    'version' AS check_name,
    sqlite_version() AS value
UNION ALL
SELECT 'integrity', 
    (SELECT group_concat(msg) FROM (PRAGMA integrity_check))
UNION ALL
SELECT 'foreign_keys',
    CASE WHEN (PRAGMA foreign_keys) = 1 THEN 'enabled' ELSE 'disabled' END
UNION ALL
SELECT 'journal_mode',
    (SELECT value FROM (PRAGMA journal_mode))
UNION ALL
SELECT 'page_count',
    CAST((SELECT value FROM (PRAGMA page_count)) AS TEXT)
UNION ALL
SELECT 'free_pages',
    CAST((SELECT value FROM (PRAGMA freelist_count)) AS TEXT);
```

## Troubleshooting

### Database Locked Issues

```sql
-- Check for locks
PRAGMA locking_mode;
PRAGMA busy_timeout;

-- Increase timeout
PRAGMA busy_timeout = 10000;

-- Use WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Check active connections (requires additional tools)
```

### Performance Problems

```sql
-- Check current settings
PRAGMA cache_size;
PRAGMA page_size;
PRAGMA synchronous;

-- Analyze query plans
EXPLAIN QUERY PLAN SELECT ...;

-- Update statistics
PRAGMA analyze;

-- Check for fragmentation
PRAGMA integrity_check;
PRAGMA page_count;
```

### Memory Issues

```sql
-- Reduce cache size
PRAGMA cache_size = -65536;  -- 64 MB

-- Disable memory mapping
PRAGMA mmap_size = 0;

-- Use disk for temp tables
PRAGMA temp_store = FILE;

-- Check memory usage
PRAGMA mem_usage;
```

## Best Practices

1. **Enable foreign keys** at connection start: `PRAGMA foreign_keys = ON;`
2. **Use WAL mode** for multi-reader applications: `PRAGMA journal_mode = WAL;`
3. **Set appropriate cache size** based on available memory
4. **Run ANALYZE** after bulk data changes
5. **Check integrity** periodically: `PRAGMA integrity_check;`
6. **Use synchronous=NORMAL** for best safety/performance balance
7. **Set busy_timeout** to avoid lock errors in concurrent applications
8. **Monitor freelist** for fragmentation issues
