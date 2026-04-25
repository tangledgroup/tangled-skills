# Queued Writes

Trading durability for performance with asynchronous write queuing.

## Overview

Queued Writes allow rqlite to accept write requests and process them asynchronously, providing significantly higher write throughput at the cost of immediate durability guarantees.

**Key characteristics:**
- Write requests return immediately after being queued
- rqlite automatically batches queued writes
- Higher throughput than synchronous writes
- Small risk of data loss if node crashes before flush
- Configurable batch size and timeout

## How It Works

### Normal Writes (Synchronous)

```
Client → Request → Leader → Raft Log → Replicate → Apply → Response
                                           ↑
                                    Waits for consensus
```

### Queued Writes (Asynchronous)

```
Client → Request → Queue → [Batch] → Leader → Raft Log → Replicate → Apply
         ↑                                             (later, in batches)
   Immediate response with sequence number
```

## Usage

### Basic Example

```bash
# Enable queued writes with ?queue parameter
curl -XPOST 'localhost:4001/db/execute?queue' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO events(type, value) VALUES(?, ?)", "click", 1]]'

# Response includes sequence number (not execution results)
{
  "results": [],
  "sequence_number": 1653314298877648934
}
```

### Multiple Queued Writes

```bash
# First request
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO logs(msg) VALUES(?)", "Event 1"]]'
# {"results": [], "sequence_number": 100}

# Second request
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO logs(msg) VALUES(?)", "Event 2"]]'
# {"results": [], "sequence_number": 101}

# Third request
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO logs(msg) VALUES(?)", "Event 3"]]'
# {"results": [], "sequence_number": 102}
```

rqlite will batch these and execute them together once the queue threshold is reached or timeout expires.

### Waiting for Queue Flush

Force wait until queued writes are persisted:

```bash
curl -XPOST 'localhost:4001/db/execute?queue&wait' \
  -d '[["INSERT INTO critical_data(value) VALUES(?)", 42]]'

# With timeout (default 30s)
curl -XPOST 'localhost:4001/db/execute?queue&wait&timeout=10s' \
  -d '[["INSERT INTO data(value) VALUES(?)", 42]]'
```

If queue doesn't flush within timeout, request returns error.

## Configuration

### Runtime Parameters

Queued writes can be configured at startup:

```bash
rqlited -node-id=1 \
  -write-queue-size=1024 \
  -write-queue-tmo=100ms \
  -write-queue-tx \
  /var/lib/rqlite/node1
```

**Flags:**
- `-write-queue-size`: Minimum requests before flush (default: varies)
- `-write-queue-tmo`: Maximum wait time before flush (default: 100ms)
- `-write-queue-tx`: Execute queued writes in transaction (default: false)

### Default Behavior

Without explicit configuration:
- Queue flushes when size threshold reached
- Or when timeout expires (whichever comes first)
- Writes not executed in transaction by default
- Sequence numbers track request ordering

## Sequence Numbers

Each queued write receives a monotonically increasing sequence number:

```bash
# Check latest persisted sequence number
curl localhost:4001/status | jq '.sequence_number'

# Example output
{
  "sequence_number": 1653314298877649973,
  "raft": {
    "leader_addr": "localhost:4002",
    "state": "Leader"
  }
}
```

**Important:**
- Sequence numbers are **local to each node**
- Different nodes have independent sequence number spaces
- Use to track when requests are persisted to Raft log
- Not guaranteed to be contiguous (gaps possible)

## Trade-offs

### Advantages

✅ **Much higher write throughput** - Can handle 10x+ more writes/sec  
✅ **Lower latency** - Immediate response without waiting for consensus  
✅ **Automatic batching** - No client-side batching required  
✅ **Configurable durability** - Tune batch size/timeout for your needs  

### Disadvantages

⚠️ **Data loss risk** - Unflushed queue lost on crash  
⚠️ **No execution results** - Can't see SQL errors immediately  
⚠️ **Ordering not guaranteed** - Batches may reorder statements  
⚠️ **Not for critical data** - Use synchronous writes for important data  

### Durability Window

The risk window is the time between:
1. Request queued and response sent
2. Queue flushed to Raft log

**Minimize risk by:**
- Reducing `-write-queue-tmo` (faster flushes)
- Reducing `-write-queue-size` (smaller batches)
- Using `&wait` parameter for critical writes
- Monitoring queue depth via `/status`

## Use Cases

### High-Volume Event Logging

```bash
# Perfect for events where occasional loss is acceptable
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO analytics(event_type, data) VALUES(?, ?)", "page_view", "{\"page\": \"/home\"}"]]'

# Can handle thousands of events/sec
```

### Metrics Collection

```bash
# Collect system metrics with high throughput
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO metrics(metric, value, timestamp) VALUES(?, ?, ?)", "cpu_usage", 45.2, strftime('%s', 'now')]]'
```

### Session Tracking

```bash
# Track user sessions (loss of some updates acceptable)
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["UPDATE sessions SET last_activity = ? WHERE session_id = ?", strftime('%s', 'now'), 'sess_123"]]'
```

### NOT Suitable For

❌ **Financial transactions** - Use synchronous writes  
❌ **User authentication data** - Use synchronous writes  
❌ **Inventory counts** - Use synchronous writes  
❌ **Any data where loss is unacceptable** - Use synchronous writes  

## Monitoring

### Check Queue Status

```bash
curl localhost:4001/status | jq '.write_queue'

# Example output
{
  "write_queue": {
    "size": 42,
    "sequence_number": 1653314298877649973,
    "last_flush": "2024-01-15T10:30:00Z"
  }
}
```

### Monitor Queue Depth

Set up alerts for queue depth:
- Warning: Queue size > 1000
- Critical: Queue size > 10000
- Indicates backlog or performance issue

### Track Sequence Numbers

Verify writes are being flushed:
```bash
# Get sequence number from queued write response
SEQ_NUM=$(curl -s -XPOST 'localhost:4001/db/execute?queue' \
  -d '[["INSERT INTO test(val) VALUES(1)]]' | jq '.sequence_number')

# Check if persisted
PERSISTED=$(curl -s localhost:4001/status | jq '.sequence_number')

if [ "$PERSISTED" -ge "$SEQ_NUM" ]; then
  echo "Write persisted"
else
  echo "Write still in queue"
fi
```

## Best Practices

### Hybrid Approach

Use both synchronous and queued writes:

```python
def log_event(event_type, data, critical=False):
    if critical:
        # Synchronous for critical events
        execute("INSERT INTO events(type, data) VALUES(?, ?)", 
                (event_type, data))
    else:
        # Queued for non-critical events
        execute_queue("INSERT INTO events(type, data) VALUES(?, ?)", 
                     (event_type, data))

# Usage
log_event("purchase", {"amount": 99.99}, critical=True)   # Synchronous
log_event("page_view", {"page": "/home"}, critical=False) # Queued
```

### Batch Critical Writes

Even for critical data, batch when possible:

```bash
# Instead of individual queued writes
for i in {1..100}; do
  curl -XPOST 'localhost:4001/db/execute?queue' \
    -d "[[\"INSERT INTO logs(msg) VALUES(?)\", \"Event $i\"]]"
done

# Better: single bulk queued write
curl -XPOST 'localhost:4001/db/execute?queue' \
  -d '[
    ["INSERT INTO logs(msg) VALUES(?)", "Event 1"],
    ["INSERT INTO logs(msg) VALUES(?)", "Event 2"],
    ...
  ]'
```

### Use Wait for Checkpoints

Periodically ensure data is flushed:

```bash
# After batch of queued writes, force flush
curl -XPOST 'localhost:4001/db/execute?queue&wait' \
  -d '[["UPDATE checkpoint SET last_flush = ? WHERE id = 1", strftime(\'%s\', \'now\')]]'
```

### Monitor and Alert

```bash
# Check queue health periodically
QUEUE_SIZE=$(curl -s localhost:4001/status | jq '.write_queue.size')

if [ "$QUEUE_SIZE" -gt 1000 ]; then
  echo "WARNING: Queue depth $QUEUE_SIZE"
  # Send alert, scale up, etc.
fi
```

## Configuration Examples

### High Throughput (Accept Higher Risk)

```bash
rqlited -node-id=1 \
  -write-queue-size=4096 \
  -write-queue-tmo=500ms \
  /var/lib/rqlite/node1
```

**Use case:** Analytics, logging where some loss acceptable

### Balanced (Moderate Risk)

```bash
rqlited -node-id=1 \
  -write-queue-size=1024 \
  -write-queue-tmo=100ms \
  /var/lib/rqlite/node1
```

**Use case:** General event tracking with occasional loss tolerance

### Low Risk (Near-Synchronous)

```bash
rqlited -node-id=1 \
  -write-queue-size=64 \
  -write-queue-tmo=10ms \
  -write-queue-tx \
  /var/lib/rqlite/node1
```

**Use case:** Important data where you want batching but minimal risk

## Troubleshooting

### Queue Not Flushing

**Symptoms:** Queue size growing, sequence number not advancing

**Causes:**
- Leader election in progress
- Disk full or I/O issues
- Network partition

**Solutions:**
- Check cluster status: `curl localhost:4001/status`
- Verify disk space: `df -h`
- Reduce queue size to force faster flushes

### High Queue Depth

**Symptoms:** Queue consistently > 1000 items

**Causes:**
- Write rate exceeds flush capacity
- Network latency too high
- Disk I/O bottleneck

**Solutions:**
- Increase flush frequency (reduce timeout)
- Scale vertically (faster disk/network)
- Reduce write rate or add more nodes

### Data Loss After Crash

**Prevention:**
- Use appropriate queue configuration for your durability needs
- Critical data should use synchronous writes
- Monitor queue depth and sequence numbers
- Implement application-level idempotency

**Recovery:**
- Accept that some queued data may be lost
- Re-send from client if possible (idempotent operations)
- Restore from backup if significant loss

## Next Steps

- Compare with [Bulk API](13-bulk-api.md) for synchronous batching
- Configure [performance tuning](09-performance.md) for queued writes
- Set up [monitoring](10-monitoring.md) for queue metrics
- Understand [non-deterministic functions](15-non-deterministic.md) with queued writes
