# SQL Reference

## Query Syntax

### SELECT Statement

```sql
SELECT [DISTINCT | ALL] select_list
FROM from_clause
[WHERE condition]
[GROUP BY group_by_list]
[HAVING condition]
[WINDOW window_name AS (window_spec)]
[ORDER BY order_list]
[LIMIT count [OFFSET offset]]
[QUALIFY condition]
```

#### Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT name, email, age FROM users;

-- With aliases
SELECT 
    u.name AS user_name,
    u.email,
    o.amount AS order_amount
FROM users u
JOIN orders o ON u.id = o.user_id;
```

#### DISTINCT and ALL

```sql
-- Unique values only
SELECT DISTINCT city FROM users;

-- All values including duplicates (default)
SELECT ALL city FROM users;

-- DISTINCT on specific columns (PostgreSQL-style)
SELECT DISTINCT ON (city) name, city, age 
FROM users 
ORDER BY city, age DESC;
```

### FROM Clause

#### Single Table

```sql
SELECT * FROM users;
SELECT * FROM schema_name.users;
SELECT * FROM database_name.schema_name.users;
```

#### Multiple Tables (JOINs)

```sql
-- INNER JOIN (default)
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN (all left rows, matching right rows)
SELECT u.name, COALESCE(o.amount, 0) AS total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN (all right rows, matching left rows)
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN (all rows from both)
SELECT COALESCE(u.name, o.customer) AS name
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN (Cartesian product)
SELECT u.name, p.product
FROM users u
CROSS JOIN products p;

-- Multiple joins
SELECT u.name, o.amount, p.product
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id
WHERE o.amount > 100;
```

#### Lateral Joins

```sql
-- CROSS JOIN LATERAL (correlated subquery)
SELECT u.name, best.amount
FROM users u
CROSS JOIN LATERAL (
    SELECT amount 
    FROM orders 
    WHERE user_id = u.id 
    ORDER BY amount DESC 
    LIMIT 1
) AS best;
```

### WHERE Clause

#### Comparison Operators

```sql
-- Basic comparisons
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE age >= 18;
SELECT * FROM users WHERE age < 18;
SELECT * FROM users WHERE age <= 18;
SELECT * FROM users WHERE age = 18;
SELECT * FROM users WHERE age != 18;  -- or <>

-- Pattern matching
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM users WHERE name LIKE 'A%';        -- Starts with A
SELECT * FROM users WHERE name LIKE '%y';        -- Ends with y
SELECT * FROM users WHERE name LIKE 'A%y';       -- Starts A, ends y
SELECT * FROM users WHERE name LIKE '%li%';      -- Contains 'li'
SELECT * FROM users WHERE name NOT LIKE '%@gmail.com';

-- Regular expressions (with inet extension)
SELECT * FROM users WHERE email ~ '.*@gmail\.com$';

-- IN operator
SELECT * FROM users WHERE city IN ('NYC', 'LA', 'SF');
SELECT * FROM users WHERE city NOT IN ('NYC', 'LA', 'SF');

-- BETWEEN (inclusive)
SELECT * FROM users WHERE age BETWEEN 18 AND 65;
SELECT * FROM users WHERE age NOT BETWEEN 18 AND 65;

-- NULL checks
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;
SELECT * FROM users WHERE email IS DISTINCT FROM 'test@example.com';
```

#### Logical Operators

```sql
-- AND, OR, NOT
SELECT * FROM users 
WHERE age >= 18 AND city = 'NYC';

SELECT * FROM users 
WHERE (age >= 18 AND city = 'NYC') OR (age >= 21 AND city = 'LA');

SELECT * FROM users 
WHERE NOT (age < 18);

-- Parentheses for grouping
SELECT * FROM users 
WHERE (city = 'NYC' OR city = 'LA') AND age > 18;
```

#### Subqueries in WHERE

```sql
-- EXISTS
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.amount > 1000
);

-- NOT EXISTS
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- IN with subquery
SELECT * FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- Comparison with subquery
SELECT * FROM users 
WHERE age > (SELECT AVG(age) FROM users);
```

### GROUP BY and Aggregation

#### Basic Grouping

```sql
-- Simple aggregation
SELECT city, COUNT(*) AS user_count, AVG(age) AS avg_age
FROM users
GROUP BY city;

-- Multiple columns
SELECT city, gender, COUNT(*) 
FROM users
GROUP BY city, gender;
```

#### Aggregate Functions

```sql
-- Count
SELECT COUNT(*) FROM users;
SELECT COUNT(user_id) FROM users;        -- Non-NULL values only
SELECT COUNT(DISTINCT user_id) FROM users;  -- Unique values

-- Sum and Average
SELECT SUM(amount), AVG(amount) FROM orders;

-- Min and Max
SELECT MIN(age), MAX(age) FROM users;
SELECT MIN(name), MAX(name) FROM users;   -- Lexicographic

-- Variance and Standard Deviation
SELECT 
    VAR_POP(age) AS population_variance,
    VAR_SAMP(age) AS sample_variance,
    STDDEV_POP(age) AS population_stddev,
    STDDEV_SAMP(age) AS sample_stddev
FROM users;

-- Median (with percentile extension)
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY age) FROM users;

-- String aggregation
SELECT STRING_AGG(name, ', ') AS all_names FROM users;
SELECT LIST(name) AS name_list FROM users;  -- Returns ARRAY

-- Boolean aggregation
SELECT BOOL_AND(active) FROM users;    -- All true?
SELECT BOOL_OR(active) FROM users;     -- Any true?
```

#### HAVING Clause

```sql
-- Filter aggregated results
SELECT city, COUNT(*) AS user_count
FROM users
GROUP BY city
HAVING COUNT(*) > 100;

-- Multiple conditions
SELECT city, AVG(age) AS avg_age
FROM users
GROUP BY city
HAVING AVG(age) > 30 AND COUNT(*) > 50;
```

#### GROUP SETS, CUBE, ROLLUP

```sql
-- GROUPING SETS
SELECT city, gender, COUNT(*)
FROM users
GROUP BY GROUPING SETS ((city, gender), city, ());

-- CUBE (all combinations)
SELECT city, gender, COUNT(*)
FROM users
GROUP BY CUBE(city, gender);

-- ROLLUP (hierarchical subtotals)
SELECT city, gender, COUNT(*)
FROM users
GROUP BY ROLLUP(city, gender);
```

### ORDER BY

```sql
-- Single column
SELECT * FROM users ORDER BY name;

-- Multiple columns
SELECT * FROM users ORDER BY city, age DESC, name ASC;

-- Default is ASC (ascending)
SELECT * FROM users ORDER BY age ASC;
SELECT * FROM users ORDER BY age DESC;

-- With NULL handling
SELECT * FROM users 
ORDER BY COALESCE(age, 0) DESC;  -- NULLs sort last

SELECT * FROM users 
ORDER BY age DESC NULLS FIRST;   -- NULLs sort first
SELECT * FROM users 
ORDER BY age DESC NULLS LAST;    -- NULLs sort last (default)

-- With expressions
SELECT name, age, 2024 - birth_year AS years_active
FROM users
ORDER BY years_active DESC;

-- With aggregate (requires GROUP BY)
SELECT city, AVG(age) AS avg_age
FROM users
GROUP BY city
ORDER BY avg_age DESC;
```

### LIMIT and OFFSET

```sql
-- Limit results
SELECT * FROM users LIMIT 10;

-- Offset (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20;  -- Rows 21-30

-- OFFSET without LIMIT (valid but unusual)
SELECT * FROM users OFFSET 5;

-- With ORDER BY for consistent results
SELECT * FROM users 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 20;
```

### QUALIFY Clause

Filter on window function results (applied before LIMIT):

```sql
-- Get highest paid employee per department
SELECT department, name, salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
FROM employees
QUALIFY RANK() OVER (PARTITION BY department ORDER BY salary DESC) = 1;

-- Equivalent with subquery:
SELECT * FROM (
    SELECT department, name, salary,
           RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
    FROM employees
) WHERE rank = 1;
```

### WINDOW Functions

#### Window Syntax

```sql
window_name AS (
    PARTITION BY column_list
    ORDER BY column_list
    [ROWS | RANGE] window_frame
)

-- Or inline:
function() OVER (
    PARTITION BY column_list
    ORDER BY column_list
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

#### Window Frame Specifications

```sql
-- Default: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
SUM(amount) OVER (PARTITION BY user_id ORDER BY date)

-- Rows-based frame
SUM(amount) OVER (
    PARTITION BY user_id 
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)

-- Fixed window
AVG(score) OVER (
    PARTITION BY student_id
    ORDER BY test_date
    ROWS BETWEEN 3 PRECEDING AND 1 FOLLOWING
)

-- Unbounded frame
SUM(amount) OVER (
    PARTITION BY user_id
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```

#### Window Functions

```sql
-- Ranking functions
SELECT 
    name,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    NTILE(4) OVER (PARTITION BY department ORDER BY salary DESC) AS quartile
FROM employees;

-- Aggregate window functions
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total,
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY date) AS user_running_total
FROM transactions;

-- Value functions (lag/lead)
SELECT 
    name,
    salary,
    LAG(salary) OVER (ORDER BY hire_date) AS prev_salary,
    LEAD(salary) OVER (ORDER BY hire_date) AS next_salary,
    LAG(salary, 2) OVER (ORDER BY hire_date) AS salary_2_ago
FROM employees;

-- First/Last value
SELECT 
    date,
    closing_price,
    FIRST_VALUE(opening_price) OVER (ORDER BY date) AS first_open,
    LAST_VALUE(opening_price) OVER (
        ORDER BY date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_open
FROM stock_prices;
```

### Common Table Expressions (CTEs)

#### Basic CTE

```sql
WITH high_value_users AS (
    SELECT user_id, SUM(amount) AS total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 1000
)
SELECT u.name, h.total_spent
FROM users u
JOIN high_value_users h ON u.id = h.user_id;
```

#### Multiple CTEs

```sql
WITH 
user_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
),
top_users AS (
    SELECT user_id
    FROM user_totals
    WHERE total > (SELECT AVG(total) FROM user_totals)
)
SELECT u.name, ut.total
FROM users u
JOIN top_users t ON u.id = t.user_id
JOIN user_totals ut ON u.id = ut.user_id;
```

#### Recursive CTEs

```sql
-- Generate numbers 1 to 10
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 10
)
SELECT * FROM numbers;

-- Hierarchical data (organization chart)
WITH RECURSIVE subordinates AS (
    -- Anchor: start with CEO
    SELECT id, name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: find direct reports
    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;
```

### SET Operations

#### UNION

```sql
-- Combine results (removes duplicates)
SELECT name FROM users
UNION
SELECT name FROM customers;

-- Keep duplicates
SELECT name FROM users
UNION ALL
SELECT name FROM customers;

-- With ORDER BY
SELECT name FROM users
UNION ALL
SELECT name FROM customers
ORDER BY name;
```

#### INTERSECT

```sql
-- Common rows only
SELECT email FROM users
INTERSECT
SELECT email FROM subscribers;

-- Keep duplicates
SELECT email FROM users
INTERSECT ALL
SELECT email FROM subscribers;
```

#### EXCEPT

```sql
-- Rows in first but not second
SELECT email FROM users
EXCEPT
SELECT email FROM unsubscribed;

-- Keep duplicates
SELECT email FROM users
EXCEPT ALL
SELECT email FROM unsubscribed;
```

### Data Modification Statements

#### INSERT

```sql
-- Single row
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');

-- Multiple rows
INSERT INTO users (id, name, email) 
VALUES 
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com');

-- From SELECT
INSERT INTO user_archive (id, name, email, archived_at)
SELECT id, name, email, CURRENT_TIMESTAMP
FROM users
WHERE last_login < '2023-01-01';

-- RETURNING clause
INSERT INTO users (name, email) 
VALUES ('Alice', 'alice@example.com')
RETURNING id, name;
```

#### UPDATE

```sql
-- Basic update
UPDATE users
SET age = 30
WHERE id = 1;

-- Multiple columns
UPDATE users
SET 
    age = 31,
    last_updated = CURRENT_TIMESTAMP
WHERE id = 1;

-- From subquery
UPDATE users
SET total_orders = (
    SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id
);

-- With JOIN
UPDATE users u
SET total_spent = o.total
FROM (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
) o
WHERE u.id = o.user_id;

-- RETURNING clause
UPDATE users
SET age = 31
WHERE id = 1
RETURNING name, age;
```

#### DELETE

```sql
-- Basic delete
DELETE FROM users WHERE id = 1;

-- With subquery
DELETE FROM users
WHERE id IN (SELECT user_id FROM inactive_users);

-- RETURNING clause
DELETE FROM users
WHERE last_login < '2023-01-01'
RETURNING id, name;
```

#### MERGE (UPSERT)

```sql
MERGE INTO inventory AS target
USING sales AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN
    UPDATE SET quantity = target.quantity - source.units_sold
WHEN NOT MATCHED THEN
    INSERT (product_id, quantity)
    VALUES (source.product_id, 0);
```

### CREATE Statements

#### CREATE TABLE

```sql
-- Basic table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- With constraints
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DOUBLE CHECK (amount > 0),
    status VARCHAR DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled'))
);

-- CTAS (Create Table As Select)
CREATE TABLE high_value_users AS
SELECT u.*, o.total_spent
FROM users u
JOIN (
    SELECT user_id, SUM(amount) AS total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 1000
) o ON u.id = o.user_id;

-- Temporary table
CREATE TEMPORARY TABLE temp_results AS
SELECT * FROM users WHERE age > 18;
```

#### CREATE VIEW

```sql
-- Basic view
CREATE VIEW active_users AS
SELECT id, name, email
FROM users
WHERE last_login > CURRENT_DATE - INTERVAL '30 days';

-- Materialized view (requires extension)
CREATE MATERIALIZED VIEW user_summary AS
SELECT 
    u.id,
    u.name,
    COUNT(o.id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW user_summary;
```

#### CREATE INDEX

```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_users_city_age ON users(city, age);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Partial index
CREATE INDEX idx_active_users ON users(id) WHERE active = true;
```

### ALTER Statements

#### ALTER TABLE

```sql
-- Add column
ALTER TABLE users ADD COLUMN phone VARCHAR;

-- Drop column
ALTER TABLE users DROP COLUMN phone;

-- Rename column
ALTER TABLE users RENAME COLUMN email TO email_address;

-- Modify column type
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- Add constraint
ALTER TABLE users ADD CONSTRAINT chk_age CHECK (age >= 0);

-- Drop constraint
ALTER TABLE users DROP CONSTRAINT chk_age;
```

#### ALTER VIEW

```sql
ALTER VIEW active_users AS
SELECT id, name, email
FROM users
WHERE last_login > CURRENT_DATE - INTERVAL '60 days';
```

### DROP Statements

```sql
-- Drop table
DROP TABLE users;
DROP TABLE IF EXISTS users;  -- No error if doesn't exist

-- Drop view
DROP VIEW active_users;

-- Drop index
DROP INDEX idx_users_email;

-- Drop schema (and all objects)
DROP SCHEMA public CASCADE;
```

### Transaction Control

```sql
-- Begin transaction
BEGIN;
START TRANSACTION;

-- Commit
COMMIT;
COMMIT TRANSACTION;

-- Rollback
ROLLBACK;
ROLLBACK TRANSACTION;

-- Savepoint
SAVEPOINT sp1;
ROLLBACK TO SAVEPOINT sp1;
RELEASE SAVEPOINT sp1;
```

## Functions Reference

### String Functions

See [Text Functions](#) for complete reference.

```sql
-- Length and case
LENGTH('hello')                    -- 5
UPPER('hello')                     -- 'HELLO'
LOWER('HELLO')                     -- 'hello'
REVERSE('hello')                   -- 'olleh'

-- Substring operations
SUBSTRING('hello', 1, 3)           -- 'hel' (1-indexed)
SUBSTR('hello', 2)                 -- 'ello'
LEFT('hello', 3)                   -- 'hel'
RIGHT('hello', 2)                  -- 'lo'

-- Search and replace
POSITION('lo' IN 'hello')          -- 4
INSTR('hello', 'lo')               -- 4
REPLACE('hello', 'l', 'L')         -- 'heLLo'
TRIM('  hello  ')                  -- 'hello'
LTRIM('  hello')                   -- 'hello'
RTRIM('hello  ')                   -- 'hello'

-- Concatenation
'hello' || ' ' || 'world'          -- 'hello world'
CONCAT('hello', ' ', 'world')      -- 'hello world'

-- Regular expressions (with inet extension)
REGEXP_MATCHES('abc123', '[0-9]+') -- ['123']
REGEXP_REPLACE('abc123', '[0-9]', 'X') -- 'abcXXX'
```

### Numeric Functions

```sql
-- Basic math
ABS(-5)                            -- 5
ROUND(3.14159, 2)                  -- 3.14
FLOOR(3.7)                         -- 3.0
CEIL(3.2)                          -- 4.0
TRUNC(3.752, 2)                    -- 3.75

-- Powers and roots
POWER(2, 8)                        -- 256
SQRT(16)                           -- 4.0
CBRT(27)                           -- 3.0
EXP(1)                             -- e (2.718...)
LN(2.718)                          -- Natural log
LOG10(100)                         -- 2

-- Trigonometry
SIN(PI()/2)                        -- 1.0
COS(0)                             -- 1.0
TAN(PI()/4)                        -- ~1.0
DEGREES(PI())                      -- 180
RADIANS(180)                       -- PI

-- Random numbers
RANDOM()                           -- 0.0 to 1.0
RANDOM_INT(100)                    -- 0 to 99
```

### Date and Time Functions

```sql
-- Current date/time
CURRENT_DATE                       -- Today's date
CURRENT_TIME                       -- Current time
CURRENT_TIMESTAMP                  -- Current timestamp
NOW()                              -- Same as CURRENT_TIMESTAMP

-- Extraction
EXTRACT(YEAR FROM CURRENT_DATE)    -- 2024
EXTRACT(MONTH FROM CURRENT_DATE)   -- Current month
EXTRACT(DAY FROM CURRENT_DATE)     -- Day of month
EXTRACT(WEEK FROM CURRENT_DATE)    -- Week number
EXTRACT(DOW FROM CURRENT_DATE)     -- Day of week (0-6)

-- Date parts
YEAR(CURRENT_DATE)                 -- 2024
MONTH(CURRENT_DATE)                -- Current month
DAY(CURRENT_DATE)                  -- Day of month
HOUR(CURRENT_TIMESTAMP)            -- Hour (0-23)
MINUTE(CURRENT_TIMESTAMP)          -- Minute (0-59)
SECOND(CURRENT_TIMESTAMP)          -- Second (0-59)

-- Date arithmetic
CURRENT_DATE + INTERVAL '7 days'   -- One week from now
CURRENT_DATE - INTERVAL '3 months' -- Three months ago
INTERVAL '1 hour' + INTERVAL '30 minutes' -- 1.5 hours

-- Date differences
AGE(CURRENT_DATE, DATE '2020-01-01') -- Time interval
DATEDIFF(day, DATE '2024-01-01', CURRENT_DATE) -- Days difference

-- Formatting (with dateformat extension)
TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD')     -- '2024-01-15'
TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') -- Full timestamp

-- Parsing
DATE '2024-01-15'                    -- Date literal
TIMESTAMP '2024-01-15 14:30:00'      -- Timestamp literal
INTERVAL '3 days 4 hours'            -- Interval literal
```

### Array Functions

```sql
-- Creation
LIST(1, 2, 3)                        -- [1, 2, 3]
ARRAY([1, 2, 3])                     -- [1, 2, 3]
LIST_VALUE(1, 2, 3)                  -- [1, 2, 3]

-- Aggregation
SELECT LIST(name) FROM users;        -- Array of all names
SELECT LIST(ORDER BY age DESC) FROM users;  -- Sorted array

-- Operations
LIST_LENGTH([1, 2, 3])               -- 3
[1, 2, 3] || [4, 5, 6]              -- [1, 2, 3, 4, 5, 6]
[1, 2, 3][1]                         -- First element (1-indexed)
[1, 2, 3][-1]                        -- Last element

-- Transformation
LIST_TRANSFORM([1, 2, 3], x -> x * 2)  -- [2, 4, 6]
LIST_FILTER([1, 2, 3, 4], x -> x > 2)  -- [3, 4]
LIST_REDUCE([1, 2, 3], (a, b) -> a + b, 0)  -- 6

-- Unnesting
SELECT * FROM UNNEST([1, 2, 3]);     -- Three rows: 1, 2, 3
```

### Struct Functions

```sql
-- Creation
STRUCT_PACK(id := 1, name := 'Alice', age := 30)

-- Access
(STRUCT_PACK(x := 10, y := 20)).x    -- 10
(STRUCT_PACK(x := 10, y := 20)).y    -- 20

-- Aggregation
SELECT LIST_AGG(STRUCT_PACK(name, age)) FROM users;
```

### Map Functions

```sql
-- Creation
MAP(['a', 'b', 'c'], [1, 2, 3])

-- Access
MAP(['x', 'y'], [10, 20])['x']      -- 10

-- Operations
MAP_KEYS(MAP(['a', 'b'], [1, 2]))   -- ['a', 'b']
MAP_VALUES(MAP(['a', 'b'], [1, 2])) -- [1, 2]
MAP_ENTRY(MAP(['a', 'b'], [1, 2]), 'a')  -- 1
```

## Useful Tips and Patterns

### Common Query Patterns

#### Top N per Group

```sql
-- Using window function (recommended)
SELECT * FROM (
    SELECT 
        department,
        employee_name,
        salary,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
    FROM employees
) WHERE rank <= 3;

-- Using QUALIFY (cleaner)
SELECT department, employee_name, salary
FROM employees
QUALIFY RANK() OVER (PARTITION BY department ORDER BY salary DESC) <= 3;
```

#### Running Totals

```sql
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total,
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3day
FROM transactions;
```

#### Gaps and Islands

```sql
-- Find consecutive ID sequences
WITH grouped AS (
    SELECT 
        id,
        id - ROW_NUMBER() OVER (ORDER BY id) AS grp
    FROM my_table
)
SELECT MIN(id) AS start_id, MAX(id) AS end_id, COUNT(*) AS count
FROM grouped
GROUP BY grp;
```

#### Pivot Tables

```sql
-- Using conditional aggregation
SELECT 
    department,
    SUM(CASE WHEN year = 2022 THEN salary END) AS total_2022,
    SUM(CASE WHEN year = 2023 THEN salary END) AS total_2023,
    SUM(CASE WHEN year = 2024 THEN salary END) AS total_2024
FROM salaries
GROUP BY department;

-- Using PIVOT statement (if available)
SELECT * FROM salaries
PIVOT (
    SUM(salary) FOR year IN (2022, 2023, 2024)
);
```
