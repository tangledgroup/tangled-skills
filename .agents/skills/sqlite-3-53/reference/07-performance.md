# Performance Optimization

Comprehensive guide to SQLite performance tuning, query optimization, indexing strategies, EXPLAIN analysis, and best practices for high-performance applications.

## Query Analysis

### EXPLAIN QUERY PLAN

Analyze query execution strategy:

```sql
-- Basic query plan
EXPLAIN QUERY PLAN 
SELECT * FROM users WHERE email = 'alice@example.com';

-- Output example:
-- id | parent |外侧 | detail
-- 1  | 0      | 0   | SEARCH TABLE users USING INDEX idx_users_email (email=?)

-- Without index (full table scan)
EXPLAIN QUERY PLAN 
SELECT * FROM users WHERE name LIKE '%alice%';

-- Output:
-- 1  | 0      | 0   | SCAN TABLE users
```

### Interpreting Query Plans

| Operation | Description | Performance |
|-----------|-------------|-------------|
| `SCAN TABLE` | Full table scan | Slow for large tables |
| `SEARCH TABLE USING INDEX` | Index lookup | Fast |
| `SEARCH TABLE USING COVERING INDEX` | Index-only scan | Very fast |
| `USE TEMP B-TREE` | Temporary sort/group | Moderate overhead |
| `SEARCH TABLE...OR ABORT` | Full scan with early exit | Depends on data |

### Optimizing Queries

```sql
-- Before: Full table scan
EXPLAIN QUERY PLAN 
SELECT * FROM orders WHERE customer_id = 123 AND order_date > '2024-01-01';

-- After: Add composite index
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

EXPLAIN QUERY PLAN 
SELECT * FROM orders WHERE customer_id = 123 AND order_date > '2024-01-01';
-- Now uses index
```

## Indexing Strategies

### Basic Indexes

```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Descending index
CREATE INDEX idx_orders_date_desc ON orders(order_date DESC);

-- Partial index (SQLite 3.9+)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

### Composite Indexes

```sql
-- Multi-column index (order matters!)
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);

-- Optimizes these queries:
SELECT * FROM orders WHERE customer_id = 123;
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending' AND order_date > '2024-01-01';

-- Does NOT optimize:
SELECT * FROM orders WHERE status = 'pending';  -- customer_id not specified
```

### Covering Indexes

Include all queried columns in index:

```sql
-- Query only uses index (no table lookup)
CREATE INDEX idx_users_lookup ON users(email, name, user_id);

SELECT user_id, name FROM users WHERE email = 'test@example.com';
-- Uses covering index - very fast!

-- Verify with EXPLAIN
EXPLAIN QUERY PLAN 
SELECT user_id, name FROM users WHERE email = 'test@example.com';
-- SEARCH TABLE users USING COVERING INDEX idx_users_lookup
```

### Expression Indexes

Index computed values:

```sql
-- Index on expression (SQLite 3.9+)
CREATE INDEX idx_users_lower_email ON users(lower(email));

-- Query uses index
SELECT * FROM users WHERE lower(email) = 'test@example.com';

-- Index on function result
CREATE INDEX idx_products_category_upper ON products(upper(category));
```

### Index Maintenance

```sql
-- Analyze to update statistics
ANALYZE;
ANALYZE users;

-- Rebuild index (drop and recreate)
CREATE INDEX NEW idx_users_email_new ON users(email);
DROP INDEX idx_users_email;
ALTER TABLE idx_users_email_new RENAME TO idx_users_email;

-- Check index usage (requires additional tracking)
-- No built-in index usage statistics in SQLite
```

### When NOT to Index

```sql
-- Don't index:
-- 1. Small tables (< 100 rows)
-- 2. Columns with low cardinality (status, gender)
-- 3. Frequently updated columns
-- 4. TEXT columns used only with LIKE '%pattern%'

-- Example: Poor index candidate
CREATE TABLE status_log (id INTEGER, status TEXT);  -- status has few distinct values
-- Index on 'status' would be ineffective
```

## Cache Configuration

### Memory Cache Tuning

```sql
-- Set cache size in pages
PRAGMA cache_size = 2000;  -- ~8MB with 4KB pages

-- Set cache size in KB (negative value)
PRAGMA cache_size = -8192;  -- 8MB cache

-- Calculate optimal cache:
-- cache_size = available_memory / number_of_connections
-- For 1GB RAM, 4 connections: -262144 (256MB per connection)

-- Check current setting
PRAGMA cache_size;
```

### Page Size Selection

```sql
-- Must be set before creating tables
PRAGMA page_size = 4096;  -- Common choice

-- Larger pages for better compression
PRAGMA page_size = 8192;

-- Smaller pages for embedded devices
PRAGMA page_size = 1024;

-- Check current size
PRAGMA page_size;
```

### Memory-Mapped I/O

```sql
-- Enable memory mapping (up to 2GB)
PRAGMA mmap_size = 2147483648;

-- Disable memory mapping
PRAGMA mmap_size = 0;

-- Optimal for read-heavy workloads with large databases
```

## WAL Mode Optimization

### Write-Ahead Log Configuration

```sql
-- Enable WAL mode
PRAGMA journal_mode = WAL;

-- Configure auto-checkpoint interval
PRAGMA wal_autocheckpoint = 1000;  -- Every 1000 pages

-- Manual checkpoint
PRAGMA wal_checkpoint(TRUNCATE);

-- WAL-specific settings
PRAGMA locking_mode = NORMAL;
PRAGMA synchronous = NORMAL;
```

### WAL Benefits

- **Concurrent readers/writers**: Multiple readers can access while one writer is active
- **No database locking**: Writers don't block readers
- **Better performance**: Reduced lock contention
- **Crash safety**: WAL provides durability

### When to Use WAL

| Scenario | Recommendation |
|----------|---------------|
| Single reader/writer | DELETE mode (default) |
| Multiple readers, single writer | WAL mode |
| High concurrency | WAL mode + PRAGMA optimizations |
| Read-only applications | WAL mode + large cache |

## Transaction Optimization

### Batch Operations

```sql
-- Slow: Individual inserts
INSERT INTO logs VALUES (1, 'message 1');
INSERT INTO logs VALUES (2, 'message 2');
INSERT INTO logs VALUES (3, 'message 3');

-- Fast: Single transaction
BEGIN TRANSACTION;
INSERT INTO logs VALUES (1, 'message 1');
INSERT INTO logs VALUES (2, 'message 2');
INSERT INTO logs VALUES (3, 'message 3');
COMMIT;

-- Even faster: WITH statement
WITH values_to_insert(id, msg) AS (
    VALUES (1, 'message 1'), (2, 'message 2'), (3, 'message 3')
)
INSERT INTO logs SELECT id, msg FROM values_to_insert;
```

### Transaction Best Practices

```sql
-- Keep transactions short
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
INSERT INTO transfers VALUES (1, 2, 100);
COMMIT;

-- Use savepoints for nested operations
BEGIN;
SAVEPOINT sp1;
-- Operation 1
SAVEPOINT sp2;
-- Operation 2
ROLLBACK TO sp2;  -- Undo operation 2 only
COMMIT;

-- Set busy timeout for concurrent access
PRAGMA busy_timeout = 5000;  // 5 seconds
```

## Query Optimization Techniques

### SELECT Optimization

```sql
-- Avoid SELECT *
SELECT id, name, email FROM users;  -- Specific columns

-- Use covering indexes
CREATE INDEX idx_users_lookup ON users(id, name, email);
SELECT id, name, email FROM users WHERE id = 123;  -- Index-only scan

-- Limit result sets
SELECT * FROM large_table LIMIT 100;

-- Use EXISTS instead of IN for subqueries
SELECT * FROM orders 
WHERE customer_id IN (SELECT id FROM customers WHERE status = 'active');

-- Better:
SELECT * FROM orders 
WHERE EXISTS (
    SELECT 1 FROM customers c 
    WHERE c.id = orders.customer_id AND c.status = 'active'
);
```

### JOIN Optimization

```sql
-- Ensure proper indexes on join columns
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_items_order ON order_items(order_id);

-- Optimize join order (SQLite usually does this automatically)
SELECT c.name, o.total, i.quantity
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items i ON o.id = i.order_id
WHERE c.status = 'active';

-- Use appropriate join types
-- INNER JOIN when all matches required
-- LEFT JOIN when outer table may not have matches
```

### Subquery Optimization

```sql
-- Correlated subqueries can be slow
SELECT name, 
    (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.id) AS order_count
FROM customers;

-- Often faster with JOIN + GROUP BY
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id;

-- Materialize subquery results when possible
WITH active_customers AS (
    SELECT id, name FROM customers WHERE status = 'active'
)
SELECT ac.name, o.total
FROM active_customers ac
JOIN orders o ON ac.id = o.customer_id;
```

### LIKE Optimization

```sql
-- Leading wildcard causes full table scan
SELECT * FROM users WHERE name LIKE '%alice%';  -- Slow!

-- Prefix pattern uses index
SELECT * FROM users WHERE name LIKE 'alice%';   -- Fast with index

-- Use full-text search for complex patterns
CREATE VIRTUAL TABLE users_fts USING fts5(name, email);
SELECT * FROM users_fts WHERE users_fts MATCH 'alice';
```

## Aggregate Function Optimization

### Efficient Aggregation

```sql
-- Add indexes for GROUP BY columns
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Fast aggregation
SELECT order_date, COUNT(*), SUM(total)
FROM orders
GROUP BY order_date;

-- Use partial indexes for filtered aggregates
CREATE INDEX idx_active_orders ON orders(order_date) WHERE status = 'completed';

SELECT order_date, SUM(total)
FROM orders
WHERE status = 'completed'
GROUP BY order_date;  -- Uses partial index
```

### Running Totals and Window Functions

```sql
-- Use window functions instead of correlated subqueries
SELECT 
    order_date,
    daily_total,
    SUM(daily_total) OVER (ORDER BY order_date) AS running_total,
    AVG(daily_total) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS week_moving_avg
FROM (
    SELECT order_date, SUM(total) AS daily_total
    FROM orders
    GROUP BY order_date
) AS daily;
```

## Database File Optimization

### VACUUM

Reclaim unused space:

```sql
-- Full vacuum (rebuilds entire database)
VACUUM;

-- Vacuum with specific page size
PRAGMA page_size = 4096;
VACUUM;

-- Note: VACUUM locks the database
-- Schedule during low-activity periods
```

### When to VACUUM

- After large DELETE operations
- After schema changes
- When freelist_count is high
- Periodically for long-running applications

```sql
-- Check if vacuum needed
PRAGMA freelist_count;  -- High value indicates fragmentation

-- Automatic vacuum (if available)
-- Not built-in, implement in application code
```

### Database Size Management

```sql
-- Get database size
SELECT page_count * page_size AS size_bytes 
FROM pragma_page_count(), pragma_page_size();

-- Get size in human-readable format
SELECT 
    page_count * page_size / 1024.0 / 1024.0 AS size_mb
FROM pragma_page_count(), pragma_page_size();

-- Monitor growth over time
CREATE TABLE db_size_history (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    size_bytes INTEGER
);

INSERT INTO db_size_history (size_bytes)
SELECT page_count * page_size 
FROM pragma_page_count(), pragma_page_size();
```

## Connection Pooling

### In Application Code

```c
// C example: Reuse prepared statements
sqlite3_stmt *cached_stmt = NULL;

void initialize_cache(sqlite3 *db) {
    sqlite3_prepare_v2(db, 
        "SELECT * FROM users WHERE id = ?", 
        -1, &cached_stmt, NULL);
}

void query_user(sqlite3 *db, int user_id) {
    sqlite3_reset(cached_stmt);
    sqlite3_clear_bindings(cached_stmt);
    sqlite3_bind_int(cached_stmt, 1, user_id);
    
    if (sqlite3_step(cached_stmt) == SQLITE_ROW) {
        // Process result
    }
}

void cleanup(sqlite3 *db) {
    sqlite3_finalize(cached_stmt);
}
```

### Connection Settings

```sql
-- Optimize per-connection settings
PRAGMA cache_size = -65536;      -- 64MB per connection
PRAGMA temp_store = MEMORY;       -- Temp tables in memory
PRAGMA busy_timeout = 5000;       -- 5 second lock timeout
PRAGMA journal_mode = WAL;        -- Concurrent access
PRAGMA synchronous = NORMAL;      -- Balance safety/speed
```

## Monitoring and Profiling

### Query Performance Tracking

```sql
-- Create performance log
CREATE TABLE query_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    duration_ms REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Log slow queries (application-level)
-- INSERT INTO query_log (query, duration_ms) VALUES (?, ?);

-- Analyze query patterns
SELECT 
    substr(query, 1, 50) AS query_pattern,
    COUNT(*) AS execution_count,
    AVG(duration_ms) AS avg_duration,
    MAX(duration_ms) AS max_duration
FROM query_log
GROUP BY query_pattern
ORDER BY avg_duration DESC
LIMIT 20;
```

### Performance Statistics

```sql
-- Create stats table
CREATE TABLE IF NOT EXISTS perf_stats (
    metric TEXT PRIMARY KEY,
    value INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Record statistics
INSERT OR REPLACE INTO perf_stats (metric, value)
SELECT 'page_count', page_count FROM pragma_page_count();

INSERT OR REPLACE INTO perf_stats (metric, value)
SELECT 'freelist_count', freelist_count FROM pragma_freelist_count();

INSERT OR REPLACE INTO perf_stats (metric, value)
SELECT 'cache_size', cache_size FROM pragma_cache_size();
```

### Benchmark Queries

```sql
-- Simple benchmark
.timer on
SELECT COUNT(*) FROM large_table;
-- Execution time displayed

-- Multiple executions
SELECT COUNT(*) FROM large_table;
SELECT COUNT(*) FROM large_table;
SELECT COUNT(*) FROM large_table;

-- Time specific operations
.time on
BEGIN;
UPDATE users SET last_login = datetime('now') WHERE id > 1000;
COMMIT;
```

## Common Performance Anti-Patterns

### Avoid These Patterns

```sql
-- Anti-pattern 1: SELECT * in production
SELECT * FROM users JOIN orders ON users.id = orders.user_id;
-- Better:
SELECT u.id, u.name, o.total, o.order_date
FROM users u JOIN orders o ON u.id = o.user_id;

-- Anti-pattern 2: Functions on indexed columns
SELECT * FROM users WHERE upper(email) = 'TEST@EXAMPLE.COM';
-- Better: Store normalized data or use expression index
CREATE INDEX idx_users_upper_email ON users(upper(email));

-- Anti-pattern 3: OR conditions preventing index use
SELECT * FROM users WHERE name = 'Alice' OR email = 'bob@example.com';
-- Better: Use UNION
SELECT * FROM users WHERE name = 'Alice'
UNION
SELECT * FROM users WHERE email = 'bob@example.com';

-- Anti-pattern 4: NOT IN with subquery
SELECT * FROM products 
WHERE id NOT IN (SELECT product_id FROM discontinued);
-- Better: Use NOT EXISTS
SELECT * FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM discontinued d WHERE d.product_id = p.id
);

-- Anti-pattern 5: Unnecessary DISTINCT
SELECT DISTINCT name, email FROM users;  -- If (name, email) is unique, DISTINCT unnecessary
```

## Performance Checklist

### Schema Design

- [ ] Appropriate data types for columns
- [ ] Primary keys on all tables
- [ ] Foreign keys with indexes
- [ ] Composite indexes for multi-column queries
- [ ] Covering indexes for frequent queries
- [ ] Partial indexes for filtered queries

### Configuration

- [ ] WAL mode enabled for concurrent access
- [ ] Cache size tuned to available memory
- [ ] Page size appropriate for workload
- [ ] Synchronous mode balanced for safety/speed
- [ ] Memory mapping enabled for large databases

### Query Patterns

- [ ] Specific columns instead of SELECT *
- [ ] Indexes used in WHERE clauses
- [ ] JOINs on indexed columns
- [ ] LIMIT on result sets
- [ ] Transactions for batch operations
- [ ] Prepared statements reused

### Maintenance

- [ ] Regular ANALYZE runs
- [ ] Periodic VACUUM as needed
- [ ] Monitor freelist count
- [ ] Track query performance
- [ ] Review slow query logs

## Troubleshooting Performance Issues

### Slow Queries

```sql
-- Identify slow queries
EXPLAIN QUERY PLAN SELECT ...;

-- Look for:
-- - SCAN TABLE (full table scan)
-- - USE TEMP B-TREE (sorting in temp storage)
-- - Multiple nested loops

-- Add missing indexes
CREATE INDEX idx_missing ON table(column);

-- Update statistics
ANALYZE;
```

### High Memory Usage

```sql
-- Reduce cache size
PRAGMA cache_size = -32768;  -- 32MB

-- Disable memory mapping
PRAGMA mmap_size = 0;

-- Use disk for temp tables
PRAGMA temp_store = FILE;
```

### Lock Contention

```sql
-- Enable WAL mode
PRAGMA journal_mode = WAL;

-- Increase busy timeout
PRAGMA busy_timeout = 10000;

-- Check for long transactions
-- (Requires application-level monitoring)
```
