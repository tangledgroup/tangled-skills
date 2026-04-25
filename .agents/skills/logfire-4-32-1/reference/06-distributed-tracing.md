# Logfire Distributed Tracing Reference

## Context Propagation

Logfire builds on OpenTelemetry's context propagation — serializing trace context to another process so the full span tree can be reconstructed.

### Automatic Propagation

Instrumented HTTP clients automatically set the `traceparent` header:
- `httpx`, `requests`, `aiohttp` clients → add `traceparent` header
- `fastapi`, `flask`, `django` servers → extract `traceparent` header automatically
- Celery integration → propagates context to child tasks (call `instrument_celery()` in both worker and producer)

### Manual Propagation

```python
import logfire

logfire.configure()

with logfire.span('parent'):
    ctx = logfire.get_context()

# ctx looks like:
# {'traceparent': '00-d1b9e555b056907ee20b0daebf62282c-7dcd821387246e1c-01'}

# In another process/service:
with logfire.attach_context(ctx):
    logfire.info('child')  # Appears as child of parent span
```

The `traceparent` format: `{version}-{trace_id}-{span_id}-{trace_flags}`

### Thread and Process Pools

`ThreadPoolExecutor` and `ProcessPoolExecutor` are automatically patched for context propagation:

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

### Unintentional Distributed Tracing

If your service is exposed to the public internet, external clients may send `traceparent` headers that cause your spans to be grouped incorrectly or dropped (if the original trace was sampled out).

Control this with `distributed_tracing`:

```python
logfire.configure(distributed_tracing=False)  # Don't extract any trace context
# or
logfire.configure(distributed_tracing=True)   # Intentional, suppress warnings
```

Default: warns when trace context is extracted from incoming headers.

For library authors, use `attach_context(context, third_party=True)` to respect the `distributed_tracing` configuration.
