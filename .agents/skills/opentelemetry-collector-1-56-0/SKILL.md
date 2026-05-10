---
name: opentelemetry-collector-1-56-0
description: Vendor-agnostic telemetry collector for OpenTelemetry providing configurable pipelines for traces, metrics, and logs. Supports agent/gateway patterns, OpAMP fleet management, and custom distributions. Use when deploying observability infrastructure, configuring OTLP data collection, managing collector fleets, or implementing production-ready telemetry with retries and batching.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - opentelemetry
  - collector
  - observability
  - telemetry
  - tracing
  - metrics
  - logs
  - opamp
  - otlp
  - pipelines
category: observability
external_references:
  - https://github.com/open-telemetry/opentelemetry-collector
  - https://github.com/open-telemetry/opamp
  - https://github.com/open-telemetry/opentelemetry-collector-contrib
  - https://github.com/open-telemetry/opentelemetry-collector/tree/main/cmd/builder
  - https://opentelemetry.io/docs/collector/
  - https://opentelemetry.io/docs/collector/quick-start/
---

# OpenTelemetry Collector 1.56.0

## Overview

The OpenTelemetry Collector offers a vendor-agnostic implementation for receiving,
processing, and exporting telemetry data. It removes the need to run, operate,
and maintain multiple agents or collectors across an observability stack. The
Collector works with open-source observability data formats (Jaeger, Prometheus,
Fluent Bit, Zipkin, etc.) and can send to one or more open-source or commercial
backends.

The Collector is a single Go binary that operates as a pipeline-based data
processor. It supports three telemetry signal types: **traces**, **metrics**,
and **logs**. Each signal flows through configurable pipelines composed of
receivers, processors, exporters, and connectors.

**Key objectives:**

- **Usability** — reasonable default configuration, supports popular protocols,
  runs and collects out of the box
- **Performance** — highly stable and performant under varying loads
- **Observability** — an exemplar of an observable service with rich internal
  telemetry
- **Extensibility** — customizable without touching core code via components
- **Unification** — single codebase deployable as agent or gateway

## When to Use

- Deploying vendor-agnostic telemetry collection infrastructure
- Configuring OTLP trace, metric, and log pipelines
- Managing collector fleets at scale with OpAMP
- Building custom collector distributions with ocb
- Implementing production-ready observability with retries, batching, encryption,
  and sensitive data filtering
- Consolidating multiple telemetry formats (Jaeger, Prometheus, Zipkin) into
  unified OTLP pipelines
- Setting up agent or gateway deployment patterns in Kubernetes or bare metal

## Core Concepts

### Telemetry Signals

The Collector processes three types of telemetry signals:

- **Traces** — distributed request tracing data (spans with trace IDs)
- **Metrics** — numerical measurements over time (counters, gauges, histograms)
- **Logs** — timestamped event records with structured or unstructured data

### Pipeline Architecture

A pipeline defines the path that data follows through the Collector: from
reception, through optional processing, to export. Each pipeline is typed
(traces, metrics, or logs) and consists of:

- **Receivers** — collect telemetry from sources (push-based like OTLP,
  pull-based like Prometheus scrapers)
- **Processors** — transform, filter, sample, or enrich telemetry data
- **Exporters** — send telemetry to observability backends
- **Connectors** — bridge two pipelines, acting as both exporter and receiver

Data flows: `Receivers → Processors (chain) → Fan-out → Exporters`

Multiple receivers feed into the first processor. Processors chain sequentially.
The last processor uses a fan-out consumer to send data copies to all exporters
in the pipeline.

### Component Model

Components are identified by `type[/name]` format. For example, `otlp`,
`otlp/2`, or `batch/custom`. Components of the same type can be defined multiple
times with unique identifiers. The five component classes are:

- **Receivers** — ingest data (e.g., otlp, jaeger, prometheus, zipkin, kafka)
- **Processors** — transform data (e.g., batch, memory_limiter, transform,
  probabilistic_sampler)
- **Exporters** — output data (e.g., otlp, prometheusremotewrite, file, debug)
- **Connectors** — route between pipelines (e.g., spanmetrics, servicegraph)
- **Extensions** — add capabilities without accessing telemetry (e.g.,
  health_check, pprof, zpages, file_storage)

### Distributions

The OpenTelemetry project provides official distributions:

- **Core** (`otel/opentelemetry-collector`) — minimal set of components
- **Contrib** (`otel/opentelemetry-collector-contrib`) — extensive component
  library including most receivers, processors, and exporters
- **Kubernetes** (`otelcol-k8s`) — Kubernetes-focused distribution
- **eBPF Profiling** (`otelcol-ebpf-profiler`) — eBPF-based profiling
- **OTLP** (`otelcol-otlp`) — OTLP-only lightweight distribution

Third-party distributions exist from AWS (ADOT), Datadog (DDOT), Dynatrace,
Elastic (EDOT), Grafana (Alloy), New Relic (NRDOT), Splunk, Sumo Logic, and
others.

### Configuration Structure

Collector configuration is YAML-based with the following top-level sections:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  otlp:
    endpoint: backend:4317
    sending_queue:
      queue_size: 5000
    retry_on_failure:
      max_elapsed_time: 10m

extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679

service:
  extensions: [health_check, pprof, zpages]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

### Configuration Providers

The `--config` flag supports multiple configuration providers via URI schemes:

- `file:` — read from a file path
- `env:` — read from an environment variable
- `yaml:` — inline YAML string with `::` delimiter for nested keys
- `http:` / `https:` — read from HTTP/HTTPS URIs

Multiple configurations can be merged:

```bash
otelcol --config=file:/path/to/receivers.yaml \
        --config=file:/path/to/exporters.yaml \
        --config=file:/path/to/service.yaml
```

Configuration files can include other files using `${file:path}` syntax within
the YAML itself. Validate configurations with `otelcol validate --config=config.yaml`.

## Installation / Setup

### Docker (Quick Start)

Pull and run the core distribution:

```bash
docker pull otel/opentelemetry-collector:0.150.0

docker run \
  -p 127.0.0.1:4317:4317 \
  -p 127.0.0.1:4318:4318 \
  -p 127.0.0.1:55679:55679 \
  otel/opentelemetry-collector:0.150.0 \
  2>&1 | tee collector-output.txt
```

Ports exposed:

- `4317` — OTLP over gRPC (default for most SDKs)
- `4318` — OTLP over HTTP
- `55679` — ZPages debug UI

### Binary Installation

Download the appropriate binary from
[releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases)
for your OS and architecture, then run:

```bash
otelcol --config=config.yaml
```

### Kubernetes

Deploy using the OpenTelemetry Operator or Helm chart. See deployment patterns
in reference files for detailed Kubernetes setups.

## Usage Examples

### Basic Trace Pipeline

Configure a Collector to receive OTLP traces and export them:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  otlp/backend:
    endpoint: jaeger.example.com:4317
    sending_queue:
      queue_size: 1000
    retry_on_failure:
      enabled: true
      max_elapsed_time: 5m

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp/backend]
```

### Multi-Signal Pipeline with Processing

Process traces, metrics, and logs with batching and memory limiting:

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
    check_interval: 1s
    limit_mib: 512
  batch:
    timeout: 5s
    send_batch_size: 1000

exporters:
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
```

### Generating Test Telemetry

Use `telemetrygen` to generate test traces:

```bash
go install github.com/open-telemetry/opentelemetry-collector-contrib/cmd/telemetrygen@latest
$GOBIN/telemetrygen traces --otlp-insecure --traces 3
```

View traces in the ZPages UI at `http://localhost:55679/debug/tracez`.

## Advanced Topics

**Architecture and Pipelines**: Deep dive into pipeline construction, component
lifecycle, data flow, and fan-out semantics → See
[Architecture and Pipelines](reference/01-architecture-and-pipelines.md)

**Configuration Reference**: Complete configuration guide covering TLS/mTLS,
environment variables, proxy support, authentication, and config providers → [Configuration Reference](reference/02-configuration-reference.md)

**Deployment Patterns**: Agent, gateway, agent-to-gateway, and multi-backend
deployment strategies with trade-offs → See
[Deployment Patterns](reference/03-deployment-patterns.md)

**Management and OpAMP**: Fleet management at scale using Open Agent Management
Protocol (OpAMP), supervisor configuration, and remote config updates → See
[Management and OpAMP](reference/04-management-and-opamp.md)

**Scaling and Resiliency**: Horizontal scaling strategies, sending queues,
persistent storage (WAL), retry mechanisms, and data loss prevention → See
[Scaling and Resiliency](reference/05-scaling-and-resiliency.md)

**Custom Distributions**: Building custom Collector binaries with ocb (OpenTelemetry
Collector Builder), manifest configuration, and custom components → See
[Custom Distributions](reference/06-custom-distributions.md)
