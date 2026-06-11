# C/C++ API

## Core Objects

The SQLite C API revolves around two principal objects:

- **`sqlite3*`** — Database connection object. Created by `sqlite3_open()`, destroyed by `sqlite3_close()`.
- **`sqlite3_stmt*`** — Prepared statement object. Created by `sqlite3_prepare_v2()`, destroyed by `sqlite3_finalize()`.

## Core Workflow

The essential eight-step workflow:

1. **Open**: `sqlite3_open(filename, &db)`
2. **Prepare**: `sqlite3_prepare_v2(db, sql, len, &stmt, &tail)`
3. **Bind**: `sqlite3_bind_text(stmt, 1, value, -1, SQLITE_STATIC)`
4. **Step**: `sqlite3_step(stmt)` — returns `SQLITE_ROW` for each result row
5. **Column**: `sqlite3_column_text(stmt, 0)` — extract column values
6. **Step again** — loop until `SQLITE_DONE`
7. **Finalize**: `sqlite3_finalize(stmt)`
8. **Close**: `sqlite3_close(db)`

## Opening a Database

```c
sqlite3 *db;
int rc = sqlite3_open("mydatabase.db", &db);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
}
```

Special filenames:
- `":memory:"` — In-memory database (private to this connection)
- `file::memory:?cache=shared` — Shared in-memory database (accessible by multiple connections)
- Empty string `""` — Temporary database on disk, auto-deleted

URI filenames enable options inline:
```c
sqlite3_open("file:/path/to/db.db?mode=ro&cache=private", &db);
```

## Prepared Statements

Prepared statements are the primary interface for executing SQL. They compile SQL text into bytecode once, then can be executed multiple times with different parameter values.

```c
sqlite3_stmt *stmt;
const char *sql = "INSERT INTO users (name, email) VALUES (?, ?)";
int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

if (rc == SQLITE_OK) {
    sqlite3_bind_text(stmt, 1, "Alice", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, "alice@example.com", -1, SQLITE_STATIC);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        fprintf(stderr, "Insert failed: %s\n", sqlite3_errmsg(db));
    }

    // Reuse with different values
    sqlite3_reset(stmt);
    sqlite3_bind_text(stmt, 1, "Bob", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, "bob@example.com", -1, SQLITE_STATIC);
    sqlite3_step(stmt);
}

sqlite3_finalize(stmt);
```

### Parameter Binding

Parameters are numbered from 1 (or named with `:name`, `$name`, `@name`):

- `sqlite3_bind_int(stmt, 1, value)`
- `sqlite3_bind_int64(stmt, 1, value)`
- `sqlite3_bind_double(stmt, 1, value)`
- `sqlite3_bind_text(stmt, 1, text, nBytes, destructor)`
- `sqlite3_bind_blob(stmt, 1, data, nBytes, destructor)`
- `sqlite3_bind_null(stmt, 1)`
- `sqlite3_bind_zeroblob(stmt, 1, nBytes)`

The destructor argument controls memory management:
- `SQLITE_STATIC` — SQLite does not copy the data; caller must keep it valid
- `SQLITE_TRANSIENT` — SQLite makes an internal copy (most common)
- A custom destructor function pointer

Call `sqlite3_clear_bindings(stmt)` to reset all bindings.

## Reading Results

After `sqlite3_step()` returns `SQLITE_ROW`, read column values:

```c
int col_count = sqlite3_column_count(stmt);
for (int i = 0; i < col_count; i++) {
    const char *name = sqlite3_column_name(stmt, i);
    int type = sqlite3_column_type(stmt, i);

    switch (type) {
        case SQLITE_INTEGER:
            printf("%s = %lld\n", name, sqlite3_column_int64(stmt, i));
            break;
        case SQLITE_FLOAT:
            printf("%s = %f\n", name, sqlite3_column_double(stmt, i));
            break;
        case SQLITE_TEXT:
            printf("%s = %s\n", name,
                   (const char*)sqlite3_column_text(stmt, i));
            break;
        case SQLITE_BLOB:
            printf("%s = %zd bytes\n", name,
                   sqlite3_column_bytes(stmt, i));
            break;
        case SQLITE_NULL:
            printf("%s = NULL\n", name);
            break;
    }
}
```

## Convenience Functions

For simple fire-and-forget operations:

```c
// Execute SQL with a callback for each result row
int callback(void *data, int argc, char **argv, char **colnames) {
    for (int i = 0; i < argc; i++)
        printf("%s = %s\n", colnames[i], argv[i] ? argv[i] : "NULL");
    return 0;
}

char *errmsg;
sqlite3_exec(db, "SELECT * FROM users", callback, NULL, &errmsg);
if (errmsg) {
    fprintf(stderr, "SQL error: %s\n", errmsg);
    sqlite3_free(errmsg);
}
```

## Error Handling

Result codes are integers. Common values:
- `SQLITE_OK` (0) — Success
- `SQLITE_ERROR` (1) — SQL error or missing database
- `SQLITE_BUSY` (5) — Database is locked
- `SQLITE_LOCKED` (11) — A table in the database is locked
- `SQLITE_MISUSE` (21) — Library used incorrectly
- `SQLITE_NOMEM` (13) — A malloc failed
- `SQLITE_IOERR` (10) — Some kind of I/O error
- `SQLITE_INTERRUPT` (9) — Operation terminated by sqlite3_interrupt()

Error messages:
- `sqlite3_errmsg(db)` — Human-readable error string
- `sqlite3_extended_errcode(db)` — Extended result code with additional detail
- `sqlite3_errcode(stmt)` — Error for a specific statement

## Configuration

Global configuration (must be called before `sqlite3_open()`):
```c
// Enable extended result codes
sqlite3_config(SQLITE_CONFIG_EXTRA_INIT, ...);

// Set memory allocation subsystem
sqlite3_config(SQLITE_CONFIG_MALLOC, &myMalloc, ...);
```

Per-connection configuration:
```c
// Enable WAL mode
sqlite3_exec(db, "PRAGMA journal_mode=WAL", NULL, NULL, NULL);

// Enable foreign key enforcement
sqlite3_exec(db, "PRAGMA foreign_keys=ON", NULL, NULL, NULL);

// Set cache size (in pages)
sqlite3_exec(db, "PRAGMA cache_size=-64000", NULL, NULL, NULL);

// Enable synchronous mode
sqlite3_exec(db, "PRAGMA synchronous=NORMAL", NULL, NULL, NULL);
```

## Custom SQL Functions

Register application-defined functions in C:

```c
static void myFunc(sqlite3_context *context, int argc, sqlite3_value **argv) {
    if (argc != 1 || sqlite3_value_type(argv[0]) != SQLITE_TEXT) {
        sqlite3_result_null(context);
        return;
    }
    const unsigned char *input = sqlite3_value_text(argv[0]);
    // Process input...
    sqlite3_result_text(context, result, -1, SQLITE_TRANSIENT);
}

sqlite3_create_function(db, "my_func", 1, SQLITE_UTF8, NULL,
                        myFunc, NULL, NULL);
```

## Backup API

Copy a database online without blocking readers:

```c
sqlite3 *source = ...;  // Open source database
sqlite3 *dest = ...;    // Open destination database

sqlite3_backup *backup = sqlite3_backup_init(dest, "main",
                                              source, "main");
if (backup) {
    int rc = SQLITE_OK;
    while (rc == SQLITE_OK) {
        rc = sqlite3_backup_step(backup, -1);  // -1 = all remaining pages
    }
    sqlite3_backup_finish(backup);
}
```

## Thread Safety

SQLite supports three threading modes:

- **Single-thread** — All mutexes disabled. Unsafe for multi-threaded use.
- **Multi-thread** — Safe for multiple threads as long as no single connection is used by more than one thread simultaneously.
- **Serialized** (default) — Any API call from any thread on any connection is safe.

Check the mode at runtime:
```c
int mode = sqlite3_threadsafe();
// Returns 0=single-thread, 1=multi-thread, 2=serialized
```

## Memory Management

SQLite provides its own memory allocation interface. The application can override it:
- `sqlite3_malloc()`, `sqlite3_free()`, `sqlite3_realloc()` — Use SQLite's allocator
- `sqlite3_msize(ptr)` — Actual allocated size of a block
- `sqlite3_memory_used()` — Current bytes allocated
- `sqlite3_memory_highwater()` — Peak bytes allocated
