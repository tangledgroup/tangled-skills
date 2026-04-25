# Exporters and Propagators

## OTLP Protocol Overview

OTLP (OpenTelemetry Protocol) is the native protocol for exporting telemetry data. It supports two transport options: HTTP (with JSON or Protobuf encoding) and gRPC (Protobuf only).

### HTTP vs gRPC Comparison

| Feature | HTTP | gRPC |
|---------|------|------|
| Encoding | JSON or Protobuf | Protobuf only |
| Port (default) | 4318 | 4317 |
| Trace path | `/v1/traces` | N/A (streaming) |
| Connection | Per-request or keep-alive | Persistent stream |
| Firewall friendly | Yes (standard HTTP) | May require special config |
| Performance | Good | Better (binary, multiplexed) |

## OTLP Span Exporters

### HTTP Protocol

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    certificate_file=None,           # Path to CA cert (default: use system certs)
    client_key_file=None,            # mTLS: client private key path
    client_certificate_file=None,    # mTLS: client cert path
    headers={"Authorization": "Bearer token"},  # Custom headers
    timeout=10,                       # Request timeout in seconds
    compression="gzip",               # "gzip", "deflate", or "none"
)

processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
```

### gRPC Protocol

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    certificate_file=None,
    client_key_file=None,
    client_certificate_file=None,
    headers={},
    timeout=10,
    compression=None,  # None or "gzip"
)

processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
```

## OTLP Metric Exporters

### HTTP Protocol

```python
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

exporter = OTLPMetricExporter(
    endpoint="http://localhost:4318/v1/metrics",
    certificate_file=None,
    client_key_file=None,
    client_certificate_file=None,
    headers={},
    timeout=10,
    compression="gzip",
)

reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])
```

### gRPC Protocol

```python
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

exporter = OTLPMetricExporter(
    endpoint="localhost:4317",
    certificate_file=None,
    headers={},
    timeout=10,
    compression=None,
)
```

## OTLP Log Exporters

```python
from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

exporter = OTLPLogExporter(
    endpoint="http://localhost:4318/v1/logs",
    certificate_file=None,
    headers={},
    timeout=10,
    compression="gzip",
)

processor = BatchLogRecordProcessor(exporter)
logger_provider.add_log_record_processor(processor)
```

## Exporter Configuration via Environment Variables

### Generic OTLP Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318/` | Base URL for all OTLP exporters |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10` | Timeout in seconds |
| `OTEL_EXPORTER_OTLP_COMPRESSION` | `none` | Compression: `gzip`, `deflate`, `none` |
| `OTEL_EXPORTER_OTLP_HEADERS` | — | Comma-separated key=value pairs (e.g., `"Authorization=Bearer token,key2=val2"`) |
| `OTEL_EXPORTER_OTLP_CERTIFICATE` | — | Path to CA certificate file |

### Signal-Specific Overrides

Each signal can override the generic settings:

**Traces:**
| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | `${OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces` | Traces endpoint |
| `OTEL_EXPORTER_OTLP_TRACES_TIMEOUT` | `${OTEL_EXPORTER_OTLP_TIMEOUT}` | Traces timeout |
| `OTEL_EXPORTER_OTLP_TRACES_COMPRESSION` | — | Traces compression override |
| `OTEL_EXPORTER_OTLP_TRACES_HEADERS` | — | Traces headers override |
| `OTEL_EXPORTER_OTLP_TRACES_CERTIFICATE` | — | Traces CA cert override |

**Metrics:**
| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | `${OTEL_EXPORTER_OTLP_ENDPOINT}/v1/metrics` | Metrics endpoint |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | — | `CUMULATIVE`, `DELTA`, or `LOWMEMORY` |

**Logs:**
| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | `${OTEL_EXPORTER_OTLP_ENDPOINT}/v1/logs` | Logs endpoint |

## Other Exporters

### Zipkin Exporter

```python
from opentelemetry.exporter.zipkin.proto import encoder
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter

# Via OTLP to a Zipkin-compatible endpoint
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
exporter = OTLPSpanExporter(endpoint="http://zipkin:9411/api/v2/spans")
```

### Jaeger Exporter (via OTLP)

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Jaeger supports OTLP gRPC on port 14250 by default
exporter = OTLPSpanExporter(endpoint="jaeger:14250")
```

### Prometheus Exporter

```python
from prometheus_client import start_http_server
from opentelemetry.sdk.metrics.export import PrometheusMetricReader

# Expose /metrics endpoint for Prometheus to scrape
provider = MeterProvider(metric_readers=[PrometheusMetricReader()])
start_http_server(8000)  # Serves /metrics on port 8000
```

### File Exporter (JSON Lines)

```python
from opentelemetry.sdk.trace.export import FileSpanExporter, BatchSpanProcessor

exporter = FileSpanExporter(
    filename="/var/log/traces.jsonl",
    indentation=2,
)
provider.add_span_processor(BatchSpanProcessor(exporter))
```

### In-Memory Exporter (Testing)

```python
from opentelemetry.sdk.trace.export import InMemorySpanExporter, SimpleSpanProcessor

exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(exporter))

# Assertions in tests
spans = exporter.get_finished_spans()
assert len(spans) == expected_count
```

## Propagators

### W3C Trace Context (Default)

Standard format: `traceparent: 00-traceId-spanId-traceFlags`

```python
# Default propagator — no setup needed
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("request") as span:
    ctx = trace.set_span_in_context(span)
    # Inject into outgoing headers
    from opentelemetry.propagate import inject
    headers = {}
    inject(headers, context=ctx)
    # headers["traceparent"] == "00-<trace_id>-<span_id>-01"
```

### B3 Propagation

Install and configure:

```bash
pip install opentelemetry-propagator-b3
```

Via environment variable (recommended):
```bash
export OTEL_PROPAGATORS=b3multi   # or "b3" for single-header format
```

Via code:
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat, B3Format

set_global_textmap(B3MultiFormat())  # or B3Format() for single-header
```

B3 headers:
- `b3`: Single header with `traceId-spanId-parentSpanId-sampled`
- `X-B3-TraceId`, `X-B3-SpanId`, `X-B3-ParentSpanId`, `X-B3-Sampled`: Multi-header format

### Jaeger Propagation

Install and configure:

```bash
pip install opentelemetry-propagator-jaeger
```

Via environment variable:
```bash
export OTEL_PROPAGATORS=jaeger
```

Via code:
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.jaeger import JaegerFormat

set_global_textmap(JaegerFormat())
```

Jaeger uses the `uber-trace-id` header.

### AWS X-Ray Propagation

Third-party propagator available separately:
```bash
pip install aws-xray-sdk
```

Via environment variable:
```bash
export OTEL_PROPAGATORS=xray
```

### No Propagation

```bash
export OTEL_PROPAGATORS=none
```

Or in code:
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagator.composite import CompositeTextMapPropagator

set_global_textmap(CompositeTextMapPropagator([]))
```

## Exporter Retry Behavior

OTLP exporters implement exponential backoff with jitter:
- Maximum retries: 6
- Backoff starts at ~2 seconds with ±20% random jitter
- Retries on transient errors (connection errors, 429, 5xx)
- Does NOT retry on non-retryable errors (4xx except 429)

```python
# This is built into OTLPSpanExporter — no configuration needed
# The exporter handles retries internally with configurable timeout
exporter = OTLPSpanExporter(timeout=10)  # Total timeout for all retries
```

## Shutdown and Cleanup

Always properly shut down exporters to flush remaining data:

```python
import atexit

# Option 1: SDK handles shutdown automatically (recommended)
# The SDK registers atexit handlers for all providers

# Option 2: Explicit shutdown
provider.shutdown()
metrics.get_meter_provider().shutdown()

# Option 3: Custom atexit handler
atexit.register(provider.shutdown)
```
