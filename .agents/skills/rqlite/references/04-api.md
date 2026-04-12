# HTTP API

How to write data and read it back using rqlite's HTTP API.

## Overview

Each rqlite node exposes an HTTP API for database operations. The API supports both JSON and plain text formats, with multiple endpoints optimized for different use cases.

## Endpoints

### `/db/execute` - Write Operations

Accepts write requests (INSERT, UPDATE, DELETE, CREATE, ALTER, DROP).

**Method:** POST

**Request Formats:**
- JSON array of SQL statements
- Plain text SQL statement

**Example - JSON:**
```bash
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[
    "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
    "INSERT INTO users(name) VALUES(\"Alice\")"
  ]'
```

**Example - Plain Text:**
```bash
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: text/plain" \
  -d 'CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)'
```

### `/db/query` - Read Operations

Accepts only read requests (SELECT). Attempting writes returns an error.

**Method:** GET or POST

**Example - GET:**
```bash
curl -G 'localhost:4001/db/query' \
  --data-urlencode 'q=SELECT * FROM users'
```

**Example - POST (JSON):**
```bash
curl -XPOST 'localhost:4001/db/query' \
  -H "Content-Type: application/json" \
  -d '["SELECT * FROM users"]'
```

### `/db/request` - Unified Endpoint

Accepts both read and write requests. Response format depends on the request type.

**Method:** POST

**Example:**
```bash
curl -XPOST 'localhost:4001/db/request' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO users(name) VALUES(\"Bob\")",
    "SELECT * FROM users"
  ]'
```

## Response Formats

### Tabular Format (Default)

```json
{
  "results": [
    {
      "columns": ["id", "name", "email"],
      "types": ["integer", "text", "text"],
      "values": [
        [1, "Alice", "alice@example.com"],
        [2, "Bob", "bob@example.com"]
      ],
      "time": 0.000123
    }
  ],
  "time": 0.000456
}
```

### Associative Format

Add `?associative` to get rows as maps:

```bash
curl -G 'localhost:4001/db/query?associative' \
  --data-urlencode 'q=SELECT * FROM users'
```

**Response:**
```json
{
  "results": [
    {
      "types": {"id": "integer", "name": "text", "email": "text"},
      "rows": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
      ],
      "time": 0.000123
    }
  ],
  "time": 0.000456
}
```

### Write Response

```json
{
  "results": [
    {
      "last_insert_id": 3,
      "rows_affected": 1,
      "time": 0.000234
    }
  ],
  "time": 0.000567
}
```

## Query Parameters

### Common Parameters

| Parameter | Description | Values | Default |
|-----------|-------------|--------|---------|
| `pretty` | Pretty-print JSON response | (boolean) | `false` |
| `timings` | Include timing information | (boolean) | `false` |
| `associative` | Return rows as maps | (boolean) | `false` |
| `blob_array` | Return BLOBs as byte arrays | (boolean) | `false` |
| `db_timeout` | Query timeout duration | Duration string | No timeout |

### Examples

```bash
# Pretty-printed response with timings
curl 'localhost:4001/db/query?pretty&timings&q=SELECT * FROM users'

# Associative format for easier parsing
curl 'localhost:4001/db/query?associative&q=SELECT * FROM users'

# Set 5-second timeout
curl 'localhost:4001/db/execute?db_timeout=5s' \
  -H "Content-Type: application/json" \
  -d '["SELECT * FROM large_table"]'
```

### Read Consistency Parameters

| Parameter | Description |
|-----------|-------------|
| `consistency=none` | Read from any node (fastest, may be stale) |
| `consistency=weak` | Read from follower with some freshness guarantee |
| `consistency=strong` | Read from leader (ensures up-to-date data) |

```bash
# Strong consistency read
curl 'localhost:4001/db/query?consistency=strong&q=SELECT * FROM users'
```

See [Read Consistency](07-read-consistency.md) for detailed guidance.

## Parameterized Statements

Prevent SQL injection using parameterized queries.

### Positional Parameters

```bash
# Write with parameters
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO users(name, email) VALUES(?, ?)", "Alice", "alice@example.com"]]'

# Read with parameters
curl -XPOST 'localhost:4001/db/query' \
  -H "Content-Type: application/json" \
  -d '[["SELECT * FROM users WHERE name=?", "Alice"]]'
```

### Named Parameters

```bash
# Write with named parameters
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO users(name, email) VALUES(:name, :email)", {"name": "Alice", "email": "alice@example.com"}]]'

# Read with named parameters
curl -XPOST 'localhost:4001/db/query' \
  -H "Content-Type: application/json" \
  -d '[["SELECT * FROM users WHERE name=:name", {"name": "Alice"}]]'
```

### Security Example

**Vulnerable (don't do this):**
```bash
# User input directly concatenated - SQL INJECTION VULNERABLE
username="Alice'; DROP TABLE users; --"
curl -XPOST 'localhost:4001/db/query' \
  -d "[\"SELECT * FROM users WHERE name='$username'\"]"
```

**Safe (use parameters):**
```bash
# Parameterized query - SAFE
curl -XPOST 'localhost:4001/db/query' \
  -H "Content-Type: application/json" \
  -d '[["SELECT * FROM users WHERE name=?", "Alice\''; DROP TABLE users; --"]]'
```

## Transactions

Execute multiple statements atomically:

```bash
curl -XPOST 'localhost:4001/db/execute?transaction' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO accounts(id, balance) VALUES(1, 1000)",
    "INSERT INTO accounts(id, balance) VALUES(2, 500)",
    "UPDATE accounts SET balance=balance-100 WHERE id=1",
    "UPDATE accounts SET balance=balance+100 WHERE id=2"
  ]'
```

**Behavior:**
- All statements succeed, or none are applied
- Processing stops at first error
- Much better performance than separate requests

## BLOB Data

### Writing BLOBs

```bash
# Using hex literal syntax
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '["INSERT INTO files(data) VALUES(x\'53514C697465\')"]'

# Using parameterized byte array
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO files(data) VALUES(?)", [83, 81, 76, 105, 116, 101]]]'
```

### Reading BLOBs

**Default (base64-encoded):**
```bash
curl 'localhost:4001/db/query?q=SELECT * FROM files'

# Response:
{
  "results": [{
    "columns": ["data"],
    "types": ["blob"],
    "values": [["U1FMaXRl"]]
  }]
}
```

**As byte arrays:**
```bash
curl 'localhost:4001/db/query?blob_array&q=SELECT * FROM files'

# Response:
{
  "results": [{
    "columns": ["data"],
    "types": ["blob"],
    "values": [[[83, 81, 76, 105, 116, 101]]]
  }]
}
```

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (check response for database errors) |
| 400 | Bad request (invalid JSON, unsupported operation) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 500 | Internal server error |
| 503 | Service unavailable (no leader, cluster issue) |

### Database Errors in Response

```json
{
  "results": [
    {
      "error": "near \"nonsense\": syntax error"
    }
  ],
  "time": 0.000123
}
```

**Always check:**
1. HTTP status code first
2. Response body for `error` key even on HTTP 200

## Backup and Restore API

### Create Backup

```bash
# Download SQLite database file
curl -s localhost:4001/db/backup -o backup.sqlite3

# Compressed backup
curl -s 'localhost:4001/db/backup?compress' -o backup.sqlite3.gz

# SQL dump format
curl -s 'localhost:4001/db/backup?fmt=sql' -o backup.sql

# Vacuum before backup
curl -s 'localhost:4001/db/backup?vacuum' -o backup.sqlite3

# Combined options
curl -s 'localhost:4001/db/backup?compress&vacuum' -o backup.sqlite3.gz
```

### Restore from Backup

```bash
# Upload SQLite database file
curl -XPOST localhost:4001/db/restore \
  --form db=@backup.sqlite3
```

**Note:** Restore requires exclusive access. Stop all nodes except one, restore to that node, then restart others with `-join`.

## Cluster Management API

### Get Node Status

```bash
curl localhost:4001/status
```

### Remove Node from Cluster

```bash
curl -XDELETE localhost:4001/db/cluster/remove \
  -d '{"id": "3"}'
```

## PRAGMA Directives

Safe to use (read-only):
```bash
curl 'localhost:4001/db/query?q=PRAGMA version'
curl 'localhost:4001/db/query?q=PRAGMA table_info(users)'
```

**Do NOT use** (interfere with rqlite operation):
- `PRAGMA journal_mode` - rqlite requires WAL mode
- `PRAGMA wal_checkpoint` - rqlite manages checkpoints
- `PRAGMA synchronous` - rqlite controls sync behavior

## Client Libraries

Official and community-maintained libraries are available:

- **Go**: `github.com/rqlite/gorqlite`
- **Python**: `rqlite-client`
- **JavaScript/Node.js**: `rqlite`
- **Java**: `rqlite-java`
- **Ruby**: `rqlite-rb`

See [Client Libraries](https://rqlite.io/docs/api/client-libraries/) for the complete list.

## Best Practices

1. **Use parameterized queries** to prevent SQL injection
2. **Batch writes in transactions** for better performance
3. **Choose appropriate consistency level** per query
4. **Handle errors gracefully** - check both HTTP status and response body
5. **Use associative format** for easier client-side parsing
6. **Set timeouts** for long-running queries
7. **Monitor response times** using `timings` parameter

## Next Steps

- Configure [backup strategies](05-backup-restore.md)
- Set up [read consistency](07-read-consistency.md) for your workload
- Enable [security](08-security.md) for production
- Optimize [performance](09-performance.md)
