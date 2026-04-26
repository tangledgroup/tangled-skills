# Context and Propagation

## Context

A Context is an immutable propagation mechanism carrying execution-scoped values across API boundaries and between logically associated execution units. All cross-cutting concerns (traces, metrics, baggage) share the same Context for in-process state access.

### Key Operations

- **Create a key**: Creates an opaque key unique to a cross-cutting concern. The key name is for debugging only and does not uniquely identify the key.
- **Get value**: Retrieves the value for a key from a Context.
- **Set value**: Returns a new Context containing the updated value (original Context is unchanged due to immutability).

### Optional Global Operations

For languages using implicit Context (thread-local, async-local):

- **Get current Context**: Returns the Context associated with the caller's current execution unit
- **Attach Context**: Associates a Context with the current execution unit. Returns a Token for restoration
- **Detach Context**: Restores the previous Context using a Token from Attach

Users writing instrumentation in languages with implicit Context are discouraged from using the Context API directly — they should manipulate Context through cross-cutting concern APIs instead.

## Propagators

Propagators serialize and deserialize cross-cutting concern values across process boundaries.

### TextMapPropagator

The primary Propagator type. Injects values into and extracts values from carriers as text (typically HTTP headers).

```python
# Injection (outgoing request)
carrier = {}
propagator.inject(carrier, context=ctx)
# carrier now contains {"traceparent": "00-...", "baggage": "..."}

# Extraction (incoming request)
ctx = propagator.extract(context=Context(), carrier=request_headers)
```

### W3C TraceContext Propagator

The standard propagator implementing the W3C Trace Context specification (`https://www.w3.org/TR/trace-context/`).

#### Headers

- **`traceparent`**: `version-traceid-spanid-traceflags`
  - Format: `{version}-{trace-id}-{span-id}-{trace-flags}`
  - Example: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
  - TraceId: 32 hex characters (16 bytes)
  - SpanId: 16 hex characters (8 bytes)
  - TraceFlags: 2 hex characters (sampling bit = `01`)

- **`tracestate`**: Vendor-specific key-value list
  - Format: `{vendor}-{key}={value},{vendor2}-{key2}={value2},...`
  - Max 32 list members
  - Used for vendor-specific context (e.g., sampling probability)

### Environment Variables as Context Propagation Carriers

Environment variables can serve as carriers for propagating context. This is useful for process spawning scenarios where HTTP headers are not available.

## Baggage

Baggage propagates application-defined name/value pairs across service boundaries. Based on the W3C Baggage Specification (`https://www.w3.org/TR/baggage/`).

### Baggage API

- **Get Value(name)**: Returns the value for a name, or null if not present
- **Get All Values()**: Returns all name/value pairs (order is not significant)
- **Set Value(name, value)**: Returns new Baggage with the entry set
- **Remove Value(name)**: Returns new Baggage with the entry removed
- **Context Interaction**: Extract/combine Baggage with Context

### Constraints

- Each name MUST map to exactly one value (more restrictive than W3C spec)
- Names are any valid non-empty UTF-8 strings
- Values are any valid UTF-8 strings
- Both names and values are case-sensitive
- Baggage container is immutable (preserves Context immutability)
- The Baggage API MUST be fully functional without an installed SDK

### W3C Baggage Header

```
Baggage: key1=value1,key2=value2;key2option=val2
```

- Keys restricted to RFC7230 token characters for wire format
- For maximum compatibility, alphanumeric names are strongly recommended
- Options can be attached to values (e.g., `key=value;xyz=abc`)

### Use Cases

- Annotating telemetry with context from prior services in a transaction
- Including API user/token context for SaaS providers
- Linking browser version to failures in downstream services
- Adding contextual information to metrics, traces, and logs

### Propagation Conflict Resolution

When both incoming and existing baggage are present, the resolution strategy determines which values take precedence. The spec defines how conflicts between extracted and local baggage entries are handled.

## Propagator Configuration

Propagators are configured through the `OTEL_PROPAGATORS` environment variable:

```bash
# Enable W3C TraceContext and Baggage (recommended default)
export OTEL_PROPAGATORS="tracecontext,baggage"

# Disable all propagation
export OTEL_PROPAGATORS=""
```
