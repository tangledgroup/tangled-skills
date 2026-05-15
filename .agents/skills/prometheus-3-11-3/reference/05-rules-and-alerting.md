# Rules and Alerting

## Contents
- Rule Files
- Recording Rules
- Alerting Rules
- Rule Evaluation Lifecycle
- Alertmanager Integration
- Alert Relabeling
- Template Functions

## Rule Files

Rule files are referenced in the main Prometheus config:

```yaml
rule_files:
  - "rules/*.yml"
  - "/etc/prometheus/alerts/*.yml"
```

Globs are evaluated at load time. Files contain groups of rules:

```yaml
groups:
  - name: example-recording
    interval: 15s               # Override global evaluation_interval
    limit: 100                  # Max number of rules in group
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)

  - name: example-alerting
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{code=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}."
```

## Recording Rules

Recording rules precompute frequently-used or computationally expensive expressions, storing results as new time series.

**When to use**:
- Expressions used repeatedly across dashboards or alerts
- Complex queries that add significant load at query time
- Pre-aggregating data for faster dashboard rendering

**Naming convention**: `level:metric:operations`
- `level` — aggregation level (e.g., `instance`, `job`, `cluster`)
- `metric` — base metric name (strip `_total` when using `rate()`)
- `operations` — operations applied, newest first

### Recording Rule Examples

```yaml
# Per-instance request rate
- record: instance:http_requests:rate5m
  expr: rate(http_requests_total[5m])

# Aggregated to job level
- record: job:http_requests:rate5m
  expr: sum without (instance)(instance:http_requests:rate5m)

# Error ratio at instance level
- record: instance:http_errors_per_requests:ratio_rate5m
  expr: |
    rate(http_requests_total{code=~"5.."}[5m])
    /
    rate(http_requests_total[5m])

# Average latency from Summary
- record: instance:http_latency:mean5m
  expr: |
    rate(http_request_duration_seconds_sum[5m])
    /
    rate(http_request_duration_seconds_count[5m])
```

**Aggregation best practices**:
- Always specify `without` clause with labels being aggregated away
- Aggregate numerator and denominator separately, then divide for ratios
- Do not average ratios or averages — statistically invalid
- Use `avg()` only for non-ratio metrics

## Alerting Rules

Alerting rules define conditions that trigger alerts sent to Alertmanager.

### Alert Rule Structure

```yaml
- alert: TargetDown
  expr: up == 0
  for: 5m
  labels:
    severity: critical
    team: infrastructure
  annotations:
    summary: "Target {{ $labels.instance }} is down"
    description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."
    runbook_url: "https://runbooks.example.com/TargetDown"
```

**Fields**:
- `alert` — Required. Unique alert name within the group.
- `expr` — Required. PromQL expression returning an instant vector.
- `for` — Optional. Duration the condition must hold before firing (default: 0, fires immediately).
- `labels` — Optional. Additional labels attached to the alert.
- `annotations` — Optional. Key-value pairs sent to Alertmanager (summary, description, runbook_url, etc.).

### Alert States

| State | Description |
|-------|-------------|
| `unknown` | Rule not yet evaluated (v3.8.0+) |
| `pending` | Expression is true but `for` duration not yet met |
| `firing` | Condition has been true for the required `for` duration |

Prometheus stores alert state as `ALERTS{alertname="<name>", <labels>}` time series and sends firing alerts to the notifier. Resolved alerts continue being sent for 15 minutes after resolution.

### Alert Rule Examples

**High error rate**:
```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{code=~"5.."}[5m])) by (job)
    /
    sum(rate(http_requests_total[5m])) by (job)
    > 0.05
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High HTTP error rate on {{ $labels.job }}"
    description: "Error rate is {{ $value | humanizePercentage }} over 5m."
```

**Disk space running low**:
```yaml
- alert: DiskSpaceLow
  expr: |
    predict_linear(
      node_filesystem_avail_bytes{fstype!="tmpfs"}[6h],
      24 * 3600
    ) < 0
  for: 30m
  labels:
    severity: critical
  annotations:
    summary: "Disk full on {{ $labels.instance }}{{ $labels.mountpoint }}"
```

**Instance unreachable**:
```yaml
- alert: InstanceDown
  expr: |
    up == 0
    and on(instance) absent_over_time(scrape_samples_scraped[5m]) == 0
  for: 2m
  labels:
    severity: critical
```

**SLO burn rate (multi-window approach)**:
```yaml
- alert: SLOBurnRate1h
  expr: |
    sum(rate(http_requests_total{code=~"5.."}[1h])) by (job)
    /
    sum(rate(http_requests_total[1h])) by (job)
    > (1 - 0.999) * 14.4
  for: 2m
  labels:
    severity: critical
    slo: "api-availability"
```

## Rule Evaluation Lifecycle

Rules are evaluated every `evaluation_interval` (global default: 1 minute). Each group can override with its own `interval`.

**Evaluation order**:
1. Rules within a group are evaluated in file order
2. Groups are evaluated in the order they appear in the file
3. Multiple rule files are processed in the order listed in `rule_files`

**Rule evaluation process**:
1. PromQL expression is evaluated against current data
2. For alerting rules: result vector determines which alerts fire/pending
3. Alert state is tracked across evaluations (pending → firing after `for` duration)
4. Firing alerts are sent to notifier → Alertmanager
5. Recording rule results are written back to storage as new time series

## Alertmanager Integration

Prometheus sends alerts to Alertmanager via the configured alerting endpoints:

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
      scheme: http
      timeout: 10s
```

**How it works**:
- Prometheus evaluates alerting rules and sends active alerts to Alertmanager
- Alertmanager handles deduplication, grouping, silencing, inhibition, and notification routing
- Prometheus does not manage alert notifications — that is Alertmanager's role
- The notifier component in Prometheus decouples alert generation from dispatching

**Alertmanager discovery**: Alertmanager targets can use service discovery (Kubernetes, Consul, etc.) for dynamic routing:

```yaml
alerting:
  alertmanagers:
    - kubernetes_sd_configs:
        - role: pod
      relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app]
          regex: "alertmanager"
          action: keep
```

## Alert Relabeling

Applied to all alerts before sending to Alertmanager. Used for filtering or transforming alert labels:

```yaml
alerting:
  alert_relabel_configs:
    # Drop informational alerts
    - source_labels: [severity]
      regex: "info"
      action: drop
    # Add cluster label to all alerts
    - target_label: cluster
      replacement: "production-us-east"
      action: replace
```

## Template Functions

Alert annotations and labels support Go template functions:

| Function | Description |
|----------|-------------|
| `{{ $value }}` | Alert expression result value |
| `{{ $labels.<name> }}` | Label value from the alerting series |
| `{{ $externalLabels.<name> }}` | External label value |
| `humanize` | Format number with SI suffixes (e.g., 1.5M) |
| `humanizePercentage` | Format as percentage (e.g., 95%) |
| `humanizeTimestamp` | Format Unix timestamp as readable date |
| `humanizeTime` | Format duration in seconds as readable time |
| `humanizeDuration` | Format duration in a human-readable format |
| `strReplace` | String replacement: `{{ "hello" \| strReplace "l" "r" }}` → "herro" |
| `title` | Capitalize first letter of each word |
| `toUpper` / `toLower` | Case conversion |
| `urlQueryEscape` | URL-encode a string (v3.8.0+) |

**Example with templates**:
```yaml
annotations:
  summary: "High latency on {{ $labels.job }} ({{ $labels.instance }})"
  description: "95th percentile latency is {{ $value | humanizeDuration }}.\n  Value: {{ $value }}\n  Labels: {{ $labels }}"
```
