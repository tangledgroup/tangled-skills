# Logfire Integrations Reference

## Web Frameworks

| Framework | Instrument Call | Notes |
|-----------|----------------|-------|
| FastAPI | `logfire.instrument_fastapi(app)` | Full request/response tracing |
| Django | `logfire.instrument_django()` | Automatic middleware setup |
| Flask | `logfire.instrument_flask(app)` | Request routing and DB spans |
| Starlette | `logfire.instrument_starlette(app)` | Base for FastAPI |
| AIOHTTP (server) | `logfire.instrument_aiohttp_server(app)` | Async web framework |
| ASGI | `logfire.instrument_asgi(app)` | Generic ASGI apps |
| WSGI | `logfire.instrument_wsgi(app)` | Generic WSGI apps |

## HTTP Clients

| Client | Instrument Call | Notes |
|--------|----------------|-------|
| HTTPX | `logfire.instrument_httpx()` | Async/sync HTTP client |
| Requests | `logfire.instrument_requests()` | Popular sync HTTP library |
| AIOHTTP (client) | `logfire.instrument_aiohttp_client()` | Async HTTP client |

## Databases

| Database | Instrument Call | Notes |
|----------|----------------|-------|
| SQLAlchemy | `logfire.instrument_sqlalchemy(engine)` | ORM queries traced |
| Psycopg | `logfire.instrument_psycopg(conn)` | PostgreSQL adapter v3 |
| Asyncpg | `logfire.instrument_asyncpg()` | Async PostgreSQL driver |
| PyMongo | `logfire.instrument_pymongo()` | MongoDB driver |
| MySQL | `logfire.instrument_mysql()` | MySQLdb connector |
| SQLite3 | `logfire.instrument_sqlite3(conn)` | Built-in SQLite |
| Redis | `logfire.instrument_redis(client)` | Redis client |
| BigQuery | N/A | Built-in, no config needed |

## LLM Clients and AI Frameworks

| Provider/Framework | Instrument Call | Notes |
|--------------------|----------------|-------|
| Pydantic AI | `logfire.instrument_pydantic_ai()` | Full agent tracing |
| OpenAI | `logfire.instrument_openai()` | Chat completions, embeddings, etc. |
| Anthropic | `logfire.instrument_anthropic()` | Claude API calls |
| Google GenAI | Built-in | Uses OTel instrumentation |
| LangChain | Built-in | OpenTelemetry support built in |
| LlamaIndex | Via package | Requires LlamaIndex OTel package |
| LiteLLM | Via callback | Requires LiteLLM callback setup |
| DSPy | Built-in | Uses OTel instrumentation |
| Magentic | Built-in | Native Logfire support |
| Mirascope | Decorator | Use `@with_logfire` decorator |
| Claude Agent SDK | Built-in | Uses OTel instrumentation |
| MCP | Built-in | Uses OTel instrumentation |

## Task Queues and Schedulers

| Tool | Instrument Call | Notes |
|------|----------------|-------|
| Celery | `logfire.instrument_celery()` | Must call in both worker and producer |
| Airflow | N/A | Built-in, config needed |
| FastStream | N/A | Built-in, config needed |

## Logging Libraries

| Library | Integration | Notes |
|---------|-------------|-------|
| Standard Library | Built-in | Bridges `logging` module |
| Loguru | Bridge available | See Logfire docs for setup |
| Structlog | Bridge available | See Logfire docs for setup |

## Cloud and Other

| Service | Instrument Call | Notes |
|---------|----------------|-------|
| AWS Lambda | `logfire.instrument_aws_lambda()` | Serverless function tracing |
| Stripe | Via other libs | Requires payment instrumentation |
| System Metrics | `logfire.instrument_system_metrics()` | CPU, memory, disk metrics |
| Pydantic Validation | `logfire.instrument_pydantic()` | Data validation performance |

## Pytest Integration

```bash
pytest --logfire
```

Built-in plugin — no code changes needed. Sets `send_to_logfire=False` by default.

## Creating Custom Integrations

Use the `logfire-api` shim package for optional Logfire dependency:

```python
import logfire_api as logfire

logfire.info('This only logs if user has logfire installed')
# Don't call logfire_api.configure() — up to your users
```

## OpenTelemetry Compatibility

Logfire works with any OTel instrumentation package from [opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib). Standard OTel instrumentation always works.
