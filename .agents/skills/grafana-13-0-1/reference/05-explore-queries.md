# Explore and Queries

## Contents
- Explore Interface
- Query Management
- Ad Hoc Filters
- Saved Queries
- Correlations

## Explore Interface

Explore is the starting point for querying, analyzing, and aggregating data in Grafana without creating a dashboard. It provides real-time data analysis with flexible visualization options.

### Getting Started

1. Click **Explore** in the left sidebar (compass icon)
2. Select a data source from the dropdown
3. Write a query in the query editor
4. Run the query and view results
5. Switch between visualization modes: Time series, Tables, Logs, Traces, Histogram

### Query Editor

The query editor provides:
- **Syntax highlighting** and auto-completion for the selected data source
- **Multi-query support** — add queries A, B, C and combine results
- **Query operations** — transform results with reduce, filter, calculate
- **Time range picker** — select custom ranges or presets (last 1h, 6h, 24h, 7d)

### Visualization Modes

| Mode | Best For |
|------|----------|
| Time series | Metrics over time |
| Tables | Structured data inspection |
| Logs | Log line analysis with filtering |
| Traces | Distributed trace exploration |
| Histogram | Distribution analysis |

## Query Management

### Multi-Query Panels

Add multiple queries to a single Explore view by clicking **+ Add query**. Each query gets a letter label (A, B, C). Use **Math** to combine results:

```
A + B       # Sum two series
A / B * 100 # Calculate percentage
```

### Query Inspector

Use the Query inspector to debug queries:
- View raw request/response from the data source
- Check query execution time
- Inspect ref IDs and dependencies between queries
- Copy generated SQL/PromQL for external use

Access via the **Inspect** button in the query editor.

## Ad Hoc Filters

Ad hoc filters add key-value conditions to all queries on a dashboard or in Explore without modifying individual queries. They appear as tags above the query editor.

### Using Ad Hoc Filters

1. Click **+ Add filter** in the ad hoc filters section
2. Select a key (auto-discovered from the data source schema)
3. Choose an operator (`=`, `<>`, `=~`, `!~`)
4. Enter a value

Example: Adding `cluster=us-east-1` and `environment=production` filters automatically appends `{cluster="us-east-1", environment="production"}` to all PromQL queries.

### Supported Data Sources

Ad hoc filters work with Prometheus, Loki, InfluxDB, MySQL, PostgreSQL, Elasticsearch, and CloudWatch.

## Saved Queries

Saved queries let you store and reuse complex queries across the team without creating full dashboards.

### Saving a Query

1. In Explore, write your query
2. Click **Save** (disk icon) in the query editor
3. Enter a name and optional description
4. Choose to save to a folder

### Using Saved Queries

- Browse saved queries from the Explore sidebar
- Load a saved query into any panel or Explore session
- Use as a starting point for new investigations
- Share with team members via folder permissions

Saved queries are particularly useful for:
- Common debugging queries
- Standard health-check queries
- On-call runbook references

## Correlations

Correlations define automatic cross-data-source lookups. When viewing data in one source, correlations suggest related data from other sources.

### How Correlations Work

1. Admin defines a correlation (e.g., "from a trace ID in logs, find the corresponding trace in Tempo")
2. When a user views log data in Explore, Grafana detects the trace ID
3. A correlation link appears, allowing one-click navigation to the trace

### Configuring Correlations

Navigate to **Connections > Correlations** (admin only). Define:
- **Source data source** — where the trigger value is found
- **Target data source** — where to look up related data
- **Extraction pattern** — regex or field path to extract the key
- **Target query** — how to query the target data source with the extracted key

Correlations are configured per organization and can be managed via provisioning YAML.
