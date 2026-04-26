# Cluster Mode

## Creating a Cluster Client

redis-py provides `RedisCluster` for Redis Cluster deployments. At minimum, one startup node is needed for cluster discovery:

```python
from redis.cluster import RedisCluster as Redis

# Using host and port
rc = Redis(host='localhost', port=6379)
print(rc.get_nodes())

# Using URL
rc = Redis.from_url('redis://localhost:6379/0')

# Using ClusterNode objects
from redis.cluster import ClusterNode
nodes = [
    ClusterNode('localhost', 6379),
    ClusterNode('localhost', 6380),
]
rc = Redis(startup_nodes=nodes)
```

If none of the startup nodes are reachable, a `RedisClusterException` is raised.

## How It Works

On initialization, `RedisCluster` builds three caches:

- **Slots cache** — Maps all 16384 hash slots to their handling nodes
- **Nodes cache** — Contains `ClusterNode` objects with connection details
- **Commands cache** — Server-supported commands from `COMMAND` output

When executing a key-based command, the target node is determined internally by the key's hash slot. Non-key-based commands use a default node (randomly selected from primaries).

```python
# Key-based — routed to the node holding the key's slot
rc.set('foo1', 'bar1')
rc.set('foo2', 'bar2')
print(rc.get('foo1'))  # b'bar1'

# Non-key-based — executed on default node
rc.keys()
rc.ping()
```

## Specifying Target Nodes

Non-key-based commands accept `target_nodes` to control execution scope. Use the built-in node flags:

- `Redis.PRIMARIES` — All primary nodes
- `Redis.REPLICAS` — All replica nodes
- `Redis.ALL_NODES` — Every node in the cluster
- `Redis.RANDOM` — A single random node

```python
from redis.cluster import RedisCluster as Redis

# Run on all nodes
rc.cluster_meet('127.0.0.1', 6379, target_nodes=Redis.ALL_NODES)

# Ping all replicas
rc.ping(target_nodes=Redis.REPLICAS)

# Ping a random node
rc.ping(target_nodes=Redis.RANDOM)

# Get keys from all nodes
rc.keys(target_nodes=Redis.ALL_NODES)

# BGSAVE on all primaries
rc.bgsave(Redis.PRIMARIES)
```

Target specific nodes directly:

```python
node = rc.get_node('localhost', 6379)
rc.keys(target_nodes=node)

# Subset of primaries
subset = [n for n in rc.get_primaries() if n.port > 6378]
rc.info(target_nodes=subset)
```

## Cluster Pipelines

`ClusterPipeline` groups commands by target node and executes them in parallel:

```python
rc = RedisCluster()
with rc.pipeline() as pipe:
    pipe.set('foo', 'value1')
    pipe.set('bar', 'value2')
    pipe.get('foo')
    pipe.get('bar')
    print(pipe.execute())
    # [True, True, b'value1', b'value2']

# Chaining
pipe.set('foo1', 'bar1').get('foo1').execute()
# [True, b'bar1']
```

Responses are returned in the same order as sent. Note: cluster pipelines currently only support key-based commands.

## Default Node Management

```python
# Get current default node
default = rc.get_default_node()

# Change default node
rc.set_default_node(node)
```

## Direct Node Access

Access a specific node's Redis client directly (no cluster retry handling):

```python
cluster_node = rc.get_node(host='localhost', port=6379)
r = cluster_node.redis_connection
r.client_list()
```

## Known Limitations

- **Pub/Sub** — Limited support in cluster mode. Pub/Sub connections are bound to a single node.
- **Multi-key commands** — Keys must hash to the same slot, or use hash tags (`{user}:1000`, `{user}:2000`).
- **Lua scripting** — Only `EVAL` and `EVALSHA` supported; all keys must be on the same node. `EVAL_RO` and `EVALSHA_RO` are not supported.
