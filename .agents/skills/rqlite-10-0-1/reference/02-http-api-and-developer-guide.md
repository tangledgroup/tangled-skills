# HTTP API Reference

## Endpoints

rqlite exposes three primary database endpoints:

### `/db/execute` — Write Operations

Execute one or more SQL statements that modify the database. Accepts POST requests with a JSON array of statements.

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' -H 'Content-Type: application/json' -d '[
    "CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, name TEXT)"
]'
```

Response:

```json
{
    "results": [
        {
            "last_insert_id": 0,
            "rows_affected": 0,
            "time": 0.000123456
        }
    ],
    "time": 0.001234567
}
```

### `/db/query` — Read Operations

Execute one or more read-only SQL queries. Supports both GET (single query via `q` parameter) and POST (multiple queries as JSON array).

```bash
# Single query via GET
curl -G 'localhost:4001/db/query?pretty' --data-urlencode 'q=SELECT * FROM users'

# Multiple queries via POST
curl -XPOST 'localhost:4001/db/query?pretty' -H 'Content-Type: application/json' -d '[
    "SELECT * FROM users",
    "SELECT count(*) FROM users"
]'
```

### `/db/request` — Unified Endpoint

The unified endpoint accepts both reads and writes in a single request. It supports transactions, associative responses, read consistency levels, and parameterized statements. **Does not support Queued Writes.**

```bash
curl -XPOST 'localhost:4001/db/request?pretty&timings&associative' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name, age) VALUES(?, ?)", "fiona", 20],
    ["INSERT INTO foo(name, age) VALUES(?, ?)", "declan", 30],
    ["SELECT * FROM foo"],
    ["SELECT * FROM bar"]
]'
```

Response with associative format:

```json
{
    "results": [
        { "last_insert_id": 1, "rows_affected": 1, "time": 0.000074612 },
        { "last_insert_id": 2, "rows_affected": 1, "time": 0.000044645 },
        {
            "types": { "age": "integer", "id": "integer", "name": "text" },
            "rows": [
                { "age": 20, "id": 1, "name": "fiona" },
                { "age": 30, "id": 2, "name": "declan" }
            ],
            "time": 0.000055248
        },
        { "error": "no such table: bar" }
    ],
    "time": 0.010571084
}
```

## Parameterized Statements

Use parameterized statements to prevent SQL injection. Each statement is an array where the first element is the SQL and subsequent elements are bind parameters:

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO users(name, age) VALUES(?, ?)", "fiona", 20],
    ["INSERT INTO users(name, age) VALUES(?, ?)", "sinead", 30]
]'
```

## Transactions

Set the `transaction` flag to wrap a bulk update in a transaction. If any statement fails, all changes are rolled back:

```bash
curl -XPOST 'localhost:4001/db/execute?pretty&transaction' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO users(name, age) VALUES(?, ?)", "alice", 25],
    ["INSERT INTO users(name, age) VALUES(?, ?)", "bob", 30]
]'
```

> **Note:** Explicit `BEGIN`, `COMMIT`, and `ROLLBACK` statements are unsupported. Use the `transaction` flag instead. If the node fails during an explicit transaction, the system may be left in a hard-to-use state.

## Associative Responses

Set the `associative` flag to receive rows as maps (column name → value) instead of arrays:

```bash
curl -G 'localhost:4001/db/query?pretty&associative' --data-urlencode 'q=SELECT * FROM users'
```

## Bulk Writes

The Bulk API allows multiple updates or queries in a single request. A bulk operation is contained within a single Raft log entry, minimizing round-trips between nodes.

```bash
# Non-parameterized bulk update
curl -XPOST 'localhost:4001/db/execute?pretty&timings' -H 'Content-Type: application/json' -d "[
    \"INSERT INTO foo(name) VALUES('fiona')\",
    \"INSERT INTO foo(name) VALUES('sinead')\"
]"

# Parameterized bulk update
curl -XPOST 'localhost:4001/db/execute?pretty&timings' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name) VALUES(?)", "fiona"],
    ["INSERT INTO foo(name) VALUES(?)", "sinead"]
]'
```

**Atomicity:** A bulk operation will never be interleaved with other requests because it is contained in a single Raft log entry and only one Raft entry is processed at a time.

## Queued Writes

Enable the `queue` parameter for higher write throughput by trading durability for performance. rqlite queues requests and batches them automatically:

```bash
curl -XPOST 'localhost:4001/db/execute?queue' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name) VALUES(?)", "fiona"]
]'
```

Response includes a monotonically-increasing `sequence_number` for tracking:

```json
{
    "results": [],
    "sequence_number": 1653314298877648934
}
```

Wait for the queue to flush with `wait`:

```bash
curl -XPOST 'localhost:4001/db/execute?queue&wait&timeout=10s' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name) VALUES(?)", "bob"]
]'
```

**Trade-offs:** Returns immediately after queuing but before Raft commit. Small risk of data loss if the node crashes before queued data is persisted.

## PRAGMA Directives

Issue `PRAGMA` directives through the API. Informational PRAGMAs are safe:

```bash
curl -G 'localhost:4001/db/query?pretty&timings' --data-urlencode 'q=PRAGMA foreign_keys'
```

**Prohibited PRAGMAs** (rqlite will return an error):

- `PRAGMA journal_mode` — rqlite requires WAL mode at all times
- `PRAGMA wal_checkpoint` — rqlite requires exclusive control over the WAL
- `PRAGMA wal_autocheckpoint=N` — same as above
- `PRAGMA synchronous=N` — don't change how rqlite manages disk writes

## Technical Details

### Request Forwarding

All write requests must be serviced by the cluster Leader. If a client sends a write to a Follower, the Follower transparently forwards it to the Leader and returns the response. Queries are also forwarded by default, depending on [read consistency level](reference/03-read-consistency.md).

### Request Forwarding Timeouts

Default timeout for forwarded requests is 30 seconds. Control with `timeout` parameter:

```bash
curl -XPOST 'localhost:4001/db/execute?timeout=2m' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name, age) VALUES(?, ?)", "fiona", 20]
]'
```

### Disabling Request Forwarding

Add `redirect` to the URL as a query parameter. If a Follower receives a request that must go to the Leader, it responds with HTTP 301 and includes the Leader's address in the `Location` header.

### Tracking Raft Indexes

Set `raft_index` as a URL parameter to learn which Raft log index a write was written into:

```bash
curl -XPOST 'localhost:4001/db/execute?raft_index' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO foo(name, age) VALUES(?, ?)", "fiona", 20]
]'
```

Response includes `"raft_index": 6`.

### Retries

Set `retries=N` to have a node automatically retry communication with other nodes:

```bash
curl -G 'localhost:4001/db/query?retries=2' --data-urlencode 'q=SELECT * FROM users'
```
