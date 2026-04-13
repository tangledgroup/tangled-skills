# Clustering

General principles for creating and managing rqlite clusters.

## Overview

rqlite uses the Raft consensus algorithm to provide fault tolerance and high availability. While single-node deployments work well for development, clustering is essential for production environments requiring resilience against node failures.

## Why Cluster?

- **Fault Tolerance**: Survive node failures without downtime
- **High Availability**: Always have a copy of data available
- **Data Safety**: Automatic replication prevents data loss
- **Read Scaling**: Add read-only nodes to handle more queries

## Cluster Fundamentals

### Quorum Requirements

For a cluster to remain operational, a majority of voting nodes must be available:

| Total Nodes | Minimum Required | Can Tolerate |
|-------------|------------------|--------------|
| 1 | 1 | 0 failures |
| 3 | 2 | 1 failure |
| 5 | 3 | 2 failures |
| 7 | 4 | 3 failures |

**Formula:** `(N / 2) + 1` nodes must be running and communicating.

### Recommended Cluster Sizes

- **Development**: 1 node (no fault tolerance)
- **Production**: 3 nodes (tolerates 1 failure) - **Most common**
- **High Availability**: 5 nodes (tolerates 2 failures)
- **Mission Critical**: 7 nodes (tolerates 3 failures)

**Note:** Always use odd numbers for voting nodes. Even-numbered clusters provide no additional fault tolerance but increase coordination overhead.

## Creating a Cluster

### Manual Cluster Creation

#### Step 1: Start the Bootstrap Node

```bash
# On host1 (first node, no -join flag)
rqlited -node-id=1 \
  -http-addr=host1.example.com:4001 \
  -raft-addr=host1.example.com:4002 \
  /var/lib/rqlite/node1
```

#### Step 2: Join Additional Nodes

```bash
# On host2 (join to bootstrap node's Raft address)
rqlite -node-id=2 \
  -http-addr=host2.example.com:4001 \
  -raft-addr=host2.example.com:4002 \
  -join=host1.example.com:4002 \
  /var/lib/rqlite/node2

# On host3 (join to any existing node)
rqlited -node-id=3 \
  -http-addr=host3.example.com:4001 \
  -raft-addr=host3.example.com:4002 \
  -join=host1.example.com:4002 \
  /var/lib/rqlite/node3
```

#### Step 3: Verify Cluster Status

```bash
rqlite host1.example.com:4001
.nodes

# Expected output:
1: api_addr: http://host1.example.com:4001 addr: host1.example.com:4002 voter: true reachable: true leader: true id: 1
2: api_addr: http://host2.example.com:4001 addr: host2.example.com:4002 voter: true reachable: true leader: false id: 2
3: api_addr: http://host3.example.com:4001 addr: host3.example.com:4002 voter: true reachable: true leader: false id: 3
```

### Node ID Guidelines

- Must be unique within the cluster
- Can be any string (numbers, hostnames, UUIDs)
- Should not change once assigned
- Common patterns: `1`, `host1`, `node-uuid-v4`

## Network Configuration

### Listening on All Interfaces

For containers or VMs where the IP may change:

```bash
rqlited -node-id=1 \
  -http-addr=0.0.0.0:4001 \
  -raft-addr=0.0.0.0:4002 \
  -http-adv-addr=host1.example.com:4001 \
  -raft-adv-addr=host1.example.com:4002 \
  /var/lib/rqlite/node1
```

**Important:** When binding to `0.0.0.0`, you must specify advertised addresses (`-http-adv-addr` and `-raft-adv-addr`) so other nodes can reach this node.

### NAT and Firewall Considerations

For nodes behind NAT or firewalls:

```bash
# Node with private IP but public address
rqlited -node-id=1 \
  -http-addr=0.0.0.0:4001 \
  -raft-addr=0.0.0.0:4002 \
  -http-adv-addr=public-ip.example.com:4001 \
  -raft-adv-addr=public-ip.example.com:4002 \
  /var/lib/rqlite/node1
```

### AWS EC2 Example

```bash
# Using private IPs for Raft, public for HTTP
rqlited -node-id=1 \
  -http-addr=0.0.0.0:4001 \
  -raft-addr=172.31.16.45:4002 \
  -http-adv-addr=ec2-12-34-56-78.us-east-1.compute.amazonaws.com:4001 \
  -raft-adv-addr=172.31.16.45:4002 \
  /var/lib/rqlite/node1
```

## Growing and Shrinking Clusters

### Adding Nodes

```bash
# Add a new node at any time
rqlited -node-id=4 \
  -http-addr=host4.example.com:4001 \
  -raft-addr=host4.example.com:4002 \
  -join=host1.example.com:4002 \
  /var/lib/rqlite/node4

# New node automatically receives all historical data
```

### Removing Nodes

**Via Shell:**
```bash
rqlite host1.example.com:4001
.remove 3
```

**Via API:**
```bash
curl -XDELETE http://host1.example.com:4001/db/cluster/remove \
  -d '{"id": "3"}'
```

**Important:** Only remove nodes that are permanently decommissioned. The cluster must have a quorum of remaining nodes.

### Automatic Removal on Shutdown

```bash
# Node removes itself when gracefully stopped
rqlited -node-id=1 \
  -raft-cluster-remove-shutdown=true \
  ...
```

## Read-Only Nodes

Read-only nodes replicate data but don't participate in consensus, allowing you to scale reads without affecting cluster quorum:

```bash
# Start a read-only node
rqlited -node-id=ro1 \
  -http-addr=readonly1.example.com:4001 \
  -raft-addr=readonly1.example.com:4002 \
  -join=host1.example.com:4002 \
  -raft-voter=false \
  /var/lib/rqlite/ro1
```

**Benefits:**
- Scale read capacity without consensus overhead
- Deploy in additional regions for lower latency
- Don't count toward quorum requirements

## Automatic Clustering

rqlite supports automatic cluster formation using discovery services:

### DNS-Based Discovery

```bash
# Nodes discover each other via DNS SRV records
rqlited -node-id=1 \
  -cluster-dns-domain=rqlite.example.com \
  -cluster-dns-srv=true \
  ...
```

### Consul Discovery

```bash
rqlited -node-id=1 \
  -cluster-addr=consul://consul.example.com/rqlite \
  ...
```

### etcd Discovery

```bash
rqlited -node-id=1 \
  -cluster-addr=etcd://etcd.example.com/rqlite \
  ...
```

See [Automatic Clustering](https://rqlite.io/docs/clustering/automatic-clustering/) for detailed configuration.

## Leader Election

### Understanding Leadership

- One node is the **Leader** (handles all writes)
- Other nodes are **Followers** (replicate data, serve reads)
- Leader election happens automatically on startup or leader failure
- Elections require quorum to succeed

### Checking Leader Status

```bash
rqlite host1.example.com:4001
.status

# Look for:
{
  "raft": {
    "leader_addr": "host1.example.com:4002",
    "state": "Leader"
  }
}
```

## Dealing with Failure

### Scenario 1: Single Node Failure (3-node cluster)

**Status:** Cluster remains operational with 2 nodes (quorum maintained)

**Action:** Replace failed node when possible
```bash
# Start replacement node with same ID
rqlited -node-id=2 ... -join=host1.example.com:4002
```

### Scenario 2: Multiple Node Failures (Lost Quorum)

**Status:** Cluster cannot elect leader, writes fail

**Recovery Steps:**
1. Start any single node without `-join` flag
2. This node becomes a single-node cluster
3. Restore data from backup if needed
4. Rebuild cluster by joining new nodes

```bash
# Emergency recovery - start single node
rqlited -node-id=1 /var/lib/rqlite/node1

# Restore from backup
rqlite host1.example.com:4001
.restore /path/to/backup.sqlite3

# Rebuild cluster
rqlited -node-id=2 ... -join=host1.example.com:4002
rqlited -node-id=3 ... -join=host1.example.com:4002
```

### Scenario 3: Split Brain Prevention

Raft prevents split-brain by requiring quorum. If network partitions:
- Partition with majority continues operating
- Partition without minority becomes read-only
- Reconnection automatically reconciles state

## Cluster Maintenance

### Rolling Updates

Update nodes one at a time to maintain availability:

```bash
# 1. Stop node 2
sudo systemctl stop rqlite2

# 2. Update binary
sudo mv /usr/local/bin/rqlited /usr/local/bin/rqlited.old
sudo cp rqlited-new /usr/local/bin/rqlited

# 3. Restart node 2
sudo systemctl start rqlite2

# 4. Verify node rejoined cluster
rqlite host1.example.com:4001
.nodes

# 5. Repeat for other nodes
```

### Monitoring Cluster Health

```bash
# Check all nodes status
for node in host1 host2 host3; do
  echo "=== $node ==="
  rqlite $node.example.com:4001 .status
done
```

## Best Practices

1. **Use 3+ nodes** for production fault tolerance
2. **Distribute across availability zones** to survive zone failures
3. **Monitor network latency** between nodes (<10ms recommended)
4. **Use persistent storage** to prevent data loss on restart
5. **Test failure scenarios** regularly in staging
6. **Keep node IDs stable** - don't change them between restarts
7. **Document cluster topology** for operational clarity

## Troubleshooting

### Node Won't Join Cluster

```bash
# Check network connectivity
telnet host1.example.com 4002

# Verify advertised addresses are correct
rqlite host1.example.com:4001 .nodes

# Check logs for error messages
journalctl -u rqlite -f
```

### Cluster Has No Leader

```bash
# Check if quorum is available
rqlite host1.example.com:4001 .nodes

# Verify network connectivity between all nodes
# Check firewall rules allow Raft port (default 4002)
```

### Write Fails with "not leader"

```bash
# Find current leader
rqlite host1.example.com:4001 .status

# Send writes to leader, or enable auto-redirect in client
```

## Next Steps

- Learn the [HTTP API](04-api.md) for application integration
- Set up [backups](05-backup-restore.md) for disaster recovery
- Configure [security](08-security.md) for production
- Optimize [performance](09-performance.md) for your workload
