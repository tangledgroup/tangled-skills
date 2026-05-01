# SQL Architecture

## Class Hierarchy

```
BaseAPI (abstract)
  └── BaseSQL (SQLAlchemy-based)
        ├── SQLite
        ├── SQLiteMem
        ├── PostgreSQL
        └── MySQL
```

`BaseSQL` provides the shared implementation for all relational database backends using SQLAlchemy ORM. Backend-specific classes override initialization pragmas and upsert strategies.

## ORM Models

### NodeSQL

Extends both `DeclarativeSQL` (SQLAlchemy declarative base) and `Node` (dataclass). Stored in table `main_nodes`:

- `_id` — BigInteger, primary key
- `weight` — Float
- `label` — Integer
- `payload_json` — Text (JSON-encoded dict of extra attributes)

### EdgeSQL

Extends both `DeclarativeSQL` and `Edge`. Stored in table `main_edges`:

- `_id` — BigInteger, primary key
- `first` — BigInteger (source node ID)
- `second` — BigInteger (target node ID)
- `is_directed` — Boolean
- `weight` — Float
- `label` — Integer
- `payload_json` — Text (JSON-encoded dict of extra attributes)

Indexes are defined on `first`, `second`, `label`, and `is_directed` columns.

### EdgeNewSQL

Temporary staging table `new_edges` with the same schema as `EdgeSQL`. Used for bulk imports — data is inserted into `new_edges` first, then migrated to `main_edges` via SQL-level operations.

## Bulk Import Pattern

The `add_stream()` method in BaseSQL supports two modes:

**Upsert mode** (`upsert=True`): Uses the parent `BaseAPI.add_stream()` which calls `add()` per chunk with individual upsert logic.

**Insert-only mode** (`upsert=False`): Inserts chunks into `EdgeNewSQL` (the staging table), then runs a dialect-specific migration query to merge into `EdgeSQL`, then clears the staging table, then calls `add_missing_nodes()`.

The migration is handled by `upsert_table()` which is abstract in BaseSQL and implemented per-dialect:

- **PostgreSQL**: `INSERT INTO main_edges SELECT * FROM new_edges ON CONFLICT (_id) DO UPDATE SET ...`
- **MySQL/BaseSQL default**: `REPLACE INTO main_edges SELECT * FROM new_edges`
- **SQLite**: Inherits the `REPLACE INTO` pattern from BaseSQL

## Session Management

BaseSQL uses a context manager `get_session()` that:

1. Creates a session bound to the engine
2. Sets `expire_on_commit = False` to avoid lazy-load errors after commit
3. Commits on success
4. Rolls back and re-raises on exception
5. Always closes the session in the finally block

## Query Filtering

Edge queries use helper methods for building filters:

- `filter_edges_containing(q, n)` — edges where `first == n OR second == n`
- `filter_edges_members(q, u, v)` — edges between specific nodes (respects directed/undirected flag)
- `filter_edges_label(q, key)` — edges matching a label

The `-1` sentinel value means "any" for node IDs and labels. When both `u` and `v` are -1, no filter is applied. For undirected graphs with two distinct nodes, the query matches `(first=u AND second=v) OR (first=v AND second=u)`.

## Performance Notes

ORM mapping can be costly. Benchmarking revealed that ORM mapping takes 2x more time than `bulk_save_objects()` for in-memory SQLite. Replacing it with `bulk_insert_mappings()` reduced import time by 70%.

Analytical queries are suboptimal — implementing them in SQL dialects is troublesome and often results in excessive memory consumption from temporary tables.

Queries can be exported without execution using `str(query)`, or compiled for a specific dialect:

```python
str(query.statement.compile(dialect=postgresql.dialect()))
```
