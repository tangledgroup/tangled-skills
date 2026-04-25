# Query API

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

See [reference/08-query-api.md](reference/08-query-api.md).
