# Logfire Configuration Reference

## Programmatic Configuration

```python
import logfire

logfire.configure(
    # Authentication
    token=None,                      # Write token (or use LOGFIRE_TOKEN env var)
    
    # Data destination
    send_to_logfire=True,            # Send data to Logfire platform
    
    # Console output
    console_colors='auto',           # 'always', 'never', 'auto'
    console_output='logs_and_spans', # What to show: 'none', 'logs', 'spans', 'logs_and_spans'
    
    # Data processing
    scrubbing=True,                  # Enable sensitive data scrubbing (or ScrubbingOptions)
    sampling=None,                   # Sampling strategy (or SamplingOptions)
    
    # Identification
    project_name='default',          # Project name for this instance
    service_name=None,               # Service name (OTel service.name resource attribute)
    environments=None,               # Environment names (list of str or comma-separated env var)
    
    # Distributed tracing
    distributed_tracing=True,        # Extract trace context from incoming headers
    
    # Limits
    max_log_size=10000,              # Max log message size in bytes
)
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LOGFIRE_TOKEN` | Write token for authentication | `LOGFIRE_TOKEN=lf_abc123...` |
| `LOGFIRE_SEND_TO_LOGFIRE` | Enable/disable sending to Logfire | `LOGFIRE_SEND_TO_LOGFIRE=false` |
| `LOGFIRE_DISTRIBUTED_TRACING` | Control trace context extraction | `LOGFIRE_DISTRIBUTED_TRACING=false` |
| `LOGFIRE_ENVIRONMENTS` | Comma-separated environment names | `LOGFIRE_ENVIRONMENTS=production,staging` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Alternative OTel backend endpoint | `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | Traces-specific endpoint | `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://jaeger:4318/v1/traces` |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | Metrics-specific endpoint | See above pattern |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | Logs-specific endpoint | See above pattern |

## pyproject.toml Configuration

```toml
[tool.logfire]
project_name = "My Project"
console_colors = "never"
send_to_logfire = false
service_name = "my-service"
```

Keys match the parameters of `logfire.configure()`.

## Multiple Configurations

You can create multiple Logfire instances for different purposes:

```python
import logfire

# Main instance
logfire.configure(
    project_name='main-app',
    service_name='api-server',
)

# Separate instance for background tasks
bg_logfire = logfire.Logfire(
    project_name='background-tasks',
    service_name='worker',
)

bg_logfire.info('Background task completed')
```

## Alternative Backends

Send data to any OTLP-compliant backend:

```python
import os
import logfire

os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://localhost:4318/v1/traces'

logfire.configure(
    service_name='my-service',
    send_to_logfire=False,  # Don't also send to Logfire platform
)
```

See the [Alternative Backends guide](../SKILL.md#alternative-backends) for full details including Jaeger integration.

## Data Regions

| Region | URL | Hosting |
|--------|-----|---------|
| US | `logfire-us.pydantic.dev` | GCP us-east4 |
| EU | `logfire-eu.pydantic.dev` | GCP europe-west4 |

Choose at signup. The global domain (`logfire.pydantic.dev`) redirects to your selected region.

## Configuration Precedence

1. Programmatic `configure()` parameters (highest)
2. Environment variables
3. `pyproject.toml` configuration (lowest)
