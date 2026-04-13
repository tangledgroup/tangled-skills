# Configuration

Complete reference for rqlite command-line flags and configuration options.

## Overview

rqlite is configured via command-line flags when starting `rqlited`. This guide documents all available options.

View all options:
```bash
rqlited -h
```

## Node Identification

### `-node-id`

Unique identifier for this node.

```bash
rqlited -node-id=node1 ...
```

**Details:**
- Must be unique within cluster
- Can be any string (numbers, hostnames, UUIDs)
- Cannot change after initial cluster join
- If not set, defaults to advertised Raft address
- Recommended: Use explicit IDs for easier management

## Network Configuration

### HTTP API

#### `-http-addr`

HTTP server bind address.

```bash
rqlited -http-addr=:4001 ...           # Default: all interfaces, port 4001
rqlited -http-addr=0.0.0.0:4001 ...    # Explicit all interfaces
rqlited -http-addr=127.0.0.1:4001 ...  # Localhost only
```

#### `-http-adv-addr`

Advertised HTTP address (what to tell other nodes/clients).

```bash
# Required when binding to 0.0.0.0 or behind NAT
rqlited -http-addr=0.0.0.0:4001 \
  -http-adv-addr=public.example.com:4001 ...
```

#### `-http-allow-origin`

CORS header value for browser-based applications.

```bash
rqlited -http-allow-origin="https://app.example.com" ...
```

### Raft Communication

#### `-raft-addr`

Raft protocol bind address.

```bash
rqlited -raft-addr=:4002 ...           # Default: all interfaces, port 4002
rqlited -raft-addr=0.0.0.0:4002 ...    # Explicit all interfaces
```

#### `-raft-adv-addr`

Advertised Raft address.

```bash
rqlited -raft-addr=0.0.0.0:4002 \
  -raft-adv-addr=public.example.com:4002 ...
```

## Cluster Management

### `-join`

Comma-delimited list of nodes to join.

```bash
# Join single node
rqlited -join=node1:4002 ...

# Join with fallbacks
rqlited -join="node1:4002,node2:4002,node3:4002" ...
```

### `-join-attempts`

Number of join attempts per address.

```bash
rqlited -join=node1:4002 -join-attempts=10 ...
```

**Default:** 5

### `-join-interval`

Period between join attempts.

```bash
rqlited -join=node1:4002 -join-interval=5s ...
```

**Default:** 5s

### `-join-as`

Username for authenticated joins.

```bash
rqlited -join=node1:4002 -join-as=admin -auth=/path/to/auth.json ...
```

### Bootstrap

#### `-bootstrap-expect`

Minimum nodes required before bootstrapping cluster.

```bash
rqlited -bootstrap-expect=3 ...
```

**Use case:** Wait for all expected nodes before electing leader.

#### `-bootstrap-expect-timeout`

Maximum time to wait for bootstrap.

```bash
rqlited -bootstrap-expect=3 -bootstrap-expect-timeout=60s ...
```

**Default:** 0 (no timeout)

## Security

### HTTPS (Client Connections)

#### `-http-cert`

Path to X.509 certificate for HTTPS.

```bash
rqlited -http-cert=/path/to/cert.pem ...
```

#### `-http-key`

Path to private key for HTTPS.

```bash
rqlited -http-key=/path/to/key.pem ...
```

#### `-http-ca-cert`

Path to CA certificate for client verification.

```bash
rqlited -http-ca-cert=/path/to/ca.pem ...
```

#### `-http-verify-client`

Enable mutual TLS for HTTPS clients.

```bash
rqlited -http-verify-client \
  -http-cert=/path/to/cert.pem \
  -http-key=/path/to/key.pem \
  -http-ca-cert=/path/to/ca.pem ...
```

### Node-to-Node TLS (Raft)

#### `-node-cert`

Certificate for inter-node encryption.

```bash
rqlited -node-cert=/path/to/node-cert.pem ...
```

#### `-node-key`

Private key for inter-node encryption.

```bash
rqlited -node-key=/path/to/node-key.pem ...
```

#### `-node-ca-cert`

CA certificate for verifying node certificates.

```bash
rqlited -node-ca-cert=/path/to/ca.pem ...
```

#### `-node-verify-client`

Enable mutual TLS for node-to-node communication.

```bash
rqlited -node-verify-client \
  -node-cert=/path/to/node-cert.pem \
  -node-key=/path/to/node-key.pem \
  -node-ca-cert=/path/to/ca.pem ...
```

#### `-node-no-verify`

Skip certificate verification (development only).

```bash
rqlited -node-no-verify ...
```

⚠️ **Warning:** Only use in development/testing.

#### `-node-verify-server-name`

Explicit hostname to verify in certificates.

```bash
rqlited -node-verify-server-name=node1.example.com ...
```

**Use case:** Use single certificate across all nodes.

### Authentication

#### `-auth`

Path to authentication/authorization file.

```bash
rqlited -auth=/path/to/auth.json ...
```

See [Security](08-security.md) for auth file format.

## Data Storage

### `-on-disk-path`

Path for SQLite database file.

```bash
rqlited -on-disk-path=/var/lib/rqlite/db.sqlite ...
```

**Default:** Auto-generated in data directory

### `-fk`

Enable foreign key constraints.

```bash
rqlited -fk ...
```

**Default:** false (disabled)

### `-raft-badger`

Use Badger DB instead of BoltDB for Raft storage.

```bash
rqlited -raft-badger ...
```

**Benefits:** Better performance for Raft log operations

## Extensions

### `-extension`

Load SQLite extension (can be specified multiple times).

```bash
rqlited -extension=/path/to/vec.so \
  -extension=/path/to/crypto.so ...
```

### `-extensions-path`

Directories containing extensions.

```bash
rqlited -extensions-path="/usr/local/lib/rqlite,/opt/extensions" ...
```

Supports directories, ZIP files, and tar.gz archives.

## CDC (Change Data Capture)

### `-cdc-config`

CDC configuration file or HTTP endpoint.

```bash
# Config file
rqlited -cdc-config=/path/to/cdc.json ...

# Direct HTTP endpoint
rqlited -cdc-config="http://kafka:9092/topic" ...
```

See [CDC](11-cdc.md) for configuration details.

## Backup and Restore

### `-auto-backup`

Automatic backup configuration file.

```bash
rqlited -auto-backup=/path/to/backup-config.json ...
```

See [Backup and Restore](05-backup-restore.md) for details.

### `-auto-restore`

Automatic restore configuration file.

```bash
rqlited -auto-restore=/path/to/restore-config.json ...
```

## Queued Writes

### `-write-queue-size`

Minimum queued writes before flush.

```bash
rqlited -write-queue-size=1024 ...
```

**Default:** Varies by version

### `-write-queue-tmo`

Maximum time before flushing queue.

```bash
rqlited -write-queue-tmo=100ms ...
```

**Default:** 100ms

### `-write-queue-tx`

Execute queued writes in transactions.

```bash
rqlited -write-queue-tx ...
```

**Default:** false

## Cluster Discovery

### `-disco-mode`

Discovery mode (consul, etcd, dns, k8s).

```bash
rqlited -disco-mode=consul ...
```

### `-disco-key`

Key prefix for discovery service.

```bash
rqlited -disco-mode=consul -disco-key=rqlite-cluster-1 ...
```

### `-disco-config`

Discovery configuration file.

```bash
rqlited -disco-config=/path/to/discovery.json ...
```

## Cluster Behavior

### `-raft-cluster-remove-shutdown`

Auto-remove node on graceful shutdown.

```bash
rqlited -raft-cluster-remove-shutdown ...
```

**Behavior:** Node removes itself from cluster config before exiting.

### `-no-recovery`

Skip automatic recovery on startup.

```bash
rqlited -no-recovery ...
```

## Logging

### `-log-level`

Logging level.

```bash
rqlited -log-level=info ...
```

**Values:** error, warn, info, debug

**Default:** info

### `-log-format`

Log output format.

```bash
rqlited -log-format=json ...
```

**Values:** text, json

**Default:** text

## Version

### `-version`

Display version and exit.

```bash
rqlited -version
```

## Example Configurations

### Production Node

```bash
rqlited \
  -node-id=node1 \
  -http-addr=0.0.0.0:4001 \
  -http-adv-addr=node1.example.com:4001 \
  -http-cert=/etc/rqlite/certs/server.crt \
  -http-key=/etc/rqlite/certs/server.key \
  -http-ca-cert=/etc/rqlite/certs/ca.crt \
  -http-verify-client \
  -raft-addr=0.0.0.0:4002 \
  -raft-adv-addr=node1.example.com:4002 \
  -node-cert=/etc/rqlite/certs/node.crt \
  -node-key=/etc/rqlite/certs/node.key \
  -node-ca-cert=/etc/rqlite/certs/ca.crt \
  -node-verify-client \
  -auth=/etc/rqlite/auth.json \
  -auto-backup=/etc/rqlite/backup.json \
  -log-level=info \
  /var/lib/rqlite/node1
```

### Development Node

```bash
rqlited \
  -node-id=dev1 \
  -http-addr=:4001 \
  -raft-addr=:4002 \
  -log-level=debug \
  /tmp/rqlite-dev
```

### High-Performance Node

```bash
rqlited \
  -node-id=perf1 \
  -http-addr=:4001 \
  -raft-addr=:4002 \
  -raft-badger \
  -write-queue-size=4096 \
  -write-queue-tmo=500ms \
  -fk \
  /var/lib/rqlite/perf1
```

## Next Steps

- Set up [security](08-security.md) with TLS and authentication
- Configure [backups](05-backup-restore.md) for data protection
- Enable [CDC](11-cdc.md) for change streaming
- Optimize [performance](09-performance.md) with appropriate flags
