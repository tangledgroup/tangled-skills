# Core Concepts

## Architecture Overview

### Embedded Database Model

DuckDB is designed as an **embedded analytical database** - it runs as a library within your application rather than as a separate server process. This architecture provides several benefits:

- **No server setup**: Link the library and start querying immediately
- **Zero network overhead**: Direct memory access, no serialization/deserialization
- **Language integration**: Native bindings for Python, R, Java, C++, and more
- **Portability**: Single binary or package installation per platform
- **Lightweight**: Minimal dependencies and resource requirements

### Columnar Storage

Unlike traditional row-oriented databases (MySQL, PostgreSQL for OLTP), DuckDB stores data in **columnar format**:

```
Row-oriented:           Columnar:
[A1, B1, C1]            [A1, A2, A3]
[A2, B2, C2]    →       [B1, B2, B3]
[A3, B3, C3]            [C1, C2, C3]
```

**Benefits:**
- Faster aggregations (read only needed columns)
- Better compression (similar values stored together)
- Vectorized execution (process batches efficiently)
- Predicate pushdown (filter before reading all data)

### Vectorized Execution Engine

DuckDB processes data in **vectors** (batches of 2048 rows by default):

```python
# Instead of processing row-by-row:
for row in table:
    if row['amount'] > 1000:
        total += row['amount']

# DuckDB processes vectorized:
vector = read_column('amount', batch_size=2048)
mask = vector > 1000
total = sum(vector[mask])
```

**Advantages:**
- CPU cache efficiency (sequential memory access)
- SIMD instruction utilization (process multiple values per cycle)
- Reduced function call overhead
- Better branch prediction

## Data Types

### Scalar Types

#### Integer Types

| Type | Size | Range |
|------|------|-------|
| `TINYINT` | 1 byte | -128 to 127 |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 |
| `INTEGER` | 4 bytes | -2B to 2B |
| `BIGINT` | 8 bytes | -9Q to 9Q |

```sql
SELECT 
    CAST(42 AS TINYINT),
    CAST(1000 AS SMALLINT),
    CAST(1000000 AS INTEGER),
    CAST(10000000000 AS BIGINT);
```

#### Floating Point Types

| Type | Precision | Notes |
|------|-----------|-------|
| `FLOAT` / `REAL` | 32-bit | Single precision |
| `DOUBLE` / `DOUBLE PRECISION` | 64-bit | Double precision |
| `HUGEINT` | 128-bit | For very large integers |

```sql
SELECT 
    3.14 AS float_value,
    3.14159265359 AS double_value;
```

#### String Types

| Type | Description |
|------|-------------|
| `VARCHAR` | Variable-length string (default) |
| `VARCHAR(n)` | Variable-length with max length hint |
| `CHAR(n)` | Fixed-length, space-padded |
| `BLOB` | Binary large object |

```sql
SELECT 
    'hello'::VARCHAR,
    'world'::VARCHAR(5),
    'test'::CHAR(10);  -- Padded to 10 chars with spaces
```

#### Temporal Types

| Type | Format | Example |
|------|--------|---------|
| `DATE` | YYYY-MM-DD | `2024-01-15` |
| `TIME` | HH:MM:SS[.fraction] | `14:30:00.123` |
| `TIMESTAMP` | Combined date+time | `2024-01-15 14:30:00` |
| `TIMESTAMPTZ` | Timestamp with timezone | `2024-01-15 14:30:00 UTC` |
| `INTERVAL` | Time duration | `INTERVAL '3 days'` |

```sql
SELECT 
    DATE '2024-01-15',
    TIME '14:30:00',
    TIMESTAMP '2024-01-15 14:30:00',
    CURRENT_TIMESTAMP,
    INTERVAL '7 days';
```

### Nested Types

#### Arrays

Arrays store ordered collections of homogeneous elements:

```sql
-- Create arrays
SELECT 
    [1, 2, 3] AS int_array,
    ['a', 'b', 'c'] AS string_array,
    LIST(1, 2, 3) AS list_function;

-- Array operations
SELECT 
    [1, 2, 3] || [4, 5, 6] AS concatenated,  -- [1,2,3,4,5,6]
    [1, 2, 3][1] AS first_element,           -- 1 (1-indexed)
    LIST_LENGTH([1, 2, 3]) AS length;        -- 3

-- Query arrays from table
SELECT 
    customer_id,
    purchases[1] AS first_purchase,
    LIST_LENGTH(purchases) AS purchase_count
FROM customers;
```

#### Structs

Structs store named fields with different types:

```sql
-- Create structs
SELECT 
    STRUCT_PACK(
        id := 1,
        name := 'Alice',
        age := 30
    ) AS person;

-- Access struct fields
SELECT 
    (STRUCT_PACK(x := 10, y := 20)).x AS x_coord,
    (STRUCT_PACK(x := 10, y := 20)).y AS y_coord;

-- Struct from table column
SELECT 
    customer.id,
    customer.name,
    customer.address.city
FROM orders;  -- customer is a STRUCT type
```

#### Maps

Maps store key-value pairs:

```sql
-- Create maps
SELECT 
    MAP(['a', 'b', 'c'], [1, 2, 3]) AS letter_to_num;

-- Access map values
SELECT 
    MAP(['x', 'y'], [10, 20])['x'] AS x_value;  -- 10

-- Map operations
SELECT 
    MAP_KEYS(MAP(['a', 'b'], [1, 2])) AS keys,      -- ['a', 'b']
    MAP_VALUES(MAP(['a', 'b'], [1, 2])) AS values;  -- [1, 2]
```

### Type Conversion

#### Implicit Conversion

DuckDB automatically converts compatible types:

```sql
SELECT 
    1 + 2.5,           -- INTEGER + DOUBLE → DOUBLE
    '123'::INTEGER,    -- String literal to integer
    TRUE = 1;          -- BOOLEAN to INTEGER
```

#### Explicit Conversion (CAST)

```sql
SELECT 
    CAST('42' AS INTEGER),
    CAST(42 AS VARCHAR),
    CAST('2024-01-15' AS DATE),
    42::BIGINT,        -- Shorthand syntax
    'true'::BOOLEAN;
```

#### TRY_CAST (Safe Conversion)

Returns NULL instead of error on failure:

```sql
SELECT 
    TRY_CAST('42' AS INTEGER),     -- 42
    TRY_CAST('not_a_number' AS INTEGER);  -- NULL (no error)
```

## Query Execution Model

### Lazy Evaluation

DuckDB uses **lazy evaluation** - queries are not executed until results are requested:

```python
import duckdb

# Query is NOT executed yet
relation = duckdb.sql("SELECT * FROM large_table WHERE amount > 1000")

# Execution happens when we fetch results
result = relation.fetchdf()  # Now query runs
```

**Benefits:**
- Query optimization before execution
- Composition of multiple operations
- Efficient execution planning

### Query Optimization

DuckDB's optimizer performs:

1. **Predicate Pushdown**: Filters applied as early as possible
2. **Column Pruning**: Only read needed columns
3. **Projection Pushdown**: Limit columns at data source
4. **Join Reordering**: Optimal join sequence selection
5. **Constant Folding**: Evaluate constants at planning time

```sql
-- DuckDB optimizes this automatically:
SELECT name, age
FROM users
WHERE age > 18 AND city = 'NYC'
ORDER BY name
LIMIT 100;

-- Only reads: name, age, city columns
-- Applies filters before sorting
-- Stops after 100 rows
```

### Explain Plans

Analyze query execution:

```sql
-- Basic execution plan
EXPLAIN SELECT * FROM users WHERE age > 18;

-- Detailed plan with statistics
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 18;

-- Graphical output (in CLI)
EXPLAIN (TYPE GRAPHICAL) SELECT * FROM users;
```

Example output:
```
ProjectedExpression [name, age]
  FilterCondition [age > 18]
    TableScan [users]
```

## Memory Management

### In-Memory vs Persistent

```python
import duckdb

# In-memory database (volatile)
con = duckdb.connect()  # or duckdb.connect(':memory:')
con.sql("CREATE TABLE temp (x INTEGER)")
# Data lost when connection closes

# Persistent database
con = duckdb.connect('my_database.db')
con.sql("CREATE TABLE permanent (x INTEGER)")
# Data persists across sessions
```

### Memory Configuration

```sql
-- Set memory limit (default: 80% of available RAM)
PRAGMA memory_limit = '4GB';

-- Check current settings
PRAGMA memory_limit;
PRAGMA threads;

-- Configure parallelism
SET threads = 4;
```

### Spill to Disk

When memory is exhausted, DuckDB automatically spills to disk:

```sql
-- Enable/disable spill to disk
SET enable_object_cache = true;

-- Configure temporary directory
SET temp_directory = '/tmp/duckdb';
```

## Transaction Model

DuckDB supports ACID transactions with **snapshot isolation**:

```sql
-- Begin transaction
BEGIN;

-- Multiple statements
INSERT INTO users VALUES (1, 'Alice');
INSERT INTO users VALUES (2, 'Bob');
UPDATE users SET age = 30 WHERE id = 1;

-- Commit all changes
COMMIT;

-- Or rollback
ROLLBACK;
```

### Isolation Levels

- **Read Committed** (default): See committed changes only
- **Serializable**: Strict isolation for concurrent transactions

```sql
SET transaction_isolation = 'serializable';
```

## Concurrency Model

### Read-Write Locks

- Multiple readers can query simultaneously
- Writers acquire exclusive locks
- Readers wait for writers to complete

```python
import duckdb
import threading

# Multiple read connections work fine
con1 = duckdb.connect('shared.db')
con2 = duckdb.connect('shared.db')

# Both can read concurrently
result1 = con1.sql("SELECT * FROM data")
result2 = con2.sql("SELECT * FROM data")
```

### Write Concurrency

Single writer at a time (file-level locking):

```python
# These will serialize automatically
con1.sql("INSERT INTO data VALUES (1)")
con2.sql("INSERT INTO data VALUES (2)")  # Waits for con1
```

## Best Practices

### When to Use Nested Types

**Use arrays when:**
- Storing lists of related values (tags, categories)
- Fixed-size collections with known cardinality
- Performance is critical (avoid joins)

**Use structs when:**
- Grouping related fields logically
- Representing JSON-like structures
- Returning complex query results

**Use maps when:**
- Key-value lookups needed
- Sparse data representation
- Configuration or metadata storage

### Type Selection Guidelines

| Use Case | Recommended Type |
|----------|------------------|
| Whole numbers < 2B | `INTEGER` |
| Large integers | `BIGINT` |
| Decimal precision | `DECIMAL(p,s)` |
| Text data | `VARCHAR` |
| Fixed-length codes | `CHAR(n)` |
| Binary data | `BLOB` |
| Timestamps with TZ | `TIMESTAMPTZ` |
| Time durations | `INTERVAL` |

### Performance Tips

1. **Use appropriate types**: Don't use BIGINT if INTEGER suffices
2. **Avoid unnecessary type conversions**: Can prevent vectorization
3. **Leverage nested types**: Reduce join complexity
4. **Use Parquet format**: Columnar storage on disk
5. **Configure memory limits**: Prevent OOM in multi-tenant scenarios

## Common Pitfalls

### Type Coercion Surprises

```sql
-- This might not do what you expect:
SELECT '100' + 50;  -- String concatenation? Or numeric addition?

-- Be explicit:
SELECT '100'::INTEGER + 50;  -- 150
```

### NULL Handling

```sql
-- NULL comparisons always return NULL (not TRUE/FALSE)
SELECT NULL = NULL;  -- Returns NULL, not TRUE

-- Use IS NULL / IS NOT NULL
SELECT * FROM users WHERE email IS NULL;

-- COALESCE for default values
SELECT COALESCE(email, 'no-email@example.com') FROM users;
```

### Integer Division

```sql
SELECT 5 / 2;      -- Returns 2 (integer division)
SELECT 5.0 / 2;    -- Returns 2.5 (floating point)
SELECT 5 / 2.0;    -- Returns 2.5 (type coercion)
```
