# C API Integration

Complete guide to SQLite C API for application integration, including connection management, prepared statements, parameter binding, result retrieval, and advanced features.

## Connection Management

### Opening Database Connections

```c
#include <sqlite3.h>

sqlite3 *db = NULL;
int rc;

// Open database (creates file if it doesn't exist)
rc = sqlite3_open("mydatabase.db", &db);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
}

// Open read-only
rc = sqlite3_open_v2("mydatabase.db", &db, SQLITE_OPEN_READONLY, NULL);

// Open in-memory database
rc = sqlite3_open(":memory:", &db);

// Open with specific VFS
rc = sqlite3_open_v2("mydatabase.db", &db, 
    SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, "unix-dotfile");
```

### Opening Flags

| Flag | Description |
|------|-------------|
| `SQLITE_OPEN_READONLY` | Open in read-only mode |
| `sqlite3_open_readwrite` | Open for reading and writing |
| `SQLITE_OPEN_CREATE` | Create database if it doesn't exist |
| `SQLITE_OPEN_NO_MUTEX` | No mutex locking |
| `SQLITE_OPEN_FULLMUTEX` | Full mutex serialization |
| `SQLITE_OPEN_SHAREDCACHE` | Enable shared cache mode |
| `SQLITE_OPEN_PRIVATECACHE` | Disable shared cache |
| `SQLITE_OPEN_URI` | Interpret database name as URI |

### URI Database Names

```c
// Database with query parameters
rc = sqlite3_open("file:mydatabase.db?mode=ro&cache=private", &db);

// In-memory database with shared cache
rc = sqlite3_open("file::memory:?cache=shared", &db);

// Multiple databases in single file
rc = sqlite3_open("file:data.db?vfs=unix", &db);
```

### Closing Database Connections

```c
// Close database (waits for statements to finish)
rc = sqlite3_close(db);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Cannot close database: %s\n", sqlite3_errmsg(db));
}

// Force close (aborts active operations)
rc = sqlite3_close_v2(db);

// Check if database is busy
if (sqlite3_get_autocommit(db) == 0) {
    printf("Database has active transaction\n");
}
```

### Database Configuration

```c
// Set busy timeout (milliseconds)
sqlite3_busy_timeout(db, 5000);  // Wait up to 5 seconds

// Set custom busy handler
int busy_handler(void *param, int count) {
    if (count > 10) return 0;  // Give up after 10 retries
    usleep(100000 * count);    // Wait longer each time
    return 1;  // Continue trying
}
sqlite3_busy_handler(db, busy_handler, NULL);

// Get database path
const char *path = sqlite3_db_filename(db, "main");

// Check if database is read-only
int readonly = sqlite3_db_readonly(db, "main");
```

## Prepared Statements

### Creating Prepared Statements

```c
sqlite3_stmt *stmt = NULL;
const char *sql = "SELECT id, name, email FROM users WHERE active = 1";
const char *tail;

// Prepare statement
rc = sqlite3_prepare_v2(db, sql, -1, &stmt, &tail);
if (rc != SQLITE_OK) {
    fprintf(stderr, "SQL error: %s\n", sqlite3_errmsg(db));
    return 1;
}

// Check for leftover SQL
if (tail && *tail) {
    printf("Unprocessed SQL: %s\n", tail);
}

// Prepare with byte count
rc = sqlite3_prepare_v2(db, sql, strlen(sql), &stmt, &tail);

// Prepare UTF-16 statement
rc = sqlite3_prepare16_v2(db, utf16_sql, -1, &stmt, &tail);
```

### Statement Lifecycle

```c
// Execute and reset (for multiple rows)
while (sqlite3_step(stmt) == SQLITE_ROW) {
    // Process row
}

// Reset statement for reuse
sqlite3_reset(stmt);

// Clear bindings for next use
sqlite3_clear_bindings(stmt);

// Finalize when done
sqlite3_finalize(stmt);
```

### Statement Information

```c
// Number of columns
int col_count = sqlite3_column_count(stmt);

// Column name
const char *col_name = sqlite3_column_name(stmt, 0);

// Parameter count
int param_count = sqlite3_bind_parameter_count(stmt);

// Parameter name (e.g., ":name", "?1")
const char *param_name = sqlite3_bind_parameter_name(stmt, 1);

// Parameter index by name
int idx = sqlite3_bind_parameter_index(stmt, ":username");

// Number of rows changed (after INSERT/UPDATE/DELETE)
sqlite3_int64 changes = sqlite3_changes(db);
sqlite3_int64 total_changes = sqlite3_total_changes(db);
```

## Parameter Binding

### Binding Parameters

Positional parameters use `?` or `?NNN`:

```c
const char *sql = "INSERT INTO users (name, email, age) VALUES (?, ?, ?)";
sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

// Bind text
sqlite3_bind_text(stmt, 1, "Alice", -1, SQLITE_TRANSIENT);
sqlite3_bind_text(stmt, 2, "alice@example.com", -1, SQLITE_TRANSIENT);

// Bind integer
sqlite3_bind_int(stmt, 3, 30);
sqlite3_bind_int64(stmt, 4, 9223372036854775807LL);

// Bind double
sqlite3_bind_double(stmt, 5, 3.14159);

// Bind NULL
sqlite3_bind_null(stmt, 6);

// Bind BLOB
const unsigned char *blob_data = "binary data";
int blob_size = strlen(blob_data);
sqlite3_bind_blob(stmt, 7, blob_data, blob_size, SQLITE_TRANSIENT);

// Execute
sqlite3_step(stmt);
sqlite3_finalize(stmt);
```

### Named Parameters

```c
const char *sql = "SELECT * FROM users WHERE name = :name AND age > :min_age";
sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

// Get parameter indices
int name_idx = sqlite3_bind_parameter_index(stmt, ":name");
int age_idx = sqlite3_bind_parameter_index(stmt, ":min_age");

// Bind by index
sqlite3_bind_text(stmt, name_idx, "Alice", -1, SQLITE_TRANSIENT);
sqlite3_bind_int(stmt, age_idx, 18);

// Execute
while (sqlite3_step(stmt) == SQLITE_ROW) {
    // Process results
}
```

### Binding with Custom Destructors

```c
// Copy data (SQLite manages memory)
char *data = strdup("value");
sqlite3_bind_text(stmt, 1, data, -1, sqlite3_free);

// Transient (copy made immediately)
sqlite3_bind_text(stmt, 1, "value", -1, SQLITE_TRANSIENT);

// Static (data must remain valid until statement finalized)
static const char *static_data = "static value";
sqlite3_bind_text(stmt, 1, static_data, -1, SQLITE_STATIC);
```

### Binding Zero-Blobs

```c
// Create placeholder for binary data
sqlite3_bind_zeroblob(stmt, 1, 1024);  // 1024-byte zero blob

// Get blob handle for writing
sqlite3_blob *blob;
sqlite3_blob_open(db, "table", "column", rowid, 0, 0, &blob);
sqlite3_blob_write(blob, data, length, offset);
sqlite3_blob_close(blob);
```

## Result Retrieval

### Getting Column Values

```c
const char *sql = "SELECT id, name, email, age, balance FROM users WHERE id = ?";
sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
sqlite3_bind_int(stmt, 1, 42);

if (sqlite3_step(stmt) == SQLITE_ROW) {
    // Get integer
    int id = sqlite3_column_int(stmt, 0);
    sqlite3_int64 large_id = sqlite3_column_int64(stmt, 0);
    
    // Get text
    const char *name = (const char *)sqlite3_column_text(stmt, 1);
    const unsigned char *email = sqlite3_column_text(stmt, 2);
    int name_len = sqlite3_column_bytes(stmt, 1);
    
    // Get double
    double balance = sqlite3_column_double(stmt, 4);
    
    // Get BLOB
    const void *blob_data = sqlite3_column_blob(stmt, 5);
    int blob_size = sqlite3_column_bytes(stmt, 5);
    
    // Get as generic value
    sqlite3_value *val = sqlite3_column_value(stmt, 1);
}

sqlite3_finalize(stmt);
```

### Checking Column Types

```c
int type = sqlite3_column_type(stmt, 0);

switch (type) {
    case SQLITE_INTEGER:
        printf("Integer: %lld\n", sqlite3_column_int64(stmt, 0));
        break;
    case SQLITE_FLOAT:
        printf("Float: %f\n", sqlite3_column_double(stmt, 0));
        break;
    case SQLITE_TEXT:
        printf("Text: %s\n", sqlite3_column_text(stmt, 0));
        break;
    case SQLITE_BLOB:
        printf("Blob size: %d\n", sqlite3_column_bytes(stmt, 0));
        break;
    case SQLITE_NULL:
        printf("NULL\n");
        break;
}

// UTF-16 text
const unsigned short *utf16_text = (const unsigned short *)sqlite3_column_text16(stmt, 0);
int utf16_bytes = sqlite3_column_bytes16(stmt, 0);
```

### Column Metadata

```c
// Column name
const char *name = sqlite3_column_name(stmt, i);
const unsigned char *name_utf16 = sqlite3_column_name16(stmt, i);

// Declared type (from CREATE TABLE)
const char *decl_type = sqlite3_column_decltype(stmt, i);
const unsigned char *decl_type_utf16 = sqlite3_column_decltype16(stmt, i);

// Table and database info
const char *table_name = sqlite3_column_table_name(stmt, i);
const char *db_name = sqlite3_column_database_name(stmt, i);
const char *origin_name = sqlite3_column_origin_name(stmt, i);
```

## Executing Statements

### Simple Execution (No Results)

```c
// Execute single statement
const char *sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')";
rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
if (rc != SQLITE_OK) {
    fprintf(stderr, "SQL error: %s\n", err_msg);
    sqlite3_free(err_msg);
}

// Execute multiple statements separated by semicolons
sql = "BEGIN; INSERT INTO users VALUES (1, 'Alice'); COMMIT;";
rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
```

### Execution with Callback

```c
// Callback for each row
int callback(void *param, int argc, char **argv, char **col_names) {
    printf("Row: ");
    for (int i = 0; i < argc; i++) {
        printf("%s=%s ", col_names[i], argv[i] ? argv[i] : "NULL");
    }
    printf("\n");
    return 0;  // Continue processing
}

const char *sql = "SELECT * FROM users";
rc = sqlite3_exec(db, sql, callback, (void *)"parameter", &err_msg);
```

### Iterating Results

```c
const char *sql = "SELECT id, name, email FROM users";
sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

while (sqlite3_step(stmt) == SQLITE_ROW) {
    int id = sqlite3_column_int(stmt, 0);
    const char *name = (const char *)sqlite3_column_text(stmt, 1);
    const char *email = (const char *)sqlite3_column_text(stmt, 2);
    
    printf("%d: %s <%s>\n", id, name, email);
}

// Check for errors
if (sqlite3_step(stmt) != SQLITE_DONE) {
    fprintf(stderr, "Execution error: %s\n", sqlite3_errmsg(db));
}

sqlite3_finalize(stmt);
```

## Error Handling

### Getting Error Information

```c
// Get error message (database connection)
const char *err_msg = sqlite3_errmsg(db);
const unsigned char *err_msg_utf16 = sqlite3_errmsg16(db);

// Get error code
int err_code = sqlite3_errcode(db);
int extended_code = sqlite3_extended_errcode(db);

// Get SQL statement that caused error (for prepared statements)
const char *sql = sqlite3_sql(stmt);

// Get last insertion ID
sqlite3_int64 last_id = sqlite3_last_insert_rowid(db);

// Get number of rows changed
sqlite3_int64 changes = sqlite3_changes(db);
```

### Error Codes

| Code | Description |
|------|-------------|
| `SQLITE_OK` | Success (0) |
| `SQLITE_ERROR` | Generic error (1) |
| `SQLITE_INTERNAL` | Internal logic error (2) |
| `SQLITE_PERM` | Permission denied (3) |
| `SQLITE_ABORT` | Callback requested abort (4) |
| `SQLITE_BUSY` | Database is locked (5) |
| `SQLITE_LOCKED` | Table is locked (6) |
| `SQLITE_NOMEM` | Out of memory (7) |
| `SQLITE_READONLY` | Read-only mode (8) |
| `SQLITE_INTERRUPT` | Operation interrupted (9) |
| `SQLITE_IOERR` | I/O error (10) |
| `SQLITE_CORRUPT` | Database corrupted (11) |
| `SQLITE_NOTFOUND` | File not found (12) |
| `SQLITE_FULL` | Disk full (13) |
| `SQLITE_CANTOPEN` | Cannot open file (14) |
| `SQLITE_PROTOCOL` | Protocol error (15) |
| `SQLITE_EMPTY` | Database is empty (16) |
| `SQLITE_SCHEMA` | Schema changed (17) |
| `SQLITE_TOOBIG` | Too large (18) |
| `SQLITE_CONSTRAINT` | Constraint violation (19) |
| `SQLITE_MISMATCH` | Type mismatch (20) |
| `SQLITE_MISUSE` | Library misuse (21) |
| `SQLITE_NOLFS` | No large file support (22) |
| `SQLITE_AUTH` | Authorization denied (23) |

### Error Handling Pattern

```c
int rc;
char *err_msg = NULL;

rc = sqlite3_exec(db, sql, NULL, NULL, &err_msg);
if (rc != SQLITE_OK) {
    fprintf(stderr, "SQL error (%d): %s\n", rc, err_msg);
    sqlite3_free(err_msg);
    // Handle error: rollback, cleanup, return
}

// For prepared statements
rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Prepare error: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
}
```

## Custom Functions

### Creating Scalar Functions

```c
// Simple scalar function
void upper_case(void *context, int argc, sqlite3_value **args) {
    if (argc != 1 || sqlite3_value_type(args[0]) != SQLITE_TEXT) {
        sqlite3_result_null(context);
        return;
    }
    
    const unsigned char *text = sqlite3_value_text(args[0]);
    char *upper = strdup((const char *)text);
    
    for (int i = 0; upper[i]; i++) {
        upper[i] = toupper(upper[i]);
    }
    
    sqlite3_result_text(context, upper, -1, free);
}

// Register function
sqlite3_create_function(db, "UPPER_CASE", 1, SQLITE_UTF8, NULL, 
    upper_case, NULL, NULL);
```

### Aggregate Functions

```c
// Aggregate function context
typedef struct AvgAccumulator {
    double sum;
    int count;
} AvgAccumulator;

// Initial step
void avg_init(void *context) {
    AvgAccumulator *acc = sqlite3_aggregate_context(context, sizeof(*acc));
    acc->sum = 0.0;
    acc->count = 0;
}

// Step function (called for each row)
void avg_step(void *context, int argc, sqlite3_value **args) {
    AvgAccumulator *acc = sqlite3_aggregate_context(context, sizeof(*acc));
    
    if (argc > 0 && sqlite3_value_type(args[0]) != SQLITE_NULL) {
        acc->sum += sqlite3_value_double(args[0]);
        acc->count++;
    }
}

// Final function (returns result)
void avg_final(void *context) {
    AvgAccumulator *acc = sqlite3_aggregate_context(context, sizeof(*acc));
    
    if (acc->count > 0) {
        sqlite3_result_double(context, acc->sum / acc->count);
    } else {
        sqlite3_result_null(context);
    }
}

// Register aggregate function
sqlite3_create_function(db, "AVG_CUSTOM", 1, SQLITE_UTF8, NULL,
    NULL, avg_step, avg_final);
```

### Collation Functions

```c
// Case-insensitive collation
int nocase_collation(void *param, int len1, const void *str1, int len2, const void *str2) {
    return strncasecmp(str1, str2, MIN(len1, len2));
}

// Register collation
sqlite3_create_collation(db, "NOCASE", SQLITE_UTF8, NULL, nocase_collation);
```

## Virtual Tables

### Using Virtual Tables

```c
// Create FTS5 virtual table
const char *sql = "CREATE VIRTUAL TABLE documents USING fts5(title, content)";
sqlite3_exec(db, sql, NULL, NULL, NULL);

// Insert data
sql = "INSERT INTO documents VALUES ('SQLite Guide', 'SQLite database tutorial')";
sqlite3_exec(db, sql, NULL, NULL, NULL);

// Search
sql = "SELECT * FROM documents WHERE documents MATCH 'SQLite'";
sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

while (sqlite3_step(stmt) == SQLITE_ROW) {
    const char *title = (const char *)sqlite3_column_text(stmt, 0);
    printf("Found: %s\n", title);
}

sqlite3_finalize(stmt);
```

### Loading Extensions

```c
// Enable loadable extensions
sqlite3_enable_load_extension(db, 1);

// Load extension
rc = sqlite3_load_extension(db, "libjson_ext.so", "json_init", NULL);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Extension load error: %s\n", sqlite3_errmsg(db));
}

// Load with specific entry point
rc = sqlite3_load_extension(db, "path/to/extension.so", "init_function", &err_msg);

// Disable loading
sqlite3_enable_load_extension(db, 0);
```

## Backup Operations

### Online Backup

```c
sqlite3 *dest_db;
sqlite3_backup *backup;
int rc;

// Open destination database
sqlite3_open("backup.db", &dest_db);

// Initialize backup (copy main database to dest)
backup = sqlite3_backup_init(dest_db, "main", db, "main");
if (backup) {
    // Step backup (step=-1 completes in one call)
    rc = sqlite3_backup_step(backup, -1);
    
    // Or step by page count
    while (rc == SQLITE_BUSY || rc == SQLITE_LOCKED) {
        // Wait and retry
        usleep(10000);
        rc = sqlite3_backup_step(backup, 5);
    }
    
    if (rc != SQLITE_DONE && rc != SQLITE_OK) {
        fprintf(stderr, "Backup failed: %s\n", sqlite3_errmsg(dest_db));
    }
    
    // Check progress
    int remaining = sqlite3_backup_remaining(backup);
    int pagecount = sqlite3_backup_pagecount(backup);
    printf("Progress: %d / %d pages\n", pagecount - remaining, pagecount);
    
    // Finish backup
    sqlite3_backup_finish(backup);
}

sqlite3_close(dest_db);
```

### Incremental Backup

```c
// Backup in chunks
for (int n = 5; ; n *= 2) {
    rc = sqlite3_backup_step(backup, n);
    if (rc == SQLITE_DONE) break;  // Complete
    if (rc == SQLITE_OK) continue; // More to do
    if (rc == SQLITE_BUSY || rc == SQLITE_LOCKED) {
        sqlite3_sleep(100);
        n = 5;  // Reset step size
        continue;
    }
    break;  // Error
}
```

## Memory Management

### Memory Configuration

```c
// Configure memory allocation before opening databases
sqlite3_config(SQLITE_CONFIG_SINGLETHREAD, NULL);
sqlite3_config(SQLITE_CONFIG_MULTITHREAD, NULL);
sqlite3_config(SQLITE_CONFIG_SERIALIZED, NULL);

// Set memory limits
sqlite3_config(SQLITE_CONFIG_MEMSTATUS, 0);  // Enable memory stats

// Get memory usage
int used_mem = sqlite3_memory_used();
int highwater_mark = sqlite3_memory_highwater(0);

// Reset highwater mark
int previous = sqlite3_memory_highwater(1);
```

### String Functions

```c
// Allocate string (must free with sqlite3_free)
char *str = (char *)sqlite3_malloc(256);
strcpy(str, "Hello");
sqlite3_free(str);

// Reallocate
str = (char *)sqlite3_realloc(str, 512);

// Format string (like sprintf, returns allocated string)
char *formatted = sqlite3_mprintf("User %d: %s", id, name);
printf("%s\n", formatted);
sqlite3_free(formatted);

// VSNPRINTF equivalent
char *vfmt = sqlite3_vmprintf(format, ap);
```

## Thread Safety

### Compilation Modes

```c
// Check thread safety mode
int mode = sqlite3_threadsafe();
if (mode == 0) {
    printf("Single-thread mode\n");
} else if (mode == 1) {
    printf("Multi-thread mode\n");
} else {
    printf("Serialized mode\n");
}
```

### Thread-Safe Usage Pattern

```c
// Each thread should have its own database connection
void *thread_func(void *arg) {
    sqlite3 *db;
    sqlite3_open("shared.db", &db);
    
    // Use connection for this thread only
    const char *sql = "SELECT * FROM data";
    sqlite3_stmt *stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        // Process data
    }
    
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}
```

## Performance Tips

### Statement Caching

```c
// Use prepared statements for repeated queries
sqlite3_stmt *cached_stmt = NULL;

void query_user(int user_id) {
    const char *sql = "SELECT * FROM users WHERE id = ?";
    
    if (!cached_stmt) {
        sqlite3_prepare_v2(db, sql, -1, &cached_stmt, NULL);
    } else {
        sqlite3_reset(cached_stmt);
        sqlite3_clear_bindings(cached_stmt);
    }
    
    sqlite3_bind_int(cached_stmt, 1, user_id);
    
    if (sqlite3_step(cached_stmt) == SQLITE_ROW) {
        // Process result
    }
}

// Clean up
sqlite3_finalize(cached_stmt);
```

### Using stmt for Multiple Executions

```c
sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, "INSERT INTO logs (msg) VALUES (?)", -1, &stmt, NULL);

for (int i = 0; i < 1000; i++) {
    sqlite3_bind_text(stmt, 1, message[i], -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_reset(stmt);  // Reset for next iteration
    sqlite3_clear_bindings(stmt);
}

sqlite3_finalize(stmt);
```
