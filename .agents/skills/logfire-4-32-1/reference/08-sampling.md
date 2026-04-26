# Sampling

## Overview

Sampling discards some traces or spans to reduce storage and analysis costs. It's a trade-off between cost and data completeness.

**Head sampling** — decision made at the beginning of a trace. Simpler and more common.

**Tail sampling** — decision delayed, possibly until trace end. More information available but adds complexity.

Sampling usually happens at trace level — entire traces are kept or discarded so remaining traces are complete.

## Random Head Sampling

```python
import logfire

logfire.configure(sampling=logfire.SamplingOptions(head=0.5))

for x in range(10):
    with logfire.span(f'span {x}'):
        logfire.info(f'log {x}')
```

Keeps ~50% of traces. Child logs are kept if and only if parent span is kept.

## Tail Sampling by Level and Duration

`logfire.SamplingOptions.level_or_duration()` creates tail sampling that keeps traces with:

1. At least one span/log with level greater than `info` (default threshold), or
2. At least one span with duration greater than 5 seconds (default threshold)

```python
import time
import logfire

logfire.configure(sampling=logfire.SamplingOptions.level_or_duration())

# These info spans are excluded
with logfire.span('excluded span'):
    logfire.info('info log')

# Error spans are included
with logfire.span('included span'):
    logfire.error('error log')

# Long-running spans are included
with logfire.span('duration span'):
    time.sleep(6)
```

Customize thresholds:

```python
logfire.configure(sampling=logfire.SamplingOptions.level_or_duration(
    level_threshold='warn',
    duration_threshold=10,  # seconds
))
```

## Combining Head and Tail Sampling

```python
import logfire

logfire.configure(sampling=logfire.SamplingOptions(level_or_duration(head=0.1)))
```

Only 10% of traces pass head sampling. Of those, tail sampling further filters — traces not meeting criteria are discarded.

## Background Rate

Keep a fraction of all traces even if they don't meet tail sampling criteria:

```python
import logfire

logfire.configure(sampling=logfire.SamplingOptions(level_or_duration(background_rate=0.3)))
```

About 30% of info-level logs and 100% of error logs are kept. The trace ID is compared against head and background rates for inclusion, so probabilities don't depend on span count.

## Caveats

### Memory Usage

For tail sampling, all spans in a trace are kept in memory until the trace is included or completed and discarded. Large traces can consume significant memory.

In practice this is usually OK because large traces typically exceed the duration threshold, triggering inclusion and freeing memory. Problems may occur when:
- Duration threshold is set very high
- Spans are produced extremely rapidly
- Spans contain large attributes

### Distributed Tracing

Logfire's tail sampling is implemented in the SDK and only works for traces within one process. For distributed tail sampling, deploy the [Tail Sampling Processor in the OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/tailsamplingprocessor/README.md).
