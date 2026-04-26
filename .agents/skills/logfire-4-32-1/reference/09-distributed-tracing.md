# Distributed Tracing

## Overview

Logfire builds on OpenTelemetry context propagation to distribute tracing across services. Context determines the parent trace/span of a new span/log and whether it should be included by sampling. Context propagation serializes this context and sends it to another process, allowing the full tree of spans to be reconstructed and viewed together.

## Manual Context Propagation

```python
import logfire

logfire.configure()

with logfire.span('parent'):
    ctx = logfire.get_context()

# Attach the context in another execution environment
with logfire.attach_context(ctx):
    logfire.info('child')  # Child of the parent span
```

`ctx` contains a `traceparent` string with four fields:
- Version number (e.g., `00`)
- `trace_id` (32-character hex)
- Parent `span_id` (16-character hex)
- `trace_flags` — indicates whether the trace should be included by sampling

Example: `{'traceparent': '00-d1b9e555b056907ee20b0daebf62282c-7dcd821387246e1c-01'}`

## Automatic Propagation via Integrations

OpenTelemetry instrumentation libraries handle context propagation automatically:

- **HTTP clients** (requests, httpx) — automatically set `traceparent` header on outgoing requests
- **Web servers** (Flask, FastAPI) — automatically extract `traceparent` header for incoming requests
- **Celery** — automatically propagates context to child tasks. Must call `logfire.instrument_celery()` in both worker processes and the application that enqueues tasks

## Thread and Pool Executors

Logfire automatically patches `ThreadPoolExecutor` and `ProcessPoolExecutor` to propagate context:

```python
from concurrent.futures import ThreadPoolExecutor
import logfire

logfire.configure()

@logfire.instrument('Doubling {x}')
def double(x: int):
    return x * 2

with logfire.span('Doubling everything') as span:
    executor = ThreadPoolExecutor()
    results = list(executor.map(double, range(3)))
    span.set_attribute('results', results)
```

**ProcessPoolExecutor note**: Configuration is serialized to child processes. If serialization fails (unpicklable objects), a warning is emitted. Define callbacks at module level when possible.

## Unintentional Distributed Tracing

Instrumented web servers automatically extract `traceparent` headers by default. This can cause issues when:
- Spans pick up wrong context from externally instrumented clients
- Cloud providers (e.g., Google Cloud Run) inject trace context
- Spans are mysteriously grouped together or missing

Logfire warns by default when trace context is extracted. Control with `distributed_tracing`:

```python
# Disable — recommended for public-facing web services
logfire.configure(distributed_tracing=False)

# Enable — silences warning, implies intentional propagation
logfire.configure(distributed_tracing=True)
```

Setting to `False` prevents trace context extraction but you can still manually attach/inject context. Setting to `True` implies intentional propagation.

The `distributed_tracing` config only applies when raw OTel API extracts context (typically third-party libraries). `logfire.attach_context()` assumes intentional propagation by default. For library authors, use `attach_context(context, third_party=True)` to respect the configuration.
