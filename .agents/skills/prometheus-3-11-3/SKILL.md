---
name: prometheus-3-11-3
description: Complete toolkit for Prometheus 3.11.3 covering configuration, PromQL querying, service discovery, rules, alerting, and storage. Use when deploying or configuring Prometheus servers, writing PromQL queries, setting up scrape configs and service discovery, authoring recording or alerting rules, tuning TSDB retention, integrating with Alertmanager, or managing remote read/write endpoints.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - prometheus
  - monitoring
  - promql
  - metrics
  - alerting
  - tsdb
  - service-discovery
category: tooling
external_references:
  - https://github.com/prometheus/prometheus/tree/v3.11.3
  - https://prometheus.io/docs/introduction/overview/
---

# Prometheus 3.11.3

## Overview

Prometheus is an open-source systems and service monitoring system. It collects metrics from configured targets at given intervals, evaluates rule expressions, displays results, and can trigger alerts when specified conditions are observed. Key distinguishing features:

- **Multi-dimensional data model**: Time series identified by metric name plus key/value label pairs
- **PromQL**: Powerful query language that leverages dimensional data
- **Autonomous single-server nodes**: No dependency on distributed storage
- **Pull-based collection**: HTTP pull model for time series scraping
- **Push support via gateway**: Pushgateway for short-lived batch jobs
- **Service discovery**: Dynamic target discovery via multiple SD mechanisms or static configuration
- **Native histograms**: Stable since v3.9, with NHCB (Custom Bucket) support

The Prometheus ecosystem includes the main server, client libraries, pushgateway, exporters, Alertmanager, and various support tools. Most components are written in Go.

## When to Use

- Deploying or configuring a Prometheus server instance
- Writing or debugging PromQL queries
- Setting up scrape configurations with service discovery
- Authoring recording rules or alerting rules
- Configuring remote read/write for long-term storage
- Tuning TSDB retention and storage settings
- Integrating Prometheus with Alertmanager for alert routing
- Debugging relabeling or target discovery issues
- Migrating configurations between Prometheus versions

## Core Concepts

**Time Series**: Streams of timestamped values belonging to the same metric and label set. Every data point in Prometheus is a time series.

**Metric Name + Labels**: Each time series is uniquely identified by its metric name (e.g., `http_requests_total`) and optional key/value labels (e.g., `{method="POST", handler="/api"}`). Label changes create new time series.

**Jobs and Instances**: A *job* is a logical group of targets serving the same purpose. An *instance* uniquely identifies a single target within a job (typically `host:port`).

**Samples**: Each sample is a float64 value (or native histogram) with millisecond-precision timestamp.

**Scraping**: Prometheus periodically pulls metrics from targets via HTTP at `/metrics`. Default scrape interval is 1 minute.

**Rules**: Recording rules precompute expensive expressions; alerting rules generate alerts sent to Alertmanager.

### Quick Configuration Example

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts.yml"
  - "records.yml"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
```

### Quick PromQL Examples

```promql
# Instant vector — current values
up{job="prometheus"}

# Range vector — last 5 minutes of data
http_requests_total{method="GET"}[5m]

# Rate of requests per second
rate(http_requests_total{method="GET"}[5m])

# Aggregation — total across all instances
sum(rate(http_requests_total[5m])) by (job)

# Histogram quantile (95th percentile latency)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Starting Prometheus

```bash
./prometheus --config.file=prometheus.yml
```

Web UI and API available at `http://localhost:9090`. Metrics endpoint at `http://localhost:9090/metrics`.

## Advanced Topics

**Data Model and Metric Types**: Time series, labels, samples, Counter/Gauge/Histogram/Summary, native histograms → [Data Model and Metric Types](reference/01-data-model-and-metrics.md)

**PromQL Querying**: Expression types, operators, functions, aggregation, matching modifiers, `@` timestamps → [PromQL Querying](reference/02-promql-querying.md)

**Configuration Reference**: YAML config structure, global settings, scrape configs, OTLP config, runtime tuning → [Configuration Reference](reference/03-configuration.md)

**Service Discovery and Relabeling**: SD mechanisms (static, file, Kubernetes, Docker, AWS, Azure, etc.), target and metric relabeling actions → [Service Discovery and Relabeling](reference/04-service-discovery-and-relabeling.md)

**Rules and Alerting**: Recording rules, alerting rules, alertmanager integration, rule evaluation lifecycle → [Rules and Alerting](reference/05-rules-and-alerting.md)

**Storage and Retention**: TSDB architecture, compaction, retention policies, remote read/write, federation → [Storage and Retention](reference/06-storage-and-retention.md)

**Operating and Management**: Command-line flags, `promtool`, web API endpoints, security hardening, upgrading → [Operating and Management](reference/07-operating-and-management.md)
