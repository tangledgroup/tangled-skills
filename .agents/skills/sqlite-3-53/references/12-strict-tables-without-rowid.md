# STRICT Tables and WITHOUT ROWID

Advanced table types in SQLite 3.53 for type enforcement and optimization.

## STRICT Tables

STRICT tables enforce rigid type checking, mimicking traditional SQL database behavior.

### Creating STRICT Tables

```sql
-- Enable strict mode for a table
CREATE STRICT TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER,
    balance REAL,
    active BLOB  -- Used as boolean (0/1)
);

-- STRICT keyword can also be at column level
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT STRICT NOT NULL,
    price REAL STRICT,
    metadata TEXT  -- Not strict, allows any type
);
```

### Type Enforcement Rules

In STRICT tables, each column enforces its declared affinity:

| Declared Type | Allowed Types | Rejected Types |
|--------------|---------------|----------------|
| INTEGER | INTEGER only | TEXT, REAL, BLOB |
| REAL | INTEGER, REAL | TEXT, BLOB |
| TEXT | TEXT only | INTEGER, REAL, BLOB |
| BLOB | BLOB only | INTEGER, REAL, TEXT |
| NUMERIC | INTEGER, REAL | TEXT, BLOB |
| ANY/NONE | Any type | None |

### Examples of Type Enforcement

```sql
-- STRICT table with INTEGER column
CREATE STRICT TABLE counts (name TEXT, value INTEGER);

INSERT INTO counts VALUES ('one', 1);        -- ✓ OK
INSERT INTO counts VALUES ('two', '2');      -- ✗ ERROR: type mismatch
INSERT INTO counts VALUES ('three', 3.0);    -- ✗ ERROR: REAL not allowed

-- Non-STRICT table (default behavior)
CREATE TABLE flexible (name TEXT, value INTEGER);

INSERT INTO flexible VALUES ('one', 1);      -- ✓ OK
INSERT INTO flexible VALUES ('two', '2');    -- ✓ OK (stored as TEXT)
INSERT INTO flexible VALUES ('three', 3.0);  -- ✓ OK (stored as REAL)
```

### Benefits of STRICT Tables

1. **Data Integrity** - Prevents accidental type mismatches
2. **Bug Prevention** - Catches type errors at insert time
3. **Documentation** - Schema clearly indicates expected types
4. **Migration Path** - Easier migration from other SQL databases
5. **Query Optimization** - Planner can make stronger assumptions

### When to Use STRICT Tables

- **Use STRICT when:**
  - Building production applications requiring data integrity
  - Migrating from PostgreSQL, MySQL, or other strict SQL databases
  - Working with teams where type safety prevents bugs
  - Creating library or framework databases
  
- **Don't use STRICT when:**
  - Building prototypes or experiments
  - Needing flexible schema for polymorphic data
  - Working with legacy code expecting dynamic typing

### Column-Level STRICT

Mix strict and flexible columns in the same table:

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER STRICT NOT NULL,    -- Must be integer
    total REAL STRICT NOT NULL,             -- Must be numeric
    status TEXT STRICT CHECK(status IN ('pending', 'completed')),
    metadata TEXT,                          -- Flexible: JSON or any type
    extra_data BLOB                         -- Flexible: binary or anything
);
```

## WITHOUT ROWID Tables

WITHOUT ROWID tables optimize storage and access for specific use cases.

### Understanding ROWID

Every SQLite table has a hidden `rowid` (also accessible as `oid` or `_rowid_`) that uniquely identifies each row:

```sql
-- Regular table with implicit rowid
CREATE TABLE users (
    name TEXT,
    email TEXT
);

INSERT INTO users VALUES ('Alice', 'alice@example.com');

-- Access the hidden rowid
SELECT rowid, * FROM users;
-- Output: 1|Alice|alice@example.com

-- Query using rowid (very fast)
SELECT * FROM users WHERE rowid = 1;
```

### Creating WITHOUT ROWID Tables

```sql
-- Table without rowid storage
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;

-- Must have a PRIMARY KEY with UNIQUE constraint
CREATE TABLE products (
    sku TEXT NOT NULL,
    name TEXT,
    price REAL,
    PRIMARY KEY (sku)
) WITHOUT ROWID;

-- Composite primary key also works
CREATE TABLE inventory (
    warehouse_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    PRIMARY KEY (warehouse_id, product_id)
) WITHOUT ROWID;
```

### How WITHOUT ROWID Works

**Regular table (with rowid):**
- Data stored in B-tree keyed by rowid
- PRIMARY KEY is a separate index pointing to rowid
- Extra storage for rowid column

**WITHOUT ROWID table:**
- Data stored in B-tree keyed by PRIMARY KEY
- No separate rowid storage
- PRIMARY KEY values are the actual record keys
- More compact storage for certain access patterns

### Storage Comparison

```sql
-- Regular table
CREATE TABLE users_rowid (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

-- WITHOUT ROWID equivalent
CREATE TABLE users_no_rowid (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
) WITHOUT ROWID;

-- Insert same data
INSERT INTO users_rowid VALUES (1, 'Alice', 'alice@example.com');
INSERT INTO users_no_rowid VALUES (1, 'Alice', 'alice@example.com');

-- Query by primary key is faster in WITHOUT ROWID
EXPLAIN QUERY PLAN SELECT * FROM users_rowid WHERE id = 1;
-- USE INDEX users_rowid ON users_rowid(id)

EXPLAIN QUERY PLAN SELECT * FROM users_no_rowid WHERE id = 1;
-- SCAN TABLE users_no_rowid USING KEY (1)  -- Direct access!
```

### Benefits of WITHOUT ROWID

1. **Faster PRIMARY KEY lookups** - Direct B-tree access, no index indirection
2. **Smaller storage** - No duplicate primary key storage in separate index
3. **Better for cover indices** - All data in the primary key structure
4. **Ideal for key-value stores** - Natural fit for lookup-by-key patterns

### When to Use WITHOUT ROWID

**Use WITHOUT ROWID when:**
- Most queries filter by PRIMARY KEY
- Building key-value store patterns
- Table has single-column or small composite PRIMARY KEY
- Storage optimization is critical
- Primary key is naturally clustered (e.g., UUIDs, hashes)

**Don't use WITHOUT ROWID when:**
- Frequently querying by non-primary-key columns
- Needing rowid for joins or references
- Primary key is large (wide composite keys)
- Using AUTOINCREMENT (works but less beneficial)

### Requirements and Limitations

```sql
-- MUST have PRIMARY KEY
CREATE TABLE bad1 (name TEXT) WITHOUT ROWID;  -- ✗ ERROR

-- PRIMARY KEY must be UNIQUE (implicit)
CREATE TABLE bad2 (
    id INTEGER,
    name TEXT,
    PRIMARY KEY (id)  -- ✓ OK
) WITHOUT ROWID;

-- Can have multiple columns in PRIMARY KEY
CREATE TABLE good (
    tenant_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    data TEXT,
    PRIMARY KEY (tenant_id, resource_id)
) WITHOUT ROWID;
```

### Cannot Use rowid Pseudocolumn

```sql
-- This won't work in WITHOUT ROWID tables
SELECT rowid FROM config;  -- ✗ ERROR: no such column: rowid
SELECT oid FROM config;    -- ✗ ERROR: no such column: oid

-- Must use the primary key instead
SELECT key FROM config WHERE key = 'setting_name';
```

### AUTOINCREMENT with WITHOUT ROWID

```sql
-- Works but consider implications
CREATE TABLE sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT
) WITHOUT ROWID;

-- AUTOINCREMENT prevents reuse of rowids even after deletion
-- In WITHOUT ROWID, this means primary key values won't be reused
```

## Combined: STRICT and WITHOUT ROWID

Combine both features for maximum type safety and performance:

```sql
CREATE STRICT TABLE config (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    created_at INTEGER NOT NULL
) WITHOUT ROWID;

-- Benefits:
-- 1. Type enforcement on all columns
-- 2. Fast key-based lookups
-- 3. Compact storage
-- 4. Clear schema documentation
```

## Migration Strategies

### Converting to STRICT

```sql
-- 1. Create new STRICT table
CREATE STRICT TABLE users_new (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);

-- 2. Migrate data (will fail if type mismatches exist)
INSERT INTO users_new SELECT * FROM users_old;

-- 3. Verify and swap
ALTER TABLE users_old RENAME TO users_backup;
ALTER TABLE users_new RENAME TO users;
```

### Converting to WITHOUT ROWID

```sql
-- 1. Ensure table has suitable PRIMARY KEY
-- 2. Create new WITHOUT ROWID table
CREATE TABLE config_new (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;

-- 3. Migrate data
INSERT INTO config_new SELECT * FROM config_old;

-- 4. Swap tables
DROP TABLE config_old;
ALTER TABLE config_new RENAME TO config;
```

## Performance Comparison

### Benchmark Example

```sql
-- Create test tables
CREATE TABLE with_rowid (
    id INTEGER PRIMARY KEY,
    data TEXT
);

CREATE TABLE without_rowid (
    id INTEGER PRIMARY KEY,
    data TEXT
) WITHOUT ROWID;

-- Insert 100,000 rows
WITH RECURSIVE cnt(x) AS (
    VALUES(1) UNION ALL SELECT x+1 FROM cnt WHERE x < 100000
)
INSERT INTO with_rowid SELECT x, 'data_' || x FROM cnt;

WITH RECURSIVE cnt(x) AS (
    VALUES(1) UNION ALL SELECT x+1 FROM cnt WHERE x < 100000
)
INSERT INTO without_rowid SELECT x, 'data_' || x FROM cnt;

-- Query by primary key (WITHOUT ROWID is faster)
.timer on
SELECT * FROM with_rowid WHERE id = 50000;
SELECT * FROM without_rowid WHERE id = 50000;

-- Query by non-key column (similar performance)
SELECT * FROM with_rowid WHERE data = 'data_50000';
SELECT * FROM without_rowid WHERE data = 'data_50000';
```

## Best Practices

1. **Use STRICT for new production tables** - Type safety prevents bugs
2. **Consider WITHOUT ROWID for key-value patterns** - Configuration, caches, lookups
3. **Test migration carefully** - Ensure data types match before converting to STRICT
4. **Profile before optimizing** - Measure actual performance impact
5. **Document your choices** - Comment why STRICT or WITHOUT ROWID is used

## Common Patterns

### Configuration Store

```sql
CREATE STRICT TABLE app_config (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    description TEXT
) WITHOUT ROWID;

-- Fast lookups by key, type-safe values
INSERT INTO app_config VALUES ('max_upload_size', '10485760', '10MB limit');
SELECT value FROM app_config WHERE key = 'max_upload_size';
```

### Cache Table

```sql
CREATE STRICT TABLE query_cache (
    cache_key TEXT PRIMARY KEY NOT NULL,
    result BLOB NOT NULL,
    expires_at INTEGER NOT NULL
) WITHOUT ROWID;

-- Efficient key-based caching
INSERT OR REPLACE INTO query_cache VALUES ('user_123', X'DEADBEEF', 1700000000);
SELECT result FROM query_cache WHERE cache_key = 'user_123' AND expires_at > strftime('%s', 'now');
```

### Key-Value Store

```sql
CREATE STRICT TABLE kv_store (
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    value BLOB,
    PRIMARY KEY (namespace, key)
) WITHOUT ROWID;

-- Namespaced key-value storage
INSERT INTO kv_store VALUES ('session', 'abc123', X'SESSION_DATA');
SELECT value FROM kv_store WHERE namespace = 'session' AND key = 'abc123';
```

## Related Documentation

- [SQL Basics](01-sql-basics.md) - Table creation syntax
- [Performance Optimization](07-performance.md) - Indexing strategies
- [Data Types](09-sql-functions.md) - Type affinity details
