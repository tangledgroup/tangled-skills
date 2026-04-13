# Bulk API

Executing multiple operations in a single request for improved performance.

## Overview

The Bulk API allows you to execute multiple SQL statements in a single HTTP request. This reduces network round-trips and improves throughput, especially for write-heavy workloads.

**Key benefits:**
- Reduced network overhead (single request instead of many)
- All operations contained in single Raft log entry
- Better throughput for batch operations
- Atomic execution when combined with transactions

## Bulk Writes

### Non-Parameterized Example

```bash
curl -XPOST 'localhost:4001/db/execute?pretty&timings' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO users(name) VALUES(\"Alice\")",
    "INSERT INTO users(name) VALUES(\"Bob\")",
    "INSERT INTO users(name) VALUES(\"Charlie\")"
  ]'

# Response:
{
  "results": [
    {
      "last_insert_id": 1,
      "rows_affected": 1,
      "time": 0.00759015
    },
    {
      "last_insert_id": 2,
      "rows_affected": 1,
      "time": 0.00669015
    },
    {
      "last_insert_id": 3,
      "rows_affected": 1,
      "time": 0.00543210
    }
  ],
  "time": 0.869015
}
```

### Parameterized Example

```bash
curl -XPOST 'localhost:4001/db/execute?pretty&timings' \
  -H "Content-Type: application/json" \
  -d '[
    ["INSERT INTO users(name, email) VALUES(?, ?)", "Alice", "alice@example.com"],
    ["INSERT INTO users(name, email) VALUES(?, ?)", "Bob", "bob@example.com"],
    ["INSERT INTO users(name, email) VALUES(?, ?)", "Charlie", "charlie@example.com"]
  ]'
```

### Named Parameters

```bash
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H "Content-Type: application/json" \
  -d '[
    ["INSERT INTO users(name, email) VALUES(:name, :email)", {"name": "Alice", "email": "alice@example.com"}],
    ["INSERT INTO users(name, email) VALUES(:name, :email)", {"name": "Bob", "email": "bob@example.com"}]
  ]'
```

## Bulk Reads

Execute multiple queries in a single request:

```bash
curl -XPOST 'localhost:4001/db/query?pretty' \
  -H "Content-Type: application/json" \
  -d '[
    "SELECT * FROM users",
    "SELECT COUNT(*) FROM orders",
    "SELECT * FROM products WHERE price < 100"
  ]'

# Response includes results for all queries
{
  "results": [
    {
      "columns": ["id", "name"],
      "types": ["integer", "text"],
      "values": [[1, "Alice"], [2, "Bob"]]
    },
    {
      "columns": ["COUNT(*)"],
      "types": ["integer"],
      "values": [[42]]
    },
    {
      "columns": ["id", "name", "price"],
      "types": ["integer", "text", "real"],
      "values": [[1, "Widget", 9.99], [2, "Gadget", 49.99]]
    }
  ]
}
```

## Transaction Support

Combine bulk operations with transactions for atomicity:

```bash
curl -XPOST 'localhost:4001/db/execute?transaction&pretty' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO accounts(id, balance) VALUES(1, 1000)",
    "INSERT INTO accounts(id, balance) VALUES(2, 500)",
    "UPDATE accounts SET balance = balance - 100 WHERE id = 1",
    "UPDATE accounts SET balance = balance + 100 WHERE id = 2"
  ]'
```

**Behavior:**
- All statements succeed or all are rolled back
- Processing stops at first error
- Much better performance than separate requests

## Important Notes

### Parameterized vs Non-Parameterized

You **cannot mix** parameterized and non-parameterized statements in a single bulk request:

```bash
# WRONG - will fail
[
  "INSERT INTO users(name) VALUES(\"Alice\")",
  ["INSERT INTO users(name) VALUES(?)", "Bob"]
]

# CORRECT - all parameterized
[
  ["INSERT INTO users(name) VALUES(?)", "Alice"],
  ["INSERT INTO users(name) VALUES(?)", "Bob"]
]

# CORRECT - all non-parameterized
[
  "INSERT INTO users(name) VALUES(\"Alice\")",
  "INSERT INTO users(name) VALUES(\"Bob\")"
]
```

### Atomicity

Bulk operations are contained within a single Raft log entry:
- Never interleaved with other requests
- All-or-nothing execution (with transaction flag)
- Consistent across all cluster nodes

### Performance Comparison

| Approach | Requests | Latency | Throughput |
|----------|----------|---------|------------|
| Individual writes | N | High | Low |
| Bulk write | 1 | Low | High |
| Queued writes | N (async) | Very Low | Very High |

## Use Cases

### Data Migration

```bash
# Migrate data in batches
for batch in {1..100}; do
  start=$((batch * 1000))
  end=$(((batch + 1) * 1000))
  
  curl -XPOST 'localhost:4001/db/execute?transaction' \
    -H "Content-Type: application/json" \
    -d "$(generate_bulk_insert $start $end)"
done
```

### Event Logging

```bash
# Batch log events
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[
    ["INSERT INTO events(type, data) VALUES(?, ?)", "click", "{\"element\": \"button\"}"],
    ["INSERT INTO events(type, data) VALUES(?, ?)", "scroll", "{\"position\": 500}"],
    ["INSERT INTO events(type, data) VALUES(?, ?)", "view", "{\"page\": \"/home\"}"]
  ]'
```

### Bulk Updates

```bash
# Update multiple records
curl -XPOST 'localhost:4001/db/execute?transaction' \
  -H "Content-Type: application/json" \
  -d '[
    "UPDATE products SET price = price * 1.1 WHERE category = \"electronics\"",
    "UPDATE products SET price = price * 1.05 WHERE category = \"clothing\"",
    "UPDATE products SET price = price * 1.08 WHERE category = \"food\""
  ]'
```

## Alternatives

### Queued Writes

For even higher throughput with acceptable durability trade-offs:

```bash
# Queue writes for async processing
curl -XPOST 'localhost:4001/db/execute?queue' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO logs(msg) VALUES(?)", "Event 1"]]'
```

See [Queued Writes](14-queued-writes.md) for details.

### Restore from Dump

For very large datasets, consider restoring from SQL dump:

```bash
# Generate SQL dump
sqlite3 source.db .dump > migration.sql

# Restore to rqlite
curl -XPOST localhost:4001/db/restore \
  --form db=@migration.sql
```

## Troubleshooting

### Request Too Large

If bulk request exceeds size limits:
- Split into smaller batches (100-1000 statements)
- Use queued writes for continuous streaming
- Consider restore from dump for initial data load

### Partial Failures

With transactions enabled:
- All statements succeed or all fail
- Check response for error details
- Review which statement caused failure

Without transactions:
- Some statements may succeed before failure
- Check individual result entries for errors
- Implement application-level rollback if needed

## Next Steps

- Use [Queued Writes](14-queued-writes.md) for maximum write throughput
- Configure [performance optimizations](09-performance.md) for bulk operations
- Set up [monitoring](10-monitoring.md) to track bulk operation latency
- Learn about [non-deterministic functions](15-non-deterministic.md) in bulk context
