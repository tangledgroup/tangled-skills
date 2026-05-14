# HTTP API Reference

## Endpoints

rqlite exposes three primary database endpoints:

- **`/db/execute`** — write requests (`INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`). POST only.
- **`/db/query`** — read-only requests (`SELECT`). GET or POST. Attempts to modify data return an error.
- **`/db/request`** — unified endpoint accepting both reads and writes. Response format depends on the request type.

Use `/db/execute` or `/db/query` when you know the request type ahead of time for predictable responses. Use `/db/request` for convenience when mixing reads and writes.

All requests can be sent to any node in the cluster. Followers transparently forward write requests to the Leader.

## Common URL Parameters

- `pretty` — pretty-print JSON responses
- `timings` — include execution time in response
- `transaction` — execute multiple statements atomically within a transaction
- `associative` — return query results as array of maps (column name → value) instead of parallel arrays
- `blob_array` — return BLOB data as byte arrays instead of base64 strings
- `level` — read consistency level (`weak`, `linearizable`, `strong`, `none`, `auto`)
- `queue` — enable queued writes mode for higher throughput

## Writing Data

### Single Statement

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '["CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, name TEXT)"]'
```

Response:

```json
{
    "results": [{
        "last_insert_id": 0,
        "rows_affected": 0,
        "time": 0.001
    }],
    "time": 0.002
}
```

### Plain Text Format

For quick prototyping (not recommended for production):

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: text/plain' \
  -d 'CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, name TEXT)'
```

## Parameterized Statements

Always use parameterized statements to prevent SQL injection. Two formats are supported:

### Positional Parameters

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '[["INSERT INTO users(name) VALUES(?)", "fiona"]]'
```

### Named Parameters

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '[["INSERT INTO users(name) VALUES(:name)", {"name": "fiona"}]]'
```

Parameterized queries work the same way:

```bash
curl -XPOST 'localhost:4001/db/query?pretty' \
  -H 'Content-Type: application/json' \
  -d '[["SELECT * FROM users WHERE name=?", "fiona"]]'
```

## Transactions

Add `transaction` to the URL to execute multiple statements atomically. If any statement fails, the entire batch is rolled back:

```bash
curl -XPOST 'localhost:4001/db/execute?pretty&transaction' \
  -H 'Content-Type: application/json' \
  -d '[
    "INSERT INTO users(name) VALUES(\"fiona\")",
    "INSERT INTO users(name) VALUES(\"sinead\")"
  ]'
```

Transactions provide much better performance for bulk INSERT/UPDATE operations. Do not use explicit `BEGIN`, `COMMIT`, or `ROLLBACK` — their behavior in a cluster is undefined. Control transactions only through the `transaction` URL parameter.

## Bulk Writes

Execute multiple statements in a single request for significantly higher throughput:

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '[
    ["INSERT INTO users(name) VALUES(?)", "fiona"],
    ["INSERT INTO users(name) VALUES(?)", "sinead"]
  ]'
```

A bulk operation is contained within a single Raft log entry, so round-trips between nodes are minimized. Combine with `transaction` for atomicity.

## Queued Writes

For maximum write throughput when ultimate durability is not critical, use queued writes:

```bash
curl -XPOST 'localhost:4001/db/execute?queue' \
  -H 'Content-Type: application/json' \
  -d '[["INSERT INTO users(name) VALUES(?)", "fiona"]]'
```

Response includes a `sequence_number` to track when the request is persisted:

```json
{
    "results": [],
    "sequence_number": 1653314298877648934
}
```

rqlite batches queued requests internally and executes them as a bulk operation. Check `/status` to see the latest persisted sequence number.

Wait for the queue to flush with `wait`:

```bash
curl -XPOST 'localhost:4001/db/execute?queue&wait&timeout=10s' \
  -H 'Content-Type: application/json' \
  -d '[["INSERT INTO users(name) VALUES(?)", "bob"]]'
```

Trade-offs: data loss is possible if the node crashes before queued data is persisted. The `HTTP 200 OK` response only confirms the request was queued, not that it was applied.

## Querying Data

### GET Request (Single Query)

```bash
curl -G 'localhost:4001/db/query?pretty' \
  --data-urlencode 'q=SELECT * FROM users'
```

Default response format:

```json
{
    "results": [{
        "columns": ["id", "name"],
        "types": ["integer", "text"],
        "values": [[1, "fiona"]],
        "time": 0.001
    }],
    "time": 0.002
}
```

### POST Request (Multiple Queries)

```bash
curl -XPOST 'localhost:4001/db/query?pretty' \
  -H 'Content-Type: application/json' \
  -d '["SELECT * FROM users", "SELECT count(*) FROM users"]'
```

### Associative Response

Add `associative` to get rows as maps:

```bash
curl -G 'localhost:4001/db/query?pretty&associative' \
  --data-urlencode 'q=SELECT * FROM users'
```

```json
{
    "results": [{
        "types": {"id": "integer", "name": "text"},
        "rows": [{"id": 1, "name": "fiona"}],
        "time": 0.001
    }]
}
```

## BLOB Data

Write BLOBs using hex literals or byte arrays:

```bash
# Hex literal
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '["INSERT INTO blobs(data) VALUES(x'"'"'53514C697465'"'"')"]'

# Byte array via parameterized statement
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '[["INSERT INTO blobs(data) VALUES(?)", [83,81,76,105,116,101]]]'
```

BLOBs are returned as base64-encoded strings by default. Use `blob_array` to get byte arrays:

```bash
curl -G 'localhost:4001/db/query?pretty&blob_array' \
  --data-urlencode 'q=SELECT * FROM blobs'
```

## Read Consistency Levels

- **`weak`** (default) — node checks if it is the Leader locally and reads its database. Fast, slight chance of stale data during leader transitions.
- **`linearizable`** — Leader contacts a quorum to confirm leadership before reading. Guarantees up-to-date results, slightly slower.
- **`none`** — no leader check at all. Fastest possible read, but data may be stale or from a disconnected node. Use with `freshness` parameter to bound staleness.
- **`strong`** — query goes through the Raft log. Guarantees all committed entries are applied before reading. Slow, not recommended for production.
- **`auto`** — automatically selects `none` for read-only nodes, `weak` for voting nodes.

Freshness controls for `none` consistency:

```bash
# Fail if node hasn't heard from leader in 1 second
curl -G 'localhost:4001/db/query?level=none&freshness=1s' \
  --data-urlencode 'q=SELECT * FROM users'

# Also verify data is not stale by the freshness interval
curl -G 'localhost:4001/db/query?level=none&freshness=1s&freshness_strict' \
  --data-urlencode 'q=SELECT * FROM users'
```

## Non-Deterministic Functions

rqlite rewrites `RANDOM()`, `RANDOMBLOB(N)`, and date/time functions containing `'now'` before writing to the Raft log, ensuring all nodes produce identical results. This rewriting applies to write requests and queries with `strong` consistency.

Disable rewriting per-request:

```bash
# Disable RANDOM() rewriting
curl -XPOST 'localhost:4001/db/execute?norwrandom' \
  -H 'Content-Type: application/json' \
  -d '["INSERT INTO foo(n) VALUES(RANDOM())"]'

# Disable time function rewriting
curl -XPOST 'localhost:4001/db/execute?norwtime' \
  -H 'Content-Type: application/json' \
  -d "['INSERT INTO t(d) VALUES(datetime('now'))']"
```

Avoid using `CURRENT_TIMESTAMP`, `CURRENT_TIME`, or `CURRENT_DATE` as column defaults — they produce different values on different nodes unless explicitly set in the row data.

## Client Libraries

Official and community-maintained libraries are available:

- **Go**: [rqlite-go-http](https://github.com/rqlite/rqlite-go-http) (thin), [gorqlite](https://github.com/rqlite/gorqlite) (richer)
- **Python**: [pyrqlite](https://github.com/rqlite/pyrqlite), [sqlalchemy-rqlite](https://github.com/rqlite/sqlalchemy-rqlite)
- **Java**: [rqlite-java-http](https://github.com/rqlite/rqlite-java-http), [rqlite-jdbc](https://github.com/rqlite/rqlite-jdbc)
- **Rust**: [rqlite](https://docs.rs/rqlite/latest/rqlite)
- **JavaScript**: [rqlite-js](https://github.com/rqlite/rqlite-js)
- **TypeScript**: [knex-rqlite](https://github.com/rqlite/knex-rqlite)
- **C#**: [rqlite-dotnet](https://github.com/rqlite/rqlite-dotnet)
- **PHP**: [rqlite-php](https://github.com/karlomikus/rqlite-php)

## Connecting to a Cluster

Four common strategies:

1. **Static list with round-robin** — configure client with fixed node addresses, cycle through them
2. **DNS-based discovery** — use a DNS name resolving to all node IPs (Kubernetes headless Service works well)
3. **Load balancer** — place HAProxy, nginx, or cloud LB in front of nodes using `/readyz` as health check
4. **Node discovery via API** — connect to one known node, query `/nodes?ver=2` to discover full cluster membership

Because rqlite transparently forwards requests to the Leader, any basic strategy works correctly without leader-aware routing.
