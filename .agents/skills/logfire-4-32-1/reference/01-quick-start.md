# Logfire Quick Start Guide

## Installation and Setup

### Python

```bash
pip install logfire
logfire auth
```

### JavaScript/TypeScript

```bash
npm install logfire
```

### Rust

See https://github.com/pydantic/logfire-rust

## Basic Usage

```python
import logfire

logfire.configure()
logfire.info('Hello, world!')
```

## Development vs Production

### Development (CLI-based)

```bash
logfire projects use <project-name>
```

Then call `logfire.configure()` without a token — it uses the CLI-selected project.

### Production (Token-based)

```bash
export LOGFIRE_TOKEN=<your-write-token>
```

Tokens are created in the Logfire web UI: Project → Settings → Write Tokens, or via CLI:
```bash
logfire read-tokens --project org/project create
```

## Auto-Instrumentation Examples

### FastAPI

```python
from fastapi import FastAPI
import logfire

app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)
```

### HTTPX

```python
import httpx
import logfire

logfire.configure()
logfire.instrument_httpx()
```

### SQLAlchemy + Psycopg

```python
import logfire

logfire.configure()
logfire.instrument_sqlalchemy()
logfire.instrument_psycopg()
```

### OpenAI

```python
import logfire

logfire.configure()
logfire.instrument_openai()
```

### Pydantic AI

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
```

## Manual Tracing

```python
import logfire

logfire.configure()

with logfire.span('Processing user {user_id}', user_id=123):
    logfire.info('Starting processing')
    result = do_work()
    logfire.info('Completed with result: {result}', result=result)
```

## Next Steps

- Read about [Concepts](../SKILL.md#core-concepts)
- Configure [scrubbing](../SKILL.md#data-scrubbing) for sensitive data
- Set up [sampling](../SKILL.md#sampling) to control costs
- Explore [SQL querying](../SKILL.md#sql-querying) in the Explore view
- Review all [integrations](references/03-integrations.md)
