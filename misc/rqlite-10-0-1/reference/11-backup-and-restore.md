# Backup & Restore

## Hot Backup

rqlite supports hot backing up of a node while it is running. Retrieving a full copy of the SQLite database is the recommended way to backup rqlite.

### Via CLI

```
127.0.0.1:4001> .backup bak.sqlite3
backup file written successfully
```

### Via API

```bash
curl -s -XGET localhost:4001/db/backup -o bak.sqlite3
```

> By default, the backup is in WAL mode. Request DELETE mode with `?fmt=delete` (requires sufficient disk space).

If the receiving node is not the Leader, it transparently forwards the request. Add `noleader` to get a backup of the actual receiving node's database. Add `redirect` to get an HTTP 301 redirect to the Leader instead.

> For large databases (100MB+), request backups directly from the Leader for faster performance.

### SQL Text Dump

```
127.0.0.1:4001> .dump bak.sql
SQL text file written successfully
```

Or via API:

```bash
curl -s -XGET 'localhost:4001/db/backup?fmt=sql' -o bak.sql
```

Limit to specific tables: `?fmt=sql&tables=users,customers`

### Compressed Backups

```bash
curl -s -XGET 'localhost:4001/db/backup?compress' -o bak.sqlite3.gz
```

Combine with VACUUM for the smallest download: `?compress&vacuum`

### VACUUMed Backups

```bash
curl -s -XGET 'localhost:4001/db/backup?vacuum' -o bak.sqlite3
```

> VACUUM may temporarily double disk usage. Ensure sufficient free space.

### Always Test Your Backups

Periodically check backups using SQLite's integrity check:

```bash
sqlite3 bak.sqlite3 "PRAGMA integrity_check"
```

## Automatic Backups

rqlite supports periodic, automatic backups to cloud storage and the local file system. Only the Leader performs backups. Backups are compressed, and rqlite skips creating a backup if the database hasn't changed since the last upload.

Configure via `-auto-backup` pointing to a JSON config file.

### Amazon S3

```json
{
    "version": 1,
    "type": "s3",
    "interval": "5m",
    "vacuum": false,
    "sub": {
        "access_key_id": "$ACCESS_KEY_ID",
        "secret_access_key": "$SECRET_ACCESS_KEY_ID",
        "region": "$BUCKET_REGION",
        "bucket": "$BUCKET_NAME",
        "path": "backups/db.sqlite3.gz"
    }
}
```

Omit `access_key_id` and `secret_access_key` (or set to null/empty) when running within AWS with IAM roles (EC2 role or IRSA for EKS).

### S3-Compatible Providers (Wasabi, MinIO, Backblaze B2)

```json
{
    "version": 1,
    "type": "s3",
    "interval": "5m",
    "sub": {
        "access_key_id": "$ACCESS_KEY_ID",
        "secret_access_key": "$SECRET_ACCESS_KEY_ID",
        "endpoint": "https://s3.minio.example.com",
        "region": "us-east-1",
        "bucket": "rqlite-backups",
        "path": "backups/db.sqlite3.gz",
        "force_path_style": true
    }
}
```

### Google Cloud Storage

```json
{
    "version": 1,
    "type": "gcs",
    "interval": "5m",
    "sub": {
        "project_id": "$PROJECT_ID",
        "bucket": "$BUCKET",
        "name": "db.sqlite3.gz",
        "credentials_path": "$CREDENTIALS_PATH"
    }
}
```

### Local File System

```json
{
    "version": 1,
    "type": "file",
    "interval": "1m",
    "sub": {
        "dir": "/var/backups/rqlite",
        "name": "backup.sqlite.gz"
    }
}
```

### Additional Options

- `no_compress: true` — disable compression
- `timestamp: true` — prepend timestamp to filename (format: `YYYYMMDDHHMMSS` UTC)
- Environment variable expansion: strings starting with `$` are replaced from the environment

Example with timestamps and no compression:

```json
{
    "version": 1,
    "type": "s3",
    "interval": "5m",
    "timestamp": true,
    "no_compress": true,
    "sub": {
        "access_key_id": "$ACCESS_KEY_ID",
        "secret_access_key": "$SECRET_ACCESS_KEY_ID",
        "region": "$BUCKET_REGION",
        "bucket": "$BUCKET_NAME",
        "path": "backups/db.sqlite3"
    }
}
```

## Restoring from SQLite

### Booting (Recommended for Large Databases)

_Booting_ enables rapid initialization of a node from a SQLite database image. Designed for **single-node setups only** — after booting, you can join new nodes to form a cluster.

Via API:

```bash
curl -XPOST 'http://localhost:4001/boot' -H "Transfer-Encoding: chunked" \
     --upload-file largedb.sqlite
```

Via CLI:

```
127.0.0.1:4001> .boot largedb.sqlite
Node booted successfully
```

### Loading

_Loading_ can target any node in a cluster (transparently forwarded to Leader if needed). Supports two source types:

- **SQLite database file** — fast for small databases, can be CPU/memory intensive above ~100MB
- **SQL text dump** — convenient but may be slow for large datasets

Via API:

```bash
# Load from SQLite binary file
curl -XPOST localhost:4001/db/load -H "Content-type: application/octet-stream" \
  --data-binary @restore.sqlite

# Load from SQL dump
curl -XPOST localhost:4001/db/load -H "Content-type: text/plain" \
  --data-binary @restore.dump
```

Via CLI:

```
127.0.0.1:4001> .restore mydb.sqlite
Database restored successfully
```

### Best Practices for Restoring

- Cluster should be **freshly deployed** without pre-existing data
- Ensure **no other write traffic** during restore
- Loading a SQLite binary file replaces all existing data
- After loading from SQL dump with foreign keys enabled, re-enable constraints:

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' -H 'Content-Type: application/json' -d '[
    "PRAGMA foreign_keys = 1"
]'
```

## Restoring from Cloud Storage

Use `-auto-restore` with a config file matching the backup source. If enabled and **the node has no pre-existing data**, rqlite downloads the backup and initializes the system:

```json
{
    "version": 1,
    "type": "s3",
    "timeout": "60s",
    "continue_on_failure": false,
    "sub": {
        "access_key_id": "$ACCESS_KEY_ID",
        "secret_access_key": "$SECRET_ACCESS_KEY_ID",
        "region": "$BUCKET_REGION",
        "bucket": "$BUCKET_NAME",
        "path": "backups/db.sqlite3.gz"
    }
}
```

Set `continue_on_failure: true` to allow the node to start even if download fails. When bootstrapping a new cluster with `-auto-restore` on each node, only the Leader actually installs the data; other nodes pick it up through Raft consensus.

> Auto-restore uses the _Load_ approach and can be memory-intensive for large databases (100MB+). For very large datasets, use the _Boot_ process instead.
