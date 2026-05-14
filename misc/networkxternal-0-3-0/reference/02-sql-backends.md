# SQL Backends

## BaseSQL

`BaseSQL` extends `BaseAPI` with SQLAlchemy-based implementation. It handles session management, ORM mapping, and SQL query generation shared by SQLite, PostgreSQL, and MySQL backends.

### ORM Models

Two declarative models map graph data to relational tables:

**NodeSQL** (table: `main_nodes`):
- `_id`: BigInteger, primary key
- `weight`: Float
- `label`: Integer
- `payload_json`: Text (JSON-encoded payload dict)

**EdgeSQL** (table: `main_edges`):
- `_id`: BigInteger, primary key
- `first`: BigInteger
- `second`: BigInteger
- `is_directed`: Boolean
- `weight`: Float
- `label`: Integer
- `payload_json`: Text (JSON-encoded payload dict)

**EdgeNewSQL** (table: `new_edges`): Temporary staging table for bulk imports, same schema as EdgeSQL.

Indexes are created on `first`, `second`, `label`, and `is_directed` columns of EdgeSQL.

### Constructor

```python
BaseSQL(url="sqlite:///:memory:", **kwargs)
```

Creates a SQLAlchemy engine from the URL, auto-creates the database if it doesn't exist (via `sqlalchemy_utils.create_database`), creates all tables, and sets up a session factory. Default is in-memory SQLite.

### Session Management

```python
@contextmanager
def get_session(self):
```

Context manager that yields a SQLAlchemy session with `expire_on_commit=False`. Commits on success, rolls back on exception, always closes the session. All database operations go through this context manager.

### Query Compilation

SQLAlchemy queries can be exported as raw SQL strings:
- `str(query)` — generic query string
- `str(query.statement.compile(dialect=postgresql.dialect()))` — dialect-specific SQL

### Performance Considerations

ORM mapping adds overhead. Benchmarking revealed ORM mapping takes 2x more time than `bulk_save_objects()` for in-memory SQLite. Using `bulk_insert_mappings()` reduced import time by 70%. Analytical queries implemented in SQL can be suboptimal and may create excessive temporary tables consuming memory.

## SQLite

### SQLiteMem

In-memory SQLite variant. Not concurrent (`__is_concurrent__ = False`). Batch size up to 5,000,000. Use for fast prototyping where persistence is not needed.

Default URL: `sqlite:///:memory:`

### SQLite (File-based)

File-based SQLite with performance optimizations. Not concurrent. Batch size up to 1,000,000.

SQLite can be the fastest option for tiny databases under 20 MB. However, write amplification is significant — bulk inserting a 250 MB unweighted undirected graph writes approximately 200 GB of data to disk, resulting in a ~1 GB file.

#### SQLite Pragmas (applied on first launch)

```python
PRAGMA page_size=4096;
PRAGMA cache_size=10000;
PRAGMA journal_mode=WAL;
PRAGMA locking_mode=EXCLUSIVE;
PRAGMA synchronous=ON;
PRAGMA temp_store=MEMORY;
PRAGMA optimize(0xfffe);
PRAGMA threads=8;
```

These pragmas optimize for write throughput with Write-Ahead Logging, exclusive locking, and increased cache. The pragmas are only applied when the database is empty (first launch detection via `number_of_edges() > 0`).

### Connection URLs

- In-memory: `sqlite:///:memory:`
- File-based: `sqlite:///path/to/graph.db`

## PostgreSQL

PostgreSQL backend extends `BaseSQL` with additional optimizations.

#### Pragmas (applied on first launch)

```python
SET synchronous_commit=0;
```

Disables synchronous commit for performance over reliability. Additional settings like `shared_buffers` and `wal_buffers` require database restart to take effect.

#### Upsert Support

PostgreSQL overrides `upsert_table()` with `ON CONFLICT DO UPDATE` syntax, providing proper upsert semantics during bulk import staging table migration:

```sql
INSERT INTO main_edges
SELECT * FROM new_edges
ON CONFLICT (_id) DO UPDATE SET
(first, second, weight, attributes_json) =
(EXCLUDED.first, EXCLUDED.second, EXCLUDED.weight, EXCLUDED.attributes_json);
```

#### Connection URL

Format: `postgresql://user:password@host:port/database`

Example: `postgresql://graph_user:secret@localhost:5432/graph_db`

### Planned Features (commented out in source)

- Bulk import via `sqlalchemy-postgres-copy` for COPY FROM STDIN
- Async operations through Gino ORM
- Native JSON sub-property querying via `sqlalchemy_utils.types.json`

## MySQL

MySQL backend extends `BaseSQL` with MySQL-specific tuning.

#### Pragmas (applied on first launch)

```python
SET GLOBAL local_infile=1;
SET GLOBAL innodb_file_per_table=1;
SET SESSION sql_mode=NO_AUTO_VALUE_ON_ZERO;
SET GLOBAL tmp_table_size=16777216;
SET GLOBAL max_heap_table_size=16777216;
```

These enable local file imports, per-table InnoDB files, prevent zero from being treated as auto-increment, and increase temporary table sizes.

#### Upsert Support

MySQL uses `REPLACE INTO` for the base `upsert_table()` implementation:

```sql
REPLACE INTO main_edges
SELECT * FROM new_edges;
```

### Connection URL

Format: `mysql+pymysql://user:password@host:port/database`

Example: `mysql+pymysql://graph_user:secret@localhost:3306/graph_db`

## Shared SQL Patterns

All SQL backends share these query patterns:

**Edge filtering by members** (`filter_edges_members`):
- Both `u` and `v` provided, directed graph: `WHERE first = u AND second = v`
- Both `u` and `v` provided, undirected graph: `WHERE (first = u AND second = v) OR (first = v AND second = u)`
- Only one endpoint: `WHERE first = u` or `WHERE second = v`
- Self-loop (`u == v`): `WHERE first = u OR second = u`

**Edge filtering by label** (`filter_edges_label`):
- `WHERE label = key` (skipped when key is None/negative)

**Bulk import flow**:
1. Insert data into `new_edges` staging table via `bulk_insert_mappings`
2. Migrate from staging to main table via `upsert_table()` or `insert_table()`
3. Clear staging table
4. Call `add_missing_nodes()` to register unregistered endpoints
