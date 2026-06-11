# SQL Reference

## Data Types

### Scalar Types

- **Numeric**: `TINYINT`, `SMALLINT`, `INTEGER`, `BIGINT`, `HUGEINT`, `UTINYINT`, `USMALLINT`, `UINTEGER`, `UBIGINT`, `FLOAT` (32-bit), `DOUBLE` (64-bit), `DECIMAL(p,s)`, `NUMERIC(p,s)`
- **Text**: `VARCHAR`, `TEXT`
- **Binary**: `BLOB`, `VARBINARY`
- **Boolean**: `BOOLEAN`
- **Temporal**: `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ`, `TIMESTAMP_S`, `TIMESTAMP_MS`, `TIMESTAMP_NS`, `INTERVAL`

### Complex Types

**Array**: Fixed-size or variable-length arrays of any type.

```sql
-- Create array literal
SELECT [1, 2, 3] AS nums;

-- Array from column
SELECT ARRAY_AGG(score) FROM students;

-- Access elements (1-indexed)
SELECT nums[1] FROM data;

-- Array functions
SELECT list_element([1,2,3], 2);       -- returns 2
SELECT list_sort([3,1,2]);             -- returns [1,2,3]
SELECT list_flatten([[1,2],[3,4]]);    -- returns [1,2,3,4]
```

**Struct**: Named fields with potentially different types.

```sql
-- Create struct literal
SELECT {'name': 'Alice', 'age': 30} AS person;

-- Access fields
SELECT person.name FROM data;
SELECT person['name'] FROM data;

-- Nested structs
SELECT {'user': {'name': 'Bob', 'scores': [90, 85]}} AS record;
```

**Map**: Key-value pairs.

```sql
-- Create map
SELECT MAP {'key1': 100, 'key2': 200} AS my_map;

-- Access values
SELECT my_map['key1'];
```

**Union**: Values that can be one of several types (similar to Rust enums / TypeScript unions).

```sql
CREATE TYPE result AS UNION (success: INTEGER, error: VARCHAR);
```

### Type Casting

```sql
-- CAST expression
SELECT CAST('123' AS INTEGER);
SELECT '123'::INTEGER;

-- Automatic coercion (Friendly SQL)
SELECT '123' + 7;  -- Returns 130 (auto-casts string to integer)
```

## Query Syntax

### SELECT with DuckDB Extensions

```sql
-- Standard SELECT
SELECT name, COUNT(*) as cnt
FROM users
WHERE active = true
GROUP BY name
HAVING cnt > 5
ORDER BY cnt DESC
LIMIT 10;
```

**QUALIFY**: Filter on window function results (DuckDB extension).

```sql
SELECT name, score, RANK() OVER (PARTITION BY class ORDER BY score DESC) as rank
FROM students
QUALIFY rank <= 3;  -- Top 3 per class
```

**PIVOT / UNPIVOT**: Transform rows to columns and vice versa.

```sql
-- PIVOT: rows to columns
PIVOT sales
ON category USING SUM(amount)
WHERE region = 'US';

-- UNPIVOT: columns to rows
UNPIVOT wide_table
ON q1, q2, q3, q4
NAME AS quarter VALUE AS revenue;
```

### FROM and JOIN

```sql
-- Cross join
SELECT * FROM a, b;

-- Inner join
SELECT * FROM a JOIN b ON a.id = b.a_id;

-- Left/Right/Full outer join
SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;

-- Semi join (rows in A that have matches in B)
SELECT * FROM a SEMI JOIN b ON a.id = b.a_id;

-- Anti join (rows in A with NO matches in B)
SELECT * FROM a ANTI JOIN b ON a.id = b.a_id;

-- AsOf join (for time-series data — joins on closest timestamp <= condition)
SELECT * FROM trades
ASOF JOIN prices ON trades.symbol = prices.symbol
AND trades.time <= prices.time;
```

### WITH (Common Table Expressions)

```sql
WITH ranked AS (
    SELECT name, score,
           ROW_NUMBER() OVER (ORDER BY score DESC) as rn
    FROM students
)
SELECT * FROM ranked WHERE rn <= 10;
```

### Window Functions

```sql
-- Standard windows
SELECT name, score,
       RANK() OVER (ORDER BY score DESC) as rank,
       AVG(score) OVER (PARTITION BY class) as class_avg,
       LAG(score) OVER (ORDER BY date) as prev_score,
       SUM(amount) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7d
FROM students;
```

### Set Operations

```sql
SELECT * FROM a UNION SELECT * FROM b;        -- distinct
SELECT * FROM a UNION ALL SELECT * FROM b;    -- with duplicates
SELECT * FROM a INTERSECT SELECT * FROM b;
SELECT * FROM a EXCEPT SELECT * FROM b;
```

### Prepared Statements

```sql
-- In SQL shell
PREPARE stmt AS SELECT * FROM users WHERE age > $1;
EXECUTE stmt(25);
DEALLOCATE stmt;

# In Python
con = duckdb.connect()
prepared = con.prepare("SELECT * FROM users WHERE age > ?")
result = prepared.execute([25]).fetchall()
```

## Functions

### Aggregate Functions

```sql
-- Standard aggregates
SELECT COUNT(*), SUM(amount), AVG(price), MIN(date), MAX(date)
FROM orders;

-- Distinct counts
SELECT COUNT(DISTINCT user_id) FROM events;

-- Statistical aggregates
SELECT STDDEV(score), VARIANCE(score), QUANTILE(score, 0.5)
FROM students;

-- String aggregation
SELECT LIST(name, ', ') FROM users ORDER BY name;
SELECT STRING_AGG(name, ', ') FROM users;

-- Quantile variants
SELECT QUANTILE_CONT(score, [0.25, 0.5, 0.75]) FROM exams;
```

### Table Functions

```sql
-- Generate series
SELECT * FROM generate_series(1, 10, 2);
-- Returns: 1, 3, 5, 7, 9

-- Read CSV with options
SELECT * FROM read_csv_auto('data.csv', header=true, delim=',');

-- Read Parquet
SELECT * FROM read_parquet('data.parquet');

-- Read JSON
SELECT * FROM read_json_auto('data.json');

-- Summarize data (auto-statistics)
SUMMARIZE table_name;
SUMMARIZE (SELECT * FROM large_table WHERE date > '2024-01-01');

-- UNNEST arrays/structs
SELECT * FROM UNNEST([1, 2, 3]);
SELECT * FROM UNNEST({'a': [1,2], 'b': [3,4]});
```

### Lambda Functions

DuckDB supports inline lambda expressions for flexible transformations:

```sql
-- List transform with lambda
SELECT list_transform([1, 2, 3], x -> x * 2);
-- Returns [2, 4, 6]

-- List filter with lambda
SELECT list_filter([1, 2, 3, 4], x -> x > 2);
-- Returns [3, 4]

-- Named parameters
SELECT list_transform([1, 2, 3], (x, idx) -> x * idx);
```

### String Functions

```sql
SELECT LOWER('Hello'), UPPER('hello');
SELECT CONCAT('a', 'b', 'c');
SELECT SUBSTR('hello', 1, 3);       -- 'hel'
SELECT SPLIT('a,b,c', ',');          -- ['a','b','c']
SELECT REGEXP_REPLACE('abc123', '[0-9]+', '');
SELECT JSON('{"key": "value"}');     -- Parse JSON string
```

### Date/Time Functions

```sql
SELECT CURRENT_DATE;
SELECT CURRENT_TIMESTAMP;
SELECT NOW();
SELECT DATE '2024-01-15' + INTERVAL 7 DAY;
SELECT EXTRACT(YEAR FROM TIMESTAMP '2024-06-15');
SELECT DATE_TRUNC('month', TIMESTAMP '2024-06-15');
SELECT EPOCH_MS(1704067200000);      -- Milliseconds to timestamp
```

## Statements

### CREATE TABLE

```sql
-- Basic table
CREATE TABLE users (
    id INTEGER,
    name VARCHAR,
    email VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    score DOUBLE NOT NULL DEFAULT 0.0
);

-- Table from query (CTAS)
CREATE TABLE active_users AS
SELECT * FROM users WHERE active = true;

-- Temporary table
CREATE TEMPORARY TABLE temp_data AS SELECT * FROM source;

-- With nested types
CREATE TABLE events (
    id INTEGER,
    tags VARCHAR[],
    metadata STRUCT(key: VARCHAR, value: VARCHAR)[]
);
```

### INSERT

```sql
-- Single row
INSERT INTO users VALUES (1, 'Alice', 'alice@example.com');

-- Multiple rows
INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie');

-- From query
INSERT INTO summary SELECT category, COUNT(*) FROM items GROUP BY category;

-- Copy from file
COPY users FROM 'users.csv' (AUTO_DETECT TRUE);
```

### Transactions

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Or rollback
BEGIN;
-- ... operations ...
ROLLBACK;
```

### MERGE INTO (Upsert)

```sql
MERGE INTO target t
USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.value = s.value
WHEN NOT MATCHED THEN INSERT (id, value) VALUES (s.id, s.value);
```

### EXPLAIN and Profiling

```sql
-- Show query plan
EXPLAIN SELECT * FROM large_table WHERE x > 100;

-- Profile execution
EXPLAIN ANALYZE SELECT COUNT(*) FROM large_table GROUP BY category;
```

## DuckDB SQL Dialect Features

**Friendly SQL**: Automatic type coercion, lenient string-to-number conversion, implicit casting in comparisons.

**Order preservation**: INSERT order is preserved for queries without ORDER BY (useful for predictable results).

**PostgreSQL compatibility**: Compatible with many PostgreSQL features including similar syntax for arrays, JSON functions, and window functions.
