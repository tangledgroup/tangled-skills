# UPSERT and RETURNING Clause

Modern SQL patterns for insert-or-update operations and result retrieval in SQLite 3.53.

## UPSERT (INSERT...ON CONFLICT)

UPSERT allows inserting data while automatically handling constraint violations by updating existing rows.

### Basic UPSERT Syntax

```sql
-- Insert or update on conflict
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...)
ON CONFLICT (conflict_target)
DO UPDATE SET column1 = value1, column2 = value2, ...;

-- Or ignore the insert on conflict
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...)
ON CONFLICT (conflict_target)
DO NOTHING;
```

### Conflict Targets

Specify what constitutes a conflict:

```sql
-- Conflict on PRIMARY KEY
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email;

-- Conflict on UNIQUE constraint
INSERT INTO products (sku, name, price)
VALUES ('ABC123', 'Widget', 9.99)
ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    price = EXCLUDED.price;

-- Conflict on multiple columns
INSERT INTO inventory (warehouse_id, product_id, quantity)
VALUES (1, 100, 50)
ON CONFLICT (warehouse_id, product_id) DO UPDATE SET
    quantity = EXCLUDED.quantity;

-- Conflict using WHERE clause (conditional upsert)
INSERT INTO logs (user_id, action, timestamp)
VALUES (42, 'login', datetime('now'))
ON CONFLICT (user_id) DO UPDATE SET
    action = EXCLUDED.action,
    timestamp = EXCLUDED.timestamp
WHERE logs.timestamp < EXCLUDED.timestamp;  -- Only update if newer
```

### The EXCLUDED Table

In the `DO UPDATE` clause, `EXCLUDED` is an implicit table containing the values that were attempted to be inserted:

```sql
-- Update with new values from EXCLUDED
INSERT INTO users (id, name, email, last_login)
VALUES (1, 'Alice', 'alice@example.com', datetime('now'))
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,                    -- Use new value
    email = EXCLUDED.email,                  -- Use new value
    last_login = EXCLUDED.last_login;        -- Use new value

-- Merge values from existing and excluded
INSERT INTO products (sku, stock, reserved)
VALUES ('ABC123', 100, 10)
ON CONFLICT (sku) DO UPDATE SET
    stock = products.stock + EXCLUDED.stock,      -- Add to existing
    reserved = EXCLUDED.reserved;                 -- Replace value

-- Use COALESCE to prefer existing values
INSERT INTO config (key, value, default_value)
VALUES ('theme', 'dark', 'light')
ON CONFLICT (key) DO UPDATE SET
    value = COALESCE(EXCLUDED.value, value),      -- Keep existing if EXCLUDED is NULL
    default_value = EXCLUDED.default_value;       -- Always update default
```

### DO NOTHING

Silently ignore conflicts without updating:

```sql
-- Insert only if doesn't exist
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO NOTHING;

-- Useful for idempotent inserts
INSERT INTO event_log (event_id, user_id, action)
VALUES ('evt_123', 42, 'page_view')
ON CONFLICT (event_id) DO NOTHING;

-- Returns number of rows inserted (0 if conflict occurred)
-- Check changes() to see if insert happened
SELECT changes();  -- 0 if conflict, 1 if inserted
```

### UPSERT with Multiple Rows

```sql
-- Upsert multiple rows at once
INSERT INTO users (id, name, email)
VALUES 
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email;

-- Bulk update existing + insert new
INSERT INTO products (sku, name, price, stock)
VALUES 
    ('A001', 'Product A', 19.99, 100),
    ('A002', 'Product B', 29.99, 50),
    ('A003', 'Product C', 39.99, 75)
ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    stock = EXCLUDED.stock;
```

### Common UPSERT Patterns

#### Idempotent Inserts

```sql
-- Insert configuration without errors if already exists
INSERT OR IGNORE INTO config (key, value)
VALUES ('max_connections', '100');

-- Equivalent using ON CONFLICT
INSERT INTO config (key, value)
VALUES ('max_connections', '100')
ON CONFLICT (key) DO NOTHING;
```

#### Update on Duplicate

```sql
-- Classic upsert: insert or update all fields
INSERT INTO users (id, name, email, settings)
VALUES (1, 'Alice', 'alice@example.com', '{"theme":"dark"}')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    settings = EXCLUDED.settings;

-- Upsert with timestamp tracking
INSERT INTO audit_log (user_id, action, created_at, updated_at)
VALUES (42, 'login', datetime('now'), datetime('now'))
ON CONFLICT (user_id) DO UPDATE SET
    action = EXCLUDED.action,
    updated_at = EXCLUDED.updated_at;
```

#### Conditional Updates

```sql
-- Only update if new value is greater
INSERT INTO scores (user_id, game_id, score)
VALUES (42, 7, 1500)
ON CONFLICT (user_id, game_id) DO UPDATE SET
    score = MAX(scores.score, EXCLUDED.score)
WHERE scores.score < EXCLUDED.score;

-- Only update if timestamp is newer
INSERT INTO user_sessions (user_id, session_data, last_activity)
VALUES (42, '{"page":"home"}', strftime('%s', 'now'))
ON CONFLICT (user_id) DO UPDATE SET
    session_data = EXCLUDED.session_data,
    last_activity = EXCLUDED.last_activity
WHERE user_sessions.last_activity < EXCLUDED.last_activity;
```

#### Counter Increment

```sql
-- Increment page views
INSERT INTO page_views (page, count)
VALUES ('/home', 1)
ON CONFLICT (page) DO UPDATE SET
    count = count + EXCLUDED.count;

-- Track user actions
INSERT INTO user_actions (user_id, action_type, total)
VALUES (42, 'login', 1)
ON CONFLICT (user_id, action_type) DO UPDATE SET
    total = total + EXCLUDED.total;
```

## RETURNING Clause

The RETURNING clause retrieves data from affected rows immediately after INSERT, UPDATE, or DELETE.

### RETURNING with INSERT

```sql
-- Return inserted row
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com')
RETURNING *;
-- Output: 1|Alice|alice@example.com|2024-01-01 00:00:00

-- Return specific columns
INSERT INTO products (name, price, category)
VALUES ('Widget', 9.99, 'tools')
RETURNING id, name, price;
-- Output: 42|Widget|9.99

-- Return computed values
INSERT INTO orders (customer_id, total)
VALUES (5, 123.45)
RETURNING id AS order_id, customer_id, total, 
        datetime('now') AS created;

-- Return after upsert
INSERT INTO config (key, value)
VALUES ('theme', 'dark')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
RETURNING key, value, 'updated' AS action;
-- Returns 'updated' if conflict occurred, or new row if inserted
```

### RETURNING with UPDATE

```sql
-- Return updated rows
UPDATE users 
SET last_login = datetime('now')
WHERE id = 1
RETURNING id, name, last_login;

-- Return before and after values
UPDATE products
SET price = price * 1.10  -- 10% increase
WHERE category = 'tools'
RETURNING id, name, price AS new_price;

-- Conditional update with RETURNING
UPDATE inventory
SET quantity = quantity - EXCLUDED.quantity
FROM (SELECT product_id, 5 AS quantity) EXCLUDED
WHERE inventory.product_id = EXCLUDED.product_id
RETURNING product_id, quantity;
```

### RETURNING with DELETE

```sql
-- Return deleted rows (for logging/archiving)
DELETE FROM sessions
WHERE expires_at < datetime('now', '-7 days')
RETURNING *;

-- Return count of affected rows
DELETE FROM temp_data
WHERE created < date('now', '-30 days')
RETURNING COUNT(*);
```

### RETURNING with Multiple Rows

```sql
-- Insert multiple rows, return all
INSERT INTO users (name, email)
VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com')
RETURNING id, name;
-- Returns 3 rows with assigned IDs

-- Update multiple, return all changed
UPDATE products
SET price = price * 1.05
WHERE category IN ('tools', 'electronics')
RETURNING id, name, price;
```

### RETURNING into Variables (CLI)

In the SQLite CLI, you can capture RETURNING results:

```sql
-- Insert and capture the generated ID
INSERT INTO users (name) VALUES ('Alice')
RETURNING id;

-- Use in subsequent queries
SELECT * FROM users WHERE id = (
    INSERT INTO users (name) VALUES ('Bob')
    RETURNING id
);
```

## Combined UPSERT with RETURNING

Combine both features for powerful insert-or-update patterns:

```sql
-- Upsert and return the final state
INSERT INTO user_settings (user_id, setting_key, value)
VALUES (42, 'theme', 'dark')
ON CONFLICT (user_id, setting_key) DO UPDATE SET
    value = EXCLUDED.value
RETURNING user_id, setting_key, value, 'upserted' AS action;

-- Returns whether row was inserted or updated
-- Can check if returned value matches EXCLUDED to determine action

-- Bulk upsert with return
INSERT INTO product_stock (product_id, warehouse_id, quantity)
VALUES 
    (1, 'A', 100),
    (2, 'A', 200),
    (3, 'B', 150)
ON CONFLICT (product_id, warehouse_id) DO UPDATE SET
    quantity = EXCLUDED.quantity
RETURNING product_id, warehouse_id, quantity, 'updated';

-- Upsert with computed return values
INSERT INTO counters (name, increment)
VALUES ('page_views', 1)
ON CONFLICT (name) DO UPDATE SET
    count = count + EXCLUDED.increment
RETURNING name, count, 
        CASE 
            WHEN changes() = 1 THEN 'updated'
            ELSE 'inserted'
        END AS action;
```

## Practical Patterns

### Rate Limiting

```sql
-- Track request counts with automatic reset
INSERT INTO rate_limits (user_id, window_start, request_count)
VALUES (
    42,
    strftime('%s', 'now') / 3600 * 3600,  -- Hour window
    1
)
ON CONFLICT (user_id, window_start) DO UPDATE SET
    request_count = request_count + 1
RETURNING request_count;

-- Check if limit exceeded
SELECT request_count <= 100 AS allowed FROM rate_limits
WHERE user_id = 42 AND window_start = strftime('%s', 'now') / 3600 * 3600;
```

### Session Management

```sql
-- Create or update session
INSERT INTO sessions (user_id, token, expires_at)
VALUES (
    42,
    'abc123xyz',
    datetime('now', '+1 hour')
)
ON CONFLICT (user_id) DO UPDATE SET
    token = EXCLUDED.token,
    expires_at = EXCLUDED.expires_at
RETURNING user_id, token;
```

### Event Deduplication

```sql
-- Insert event, ignore if already exists
INSERT INTO events (event_id, user_id, action, timestamp)
VALUES ('evt_123', 42, 'purchase', datetime('now'))
ON CONFLICT (event_id) DO NOTHING
RETURNING event_id;  -- Returns NULL if duplicate

-- Check if insert happened
SELECT changes() > 0 AS inserted;
```

### Cache with Expiration

```sql
-- Insert cache entry or update if exists and not expired
INSERT INTO cache (key, value, expires_at)
VALUES ('user_42', '{"name":"Alice"}', datetime('now', '+1 hour'))
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    expires_at = EXCLUDED.expires_at
WHERE cache.expires_at > datetime('now')  -- Only update if not expired
RETURNING key, value;
```

### Leaderboard Updates

```sql
-- Add score, updating existing entry
INSERT INTO leaderboard (user_id, game_id, score, updated_at)
VALUES (42, 7, 1500, datetime('now'))
ON CONFLICT (user_id, game_id) DO UPDATE SET
    score = MAX(leaderboard.score, EXCLUDED.score),
    updated_at = EXCLUDED.updated_at
WHERE leaderboard.score < EXCLUDED.score
RETURNING user_id, score, 
        RANK() OVER (ORDER BY score DESC) AS rank;
```

## Error Handling

```sql
-- Handle conflicts explicitly
BEGIN;

INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name;

-- Check how many rows were affected
SELECT changes() AS rows_affected;

COMMIT;

-- Use RETURNING to get conflict information
INSERT INTO orders (order_id, customer_id, total)
VALUES ('ORD123', 5, 99.99)
ON CONFLICT (order_id) DO UPDATE SET
    total = EXCLUDED.total
RETURNING 
    order_id,
    'conflict_resolved' AS status;
```

## Performance Considerations

1. **UPSERT is atomic** - Single statement, no race conditions
2. **Indexes matter** - Ensure conflict target columns are indexed
3. **EXCLUDED overhead** - Minimal, but avoid complex EXCLUDED references
4. **RETURNING cost** - Slight overhead for materializing returned rows
5. **Batch operations** - UPSERT multiple rows in single statement when possible

## Best Practices

1. **Be explicit about conflict targets** - Don't rely on implicit PRIMARY KEY
2. **Use WHERE clauses carefully** - Conditional updates can be subtle
3. **Test edge cases** - Verify behavior with NULL values and duplicates
4. **Monitor changes()** - Use to determine if insert or update occurred
5. **Index conflict columns** - Ensure fast conflict detection
6. **Consider transaction isolation** - UPSERT behavior depends on isolation level

## Related Documentation

- [SQL Basics](01-sql-basics.md) - INSERT and UPDATE syntax
- [Advanced SQL](10-advanced-sql.md) - CTEs and complex queries
- [Performance Optimization](07-performance.md) - Indexing strategies
- [Transactions](14-transactions-isolation.md) - Transaction isolation levels
