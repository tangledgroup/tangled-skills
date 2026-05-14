# Tracing

## TracerProvider

The `TracerProvider` is the entry point for the tracing API. It holds configuration and provides access to `Tracer` instances.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

provider = TracerProvider(
    resource=Resource.create({"service.name": "my-service"}),
    shutdown_on_exit=True,
)
trace.set_tracer_provider(provider)
```

Key parameters:

- `sampler` — Controls which spans are recorded (default: `ParentBased(AlwaysOn())`)
- `resource` — Entity producing telemetry
- `shutdown_on_exit` — Register atexit handler to flush on process exit
- `active_span_processor` — Pre-configured span processor
- `id_generator` — Custom ID generator (default: `RandomIdGenerator`)
- `span_limits` — Limits for attributes, events, links per span

Get a tracer by instrumentation scope name:

```python
tracer = trace.get_tracer("my-library", "1.0.0")
# or via the provider directly
tracer = provider.get_tracer("my-library", "1.0.0")
```

## Tracer and Span Creation

The `Tracer` creates spans. Use `start_as_current_span` for context-manager-based spans or `start_span` for manual lifecycle control.

```python
# Context manager — span auto-ends on exit
with tracer.start_as_current_span("operation", kind=trace.SpanKind.SERVER) as span:
    span.set_attribute("http.method", "GET")
    span.set_attribute("http.status_code", 200)

# Manual lifecycle
span = tracer.start_span("manual-operation")
span.set_attribute("key", "value")
# ... do work ...
span.end()
```

Span kinds:

- `SpanKind.INTERNAL` — Default, internal operation
- `SpanKind.SERVER` — Incoming request handler
- `SpanKind.CLIENT` — Outgoing request caller
- `SpanKind.PRODUCER` — Message producer (async)
- `SpanKind.CONSUMER` — Message consumer (async)

## Span Operations

Once a span is created and recording, you can enrich it:

```python
# Set attributes
span.set_attribute("http.method", "GET")
span.set_attributes({"key1": "val1", "key2": 42})

# Add events (timestamped annotations)
span.add_event("user.login", {"user.id": "12345"})

# Add links to other spans
span.add_link(other_span.get_span_context(), {"link.reason": "correlation"})

# Set status
from opentelemetry.trace import Status, StatusCode
span.set_status(Status(StatusCode.OK))
span.set_status(Status(StatusCode.ERROR, "Something failed"))

# Record exceptions
span.record_exception(ValueError("invalid input"))

# Update span name
span.update_name("actual-operation-name")

# Check if recording
if span.is_recording():
    span.set_attribute("extra", "data")
```

## ReadableSpan

The SDK's `ReadableSpan` provides read-only access to all span data. Used by span processors and exporters:

```python
# Properties available on ReadableSpan
span.name          # Span operation name
span.context       # SpanContext (trace_id, span_id, trace_flags)
span.kind          # SpanKind
span.parent        # Parent SpanContext or None
span.start_time    # Start time in nanoseconds
span.end_time      # End time in nanoseconds
span.status        # Status (StatusCode + optional description)
span.attributes    # MappingProxyType of attributes
span.events        # Tuple of Event objects
span.links         # Tuple of Link objects
span.resource      # Resource producing the telemetry
span.instrumentation_scope  # InstrumentationScope info

# Export as JSON
json_data = span.to_json()
```

## SpanProcessor

Span processors hook into span lifecycle events. Two built-in multi-processors compose multiple processors:

```python
from opentelemetry.sdk.trace import (
    SynchronousMultiSpanProcessor,
    ConcurrentMultiSpanProcessor,
)

# Sequential processing
multi = SynchronousMultiSpanProcessor()
multi.add_span_processor(processor_a)
multi.add_span_processor(processor_b)

# Parallel processing (configurable thread count)
concurrent = ConcurrentMultiSpanProcessor(num_threads=4)
concurrent.add_span_processor(processor_a)
concurrent.add_span_processor(processor_b)
```

Custom processor:

```python
from opentelemetry.sdk.trace import SpanProcessor

class CustomProcessor(SpanProcessor):
    def on_start(self, span, parent_context=None):
        # Called synchronously when span starts
        pass

    def on_end(self, span):
        # Called synchronously when span ends
        pass

    def shutdown(self):
        # Called on TracerProvider shutdown
        pass

    def force_flush(self, timeout_millis=30000):
        # Export pending spans
        return True
```

## Sampling

Sampling controls which traces are recorded to reduce overhead. Built-in samplers:

```python
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_ON,
    ALWAYS_OFF,
    TraceIdRatioBased,
    ParentBased,
)

# Always sample
provider = TracerProvider(sampler=ALWAYS_ON)

# Sample 10% of root spans, respect parent decision for children
provider = TracerProvider(
    sampler=ParentBased(root=TraceIdRatioBased(0.1))
)

# Never sample
provider = TracerProvider(sampler=ALWAYS_OFF)
```

Sampler selection via environment variables:

- `OTEL_TRACES_SAMPLER` — One of: `always_on`, `always_off`, `traceidratio`, `parentbased_always_on` (default), `parentbased_always_off`, `parentbased_traceidratio`
- `OTEL_TRACES_SAMPLER_ARG` — Rate for ratio-based samplers (0.0 to 1.0)

```bash
# Sample 1 in 1000 traces, respecting parent decisions
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.001
```

Custom sampler:

```python
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision
from opentelemetry.trace import SpanContext, TraceState

class CustomSampler(Sampler):
    def should_sample(
        self, parent_context, trace_id, name, kind, attributes, links
    ):
        if name.startswith("health"):
            return SamplingResult(Decision.DROP)
        return SamplingResult(
            Decision.RECORD_AND_SAMPLE,
            attributes,
        )

    def get_description(self):
        return "CustomSampler"
```

## SpanLimits

Controls memory usage by limiting the number of attributes, events, and links per span:

```python
from opentelemetry.sdk.trace import SpanLimits

limits = SpanLimits(
    max_attributes=128,           # Global attribute count limit
    max_events=128,              # Max events per span
    max_links=128,               # Max links per span
    max_span_attributes=128,     # Max attributes on a span
    max_event_attributes=128,    # Max attributes per event
    max_link_attributes=128,     # Max attributes per link
    max_attribute_length=None,   # Max attribute value length (None = unlimited)
    max_span_attribute_length=None,
)

provider = TracerProvider(span_limits=limits)
```

Environment variable overrides:

- `OTEL_ATTRIBUTE_COUNT_LIMIT` — Global default: 128
- `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` — Span-specific default: 128
- `OTEL_SPAN_EVENT_COUNT_LIMIT` — Default: 128
- `OTEL_SPAN_LINK_COUNT_LIMIT` — Default: 128
- `OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT` — Default: 128
- `OTEL_LINK_ATTRIBUTE_COUNT_LIMIT` — Default: 128
- `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` — No default (unlimited)
- `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` — Inherits from global

## Context Management

Spans are implicitly propagated through context:

```python
from opentelemetry import trace
from opentelemetry.context import get_current, set_value

# Get current span
current_span = trace.get_current_span()

# Get current span from a specific context
span = trace.get_current_span(some_context)

# Set active span in context
ctx = trace.set_span_in_context(span)

# Use span as the current span
with trace.use_span(span):
    # New child spans will use this as parent
    child = tracer.start_span("child")
```

## Exception Handling

When used as a context manager, spans automatically record exceptions and set error status:

```python
try:
    with tracer.start_as_current_span(
        "risky-operation",
        record_exception=True,       # Record exception as event (default)
        set_status_on_exception=True, # Set ERROR status on exception (default)
    ) as span:
        raise ValueError("something went wrong")
except ValueError:
    pass  # Span has exception event + ERROR status recorded
```

Manual exception recording:

```python
span.record_exception(
    exception=ValueError("bad"),
    attributes={"extra.context": "info"},
    escaped=True,  # Whether exception is escaping the scope
)
```
