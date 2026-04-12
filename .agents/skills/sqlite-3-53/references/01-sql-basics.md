# SQL Basics

Fundamental SQL language features for SQLite 3.53, including data types, DDL statements, query construction, joins, and subqueries.

## Data Types

SQLite uses dynamic typing with five storage classes:

### Storage Classes

| Storage Class | Description | Use Case |
|--------------|-------------|----------|
| `NULL` | Null value | Missing or unknown data |
| `INTEGER` | Signed integer (1-8 bytes) | IDs, counts, numeric values |
| `REAL` | Floating point (8 bytes) | Decimals, measurements |
| `TEXT` | Unicode string | Names, descriptions, JSON |
| `BLOB` | Binary data | Images, files, serialized objects |

### Type Affinity

Columns have type affinity that influences storage:

```sql
CREATE TABLE examples (
    id INTEGER PRIMARY KEY,      -- INTEGER affinity
    name TEXT,                   -- TEXT affinity
    price REAL,                  -- REAL affinity
    data BLOB,                   -- BLOB affinity
    code VARCHAR(10),            -- TEXT affinity (contains TEXT)
    qty INT,                     -- INTEGER affinity (contains INT)
    flag CHAR,                   -- TEXT affinity (contains CHAR)
    amount DOUBLE PRECISION      -- REAL affinity (contains REAL/DOUBLE)
);
```

### Typeless Columns

Columns without declared type have NONE affinity:

```sql
CREATE TABLE flexible (
    anything  -- Accepts any type, stored as provided
);
```

## CREATE TABLE

### Basic Table Creation

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
    login_count INTEGER DEFAULT 0
);
```

### Constraints

**PRIMARY KEY:**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    sku TEXT PRIMARY KEY        -- Alternative primary key
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

**FOREIGN KEY:**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Enable foreign key enforcement
PRAGMA foreign_keys = ON;
```

**CHECK Constraints:**
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    age INTEGER CHECK(age >= 18 AND age <= 100),
    salary REAL CHECK(salary > 0),
    email TEXT CHECK(email LIKE '%@%.%'),
    department TEXT CHECK(department IN ('engineering', 'sales', 'support'))
);
```

**DEFAULT Values:**
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    published BOOLEAN DEFAULT 0,
    version INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

### Table Options

```sql
-- Create table in specific database
CREATE TABLE analytics.events (
    id INTEGER PRIMARY KEY,
    event_type TEXT
);

-- Create temporary table (session-only)
CREATE TEMP TABLE session_data (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Create table if not exists
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value BLOB,
    expires_at DATETIME
);

-- Create table with WITHOUT ROWID (more efficient for unique keys)
CREATE TABLE config (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
) WITHOUT ROWID;
```

## ALTER TABLE

### Add Column

```sql
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN last_login DATETIME DEFAULT NULL;
```

### Rename Table

```sql
ALTER TABLE users RENAME TO accounts;
```

### Limitations

SQLite's ALTER TABLE is limited. For complex changes:

```sql
-- Strategy: Create new table, copy data, replace old
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,           -- New column
    age INTEGER,          -- New column
    created_at DATETIME
);

INSERT INTO users_new (id, username, email, created_at)
SELECT id, username, email, created_at FROM users;

DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
```

## DROP and TRUNCATE

```sql
-- Drop table
DROP TABLE IF EXISTS temp_data;

-- Truncate table (faster than DELETE)
DELETE FROM large_table;  -- No direct TRUNCATE in SQLite

-- Drop all tables in database
SELECT 'DROP TABLE ' || name || ';' 
FROM sqlite_master 
WHERE type='table' AND name NOT LIKE 'sqlite_%';
```

## SELECT Queries

### Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, username, email FROM users;

-- With aliases
SELECT 
    u.id AS user_id,
    u.username AS "User Name",
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

### WHERE Clauses

**Comparison Operators:**
```sql
SELECT * FROM products WHERE price > 100;
SELECT * FROM products WHERE price >= 100;
SELECT * FROM products WHERE price < 100;
SELECT * FROM products WHERE price <= 100;
SELECT * FROM products WHERE price = 100;
SELECT * FROM products WHERE price != 100;
SELECT * FROM products WHERE price <> 100;
```

**Pattern Matching:**
```sql
-- LIKE patterns
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM users WHERE username LIKE 'a%';          -- Starts with 'a'
SELECT * FROM users WHERE username LIKE '%z';          -- Ends with 'z'
SELECT * FROM users WHERE username LIKE '%o%';         -- Contains 'o'
SELECT * FROM users WHERE username NOT LIKE '%admin%';

-- Glob (Unix-style patterns)
SELECT * FROM files WHERE name GLOB '*.jpg';
SELECT * FROM files WHERE name GLOB '[A-M]*';

-- Regex (if compiled in)
SELECT * FROM users WHERE email REGEXP '^[a-z]+@[a-z]+\.[a-z]{2,}$';
```

**Range Queries:**
```sql
SELECT * FROM products WHERE price BETWEEN 10 AND 100;
SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';
SELECT * FROM users WHERE age NOT BETWEEN 18 AND 65;
```

**IN and NOT IN:**
```sql
SELECT * FROM products WHERE category IN ('electronics', 'books', 'clothing');
SELECT * FROM users WHERE status NOT IN ('suspended', 'banned');

-- Subquery with IN
SELECT * FROM orders 
WHERE user_id IN (SELECT id FROM users WHERE country = 'USA');
```

**IS NULL and IS NOT NULL:**
```sql
SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM users WHERE middle_name IS NOT NULL;

-- Note: Use IS NULL, not = NULL
SELECT * FROM users WHERE phone != NULL;  -- Returns nothing!
```

**Compound Conditions:**
```sql
SELECT * FROM products 
WHERE price > 50 AND category = 'electronics';

SELECT * FROM users 
WHERE age < 18 OR age > 65;

SELECT * FROM orders 
WHERE (status = 'pending' AND total > 100) 
   OR (status = 'approved');
```

### ORDER BY

```sql
-- Single column
SELECT * FROM products ORDER BY price;
SELECT * FROM products ORDER BY price DESC;

-- Multiple columns
SELECT * FROM users 
ORDER BY country ASC, last_name ASC, first_name ASC;

-- With expressions
SELECT * FROM products 
ORDER BY (price * quantity) DESC;

-- With aliases
SELECT name, price * 0.9 AS sale_price 
FROM products 
ORDER BY sale_price;

-- NULL handling
SELECT * FROM users 
ORDER BY last_name NULLS FIRST;   -- NULLs first (default in SQLite)
SELECT * FROM users 
ORDER BY last_name NULLS LAST;    -- NULLs last
```

### LIMIT and OFFSET

```sql
-- First 10 rows
SELECT * FROM users LIMIT 10;

-- Pagination: page 2, 10 per page
SELECT * FROM users LIMIT 10 OFFSET 10;

-- Top N by score
SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10;

-- Limit with percentage (SQLite 3.36+)
SELECT * FROM users LIMIT 10%;  -- First 10% of rows
```

### DISTINCT

```sql
-- Unique values
SELECT DISTINCT country FROM users;

-- Count distinct
SELECT COUNT(DISTINCT user_id) FROM orders;

-- Multiple columns
SELECT DISTINCT first_name, last_name FROM users;
```

## JOINs

### INNER JOIN

```sql
-- Basic inner join
SELECT u.username, o.order_date, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Multiple joins
SELECT u.username, p.name AS product, oi.quantity, oi.price
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

### LEFT JOIN (Left Outer Join)

```sql
-- Users and their orders (include users with no orders)
SELECT u.username, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- Products with category info (include uncategorized products)
SELECT p.name, c.category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id;
```

### RIGHT JOIN

SQLite doesn't support RIGHT JOIN directly. Use LEFT JOIN with reversed tables:

```sql
-- Instead of RIGHT JOIN
SELECT o.total, u.username
FROM orders o
RIGHT JOIN users u ON o.user_id = u.id;

-- Use LEFT JOIN (equivalent)
SELECT o.total, u.username
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

### FULL OUTER JOIN

SQLite doesn't support FULL OUTER JOIN. Use UNION:

```sql
-- Instead of FULL OUTER JOIN
SELECT u.id, u.username, o.order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id

UNION

SELECT u.id, u.username, o.order_date
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- Or using LEFT JOIN + UNION (equivalent)
SELECT u.id, u.username, o.order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id

UNION

SELECT u.id, u.username, o.order_date
FROM users u
RIGHT JOIN orders o ON o.user_id = u.id
WHERE u.id IS NULL;
```

### CROSS JOIN (Cartesian Product)

```sql
-- All combinations
SELECT c.color, s.size
FROM colors c
CROSS JOIN sizes s;

-- Or comma syntax (equivalent)
SELECT c.color, s.size
FROM colors c, sizes s;
```

### SELF JOIN

```sql
-- Employees and their managers
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find users with same email domain
SELECT u1.username, u2.username, u1.email_domain
FROM users u1
JOIN users u2 ON u1.email_domain = u2.email_domain
WHERE u1.id < u2.id;  -- Avoid duplicates and self-matches
```

### NATURAL JOIN

```sql
-- Join on common column names automatically
SELECT * FROM users
NATURAL JOIN user_preferences;

-- With LEFT OUTER
SELECT * FROM orders
NATURAL LEFT OUTER JOIN order_items;
```

## Subqueries

### Scalar Subqueries

```sql
-- Single value subquery in SELECT
SELECT 
    username,
    (SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id) AS order_count
FROM users;

-- Subquery in WHERE
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Subquery in ORDER BY
SELECT * FROM products p
ORDER BY (SELECT COUNT(*) FROM order_items WHERE product_id = p.id) DESC;
```

### Row Subqueries

```sql
-- Compare row values
SELECT * FROM employees e
WHERE (e.department, e.salary) IN (
    SELECT department, MAX(salary) 
    FROM employees 
    GROUP BY department
);
```

### Table Subqueries (Derived Tables)

```sql
-- Subquery in FROM clause
SELECT dept_stats.department, dept_stats.avg_salary
FROM (
    SELECT department, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
) AS dept_stats
WHERE dept_stats.avg_salary > 50000;

-- Multiple derived tables
SELECT 
    users.username,
    user_stats.order_count,
    order_stats.total_spent
FROM users
JOIN (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
) AS user_stats ON users.id = user_stats.user_id
JOIN (
    SELECT user_id, SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
) AS order_stats ON users.id = order_stats.user_id;
```

### Correlated Subqueries

```sql
-- Subquery that references outer query
SELECT * FROM products p
WHERE EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.product_id = p.id
);

-- Update with correlated subquery
UPDATE employees
SET department_avg = (
    SELECT AVG(salary) FROM employees e2 WHERE e2.department = employees.department
);
```

### NOT EXISTS

```sql
-- Users who never ordered
SELECT * FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id
);

-- Products never purchased
SELECT p.* FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.product_id = p.id
);
```

## INSERT Operations

### Basic INSERT

```sql
-- Single row, all columns
INSERT INTO users (username, email, password_hash)
VALUES ('alice', 'alice@example.com', 'hashed_password');

-- Single row, specified columns
INSERT INTO users (username, email)
VALUES ('bob', 'bob@example.com');

-- Multiple rows
INSERT INTO users (username, email) VALUES
    ('charlie', 'charlie@example.com'),
    ('diana', 'diana@example.com'),
    ('eve', 'eve@example.com');
```

### INSERT with SELECT

```sql
-- Copy from another table
INSERT INTO users_archive (id, username, email, archived_at)
SELECT id, username, email, datetime('now')
FROM users WHERE status = 'inactive';

-- Insert computed values
INSERT INTO stats (date, user_count, order_count)
SELECT 
    date(created_at),
    COUNT(DISTINCT u.id),
    COUNT(DISTINCT o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY date(created_at);
```

### INSERT OR Conflict Actions

```sql
-- Ignore if conflict
INSERT OR IGNORE INTO users (username, email)
VALUES ('alice', 'alice@example.com');

-- Replace entire row on conflict
INSERT OR REPLACE INTO config (setting_key, setting_value)
VALUES ('theme', 'dark');

-- Abort on conflict (default)
INSERT OR ABORT INTO users (username, email)
VALUES ('alice', 'alice@example.com');

-- Rollback transaction on conflict
INSERT OR ROLLBACK INTO users (username, email)
VALUES ('alice', 'alice@example.com');

-- Fail with error code
INSERT OR FAIL INTO users (username, email)
VALUES ('alice', 'alice@example.com');
```

### UPSERT (INSERT ... ON CONFLICT)

```sql
-- Insert or update on conflict
INSERT INTO users (username, email, last_login)
VALUES ('alice', 'alice@example.com', datetime('now'))
ON CONFLICT(username) DO UPDATE SET
    email = excluded.email,
    last_login = excluded.last_login;

-- Upsert with condition
INSERT INTO stats (date, metric, value)
VALUES ('2024-01-01', 'users', 100)
ON CONFLICT(date, metric) DO UPDATE SET
    value = value + excluded.value
WHERE excluded.value > 0;

-- Do nothing on conflict
INSERT INTO unique_log (event_id, timestamp)
VALUES (123, datetime('now'))
ON CONFLICT(event_id) DO NOTHING;
```

## UPDATE Operations

### Basic UPDATE

```sql
-- Update single column
UPDATE users SET status = 'inactive' WHERE id = 1;

-- Update multiple columns
UPDATE users 
SET email = 'new_email@example.com',
    updated_at = datetime('now')
WHERE username = 'alice';

-- Update with expression
UPDATE products SET price = price * 1.10 WHERE category = 'electronics';

-- Update with CASE
UPDATE orders SET status = 
    CASE 
        WHEN total > 100 THEN 'priority'
        WHEN total > 50 THEN 'standard'
        ELSE 'economy'
    END
WHERE status IS NULL;
```

### UPDATE with Subquery

```sql
-- Update from another table
UPDATE users
SET order_count = (
    SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id
);

-- Update with JOIN-like syntax
UPDATE users u
SET total_spent = (
    SELECT SUM(total) FROM orders o WHERE o.user_id = u.id
);
```

## DELETE Operations

### Basic DELETE

```sql
-- Delete specific rows
DELETE FROM users WHERE status = 'inactive';

-- Delete with subquery
DELETE FROM products
WHERE id IN (SELECT product_id FROM discontinued_items);

-- Delete oldest records
DELETE FROM logs
WHERE id NOT IN (
    SELECT id FROM logs ORDER BY created_at DESC LIMIT 10000
);

-- Clear entire table
DELETE FROM session_data;

-- Delete with limit (SQLite doesn't support LIMIT in DELETE directly)
-- Use subquery instead:
DELETE FROM users WHERE id IN (
    SELECT id FROM users ORDER BY created_at LIMIT 100
);
```

### CASCADE Deletes

```sql
-- Enable foreign keys for cascade to work
PRAGMA foreign_keys = ON;

-- Delete parent (children deleted automatically)
DELETE FROM users WHERE id = 5;
-- This also deletes related orders if ON DELETE CASCADE is defined
```

## Common Table Expressions (CTEs)

### Basic CTE

```sql
-- Define reusable query fragment
WITH active_users AS (
    SELECT id, username FROM users WHERE status = 'active'
)
SELECT au.username, COUNT(o.id) AS order_count
FROM active_users au
LEFT JOIN orders o ON au.id = o.user_id
GROUP BY au.id;
```

### Multiple CTEs

```sql
WITH 
user_stats AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
),
top_users AS (
    SELECT * FROM user_stats WHERE order_count > 10
)
SELECT u.username, ts.order_count, ts.total_spent
FROM users u
JOIN top_users ts ON u.id = ts.user_id;
```

### Recursive CTEs

```sql
-- Organizational hierarchy
WITH RECURSIVE org_chart(employee, manager, level) AS (
    -- Base case: top-level (CEO)
    SELECT name, manager_id, 0
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: report to manager
    SELECT e.name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart;

-- File system traversal
WITH RECURSIVE file_tree(path, depth) AS (
    SELECT path, 0 FROM directories WHERE parent_id IS NULL
    UNION ALL
    SELECT d.path, ft.depth + 1
    FROM directories d
    JOIN file_tree ft ON d.parent_id = ft.id
)
SELECT * FROM file_tree;

-- Number sequence
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 100
)
SELECT * FROM numbers;
```

## Transactions

### Basic Transactions

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
INSERT INTO transfers (from_id, to_id, amount) VALUES (1, 2, 100);

COMMIT;

-- Or rollback on error
BEGIN;
-- ... operations ...
ROLLBACK;
```

### Transaction Commands

```sql
-- Start transaction
BEGIN;
BEGIN TRANSACTION;
BEGIN DEFERRED;      -- Default, waits for read lock
BEGIN IMMEDIATE;     -- Gets write lock immediately
BEGIN EXCLUSIVE;     -- Gets write lock and prevents other connections

-- Commit
COMMIT;
END;

-- Rollback
ROLLBACK;
ROLLBACK TO SAVEPOINT sp1;
```

### Savepoints

```sql
BEGIN;

SAVEPOINT sp1;
UPDATE table1 SET col = 1;

SAVEPOINT sp2;
UPDATE table2 SET col = 2;

-- Rollback to sp2 (undoes table2 update only)
ROLLBACK TO SAVEPOINT sp2;

-- Continue and commit
UPDATE table3 SET col = 3;
COMMIT;
```

## Views

### Creating Views

```sql
-- Simple view
CREATE VIEW active_users AS
SELECT id, username, email FROM users WHERE status = 'active';

-- View with computed columns
CREATE VIEW user_order_summary AS
SELECT 
    u.id,
    u.username,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent,
    MAX(o.order_date) AS last_order
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- View with IF NOT EXISTS
CREATE VIEW IF NOT EXISTS recent_orders AS
SELECT * FROM orders WHERE order_date > date('now', '-30 days');
```

### Using Views

```sql
-- Query view like a table
SELECT * FROM active_users;

-- Join views
SELECT uos.username, uos.order_count, p.name AS last_product
FROM user_order_summary uos
JOIN last_orders_view lo ON uos.id = lo.user_id;

-- View in subquery
SELECT * FROM users
WHERE id IN (SELECT user_id FROM top_customers);
```

### Modifying Views

```sql
-- Drop view
DROP VIEW IF EXISTS active_users;

-- Replace view
CREATE VIEW active_users AS
SELECT id, username, email, phone FROM users WHERE status = 'active';

-- SQLite doesn't support ALTER VIEW directly
```

### Updatable Views

```sql
-- Simple views are updatable
INSERT INTO active_users (username, email) VALUES ('new', 'new@example.com');

UPDATE active_users SET email = 'updated@example.com' WHERE username = 'new';

DELETE FROM active_users WHERE username = 'new';

-- Complex views with aggregates/joins may not be updatable
```
