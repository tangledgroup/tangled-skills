# SQL Language Reference

## Statement Types

SQLite supports most standard SQL statement types. Multiple statements can be passed as a semicolon-separated list to `sqlite3_exec()`, `sqlite3_prepare_v2()`, and the CLI.

**Data Definition:**
- `CREATE TABLE` — Create a new table
- `CREATE INDEX` — Create an index on a table
- `CREATE VIEW` — Create a virtual table view
- `CREATE TRIGGER` — Create a trigger
- `CREATE VIRTUAL TABLE` — Create a virtual table (FTS5, R-Tree, etc.)
- `ALTER TABLE` — Rename tables or add columns
- `DROP TABLE`, `DROP INDEX`, `DROP VIEW`, `DROP TRIGGER`
- `PRAGMA` — SQLite-specific configuration queries

**Data Manipulation:**
- `SELECT` — Query data
- `INSERT` — Add rows
- `UPDATE` — Modify existing rows
- `DELETE` — Remove rows
- `REPLACE` — Delete then insert (shortcut for UPSERT)

**Transaction Control:**
- `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK`
- `SAVEPOINT` / `RELEASE SAVEPOINT` / `ROLLBACK TO SAVEPOINT`

**Schema and Utility:**
- `ATTACH DATABASE` / `DETACH DATABASE`
- `ANALYZE` — Collect table statistics for the query planner
- `REINDEX` — Rebuild indexes
- `VACUUM` — Rebuild the entire database to reclaim space

## CREATE TABLE

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Key options:
- `INTEGER PRIMARY KEY` — Aliases the rowid; auto-increments on INSERT of NULL
- `AUTOINCREMENT` — Guarantees monotonically increasing rowids (use only when strictly necessary, adds overhead)
- `NOT NULL` — Column cannot contain NULL
- `UNIQUE` — Values must be unique across all rows
- `CHECK(expr)` — Enforces a constraint expression
- `DEFAULT value` — Default value when column is omitted in INSERT
- `REFERENCES table(column)` — Foreign key declaration (enforced only when `PRAGMA foreign_keys = ON`)

### STRICT Tables

Add the `STRICT` keyword to enforce rigid type checking:

```sql
CREATE TABLE strict_example (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
) STRICT;
```

In a STRICT table, inserting a TEXT value into an INTEGER column raises an error. This behavior matches traditional SQL databases.

### WITHOUT ROWID Tables

Omit the implicit rowid column using a clustered index:

```sql
CREATE TABLE events (
    event_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    data TEXT,
    PRIMARY KEY(event_id, timestamp)
) WITHOUT ROWID;
```

Benefits: Smaller storage for wide tables with composite primary keys, faster range queries on the primary key. Requires an explicit PRIMARY KEY with all columns NOT NULL.

## INSERT and UPSERT

```sql
-- Basic insert
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Multi-row insert
INSERT INTO users (name, email) VALUES
    ('Bob', 'bob@example.com'),
    ('Carol', 'carol@example.com');

-- Insert from query
INSERT INTO archive SELECT * FROM users WHERE created_at < '2024-01-01';

-- UPSERT: insert or update on conflict
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice Updated')
ON CONFLICT(email) DO UPDATE SET name = excluded.name;
```

The `excluded` table refers to the row that would have been inserted. UPSERT uses the `ON CONFLICT` clause with either `DO NOTHING` or `DO UPDATE SET ...`.

## UPDATE and DELETE

Both support `RETURNING`, `WHERE`, and `ORDER BY`/`LIMIT`:

```sql
-- Update with returning
UPDATE users SET name = 'Alice Smith' WHERE email = 'alice@example.com'
RETURNING id, name;

-- Delete oldest rows first, limited
DELETE FROM logs WHERE level = 'DEBUG'
ORDER BY created_at ASC LIMIT 1000;
```

## SELECT

SQLite supports a comprehensive SELECT syntax:

```sql
SELECT columns
FROM tables
WHERE conditions
GROUP BY grouping_columns
HAVING group_conditions
ORDER BY sort_columns
LIMIT count OFFSET offset;
```

**Compound SELECTs:** Combine queries with `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`.

**Common Table Expressions (WITH clause):**

```sql
WITH monthly_revenue AS (
    SELECT strftime('%Y-%m', order_date) AS month,
           SUM(amount) AS revenue
    FROM orders
    GROUP BY month
)
SELECT month, revenue,
       AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM monthly_revenue;
```

## RETURNING Clause

Available on INSERT, UPDATE, and DELETE to return the affected rows:

```sql
INSERT INTO products (name, price) VALUES ('Widget', 9.99)
RETURNING id, name, price;

UPDATE products SET price = price * 0.9 WHERE category = 'sale'
RETURNING id, name, old_price, price AS new_price;
```

## Indexes

```sql
-- Simple index
CREATE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_orders_date_status ON orders(date, status);

-- Partial index (only indexes rows matching a condition)
CREATE INDEX idx_active_users ON users(email) WHERE active = 1;

-- Expression index
CREATE INDEX idx_lower_name ON users(LOWER(name));
```

## Generated Columns

Columns computed from other columns:

```sql
CREATE TABLE products (
    price REAL NOT NULL,
    tax_rate REAL NOT NULL DEFAULT 0.1,
    total AS (price * (1.0 + tax_rate)) STORED
);
```

Generated columns can be `STORED` (physically stored) or `VIRTUAL` (computed on read). Stored columns can be indexed.

## Row Values

SQLite supports tuple comparisons:

```sql
SELECT * FROM events
WHERE (start_date, end_date) OVERLAPS ('2024-01-01', '2024-06-30');
```

Row values enable compound key comparisons and range overlap checks.

## Collating Sequences

Control text comparison order:

- `BINARY` — Compare by UTF-8 codepoint values (default)
- `NOCASE` — Case-insensitive comparison
- `RTRIM` — Ignore trailing spaces

Custom collations can be registered via the C API with `sqlite3_create_collation()`.
