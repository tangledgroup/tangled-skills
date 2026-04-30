# Monitoring

## Status API

rqlite serves diagnostic and statistical information at `/status`:

```bash
curl localhost:4001/status?pretty
```

The `pretty` parameter is optional and results in pretty-printed JSON. Output can be periodically written to a monitoring system.

Via CLI:

```
127.0.0.1:4001> .status
build:
  build_time: unknown
  commit: unknown
  version: 10
  branch: unknown
http:
  addr: 127.0.0.1:4001
  auth: disabled
node:
  start_time: 2025-01-01T00:00:00.000000000+00:00
  uptime: 16.963009139s
runtime:
  num_goroutine: 9
  version: go1.26
```

## Nodes API

Returns basic information for all nodes in the cluster, as seen by the receiving node. The node also checks whether it can actually connect to all other nodes:

```bash
# Basic format
curl localhost:4001/nodes?pretty

# Improved JSON format (easier for parsing)
curl localhost:4001/nodes?pretty&ver=2

# Include non-voting nodes
curl localhost:4001/nodes?nonvoters&pretty

# Custom timeout (default 30 seconds)
curl localhost:4001/nodes?timeout=5s
```

Via CLI:

```
127.0.0.1:4001> .nodes
```

## Leader API

Determine the cluster leader:

```bash
curl localhost:4001/leader?pretty
```

Response:

```json
{
    "id": "1",
    "api_addr": "http://localhost:4001",
    "addr": "localhost:4002",
    "version": "10",
    "voter": true,
    "reachable": true,
    "leader": true
}
```

Force a leadership election:

```bash
curl -XPOST http://localhost:4001/leader

# Or specify the new Leader
curl -XPOST http://localhost:4001/leader -H 'Content-Type: application/json' \
  -d '{"id": "node1"}'
```

Or via CLI: `.stepdown`

## Readiness Checks

rqlite serves a "ready" status at `/readyz`. Returns HTTP 200 if the node is ready to respond to database requests and cluster management operations:

```bash
curl localhost:4001/readyz
[+]node ok
[+]leader ok
[+]store ok
```

Check if the node is responsive regardless of Leader status:

```bash
curl localhost:4001/readyz?noleader
[+]node ok
```

### Sync Flag

Block until the node has received the log entry equal to the Leader's Commit Index:

```bash
curl localhost:4001/readyz?sync&timeout=5s
[+]node ok
[+]leader ok
[+]store ok
[+]sync ok
```

The timeout defaults to 30 seconds. If the receiving node is the Leader, this flag has no effect (the Leader is always caught up with itself).

> Strictly speaking, `readyz` indicates the database is ready for all write requests and all read requests with _Weak_ or _Strong_ consistency. A node can **always** respond to reads with _None_ consistency.

## expvar Support

rqlite exports [expvar](https://pkg.go.dev/expvar) information — mostly counters of various rqlite activity:

```bash
curl localhost:4001/debug/vars
```

Filter by key:

```bash
curl 'localhost:4001/debug/vars?key=http'
```

Via CLI: `.expvar`

## pprof Support

[pprof](https://golang.org/pkg/net/http/pprof/) profiling information is available by default:

```bash
curl localhost:4001/debug/pprof/cmdline
curl localhost:4001/debug/pprof/profile
curl localhost:4001/debug/pprof/symbol
```
