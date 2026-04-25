---
name: opentelemetry-python-1-41-0
description: Complete OpenTelemetry Python toolkit v1.41.0 for distributed tracing, metrics collection, and log management with support for OTLP exporters, automatic instrumentation, custom sampling, context propagation, and semantic conventions. Use when instrumenting Python applications for observability, configuring trace/metric/log pipelines, setting up OTLP exporters, implementing custom samplers, or integrating with distributed tracing backends like Jaeger, Zipkin, Prometheus, or the OpenTelemetry Collector.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.41.0"
tags:
  - observability
  - distributed-tracing
  - metrics
  - logging
  - opentelemetry
  - otel
  - telemetry
  - monitoring
category: observability
external_references:
  - https://github.com/open-telemetry/opentelemetry-python/tree/v1.41.0
  - https://github.com/open-telemetry/opentelemetry-python-contrib
  - https://github.com/open-telemetry/opentelemetry-specification
  - https://opentelemetry-python.readthedocs.io/
  - https://opentelemetry.io/ecosystem/registry/?component=instrumentation&language=python
  - https://opentelemetry.io/docs/languages/python/
---
## Overview
Complete OpenTelemetry Python toolkit v1.41.0 for distributed tracing, metrics collection, and log management with support for OTLP exporters, automatic instrumentation, custom sampling, context propagation, and semantic conventions. Use when instrumenting Python applications for observability, configuring trace/metric/log pipelines, setting up OTLP exporters, implementing custom samplers, or integrating with distributed tracing backends like Jaeger, Zipkin, Prometheus, or the OpenTelemetry Collector.

Complete toolkit for OpenTelemetry Python v1.41.0, the official observability framework for distributed tracing, metrics, and logs in Python applications. Provides API and SDK packages with support for OTLP protocol exporters, automatic instrumentation via `opentelemetry-instrument`, custom sampling strategies, context propagation across multiple formats, and semantic conventions for common frameworks.

## When to Use
- Instrumenting Python applications (Flask, Django, FastAPI, etc.) for distributed tracing
- Setting up metrics collection with counters, histograms, gauges, and UpDownCounters
- Configuring OTLP exporters (HTTP/gRPC) for sending telemetry to backends
- Implementing automatic zero-code instrumentation with `opentelemetry-instrument`
- Creating custom sampling strategies for trace filtering
- Propagating context across service boundaries (W3C Trace Context, B3, Jaeger, X-Ray)
- Integrating Python services with the OpenTelemetry Collector
- Setting up log correlation with trace/span IDs

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Architecture Overview
OpenTelemetry Python is split into two main packages:

1. **`opentelemetry-api`** — Abstract interfaces and no-op implementations. Libraries that produce telemetry depend only on this.
2. **`opentelemetry-sdk`** — Reference implementation. Applications depend on this to actually emit telemetry.

The three signals are:
- **Traces** — Request flow tracking across services (Stable)
- **Metrics** — Counters, histograms, gauges for quantitative data (Stable)
- **Logs** — Log records correlated with traces (Development/Stabilizing in 1.41.0)

See [Core Concepts](reference/01-core-concepts.md) for detailed architecture diagrams and signal explanations.

## Installation / Setup
### Core Packages

```bash
# API only (for library authors)
pip install opentelemetry-api

# Full SDK (for application developers)
pip install opentelemetry-sdk
```

### Semantic Conventions

```bash
pip install opentelemetry-semantic-conventions
```

### OTLP Exporters

```bash
# HTTP protocol exporters
pip install opentelemetry-exporter-otlp-proto-http

# gRPC protocol exporters
pip install opentelemetry-exporter-otlp-proto-grpc
```

### Propagators

```bash
pip install opentelemetry-propagator-b3       # B3 single-header
pip install opentelemetry-propagator-jaeger   # Jaeger format
```

### Automatic Instrumentation (Full Distribution)

```bash
pip install opentelemetry-distro
```

### Framework-Specific Instrumentation

Available as `opentelemetry-instrumentation-<name>`:
```bash
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-django
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-psycopg2
# ... and many more at https://opentelemetry.io/ecosystem/registry/?component=instrumentation&language=python
```

## Quick Start: Tracing
### Minimal Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# 1. Configure the TracerProvider
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# 2. Set as global default
trace.set_tracer_provider(provider)

# 3. Get a tracer (use library/instrumentation name, not __name__)
tracer = trace.get_tracer("my.library", "1.0.0")

# 4. Create spans
with tracer.start_as_current_span("operation-name") as span:
    span.set_attribute("key", "value")
```

See [Tracing Deep Dive](reference/02-tracing-deep-dive.md) for advanced patterns including nested spans, decorators, context propagation, explicit parent contexts, and custom exporters.

## Quick Start: Metrics
### Minimal Setup

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("my.meter", "1.0.0")
counter = meter.create_counter("http.requests", unit="1")
counter.add(1, {"method": "GET"})
```

See [Metrics Deep Dive](reference/03-metrics-deep-dive.md) for synchronous/asynchronous instruments, views, exemplars, and all instrument types.

## Quick Start: Logs
> **Note:** The Logs signal is under development in v1.41.0 and may change.

```python
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogRecordExporter
from opentelemetry._logs import set_logger_provider

provider = LoggerProvider()
processor = BatchLogRecordProcessor(ConsoleLogRecordExporter())
provider.add_log_record_processor(processor)
set_logger_provider(provider)

handler = LoggingHandler(level=logging.DEBUG, logger_provider=provider)
logging.getLogger().addHandler(handler)
logging.getLogger(__name__).info("Application started")
```

## Quick Start: OTLP Export (Production)
```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
    compression="gzip",
)
provider.add_span_processor(BatchSpanProcessor(exporter))
```

See [Exporters and Propagators](reference/04-exporters-and-propagators.md) for complete exporter reference, gRPC vs HTTP comparison, all environment variables, propagator configuration (B3, Jaeger, X-Ray), and shutdown patterns.

## Automatic (Zero-Code) Instrumentation
```bash
# Install the distribution package
pip install opentelemetry-distro

# Auto-discover installed instrumentation packages
opentelemetry-bootstrap -a install

# Instrument and run in one command
opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --service_name my-app \
    python app.py
```

## Sampling Configuration
```python
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_ON, ALWAYS_OFF, TraceIdRatioBased, ParentBasedTraceIdRatio,
)

# 10% probabilistic sampling with parent awareness
trace.set_tracer_provider(TracerProvider(sampler=ParentBasedTraceIdRatio(rate=0.1)))
```

Via environment variables:
```bash
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1
```

## Testing with In-Memory Exporters
```python
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, InMemorySpanExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

span_exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("test-span"):
    pass

spans = span_exporter.get_finished_spans()
assert len(spans) == 1
```

## Key Environment Variables Reference
| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SERVICE_NAME` | — | Primary service name (highest priority) |
| `OTEL_PROPAGATORS` | `tracecontext,baggage` | Propagation formats: tracecontext, baggage, b3, b3multi, jaeger, xray, ottrace, none |
| `OTEL_TRACES_SAMPLER` | `parentbased_always_on` | Sampler type |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Sampler argument (rate for traceidratio) |
| `OTEL_SDK_DISABLED` | `false` | Disable SDK entirely |
| `OTEL_LOGS_EXPORTER` | — | Logs exporter: console, otlp, none |
| `OTEL_TRACES_EXPORTER` | — | Traces exporter: console, otlp, zipkin, jaeger, none |
| `OTEL_METRICS_EXPORTER` | — | Metrics exporter: console, prometheus, otlp, none |

### SDK Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per span/resource |
| `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per span |
| `OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per event |
| `OTEL_LINK_ATTRIBUTE_COUNT_LIMIT` | 128 | Max attributes per link |
| `OTEL_SPAN_EVENT_COUNT_LIMIT` | 128 | Max events per span |
| `OTEL_SPAN_LINK_COUNT_LIMIT` | 128 | Max links per span |

### OTLP Exporter Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318/` | Base endpoint for all exporters |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | `${ENDPOINT}/v1/traces` | Traces-specific endpoint |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | `${ENDPOINT}/v1/metrics` | Metrics-specific endpoint |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10` | Timeout in seconds |
| `OTEL_EXPORTER_OTLP_COMPRESSION` | `none` | Compression: gzip, deflate, none |
| `OTEL_EXPORTER_OTLP_HEADERS` | — | Comma-separated key=value pairs |

## Common Patterns
### Flask with Auto-Instrumentation

```bash
pip install opentelemetry-distro opentelemetry-instrumentation-flask
opentelemetry-instrument --traces_exporter otlp flask run -p 8080
```

### FastAPI with Manual + Automatic Instrumentation

```python
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
))
trace.set_tracer_provider(provider)

app = FastAPI()
tracer = trace.get_tracer(__name__)

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    with tracer.start_as_current_span("get_item") as span:
        span.set_attribute("item.id", item_id)
        return {"item": item_id}
```

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Tracing Deep Dive](reference/02-tracing-deep-dive.md)
- [Metrics Deep Dive](reference/03-metrics-deep-dive.md)
- [Exporters And Propagators](reference/04-exporters-and-propagators.md)

