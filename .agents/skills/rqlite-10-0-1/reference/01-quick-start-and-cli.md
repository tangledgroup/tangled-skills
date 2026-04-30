# Quick Start & CLI

## Starting a Single Node

The quickest way to get running is to download a pre-built release binary from the [GitHub releases page](https://github.com/rqlite/rqlite/releases/latest). Releases are available for **Linux**, **macOS**, and **Windows**.

```bash
rqlited -node-id=1 data/
```

`data/` is the path to a directory rqlite will use for storage. Once launched, rqlite listens on `http://localhost:4001`.

### Docker

Docker images are available for a variety of platforms and are mirrored to ghcr.io:

```bash
docker run -p 4001:4001 rqlite/rqlite
# or
docker pull ghcr.io/rqlite/rqlite
```

### Homebrew (macOS)

```bash
brew install rqlite
```

### Windows

Download the Windows release from the [GitHub releases page](https://github.com/rqlite/rqlite/releases). Top-of-tree builds are also available from AppVeyor.

## What's Included?

An rqlite release includes two key binaries:

- `rqlited`: the actual rqlite server
- `rqlite`: a command-line tool for interacting with rqlite

Depending on the packaging process, a simple benchmarking tool, `rqbench`, may also be included.

## Inserting Records

Use the rqlite shell to create tables and insert data using standard SQLite syntax:

```
$ rqlite
127.0.0.1:4001> CREATE TABLE foo (id INTEGER NOT NULL PRIMARY KEY, name TEXT)
1 row affected (0.000668 sec)
127.0.0.1:4001> .schema
+-----------------------------------------------------------------------------+
| sql                                                                         |
+-----------------------------------------------------------------------------+
| CREATE TABLE foo (id INTEGER NOT NULL PRIMARY KEY, name TEXT)               |
+-----------------------------------------------------------------------------+
127.0.0.1:4001> INSERT INTO foo(name) VALUES("fiona")
1 row affected
127.0.0.1:4001> SELECT * FROM foo
+----+-------+
| id | name  |
+----+-------+
| 1  | fiona |
+----+-------+
```

## Forming a Cluster

You don't need to deploy a cluster to use rqlite well, but running multiple nodes means you'll have a fault-tolerant system. Start two more nodes to tolerate failure of a single node:

```bash
rqlited -node-id 2 -http-addr localhost:4003 -raft-addr localhost:4004 -join localhost:4002 data2/
rqlited -node-id 3 -http-addr localhost:4005 -raft-addr localhost:4006 -join localhost:4002 data3/
```

Check the cluster:

```
127.0.0.1:4001> .nodes
1:
  api_addr: http://localhost:4001
  addr: localhost:4002
  voter: true
  reachable: true
  leader: true
  id: 1
2:
  api_addr: http://localhost:4003
  addr: localhost:4004
  voter: true
  reachable: true
  leader: false
  id: 2
3:
  api_addr: http://localhost:4005
  addr: localhost:4006
  voter: true
  reachable: true
  leader: false
  id: 3
```

## rqlite Shell

The `rqlite` command-line tool connects to an rqlite node and provides interactive SQL access. Consult the [SQLite query language documentation](https://www.sqlite.org/lang.html) for full details on supported SQL syntax.

### Shell Options

```
$ rqlite -h
Options:

  -h, --help                    display help information
  -a, --alternatives            comma separated list of 'host:port' pairs to use as fallback
  -s, --scheme[=http]           protocol scheme (http or https)
  -H, --host[=127.0.0.1]        rqlited host address
  -p, --port[=4001]             rqlited host port
  -P, --prefix[=/]              rqlited HTTP URL prefix
  -i, --insecure[=false]        do not verify rqlited HTTPS certificate
  -c, --ca-cert                 path to trusted X.509 root CA certificate
  -u, --user                    set basic auth credentials in form username:password
  -v, --version                 display CLI version
```

### Shell Commands

```
127.0.0.1:4001> .help
.backup <file>                      Write database backup to SQLite file
.consistency [none|weak|strong]     Show or set read consistency level
.dump <file>                        Dump the database in SQL text format to a file
.exit                               Exit this program
.expvar                             Show expvar (Go runtime) information for connected node
.help                               Show this message
.indexes                            Show names of all indexes
.nodes                              Show connection status of all nodes in cluster
.ready                              Show ready status for connected node
.remove <raft ID>                   Remove a node from the cluster
.restore <file>                     Restore the database from a SQLite database file or dump file
.schema                             Show CREATE statements for all tables
.status                             Show status and diagnostic information for connected node
.sysdump <file>                     Dump system diagnostics to a file for offline analysis
.tables                             List names of tables
```

### Connecting to Remote Hosts

```bash
$ rqlite -H 192.168.0.1
192.168.0.1:4001>
```

### Command History

Command history is stored and reloaded between sessions in a hidden file named `.rqlite_history` in the user's home directory. By default 100 previous commands are stored, though this can be set via the environment variable `RQLITE_HISTFILESIZE`. Set it to 0 to disable history file writing.

## UI Applications

### Built-in Console Application

rqlite serves a built-in console app at `http://localhost:4001/console` by default. Adjust the address if running on a different hostname or port.

### Third-Party Applications

- [Dataflare](https://dataflare.app)
- [LibSQL Studio](https://libsqlstudio.com/)
