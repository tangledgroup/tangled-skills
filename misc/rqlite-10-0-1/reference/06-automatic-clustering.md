# Automatic Clustering

All autoclustering methods are **idempotent**. If a node is configured to autocluster but is already part of an existing cluster, the autoclustering flags are effectively ignored. This simplifies automation — use the same startup configuration for all nodes regardless of current membership status.

> In examples below, each node uses the same addresses for listening and being contacted. If using Bridge Networks or similar, set `-http-adv-addr` and `-raft-adv-addr` to specify the addresses other nodes should use.

## Automatic Bootstrapping

Start all nodes simultaneously with identical configuration. Each node knows the network addresses of all others ahead of time:

```bash
# Node 1
rqlited -node-id=1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data

# Node 2
rqlited -node-id=2 -http-addr=$HOST2:4001 -raft-addr=$HOST2:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data

# Node 3
rqlited -node-id=3 -http-addr=$HOST3:4001 -raft-addr=$HOST3:4002 \
  -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002 data
```

`-bootstrap-expect` sets the number of nodes that must be available before bootstrapping commences. All launch commands must have the same values for `-bootstrap-expect` and `-join`.

**Docker:**

```bash
docker run rqlite/rqlite -bootstrap-expect=3 -join=$HOST1:4002,$HOST2:4002,$HOST3:4002
```

To grow the cluster after bootstrapping, launch more nodes with the exact same options. New nodes always attempt a normal join first before trying the bootstrap approach.

## DNS-Based Discovery

Nodes learn IP addresses by resolving a hostname via DNS instead of passing `-join` addresses:

```bash
rqlited -node-id=1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -disco-mode=dns -disco-config='{"name":"rqlite.cluster"}' -bootstrap-expect=3 data
```

Create a DNS A Record for `rqlite.cluster` that returns the IP addresses of all nodes. Each node assumes other nodes listen on the same Raft port.

### DNS SRV

DNS SRV records encode both hostnames and port numbers, allowing different Raft ports per node:

```bash
rqlited -node-id=$ID -http-addr=$HOST:4001 -raft-addr=$HOST:4002 \
  -disco-mode=dns-srv -disco-config='{"name":"rqlite.local","service":"rqlite-raft"}' \
  -bootstrap-expect=3 data
```

rqlite looks up SRV records at `_rqlite-raft._tcp.rqlite.local`.

## Consul-Based Discovery

Nodes use Consul's key-value store to share networking information:

```bash
# Node 1
rqlited -node-id=$ID1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -disco-key=rqlite1 -disco-mode=consul-kv -disco-config='{"address":"example.com:8500"}' data

# Node 2
rqlited -node-id=$ID2 -http-addr=$HOST2:4001 -raft-addr=$HOST2:4002 \
  -disco-key=rqlite1 -disco-mode=consul-kv -disco-config='{"address":"example.com:8500"}' data

# Node 3
rqlited -node-id=$ID3 -http-addr=$HOST3:4001 -raft-addr=$HOST3:4002 \
  -disco-key=rqlite1 -disco-mode=consul-kv -disco-config='{"address":"example.com:8500"}' data
```

The cluster Leader continually updates Consul with its address, so new nodes can join at any time even if the Leader changes. `-disco-key` allows running multiple rqlite clusters on a single Consul system (use different keys).

**Docker:**

```bash
docker run rqlite/rqlite -disco-mode=consul-kv -disco-config='{"address":"example.com:8500"}'
```

## etcd-Based Discovery

Similar to Consul, using etcd's key-value store:

```bash
# Node 1
rqlited -node-id=$ID1 -http-addr=$HOST1:4001 -raft-addr=$HOST1:4002 \
  -disco-key=rqlite1 -disco-mode=etcd-kv -disco-config='{"endpoints":["example.com:2379"]}' data

# Node 2
rqlited -node-id=$ID2 -http-addr=$HOST2:4001 -raft-addr=$HOST2:4002 \
  -disco-key=rqlite1 -disco-mode=etcd-kv -disco-config='{"endpoints":["example.com:2379"]}' data

# Node 3
rqlited -node-id=$ID3 -http-addr=$HOST3:4001 -raft-addr=$HOST3:4002 \
  -disco-key=rqlite1 -disco-mode=etcd-kv -disco-config='{"endpoints":["example.com:2379"]}' data
```

**Docker:**

```bash
docker run rqlite/rqlite -disco-mode=etcd-kv -disco-config='{"endpoints":["example.com:2379"]}'
```

## Discovery Configuration

`-disco-config` can be a JSON string or a path to a JSON config file. Supports environment variable expansion (variables starting with `$`).

Full configuration specifications:

- [Consul configuration](https://github.com/rqlite/rqlite-disco-clients/blob/main/consul/config.go)
- [etcd configuration](https://github.com/rqlite/rqlite-disco-clients/blob/main/etcd/config.go)
- [DNS configuration](https://github.com/rqlite/rqlite-disco-clients/blob/main/dns/config.go)
- [DNS SRV configuration](https://github.com/rqlite/rqlite-disco-clients/blob/main/dnssrv/config.go)

## Running Multiple Clusters

- **Consul/etcd:** Set `-disco-key` to a different value for each cluster
- **DNS:** Use a different domain name per cluster
