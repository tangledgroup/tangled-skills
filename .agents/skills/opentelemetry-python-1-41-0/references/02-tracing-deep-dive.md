# Tracing Deep Dive

## Span Creation API

### start_span() vs start_as_current_span()

```python
# start_span — returns span without modifying context
span = tracer.start_span("manual-span")
try:
    do_work(span)
finally:
    span.end()

# start_as_current_span — sets as current span in context, auto-ends on exit
with tracer.start_as_current_span("context-manager") as span:
    # trace.get_current_span() returns THIS span
    pass  # span automatically ended here

# Decorator usage — equivalent to wrapping function body with span
@tracer.start_as_current_span("decorated-function")
def my_function(arg):
    return process(arg)
```

### Using use_span() for Manual Context Management

```python
from opentelemetry.trace import use_span

span = tracer.start_span("long-lived-span")
with use_span(span, end_on_exit=True):
    # span is current in context
    do_work()
# span ended here due to end_on_exit=True
```

### Explicit Parent Context

```python
from opentelemetry.trace import set_span_in_context

# Create a span as child of an explicitly specified parent
parent = tracer.start_span("explicit-parent")
ctx = set_span_in_context(parent)

child = tracer.start_span("explicit-child", context=ctx)
try:
    # child's parent is 'parent', even if another span is currently active
    pass
finally:
    child.end()
    parent.end()
```

## Span Attributes

### Attribute Types

Attributes support the following types: `str`, `bool`, `int`, `float`, and arrays of these types.

```python
span.set_attribute("string_attr", "value")
span.set_attribute("int_attr", 42)
span.set_attribute("float_attr", 3.14)
span.set_attribute("bool_attr", True)
span.set_attribute("array_str", ["a", "b", "c"])
span.set_attribute("array_int", [1, 2, 3])

# Attribute limits — exceeding these silently drops attributes
# OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT (default: 128)
# OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT (default: unlimited)
```

### BoundedAttributes

The SDK uses `BoundedAttributes` which automatically enforce attribute count and value length limits. Excess attributes are silently dropped. Check for drops:

```python
span = tracer.start_as_current_span("test")
span.set_attribute("key1", "val1")
# ... many more attributes ...
# span.dropped_attributes would be > 0 if limit was hit
```

## Span Events

Events are timestamped annotations on a span:

```python
span.add_event("cache.miss", {"cache.key": "user:123"})
span.add_event("database.query", {"db.statement": "SELECT * FROM users WHERE id = ?", "db.rows": 5})
span.add_event("http.response", {"http.status_code": 200, "http.content_length": 1024})

# Event limits — OTEL_SPAN_EVENT_COUNT_LIMIT (default: 128)
# OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT (default: 128)
```

## Span Status

```python
from opentelemetry.trace import Status, StatusCode

# Default: UNSET (no status explicitly set)
span.status  # Status(StatusCode.UNSET)

# Set error status on exception
try:
    risky_operation()
except Exception as ex:
    span.set_status(Status(StatusCode.ERROR, str(ex)))
    span.record_exception(ex)

# Explicitly mark success (overrides UNSET)
span.set_status(Status(StatusCode.OK))

# Auto-set on exception (set_status_on_exception=True by default in start_as_current_span)
with tracer.start_as_current_span("auto-error", set_status_on_exception=True):
    raise ValueError("something went wrong")
    # span status automatically set to ERROR with exception details
```

## Span Links

Links connect spans that are causally related but not parent-child:

```python
from opentelemetry.trace import Link

# Fan-out pattern: one batch span linked to multiple child spans
with tracer.start_as_current_span("batch-job") as batch_span:
    for item_id in items:
        # Get context of the batch span to link to it
        batch_ctx = batch_span.get_span_context()
        link = Link(batch_ctx, {"item.id": item_id})

        with tracer.start_as_current_span(
            f"process-item-{item_id}",
            links=[link]  # causal link to batch span
        ) as item_span:
            process(item_id)

# Fan-in pattern: multiple upstream spans linked to downstream consumer
upstream_contexts = [get_span_context(s) for s in upstream_spans]
links = [Link(ctx, {"upstream.service": get_service_name(s)}) for ctx in upstream_contexts]

with tracer.start_as_current_span("consume-messages", links=links):
    process_all()
```

## SpanKinds Reference

| Kind | Value | Description | Parent | Child |
|------|-------|-------------|--------|-------|
| `INTERNAL` | 0 | Default; internal operation | Any | INTERNAL, SERVER, CLIENT |
| `SERVER` | 1 | Handles remote request | CLIENT (remote) | INTERNAL, CLIENT |
| `CLIENT` | 2 | Calls remote service | SERVER or any | INTERNAL, CLIENT |
| `PRODUCER` | 3 | Sends message to broker | Any | CONSUMER |
| `CONSUMER` | 4 | Receives message from broker | PRODUCER | INTERNAL |

## SpanProcessor Interface

Implement custom span processors by subclassing `SpanProcessor`:

```python
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan, Span
from opentelemetry.context import Context

class MySpanProcessor(SpanProcessor):
    def on_start(self, span: Span, parent_context: Context = None) -> None:
        # Called when a span starts (synchronous, non-blocking)
        pass

    def _on_ending(self, span: Span) -> None:
        # Called when span is about to end (synchronous, non-blocking)
        pass

    def on_end(self, span: ReadableSpan) -> None:
        # Called when a span ends (synchronous, non-blocking)
        # This is where you'd export the span
        self.export_span(span)

    def shutdown(self) -> None:
        # Called when TracerProvider is shut down
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        # Force immediate export of all pending spans
        return True
```

## Span Exporters

### ConsoleSpanExporter (Debugging)

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)
# Outputs JSON spans to stdout
```

### FileSpanExporter

```python
from opentelemetry.sdk.trace.export import FileSpanExporter, BatchSpanProcessor

exporter = FileSpanExporter(
    filename="/var/log/traces.jsonl",
    indentation=2,
)
provider.add_span_processor(BatchSpanProcessor(exporter))
```

### InMemorySpanExporter (Testing)

```python
from opentelemetry.sdk.trace.export import InMemorySpanExporter, SimpleSpanProcessor

exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(exporter))

# Later, in tests:
spans = exporter.get_finished_spans()
assert len(spans) == 1
assert spans[0].name == "expected-span-name"
```

### Custom SpanExporter

```python
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult, ReadableSpan
from typing import Sequence

class MyCustomExporter(SpanExporter):
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            # Access span data
            print(f"Span: {span.name}, Trace: {span.context.trace_id:032x}")
            for attr_name, attr_value in span.attributes.items():
                print(f"  {attr_name}: {attr_value}")
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
```

## TracerProvider Configuration

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

provider = TracerProvider(
    resource=Resource.create({
        "service.name": "my-service",
        "service.version": "1.0.0",
    }),
    sampler=ParentBasedTraceIdRatio(rate=0.1),  # 10% sampling
    # tracer_configs can be used for per-library configuration
)
```

## Tracer Configuration

```python
# Get tracer with full metadata
tracer = provider.get_tracer(
    instrumenting_module_name="my.library",
    instrumenting_library_version="2.0.0",
    schema_url="https://opentelemetry.io/schemas/1.15.0",
    attributes={"library.language": "python"},
)

# Using convenience function (uses global provider if none specified)
from opentelemetry import trace
tracer = trace.get_tracer("my.library", "2.0.0")
```

## IdGenerator

Customize trace/span ID generation:

```python
from opentelemetry.sdk.trace.id_generator import IdGenerator, RandomIdGenerator

# Default: 16-byte random IDs
provider = TracerProvider(id_generator=RandomIdGenerator())

# Custom ID generator (must produce valid 16-byte trace IDs and 8-byte span IDs)
class MyIdGenerator(IdGenerator):
    def generate_trace_id(self) -> int:
        return ...  # 128-bit integer

    def generate_span_id(self) -> int:
        return ...  # 64-bit integer
```
