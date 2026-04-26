# Transactions and Concurrency

## Transaction Basics

SQLite implements serializable transactions by actually serializing writes. There can only be one writer at a time, but multiple readers can operate concurrently (especially in WAL mode).

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

Transaction statements:
- `BEGIN` or `BEGIN TRANSACTION` — Start a transaction
- `BEGIN DEFERRED` — Acquire locks only when needed (default)
- `BEGIN IMMEDIATE` — Acquire a RESERVED lock immediately
- `BEGIN EXCLUSIVE` — Acquire an EXCLUSIVE lock immediately
- `COMMIT` or `END` — Commit the transaction
- `ROLLBACK` — Abort and undo all changes

## Savepoints

Nested transactions via savepoints:

```sql
BEGIN;
INSERT INTO t1 VALUES(1);
SAVEPOINT sp1;
INSERT INTO t1 VALUES(2);
SAVEPOINT sp2;
INSERT INTO t1 VALUES(3);
ROLLBACK TO sp2;  -- Undoes only the INSERT of 3
INSERT INTO t1 VALUES(4);
RELEASE sp1;     -- Commits the INSERT of 2 and 4
COMMIT;          -- Commits everything including the INSERT of 1
```

- `SAVEPOINT name` — Create a savepoint
- `RELEASE SAVEPOINT name` — Commit changes since the savepoint
- `ROLLBACK TO SAVEPOINT name` — Undo changes since the savepoint

## Write-Ahead Logging (WAL)

WAL mode is activated with `PRAGMA journal_mode=WAL`. It offers significant advantages over the default rollback journal:

- **Faster** — WAL is significantly faster in most scenarios
- **More concurrent** — Readers do not block writers, and a writer does not block readers
- **Sequential I/O** — Disk operations tend to be more sequential
- **Fewer fsync() calls** — Less vulnerable to systems with broken fsync

Disadvantages:
- All processes must be on the same host (does not work over network filesystems)
- WAL requires shared memory for the wal-index
- The database file size never decreases automatically (requires `VACUUM` or checkpoint)
- On very small databases, rollback journal may be faster

### How WAL Works

Instead of modifying the database file directly, changes are appended to a separate write-ahead log file (`database-name-wal`). A separate shared-memory file (`database-name-shm`) tracks which pages are in the WAL. Periodically, a checkpoint operation copies WAL content back into the main database file.

### Checkpointing

```sql
-- Manual checkpoint
PRAGMA wal_checkpoint(TRUNCATE);

-- Returns: 0=success, 1=busy, 2=nothing to do
```

Checkpoint modes:
- `PASSIVE` — Checkpoint as many tables as possible without waiting
- `FULL` — Wait for readers, then checkpoint all tables
- `RESTART` — Like FULL but restarts writers after checkpointing
- `TRUNCATE` — Like FULL but also truncates the WAL file afterward

Automatic checkpointing occurs when the WAL file reaches 1000 pages (configurable via `PRAGMA wal_autocheckpoint=N`).

## Isolation Levels

SQLite provides **serializable** isolation by default. Changes made by one database connection are invisible to other connections until committed. This is true regardless of whether connections are in the same thread, different threads, or different processes.

The only exception is when shared cache mode is enabled AND `PRAGMA read_uncommitted = ON` — then a reader can see uncommitted changes from another connection sharing the same cache. This combination should be used with extreme caution.

## Locking

SQLite uses file-level locks:

- **UNLOCKED** — No lock held
- **PENDING** — Writer is waiting for readers to finish
- **SHARED** — Reader holds this lock; multiple readers can hold it simultaneously
- **RESERVED** — Writer has acquired this lock but has not started writing
- **EXCLUSIVE** — Writer has exclusive access

In WAL mode, the locking protocol is different. Readers acquire a shared lock on the wal-index (via shared memory), and writers append to the WAL file without blocking readers.

## Concurrency Patterns

### Handling SQLITE_BUSY

When `sqlite3_step()` or `sqlite3_exec()` returns `SQLITE_BUSY`, the database is locked by another connection. Strategies:

1. **Retry with delay** — Loop with exponential backoff
2. **Busy timeout** — Set a timeout so SQLite retries automatically:
   ```c
   sqlite3_busy_timeout(db, 5000);  // Wait up to 5 seconds
   ```
3. **Busy handler** — Register a callback:
   ```c
   sqlite3_busy_handler(db, myHandler, (void*)userData);
   ```

### Connection Pooling

For high-concurrency applications:
- Use WAL mode for maximum reader/writer concurrency
- Open one connection per thread
- Use prepared statements with bound parameters
- Keep transactions short to minimize lock contention

## Memory-Mapped I/O

Enable memory-mapped I/O for improved read performance:

```sql
PRAGMA mmap_size = 268435456;  -- 256 MB
```

This allows SQLite to use `mmap()` system calls to access database pages directly from the OS page cache. Default is typically 0 (disabled) or a small value.

## URI Filenames

URI mode enables special options in the filename:

```c
sqlite3_open("file:/path/to/db.db?mode=ro&nolock=1&nomutex=1", &db);
```

Options:
- `mode=ro|rw|rwc` — Read-only, read-write, or read-write-create
- `cache=shared|private` — Shared or private page cache
- `nolock=1` — Do not use file locks
- `nomutex=1` — Disable mutexes
- `immutable=1` — Database will never change
- `lockfile=0` — Do not use a separate lock file
