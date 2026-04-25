# SQL Querying

Logfire stores data in two tables queryable via SQL:

### Records Table (Traces and Logs)

```sql
SELECT message, start_timestamp, duration * 1000 AS duration_ms, attributes
FROM records
WHERE is_exception = true
  AND span_name LIKE '%api%'
ORDER BY start_timestamp DESC
LIMIT 50;
```

Common columns: `trace_id`, `span_id`, `parent_span_id`, `span_name`, `message`, `start_timestamp`, `duration`, `attributes` (JSONB), `otel_scope_*`, `service_name`, `is_exception`.

### Metrics Table

```sql
SELECT metric_name, scalar_value, recorded_timestamp
FROM metrics
WHERE metric_name = 'http.server.duration'
ORDER BY recorded_timestamp DESC;
```

See [reference/07-sql-reference.md](reference/07-sql-reference.md) for the complete SQL reference.
