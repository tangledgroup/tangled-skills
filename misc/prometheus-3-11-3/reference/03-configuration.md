# Configuration Reference

## Contents
- Configuration File Structure
- Global Configuration
- Runtime Configuration
- OTLP Configuration
- Scrape Configuration
- Alerting Configuration
- Rule Files
- Remote Read/Write
- TSDB and Storage Configuration
- Feature Flags

## Configuration File Structure

Prometheus uses a YAML configuration file specified via `--config.file`. The top-level structure:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

runtime:
  go_gc_ratio: 100

otlp:
  translation_strategy: NoUTF8EscapingWithSuffixes

storage:
  tsdb:
    retention.time: 15d
    retention.size: 50GB

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

remote_write:
  - url: "http://remote-storage:9090/api/v1/write"

remote_read:
  - url: "http://remote-storage:9090/api/v1/read"
```

Configuration is reloaded on `SIGHUP` or via `/-/reload` API endpoint without restarting the server.

## Global Configuration

```yaml
global:
  scrape_interval: 15s          # How often to scrape targets
  scrape_timeout: 10s           # Max time per scrape (capped at scrape_interval)
  evaluation_interval: 15s      # How often to evaluate rules
  scrape_protocols:             # Preferred scrape protocols (order matters)
    - PrometheusProto
    - OpenMetricsText1.0.0
    - PrometheusText0.0.4
  http_sd_configs:              # Global HTTP-based SD for alertmanagers
  external_labels:              # Labels added to all time series
    cluster: "production"
    region: "us-east-1"
  scrape_native_histograms: true        # Enable native histogram ingestion (stable v3.9+)
  convert_classic_histograms_to_nhcb: false  # Convert classic → NHCB
  always_scrape_classic_histograms: false   # Always scrape classic alongside native
  extra_scrape_metrics: false               # Expose scrape metadata metrics
  metric_name_validation_scheme: UTF8Validation  # UTF8 or Legacy
  metric_name_escaping_scheme: AllowUTF8      # AllowUTF8, Underscores, Dots
```

**External labels**: Added to every time series scraped or created by rules. Used for federation identification and remote write tagging. Supports environment variable expansion via `${VAR}` syntax.

## Runtime Configuration

```yaml
runtime:
  go_gc_ratio: 100    # Go runtime GC target percentage (default: auto)
```

Controls Go garbage collector aggressiveness. Lower values trigger GC more frequently, reducing heap size at CPU cost.

## OTLP Configuration

Prometheus accepts OpenTelemetry data via the OTLP receiver:

```yaml
otlp:
  translate_using_prometheus_compact_name: false
  keep_identifying_resource_attributes: true
  promote_resource_attributes:
    - service.name
    - deployment.environment
  translation_strategy: NoUTF8EscapingWithSuffixes
  metric_suffix_list_mode: suffixed
```

**Translation strategies**:
- `NoUTF8EscapingWithSuffixes` — No escaping, adds type/unit suffixes
- `UnderscoreEscapingWithSuffixes` — Underscore escaping, adds suffixes
- `UnderscoreEscapingWithoutSuffixes` — Underscore escaping, no suffixes
- `NoTranslation` — Pass through as-is (requires UTF8 validation)

OTLP receiver listens on port 4318 (HTTP) and 4317 (gRPC) by default.

## Scrape Configuration

Each `scrape_configs` entry defines a job:

```yaml
scrape_configs:
  - job_name: "my-app"
    scrape_interval: 30s           # Override global
    scrape_timeout: 10s
    metrics_path: /metrics          # Default: /metrics
    scheme: http                    # http or https
    honor_labels: false             # Keep target labels over clash
    honor_timestamps: true          # Use timestamps from target
    follow_redirects: true
    enable_http2: true
    basic_auth:                     # Basic authentication
      username: "user"
      password: "secret"
    authorization:                  # Bearer token auth
      type: Bearer
      credentials: "token"
    tls_config:                     # TLS settings
      ca_file: /etc/ssl/cert.pem
      cert_file: /etc/ssl/client.crt
      key_file: /etc/ssl/client.key
      insecure_skip_verify: false

    # Service Discovery
    static_configs:
      - targets: ["localhost:9090", "localhost:9091"]
        labels:
          env: "production"
    file_sd_configs:
      - files:
          - "/etc/prometheus/targets/*.json"
        refresh_interval: 5m
    kubernetes_sd_configs:
      - role: pod

    # Relabeling
    relabel_configs:
      - source_labels: [__address__]
        target_label: __address__
        regex: "(.+):.*"
        replacement: "${1}:9100"
        action: replace

    metric_relabel_configs:
      - source_labels: [__name__]
        regex: "go_.*"
        action: drop
```

**Key fields**:
- `job_name` — Required, unique identifier. Added as `job` label to all scraped series.
- `honor_labels` — When true, target's own labels take precedence over scrape-config labels during conflicts.
- `scrape_protocols` — Per-job protocol preference override.

## Alerting Configuration

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
      scheme: http
      basic_auth:
        username: "user"
        password: "secret"
      # Service discovery for alertmanagers
      kubernetes_sd_configs:
        - role: service
      relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          regex: "alertmanager"
          action: keep
  alert_relabel_configs:
    - source_labels: [alertname]
      regex: "Info.*"
      action: drop
```

Alert relabeling is applied to all alerts before sending to Alertmanager.

## Rule Files

```yaml
rule_files:
  - "rules/*.yml"
  - "/etc/prometheus/alerts.yml"
```

Globs are evaluated at load time. Rules are reloaded on config reload.

## Remote Read/Write

### Remote Write

```yaml
remote_write:
  - url: "http://remote-storage:9090/api/v1/write"
    name: "default"
    send_native_histograms: true
    remote_timeout: 30s
    retry_on_http_429: true
    queue_config:
      capacity: 10000
      min_shards: 1
      max_shards: 50
      max_samples_per_send: 5000
      batch_send_deadline: 5s
    basic_auth:
      username: "user"
      password: "secret"
    tls_config:
      ca_file: /etc/ssl/ca.pem
    write_relabel_configs:
      - source_labels: [__name__]
        regex: "temp_.*"
        action: drop
```

### Remote Read

```yaml
remote_read:
  - url: "http://remote-storage:9090/api/v1/read"
    read_recent: true
    required_matchers:
      cluster: "production"
```

`read_recent: true` enables reading recent data from remote storage (otherwise only used for historical queries beyond local retention).

## TSDB and Storage Configuration

```yaml
storage:
  tsdb:
    retention.time: 15d          # Time-based retention
    retention.size: 50GB         # Size-based retention
    retention.percentage: 80     # Max % of disk usable (v3.11.0+)
    out_of_order_time_window: 0s # Accept out-of-order samples within window
```

Both time and size retention can be set simultaneously — whichever is hit first triggers compaction. When both are removed from config, CLI flag values are used as fallback.

## Feature Flags

Enable experimental features via command line:

```bash
prometheus --config.file=prometheus.yml \
  --enable-feature=fast-startup \
  --enable-feature=st-storage \
  --enable-feature=xor2-encoding
```

**Available feature flags (v3.11.x)**:
- `fast-startup` — Writes `series_state.json` to WAL for faster restart recovery
- `st-storage` — Stores ingested start timestamps in TSDB, exposes via Remote Write 2.0
- `xor2-encoding` — New TSDB block float sample chunk encoding optimized for scraped data
- `promql-duration-expr` — Duration expressions in PromQL
- `promql-experimental-functions` — Experimental PromQL functions
- `extended-attribute` — Extended attribute support
- `auto-reload-config` — Automatic config file watching

## Agent Mode

Run Prometheus in agent mode for metrics collection without local storage:

```bash
prometheus --config.file=prometheus-agent.yml --storage.agent
```

Agent mode disables: alerting, rule evaluation, remote read. Only scrape and remote write are available. Use with `documentation/examples/prometheus-agent.yml` as starting point.
