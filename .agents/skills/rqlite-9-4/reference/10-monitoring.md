# Monitoring rqlite

Monitoring, metrics, and observability for rqlite deployments.

## Overview

Effective monitoring is essential for maintaining healthy rqlite clusters in production. This guide covers built-in diagnostics, metrics exposure, alerting strategies, and integration with popular monitoring systems.

## Built-in Diagnostics

### Status Endpoint

Get comprehensive node status:

```bash
curl localhost:4001/status

# Response includes:
{
  "raft": {
    "leader_addr": "host1:4002",
    "state": "Leader",
    "term": 5,
    "applied_index": 15234,
    "commit_index": 15234,
    "last_log_index": 15234
  },
  "db": {
    "db_size": 52428800,
    "file_format_version": 4,
    "freelist_count": 0,
    "num_queries": 89234,
    "num_writes": 12456
  },
  "store": {
    "applied_index": 15234,
    "commit_index": 15234,
    "num_snapshots": 3,
    "num_wal_snapshots": 12,
    "num_wals": 45
  }
}
```

### Ready Endpoint

Check if node is ready to serve requests:

```bash
curl localhost:4001/ready

# Returns HTTP 200 if ready, 503 if not
```

### Cluster Nodes Status

View all nodes in cluster:

```bash
rqlite 127.0.0.1:4001 ".nodes"

# Output:
1: api_addr: http://host1:4001 addr: host1:4002 voter: true reachable: true leader: true id: 1
2: api_addr: http://host2:4001 addr: host2:4002 voter: true reachable: true leader: false id: 2
3: api_addr: http://host3:4001 addr: host3:4002 voter: true reachable: true leader: false id: 3
```

### System Diagnostics Dump

Export comprehensive diagnostics:

```bash
rqlite 127.0.0.1:4001 ".sysdump diagnostics.json"

# Or via API
curl localhost:4001/db/sysdump -o diagnostics.json
```

## Metrics Exposure

### expvar (Go Runtime Metrics)

rqlite exposes Go runtime metrics via expvar:

```bash
# View in shell
rqlite 127.0.0.1:4001 ".expvar"

# Or directly
curl localhost:4001/debug/vars
```

**Available metrics:**
- Memory usage (heap, stack)
- Goroutine count
- GC statistics
- Network I/O
- Database operations

### Prometheus Metrics

rqlite can expose metrics in Prometheus format. Configure your rqlite deployment to enable metrics endpoint, then scrape with Prometheus.

**Example Prometheus configuration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'rqlite'
    static_configs:
      - targets: ['host1:4001', 'host2:4001', 'host3:4001']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## Key Metrics to Monitor

### Cluster Health

| Metric | Alert Threshold | Severity |
|--------|----------------|----------|
| Leader count | != 1 | Critical |
| Node reachable | false for any voter | Warning |
| Quorum available | < N/2+1 nodes | Critical |
| Term increasing rapidly | > 10 elections/hour | Warning |

### Performance

| Metric | Alert Threshold | Severity |
|--------|----------------|----------|
| Write latency p99 | > 100ms | Warning |
| Read latency p99 | > 50ms | Warning |
| Query timeout rate | > 1% | Warning |
| Transaction failure rate | > 0.1% | Critical |

### Resource Usage

| Metric | Alert Threshold | Severity |
|--------|----------------|----------|
| Database size growth | > 10%/day | Info |
| Disk usage | > 80% | Warning |
| Memory usage | > 85% | Warning |
| CPU usage | > 80% sustained | Warning |

### Data Consistency

| Metric | Alert Threshold | Severity |
|--------|----------------|----------|
| Applied index lag | > 1000 behind commit | Warning |
| Snapshot frequency | > 10/hour | Info |
| WAL file count | > 100 | Warning |

## Monitoring with Prometheus and Grafana

### Prometheus Setup

**Step 1: Install Prometheus**
```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**Step 2: Configure scraping**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rqlite-cluster'
    static_configs:
      - targets: 
          - 'rqlite1:4001'
          - 'rqlite2:4001'
          - 'rqlite3:4001'
    metrics_path: '/debug/vars'
```

### Grafana Dashboards

Import or create dashboards for:

**Cluster Overview:**
- Leader status per node
- Node reachability
- Cluster term history
- Applied vs commit index

**Performance:**
- Query/write latency percentiles
- Requests per second
- Error rates

**Resources:**
- Database size over time
- Disk usage per node
- Memory and CPU utilization

**Example Grafana panel queries:**
```promql
# Leader status (1 = is leader)
rqlite_raft_state == "Leader"

# Write latency p99
histogram_quantile(0.99, rate(rqlite_write_latency_bucket[5m]))

# Request rate
rate(rqlite_requests_total[5m])

# Database size
rqlite_db_size_bytes
```

## Logging Best Practices

### Log Levels

```bash
# Set log level at startup
rqlited -log-level=info ...

# Available levels: error, warn, info, debug
```

### Structured Logging

Configure JSON output for log aggregation:

```bash
rqlited -log-format=json ...
```

### Log Aggregation

**With Docker:**
```yaml
services:
  rqlite1:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
```

**Integrate with:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana
- CloudWatch Logs
- Datadog
- Splunk

### Key Log Patterns to Alert On

```bash
# Leader election events
grep "leader.*elected" /var/log/rqlite.log

# Connection failures
grep "connection refused" /var/log/rqlite.log

# Disk space warnings
grep "no space left" /var/log/rqlite.log

# Consensus errors
grep "raft.*error" /var/log/rqlite.log
```

## Health Checks

### Docker Health Check

```yaml
services:
  rqlite1:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4001/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### Kubernetes Liveness and Readiness

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: rqlite
spec:
  containers:
    - name: rqlite
      livenessProbe:
        httpGet:
          path: /ready
          port: 4001
        initialDelaySeconds: 30
        periodSeconds: 10
      readinessProbe:
        httpGet:
          path: /ready
          port: 4001
        initialDelaySeconds: 5
        periodSeconds: 5
```

### Custom Health Check Script

```bash
#!/bin/bash
# health-check.sh

NODES=("host1:4001" "host2:4001" "host3:4001")
REQUIRED=2
HEALTHY=0

for node in "${NODES[@]}"; do
  if curl -sf "http://${node}/ready" > /dev/null; then
    ((HEALTHY++))
  fi
done

if [ $HEALTHY -ge $REQUIRED ]; then
  echo "Cluster healthy: $HEALTHY/${#NODES[@]} nodes"
  exit 0
else
  echo "Cluster unhealthy: $HEALTHY/${#NODES[@]} nodes"
  exit 1
fi
```

## Alerting Strategies

### Critical Alerts (Page immediately)

- No leader in cluster
- Lost quorum (< N/2+1 nodes available)
- All nodes unreachable
- Data corruption detected

### Warning Alerts (Investigate within 1 hour)

- Single node down in 3-node cluster
- High latency (>100ms p99)
- Disk usage > 80%
- Frequent leader elections

### Info Alerts (Review during business hours)

- Snapshot created
- Configuration changed
- Backup completed/failed
- Certificate expiring soon (< 30 days)

### Example Alert Rules (Prometheus)

```yaml
# alerting.yml
groups:
  - name: rqlite
    rules:
      - alert: RQLiteNoLeader
        expr: sum(rqlite_raft_state == "Leader") == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "No rqlite leader"
          description: "Cluster has no leader for more than 1 minute"

      - alert: RQLiteNodeDown
        expr: rqlite_node_up == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "rqlite node down"
          description: "Node {{ $labels.instance }} has been down for 2 minutes"

      - alert: RQLiteHighLatency
        expr: histogram_quantile(0.99, rate(rqlite_write_latency_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High write latency"
          description: "Write latency p99 is above 100ms"

      - alert: RQLiteDiskSpace
        expr: rqlite_disk_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is above 80%"
```

## Troubleshooting with Metrics

### Identify Slow Queries

```bash
# Check query timing in status
curl localhost:4001/status | jq '.db'

# Enable timings in API responses
curl 'localhost:4001/db/query?timings&q=SELECT * FROM slow_table'
```

### Detect Leader Election Storms

```bash
# Monitor term increases
watch -n 5 'curl localhost:4001/status | jq .raft.term'

# Alert on rapid changes (> 10 elections/hour indicates instability)
```

### Find Resource Bottlenecks

```bash
# Check expvar for memory pressure
curl localhost:4001/debug/vars | jq '.memstats.HeapAlloc'

# Monitor goroutine count (high count may indicate blocking)
curl localhost:4001/debug/vars | jq '.goroutines'
```

## Next Steps

- Implement [backup monitoring](05-backup-restore.md) to verify backup success
- Set up [performance tracking](09-performance.md) baselines
- Configure [security monitoring](08-security.md) for authentication failures
- Enable [CDC](11-cdc.md) for real-time analytics dashboards
