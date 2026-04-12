# Direct SQLite Access

Accessing the underlying SQLite database directly from rqlite nodes.

## ⚠️ Warning

**Read this carefully before proceeding.** Improper direct access to the SQLite database can lead to data corruption and loss.

rqlite manages the SQLite database internally for consistency and high availability. Most applications should interact exclusively through the HTTP API. Direct access is only recommended for specific use cases with proper precautions.

## What You MUST NOT Do

### ❌ Never Modify the Database Directly

```bash
# DANGEROUS - DO NOT DO THIS!
sqlite3 /var/lib/rqlite/db.sqlite "INSERT INTO users VALUES(1, 'Alice')"
```

**Why it's dangerous:**
- Bypasses Raft consensus
- Data not replicated to other nodes
- Causes cluster divergence
- May corrupt the database

### ❌ Never Change Journal Mode

```bash
# DANGEROUS - DO NOT DO THIS!
sqlite3 /var/lib/rqlite/db.sqlite "PRAGMA journal_mode = DELETE"
```

rqlite **requires** WAL (Write-Ahead Logging) mode. Changing this breaks rqlite.

### ❌ Never Checkpoint the WAL

```bash
# DANGEROUS - DO NOT DO THIS!
sqlite3 /var/lib/rqlite/db.sqlite "PRAGMA wal_checkpoint(TRUNCATE)"
```

rqlite manages WAL checkpointing exclusively. External checkpoints break replication.

## What You CAN Do

### ✅ Read-Only Access (With Precautions)

You may read the SQLite database directly if you follow these guidelines:

#### 1. Enforce Read-Only at OS Level

```bash
# Set directory permissions to prevent accidental writes
chown -R rqlite:rqlite /var/lib/rqlite/node1
chmod 750 /var/lib/rqlite/node1

# Or mount as read-only (for dedicated read processes)
mount -o remount,ro /var/lib/rqlite/node1
```

#### 2. Open Database in Read-Only Mode

```bash
# Using SQLite CLI with URI mode
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro"

# Example queries
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" "SELECT * FROM users LIMIT 10;"
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" ".schema"
```

**Programmatic examples:**

```python
# Python with sqlite3
import sqlite3

conn = sqlite3.connect("file:/var/lib/rqlite/node1/db.sqlite?mode=ro", uri=True)
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
conn.close()
```

```go
// Go with modernc.org/sqlite
import "modernc.org/sqlite"

db, err := sqlite.Open("/var/lib/rqlite/node1/db.sqlite?mode=ro")
if err != nil {
    log.Fatal(err)
}
defer db.Close()

rows, err := db.Query("SELECT * FROM users")
```

#### 3. Avoid Exclusive Locking

```bash
# DANGEROUS - May block rqlite
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro&locking=exclusive"

# SAFE - Shared locking (default)
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro"
```

## Why These Guidelines Matter

### WAL Checkpointing Risk

Even read-only connections may checkpoint the WAL when closing:

```
SQLite Client Opens DB → Reads Data → Closes Connection
                                              ↓
                                    May trigger WAL checkpoint
                                              ↓
                                    Alters database state
                                              ↓
                              Breaks rqlite replication!
```

**Prevention:** Use `mode=ro` URI parameter to prevent checkpointing.

### Long-Running Reads

rqlite periodically snapshots the database, requiring exclusive access:

```
Long Read Transaction Holds Lock
         ↓
rqlite Needs Exclusive Access for Snapshot
         ↓
    Snapshot Blocked
         ↓
Disk Usage Grows / Performance Degrades
```

**Mitigation:** Keep read transactions short, monitor snapshot latency.

## Protected Files

These files must be protected from modification:

| File | Purpose | Protection Required |
|------|---------|-------------------|
| `db.sqlite` | Main database | Read-only for external access |
| `db.sqlite-wal` | Write-ahead log | Never access directly |
| `db.sqlite-shm` | Shared memory | Never access directly |

## Use Cases for Direct Access

### ✅ Analytics and Reporting

```bash
# Run analytics queries without affecting rqlite performance
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" \
  "SELECT DATE(created_at), COUNT(*) FROM events GROUP BY DATE(created_at);"
```

### ✅ Data Export

```bash
# Export data for external processing
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" \
  ".mode csv" \
  ".output /tmp/export.csv" \
  "SELECT * FROM users;"
```

### ✅ Schema Inspection

```bash
# View database schema
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" ".schema"

# List tables
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" \
  "SELECT name FROM sqlite_master WHERE type='table';"
```

### ✅ Emergency Recovery

```bash
# Last resort: Extract data from failed node
# Only if HTTP API is unavailable and no backup exists
sqlite3 "file:/var/lib/rqlite/node1/db.sqlite?mode=ro" \
  ".dump" > emergency_dump.sql
```

## Monitoring Direct Access

### Detect Long-Running Reads

```bash
# Check for blocked operations
curl localhost:4001/status | jq '.db'

# Monitor snapshot latency in logs
grep "snapshot" /var/log/rqlite.log | grep -i "slow\|block"
```

### Monitor Disk Usage

```bash
# Watch for WAL growth (indicates checkpoint issues)
du -sh /var/lib/rqlite/node1/*
ls -lh /var/lib/rqlite/node1/*.wal
```

## Best Practices

### 1. Prefer HTTP API

```python
# Instead of direct access, use HTTP API
import requests

resp = requests.get("http://localhost:4001/db/query", params={'q': 'SELECT * FROM users'})
data = resp.json()
```

### 2. Use Read-Only Nodes for Heavy Reads

```bash
# Add read-only node for analytics
rqlited -node-id=analytics \
  -join=node1:4002 \
  -raft-voter=false \
  /var/lib/rqlite/analytics

# Run heavy queries on read-only node via HTTP API
curl 'http://analytics-node:4001/db/query?q=SELECT COUNT(*) FROM large_table'
```

### 3. Implement Caching Layer

```python
# Cache frequent reads to reduce direct access needs
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=60)

def get_users():
    if 'users' not in cache:
        resp = requests.get("http://localhost:4001/db/query?q=SELECT * FROM users")
        cache['users'] = resp.json()
    return cache['users']
```

### 4. Use CDC for Real-Time Sync

Instead of polling the database, use Change Data Capture:

```bash
# Configure CDC to stream changes
rqlited -cdc-config=/path/to/cdc.json ...

# External system receives changes in real-time
# No need for direct database access
```

See [CDC](11-cdc.md) for setup.

## Troubleshooting

### Database Won't Open

**Symptom:** "database is locked" error

**Cause:** rqlite has exclusive lock, or another process holds lock

**Solution:**
- Ensure using `mode=ro` URI parameter
- Check for other processes accessing database
- Wait for rqlite operations to complete

### Unexpected Data Changes

**Symptom:** Data appears modified after "read-only" access

**Cause:** WAL checkpoint occurred on connection close

**Solution:**
- Verify using `mode=ro` parameter
- Check file permissions prevent writes
- Monitor WAL file size changes

### Performance Degradation

**Symptom:** rqlite slows down during direct reads

**Cause:** Long-running read blocking snapshots

**Solution:**
- Keep read transactions short
- Use read-only nodes for heavy queries
- Monitor and alert on snapshot latency

## Summary

| Operation | Allowed? | How |
|-----------|----------|-----|
| Read data | ✅ Yes | `mode=ro` URI, OS-level read-only |
| Write data | ❌ No | Use HTTP API only |
| Change schema | ❌ No | Use HTTP API only |
| Checkpoint WAL | ❌ No | rqlite manages exclusively |
| Change journal mode | ❌ No | Must remain WAL mode |
| Access WAL/shm files | ❌ No | Internal use only |

## Next Steps

- Use [HTTP API](04-api.md) for all write operations
- Set up [CDC](11-cdc.md) for real-time data sync
- Configure [read-only nodes](03-clustering.md) for heavy reads
- Implement [backups](05-backup-restore.md) instead of direct access
