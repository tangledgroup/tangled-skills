# Storage and Retention

## Contents
- TSDB Architecture
- On-Disk Layout
- Compaction
- Retention Policies
- Remote Write
- Remote Read
- Federation
- Out-of-Order Ingestion

## TSDB Architecture

Prometheus stores time series data in a local time-series database (TSDB). The TSDB is self-contained — no external dependencies. Each Prometheus server manages its own storage autonomously.

**Key components**:
- **Head block**: In-memory buffer for recent samples, periodically flushed to disk
- **Blocks**: Immutable on-disk chunks of time series data, each covering a fixed time range
- **WAL (Write-Ahead Log)**: On-disk log of all pending samples for crash recovery
- **Index**: Inverted index mapping label matchers to series IDs and chunk references
- **Chunks**: Compressed time-series data stored in fixed-size files

**Fanout storage**: Abstracts local TSDB and remote storage. Reads merge results from local and remote sources; writes duplicate to all configured destinations.

### Block Structure

Each block contains:
```
block/
├── chunks/           # Compressed sample data
│   └── 000001
├── index             # Inverted index (label → series → chunks)
├── meta.json         # Block metadata (time range, stats)
├── stats             # Block statistics
└── tombstones        # Deleted time series markers
```

Blocks are immutable once created. Modifications (deletions) are tracked via tombstones.

## Compaction

The TSDB periodically compacts the head block and smaller blocks into larger ones:

- Head block → new on-disk block when it reaches size threshold
- Multiple small blocks → single larger block
- Target block duration: 2 hours (configurable)
- Maximum block duration: 2 weeks

Compaction reduces disk I/O for queries spanning large time ranges and enforces retention policies.

**v3.11.0 experimental features**:
- `fast-startup` — Writes `series_state.json` to WAL directory to track active series state across restarts, reducing startup time
- `xor2-encoding` — New TSDB block float sample chunk encoding optimized for scraped data

## Retention Policies

Configure retention in the config file or via CLI flags:

```yaml
storage:
  tsdb:
    retention.time: 15d       # Time-based retention
    retention.size: 50GB      # Size-based retention
    retention.percentage: 80  # Max % of disk usable (v3.11.0+)
```

**Behavior**:
- Both time and size can be set simultaneously — whichever triggers first initiates compaction
- Oldest blocks are deleted first when retention limit is reached
- `retention.percentage` (v3.11.0+) caps TSDB usage as a percentage of available disk space
- When config values are removed, CLI flag values serve as fallback

**CLI flags**:
```bash
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=50GB
--storage.tsdb.path=/prometheus   # Data directory (default: ./data/)
--storage.tsdb.no-lock-file       # Skip file lock
--storage.tsdb.wal-compression    # Compress WAL (default: true)
--storage.tsdb.allow-overlapping-blocks  # Allow overlapping blocks
--storage.tsdb.block-reload-interval     # TSDB block reload interval
--storage.tsdb.delay-compact-file.path   # For Thanos interoperability
```

## Remote Write

Sends ingested samples to external storage systems in real-time:

```yaml
remote_write:
  - url: "http://thanos-receive:19291/api/v1/receive"
    name: "default"
    send_native_histograms: true
    remote_timeout: 30s
    headers:
      X-Custom-Header: "value"
    basic_auth:
      username: "user"
      password: "secret"
    tls_config:
      ca_file: /etc/ssl/ca.pem
    queue_config:
      capacity: 10000           # Queue size
      min_shards: 1             # Minimum parallel shards
      max_shards: 50            # Maximum parallel shards
      max_samples_per_send: 5000
      batch_send_deadline: 5s
      retry_on_http_429: true   # Retry on rate limiting
    write_relabel_configs:
      - source_labels: [__name__]
        regex: "temp_.*"
        action: drop
```

**Queue manager**: Each remote_write endpoint gets a `QueueManager` that shards writes dynamically based on load. Shards scale up/down automatically.

**v3.11.0 performance improvement**: WAL watching for remote write reuses internal buffers, reducing allocations.

### Remote Write 2.0

Remote Write 2.0 protocol supports:
- Native histograms as first-class types
- Start timestamps (ST) — previously called "created timestamps"
- Aggregator hints
- Histogram exemplars

Enable via `st-storage` feature flag for start timestamp storage.

## Remote Read

Reads historical data from external storage as part of queries:

```yaml
remote_read:
  - url: "http://thanos-query:10901/api/v1/read"
    read_recent: true              # Also read recent data from remote
    required_matchers:
      cluster: "production"        # Filter by external labels
    basic_auth:
      username: "user"
      password: "secret"
```

**Behavior**:
- Without `read_recent`: Only used for queries beyond local retention window
- With `read_recent`: Merged with local results for all queries
- Results from multiple remote_read sources are merged
- `required_matchers` filters remote data by external labels to avoid cross-cluster contamination

**v3.11.3 security fix**: Remote-read rejects snappy-compressed requests whose declared decoded length exceeds the decode limit (CVE-2026-42154).

## Federation

Federation allows one Prometheus server to scrape metrics from another, enabling hierarchical monitoring:

```yaml
# Federating (child) Prometheus — exports aggregated metrics
scrape_configs:
  - job_name: "federate"
    honor_labels: true
    metrics_path: "/federate"
    params:
      'match[]':
        - '{job="prometheus"}'
        - 'up'
        - 'node_cpu_seconds_total'
    static_configs:
      - targets: ["localhost:9090"]
```

```yaml
# Federating (parent) Prometheus — scrapes from children
scrape_configs:
  - job_name: "federate"
    honor_labels: true
    metrics_path: "/federate"
    params:
      'match[]':
        - '{job="prometheus"}'
        - 'up'
    static_configs:
      - targets:
          - "prometheus-us-east:9090"
          - "prometheus-eu-west:9090"
```

**Use cases**:
- Aggregating metrics from multiple regional Prometheus instances
- Selective metric sharing between teams
- Horizontal scaling of query load

**`/federate` endpoint**: Accepts `match[]` parameters specifying which series to return. Returns only the matched series in Prometheus text format.

## Out-of-Order Ingestion

Prometheus can accept samples with timestamps older than the most recently ingested sample:

```yaml
storage:
  tsdb:
    out_of_order_time_window: 10m   # Accept OOO samples within this window
```

Enabled via `--enable-feature=ooo-ingest` flag plus config setting. Useful for:
- Handling clock skew between targets
- Receiving delayed metrics from unreliable network paths
- Integrating with systems that produce late data

**New histogram**: `prometheus_tsdb_sample_ooo_delta` tracks the distribution of out-of-order samples in seconds (v3.9.0+).

## Storage Monitoring

Key metrics for monitoring storage health:

| Metric | Description |
|--------|-------------|
| `prometheus_tsdb_storage_blocks_bytes` | Total bytes in storage blocks |
| `prometheus_tsdb_wal_corruptions_total` | WAL corruption count |
| `prometheus_tsdb_compactions_failed_total` | Failed compaction count |
| `prometheus_tsdb_head_samples_appended_total` | Samples appended to head |
| `prometheus_tsdb_reloads_total` | TSDB reload count |
| `prometheus_tsdb_lowest_timestamp` | Oldest sample timestamp |
| `prometheus_tsdb_head_head_chunks` | Number of head chunks |
