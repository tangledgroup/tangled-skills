# Read Consistency

Understanding and configuring read consistency levels in rqlite.

## Overview

rqlite provides tunable read consistency, allowing you to trade off data freshness for performance. This is particularly useful in distributed systems where different queries may have different consistency requirements.

## Consistency Levels

### None (Fastest, Potentially Stale)

Reads are served from the local node without checking if data is up-to-date with the leader.

**Use case:** Cache-like reads where stale data is acceptable.

```bash
# Via API
curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM users'

# Via shell
rqlite 127.0.0.1:4001
.consistency none
SELECT * FROM users
```

**Characteristics:**
- Fastest read performance
- May return stale data (milliseconds to seconds old)
- No coordination overhead
- Ideal for read-heavy workloads with tolerance for eventual consistency

### Weak (Balanced)

Reads attempt to get recent data but may accept slightly stale responses.

**Use case:** General-purpose reads where slight staleness is acceptable.

```bash
# Via API
curl 'localhost:4001/db/query?consistency=weak&q=SELECT * FROM users'

# Via shell
rqlite 127.0.0.1:4001
.consistency weak
SELECT * FROM users
```

**Characteristics:**
- Good balance of performance and freshness
- May read from followers with recent data
- Small coordination overhead
- Suitable for most application reads

### Strong (Most Fresh)

Reads are forwarded to the leader, ensuring the most up-to-date data.

**Use case:** Critical reads that must reflect all committed writes.

```bash
# Via API
curl 'localhost:4001/db/query?consistency=strong&q=SELECT * FROM users'

# Via shell
rqlite 127.0.0.1:4001
.consistency strong
SELECT * FROM users
```

**Characteristics:**
- Guarantees reading latest committed data
- Higher latency (must contact leader)
- More network overhead
- Required for financial transactions, inventory checks, etc.

## Choosing the Right Level

### Decision Framework

| Scenario | Recommended Level | Rationale |
|----------|-------------------|-----------|
| User profile display | `none` or `weak` | Stale data acceptable, performance important |
| Shopping cart | `strong` | Must see latest additions/removals |
| Product catalog | `weak` | Updates are infrequent, freshness nice-to-have |
| Inventory count | `strong` | Must prevent overselling |
| Analytics dashboard | `none` | Real-time accuracy not critical |
| Authentication/authorization | `strong` | Security-critical, must be current |
| Feed/timeline display | `weak` | Slight staleness acceptable for performance |
| Payment processing | `strong` | Financial transactions require latest state |

### Performance vs. Consistency Trade-off

```
Latency:     none < weak < strong
Freshness:   none < weak < strong
Throughput:  none > weak > strong
```

## Implementation Examples

### Per-Query Consistency (API)

```bash
# Fast read for non-critical data
curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM products'

# Strong read for critical data
curl 'localhost:4001/db/query?consistency=strong&q=SELECT balance FROM accounts WHERE id=123'
```

### Session-Level Consistency (Shell)

```bash
rqlite 127.0.0.1:4001

# Set consistency for entire session
.consistency weak

# All subsequent queries use this level
SELECT * FROM users
SELECT * FROM orders

# Change mid-session if needed
.consistency strong
SELECT balance FROM accounts

# Reset to default
.consistency none
```

### Application-Level Strategy (Pseudocode)

```python
class DatabaseClient:
    def read_non_critical(self, query):
        """For cache-like reads"""
        return self.query(query, consistency='none')
    
    def read_standard(self, query):
        """For general application reads"""
        return self.query(query, consistency='weak')
    
    def read_critical(self, query):
        """For transactions and security"""
        return self.query(query, consistency='strong')

# Usage examples
user = db.read_non_critical("SELECT * FROM users WHERE id=?", user_id)
products = db.read_standard("SELECT * FROM products")
balance = db.read_critical("SELECT balance FROM accounts WHERE id=?", account_id)
```

## Leader-Follower Architecture

### How Reads Work

**None consistency:**
```
Client → Follower (serves from local copy, no coordination)
```

**Weak consistency:**
```
Client → Follower (may check with leader for freshness)
         ↓
     Leader (optional verification)
```

**Strong consistency:**
```
Client → Follower (forwards to leader)
         ↓
     Leader (serves from authoritative copy)
         ↓
     Follower (returns to client)
```

### Impact on Cluster Load

- **None**: Reads distributed across all nodes, minimal leader load
- **Weak**: Most reads served locally, occasional leader checks
- **Strong**: All reads go through leader, can create bottleneck

## Monitoring Consistency Impact

### Check Current Settings

```bash
rqlite 127.0.0.1:4001
.status

# Look for read statistics
{
  "db": {
    "num_queries": 1523,
    "num_writes": 89
  }
}
```

### Measure Latency Differences

```bash
# Time a none-consistency read
time curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM large_table'

# Time a strong-consistency read
time curl 'localhost:4001/db/query?consistency=strong&q=SELECT * FROM large_table'
```

## Best Practices

### Default to Weak Consistency

Start with `weak` consistency for most reads, then optimize per-query:

```bash
# Set default in application
DEFAULT_CONSISTENCY = 'weak'

# Override for specific queries
user_count = query("SELECT COUNT(*) FROM users", consistency='none')
account_balance = query("SELECT balance FROM accounts...", consistency='strong')
```

### Use Strong Consistency for Writes-Followed-By-Reads

After a write, use strong consistency to ensure the read sees the write:

```python
def transfer_funds(from_account, to_account, amount):
    # Write operation
    execute("""
        BEGIN;
        UPDATE accounts SET balance = balance - ? WHERE id = ?;
        UPDATE accounts SET balance = balance + ? WHERE id = ?;
        COMMIT;
    """, (amount, from_account, amount, to_account))
    
    # Read with strong consistency to see the update
    new_balance = query(
        "SELECT balance FROM accounts WHERE id = ?", 
        consistency='strong',
        params=(from_account,)
    )
    return new_balance
```

### Avoid Strong Consistency for Bulk Reads

For reporting or analytics, use `none` consistency:

```bash
# Analytics query - stale data acceptable
curl 'localhost:4001/db/query?consistency=none&q=SELECT DATE(created), COUNT(*) FROM events GROUP BY DATE(created)'
```

### Test Your Consistency Choices

```bash
# Simulate cluster behavior
docker-compose up -d  # Start 3-node cluster

# Write to leader
curl -XPOST 'localhost:4001/db/execute' \
  -d '["INSERT INTO test(val) VALUES(1)"]'

# Read from different nodes with different consistency
curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM test'
curl 'localhost:4003/db/query?consistency=none&q=SELECT * FROM test'
curl 'localhost:4001/db/query?consistency=strong&q=SELECT * FROM test'
```

## Common Pitfalls

### Reading Your Own Writes

**Problem:** Write then immediately read with `none` consistency may not see the write.

**Solution:** Use `strong` consistency for the follow-up read, or wait for replication.

```python
# WRONG - may not see the insert
insert("INSERT INTO logs(msg) VALUES(?)", "Event occurred")
logs = query("SELECT * FROM logs WHERE msg=?", "Event occurred", consistency='none')  # May be empty!

# CORRECT - use strong consistency
insert("INSERT INTO logs(msg) VALUES(?)", "Event occurred")
logs = query("SELECT * FROM logs WHERE msg=?", "Event occurred", consistency='strong')  # Will see it
```

### Assuming All Nodes Have Same Data

**Problem:** With `none` or `weak` consistency, different nodes may return different results.

**Solution:** Be aware of this in your application logic, use strong consistency for critical decisions.

### Overusing Strong Consistency

**Problem:** Using `strong` for all reads creates leader bottleneck.

**Solution:** Profile your application and only use strong consistency where necessary.

## Next Steps

- Optimize [performance](09-performance.md) with appropriate consistency choices
- Set up [monitoring](10-monitoring.md) to track read patterns
- Configure [queued writes](https://rqlite.io/docs/api/queued-writes/) for high-write workloads
- Learn about [bulk API](https://rqlite.io/docs/api/bulk-api/) for efficient batch operations
