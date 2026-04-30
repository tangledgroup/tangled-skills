# Configuration Reference

This reference lists all `rqlited` command-line flags organized by category.

## General

- `-version` — Show version information and exit
- `-node-id` — Unique ID for node. If not set, set to advertised Raft address. Once set, a node's ID cannot change.
- `-extensions-path` — Comma-delimited list of paths to directories, zipfiles, or tar.gz files containing SQLite extensions
- `-compress-snap-transport` — Enable zstd compression when transferring snapshots between nodes. Must be set to the same value on every node.
- `-fk` — Enable SQLite foreign key constraints. Must be set on every node in the cluster.

## HTTP API

- `-http-addr` — HTTP server bind address (default `:4001`). To enable HTTPS, set X.509 certificate and key. Use `0.0.0.0` to listen on all interfaces (then set `-http-adv-addr`).
- `-http-adv-addr` — Advertised HTTP address. Required if binding to `0.0.0.0` or behind a firewall.
- `-http-allow-origin` — Value for Access-Control-Allow-Origin header (CORS support)

## HTTPS / TLS (Client-to-Server)

- `-http-ca-cert` — Path to X.509 CA certificate for HTTPS. Validates client certificates and other nodes' HTTPS certificates.
- `-http-cert` — Path to HTTPS X.509 certificate presented to clients
- `-http-key` — Path to HTTPS X.509 private key
- `-http-verify-client` — Enable mutual TLS for HTTPS (only clients with trusted certificates can connect)

## Node-to-Node Encryption

- `-node-ca-cert` — Path to X.509 CA certificate for node-to-node encryption
- `-node-cert` — Path to X.509 certificate for inter-node communication
- `-node-key` — Path to X.509 private key for inter-node communication
- `-node-no-verify` — Skip verification of any presented certificate (testing only)
- `-node-verify-client` — Enable mutual TLS for node-to-node communication
- `-node-verify-server-name` — Hostname to verify on peer certificates (useful with a single cert across all nodes)

## Clustering / Discovery

- `-raft-addr` — Raft communication bind address (default `:4002`). Use `0.0.0.0` to listen on all interfaces (then set `-raft-adv-addr`).
- `-raft-adv-addr` — Advertised Raft communication address
- `-join` — Comma-delimited list of nodes in `host:port` form through which a cluster can be joined
- `-join-attempts` — Number of join attempts per address
- `-join-interval` — Period between join attempts
- `-join-as` — Username in auth file to join as (avoids exposing credentials on command line)
- `-bootstrap-expect` — Minimum number of nodes required for automatic bootstrap
- `-bootstrap-expect-timeout` — Maximum time for bootstrap process
- `-disco-mode` — Clustering discovery mode (`dns`, `dns-srv`, `consul-kv`, `etcd-kv`)
- `-disco-key` — Key prefix for cluster discovery service (allows multiple clusters on one discovery system)
- `-disco-config` — Discovery config as JSON string or path to config file

## Raft Consensus

- `-raft-non-voter` — Configure as non-voting (read-only) node
- `-raft-snap` — Number of outstanding log entries that triggers a Raft snapshot
- `-raft-snap-wal-size` — SQLite WAL file size in bytes that triggers a snapshot (default 4MB, set to 0 to disable)
- `-raft-snap-int` — Snapshot threshold check interval
- `-raft-leader-lease-timeout` — Leader lease timeout (use `0s` for Raft default)
- `-raft-heartbeat-timeout` — Time a Follower waits without contact before initiating an election
- `-raft-commit-timeout` — Time without an Apply operation before sending AppendEntry RPC
- `-raft-election-timeout` — Time a Candidate waits before initiating a new election
- `-raft-apply-timeout` — Raft apply timeout
- `-raft-remove-shutdown` — Shutdown Raft if node is removed from cluster (prevents self-election as sole node)
- `-raft-cluster-remove-shutdown` — Node removes itself from cluster on graceful shutdown
- `-raft-shutdown-stepdown` — If leader, step down before shutting down (enabled by default)
- `-raft-reap-node-timeout` — Time after which a non-reachable voting node is reaped
- `-raft-reap-read-only-node-timeout` — Time after which a non-reachable read-only node is reaped
- `-raft-log-level` — Minimum log level for Raft module (`ERROR`, `WARN`, `INFO`, `DEBUG`)
- `-cluster-connect-timeout` — Timeout for initial connection to other nodes

## Authentication / Authorization

- `-auth` — Path to authentication and authorization JSON file. If not set, auth is disabled.

## Queued Writes

- `-write-queue-capacity` — Maximum number of queued write requests
- `-write-queue-batch-size` — Number of queued write statements batched per Raft log entry
- `-write-queue-timeout` — Timeout after which queued writes are flushed regardless of batch size
- `-write-queue-tx` — Use a transaction when processing queued writes

## SQLite Maintenance

- `-auto-vacuum-int` — Period between automatic VACUUMs (e.g., `24h`). Set to 0 to disable.
- `-auto-optimize-int` — Period between automatic `PRAGMA optimize` (default daily). Set to `0h` to disable.

## Change Data Capture

- `-cdc-config` — Set CDC HTTP endpoint URL or path to CDC config file. If not set, CDC is not enabled.

## Automatic Backup / Restore

- `-auto-backup` — Path to automatic backup configuration file (S3, GCS, or local filesystem)
- `-auto-restore` — Path to automatic restore configuration file

## Profiling

- `-cpu-profile` — Path to file for CPU profiling information
- `-mem-profile` — Path to file for memory profiling information
- `-trace-profile` — Path to file for trace profiling information
