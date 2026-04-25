# Performance Optimization

## Configuration Options

### Memory Management

#### Memory Limit

Control how much memory DuckDB can use:

```sql
-- Set memory limit (default: 80% of available RAM)
PRAGMA memory_limit = '4GB';
PRAGMA memory_limit = '2097152';  -- Also accepts bytes as integer

-- Check current setting
PRAGMA memory_limit;

-- Per-connection limit
SET memory_limit = '2GB';
```

**Best Practices:**
- Set to 60-80% of available RAM for single-instance workloads
- Reduce limit when running multiple DuckDB instances
- Monitor memory usage with `EXPLAIN ANALYZE`

#### Thread Count

Control parallelism:

```sql
-- Set thread count (default: number of CPU cores)
PRAGMA threads = 4;
SET threads = 8;

-- Check current setting
PRAGMA threads;

-- Per-query override
SET threads = 2;
SELECT * FROM large_table;
SET threads = DEFAULT;
```

**Best Practices:**
- Use all cores for CPU-bound queries
- Reduce threads for I/O-bound workloads
- Match thread count to data parallelism opportunities

#### Temp Directory

Configure spill-to-disk location:

```sql
-- Set temporary directory
SET temp_directory = '/tmp/duckdb';

-- Check current setting
PRAGMA temp_directory;
```

**Best Practices:**
- Use fast SSD storage for temp directory
- Ensure adequate disk space (2-3x memory_limit recommended)
- Use separate disk from database files if possible

### Query Execution Settings

#### Vector Size

Control batch size for vectorized execution:

```sql
-- Default is 2048, adjust for specific workloads
SET cpu_feature_override = 'no_avx';  -- Disable AVX if problematic
```

#### Statistics Collection

Enable query planner statistics:

```sql
-- Collect table statistics
ANALYZE table_name;
ANALYZE;  -- All tables

-- Check statistics
SELECT * FROM duckdb_statistic;
```

**Best Practices:**
- Run ANALYZE after bulk loads
- Re-analyze after significant data changes
- Statistics improve join ordering and filter pushdown

### File I/O Settings

#### File Search Path

Configure relative path resolution:

```sql
-- Set search paths (colon-separated on Unix, semicolon on Windows)
SET file_search_path = '/data;/backup/data';

-- Check current setting
PRAGMA file_search_path;
```

#### Extension Directory

Custom extension storage location:

```sql
SET extension_directory = '/opt/duckdb/extensions';
```

## Query Optimization

### Understanding Execution Plans

#### Basic EXPLAIN

```sql
-- Show query plan
EXPLAIN SELECT * FROM users WHERE age > 18;

-- Example output:
-- Project [name, email]
--   Filter [age > 18]
--     TableScan [users]
```

#### EXPLAIN ANALYZE

```sql
-- Execute query and show actual statistics
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 18;

-- Example output includes:
-- - Estimated vs actual row counts
-- - Execution time per operator
-- - Memory usage
-- - I/O statistics
```

#### Plan Types

```sql
-- Text format (default)
EXPLAIN query;

-- Graphical format (CLI only)
EXPLAIN (TYPE GRAPHICAL) query;

-- With settings
EXPLAIN (VERBOSE, COSTS OFF) query;
```

### Optimization Techniques

#### Predicate Pushdown

Filters applied as early as possible:

```sql
-- Good: Filter pushed down to scan
SELECT name FROM users WHERE age > 18;

-- DuckDB automatically optimizes:
-- TableScan with filter [age > 18] -> Project [name]
```

**Enable predicate pushdown:**
- Use simple WHERE conditions
- Avoid complex expressions that prevent pushdown
- Check with `EXPLAIN` to verify

#### Column Pruning

Only read needed columns:

```sql
-- Good: Only reads name and email columns
SELECT name, email FROM users;

-- Bad: Reads all columns even if not used
SELECT * FROM users;
```

**Best Practices:**
- Always specify columns instead of `SELECT *`
- Use views to define common column subsets
- Verify with `EXPLAIN ANALYZE`

#### Join Optimization

##### Choose Appropriate Join Type

```sql
-- INNER JOIN (default) - only matching rows
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN - all left rows, matching right
SELECT u.name, COALESCE(SUM(o.amount), 0) AS total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Hash join (automatic for equality joins)
-- Sort-merge join (for sorted data or range conditions)
```

##### Join Order

DuckDB automatically optimizes join order, but you can hint:

```sql
-- DuckDB will choose optimal order
SELECT * FROM a JOIN b ON a.id = b.a_id JOIN c ON b.id = c.b_id;

-- Force specific order with nested subqueries
SELECT * FROM (
    SELECT * FROM a JOIN b ON a.id = b.a_id
) JOIN c ON b.id = c.b_id;
```

##### Index Joins

For small lookup tables:

```sql
-- Create index on join column
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- DuckDB will use index for nested loop joins when beneficial
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

#### Aggregation Optimization

##### Use Appropriate Aggregate Functions

```sql
-- Efficient: Single pass aggregation
SELECT 
    category,
    COUNT(*) AS cnt,
    SUM(amount) AS total,
    AVG(amount) AS avg_amount,
    MIN(amount) AS min_amount,
    MAX(amount) AS max_amount
FROM orders
GROUP BY category;

-- Inefficient: Multiple passes
SELECT category, cnt, total/cnt AS avg
FROM (
    SELECT category, COUNT(*) AS cnt, SUM(amount) AS total
    FROM orders
    GROUP BY category
);
```

##### Partial Aggregation

For large datasets:

```sql
-- DuckDB automatically uses partial aggregation for parallel execution
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;

-- Plan shows: HashAggregate (partial) -> HashAggregate (final)
```

#### Window Function Optimization

##### Minimize Window Frame Size

```sql
-- Efficient: Small window
SELECT 
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3day
FROM transactions;

-- Less efficient: Large or unbounded window
SELECT 
    date,
    amount,
    AVG(amount) OVER (ORDER BY date) AS running_total
FROM transactions;
```

##### Use Appropriate Window Functions

```sql
-- Efficient: Single pass
SELECT 
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
FROM employees;

-- Avoid redundant window functions
SELECT 
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank  -- Same partition/order
FROM employees;
```

### Materialization Strategies

#### Use CTEs Wisely

```sql
-- CTE may be inlined (not materialized)
WITH summary AS (
    SELECT department, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department
)
SELECT * FROM summary WHERE avg_sal > 50000;

-- Force materialization with MATERIALIZED keyword
WITH MATERIALIZED summary AS (
    SELECT department, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department
)
SELECT * FROM summary WHERE avg_sal > 50000;
```

#### Temporary Tables

For complex multi-step queries:

```sql
-- Create temporary table for intermediate results
CREATE TEMPORARY TABLE user_summary AS
SELECT 
    u.id,
    u.name,
    COUNT(o.id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Create index on temp table
CREATE INDEX idx_user_summary_total ON user_summary(total_spent);

-- Use in subsequent queries
SELECT * FROM user_summary WHERE total_spent > 10000 ORDER BY total_spent DESC;
```

#### Materialized Views

For frequently accessed aggregations:

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW daily_sales AS
SELECT 
    DATE(order_date) AS sale_date,
    category,
    SUM(amount) AS total_sales,
    COUNT(*) AS order_count
FROM orders
GROUP BY DATE(order_date), category;

-- Refresh when data changes
REFRESH MATERIALIZED VIEW daily_sales;

-- Query is fast (reads pre-computed results)
SELECT * FROM daily_sales WHERE sale_date = CURRENT_DATE;
```

## Indexing Strategies

### When to Use Indexes

**Good candidates:**
- Columns in WHERE clauses with high selectivity
- JOIN keys on frequently joined columns
- ORDER BY columns for large result filtering
- UNIQUE constraints

**Poor candidates:**
- Low cardinality columns (e.g., boolean, gender)
- Frequently updated columns
- Small tables (< 10K rows)
- Columns used only in OR conditions

### Index Types

#### B-Tree Indexes (Default)

```sql
-- Standard index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_date_user ON orders(order_date, user_id);

-- Descending index
CREATE INDEX idx_users_created_desc ON users(created_at DESC);

-- Partial index
CREATE INDEX idx_active_users ON users(id) WHERE active = true;

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

#### When Composite Indexes Help

```sql
-- Query matches index order (efficient)
SELECT * FROM orders WHERE order_date = '2024-01-01' AND user_id = 123;

-- Query uses first column only (still efficient)
SELECT * FROM orders WHERE order_date = '2024-01-01';

-- Query skips first column (index not used)
SELECT * FROM orders WHERE user_id = 123;
```

### Index Maintenance

```sql
-- Check index usage with EXPLAIN
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Drop unused indexes
DROP INDEX idx_users_email;

-- Rebuild index (if fragmentation occurs)
-- DuckDB handles this automatically in most cases
```

## Data Loading Optimization

### Bulk Insert Strategies

#### COPY Command (Fastest)

```sql
-- Load from CSV
COPY users FROM 'users.csv' (HEADER true, DELIMITER ',');

-- Load from Parquet (very fast)
COPY orders FROM 'orders.parquet';

-- Multiple files with wildcard
COPY transactions FROM 'transactions_*.csv' (HEADER true);

-- With error handling
COPY products FROM 'products.csv' (
    HEADER true,
    DELIMITER ',',
    NULL_VALUE 'NULL',
    ERROR_ON_INVALID_DATA false
);
```

#### Appender API (Programmatic)

```python
import duckdb

con = duckdb.connect('mydb.db')

# Create table
con.execute("CREATE TABLE data (id INTEGER, value VARCHAR)")

# Use appender for bulk insert
appender = con.append("data")

# Append in batches (recommended)
batch_size = 10000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    appender.append_rows([
        (row['id'], row['value']) for row in batch
    ])

appender.close()
```

**Best Practices:**
- Batch inserts (10K-100K rows per batch)
- Use Parquet format when possible
- Disable indexes during load, recreate after
- Use transactions for large loads

### Data Format Selection

| Format | Read Speed | Write Speed | Compression | Best For |
|--------|-----------|-------------|-------------|----------|
| Parquet | Excellent | Excellent | High | Analytics, large datasets |
| CSV | Good | Good | None/low | Simple data, interoperability |
| JSON | Fair | Fair | Medium | Semi-structured data |
| Avro | Good | Good | Medium | Schema evolution |

```sql
-- Parquet (recommended for analytics)
COPY (SELECT * FROM large_table) TO 'output.parquet' (
    COMPRESSION SNAPPY,
    ROW_GROUP_SIZE 100000
);

-- CSV (for interoperability)
COPY (SELECT * FROM report) TO 'report.csv' (HEADER true);

-- JSON (for web APIs)
COPY (SELECT * FROM config) TO 'config.json' (FORMAT JSON);
```

## Monitoring and Debugging

### Query Performance Analysis

#### EXPLAIN ANALYZE Deep Dive

```sql
EXPLAIN (ANALYZE, TIMING, BUFFERS) 
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2023-01-01'
GROUP BY u.id
HAVING COUNT(o.id) > 10
ORDER BY order_count DESC
LIMIT 100;

-- Output includes:
-- - Actual execution time
-- - Rows processed
-- - Memory allocated
-- - Buffer usage (disk I/O)
```

#### Identify Bottlenecks

```sql
-- Check for sequential scans on large tables
EXPLAIN SELECT * FROM large_table WHERE rare_column = 'value';

-- Look for expensive operations:
-- - HashAggregate with high memory
-- - Sort with disk spills
-- - Nested Loop joins on large tables
```

### Performance Queries

#### Table Statistics

```sql
-- Check table sizes and row counts
SELECT 
    schema_name,
    table_name,
    row_count,
    total_size,
    total_size / NULLIF(row_count, 0) AS avg_row_size_bytes
FROM duckdb_tables()
ORDER BY total_size DESC;
```

#### Query History (if enabled)

```sql
-- View recent queries and their performance
SELECT * FROM duckdb_query_history() LIMIT 100;
```

### Configuration Tuning Checklist

- [ ] Set `memory_limit` to 60-80% available RAM
- [ ] Set `threads` to match CPU cores for CPU-bound workloads
- [ ] Configure `temp_directory` on fast SSD
- [ ] Run `ANALYZE` after bulk data loads
- [ ] Create indexes on high-selectivity filter columns
- [ ] Use Parquet format for large datasets
- [ ] Batch inserts in groups of 10K-100K rows
- [ ] Avoid `SELECT *` in production queries
- [ ] Use `EXPLAIN ANALYZE` for slow queries
- [ ] Consider materialized views for complex aggregations

## Common Performance Pitfalls

### N+1 Query Pattern

```sql
-- Bad: Running query in a loop
for user_id in user_ids:
    total = duckdb.sql(f"SELECT SUM(amount) FROM orders WHERE user_id = {user_id}").fetchone()

-- Good: Single batched query
results = duckdb.sql("""
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE user_id IN ({})
    GROUP BY user_id
""".format(','.join('?' * len(user_ids)))), *user_ids).fetchall()
```

### Unnecessary Type Conversions

```sql
-- Bad: Implicit conversion prevents vectorization
SELECT * FROM users WHERE age > '18';  -- String compared to integer

-- Good: Explicit, matching types
SELECT * FROM users WHERE age > 18;
```

### Overuse of DISTINCT

```sql
-- Bad: DISTINCT on all columns (expensive)
SELECT DISTINCT * FROM large_table;

-- Good: DISTINCT on specific columns
SELECT DISTINCT city, state FROM users;

-- Better: Use GROUP BY if aggregating anyway
SELECT city, state, COUNT(*) FROM users GROUP BY city, state;
```

### Correlated Subqueries

```sql
-- Bad: Executed once per row
SELECT name, (SELECT SUM(amount) FROM orders WHERE user_id = users.id) AS total
FROM users;

-- Good: Rewritten as JOIN
SELECT u.name, COALESCE(SUM(o.amount), 0) AS total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```
