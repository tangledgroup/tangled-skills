# SQL Functions Reference

Comprehensive reference for SQLite's built-in SQL functions including aggregate, mathematical, string, date/time, encoding, and window functions.

## Aggregate Functions

### COUNT

Count rows or non-NULL values:

```sql
-- Count all rows
SELECT COUNT(*) FROM users;

-- Count non-NULL values
SELECT COUNT(email) FROM users;

-- Count distinct values
SELECT COUNT(DISTINCT status) FROM users;

-- Count with condition
SELECT COUNT(*) FROM users WHERE status = 'active';

-- Grouped counts
SELECT status, COUNT(*) AS user_count 
FROM users 
GROUP BY status;

-- Conditional counting
SELECT 
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_count,
    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) AS inactive_count
FROM users;
```

### SUM

Sum of values:

```sql
-- Basic sum
SELECT SUM(price) FROM order_items;

-- Sum with grouping
SELECT customer_id, SUM(total) AS total_spent
FROM orders
GROUP BY customer_id;

-- Sum with condition
SELECT SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END) 
FROM orders;

-- Handle NULL values
SELECT COALESCE(SUM(amount), 0) AS total FROM transactions;
```

### AVG

Average of values:

```sql
-- Basic average
SELECT AVG(price) FROM products;

-- Average with grouping
SELECT category, AVG(price) AS avg_price
FROM products
GROUP BY category;

-- Average with rounding
SELECT ROUND(AVG(rating), 2) AS avg_rating FROM reviews;

-- Weighted average
SUM(value * weight) / SUM(weight) AS weighted_avg
```

### MIN and MAX

Minimum and maximum values:

```sql
-- Basic min/max
SELECT MIN(created_at), MAX(created_at) FROM orders;

-- Min/max with grouping
SELECT category, MIN(price), MAX(price)
FROM products
GROUP BY category;

-- Find row with minimum/maximum value
SELECT * FROM orders 
WHERE total = (SELECT MIN(total) FROM orders);

-- Multiple columns
SELECT MIN(price), MAX(price), AVG(price) FROM products;

-- Min/max on text (lexicographic)
SELECT MIN(name), MAX(name) FROM users;
```

### GROUP_CONCAT

Concatenate group values:

```sql
-- Basic concatenation
SELECT user_id, GROUP_CONCAT(product_name, ', ') AS products
FROM order_items
GROUP BY user_id;

-- With ordering (requires subquery in SQLite)
SELECT user_id, 
    (SELECT GROUP_CONCAT(product_name, ', ') 
     FROM order_items o2 
     WHERE o2.user_id = o1.user_id 
     ORDER BY o2.order_date) AS ordered_products
FROM order_items o1
GROUP BY user_id;

-- Limit concatenated values
SELECT user_id, SUBSTR(GROUP_CONCAT(tag, ','), 1, 50) AS tags
FROM article_tags
GROUP BY user_id;
```

### STDDEV and VAR (SQLite 3.91+)

Statistical functions:

```sql
-- Standard deviation
SELECT STDDEV(salary) FROM employees;

-- Variance
SELECT VAR(salary) FROM employees;

-- Population vs sample
SELECT 
    STDDEV_POP(salary) AS population_stddev,
    STDDEV_SAMPLE(salary) AS sample_stddev
FROM employees;
```

## Mathematical Functions

### Basic Arithmetic

```sql
-- Absolute value
SELECT ABS(-42);  -- Returns: 42

-- Random number (0 to MAXINT)
SELECT RANDOM();

-- Random integer in range
SELECT RANDOM() % 10;  -- 0-9

-- Round to nearest integer
SELECT ROUND(3.567);     -- 4.0
SELECT ROUND(3.5);       -- 4.0 (rounds away from zero)
SELECT ROUND(3.4);       -- 3.0

-- Round to decimal places
SELECT ROUND(3.567, 2);  -- 3.57
SELECT ROUND(123.456, -1);  -- 120.0

-- Floor (round down)
SELECT floor(3.9);  -- 3.0

-- Ceiling (round up)
SELECT ceil(3.1);   -- 4.0

-- Truncate decimal places
SELECT trunc(3.567, 2);  -- 3.56
```

### Power and Root

```sql
-- Square root
SELECT sqrt(16);     -- 4.0
SELECT sqrt(2);      -- 1.4142135623731

-- Power (base^exponent)
-- SQLite doesn't have POWER(), use ** operator
SELECT 2 ** 10;      -- 1024
SELECT 5 ** 3;       -- 125

-- Cube root (using exponent)
SELECT 27 ** (1.0/3);  -- 3.0

-- nth root
SELECT 1000 ** (1.0/3);  -- 10.0
```

### Trigonometric Functions (SQLite 3.35+)

```sql
-- Pi constant
SELECT pi();  -- 3.14159265358979

-- Radians to degrees
SELECT radians(180);   -- Converts to radians

-- Degrees to radians  
SELECT degrees(3.14159);  -- Converts to degrees

-- Sine
SELECT sin(0);           -- 0.0
SELECT sin(pi()/2);      -- 1.0
SELECT sin(pi());        -- ~0.0 (very small)

-- Cosine
SELECT cos(0);           -- 1.0
SELECT cos(pi()/2);      -- ~0.0
SELECT cos(pi());        -- -1.0

-- Tangent
SELECT tan(0);           -- 0.0
SELECT tan(pi()/4);      -- ~1.0

-- Inverse trigonometric functions
SELECT asin(0);          -- 0.0
SELECT acos(1);          -- 0.0
SELECT atan(1);          -- ~0.785 (pi/4)

-- Hyperbolic functions
SELECT sinh(0);          -- 0.0
SELECT cosh(0);          -- 1.0
SELECT tanh(0);          -- 0.0
```

### Logarithmic Functions

```sql
-- Natural logarithm (base e)
SELECT ln(2.71828);      -- ~1.0
SELECT ln(1);            -- 0.0

-- Log base 10
SELECT log10(100);       -- 2.0
SELECT log10(1000);      -- 3.0

-- Log base 2
SELECT log2(8);          -- 3.0
SELECT log2(1024);       -- 10.0

-- Arbitrary base logarithm: log(base, value)
SELECT log(2, 8);        -- 3.0 (log base 2 of 8)
SELECT log(10, 1000);    -- 3.0 (log base 10 of 1000)

-- Exponential (e^x)
SELECT exp(1);           -- 2.71828...
SELECT exp(0);           -- 1.0
SELECT exp(2);           -- 7.389...
```

### Special Math Functions

```sql
-- Sign function
SELECT sign(-10);        -- -1
SELECT sign(0);          -- 0
SELECT sign(42);         -- 1

-- Factorial (integer only)
SELECT factorial(5);     -- 120
SELECT factorial(10);    -- 3628800

-- Greatest common divisor
SELECT gcd(12, 8);       -- 4

-- Least common multiple  
SELECT lcm(12, 8);       -- 24

-- Hexadecimal conversion
SELECT hex(255);         -- "FF"
SELECT hex(-1);          -- "FFFFFFFF" (two's complement)

-- Unhex (convert hex to blob)
SELECT unhex('48656C6C6F');  -- "Hello" as BLOB
```

## String Functions

### Length and Position

```sql
-- String length (characters)
SELECT length('Hello');           -- 5
SELECT length('');                -- 0

-- UTF-16 length (bytes / 2)
SELECT length(utf16_text);

-- Find substring position (1-indexed)
SELECT instr('Hello World', 'World');  -- 7
SELECT instr('Hello Hello', 'Hello');  -- 1 (first occurrence)
SELECT instr('abcdef', 'xy');          -- 0 (not found)

-- Case-insensitive search
SELECT instr(lower('Hello World'), lower('world'));  -- 7
```

### Substring Extraction

```sql
-- substr(string, start) - from position to end
SELECT substr('Hello World', 7);     -- "World"

-- substr(string, start, length)
SELECT substr('Hello World', 1, 5);  -- "Hello"
SELECT substr('Hello World', 7, 5);  -- "World"

-- Negative start (from end)
SELECT substr('Hello World', -5);       -- "World"
SELECT substr('Hello World', -5, 3);    -- "Wor"

-- Zero and negative indexing
SELECT substr('Hello', 0, 3);    -- "Hel" (same as start=1)
SELECT substr('Hello', -2, 1);   -- "l"
```

### Case Conversion

```sql
-- Upper case
SELECT upper('hello world');     -- "HELLO WORLD"
SELECT upper('HeLLo WoRLD');     -- "HELLO WORLD"

-- Lower case
SELECT lower('HELLO WORLD');     -- "hello world"
SELECT lower('HeLLo');           -- "hello"

-- Case-insensitive comparison
SELECT * FROM users 
WHERE lower(email) = lower('Test@Example.com');

-- Create index for case-insensitive search
CREATE INDEX idx_users_lower_email ON users(lower(email));
```

### Padding and Trimming

```sql
-- Left pad
SELECT lpad('42', 5, '0');       -- "00042"
SELECT lpad('abc', 2, 'x');      -- "bc" (truncated)

-- Right pad
SELECT rpad('42', 5, '0');       -- "42000"
SELECT rpad('hello', 3, '-');    -- "hel" (truncated)

-- Remove leading spaces
SELECT ltrim('   hello');        -- "hello"

-- Remove trailing spaces
SELECT rtrim('hello   ');        -- "hello"

-- Remove both
SELECT trim('   hello   ');      -- "hello"

-- Custom characters to remove
SELECT ltrim('xxxhelloxxx', 'x');     -- "helloxxx"
SELECT rtrim('xxxhelloxxx', 'x');     -- "xxxhello"
SELECT trim('xxxhelloxxx', 'x');      -- "hello"
```

### String Concatenation

```sql
-- Using || operator
SELECT 'Hello' || ' ' || 'World';     -- "Hello World"
SELECT first_name || ' ' || last_name AS full_name FROM users;

-- Using CONCAT function
SELECT CONCAT('Hello', ' ', 'World');  -- "Hello World"
SELECT CONCAT('abc', NULL, 'def');     -- "abcdef" (NULL treated as empty)

-- Multiple concatenations
SELECT CONCAT('User: ', username, ' (', email, ')');

-- Concat with numbers (auto-converted to text)
SELECT CONCAT('Price: $', price);      -- "Price: $9.99"
```

### String Replacement

```sql
-- Replace all occurrences
SELECT replace('Hello World', 'World', 'SQLite');  -- "Hello SQLite"
SELECT replace('aaa', 'a', 'b');                  -- "bbb"

-- Replace with empty string (delete)
SELECT replace('hello-world', '-', '');           -- "helloworld"

-- Case-sensitive replacement
SELECT replace('Hello HELLO hello', 'hello', 'X');  -- "Hello HELLO X"

-- Nested replacements
SELECT replace(replace('a.b.c', '.', '-'), '-', '_');  -- "a_b_c"
```

### String Formatting

```sql
-- Format with printf-style formatting
SELECT printf('Price: $%.2f', 9.5);        -- "Price: $9.50"
SELECT printf('%d-%02d-%02d', 2024, 1, 5); -- "2024-01-05"

-- Format numbers
SELECT printf('%'.d', 1234567.89);         -- "1,234,567.89" (if locale supports)

-- Format dates
SELECT printf('%Y-%m-%d', strftime('%Y', created_at), 
                                       strftime('%m', created_at),
                                       strftime('%d', created_at));
```

## Date and Time Functions

### Current Date and Time

```sql
-- Current date/time values
SELECT current_time;   -- "HH:MM:SS"
SELECT current_date;   -- "YYYY-MM-DD"
SELECT current_timestamp;  -- "YYYY-MM-DD HH:MM:SS"

-- Equivalent functions
SELECT time('now');
SELECT date('now');
SELECT datetime('now');

-- Julian day number
SELECT julianday('now');     -- Days since November 24, 4714 BC
SELECT julianday('2024-01-01');

-- Unix timestamp (seconds since 1970-01-01)
SELECT unixepoch('now');
SELECT unixepoch('2024-01-01 00:00:00');
```

### Date/Time Formatting

```sql
-- Format date components
SELECT strftime('%Y', 'now');        -- "2024" (year)
SELECT strftime('%m', 'now');        -- "01" (month)
SELECT strftime('%d', 'now');        -- "15" (day)
SELECT strftime('%H', 'now');        -- "14" (hour 24h)
SELECT strftime('%M', 'now');        -- "30" (minute)
SELECT strftime('%S', 'now');        -- "45" (second)

-- Custom formats
SELECT strftime('%Y-%m-%d %H:%M:%S', 'now');  -- "2024-01-15 14:30:45"
SELECT strftime('%A, %B %d, %Y', 'now');      -- "Monday, January 15, 2024"
SELECT strftime('%D', 'now');                  -- "01/15/24" (US format)

-- Format codes:
-- %Y: 4-digit year, %y: 2-digit year
-- %m: month (01-12), %d: day (01-31)
-- %H: hour (00-23), %h: hour (01-12)
-- %M: minute (00-59), %S: second (00-59)
-- %w: weekday (0=Sunday), %W: ISO week
```

### Date/Time Modifiers

```sql
-- Add/subtract time
SELECT date('now', '+1 day');           -- Tomorrow
SELECT date('now', '-7 days');          -- 7 days ago
SELECT datetime('now', '+3 hours');     -- 3 hours from now
SELECT datetime('now', '-30 minutes');  -- 30 minutes ago

-- Multiple modifiers
SELECT datetime('now', '+1 day', '-2 hours', '+30 minutes');

-- Common patterns
SELECT date('now', 'start of month');   -- First day of current month
SELECT date('now', 'start of year');    -- January 1st of current year
SELECT date('now', 'end of month');     -- Last day of current month
SELECT date('now', '+1 month', 'start of month');  -- First day of next month

-- Week calculations
SELECT date('now', 'weekday 1');        -- This Monday (weekday 0=Sunday)
SELECT date('now', '-7 days', 'weekday 1');  -- Last Monday

-- Business days
SELECT date('now', '+5 days', 'weekday 1', '-1 day');  -- 5 business days ahead
```

### Date/Time Calculations

```sql
-- Age in years
SELECT strftime('%Y', 'now') - strftime('%Y', birth_date) AS age 
FROM users;

-- More accurate age (accounts for month/day)
SELECT 
    strftime('%Y', 'now') - strftime('%Y', birth_date) -
    (strftime('%m-%d', 'now') < strftime('%m-%d', birth_date)) AS age
FROM users;

-- Days between dates
SELECT julianday('2024-12-31') - julianday('2024-01-01');  -- 365

-- Hours between timestamps
SELECT (julianday('2024-01-15 14:30:00') - julianday('2024-01-15 09:00:00')) * 24;  -- 5.5

-- Duration formatting
SELECT 
    printf('%d days %d hours %d minutes',
        (julianday(end_time) - julianday(start_time)) * 24 / 1,
        ((julianday(end_time) - julianday(start_time)) * 24) % 24,
        (((julianday(end_time) - julianday(start_time)) * 24 * 60) % 60)
    ) AS duration
FROM events;
```

### Time Zone Handling

```sql
-- SQLite stores UTC internally
SELECT datetime('now', 'utc');

-- Convert to local time
SELECT datetime('now', 'localtime');

-- Specific timezone offset
SELECT datetime('2024-01-15 12:00:00', '+5 hours');   -- UTC+5
SELECT datetime('2024-01-15 12:00:00', '-8 hours');   -- UTC-8

-- Store as UTC, display in local time
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_time TEXT  -- Store as UTC
);

INSERT INTO events VALUES (1, datetime('now', 'utc'));

SELECT 
    event_time AS utc_time,
    datetime(event_time, 'localtime') AS local_time
FROM events;
```

## Encoding Functions

### Hex Encoding

```sql
-- Convert to hexadecimal
SELECT hex('Hello');           -- "48656C6C6F"
SELECT hex(12345);             -- "3039"
SELECT hex(X'48656C6C6F');     -- "48656C6C6F" (BLOB)

-- Convert from hexadecimal
SELECT unhex('48656C6C6F');    -- "Hello" as BLOB
SELECT cast(unhex('48656C6C6F') AS TEXT);  -- "Hello" as text

-- Case-insensitive input
SELECT unhex('48656c6c6f');    -- Also works
```

### Base64 Encoding (SQLite 3.91+)

```sql
-- Encode to base64
SELECT encode('Hello World', 'base64');  -- "SGVsbG8gV29ybGQ="

-- Decode from base64
SELECT decode('SGVsbG8gV29ybGQ=', 'base64');  -- "Hello World"

-- Store binary data as text
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    name TEXT,
    content_base64 TEXT  -- Base64 encoded content
);

INSERT INTO files VALUES 
    (1, 'document.txt', encode(readfile('document.txt'), 'base64'));

-- Retrieve and decode
SELECT decode(content_base64, 'base64') AS content FROM files WHERE id = 1;
```

### URL Encoding (SQLite 3.91+)

```sql
-- URL encode
SELECT encode('hello world!', 'percent');  -- "hello%20world%21"

-- URL decode
SELECT decode('hello%20world%21', 'percent');  -- "hello world!"

-- Encode query parameters
SELECT 
    name || '=' || encode(value, 'percent') AS param
FROM config;

-- Build URL with encoded parameters
SELECT 
    'https://example.com/search?' ||
    encode('q=' || search_query, 'percent') AS url
FROM searches;
```

### UUID Generation

```sql
-- Generate UUID v4 (random)
SELECT lower(
    replace(
        hex(randomblob(16)),
        substr(hex(randomblob(16)), 1, 8) || 
        '4' || 
        substr(hex(randomblob(16)), 3, 4) || 
        substr(hex(randomblob(16)), 1, 2),
        -- Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        ''
    )
);

-- Simpler UUID (not standards-compliant but unique enough)
SELECT hex(randomblob(16)) AS uuid;

-- Use as primary key
CREATE TABLE sessions (
    id TEXT PRIMARY KEY DEFAULT (hex(randomblob(16))),
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Window Functions

### Ranking Functions

```sql
-- RANK: Dense ranking with gaps
SELECT 
    name,
    score,
    RANK() OVER (ORDER BY score DESC) AS rank
FROM players;

-- DENSE_RANK: Ranking without gaps
SELECT 
    name,
    score,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM players;

-- ROW_NUMBER: Sequential numbering
SELECT 
    name,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num
FROM players;

-- NTILE: Divide into buckets
SELECT 
    name,
    score,
    NTILE(4) OVER (ORDER BY score DESC) AS quartile
FROM players;  -- Divides into 4 groups
```

### Partitioned Window Functions

```sql
-- Rank within groups
SELECT 
    department,
    employee,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;

-- Row number within partition
SELECT 
    order_date,
    customer_id,
    total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS purchase_num
FROM orders;

-- Multiple partitions
SELECT 
    region,
    category,
    product,
    sales,
    RANK() OVER (PARTITION BY region, category ORDER BY sales DESC) AS rank
FROM products;
```

### Aggregate Window Functions

```sql
-- Running total
SELECT 
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date) AS running_total
FROM daily_sales;

-- Running average
SELECT 
    date,
    value,
    AVG(value) OVER (ORDER BY date) AS running_avg
FROM metrics;

-- Moving average (last 7 days)
SELECT 
    date,
    value,
    AVG(value) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily_metrics;

-- Year-to-date total
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY strftime('%Y', order_date)
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS ytd_total
FROM orders;
```

### Window Frame Specifications

```sql
-- Rows-based frames
SELECT 
    date,
    value,
    SUM(value) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS sum_last_3_rows
FROM metrics;

-- Range-based frames
SELECT 
    salary,
    COUNT(*) OVER (
        ORDER BY salary
        RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS employees_at_or_below_salary
FROM employees;

-- Fixed size window
SELECT 
    date,
    value,
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) AS centered_moving_avg
FROM metrics;

-- Unbounded frames
SELECT 
    date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_total,
    SUM(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
    ) AS remaining_total
FROM daily_sales;
```

### Analytic Functions

```sql
-- LAG: Access previous row
SELECT 
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) AS prev_day_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS daily_change
FROM daily_sales;

-- LEAD: Access next row
SELECT 
    event_date,
    event_name,
    LEAD(event_date, 1) OVER (ORDER BY event_date) AS next_event_date,
    julianday(LEAD(event_date, 1) OVER (ORDER BY event_date)) - 
        julianday(event_date) AS days_until_next
FROM events;

-- FIRST_VALUE: First value in window
SELECT 
    date,
    price,
    FIRST_VALUE(price) OVER (
        PARTITION BY strftime('%Y-%m', date) 
        ORDER BY date
    ) AS month_opening_price
FROM stock_prices;

-- LAST_VALUE: Last value in window
SELECT 
    date,
    price,
    LAST_VALUE(price) OVER (
        PARTITION BY strftime('%Y-%m', date)
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS month_closing_price
FROM stock_prices;

-- NTH_VALUE: Nth value in window
SELECT 
    category,
    product,
    sales,
    NTH_VALUE(product, 2) OVER (
        PARTITION BY category 
        ORDER BY sales DESC
    ) AS second_best_seller
FROM products;
```

## Special Functions

### typeof()

Get the storage class of a value:

```sql
SELECT typeof(123);              -- "integer"
SELECT typeof(12.5);             -- "real"
SELECT typeof('hello');          -- "text"
SELECT typeof(X'48656C6C6F');    -- "blob"
SELECT typeof(NULL);             -- "null"

-- Check column types dynamically
SELECT name, typeof(value) AS type FROM config;
```

### quote()

Return SQL representation of value:

```sql
SELECT quote('hello');           -- "'hello'"
SELECT quote(123);               -- "123"
SELECT quote('It''s fine');      -- "'It''s fine'" (escaped)
SELECT quote(NULL);              -- "NULL"
```

### zero() and one()

Return constant values:

```sql
SELECT zero();   -- 0
SELECT one();    -- 1

-- Useful in expressions without literals
SELECT price * (one() - discount_rate) AS final_price FROM products;
```

## Function Flags and Properties

### Deterministic Functions

Functions that always return same result for same input:

```sql
-- These functions are deterministic:
-- - All mathematical functions (sin, cos, sqrt, etc.)
-- - String functions (upper, lower, length, etc.)
-- - Date/time functions with fixed inputs (date('2024-01-01'))
-- - NOT: random(), current_time, datetime('now')

-- Deterministic functions can be used in:
-- - Expression indexes
-- - Generated columns
-- - Partial indexes
```

### Innocuous Functions

Safe functions that don't modify database:

```sql
-- Most built-in functions are innocuous
-- Can be used in triggers and views safely

-- Non-innocuous functions (rare):
-- - Functions with side effects
-- - Custom functions that modify state
```

## Performance Considerations

### Function Optimization

```sql
-- Use indexes with function results
CREATE INDEX idx_lower_email ON users(lower(email));
SELECT * FROM users WHERE lower(email) = 'test@example.com';

-- Avoid functions on indexed columns in WHERE
-- Bad:
SELECT * FROM users WHERE upper(name) = 'ALICE';

-- Good (if index exists):
SELECT * FROM users WHERE name = 'Alice';

-- Or create expression index:
CREATE INDEX idx_upper_name ON users(upper(name));
```

### Function Caching

```sql
-- SQLite may cache results of deterministic functions
-- Beneficial for repeated calculations in large queries

-- Use CTEs to avoid recalculating
WITH calculated AS (
    SELECT id, price * 1.1 AS new_price FROM products
)
SELECT * FROM calculated WHERE new_price > 100;
```

## Best Practices

1. **Use appropriate functions** - Choose the right function for the task
2. **Understand NULL handling** - Most functions return NULL for NULL input
3. **Be aware of types** - Functions may convert types implicitly
4. **Consider performance** - Functions on indexed columns prevent index use
5. **Test edge cases** - Empty strings, very large numbers, special characters
6. **Use window functions wisely** - They can be memory-intensive on large datasets
7. **Leverage date modifiers** - SQLite's date/time modifiers are powerful and flexible
