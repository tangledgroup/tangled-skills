# Security

## File System Security

Control access to the data directory that each rqlite node uses. There is no reason for any user to directly access this directory. File-level security is critical when using TLS certificates and keys. Consider running rqlite on an encrypted file system.

If you change the SQLite database path via command-line flags, secure access to it as well. Writing to the SQLite file will cause rqlite to fail.

## Network Security

Each rqlite node listens on 2 TCP ports: one for the HTTP API and one for inter-node (Raft) communication. Only the HTTP API port needs to be reachable from outside the cluster.

Configure the network so the Raft port on each node is only accessible from other nodes in the cluster. Run Raft connections on a physically or logically different network from the HTTP API. If client IP addresses are known, limit HTTP API access to those addresses only (e.g., AWS Security Groups).

## HTTPS and Mutual TLS

rqlite supports secure access via HTTPS using Transport Layer Security (TLS):

```bash
rqlited -http-cert server.crt -http-key key.pem ~/node
```

For mutual TLS (mTLS), where only clients presenting trusted certificates can connect:

```bash
rqlited -http-ca-cert ca.crt -http-cert server.crt -http-key key.pem \
  -http-verify-client ~/node
```

> rqlite continuously monitors certificate and key files, automatically reloading them when changes are detected. This allows rotation without restarting the node. CA certificate changes require a restart.

## Encrypting Node-to-Node Communication

rqlite supports TLS encryption for all inter-node traffic:

```bash
rqlited -node-cert node.crt -node-key node-key.pem ~/node
```

For mutual TLS between nodes:

```bash
rqlited -node-ca-cert ca.crt -node-cert node.crt -node-key node-key.pem \
  -node-verify-client ~/node
```

Every node in a cluster must operate with inter-node encryption enabled, or none at all.

## Basic Authentication

The HTTP API supports [Basic Auth](https://tools.ietf.org/html/rfc2617). Pass a JSON-formatted configuration file via `-auth`:

```bash
rqlited -auth config.json ~/node
```

Each node can have its own credentials file, but for consistent access across the cluster, ensure every node contains the same user information.

## User-Level Permissions

Each user can be granted one or more of the following permissions:

- `all` — user can perform all operations on a node
- `backup` — retrieve a backup via `/db/backup`
- `execute` — access the execute endpoint at `/db/execute`
- `join` — join a cluster (used by nodes joining, not clients)
- `join-read-only` — join a cluster as a read-only node
- `leader-ops` — perform Leader-related operations via `/leader`
- `load` — load an SQLite dump file via `/db/load` or `/boot`
- `query` — access the query endpoint at `/db/query` and SQL rewriting at `/db/sql`
- `ready` — retrieve node readiness via `/readyz`
- `remove` — remove a node from a cluster
- `snapshot` — initiate a Raft Snapshot via `/snapshot`
- `status` — retrieve node status and Go runtime information
- `ui` — access the built-in management application at `/console`

> For the [Unified Endpoint](reference/02-http-api-and-developer-guide.md#db-request--unified-endpoint), a user must have **both** `execute` and `query` permissions.

## Example Permissions File

```json
[
  {
    "username": "bob",
    "password": "secret1",
    "perms": ["all"]
  },
  {
    "username": "mary",
    "password": "secret2",
    "perms": ["query", "backup", "join"]
  },
  {
    "username": "*",
    "perms": ["status", "ready", "join-read-only"]
  }
]
```

`*` is a special username indicating that all users — even anonymous requests without BasicAuth — have the specified permissions.

## Secure Cluster Example

Starting a node with HTTPS, node-to-node encryption, and authentication:

```bash
rqlited -auth config.json -http-cert server.crt -http-key key.pem \
  -node-cert node.crt -node-key node-key.pem ~/node.1
```

Joining a second node using bob's credentials:

```bash
rqlited -auth config.json -http-addr localhost:4003 -http-cert server.crt \
  -http-key key.pem -raft-addr :4004 -join localhost:4002 -join-as bob \
  -node-cert node.crt -node-key node-key.pem ~/node.2
```

Querying as user mary:

```bash
curl -G 'https://mary:secret2@localhost:4001/db/query?pretty&timings' \
  --data-urlencode 'q=SELECT * FROM foo'
```

## Protecting Against SQL Injection

Use [parameterized statements](reference/02-http-api-and-developer-guide.md#parameterized-statements) to protect against SQL injection attacks. The `/db/query` endpoint executes all SQL using a read-only connection, so no request sent to `/db/query` can ever modify the database.

## Generating Certificates and Keys

Use [OpenSSL](https://www.openssl.org/) or similar tools to create and sign X.509 certificates and keys for both HTTPS and node-to-node encryption.
