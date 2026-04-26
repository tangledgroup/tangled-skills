# Installation & Setup

## Binary Releases

Pre-built binaries are available for **Linux**, **macOS**, and **Windows** on the [GitHub releases page](https://github.com/rqlite/rqlite/releases/latest). Builds are provided for x86, AMD64, ARM, MIPS, RISC-V, and PowerPC architectures.

A release includes two key binaries:

- `rqlited` — the server daemon
- `rqlite` — the command-line shell

### Starting a Single Node

```bash
rqlited -node-id=1 data/
```

The `data/` directory stores the Raft log and SQLite database. The node listens on `http://localhost:4001`.

### Command-Line Flags

Key flags for `rqlited`:

- `-node-id` — unique identifier for this node (required for cluster management, defaults to advertised Raft address if omitted)
- `-http-addr` — HTTP API bind address (default `:4001`)
- `-http-adv-addr` — advertised HTTP address (needed when binding to `0.0.0.0` or behind a firewall)
- `-raft-addr` — Raft communication bind address (default `:4002`)
- `-raft-adv-addr` — advertised Raft address
- `-join` — comma-delimited list of `host:port` to join an existing cluster
- `-extensions-path` — paths to SQLite extension directories, files, zip archives, or tar.gz files
- `-auth` — path to authentication/authorization JSON file
- `-fk` — enable SQLite foreign key constraints (disabled by default in SQLite)

### Docker

Official images on [Docker Hub](https://hub.docker.com/r/rqlite/rqlite/) and [GitHub Container Registry](https://github.com/rqlite/rqlite/pkgs/container/rqlite):

```bash
docker run -p 4001:4001 rqlite/rqlite
docker pull ghcr.io/rqlite/rqlite
```

Enable built-in extensions via environment variable:

```bash
docker run -e SQLITE_EXTENSIONS='sqlean,icu' -p 4001:4001 rqlite/rqlite
```

Built-in Docker extensions: `sqlean`, `sqlite-vec`, `sqliteai-vector`, `icu`, `misc`.

### Homebrew (macOS)

```bash
brew install rqlite
```

### Building from Source

rqlite is written in Go. Build with:

```bash
go build -o rqlited ./cmd/rqlited
go build -o rqlite ./cmd/rqlite
```

See the [building from source guide](https://rqlite.io/docs/install-rqlite/building-from-source/) for details on cross-compilation and custom SQLite configurations.

## rqlite Shell

The `rqlite` CLI connects to an rqlite node and provides an interactive SQL prompt:

```bash
$ rqlite -H 192.168.0.1
192.168.0.1:4001> .help
```

Shell options:

- `-H` — host address (default `127.0.0.1`)
- `-p` — port (default `4001`)
- `-s` — scheme (`http` or `https`)
- `-u` — basic auth credentials as `username:password`
- `-i` — skip HTTPS certificate verification
- `-c` — path to trusted CA certificate
- `-a` — comma-separated fallback host:port pairs

Shell commands (prefixed with `.`):

- `.backup <file>` — write database backup to SQLite file
- `.dump <file>` — dump database in SQL text format
- `.restore <file>` — restore from SQLite database or dump file
- `.schema` — show CREATE statements for all tables
- `.tables` — list table names
- `.indexes` — show index names
- `.nodes` — show cluster node status
- `.remove <node ID>` — remove a node from the cluster
- `.status` — show diagnostic information
- `.consistency [none|weak|strong]` — set read consistency level
- `.expvar` — show Go runtime expvar information
- `.ready` — show ready status

Command history is stored in `~/.rqlite_history` (100 entries by default, configurable via `RQLITE_HISTFILESIZE`).

## Kubernetes

Deploy rqlite on Kubernetes using the official [Helm charts](https://github.com/rqlite/helm-charts) or manually with a StatefulSet. The recommended approach uses DNS-based auto-discovery with a headless Service:

```bash
kubectl apply -f service.yaml    # Creates rqlite-svc and rqlite-svc-internal
kubectl apply -f statefulset-3-node.yaml
```

Scale the cluster:

```bash
kubectl scale statefulsets rqlite --replicas=5
```

When shrinking, remove nodes one at a time and explicitly remove each from the cluster (or enable `-raft-cluster-remove-shutdown=true`) to avoid losing quorum.

## Docker Compose

See the [rqlite docker-compose repo](https://github.com/rqlite/docker-compose) for examples covering single-node setups, manual 3-node clusters, and automatic clustering.
