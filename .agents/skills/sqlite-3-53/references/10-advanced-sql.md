# Advanced SQL Features

Comprehensive guide to advanced SQLite SQL features including Common Table Expressions (CTEs), recursive queries, triggers, views, window functions, and complex query patterns.

## Common Table Expressions (CTEs)

### Basic CTEs

Named temporary result sets:

```sql
-- Simple CTE
WITH active_users AS (
    SELECT id, username, email 
    FROM users 
    WHERE status = 'active'
)
SELECT au.*, COUNT(o.id) AS order_count
FROM active_users au
LEFT JOIN orders o ON au.id = o.user_id
GROUP BY au.id;

-- Multiple CTEs
WITH 
user_stats AS (
    SELECT 
        user_id,
        COUNT(*) AS order_count,
        SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
),
top_users AS (
    SELECT * FROM user_stats WHERE order_count > 10
)
SELECT u.username, us.order_count, us.total_spent
FROM users u
JOIN top_users us ON u.id = us.user_id;

-- CTE with computed columns
WITH price_analysis AS (
    SELECT 
        category,
        AVG(price) AS avg_price,
        MIN(price) AS min_price,
        MAX(price) AS max_price,
        MAX(price) - MIN(price) AS price_range
    FROM products
    GROUP BY category
)
SELECT * FROM price_analysis WHERE price_range > 100;
```

### CTE Benefits

- **Readability**: Complex queries become more understandable
- **Reusability**: Define once, reference multiple times
- **Maintainability**: Changes in one place
- **Debugging**: Test CTEs independently

### CTE vs Subquery Comparison

```sql
-- Using subquery (less readable)
SELECT username, order_count
FROM users
WHERE id IN (
    SELECT user_id FROM orders 
    GROUP BY user_id 
    HAVING COUNT(*) > 5
);

-- Using CTE (more readable)
WITH frequent_buyers AS (
    SELECT user_id 
    FROM orders 
    GROUP BY user_id 
    HAVING COUNT(*) > 5
)
SELECT u.username, COUNT(o.id) AS order_count
FROM users u
JOIN frequent_buyers fb ON u.id = fb.user_id
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

## Recursive CTEs

### Basic Recursive Structure

```sql
-- Anatomy of recursive CTE:
WITH RECURSIVE cte_name AS (
    -- Base case (non-recursive)
    SELECT ...
    
    UNION ALL [or UNION]
    
    -- Recursive case
    SELECT ... FROM cte_name ...
)
SELECT * FROM cte_name;
```

### Organizational Hierarchy

```sql
-- Employee hierarchy
WITH RECURSIVE org_chart(employee_id, employee_name, manager_id, manager_name, level) AS (
    -- Base case: Top-level executives (no manager)
    SELECT 
        id,
        name,
        manager_id,
        NULL AS manager_name,
        0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: Report to manager
    SELECT 
        e.id,
        e.name,
        e.manager_id,
        oc.manager_name || ' -> ' || oc.employee_name,
        oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart ORDER BY level, employee_name;

-- Find all subordinates of a manager
WITH RECURSIVE subordinates(subordinate_id, subordinate_name, manager_path, depth) AS (
    -- Base: Direct reports
    SELECT 
        id,
        name,
        name,
        1
    FROM employees
    WHERE manager_id = 42  -- Manager ID
    
    UNION ALL
    
    -- Recursive: Reports of reports
    SELECT 
        e.id,
        e.name,
        s.manager_path || ' -> ' || e.name,
        s.depth + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.subordinate_id
)
SELECT * FROM subordinates;
```

### File System Traversal

```sql
-- Directory structure
CREATE TABLE directories (
    id INTEGER PRIMARY KEY,
    name TEXT,
    parent_id INTEGER,
    path TEXT
);

-- Build full paths recursively
WITH RECURSIVE dir_tree(id, name, full_path, depth) AS (
    -- Base: Root directories
    SELECT 
        id,
        name,
        '/' || name,
        0
    FROM directories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive: Child directories
    SELECT 
        d.id,
        d.name,
        dt.full_path || '/' || d.name,
        dt.depth + 1
    FROM directories d
    JOIN dir_tree dt ON d.parent_id = dt.id
)
SELECT * FROM dir_tree ORDER BY full_path;

-- Find all descendants of a directory
WITH RECURSIVE descendants(id, name, path, level) AS (
    SELECT id, name, path, 0 
    FROM directories WHERE id = 5
    
    UNION ALL
    
    SELECT d.id, d.name, dt.path || '/' || d.name, dt.level + 1
    FROM directories d
    JOIN descendants dt ON d.parent_id = dt.id
)
SELECT * FROM descendants;
```

### Number Sequences

```sql
-- Generate numbers 1 to 100
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 100
)
SELECT * FROM numbers;

-- Generate date range
WITH RECURSive date_range(d) AS (
    SELECT date('2024-01-01')
    UNION ALL
    SELECT date(d, '+1 day') FROM date_range 
    WHERE d < '2024-12-31'
)
SELECT d, strftime('%Y-%W', d) AS week FROM date_range;

-- Fibonacci sequence
WITH RECURSIVE fib(n, a, b) AS (
    SELECT 0, 0, 1
    UNION ALL
    SELECT n + 1, b, a + b FROM fib WHERE n < 20
)
SELECT n, a AS fibonacci FROM fib;

-- Factorial calculation
WITH RECURSIVE factorial(n, result) AS (
    SELECT 0, 1
    UNION ALL
    SELECT n + 1, result * (n + 1) FROM factorial WHERE n < 10
)
SELECT n, result FROM factorial;
```

### Bill of Materials (BOM) Explosion

```sql
-- Product components
CREATE TABLE components (
    parent_part TEXT,
    child_part TEXT,
    quantity INTEGER
);

-- Explode BOM recursively
WITH RECURSIVE bom_explosion(parent, component, total_qty, depth, path) AS (
    -- Base: Direct components
    SELECT 
        parent_part,
        child_part,
        quantity,
        1,
        parent_part || ' -> ' || child_part
    FROM components
    WHERE parent_part = 'Widget-100'
    
    UNION ALL
    
    -- Recursive: Components of components
    SELECT 
        be.parent,
        c.child_part,
        be.total_qty * c.quantity,
        be.depth + 1,
        be.path || ' -> ' || c.child_part
    FROM bom_explosion be
    JOIN components c ON be.component = c.parent_part
)
SELECT component, SUM(total_qty) AS total_required
FROM bom_explosion
GROUP BY component
ORDER BY total_qty DESC;
```

### Pathfinding and Graph Traversal

```sql
-- Simple graph
CREATE TABLE edges (from_node TEXT, to_node TEXT, distance REAL);

-- Find all paths from start node
WITH RECURSIVE paths(node, path, total_distance, visited) AS (
    -- Start at source
    SELECT 
        'A',
        'A',
        0,
        'A'
    
    UNION ALL
    
    -- Follow edges
    SELECT 
        e.to_node,
        p.path || ' -> ' || e.to_node,
        p.total_distance + e.distance,
        p.visited || ',' || e.to_node
    FROM paths p
    JOIN edges e ON p.node = e.from_node
    WHERE instr(',' || p.visited || ',', ',' || e.to_node || ',') = 0  -- Avoid cycles
)
SELECT * FROM paths WHERE node = 'Z';  -- Reach destination

-- Shortest path (requires additional processing)
SELECT path, total_distance 
FROM paths 
WHERE node = 'Z'
ORDER BY total_distance 
LIMIT 1;
```

## Triggers

### Trigger Basics

Automated actions on table events:

```sql
-- AFTER INSERT trigger
CREATE TRIGGER after_user_insert
AFTER INSERT ON users
BEGIN
    INSERT INTO audit_log (table_name, operation, rowid, timestamp)
    VALUES ('users', 'INSERT', NEW.id, datetime('now'));
END;

-- BEFORE UPDATE trigger
CREATE TRIGGER before_user_update
BEFORE UPDATE ON users
WHEN OLD.status != NEW.status
BEGIN
    INSERT INTO status_changes (user_id, old_status, new_status, changed_at)
    VALUES (OLD.id, OLD.status, NEW.status, datetime('now'));
END;

-- AFTER DELETE trigger
CREATE TRIGGER after_user_delete
AFTER DELETE ON users
BEGIN
    INSERT INTO users_archive (id, username, email, deleted_at)
    VALUES (OLD.id, OLD.username, OLD.email, datetime('now'));
END;
```

### Row-level vs Statement-level

```sql
-- Row-level trigger (fires for each row)
CREATE TRIGGER log_price_changes
AFTER UPDATE OF price ON products
FOR EACH ROW
WHEN OLD.price != NEW.price
BEGIN
    INSERT INTO price_history (product_id, old_price, new_price, changed_at)
    VALUES (OLD.id, OLD.price, NEW.price, datetime('now'));
END;

-- Statement-level trigger (fires once per statement)
-- SQLite doesn't support FOR STATEMENT, all triggers are FOR EACH ROW
```

### INSERT or DEFAULT Trigger

```sql
-- Automatically set default values
CREATE TRIGGER set_user_defaults
BEFORE INSERT ON users
FOR EACH ROW
WHEN NEW.created_at IS NULL
BEGIN
    UPDATE SET created_at = datetime('now');
END;

WHEN NEW.updated_at IS NULL
BEGIN
    UPDATE SET updated_at = datetime('now');
END;

-- Better: Use DEFAULT in table definition instead
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Validation Triggers

```sql
-- Enforce business rules
CREATE TRIGGER validate_order_total
BEFORE INSERT ON orders
WHEN NEW.total < 0
BEGIN
    SELECT RAISE(ABORT, 'Order total cannot be negative');
END;

-- Check referential integrity (if foreign keys disabled)
CREATE TRIGGER validate_customer_exists
BEFORE INSERT ON orders
WHEN NOT EXISTS (SELECT 1 FROM customers WHERE id = NEW.customer_id)
BEGIN
    SELECT RAISE(ABORT, 'Customer does not exist');
END;

-- Complex validation
CREATE TRIGGER validate_employee_age
BEFORE INSERT ON employees
WHEN NEW.age < 18 OR NEW.age > 100
BEGIN
    SELECT RAISE(ABORT, 'Employee age must be between 18 and 100');
END;
```

### Cascading Updates

```sql
-- Cascade price changes to order items
CREATE TRIGGER cascade_price_update
AFTER UPDATE OF price ON products
FOR EACH ROW
WHEN OLD.price != NEW.price
BEGIN
    -- Update pending orders
    UPDATE order_items 
    SET unit_price = NEW.price
    WHERE product_id = OLD.id 
    AND order_id IN (
        SELECT id FROM orders WHERE status = 'pending'
    );
    
    -- Log the change
    INSERT INTO price_change_log (
        product_id, old_price, new_price, affected_orders
    ) VALUES (
        OLD.id, OLD.price, NEW.price,
        (SELECT COUNT(*) FROM order_items 
         WHERE product_id = OLD.id 
         AND order_id IN (SELECT id FROM orders WHERE status = 'pending'))
    );
END;
```

### INSTEAD OF Triggers (for Views)

```sql
-- Create view
CREATE VIEW user_order_summary AS
SELECT 
    u.id,
    u.username,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- INSTEAD OF INSERT trigger
CREATE TRIGGER user_order_summary_insert
INSTEAD OF INSERT ON user_order_summary
BEGIN
    -- Insert into actual tables
    INSERT INTO users (username) VALUES (NEW.username);
    
    -- Get inserted user ID and insert orders if needed
    INSERT INTO orders (user_id, total)
    SELECT last_insert_rowid(), NEW.total_spent
    WHERE NEW.order_count > 0;
END;

-- INSTEAD OF UPDATE trigger
CREATE TRIGGER user_order_summary_update
INSTEAD OF UPDATE ON user_order_summary
WHEN OLD.username != NEW.username
BEGIN
    UPDATE users SET username = NEW.username WHERE id = OLD.id;
END;
```

## Advanced Views

### Materialized View Pattern

SQLite doesn't have true materialized views, but can simulate:

```sql
-- Create summary table
CREATE TABLE user_stats_materialized (
    user_id INTEGER PRIMARY KEY,
    order_count INTEGER,
    total_spent REAL,
    last_order_date DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Populate initial data
INSERT INTO user_stats_materialized (user_id, order_count, total_spent, last_order_date)
SELECT 
    u.id,
    COUNT(o.id),
    SUM(o.total),
    MAX(o.order_date)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- Trigger to keep materialized view updated
CREATE TRIGGER update_user_stats_after_order_insert
AFTER INSERT ON orders
BEGIN
    INSERT INTO user_stats_materialized (user_id, order_count, total_spent, last_order_date)
    SELECT 
        NEW.customer_id,
        COUNT(*),
        SUM(total),
        MAX(order_date)
    FROM orders
    WHERE customer_id = NEW.customer_id
    ON CONFLICT(user_id) DO UPDATE SET
        order_count = excluded.order_count,
        total_spent = excluded.total_spent,
        last_order_date = excluded.last_order_date,
        updated_at = datetime('now');
END;

CREATE TRIGGER update_user_stats_after_order_delete
AFTER DELETE ON orders
BEGIN
    INSERT INTO user_stats_materialized (user_id, order_count, total_spent, last_order_date)
    SELECT 
        OLD.customer_id,
        COUNT(*),
        SUM(total),
        MAX(order_date)
    FROM orders
    WHERE customer_id = OLD.customer_id
    ON CONFLICT(user_id) DO UPDATE SET
        order_count = excluded.order_count,
        total_spent = excluded.total_spent,
        last_order_date = excluded.last_order_date,
        updated_at = datetime('now');
END;

-- Refresh materialized view (manual)
DELETE FROM user_stats_materialized;
INSERT INTO user_stats_materialized (user_id, order_count, total_spent, last_order_date)
SELECT 
    u.id,
    COUNT(o.id),
    SUM(o.total),
    MAX(o.order_date)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

### Updatable Views

```sql
-- Simple updatable view (single table, no aggregates)
CREATE VIEW active_users_view AS
SELECT id, username, email, phone
FROM users
WHERE status = 'active';

-- Insert through view
INSERT INTO active_users_view (username, email) 
VALUES ('Alice', 'alice@example.com');

-- Update through view
UPDATE active_users_view 
SET phone = '555-1234' 
WHERE username = 'Alice';

-- Delete through view
DELETE FROM active_users_view WHERE username = 'Alice';

-- Limitations:
-- - Cannot aggregate
-- - Cannot JOIN (in most cases)
-- - Cannot use DISTINCT
-- - Cannot use WHERE with non-updatable conditions
```

### View with Check Option

```sql
-- Create view with restriction
CREATE VIEW editable_products AS
SELECT id, name, price, category
FROM products
WHERE discontinued = 0
WITH CHECK OPTION;

-- This works:
INSERT INTO editable_products (name, price, category) 
VALUES ('Widget', 9.99, 'tools');

-- This fails (violates check option):
INSERT INTO editable_products (name, price, category, discontinued) 
VALUES ('Old Product', 5.99, 'legacy', 1);
-- Error: CHECK constraint failed
```

## Advanced Window Functions

### Complex Window Patterns

```sql
-- Running percentage of total
SELECT 
    category,
    sales,
    SUM(sales) OVER (PARTITION BY category ORDER BY date) AS running_total,
    ROUND(
        100.0 * sales / SUM(sales) OVER (PARTITION BY category),
        2
    ) AS pct_of_category
FROM monthly_sales;

-- Compare to previous period
SELECT 
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) AS prev_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS change,
    ROUND(
        100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY date)) / 
        NULLIF(LAG(revenue, 1) OVER (ORDER BY date), 0),
        2
    ) AS pct_change
FROM daily_revenue;

-- Compare to same period last year
SELECT 
    order_date,
    revenue,
    LAG(revenue, 52) OVER (PARTITION BY strftime('%W', order_date) ORDER BY order_date) AS last_year,
    revenue - LAG(revenue, 52) OVER (PARTITION BY strftime('%W', order_date) ORDER BY order_date) AS yoy_change
FROM weekly_revenue;
```

### Sessionization

```sql
-- Group user actions into sessions (30-min gap)
WITH user_actions_with_prev AS (
    SELECT 
        *,
        LAG(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) AS prev_action
    FROM user_events
),
session_gaps AS (
    SELECT 
        *,
        CASE 
            WHEN julianday(timestamp) - julianday(prev_action) > 30.0/1440.0 THEN 1
            ELSE 0
        END AS new_session
    FROM user_actions_with_prev
),
session_ids AS (
    SELECT 
        *,
        SUM(new_session) OVER (PARTITION BY user_id ORDER BY timestamp) AS session_id
    FROM session_gaps
)
SELECT 
    user_id,
    session_id,
    MIN(timestamp) AS session_start,
    MAX(timestamp) AS session_end,
    julianday(MAX(timestamp)) - julianday(MIN(timestamp)) AS session_duration_days,
    COUNT(*) AS actions_in_session
FROM session_ids
GROUP BY user_id, session_id;
```

### Top N per Group

```sql
-- Get top 3 products per category by sales
WITH ranked_products AS (
    SELECT 
        category,
        product_name,
        sales,
        RANK() OVER (PARTITION BY category ORDER BY sales DESC) AS rank_in_category
    FROM products
)
SELECT * FROM ranked_products WHERE rank_in_category <= 3;

-- Alternative using ROW_NUMBER for unique ranking
WITH ranked AS (
    SELECT 
        department,
        employee,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT * FROM ranked WHERE rn <= 5;

-- Get top N and bottom N
WITH ranked AS (
    SELECT 
        product,
        sales,
        ROW_NUMBER() OVER (ORDER BY sales DESC) AS rank_desc,
        ROW_NUMBER() OVER (ORDER BY sales ASC) AS rank_asc,
        COUNT(*) OVER () AS total_count
    FROM products
)
SELECT * FROM ranked 
WHERE rank_desc <= 10 OR rank_asc <= 10;
```

### Cumulative Distributions

```sql
-- Running percentage
SELECT 
    salary,
    employee_count,
    SUM(employee_count) OVER (ORDER BY salary) AS cumulative_count,
    ROUND(
        100.0 * SUM(employee_count) OVER (ORDER BY salary) / 
        SUM(employee_count) OVER (),
        2
    ) AS cumulative_pct
FROM salary_distribution
ORDER BY salary;

-- Quartiles and percentiles
SELECT 
    score,
    NTILE(4) OVER (ORDER BY score) AS quartile,
    NTILE(100) OVER (ORDER BY score) AS percentile
FROM test_results;

-- Find median
WITH ranked AS (
    SELECT 
        value,
        ROW_NUMBER() OVER (ORDER BY value) AS rn,
        COUNT(*) OVER () AS cnt
    FROM values_table
)
SELECT AVG(value) AS median
FROM ranked
WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2);
```

## Generated Columns

### Stored Generated Columns

Automatically computed and stored:

```sql
-- Create table with generated columns
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    unit_price REAL,
    tax_rate REAL DEFAULT 0.08,
    price_with_tax REAL GENERATED ALWAYS AS (unit_price * (1 + tax_rate)) STORED,
    name_upper TEXT GENERATED ALWAYS AS (upper(name)) STORED
);

-- Insert data (generated columns auto-populate)
INSERT INTO products (name, unit_price) VALUES ('Widget', 9.99);

SELECT name, unit_price, price_with_tax, name_upper FROM products;
-- Widget | 9.99 | 10.7892 | WIDGET

-- Query generated columns efficiently (can use indexes)
CREATE INDEX idx_products_name_upper ON products(name_upper);
SELECT * FROM products WHERE name_upper LIKE 'W%';

-- Update base columns (generated auto-updates)
UPDATE products SET unit_price = 12.99 WHERE id = 1;
-- price_with_tax automatically recalculated
```

### Virtual Generated Columns

Computed on-the-fly, not stored:

```sql
-- Virtual column (computed when queried)
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) VIRTUAL,
    email TEXT GENERATED ALWAYS AS (lower(first_name) || '.' || lower(last_name) || '@company.com') VIRTUAL
);

-- Insert data
INSERT INTO employees (first_name, last_name) VALUES ('Alice', 'Smith');

SELECT id, first_name, last_name, full_name, email FROM employees;
-- 1 | Alice | Smith | Alice Smith | alice.smith@company.com

-- Trade-offs:
-- STORED: Faster reads, slower writes, uses disk space
-- VIRTUAL: Slower reads, faster writes, no extra storage
```

### Generated Column Use Cases

```sql
-- Composite key components
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    line_number INTEGER,
    unique_key TEXT GENERATED ALWAYS AS (
        printf('%d-%d-%d', order_id, product_id, line_number)
    ) STORED,
    PRIMARY KEY (unique_key)
);

-- Date components
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_datetime DATETIME,
    event_date TEXT GENERATED ALWAYS AS (date(event_datetime)) STORED,
    event_hour INTEGER GENERATED ALWAYS AS (CAST(strftime('%H', event_datetime) AS INTEGER)) STORED,
    event_year INTEGER GENERATED ALWAYS AS (CAST(strftime('%Y', event_datetime) AS INTEGER)) STORED
);

-- Create indexes on generated columns
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_year_hour ON events(event_year, event_hour);

-- JSON extraction
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    data JSON,
    username TEXT GENERATED ALWAYS AS (json_extract(data, '$.username')) VIRTUAL,
    email TEXT GENERATED ALWAYS AS (json_extract(data, '$.email')) VIRTUAL
);

-- Query with generated columns
SELECT * FROM user_profiles WHERE email LIKE '%@example.com';
```

## JSON in Advanced Queries

### JSON Aggregation

```sql
-- Aggregate rows into JSON array
SELECT 
    category,
    json_group_array(
        json_object('id', id, 'name', name, 'price', price)
    ) AS products
FROM products
GROUP BY category;

-- Result: {"electronics": [{"id":1,"name":"Widget","price":9.99}, ...]}

-- Conditional aggregation into JSON
SELECT 
    json_group_object(
        status,
        json_group_array(id)
    ) AS users_by_status
FROM users;

-- Result: {"active": [1,2,3], "inactive": [4,5]}
```

### JSON in CTEs

```sql
-- Process JSON data with CTE
WITH parsed_data AS (
    SELECT 
        id,
        json_extract(data, '$.user_id') AS user_id,
        json_extract(data, '$.action') AS action,
        json_extract(data, '$.timestamp') AS timestamp
    FROM events
    WHERE json_valid(data) = 1
),
aggregated AS (
    SELECT 
        user_id,
        json_group_array(action) AS actions,
        COUNT(*) AS event_count
    FROM parsed_data
    GROUP BY user_id
)
SELECT * FROM aggregated WHERE event_count > 10;
```

## Transaction Patterns

### Savepoint Patterns

```sql
-- Nested transactions with savepoints
BEGIN;

-- Operation 1
INSERT INTO users (username) VALUES ('Alice');

SAVEPOINT sp1;

-- Operation 2 (might fail)
INSERT INTO orders (user_id, total) VALUES (last_insert_rowid(), 99.99);

-- Operation 3
UPDATE users SET login_count = login_count + 1 WHERE username = 'Alice';

-- Rollback to savepoint if needed
ROLLBACK TO sp1;  -- Undoes order insert and update, keeps user

-- Continue with more operations
INSERT INTO audit_log (action) VALUES ('User created');

COMMIT;  -- Commits user insert and audit log
```

### Transaction Isolation

```sql
-- Deferred transaction (default, waits for lock)
BEGIN DEFERRED;
SELECT * FROM users;
COMMIT;

-- Immediate transaction (gets write lock immediately)
BEGIN IMMEDIATE;
UPDATE users SET last_seen = datetime('now');
COMMIT;

-- Exclusive transaction (full exclusive lock)
BEGIN EXCLUSIVE;
-- No other connections can read or write
DELETE FROM temp_data;
COMMIT;
```

### Optimistic Locking

```sql
-- Add version column to table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    balance REAL,
    version INTEGER DEFAULT 0
);

-- Update with version check
UPDATE accounts 
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND version = (SELECT version FROM accounts WHERE id = 1);

-- Check if update succeeded
SELECT changes();  -- Returns 0 if concurrent modification occurred
```

## Best Practices

### Performance with Advanced Features

1. **CTEs**: Use for readability, not just performance (SQLite may not optimize)
2. **Recursive CTEs**: Always include termination condition to prevent infinite loops
3. **Triggers**: Keep logic simple and fast; avoid nested triggers
4. **Generated columns**: Use STORED for frequently queried computed values
5. **Window functions**: Be mindful of memory usage on large datasets

### Maintainability

1. **Document complex queries** with comments explaining logic
2. **Use CTEs** to break down complex queries into logical parts
3. **Name your CTEs** descriptively for clarity
4. **Test triggers thoroughly** including edge cases and error conditions
5. **Consider view refresh strategy** for materialized views

### Debugging Tips

```sql
-- Test CTE independently
WITH debug_cte AS (
    SELECT ...
)
SELECT * FROM debug_cte;  -- Inspect intermediate results

-- Check trigger execution
CREATE TABLE trigger_debug (
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    info TEXT
);

-- Add to trigger:
INSERT INTO trigger_debug (info) VALUES ('Trigger fired: ' || NEW.id);

-- Verify generated columns
SELECT 
    id,
    base_column,
    generated_column,
    -- Expected value for comparison
    (base_column * 1.1) AS expected
FROM table
WHERE generated_column != (base_column * 1.1);  -- Find mismatches
```
