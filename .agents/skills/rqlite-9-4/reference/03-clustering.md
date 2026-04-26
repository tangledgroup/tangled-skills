# Clustering

## Why Cluster?

You do not need a cluster to use rqlite. A single-node system works well for networked SQLite access via HTTP. However, clustering provides fault tolerance and high availability — even if some nodes fail, the database remains online.

## Quorum Requirements

rqlite uses Raft consensus, requiring a majority of voting nodes to be online:

- 3 nodes → tolerates 1 failure
- 5 nodes → tolerates 2 failures
- 7 nodes → tolerates 3 failures

Clusters with even numbers of nodes are not recommended — they provide no additional fault tolerance over the next smaller odd number.

## Manual Cluster Creation

### Step 1: Start the Leader

```bash
rqlited -node-id=1 -http-addr host1:4001 -raft-addr host1:4002 data1/
```

The node listens on port `4001` for HTTP API requests and `4002` for Raft inter-node communication.

### Step 2: Join Additional Nodes

```bash
# On host2
rqlited -node-id=2 -http-addr host2:4001 -raft-addr host2:4002 -join host1:4002 data2/

# On host3
rqlited -node-id=3 -http-addr host3:4001 -raft-addr host3:4002 -join host1:4002 data3/
```

A node can join by contacting any cluster member — if the contacted node is not the Leader, it redirects the joining node. You can specify multiple `-join` addresses for redundancy.

### Listening on All Interfaces

When binding to `0.0.0.0`, you must set advertised addresses:

```bash
rqlited -node-id=1 \
  -http-addr 0.0.0.0:4001 -http-adv-addr host1:4001 \
  -raft-addr 0.0.0.0:4002 -raft-adv-addr host1:4002 \
  data/
```

This is also required when nodes are behind firewalls or NAT (e.g., AWS EC2 security groups).

## Automatic Clustering

All auto-clustering methods are **idempotent** — if a node is already part of a cluster, the auto-clustering flags are ignored. This simplifies automation since you can use the same startup command for initial bootstrap and adding new nodes.

### Automatic Bootstrapping

Start all nodes simultaneously with `-bootstrap-expect`:

```bash
# Node 1
rqlited -node-id=1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data1/

# Node 2 (same -join and -bootstrap-expect values)
rqlited -node-id=2 -http-addr=$HOST2:4001 -raft-addr=$HOST2:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data2/

# Node 3
rqlited -node-id=3 -http-addr=$HOST3:4001 -raft-addr=$HOST3:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data3/
```

All nodes must have identical `-bootstrap-expect` and `-join` values. The first node to detect enough peers bootstraps the cluster; others become Followers.

### DNS-Based Discovery

Create DNS A records for a hostname pointing to each node's IP:

```bash
rqlited -node-id=1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -disco-mode=dns -disco-config='{"name":"rqlite.cluster"}' \
  -bootstrap-expect=3 data/
```

For DNS SRV records (allows different ports per node):

```bash
rqlited -node-id=$ID -http-addr=$HOST:4001 -raft-addr=$HOST:4002 \
  -disco-mode=dns-srv \
  -disco-config='{"name":"rqlite.local","service":"rqlite-raft"}' \
  -bootstrap-expect=3 data/
```

Resolves `_rqlite-raft._tcp.rqlite.local`.

### Consul Discovery

```bash
rqlited -node-id=$ID -http-addr=$HOST:4001 -raft-addr=$HOST:4002 \
  -disco-key=rqlite1 -disco-mode=consul-kv \
  -disco-config='{"address":"example.com:8500"}' data/
```

The `-disco-key` allows multiple rqlite clusters to share one Consul instance.

### etcd Discovery

```bash
rqlited -node-id=$ID -http-addr=$HOST:4001 -raft-addr=$HOST:4002 \
  -disco-key=rqlite1 -disco-mode=etcd-kv \
  -disco-config='{"endpoints":["example.com:2379"]}' data/
```

## Read-Only Nodes

Read-only (non-voting) nodes scale out read capacity without affecting Raft quorum. They receive the full write stream from the Leader but do not vote in elections.

Enable with `-raft-non-voter=true`:

```bash
rqlited -node-id=ro1 -http-addr edge-host:4001 -raft-addr edge-host:4002 \
  -raft-non-voter=true -join host1:4002 data/
```

Query read-only nodes with `level=none` or `level=auto` to avoid forwarding to the Leader:

```bash
curl -G 'edge-host:4001/db/query?level=none&freshness=1s' \
  --data-urlencode 'q=SELECT * FROM users'
```

Read-only nodes are compatible with all automatic clustering methods but cannot bootstrap a cluster (setting `-bootstrap-expect` on a read-only node causes it to exit with an error).

## Growing and Shrinking Clusters

### Adding Nodes

Start a new node with a never-before-used `-node-id` and have it join:

```bash
rqlited -node-id=4 -http-addr host4:4001 -raft-addr host4:4002 \
  -join host1:4002 data4/
```

The new node automatically receives all historical changes.

### Removing Nodes

Via CLI:

```
127.0.0.1:4001> .remove <node ID>
```

Via API:

```bash
curl -XDELETE http://host:4001/remove -d '{"id": "<node ID>"}'
```

### Auto-Remove on Shutdown

Enable graceful self-removal:

```bash
rqlited -raft-cluster-remove-shutdown=true data/
```

On `SIGTERM`, the node contacts the Leader to remove itself before shutting down.

### Auto-Reap Failed Nodes

Automatically remove unreachable nodes after a timeout:

```bash
rqlited -raft-reap-node-timeout=48h \
  -raft-reap-read-only-node-timeout=30m data/
```

Set conservatively — too aggressive reaping can remove temporarily unreachable nodes. Must be set on every voting node.

## Changing Node Addresses

To change a node's Raft address, restart with the new address and explicitly pass `-join` again. The Leader will remove the old record before adding the new one. You cannot change all nodes' addresses simultaneously — always maintain a quorum during changes.

## Failure Recovery

### Single Node Failure

Simply restart the failed node. It automatically catches up with the cluster.

### Loss of Quorum

If too many nodes fail and quorum is lost, partial recovery is possible from remaining nodes' data. This may commit uncommitted Raft log entries or lose some committed data. The recovery process is documented in the [official guide](https://rqlite.io/docs/clustering/general-guidelines/#dealing-with-failure).

Key principle: bring back enough nodes to restore quorum, then perform recovery operations. If insufficient nodes can be recovered, manual intervention with on-disk Raft data is required.
