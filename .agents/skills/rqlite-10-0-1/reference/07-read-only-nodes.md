# Read-Only Nodes

rqlite supports adding _read-only nodes_ (also called non-voting nodes) to a cluster. These nodes increase read scalability without affecting Raft consensus.

> An rqlite node can serve thousands of queries per second using the default read consistency level. Don't add read-only nodes unless you are sure you need them.

## Purpose and Benefits

Read-only nodes are especially useful:

- At the network edge, where the link between edge and voting nodes is slow or unreliable
- For scaling out read traffic without adding consensus overhead
- In different geographic regions for lower-latency access
- As distributed copies of reference data that must stay in sync

A failed read-only node does not prevent the cluster from processing write requests.

## How Read-Only Nodes Work

- Read-only nodes do **not** participate in Raft consensus
- They do **not** count towards quorum
- They do **not** vote in Leader elections
- They **do** receive the Leader's stream of writes and apply them to their local SQLite database

## Enabling Read-Only Mode

Pass `-raft-non-voter=true` to `rqlited`:

```bash
rqlited -node-id reader1 -http-addr edge-host:4001 -raft-addr edge-host:4002 \
  -raft-non-voter=true -join host1:4002 ~/node
```

## Querying a Read-Only Node

A read request to a read-only node **must** use a [read consistency level](reference/03-read-consistency.md) of `none` or `auto`. If any other level is specified (or if no level is set), the node transparently forwards the request to the Leader, negating the benefits of using a read-only node.

```bash
# Use none with freshness to bound staleness
curl -G 'localhost:4001/db/query?level=none&freshness=5s' --data-urlencode 'q=SELECT * FROM config'

# Or use auto for automatic level selection
curl -G 'localhost:4001/db/query?level=auto&freshness=5s' --data-urlencode 'q=SELECT * FROM config'
```

The [`freshness`](reference/03-read-consistency.md#limiting-read-staleness-with-freshness) parameter ensures the read-only node hasn't been disconnected from the cluster for too long.

## Read-Only Node Management

Read-only nodes join and are removed using the [same operations as voting nodes](reference/05-clustering.md).

### Handling Failure

If a read-only node becomes unreachable, the Leader periodically attempts to reconnect. Since read-only nodes don't vote, a failed read-only node does not prevent the cluster from processing writes.

Use `-raft-reap-read-only-node-timeout` to automatically remove non-reachable read-only nodes after a specified duration:

```bash
rqlited -node-id 1 -raft-reap-read-only-node-timeout=30m data
```

## Automatic Clustering Compatibility

Read-only nodes are fully compatible with DNS-based, Consul-based, and etcd-based [automatic clustering](reference/06-automatic-clustering.md) methods. However, read-only nodes **cannot** bootstrap a cluster. Setting `-bootstrap-expect` to a non-zero value on a read-only node will cause `rqlited` to terminate with an error.
