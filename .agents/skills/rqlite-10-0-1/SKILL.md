---
name: rqlite-10-0-1
description: Comprehensive toolkit for rqlite 10.0.1, a lightweight distributed relational database built on SQLite with Raft consensus. Use when deploying fault-tolerant databases, building edge/IoT applications with SQL, creating globally distributed read-intensive systems, configuring Change Data Capture pipelines, loading SQLite extensions for vector search, or needing simple high-availability without complex administration.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "10.0.1"
tags:
  - database
  - distributed-systems
  - sqlite
  - raft
  - high-availability
  - edge-computing
  - iot
  - relational-database
  - cdc
  - change-data-capture
category: database
external_references:
  - https://rqlite.io/docs/
  - https://github.com/rqlite/rqlite/tree/v10.0.1
  - https://github.com/rqlite/rqlite.io
---

# rqlite 10.0.1

## Overview

rqlite is a lightweight, fault-tolerant, distributed relational database built on [SQLite](https://www.sqlite.org/). It combines SQLite's simplicity and rock-solid reliability with the Raft consensus algorithm for automatic replication across multiple nodes.

rqlite is delivered as a single self-contained binary with no external dependencies. Every write goes through the Raft log, ensuring strong consistency and high availability — every node in a cluster has a full copy of the database. It prioritizes data safety and availability over raw write throughput, making it ideal for applications where keeping data safe and available matters more than maximum write scaling.

Key differentiators from traditional databases:

- **Single binary** — no external dependencies, up and running in seconds
- **Full SQL via SQLite** — including FTS5 full-text search, JSON1 support, window functions, and more
- **Raft consensus** — automatic replication, leader election, fault tolerance
- **HTTP API** — simple JSON-based interface, no special drivers required
- **Tunable consistency** — choose between speed and freshness per query
- **Extensible** — load SQLite extensions for vector search, crypto, math functions, and more
- **Change Data Capture** — stream INSERT/UPDATE/DELETE events to HTTP webhooks with at-least-once delivery

## When to Use

Deploy rqlite when you need:

- A fault-tolerant relational database without the complexity of PostgreSQL or MySQL clustering
- Networked SQLite access via HTTP (many users run a single node just for this)
- Edge/IoT deployments where lightweight footprint and reliability are critical
- Read-heavy workloads with globally distributed replicas via read-only nodes
- Configuration stores, metadata databases, or operational datastores in cloud/microservice architectures
- Simple high-availability without managing separate consensus layers
- Real-time change streaming to external systems via CDC

rqlite is **not** designed for write-scaling (every write goes through Raft consensus). For extreme write throughput, consider a database built for horizontal write partitioning.

## Core Concepts

### Architecture

Each rqlite node runs two components:

- **`rqlited`** — the server daemon, listening on two TCP ports:
  - HTTP API port (default `4001`) — client requests
  - Raft port (default `4002`) — inter-node consensus communication
- **`rqlite`** — a command-line shell for interactive use

### Raft Consensus

rqlite uses the [Raft consensus protocol](https://raft.github.io/) to replicate data across nodes. Key implications:

- A cluster always has one **Leader** and one or more **Followers**
- All writes must be processed by the Leader
- A cluster of N voting nodes requires `(N/2)+1` nodes online to remain operational
- Practical cluster sizes: 3 (tolerates 1 failure), 5 (tolerates 2), 7 (tolerates 3)
- Even-numbered clusters are not recommended
- Read-only (non-voting) nodes can be added for read scaling without affecting quorum

### SQLite Integration

rqlite runs SQLite in WAL mode with `SYNCHRONOUS=off` for maximum write performance. Periodically, rqlite switches to `SYNCHRONOUS=full` and fsyncs the database to disk for crash safety. On restart, it begins from the last known good fsync or rebuilds from the Raft log if needed.

### Statement-Based Replication

Every SQL statement is stored in the Raft log exactly as received. Each node reads the log and applies statements to its local SQLite copy. Non-deterministic functions like `RANDOM()` and date/time functions are rewritten by the receiving node before being logged, ensuring all nodes produce identical results.

### Transparent Request Forwarding

Clients can send requests to any node. If a Follower receives a write request, it transparently forwards it to the Leader, waits for the response, and returns it to the client. This means clients do not need to know which node is the Leader.

## Installation / Setup

### Quick Start

Download a pre-built release from [GitHub releases](https://github.com/rqlite/rqlite/releases/latest) (Linux, macOS, Windows). Start a single node:

```bash
rqlited -node-id=1 data/
```

The node listens on `http://localhost:4001`. Docker is also available:

```bash
docker run -p 4001:4001 rqlite/rqlite
```

Or via Homebrew on macOS:

```bash
brew install rqlite
```

### First Steps

Connect with the CLI shell and create a table:

```
$ rqlite
127.0.0.1:4001> CREATE TABLE foo (id INTEGER NOT NULL PRIMARY KEY, name TEXT)
127.0.0.1:4001> INSERT INTO foo(name) VALUES("fiona")
127.0.0.1:4001> SELECT * FROM foo
+----+-------+
| id | name  |
+----+-------+
| 1  | fiona |
+----+-------+
```

Form a 3-node cluster for fault tolerance:

```bash
# Node 1 (leader)
rqlited -node-id=1 data1/

# Node 2 and 3 join node 1
rqlited -node-id=2 -http-addr localhost:4003 -raft-addr localhost:4004 -join localhost:4002 data2/
rqlited -node-id=3 -http-addr localhost:4005 -raft-addr localhost:4006 -join localhost:4002 data3/
```

Verify the cluster:

```
127.0.0.1:4001> .nodes
```

## Usage Examples

### Writing data via HTTP API

```bash
# Create a table
curl -XPOST 'localhost:4001/db/execute?pretty' -H 'Content-Type: application/json' -d '[
    "CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, name TEXT, age INTEGER)"
]'

# Insert with parameterized statement (prevents SQL injection)
curl -XPOST 'localhost:4001/db/execute?pretty' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO users(name, age) VALUES(?, ?)", "fiona", 20]
]'

# Bulk insert in a transaction
curl -XPOST 'localhost:4001/db/execute?pretty&transaction' -H 'Content-Type: application/json' -d '[
    ["INSERT INTO users(name, age) VALUES(?, ?)", "sinead", 25],
    ["INSERT INTO users(name, age) VALUES(?, ?)", "declan", 30]
]'
```

### Querying data

```bash
# Simple query via GET
curl -G 'localhost:4001/db/query?pretty' --data-urlencode 'q=SELECT * FROM users'

# Parameterized query via POST
curl -XPOST 'localhost:4001/db/query?pretty' -H 'Content-Type: application/json' -d '[
    ["SELECT * FROM users WHERE age > ?", 22]
]'

# Associative response (rows as maps instead of arrays)
curl -G 'localhost:4001/db/query?pretty&associative' --data-urlencode 'q=SELECT * FROM users'
```

### Tunable read consistency

```bash
# Weak (default) — fast, served by leader if it believes it is leader
curl -G 'localhost:4001/db/query?level=weak' --data-urlencode 'q=SELECT * FROM users'

# Linearizable — guaranteed up-to-date, slightly slower
curl -G 'localhost:4001/db/query?level=linearizable' --data-urlencode 'q=SELECT * FROM users'

# None — fastest, no leader check (use with read-only nodes)
curl -G 'localhost:4001/db/query?level=none&freshness=1s' --data-urlencode 'q=SELECT * FROM users'
```

### Hot backup

```bash
# Via CLI
127.0.0.1:4001> .backup bak.sqlite3

# Via API
curl -s -XGET localhost:4001/db/backup -o bak.sqlite3

# Compressed backup
curl -s -XGET 'localhost:4001/db/backup?compress' -o bak.sqlite3.gz
```

## Advanced Topics

**Quick Start & CLI**: Getting started, rqlite shell commands, UI applications → [Quick Start & CLI](reference/01-quick-start-and-cli.md)

**HTTP API Reference**: Endpoints, writing/querying data, parameterized statements, transactions, bulk writes, queued writes, PRAGMA directives → [HTTP API](reference/02-http-api-and-developer-guide.md)

**Read Consistency**: Weak, Linearizable, Strong, None, Auto levels; freshness controls; choosing the right level → [Read Consistency](reference/03-read-consistency.md)

**Non-Deterministic Functions**: How rqlite rewrites RANDOM(), RANDOMBLOB(), and date/time functions for deterministic replication → [Non-Deterministic Functions](reference/04-non-deterministic-functions.md)

**Clustering**: Manual cluster creation, node management, growing/shrinking clusters, failure recovery, quorum guidelines → [Clustering](reference/05-clustering.md)

**Automatic Clustering**: DNS, DNS SRV, Consul, and etcd-based discovery; automatic bootstrapping → [Automatic Clustering](reference/06-automatic-clustering.md)

**Read-Only Nodes**: Adding non-voting nodes for read scaling, querying with freshness controls → [Read-Only Nodes](reference/07-read-only-nodes.md)

**Client Connection Strategies**: Static lists, DNS discovery, load balancers, API-based node discovery, client libraries → [Client Connection Strategies](reference/08-client-connection-strategies.md)

**Configuration Reference**: All rqlited command-line flags organized by category → [Configuration](reference/09-configuration.md)

**Security**: TLS/HTTPS, mutual TLS, Basic Auth, role-based permissions, network security → [Security](reference/10-security.md)

**Backup & Restore**: Hot backups, SQL dumps, automatic cloud backups (S3/GCS/file), booting and loading from SQLite → [Backup & Restore](reference/11-backup-and-restore.md)

**Monitoring**: /status, /nodes, /leader, /readyz, expvar, pprof endpoints → [Monitoring](reference/12-monitoring.md)

**Kubernetes & Docker Compose**: Helm charts, StatefulSet deployment, scaling, Docker Compose scenarios → [Kubernetes & Docker Compose](reference/13-kubernetes-and-docker-compose.md)

**Extensions & CDC**: Loading SQLite extensions (vector search, crypto, math), Change Data Capture configuration and event model → [Extensions & CDC](reference/14-extensions-and-cdc.md)

**Performance & Direct Access**: Performance factors, VACUUM/PRAGMA optimize, batching, memory tuning, direct SQLite access guidelines → [Performance & Direct Access](reference/15-performance-and-direct-access.md)

**Design & FAQ**: Architecture internals, Raft log compaction, SQLite WAL strategy, CAP theorem positioning, comparison with alternatives → [Design & FAQ](reference/16-design-and-faq.md)
