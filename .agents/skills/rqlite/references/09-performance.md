# Performance

Performance tuning and optimization for rqlite deployments.

## Overview

rqlite prioritizes data consistency and high availability over raw write throughput. Understanding this trade-off and optimizing for your specific workload is key to achieving good performance.

## Architecture Considerations

### Write Path

All writes go through Raft consensus:
```
Client → Leader → Raft Log → Replicate to Followers → Apply to SQLite
```

**Implications:**
- Write latency includes network round-trips to majority of nodes
- Single point of serialization (leader)
- Cannot scale writes by adding more voting nodes

### Read Path

Reads can be served from any node:
```
Client → Any Node → Local SQLite (with optional leader coordination)
```

**Implications:**
- Reads can be scaled horizontally
- Consistency level affects latency
- Read-only nodes don't affect consensus

## Performance Optimization Strategies

### 1. Batch Writes in Transactions

Execute multiple statements atomically for better throughput:

```bash
# Slow: Individual writes
for i in {1..100}; do
  curl -XPOST 'localhost:4001/db/execute' \
    -d "[\"INSERT INTO logs(msg) VALUES('Event $i')\"]"
done

# Fast: Batched transaction
curl -XPOST 'localhost:4001/db/execute?transaction' \
  -H "Content-Type: application/json" \
  -d @<(seq 1 100 | sed 's/.*/INSERT INTO logs(msg) VALUES(Event &)/' | jq -R . | jq -s .)
```

**Performance improvement:** 5-10x faster for bulk inserts.

### 2. Use Appropriate Read Consistency

Choose consistency level based on requirements:

```bash
# Fastest (may be stale)
curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM cache_table'

# Balanced (good for most reads)
curl 'localhost:4001/db/query?consistency=weak&q=SELECT * FROM products'

# Most fresh (higher latency)
curl 'localhost:4001/db/query?consistency=strong&q=SELECT balance FROM accounts'
```

**Latency comparison:** `none` < `weak` < `strong`

### 3. Add Read-Only Nodes

Scale reads without affecting consensus:

```bash
# Start read-only node
rqlited -node-id=ro1 \
  -join=leader:4002 \
  -raft-voter=false \
  /var/lib/rqlite/ro1
```

**Benefits:**
- Handle more read traffic
- Deploy in additional regions for lower latency
- Don't count toward quorum requirements

### 4. Index Frequently Queried Columns

Use SQLite indexes for faster lookups:

```bash
# Create indexes on query columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_events_created ON events(created DESC);

# Check existing indexes
rqlite 127.0.0.1:4001 ".indexes"

# Analyze table for query optimization
ANALYZE;
```

### 5. Use Queued Writes for Non-Critical Data

For workloads where occasional data loss is acceptable:

```bash
# Enable queued writes mode
rqlited -node-id=1 \
  -queued-writes \
  /var/lib/rqlite/node1

# Write with queue (higher throughput, eventual durability)
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO metrics(value) VALUES(?)", 42]]'
```

**Trade-off:** Higher write throughput but potential data loss on crash.

See [Queued Writes](https://rqlite.io/docs/api/queued-writes/) for details.

### 6. Optimize Network Latency

Raft performance is sensitive to network latency:

**Recommendations:**
- Keep nodes in same datacenter (<10ms latency)
- Use dedicated network interfaces for Raft traffic
- Avoid NAT when possible
- Monitor network metrics continuously

**Impact:**
- 10ms latency: ~100-200 writes/sec
- 50ms latency: ~20-50 writes/sec
- 100ms+ latency: Significant performance degradation

### 7. Use Badger for Raft Storage

Badger LSM tree can outperform BoltDB for Raft log:

```bash
rqlited -node-id=1 \
  -raft-badger \
  /var/lib/rqlite/node1
```

**Benefits:**
- Better write performance for Raft log
- Lower latency for consensus operations
- More efficient disk usage

## Workload-Specific Optimization

### Read-Heavy Workloads

```yaml
# Optimal cluster configuration
- 3 voting nodes (for fault tolerance)
- 5+ read-only nodes (for read scaling)
- Consistency level: weak or none for most reads
- CDN/cache layer in front of frequently-read data
```

**Example:**
```bash
# Use weak consistency for catalog reads
curl 'localhost:4001/db/query?consistency=weak&q=SELECT * FROM products'

# Add read-only nodes in multiple regions
rqlited -node-id=ro-us-east -join=leader:4002 -raft-voter=false
rqlited -node-id=ro-eu-west -join=leader:4002 -raft-voter=false
```

### Write-Heavy Workloads

```yaml
# Optimal cluster configuration
- 3 voting nodes (minimum for fault tolerance)
- Batch writes in transactions
- Use queued writes for non-critical data
- Consider write-ahead logging at application level
```

**Example:**
```bash
# Batch inserts in transaction
curl -XPOST 'localhost:4001/db/execute?transaction' \
  -d '[
    "INSERT INTO events(type, data) VALUES("click", ?)",
    "INSERT INTO events(type, data) VALUES("scroll", ?)",
    "INSERT INTO events(type, data) VALUES("view", ?)"
  ]'
```

### Mixed Workloads

```yaml
# Optimal cluster configuration
- 3-5 voting nodes (balance fault tolerance and performance)
- Separate read-only nodes for analytics/reporting
- Use appropriate consistency per query type
- Implement application-level caching
```

## Monitoring Performance

### Key Metrics to Track

```bash
# Check node status
curl localhost:4001/status

# Monitor from shell
rqlite 127.0.0.1:4001 ".status"
```

**Important metrics:**
- `raft.leader_addr`: Verify leader is stable
- `raft.state`: Should be "Leader" or "Follower" (not "Candidate")
- `db.num_queries`, `db.num_writes`: Track operation counts
- Response times: Monitor via application logs

### Latency Measurements

```bash
# Measure query latency
time curl -G 'localhost:4001/db/query?timings&q=SELECT * FROM users'

# Measure write latency
time curl -XPOST 'localhost:4001/db/execute?timings' \
  -d '[["INSERT INTO logs(msg) VALUES("test")"]]'
```

### Load Testing

```bash
# Simple load test with parallel requests
for i in {1..10}; do
  curl -XPOST 'localhost:4001/db/execute' \
    -d "[\"INSERT INTO test(val) VALUES($i)\"]" &
done
wait

# Use specialized tools
wrk -t12 -c400 -d30s \
  --post '["SELECT 1"]' \
  --header "Content-Type: application/json" \
  http://localhost:4001/db/query
```

## Common Performance Issues

### High Write Latency

**Symptoms:** Writes taking >100ms

**Causes and Solutions:**
1. **Network latency**: Move nodes closer together
2. **Disk I/O bottleneck**: Use SSDs, check disk utilization
3. **Leader overload**: Add read-only nodes, optimize queries
4. **Large transactions**: Break into smaller batches

### Read Performance Degradation

**Symptoms:** Slow SELECT queries

**Causes and Solutions:**
1. **Missing indexes**: Add indexes on query columns
2. **Strong consistency overuse**: Use weak/none where appropriate
3. **Complex queries**: Simplify or pre-compute results
4. **No read scaling**: Add read-only nodes

### Cluster Instability

**Symptoms:** Frequent leader elections

**Causes and Solutions:**
1. **Network partitions**: Improve network reliability
2. **Resource constraints**: Increase CPU/memory
3. **Slow disk**: Upgrade to faster storage
4. **Clock skew**: Ensure NTP synchronization

## Benchmarking

### Basic Performance Test

```bash
# Create test table
curl -XPOST 'localhost:4001/db/execute' \
  -d '["CREATE TABLE benchmark (id INTEGER PRIMARY KEY, data TEXT)"]'

# Insert 1000 rows (batched)
seq 1 1000 | xargs -I{} curl -XPOST 'localhost:4001/db/execute?transaction' \
  -d "[\"INSERT INTO benchmark(data) VALUES('data-{}')\"]"

# Query performance
time for i in {1..100}; do
  curl -G 'localhost:4001/db/query?q=SELECT * FROM benchmark WHERE id BETWEEN 1 AND 100' > /dev/null
done
```

### Using rqbench (if available)

```bash
# Run built-in benchmark
rqbench -n localhost:4001 -w 1000 -r 10000

# Parameters:
# -n: Node address
# -w: Number of writes
# -r: Number of reads
```

## Hardware Recommendations

### Minimum (Development)
- CPU: 2 cores
- Memory: 2 GB
- Disk: SSD, 10 GB free
- Network: 1 Gbps

### Production (3-node cluster)
- CPU: 4+ cores per node
- Memory: 8+ GB per node
- Disk: NVMe SSD, sized for database + WAL
- Network: 1+ Gbps, low latency between nodes

### High-Performance
- CPU: 8+ cores per node
- Memory: 16+ GB per node
- Disk: Enterprise NVMe with RAID
- Network: 10 Gbps, dedicated Raft network

## Next Steps

- Set up [monitoring](10-monitoring.md) for performance metrics
- Configure [backup strategies](05-backup-restore.md) that don't impact performance
- Implement [CDC](11-cdc.md) for real-time analytics without load on primary
- Use [extensions](12-extensions.md) to offload complex computations
