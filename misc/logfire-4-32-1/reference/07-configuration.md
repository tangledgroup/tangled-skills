# Configuration

## Methods and Precedence

Three ways to configure Logfire, in order of precedence (highest first):

1. Programmatically via `logfire.configure()`
2. Environment variables
3. Configuration file (`pyproject.toml`)

## Programmatic Configuration

```python
import logfire

logfire.configure(
    service_name='my-service',
    service_version='1.0.0',
    send_to_logfire=True,
    console=True,
    console_colors='auto',
)
```

Key parameters:
- `service_name` — identifies the service in traces (important for backends like Jaeger)
- `service_version` — version label
- `send_to_logfire` — whether to send data to Logfire cloud (default True)
- `console` — enable/disable console output
- `console_colors` — `'auto'`, `'always'`, `'never'`
- `scrubbing` — sensitive data redaction (default True)
- `sampling` — sampling strategy
- `distributed_tracing` — control trace context extraction
- `inspect_arguments` — f-string variable inspection (default True in Python 3.11+)
- `advanced` — `AdvancedOptions` for base_url, custom exporters, etc.

## Environment Variables

Key environment variables:
- `LOGFIRE_TOKEN` — write token for authentication
- `LOGFIRE_ENVIRONMENT` — environment label (e.g., 'development', 'production')
- `OTEL_EXPORTER_OTLP_ENDPOINT` — OTLP endpoint URL
- `OTEL_EXPORTER_OTLP_HEADERS` — OTLP headers (e.g., `'Authorization=your-write-token'`)
- `OTEL_RESOURCE_ATTRIBUTES` — resource attributes (e.g., `'service.name=my_service'`)

When using environment variables, you still need to call `logfire.configure()` but can leave out arguments.

## Configuration File (`pyproject.toml`)

```toml
[tool.logfire]
project_name = "My Project"
console_colors = "never"
```

Keys match the parameters of `logfire.configure()`.

## Multiple Configurations

Use `logfire.configure(local=True, ...)` for different configurations in different parts of an application:

```python
import logfire

# Global configuration (once)
logfire.configure()

# Local instance without console logging
no_console_logfire = logfire.configure(local=True, console=False)

logfire.info('Uses global config — appears in console')
no_console_logfire.info('Uses local config — no console output')

# Instrumentation uses the instance it's called on
logfire.instrument_httpx()                      # global config
no_console_logfire.instrument_psycopg()         # local config
```

## Advanced Options

```python
import logfire

# Self-hosted instance
logfire.configure(
    advanced=logfire.AdvancedOptions(base_url='https://logfire.my-company.com'),
)

# Data region selection
logfire.configure(advanced=logfire.AdvancedOptions(region='eu'))
```

## CLI Configuration

```bash
logfire --region eu auth          # specify data region
logfire --base-url="https://<hostname>" auth   # self-hosted instance
```

Credentials are stored in `~/.logfire/default.toml`.
