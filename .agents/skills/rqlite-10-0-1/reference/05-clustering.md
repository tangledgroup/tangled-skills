# Clustering

## Why Cluster?

You do not need a cluster to use rqlite. A single-node system works well for networked SQLite access via HTTP. However, clustering provides **fault tolerance and high availability** — even if some nodes fail, the database remains online with minimal downtime and continuous access.

## Practical Cluster Size

For a cluster of N voting nodes to remain operational, at least `(N/2)+1` nodes must be up and running and in contact with each other.

| Cluster size (N) | Quorum | Fault tolerance |
| :---             | :----: | :----:          |
| 1                | 1      | 0 nodes         |
| 2                | 2      | 0 nodes         |
| 3                | 2      | 1 node          |
| 4                | 3      | 1 node          |
| 5                | 3      | 2 nodes         |

Clusters of 3, 5, 7, or 9 nodes are most practical. Even-numbered clusters offer no distinct advantage over the preceding odd number (e.g., a 4-node cluster tolerates the same 1 failure as a 3-node cluster).

**Read-only nodes** do not count towards N since they don't vote. You can add many read-only nodes for read scaling without affecting quorum.

The practical limit for voting nodes is about 11. Go bigger by adding read-only nodes.

## Creating a Cluster Manually

Start with one node as the initial leader on _host1_:

```bash
rqlited -node-id 1 -http-addr host1:4001 -raft-addr host1:4002 ~/node
```

`-http-addr` is the client-facing API port. `-raft-addr` is for inter-node Raft communication. Both must be reachable from other nodes.

Join a second node on _host2_:

```bash
rqlited -node-id 2 -http-addr host2:4001 -raft-addr host2:4002 -join host1:4002 ~/node
```

Join a third node on _host3_:

```bash
rqlited -node-id 3 -http-addr host3:4001 -raft-addr host3:4002 -join host1:4002 ~/node
```

You now have a fault-tolerant cluster that can tolerate the failure of any single node, including the leader.

### Key Notes

- `-node-id` can be any unique string. It should not change once chosen.
- If a node receives a join request and is not the Leader, it redirects the joining node to the Leader.
- You can specify multiple `-join` addresses; the node tries each until one succeeds.
- Cluster joins are idempotent — if a node attempts to join a cluster it's already in (same ID and Raft address), the Leader ignores the request.
- When simply restarting a node, there is no need to pass `-join` again.

### Listening on All Interfaces

Pass `0.0.0.0` to `-http-addr` and/or `-raft-addr`, but then set `-http-adv-addr` and `-raft-adv-addr` to the actual reachable address:

```bash
rqlited -node-id 1 -http-addr 0.0.0.0:4001 -http-adv-addr host1:4001 \
  -raft-addr 0.0.0.0:4002 -raft-adv-addr host1:4002 ~/node
```

### Through the Firewall

On networks like AWS EC2 where nodes have non-routable internal IPs, set `-http-adv-addr` and `-raft-adv-addr` to the routable address broadcast to other nodes.

## Growing a Cluster

Start a new node with a never-before-used node ID and have it join:

```bash
rqlited -node-id 4 -http-addr host4:4001 -raft-addr host4:4002 -join host1:4002 ~/node
```

The new node automatically picks up all changes since the cluster started.

## Removing or Replacing a Node

Via the rqlite CLI:

```
127.0.0.1:4001> .remove <node ID>
```

Or via HTTP API:

```bash
curl -XDELETE http://host:4001/remove -d '{"id": "<node ID>"}'
```

The cluster must be functional (have an operational Leader) for removal to succeed. If quorum is lost, bring back the failed node first.

### Automatic Removal on Shutdown

Pass `-raft-cluster-remove-shutdown=true` so a node removes itself from the cluster on graceful shutdown (e.g., receiving `SIGTERM`):

```bash
rqlited -node-id 1 -raft-cluster-remove-shutdown=true ~/node
```

### Automatically Reaping Failed Nodes

Set `-raft-reap-node-timeout` for voting nodes and `-raft-reap-read-only-node-timeout` for read-only nodes:

```bash
rqlited -node-id 1 -raft-reap-node-timeout=48h -raft-reap-read-only-node-timeout=30m data
```

**Must be set on every voting node.** Set conservatively to avoid reaping during normal network outages.

## Modifying a Node's Raft Address

Change the Raft address between restarts, but explicitly tell the node to re-join:

```bash
rqlited -node-id 1 -raft-addr newhost:4002 -join host2:4002 ~/node
```

The Leader removes the previous record and adds a new one. **Requires a quorum of other nodes running.** You cannot change all nodes' addresses simultaneously.

## Dealing with Failure

If an rqlite process crashes, simply restart it. The node picks up any changes that happened while offline.

### Recovering a Cluster That Has Permanently Lost Quorum

1. Stop all remaining nodes
2. In each node's data directory, inside `raft/`, create a `peers.json` file:

```json
[
  { "id": "1", "address": "10.1.0.1:4002", "non_voter": false },
  { "id": "2", "address": "10.1.0.2:4002", "non_voter": false }
]
```

3. Ensure the file is identical across all remaining nodes
4. Restart the cluster

Once recovery completes, `peers.json` is renamed to `peers.info`.

> The most robust disaster recovery approach: recover a **single** node first, then join new nodes to it. Alternatively, recover a single node and restore from backup.
