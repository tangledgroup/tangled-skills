# Trace API & SDK

**Status**: Stable (except where noted)

## Tracing API Components

The Tracing API consists of three main components:

1. **TracerProvider** — Entry point, provides access to Tracers
2. **Tracer** — Responsible for creating Spans
3. **Span** — The API to trace an operation

### Data Types

- **Timestamp**: Time since Unix epoch, millisecond-to-nanosecond precision
- **Duration**: Elapsed time between two events, millisecond-to-nanosecond precision

## TracerProvider

`TracerProvider` is the stateful configuration object. The API SHOULD provide a way to set/register and access a global default `TracerProvider`. Applications may need multiple providers with different configurations (e.g., different SpanProcessors).

### Get a Tracer

```
TracerProvider.get_tracer(
    name: str,           # REQUIRED — instrumentation scope name
    version: str = "",   # OPTIONAL — instrumentation scope version
    schema_url: str = "",# OPTIONAL — since 1.4.0
    attributes: dict = {}# OPTIONAL — since 1.13.0
) -> Tracer
```

**Parameters:**
- `name`: MUST uniquely identify the instrumentation scope (e.g., `io.opentelemetry.contrib.mongodb`). If null/empty, return a working Tracer fallback with empty name and log warning.
- `version`: Instrumentation scope version (e.g., `1.0.0`)
- `schema_url`: Schema URL for emitted telemetry
- `attributes`: Instrumentation scope attributes

**Identical vs Distinct**: Two Tracers are *identical* when all parameters match, *distinct* otherwise. Implementations MUST NOT require users to re-obtain a Tracer to pick up configuration changes — new config applies to previously returned Tracers.

## Span Lifecycle

### Creating a Span

```python
# Start a span (parent is implicit from context)
span = tracer.start_span("operation-name")

# Or as a context manager (auto-ends on exit)
with tracer.start_as_current_span("http-request") as span:
    span.set_attribute("http.method", "GET")
    do_work()
```

### Span Creation with Parent Context

```python
# Explicit parent from extracted context
parent_ctx = extract(request.headers)
with tracer.start_as_current_span(
    "child-operation",
    context=parent_ctx,
    kind=SpanKind.CLIENT
) as span:
    span.set_attribute("rpc.system", "grpc")
    do_work()
```

### SpanKind

| Kind | Description |
|------|-------------|
| `INTERNAL` | Default. Span used internally within a service |
| `SERVER` | Represents the server-side span of an RPC or HTTP request |
| `CLIENT` | Represents a client-side outbound call to a remote service |
| `PRODUCER` | Represents a producer sending messages to a broker |
| `CONSUMER` | Represents a consumer receiving messages from a broker |

### Span Operations

#### Set Attributes

```python
span.set_attribute("key", "value")
span.set_attributes({"key1": "val1", "key2": 42})
```

- Attribute keys MUST be non-null, non-empty strings (case-sensitive)
- Attribute values: string, boolean, double, int64, array of primitives, byte array, map<string, AnyValue>, or empty value
- Sets overwrite existing values for the same key
- Default attribute limits: 128 attributes per span, no value length limit

#### Add Events

```python
span.add_event(
    name="user.login",
    attributes={"user.id": "abc123", "ip": "10.0.0.1"},
    timestamp=datetime.utcnow()
)
```

- Event names MUST be strings
- Default event attribute count limit: 128 per event
- Default event count limit: 128 per span

#### Add Links

```python
from opentelemetry.trace import Link

# Link to a span in the same trace
link = Link(parent_span_context)

# Link across traces (batch processing scenario)
links = [
    Link(ctx.trace_id, ctx.span_id, attributes={"batch.item.id": str(i)})
    for i, ctx in enumerate(batch_contexts)
]

span.add_links(links)
```

- Links point to spans inside a single trace OR across different traces
- Default link count limit: 128 per span
- Default link attribute count limit: 128 per link

#### Record Exception

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

- Event name MUST be `"exception"`
- SHOULD include `exception.message`, `exception.stacktrace`, `exception.type` attributes
- Only record if exception remains unhandled and causes span status to ERROR

#### Set Status

```python
from opentelemetry.trace import StatusCode

span.set_status(StatusCode.OK, "Request processed successfully")
# or
span.set_status(StatusCode.ERROR, "Database connection failed")
```

Status values: `UNSET` (default), `OK`, `ERROR`. Once set to OK or ERROR, cannot be changed.

#### End Span

```python
span.end()  # Explicit end
# or automatic via context manager
```

- Records end timestamp
- Triggers SpanProcessor.on_end() for export

## SpanContext

`SpanContext` identifies a span within a trace and is propagated across process boundaries. It is **immutable**.

### Fields

| Field | Description |
|-------|-------------|
| `trace_id` | 16-byte array (32 hex chars), at least one non-zero byte |
| `span_id` | 8-byte array (16 hex chars), at least one non-zero byte |
| `trace_flags` | 1-byte bitmap: sampled (0x1), random (bit 7) |
| `trace_state` | List of key-value pairs for vendor-specific context |
| `is_remote` | True if received from remote, false if locally generated |
| `is_valid` | True if trace_id and span_id are non-zero |

### TraceFlags

| Flag | Bit | Description |
|------|-----|-------------|
| Sampled | 0x1 | Trace is sampled |
| Random | 0x80 | Uses random trace ID (no parent) |

### TraceState

- Carries tracing-system-specific context
- Key-value pairs separated by `,`, key=value pairs separated by `=`
- Max 32 entries, keys/values max 255 chars each
- Keys MUST match `[[a-z2-7][-a-z2-7.]{0,24},]` or vendor format `@vendor:key`

### SpanContext Operations

```python
# Create from trace/span IDs
ctx = SpanContext(
    trace_id=bytes.fromhex("..." * 32),
    span_id=bytes.fromhex("..." * 16),
    trace_flags=TraceFlags.SAMPLED,
    trace_state=TraceState(),
    is_remote=False,
    valid=True
)

# Access identifiers
trace_id_hex = ctx.trace_id.hex()   # 32-char lowercase hex
span_id_hex = ctx.span_id.hex()     # 16-char lowercase hex
trace_id_bytes = ctx.trace_id       # 16-byte array
span_id_bytes = ctx.span_id         # 8-byte array

# Validation checks
if ctx.is_valid:
    process_span(ctx)
```

## Sampling

Sampling controls which spans are recorded/exported. The SDK provides several sampler types.

### Sampler Types

| Sampler | Description | Config Parameter |
|---------|-------------|------------------|
| `AlwaysOnSampler` | Record all spans | — |
| `AlwaysOffSampler` | Record no spans | — |
| `TraceIdRatioBased` | Sample by probability | probability ∈ [0.0, 1.0] |
| `ParentBased(...)` | Respect parent's decision, use root for root spans | root sampler |
| `JaegerRemoteSampler` | Remote sampling strategy from Jaeger agent | endpoint, pollingIntervalMs, initialSamplingRate |

### Probability Sampling

```python
# Sample 25% of traces
from opentelemetry.sdk.trace.sampling import (
    ParentBased, TraceIdRatioBased, AlwaysOnSampler
)

provider = TracerProvider(
    sampler=ParentBased(root=TraceIdRatioBased(0.25))
)
```

### Remote Sampling (Jaeger)

```python
from opentelemetry.sdk.trace.sampling import JaegerRemoteSampler

sampler = JaegerRemoteSampler(
    endpoint="http://localhost:14250",
    pollingIntervalMs=5000,
    initialSamplingRate=0.25
)
# Polls backend for strategy updates; uses initial rate until reachable
```

### Span Limits (Configurable)

| Limit | Default Env Var | Default Value |
|-------|-----------------|---------------|
| Attribute count per span | `OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT` | 128 |
| Attribute value length | `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` | no limit |
| Event count per span | `OTEL_SPAN_EVENT_COUNT_LIMIT` | 128 |
| Link count per span | `OTEL_SPAN_LINK_COUNT_LIMIT` | 128 |
| Attributes per event | `OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT` | 128 |
| Attributes per link | `OTEL_LINK_ATTRIBUTE_COUNT_LIMIT` | 128 |

### TraceState Handling

- When a span is sampled **out**, the SDK MUST remove all keys from `TraceState` before propagation
- When a span is sampled **in**, `TraceState` is propagated as-is
- Implementations MUST support reading and writing `TraceState` per W3C spec

## Tracer Enabled API (Development)

```python
# Check if tracer is enabled before expensive operations
if tracer.is_enabled():
    # Only run if span will be created
    result = expensive_computation()
    span.set_attribute("result", str(result))
```

- Returns boolean: true if tracer is enabled, false otherwise
- Value can change over time — call each time before creating spans
- Helps avoid expensive operations when no spans are being recorded
