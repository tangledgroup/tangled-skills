# Transactions and Isolation Levels

Comprehensive guide to transaction management, isolation levels, and concurrency control in SQLite 3.53.

## Transaction Basics

SQLite supports full ACID compliance with proper transaction handling.

### Explicit Transactions

```sql
-- Begin a transaction
BEGIN TRANSACTION;

-- Multiple SQL statements
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;

-- Commit to make changes permanent
COMMIT;

-- Or rollback to undo all changes
ROLLBACK;
```

### Transaction Types

```sql
-- Default transaction (DEFERRED)
BEGIN;
BEGIN TRANSACTION;
BEGIN DEFERRED TRANSACTION;

-- Immediate transaction (locks database immediately)
BEGIN IMMEDIATE;

-- Exclusive transaction (locks with exclusive access)
BEGIN EXCLUSIVE;
```

### Transaction Type Comparison

| Type | Lock Timing | Lock Type | Use Case |
|------|-------------|-----------|----------|
| DEFERRED | First read/write | Shared | Default, read-heavy workloads |
| IMMEDIATE | At BEGIN | Reserved | Write transactions, prevent conflicts |
| EXCLUSIVE | At BEGIN | Exclusive | Full database modifications |

### Deferred Transactions (Default)

```sql
BEGIN DEFERRED TRANSACTION;

-- No lock acquired yet
SELECT * FROM users;  -- Shared lock acquired here

-- Lock upgrade on first write
INSERT INTO users VALUES (1, 'Alice');  -- Upgrades to reserved lock

COMMIT;
```

**Characteristics:**
- No lock until first database access
- Can fail with "database is locked" on first write if another transaction holds lock
- Best for read-mostly transactions

### Immediate Transactions

```sql
BEGIN IMMEDIATE TRANSACTION;

-- Reserved lock acquired immediately
-- Prevents other writers from starting

INSERT INTO users VALUES (1, 'Alice');
INSERT INTO users VALUES (2, 'Bob');

COMMIT;  -- Other readers can still read
```

**Characteristics:**
- Acquires reserved lock at BEGIN
- Prevents other writers from starting transactions
- Readers can still read during transaction
- Best for write transactions that should avoid conflicts

### Exclusive Transactions

```sql
BEGIN EXCLUSIVE TRANSACTION;

-- Exclusive lock acquired immediately
-- No other readers or writers

DELETE FROM users;
DROP TABLE temp_data;
CREATE INDEX idx_name ON users(name);

COMMIT;  -- Releases all locks
```

**Characteristics:**
- Acquires exclusive lock at BEGIN
- Blocks all other connections (readers and writers)
- Best for schema changes or bulk operations

## Savepoints

Savepoints allow partial rollbacks within a transaction.

### Basic Savepoint Usage

```sql
BEGIN TRANSACTION;

-- First operation
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Create savepoint
SAVEPOINT sp1;

-- More operations
INSERT INTO orders (user_id, total) VALUES (1, 99.99);
INSERT INTO orders (user_id, total) VALUES (1, 149.99);

-- Rollback to savepoint (keeps first insert)
ROLLBACK TO SAVEPOINT sp1;

-- Continue with different operations
INSERT INTO orders (user_id, total) VALUES (1, 49.99);

-- Release savepoint
RELEASE SAVEPOINT sp1;

COMMIT;  -- Commits user insert and single order
```

### Nested Savepoints

```sql
BEGIN TRANSACTION;

SAVEPOINT level1;
INSERT INTO logs (message) VALUES ('Level 1');

SAVEPOINT level2;
INSERT INTO logs (message) VALUES ('Level 2');

SAVEPOINT level3;
INSERT INTO logs (message) VALUES ('Level 3');

-- Rollback to middle level
ROLLBACK TO SAVEPOINT level2;

-- Level 3 insert is undone, levels 1 and 2 remain
RELEASE SAVEPOINT level2;
RELEASE SAVEPOINT level1;

COMMIT;
```

### Savepoint Error Handling

```sql
BEGIN TRANSACTION;

SAVEPOINT safe_point;

-- Risky operation
INSERT INTO critical_data SELECT * FROM unvalidated_source;

-- If error detected, rollback to savepoint
-- In application code, check for errors and execute:
ROLLBACK TO SAVEPOINT safe_point;

-- Continue with safe defaults
INSERT INTO critical_data VALUES (default_values);

RELEASE SAVEPOINT safe_point;
COMMIT;
```

## Isolation Levels

SQLite supports multiple isolation levels through PRAGMA settings.

### Default Isolation: READ COMMITTED

```sql
PRAGMA journal_mode = WAL;  -- Required for proper isolation

-- Transaction A
BEGIN;
SELECT balance FROM accounts WHERE user_id = 1;  -- Reads committed value
COMMIT;

-- Transaction B (concurrent)
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
COMMIT;

-- Transaction A's next read sees Transaction B's changes
```

**Characteristics:**
- Can only read data committed before query started
- Prevents dirty reads (reading uncommitted data)
- Allows non-repeatable reads (same query can return different results)
- Allows phantom reads (new rows can appear)

### Serializable Isolation

```sql
PRAGMA isolation_level = SERIALIZABLE;

-- Or use IMMEDIATE/EXCLUSIVE transactions
BEGIN IMMEDIATE;

SELECT balance FROM accounts WHERE user_id = 1;
-- Snapshot taken at transaction start
-- Will see same values until commit

UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
COMMIT;
```

**Characteristics:**
- Strictest isolation level
- Prevents dirty reads, non-repeatable reads, and phantom reads
- Transactions appear to execute serially
- Higher chance of conflicts requiring rollback

### Read Uncommitted (Not Directly Supported)

SQLite does not support true READ UNCOMMITTED. All reads see only committed data.

## Concurrency Control

### Locking Modes

```sql
-- Shared lock (readers)
SELECT * FROM users;  -- Multiple readers can hold shared locks

-- Reserved lock (writer, allows readers)
BEGIN IMMEDIATE;
INSERT INTO users VALUES (1, 'Alice');

-- Exclusive lock (single writer, no readers)
BEGIN EXCLUSIVE;
DELETE FROM users;
```

### Lock Timeout

```sql
-- Set timeout in milliseconds
PRAGMA busy_timeout = 5000;  -- Wait up to 5 seconds for lock

-- In CLI
.timeout 5000

-- In application code (C API)
sqlite3_busy_timeout(db, 5000);
```

### Handling Lock Conflicts

```sql
-- Strategy 1: Use busy_timeout
PRAGMA busy_timeout = 5000;

BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;  -- Will wait up to 5 seconds for lock

-- Strategy 2: Retry on conflict
-- In application code:
try {
    BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    COMMIT;
} catch (LockException) {
    sleep(random(10, 100));  // Exponential backoff
    retry();
}

-- Strategy 3: Use IMMEDIATE transactions
BEGIN IMMEDIATE;
-- Fails fast if lock not available
COMMIT;
```

## Write-Ahead Logging (WAL) and Concurrency

WAL mode significantly improves concurrency.

### Enabling WAL Mode

```sql
PRAGMA journal_mode = WAL;
```

### WAL Concurrency Benefits

```sql
-- Connection 1: Long-running read
BEGIN;
SELECT * FROM large_table;  -- Holds shared lock

-- Connection 2: Can still write (in WAL mode)
BEGIN;
INSERT INTO users VALUES (2, 'Bob');
COMMIT;  -- Commits successfully, reader continues

-- Connection 3: Another writer
BEGIN;
UPDATE accounts SET balance = 100 WHERE id = 1;
COMMIT;

-- Connection 1 completes read
COMMIT;  -- Sees all committed changes
```

**WAL Advantages:**
- Multiple readers and one writer concurrently
- Writers don't block readers
- Readers don't block writers (except during checkpoint)
- Better performance for mixed workloads

### Checkpoint Management

```sql
-- Passive checkpoint (default, during normal operations)
PRAGMA wal_autocheckpoint = 1000;  -- Every 1000 pages

-- Full checkpoint (synchronous, blocks writers)
PRAGMA wal_checkpoint(FULL);

-- Restart checkpoint (returns when WAL can be truncated)
PRAGMA wal_checkpoint(RESTART);

-- Truncate checkpoint (attempts to truncate WAL file)
PRAGMA wal_checkpoint(TRUNCATE);
```

## Transaction Best Practices

### Keep Transactions Short

```sql
-- GOOD: Short transaction
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
INSERT INTO transactions (from_id, to_id, amount) VALUES (1, 2, 100);
COMMIT;

-- BAD: Long transaction with external I/O
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Don't do this:
send_email_confirmation();  -- Slow external call
process_payment_gateway();   -- More external I/O
COMMIT;  -- Lock held too long
```

### Use Appropriate Transaction Type

```sql
-- Read-only query: use default DEFERRED
SELECT * FROM users WHERE id = 1;

-- Single write: use IMMEDIATE to prevent conflicts
BEGIN IMMEDIATE;
INSERT INTO audit_log (action, timestamp) VALUES ('login', datetime('now'));
COMMIT;

-- Schema changes: use EXCLUSIVE
BEGIN EXCLUSIVE;
ALTER TABLE users ADD COLUMN phone TEXT;
CREATE INDEX idx_phone ON users(phone);
COMMIT;
```

### Handle Errors Properly

```sql
-- Use savepoints for complex operations
BEGIN;

SAVEPOINT op1;
INSERT INTO orders (user_id, total) VALUES (1, 99.99);

SAVEPOINT op2;
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES (last_insert_rowid(), 42, 2);

-- If error detected:
ROLLBACK TO SAVEPOINT op2;  -- Undo last insert only
-- Or:
ROLLBACK;  -- Undo entire transaction

COMMIT;
```

### Avoid Holding Locks Unnecessarily

```sql
-- BAD: Select outside transaction when not needed
SELECT * FROM config WHERE key = 'max_size';
BEGIN;
-- Use value from earlier SELECT (might be stale)
INSERT INTO uploads (size) VALUES (1024);
COMMIT;

-- GOOD: Read within same transaction
BEGIN;
SELECT max_size FROM config WHERE key = 'max_size';
INSERT INTO uploads (size) VALUES (1024);
COMMIT;
```

## Deadlock Prevention

SQLite's locking protocol prevents most deadlocks, but be aware:

```sql
-- Potential deadlock scenario (avoid this pattern):

-- Connection 1
BEGIN;
UPDATE table_a SET x = 1 WHERE id = 1;  -- Locks row A
-- Connection 2 starts here
UPDATE table_b SET y = 2 WHERE id = 2;  -- Locks row B
COMMIT;

-- Connection 2
BEGIN;
UPDATE table_b SET y = 2 WHERE id = 2;  -- Locks row B
UPDATE table_a SET x = 1 WHERE id = 1;  -- Waits for row A (deadlock!)
COMMIT;

-- Prevention: Always access tables in same order
-- Or use IMMEDIATE transactions to fail fast
```

## Practical Patterns

### Transfer Money (Classic Transaction)

```sql
BEGIN IMMEDIATE;

-- Deduct from sender
UPDATE accounts SET balance = balance - :amount 
WHERE user_id = :from_user;

-- Verify deduction happened
SELECT COUNT(*) FROM sqlite_master WHERE COUNT(*) = 1;

-- Add to recipient
UPDATE accounts SET balance = balance + :amount 
WHERE user_id = :to_user;

-- Record transaction
INSERT INTO transactions (from_user, to_user, amount, timestamp)
VALUES (:from_user, :to_user, :amount, datetime('now'));

-- Verify balances are consistent
SELECT SUM(balance) FROM accounts;

COMMIT;
```

### Bulk Insert with Transaction

```sql
BEGIN IMMEDIATE;

INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');
INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com');
-- ... 1000 more inserts ...

COMMIT;  -- All or nothing, much faster than individual inserts
```

### Read-Write-Verify Pattern

```sql
BEGIN IMMEDIATE;

-- Read current value
SELECT balance INTO :current_balance FROM accounts WHERE user_id = 1;

-- Verify constraints
-- (In application code: check if current_balance >= amount)

-- Update
UPDATE accounts SET balance = balance - :amount WHERE user_id = 1;

-- Verify update
SELECT balance FROM accounts WHERE user_id = 1;

COMMIT;
```

### Optimistic Locking Pattern

```sql
BEGIN;

-- Read with version
SELECT data, version FROM config WHERE key = 'settings';

-- Application modifies data...

-- Update with version check
UPDATE config 
SET data = :new_data, version = version + 1
WHERE key = 'settings' AND version = :original_version;

-- Check if update affected a row
SELECT changes();  -- 0 means conflict, another transaction modified it

COMMIT;
```

## Related Documentation

- [Pragmas](03-pragmas.md) - journal_mode and WAL configuration
- [CLI Commands](11-cli-commands.md) - Transaction commands in CLI
- [Performance Optimization](07-performance.md) - Transaction performance tips
- [C API](02-c-api.md) - Programmatic transaction management
