# Non-Deterministic Functions

rqlite performs _statement-based replication_, meaning every SQL statement is stored in the Raft log exactly as received. Each node then reads the log and applies the statements to its local SQLite copy. If a statement contains a non-deterministic function, this could result in different data on each node.

## How rqlite Solves This

rqlite rewrites received SQL statements containing certain non-deterministic functions before writing them to the Raft log. The rewritten statement is then applied to SQLite as usual, ensuring all nodes produce identical results.

## RANDOM()

Any SQL statement containing [`RANDOM()`](https://www.sqlite.org/lang_corefunc.html#random) is rewritten following these rules:

- The statement is part of a write-request (sent to `/db/execute`)
- The statement is part of a read-request (sent to `/db/query`) **with _strong_ read consistency**
- If `RANDOM()` is used as an `ORDER BY` qualifier, it is **not** rewritten
  - Example: `INSERT INTO foo (x) SELECT x FROM bar ORDER BY RANDOM()` — not rewritten, may produce different data on each node
- The HTTP request does not have the query parameter `norwrandom` present

`RANDOM()` is replaced with a random integer between -9223372036854775808 and +9223372036854775807.

### Examples

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '[
    "INSERT INTO foo(id, age) VALUES(1234, RANDOM())"
]'

# RANDOM() rewriting explicitly disabled
curl -XPOST 'localhost:4001/db/execute?norwrandom' -H 'Content-Type: application/json' -d '[
    "INSERT INTO foo(id, age) VALUES(1234, RANDOM())"
]'

# Not rewritten (read-request without strong consistency)
curl -G 'localhost:4001/db/query' --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'

# Rewritten (strong consistency)
curl -G 'localhost:4001/db/query?level=strong' --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'
```

## RANDOMBLOB(N)

Any statement containing [`RANDOMBLOB(N)`](https://www.sqlite.org/lang_corefunc.html#randomblob) follows the same rules as `RANDOM()`, except it is replaced by a literal blob value containing N random bytes:

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '[
    "INSERT INTO bar(uuid) VALUES(hex(RANDOMBLOB(16)))"
]'
```

## Date and Time Functions

SQLite date and time functions with `now` are non-deterministic because `now` is evaluated at the moment of execution. rqlite rewrites these by replacing `now` with the current time at the moment the node receives the request:

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '[
    "INSERT INTO datetime_text (d1) VALUES(datetime('now'))"
]'

# Not rewritten (rewriting explicitly disabled)
curl -XPOST 'localhost:4001/db/execute?norwtime' -H 'Content-Type: application/json' -d '[
    "INSERT INTO datetime_text (d1) VALUES(datetime('now'))"
]'

# Not rewritten (deterministic — uses a fixed date)
curl -XPOST 'localhost:4001/db/execute' -H 'Content-Type: application/json' -d '[
    "INSERT INTO datetime_text (d1) VALUES(date('2020-01-01'))"
]'
```

> Like RANDOM(), only write requests and queries with _Strong_ read consistency are rewritten.

## CURRENT_TIMESTAMP, CURRENT_TIME, CURRENT_DATE

Using `CURRENT_TIMESTAMP`, `CURRENT_TIME`, or `CURRENT_DATE` as a default column value can produce different values on different nodes unless the column is explicitly set by the writing system. To avoid this, avoid using default timestamps and explicitly set them in row data when writing to rqlite.

## Testing Rewrites

Examine how rqlite rewrites SQL statements without making any changes to the database by sending statements to `/db/sql`:

```bash
curl -XPOST 'localhost:4001/db/sql?pretty' -H 'Content-Type: application/json' -d '[
    "INSERT INTO foo(v) VALUES(RANDOM())",
    "INSERT INTO foo(v) VALUES(RANDOMBLOB(16))"
]'
```

Response:

```json
{
    "results": [
        {
            "original": "INSERT INTO foo(v) VALUES(RANDOM())",
            "rewritten": "INSERT INTO \"foo\" (\"v\") VALUES (954556320032354600)"
        },
        {
            "original": "INSERT INTO foo(v) VALUES(RANDOMBLOB(16))",
            "rewritten": "INSERT INTO \"foo\" (\"v\") VALUES (x'C3CF32746F0B10FD0D0E1F3AEC6D877B')"
        }
    ]
}
```

Date/time rewriting:

```bash
curl -G 'localhost:4001/db/sql?pretty' --data-urlencode 'q=INSERT INTO foo(t) VALUES(datetime("now"))'
```

Response:

```json
{
    "results": [
        {
            "original": "INSERT INTO foo(t) VALUES(datetime(\"now\"))",
            "rewritten": "INSERT INTO \"foo\" (\"t\") VALUES (datetime(2461077.945987))"
        }
    ]
}
```
