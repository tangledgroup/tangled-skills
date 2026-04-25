# Distributed Tracing

Logfire automatically propagates context across services via the `traceparent` header when using instrumented HTTP clients and servers. For manual propagation:

```python
import logfire

logfire.configure()

with logfire.span('parent'):
    ctx = logfire.get_context()

# In another process/service:
with logfire.attach_context(ctx):
    logfire.info('child')  # Appears as child of parent span
```

ThreadPoolExecutor and ProcessPoolExecutor are automatically patched for context propagation.

For web services exposed to the public internet, set `distributed_tracing=False` to prevent accidental context extraction from external clients.

See [reference/06-distributed-tracing.md](reference/06-distributed-tracing.md).
