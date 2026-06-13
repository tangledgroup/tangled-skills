# SQL Fundamentals

## Contents
- CREATE TABLE
- INSERT
- SELECT
- UPDATE and DELETE
- COPY
- ATTACH and DETACH
- ALTER TABLE
- CREATE VIEW
- DROP
- DESCRIBE and SHOW

## CREATE TABLE

Create a table with explicit column types:

```sql
CREATE TABLE users (
    id INTEGER,
    name VARCHAR,
    created_at TIMESTAMP
);
```

Create from query results (CTAS):

```sql
CREATE TABLE active_users AS
SELECT * FROM 'users.csv' WHERE active = true;
```

Temporary tables (session-scoped, not persisted):

```sql
CREATE TEMP TABLE temp_results AS
SELECT name, COUNT(*) AS cnt FROM events GROUP BY name;
```

## INSERT

Insert single or multiple rows:

```sql
INSERT INTO users VALUES (1, 'Alice', CURRENT_TIMESTAMP);
INSERT INTO users VALUES (2, 'Bob', CURRENT_TIMESTAMP), (3, 'Carol', CURRENT_TIMESTAMP);
```

Insert from query:

```sql
INSERT INTO summary
SELECT name, COUNT(*) AS total FROM events GROUP BY name;
```

## SELECT

Standard SQL SELECT with DuckDB extensions:

```sql
SELECT name, AVG(score) AS avg_score
FROM 'students.csv'
WHERE score > 80
GROUP BY name
HAVING AVG(score) > 85
ORDER BY avg_score DESC
LIMIT 10;
```

DuckDB supports reading files directly in FROM clauses:

```sql
SELECT * FROM 'data.parquet';
SELECT * FROM read_csv_auto('data.csv');
SELECT * FROM read_json_array('data.json');
```

## UPDATE and DELETE

Update rows:

```sql
UPDATE users SET name = 'Alice Smith' WHERE id = 1;
```

Delete rows:

```sql
DELETE FROM users WHERE created_at < '2024-01-01';
```

> When updating nested types in tables with ART indexes (primary keys or unique constraints), DuckDB performs delete-then-insert, which can trigger constraint violations.

## COPY

Export data to files:

```sql
COPY (SELECT * FROM users WHERE active = true) TO 'active_users.csv' (HEADER true);
COPY events TO 'events.parquet' (COMPRESSION 'zstd');
```

Import data into tables:

```sql
COPY users FROM 'users.csv' (AUTO_DETECT true, HEADER true);
COPY events FROM 'events.parquet';
```

The Python API provides equivalent methods: `.write_csv()`, `.write_parquet()`.

## ATTACH and DETACH

Attach external DuckDB databases:

```sql
ATTACH 'other.db' AS other_db;
SELECT * FROM other_db.my_table;
DETACH other_db;
```

Attach with read-only access:

```sql
ATTACH 'readonly.db' (READ_ONLY);
```

## ALTER TABLE

Modify table structure:

```sql
ALTER TABLE users ADD COLUMN email VARCHAR;
ALTER TABLE users RENAME COLUMN name TO full_name;
ALTER TABLE users DROP COLUMN email;
```

Rename a table:

```sql
ALTER TABLE old_name RENAME TO new_name;
```

## CREATE VIEW

Create a named query:

```sql
CREATE VIEW user_summary AS
SELECT name, COUNT(*) AS event_count
FROM events
GROUP BY name;
```

Replace an existing view:

```sql
CREATE OR REPLACE VIEW user_summary AS
SELECT name, COUNT(*) AS event_count, MAX(ts) AS last_event
FROM events
GROUP BY name;
```

## DROP

Drop objects:

```sql
DROP TABLE users;
DROP VIEW IF EXISTS user_summary;
DROP SCHEMA IF EXISTS analytics CASCADE;
```

## DESCRIBE and SHOW

Inspect table structure:

```sql
DESCRIBE users;
```

List tables in current schema:

```sql
SHOW TABLES;
```

List all databases:

```sql
SHOW DATABASES;
```
