# Data Model and Metric Types

## Contents
- Time Series
- Metric Names and Labels
- Samples
- Notation
- Metric Types (Counter, Gauge, Histogram, Summary)
- Native Histograms vs Classic Histograms

## Time Series

Prometheus stores all data as time series: streams of timestamped values belonging to the same metric and the same set of labeled dimensions. Besides stored time series, Prometheus generates temporary derived time series as query results.

## Metric Names and Labels

Every time series is uniquely identified by its metric name and optional key-value pairs called labels.

### Metric Names

- SHOULD match `[a-zA-Z_:][a-zA-Z0-9_:]*` for best compatibility
- MAY use any UTF-8 characters (v3.0+, requires quoting in PromQL if outside recommended set)
- Colons (`:`) are reserved for user-defined recording rules — exporters and direct instrumentation should not use them
- SHOULD specify the general feature measured (e.g., `http_requests_total`)

### Metric Labels

Labels capture different dimensions of the same metric name (the "dimensional data model"). The query language allows filtering and aggregation based on these dimensions.

- Label names SHOULD match `[a-zA-Z_][a-zA-Z0-9_]*`
- Names beginning with `__` are reserved for internal Prometheus use
- Label values may contain any UTF-8 characters
- Empty label values are equivalent to missing labels
- Changing any label value creates a new time series

## Samples

Each sample consists of:
- A float64 value or native histogram
- A millisecond-precision timestamp

## Notation

Time series are identified using this notation:

```
<metric_name>{<label_name>="<label_value>", ...}
```

Examples:
```
http_requests_total{method="POST", handler="/api/messages"}
up{job="prometheus", instance="localhost:9090"}
```

UTF-8 names outside the recommended character set must be quoted:
```
{"metric-name-with-dashes", label="value"}
```

Internally, metric names are represented as a special label `__name__`:
```
{__name__="http_requests_total", method="POST"}
```

## Metric Types

Prometheus instrumentation libraries provide four core metric types. The server flattens Counter, Gauge, and Summary into untyped float time series. Only Histograms (native) are stored as composite samples.

### Counter

A cumulative metric representing a single monotonically increasing value that can only increase or reset to zero on restart.

**Use for**: Request counts, tasks completed, error counts, bytes transferred.

**Do not use for**: Values that can decrease (use Gauge instead).

```
http_requests_total{method="GET"}  15234
http_requests_total{method="POST"}  3891
```

Counters conventionally end with `_total`. When using `rate()` or `increase()`, counter resets are automatically handled.

### Gauge

A single numerical value that can arbitrarily go up and down.

**Use for**: Current memory usage, temperature, concurrent requests, queue size, uptime.

```
node_memory_MemAvailable_bytes{instance="server1:9100"}  4294967296
go_goroutines{instance="prometheus:9090"}                 42
```

### Histogram

Records observations (request durations, response sizes) by counting them in configurable buckets. Also provides a sum of all observed values.

**Classic Histogram**: Exposed as multiple time series:
- `<basename>_bucket{le="<upper_bound>"}` — cumulative counters per bucket
- `<basename>_sum` — total sum of observed values
- `<basename>_count` — total count of observations (equals `le="+Inf"`)

```
http_request_duration_seconds_bucket{le="0.1"}    2455
http_request_duration_seconds_bucket{le="0.5"}    3344
http_request_duration_seconds_bucket{le="1.0"}    4089
http_request_duration_seconds_bucket{le="+Inf"}   4321
http_request_duration_seconds_sum                  1756.4
http_request_duration_seconds_count                4321
```

Calculate quantiles with `histogram_quantile()`:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Native Histograms**: The modern alternative. Exposed as composite samples with dynamic buckets. More efficient, higher resolution, no explicit bucket configuration needed, always aggregatable regardless of resolution changes. Enabled via `scrape_native_histograms` config option (stable since v3.9).

**NHCB (Native Histograms with Custom Buckets)**: Converts classic histograms to a special native form during ingestion. Use `convert_classic_histograms_to_nhcb` global config option. Retains the original bucket layout but gains efficiency and atomic network transfer benefits.

### Summary

Similar to histogram but calculates configurable quantiles over a sliding time window on the client side.

Exposed as:
- `<basename>{quantile="<φ>"}` — streaming φ-quantiles (0 ≤ φ ≤ 1)
- `<basename>_sum` — total sum
- `<basename>_count` — total count

```
http_request_duration_seconds{quantile="0.5"}  0.3
http_request_duration_seconds{quantile="0.9"}  0.8
http_request_duration_seconds{quantile="0.99"} 1.2
http_request_duration_seconds_sum              1756.4
http_request_duration_seconds_count            4321
```

**Key difference from histograms**: Summaries calculate quantiles on the client side and cannot be aggregated across instances. Histograms are aggregatable server-side. Prefer histograms for most use cases.

## Native Histogram Details

Native histograms are stable since v3.9. Use `scrape_native_histograms: true` in global config to enable ingestion.

**Advantages over classic histograms**:
- Dynamic bucket boundaries — no pre-configuration needed
- Much more efficient storage (composite samples vs many time series)
- Always aggregatable even with different resolutions
- Atomic network transfer (single sample vs multiple independent series)

**Histogram trimming operators** (v3.11.0+):
- `</` and `>/` — trim observations from native histograms to filter for desired observation bands

**Native histogram functions**:
- `histogram_fraction()` — calculate fractions of observations within given boundaries
- `histogram_quantiles()` (experimental) — compute multiple quantiles at once
- `histogram_stddev()` / `histogram_stdvar()` — standard deviation/variance
