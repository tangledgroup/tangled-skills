# Core Concepts

## The Three Signals

OpenTelemetry collects three types of telemetry data:

### Traces
A trace represents the journey of a request as it flows through a distributed system. Each trace consists of one or more spans that form a directed acyclic graph (DAG). Spans are created when an operation starts and ended when it completes, with each span recording its duration, attributes, events, and status.

Key components:
- **Trace**: A tree of spans representing a single request flow
- **Span**: A single operation within a trace (has start time, end time, attributes, parent)
- **SpanContext**: Immutable identifier for a span (trace_id, span_id, trace_flags)
- **Tracer**: The API object used to create and manage spans
- **TracerProvider**: Factory that produces Tracers

### Metrics
Metrics are numerical measurements collected over time. OpenTelemetry supports four instrument types:

| Instrument | Type | Direction | Example |
|------------|------|-----------|---------|
| Counter | Synchronous | Monotonic increase | Total requests served |
| UpDownCounter | Synchronous | Can go up or down | Active connections |
| Histogram | Synchronous | Distribution of values | Request latency |
| Gauge | Synchronous (point) | Current value | Memory usage |

Plus asynchronous variants that use callbacks for values that can't be instrumented inline:
- **ObservableCounter**: Monotonic, read via callback
- **ObservableUpDownCounter**: Can go up/down, read via callback
- **ObservableGauge**: Current value, read via callback

### Logs
Logs are structured log records that can be correlated with traces. In v1.41.0, logs are integrated by wrapping Python's standard `logging` module with a `LoggingHandler` that enriches log records with trace context (trace_id, span_id, service name).

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│           Application Code                  │
│  tracer.start_as_current_span(...)          │
│  meter.create_counter(...)                  │
│  logging.info(...)                          │
└──────────────────────────┬──────────────────┘
                           │
┌──────────────────────────▼──────────────────┐
│           opentelemetry-api                 │
│  TracerProvider, MeterProvider, Logger      │
│  (abstract interfaces + no-op impl)         │
└──────────────────────────┬──────────────────┘
                           │
┌──────────────────────────▼──────────────────┐
│           opentelemetry-sdk                 │
│  TracerProvider, MeterProvider, Logger      │
│  (reference implementation)                 │
│  ┌─────────────┬────────────┬────────────┐ │
│  │   Tracing   │   Metrics  │    Logs    │ │
│  │ SpanProcessor│ MeterRead │ LogRecord  │ │
│  │ Sampler     │ Instruments│ Handler    │ │
│  └─────────────┴────────────┴────────────┘ │
└──────────────────────────┬──────────────────┘
                           │
┌──────────────────────────▼──────────────────┐
│         Exporters / Propagators             │
│  OTLP, Zipkin, Jaeger, Prometheus           │
│  B3, W3C Trace Context, Jaeger format       │
└─────────────────────────────────────────────┘
```

## Span Lifecycle

1. **Creation**: `tracer.start_span(name)` or `tracer.start_as_current_span(name)`
2. **Active**: Span is the current span in context; attributes/events can be added
3. **End**: `span.end()` called explicitly, or context manager exits
4. **Processing**: `SpanProcessor.on_start()` → work → `SpanProcessor._on_ending()` → `SpanProcessor.on_end()`
5. **Export**: Exporter sends span data to backend

## Context Propagation

OpenTelemetry uses a context system to carry trace information across execution boundaries:

1. **Context** — Thread-local storage for current span, baggage, and custom values
2. **Propagator** — Serializes/deserializes context into carrier (HTTP headers, MQ headers)
3. **Carrier** — Transport-specific data structure (e.g., HTTP headers dict)

Default propagators: W3C Trace Context (`traceparent`/`tracestate`) + W3C Baggage.

## Resources

Resources identify the entity producing telemetry. They are attached to every span, metric, and log record:

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
})
```

Auto-detected attributes include `telemetry.sdk.*`, `process.*`, and `os.*` attributes.

## Instrumentation Scope

Each tracer/meter is associated with an instrumentation scope containing:
- **name**: Library/instrumentation name (e.g., `"opentelemetry.instrumentation.flask"`)
- **version**: Version string of the instrumentation library
- **schema_url**: Optional URL to the schema definition

## Semantic Conventions

Standardized attribute names for common operations. Install with `pip install opentelemetry-semantic-conventions`:

```python
from opentelemetry.semconv.trace import SpanAttributes

span.set_attribute(SpanAttributes.HTTP_METHOD, "GET")
span.set_attribute(SpanAttributes.HTTP_URL, "https://example.com/api")
span.set_attribute(SpanAttributes.DB_SYSTEM, "postgresql")
span.set_attribute(SpanAttributes.NET_TRANSPORT, "IP.TCP")
```

## Sampling

Sampling controls which spans are recorded and exported. It happens at span creation time:

1. **Root sampler** is called for root spans (no parent)
2. **ParentBased wrapper** checks parent's sampling decision first
3. If parent is sampled, child inherits; if not, root sampler decides

Built-in samplers:
- `ALWAYS_ON` — Record everything
- `ALWAYS_OFF` — Record nothing
- `TraceIdRatioBased(rate)` — Probabilistic sampling by trace ID hash
- `ParentBased(root)` — Respect parent's decision, use root for new traces
- `ParentBasedTraceIdRatio(rate)` — Parent-aware probabilistic (default)

Custom samplers implement `Sampler.should_sample()` and `Sampler.get_description()`.
