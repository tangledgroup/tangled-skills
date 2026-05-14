# Data Sources

## Contents
- Managing Data Sources
- Built-in Data Sources
- Query Editors
- Custom Plugins
- Data Source Provisioning

## Managing Data Sources

Data sources are managed under **Connections > Data sources** in the left-side menu. Only organization administrators can add or remove data sources. By default, any user in an organization can query any data source. With Grafana Enterprise or Grafana Cloud, configure data source permissions to restrict access per user, team, or role.

Each data source provides a **query editor** tailored to its data model. After adding a data source, use it in Explore, panels, and alert rules.

### Adding a Data Source

1. Navigate to **Connections > Data sources**
2. Click **Add data source**
3. Select the data source type
4. Configure connection settings (URL, authentication, default options)
5. Click **Save & test**

### Common Configuration Options

| Setting | Description |
|---------|-------------|
| `name` | Display name shown in query editors and dashboards |
| `url` | HTTP endpoint of the data source server |
| `access` | `proxy` (Grafana proxies requests) or `direct` (browser queries directly) |
| `isDefault` | Mark as default data source for new queries |
| `jsonData` | Source-specific JSON configuration |
| `secureJsonData` | Encrypted sensitive data (passwords, tokens) |

## Built-in Data Sources

Grafana ships with built-in support for many data sources. The most commonly used:

### Prometheus
- **Type**: `prometheus`
- **Query language**: PromQL
- **Use case**: Metrics from applications and infrastructure
- **Key config**: URL to Prometheus server, scrape interval awareness

Example query:
```promql
rate(http_requests_total{job="api"}[5m])
```

### Loki
- **Type**: `loki`
- **Query language**: LogQL
- **Use case**: Log aggregation and analysis
- **Key config**: URL to Loki server, max lines setting

Example query:
```logql
{job="app"} |= "error"
```

### Tempo
- **Type**: `tempo`
- **Query language**: Service maps, trace search
- **Use case**: Distributed tracing
- **Key config**: URL to Tempo server, service map data source

### PostgreSQL
- **Type**: `postgres`
- **Query language**: SQL
- **Use case**: Relational data queries
- **Key config**: Host, port, database name, SSL mode

Example query:
```sql
SELECT time, value FROM metrics WHERE time > NOW() - INTERVAL '1 hour'
```

### Elasticsearch
- **Type**: `elasticsearch`
- **Query language**: Lucene / Detect
- **Use case**: Log and document search
- **Key config**: URL, index name, time field name

### CloudWatch
- **Type**: `cloudwatch`
- **Use case**: AWS metrics and logs
- **Key config**: Authentication via IAM roles, credentials, or environment

### InfluxDB
- **Type**: `influxdb`
- **Query language**: Flux (InfluxDB 2.x) or InfluxQL (1.x)
- **Use case**: Time-series data

## Query Editors

Each data source has its own query editor with:
- **Syntax highlighting** and auto-completion for the native query language
- **Multi-query support** — add multiple queries (A, B, C) to a single panel
- **Math operations** — combine results from multiple queries using expressions
- **Query history** — recent queries saved per data source

### Query Operations

After writing a base query, apply transformations:
- **Alias by** — rename series for clarity
- **Reduce** — convert time series to single values (avg, max, min, last)
- **Filter** — show/hide series matching conditions
- **Format as** — table, time series, logs, traces

## Custom Plugins

Install additional data source plugins from the [Grafana Plugin Catalog](https://grafana.com/plugins/) or by downloading directly.

### Installing a Plugin

```bash
# Via grafana-cli
sudo grafana-cli plugins install <plugin-id>
sudo systemctl restart grafana-server

# Example: install MySQL plugin
sudo grafana-cli plugins install grafana-mysql-datasource
```

### Managing Plugins

View installed plugins at **Connections > Plugins**. Admins can update, configure, or remove plugins. Use `--allow-install` flag if plugin signing verification is disabled.

For production, consider pre-installing plugins in Docker images:

```dockerfile
FROM grafana/grafana:13.0.1
RUN grafana-cli plugins install grafana-mysql-datasource
```

## Data Source Provisioning

Define data sources in YAML files under the provisioning directory for version-controlled, repeatable configuration.

### Provisioning Configuration

Create `/etc/grafana/provisioning/datasources/prometheus.yaml`:

```yaml
apiVersion: 1

deleteDatasources:
  - name: Prometheus
    orgId: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 15s
      httpMethod: POST
    secureJsonData:
      basicAuthPassword: "${PROMETHEUS_PASSWORD}"
```

Enable provisioning in `grafana.ini`:

```ini
[paths]
provisioning = /etc/grafana/provisioning
```

Or via a separate provisioning config file that Grafana reads automatically from the `provisioning/` directory.

Environment variables are supported using `$ENV_VAR` or `${ENV_VAR}` syntax in provisioning YAML values.
