# Logfire Sampling Reference

## Overview

Sampling discards some traces/spans to reduce storage and cost. Trade-off between completeness and efficiency.

- **Head sampling**: Decision made at trace start (simpler, more common)
- **Tail sampling**: Decision delayed until trace end (more information available, more complex)

## Random Head Sampling

```python
import logfire

logfire.configure(sampling=logfire.SamplingOptions(head=0.5))  # Keep 50% of traces
```

Child logs/spans are kept only if the parent span is kept.

## Tail Sampling by Level and Duration

Keep all traces with errors/warnings or duration > threshold:

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        level_threshold='info',   # Keep spans/logs above this level
        duration_threshold=5.0,   # Keep spans lasting > 5 seconds
    )
)
```

## Combined Head + Tail Sampling

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        head=0.1,               # Max 10% of traces kept
    )
)
```

## Background Rate

Keep a fraction of all traces even if they don't meet tail criteria:

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        background_rate=0.3,     # Keep ~30% of non-notable traces
    )
)
```

## Custom Head Sampling

Pass an OpenTelemetry Sampler for full control:

```python
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF, ALWAYS_ON, ParentBased, Sampler, TraceIdRatioBased,
)
import logfire


class MySampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, *args, **kwargs):
        if name == 'exclude_me':
            return ALWAYS_OFF
        elif name == 'partial':
            return TraceIdRatioBased(0.5)
        else:
            return ALWAYS_ON

    def get_description(self):
        return 'MySampler'


logfire.configure(
    sampling=logfire.SamplingOptions(head=ParentBased(MySampler()))
)
```

Always wrap custom samplers in `ParentBased` to keep child spans with their parents.

## Custom Tail Sampling

Pass a function that returns probability (0.0–1.0) of including the trace:

```python
import logfire


def get_tail_sample_rate(span_info):
    if span_info.duration >= 1:
        return 0.5   # 50% of traces lasting >= 1 second
    if span_info.level > 'warn':
        return 0.3   # 30% of warning/error traces under 1 second
    return 0.1       # 10% of other traces


logfire.configure(
    sampling=logfire.SamplingOptions(head=0.5, tail=get_tail_sample_rate)
)
```

`span_info` is a `TailSamplingSpanInfo` with:
- `duration`: Trace duration in seconds
- `level`: Special `SpanLevel` object (comparable to log level names)

## Caveats

### Memory Usage

Tail sampling keeps all spans in memory until the trace is included or completed. Large traces with many spans can consume significant memory. The duration threshold helps because Logfire can detect exceeding it before a span completes.

### Distributed Tracing

Logfire's tail sampling works only within one process. For distributed tail sampling, deploy the [Tail Sampling Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/tailsamplingprocessor/README.md) in the OpenTelemetry Collector.

If a trace spans multiple processes:
- Spans from the Logfire SDK may be discarded while spans from other processes are included → incomplete trace
- Workaround: use `logfire.attach_context({})` to start new traces for background tasks

### Background Tasks After Root Span Ends

If a root span ends and doesn't meet tail criteria, all its spans are discarded. Spans started after the root ends will be included but without their parent. Fix with:

```python
async def background_task():
    with logfire.attach_context({}):  # Start new trace
        with logfire.span('new trace'):
            await asyncio.sleep(0.2)
            logfire.info('background')
```
