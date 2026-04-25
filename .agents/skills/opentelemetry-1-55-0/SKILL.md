---
name: opentelemetry-1-55-0
description: Complete OpenTelemetry 1.55.0 specification toolkit for implementing distributed tracing, metrics collection, and logging across polyglot applications. Use when instrumenting services with OTel SDKs, configuring OTLP exporters, implementing sampling strategies, setting up context propagation, or building observability pipelines following the official OTel 1.55.0 spec.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.55.0"
tags:
  - distributed-tracing
  - metrics
  - logging
  - observability
  - OTLP
  - context-propagation
  - sampling
  - semantic-conventions
category: observability
external_references:
  - https://opentelemetry.io/
  - https://github.com/open-telemetry/opentelemetry-collector
  - https://github.com/open-telemetry/opentelemetry-proto
  - https://github.com/open-telemetry/opentelemetry-specification
  - https://github.com/open-telemetry/semantic-conventions
  - https://opentelemetry.io/docs/
  - https://www.w3.org/TR/baggage/
  - https://www.w3.org/TR/trace-context/
  - https://opentelemetry.io/docs/specs/otel/overview/
---

# OpenTelemetry 1.55.0

## Overview

OpenTelemetry is an open-source observability framework providing a unified set of APIs, SDKs, tooling, and integrations for generating, collecting, exporting, and managing telemetry data (traces, metrics, logs) from applications and infrastructure. It supports four signals: **Tracing**, **Metrics**, **Logs**, and **Baggage**.

The project is organized into four component types:
- **API** — Cross-cutting public interfaces for instrumentation (imported by application code)
- **SDK** — Implementation of the API, installed and managed by the application owner
- **Semantic Conventions** — Keys and values describing common concepts (separate repo)
- **Contrib** — Optional integrations for web frameworks, databases, message queues, exporters

## When to Use

Use this skill when:
- Instrumenting applications with OpenTelemetry SDKs (Python, Java, Go, JS, C#, C++, Rust, Node.js, PHP, etc.)
- Configuring OTLP exporters to send telemetry to backends (Jaeger, Zipkin, Prometheus, Datadog, New Relic, etc.)
- Implementing distributed tracing with spans, contexts, and propagators
- Setting up metrics collection with counters, histograms, gauges, and exponential histograms
- Configuring logging integration via the Logs API
- Implementing sampling strategies (always_on, always_off, traceidratio, parentbased_*)
- Setting up context propagation across service boundaries (W3C TraceContext, W3C Baggage, B3, Jaeger)
- Migrating from OpenTracing or OpenCensus to OpenTelemetry
- Configuring the OpenTelemetry Collector for aggregation and forwarding
- Working with semantic conventions for HTTP, database, messaging, and gRPC

## Core Concepts

### Signals

OpenTelemetry organizes observability into four independent signals sharing a common context propagation subsystem:

1. **Tracing** — Distributed traces as DAGs of spans representing logical operations across process/network boundaries
2. **Metrics** — Raw measurements with predefined aggregations (counters, histograms, gauges)
3. **Logs** — Structured log records with severity, body, and attributes bridging existing logging frameworks
4. **Baggage** — Name/value pairs for propagating application-defined context across service boundaries

### Architecture Components

```
┌─────────────────────────────────────────────────────┐
│                    Application Code                  │
│  (imports API only — never SDK directly)            │
├─────────────────────────────────────────────────────┤
│  TracerProvider ─→ Tracer ─→ Span                  │
│  MeterProvider ─→ Meter ─→ Instrument              │
│  LoggerProvider ─→ Logger ─→ LogRecord             │
├─────────────────────────────────────────────────────┤
│                      SDK                             │
│  (SpanProcessor, MetricReader, Sampler, Exporter)   │
├─────────────────────────────────────────────────────┤
│                  Exporters                           │
│  OTLP → Jaeger/Zipkin/Prometheus/Backend            │
└─────────────────────────────────────────────────────┘
```

### Span Lifecycle

A **Span** represents an operation within a transaction:
- Operation name, start/finish timestamps
- Attributes (key-value pairs)
- Events (timestamped named annotations with attributes)
- Links to causally-related spans (within same or different traces)
- Parent span identifier
- SpanContext (TraceId, SpanId, TraceFlags, TraceState)

### Context Propagation

All signals share a `Context` mechanism — an immutable propagation carrier for execution-scoped values:
- Create keys, get/set values in context
- Implicit context support (thread-local, task-local storage)
- Attach/detach context for scope switching

### Propagators

Serialize and deserialize cross-cutting concern values across process boundaries:
- **W3C TraceContext** — Standard trace propagation (traceparent/tracestate headers)
- **W3C Baggage** — Application context propagation
- **B3** — Spring Cloud Sleuth / Zipkin format (single or multi-header)
- **Jaeger** — Legacy Jaeger propagation (deprecated)
- **AWS X-Ray**, **OT Trace** (third-party/deprecated)

### Resources

`Resource` captures identity about the entity producing telemetry:
- `service.name`, `service.version`, `service.instance.id`
- Cloud provider, container, host, process information
- Immutable and sent once per batch

### Sampling

Controls which spans are recorded/exported to manage volume:
- **AlwaysOnSampler** — Record all spans
- **AlwaysOffSampler** — Record no spans
- **TraceIdRatioBased** — Sample by probability (e.g., 0.25 = 25%)
- **ParentBased_* variants** — Respect parent's sampling decision with custom root
- **Remote samplers** — Jaeger centralized sampling strategy

### OTLP (OpenTelemetry Protocol)

The wire protocol for exporting telemetry:
- gRPC or HTTP/protobuf transport
- Supports traces, metrics, and logs in a single connection
- Batched exports with configurable timeouts and queue sizes

## Installation / Setup

### General SDK Initialization Pattern

```python
# Python example — universal initialization pattern
from opentelemetry import trace, metrics, logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 1. Create resource
resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
})

# 2. Configure tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 3. Configure metrics
metrics.set_meter_provider(MeterProvider(resource=resource))
meter = metrics.get_meter(__name__)

# 4. Configure logs
logs.set_logger_provider(LoggerProvider(resource=resource))
logger = logs.get_logger(__name__)

# 5. Add OTLP exporter
exporter = OTLPSpanExporter(endpoint="localhost:4317")
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(exporter)
)
```

### Zero-Code Auto-Instrumentation

Many languages support automatic instrumentation via environment variables and agent libraries, requiring no code changes. See [Reference: Getting Started](references/02-getting-started.md).

## Usage Examples

### Basic Tracing

```python
with tracer.start_as_current_span("http-request") as span:
    span.set_attribute("http.method", "GET")
    span.set_attribute("http.url", "https://api.example.com/users")
    # ... do work ...
    result = process_request()
    span.set_status(StatusCode.OK)
return result
```

### Recording Exceptions on Spans

```python
try:
    do_work()
except Exception as e:
    span.record_exception(e)  # Creates "exception" event
    span.set_attribute("error.type", type(e).__name__)
    span.set_status(StatusCode.ERROR, str(e))
    raise
finally:
    span.end()
```

### Metrics — Counter and Histogram

```python
# Synchronous counter
request_counter = meter.create_counter(
    name="http.requests.total",
    unit="1",
    description="Total number of HTTP requests"
)
request_counter.add(1, {"method": "GET", "status": "200"})

# Histogram with advisory bucket boundaries
latency_histogram = meter.create_histogram(
    name="http.request.duration",
    unit="ms",
    description="HTTP request duration",
    explicit_bucket_boundaries=[0, 5, 10, 25, 50, 100, 250, 500, 1000]
)
latency_histogram.record(42.5)

# Asynchronous gauge (callback-based)
def cpu_callback(collection_context):
    yield gauge.Measurement(get_cpu_usage(), {"core": "0"})

cpu_gauge = meter.create_up_down_counter("cpu.usage.pct")
meter.create_obsupable_updowncounter(
    name="cpu.usage.pct",
    callbacks=[cpu_callback],
    unit="%"
)
```

### Context Propagation Across Services

```python
# Inject context into outgoing HTTP request
from opentelemetry.propagate import inject
headers = {}
inject(headers)  # Adds traceparent, baggage headers

response = requests.get(url, headers=headers)

# Extract context from incoming request
from opentelemetry.propagate import extract
ctx = extract(request.headers)
with trace.use_span(span, True) as child:
    process_in_context(child)
```

### Baggage for Request Context

```python
from opentelemetry.baggage import set_baggage, get_baggage, get_baggage_context

# Set baggage values
set_baggage("user.id", "abc123")
set_baggage("tenant", "acme-corp")

# Access in downstream services
user_id = get_baggage("user.id")  # Returns "abc123"

# Create context with baggage for a specific operation
with get_baggage_context({"region": "us-east-1"}):
    do_work()  # Has region=us-east-1 baggage attached
```

### Sampling Configuration

```python
from opentelemetry.sdk.trace.sampling import (
    ParentBased, AlwaysOnSampler, TraceIdRatioBased,
    JaegerRemoteSampler
)

# Probability-based sampling at 25%
provider = TracerProvider(
    sampler=ParentBased(root=TraceIdRatioBased(0.25))
)

# Remote sampling via Jaeger agent
provider = TracerProvider(
    sampler=ParentBased(
        root=JaegerRemoteSampler(
            endpoint="http://localhost:14250/api/traces",
            pollingIntervalMs=5000,
            initialSamplingRate=0.25
        )
    )
)
```

### OTLP Exporter Configuration

```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# gRPC trace exporter
trace_exporter = OTLPSpanExporter(
    endpoint="otel-collector:4317",
    headers={"authorization": "Bearer token"},
    timeout=30
)
processor = BatchSpanProcessor(trace_exporter)
trace.get_tracer_provider().add_span_processor(processor)

# HTTP metrics exporter
metric_exporter = OTLPMetricExporter(
    endpoint="http://otel-collector:4318/v1/metrics",
    headers={"Content-Type": "application/x-protobuf"}
)
```

### Prometheus Metrics Exporter

```python
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
meter = provider.get_meter("myapp")

# Scrape endpoint: http://localhost:9464/metrics
```

### Log Records

```python
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource
import logging

resource = Resource.create({"service.name": "my-service"})
logger_provider = LoggerProvider(resource=resource)
logging.setLoggerClass(logging.Handler)

# Bridge to Python's standard logging
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.info("User logged in", extra={"user.id": "abc123"})
```

### View Configuration for Metrics

```python
from opentelemetry.sdk.metrics.view import View, InstrumentType, SumAggregation

provider = MeterProvider(
    views=[
        # Custom aggregation for HTTP duration
        View(
            instrument_name="http.request.duration",
            aggregation=ExplicitBucketHistogramAggregation(
                boundaries=[0, 5, 10, 25, 50, 100, 250, 500, 1000, 2500]
            ),
            attribute_keys={"http.method", "http.status_code"}
        ),
        # Drop unnecessary attributes
        View(
            instrument_name="db.operation.duration",
            attribute_keys=["db.system", "db.name"]
        ),
    ]
)
```

### Resource Detection

```python
from opentelemetry.sdk.resources import Resource, ResourceDetector, TelemetrySDKResourceDetector

# Built-in resource detectors
resource = Resource.create(
    attributes={
        "service.name": "my-service",
        **TelemetrySDKResourceDetector().detect().attributes
    }
)

# Custom detector for cloud provider
class CloudResourceDetector(ResourceDetector):
    def detect(self):
        # Detect AWS, GCP, Azure metadata
        return Resource.create({"cloud.provider": "aws"})
```

## Advanced Topics

- **SDK Plugin Interfaces** — SpanProcessor, Exporter, Sampler, MetricReader implementations
- **Exemplars** — Linking metrics to specific trace spans for root-cause analysis
- **Schema Files** — Semantic versioning of semantic conventions via schema transformations
- **Entity Model** — New entity-based resource identification and propagation
- **Declarative Configuration** — YAML/JSON SDK configuration files with env var substitution
- **OpenTelemetry Collector** — Agent mode (sidecar) and standalone collector deployments
- **Attribute Limits** — Configurable truncation for attribute count and value size
- **Error Handling** — SDK internal logger, self-diagnostics, error callbacks

See [Reference: Trace API & SDK](references/01-trace-api-sdk.md) for detailed span/spancontext/sampling documentation.
See [Reference: Metrics API & SDK](references/02-metrics-api-sdk.md) for instrument types, data model, views, exemplars.
See [Reference: Logs API & SDK](references/03-logs-api-sdk.md) for log records, severity levels, exporters.
See [Reference: Configuration & Environment Variables](references/04-configuration.md) for all env vars and limits.
See [Reference: OTLP Protocol](references/05-otlp-protocol.md) for wire protocol details.
See [Reference: Context, Propagators & Baggage](references/06-context-propagation.md) for context propagation mechanisms.
See [Reference: Common Concepts & Resources](references/07-common-concepts.md) for AnyValue, attributes, resources.
See [Reference: Versioning & Stability](references/08-versioning-stability.md) for signal lifecycle and versioning rules.

