# SQL Reference

## Overview

Logfire exposes observability data via SQL using Apache DataFusion with PostgreSQL-compatible syntax. Extended with JSON functions and operators such as `->>`.

Primary reference: [DataFusion SQL Language Reference](https://datafusion.apache.org/user-guide/sql/index.html). Generally matches [PostgreSQL syntax](https://www.postgresql.org/docs/current/queries.html).

## Tables

**`records`** — spans and logs. Each row is a span or log (essentially a span with no duration). A trace is a collection of spans sharing the same `trace_id`, structured as a tree.

**`metrics`** — pre-aggregated numerical data. More efficient than `records` for certain queries.

## Records Columns

### Basic Columns

- **`span_name`** — Low-cardinality string label shared by similar records. Template without arguments filled in (e.g., `'Hello {name}'`). Indexed for efficient filtering.
- **`message`** — Human-readable description with arguments filled in (e.g., `'Hello Alice'`). Primarily for display, use `span_name` for queries.
- **`attributes`** — JSON object of arbitrary structured data. Query with `->>` operator: `attributes->>'name' = 'Alice'`. For nested JSON, chain operators: `attributes->>'nested'->>'key'`.
- **`tags`** — Optional array of strings for grouping records. Query with `array_has(tags, 'my-tag')`.
- **`level`** — Severity level stored as integer but queryable by name: `level = 'warn'`, `level > 'info'`. Common values: `info` (9), `notice` (11), `warn` (13), `error` (17). Use `level_num('warn')` to convert names to numbers, `level_name(level)` for the reverse.

### Span Tree Columns

- **`trace_id`** — Unique 32-character hex identifier for the trace. Includes in SELECT for clickable links in UI.
- **`span_id`** — Unique 16-character hex identifier for a single span/log within a trace.
- **`parent_span_id`** — Parent span reference. Filter root spans with `WHERE parent_span_id IS NULL`.

### Timestamp Columns

- **`start_timestamp`** — UTC time when the span/log was created. Used by UI time range filters.
- **`end_timestamp`** — UTC time when the span ended (same as start for logs).
- Duration: `extract('seconds' from end_timestamp - start_timestamp)`

## Common Queries

### Find errors

```sql
SELECT trace_id, span_name, message, level
FROM records
WHERE level > 'info'
ORDER BY start_timestamp DESC
LIMIT 100
```

### Filter by attribute

```sql
SELECT trace_id, span_name, message
FROM records
WHERE attributes->>'http.method' = 'POST'
  AND attributes->>'http.status_code' >= '500'
ORDER BY start_timestamp DESC
```

### Parent-child join

```sql
SELECT
    parent.message AS parent_message,
    child.message  AS child_message
FROM records parent
JOIN records child
    ON  child.trace_id       = parent.trace_id
    AND child.parent_span_id = parent.span_id
```

### Time range filter

```sql
SELECT span_name, message
FROM records
WHERE start_timestamp >= now() - interval '5 minutes'
ORDER BY start_timestamp DESC
```

### Dashboard time series

```sql
SELECT
    time_bucket($resolution, start_timestamp) AS bucket,
    count(*) AS request_count
FROM records
WHERE span_name = 'GET /api/users/{id}'
GROUP BY bucket
ORDER BY bucket
```

`$resolution` is a dashboard variable replaced with the time resolution (e.g., `'1 minute'`).

## Setting Values from Non-Python OTel SDKs

When using other OpenTelemetry SDKs:
- Set `logfire.msg` attribute for the `message` column
- Set `logfire.tags` attribute for the `tags` column
- Set `logfire.level_num` attribute for custom level values
