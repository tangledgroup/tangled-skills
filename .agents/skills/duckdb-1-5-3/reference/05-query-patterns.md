# Query Patterns

## Contents
- FROM and JOIN Clauses
- WHERE Filtering
- GROUP BY and HAVING
- ORDER BY and LIMIT
- WINDOW Functions
- QUALIFY Clause
- Common Table Expressions (CTEs)
- Subqueries
- Set Operations
- PIVOT and UNPIVOT

## FROM and JOIN Clauses

### Basic FROM

```sql
SELECT name, score FROM students;
SELECT * FROM 'data.csv';
```

### Cross Join

```sql
SELECT a.name, b.category
FROM products a, categories b;
```

### Inner Join

```sql
SELECT u.name, e.event_type
FROM users u
JOIN events e ON u.id = e.user_id;
```

### Left/Right/Full Outer Joins

```sql
SELECT u.name, COUNT(e.id) AS event_count
FROM users u
LEFT JOIN events e ON u.id = e.user_id
GROUP BY u.name;
```

### Semi and Anti Joins

Semi join — return rows from left table that have matches:

```sql
SELECT name FROM users
WHERE id IN (SELECT user_id FROM events WHERE type = 'purchase');
```

Anti join — return rows from left table with no matches:

```sql
SELECT name FROM users
WHERE id NOT IN (SELECT user_id FROM events WHERE type = 'purchase');
```

### Cross Join Lateral

Apply a table function to each row:

```sql
SELECT t.id, elem
FROM teams t, LATERAL unnest(t.members) AS elem;
```

## WHERE Filtering

Standard SQL filtering with DuckDB extensions:

```sql
SELECT * FROM events
WHERE type = 'click'
  AND ts BETWEEN '2024-01-01' AND '2024-12-31'
  AND user_id IN (1, 2, 3);
```

### Filtering on Nested Types

```sql
-- Filter by struct field
SELECT * FROM data WHERE info.name = 'Alice';

-- Filter by array element
SELECT * FROM data WHERE 42 = ANY(scores);
```

## GROUP BY and HAVING

Aggregate with grouping:

```sql
SELECT name,
       COUNT(*) AS total,
       AVG(score) AS avg_score,
       MAX(score) AS max_score
FROM students
GROUP BY name
HAVING COUNT(*) > 5 AND AVG(score) > 80;
```

### GROUPING SETS

Multiple groupings in one query:

```sql
SELECT region, category, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS ((region), (category), ());
```

## ORDER BY and LIMIT

Sort and limit results:

```sql
SELECT name, score
FROM students
ORDER BY score DESC, name ASC
LIMIT 10 OFFSET 20;
```

NULL ordering:

```sql
SELECT * FROM data ORDER BY value NULLS LAST;
```

## WINDOW Functions

Window functions compute values across related rows without collapsing groups:

```sql
SELECT name, score,
       RANK() OVER (ORDER BY score DESC) AS rank,
       AVG(score) OVER (PARTITION BY class) AS class_avg,
       LAG(score) OVER (ORDER BY ts) AS prev_score,
       SUM(score) OVER (ORDER BY ts ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_sum
FROM students;
```

Common window functions:
- `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` — ranking
- `LAG(expr, n)`, `LEAD(expr, n)` — offset access
- `SUM() OVER`, `AVG() OVER` — running aggregates
- `NTILE(n)` — bucket assignment

Window frame specifications:

```sql
-- Default for ORDER BY: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
SUM(score) OVER (ORDER BY ts ROWS BETWEEN 5 PRECEDING AND CURRENT ROW);
```

## QUALIFY Clause

Filter on window function results — equivalent to wrapping in a subquery:

```sql
SELECT name, score,
       RANK() OVER (PARTITION BY class ORDER BY score DESC) AS rank
FROM students
QUALIFY RANK() OVER (PARTITION BY class ORDER BY score DESC) <= 3;
```

Or reference the window function alias:

```sql
SELECT name, score,
       RANK() OVER (PARTITION BY class ORDER BY score DESC) AS rank
FROM students
QUALIFY rank <= 3;
```

## Common Table Expressions (CTEs)

Named subqueries for readability and reuse:

```sql
WITH active_users AS (
    SELECT user_id FROM events WHERE ts > '2024-01-01'
),
user_scores AS (
    SELECT u.name, AVG(e.score) AS avg_score
    FROM users u
    JOIN active_users a ON u.id = a.user_id
    JOIN events e ON u.id = e.user_id
    GROUP BY u.name
)
SELECT * FROM user_scores WHERE avg_score > 80;
```

Recursive CTEs:

```sql
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 10
)
SELECT * FROM numbers;
```

## Subqueries

Scalar subquery:

```sql
SELECT name, score,
       (SELECT AVG(score) FROM students) AS overall_avg
FROM students;
```

Correlated subquery:

```sql
SELECT name, score
FROM students s
WHERE score > (SELECT AVG(score) FROM students WHERE class = s.class);
```

## Set Operations

Combine results from multiple queries:

```sql
-- Union (removes duplicates)
SELECT name FROM customers
UNION
SELECT name FROM vendors;

-- Union All (keeps duplicates)
SELECT name FROM customers
UNION ALL
SELECT name FROM vendors;

-- Intersect (common rows)
SELECT name FROM customers
INTERSECT
SELECT name FROM vendors;

-- Except (rows in first but not second)
SELECT name FROM customers
EXCEPT
SELECT name FROM vendors;
```

## PIVOT and UNPIVOT

Pivot rows into columns:

```sql
PIVOT sales
    SUM(revenue)
    FOR category IN ('Electronics', 'Clothing', 'Food');
```

Unpivot columns into rows:

```sql
UNPIVOT wide_table
    VALUE INTO measurement
    NAME INTO metric
    FROM (q1, q2, q3, q4);
```
