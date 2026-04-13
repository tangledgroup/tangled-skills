---
name: rqlite-9-4
description: Comprehensive toolkit for rqlite 9.4, a lightweight distributed relational database built on SQLite with Raft consensus. Use when deploying fault-tolerant databases, building edge/IoT applications with SQL, creating globally distributed read-intensive systems, or needing simple high-availability without complex administration.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - database
  - distributed-systems
  - sqlite
  - raft
  - high-availability
  - edge-computing
  - iot
  - relational-database
category: database
required_environment_variables:
  - name: RQLITE_NODE_ID
    prompt: "Enter unique node ID for this rqlite instance (e.g., 1, 2, 3)"
    help: "Each node in a cluster must have a unique integer ID"
    required_for: "cluster deployment"
  - name: RQLITE_JOIN_ADDR
    prompt: "Enter address of existing cluster node to join (e.g., host:4002)"
    help: "Address of a node already in the cluster (Raft port, default 4002)"
    required_for: "joining existing cluster"
  - name: AWS_ACCESS_KEY_ID
    prompt: "Enter AWS access key ID for automated S3 backups"
    help: "AWS credential for automated backup to S3 (optional)"
    required_for: "automated S3 backups"
  - name: AWS_SECRET_ACCESS_KEY
    prompt: "Enter AWS secret access key for automated S3 backups"
    help: "AWS credential for automated backup to S3 (optional)"
    required_for: "automated S3 backups"
---

# rqlite 9.4 Distributed Database Skill

A comprehensive skill for using rqlite, a lightweight, user-friendly distributed relational database built on SQLite. This skill covers installation, configuration, clustering, API usage, backup/restore, and operational best practices.

## When to Use

- Deploy a fault-tolerant, highly-available relational database
- Need SQLite with distributed consensus (Raft) for high availability
- Build edge/IoT applications requiring local SQL with optional replication
- Create read-intensive globally distributed applications
- Need simple deployment without complex database administration
- Require atomic multi-statement execution across a cluster
- Want hot backups and automated cloud storage integration

## Quick Start

### Install via Docker (Fastest)

```bash
# Start single node
docker run -p 4001:4001 rqlite/rqlite

# Verify it's running
curl localhost:4001/db/query?q=SELECT+1
```

See [Installation](references/01-installation.md) for other installation methods.

### Create a Table and Insert Data

```bash
# Connect to rqlite shell
rqlite 127.0.0.1:4001

# Create table
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)

# Insert data
INSERT INTO users(name, email) VALUES("Alice", "alice@example.com")
INSERT INTO users(name, email) VALUES("Bob", "bob@example.com")

# Query data
SELECT * FROM users

# Exit shell
.quit
```

See [rqlite Shell](references/02-shell.md) for interactive usage.

### Form a 3-Node Cluster

```bash
# Node 1 (bootstrap node)
docker run -d --name rqlite1 -p 4001:4001 -p 4002:4002 \
  rqlite/rqlite -node-id=1

# Node 2 (joins cluster)
docker run -d --name rqlite2 -p 4003:4001 -p 4004:4002 \
  rqlite/rqlite -node-id=2 -join=rqlite1:4002

# Node 3 (joins cluster)
docker run -d --name rqlite3 -p 4005:4001 -p 4006:4002 \
  rqlite/rqlite -node-id=3 -join=rqlite1:4002

# Check cluster status
rqlite 127.0.0.1:4001
.nodes
```

See [Clustering](references/03-clustering.md) for detailed clustering guides.

### Using the HTTP API

```bash
# Create table via API
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '["CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"]'

# Insert data with parameterized query (prevents SQL injection)
curl -XPOST 'localhost:4001/db/execute' \
  -H "Content-Type: application/json" \
  -d '[["INSERT INTO products(name, price) VALUES(?, ?)", "Widget", 9.99]]'

# Query data
curl -G 'localhost:4001/db/query' --data-urlencode 'q=SELECT * FROM products'

# Associative response format (easier to parse)
curl -G 'localhost:4001/db/query?associative' \
  --data-urlencode 'q=SELECT * FROM products'
```

See [HTTP API](references/04-api.md) for comprehensive API documentation.

### Backup and Restore

```bash
# Create backup via shell
rqlite 127.0.0.1:4001
.backup backup.sqlite3

# Create backup via API
curl -s localhost:4001/db/backup -o backup.sqlite3

# Create compressed backup
curl -s 'localhost:4001/db/backup?compress' -o backup.sqlite3.gz

# Restore from backup (requires stopping node first)
# See Backup and Restore guide for details
```

See [Backup and Restore](references/05-backup-restore.md) for comprehensive backup strategies.

## Core Concepts

### Architecture

rqlite combines SQLite's simplicity with Raft consensus for:
- **High Availability**: Data replicated across multiple nodes
- **Fault Tolerance**: Cluster survives node failures (N/2 + 1 nodes must be up)
- **Strong Consistency**: All replicas see the same data
- **Simplicity**: Single binary, no external dependencies

### Key Features

| Feature | Description |
|---------|-------------|
| **Relational** | Full SQL support via SQLite (SELECT, INSERT, UPDATE, DELETE, etc.) |
| **Atomic Writes** | Multiple statements executed atomically in a single request |
| **Extensible** | Load SQLite extensions for vector search, cryptography, etc. |
| **Change Data Capture** | Stream database changes to external systems |
| **Read-Only Nodes** | Scale reads without affecting consensus |
| **Hot Backups** | Backup without downtime, with cloud storage integration |
| **Security** | TLS encryption and role-based access control |

### Cluster Sizes

| Nodes | Fault Tolerance | Use Case |
|-------|----------------|----------|
| 1 | None | Development, simple deployments |
| 3 | 1 node failure | Production (most common) |
| 5 | 2 node failures | High availability requirements |
| 7 | 3 node failures | Mission-critical systems |

**Note:** Always use odd-numbered clusters for voting nodes. Even numbers provide no additional fault tolerance but increase coordination overhead.

## Common Patterns

### Single-Node Deployment (Development)

```bash
# Quick start for development
docker run -p 4001:4001 rqlite/rqlite

# Or via binary
rqlited -node-id=1 /var/lib/rqlite
```

### Production Cluster with Docker Compose

```yaml
# docker-compose.yml
version: '3'
services:
  rqlite1:
    image: rqlite/rqlite
    container_name: rqlite1
    ports:
      - "4001:4001"
      - "4002:4002"
    command: -node-id=1
    volumes:
      - rqlite1-data:/rqlite

  rqlite2:
    image: rqlite/rqlite
    container_name: rqlite2
    ports:
      - "4003:4001"
      - "4004:4002"
    command: -node-id=2 -join=rqlite1:4002
    volumes:
      - rqlite2-data:/rqlite

  rqlite3:
    image: rqlite/rqlite
    container_name: rqlite3
    ports:
      - "4005:4001"
      - "4006:4002"
    command: -node-id=3 -join=rqlite1:4002
    volumes:
      - rqlite3-data:/rqlite

volumes:
  rqlite1-data:
  rqlite2-data:
  rqlite3-data:
```

See [Docker Compose Guide](references/06-docker-compose.md) for production-ready configurations.

### Transactional Writes

```bash
# Execute multiple statements atomically
curl -XPOST 'localhost:4001/db/execute?transaction' \
  -H "Content-Type: application/json" \
  -d '[
    "INSERT INTO accounts(id, balance) VALUES(1, 1000)",
    "INSERT INTO accounts(id, balance) VALUES(2, 500)",
    "CREATE INDEX idx_balance ON accounts(balance)"
  ]'
```

### Read Consistency Levels

```bash
# Weak consistency (fastest, may read stale data)
curl 'localhost:4001/db/query?consistency=none&q=SELECT * FROM users'

# Strong consistency (reads from leader, ensures freshness)
curl 'localhost:4001/db/query?consistency=strong&q=SELECT * FROM users'
```

See [Read Consistency](references/07-read-consistency.md) for detailed guidance.

### Automated Backups to S3

```json
// auto-backup.json
{
  "version": 1,
  "type": "s3",
  "interval": "5m",
  "vacuum": false,
  "sub": {
    "access_key_id": "$AWS_ACCESS_KEY_ID",
    "secret_access_key": "$AWS_SECRET_ACCESS_KEY",
    "region": "us-east-1",
    "bucket": "my-rqlite-backups",
    "path": "backups/db.sqlite3.gz"
  }
}
```

Start rqlite with: `rqlited -auto-backup=auto-backup.json ...`

See [Backup and Restore](references/05-backup-restore.md) for all backup options.

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Node won't join cluster | Check `-join` address is reachable; verify Raft port (default 4002) is open |
| Cluster has no leader | Ensure quorum (N/2+1 nodes) are running and network-connected |
| Write fails with "not leader" | Request was sent to follower; enable auto-redirect or send to leader |
| Backup fails | Check disk space; WAL mode backups need ~1.5x database size |
| Query timeout | Set `db_timeout` parameter; check for long-running transactions |

### Diagnostic Commands

```bash
# Check cluster status
rqlite 127.0.0.1:4001
.status
.nodes

# Check node readiness
.ready

# View schema
.schema

# List tables
.tables

# Export diagnostics
.sysdump diagnostics.json
```

### Recovering from Failure

If you lose quorum and cannot elect a leader:
1. Start a single node without `-join` flag
2. Restore data from backup using `.restore` command
3. Rebuild cluster by joining new nodes

See [Clustering](references/03-clustering.md) for detailed recovery procedures.

## Reference Files

### Core Operations
- [`references/01-installation.md`](references/01-installation.md) - Installation methods (binary, Docker, Homebrew, source)
- [`references/02-shell.md`](references/02-shell.md) - Interactive rqlite shell commands and usage
- [`references/03-clustering.md`](references/03-clustering.md) - Cluster creation, management, and failure recovery
- [`references/04-api.md`](references/04-api.md) - HTTP API endpoints, request/response formats, parameters
- [`references/05-backup-restore.md`](references/05-backup-restore.md) - Backup strategies, restore procedures, automated backups
- [`references/06-docker-compose.md`](references/06-docker-compose.md) - Docker Compose configurations for development and production

### Advanced Topics
- [`references/07-read-consistency.md`](references/07-read-consistency.md) - Read consistency levels and trade-offs
- [`references/08-security.md`](references/08-security.md) - TLS, authentication, and access control
- [`references/09-performance.md`](references/09-performance.md) - Performance tuning and optimization
- [`references/10-monitoring.md`](references/10-monitoring.md) - Monitoring, metrics, and observability
- [`references/11-cdc.md`](references/11-cdc.md) - Change Data Capture for streaming database changes
- [`references/12-extensions.md`](references/12-extensions.md) - SQLite extensions for extended functionality

### API Deep Dives
- [`references/13-bulk-api.md`](references/13-bulk-api.md) - Bulk operations for high-throughput batch processing
- [`references/14-queued-writes.md`](references/14-queued-writes.md) - Asynchronous write queuing for maximum throughput
- [`references/15-non-deterministic.md`](references/15-non-deterministic.md) - Handling RANDOM() and datetime functions in distributed context
- [`references/16-cluster-client.md`](references/16-cluster-client.md) - Client connection strategies for clusters

### Configuration and Access
- [`references/17-config.md`](references/17-config.md) - Complete command-line flag reference
- [`references/18-direct-access.md`](references/18-direct-access.md) - Safely accessing underlying SQLite database
- [`references/19-ui-applications.md`](references/19-ui-applications.md) - Third-party graphical tools and interfaces
- [`references/20-faq.md`](references/20-faq.md) - Frequently asked questions and common scenarios

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/rqlite-9-4/`). All paths are relative to this directory.

## Best Practices

### Production Deployment

1. **Use 3 or more nodes** for fault tolerance
2. **Enable TLS** for all communications (client-to-server and inter-node)
3. **Configure automated backups** to cloud storage
4. **Set appropriate timeouts** based on your workload
5. **Monitor cluster health** with regular status checks
6. **Use parameterized queries** to prevent SQL injection
7. **Keep rqlite updated** for security patches and improvements

### Performance Tips

1. **Batch writes** using transactions for better throughput
2. **Use read-only nodes** to scale read-heavy workloads
3. **Choose appropriate consistency level** (none/weak/strong) per query
4. **Enable queued writes** for non-critical data with higher write volume
5. **Index frequently queried columns** using standard SQLite indexing

### Development Workflow

1. **Start single-node** for local development
2. **Use Docker Compose** for testing cluster behavior
3. **Leverage the shell** for ad-hoc queries and debugging
4. **Test backup/restore** procedures regularly
5. **Validate SQL compatibility** with SQLite documentation
