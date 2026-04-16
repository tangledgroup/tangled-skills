---
name: logfire-4-32-1
description: Complete toolkit for Pydantic Logfire 4.32.1 — production-grade AI observability built on OpenTelemetry. Use when instrumenting Python/JS/Rust apps with distributed tracing, spans, metrics, and logs; configuring auto-instrumentation for FastAPI, OpenAI, LangChain, databases, and web frameworks; querying trace data via SQL; scrubbing sensitive data; implementing sampling strategies; or integrating with the Logfire platform.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.32.1"
tags:
  - observability
  - tracing
  - OpenTelemetry
  - logging
  - metrics
  - AI
  - LLM
category: developer-tools
external_references:
  - https://github.com/pydantic/logfire/tree/v4.32.1/docs
---

# Pydantic Logfire 4.32.1

## Overview

Pydantic **Logfire** is a production-grade AI and general observability platform built on OpenTelemetry. It provides distributed tracing, metrics, logs, and LLM-specific observability for Python, JavaScript/TypeScript, Rust, and any language with OTel support. Logfire offers auto-instrumentation for 40+ popular libraries, SQL-based querying of trace data, scrubbing of sensitive data, configurable sampling, and a web UI for exploring traces.

Logfire is built by the team behind Pydantic Validation and integrates natively with Pydantic AI, FastAPI, OpenAI, Anthropic, LangChain, LlamaIndex, and many more. The Python SDK is open source under the MIT license.

## When to Use

Use this skill when:
- Setting up distributed tracing in Python, JavaScript/TypeScript, or Rust applications
- Auto-instrumenting web frameworks (FastAPI, Django, Flask, Starlette), HTTP clients (HTTPX, Requests), databases (SQLAlchemy, Psycopg, Redis), or LLM clients (OpenAI, Anthropic, LangChain)
- Configuring Logfire SDK: `logfire.configure()` with custom settings
- Implementing manual tracing with `logfire.span()` and `logfire.log()`
- Querying trace/metric data using SQL in the Explore view or via the Query API
- Scrubbing sensitive data (passwords, API keys, PII) before export
- Configuring sampling strategies (random head sampling, tail sampling by level/duration)
- Setting up context propagation across services (distributed tracing)
- Integrating with the OpenTelemetry Collector for centralized processing
- Using the MCP server to allow LLMs to query telemetry data
- Writing tests that assert emitted spans/logs using `logfire.testing`
- Deploying Logfire in Kubernetes with OTel Collector sidecars

## Core Concepts

### Spans and Traces
- **Span**: The atomic unit of telemetry — a timed operation with name, attributes, logs, and child spans. Think of it as a log with extra functionality.
- **Trace**: A tree structure of related spans showing the path of a request through your system. Spans are ordered and nested.

### Metrics
Calculated values collected at regular intervals (latency, CPU load, queue length). Aggregated over time for charting trends, establishing SLOs, and triggering alerts. Logfire integrations set up common metrics automatically.

### Logs
Timestamped text records with optional metadata. No duration — they record discrete events. Available at levels: `trace`, `debug`, `notice`, `info`, `warn`, `error`, `fatal`.

### OpenTelemetry Foundation
Logfire is fully OTel-compatible. You can send data to any OTLP-compliant backend, use standard OTel instrumentation libraries, and forward subsets to your SIEM/warehouse without vendor lock-in.

## Installation

```bash
pip install logfire
```

Authenticate your local environment:
```bash
logfire auth
```

For JavaScript/TypeScript:
```bash
npm install logfire
```

For Rust: see the [logfire-rust](https://github.com/pydantic/logfire-rust) repository.

## Quick Start

### Development Setup

```python
import logfire

logfire.configure()  # Initialize Logfire
logfire.info('Hello, {name}!', name='world')
```

### Production Setup

```bash
export LOGFIRE_TOKEN=<your-write-token>
```

```python
import logfire

logfire.configure()  # Uses LOGFIRE_TOKEN from environment
logfire.info('Production log entry')
```

## Configuration

The primary configuration method is `logfire.configure()`:

```python
import logfire

logfire.configure(
    token='your-write-token',       # Write token (or use LOGFIRE_TOKEN env var)
    send_to_logfire=True,           # Send data to Logfire platform
    console_colors='auto',          # Colorize console output: 'always', 'never', 'auto'
    console_output='logs_and_spans', # What to show in console
    scrubbing=True,                 # Enable sensitive data scrubbing
    sampling=None,                  # Sampling strategy (see below)
    environments=['production'],    # Environment names for this instance
    project_name='my-project',      # Project name
    service_name='my-service',      # Service name
    distributed_tracing=True,       # Extract trace context from headers
    max_log_size=10000,             # Max log message size in bytes
)
```

Configuration can also be set via:
- **Environment variables** (see [references/02-configuration.md](references/02-configuration.md))
- **`pyproject.toml`**: `[tool.logfire]` section with same keys as `configure()` parameters

### Environment Variables

Key environment variables include:
| Variable | Purpose |
|----------|---------|
| `LOGFIRE_TOKEN` | Write token for authentication |
| `LOGFIRE_SEND_TO_LOGFIRE` | Enable/disable sending to Logfire (`true`/`false`) |
| `LOGFIRE_DISTRIBUTED_TRACING` | Control trace context extraction (`true`/`false`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Alternative backend endpoint URL |
| `LOGFIRE_ENVIRONMENTS` | Comma-separated environment names |

See [references/02-configuration.md](references/02-configuration.md) for the full list.

## Manual Tracing

### Spans

```python
import logfire
from pathlib import Path

logfire.configure()

cwd = Path.cwd()
total_size = 0

with logfire.span('counting size of {cwd=}', cwd=cwd):
    for path in cwd.iterdir():
        if path.is_file():
            with logfire.span('reading {path}', path=path.relative_to(cwd)):
                total_size += len(path.read_bytes())
    logfire.info('total size is {size} bytes', size=total_size)
```

### Decorator-based Spans

```python
@logfire.instrument('Processing item {item_id}')
def process_item(item_id: str):
    # Code here is wrapped in a span
    return do_work(item_id)
```

### Logging Levels

```python
logfire.trace('Detailed diagnostic info')
logfire.debug('Debug information')
logfire.notice('Notable but not significant event')
logfire.info('General informational message')
logfire.warn('Warning — something unexpected happened')
logfire.error('Error — operation failed')
logfire.fatal('Fatal — application may crash')
```

### F-strings and Message Templates

Use message templates (not f-strings) for proper scrubbing:
```python
# ✅ Safe — arguments are parsed separately, scrubbed if they match patterns
logfire.info('User {user} logged in', user=User(id=123, password='secret'))

# ⚠️ Only safe in Python 3.11+ with inspect_arguments enabled
logfire.info(f'User {user} logged in')

# ❌ Unsafe — entire string is logged as-is, not scrubbed
user_str = str(user)
logfire.info(f'User {user_str} logged in')
```

## Auto-Instrumentation

Logfire provides one-call instrumentation for 40+ libraries:

```python
import logfire
from fastapi import FastAPI
import httpx

logfire.configure()

app = FastAPI()
logfire.instrument_fastapi(app)
logfire.instrument_httpx()
logfire.instrument_sqlalchemy()
logfire.instrument_psycopg()
logfire.instrument_redis()
logfire.instrument_openai()
logfire.instrument_anthropic()
logfire.instrument_pydantic_ai()
```

### Integration Matrix

| Category | Libraries | Instrument Call |
|----------|-----------|-----------------|
| **Web Frameworks** | FastAPI, Django, Flask, Starlette, AIOHTTP, ASGI, WSGI | `instrument_<framework>()` |
| **HTTP Clients** | HTTPX, Requests, AIOHTTP (client) | `instrument_httpx()`, `instrument_requests()`, `instrument_aiohttp_client()` |
| **Databases** | SQLAlchemy, Psycopg, Asyncpg, PyMongo, MySQL, SQLite3, Redis, BigQuery | `instrument_<db>()` |
| **LLM Clients** | OpenAI, Anthropic, Google GenAI, DSPy, LangChain, LlamaIndex, LiteLLM, Magentic, Mirascope, Pydantic AI, Claude Agent SDK, MCP | `instrument_<llm>()` or built-in support |
| **Task Queues** | Celery, Airflow, FastStream | `instrument_celery()` or built-in |
| **Logging** | Standard Library Logging, Loguru, Structlog | Built-in bridge |
| **Cloud** | AWS Lambda | `instrument_aws_lambda()` |
| **Testing** | Pytest | `pytest --logfire` (built-in plugin) |
| **Other** | Stripe, System Metrics, Pydantic Validation | `instrument_stripe()`, `instrument_system_metrics()`, `instrument_pydantic()` |

See [references/03-integrations.md](references/03-integrations.md) for detailed integration documentation.

## Data Scrubbing

Logfire automatically redacts sensitive data matching these default patterns:
- `password`, `passwd`, `mysql_pwd`, `secret`, `auth` (not authours), `credential`
- `private_key`, `api_key`, `session`, `cookie`
- `social_security`, `credit_card`, `csrf`, `xrf`, `jwt`, `ssn`

### Custom Patterns

```python
import logfire

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(
        extra_patterns=['my_custom_pattern'],
    )
)
```

### Scrubbing Callback

```python
def scrubbing_callback(match: logfire.ScrubMatch):
    if match.path == ('attributes', 'my_safe_value'):
        return match.value  # Prevent redaction for this field

logfire.configure(
    scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback)
)
```

### LLM Message Content

Scrubbing is **disabled** for LLM message attributes (`gen_ai.input.messages`, `gen_ai.output.messages`) to avoid false positives. To exclude content entirely:

```python
logfire.instrument_pydantic_ai(include_content=False)
```

See [references/04-scrubbing.md](references/04-scrubbing.md) for complete scrubbing guide.

## Sampling

Control data volume and cost with sampling strategies:

### Random Head Sampling (50% of traces)

```python
logfire.configure(sampling=logfire.SamplingOptions(head=0.5))
```

### Tail Sampling by Level and Duration

Keep all traces with errors/warnings or duration > 5 seconds:

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        level_threshold='info',
        duration_threshold=5.0,  # seconds
    )
)
```

### Combined Head + Tail Sampling

```python
logfire.configure(
    sampling=logfire.SamplingOptions.level_or_duration(
        head=0.1,           # Keep max 10% of traces
        background_rate=0.3, # But keep 30% of non-notable traces anyway
    )
)
```

### Custom Sampling

```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

logfire.configure(
    sampling=logfire.SamplingOptions(
        head=ParentBased(MyCustomSampler())
    )
)
```

See [references/05-sampling.md](references/05-sampling.md) for comprehensive sampling documentation.

## Distributed Tracing

Logfire automatically propagates context across services via the `traceparent` header when using instrumented HTTP clients and servers. For manual propagation:

```python
import logfire

logfire.configure()

with logfire.span('parent'):
    ctx = logfire.get_context()

# In another process/service:
with logfire.attach_context(ctx):
    logfire.info('child')  # Appears as child of parent span
```

ThreadPoolExecutor and ProcessPoolExecutor are automatically patched for context propagation.

For web services exposed to the public internet, set `distributed_tracing=False` to prevent accidental context extraction from external clients.

See [references/06-distributed-tracing.md](references/06-distributed-tracing.md).

## SQL Querying

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

See [references/07-sql-reference.md](references/07-sql-reference.md) for the complete SQL reference.

## Query API

Programmatic access via Python clients:

```python
from logfire.query_client import LogfireQueryClient, AsyncLogfireQueryClient

client = LogfireQueryClient(token='your-read-token')
result = client.query('SELECT * FROM records LIMIT 10')

# Response formats:
result.json()      # JSON format
result.csv()       # CSV format
result.arrow()     # Apache Arrow format (requires pyarrow)
```

Read tokens are created in the Logfire web UI under Project → Settings → Read Tokens, or via CLI:
```bash
logfire read-tokens --project org/project create
```

See [references/08-query-api.md](references/08-query-api.md).

## OpenTelemetry Collector Integration

Use the OTel Collector for centralized configuration, data transformation, and enrichment:

```yaml title="config.yaml"
receivers:
  otlp:
    protocols:
      http:
        endpoint: "0.0.0.0:4318"
exporters:
  otlphttp:
    endpoint: "https://logfire-us.pydantic.dev"
    headers:
      Authorization: "Bearer ${env:LOGFIRE_TOKEN}"
processors:
  batch:
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp]
```

Use cases: centralized credentials, data scrubbing, Kubernetes metadata enrichment, backing up to S3.

See [references/09-otel-collector.md](references/09-otel-collector.md) for deployment examples.

## MCP Server

Allow LLMs to query your telemetry data via Model Context Protocol:

### Remote MCP Server (Recommended)

```json
{
  "mcpServers": {
    "logfire": {
      "type": "http",
      "url": "https://logfire-us.pydantic.dev/mcp"
    }
  }
}
```

Supported clients: Cursor, Claude Code, Claude Desktop, Cline, VS Code, Zed. Use `logfire-eu.pydantic.dev` for EU region.

See [references/10-mcp-server.md](references/10-mcp-server.md).

## Testing

Assert emitted spans and logs in unit tests:

```python
import pytest
import logfire
from logfire.testing import CaptureLogfire

def test_observability(capfire: CaptureLogfire):
    with pytest.raises(Exception):
        with logfire.span('a span!'):
            logfire.info('a log!')
            raise Exception('an exception!')

    spans = capfire.exporter.exported_spans_as_dict()
    assert len(spans) == 2
```

When running under pytest, `send_to_logfire=False` by default.

See [references/11-testing.md](references/11-testing.md).

## CLI Reference

```bash
logfire auth                    # Authenticate locally
logfire projects use <name>     # Select project
logfire projects create         # Create a new project
logfire read-tokens --project org/project create  # Create read token
logfire --help                  # Full command reference
```

## Data Regions

Logfire hosts data in two regions:
| Region | URL | Hosting |
|--------|-----|---------|
| 🇺🇸 US | `logfire-us.pydantic.dev` | GCP us-east4 |
| 🇪🇺 EU | `logfire-eu.pydantic.dev` | GCP europe-west4 |

Regions are strictly separated — no data sharing, separate authentication. Choose at signup based on geographic proximity and compliance requirements (GDPR → EU region).

## Languages Supported

- **Python**: Full SDK with deep AI framework integrations ([GitHub](https://github.com/pydantic/logfire))
- **JavaScript/TypeScript**: Browser, Node.js, Next.js, Cloudflare Workers, Deno ([GitHub](https://github.com/pydantic/logfire-js))
- **Rust**: First-class SDK ([GitHub](https://github.com/pydantic/logfire-rust))
- **Any language**: Via OpenTelemetry — Go, Java, .NET, Ruby, and all OTel-supported languages

## Web UI Features

The Logfire web UI provides:
- **Live View**: Real-time stream of spans/logs as they arrive
- **Explore**: SQL query editor for traces and metrics
- **Dashboards**: Pre-built and custom dashboards with visualizations
- **Alerts**: SQL-backed alerting on trace/metric conditions
- **Issues**: Automatic detection of errors, regressions, and anomalies
- **Prompt Playground**: Test and iterate on prompts
- **Public Traces**: Shareable read-only trace views

## Self-Hosting

The Logfire SDKs are open source (MIT), but the server application and UI are closed source. Enterprise plans include self-hosted deployment options. EU and US hosting regions available for data residency requirements.

## Key API Reference

### `logfire.configure(**kwargs)`
Initialize Logfire. Call once at application startup. Parameters control token, scrubbing, sampling, environments, service name, distributed tracing behavior, and more.

### `logfire.span(name, **attributes)`
Create a span (context manager or decorator). Measures duration, captures exceptions, accepts child spans/logs.

### `logfire.info(message, **kwargs)` through `logfire.fatal()`
Log messages at various severity levels. Use message templates with `{placeholder}` syntax.

### `logfire.metric_histogram(name, unit, description)`
Create a histogram metric for recording latency/distribution data. Call `.record(value)` to add samples.

### `logfire.instrument_<package>()`
One-call auto-instrumentation for 40+ libraries. Must be called after `configure()`.

### `logfire.ScrubbingOptions(extra_patterns=[], callback=None)`
Configure sensitive data scrubbing behavior.

### `logfire.SamplingOptions(head=rate, tail=func, level_or_duration())`
Configure sampling strategies for controlling data volume.

## References

- Official documentation: https://pydantic.dev/logfire/docs/
- GitHub repository: https://github.com/pydantic/logfire/tree/v4.32.1
- JavaScript SDK: https://github.com/pydantic/logfire-js
- Rust SDK: https://github.com/pydantic/logfire-rust
- MCP Server: https://github.com/pydantic/logfire-mcp
- OpenTelemetry: https://opentelemetry.io/
