# Non-Deterministic Functions

How rqlite handles functions like RANDOM() and datetime functions in a distributed system.

## The Problem

rqlite uses **statement-based replication**: SQL statements are stored in the Raft log and applied to each node's SQLite database. This works fine for deterministic statements, but causes issues with non-deterministic functions:

```sql
-- Problem: Each node evaluates RANDOM() independently
INSERT INTO foo (n) VALUES(random());
```

**Result:** Different values on different nodes → Data divergence!

## rqlite's Solution

rqlite rewrites SQL statements containing non-deterministic functions **before** adding them to the Raft log. The leader node evaluates the function and replaces it with a literal value, ensuring all nodes apply the same statement.

### What Gets Rewritten?

#### RANDOM()

Any statement containing `RANDOM()` is rewritten when:
- It's part of a write request (`/db/execute`)
- It's part of a read request with **strong** consistency (`/db/query?level=strong`)
- The `norwrandom` parameter is NOT present

**Rewriting rules:**
- `RANDOM()` → Random integer between -9223372036854775808 and +9223372036854775807
- Evaluated by the node that first receives the request
- Same value replicated to all nodes

**Examples:**

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO foo(id, val) VALUES(1234, RANDOM())" ]'

# Rewritten to something like:
# INSERT INTO foo(id, val) VALUES(1234, 5789123456789012345)

# RANDOM() rewriting disabled
curl -XPOST 'localhost:4001/db/execute?norwrandom' \
  -d '[ "INSERT INTO foo(id, val) VALUES(1234, RANDOM())" ]'

# NOT rewritten (read without strong consistency)
curl -G 'localhost:4001/db/query' \
  --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'

# Rewritten (read with strong consistency)
curl -G 'localhost:4001/db/query?level=strong' \
  --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'
```

**Not rewritten:**
- `ORDER BY RANDOM()` - Used for randomization, not data storage
- Read queries without strong consistency
- Requests with `?norwrandom` parameter

#### RANDOMBLOB(N)

Similar to `RANDOM()`, but generates N random bytes:

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO bar(uuid) VALUES(hex(RANDOMBLOB(16)))" ]'

# Rewritten to something like:
# INSERT INTO bar(uuid) VALUES(hex(x'C3CF32746F0B10FD0D0E1F3AEC6D877B'))
```

**Use case:** Generating UUIDs or random identifiers

### Date and Time Functions

SQLite date/time functions with `'now'` are non-deterministic:

```sql
-- Problem: 'now' evaluated at execution time, differs per node
INSERT INTO datetime_text (d1) VALUES(datetime('now'));
```

**rqlite's solution:** Replaces `'now'` with the exact timestamp when the leader receives the request.

**Rewritten functions:**
- `datetime('now')`
- `date('now')`
- `time('now')`
- `unixepoch('now')`
- `julianday('now')`
- Any function using `'now'` modifier

**Examples:**

```bash
# Will be rewritten
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO events(timestamp) VALUES(unixepoch(\'now\'))" ]'

# Rewritten to something like:
# INSERT INTO events(timestamp) VALUES(unixepoch(1705312200))

# Rewriting disabled
curl -XPOST 'localhost:4001/db/execute?norwtime' \
  -d '[ "INSERT INTO events(timestamp) VALUES(unixepoch(\'now\'))" ]'

# Not rewritten (explicit timestamp is deterministic)
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO events(timestamp) VALUES(date(\'2024-01-15\'))" ]'
```

**Rewriting rules:**
- Only write requests and strong consistency reads
- Can be disabled with `?norwtime` parameter
- Deterministic timestamps (e.g., `'2024-01-15'`) not rewritten

### CURRENT_TIMESTAMP, CURRENT_TIME, CURRENT_DATE

These can be problematic as default values:

```sql
-- Problem: Different nodes may use different times
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  created_at DEFAULT CURRENT_TIMESTAMP
);
```

**Recommendation:** Avoid using `CURRENT_TIMESTAMP` as column defaults. Explicitly set timestamps in INSERT statements instead:

```sql
-- Better: Explicit timestamp
INSERT INTO events (id, created_at) 
VALUES (1, datetime('now'));  -- Will be rewritten by rqlite
```

## Testing Rewriting

Use the `/db/sql` endpoint to see how rqlite rewrites statements without executing them:

```bash
# Test RANDOM() rewriting
curl -XPOST 'localhost:4001/db/sql?pretty' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO foo(v) VALUES(RANDOM())",
    "INSERT INTO foo(v) VALUES(RANDOMBLOB(16))"
  ]'

# Response:
{
  "results": [
    {
      "original": "INSERT INTO foo(v) VALUES(RANDOM())",
      "rewritten": "INSERT INTO \"foo\" (\"v\") VALUES (5789123456789012345)"
    },
    {
      "original": "INSERT INTO foo(v) VALUES(RANDOMBLOB(16))",
      "rewritten": "INSERT INTO \"foo\" (\"v\") VALUES (x'C3CF32746F0B10FD0D0E1F3AEC6D877B')"
    }
  ]
}

# Test datetime rewriting
curl -G 'localhost:4001/db/sql?pretty' \
  --data-urlencode 'q=INSERT INTO foo(t) VALUES(datetime("now"))'

# Response:
{
  "results": [
    {
      "original": "INSERT INTO foo(t) VALUES(datetime(\"now\"))",
      "rewritten": "INSERT INTO \"foo\" (\"t\") VALUES (datetime(2460326.5))"
    }
  ]
}
```

## Best Practices

### Use Rewriting for Consistency

✅ **Do use rewriting** for:
- Generating unique IDs with `RANDOM()` or `RANDOMBLOB()`
- Timestamps with `datetime('now')`
- Any non-deterministic function in write statements

```bash
# Good: UUID generation
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO sessions(id, token) VALUES(hex(RANDOMBLOB(16)), ?)" ]'

# Good: Automatic timestamps
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO logs(message, created_at) VALUES(?, datetime(\'now\'))" ]'
```

### Disable Rewriting When Needed

❌ **Disable rewriting** when:
- You want true randomness on each node (rare)
- Testing replication behavior
- Using `ORDER BY RANDOM()` for shuffling

```bash
# Disable RANDOM() rewriting
curl -XPOST 'localhost:4001/db/execute?norwrandom' \
  -d '[ "SELECT RANDOM()" ]'

# Disable datetime rewriting
curl -XPOST 'localhost:4001/db/execute?norwtime' \
  -d '[ "SELECT datetime(\'now\')" ]'

# Disable both
curl -XPOST 'localhost:4001/db/execute?norwrandom&norwtime' \
  -d '[ "INSERT INTO foo(x, t) VALUES(RANDOM(), datetime(\'now\'))" ]'
```

### Avoid Problematic Patterns

❌ **Don't use:**
- `CURRENT_TIMESTAMP` as column defaults
- `ORDER BY RANDOM()` in INSERT SELECT statements
- Non-deterministic functions without rewriting in distributed context

```sql
-- Problematic: ORDER BY RANDOM() not rewritten
INSERT INTO sample (x) 
SELECT x FROM large_table ORDER BY RANDOM() LIMIT 10;

-- Better: Use application-level randomization
-- Or accept that results may differ slightly across nodes
```

### Use Strong Consistency for Reads

When reading with non-deterministic functions, use strong consistency:

```bash
# Weak consistency (not rewritten)
curl -G 'localhost:4001/db/query' \
  --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'

# Strong consistency (rewritten, consistent across nodes)
curl -G 'localhost:4001/db/query?level=strong' \
  --data-urlencode 'q=SELECT * FROM foo WHERE id = RANDOM()'
```

## Common Use Cases

### Generating UUIDs

```bash
# Insert with auto-generated UUID
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO sessions(user_id, session_token) VALUES(?, hex(RANDOMBLOB(16)))" ]'

# Result: Consistent UUID across all nodes
# sessions table:
# user_id | session_token
# 1       | A3F2B8C9D1E4F5A6B7C8D9E0F1A2B3C4
```

### Audit Logging with Timestamps

```bash
# Log action with automatic timestamp
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ 
    "INSERT INTO audit_log(user_id, action, timestamp) VALUES(?, ?, datetime(\'now\'))",
    123,
    \'user_login\'
  ]'

# All nodes see the same timestamp
```

### Rate Limiting Tokens

```bash
# Generate random token for rate limiting
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ 
    "INSERT INTO rate_limit(client_id, token, expires_at) VALUES(?, RANDOM(), datetime(\'now\', \'+1 hour\'))"
  ]'
```

## Troubleshooting

### Data Divergence

**Symptom:** Different data on different nodes

**Cause:** Non-deterministic function not rewritten

**Solution:**
- Check if using `?norwrandom` or `?norwtime` inadvertently
- Ensure write requests (not reads) for data-modifying statements
- Use `/db/sql` to verify rewriting occurs

### Unexpected Values

**Symptom:** RANDOM() or datetime values not what you expect

**Cause:** Rewriting happens at request receipt, not execution

**Solution:**
- Understand that value is fixed when leader receives request
- Use `/db/sql` to see exact rewritten statement
- Check node logs for rewriting details

### Performance Impact

**Symptom:** Slight performance degradation with rewriting

**Cause:** Statement parsing and rewriting adds overhead

**Impact:** Minimal (<1% typically)

**Solution:** Acceptable trade-off for data consistency

## Summary

| Function | Rewritten? | When | Disable With |
|----------|-----------|------|--------------|
| `RANDOM()` | ✅ Yes | Writes, strong reads | `?norwrandom` |
| `RANDOMBLOB(N)` | ✅ Yes | Writes, strong reads | `?norwrandom` |
| `datetime('now')` | ✅ Yes | Writes, strong reads | `?norwtime` |
| `date('now')` | ✅ Yes | Writes, strong reads | `?norwtime` |
| `unixepoch('now')` | ✅ Yes | Writes, strong reads | `?norwtime` |
| `ORDER BY RANDOM()` | ❌ No | - | - |
| Explicit timestamps | ❌ No | Already deterministic | - |

## Next Steps

- Use [Bulk API](13-bulk-api.md) for efficient batch operations with rewritten functions
- Configure [read consistency](07-read-consistency.md) appropriately
- Set up [monitoring](10-monitoring.md) to detect data divergence
- Review [FAQ](18-faq.md) for common questions about replication
