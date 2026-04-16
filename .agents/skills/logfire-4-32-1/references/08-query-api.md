# Logfire Query API Reference

## Overview

The Logfire Query API provides programmatic SQL-based access to your trace and metric data. Available at `https://logfire-api.pydantic.dev/v1/query`.

## Authentication

Requires a **read token**. Create one via:

### Web UI

1. Open https://logfire.pydantic.dev
2. Select your project
3. Click ⚙️ Settings → Read tokens tab
4. Click "Create read token" and copy the token

### CLI

```bash
logfire read-tokens --project org/project create
```

## Python Clients

Install with optional Arrow support:
```bash
pip install logfire[query]  # includes httpx + pyarrow
# or separately:
pip install httpx pyarrow
```

### Synchronous Client

```python
from logfire.query_client import LogfireQueryClient

client = LogfireQueryClient(token='your-read-token')

# Run a query
result = client.query('SELECT * FROM records LIMIT 10')

# Response formats:
data = result.json()       # List of dicts
csv_data = result.csv()    # CSV string
arrow_table = result.arrow()  # pyarrow Table (requires pyarrow)
```

### Asynchronous Client

```python
from logfire.query_client import AsyncLogfireQueryClient
import asyncio

async def main():
    client = AsyncLogfireQueryClient(token='your-read-token')
    result = await client.query('SELECT * FROM records LIMIT 10')
    print(result.json())

asyncio.run(main())
```

## Direct HTTP Requests

```bash
curl -X POST "https://logfire-api.pydantic.dev/v1/query" \
  -H "Authorization: Bearer your-read-token" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM records LIMIT 5"}'
```

Response format is controlled by the `Accept` header:
- `application/json` (default)
- `text/csv`
- `application/vnd.apache.arrow.stream` (requires pyarrow on client side)

## Environment Variables for Alternative Endpoints

For EU region:
```python
import os
os.environ['LOGFIRE_API_BASE_URL'] = 'https://logfire-eu.pydantic.dev'
```
