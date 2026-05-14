# Auto-Instrumentation

## Overview

The `opentelemetry-instrument` CLI tool and `opentelemetry-instrumentation` package enable automatic instrumentation of Python applications without code changes. Instrumentation packages are maintained in the `opentelemetry-python-contrib` repository.

## The opentelemetry-instrument CLI

```bash
# Auto-instrument a Python application
opentelemetry-instrument python app.py

# With specific instrumentations
opentelemetry-instrument --traces-exporter console python app.py

# Disable auto-instrumentation for a command
OTEL_PYTHON_AUTO_INSTRUMENTATION_ENABLED=false opentelemetry-instrument python app.py
```

## Supported Instrumentations

The contrib repository provides 40+ instrumentation packages. Key ones:

### Web Frameworks

- **Flask** (`opentelemetry-instrumentation-flask`) — HTTP request/response tracing with metrics
- **Django** (`opentelemetry-instrumentation-django`) — Request tracing, view/span naming
- **FastAPI** (`opentelemetry-instrumentation-fastapi`) — ASGI-based tracing with metrics
- **Starlette** (`opentelemetry-instrumentation-starlette`) — ASGI framework support
- **Falcon** (`opentelemetry-instrumentation-falcon`) — Falcon framework tracing
- **Tornado** (`opentelemetry-instrumentation-tornado`) — Tornado HTTP server
- **Pyramid** (`opentelemetry-instrumentation-pyramid`) — Pyramid WSGI framework
- **ASGI** (`opentelemetry-instrumentation-asgi`) — Generic ASGI middleware
- **WSGI** (`opentelemetry-instrumentation-wsgi`) — Generic WSGI middleware

### HTTP Clients

- **requests** (`opentelemetry-instrumentation-requests`) — Session-level tracing
- **httpx** (`opentelemetry-instrumentation-httpx`) — Sync and async HTTP client
- **urllib** (`opentelemetry-instrumentation-urllib`) — Standard library urllib
- **urllib3** (`opentelemetry-instrumentation-urllib3`) — Popular HTTP library
- **aiohttp-client** (`opentelemetry-instrumentation-aiohttp-client`) — Async HTTP client

### Databases

- **SQLAlchemy** (`opentelemetry-instrumentation-sqlalchemy`) — SQL query tracing
- **psycopg2** (`opentelemetry-instrumentation-psycopg2`) — PostgreSQL adapter
- **psycopg** (`opentelemetry-instrumentation-psycopg`) — PostgreSQL v3 adapter
- **PyMySQL** (`opentelemetry-instrumentation-pymysql`) — MySQL connector
- **mysqlclient** (`opentelemetry-instrumentation-mysqlclient`) — MySQL C extension
- **pymongo** (`opentelemetry-instrumentation-pymongo`) — MongoDB driver
- **pymssql** (`opentelemetry-instrumentation-pymssql`) — MSSQL driver
- **mysql-connector** (`opentelemetry-instrumentation-mysql`) — Oracle MySQL connector
- **sqlite3** (`opentelemetry-instrumentation-sqlite3`) — SQLite3 standard library
- **aiopg** (`opentelemetry-instrumentation-aiopg`) — Async PostgreSQL
- **asyncpg** (`opentelemetry-instrumentation-asyncpg`) — Modern async PostgreSQL
- **cassandra** (`opentelemetry-instrumentation-cassandra`) — Cassandra/Scylla driver
- **elasticsearch** (`opentelemetry-instrumentation-elasticsearch`) — Elasticsearch client
- **dbapi** (`opentelemetry-instrumentation-dbapi`) — Generic DB-API 2.0 wrapper

### Caching

- **redis** (`opentelemetry-instrumentation-redis`) — Redis client tracing
- **pymemcache** (`opentelemetry-instrumentation-pymemcache`) — Memcached client

### Message Queues

- **Celery** (`opentelemetry-instrumentation-celery`) — Task queue tracing
- **Kafka** (`opentelemetry-instrumentation-kafka-python`) — Kafka producer/consumer
- **confluent-kafka** (`opentelemetry-instrumentation-confluent-kafka`) — Confluent Kafka
- **aiokafka** (`opentelemetry-instrumentation-aiokafka`) — Async Kafka
- **pika** (`opentelemetry-instrumentation-pika`) — RabbitMQ client
- **aio-pika** (`opentelemetry-instrumentation-aio-pika`) — Async RabbitMQ
- **remoulade** (`opentelemetry-instrumentation-remoulade`) — Task queue
- **boto3sqs** (`opentelemetry-instrumentation-boto3sqs`) — AWS SQS

### Other

- **gRPC** (`opentelemetry-instrumentation-grpc`) — gRPC client/server
- **Jinja2** (`opentelemetry-instrumentation-jinja2`) — Template rendering
- **logging** (`opentelemetry-instrumentation-logging`) — Python stdlib logging bridge
- **botocore** (`opentelemetry-instrumentation-botocore`) — AWS SDK calls
- **AWS Lambda** (`opentelemetry-instrumentation-aws-lambda`) — Lambda runtime
- **click** (`opentelemetry-instrumentation-click`) — CLI framework
- **asyncio** (`opentelemetry-instrumentation-asyncio`) — Async task tracing
- **threading** (`opentelemetry-instrumentation-threading`) — Thread tracing
- **system-metrics** (`opentelemetry-instrumentation-system-metrics`) — CPU, memory, disk metrics
- **tortoise-orm** (`opentelemetry-instrumentation-tortoiseorm`) — Async ORM

## Manual Instrumentor Usage

Instrument programmatically instead of via CLI:

```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Auto-instrument
FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument(enable_commenter=True, dbapi_statement_params=("commenter_suffixes",))

# Uninstrument when needed
FlaskInstrumentor().uninstrument()
```

## Environment Variables for Auto-Instrumentation

- `OTEL_PYTHON_AUTO_INSTRUMENTATION_ENABLED` — Enable/disable all auto-instrumentation (default: true when using CLI)
- `OTEL_TRACES_EXPORTER` — Trace exporter for instrumented apps
- `OTEL_METRICS_EXPORTER` — Metric exporter for instrumented apps
- `OTEL_LOGS_EXPORTER` — Log exporter for instrumented apps

## Instrumentation Best Practices

- Libraries should depend on `opentelemetry-api` only and use manual instrumentation
- Applications should use auto-instrumentation for frameworks and manual instrumentation for business logic
- Set `service.name` via `OTEL_SERVICE_NAME` or `Resource.create()` before starting the app
- Use `BatchSpanProcessor` (not `SimpleSpanProcessor`) in production
- Configure sampling to control data volume: `OTEL_TRACES_SAMPLER=parentbased_traceidratio` with `OTEL_TRACES_SAMPLER_ARG=0.1`
- Suppress instrumentation for internal calls using `context._SUPPRESS_INSTRUMENTATION_KEY`

## Semantic Conventions

OpenTelemetry semantic conventions define standard attribute names. The Python SDK includes `opentelemetry-semantic-conventions`:

```python
from opentelemetry.semconv.attributes import http_attributes
from opentelemetry.semconv.resource import ResourceAttributes

# HTTP attributes
HTTP_METHOD = http_attributes.HTTP_METHOD
HTTP_STATUS_CODE = http_attributes.HTTP_STATUS_CODE

# Resource attributes
SERVICE_NAME = ResourceAttributes.SERVICE_NAME
SERVICE_VERSION = ResourceAttributes.SERVICE_VERSION
```

Note: Semantic conventions are transitioning between stable and incubating namespaces. The `opentelemetry-semantic-conventions` package provides both.
