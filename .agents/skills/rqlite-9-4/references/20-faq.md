# FAQ

Frequently asked questions about rqlite.

## General Questions

### What exactly does rqlite do?

rqlite replicates data written via SQL across multiple nodes for fault tolerance and high availability. It uses the Raft Consensus Protocol to ensure all copies of the data remain consistent, with one node (the Leader) serving as the authoritative source.

**Key benefits:**
- Data replicated automatically across nodes
- Survives node failures without data loss
- Strong consistency guarantees
- Simple SQL interface via HTTP API

### When should I use rqlite?

Use rqlite when you need:
- ✅ Fault-tolerant, highly-available relational database
- ✅ Simple deployment and operations
- ✅ SQLite compatibility with distribution
- ✅ Edge/IoT deployments with local storage
- ✅ Read-intensive workloads with global distribution

Don't use rqlite for:
- ❌ Write-scaling needs (all writes go through leader)
- ❌ Extremely high write throughput requirements
- ❌ Complex transaction needs beyond atomic batches

### Why use rqlite versus other distributed databases?

**Advantages:**
- **Simplicity:** Single binary, no external dependencies
- **Ease of deployment:** Form cluster in seconds
- **SQLite compatibility:** Full SQL support, familiar interface
- **Lightweight:** Minimal resource requirements
- **Complete control:** You own the infrastructure and data

**Trade-offs:**
- Lower write throughput than specialized systems
- No horizontal write scaling
- Best for moderate workloads prioritizing simplicity

### Is rqlite a drop-in replacement for SQLite?

**No.** While rqlite uses SQLite as its storage engine:
- All writes must go through HTTP API
- Cannot modify database file directly
- Some SQLite features behave differently in distributed context

However, applications using SQLite may require minimal changes to work with rqlite's HTTP API.

## Access and Usage

### How do I access the database?

**Primary method:** HTTP API
```bash
curl -XPOST 'localhost:4001/db/execute' \
  -d '[ "INSERT INTO users(name) VALUES(\"Alice\")" ]'
```

**Alternative methods:**
- rqlite shell (CLI tool)
- Client libraries (Go, Python, JavaScript, etc.)
- Third-party UI applications

See [HTTP API](04-api.md) and [rqlite Shell](02-shell.md) for details.

### Can I run a single node?

**Yes.** Many users run single-node rqlite for:
- Development and testing
- Simple deployments where HA not required
- Networked SQLite access via HTTP

```bash
rqlited -node-id=1 /var/lib/rqlite
```

**Note:** Single node = no fault tolerance. If it fails, you must restart it.

### Can any node execute write requests?

**Yes.** You can send writes to any node:
- If node is Leader: Processes directly
- If node is Follower: Forwards to Leader transparently
- Client doesn't need to know which node is Leader

**Under the hood:** Only Leader actually modifies database, but forwarding is automatic.

### Can I send read requests to any node?

**Yes.** Read behavior depends on consistency level:
- **None/Weak:** Served by local node (fast, may be stale)
- **Strong:** Forwarded to Leader if needed (ensures freshness)

If node cannot contact Leader (partition), reads requiring Leader will fail.

## Performance and Scaling

### Does rqlite increase SQLite performance?

**For reads:** Yes, if using `consistency=none`
- Reads distributed across all nodes
- Can scale read throughput by adding nodes

**For writes:** No
- All writes go through single Leader
- Actually slower than standalone SQLite due to consensus overhead

rqlite is for **high availability**, not write performance scaling.

### What's the best way to increase performance?

1. **Vertical scaling:** Better disks, faster network
2. **Bulk operations:** Use [Bulk API](13-bulk-api.md) for batch writes
3. **Queued writes:** Use [Queued Writes](14-queued-writes.md) for higher throughput
4. **Read scaling:** Add read-only nodes
5. **Appropriate consistency:** Use `none` or `weak` where possible

See [Performance Guide](09-performance.md) for detailed optimization.

### How does rqlite fit into CAP theorem?

rqlite is a **CP (Consistency + Partition Tolerance)** system:
- **Consistency:** All nodes see same data
- **Partition tolerance:** Survives network partitions
- **Availability:** Only majority partition remains available during partition

During network partition:
- Majority side: Continues serving reads and writes
- Minority side: Becomes read-only or unavailable
- After heal: Automatic reconciliation

## Clustering

### How do I change from multi-node to single-node?

**Option 1: Backup and restore (simplest)**
```bash
# Backup cluster
curl localhost:4001/db/backup -o backup.sqlite3

# Start new single node
rqlited -node-id=1 /var/lib/rqlite

# Restore
curl -XPOST localhost:4001/db/restore --form db=@backup.sqlite3
```

**Option 2: Force reconfiguration**
- Requires cluster to be functional
- Remove nodes one by one via `.remove` command
- Last remaining node becomes single-node cluster

### What happens if I lose quorum?

If < (N/2)+1 nodes are available:
- Cluster cannot elect Leader
- Writes fail with "no leader" error
- Reads may work (depending on consistency level)

**Recovery:**
1. Bring enough nodes back online to achieve quorum
2. If impossible, start single node and restore from backup
3. Rebuild cluster by joining new nodes

See [Clustering](03-clustering.md) for detailed recovery procedures.

### How do I detect a cluster partition?

**Client-side indicators:**
- Write requests timeout or fail with "no leader"
- Redirect to Leader fails (cannot reach Leader)
- Inconsistent read results across nodes

**Monitoring:**
```bash
# Check cluster status
curl localhost:4001/status | jq '.raft.state'

# View all nodes
rqlite localhost:4001 ".nodes"
```

## Operations

### How do I monitor rqlite?

**Built-in endpoints:**
- `/status` - Node status and metrics
- `/ready` - Health check endpoint
- `/nodes` - Cluster membership

**External tools:**
- Prometheus (via expvar or metrics endpoint)
- Grafana dashboards
- Custom monitoring via HTTP API

See [Monitoring Guide](10-monitoring.md) for complete setup.

### How do I deploy on Kubernetes?

rqlite provides official Kubernetes manifests and Helm charts:

```bash
# Using Helm
helm install rqlite rqlite/rqlite --set replicaCount=3

# Using manifests
kubectl apply -f https://raw.githubusercontent.com/rqlite/rqlite/main/docker/k8s/rqlite-statefulset.yaml
```

See [Kubernetes Guide](https://rqlite.io/docs/guides/kubernetes/) for detailed deployment.

### Does rqlite require consensus before accepting writes?

**Yes,** with one exception:
- Normal writes: Wait for Raft consensus (durability guarantee)
- Queued writes: Return immediately, process later (performance optimization)

Consensus time depends on:
- Network latency between nodes
- Number of nodes in cluster
- Disk write performance

Typical consensus time: 10-50ms in same datacenter.

## Data and Schema

### Can I use SQLite extensions?

**Yes.** rqlite supports loading SQLite extensions:

```bash
rqlited -extension=/path/to/vec.so ...
```

**Popular extensions:**
- `sqlite-vec` - Vector search for AI/ML
- `sqlean/crypto` - Encryption and hashing
- `spatialite` - Geographic data
- FTS5 - Full-text search (built-in)

See [Extensions Guide](12-extensions.md) for details.

### How do I handle non-deterministic functions like RANDOM()?

rqlite automatically rewrites statements with:
- `RANDOM()` → Replaced with literal random value
- `RANDOMBLOB(N)` → Replaced with literal blob
- `datetime('now')` → Replaced with literal timestamp

Rewriting ensures all nodes apply same value.

**Disable rewriting:** Use `?norwrandom` or `?norwtime` parameters.

See [Non-Deterministic Functions](15-non-deterministic.md) for details.

### Can I access the SQLite file directly?

**Read-only:** Yes, with precautions (use `mode=ro` URI parameter)
**Write:** No, must use HTTP API

⚠️ **Warning:** Improper direct access can corrupt data. See [Direct Access Guide](18-direct-access.md) for safe practices.

## Troubleshooting

### Write fails with "not leader" error

**Cause:** Request sent to follower, cannot reach Leader

**Solutions:**
- Wait for cluster to stabilize
- Check network connectivity between nodes
- Verify Leader is running: `curl localhost:4001/status`
- Client should handle retry with different node

### Cluster has no leader

**Causes:**
- Lost quorum (< N/2+1 nodes available)
- Network partition
- All nodes crashed

**Solutions:**
1. Bring enough nodes online for quorum
2. Check network connectivity
3. If unrecoverable, start single node and restore from backup

### High write latency

**Causes:**
- High network latency between nodes
- Slow disk I/O
- Large transactions
- Frequent leader elections

**Solutions:**
- Move nodes closer (same datacenter)
- Use faster disks (NVMe SSD)
- Batch writes in transactions
- Check for instability causing elections

## Next Steps

- Review [Performance Guide](09-performance.md) for optimization
- Set up [Monitoring](10-monitoring.md) for production
- Configure [Security](08-security.md) for access control
- Learn about [CDC](11-cdc.md) for change streaming
- Explore [Extensions](12-extensions.md) for advanced features
