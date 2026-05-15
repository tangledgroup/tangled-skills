# Metric Types

## Contents
- Counter
- Gauge
- Summary
- Histogram
- Info
- Enum

## Counter

A value that only ever goes up. Use for things you count — requests served, errors raised, bytes sent. Resets to zero when the process restarts.

### Constructor

```python
Counter(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY)
```

`namespace`, `subsystem`, and `name` join with underscores: `myapp_http_requests_total`.

If the name has a `_total` suffix, it is stripped internally and re-added on exposition (OpenMetrics compatibility).

Pass `registry=None` to skip global registration (useful in tests).

### Methods

**`inc(amount=1, exemplar=None)`** — Increment by given amount. Amount must be non-negative. Fractional increments allowed.

```python
c.inc()                    # +1
c.inc(5)                   # +5
c.inc(0.7)                 # fractional OK
c.inc(exemplar={'trace_id': 'abc123'})  # with exemplar (OpenMetrics only)
```

**`reset()`** — Reset to zero. Use when a logical process restarts without restarting the Python process.

```python
c.reset()
```

**`count_exceptions(exception=Exception)`** — Decorator or context manager that increments on exception.

```python
@c.count_exceptions()
def f():
    pass

with c.count_exceptions(ValueError):
    pass
```

### Real-world example

```python
from prometheus_client import Counter, start_http_server

REQUESTS = Counter(
    'requests_total',
    'Total HTTP requests received',
    labelnames=['method', 'status'],
    namespace='myapp',
)
EXCEPTIONS = Counter(
    'exceptions_total',
    'Total unhandled exceptions',
    labelnames=['handler'],
    namespace='myapp',
)

def handle_request(method, handler):
    with EXCEPTIONS.labels(handler=handler).count_exceptions():
        status = '200'
    REQUESTS.labels(method=method, status=status).inc()

if __name__ == '__main__':
    start_http_server(8000)
```

Produces: `myapp_requests_total{method="GET",status="200"}`

## Gauge

A value that can go up and down. Use for things sampled at a point in time — active connections, queue depth, memory usage, temperature.

### Constructor

```python
Gauge(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY, multiprocess_mode='all')
```

`multiprocess_mode` controls aggregation across processes: `all`, `min`, `max`, `sum`, `mostrecent`, or prepend `live` (e.g. `livesum`) to only consider living processes.

### Methods

**`inc(amount=1)`** / **`dec(amount=1)`** — Increment or decrement.

```python
g.inc()
g.inc(3)
g.dec()
g.dec(10)
```

Note: raises `RuntimeError` if `multiprocess_mode` is `mostrecent` or `livemostrecent`.

**`set(value)`** — Set to exact value.

```python
g.set(42.5)
```

**`set_to_current_time()`** — Set to current Unix timestamp. Useful for tracking when an event last occurred.

```python
g.set_to_current_time()
```

**`track_inprogress()`** — Decorator or context manager that increments on entry, decrements on exit.

```python
@g.track_inprogress()
def process_job():
    pass

with g.track_inprogress():
    pass
```

**`time()`** — Set the gauge to the duration in seconds of the most recent execution. Overwrites each time (unlike Histogram/Summary which accumulate).

```python
@g.time()
def process():
    pass

with g.time() as t:
    pass
print(t.duration)  # observed time in seconds
```

**`set_function(f)`** — Bind a callback. Called on every scrape. All other methods become no-ops after this.

```python
queue = []
g.set_function(lambda: len(queue))
```

### Real-world example

```python
from prometheus_client import Gauge, start_http_server

ACTIVE_CONNECTIONS = Gauge('connections_active', 'Active DB connections', namespace='myapp')
QUEUE_SIZE = Gauge('job_queue_size', 'Jobs waiting in queue', namespace='myapp')

job_queue = []
QUEUE_SIZE.set_function(lambda: len(job_queue))

def acquire():
    ACTIVE_CONNECTIONS.inc()

def release():
    ACTIVE_CONNECTIONS.dec()
```

## Summary

Samples observations and tracks total count and sum. Use when you want averages but do not need per-bucket quantiles. The Python client does not compute quantiles locally — use Histogram for p50/p95/p99.

### Constructor

```python
Summary(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY)
```

Note: `quantile` is reserved and cannot be used as a label name.

### Output

Two time series per metric:
- `<name>_count` — total observations
- `<name>_sum` — sum of observed values

### Methods

**`observe(amount)`** — Record a single observation.

```python
s.observe(0.43)   # 430ms
s.observe(1024)   # bytes
```

**`time()`** — Decorator or context manager that observes duration and accumulates.

```python
@s.time()
def process():
    pass

with s.time() as t:
    pass
print(t.duration)  # observed time in seconds
```

### Real-world example

```python
from prometheus_client import Summary, start_http_server

TASK_DURATION = Summary(
    'task_duration_seconds',
    'Time spent processing background tasks',
    labelnames=['task_type'],
    namespace='myapp',
)

def run_task(task_type, task):
    with TASK_DURATION.labels(task_type=task_type).time():
        pass  # run the task

if __name__ == '__main__':
    start_http_server(8000)
```

Compute average in PromQL:

```
rate(myapp_task_duration_seconds_sum[5m]) / rate(myapp_task_duration_seconds_count[5m])
```

## Histogram

Samples observations and counts them in configurable buckets. Use when you need quantile calculations (p50, p95, p99) in Prometheus queries.

### Constructor

```python
Histogram(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY, buckets=DEFAULT_BUCKETS)
```

Note: `le` is reserved and cannot be used as a label name.

**Default buckets** (intended for web/RPC latency in seconds):

```
.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, +Inf
```

Override with workload-specific buckets:

```python
h = Histogram('request_latency_seconds', 'Latency', buckets=[.1, .5, 1, 2, 5])
```

### Output

Three time series per metric:
- `<name>_bucket{le="<bound>"}` — cumulative count ≤ bound
- `<name>_sum` — sum of all observed values
- `<name>_count` — total observations

### Methods

**`observe(amount, exemplar=None)`** — Record a single observation.

```python
h.observe(0.43)
h.observe(0.43, exemplar={'trace_id': 'abc123'})  # with exemplar
```

**`time()`** — Decorator or context manager that observes duration and accumulates.

```python
@h.time()
def process():
    pass

with h.time() as t:
    pass
print(t.duration)  # observed time in seconds
```

### Real-world example

```python
from prometheus_client import Histogram, start_http_server

REQUEST_LATENCY = Histogram(
    'request_duration_seconds',
    'HTTP request latency',
    labelnames=['method', 'endpoint'],
    namespace='myapp',
    buckets=[.01, .05, .1, .25, .5, 1, 2.5, 5],
)

def handle_request(method, endpoint):
    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        pass  # handle the request

if __name__ == '__main__':
    start_http_server(8000)
```

Produces:

```
myapp_request_duration_seconds_bucket{method="GET",endpoint="/api/users",le="0.1"} 42
myapp_request_duration_seconds_sum{method="GET",endpoint="/api/users"} 3.7
myapp_request_duration_seconds_count{method="GET",endpoint="/api/users"} 50
```

## Info

Tracks static key-value pairs that describe a target — build version, configuration, environment metadata. Once set, outputs a single time series with all key-value pairs as labels and value 1.

**Does not work in multiprocess mode.** Cannot have a unit (raises `ValueError`).

### Constructor

```python
Info(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY)
```

`_info` suffix is appended automatically on exposition.

### Methods

**`info(val)`** — Set key-value pairs. `val` must be `dict[str, str]`. Keys must not overlap with label names. Calling again overwrites.

```python
i.info({'version': '1.4.2', 'revision': 'abc123', 'branch': 'main'})
```

### Real-world example

```python
from prometheus_client import Info, start_http_server

BUILD_INFO = Info('build', 'Application build information', namespace='myapp')

BUILD_INFO.info({
    'version': '1.4.2',
    'revision': 'abc123def456',
    'branch': 'main',
    'build_date': '2024-01-15',
})

if __name__ == '__main__':
    start_http_server(8000)
```

Produces:

```
myapp_build_info{branch="main",build_date="2024-01-15",revision="abc123def456",version="1.4.2"} 1.0
```

## Enum

Tracks which of a fixed set of states something is currently in. Only one state active at a time. Use for task state machines or lifecycle phases.

**Does not work in multiprocess mode.** Cannot have a unit (raises `ValueError`).

### Constructor

```python
Enum(name, documentation, labelnames=(), namespace='', subsystem='', unit='', registry=REGISTRY, states=[])
```

`states` is required and must be non-empty. First entry is the initial state. The metric name itself cannot be used as a label name.

### Methods

**`state(state)`** — Set current state. Must be one of the strings in `states`. Raises `ValueError` if unrecognized.

```python
e.state('running')
e.state('stopped')
```

### Real-world example

```python
from prometheus_client import Enum, start_http_server

WORKER_STATE = Enum(
    'worker_state',
    'Current state of the background worker',
    states=['idle', 'running', 'error'],
    namespace='myapp',
)

def process_job():
    WORKER_STATE.state('running')
    try:
        pass  # do work
    except Exception:
        WORKER_STATE.state('error')
        raise
    finally:
        WORKER_STATE.state('idle')

if __name__ == '__main__':
    start_http_server(8000)
```

Produces:

```
myapp_worker_state{myapp_worker_state="idle"} 0.0
myapp_worker_state{myapp_worker_state="running"} 1.0
myapp_worker_state{myapp_worker_state="error"} 0.0
```
