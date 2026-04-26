---
name: rqlite-9-4
description: Comprehensive toolkit for rqlite 9.4, a lightweight distributed relational database built on SQLite with Raft consensus. Use when deploying fault-tolerant databases, building edge/IoT applications with SQL, creating globally distributed read-intensive systems, or needing simple high-availability without complex administration.
version: "0.3.0"
author: Tangled <noreply@tangledgroup.com>
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
external_references:
  - https://rqlite.io/docs/
  - https://github.com/rqlite/rqlite
---

# rqlite 9.4

## Overview

rqlite is a lightweight, fault-tolerant, distributed relational database built on [SQLite](https://www.sqlite.org/). It combines SQLite's simplicity and rock-solid reliability with the Raft consensus algorithm for automatic replication across multiple nodes. The latest stable release is **v9.4.5**.

rqlite is delivered as a single self-contained binary with no external dependencies. Every write goes through the Raft log, ensuring strong consistency and high availability — every node in a cluster has a full copy of the database. It prioritizes data safety and availability over raw write throughput, making it ideal for applications where keeping data safe and available matters more than maximum write scaling.

Key differentiators from traditional databases:

- **Single binary** — no external dependencies, up and running in seconds
- **Full SQL via SQLite** — including FTS5 full-text search, JSON1 support, window functions, and more
- **Raft consensus** — automatic replication, leader election, fault tolerance
- **HTTP API** — simple JSON-based interface, no special drivers required
- **Tunable consistency** — choose between speed and freshness per query
- **Extensible** — load SQLite extensions for vector search, crypto, and more

## When to Use

Deploy rqlite when you need:

- A fault-tolerant relational database without the complexity of PostgreSQL or MySQL clustering
- Networked SQLite access via HTTP (many users run a single node just for this)
- Edge/IoT deployments where lightweight footprint and reliability are critical
- Read-heavy workloads with globally distributed replicas
- Configuration stores, metadata databases, or operational datastores in cloud/microservice architectures
- Simple high-availability without managing separate consensus layers

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

### SQLite Integration

rqlite runs SQLite in WAL mode with `SYNCHRONOUS=off` for maximum write performance. Periodically, rqlite switches to `SYNCHRONOUS=full` and fsyncs the database to disk for crash safety. On restart, it begins from the last known good fsync or rebuilds from the Raft log if needed.

### Statement-Based Replication

Every SQL statement is stored in the Raft log exactly as received. Each node reads the log and applies statements to its local SQLite copy. Non-deterministic functions like `RANDOM()` and date/time functions are rewritten by the receiving node before being logged, ensuring all nodes produce identical results.

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

**Installation & Setup**: Binary releases, Docker, Homebrew, building from source → [Installation](reference/01-installation-setup.md)

**HTTP API Reference**: Endpoints, writing/querying data, parameterized statements, transactions, BLOBs, bulk writes, queued writes → [HTTP API](reference/02-http-api.md)

**Clustering**: Manual and automatic cluster formation, DNS/Consul/etcd discovery, read-only nodes, growing/shrinking clusters, failure recovery → [Clustering](reference/03-clustering.md)

**Security**: TLS for HTTP and node-to-node, mutual TLS, authentication, role-based permissions, network security → [Security](reference/04-security.md)

**Advanced Operations**: Change Data Capture (CDC), SQLite extensions, backup/restore strategies, performance tuning, monitoring endpoints → [Advanced Topics](reference/05-advanced-topics.md)
