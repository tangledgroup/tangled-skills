# RustFS Observability Guide

This reference covers monitoring, logging, tracing, and metrics collection for RustFS 1.0.0-alpha.93 using OpenTelemetry, Prometheus, Grafana, and distributed tracing.

## Overview

RustFS provides comprehensive observability features:

- **Metrics**: Prometheus-compatible metrics endpoint
- **Logging**: Structured logging with configurable levels and outputs
- **Tracing**: Distributed tracing via OpenTelemetry
- **Health Checks**: Built-in health endpoints for monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RustFS Instance                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Metrics  │  │   Logs   │  │  Traces  │                  │
│  │Exporter  │  │  Exporter│  │ Exporter │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       └─────────────┴─────────────┘                         │
│                      │                                      │
│              OpenTelemetry Protocol                         │
└──────────────────────┼──────────────────────────────────────┘
                       │
           ┌───────────▼───────────┐
           │  OTel Collector       │
           │  (receives all data)  │
           └───────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────────┐ ┌──▼───────┐ ┌───▼────────┐
│  Prometheus    │ │Grafana   │ │Tempo/Jaeger│
│  (metrics)     │ │(visual)  │ │(traces)    │
└────────────────┘ └──────────┘ └────────────┘
```

## Logging Configuration

### Log Levels

| Level | Use Case | Description |
|-------|----------|-------------|
| `trace` | Debugging | Most detailed logging, performance impact |
| `debug` | Development | Detailed debugging information |
| `info` | Production | Normal operational messages |
| `warn` | Minimal | Only warnings and above |
| `error` | Critical | Errors only |

### Configure Log Level

```bash
# Environment variable
export RUSTFS_OBS_LOGGER_LEVEL=info

# Docker
docker run -e RUSTFS_OBS_LOGGER_LEVEL=debug rustfs/rustfs:latest

# Systemd service (in /etc/rustfs/rustfs.env)
RUSTFS_OBS_LOGGER_LEVEL=info
```

### Log Output Destinations

#### stdout (Default)

```bash
# Logs to stdout (captured by Docker/systemd)
# No additional configuration needed
export RUSTFS_OBS_LOG_DIRECTORY=""
```

#### File Directory

```bash
# Log to file directory
export RUSTFS_OBS_LOG_DIRECTORY=/var/log/rustfs

# Docker volume mount
docker run -v /var/log/rustfs:/logs \
  -e RUSTFS_OBS_LOG_DIRECTORY=/logs \
  rustfs/rustfs:latest
```

#### Remote Endpoint (OpenTelemetry)

```bash
# Send logs to OTel collector
export RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
export RUSTFS_OBS_LOGGER_LEVEL=info
```

### Log Sampling

Reduce log volume in high-traffic environments:

```bash
# Sample 50% of logs
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=0.5

# Sample all logs (default)
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=1.0

# Sample 10% of logs
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=0.1
```

### Log Rotation

For file-based logging, configure logrotate:

**/etc/logrotate.d/rustfs:**
```bash
/var/log/rustfs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    size 100M
}
```

## Metrics Configuration

### Prometheus Metrics Endpoint

RustFS exposes metrics at `/metrics` endpoint:

```bash
# Access metrics directly
curl http://localhost:9000/metrics

# With authentication (if required)
curl -u rustfsadmin:rustfsadmin http://localhost:9000/metrics
```

### Key Metrics

#### Request Metrics

- `rustfs_requests_total`: Total number of HTTP requests (by method, status code)
- `rustfs_request_duration_seconds`: Request latency histogram
- `rustfs_request_size_bytes`: Request size distribution
- `rustfs_response_size_bytes`: Response size distribution

#### Storage Metrics

- `rustfs_buckets_count`: Number of buckets
- `rustfs_objects_count`: Total objects across all buckets
- `rustfs_usage_bytes`: Total storage used
- `rustfs_capacity_bytes`: Total storage capacity

#### Performance Metrics

- `rustfs_io_read_bytes_total`: Total bytes read from disk
- `rustfs_io_write_bytes_total`: Total bytes written to disk
- `rustfs_io_operations_total`: Total I/O operations
- `rustfs_concurrent_requests`: Current concurrent request count

#### Error Metrics

- `rustfs_errors_total`: Total errors (by type)
- `rustfs_heal_operations_total`: Healing operations performed
- `rustfs_bitrot_detections_total`: Bitrot detections

### Prometheus Configuration

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rustfs'
    static_configs:
      - targets: ['rustfs:9000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scheme: 'http'
    
  # For TLS-enabled RustFS
  - job_name: 'rustfs-tls'
    static_configs:
      - targets: ['rustfs:9000']
    metrics_path: '/metrics'
    scheme: 'https'
    tls_config:
      ca_file: '/etc/prometheus/certs/ca.crt'
```

### Grafana Dashboards

#### Import Dashboard

1. Access Grafana at `http://localhost:3000`
2. Go to Dashboards → Import
3. Upload RustFS dashboard JSON or use dashboard ID

#### Key Panels

**Overview Dashboard:**
- Request rate (requests/sec)
- Error rate (errors/sec)
- Storage usage gauge
- Active connections

**Performance Dashboard:**
- Request latency (p50, p95, p99)
- I/O throughput (MB/s)
- CPU and memory usage
- Disk I/O operations

**Storage Dashboard:**
- Bucket count over time
- Object count by bucket
- Storage capacity vs usage
- Top buckets by size

#### Custom Queries

```promql
# Request rate (last 5 minutes)
rate(rustfs_requests_total[5m])

# Error rate
rate(rustfs_errors_total[5m])

# P99 latency
histogram_quantile(0.99, rate(rustfs_request_duration_seconds_bucket[5m]))

# Storage usage percentage
rustfs_usage_bytes / rustfs_capacity_bytes * 100

# Top buckets by object count
topk(10, rustfs_objects_count)
```

## Distributed Tracing

### OpenTelemetry Collector Configuration

**otel-collector-config.yaml:**
```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

  prometheus:
    metrics:
      namespace: rustfs
    scrapers:
      - job_name: 'rustfs'
        static_configs:
          - targets: ['rustfs:9000']

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
    
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
      
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheus]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo, otlp/jaeger]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
```

### RustFS Tracing Configuration

```bash
# Enable tracing via OTel endpoint
export RUSTFS_OBS_ENDPOINT=http://otel-collector:4318

# Set service name for traces
export RUSTFS_OBS_SERVICE_VERSION=1.0.0-alpha.93

# Configure trace sampling
export RUSTFS_OBS_LOGGER_SAMPLE_RATIO=1.0  # Trace all requests
```

### Tempo Configuration

**tempo.yaml:**
```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318
        grpc:
          endpoint: 0.0.0.0:4317
    jaeger:
      protocols:
        thrift_http:
          endpoint: 0.0.0.0:14268
        grpc:
          endpoint: 0.0.0.0:14250

ingester:
  max_block_duration: 5m

storage:
  trace:
    backend: local
    wal:
      path: /var/tempo/wal
    local:
      path: /var/tempo/blocks

traceserver:
  http_server:
    http_listen_port: 14268
```

### Jaeger Configuration

**docker-compose service:**
```yaml
jaeger:
  image: jaegertracing/all-in-one:1.68.0
  ports:
    - "5775:5775/udp"
    - "6831:6831/udp"
    - "6832:6832/udp"
    - "5778:5778"
    - "16686:16686"  # Jaeger UI
    - "14268:14268"
  environment:
    - COLLECTOR_OTLP_ENABLED=true
```

### Viewing Traces

#### Tempo UI

Access at `http://localhost:3200`

1. Select time range
2. Filter by service name (rustfs)
3. Click on trace to view details
4. Analyze span durations and dependencies

#### Jaeger UI

Access at `http://localhost:16686`

1. Select service: rustfs
2. Set operation filter (optional)
3. Set duration range
4. Click "Find Traces"
5. Click on trace ID to view detailed span tree

### Trace Analysis

#### Common Trace Patterns

**Normal Request:**
```
[Client] → [RustFS S3 API] → [Object Storage] → [Response]
   ↓              ↓                  ↓
  5ms           45ms               10ms
Total: 60ms
```

**Slow Disk I/O:**
```
[Client] → [RustFS S3 API] → [Object Storage] → [Disk Read] → [Response]
   ↓              ↓                  ↓              ↓
  2ms           5ms               15ms          850ms
Total: 872ms (slow due to disk I/O)
```

**Healing Operation:**
```
[Background] → [Heal Scanner] → [Read Shards] → [Compare] → [Repair]
                    ↓                ↓             ↓           ↓
                   10ms            200ms        50ms       300ms
Total: 560ms (background operation)
```

## Health Checks

### Health Endpoints

#### S3 API Health

```bash
# Basic health check
curl -f http://localhost:9000/health

# Detailed health info
curl http://localhost:9000/minio.health/live

# Readiness check
curl http://localhost:9000/minio.health/ready
```

#### Console Health

```bash
# Console health check
curl -f http://localhost:9001/rustfs/console/health
```

### Kubernetes Probes

**Deployment configuration:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rustfs
spec:
  template:
    spec:
      containers:
        - name: rustfs
          image: rustfs/rustfs:1.0.0-alpha.93
          ports:
            - containerPort: 9000
            - containerPort: 9001
          livenessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 40
            periodSeconds: 30
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /minio.health/ready
              port: 9000
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
```

### Docker Healthcheck

**docker-compose.yml:**
```yaml
services:
  rustfs:
    image: rustfs/rustfs:latest
    healthcheck:
      test:
        [
          "CMD",
          "sh",
          "-c",
          "curl -f http://127.0.0.1:9000/health && curl -f http://127.0.0.1:9001/rustfs/console/health"
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Alerting Configuration

### Prometheus Alert Rules

**rustfs-alerts.yml:**
```yaml
groups:
  - name: rustfs
    rules:
      # High error rate
      - alert: RustFSErrorRateHigh
        expr: rate(rustfs_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on RustFS"
          description: "Error rate is {{ $value }} errors/sec (threshold: 0.1)"

      # High latency
      - alert: RustFSLatencyHigh
        expr: histogram_quantile(0.95, rate(rustfs_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency on RustFS"
          description: "P95 latency is {{ $value }}s (threshold: 1s)"

      # Storage capacity
      - alert: RustFSCapacityLow
        expr: (rustfs_usage_bytes / rustfs_capacity_bytes) * 100 > 85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Storage capacity low on RustFS"
          description: "Storage usage is {{ $value }}% (threshold: 85%)"

      # Disk I/O errors
      - alert: RustFSDiskIOErrors
        expr: increase(rustfs_io_errors_total[5m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk I/O errors on RustFS"
          description: "Detected {{ $value }} I/O errors in last 5 minutes"

      # Instance down
      - alert: RustFSInstanceDown
        expr: up{job="rustfs"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "RustFS instance is down"
          description: "RustFS instance {{ $labels.instance }} has been down for more than 1 minute"
```

### Alertmanager Configuration

**alertmanager.yml:**
```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@example.com'
        send_resolved: true
        
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
        channel: '#alerts'
        send_resolved: true
        title: '{{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Value:* {{ .Value }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

## Complete Observability Stack

### Docker Compose Setup

**docker-compose-observability.yml:**
```yaml
version: '3.8'

services:
  rustfs:
    image: rustfs/rustfs:1.0.0-alpha.93
    container_name: rustfs
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - RUSTFS_VOLUMES=/data/rustfs{0..3}
      - RUSTFS_ACCESS_KEY=rustfsadmin
      - RUSTFS_SECRET_KEY=rustfsadmin
      - RUSTFS_CONSOLE_ENABLE=true
      - RUSTFS_OBS_LOGGER_LEVEL=info
      - RUSTFS_OBS_ENDPOINT=http://otel-collector:4318
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    networks:
      - observability
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.115.0
    container_name: otel-collector
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/otel-collector.yml:ro
    command: ["--config=/etc/otelcol-contrib/otel-collector.yml"]
    ports:
      - "4317:4317"
      - "4318:4318"
      - "8888:8888"
    networks:
      - observability

  prometheus:
    image: prom/prometheus:v2.52.0
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
    ports:
      - "9090:9090"
    networks:
      - observability

  grafana:
    image: grafana/grafana:11.2.0
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - observability
    depends_on:
      - prometheus

  tempo:
    image: grafana/tempo:2.5.1
    container_name: tempo
    user: "10001"
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml:ro
      - tempo_data:/var/tempo
    command: ["-config.file=/etc/tempo.yaml"]
    ports:
      - "3200:3200"
      - "4317"
      - "4318"
    networks:
      - observability

volumes:
  prometheus_data:
  grafana_data:
  tempo_data:

networks:
  observability:
    driver: bridge
```

### Start Observability Stack

```bash
# Create directory structure
mkdir -p data logs

# Set permissions
chown -R 10001:10001 data

# Start all services
docker compose -f docker-compose-observability.yml up -d

# View logs
docker compose logs -f rustfs

# Check status
docker compose ps
```

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| RustFS S3 API | http://localhost:9000 | rustfsadmin/rustfsadmin |
| RustFS Console | http://localhost:9001 | rustfsadmin/rustfsadmin |
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3000 | admin/admin |
| Tempo | http://localhost:3200 | None |

## Performance Monitoring

### Key Performance Indicators (KPIs)

#### Throughput

- **Requests per second**: Target > 1000 req/s for production
- **Data throughput**: Target > 100 MB/s for data lake workloads
- **IOPS**: Monitor disk I/O operations per second

#### Latency

- **P50 latency**: Should be < 10ms for small objects
- **P95 latency**: Should be < 50ms for small objects
- **P99 latency**: Should be < 100ms for small objects

#### Reliability

- **Error rate**: Should be < 0.1% of total requests
- **Availability**: Target > 99.9% uptime
- **Heal operations**: Monitor for data integrity issues

### Capacity Planning

```promql
# Storage growth rate (bytes per day)
increase(rustfs_usage_bytes[24h])

# Predict when storage will reach 80% capacity
(rustfs_capacity_bytes * 0.8 - rustfs_usage_bytes) / increase(rustfs_usage_bytes[24h]) * 86400

# Request rate trend
rate(rustfs_requests_total[1h])
```

## Troubleshooting Observability

### Metrics Not Appearing

```bash
# Check if metrics endpoint is accessible
curl http://localhost:9000/metrics

# Verify Prometheus can scrape RustFS
curl http://prometheus:9090/api/v1/targets

# Check OTel collector logs
docker logs otel-collector
```

### Traces Not Showing

```bash
# Verify OTel endpoint configuration
docker exec rustfs env | grep RUSTFS_OBS

# Test OTel connection
curl -X POST http://otel-collector:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{}'

# Check Tempo logs
docker logs tempo
```

### High Cardinality Issues

```bash
# Monitor label cardinality
# In Grafana, query: count(rustfs_requests_total)

# If high, consider reducing label dimensions
# Avoid using request IDs or other unique values as labels
```

See [`06-troubleshooting.md`](06-troubleshooting.md) for detailed troubleshooting procedures.
