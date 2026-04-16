# Logfire SQL Reference

## Overview

Logfire uses Apache DataFusion as its query engine, with PostgreSQL-compatible syntax. Extends standard SQL with JSON functions (`->>`) for querying attributes.

## Tables

### `records` (Primary)

Contains all spans and logs. Each row is a span or log (span with no duration). A trace is a collection of spans sharing the same `trace_id`.

**Common columns:**

| Column | Type | Description |
|--------|------|-------------|
| `trace_id` | string | Unique identifier for the entire trace |
| `span_id` | string | Unique identifier for this span |
| `parent_span_id` | string | Parent span's ID (null for root spans) |
| `span_name` | string | Low-cardinality label, e.g. `'GET /users/{id}'` |
| `message` | string | Human-readable description with arguments filled in |
| `start_timestamp` | timestamp | When the span/log started |
| `duration` | float | Duration in seconds (0 for logs) |
| `attributes` | JSONB | Span-specific attributes |
| `otel_scope_name` | string | Instrumentation scope name |
| `otel_scope_version` | string | Instrumentation scope version |
| `service_name` | string | Service that generated the span |
| `service_version` | string | Service version |
| `is_exception` | boolean | Whether this record has an exception |
| `exception_message` | string | Exception message if present |

### `metrics`

Contains pre-aggregated numerical data. More efficient for time-series queries.

**Schema:**
```sql
CREATE TABLE metrics AS (
    recorded_timestamp timestamp with time zone,
    metric_name text,
    metric_type text,
    unit text,
    start_timestamp timestamp with time zone,
    aggregation_temporality text,
    is_monotonic boolean,
    metric_description text,
    scalar_value double precision,
    histogram_min double precision,
    histogram_max double precision,
    histogram_count integer,
    histogram_sum double precision,
    histogram_bucket_counts integer[],
    histogram_explicit_bounds double precision[],
    attributes jsonb,
    otel_scope_name text,
    service_name text,
    service_version text,
    process_pid integer
);
```

## Example Queries

### Find All Exceptions

```sql
SELECT message, start_timestamp, duration * 1000 AS duration_ms
FROM records
WHERE is_exception = true
ORDER BY start_timestamp DESC;
```

### Filter by Service and Time Range

```sql
SELECT span_name, count(*)
FROM records
WHERE service_name = 'api-server'
  AND start_timestamp > now() - interval '1 hour'
GROUP BY span_name
ORDER BY count(*) DESC;
```

### Find Slow Spans

```sql
SELECT span_name, message, duration * 1000 AS duration_ms
FROM records
WHERE duration > 1.0
ORDER BY duration DESC;
```

### Query Attributes (JSONB)

```sql
SELECT message, attributes->>'http.method' AS http_method, attributes->>'http.url' AS url
FROM records
WHERE span_name LIKE 'GET %';
```

### Kubernetes Attributes (if using OTel Collector k8sattributes processor)

```sql
SELECT exception_message
FROM records
WHERE is_exception = true
  AND otel_resource_attributes->>'k8s.namespace.name' = 'default';
```

### Query Metrics

```sql
SELECT metric_name, scalar_value, recorded_timestamp
FROM metrics
WHERE metric_name = 'system.cpu.time'
  AND recorded_timestamp > now() - interval '1 hour'
ORDER BY recorded_timestamp;
```

## Tips

- `span_name` should be low-cardinality (use templates like `'GET /users/{id}'`, not `'GET /users/123'`)
- Use `duration * 1000` to get milliseconds
- Click the `span_name` bubble in the Live View to filter by that span name
- Take any `trace_id` or `span_id` from query results and search in the Live View

## Full Documentation

See https://datafusion.apache.org/user-guide/sql/index.html for DataFusion SQL syntax details.
