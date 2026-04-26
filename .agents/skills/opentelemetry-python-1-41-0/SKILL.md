---
name: opentelemetry-python-1-41-0
description: Complete OpenTelemetry Python v1.41.0 toolkit for distributed tracing, metrics collection, and log management with support for OTLP exporters, automatic instrumentation, custom sampling, context propagation, and semantic conventions. Use when instrumenting Python applications for observability, configuring trace/metric/log pipelines, setting up OTLP exporters, implementing custom samplers, or integrating with distributed tracing backends like Jaeger, Zipkin, Prometheus, or the OpenTelemetry Collector.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.41.0"
tags:
  - opentelemetry
  - observability
  - tracing
  - metrics
  - logging
  - distributed-tracing
  - otel
  - python
category: observability
external_references:
  - https://github.com/open-telemetry/opentelemetry-python/tree/v1.41.0
  - https://github.com/open-telemetry/opentelemetry-python-contrib
  - https://github.com/open-telemetry/opentelemetry-specification
  - https://opentelemetry-python.readthedocs.io/
  - https://opentelemetry.io/ecosystem/registry/?component=instrumentation&language=python
  - https://opentelemetry.io/docs/languages/python/
---

# OpenTelemetry Python 1.41.0

## Overview

OpenTelemetry Python is the official Python implementation of the OpenTelemetry observability framework. Version 1.41.0 provides stable support for traces and metrics, with logs in development status. It consists of two main packages: `opentelemetry-api` (abstract interfaces and no-op implementations) and `opentelemetry-sdk` (the reference SDK implementation). Libraries should depend only on the API package, while applications choose and configure the SDK.

The project follows the OpenTelemetry specification and supports three telemetry signals:

- **Traces** — Stable. Distributed request tracing with spans, span processors, sampling, and exporters.
- **Metrics** — Stable. Synchronous and asynchronous instruments (Counter, UpDownCounter, Histogram, Gauge, Observable variants) with MetricReader-based architecture.
- **Logs** — Development status. LoggerProvider/Logger API with LogRecord, SeverityNumber, and bridge to Python's standard `logging` module via `LoggingHandler`.

## When to Use

- Instrumenting Python applications for distributed tracing (HTTP servers, databases, message queues)
- Setting up metrics collection with counters, histograms, gauges, and up-down counters
- Configuring OTLP exporters to send telemetry to backends (Jaeger, Zipkin, Prometheus, OpenTelemetry Collector)
- Implementing custom samplers or span processors for fine-grained control
- Propagating trace context across service boundaries using W3C TraceContext and Baggage
- Using auto-instrumentation for frameworks like Flask, Django, FastAPI, SQLAlchemy, Redis, and more
- Building observability pipelines following the OpenTelemetry 1.55.0 specification
- Integrating with Python's standard `logging` module for structured log correlation with traces

## Core Concepts

**Signals**: OpenTelemetry collects three types of telemetry — traces (request flows), metrics (numerical measurements), and logs (structured event records). Each signal has its own Provider, instrument type, and exporter.

**API vs SDK**: The API package (`opentelemetry-api`) defines abstract interfaces. The SDK package (`opentelemetry-sdk`) provides the reference implementation. Libraries depend on API only; applications configure the SDK.

**Context Propagation**: Trace context flows through `opentelemetry.context.Context` objects, implicitly propagated via thread-local storage or explicitly passed. W3C TraceContext and Baggage propagators handle cross-process context transfer via HTTP headers.

**Resource**: An immutable representation of the entity producing telemetry (service name, host, container, Kubernetes metadata). Created via `Resource.create()` and attached to providers.

## Installation / Setup

Two core packages are installed separately:

```python
# API only — for libraries that produce telemetry
import opentelemetry.trace
import opentelemetry.metrics
import opentelemetry._logs

# SDK — for applications that consume and export telemetry
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
```

Exporters and instrumentation packages live in the `opentelemetry-python-contrib` repository and are installed separately (e.g., `opentelemetry-exporter-otlp-proto-grpc`, `opentelemetry-instrumentation-flask`).

## Usage Examples

Basic manual tracing:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

# Configure the global tracer provider
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Create and use a tracer
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("hello") as span:
    span.set_attribute("custom.key", "value")
    span.add_event("processing complete")
```

Basic metrics:

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

# Configure the global meter provider
metrics.set_meter_provider(
    MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(ConsoleMetricExporter())
        ]
    )
)

# Create and use a meter
meter = metrics.get_meter(__name__)
counter = meter.create_counter("requests.total", unit="req", description="Total requests")
counter.add(1, {"method": "GET", "path": "/api"})
```

## Advanced Topics

**Tracing API and SDK**: Spans, TracerProvider, SpanProcessor, sampling strategies, span limits, and context management → [Tracing](reference/01-tracing.md)

**Metrics API and SDK**: Instruments (Counter, Histogram, Gauge, UpDownCounter), MetricReader architecture, views, aggregation, and exemplars → [Metrics](reference/02-metrics.md)

**Logs API and SDK**: LoggerProvider, LogRecord, SeverityNumber, LoggingHandler bridge to stdlib logging, and log export → [Logs](reference/03-logs.md)

**Context Propagation**: W3C TraceContext, Baggage, TextMapPropagator, inject/extract patterns for cross-service tracing → [Context Propagation](reference/04-context-propagation.md)

**Exporters and Configuration**: OTLP (gRPC/HTTP), BatchSpanProcessor, SpanLimits, environment variables, Resource detection, and the SDK configurator → [Exporters and Configuration](reference/05-exporters-configuration.md)

**Auto-Instrumentation**: The `opentelemetry-instrument` CLI, supported frameworks (Flask, Django, FastAPI, SQLAlchemy, Redis, HTTPX, gRPC, Celery, and 40+ more), and instrumentation best practices → [Auto-Instrumentation](reference/06-auto-instrumentation.md)
