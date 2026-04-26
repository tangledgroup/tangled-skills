# RESP3 Features

## Protocol Selection

RESP3 is the default from redis-py 8.0+. For earlier versions, enable explicitly:

```python
import redis
r = redis.Redis(host='localhost', port=6379, protocol=3)
```

URL scheme:

```python
r = redis.from_url('redis://localhost:6379?protocol=3')
```

Async with RESP3:

```python
import redis.asyncio as redis
r = redis.Redis(host='localhost', port=6379, protocol=3)
await r.ping()
```

Cluster with RESP3:

```python
from redis.cluster import RedisCluster, ClusterNode
r = RedisCluster(
    startup_nodes=[ClusterNode('localhost', 6379)],
    protocol=3
)
```

## Benefits of RESP3

- Faster — fewer type translations in the client
- New response types: doubles, true simple strings, maps, booleans, arrays
- Push notifications for out-of-band data
- Client-side caching support

## Push Notifications

RESP3 includes a push type for out-of-band messages. By default, clients log simple messages. Provide a custom handler:

```python
from redis import Redis

def our_func(message):
    if "This special thing happened" in message:
        raise IOError(f"This was the message:\n{message}")

r = Redis()
p = r.pubsub(push_handler_func=our_func)
```

## Client-Side Caching

Client-side caching uses application server memory to cache a subset of data. Available with RESP3 on sync clients only (standalone, cluster, and sentinel).

Enable with default configuration:

```python
import redis
from redis.cache import CacheConfig

r = redis.Redis(
    host='localhost', port=6379,
    cache_config=CacheConfig()
)
```

Custom cache implementation:

```python
from foo.bar import CacheImpl  # Must implement CacheInterface

r = redis.Redis(
    host='localhost', port=6379,
    cache=CacheImpl()
)
```

Custom implementations should conform to the `CacheInterface` in `redis.cache`.

## RESP2/RESP3 Response Unification

Starting with redis-py 8.0, command return types are unified across RESP2 and RESP3 protocols. The same command returns the same Python type regardless of protocol version.

Key changes for RESP2 users (redis-py 8.0+):

- **Sorted sets** — `(member, score)` tuples become `[member, score]` lists; scores are always `float`
- **Blocking pops** — `BLPOP`, `BRPOP` return lists instead of tuples
- **ZRANDMEMBER** with `withscores=True` returns nested structures
- **Custom `score_cast_func`** now receives `float` instead of raw bytes

```python
# redis-py 8.0+ (both RESP2 and RESP3)
r.zrange('myset', 0, -1, withscores=True)
# [[b'a', 1.0], [b'b', 2.0]] — list of lists, float scores

# redis-py 7.x RESP2 only
# [(b'a', 1), (b'b', 2)] — list of tuples, int scores
```

Approximately 84 commands are affected across core Redis, Search, JSON, TimeSeries, and Probabilistic modules.
