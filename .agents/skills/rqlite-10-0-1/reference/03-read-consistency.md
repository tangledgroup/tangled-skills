# Read Consistency

rqlite offers selectable read consistency levels: **weak** (default), **linearizable**, **strong**, **none**, and **auto**. Each trades off freshness against performance.

## Weak

_Weak_ is the default and almost certainly the right choice for most applications.

The node checks if it is the Leader locally, and if so reads its local SQLite database directly. If not the Leader, it transparently forwards the request to the Leader.

**Pros:** Usually very fast. In practice, inconsistency is unlikely to happen.

**Cons:** There is a small window (less than a second by default) during which a node may think it's the Leader but has actually been deposed. In that window, stale data may be returned. Technically, weak reads are not Linearizable.

```bash
curl -G 'localhost:4001/db/query?level=weak' --data-urlencode 'q=SELECT * FROM users'
```

## Linearizable

Linearizable reads implement the process from section 6.4 of the [Raft dissertation](https://raw.githubusercontent.com/ongardie/dissertation/refs/heads/master/online.pdf). Each read returns results of the latest committed write.

The Leader records the Raft Commit Index, heartbeats with Followers, waits for a quorum of responses, then waits until at least the recorded commit index is applied to SQLite before performing the read.

**Pros:** Guaranteed up-to-date reads. No chance of stale data.

**Cons:** Measurably slower than weak reads because the Leader contacts at least a quorum of nodes. Performance depends on network latency between nodes.

```bash
curl -G 'localhost:4001/db/query?level=linearizable' --data-urlencode 'q=SELECT * FROM users'

# With timeout
curl -G 'localhost:4001/db/query?level=linearizable&linearizable_timeout=1s' --data-urlencode 'q=SELECT * FROM users'
```

## None

With _none_, the node queries its local SQLite database without any Leadership or cluster-contact checks. The node could be completely disconnected from the cluster, but the query will still succeed.

**Pros:** Absolute fastest query response.

**Cons:** Risk of stale reads if the Leader changes or the node becomes disconnected.

```bash
curl -G 'localhost:4001/db/query?level=none' --data-urlencode 'q=SELECT * FROM users'
```

### Limiting Read Staleness with `freshness`

Set the `freshness` parameter to a Go duration string to limit how long the node may have been disconnected from the Leader:

```bash
# Succeed only if node heard from Leader within the last 1 second
curl -G 'localhost:4001/db/query?level=none&freshness=1s' --data-urlencode 'q=SELECT * FROM users'
```

**Important notes about `freshness`:**

- Always ignored if the node serving the query is the Leader
- Ignored for all consistency levels except `none`
- Ignores if set to zero
- Checks that the node has been in contact with the Leader, but does not guarantee the node is caught up with all changes

### `freshness_strict`

Add `freshness_strict` to also check that the most recently received data was appended by the Leader within the freshness interval. This works by comparing timestamps, so clock skew between nodes affects correctness:

```bash
curl -G 'localhost:4001/db/query?level=none&freshness=1s&freshness_strict' --data-urlencode 'q=SELECT * FROM users'
```

## Auto

_Auto_ is not an actual consistency level. Instead, the receiving node automatically selects the most sensible level for its type:

- Read-only (non-voting) nodes → `none` (with freshness check if set)
- Voting nodes → `weak` (freshness value ignored)

This simplifies clients that don't know ahead of time whether they're talking to a read-only or voting node:

```bash
curl -G 'localhost:4001/db/query?level=auto&freshness=1s' --data-urlencode 'q=SELECT * FROM users'
```

## Strong

_Strong_ consistency sends the query through the actual Raft log, ensuring all committed entries have been applied to SQLite at query time.

**Do not use in production.** Strong reads are costly, consume disk space, and offer no benefit over linearizable reads. They can be useful in specific testing scenarios.

```bash
curl -G 'localhost:4001/db/query?level=strong' --data-urlencode 'q=SELECT * FROM users'
```

## Which Should I Use?

- **Weak** — the default and right choice for most applications. Unless your cluster Leader is continually changing during writes, there will be no difference between weak and linearizable, but linearizable will result in slower queries.
- **Linearizable** — when you need guaranteed up-to-date reads. Use if your application requires strong consistency guarantees on reads.
- **None** — primarily for querying read-only nodes where you want to avoid forwarding to the Leader. Combine with `freshness` to bound staleness.
- **Auto** — when your client talks to both voting and read-only nodes and wants automatic level selection.
- **Strong** — only for testing. Use linearizable in production instead.

## Summary Table

| Level | Speed | Freshness Guarantee | Leader Check | Raft Log | Best For |
|-------|-------|---------------------|-------------|----------|----------|
| weak | Fast | Leader-local (may be slightly stale) | Yes | No | Default, most applications |
| linearizable | Moderate | Latest committed write | Yes (quorum) | No | Guaranteed up-to-date reads |
| none | Fastest | None (may be very stale) | No | No | Read-only nodes, edge reads |
| auto | Varies | Depends on node type | Auto | No | Mixed voting + read-only clients |
| strong | Slowest | All committed entries applied | Yes | Yes | Testing only |
