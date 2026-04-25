# Database Administration

Complete guide to SQLite database administration including backup and recovery, integrity checking, security, maintenance operations, and production best practices.

## Backup and Recovery

### Online Backup API

Programmatic backup using C API:

```c
// Create online backup
sqlite3 *src_db, *dest_db;
sqlite3_backup *backup;

sqlite3_open("source.db", &src_db);
sqlite3_open("backup.db", &dest_db);

// Initialize backup
backup = sqlite3_backup_init(dest_db, "main", src_db, "main");

if (backup) {
    // Step backup (step=-1 for all-at-once)
    int rc = sqlite3_backup_step(backup, -1);
    
    if (rc == SQLITE_BUSY || rc == SQLITE_LOCKED) {
        // Wait and retry
        sqlite3_sleep(100);
        rc = sqlite3_backup_step(backup, 5);
    }
    
    // Check progress
    int remaining = sqlite3_backup_remaining(backup);
    int total = sqlite3_backup_pagecount(backup);
    printf("Progress: %d/%d pages\n", total - remaining, total);
    
    sqlite3_backup_finish(backup);
}

sqlite3_close(src_db);
sqlite3_close(dest_db);
```

### CLI Backup Commands

Using SQLite command-line interface:

```bash
# Create backup
sqlite3 source.db ".backup 'backup.db'"

# Restore from backup
sqlite3 target.db ".restore 'backup.db'"

# Backup with schema only
sqlite3 source.db ".schema" > schema.sql

# Full dump (schema + data)
sqlite3 source.db ".dump" > full_backup.sql

# Restore from dump
sqlite3 new.db < full_backup.sql
```

### Incremental Backup Strategy

```sql
-- Track changes with timestamps
CREATE TABLE change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    operation TEXT,
    rowid INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to log changes
CREATE TRIGGER log_users_changes AFTER UPDATE ON users
BEGIN
    INSERT INTO change_log (table_name, operation, rowid)
    VALUES ('users', 'UPDATE', OLD.rowid);
END;

-- Backup only changed data since last backup
SELECT * FROM change_log 
WHERE timestamp > (SELECT last_backup FROM config WHERE key = 'last_full_backup');
```

### Point-in-Time Recovery

```sql
-- Enable WAL mode for better recovery
PRAGMA journal_mode = WAL;

-- Regular checkpoints
PRAGMA wal_autocheckpoint = 1000;

-- Backup WAL file along with database
-- Copy both *.db and *.db-wal files together
```

## Integrity Checking

### Basic Integrity Check

```sql
-- Full integrity check
PRAGMA integrity_check;

-- Expected output: "ok" (single row)
-- Any other output indicates problems

-- Quick check (faster, less thorough)
PRAGMA quick_check;
```

### Detailed Integrity Analysis

```sql
-- Check specific database in ATTACH scenario
PRAGMA main.integrity_check;
PRAGMA temp.integrity_check;
PRAGMA attached_db.integrity_check;

-- Check foreign key constraints
PRAGMA foreign_key_check;

-- Returns rows with violations:
-- table | rowid | fk_id | parent_table | parent_rowid
```

### Schema Validation

```sql
-- Verify table schemas match expectations
SELECT * FROM sqlite_master WHERE type = 'table';

-- Check index definitions
SELECT * FROM sqlite_master WHERE type = 'index';

-- Verify triggers exist
SELECT * FROM sqlite_master WHERE type = 'trigger';

-- Check for orphaned indexes
SELECT name FROM sqlite_master 
WHERE type = 'index' AND tbl_name NOT IN (
    SELECT name FROM sqlite_master WHERE type = 'table'
);
```

### Corruption Recovery

```sql
-- Attempt to recover data from corrupted database
-- 1. Try integrity check first
PRAGMA integrity_check;

-- 2. Extract what's readable
SELECT * INTO recovered_table FROM corrupted_table;

-- 3. Use .recover command (SQLite 3.36+)
sqlite3 corrupted.db ".recover" > recovered.sql
sqlite3 new.db < recovered.sql

-- 4. Last resort: hex dump and manual recovery
-- (Requires deep SQLite file format knowledge)
```

## Security

### File Permissions

```bash
# Restrict database file access
chmod 600 database.db          # Owner read/write only
chown appuser:appgroup database.db

# Restrict WAL and lock files
chmod 600 database.db-wal
chmod 600 database.db-shm
chmod 600 database.db-lock
```

### Application-Level Security

```sql
-- Enable foreign key enforcement
PRAGMA foreign_keys = ON;

-- Use parameterized queries (prevent SQL injection)
-- In application code, never concatenate user input into SQL strings

-- Restrict dangerous operations
-- Don't allow users to execute:
-- DROP TABLE, DROP DATABASE, DELETE without WHERE
```

### Secure Delete

Overwrite deleted data:

```sql
-- Enable secure delete (overwrites with zeros)
PRAGMA secure_delete = ON;

-- Note: Significantly impacts DELETE performance
-- Use only when security requirement justifies performance cost
```

### Encryption (SQLCipher)

If using SQLCipher extension:

```sql
-- Set encryption key
PRAGMA key = 'secret-password';

-- Change encryption key
PRAGMA rekey = 'new-password';

-- Set encryption cipher
PRAGMA cipher = 'aes-256-cbc';

-- Configure key derivation
PRAGMA kdf_iter = 64000;  -- Higher = more secure, slower
```

## Maintenance Operations

### VACUUM

Reclaim space and defragment:

```sql
-- Full vacuum (rebuilds entire database)
VACUUM;

-- Vacuum with specific page size
PRAGMA page_size = 4096;
VACUUM;

-- Check if vacuum needed
PRAGMA freelist_count;  -- High value indicates fragmentation

-- Monitor database size
SELECT 
    page_count * page_size AS current_size,
    freelist_count * page_size AS free_space
FROM pragma_page_count(), pragma_page_size(), pragma_freelist_count();
```

### When to VACUUM

- After large DELETE operations (10%+ of table)
- After schema changes that shrink rows
- When freelist_count > 10% of page_count
- Periodically for long-running applications
- Before backup (reduces backup size)

### ANALYZE

Update query planner statistics:

```sql
-- Analyze entire database
ANALYZE;

-- Analyze specific table
ANALYZE users;

-- Analyze specific index
ANALYZE idx_users_email;

-- Schedule regular analysis
-- After bulk inserts/updates/deletes
-- Weekly for production databases
```

### REINDEX

Rebuild indexes:

```sql
-- Rebuild all indexes
REINDEX;

-- Rebuild specific index
REINDEX idx_users_email;

-- Rebuild table (recreates all its indexes)
REINDEX users;

-- When to reindex:
-- - After bulk data changes
-- - If index corruption suspected
-- - After changing collation sequences
```

## Monitoring

### Database Size Tracking

```sql
-- Create monitoring table
CREATE TABLE IF NOT EXISTS db_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    page_count INTEGER,
    page_size INTEGER,
    size_bytes INTEGER,
    freelist_count INTEGER
);

-- Record current state
INSERT INTO db_monitoring (page_count, page_size, size_bytes, freelist_count)
SELECT 
    pc.value,
    ps.value,
    pc.value * ps.value,
    ff.value
FROM 
    (SELECT value AS value FROM (PRAGMA page_count)) pc,
    (SELECT value AS value FROM (PRAGMA page_size)) ps,
    (SELECT value AS value FROM (PRAGMA freelist_count)) ff;

-- View growth over time
SELECT 
    date(timestamp) AS date,
    AVG(size_bytes / 1024.0 / 1024.0) AS avg_size_mb,
    MAX(size_bytes / 1024.0 / 1024.0) AS max_size_mb
FROM db_monitoring
GROUP BY date(timestamp)
ORDER BY date DESC;
```

### Query Performance Monitoring

```sql
-- Create query log
CREATE TABLE query_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_pattern TEXT,
    execution_time_ms REAL,
    rows_affected INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Log slow queries (application-level)
INSERT INTO query_performance (query_pattern, execution_time_ms, rows_affected)
VALUES ('SELECT * FROM users WHERE...', 150.5, 25);

-- Analyze patterns
SELECT 
    query_pattern,
    COUNT(*) AS execution_count,
    AVG(execution_time_ms) AS avg_time_ms,
    MAX(execution_time_ms) AS max_time_ms
FROM query_performance
GROUP BY query_pattern
HAVING AVG(execution_time_ms) > 100
ORDER BY avg_time_ms DESC;
```

### Connection Monitoring

```sql
-- SQLite doesn't track connections internally
-- Implement in application code:

CREATE TABLE connection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id TEXT,
    action TEXT,  -- 'open', 'close', 'query'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Track connection lifecycle
INSERT INTO connection_log (connection_id, action) 
VALUES ('conn_123', 'open');

-- Monitor for leaked connections
SELECT connection_id, MAX(timestamp) AS last_activity
FROM connection_log
WHERE action = 'open'
GROUP BY connection_id
HAVING MAX(timestamp) < datetime('now', '-1 hour');
```

## Schema Management

### Version Tracking

```sql
-- Set application version
PRAGMA user_version = 3;

-- Get current version
PRAGMA user_version;

-- Store schema migrations
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record migration
INSERT INTO schema_migrations (version, description)
VALUES ('3.0.0', 'Added user preferences table');

-- Check pending migrations
SELECT * FROM schema_migrations 
WHERE version NOT IN (SELECT applied_version FROM applied_migrations);
```

### Schema Evolution

```sql
-- Safe migration pattern
BEGIN TRANSACTION;

-- 1. Create new structure
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,          -- New column
    created_at DATETIME
);

-- 2. Copy data
INSERT INTO users_new (id, username, email, created_at)
SELECT id, username, email, created_at FROM users;

-- 3. Verify data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users_new;
-- Counts should match

-- 4. Swap tables
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;

-- 5. Create indexes
CREATE INDEX idx_users_email ON users(email);

-- 6. Record migration
INSERT INTO schema_migrations (version, description)
VALUES ('3.1.0', 'Added phone column to users');

COMMIT;
```

### Schema Documentation

```sql
-- Generate schema documentation
SELECT 
    m.name AS table_name,
    GROUP_CONCAT(
        c.cid || '. ' || c.name || ' ' || c.type || 
        CASE WHEN c.notnull THEN ' NOT NULL' ELSE '' END ||
        CASE WHEN c.dflt_value THEN ' DEFAULT ' || c.dflt_value ELSE '' END,
        '\n'
    ) AS columns
FROM sqlite_master m
JOIN pragma_table_info(m.name) c ON m.name = c.tbl_name
WHERE m.type = 'table' AND m.name NOT LIKE 'sqlite_%'
GROUP BY m.name;

-- Export complete schema
.schema > schema.sql

-- Export with data
.dump > full_backup.sql
```

## Troubleshooting

### Database Locked

```sql
-- Check for active transactions
PRAGMA locking_mode;

-- Increase busy timeout
PRAGMA busy_timeout = 10000;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- In application code:
// - Ensure all connections are properly closed
// - Check for uncommitted transactions
// - Implement retry logic with exponential backoff
```

### Disk Full

```sql
-- Check available space (application-level)
-- Reduce cache size
PRAGMA cache_size = -10240;  -- 10MB

-- Vacuum to reclaim space
VACUUM;

-- Delete unnecessary data
DELETE FROM logs WHERE timestamp < datetime('now', '-90 days');

-- Enable auto-vacuum if available
PRAGMA auto_vacuum = FULL;
```

### Corrupted Database

```sql
-- 1. Stop all writes immediately

-- 2. Run integrity check
PRAGMA integrity_check;

-- 3. Try to recover readable data
sqlite3 corrupted.db ".recover" > recovered.sql

-- 4. Create new database from recovery
sqlite3 recovered.db < recovered.sql

-- 5. Verify recovered data
PRAGMA integrity_check;

-- 6. Restore from backup if recovery fails
```

### Performance Degradation

```sql
-- Check for common issues

-- 1. Outdated statistics
ANALYZE;

-- 2. Fragmentation
PRAGMA freelist_count;
VACUUM IF freelist_count > page_count * 0.1;

-- 3. Missing indexes
EXPLAIN QUERY PLAN SELECT ...;
-- Look for SCAN TABLE, add indexes

-- 4. Cache too small
PRAGMA cache_size = -262144;  -- Increase to 256MB

-- 5. WAL file too large
PRAGMA wal_checkpoint(TRUNCATE);
```

## Production Best Practices

### Connection Management

```c
// C code example: Connection pool pattern

typedef struct {
    sqlite3 **connections;
    int count;
    int max;
} ConnectionPool;

ConnectionPool* create_pool(int size, const char *db_path) {
    ConnectionPool *pool = malloc(sizeof(ConnectionPool));
    pool->connections = malloc(sizeof(sqlite3*) * size);
    pool->count = 0;
    pool->max = size;
    
    for (int i = 0; i < size; i++) {
        sqlite3_open(db_path, &pool->connections[i]);
        
        // Configure connection
        sqlite3_exec(pool->connections[i], "PRAGMA journal_mode = WAL", NULL, NULL, NULL);
        sqlite3_exec(pool->connections[i], "PRAGMA busy_timeout = 5000", NULL, NULL, NULL);
        sqlite3_exec(pool->connections[i], "PRAGMA cache_size = -65536", NULL, NULL, NULL);
        
        pool->count++;
    }
    
    return pool;
}

sqlite3* acquire_connection(ConnectionPool *pool) {
    // Implement connection acquisition logic
    // With timeout and retry
}

void release_connection(ConnectionPool *pool, sqlite3 *db) {
    // Return connection to pool
    // Reset state, clear bindings
}
```

### Error Handling

```c
// Comprehensive error handling pattern

int execute_query(sqlite3 *db, const char *sql, char **err_msg) {
    int rc = sqlite3_exec(db, sql, NULL, NULL, err_msg);
    
    if (rc != SQLITE_OK) {
        // Log error with context
        log_error("SQL Error %d: %s", rc, *err_msg);
        
        // Handle specific error codes
        switch (rc) {
            case SQLITE_BUSY:
                // Retry with backoff
                return retry_query(db, sql, err_msg);
            
            case SQLITE_CONSTRAINT:
                // Handle constraint violation
                log_constraint_violation(sql);
                break;
            
            case SQLITE_IOERR:
                // Check disk space, permissions
                check_disk_health();
                break;
            
            default:
                // Generic error handling
                break;
        }
    }
    
    return rc;
}
```

### Logging and Auditing

```sql
-- Create audit log table
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
    old_values JSON,
    new_values JSON,
    user_id INTEGER,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create triggers for auditing
CREATE TRIGGER audit_users_update AFTER UPDATE ON users
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, new_values, user_id)
    VALUES (
        'users',
        'UPDATE',
        json_object('id', OLD.id, 'status', OLD.status, 'role', OLD.role),
        json_object('id', NEW.id, 'status', NEW.status, 'role', NEW.role),
        @current_user_id  -- Set by application
    );
END;

CREATE TRIGGER audit_users_delete AFTER DELETE ON users
BEGIN
    INSERT INTO audit_log (table_name, operation, old_values, user_id)
    VALUES (
        'users',
        'DELETE',
        json_object('id', OLD.id, 'username', OLD.username),
        @current_user_id
    );
END;
```

### High Availability

```sql
-- Master-replica setup (application-level)

-- On master: Enable WAL mode
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- Regular backups to replicas
-- Copy database file during maintenance window
-- Or use continuous WAL shipping

-- Monitor replication lag
SELECT 
    master_file_size,
    replica_file_size,
    master_file_size - replica_file_size AS lag_bytes
FROM (
    SELECT file_size('master.db') AS master_file_size
), (
    SELECT file_size('replica.db') AS replica_file_size
);
```

## Disaster Recovery

### Backup Strategy

```bash
# Daily full backup
0 2 * * * sqlite3 /path/database.db ".dump" | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz

# Hourly incremental (WAL file)
0 * * * * cp /path/database.db-wal /backup/wal_$(date +\%Y\%m\%d_\%H).wal

# Weekly archive to remote storage
0 3 * * 0 rsync -avz /backup/ user@backup-server:/remote/backups/sqlite/
```

### Recovery Procedures

```bash
# Full recovery from backup
gunzip < /backup/db_20240115.sql.gz | sqlite3 /path/database.db

# Point-in-time recovery
sqlite3 /path/database.db ".dump" > base.sql
for wal in /backup/wal_20240115_*.wal; do
    # Apply WAL files in order
    # (Requires custom script to parse and replay)
done

# Verify recovery
sqlite3 /path/database.db "PRAGMA integrity_check;"
```

### Testing Recovery

```sql
-- Regular recovery drills

-- 1. Restore to test environment
sqlite3 test.db < /backup/db_latest.sql.gz

-- 2. Verify integrity
PRAGMA integrity_check;

-- 3. Spot-check data
SELECT COUNT(*) FROM critical_table;
SELECT * FROM recent_transactions ORDER BY timestamp DESC LIMIT 10;

-- 4. Test application connectivity
-- Run application health checks against restored database
```

## Performance Baseline

### Establishing Baselines

```sql
-- Record performance metrics
CREATE TABLE performance_baseline (
    metric TEXT PRIMARY KEY,
    baseline_value REAL,
    measured_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Measure key metrics
INSERT INTO performance_baseline VALUES ('page_size', (SELECT value FROM (PRAGMA page_size)));
INSERT INTO performance_baseline VALUES ('cache_size', (SELECT value FROM (PRAGMA cache_size)));
INSERT INTO performance_baseline VALUES ('freelist_ratio', 
    (SELECT CAST(ff.value AS REAL) / pc.value 
     FROM (PRAGMA freelist_count) ff, (PRAGMA page_count) pc));

-- Query performance baseline
INSERT INTO query_baselines (query_id, avg_time_ms)
SELECT 
    'user_lookup',
    AVG(execution_time)
FROM query_log 
WHERE query_pattern LIKE '%users WHERE id=%'
GROUP BY query_pattern;
```

### Alerting Thresholds

```sql
-- Define alert conditions
CREATE TABLE alert_thresholds (
    metric TEXT PRIMARY KEY,
    warning_threshold REAL,
    critical_threshold REAL
);

INSERT INTO alert_thresholds VALUES 
    ('freelist_ratio', 0.1, 0.25),      -- Warn if >10% free, critical if >25%
    ('query_time_p99', 100, 500),       -- Warn if p99 >100ms, critical if >500ms
    ('database_growth_mb_per_day', 100, 500);

-- Check thresholds (run periodically)
SELECT 
    'freelist_ratio' AS metric,
    CAST(ff.value AS REAL) / pc.value AS current_value,
    t.warning_threshold,
    t.critical_threshold,
    CASE 
        WHEN CAST(ff.value AS REAL) / pc.value > t.critical_threshold THEN 'CRITICAL'
        WHEN CAST(ff.value AS REAL) / pc.value > t.warning_threshold THEN 'WARNING'
        ELSE 'OK'
    END AS status
FROM (PRAGMA freelist_count) ff, (PRAGMA page_count) pc
JOIN alert_thresholds t ON t.metric = 'freelist_ratio';
```

## Checklist: Production Deployment

### Pre-Deployment

- [ ] Run `PRAGMA integrity_check` - result is "ok"
- [ ] Enable WAL mode: `PRAGMA journal_mode = WAL`
- [ ] Set appropriate cache size based on available memory
- [ ] Configure busy timeout for concurrent access
- [ ] Create all necessary indexes
- [ ] Run `ANALYZE` to populate statistics
- [ ] Test backup and restore procedures
- [ ] Verify file permissions (600 for database files)
- [ ] Document schema version in `PRAGMA user_version`

### Monitoring Setup

- [ ] Database size tracking enabled
- [ ] Query performance logging configured
- [ ] Alert thresholds defined
- [ ] Backup schedule established
- [ ] Recovery procedures documented and tested

### Maintenance Schedule

- [ ] Daily: Automated backups
- [ ] Weekly: `ANALYZE` to update statistics
- [ ] Monthly: `VACUUM` if fragmentation >10%
- [ ] Quarterly: Full recovery drill
- [ ] As needed: Index maintenance based on query patterns
