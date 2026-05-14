# Metrics

## MeterProvider and Meter

The `MeterProvider` is the entry point for the metrics API. It provides access to `Meter` instances which create instruments.

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)

provider = MeterProvider(
    metric_readers=[
        PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=5000,
            export_timeout_millis=30000,
        )
    ]
)
metrics.set_meter_provider(provider)

# Get a meter by instrumentation scope name
meter = metrics.get_meter("my-app", "1.0.0")
```

## Synchronous Instruments

Synchronous instruments record measurements at the time the measured occurrence happens.

### Counter

Monotonically increasing cumulative value:

```python
counter = meter.create_counter(
    "http.requests.total",
    unit="req",
    description="Total HTTP requests"
)
counter.add(1, attributes={"method": "GET", "status": "200"})
```

### UpDownCounter

Value that can go up and down:

```python
updown = meter.create_up_down_counter(
    "active.connections",
    unit="conn",
    description="Active connections"
)
updown.add(1, attributes={"endpoint": "/api"})   # connection opened
updown.add(-1, attributes={"endpoint": "/api"})  # connection closed
```

### Histogram

Distribution of values (e.g., request durations):

```python
histogram = meter.create_histogram(
    "http.request.duration",
    unit="ms",
    description="HTTP request duration"
)
histogram.record(42.5, attributes={"method": "GET", "path": "/api"})
```

### Gauge

Point-in-time value measurement:

```python
gauge = meter.create_observable_gauge(
    "cpu.utilization",
    callbacks=[lambda obs: obs.observations(get_cpu_usage())],
)
```

Note: The synchronous `Gauge` instrument is available as `_Gauge` (underscore prefix indicates it may be renamed).

## Asynchronous (Observable) Instruments

Asynchronous instruments report values through callbacks, evaluated at collection time.

```python
def cpu_callback(options):
    yield metrics.Observation(get_cpu_percent(), {"cpu": "0"})
    yield metrics.Observation(get_cpu_percent(), {"cpu": "1"})

observable_counter = meter.create_observable_counter(
    "tasks.completed",
    callbacks=[lambda options: metrics.Observation(task_count())],
    unit="tasks",
    description="Total completed tasks"
)

observable_gauge = meter.create_observable_gauge(
    "cpu.percent",
    callbacks=[cpu_callback],
    unit="%",
    description="CPU utilization per core"
)

observable_updown = meter.create_observable_up_down_counter(
    "network.bytes.delta",
    callbacks=[lambda options: metrics.Observation(net_delta())],
    unit="By",
    description="Network bytes delta"
)
```

## MetricReader Architecture

The metrics SDK uses a pull-based architecture via `MetricReader`:

```python
from opentelemetry.sdk.metrics.export import (
    MetricReader,
    PeriodicExportingMetricReader,
    InMemoryMetricReader,
)

# PeriodicExportingMetricReader — pushes to an exporter on a timer
reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=60000,  # OTEL_METRIC_EXPORT_INTERVAL
    export_timeout_millis=30000,   # OTEL_METRIC_EXPORT_TIMEOUT
)

# InMemoryMetricReader — pull metrics into memory (useful for testing)
mem_reader = InMemoryMetricReader()
metrics_data = mem_reader.get_metrics_data()

# Custom MetricReader
class CustomReader(MetricReader):
    def _receive_metrics(self, metrics_data, timeout_millis=None):
        # Process collected metrics
        pass

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=None):
        pass
```

## MetricExporter

The `MetricExporter` interface defines how metrics are exported:

```python
from opentelemetry.sdk.metrics.export import MetricExporter, MetricExportResult

class CustomExporter(MetricExporter):
    def export(self, metrics, timeout_millis=None):
        # Export metrics data
        return MetricExportResult.SUCCESS

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=None):
        pass

    @property
    def preferred_temporality(self):
        # Return temporality preference per instrument kind
        from opentelemetry.sdk.metrics import AggregationTemporality
        return {
            Counter: AggregationTemporality.CUMULATIVE,
            UpDownCounter: AggregationTemporality.CUMULATIVE,
            Histogram: AggregationTemporality.CUMULATIVE,
        }

    @property
    def preferred_aggregation(self):
        # Return aggregation preference per instrument class
        return {}
```

## Views

Views transform instrument data before export, allowing different aggregations for the same instrument:

```python
from opentelemetry.sdk.metrics.view import (
    View,
    ExplicitBucketHistogramAggregation,
    DefaultAggregation,
    DropAggregation,
)

# Create a view that changes histogram buckets for a specific instrument
view = View(
    instrument_name="http.request.duration",
    attribute_keys={"method", "status"},  # Keep only these attributes
    aggregation=ExplicitBucketHistogramAggregation(
        boundaries=[0, 5, 10, 25, 50, 100, 250, 500, 1000]
    ),
)

provider = MeterProvider(
    metric_readers=[reader],
    views=[view],
)
```

Common aggregations:

- `DefaultAggregation` — SDK default per instrument kind
- `ExplicitBucketHistogramAggregation` — Custom bucket boundaries
- `DropAggregation` — Drop the instrument entirely
- `LastValueAggregation` — Keep only the last recorded value
- `SumAggregation` — Sum of all recorded values

## Exemplars

Exemplars are sampled data points that provide examples of measurements contributing to histogram buckets:

```python
from opentelemetry.sdk.metrics import (
    AlwaysOnExemplarFilter,
    AlwaysOffExemplarFilter,
    TraceBasedExemplarFilter,
    SimpleFixedSizeExemplarReservoir,
    AlignedHistogramBucketExemplarReservoir,
)

# Filter controls which measurements become exemplars
view = View(
    instrument_name="http.request.duration",
    aggregation=ExplicitBucketHistogramAggregation(
        boundaries=[0, 5, 10, 25, 50, 100],
        record_min_max=True,
    ),
    exemplar_filter=TraceBasedExemplarFilter(),  # Only from sampled spans
)
```

Exemplar filters:

- `AlwaysOnExemplarFilter` — All measurements can become exemplars
- `AlwaysOffExemplarFilter` — No exemplars collected
- `TraceBasedExemplarFilter` — Only measurements from sampled spans

Environment variable `OTEL_METRICS_EXEMPLAR_FILTER` controls the default filter.

## Aggregation Temporality

Controls whether metrics report cumulative or delta values:

```python
from opentelemetry.sdk.metrics import AggregationTemporality

# CUMULATIVE — since instrument creation (default for most backends)
# DELTA — since last collection
temporality = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
    Histogram: AggregationTemporality.DELTA,
}
```

Set via `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`:

- `CUMULATIVE` — All instruments use cumulative
- `DELTA` — Counter, AsyncCounter, Histogram use delta; UpDownCounter uses cumulative
- `LOWMEMORY` — Counter, Histogram use delta; UpDownCounter, AsyncCounter, AsyncUpDownCounter use cumulative

## Data Model

The metrics data model hierarchy:

```
MetricsData
└── ResourceMetrics
    ├── resource          # Resource producing the metrics
    ├── schema_url
    └── scope_metrics     # List[ScopeMetrics]
        ├── scope         # InstrumentationScope
        ├── schema_url
        └── metrics       # List[Metric]
            ├── name
            ├── description
            ├── unit
            └── data      # Sum, Gauge, Histogram, ExponentialHistogram
                └── data_points  # List[NumberDataPoint / HistogramDataPoint]
                    ├── attributes
                    ├── start_time_unix_nano
                    ├── time_unix_nano
                    └── value / bucket_counts
```

## Environment Variables

- `OTEL_METRIC_EXPORT_INTERVAL` — Time between export attempts (ms)
- `OTEL_METRIC_EXPORT_TIMEOUT` — Maximum time for each export (ms)
- `OTEL_METRICS_EXEMPLAR_FILTER` — Exemplar filter selection
- `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` — Cumulative/Delta/LowMemory
- `OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION` — Default histogram aggregation
