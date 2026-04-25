---
name: opentelemetry-collector-1-56-0
description: Complete toolkit for OpenTelemetry Collector 1.56 covering configuration, deployment patterns (agent/gateway), pipelines with receivers-processors-exporters, internal telemetry monitoring, OpAMP fleet management, custom distribution building with OCB, TLS/mTLS security, and YAML-based pipeline orchestration. Use when deploying vendor-agnostic telemetry collection infrastructure, configuring OTLP trace/metric/log pipelines, or managing collector fleets at scale.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.56.0"
tags:
  - observability
  - tracing
  - metrics
  - logging
  - otel
  - telemetry
  - collector
  - opamp
category: observability
external_references:
  - https://github.com/open-telemetry/opentelemetry-collector
  - https://github.com/open-telemetry/opamp
  - https://github.com/open-telemetry/opentelemetry-collector-contrib
  - https://github.com/open-telemetry/opentelemetry-collector/tree/main/cmd/builder
  - https://opentelemetry.io/docs/collector/
  - https://opentelemetry.io/docs/collector/quick-start/
---
## Overview
The OpenTelemetry Collector is a vendor-agnostic implementation for receiving, processing, and exporting telemetry data (traces, metrics, and logs). It removes the need to run multiple agents/collectors and provides scalability, protocol support, and extensibility. The collector can be deployed as an agent (sidecar/daemon) or as a gateway service.

## When to Use
- Deploying telemetry collection infrastructure for traces, metrics, and logs
- Configuring OTLP receivers/exporters for application instrumentation pipelines
- Setting up agent or gateway deployment patterns in Kubernetes or VMs
- Building custom collector distributions with OCB (OpenTelemetry Collector Builder)
- Managing fleets of collectors via OpAMP protocol
- Monitoring collector health through internal telemetry metrics
- Adding TLS/mTLS security to receiver and exporter endpoints

## Core Concepts
### Pipeline Architecture

Data flows through pipelines: **Receivers → Processors → Exporters**. Each pipeline handles one signal type (traces, metrics, or logs). The same receiver can feed multiple pipelines; the same exporter can receive from multiple pipelines.

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp_grpc]
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_grpc]
```

### Component Types

| Type | Role | Examples |
|------|------|----------|
| **Receivers** | Collect telemetry from sources | `otlp`, `jaeger`, `zipkin`, `prometheus`, `hostmetrics`, `fluentforward`, `kafka` |
| **Processors** | Transform/filter/enrich data | `memory_limiter`, `batch`, `attributes`, `filter`, `resource`, `transform`, `probabilistic_sampler` |
| **Exporters** | Send to backends | `otlp_grpc`, `otlp_http`, `debug`, `prometheus`, `prometheusremotewrite`, `jaeger`, `kafka`, `file`, `zipkin` |
| **Connectors** | Join two pipelines (export+receiver) | `spanmetrics`, `count` |
| **Extensions** | Non-telemetry capabilities | `health_check`, `pprof`, `zpages`, `oidc`, `oauth2client` |

### Deployment Patterns

**Agent pattern**: Collector runs alongside application (sidecar/daemonset). Each app sends to its local collector. Simple, one-to-one mapping. Limited scalability for large teams.

**Gateway pattern**: Centralized collectors receive from agents/apps and forward to backends. Separation of concerns, centralized credentials/policy. Use load-balancing exporter or external LB (NGINX) for distribution. Can use two-tier with tail sampling processor.

### Configuration Structure

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 5s
    limit_mib: 4000
    spike_limit_mib: 500
  batch: {}

exporters:
  otlp_grpc:
    endpoint: backend:4317
    tls:
      insecure: true

extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  zpages:
    endpoint: 0.0.0.0:55679

service:
  extensions: [health_check, zpages]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp_grpc]
```

### Key Processors

- **`memory_limiter`**: Protects collector from OOM with `check_interval`, `limit_mib`, `spike_limit_mib`
- **`batch`**: Batches telemetry for efficient export; configure `send_batch_size`, `timeout`, `max_batch_size`
- **`attributes`**: Insert/update/delete/uppercase/lowercase attributes via `actions`
- **`filter`**: Filter spans/metrics/logs by conditions (supports span, spanevent, metric, datapoint, log_record)
- **`resource`**: Add/modify/delete resource attributes with `from_attribute` support
- **`transform`**: Execute statements against telemetry using CEL expressions (`trace_statements`, `metric_statements`, `log_statements`)
- **`probabilistic_sampler`**: Sample traces by percentage with optional `hash_seed`
- **`k8sattributes`**: Enrich telemetry with Kubernetes metadata (pods, nodes, namespaces)

### Security & TLS

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: /path/to/cert.pem
          key_file: /path/to/key.pem
          client_ca_file: /path/to/ca.pem  # for mTLS

exporters:
  otlp_grpc:
    endpoint: backend:4317
    tls:
      ca_file: /path/to/ca.pem
      cert_file: /path/to/client-cert.pem  # mTLS client cert
      key_file: /path/to/client-key.pem
```

Common TLS settings: `ca_file`, `cert_file`, `key_file`, `client_ca_file`, `insecure`, `insecure_skip_verify`, `min_version`, `max_version`, `reload_interval`.

### Authentication

Uses the extensions mechanism. Add authenticator extension under `.extensions`, reference in `.service.extensions`, then attach to receiver/exporter config:

```yaml
extensions:
  oidc:
    issuer_url: http://auth-server/realms/opentelemetry
    audience: collector

receivers:
  otlp/auth:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        auth:
          authenticator: oidc
```

### Internal Telemetry

The Collector exposes its own observability:
- **Metrics**: Prometheus at `http://127.0.0.1:8888/metrics` (default)
- **Logs**: Emitted to `stderr` by default
- **Traces**: Experimental, must be explicitly enabled

Configure via `service.telemetry.metrics` and `service.telemetry.logs`. Metric verbosity levels: `none`, `basic`, `normal` (default), `detailed`.

Key metrics include `otelcol_receiver_accepted_*`, `otelcol_receiver_refused_*`, `otelcol_exporter_sent_*`, `otelcol_exporter_send_failed_*`, `otelcol_process_uptime`, `otelcol_process_memory_rss`.

### Distributions

| Distribution | Use Case |
|-------------|----------|
| `otelcol` (Core) | Minimal set of core components |
| `otelcol-contrib` | Full set including community-maintained components |
| `otelcol-k8s` | Kubernetes-specific extensions and detectors |
| `otelcol-otlp` | Focused on OTLP protocol support |
| `otelcol-ebpf-profiler` | eBPF-based profiling support |

Custom distributions can be built with **OCB** (OpenTelemetry Collector Builder).

### OpAMP Management

The Open Agent Management Protocol (OpAMP) enables centralized fleet management:
- Remote configuration updates
- Health reporting and monitoring
- Agent lifecycle management (upgrade/downgrade)
- Own metrics/traces/log reporting to control plane

Use `opampsupervisor` binary to run collector under OpAMP supervision.

## Installation / Setup
### Docker (Quick Start)
```bash
docker pull otel/opentelemetry-collector:1.56.0
docker run -p 4317:4317 -p 4318:4318 -p 55679:55679 \
  otel/opentelemetry-collector:1.56.0
```

### Binary Installation
Download from [GitHub releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases/latest).

### Build from Source
```bash
git clone https://github.com/open-telemetry/opentelemetry-collector.git
cd opentelemetry-collector
make install-tools
make otelcorecol
```

### Custom Distribution with OCB
1. Download `ocb` binary for your platform
2. Create `builder-config.yaml`:
```yaml
dist:
  name: my-otelcol
  description: My custom collector
  output_path: ./my-otelcol
receivers:
  - gomod: go.opentelemetry.io/collector/receiver/otlpreceiver v0.xxx.0
processors:
  - gomod: go.opentelemetry.io/collector/processor/batchprocessor v0.xxx.0
exporters:
  - gomod: go.opentelemetry.io/collector/exporter/otlpexporter v0.xxx.0
```
3. Run `./ocb --config builder-config.yaml`

## Usage Examples
### Basic OTLP Pipeline (Traces + Metrics + Logs)
See Configuration Structure above for complete example.

### Host Metrics Scraping
```yaml
receivers:
  hostmetrics:
    scrapers:
      enabled: [cpu, memory, disk, network, load, filesystem, process]

service:
  pipelines:
    metrics:
      receivers: [hostmetrics]
      exporters: [prometheusremotewrite]
```

### Filtering Sensitive Data
```yaml
processors:
  attributes/example:
    actions:
      - key: password
        action: delete
      - key: email
        action: hash
      - key: environment
        value: production
        action: insert
```

### Multi-Pipeline with Same Receiver
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

service:
  pipelines:
    traces/prod:
      receivers: [otlp]
      processors: [memory_limiter]
      exporters: [otlp_grpc/prod]
    traces/dev:
      receivers: [otlp]
      processors: [probabilistic_sampler]
      exporters: [debug]
```

### Gateway with Load Balancing Exporter
```yaml
exporters:
  loadbalancing:
    protocol:
      otlp:
        tls:
          insecure: true
    resolver:
      dns:
        hostname: collectors.example.com
        port: 4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [loadbalancing]
```

### Internal Telemetry Configuration
```yaml
service:
  telemetry:
    metrics:
      readers:
        - pull:
            exporter:
              prometheus:
                host: '0.0.0.0'
                port: 8888
      level: detailed
    logs:
      level: DEBUG
      encoding: json
      output_paths: [stderr, /var/log/otel-collector.log]
```

## Advanced Topics
## Advanced Topics

- [Receivers](reference/01-receivers.md)
- [Processors](reference/02-processors.md)
- [Exporters](reference/03-exporters.md)
- [Deployment Patterns](reference/04-deployment-patterns.md)

