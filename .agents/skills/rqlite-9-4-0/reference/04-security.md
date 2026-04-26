# Security

## Network Security

Each rqlite node listens on two TCP ports:

- **HTTP API port** (default `4001`) — client requests
- **Raft port** (default `4002`) — inter-node consensus communication

Only the HTTP API port needs to be reachable from outside the cluster. Configure firewalls so the Raft port is accessible only between cluster nodes. On AWS EC2, use Security Groups to restrict access.

## HTTPS and TLS

Enable HTTPS by providing an X.509 certificate and private key:

```bash
rqlited -http-cert server.crt -http-key key.pem data/
```

### Mutual TLS (mTLS)

Restrict clients to only those presenting trusted certificates:

```bash
rqlited -http-cert server.crt -http-key key.pem \
  -http-ca-cert ca.pem -http-verify-client data/
```

Certificate and key files are monitored for changes and reloaded automatically without restart. CA certificate changes require a restart.

### Node-to-Node Encryption

Encrypt all inter-node Raft traffic:

```bash
rqlited -node-cert node.crt -node-key node-key.pem data/
```

Enable mutual TLS between nodes:

```bash
rqlited -node-cert node.crt -node-key node-key.pem \
  -node-ca-cert ca.pem -node-verify-client data/
```

Every node in a cluster must have inter-node encryption enabled, or none at all. Use `-node-verify-server-name` to verify a specific hostname on peer certificates (useful with a single certificate across all nodes).

### Skip Verification (Testing Only)

```bash
rqlited -node-cert node.crt -node-key node-key.pem \
  -node-no-verify data/
```

## Authentication and Authorization

Enable Basic Auth with a JSON configuration file:

```bash
rqlited -auth config.json data/
```

### Permissions File Format

```json
[
  {
    "username": "admin",
    "password": "secret1",
    "perms": ["all"]
  },
  {
    "username": "reader",
    "password": "secret2",
    "perms": ["query", "status"]
  },
  {
    "username": "*",
    "perms": ["status", "ready"]
  }
]
```

The `*` username applies to all users including anonymous requests.

### Permission Levels

- `all` — full access to all operations
- `execute` — access to `/db/execute`
- `query` — access to `/db/query` and `/db/sql`
- `load` — load SQLite dump via `/db/load` or `/boot`
- `backup` — retrieve backup via `/db/backup`
- `snapshot` — initiate Raft snapshot via `/snapshot`
- `status` — retrieve node status and runtime info
- `ready` — check readiness via `/readyz`
- `join` — join a cluster (used by nodes, not clients)
- `join-read-only` — join as a read-only node
- `remove` — remove a node from the cluster
- `leader-ops` — perform leader operations via `/leader`

To access the unified endpoint (`/db/request`), a user needs both `execute` and `query` permissions.

### Connecting with Credentials

Via curl:

```bash
curl -G 'https://reader:secret2@localhost:4001/db/query?pretty' \
  --data-urlencode 'q=SELECT * FROM users'
```

Via CLI:

```bash
rqlite -u reader:secret2 -s https -i localhost
```

### Joining with Credentials

When a node joins a secured cluster, specify the user with `-join-as`:

```bash
rqlited -auth config.json \
  -http-addr host2:4003 -raft-addr host2:4004 \
  -join host1:4002 -join-as admin \
  data2/
```

Using `-join-as` avoids putting credentials on the command line.

## SQL Injection Protection

Always use parameterized statements instead of string interpolation:

```bash
# Safe — parameterized
curl -XPOST 'localhost:4001/db/query?pretty' \
  -H 'Content-Type: application/json' \
  -d '[["SELECT * FROM users WHERE name=?", "fiona"]]'
```

The `/db/query` endpoint uses a read-only SQLite connection, so no request to that endpoint can modify the database regardless of content.

## File System Security

Control access to each node's data directory. The Raft log and SQLite database files should only be accessible by the rqlite process. Consider running on an encrypted file system for sensitive data.

Never allow external processes to write to the SQLite database file — doing so causes undefined behavior and potential data loss. If another system needs to read the SQLite file directly, it must use read-only mode (`mode=ro` URI parameter) and never open in EXCLUSIVE locking mode.

## CORS

For browser-based applications, set the CORS header:

```bash
rqlited -http-allow-origin="https://example.com" data/
```
