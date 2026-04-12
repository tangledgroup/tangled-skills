# rqlite Shell

How to access rqlite using the interactive command-line tool.

## Overview

The `rqlite` shell is a command-line tool for interacting with rqlite nodes. It provides an interactive interface similar to the SQLite shell, with additional commands for cluster management and diagnostics.

## Starting the Shell

### Basic Connection

```bash
# Connect to local node
rqlite 127.0.0.1:4001

# Connect to remote node
rqlite -H 192.168.1.100

# Specify custom port
rqlite -H 192.168.1.100 -p 4003

# Use HTTPS
rqlite -H example.com -s https

# Skip certificate verification (development only)
rqlite -H example.com -s https -i
```

### Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `-h, --help` | Display help information | - |
| `-H, --host` | rqlited host address | `127.0.0.1` |
| `-p, --port` | rqlited host port | `4001` |
| `-P, --prefix` | HTTP URL prefix | `/` |
| `-s, --scheme` | Protocol scheme (http or https) | `http` |
| `-i, --insecure` | Do not verify HTTPS certificate | `false` |
| `-c, --ca-cert` | Path to trusted X.509 root CA certificate | - |
| `-u, --user` | Basic auth credentials (username:password) | - |
| `-a, --alternatives` | Comma-separated fallback host:port pairs | - |
| `-v, --version` | Display CLI version | - |

## Interactive Commands

### SQL Commands

Standard SQLite SQL is fully supported:

```bash
127.0.0.1:4001> CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
0 row affected (0.000362 sec)

127.0.0.1:4001> INSERT INTO users(name, email) VALUES("Alice", "alice@example.com")
1 row affected (0.000117 sec)

127.0.0.1:4001> SELECT * FROM users
+----+-------+---------------------+
| id | name  | email               |
+----+-------+---------------------+
| 1  | Alice | alice@example.com   |
+----+-------+---------------------+

127.0.0.1:4001> UPDATE users SET email="new@example.com" WHERE id=1
1 row affected (0.000089 sec)

127.0.0.1:4001> DELETE FROM users WHERE id=1
1 row affected (0.000067 sec)
```

### Dot Commands

rqlite shell supports special dot commands for cluster management and diagnostics:

| Command | Description |
|---------|-------------|
| `.help` | Show help message |
| `.exit` or `.quit` | Exit the program |
| `.schema` | Show CREATE statements for all tables |
| `.tables` | List names of all tables |
| `.indexes` | Show names of all indexes |
| `.nodes` | Show connection status of all nodes in cluster |
| `.status` | Show status and diagnostic information |
| `.ready` | Show ready status for connected node |
| `.backup <file>` | Write database backup to SQLite file |
| `.dump <file>` | Dump database in SQL text format to file |
| `.restore <file>` | Restore database from SQLite file or dump |
| `.consistency [none\|weak\|strong]` | Show or set read consistency level |
| `.expvar` | Show Go runtime expvar information |
| `.sysdump <file>` | Dump system diagnostics to file |

### Using Dot Commands

```bash
# List all tables
127.0.0.1:4001> .tables
users
products
orders

# View schema
127.0.0.1:4001> .schema
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)

# Show cluster nodes
127.0.0.1:4001> .nodes
1: api_addr: http://localhost:4001 addr: localhost:4002 voter: true reachable: true leader: true id: 1
2: api_addr: http://localhost:4003 addr: localhost:4004 voter: true reachable: true leader: false id: 2
3: api_addr: http://localhost:4005 addr: localhost:4006 voter: true reachable: true leader: false id: 3

# Check node status
127.0.0.1:4001> .status
{
  "db": {
    "db_size": 32768,
    "file_format_version": 4,
    "freelist_count": 0
  },
  "raft": {
    "applied_index": 156,
    "commit_index": 156,
    "last_log_index": 156,
    "leader_addr": "localhost:4002",
    "state": "Leader"
  }
}

# Create backup
127.0.0.1:4001> .backup /tmp/backup.sqlite3
backup file written successfully

# Set read consistency to strong
127.0.0.1:4001> .consistency strong
Read consistency level is now: strong
```

## Command History

The shell stores command history in `~/.rqlite_history`:

```bash
# Default: 100 commands stored
# Custom history size
export RQLITE_HISTFILESIZE=500

# Disable history
export RQLITE_HISTFILESIZE=0
```

## Read Consistency Levels

Set consistency level for queries:

```bash
# None (fastest, may read stale data from follower)
127.0.0.1:4001> .consistency none

# Weak (may read slightly stale data)
127.0.0.1:4001> .consistency weak

# Strong (reads from leader, ensures freshness)
127.0.0.1:4001> .consistency strong
```

## Removing Nodes

Remove a node from the cluster:

```bash
# Remove node by ID
127.0.0.1:4001> .remove 3

# Node removed successfully
```

**Warning:** Only remove nodes that are decommissioned or failed permanently. Ensure you have quorum before removing nodes.

## Working with Large Results

### Pager Configuration

```bash
# Disable pager for large outputs
set PAGER=cat

# Or use less with specific options
set PAGER="less -S"
```

### Limiting Results

```bash
# Use LIMIT in queries
SELECT * FROM users LIMIT 100

# Paginate results
SELECT * FROM users ORDER BY id LIMIT 100 OFFSET 0
SELECT * FROM users ORDER BY id LIMIT 100 OFFSET 100
```

## Tips and Tricks

### Quick Database Inspection

```bash
# Connect and immediately list tables
rqlite 127.0.0.1:4001 << EOF
.tables
.schema
.quit
EOF
```

### Export Schema Only

```bash
rqlite 127.0.0.1:4001 << EOF
.schema > schema.sql
.quit
EOF
```

### Batch Operations

```bash
# Execute multiple commands from file
rqlite 127.0.0.1:4001 < commands.txt

# Where commands.txt contains:
# CREATE TABLE ...
# INSERT INTO ...
# SELECT ...
```

### Alternative Hosts for High Availability

```bash
# Specify fallback hosts if primary is unavailable
rqlite -a "host1:4001,host2:4001,host3:4001"
```

## Troubleshooting

### Connection Issues

```bash
# Check if node is responding
curl http://127.0.0.1:4001/status

# Verify network connectivity
telnet 127.0.0.1 4001

# Check for firewall rules
sudo ufw status
```

### Authentication Errors

```bash
# Provide credentials
rqlite -H example.com -u admin:password

# Use HTTPS with CA certificate
rqlite -H example.com -s https -c /path/to/ca.crt
```

## Next Steps

- Learn the [HTTP API](04-api.md) for programmatic access
- Set up [clustering](03-clustering.md) for production
- Configure [backups](05-backup-restore.md) for data protection
- Enable [security](08-security.md) for production deployments
