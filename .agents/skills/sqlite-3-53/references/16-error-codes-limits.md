# Error Codes and System Limits

Comprehensive reference for SQLite error handling, result codes, and system limits.

## Result and Error Codes

SQLite uses numeric result codes to indicate success or failure of operations.

### Success Codes

| Code | Value | Constant | Description |
|------|-------|----------|-------------|
| OK | 0 | `SQLITE_OK` | Successful operation |
| IOERR | 10 | `SQLITE_IOERR` | I/O error (with subcodes) |
| BUSY | 5 | `SQLITE_BUSY` | Database is locked |
| LOCKED | 6 | `SQLITE_LOCKED` | Database table is locked |

### Error Codes

| Code | Value | Constant | Description |
|------|-------|----------|-------------|
| ERROR | 1 | `SQLITE_ERROR` | Generic error |
| INTERNAL | 11 | `SQLITE_INTERNAL` | Internal logic error |
| PERM | 20 | `SQLITE_PERM` | Permission denied |
| ABORT | 17 | `SQLITE_ABORT` | Callback routine requested an abort |
| CONSTRAINT | 19 | `SQLITE_CONSTRAINT` | Constraint violation |
| NOTFOUND | 12 | `SQLITE_NOTFOUND` | Unknown database object |
| FULL | 13 | `SQLITE_FULL` | Database or disk is full |
| CANTOPEN | 14 | `SQLITE_CANTOPEN` | Cannot open database file |
| PROTOCOL | 15 | `SQLITE_PROTOCOL` | Database lock protocol error |
| EMPTY | 21 | `SQLITE_EMPTY` | Database is empty |
| SCHEMA | 22 | `SQLITE_SCHEMA` | Database schema changed |
| TOOBIG | 18 | `SQLITE_TOOBIG` | String or BLOB exceeds size limit |
| NOMEM | 7 | `SQLITE_NOMEM` | Out of memory |
| CORRUPT | 11 | `SQLITE_CORRUPT` | Database disk image is malformed |
| FORMAT | 23 | `SQLITE_FORMAT` | Unrecognized file format |
| RANGE | 24 | `SQLITE_RANGE` | 64-bit overflow/underflow |
| NOTADB | 25 | `SQLITE_NOTADB` | File is not a database |

### Extended Error Codes

Extended error codes provide more specific information:

```c
// Request extended error codes
sqlite3_extended_result_codes(db, 1);

// Common extended codes
SQLITE_IOERR_READ        (10 | (1 << 8))   - Read error
SQLITE_IOERR_WRITE       (10 | (2 << 8))   - Write error
SQLITE_IOERR_DELETE      (10 | (3 << 8))   - Delete file error
SQLITE_IOERR_TRUNCATE    (10 | (4 << 8))   - Truncate error
SQLITE_IOERR_FSYNC       (10 | (5 << 8))   - fsync() error
SQLITE_IOERR_DIR_SYNC    (10 | (6 << 8))   - Directory sync error
SQLITE_IOERR_FALK        (10 | (7 << 8))   - chmod() error
SQLITE_IOERR_CHDIR       (10 | (8 << 8))   - chdir() error
SQLITE_IOERR_CLOSE       (10 | (9 << 8))   - close() error
SQLITE_IOERR_DIR_OPEN    (10 | (10 << 8))  - Directory open error
SQLITE_IOERR_SHMOPEN     (10 | (11 << 8))  - Shared memory open error
SQLITE_IOERR_SHMSIZE     (10 | (12 << 8))  - Shared memory size error
SQLITE_IOERR_SHMLOCK     (10 | (13 << 8))  - Shared memory lock error
SQLITE_IOERR_SHMMAP      (10 | (14 << 8))  - Shared memory map error
SQLITE_IOERR_SEEK        (10 | (15 << 8))  - Seek error
```

### Constraint Violation Codes

```c
SQLITE_CONSTRAINT_CHECK      (19 | (1 << 8))   - CHECK constraint failed
SQLITE_CONSTRAINT_COMMITHOOK (19 | (2 << 8))   - Commit hook aborted transaction
SQLITE_CONSTRAINT_FOREIGNKEY (19 | (3 << 8))   - Foreign key constraint failed
SQLITE_CONSTRAINT_FUNCTION   (19 | (4 << 8))   - Result of function violated constraint
SQLITE_CONSTRAINT_NOTNULL    (19 | (5 << 8))   - NOT NULL constraint failed
SQLITE_CONSTRAINT_PRIMARYKEY (19 | (6 << 8))   - PRIMARY KEY must be unique
SQLITE_CONSTRAINT_TRIGGER    (19 | (7 << 8))   - RAISE() within trigger
SQLITE_CONSTRAINT_UNIQUE     (19 | (8 << 8))   - UNIQUE constraint failed
SQLITE_CONSTRAINT_VTAB       (19 | (9 << 8))   - Virtual table constraint
SQLITE_CONSTRAINT_ROWID      (19 | (10 << 8))  - Row ID must be unique
```

## Error Handling in SQL

### Getting Error Information

```sql
-- After an error, check error message in CLI
SELECT last_insert_rowid();  -- Returns 0 on error

-- Check changes affected
SELECT changes();  -- Returns number of rows modified

-- Check total changes since connection open
SELECT total_changes();
```

### Error Messages in Applications

```c
// C API error handling
sqlite3 *db;
int rc = sqlite3_open("database.db", &db);

if (rc != SQLITE_OK) {
    const char *error_msg = sqlite3_errmsg(db);
    printf("Error: %s\n", error_msg);
    
    int error_code = sqlite3_errcode(db);
    printf("Error code: %d\n", error_code);
    
    sqlite3_close(db);
    return 1;
}

// Extended error codes
rc = sqlite3_extended_errcode(db);
```

### SQL Error Detection

```sql
-- Use RAISE() to generate errors
CREATE TRIGGER check_price
BEFORE INSERT ON products
WHEN NEW.price < 0
BEGIN
    SELECT RAISE(ABORT, 'Price cannot be negative');
END;

-- Custom error messages with RAISE()
SELECT RAISE(IGNORE, 'This row is skipped');
SELECT RAISE(ROLLBACK, 'Transaction rolled back');
SELECT RAISE(ABORT, 'Operation aborted');
```

## System Limits

SQLite has various configurable limits that control resource usage.

### Viewing Current Limits

```sql
-- List all limits
PRAGMA limits;

-- Get specific limit
PRAGMA limits.string_length;
PRAGMA limits.sql_length;
PRAGMA limits.column_count;

-- In C API
int limit = sqlite3_limit(db, SQLITE_LIMIT_STRING_LENGTH, -1);
```

### Configurable Limits

| Limit Name | Constant | Default | Minimum | Maximum | Description |
|------------|----------|---------|---------|---------|-------------|
| string_length | SQLITE_LIMIT_STRING_LENGTH | 1,000,000,000 | 0 | 2,147,483,647 | Max length of strings |
| sql_length | SQLITE_LIMIT_SQL_LENGTH | 1,000,000,000 | 0 | 2,147,483,647 | Max length of SQL statement |
| column_count | SQLITE_LIMIT_COLUMN_COUNT | 999 | 1 | 32,766 | Max columns in table/index/SELECT |
| column_depth | SQLITE_LIMIT_COLUMN_DEPTH | 1000 | 0 | 1000 | Max nesting in expressions |
| composite_key_count | SQLITE_LIMIT_COMPOSITE_KEY_COUNT | 999 | 1 | 255 | Max columns in composite key |
| attached_databases | SQLITE_LIMIT_ATTACHED | 10 | 0 | 125 | Max attached databases |
| like_pattern_length | SQLITE_LIMIT_LIKE_PATTERN_LENGTH | 50,000 | 0 | 50,000 | Max pattern length in LIKE |
| expression_depth | SQLITE_LIMIT_EXPRESSION_DEPTH | 1000 | 0 | 1000 | Max expression tree depth |
| variable_number | SQLITE_LIMIT_VARIABLE_NUMBER | 32,766 | 0 | 999,999,999 | Max parameter index |
| trigger_depth | SQLITE_LIMIT_TRIGGER_DEPTH | 1000 | 0 | 1000 | Max trigger recursion depth |
| worker_threads | SQLITE_LIMIT_WORKER_THREADS | 8 | 0 | 256 | Max background threads |

### Setting Limits

```sql
-- Set limit for string length (in bytes)
PRAGMA limits.string_length = 500000000;  -- 500MB

-- Set maximum SQL statement length
PRAGMA limits.sql_length = 2000000000;  -- 2GB

-- Reduce column count limit for memory-constrained environments
PRAGMA limits.column_count = 100;

-- Increase variable number for complex queries
PRAGMA limits.variable_number = 10000;
```

### C API Limit Management

```c
// Get current limit
int current = sqlite3_limit(db, SQLITE_LIMIT_STRING_LENGTH, -1);

// Set new limit (returns old limit)
int old_limit = sqlite3_limit(db, SQLITE_LIMIT_STRING_LENGTH, 500000000);

// Reset to default
sqlite3_limit(db, SQLITE_LIMIT_STRING_LENGTH, 1000000000);

// Check all limits
for (int i = SQLITE_LIMIT_STRING_LENGTH; i <= SQLITE_LIMIT_WORKER_THREADS; i++) {
    int current = sqlite3_limit(db, i, -1);
    printf("Limit %d: %d\n", i, current);
}
```

## Fixed Limits (Not Configurable)

Some limits are fixed and cannot be changed:

| Limit | Value | Description |
|-------|-------|-------------|
| Maximum database size | ~140 TB | 2^64 bytes minus overhead |
| Maximum page size | 65,536 bytes | Must be power of 2 |
| Minimum page size | 512 bytes | Power of 2 constraint |
| Maximum record size | ~2 GB | Limited by 32-bit rowid |
| Maximum index depth | 8 levels | For B-tree structure |
| Maximum number of tables per database | No practical limit | Memory constrained |

## Handling Specific Errors

### Database Locked

```sql
-- Set busy timeout (milliseconds)
PRAGMA busy_timeout = 5000;

-- In CLI
.timeout 5000

-- Retry logic in application
int retry_count = 0;
int rc;
do {
    rc = sqlite3_exec(db, sql, callback, user_data, &err_msg);
    if (rc == SQLITE_BUSY) {
        sleep(100 * (++retry_count));  // Exponential backoff
    }
} while (rc == SQLITE_BUSY && retry_count < 5);
```

### Constraint Violations

```sql
-- Check constraint before insert
INSERT INTO users (email, name) 
VALUES ('test@example.com', 'Test User')
ON CONFLICT (email) DO NOTHING;

-- Get constraint violation details
SELECT 
    CASE 
        WHEN sql_error_code() & 0xFF = 19 THEN 'Constraint violation'
        ELSE 'Other error'
    END AS error_type;
```

### Out of Memory

```sql
-- Reduce memory usage
PRAGMA cache_size = -100;  -- 100KB cache
PRAGMA temp_store = MEMORY;  -- Use memory for temp tables

-- Monitor memory usage
SELECT sqlite3_memory_used() AS current_usage;
SELECT sqlite3_memory_highwater(1) AS peak_usage;
```

### Database Corrupted

```sql
-- Check database integrity
PRAGMA integrity_check;

-- Quick check (faster but less thorough)
PRAGMA quick_check;

-- Fix minor issues
VACUUM;

-- In severe cases, restore from backup
-- SQLite cannot auto-repair corrupted databases
```

### Permission Denied

```sql
-- Check file permissions (Unix)
-- sqlite3 database.db 2>&1 | grep "Permission denied"

-- Create database in writable location
CREATE TABLE temp_data (id INTEGER);
-- Then copy to desired location
```

## Error Logging

### Enable Error Log

```c
// C API: Set up error logging
void error_logger(void *pArg, int iErrCode, const char *zMsg) {
    fprintf(stderr, "SQLite Error %d: %s\n", iErrCode, zMsg);
}

sqlite3_config(SQLITE_CONFIG_LOG, error_logger, NULL);
```

### Warning Log (SQL)

```sql
-- Enable warning log
PRAGMA warn_on_unused_cols = ON;

-- View warnings
SELECT * FROM pragma_warn_unused_cols;
```

## Best Practices

1. **Always check return codes** - Never assume operations succeed
2. **Use extended error codes** - Provide more diagnostic information
3. **Set appropriate limits** - Adjust for your workload requirements
4. **Implement retry logic** - For transient errors like SQLITE_BUSY
5. **Log errors with context** - Include SQL statement and parameters
6. **Validate constraints early** - Check before attempting inserts/updates
7. **Monitor memory usage** - Especially in long-running applications
8. **Regular integrity checks** - Catch corruption early

## Debugging Tips

```sql
-- Enable verbose error messages
PRAGMA full_column_names = ON;
PRAGMA header = ON;

-- Trace SQL execution
PRAGMA trace_off;  -- Disable tracing
PRAGMA trace_on;   -- Enable to stdout

-- Profile query performance
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';

-- Check for schema changes
SELECT * FROM sqlite_sequence;
SELECT name, sql FROM sqlite_master WHERE type = 'table';
```

## Related Documentation

- [C API](02-c-api.md) - Programmatic error handling
- [Administration](08-administration.md) - Database integrity checking
- [Performance Optimization](07-performance.md) - Resource management
- [CLI Commands](11-cli-commands.md) - Error display in CLI
