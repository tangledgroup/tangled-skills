# OTLP Protocol

**Status**: Stable (except where noted)

## Overview

The OpenTelemetry Protocol (OTLP) is the official wire protocol for exporting telemetry data from instrumented applications to collectors and backends. It supports traces, metrics, and logs over a single connection.

### Design Goals

- **Efficiency**: Low overhead for high-throughput telemetry
- **Flexibility**: Support multiple transport protocols
- **Extensibility**: Allow new signal types without breaking changes
- **Interoperability**: Work across all language implementations

## Transport Protocols

OTLP supports three transport options:

| Transport | Protocol | Env Var | Default |
|-----------|----------|---------|---------|
| gRPC | HTTP/2 + Protocol Buffers | `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` |
| HTTP/protobuf | HTTP/1.1 or 2 + Protobuf | `http/protobuf` | — |
| HTTP/JSON | HTTP/1.1 or 2 + JSON | `http/json` | — |

### gRPC Transport

- Binary Protocol Buffers encoding
- Multiplexed streams via HTTP/2
- Best performance, recommended for production
- Supports compression via `OTEL_EXPORTER_OTLP_COMPRESSION=gzip`

### HTTP/protobuf Transport

- Single POST request per export batch
- Content-Type: `application/x-protobuf`
- Simpler firewall/network configuration
- No HTTP/2 required

### HTTP/JSON Transport

- Human-readable JSON encoding
- Content-Type: `application/json`
- Larger payload size, useful for debugging
- Same structure as protobuf but text-encoded

## Endpoint Configuration

```bash
# General endpoint (applies to all signals)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://collector:4317"

# Signal-specific overrides
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://traces-collector:4318/v1/traces"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://metrics-collector:4318/v1/metrics"
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="http://logs-collector:4318/v1/logs"
```

**Precedence**: Signal-specific endpoints override the general endpoint. The general endpoint overrides per-signal defaults.

## Request/Response Structure

### gRPC Services

```protobuf
// Traces
service TraceService {
  rpc Export(ExportTraceServiceRequest) returns (ExportTraceServiceResponse);
}

// Metrics
service MetricsService {
  rpc Export(ExportMetricsServiceRequest) returns (ExportMetricsServiceResponse);
}

// Logs
service LogService {
  rpc Export(ExportLogsServiceRequest) returns (ExportLogsServiceResponse);
}
```

### Trace Data Model

```protobuf
message ExportTraceServiceRequest {
  repeated ResourceSpans resource_spans = 1;
}

message ResourceSpans {
  Resource resource = 1;
  repeated ScopeSpans scope_spans = 2;
  // schema_url is optional
}

message ScopeSpans {
  InstrumentationScope scope = 1;
  repeated Span spans = 2;
  // schema_url, start_time_unix_nano, time_unix_nano optional
}

message Span {
  string trace_id = 1;           // 16 bytes hex-encoded
  string span_id = 2;           // 8 bytes hex-encoded
  string trace_state = 3;       // W3C tracestate
  SpanKind kind = 4;            // INTERNAL, SERVER, CLIENT, etc.
  string name = 5;
  // parent_span_id optional
  // links, events, status, attributes...
  uint64 start_time_unix_nano = 8;
  uint64 end_time_unix_nano = 9;
}
```

### Metric Data Model

```protobuf
message ExportMetricsServiceRequest {
  repeated ResourceMetrics resource_metrics = 1;
}

message ResourceMetrics {
  Resource resource = 1;
  repeated ScopeMetrics scope_metrics = 2;
}

message ScopeMetrics {
  InstrumentationScope scope = 1;
  repeated Metric metrics = 2;
}

message Metric {
  string name = 1;
  string description = 3;
  string unit = 4;
  // One of: sum, gauge, histogram, exponential_histogram, summary, attributes_record
  oneof data {
    Sum sum = 5;
    Gauge gauge = 6;
    Histogram histogram = 7;
    ExponentialHistogram exponential_histogram = 8;
    Summary summary = 9;
  }
}

message Sum {
  bool is_monotonic = 1;  // true for Counter, false for UpDownCounter
  repeated NumberDataPoint data_points = 2;
}

message Histogram {
  bool is_monotonic = 1;
  repeated HistogramDataPoint data_points = 2;
}
```

### Log Data Model

```protobuf
message ExportLogsServiceRequest {
  repeated ResourceLogs resource_logs = 1;
}

message ResourceLogs {
  Resource resource = 1;
  repeated ScopeLogs scope_logs = 2;
}

message ScopeLogs {
  InstrumentationScope scope = 1;
  repeated LogRecord log_records = 2;
}

message LogRecord {
  // Timestamps in nanoseconds since Unix epoch
  uint64 time_unix_nano = 1;
  uint64 observed_time_unix_nano = 2;
  // Severity levels
  SeverityNumber severity_number = 3;
  string severity_text = 4;
  bytes body = 5;             // AnyValue (oneof)
  repeated KeyValue[] attributes = 6;
  uint32 dropped_attributes_count = 7;
  // Trace context for linking logs to traces
  bytes trace_id = 9;
  bytes span_id = 10;
  uint32 flags = 11;          // Bit field (OTEL_FLAGS_MASK = 0x000000FF)
}
```

## Resource Model

```protobuf
message Resource {
  repeated KeyValue attributes = 1;
  uint32 dropped_attributes_count = 2;
}

message InstrumentationScope {
  string name = 1;
  string version = 2;
  repeated KeyValue attributes = 3;
  uint32 dropped_attributes_count = 4;
}
```

### Common Resource Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `service.name` | Logical service name | `payment-service` |
| `service.version` | Service version | `1.2.3` |
| `service.instance.id` | Unique instance identifier | `abc-123` |
| `service.namespace` | Service namespace | `production` |
| `deployment.environment.name` | Deployment environment | `production`, `staging` |
| `cloud.provider` | Cloud provider | `aws`, `gcp`, `azure` |
| `cloud.region` | Cloud region | `us-east-1` |
| `container.id` | Container ID | `abc123def456` |
| `host.name` | Host name | `web-server-01` |
| `process.pid` | Process ID | `12345` |
| `process.executable.name` | Executable name | `python` |

## Attribute Encoding

### AnyValue Types

| Type | Protobuf Field | Python Example |
|------|---------------|----------------|
| String | `string_value` | `"hello"` |
| Bool | `bool_value` | `True` |
| Double | `double_value` | `3.14` |
| Int | `int_value` | `42` |
| Array | `array_value` | `[1, 2, 3]` |
| Map | `kvlist_value` | `{"key": "val"}` |
| Bytes | `bytes_value` | `b"\x00\x01"` |

### Non-OTLP Encoding (Fallback)

For protocols without native AnyValue support:

| Type | Encoding Example |
|------|-----------------|
| String | As-is: `hello world` |
| Boolean | JSON: `true`, `false` |
| Integer | JSON number: `42`, `-123` |
| Float | JSON number: `3.14`, `NaN`, `Infinity` |
| Byte Array | Base64: `aGVsbG8=` |
| Empty Value | Empty string |
| Array | JSON array: `[1, 2, "a"]` |
| Map | JSON object: `{"key": "val"}` |

**Warning**: Non-OTLP encoding is lossy — type information is lost and numeric precision may be reduced.

## Sampling & Batching

### Batch Export

All OTLP exporters use batched exports for efficiency:

```python
# Trace batch (gRPC)
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

processor = BatchSpanProcessor(
    exporter,
    schedule_delay_millis=5000,   # Export every 5 seconds
    export_timeout_millis=30000,  # Max 30s per export
    max_queue_size=2048,          # Queue up to 2048 spans
    max_export_batch_size=512     # Export at most 512 spans at once
)
```

### Retry Policy

OTLP exporters SHOULD implement retry with exponential backoff for transient errors:
- HTTP 429 (Too Many Requests): retry with backoff
- HTTP 502/503/504: retry with backoff
- gRPC `UNAVAILABLE`, `RESOURCE_EXHAUSTED` (if retry policy allows): retry

### Compression

```bash
# Enable gzip compression for all exporters
export OTEL_EXPORTER_OTLP_COMPRESSION=gzip

# Per-signal override
export OTEL_EXPORTER_OTLP_TRACES_COMPRESSION=gzip
```

## File Exporter (Development)

For debugging, OTLP data can be written to files instead of network:

```bash
# Write traces to file
export OTEL_TRACES_EXPORTER=otlp/stdout

# Or configure via SDK
from opentelemetry.exporter.otlp.proto.grpc.exporter import OTLPSpanExporter
exporter = OTLPSpanExporter(insecure=True)  # for local debugging
```

## Error Handling

OTLP responses include status codes:

| gRPC Code | Meaning | Action |
|-----------|---------|--------|
| OK | Success | Continue normally |
| INVALID_ARGUMENT | Malformed request | Do not retry, log error |
| FAILED_PRECONDITION | Server rejected (e.g., unknown signal) | Do not retry, log error |
| UNAVAILABLE | Server unavailable | Retry with backoff |
| RESOURCE_EXHAUSTED | Rate limited | Retry if retry policy allows |
| CANCELLED | Request cancelled | Do not retry |

SDK internal errors are logged via the SDK logger at the configured `OTEL_LOG_LEVEL`.
