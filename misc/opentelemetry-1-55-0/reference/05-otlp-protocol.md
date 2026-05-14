# OTLP Protocol

## Overview

The OpenTelemetry Protocol (OTLP) is the standard wire protocol for exporting telemetry data. It supports traces, metrics, logs, and profiles in a unified binary (Protobuf) format over HTTP or gRPC.

## Transport Options

### OTLP/HTTP

- Default endpoint: `http://localhost:4318`
- Uses HTTP POST with Protobuf-encoded body
- Per-signal paths appended to the endpoint URL:
  - Traces: `/v1/traces`
  - Metrics: `/v1/metrics`
  - Logs: `/v1/logs`
- Content-Type: `application/x-protobuf`

### OTLP/gRPC

- Default endpoint: `http://localhost:4317`
- Uses gRPC streaming for efficient bidirectional communication
- Supports compression (gzip)
- Service methods: `Export` for each signal type

## Configuration Options

All configuration options MUST be overridable by signal-specific variants.

### Endpoint

**OTLP/HTTP:**
```bash
# Global endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otel-collector.example.com:4318"

# Per-signal endpoints (take precedence)
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://traces.example.com/v1/traces"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="https://metrics.example.com/v1/metrics"
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://logs.example.com/v1/logs"
```

**OTLP/gRPC:**
```bash
# Global endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="localhost:4317"

# Per-signal endpoints
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="traces.example.com:4317"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="metrics.example.com:4317"
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="logs.example.com:4317"
```

### Secure/Insecure Connection

For OTLP/gRPC, scheme determines security:

- `https://` → secure connection (TLS)
- `http://` → insecure connection
- No scheme → controlled by `OTEL_EXPORTER_OTLP_INSECURE` (default: false = secure)

```bash
# Explicitly allow insecure gRPC
export OTEL_EXPORTER_OTLP_INSECURE="true"
```

For OTLP/HTTP, the scheme in the endpoint URL always determines security.

### TLS/mTLS Configuration

```bash
# Server certificate for TLS verification
export OTEL_EXPORTER_OTLP_CERTIFICATE="/path/to/ca.pem"

# Client key and certificate for mTLS
export OTEL_EXPORTER_OTLP_CLIENT_KEY="/path/to/client-key.pem"
export OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE="/path/to/client-cert.pem"
```

### Headers

Key-value pairs for HTTP/gRPC request headers:

```bash
# Comma-separated key=value pairs
export OTEL_EXPORTER_OTLP_HEADERS="key1=val1,key2=val2"

# Per-signal headers
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="authorization=Bearer token123"
export OTEL_EXPORTER_OTLP_METRICS_HEADERS="x-api-key=abc456"
```

### Timeout

Configurable export timeout:

```bash
export OTEL_EXPORTER_OTLP_TIMEOUT="30000"  # milliseconds
export OTEL_EXPORTER_OTLP_TRACES_TIMEOUT="10000"
```

## Endpoint URL Construction (OTLP/HTTP)

When using the global `OTEL_EXPORTER_OTLP_ENDPOINT`, per-signal URLs are constructed:

1. Parse the endpoint URL (scheme, host, port, path)
2. Append signal-specific path segment
3. Result: `{endpoint}/v1/{signal}`

Example:
- Endpoint: `http://collector:4318/custom/path`
- Traces URL: `http://collector:4318/custom/path/v1/traces`
- Metrics URL: `http://collector:4318/custom/path/v1/metrics`

Per-signal endpoint options use the URL as-is without modification.

## Retry Behavior

### Transient Errors

The OTLP exporter retries on transient failures:

- HTTP 429 (Too Many Requests)
- HTTP 502 (Bad Gateway), 503 (Service Unavailable), 504 (Gateway Timeout)
- gRPC UNAVAILABLE, RESOURCE_EXHAUSTED
- Network-level errors (connection reset, timeout)

### Retry Strategy

- Exponential backoff with jitter
- Configurable max elapsed time
- Retry on transient errors only
- Non-transient errors (4xx except 429) are not retried

## User Agent

The OTLP exporter sends a `User-Agent` header identifying the SDK:

```
User-Agent: OTel-OTLP-Exporter-Python/1.27.0
```

Format: `{sdk-name}-OTLP-Exporter-{language}/{version}`

## Protocol Requirements

- OTLP Exporter is a required plugin for all SDK implementations
- MUST support both OTLP/HTTP and OTLP/gRPC
- MUST honor retry-on-failure semantics
- MUST support compression (gzip) for large payloads
