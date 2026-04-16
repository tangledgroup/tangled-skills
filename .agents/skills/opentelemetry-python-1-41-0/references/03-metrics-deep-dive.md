# Metrics Deep Dive

## MeterProvider Setup

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
    InMemoryMetricReader,
)

# Single reader with console export
reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# Multiple readers (export to multiple backends simultaneously)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

otlp_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[otlp_reader, console_reader])
```

## Synchronous Instruments

### Counter

Monotonically increasing value. Use for counts that only go up.

```python
meter = metrics.get_meter("my.meter")

# Create once at module level
request_counter = meter.create_counter(
    name="http.server.requests",
    unit="1",
    description="Number of HTTP requests received"
)

# Record measurements inline with business logic
def handle_request(request):
    request_counter.add(1, {
        "method": request.method,
        "path": request.path,
        "status": str(request.status_code),
    })
```

### UpDownCounter

Can increase or decrease. Use for quantities that fluctuate.

```python
active_users = meter.create_up_down_counter(
    name="app.active_users",
    unit="1",
    description="Number of currently active users"
)

def user_login(user_id):
    active_users.add(1, {"user.id": user_id})

def user_logout(user_id):
    active_users.add(-1, {"user.id": user_id})
```

### Histogram

Distribution of values with configurable bucket boundaries.

```python
duration_histogram = meter.create_histogram(
    name="http.server.duration",
    unit="ms",
    description="HTTP server request duration",
    explicit_bucket_boundaries_advisory=[0, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
)

def handle_request(request):
    with tracer.start_as_current_span("request") as span:
        start = time.time()
        response = process(request)
        duration_ms = (time.time() - start) * 1000
        duration_histogram.record(duration_ms, {
            "method": request.method,
            "path": request.path,
        })
        return response
```

The `explicit_bucket_boundaries_advisory` parameter suggests bucket boundaries for histograms. The SDK uses these to create the actual histogram buckets. Choose boundaries appropriate for your data distribution.

### Gauge (Synchronous, Point-in-Time)

Represents a single current value. Note: this is a synchronous gauge that records values at measurement time.

```python
memory_gauge = meter.create_gauge(
    name="app.memory.usage",
    unit="bytes",
    description="Current memory usage"
)

# Record the current value (not cumulative)
def check_memory():
    import psutil
    mem = psutil.virtual_memory().used
    memory_gauge.set(mem)  # Synchronous gauge uses .set() not .add()
```

## Asynchronous Instruments

Asynchronous instruments use callback functions that are invoked during metric collection. They're ideal for values that can't be measured inline with application logic.

### ObservableCounter

```python
def disk_usage_callback(options: CallbackOptions):
    import psutil
    usage = psutil.disk_usage("/")
    yield Observation(usage.used, {"mountpoint": "/"})
    yield Observation(usage.free, {"mountpoint": "/"})

meter.create_observable_counter(
    name="disk.usage",
    callbacks=[disk_usage_callback],
    unit="bytes",
    description="Disk usage breakdown"
)
```

### ObservableGauge

```python
def cpu_callback(options: CallbackOptions):
    import psutil
    percpu = psutil.cpu_percent(interval=None, percpu=True)
    for i, pct in enumerate(percpcu):
        yield Observation(pct, {"core": str(i)})

meter.create_observable_gauge(
    name="system.cpu.utilization",
    callbacks=[cpu_callback],
    unit="%",
    description="CPU utilization per core"
)
```

### ObservableUpDownCounter

```python
def queue_size_callback(options: CallbackOptions):
    size = my_queue.qsize()  # Can go up or down
    yield Observation(size, {"queue": "default"})

meter.create_observable_up_down_counter(
    name="app.queue.size",
    callbacks=[queue_size_callback],
    unit="1",
    description="Current queue depth"
)
```

### Callback Signature

Callbacks must:
1. Accept a `CallbackOptions` parameter with `timeout_millis` attribute
2. Return an iterable of `Observation` objects
3. Each `Observation` contains a numeric value and optional attributes

```python
from opentelemetry.metrics import CallbackOptions, Observation

def my_callback(options: CallbackOptions) -> Iterable[Observation]:
    # Respect the timeout to avoid blocking indefinitely
    result = fetch_value(timeout=options.timeout_millis / 1000)
    yield Observation(result, {"label": "value"})
```

## Metric Readers and Exporters

### PeriodicExportingMetricReader

Push-based: exports metrics at fixed intervals.

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(),
    export_interval_millis=30000,  # Every 30 seconds
    export_timeout_millis=10000,   # Timeout per export
)
```

### InMemoryMetricReader

Pull-based: stores metrics in memory for testing.

```python
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

reader = InMemoryMetricReader()
provider = MeterProvider(metric_readers=[reader])

# Later, in tests:
metrics_data = reader.get_metrics_data()
# Assert on collected metrics
```

### ConsoleMetricExporter

Debugging only — prints metrics as JSON to stdout.

```python
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[reader])
```

### PrometheusMetricReader

Pull-based: exposes a `/metrics` endpoint for Prometheus scraping.

```python
from opentelemetry.sdk.metrics.export import PrometheusMetricReader

# Requires prometheus_client package
provider = MeterProvider(metric_readers=[PrometheusMetricReader()])
```

## Views

Views modify how instruments are aggregated and exported.

```python
from opentelemetry.sdk.metrics.view import (
    View,
    InstrumentType,
    SumAggregation,
    LastValueAggregation,
    HistogramAggregation,
    DropAggregation,
)

# Rename an instrument
View(
    instrument_name="old.name",
    instrument_type=InstrumentType.COUNTER,
    name="new.name",
    description="Updated description",
)

# Change aggregation for all histograms
View(
    instrument_type=InstrumentType.HISTOGRAM,
    aggregation=HistogramAggregation(
        explicit_bucket_boundaries=[0, 5, 10, 25, 50, 100]
    ),
)

# Drop a specific instrument entirely
View(
    instrument_name="internal.debug.metric",
    aggregation=DropAggregation(),
)

# Apply to all instruments matching a pattern
View(
    instrument_name="http.*",  # Wildcard matching
    aggregation=SumAggregation(),
)
```

## Exemplars

Exemplars link metric data points to specific trace spans, providing context for outlier values.

```python
from opentelemetry.sdk.metrics.exemplar import (
    AlwaysOnExemplarFilter,
    AlwaysOffExemplarFilter,
    TraceBasedExemplarFilter,
)

# Only record exemplars for sampled spans (recommended default)
reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(),
    exemplar_filter=TraceBasedExemplarFilter(),
)

# Never record exemplars
reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(),
    exemplar_filter=AlwaysOffExemplarFilter(),
)

# Always record exemplars (may impact performance)
reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(),
    exemplar_filter=AlwaysOnExemplarFilter(),
)
```

Configure via environment:
```bash
export OTEL_METRICS_EXEMPLAR_FILTER=trace_based  # or always_on, always_off
```

## Instrument Registration Conflicts

Creating two instruments with the same name but different types/unit/description raises a conflict warning. Always create instruments once at module level and reuse them.

```python
# BAD: Creating inside a function (may be called multiple times)
def handle_request():
    counter = meter.create_counter("http.requests")  # Conflict on subsequent calls!
    counter.add(1)

# GOOD: Create once at module level
_request_counter = None

def get_counter():
    global _request_counter
    if _request_counter is None:
        _request_counter = meter.create_counter("http.requests")
    return _request_counter
```
