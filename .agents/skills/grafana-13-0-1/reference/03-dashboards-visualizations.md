# Dashboards and Visualizations

## Contents
- Dashboard Basics
- Dynamic Dashboards (GA in v13)
- Panel Types
- Variables and Templating
- Annotations
- Dashboard Sharing

## Dashboard Basics

A dashboard is a collection of panels arranged in a layout. Each panel displays data from one or more queries against configured data sources.

### Creating a Dashboard

1. Click **Dashboards > New dashboard**
2. Click **Add visualization** to add a panel
3. Select a data source and write a query
4. Choose a visualization type
5. Configure panel options (title, thresholds, overrides)
6. Click **Save dashboard**

### Dashboard Structure

- **Panels** — individual visualizations arranged in rows or free-form layout
- **Rows** — logical grouping of panels (collapsible)
- **Templates/Variables** — dynamic values that filter or parameterize all queries
- **Annotations** — event markers overlaid on time-series panels

### Saving and Managing

Dashboards can be saved to folders for organization. Use dashboard links to create navigation between related dashboards. Link to other dashboards, external URLs, or panel drill-downs.

## Dynamic Dashboards (GA in v13)

Dynamic dashboards reached general availability in Grafana 13.0 and are on by default. Every new and existing dashboard uses the new layout engine automatically. Existing dashboards are migrated to the new schema when opened — no manual steps required.

Key improvements:
- **Flexible layout** — panels can be freely positioned and resized without rigid row constraints
- **Adaptive editing** — improved editing experience with better performance
- **Auto-migration** — existing dashboards convert to new schema transparently
- **Dashboard templates** — create reusable dashboard structures with Grafana Assistant

## Panel Types

Grafana provides many visualization types. Choose based on the data pattern:

### Time Series
- Line charts for metrics over time
- Supports multiple queries with different colors
- Options: stacking, smoothing, threshold fill, point display
- Best for: CPU usage, request rates, memory trends

### Stat
- Single large value with optional sparkline
- Threshold-based color coding (green/yellow/red)
- Best for: current status, uptime percentage, error count

### Gauge (new in v13)
- Circular or bar gauge showing value relative to range
- Configurable min/max and thresholds
- Best for: capacity utilization, progress indicators

### Table
- Tabular data display with sorting and filtering
- Supports time series and instant queries
- Options: cell overlays, sparklines in cells, conditional formatting
- Best for: top-N lists, inventory, detailed metrics

### Logs
- Log lines from Loki or Elasticsearch with syntax highlighting
- Options: deduplication, wrapping, filtering by level
- Best for: application logs, error tracking

### Heatmap
- Density visualization of values over time and categories
- Best for: request latency distributions, resource usage patterns

### Trace
- Distributed trace visualization from Tempo or Jaeger
- Shows service-to-service call chains with timing
- Best for: debugging slow requests, understanding service dependencies

### Canvas
- Free-form visual layout with shapes, text, and data bindings
- Best for: custom operational views, status walls

### Node Graph
- Network topology visualization
- Best for: service dependency maps, infrastructure diagrams

### Bar Gauge
- Horizontal or vertical bar showing value against thresholds
- Best for: comparing multiple metrics at a glance

### Pie Chart
- Proportional breakdown of categories
- Best for: error type distribution, traffic source split

## Variables and Templating

Dashboard variables make dashboards dynamic by allowing users to filter data at runtime.

### Variable Types

| Type | Description | Example |
|------|-------------|---------|
| Query | Values from a data source query | List of hosts from Prometheus |
| Custom | Hard-coded list of values | `prod,staging,dev` |
| Interval | Time intervals | `1m,5m,15m,1h` |
| DataSource | List of available data sources | Switch between Prometheus instances |
| Constant | Single static value | Environment name |
| Text | Free-form text input | Search string |
| Ad hoc | Key-value filters added to all queries | Add `cluster=us-east-1` to every query |

### Using Variables in Queries

Reference variables with `$variable_name`:

```promql
up{job="$job", instance=~"$instance"}
```

For regex matching, use `=~` with the variable. For multi-value variables, Grafana expands `$var` to `(value1|value2|value3)`.

### All Variable

The built-in `$__all` value represents "select all" for multi-value variables. Use it to match every possible value:

```promql
up{instance=~"$instance"}
```

When all is selected, this expands to `instance=~".*"`.

## Annotations

Annotations mark specific events on time-series panels.

### Query-based Annotations
- Define a query that returns events (e.g., deployment records from Loki)
- Events appear as vertical lines on the panel
- Click to see event details

### Dashboard Annotations
- Manually add annotations while viewing a dashboard
- Useful for marking incidents, maintenance windows

### Alert Annotations
- Alert state changes automatically create annotation markers

## Dashboard Sharing

### Share via Link
- Generate a direct link to the dashboard
- Options: include time range, include variable values

### Snapshots
- Create a point-in-time snapshot of dashboard state
- Store internally or on public snapshot server
- Snapshots are read-only copies

### Embed
- Embed dashboards in external applications via iframe
- Configure CORS and authentication for secure embedding
