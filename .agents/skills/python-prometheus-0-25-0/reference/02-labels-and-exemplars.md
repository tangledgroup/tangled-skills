# Labels and Exemplars

## Contents
- Declaring Labels
- Using Labels
- Initializing Label Sets
- Removing Label Sets
- Exemplars

## Declaring Labels

Labels are declared via `labelnames` in the metric constructor. They define dimensions for grouping related time series.

```python
from prometheus_client import Counter

c = Counter('my_requests_total', 'HTTP requests', labelnames=['method', 'endpoint'])
```

Follow Prometheus best practices on [naming](https://prometheus.io/docs/practices/naming/) and [labels](https://prometheus.io/docs/practices/instrumentation/#use-labels).

Reserved label names:
- `quantile` — reserved by Summary
- `le` — reserved by Histogram

## Using Labels

Apply labels via `.labels()` before calling the metric method. Use positional or keyword arguments.

**Positional** (values in same order as `labelnames`):

```python
c.labels('get', '/').inc()
c.labels('post', '/submit').inc()
```

**Keyword arguments**:

```python
c.labels(method='get', endpoint='/').inc()
c.labels(method='post', endpoint='/submit').inc()
```

Chaining works with any metric type:

```python
gauge.labels(host='server1').set(42)
histogram.labels(method='GET').observe(0.5)
summary.labels(task_type='email').time()
```

## Initializing Label Sets

Metrics with labels are not initialized until `.labels()` is called, because the client cannot know what label values will appear. It is recommended to pre-initialize known label sets:

```python
c = Counter('my_requests_total', 'HTTP requests', ['method', 'endpoint'])
c.labels('get', '/')       # initializes this labelset
c.labels('post', '/submit') # initializes this labelset
```

This ensures the label set appears in output even if its value is zero.

## Removing Label Sets

**`remove(*labelvalues)`** — Remove a specific labelset. Values in same order as `labelnames`.

```python
c.labels('get', '/').inc()
c.remove('get', '/')
```

**`remove_by_labels(labels)`** — Remove all labelsets that partially match the given dict.

```python
c.remove_by_labels({'method': 'get'})  # removes all where method='get'
```

**`clear()`** — Remove all labelsets at once.

```python
c.clear()
```

Note: Remove and clear of labels are not supported in multiprocess mode.

## Exemplars

Exemplars attach trace context to individual observations on Counter and Histogram metrics. They enable tracing from metrics in Prometheus UI.

### Usage

**Counter**:

```python
from prometheus_client import Counter

c = Counter('my_requests_total', 'HTTP Failures', ['method', 'endpoint'])
c.labels('get', '/').inc(exemplar={'trace_id': 'abc123'})
c.labels('post', '/submit').inc(1.0, {'trace_id': 'def456'})
```

**Histogram**:

```python
from prometheus_client import Histogram

h = Histogram('request_latency_seconds', 'Description of histogram')
h.observe(4.7, {'trace_id': 'abc123'})
```

### Important notes

- Exemplars are only rendered in **OpenMetrics** exposition format
- To view exemplars, use `generate_latest` from `prometheus_client.openmetrics.exposition`
- Prometheus requires the feature flag: `--enable-feature=exemplar-storage`
- Exemplars are not supported in multiprocess mode
