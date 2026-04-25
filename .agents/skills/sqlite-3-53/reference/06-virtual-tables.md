# Virtual Tables and Extensions

Complete guide to SQLite virtual tables, including built-in modules (FTS5, R*Tree), creating custom virtual tables, loadable extensions, and module development.

## Overview

Virtual tables provide flexible data storage and retrieval mechanisms:

- **Built-in modules**: FTS5 (full-text search), R*Tree (spatial indexing)
- **Custom modules**: User-defined virtual table implementations
- **Loadable extensions**: Dynamic library-based functionality
- **Table-valued functions**: Query-like interfaces to data

## Built-in Virtual Table Modules

### FTS5 (Full-Text Search)

See [Full-Text Search with FTS5](05-fts5.md) for comprehensive documentation.

```sql
-- Basic FTS5 table
CREATE VIRTUAL TABLE documents USING fts5(title, content);

-- With configuration
CREATE VIRTUAL TABLE articles USING fts5(
    title,
    body,
    tokenize='unicode61 "en"',
    prefix=3
);
```

### R*Tree (Spatial Indexing)

Efficient spatial data storage and range queries:

```sql
-- Create R*Tree index
CREATE VIRTUAL TABLE spatial_index USING rtree(
    id,              -- Integer primary key
    minx, maxx,      -- X-axis range
    miny, maxy       -- Y-axis range
);

-- Insert spatial data (bounding boxes)
INSERT INTO spatial_index VALUES (1, 0.0, 10.0, 0.0, 10.0);   -- Box 1
INSERT INTO spatial_index VALUES (2, 5.0, 15.0, 5.0, 15.0);   -- Box 2
INSERT INTO spatial_index VALUES (3, 20.0, 30.0, 20.0, 30.0); -- Box 3

-- Find overlapping regions
SELECT * FROM spatial_index 
WHERE maxx >= 5 AND minx <= 10 AND maxy >= 5 AND miny <= 10;
-- Returns: boxes 1 and 2 (overlap with query region)

-- Find containing regions
SELECT * FROM spatial_index 
WHERE minx <= 7 AND maxx >= 13 AND miny <= 7 AND maxy >= 13;
-- Returns: box 2 (contains point 7,7)

-- Multi-dimensional (add minz, maxz for 3D)
CREATE VIRTUAL TABLE spatial_3d USING rtree(
    id,
    minx, maxx,
    miny, maxy,
    minz, maxz
);
```

### R*Tree with External Content

Link R*Tree to external table:

```sql
-- Create content table
CREATE TABLE polygons (
    id INTEGER PRIMARY KEY,
    name TEXT,
    geometry TEXT
);

-- Create R*Tree index referencing content
CREATE VIRTUAL TABLE polygons_spatial USING rtree(
    id,
    minx, maxx,
    miny, maxy,
    content='polygons'  -- External content table
);

-- Insert into both tables
INSERT INTO polygons VALUES (1, 'Park', 'POLYGON(...)');
INSERT INTO polygons_spatial VALUES (1, 0.0, 10.0, 0.0, 10.0);

-- Query with spatial filter
SELECT p.* 
FROM polygons p
JOIN polygons_spatial s ON p.id = s.id
WHERE s.maxx >= 5 AND s.minx <= 10;
```

## Creating Custom Virtual Tables

### Virtual Table Interface

Virtual tables implement these methods:

```c
// Virtual table module structure
typedef struct sqlite3_vtab {
    struct sqlite3_vtab *pNext;  // Next in list
    sqlite3_mod *pModule;        // Module that created this vtab
    char *zErrMsg;               // Error message
    // Module-specific data follows
} sqlite3_vtab;

typedef struct sqlite3_vtab_cursor {
    sqlite3_vtab *pVtab;         // Virtual table
    // Cursor-specific data follows
} sqlite3_vtab_cursor;

// Module definition
struct sqlite3_module {
    int iVersion;                // API version (1 or 2)
    int (*xCreate)(sqlite3*, void*, int, const char**, 
                   sqlite3_vtab**, char**);
    int (*xConnect)(sqlite3*, void*, int, const char**,
                    sqlite3_vtab**, char**);
    int (*xBestIndex)(sqlite3_vtab*, sqlite3_index_info*);
    int (*xDisconnect)(sqlite3_vtab*);
    int (*xDestroy)(sqlite3_vtab*);
    int (*xOpen)(sqlite3_vtab*, sqlite3_vtab_cursor**);
    int (*xClose)(sqlite3_vtab_cursor*);
    int (*xFilter)(sqlite3_vtab_cursor*, int, const char*, int, 
                   sqlite3_index_constraint**);
    int (*xNext)(sqlite3_vtab_cursor*);
    int (*xEof)(sqlite3_vtab_cursor*);
    int (*xColumn)(sqlite3_vtab_cursor*, sqlite3_context*, int);
    int (*xRowid)(sqlite3_vtab_cursor*, sqlite_int64*);
    // Optional methods: xUpdate, xBegin, xCommit, xRollback, etc.
};
```

### Simple Example: Sequence Generator

```c
// C code for simple sequence virtual table

typedef struct SeqVtab {
    sqlite3_vtab base;
    int current_value;
} SeqVtab;

typedef struct SeqCursor {
    sqlite3_vtab_cursor base;
    int value;
} SeqCursor;

// Create virtual table
static int seqCreate(sqlite3 *db, void *pAux, int argc, char **argv,
                     sqlite3_vtab **ppVtab, char **pzErr) {
    SeqVtab *p = malloc(sizeof(SeqVtab));
    p->base.zErrMsg = NULL;
    p->current_value = 0;
    *ppVtab = &p->base;
    return SQLITE_OK;
}

// Connect to existing table
static int seqConnect(sqlite3 *db, void *pAux, int argc, char **argv,
                      sqlite3_vtab **ppVtab, char **pzErr) {
    return seqCreate(db, pAux, argc, argv, ppVtab, pzErr);
}

// Open cursor
static int seqOpen(sqlite3_vtab *pVtab, sqlite3_vtab_cursor **ppCursor) {
    SeqCursor *p = malloc(sizeof(SeqCursor));
    p->value = 0;
    *ppCursor = &p->base;
    return SQLITE_OK;
}

// Move to next row
static int seqNext(sqlite3_vtab_cursor *pCursor) {
    SeqCursor *p = (SeqCursor*)pCursor;
    p->value++;
    return SQLITE_OK;
}

// Check if at end
static int seqEof(sqlite3_vtab_cursor *pCursor) {
    // Never ends for infinite sequence
    return 0;
}

// Return column value
static int seqColumn(sqlite3_vtab_cursor *pCursor, sqlite3_context *ctx, 
                     int iCol) {
    SeqCursor *p = (SeqCursor*)pCursor;
    if (iCol == 0) {
        sqlite3_result_int(ctx, p->value);
    } else {
        sqlite3_result_null(ctx);
    }
    return SQLITE_OK;
}

// Return rowid
static int seqRowid(sqlite3_vtab_cursor *pCursor, sqlite_int64 *pRowid) {
    SeqCursor *p = (SeqCursor*)pCursor;
    *pRowid = p->value;
    return SQLITE_OK;
}

// Close cursor
static int seqClose(sqlite3_vtab_cursor *pCursor) {
    free(pCursor);
    return SQLITE_OK;
}

// Destroy table
static int seqDestroy(sqlite3_vtab *pVtab) {
    free(pVtab);
    return SQLITE_OK;
}

// Disconnect
static int seqDisconnect(sqlite3_vtab *pVtab) {
    return SQLITE_OK;
}

// Module definition
static sqlite3_module seqModule = {
    1,                      // iVersion
    seqCreate,              // xCreate
    seqConnect,             // xConnect
    NULL,                   // xBestIndex (no indexing)
    seqDisconnect,          // xDisconnect
    seqDestroy,             // xDestroy
    seqOpen,                // xOpen
    seqClose,               // xClose
    NULL,                   // xFilter (no filtering)
    seqNext,                // xNext
    seqEof,                 // xEof
    seqColumn,              // xColumn
    seqRowid,               // xRowid
    NULL                    // xUpdate (read-only)
};

// Register module
sqlite3_create_vtab(db, "sequence", &seqModule, NULL);
```

### Using the Sequence Table

```sql
-- Create virtual table
CREATE VIRTUAL TABLE sequence USING sequence;

-- Generate sequence values
SELECT * FROM sequence LIMIT 10;
-- Returns: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

-- Use in INSERT
INSERT INTO counters (value) SELECT * FROM sequence LIMIT 100;
```

## Loadable Extensions

### Loading Extensions

```sql
-- Enable loadable extensions
PRAGMA compile_options;  -- Check if ENABLE_LOAD_EXTENSION is set

-- Load extension from shared library
LOAD EXTENSION 'libjson_ext.so';

-- Load with specific entry point
LOAD EXTENSION 'libmyext.so' 'my_init_function';

-- Platform-specific paths
-- Linux:   LOAD EXTENSION './libmyext.so';
-- macOS:   LOAD EXTENSION './libmyext.dylib';
-- Windows: LOAD EXTENSION '.\myext.dll';
```

### Enabling Load Extensions in C Code

```c
// Enable at program startup (before opening database)
sqlite3_config(SQLITE_CONFIG_ENABLE_LOAD_EXTENSION, NULL);

// Or per-connection
sqlite3_enable_load_extension(db, 1);

// Load extension
char *err_msg;
int rc = sqlite3_load_extension(db, "libextension.so", "init_func", &err_msg);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Load error: %s\n", err_msg);
    sqlite3_free(err_msg);
}
```

### Building Loadable Extensions

```c
// Extension entry point
__attribute__((visibility("default")))
int sqlite3_extension_init(
    sqlite3 *db,
    char **pzErrMsg,
    const sqlite3_api_routines *pApi
) {
    // Initialize extension here
    // Register functions, virtual tables, etc.
    
    if (error) {
        *pzErrMsg = sqlite3_mprintf("Error message");
        return SQLITE_ERROR;
    }
    
    return SQLITE_OK;
}

// Register custom function
sqlite3_create_function(
    db,
    "my_function",
    1,                    // Number of arguments
    SQLITE_UTF8,
    NULL,                 // Client data
    my_function_impl,     // Implementation
    NULL,                 // xStep (scalar function)
    NULL                  //xFinal (not aggregate)
);

// Register virtual table module
sqlite3_create_vtab(db, "my_module", &my_module, NULL);
```

### Compilation Commands

```bash
# Linux/macOS
gcc -shared -fPIC -o libmyext.so myext.c \
    $(pkg-config --cflags --libs sqlite3)

# With function export
gcc -shared -fPIC -o libmyext.so myext.c \
    -DSQLITE_EXTENSION_INIT_FUNC \
    $(pkg-config --cflags --libs sqlite3)

# macOS specific
clang -shared -fPIC -o libmyext.dylib myext.c \
    -I/usr/local/include/sqlite3 \
    -L/usr/local/lib -lsqlite3

# Windows (MinGW)
gcc -shared -o myext.dll myext.c \
    -DSDL_MAIN_NOIMPL \
    $(pkg-config --cflags --libs sqlite3)
```

## Table-Valued Functions

### Built-in Table Functions

#### json_each()

Decompose JSON array or object:

```sql
-- Array decomposition
SELECT * FROM json_each('[1, 2, 3]');
-- key | value | path
-- 0   | 1     | $[0]
-- 1   | 2     | $[1]
-- 2   | 3     | $[2]

-- Object decomposition
SELECT * FROM json_each('{"a": 1, "b": 2}');
-- key | value | path
-- a   | 1     | $.a
-- b   | 2     | $.b

-- In queries
SELECT 
    product_id,
    j.value AS tag
FROM products p, json_each(p.tags) j
WHERE j.value = 'sale';
```

#### json_tree()

Recursive JSON traversal:

```sql
SELECT * FROM json_tree('{"a": 1, "b": {"c": [2, 3]}}');
-- id | parent | key | type   | value | path
```

#### generate_series() (if available)

Generate number sequences:

```sql
-- Generate sequence 1 to 10
SELECT * FROM generate_series(1, 10);

-- With step
SELECT * FROM generate_series(0, 100, 10);
-- Returns: 0, 10, 20, ..., 100
```

### Creating Custom Table Functions

```c
// C code for custom table-valued function

typedef struct MyCursor {
    sqlite3_vtab_cursor base;
    int current;
    int max;
} MyCursor;

static int myOpen(sqlite3_vtab *p, sqlite3_vtab_cursor **pp) {
    MyCursor *cur = malloc(sizeof(MyCursor));
    cur->current = 0;
    cur->max = 100;  // Default max
    *pp = &cur->base;
    return SQLITE_OK;
}

static int myNext(sqlite3_vtab_cursor *p) {
    MyCursor *cur = (MyCursor*)p;
    cur->current++;
    return SQLITE_OK;
}

static int myEof(sqlite3_vtab_cursor *p) {
    MyCursor *cur = (MyCursor*)p;
    return cur->current > cur->max;
}

static int myColumn(sqlite3_vtab_cursor *p, sqlite3_context *ctx, int i) {
    MyCursor *cur = (MyCursor*)p;
    if (i == 0) {
        sqlite3_result_int(ctx, cur->current);
    } else {
        sqlite3_result_null(ctx);
    }
    return SQLITE_OK;
}

// Usage: SELECT * FROM my_function(50);  // Generates 0-50
```

## Popular Extensions

### mathfuncs (Mathematical Functions)

Adds advanced mathematical functions:

```sql
-- Load extension
LOAD EXTENSION 'libmathfuncs.so';

-- Trigonometric functions
SELECT sin(3.14159/2);     -- 1.0
SELECT cos(0);             -- 1.0
SELECT tan(3.14159/4);     -- ~1.0

-- Logarithms
SELECT log10(100);         -- 2.0
SELECT ln(2.71828);        -- ~1.0

-- Power and root
SELECT sqrt(16);           -- 4.0
SELECT pow(2, 10);         -- 1024

-- Rounding
SELECT round(3.567, 2);    -- 3.57
SELECT floor(3.9);         -- 3.0
SELECT ceil(3.1);          -- 4.0
```

### geo (Geospatial Functions)

Geographic and geometric operations:

```sql
LOAD EXTENSION 'libgeo.so';

-- Distance calculation
SELECT haversine_distance(
    40.7128, -74.0060,  -- New York
    51.5074, -0.1278    -- London
);

-- Bounding box intersection
SELECT bbox_intersects(
    -180, -90, 180, 90,
    -100, 40, -90, 50
);
```

### datetime extensions (Extended Date/Time)

Additional date/time functions:

```sql
LOAD EXTENSION 'libdatetime_ext.so';

-- Business days between dates
SELECT business_days_between('2024-01-01', '2024-01-31');

-- Age calculation
SELECT age_in_years('1990-05-15', 'now');

-- Working hours calculation
SELECT working_hours_between('2024-01-01 09:00', '2024-01-01 17:00');
```

## Security Considerations

### Sandboxed Extensions

```c
// Mark extension as safe (no file I/O, network, etc.)
sqlite3_create_function_v2(
    db,
    "safe_func",
    1,
    SQLITE_UTF8 | SQLITE_INNOCUOUS,  // INNOCUOUS flag
    NULL,
    safe_func_impl,
    NULL,
    NULL
);
```

### Function Flags

| Flag | Description |
|------|-------------|
| `SQLITE_INNOCUOUS` | Safe for use in indexes, triggers |
| `SQLITE_DETERMINISTIC` | Same input always produces same output |
| `SQLITE_DIRECTONLY` | Cannot be used in views, triggers |
| `SQLITE_SUBTYPE` | Accepts subtype information |

### Secure Extension Loading

```c
// Only load from trusted paths
int is_trusted_path(const char *path) {
    return strcmp(path, "/trusted/lib.so") == 0;
}

if (is_trusted_path(extension_path)) {
    sqlite3_load_extension(db, extension_path, "init", &err);
} else {
    fprintf(stderr, "Untrusted extension path\n");
}
```

## Debugging Virtual Tables

### Verbose Mode

```sql
-- Enable verbose error messages
PRAGMA verbose_errors = ON;

-- Check module list
PRAGMA module_list;

-- Test virtual table creation
CREATE VIRTUAL TABLE test USING fts5(content);
SELECT * FROM test WHERE test MATCH 'test';
DROP TABLE test;
```

### Performance Analysis

```sql
-- Analyze query plan with virtual tables
EXPLAIN QUERY PLAN 
SELECT * FROM documents WHERE documents MATCH 'search term';

-- Check if index is being used
-- Look for "USING INDEX" in output
```

## Best Practices

1. **Use built-in modules** when available (FTS5, R*Tree)
2. **Validate extension sources** before loading
3. **Test thoroughly** before production deployment
4. **Document custom modules** with usage examples
5. **Handle errors gracefully** in xCreate and xConnect
6. **Implement xBestIndex** for query optimization
7. **Use SQLITE_INNOCUOUS** for deterministic functions
8. **Consider thread safety** in extension implementations

## Troubleshooting

### Extension Load Failures

```sql
-- Check compile options
PRAGMA compile_options;  -- Should include ENABLE_LOAD_EXTENSION

-- Check error message
SELECT last_insert_rowid(), sqlite3_errmsg();

-- Verify file exists and is readable
-- Linux: ls -la libextension.so
-- Check permissions: chmod 755 libextension.so
```

### Virtual Table Errors

```sql
-- Check table creation
CREATE VIRTUAL TABLE test USING fts5(content);

-- If fails, check module availability
SELECT name FROM sqlite_master WHERE type='table' AND name='test';

-- Rebuild if corrupted
DELETE FROM test;
INSERT INTO test(test) VALUES('reindex');
```
