# Database Backends

## SQLite

**Best for**: Tiny databases under 20 MB, embedded single-file storage.

SQLite is the fastest option for small graphs but has huge write amplification — bulk inserting a 250 MB unweighted undirected graph writes ~200 GB to disk with a final file size of ~1 GB.

### Performance Pragmas

On first launch (when edge count is 0), SQLite applies these pragmas:

- `page_size=4096` — larger pages reduce I/O overhead
- `cache_size=10000` — increase page cache
- `journal_mode=WAL` — Write-Ahead Logging for better concurrency
- `locking_mode=EXCLUSIVE` — reduce filesystem system calls
- `synchronous=ON` — balance between speed and safety
- `temp_store=MEMORY` — temp tables in RAM
- `optimize(0xfffe)` — allow automatic query optimization
- `threads=8` — up to 8 auxiliary threads for queries

### Classes

- `SQLite(url)` — file-based SQLite. Requires URL like `sqlite:///path/to/db.db`.
- `SQLiteMem()` — in-memory SQLite. No persistence across sessions. Not concurrent.

Both set `__max_batch_size__` to 1,000,000 (SQLite) or 5,000,000 (in-memory).

## PostgreSQL

**Best for**: Feature-rich relational storage with optimized upserts.

PostgreSQL extends BaseSQL with `ON CONFLICT DO UPDATE` for efficient upsert operations during bulk imports. Uses `synchronous_commit=0` on first launch for performance over reliability.

### Connection URL Format

```
postgresql://user:password@host:port/database_name
```

### Bulk Import Strategy

PostgreSQL supports the `upsert_table()` method using `INSERT ... ON CONFLICT (_id) DO UPDATE SET`, which atomically handles both inserts and updates in a single statement. This is more reliable than the INSERT-then-DELETE pattern used by other backends.

### Future Support

Planned but not yet implemented:
- `upsert_bulk_from_path()` — COPY-based bulk import from CSV files using `sqlalchemy-postgres-copy`
- Async operations via Gino ORM (PostgreSQL-only async framework)
- Native JSON sub-property querying via `sqlalchemy_utils.types.json`

## MySQL

**Best for**: Widely-deployed relational infrastructure.

MySQL extends BaseSQL with session-level tuning on first launch:

- `local_infile=1` — allow direct CSV imports
- `innodb_file_per_table=1` — separate tablespace files
- `sql_mode=NO_AUTO_VALUE_ON_ZERO` — prevent auto-increment from using 0 as ID
- `tmp_table_size=16MB` and `max_heap_table_size=16MB` — larger temp tables

### Connection URL Format

```
mysql://user:password@host:port/database_name
```

### Bulk Import

CSV import via `LOAD DATA LOCAL INFILE` is planned but not yet implemented. Requires the file to be mounted on the same filesystem as the MySQL server.

## MongoDB

**Best for**: Distributed document storage, horizontal scaling.

MongoDB implements BaseAPI directly (not through BaseSQL). Uses aggregation pipelines for edge queries and `bulk_write()` with `UpdateOne` operations for upserts.

### Connection URL Format

```
mongodb://localhost:27017/graph
```

The database name is extracted from the URL path (defaults to `graph`).

### Batch Limits

MongoDB batch size is capped at 10,000 documents. Beyond this point there's minimal improvement. The write command batch limit is documented at 100,000 elements, but not every document fits in RAM at that scale.

### Indexes

On initialization, sparse indexes are created on `first`, `second`, and `is_directed` fields of the edges collection.

## Neo4J

**Best for**: Native graph queries with Cypher DSL.

Neo4J implements BaseAPI directly using the Bolt protocol and Cypher queries. Note significant caveats (see [Neo4J Implementation](reference/04-neo4j-implementation.md)).

### Connection URL Format

```
bolt://username:password@localhost:7687/graph
```

The last character of the database name is used as a label suffix to distinguish disjoint datasets within the same Neo4J instance.

### Batch Limits

Batch size is limited to 1,000 edges due to Java heap space constraints on typical hardware. Importing a 30 MB CSV file allocated 1.4 GB of RAM in benchmarks.
