# Sampling

Control data volume and cost with sampling strategies:

### Random Head Sampling (50% of traces)

```python
logfire.configure(sampling=logfire.SamplingOptions(head=0.5))
```

### Tail Sampling by Level and Duration

Keep all traces with errors/warnings or duration > 5 seconds:

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        level_threshold='info',
        duration_threshold=5.0,  # seconds
    )
)
```

### Combined Head + Tail Sampling

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        head=0.1,           # Keep max 10% of traces
        background_rate=0.3, # But keep 30% of non-notable traces anyway
    )
)
```

### Custom Sampling

```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

logfire.configure(
    sampling=logfire.SamplingOptions(
        head=ParentBased(MyCustomSampler())
    )
)
```

See [reference/05-sampling.md](reference/05-sampling.md) for comprehensive sampling documentation.
