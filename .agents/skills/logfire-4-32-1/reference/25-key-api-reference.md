# Key API Reference

### `logfire.configure(**kwargs)`
Initialize Logfire. Call once at application startup. Parameters control token, scrubbing, sampling, environments, service name, distributed tracing behavior, and more.

### `logfire.span(name, **attributes)`
Create a span (context manager or decorator). Measures duration, captures exceptions, accepts child spans/logs.

### `logfire.info(message, **kwargs)` through `logfire.fatal()`
Log messages at various severity levels. Use message templates with `{placeholder}` syntax.

### `logfire.metric_histogram(name, unit, description)`
Create a histogram metric for recording latency/distribution data. Call `.record(value)` to add samples.

### `logfire.instrument_<package>()`
One-call auto-instrumentation for 40+ libraries. Must be called after `configure()`.

### `logfire.ScrubbingOptions(extra_patterns=[], callback=None)`
Configure sensitive data scrubbing behavior.

### `logfire.SamplingOptions(head=rate, tail=func, level_or_duration())`
Configure sampling strategies for controlling data volume.
