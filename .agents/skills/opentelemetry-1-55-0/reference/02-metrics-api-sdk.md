# Metrics API & SDK

**Status**: Stable (except where noted)

## Overview

The Metrics API consists of:
- **MeterProvider** — Entry point, provides access to Meters
- **Meter** — Responsible for creating Instruments
- **Instrument** — Responsible for reporting Measurements

```
+-- MeterProvider(default)
    |
    +-- Meter(name='io.opentelemetry.runtime', version='1.0.0')
    |   |
    |   +-- Instrument<Asynchronous Gauge, int>(name='cpython.gc', unit='kB')
    |   +-- instruments...
    |
    +-- Meter(name='bank.payment', version='23.3.5')
        +-- Instrument<Counter, int>(name='client.exception', unit='1')
        +-- Instrument<Histogram, double>(name='client.duration', unit='ms')
```

## MeterProvider

### Get a Meter

```python
meter = meter_provider.get_meter(
    name: str,           # REQUIRED — instrumentation scope name
    version: str = "",   # OPTIONAL
    schema_url: str = "",# OPTIONAL — since 1.4.0
    attributes: dict = {}# OPTIONAL — since 1.13.0
) -> Meter
```

Same parameter semantics as TracerProvider.get_tracer().

## Instrument Types

### Synchronous Instruments

| Instrument | Value Type | Direction | Use Case |
|------------|-----------|-----------|----------|
| `Counter` | int/float | Monotonic increase | Request counts, bytes sent |
| `UpDownCounter` | int/float | Can go up or down | Active connections, queue size |
| `Histogram` | float | Non-negative | Latency distributions, response sizes |

### Asynchronous Instruments (callback-based)

| Instrument | Value Type | Direction | Use Case |
|------------|-----------|-----------|----------|
| `ObservableCounter` | int/float | Monotonic increase | Total bytes read by process |
| `ObservableUpDownCounter` | int/float | Can go up or down | Memory used by object pool |
| `ObservableGauge` | int/float | Arbitrary | CPU usage, temperature sensor |

**Key distinction**: Synchronous instruments record measurements inline with application logic and can be associated with the current Context. Asynchronous instruments register callbacks invoked on-demand during SDK collection; their measurements CANNOT be associated with a Context.

## Instrument Creation

### Counter

```python
counter = meter.create_counter(
    name="http.requests.total",
    unit="1",
    description="Total number of HTTP requests"
)
counter.add(1, {"method": "GET", "status": "200"})
# Or with attributes dict
counter.add(1, {"method": "POST", "status": "201"})
```

### UpDownCounter

```python
active_connections = meter.create_up_down_counter(
    name="http.active.connections",
    unit="1",
    description="Number of active HTTP connections"
)
active_connections.add(1, {"method": "GET"})  # connection established
# ... later ...
active_connections.add(-1, {"method": "GET"})  # connection closed
```

### Histogram

```python
latency = meter.create_histogram(
    name="http.request.duration",
    unit="ms",
    description="HTTP request duration in milliseconds",
    # Advisory: recommended bucket boundaries
    explicit_bucket_boundaries=[0, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
)
latency.record(42.5, {"method": "GET"})
latency.record(128.3, {"method": "POST"})
```

### Asynchronous Instruments

```python
# Observable gauge — callback invoked on collection
def memory_callback(context):
    import psutil
    mem = psutil.virtual_memory()
    yield GaugeMeasurement(mem.used, {"type": "used"})
    yield GaugeMeasurement(mem.available, {"type": "available"})

meter.create_observable_gauge(
    name="system.memory.usage.bytes",
    callbacks=[memory_callback],
    unit="By"
)

# Observable counter — must only increase
def total_bytes_read_callback(context):
    with open("/proc/self/io") as f:
        for line in f:
            if line.startswith("read_bytes:"):
                yield Measurement(int(line.split()[1]))

meter.create_observable_up_down_counter(
    name="process.io.read.bytes",
    callbacks=[total_bytes_read_callback],
    unit="By"
)
```

## Instrument Naming Rules

```
instrument-name = ALPHA 0*254 ("_" / "." / "-" / "/" / ALPHA / DIGIT)
```

- First character: alphabetic (A-Z, a-z)
- Subsequent characters: alphanumeric, `_`, `.`, `-`, `/`
- Maximum length: 255 characters
- Case-insensitive comparison for identity
- Unit: case-sensitive ASCII string, max 63 characters
- Description: BMP Unicode, min support 1023 characters

## Measurements

A `Measurement` consists of:
- Value (number)
- Attributes (key-value pairs)
- Optional context reference (synchronous instruments only)

```python
# Synchronous: measurement tied to current context
counter.add(1, {"status": "200"})

# Asynchronous: callback reports measurements without context
def callback(context):
    yield Measurement(value=42.5, attributes={"region": "us-east-1"})
```

## Metrics Data Model

### Metric Types

| OTLP Type | API Instrument | Aggregation |
|-----------|---------------|-------------|
| Sum | Counter, UpDownCounter | Sum of values |
| Gauge | ObservableGauge | Last value at collection time |
| Histogram | Histogram | Bucket counts + sum/count |
| ExponentialBucketHistogram | Histogram | Exponential bucket histogram |

### Data Point Semantics

1. **Event model** (API): Raw measurements with attributes
2. **In-flight model** (SDK/OTLP): Aggregated data points with start/end timestamps
3. **TimeSeries model** (exporters): How exporters interpret the in-flight model

## Views

Views customize how instrument data is aggregated and exported.

```python
from opentelemetry.sdk.metrics.view import (
    View, InstrumentType, SumAggregation,
    ExplicitBucketHistogramAggregation, DropAggregation
)

provider = MeterProvider(
    views=[
        # Custom histogram buckets for HTTP duration
        View(
            instrument_name="http.request.duration",
            aggregation=ExplicitBucketHistogramAggregation(
                boundaries=[0, 5, 10, 25, 50, 100, 250, 500, 1000, 2500]
            ),
            attribute_keys={"http.method", "http.status_code"}
        ),
        # Rename instrument
        View(
            instrument_name="old.name",
            new_name="new.name"
        ),
        # Drop specific instrument
        View(
            instrument_name="debug.*",
            aggregation=DropAggregation()
        ),
    ]
)
```

### View Configuration

| Parameter | Description |
|-----------|-------------|
| `instrument_name` | Match by name (supports wildcards: `*`, `?`) |
| `instrument_type` | Match by type (Counter, Histogram, etc.) |
| `meter_name` / `meter_version` | Match by meter identity |
| `attribute_keys` | Keep only specified attributes |
| `aggregation` | How to aggregate data (Sum, LastValue, Histogram, etc.) |

## Exemplars

Exemplars link metric data points to specific trace spans for root-cause analysis.

```python
# Configure exemplar filter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(),
    exemplar_filter="trace_based"  # or "always_on", "always_off"
)
provider = MeterProvider(metric_readers=[reader])
```

### Exemplar Filter Types

| Filter | Description | Default Env Var |
|--------|-------------|-----------------|
| `always_on` | All measurements become exemplars | `OTEL_METRICS_EXEMPLAR_FILTER=always_off` |
| `always_off` | No exemplars (default) | — |
| `trace_based` | Only sampled span-linked measurements | `OTEL_METRICS_EXEMPLAR_FILTER=trace_based` |

## Metric Reader Types

### Periodic Exporting MetricReader

```python
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

reader = PeriodicExportingMetricReader(
    exporter,
    export_interval_millis=60000,  # How often to collect+export
    export_timeout_millis=30000   # Max time for each export
)
```

### Push Metrics Exporters

| Env Var | Default | Description |
|---------|---------|-------------|
| `OTEL_METRIC_EXPORT_INTERVAL` | 60000 ms | Time between export attempts |
| `OTEL_METRIC_EXPORT_TIMEOUT` | 30000 ms | Max time for each export |

### In-Memory MetricReader (Testing)

```python
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

reader = InMemoryMetricReader()
provider = MeterProvider(metric_readers=[reader])

# Retrieve collected data
data = reader.get_metrics_data()
for resource_metric in data.resource_metrics:
    for scope_metric in resource_metric.scope_metrics:
        for metric in scope_metric.metrics:
            print(f"{metric.name}: {metric.data.data_points}")
```

### Prometheus Reader

```python
from opentelemetry.exporter.prometheus import PrometheusMetricReader

reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
# Scrape at http://localhost:9464/metrics
```

## Advisory Parameters

Parameters provided by instrument authors to help SDKs produce useful output:

| Parameter | Applies To | Description |
|-----------|-----------|-------------|
| `ExplicitBucketBoundaries` | Histogram | Recommended bucket boundaries for histogram aggregation |
| `Attributes` | All instruments | Recommended attribute keys for resulting metrics (Development) |

SDKs MAY ignore advisory parameters but MUST handle them as documented.

## Attribute Limits

Attribute limits apply to metric data points differently than spans:
- Metric attributes are exempt from general attribute limits at this time
- Instrument-specific limits may be configured per instrument
