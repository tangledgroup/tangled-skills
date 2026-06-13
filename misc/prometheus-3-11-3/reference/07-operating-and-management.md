# Operating and Management

## Contents
- Command-Line Flags
- promtool
- Web API Endpoints
- Health and Readiness Probes
- Security Hardening
- Upgrading
- Docker Deployment

## Command-Line Flags

### Prometheus Server

```bash
prometheus --config.file=prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.listen-address=:9090 \
  --web.enable-lifecycle \
  --log.level=info
```

**Key flags**:

| Flag | Description | Default |
|------|-------------|---------|
| `--config.file` | Path to configuration file | `prometheus.yml` |
| `--storage.tsdb.path` | TSDB data directory | `./data/` |
| `--storage.agent.path` | Agent mode data directory | `./agent_data/` |
| `--web.listen-address` | Web UI and API listen address | `:9090` |
| `--web.read-timeout` | Maximum duration for reads | `5m` |
| `--web.max-connections` | Maximum simultaneous connections | `512` |
| `--web.enable-lifecycle` | Enable `/-/reload` and `/-/quit` endpoints | disabled |
| `--web.enable-admin-api` | Enable admin API (delete series, clean turds) | disabled |
| `--web.config.file` | Web server config (TLS, auth) | — |
| `--storage.tsdb.retention.time` | Time-based retention | `15d` |
| `--storage.tsdb.retention.size` | Size-based retention | — |
| `--storage.tsdb.wal-compression` | Compress WAL | true |
| `--enable-feature` | Enable experimental features (repeatable) | — |
| `--query.max-concurrency` | Max concurrent queries | 20 |
| `--query.max-samples` | Max samples in a query | 50,000,000 |
| `--query.timeout` | Maximum query execution time | `2m` |
| `--rules.alert.for-outage-tolerance` | Tolerance for alert `for` during outage | `1h` |
| `--rules.alert.for-grace-period` | Grace period for newly appearing alerts | `10m` |
| `--rules.rule-eval-delay` | Delay rule evaluation relative to cycle | `0s` |

**Agent mode flags**:
```bash
prometheus --storage.agent --config.file=prometheus-agent.yml
```

## promtool

`promtool` is a command-line utility for validating configs, testing rules, and inspecting TSDB data.

### Config Validation

```bash
# Validate configuration file
promtool check config prometheus.yml

# Validate rule files
promtool check rules alerts.yml

# Check soundness of config (warnings + errors)
promtool check config --strict prometheus.yml
```

### Rule Testing

```bash
# Run rule unit tests
promtool test rules test-rules.yml
```

Rule unit test format:
```yaml
tests:
  - interval: 1m
    input_series:
      - series: "http_requests_total{job=\"api\",code=\"200\"}"
        values: "100 200 300 400"
    promql: |
      sum(rate(http_requests_total[1m])) by (job)
    eval_time: 3m
    expected_series:
      - series: "SUM:rate:http_requests_total:1m BY job{job=\"api\"}"
        values: ["25"]
```

### TSDB Operations

```bash
# Dump TSDB contents
promtool tsdb dump /path/to/prometheus/data

# Analyze TSDB
promtool tsdb analyze /path/to/prometheus/data

# Dump series in JSON format (v3.9.0+)
promtool tsdb dump --format=seriesjson /path/to/prometheus/data
```

### Push Metrics (v3.8.0+)

```bash
# Push metrics to remote write endpoint
promtool push metrics --url=http://localhost:9090/api/v1/write metrics.txt

# With Remote Write 2.0 protobuf
promtool push metrics --protobuf-message --url=http://localhost:9090/api/v1/write metrics.txt
```

## Web API Endpoints

Base URL: `http://localhost:9090/api/v1/`

### Query Endpoints

| Endpoint | Description |
|----------|-------------|
| `/query` | Instant query | `?query=up` |
| `/query_range` | Range query | `?query=up&start=&end=&step=` |
| `/query_explain` | Explain a query plan | `?query=up` |
| `/query_index` | Query index stats | `?query=up` |

### Metadata and Labels

| Endpoint | Description |
|----------|-------------|
| `/labels` | List all label names |
| `/series` | List series matching matchers | `?match[]=up` |
| `/label/<name>/values` | Values for a specific label |
| `/label/<name>/values?match[]=...` | Values filtered by matchers |
| `/targets` | List scrape targets and health |
| `/targets/metadata` | Target metadata |
| `/targets/relabel_steps` | Relabeling steps per target |

### Rules and Alerts

| Endpoint | Description |
|----------|-------------|
| `/rules` | List all rule groups and rules |
| `/alerts` | List current alerts |

### TSDB and Status

| Endpoint | Description |
|----------|-------------|
| `/status/config` | Current server configuration |
| `/status/flags` | Command-line flags |
| `/status/tsdb` | TSDB stats |
| `/status/buildinfo` | Build information |
| `/status/async_workers` | Async worker stats |

### Admin Endpoints (requires `--web.enable-admin-api`)

| Endpoint | Description |
|----------|-------------|
| `POST /admin/tsdb/delete_series` | Delete series by matchers |
| `POST /admin/tsdb/clean_tombstones` | Remove tombstoned data |
| `POST /admin/tsdb/snapshot` | Create TSDB snapshot |

### Features Endpoint (v3.9.0+)

```
GET /api/v1/features
```

Returns which experimental features are enabled and supported capabilities.

### OpenAPI Specification (v3.10.0+)

```
GET /api/v1/openapi.yaml
```

OpenAPI 3.2 specification for the HTTP API.

## Health and Readiness Probes

| Endpoint | Description |
|----------|-------------|
| `/-/healthy` | Returns 200 when Prometheus is healthy |
| `/-/ready` | Returns 200 when Prometheus is ready (has loaded config and data) |
| `/-/reload` | Reload configuration (requires `--web.enable-lifecycle`) |
| `/-/quit` | Shut down Prometheus (requires `--web.enable-lifecycle`) |
| `/-/metrics` | Prometheus's own metrics |

**Kubernetes probe example**:
```yaml
livenessProbe:
  httpGet:
    path: /-/healthy
    port: 9090
readinessProbe:
  httpGet:
    path: /-/ready
    port: 9090
```

## Security Hardening

### Web Server Configuration

Use `--web.config.file` for TLS and authentication:

```yaml
# web-config.yml
tls_server_config:
  cert_file: /etc/ssl/prometheus.crt
  key_file: /etc/ssl/prometheus.key
  min_version: TLS13

basic_auth_users:
  admin: "$apr1$..."    # htpasswd-style hash

# Or use file-based credentials
basic_auth_users:
  admin:
    password_file: /etc/prometheus/admin-password
```

### Security Considerations

- **Do not expose** Prometheus directly to the internet without authentication
- Enable `--web.enable-admin-api` only when needed — it allows deleting data
- Use `--web.config.file` for TLS termination and basic auth
- v3.11.3 fixes multiple security issues:
  - AzureAD OAuth `client_secret` exposure via `/-/config` endpoint (CVE-2026-42151)
  - Remote-read snappy decode vulnerability (CVE-2026-42154)
  - Stored XSS in old UI heatmap chart (GHSA-fw8g-cg8f-9j28)
  - Stored XSS via unescaped metric names/labels (CVE-2026-40179)

### v3.10.0+ Distroless Docker Image

```bash
# Distroless variant — minimal base, UID/GID 65532, no VOLUME
docker run prom/prometheus:latest-distroless

# Busybox variant (default, backwards compatible)
docker run prom/prometheus:latest
```

## Upgrading

### Pre-Upgrade Checklist

1. Create a TSDB snapshot: `curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot`
2. Back up the data directory
3. Review changelog for breaking changes
4. Test new binary with `promtool check config prometheus.yml`
5. Verify feature flags compatibility

### Upgrade Process

```bash
# 1. Stop Prometheus gracefully
curl -X POST http://localhost:9090/-/quit
# Or send SIGTERM

# 2. Replace binary
cp prometheus-new /usr/local/bin/prometheus

# 3. Validate config with new binary
promtool check config prometheus.yml

# 4. Start with new binary
prometheus --config.file=prometheus.yml --storage.tsdb.path=/prometheus
```

TSDB format is generally backwards-compatible within major versions. Cross-major upgrades may require intermediate steps.

## Docker Deployment

### Basic Deployment

```bash
docker run -d \
  --name prometheus \
  -p 127.0.0.1:9090:9090 \
  -v /etc/prometheus:/etc/prometheus \
  -v /prometheus-data:/prometheus \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.enable-lifecycle
```

### Docker Compose

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.enable-lifecycle"
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    restart: unless-stopped

volumes:
  prometheus-data:
```

### Kubernetes (minimal)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: "prometheus"
        static_configs:
          - targets: ["localhost:9090"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest
          args:
            - "--config.file=/etc/prometheus/prometheus.yml"
            - "--storage.tsdb.path=/prometheus"
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: data
              mountPath: /prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: data
          emptyDir: {}
```

For production Kubernetes deployments, use the [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) which provides native Kubernetes CRDs for Prometheus, Alertmanager, and ServiceMonitor resources.
