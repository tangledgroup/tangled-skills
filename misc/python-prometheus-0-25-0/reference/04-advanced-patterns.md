# Advanced Patterns

## Contents
- Registry
- Restricted Registry
- Custom Collectors
- Multiprocess Mode
- Parser

## Registry

`CollectorRegistry` holds all collectors whose metrics are exposed when scraped. `REGISTRY` is the global default instance, created with `auto_describe=True`.

### Constructor

```python
CollectorRegistry(auto_describe=False, target_info=None, support_collectors_without_names=False)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `auto_describe` | `bool` | `False` | Calls `collect()` at registration time if collector lacks `describe()`, to detect name collisions. Default `REGISTRY` uses `True`. |
| `target_info` | `Dict[str, str]` | `None` | Key-value labels exposed as `target_info` metric. |
| `support_collectors_without_names` | `bool` | `False` | Allows registering collectors producing no named metrics. Required by `MultiProcessCollector`. |

### Methods

**`register(collector)`** — Register a collector. Raises `ValueError` on name collision.

```python
from prometheus_client.registry import Collector

class MyCollector(Collector):
    def collect(self):
        ...

REGISTRY.register(MyCollector())
```

**`unregister(collector)`** — Remove a previously registered collector.

```python
from prometheus_client import GC_COLLECTOR
REGISTRY.unregister(GC_COLLECTOR)
```

**`collect()`** — Yield all metrics from every registered collector.

```python
for metric in REGISTRY.collect():
    print(metric.name, metric.type)
```

**`get_sample_value(name, labels=None)`** — Return current value of a single sample, or `None`. Intended for unit tests.

```python
from prometheus_client import Counter, CollectorRegistry

r = CollectorRegistry()
c = Counter('requests_total', 'Total requests', registry=r)
c.inc(3)

assert r.get_sample_value('requests_total') == 3.0
```

**`set_target_info(labels)`** / **`get_target_info()`** — Set or retrieve target metadata labels.

```python
REGISTRY.set_target_info({'env': 'production', 'region': 'us-east-1'})
info = REGISTRY.get_target_info()
```

### Skipping registration

Pass `registry=None` to skip global registration (useful in tests):

```python
c = Counter('my_counter', 'A counter', registry=None)
```

Register with a custom registry:

```python
r = CollectorRegistry()
c2 = Counter('my_counter', 'A counter', registry=r)
```

## Restricted Registry

Expose only specific metrics from a registry. Useful for partial scrapes or reducing output size.

**Via HTTP query parameter** (built-in server):

```bash
curl --get --data-urlencode "name[]=python_gc_objects_collected_total" \
     --data-urlencode "name[]=python_info" \
     http://127.0.0.1:9200/metrics
```

**Via `generate_latest`**:

```python
from prometheus_client import generate_latest, REGISTRY

subset = REGISTRY.restricted_registry(['python_gc_objects_collected_total', 'python_info'])
output = generate_latest(subset)
```

## Custom Collectors

For proxying metrics from external systems not directly instrumentable. Create a class implementing the Collector protocol and register it.

### Collector Protocol

**`collect()`** — Returns iterable of metric family objects. Called on every scrape. Use `yield` (generator) for lazy iteration.

**`describe()`** — Optional. Returns metric families used only to determine metric names for collision detection. If not implemented and `auto_describe=True`, `collect()` is called at registration time instead.

### Basic example

```python
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from prometheus_client.registry import Collector

class CustomCollector(Collector):
    def collect(self):
        yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        c = CounterMetricFamily('my_counter_total', 'Help text', labels=['foo'])
        c.add_metric(['bar'], 1.7)
        c.add_metric(['baz'], 3.8)
        yield c

REGISTRY.register(CustomCollector())
```

### value vs labels pattern

Every MetricFamily constructor accepts either inline data or `labels`, but not both:

- **Inline**: pass the data parameter (`value`, `count_value`/`sum_value`, `buckets`) directly
- **Labelled**: pass `labels` (sequence of label names) and call `add_metric()` for each time series

```python
# single unlabelled value
GaugeMetricFamily('my_gauge', 'Help text', value=7)

# labelled metrics
g = GaugeMetricFamily('my_gauge', 'Help text', labels=['region'])
g.add_metric(['us-east-1'], 3)
g.add_metric(['eu-west-1'], 5)
```

### GaugeMetricFamily

```python
GaugeMetricFamily(name, documentation, value=None, labels=None, unit='')
```

**`add_metric(labels, value, timestamp=None)`** — Add a labelled sample.

```python
g = GaugeMetricFamily('temperature_celsius', 'Temperature by location', labels=['location'])
g.add_metric(['living_room'], 21.5)
g.add_metric(['basement'], 18.0)
yield g
```

### CounterMetricFamily

```python
CounterMetricFamily(name, documentation, value=None, labels=None, created=None, unit='', exemplar=None)
```

Trailing `_total` is stripped and re-added on exposition.

**`add_metric(labels, value, created=None, timestamp=None, exemplar=None)`**

```python
c = CounterMetricFamily('http_requests_total', 'HTTP requests by status', labels=['status'])
c.add_metric(['200'], 1200)
c.add_metric(['404'], 43)
c.add_metric(['500'], 7)
yield c
```

### SummaryMetricFamily

```python
SummaryMetricFamily(name, documentation, count_value=None, sum_value=None, labels=None, unit='')
```

`count_value` and `sum_value` must be provided together or not at all.

**`add_metric(labels, count_value, sum_value, timestamp=None)`**

```python
s = SummaryMetricFamily('rpc_duration_seconds', 'RPC duration', labels=['method'])
s.add_metric(['get'], count_value=1000, sum_value=53.2)
s.add_metric(['put'], count_value=400, sum_value=28.7)
yield s
```

### HistogramMetricFamily

```python
HistogramMetricFamily(name, documentation, buckets=None, sum_value=None, labels=None, unit='')
```

Each bucket entry is `(le, value)` or `(le, value, exemplar)`. Must include `+Inf` bucket and be sorted.

**`add_metric(labels, buckets, sum_value, timestamp=None)`** — Pass `sum_value=None` for histograms with negative buckets.

```python
h = HistogramMetricFamily('request_size_bytes', 'Request sizes', labels=['handler'])
h.add_metric(
    ['api'],
    buckets=[('100', 5), ('1000', 42), ('+Inf', 50)],
    sum_value=18350.0,
)
yield h
```

### InfoMetricFamily

```python
InfoMetricFamily(name, documentation, value=None, labels=None)
```

`_info` suffix added automatically on exposition.

**`add_metric(labels, value, timestamp=None)`** — `value` is `Dict[str, str]`.

```python
# single unlabelled info metric
yield InfoMetricFamily('build', 'Build metadata', value={'version': '1.2.3', 'commit': 'abc123'})

# labelled — one info per service
i = InfoMetricFamily('service_build', 'Per-service build info', labels=['service'])
i.add_metric(['auth'], {'version': '2.0.1', 'commit': 'def456'})
i.add_metric(['api'], {'version': '1.9.0', 'commit': 'ghi789'})
yield i
```

### Real-world example

Proxying metrics from an external data source:

```python
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, REGISTRY
from prometheus_client.registry import Collector
from prometheus_client import start_http_server

_QUEUE_STATS = {
    'orders': {'depth': 14, 'processed': 9821},
    'notifications': {'depth': 3, 'processed': 45210},
}

class QueueCollector(Collector):
    def collect(self):
        depth = GaugeMetricFamily('queue_depth', 'Messages waiting in queue', labels=['queue'])
        processed = CounterMetricFamily('queue_messages_processed_total', 'Total messages processed', labels=['queue'])
        for name, stats in _QUEUE_STATS.items():
            depth.add_metric([name], stats['depth'])
            processed.add_metric([name], stats['processed'])
        yield depth
        yield processed

REGISTRY.register(QueueCollector())
```

## Multiprocess Mode

Python's multiprocessing model (e.g. Gunicorn workers) breaks the shared-memory assumption of Prometheus clients. Multiprocess mode stores per-process metrics in files and aggregates them on scrape.

### Limitations

- Custom collectors do not work (including process CPU/memory metrics)
- Gauges cannot use `set_function`
- Info and Enum metrics do not work
- Pushgateway cannot be used
- Exemplars are not supported
- Remove and clear of labels not supported
- Gauges cannot use the `pid` label

### Setup steps

**1. Set environment variable** (from shell script, not Python):

```bash
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
rm -rf "$PROMETHEUS_MULTIPROC_DIR"/*  # wipe before each run
```

**2. Create registry with MultiProcessCollector inside request context**:

```python
from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

def app(environ, start_response):
    registry = CollectorRegistry(support_collectors_without_names=True)
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    status = '200 OK'
    response_headers = [
        ('Content-type', CONTENT_TYPE_LATEST),
        ('Content-Length', str(len(data))),
    ]
    start_response(status, response_headers)
    return iter([data])
```

**3. Gunicorn config** — mark dead workers:

```python
from prometheus_client import multiprocess

def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
```

**4. Gauge tuning** — select aggregation mode per gauge:

```python
from prometheus_client import Gauge

# Default: one time series per process, labelled by pid
IN_PROGRESS = Gauge("inprogress_requests", "help")

# Sum across living processes only
IN_PROGRESS = Gauge("inprogress_requests", "help", multiprocess_mode='livesum')
```

Available modes: `all`, `min`, `max`, `sum`, `mostrecent`. Prepend `live` (e.g. `livesum`) to only consider living processes.

### API Reference

**`MultiProcessCollector(registry, path=None)`** — Aggregates metrics from all processes in the multiprocess directory.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `registry` | `CollectorRegistry` | required | Registry created inside request context. Must have `support_collectors_without_names=True`. |
| `path` | `Optional[str]` | `None` | Directory path. Defaults to `PROMETHEUS_MULTIPROC_DIR`. |

**`mark_process_dead(pid, path=None)`** — Removes per-process files for a dead worker. Call from process manager on worker exit. Only removes files for `live*` gauge modes.

## Parser

Parse Prometheus text format into metric families. For advanced use cases where you need to read metrics from external sources.

```python
from prometheus_client.parser import text_string_to_metric_families

for family in text_string_to_metric_families(u"my_gauge 1.0\n"):
    for sample in family.samples:
        print(f"Name: {sample[0]} Labels: {sample[1]} Value: {sample[2]}")
```
