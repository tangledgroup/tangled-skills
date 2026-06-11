# PromQL Querying

## Contents
- Expression Types
- Selectors (Instant and Range Vectors)
- Operators
- Aggregation Operators
- Binary Operations Between Vectors
- Functions
- Matching Modifiers
- @ Timestamp Modifier
- Query Examples

## Expression Types

PromQL expressions evaluate to one of four types:

| Type | Description | Example |
|------|-------------|---------|
| Instant Vector | Single sample per time series | `up` |
| Range Vector | Time bucket of samples per series | `up[5m]` |
| Scalar | Simple numerical value | `pi()` |
| String | Text value (limited use) | `"hello"` |

## Selectors

### Instant Vector Selector

Selects current values for matching time series:

```promql
http_requests_total
http_requests_total{method="GET", handler="/api"}
```

Label matchers:
- `=` exact match
- `!=` not equal
- `=~` regex match
- `!~` regex not match

```promql
http_requests_total{method=~"(GET|POST)", handler!~"/internal/.*"}
```

### Range Vector Selector

Selects a time window of samples:

```promql
http_requests_total[5m]
up{job="prometheus"}[1h]
```

Duration formats: `ms`, `s`, `m`, `h`, `d`, `w`, `y`.

## Operators

### Comparison Operators
- `==`, `!=`, `>`, `<`, `>=`, `<=`

```promql
up == 1                          # All healthy targets
http_requests_total > 1000       # High-traffic series
```

Comparison between vectors and scalars produces instant vectors.

### Arithmetic Operators
- `+`, `-`, `*`, `/`, `%`, `^`

```promql
rate(http_requests_total[5m]) * 100    # Scale rate
a - b                                   # Element-wise subtraction
```

### Boolean Operators
- `and` — intersection (keep series present in both)
- `or` — union (keep all series)
- `unless` — set difference (remove matching series from left)

```promql
up and on(job) job:request_rate:5m    # Only healthy targets
a or b                                 # All series from both
a unless on(instance) b                # Series in a not in b
```

### Histogram Trim Operators (v3.11.0+)
- `</` — trim observations below threshold
- `>/` — trim observations above threshold

```promql
http_request_duration_seconds </ 0.5   # Only observations < 0.5s
http_request_duration_seconds >/ 1.0   # Only observations > 1.0s
```

## Aggregation Operators

Reduce or expand vectors by grouping labels:

| Operator | Description |
|----------|-------------|
| `sum` | Sum of all values |
| `min` / `max` | Minimum / maximum value |
| `avg` | Average value |
| `count` | Number of elements |
| `count_values` | Count per value |
| `bottomk` / `topk` | Smallest / largest k elements |
| `stddev` / `stdvar` | Standard deviation / variance |
| `quantile` | φ-quantile (0 ≤ φ ≤ 1) |
| `group` | 1 for each element (useful for filtering) |

Grouping clauses:
```promql
sum(rate(http_requests_total[5m])) by (job, method)
sum(rate(http_requests_total[5m])) without (instance)
```

- `by (labels)` — keep only specified labels
- `without (labels)` — remove specified labels, keep all others

### fill Modifiers (v3.10.0+)

Specify default values for missing series in binary operations:
```promql
a + fill(right, 0) b     # Missing right-side series treated as 0
a - fill(left, 1) b      # Missing left-side series treated as 1
```

Modifiers: `fill(left|right, <value>)`, `fill_left(<value>)`, `fill_right(<value>)`.

## Binary Operations Between Vectors

Vector matching controls how series are paired:
- **One-to-one**: Each element on left matches exactly one on right by label set
- **Many-to-one / One-to-many**: Use `on` and `ignoring` to specify matching labels

```promql
# Match only on job label, ignore other labels
http_requests_total / on(job) group_left http_errors_total

# Ignore instance label for matching
a - ignoring(instance) b
```

## Functions

### Rate and Derivative Functions

| Function | Description |
|----------|-------------|
| `rate(v)` | Per-second counter rate, handles resets |
| `irate(v)` | Instant rate using last two points |
| `increase(v)` | Counter increase over time |
| `idelta(v)` | Instant delta (gauge) |
| `delta(v)` | Change over time (gauge) |
| `deriv(v)` | Per-second derivative (linear regression) |

```promql
rate(http_requests_total[5m])
increase(errors_total[1h])
irate(cpu_seconds_total[1m])
```

### Aggregation Over Time

| Function | Description |
|----------|-------------|
| `avg_over_time(v)` | Average over time range |
| `min_over_time(v)` | Minimum over time range |
| `max_over_time(v)` | Maximum over time range |
| `sum_over_time(v)` | Sum over time range |
| `count_over_time(v)` | Count of samples in range |
| `stddev_over_time(v)` | Standard deviation over time |
| `stdvar_over_time(v)` | Variance over time |
| `last_over_time(v)` | Last non-empty value |
| `present_over_time(v)` | 1 if data present, 0 if empty |

```promql
avg_over_time(http_request_duration_seconds{job="api"}[1h])
max_over_time(memory_usage_bytes[24h])
present_over_time(up[5m])   # Check if target was seen
```

### Label Manipulation

| Function | Description |
|----------|-------------|
| `label_replace(v, dst, replacement, src, regex)` | Replace label value |
| `label_join(v, dst, sep, src1, src2, ...)` | Join labels into one |
| `label_delete(v, lbl)` | Delete a label |
| `label_keep(v, lbl1, lbl2, ...)` | Keep only listed labels |

```promql
label_replace(up, "env", "$1", "instance", "(.+):.*")
label_join(requests, "path_method", "/", "path", "method")
```

### Type Conversion and Math

| Function | Description |
|----------|-------------|
| `abs(v)` | Absolute value |
| `ceil(v)` / `floor(v)` | Round up / down |
| `round(v[, to_nearest])` | Round to nearest |
| `clamp_min(v, m)` / `clamp_max(v, m)` | Clamp to min/max |
| `scalar(v)` | Extract scalar from single-element vector |
| `vector(d)` | Wrap scalar as instant vector |

### Histogram Functions

| Function | Description |
|----------|-------------|
| `histogram_quantile(φ, v)` | φ-quantile from histogram |
| `histogram_fraction(low, high, v)` | Fraction of observations in range |
| `histogram_count(v)` | Total observation count |
| `histogram_sum(v)` | Sum of observed values |
| `histogram_stddev(v)` | Standard deviation |
| `histogram_stdvar(v)` | Variance |
| `histogram_quantiles(φ1, φ2, ..., v)` | Multiple quantiles (experimental) |

```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
histogram_fraction(0.1, 0.5, http_request_duration_seconds)
```

### Prediction Functions

| Function | Description |
|----------|-------------|
| `predict_linear(v, t)` | Predict value t seconds into future |
| `changes(v)` | Number of value changes |
| `resets(v)` | Number of counter resets |

```promql
predict_linear(node_filesystem_avail_bytes[1h], 7 * 24 * 3600) > 0
resets(http_requests_total[1h])   # Detect restarts
```

### String Functions

| Function | Description |
|----------|-------------|
| `time()` | Current Unix timestamp |
| `timestamp(v)` | Timestamp of sample |
| `minute()` / `hour()` / `day_of_month()` / `day_of_week()` / `days_in_month()` | Time components |

### Info Function

```promql
info(http_requests_total, target_info, "instance")
```

Joins metric data with `target_info` metadata using specified matching labels.

## @ Timestamp Modifier

Evaluate part of expression at a specific absolute timestamp:

```promql
rate(http_requests_total[@1609459200][5m])
up - up@-1h    # Compare current state to 1 hour ago
```

Useful for comparing values across different time windows without subquery complexity.

## Query Examples

### Request Rate with Error Ratio
```promql
sum(rate(http_requests_total{code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

### Node Memory Usage Percentage
```promql
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```

### Disk Space Prediction (alert if < 24h remaining)
```promql
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 24*3600) < 0
```

### Instance Uptime
```promql
time() - node_boot_time_seconds
```

### SLO Burn Rate (99.9% target over 5m)
```promql
sum(rate(http_requests_total{code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
> (1 - 0.999) * 14.4
```
