# Context, Propagators & Baggage

**Status**: Stable (except where noted)

## Context Mechanism

A `Context` is an immutable propagation mechanism for carrying execution-scoped values across API boundaries and between logically associated execution units. All cross-cutting concerns (traces, metrics, baggage) share the same Context object.

### Core Operations

```python
from opentelemetry.context import (
    Context, get_current, set_value, get_value,
    attach, detach, create_key
)

# Create a key for a cross-cutting concern
span_key = create_key("span")

# Get current context
current_ctx = get_current()

# Set value in context (returns NEW context — original is immutable)
new_ctx = set_value(current_ctx, span_key, my_span)

# Get value from context
span = get_value(span_key, context=new_ctx)

# Attach/detach for implicit context propagation (thread-local/task-local)
token = attach(new_ctx)      # Make new_ctx the current context
detach(token)                # Restore previous context
```

### Implicit Context (Language-Specific)

Languages with implicit context support provide additional operations:

| Operation | Description |
|-----------|-------------|
| `get_current()` | Get the implicit current context |
| `attach(context)` | Make context the current one, return token |
| `detach(token)` | Restore previous context from token |
| `set_value(key, value)` | Set in current implicit context |
| `get_value(key)` | Get from current implicit context |

## Propagators

Propagators serialize and deserialize cross-cutting concern values across process boundaries.

### TextMapPropagator Interface

```python
from opentelemetry.propagate import extract, inject, propagate

# Extract context from carrier (e.g., HTTP headers)
ctx = extract(carrier_getter)  # Returns Context
# Or with dict:
ctx = extract(headers_dict)

# Inject context into carrier
inject(carrier_setter)  # Calls setter for each header
# Or with dict:
inject(headers_dict)

# Enable global propagation
propagate.set_global_textmap(propagator)
```

### Built-in Propagators

| Propagator | Headers | Description |
|------------|---------|-------------|
| `TraceContextPropagator` | `traceparent`, `tracestate` | W3C TraceContext standard |
| `BaggagePropagator` | `baggage` | W3C Baggage standard |
| `B3SingleFormatPropagator` | `b3` | B3 single-header format |
| `B3MultiFormatPropagator` | `X-B3-TraceId`, `X-B3-SpanId`, etc. | B3 multi-header format |
| `JaegerPropagator` | `uber-trace-id` | Legacy Jaeger format (deprecated) |

### Configuring Propagators

```bash
# Set propagators via environment variable
export OTEL_PROPAGATORS=tracecontext,baggage,b3

# No automatic propagation
export OTEL_PROPAGATORS=none
```

```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormatPropagator

# Set a single propagator
set_global_textmap(B3MultiFormatPropagator())

# Multiple propagators (order matters — last one wins on conflicts)
from opentelemetry.propagate import CompositePropagator
propagator = CompositePropagator([
    TraceContextPropagator(),
    B3MultiFormatPropagator(),
])
set_global_textmap(propagator)
```

## Baggage API

Baggage is a set of name/value pairs for propagating application-defined context across service boundaries. Based on the W3C Baggage Specification.

### Key Properties

- Each name associated with **exactly one value** (more restrictive than W3C spec)
- Names: any valid non-empty UTF-8 string (alpha-numeric recommended for compatibility)
- Values: any valid UTF-8 string
- Case-sensitive names AND values
- Immutable container

### Operations

```python
from opentelemetry.baggage import (
    set_baggage, get_baggage, get_all_baggage,
    remove_baggage, get_baggage_context, update_baggage
)

# Set baggage values
set_baggage("user.id", "abc123")
set_baggage("tenant", "acme-corp")
set_baggage("feature.flag", "new-ui%20beta")  # URL-encoding for special chars

# Get a specific value
user_id = get_baggage("user.id")  # Returns "abc123"

# Get all name/value pairs
all_baggage = get_all_baggage()  # Returns dict-like object

# Create context with baggage for a specific operation
with get_baggage_context({"region": "us-east-1", "version": "2"}):
    do_work()  # Has region and version baggage attached

# Update baggage in current context
update_baggage({"user.tier": "premium"})

# Remove specific key
remove_baggage("tenant")
```

### URL Encoding

Baggage values use percent-encoding for special characters:
- Space → `%20`
- Comma → `%2C` (separator character)
- Equals → `%3D`
- Control characters must be encoded

### Baggage in Context

Baggage is automatically propagated with the Context through all cross-cutting concerns. When extracting context from incoming requests, baggage headers are parsed and associated with the resulting Context.

```python
# Incoming request — extract propagates baggage
ctx = extract(request.headers)  # Parses traceparent + baggage headers
user_id = get_baggage("user.id", context=ctx)

# Outgoing request — inject propagates baggage
headers = {}
inject(headers, context=ctx)  # Adds Baggage header
```

## TraceContext Header Format

### traceparent Header

```
traceparent: {version}-{trace-id}-{parent-id}-{trace-flags}
```

Example:
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

| Component | Length | Description |
|-----------|--------|-------------|
| version | 2 hex chars | Version (currently `00`) |
| trace-id | 32 hex chars | 128-bit trace ID |
| parent-id | 16 hex chars | 64-bit span ID |
| trace-flags | 2 hex chars | Bit flags (bit 0 = sampled) |

### tracestate Header

```
tracestate: vendor=value,vendor2=value2
```

- Max 32 key-value pairs
- Each key/max value: 255 characters
- Keys match `[[a-z2-7][-a-z2-7.]{0,24},]` or `@vendor:key` format
- Comma-separated entries, key=value pairs separated by `=`

## IsRemote Flag

The `is_remote` flag on SpanContext indicates whether the context was received from a remote source:

| Scenario | is_remote |
|----------|-----------|
| Extracted from incoming headers | `true` |
| Newly created child span | `false` |
| Locally generated root span | `false` |

This flag is used by propagators and sampling logic to distinguish between locally-originated and remotely-propagated context.
