# Metrics

## MeterProvider

The entry point of the Metrics API. Provides access to Meters.

- MUST provide a way to specify a Resource, associated with all metrics from any Meter
- SHOULD allow creation of multiple independent MeterProviders
- Configuration (MetricExporters, MetricReaders, Views) is owned by the MeterProvider
- If configuration is updated, it MUST apply to all already returned Meters

### Get a Meter

```
meter = meter_provider.get_meter(name, version, schema_url, attributes)
```

- `name` (required): Uniquely identifies the instrumentation scope
- `version` (optional): Library version string
- `schema_url` (optional): Schema URL for emitted telemetry
- `attributes` (optional): Instrumentation scope attributes

If an invalid name is specified, a working Meter MUST be returned as fallback.

## Instruments

Instruments report Measurements and are identified by name, kind, description, and unit.

### Synchronous Instruments

Invoked inline by application logic.

#### Counter

Monotonically increasing value. Supports `add(value, attributes)`.

```python
counter = meter.create_counter("http.requests", unit="1", description="HTTP request count")
counter.add(1, {"http.method": "GET", "http.status_code": 200})
```

#### UpDownCounter

Value that can go up and down. Supports `add(value, attributes)` where value can be negative.

```python
gauge = meter.create_up_down_counter("active.connections", unit="1")
gauge.add(-1, {"direction": "outbound"})  # connection closed
```

#### Histogram

Captures distribution of measurements. Supports `record(value, attributes)`.

```python
histogram = meter.create_histogram("http.duration", unit="ms", description="HTTP request duration")
histogram.record(42.5, {"http.method": "GET"})
```

### Asynchronous Instruments

User registers a callback function invoked on demand by the SDK.

#### Asynchronous Gauge

Reports current value(s). Callback receives an observer:

```python
def callback(observer):
    observer.observe(get_memory_usage(), {"state": "heap_used"})

async_gauge = meter.create_observable_gauge("process.memory", callbacks=[callback])
```

#### Asynchronous Counter

Monotonically increasing. Same callback pattern as async gauge.

#### Asynchronous UpDownCounter

Value that can go up and down. Same callback pattern.

### Multiple-Instrument Callbacks

A single callback can observe multiple instruments:

```python
def callback(observable):
    observable.observe(counter1, value1)
    observable.observe(gauge1, value2)
```

## Instrument Naming

- Name syntax follows language-specific conventions
- Instruments with conflicting names (same name, unit, description) are handled by the SDK — typically the first registration wins
- Advisory parameters (ExplicitBucketBoundaries, Attributes) can be provided during creation

## Views

Views configure how data from an Instrument is processed, aggregated, and exported. Configured through MeterProvider.

### Stream Configuration

A View maps instruments to streams with specific aggregation, attribute filtering, and name transformation.

### Aggregation Types

- **Drop**: Discards all measurements
- **Default**: Uses the instrument's default aggregation
- **Sum**: Accumulates values (supports Cumulative and Delta temporality)
- **LastValue** (Gauge): Reports the last recorded value
- **ExplicitBucketHistogram**: Fixed bucket boundaries
- **Base2ExponentialBucketHistogram**: Dynamic exponential buckets

### View Examples

```yaml
# Drop specific instrument
- name: drop_debug_metrics
  selector:
    instrument_name: debug.*
  aggregation: drop

# Custom histogram with explicit buckets
- name: http_duration_histogram
  selector:
    instrument_name: http.duration
  aggregation:
    histogram:
      explicit_bounds: [0, 5, 10, 25, 50, 100, 250, 500, 1000]
```

## MetricReader

Collects metrics from the SDK pipeline.

### Operations

- **Collect**: Returns current metric data
- **Shutdown**: Cleanup
- **ForceFlush**: Flush pending exports

### Periodic Exporting

MetricReaders can export on a configurable interval (push model).

### maxExportBatchSize (Development, 1.56.0)

The Periodic exporting MetricReader accepts an in-development `maxExportBatchSize` parameter that controls the maximum number of data points sent per export call. This allows better control over export payload sizes and network efficiency.

## MetricExporter

Pushes metrics to a backend.

### Interface

- **Export(batch)**: Exports a batch of metric data points
- **ForceFlush()**: Flush pending exports
- **Shutdown()**: Cleanup

### Pull Model

Some backends pull metrics. The SDK supports Pull Metric Exporters that respond to collection requests rather than pushing.

## Temporality

- **Cumulative**: Data from start time to current time. Stateful — requires tracking state on the client.
- **Delta**: Data since last export. Stateless — no client-side state needed.

Sums support both. Histograms can be either. Gauges are point-in-time (no temporality).

## Resets and Gaps

- Cumulative streams may have unknown start times
- True reset points can be inserted for cumulative sums
- Overlap between data points is resolved by the consumer
- Missing timestamps are handled per the data model

## Exemplars

Exemplars are sample data points that provide additional context for metrics.

### ExemplarFilter

- **AlwaysOn**: Collect exemplars for all measurements
- **AlwaysOff**: Never collect exemplars
- **TraceBased**: Collect exemplars only when a span is active (links metrics to traces)

### ExemplarReservoir

- **SimpleFixedSizeExemplarReservoir**: Fixed-size reservoir with random sampling
- **AlignedHistogramBucketExemplarReservoir**: One exemplar per histogram bucket

## Cardinality Limits

Configurable limits on the number of unique attribute combinations:

- Synchronous instrument cardinality limits
- Asynchronous instrument cardinality limits
- Overflow attributes are tracked when limits are exceeded

## Metrics Data Model

The data model defines three semantics:

1. **Event Model**: Used by the API — discrete measurements
2. **In-flight Data Model**: Used by SDK and OTLP — aggregated data points
3. **TimeSeries Model**: How exporters interpret the in-flight model

Transformations supported on the collection path:

- **Temporal reaggregation**: High-frequency data re-aggregated into longer intervals
- **Spatial reaggregation**: Attributes dropped to reduce cardinality
- **Delta-to-Cumulative**: Delta temporality converted to cumulative

## Prometheus Metrics Exporter Compatibility (Stabilized in 1.56.0)

Multiple transformations between Prometheus and OpenTelemetry metrics were stabilized in 1.56.0:

### Stabilized Transformations

- **Host configuration** for the Prometheus exporter
- **Temporality** settings
- **Port configuration**
- **Prometheus Classic Histogram to OTLP Explicit Histogram**: Conversion rules for translating Prometheus classic histogram buckets to OTLP explicit bucket histograms
- **Prometheus Timestamp and Start Timestamp**: Transformation of Prometheus timestamp fields to OTLP data point timestamps
- **Prometheus Native Histogram to OTLP Exponential Histogram**: Including conversion rules for Native Histograms with Custom Buckets (NHCB) to OTLP Histogram
- **Prometheus Dropped Types**: Handling of dropped metric types in transformation
- **OpenTelemetry Attributes to Prometheus Labels**: Mapping OTel attributes to Prometheus label format
- **Prometheus Exemplar to OpenTelemetry Exemplar**: Bidirectional exemplar conversion
- **Prometheus Metadata**: Transformation of Prometheus metric metadata (help text, type)
- **OpenTelemetry Metric Metadata to Prometheus**: Converting OTel instrument descriptions and units to Prometheus metadata
- **OpenTelemetry Exemplar to Prometheus Exemplar**: Exporting OTel exemplars in Prometheus format

### Also Stabilized

- **Prometheus Summary to OTLP Summary** (stabilized in 1.55.0)
- **`otel_scope_` label prefix translation** to OTLP Instrumentation Scope
- **OpenTelemetry Gauge and Sum to Prometheus transformations**
- **OpenTelemetry Instrumentation Scope to Prometheus labels transformation**
