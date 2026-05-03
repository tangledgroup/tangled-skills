# Raft Client Interaction

## Contents
- Leader Discovery
- Linearizability and Idempotency
- Read-Only Operations
- Timing Requirements

## Leader Discovery

Clients send all requests to the leader. The interaction pattern:

1. **Initial connection**: client connects to a randomly-chosen server
2. **If not leader**: server rejects request and supplies information about the most recent leader it has heard from (AppendEntries requests include the leader's network address)
3. **Client retries** with the indicated leader
4. **If leader crashes**: client requests time out; client retries with randomly-chosen servers

This simple redirect pattern means clients don't need to know cluster topology — they discover the leader through failed attempts.

## Linearizability and Idempotency

Raft aims for **linearizable semantics**: each operation appears to execute instantaneously, exactly once, at some point between its invocation and its response.

### The duplicate execution problem

Without additional measures, Raft can execute a command multiple times:
- Leader crashes after committing the log entry but before responding to the client
- Client retries the command with a new leader
- The new leader executes it again

### Solution: unique serial numbers

1. **Client generates** a unique serial number for each request (client ID + request number)
2. **When retrying**, client reuses the original serial number
3. **Leader tracks** the latest serial number processed for each client, plus the associated response (stored persistently)
4. **On duplicate detection**, leader sends the old response without re-executing the request

This ensures exactly-once semantics even with retries and leader changes.

## Read-Only Operations

Read-only operations can be handled without writing to the log. However, this risks returning stale data if the responding leader has been superseded by a newer leader it doesn't know about.

### Two precautions for linearizable reads

1. **No-op entry at term start**: Each leader commits a blank no-op entry into the log at the start of its term. This ensures the leader knows which entries are committed (Leader Completeness Property guarantees the leader has all committed entries, but it may not know which ones at the start of its term).

2. **Deposition check before read**: Before processing a read-only request, the leader exchanges heartbeat messages with a majority of the cluster to verify it hasn't been deposed. If heartbeats succeed, the leader is still valid and can serve the read.

### Alternative: lease-based reads

Instead of checking for deposition on each read, the leader could rely on heartbeats to establish a form of **lease**. However, this relies on timing for safety (assumes bounded clock skew), which Raft avoids in its core protocol.

## Timing Requirements

Raft's safety does not depend on timing — it never produces incorrect results due to fast or slow events. However, **availability** depends critically on timing.

### The timing inequality

```
broadcastTime << electionTimeout << MTBF
```

| Parameter | Description | Typical range |
|-----------|-------------|---------------|
| `broadcastTime` | Average time to send RPCs in parallel to every server and receive responses | 0.5ms – 20ms |
| `electionTimeout` | Time a follower waits before starting an election | 10ms – 500ms |
| `MTBF` | Mean time between failures for a single server | Weeks to months |

- `broadcastTime` should be an order of magnitude less than `electionTimeout` so leaders can reliably send heartbeats and split votes are unlikely
- `electionTimeout` should be a few orders of magnitude less than `MTBF` so the system makes steady progress

### Recommended election timeout

**150–300ms** is recommended. Lower timeouts reduce downtime but risk unnecessary leader changes (leaders can't broadcast heartbeats before others start elections). Higher timeouts increase stability but increase unavailability after leader crashes.

### Measured performance

With a 5-server cluster and ~15ms broadcast time:
- Election timeout 150–300ms: reliable leader election, median downtime ~287ms
- Election timeout 12–24ms: average 35ms to elect, but violates timing requirement
- Without randomization in timeouts: consistently >10 seconds due to split votes
- With just 5ms of randomness: significant improvement (median 287ms)
