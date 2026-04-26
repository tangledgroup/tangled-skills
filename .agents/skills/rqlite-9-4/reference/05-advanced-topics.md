# Advanced Topics

## Change Data Capture (CDC)

CDC streams INSERT, UPDATE, and DELETE activity to an HTTP webhook as JSON. Only the cluster Leader transmits events. Delivery is **at-least-once** with deduplication via a unique CDC Event Index.

### Enabling CDC

Pass a URL directly:

```bash
rqlited -cdc-config="http://localhost:8000/webhook" data/
```

Print to stdout for testing:

```bash
rqlited -cdc-config=stdout data/
```

Or use a configuration file:

```bash
rqlited -cdc-config=/path/to/cdc.json data/
```

### CDC Configuration

```json
{
  "endpoint": "https://webhook.example.com/cdc",
  "service_id": "prod-cluster",
  "row_ids_only": false,
  "table_filter": "^(users|orders)$",
  "tls": {
    "ca_cert_file": "/etc/certs/ca.pem",
    "cert_file": "/etc/certs/client.crt",
    "key_file": "/etc/certs/client.key",
    "insecure_skip_verify": false,
    "server_name": "webhook.example.com"
  },
  "max_batch_size": 500,
  "max_batch_delay": "250ms",
  "high_watermark_interval": "1s",
  "transmit_timeout": "5s",
  "transmit_max_retries": 8,
  "transmit_retry_policy": "ExponentialRetryPolicy",
  "transmit_min_backoff": "100ms",
  "transmit_max_backoff": "5s"
}
```

Key options:

- `endpoint` — HTTP webhook URL or `"stdout"`
- `service_id` — identifier to distinguish multiple CDC sources
- `row_ids_only` — send only primary key IDs and operation type (omit full row data)
- `table_filter` — regex pattern for tables to include
- `max_batch_size` / `max_batch_delay` — control batching throughput vs. latency
- `transmit_retry_policy` — `LinearRetryPolicy` (default) or `ExponentialRetryPolicy`

### Event Format

```json
{
  "node_id": "127.0.0.1:4002",
  "service_id": "prod-cluster",
  "payload": [
    {
      "index": 3,
      "commit_timestamp": 1757892884812603,
      "events": [
        {
          "op": "INSERT",
          "table": "users",
          "new_row_id": 7,
          "before": null,
          "after": {"id": 7, "name": "fiona"}
        }
      ]
    }
  ]
}
```

### Best Practices

- Set `table_filter` early to avoid unnecessary load
- Track the highest processed `index` for downstream deduplication
- Monitor disk usage when using infinite retries — queues grow until disk is full
- Keep webhook handlers fast; offload heavy processing to workers

## SQLite Extensions

rqlite supports loading [SQLite Run-Time Loadable Extensions](https://www.sqlite.org/loadext.html).

### Built-in Docker Extensions

The official Docker image includes:

- `sqlean` — curated set of useful functions (crypto, math, hash)
- `sqlite-vec` — vector search engine
- `sqliteai-vector` — alternative vector search engine
- `icu` — International Components for Unicode
- `misc` — subset of SQLite miscellaneous extensions

Enable with environment variable:

```bash
docker run -e SQLITE_EXTENSIONS='sqlean,sqlite-vec' -p 4001:4001 rqlite/rqlite
```

### Loading Custom Extensions

Compile the extension as a shared library and pass its path at startup:

```bash
gcc -g -fPIC -shared rot13.c -o ~/extensions/rot13.so
rqlited -extensions-path=~/extensions data/
```

`-extensions-path` accepts comma-delimited paths to files, directories, zip archives, or gzipped tarballs. If any extension fails to load, rqlite exits.

Verify loaded extensions:

```
127.0.0.1:4001> .extensions
rot13.so
```

**Important**: In a cluster, the identical extension configuration must be supplied to every node. Loading extensions on only some nodes results in undefined behavior.

## Backup and Restore

### Hot Backup

Retrieve a consistent copy of the SQLite database without stopping the node:

```bash
# Via CLI
127.0.0.1:4001> .backup bak.sqlite3

# Via API
curl -s -XGET localhost:4001/db/backup -o bak.sqlite3
```

Backup options:

- `?fmt=delete` — request DELETE journal mode instead of WAL
- `?fmt=sql` — SQL text dump format
- `?tables=users,orders` — limit SQL dump to specific tables
- `?vacuum` — VACUUM the backup before serving (may double disk usage temporarily)
- `?compress` — GZIP-compressed backup
- `?noleader` — backup from the receiving node instead of forwarding to Leader
- `?redirect` — return HTTP 301 with Leader address instead of forwarding

### Automatic Backups

Configure periodic backups to cloud storage or local filesystem:

```json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "vacuum": false,
  "timestamp": true,
  "sub": {
    "access_key_id": "$AWS_ACCESS_KEY",
    "secret_access_key": "$AWS_SECRET_KEY",
    "region": "us-east-1",
    "bucket": "my-rqlite-backups",
    "path": "backups/db.sqlite3.gz"
  }
}
```

Supported backends:

- **S3** — Amazon S3 and any S3-compatible provider (Wasabi, Backblaze B2, MinIO)
- **GCS** — Google Cloud Storage
- **file** — local filesystem directory

For S3-compatible providers, set `endpoint` and optionally `force_path_style: true` (MinIO). For AWS IAM roles, omit credentials to use the default credential chain.

Configuration file supports environment variable expansion (`$VAR`).

### Restore from SQLite

Boot a node from an existing SQLite database:

```bash
curl -XPOST 'http://localhost:4001/boot' \
  -H "Transfer-Encoding: chunked" \
  --upload-file largedb.sqlite
```

Or via CLI:

```
127.0.0.1:4001> .boot largedb.sqlite
```

Booting is designed for single-node setups. After booting, join additional nodes to form a cluster.

Load data into an existing node:

```bash
curl -XPOST 'http://localhost:4001/db/load' \
  --upload-file dump.sql
```

## Performance Tuning

### Key Factors

rqlite performance is determined by:

1. **Disk I/O** — every write goes through Raft, which calls `fsync()` after each log entry
2. **Network latency** — Raft contacts all nodes twice per commit (in parallel)

Typical throughput ranges from 10 to hundreds of requests per second depending on hardware.

### Improving Write Performance

- **Batching** — include as many statements as possible in a single request. Bulk writes with transactions can improve throughput by 2 orders of magnitude
- **Queued writes** — trade some durability for significant write performance gains
- **Faster disks** — SSDs or NVMe make the biggest difference on low-latency networks
- **Memory-backed filesystem** — tmpfs can give ~100x improvement but risks data loss on power failure:

```bash
mount -t tmpfs -o size=512m tmpfs /mnt/ramdisk
rqlited -node-id=1 /mnt/ramdisk/data
```

- **Separate SQLite and Raft storage** — place the SQLite database on a different disk from the Raft log:

```bash
rqlited -on-disk-path /disk2/db.sqlite /disk1/data
```

### Improving Read Performance

- Use `level=weak` (default) for fast reads served by the Leader
- Add read-only nodes with `level=none` for edge deployments
- Tune snapshot frequency (`-raft-snap`, `-raft-snap-wal-size`) to balance startup time and I/O load

### Database Maintenance

Run VACUUM periodically to defragment:

```bash
curl -XPOST 'localhost:4001/db/execute' \
  -H 'Content-Type: application/json' \
  -d '["VACUUM"]'
```

Or enable automatic VACUUM:

```bash
rqlited -auto-vacuum-int=24h data/
```

Run `PRAGMA optimize` to update query statistics:

```bash
curl -XPOST 'localhost:4001/db/execute' \
  -H 'Content-Type: application/json' \
  -d '["PRAGMA optimize"]'
```

rqlite runs `PRAGMA optimize` automatically once per day. Adjust with `-auto-optimize-int`.

## Monitoring

### Status Endpoint

```bash
curl localhost:4001/status?pretty
```

Returns build info, HTTP configuration, node start time, uptime, and runtime statistics.

### Nodes Endpoint

```bash
curl localhost:4001/nodes?pretty&ver=2
```

Returns each node's `api_addr`, `addr`, `leader`, `voter`, and `reachable` status. Add `?nonvoters` to include read-only nodes.

### Leader Endpoint

```bash
# Get current leader
curl localhost:4001/leader?pretty

# Force leadership election
curl -XPOST http://localhost:4001/leader

# Step down to specific node
curl -XPOST http://localhost:4001/leader \
  -H 'Content-Type: application/json' \
  -d '{"id": "node2"}'
```

### Readiness Checks

```bash
# Full readiness (node + leader + store)
curl localhost:4001/readyz

# Node only (no leader check, useful for automation)
curl localhost:4001/readyz?noleader

# Wait until caught up with leader
curl localhost:4001/readyz?sync&timeout=5s
```

Use `/readyz` as the health check endpoint for load balancers and Kubernetes.

### expvar

Go runtime statistics:

```bash
curl localhost:4001/debug/vars
```

Filter by key: `localhost:4001/debug/vars?key=http`.

### pprof

Standard Go profiling endpoints:

```bash
curl localhost:4001/debug/pprof/profile
curl localhost:4001/debug/pprof/heap
```

## Direct SQLite Access

You may read the SQLite database directly but must follow strict guidelines:

- Use OS-level permissions to enforce **read-only** access
- Open connections in read-only mode (`mode=ro` URI parameter)
- Never open in EXCLUSIVE locking mode
- Never modify the SQLite file, WAL, or shared-memory files

Long-running reads from external processes can block rqlite's snapshotting. Monitor for this issue if direct access is needed.
