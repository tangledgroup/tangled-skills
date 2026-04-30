# Extensions & CDC

## SQLite Extensions

rqlite supports loading [SQLite Run-Time Loadable Extensions](https://www.sqlite.org/loadext.html). Extensions enable advanced data types, custom functions, vector search, cryptography, and more.

### Docker Built-In Extensions

The [rqlite Docker image](https://hub.docker.com/r/rqlite/rqlite/) comes preloaded with useful extensions. Enable them via the `SQLITE_EXTENSIONS` environment variable:

| Extension | Purpose | Key |
|-----------------|-----------------|-----------------|
| [Sqlean](https://github.com/nalgeon/sqlean) | Curated set of useful functions | `sqlean` |
| [sqlite-vec](https://github.com/asg017/sqlite-vec) | Vector search engine | `sqlite-vec` |
| [sqliteai-vector](https://github.com/sqliteai/sqlite-vector) | Vector search engine | `sqliteai-vector` |
| [SQLite ICU](https://sqlite.org/src/dir/ext/icu) | Unicode library integration | `icu` |
| [SQLite Misc](https://sqlite.org/src/dir/ext/misc) | Subset of miscellaneous extensions | `misc` |

```bash
docker run -e SQLITE_EXTENSIONS='sqlean,icu' -p 4001:4001 rqlite/rqlite
```

### Loading Custom Extensions

Two-step process: compile the extension as a shared library/DLL, then supply it via `-extensions-path`:

```bash
# Compile extensions
mkdir ~/extensions
gcc -g -fPIC -shared rot13.c -o ~/extensions/rot13.so
gcc -g -fPIC -shared carray.c -o ~/extensions/carray.so

# Load via directory
rqlited -extensions-path=~/extensions data

# Or via zip archive
zip -j ~/extensions.zip ~/extensions/rot13.so ~/extensions/carray.so
rqlited -extensions-path=~/extensions.zip data

# Or individual files
rqlited -extensions-path=~/extensions/rot13.so,~/extensions/carray.so data
```

`-extensions-path` supports: single files, directories, zip archives, and gzipped tarballs (flat archives only). If any extension fails to load, rqlite exits.

### Checking Loaded Extensions

```
127.0.0.1:4001> .extensions
carray.so
rot13.so
```

### Extensions in Clusters

It is **required** that the identical extension configuration be supplied to **every** node in a cluster. Loading extensions into only a subset of nodes results in undefined behavior.

## Change Data Capture (CDC)

CDC captures INSERT, UPDATE, and DELETE activity and sends it to a user-defined HTTP endpoint as JSON. Only the cluster Leader transmits events. Delivery is **at-least-once** with deduplication via an always-unique CDC Event Index.

### Guarantees and Design

- **At-least-once** delivery — HTTP 200 or 202 is considered successful
- **Leader-only emission** — Followers never transmit but record events to a disk-backed FIFO queue
- **High-water mark (HWM)** — The Leader broadcasts the Raft index of the highest successfully delivered event. Other nodes drop events below the HWM. New Leaders skip events ≤ HWM.
- **No dependence on the Raft log** — CDC uses a disk-backed FIFO queue independent of Raft log compaction

### Enabling CDC

Pass a URL directly or a path to a JSON config file via `-cdc-config`:

```bash
# Direct URL
rqlited -cdc-config="http://localhost:8000/my-cdc-endpoint" ~/node-data

# Print to stdout for testing
rqlited -cdc-config=stdout ~/node-data

# Config file
rqlited -cdc-config=/path/to/cdc.json ~/node-data
```

### Configuration

```json
{
    "endpoint": "https://webhook.example.com/cdc",
    "service_id": "prod-eu-cluster",
    "row_ids_only": false,
    "table_filter": "^(users|orders|inventory)$",
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

Key configuration fields:

- `endpoint` — HTTP endpoint or `"stdout"` (required)
- `service_id` — Distinguishes multiple CDC sources
- `row_ids_only` — When true, send only primary key IDs and operation type (omit before/after data)
- `table_filter` — Regex pattern for table names to include
- `max_batch_size` — Max events per POST
- `max_batch_delay` — Max wait before sending a partially filled batch
- `high_watermark_interval` — Period for HWM broadcasts between nodes
- `transmit_retry_policy` — `LinearRetryPolicy` (default) or `ExponentialRetryPolicy`

> With infinite retries and an unavailable endpoint, CDC queues will grow until disk is full. Monitor disk usage.

### Event Model

Events are sent as HTTP POST JSON. Each payload entry corresponds to one committed Raft log index:

```json
{
    "node_id": "127.0.0.1:4002",
    "service_id": "prod-eu-cluster",
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
                    "after": { "id": 7, "name": "fiona" }
                }
            ]
        }
    ]
}
```

Operations: `INSERT`, `UPDATE`, `DELETE`. When `row_ids_only` is true, `before` and `after` are omitted.

### Downstream De-duplication

Track the highest processed **index**. Ignore any payload groups with `index` ≤ last processed. Alternatively, ensure downstream handlers are idempotent.

### Best Practices

- Keep the webhook handler fast; offload heavy processing to queues or workers
- Validate request signatures or require mTLS for authentication
- Use `service_id` to multiplex events from multiple clusters
- Set a `table_filter` early to avoid unnecessary load
- Log and alert on repeated retry cycles and growing local queues
- Prefer TLS with verified server certificates; use mTLS for stronger authentication
