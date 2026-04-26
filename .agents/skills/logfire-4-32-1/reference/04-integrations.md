# Integrations

## Overview

Logfire supports first-class integration with many popular Python packages using a single `logfire.instrument_<package>()` call. Each should be called exactly once after `logfire.configure()`.

```python
from fastapi import FastAPI
import logfire

app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)
logfire.instrument_httpx()
```

## Web Frameworks

**FastAPI**: `logfire.instrument_fastapi(app)` — adds request spans with duration, status codes, endpoint arguments, and validation errors. Supports `request_attributes_mapper` for customizing logged attributes and `extra_spans=True` for separate argument-parsing spans.

**Django**: `logfire.instrument_django()`

**Flask**: `logfire.instrument_flask(app)`

**Starlette**: `logfire.instrument_starlette(app)`

**AIOHTTP**: `logfire.instrument_aiohttp_server(app)`, `logfire.instrument_aiohttp_client()`

**ASGI/WSGI**: `logfire.instrument_asgi()`, `logfire.instrument_wsgi()` — middleware-level instrumentation

## Database Clients

**Psycopg**: `logfire.instrument_psycopg()`
**SQLAlchemy**: `logfire.instrument_sqlalchemy()`
**Asyncpg**: `logfire.instrument_asyncpg()`
**PyMongo**: `logfire.instrument_pymongo()`
**MySQL**: `logfire.instrument_mysql()`
**SQLite3**: `logfire.instrument_sqlite3()`
**Redis**: `logfire.instrument_redis()`
**BigQuery**: Built-in, no config needed

## HTTP Clients

**HTTPX**: `logfire.instrument_httpx()`
**Requests**: `logfire.instrument_requests()`
**AIOHTTP Client**: `logfire.instrument_aiohttp_client()`

## LLM and AI Frameworks

**OpenAI**: `logfire.instrument_openai()` or `logfire.instrument_openai(client)` — instruments chat completions, embeddings, image generation, and streaming responses

**Anthropic**: `logfire.instrument_anthropic()`

**Pydantic AI**: `logfire.instrument_pydantic_ai()`

**LangChain**: Built-in OTel support (no special call needed)

**LlamaIndex**: Requires LlamaIndex OpenTelemetry package

**LiteLLM**: Requires LiteLLM callback setup

**Google GenAI**: `logfire.instrument_google_genai()`

**Mirascope**: Use `@with_logfire` decorator

**MCP**: Model Context Protocol support via `logfire.instrument_mcp()`

## Task Queues and Schedulers

**Celery**: `logfire.instrument_celery()` — must be called in both worker processes and the application that enqueues tasks. Automatically propagates context to child tasks.

**Airflow**: Built-in, config needed
**FastStream**: Built-in, config needed

## Logging Libraries

**Standard Library Logging**: Automatic integration
**Loguru**: See Loguru-specific documentation
**Structlog**: See Structlog-specific documentation
**Print**: `logfire.instrument_print()` — captures print() output as spans

## Other Integrations

**Pydantic Validation**: `logfire.instrument_pydantic()` — records validation details automatically

**Pytest**: Built-in plugin, use `pytest --logfire`

**Stripe**: Requires other instrumentations (no dedicated call)

**AWS Lambda**: `logfire.instrument_aws_lambda()`

**System Metrics**: `logfire.instrument_system_metrics()`

## Custom Integrations

Use `logfire-api` as a lightweight shim package with no dependencies. It uses Logfire if installed, otherwise falls back to no-op:

```python
import logfire_api as logfire
logfire.info('Hello, Logfire!')
```

Do not call `logfire_api.configure()` — users call `logfire.configure()` themselves.

## OpenTelemetry Integrations

Since Logfire is OpenTelemetry compatible, any OTel instrumentation package works. See the [OTel Python Contrib](https://opentelemetry-python-contrib.readthedocs.io/en/latest/) for the full list.
