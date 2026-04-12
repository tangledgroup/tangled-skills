# Backup and Restore

Backing up and restoring your rqlite system.

## Overview

rqlite supports hot backups without downtime, with multiple backup formats and automated cloud storage integration. Proper backup strategy is essential for disaster recovery and cluster cloning.

## Manual Backups

### Using the Shell

```bash
# Connect to rqlite shell
rqlite 127.0.0.1:4001

# Create backup
.backup backup.sqlite3
backup file written successfully

# Create SQL dump
.dump backup.sql
SQL text file written successfully

# Exit
.quit
```

### Using the API

```bash
# Download SQLite database (WAL mode)
curl -s localhost:4001/db/backup -o backup.sqlite3

# Download compressed backup
curl -s 'localhost:4001/db/backup?compress' -o backup.sqlite3.gz

# Download SQL dump
curl -s 'localhost:4001/db/backup?fmt=sql' -o backup.sql

# Download specific tables only
curl -s 'localhost:4001/db/backup?fmt=sql&tables=users,products' -o backup.sql

# Vacuum before backup (smaller file, but uses more disk temporarily)
curl -s 'localhost:4001/db/backup?vacuum' -o backup.sqlite3

# Combined options
curl -s 'localhost:4001/db/backup?compress&vacuum' -o backup.sqlite3.gz
```

### Backup Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fmt=sql` | Return SQL dump instead of binary | Binary SQLite file |
| `fmt=delete` | Return DELETE journal mode (not WAL) | WAL mode |
| `compress` | GZIP compress the backup | Uncompressed |
| `vacuum` | VACUUM database before backup | No vacuum |
| `tables=name1,name2` | Include only specified tables (SQL format) | All tables |
| `noleader` | Backup from this node, don't redirect to leader | Redirects to leader |
| `redirect` | Return HTTP 301 if not leader | Forwards to leader |

## Restore Procedures

### Restore via Shell

```bash
# Stop all nodes except one
# Then connect to the remaining node
rqlite 127.0.0.1:4001

# Restore from SQLite file
.restore backup.sqlite3
database restored successfully

# Or restore from SQL dump
.restore backup.sql
database restored successfully

# Verify restoration
.tables
.schema
```

### Restore via API

```bash
# Upload SQLite database file
curl -XPOST localhost:4001/db/restore \
  --form db=@backup.sqlite3

# Check status
curl localhost:4001/status
```

### Full Cluster Restore

**Step-by-step procedure:**

1. **Stop all nodes in the cluster**
   ```bash
   sudo systemctl stop rqlite1 rqlite2 rqlite3
   ```

2. **Clear data directories** (optional, if replacing entire cluster)
   ```bash
   rm -rf /var/lib/rqlite/node1/*
   rm -rf /var/lib/rqlite/node2/*
   rm -rf /var/lib/rqlite/node3/*
   ```

3. **Start single node without -join**
   ```bash
   rqlited -node-id=1 /var/lib/rqlite/node1
   ```

4. **Restore backup to single node**
   ```bash
   curl -XPOST localhost:4001/db/restore \
     --form db=@backup.sqlite3
   ```

5. **Stop the node**
   ```bash
   sudo systemctl stop rqlite1
   ```

6. **Restart all nodes with original cluster configuration**
   ```bash
   rqlited -node-id=1 /var/lib/rqlite/node1
   rqlited -node-id=2 -join=host1:4002 /var/lib/rqlite/node2
   rqlited -node-id=3 -join=host1:4002 /var/lib/rqlite/node3
   ```

7. **Verify cluster status**
   ```bash
   rqlite host1:4001
   .nodes
   ```

## Automated Backups

rqlite can automatically backup to cloud storage or local filesystem at configured intervals.

### Configuration File Format

Create a JSON configuration file and pass it with `-auto-backup`:

```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "vacuum": false,
  "timestamp": true,
  "no_compress": false,
  "sub": {
    // Type-specific configuration
  }
}
```

### Top-Level Options

| Field | Type | Description |
|-------|------|-------------|
| `version` | int | Configuration version (use 1) |
| `type` | string | Backup destination: `s3`, `gcs`, `file` |
| `interval` | string | Go duration string (e.g., "5m", "1h", "30s") |
| `vacuum` | boolean | VACUUM before backup (uses more disk) |
| `timestamp` | boolean | Prepend timestamp to filename |
| `no_compress` | boolean | Disable compression (larger files) |

### Amazon S3 Backups

```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "vacuum": false,
  "timestamp": true,
  "sub": {
    "access_key_id": "$AWS_ACCESS_KEY_ID",
    "secret_access_key": "$AWS_SECRET_ACCESS_KEY",
    "region": "us-east-1",
    "bucket": "my-rqlite-backups",
    "path": "backups/db.sqlite3.gz"
  }
}
```

**Start rqlite:**
```bash
rqlited -auto-backup=backup-config.json ...
```

**IAM Role (AWS EC2/EKS):**
```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "sub": {
    "access_key_id": "",
    "secret_access_key": "",
    "region": "us-east-1",
    "bucket": "my-rqlite-backups",
    "path": "backups/db.sqlite3.gz"
  }
}
```

Empty credentials trigger AWS SDK's default credential chain (IAM role).

### S3-Compatible Storage (MinIO, Wasabi)

**MinIO (path-style):**
```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "sub": {
    "access_key_id": "$MINIO_ACCESS_KEY",
    "secret_access_key": "$MINIO_SECRET_KEY",
    "endpoint": "https://minio.example.com",
    "region": "us-east-1",
    "bucket": "rqlite-backups",
    "path": "backups/db.sqlite3.gz",
    "force_path_style": true
  }
}
```

**Wasabi:**
```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "sub": {
    "access_key_id": "$WASABI_ACCESS_KEY",
    "secret_access_key": "$WASABI_SECRET_KEY",
    "endpoint": "https://s3.eu-central-1.wasabisys.com",
    "region": "eu-central-1",
    "bucket": "rqlite-backups",
    "path": "backups/db.sqlite3.gz"
  }
}
```

### Google Cloud Storage

```json
{
  "version": 1,
  "type": "gcs",
  "interval": "5m",
  "vacuum": false,
  "sub": {
    "project_id": "$GCP_PROJECT_ID",
    "bucket": "my-rqlite-backups",
    "name": "db.sqlite3.gz",
    "credentials_path": "/path/to/service-account.json"
  }
}
```

### Local File System

```json
{
  "version": 1,
  "type": "file",
  "interval": "1h",
  "vacuum": false,
  "timestamp": true,
  "sub": {
    "dir": "/var/backups/rqlite",
    "name": "backup.sqlite3.gz"
  }
}
```

### Environment Variable Expansion

Configuration supports variable expansion:

```json
{
  "version": 1,
  "type": "s3",
  "interval": "$BACKUP_INTERVAL",
  "sub": {
    "access_key_id": "$AWS_ACCESS_KEY_ID",
    "secret_access_key": "$AWS_SECRET_ACCESS_KEY",
    "region": "$AWS_REGION",
    "bucket": "$S3_BUCKET",
    "path": "backups/db.sqlite3.gz"
  }
}
```

## Backup Best Practices

### Testing Backups

**Regularly verify backup integrity:**

```bash
# Test SQLite file with integrity check
sqlite3 backup.sqlite3 "PRAGMA integrity_check;"

# Test SQL dump by restoring to test instance
docker run -d --name rqlite-test -p 4001:4001 rqlite/rqlite
curl -XPOST localhost:4001/db/restore --form db=@backup.sql
rqlite 127.0.0.1:4001 ".tables"
```

### Backup Frequency

| Data Criticality | Recommended Frequency | Retention |
|------------------|----------------------|-----------|
| Development | Daily | 7 days |
| Production (low churn) | Hourly | 30 days |
| Production (high churn) | Every 5-15 minutes | 7-30 days |
| Mission-critical | Continuous (CDC) + hourly | 90+ days |

### Storage Considerations

- **WAL mode backups**: ~1.5x database size
- **Compressed backups**: Typically 60-80% smaller
- **VACUUM before backup**: Can double temporary disk usage
- **Monitor disk space** to prevent backup failures

### Offsite Backup Strategy

1. **Primary**: Automated S3/GCS backups every 5 minutes
2. **Secondary**: Daily backups to different region
3. **Tertiary**: Weekly backups to cold storage (Glacier)
4. **Local**: Hourly filesystem backups for quick recovery

## Restore Best Practices

### Point-in-Time Recovery

With timestamped backups:

```bash
# List available backups
aws s3 ls s3://my-backups/backups/ | grep db.sqlite3

# Restore specific point in time
aws s3 cp s3://my-backups/backups/20240115143000_db.sqlite3.gz ./
gunzip 20240115143000_db.sqlite3.gz
curl -XPOST localhost:4001/db/restore --form db=@20240115143000_db.sqlite3
```

### Minimizing Downtime

For large databases:

1. **Pre-stage new cluster** with restored data
2. **Use CDC** to capture changes during restore
3. **Switch traffic** to new cluster when caught up
4. **Decommission old cluster** after verification

## Troubleshooting

### Backup Fails

**Check disk space:**
```bash
df -h /var/lib/rqlite
```

**Check rqlite logs:**
```bash
journalctl -u rqlite -f
```

**Verify node is leader:**
```bash
curl localhost:4001/status | grep state
```

### Restore Fails

**Ensure exclusive access:**
- Stop all other nodes
- Don't have clients connected

**Check file format:**
```bash
# Verify SQLite file
file backup.sqlite3
sqlite3 backup.sqlite3 "PRAGMA integrity_check;"
```

**Clear existing data:**
```bash
rm -rf /var/lib/rqlite/node1/*
```

### Automated Backup Not Running

**Verify configuration:**
```bash
# Check config file is valid JSON
cat backup-config.json | python3 -m json.tool

# Verify rqlite started with flag
ps aux | grep rqlited
```

**Check credentials:**
```bash
# Test S3 access manually
aws s3 ls s3://my-backups/
```

## Next Steps

- Set up [monitoring](10-monitoring.md) to track backup success
- Configure [CDC](11-cdc.md) for continuous data replication
- Implement [security](08-security.md) for backup storage access
- Optimize [performance](09-performance.md) for large databases
