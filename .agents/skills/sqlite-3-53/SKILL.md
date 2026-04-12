---
name: sqlite-3-53
description: Complete toolkit for SQLite 3.53 database operations including SQL queries, C API integration, JSON/JSONB processing, full-text search with FTS5, virtual tables, and database administration. Use when building applications requiring embedded SQL databases, performing data analysis, implementing persistent storage, or working with SQLite's advanced features like JSON functions, window functions, and full-text search.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - sqlite
  - database
  - sql
  - json
  - fts
  - embedded-database
  - persistence
category: database
required_environment_variables: []
---

# SQLite 3.53

Comprehensive toolkit for SQLite 3.53, a self-contained, serverless, zero-configuration, transactional SQL database engine. This skill covers SQL language features, C API integration, JSON/JSONB processing, full-text search (FTS3/FTS5), virtual tables, and advanced database operations.

## When to Use

- Building applications requiring lightweight embedded databases
- Performing SQL queries and data manipulation
- Working with JSON data using SQLite's JSON1 extension
- Implementing full-text search with FTS5
- Creating custom virtual tables and loadable extensions
- Database administration and optimization
- Converting between JSON and relational data
- Using window functions and advanced SQL features
- Integrating SQLite via C API in applications

## Quick Start

### Basic Setup

SQLite requires no installation for command-line use. The `sqlite3` CLI tool is available on most systems:

```bash
# Install SQLite (if needed)
# Debian/Ubuntu
sudo apt install sqlite3 libsqlite3-dev

# macOS
brew install sqlite

# Create and open a database
sqlite3 mydatabase.db
```

### First Query

```sql
-- Create a table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');

-- Query data
SELECT * FROM users WHERE name LIKE '%li%';

-- Use JSON functions
SELECT json_object('id', id, 'name', name) AS user_json FROM users;
```

See [SQL Basics](references/01-sql-basics.md) for detailed SQL language coverage.

### JSON Processing

SQLite 3.53 includes comprehensive JSON support with both text and binary (JSONB) formats:

```sql
-- Store JSON data
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    data JSON
);

INSERT INTO products VALUES (1, '{"name": "Widget", "price": 9.99, "tags": ["gadget", "tool"]}');

-- Extract JSON values
SELECT json_extract(data, '$.name') AS name FROM products;
SELECT json_extract(data, '$.price') AS price FROM products;

-- Use PostgreSQL-style operators
SELECT data->'$.name' AS name FROM products;
SELECT data->>'$.name' AS name_text FROM products;

-- Work with binary JSON (JSONB) for better performance
SELECT jsonb(data) AS binary_json FROM products;
SELECT jsonb_extract(jsonb(data), '$.tags[0]') AS first_tag FROM products;
```

Refer to [JSON and JSONB Functions](references/04-json-jsonb.md) for complete JSON function reference.

### Full-Text Search

FTS5 provides powerful full-text search capabilities:

```sql
-- Enable FTS5 (built into SQLite 3.53)
CREATE VIRTUAL TABLE documents USING fts5(
    title,
    content,
    tokenize='unicode61'
);

-- Insert documents
INSERT INTO documents VALUES ('SQLite Guide', 'SQLite is a lightweight SQL database engine');
INSERT INTO documents VALUES ('JSON Support', 'SQLite provides JSON functions for data processing');

-- Search documents
SELECT * FROM documents WHERE documents MATCH 'SQLite AND database';
SELECT * FROM documents WHERE documents MATCH 'SQLite NEAR database';

-- Ranked search with snippets
SELECT rank, snippet(documents) AS excerpt, title 
FROM documents 
WHERE documents MATCH 'database'
ORDER BY rank;
```

See [Full-Text Search with FTS5](references/05-fts5.md) for comprehensive FTS5 documentation.

## Reference Files

This skill includes detailed reference files organized by topic:

### Core SQL and Database Operations

- [`references/01-sql-basics.md`](references/01-sql-basics.md) - SQL language fundamentals, data types, DDL statements, SELECT queries, joins, and subqueries
- [`references/02-c-api.md`](references/02-c-api.md) - C API integration including connection management, prepared statements, binding parameters, and result retrieval
- [`references/03-pragmas.md`](references/03-pragmas.md) - Configuration pragmas for database behavior, performance tuning, and SQLite customization

### Advanced Features

- [`references/04-json-jsonb.md`](references/04-json-jsonb.md) - Complete JSON and binary JSON (JSONB) function reference with examples for data extraction, modification, and validation
- [`references/05-fts5.md`](references/05-fts5.md) - Full-text search implementation using FTS5 including tokenizers, query syntax, ranking, and configuration
- [`references/06-virtual-tables.md`](references/06-virtual-tables.md) - Virtual table creation, loadable extensions, and custom module development

### Performance and Administration

- [`references/07-performance.md`](references/07-performance.md) - Query optimization, indexing strategies, EXPLAIN analysis, and performance tuning techniques
- [`references/08-administration.md`](references/08-administration.md) - Database maintenance, backup/recovery, WAL mode, integrity checking, and security considerations

### SQL Functions and Features

- [`references/09-sql-functions.md`](references/09-sql-functions.md) - Built-in SQL functions including aggregate, mathematical, string, date/time, and window functions
- [`references/10-advanced-sql.md`](references/10-advanced-sql.md) - Advanced SQL features: CTEs, recursive queries, triggers, views, and window functions

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/sqlite-3-53/`). All paths are relative to this directory.

## Common Operations

### Database Backup and Restore

```sql
-- Create an online backup
BACKUP TO 'backup.db' FROM main;

-- Or using the CLI
sqlite3 source.db ".backup 'backup.db'"

-- Restore from backup (replace database)
sqlite3 target.db ".restore 'backup.db'"
```

### Import/Export Data

```bash
# Export to CSV
sqlite3 database.db -header -csv "SELECT * FROM users" > users.csv

# Import from CSV
sqlite3 database.db ".mode csv" ".import users.csv users"

# Export entire database schema
sqlite3 database.db ".schema" > schema.sql

# Export data as SQL INSERT statements
sqlite3 database.db ".dump" > full_backup.sql
```

### Working with Multiple Databases

```sql
-- Attach additional databases
ATTACH DATABASE 'analytics.db' AS analytics;
ATTACH DATABASE 'cache.db' AS cache;

-- Query across databases
SELECT u.name, a.page_views 
FROM main.users u
JOIN analytics.pages a ON u.id = a.user_id;

-- Copy data between databases
INSERT INTO analytics.users SELECT * FROM main.users;

-- Detach when done
DETACH DATABASE analytics;
```

### Using Window Functions

```sql
-- Running total
SELECT 
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date) AS running_total
FROM sales;

-- Ranking within groups
SELECT 
    department,
    employee,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;

-- Moving average
SELECT 
    date,
    value,
    AVG(value) OVER (
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3
FROM metrics;
```

## Troubleshooting

### Common Issues

**Database is locked:**
- Check for uncommitted transactions: `SELECT * FROM sqlite_master WHERE type='table';`
- Use `.timeout 5000` in CLI to wait for locks
- Enable WAL mode for better concurrency: `PRAGMA journal_mode=WAL;`

**JSON parsing errors:**
- Validate JSON first: `SELECT json_valid(your_column);`
- Check error position: `SELECT json_error_position(your_column);`
- Ensure proper escaping of special characters

**FTS5 search not working:**
- Verify FTS5 is compiled in: `SELECT sqlite_version();`
- Check for typos in MATCH queries
- Use `MATCH 'term*'` for prefix searches
- Rebuild index if corrupted: `INSERT INTO documents(documents) VALUES('reindex');`

**Query performance issues:**
- Use `EXPLAIN QUERY PLAN` to analyze query execution
- Add appropriate indexes on frequently queried columns
- Avoid SELECT * in production queries
- Consider covering indexes for frequent query patterns

### Getting Help

```bash
# Check SQLite version and compile options
sqlite3 "SELECT sqlite_version(), sqlite_compileoption_used('ENABLE_FTS5');"

# List available commands in CLI
sqlite3 ".help"

# Check database integrity
sqlite3 database.db "PRAGMA integrity_check;"

# View query execution plan
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';
```

See [Administration and Maintenance](references/08-administration.md) for detailed troubleshooting guidance.

## Best Practices

1. **Use prepared statements** - Always use parameterized queries to prevent SQL injection
2. **Enable WAL mode** - For better concurrency in multi-reader applications: `PRAGMA journal_mode=WAL;`
3. **Add indexes strategically** - Index columns used in WHERE, JOIN, and ORDER BY clauses
4. **Use JSONB for frequent updates** - Binary JSON format is more efficient for repeated modifications
5. **Regular integrity checks** - Run `PRAGMA integrity_check;` periodically on production databases
6. **Backup before schema changes** - Always backup before ALTER TABLE or major modifications
7. **Use transactions for bulk operations** - Wrap multiple inserts/updates in BEGIN...COMMIT blocks
8. **Limit result sets** - Use LIMIT clauses to prevent accidentally loading all data

## Performance Tips

- Set `PRAGMA cache_size` appropriately for your workload (negative value = KB of cache)
- Use `PRAGMA synchronous=NORMAL` for better performance with acceptable safety
- Enable `PRAGMA temp_store=MEMORY` for faster temporary table operations
- Consider `PRAGMA mmap_size` for memory-mapped I/O on large databases
- Use FTS5 instead of LIKE for text search on large datasets

## Limitations

- Maximum database size: ~140 Terabytes (theoretical)
- Maximum row size: ~2GB
- Maximum number of columns per table: 32,766
- Connection limits depend on application implementation
- Some features require compile-time enablement (check with `PRAGMA compile_options;`)

For complete documentation, see the [SQLite Documentation](https://sqlite.org/docs.html).
