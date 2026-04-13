---
name: redis-py-7-4
description: Comprehensive Python client for Redis database and key-value store. Use when building Python applications requiring Redis connectivity, including standalone, cluster, sentinel, and async modes with support for all Redis commands, pipelines, pub/sub, Lua scripting, Redis modules (Bloom, JSON, Search, TimeSeries), RESP3 protocol, client-side caching, OpenTelemetry observability, connection pooling, retry logic, and distributed locking.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - redis
  - database
  - key-value-store
  - caching
  - async
  - clustering
  - pubsub
  - pipelines
  - lua-scripting
category: database
required_environment_variables:
  - name: REDIS_URL
    prompt: "What is your Redis connection URL?"
    help: "Redis connection string (e.g., redis://localhost:6379/0 or rediss:// for TLS)"
    required_for: "connecting to Redis server"
---

# redis-py 7.4 - Python Client for Redis

Comprehensive Python client library for Redis database and key-value store, supporting all Redis commands, cluster mode, sentinel high availability, async operations, pipelines, pub/sub messaging, Lua scripting, Redis modules (Bloom filters, JSON, Search, TimeSeries), RESP3 protocol with push notifications and client-side caching, native OpenTelemetry metrics collection, connection pooling, retry strategies, and distributed locking.

**redis-py 7.4 supports:** Python 3.10+, Redis 7.2-8.2

## When to Use

- Connecting to Redis standalone, cluster, or sentinel deployments
- Executing Redis commands (strings, hashes, lists, sets, sorted sets, streams)
- Implementing async Redis operations with asyncio
- Using Redis modules (Bloom filters, JSON, Search, TimeSeries)
- Building high-performance applications with pipelines and batching
- Implementing pub/sub messaging patterns
- Executing Lua scripts for atomic operations
- Enabling RESP3 protocol features (push notifications, client-side caching)
- Collecting observability metrics with OpenTelemetry
- Implementing distributed locks and optimistic locking
- Configuring connection pooling and retry strategies
- Working with Redis Cluster (sharding, slot management, read replicas)

## Installation

Install via pip:

```bash
# Basic installation
pip install redis

# With hiredis for faster performance (compiled parser)
pip install "redis[hiredis]"

# With xxhash for cluster support
pip install "redis[xxhash]"

# With OpenTelemetry support
pip install "redis[otel]"

# With OCSP/TLS verification
pip install "redis[ocsp]"

# With JWT authentication
pip install "redis[jwt]"

# With circuit breaker pattern
pip install "redis[circuit_breaker]"
```

## Quick Start

### Basic Connection

```python
import redis

# Connect to localhost:6379 (default)
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # True

# With response decoding to strings
r = redis.Redis(decode_responses=True)
r.set('foo', 'bar')
r.get('foo')  # 'bar' (str instead of b'bar')

# Using connection URL
r = redis.from_url('redis://localhost:6379/0')
r = redis.from_url('rediss://localhost:6380')  # TLS connection
```

### Async Connection

```python
import redis.asyncio as redis

# Async client
r = redis.Redis(host='localhost', port=6379)
await r.ping()  # True
await r.set('foo', 'bar')
result = await r.get('foo')  # b'bar'

# Async with URL
r = await redis.from_url('redis://localhost:6379/0')
```

### RESP3 Protocol

Enable RESP3 for better performance and new features (push notifications, client-side caching):

```python
import redis

# Sync RESP3 connection
r = redis.Redis(host='localhost', port=6379, protocol=3)
r.ping()  # PONG response with type info

# Async RESP3 connection
import redis.asyncio as redis
r = redis.Redis(host='localhost', port=6379, protocol=3)
await r.ping()
```

## Common Operations

### Strings

See [String Operations](references/01-core-commands.md) for complete reference.

```python
r = redis.Redis()

# Basic string operations
r.set('key', 'value')              # True
r.set('key', 'value', ex=3600)     # True (expires in 1 hour)
r.get('key')                        # b'value'
r.delete('key')                     # 1 (keys deleted)

# Increment/decrement
r.incr('counter')                   # 1
r.incrby('counter', 5)              # 6
r.decrby('counter', 2)              # 4

# Append to string
r.append('key', 'more')             # 7 (new length)
```

### Hashes

```python
r = redis.Redis()

# Set hash fields
r.hset('user:1', 'name', 'Alice')   # 1 (new fields created)
r.hset('user:1', mapping={'name': 'Alice', 'age': 30})  # 2

# Get hash fields
r.hget('user:1', 'name')            # b'Alice'
r.hgetall('user:1')                 # {b'name': b'Alice', b'age': b'30'}
r.hkeys('user:1')                   # [b'name', b'age']
r.hvals('user:1')                   # [b'Alice', b'30']

# Increment hash field (numeric)
r.hincrby('user:1', 'age', 1)       # 31
```

### Lists

See [List Operations](references/01-core-commands.md) for complete reference.

```python
r = redis.Redis()

# Push to list
r.lpush('mylist', 'one')            # 1 (length after push)
r.rpush('mylist', 'two')            # 2
r.rpush('mylist', 'three', 'four')  # 4

# Get from list
r.lrange('mylist', 0, -1)           # [b'one', b'two', b'three', b'four']
r.lindex('mylist', 0)               # b'one'
r.llen('mylist')                    # 4

# Pop from list
r.lpop('mylist')                    # b'one'
r.rpop('mylist')                    # b'four'
```

### Pipelines

See [Pipelines and Transactions](references/02-pipelines-transactions.md) for detailed examples.

```python
r = redis.Redis()

# Basic pipeline (batch commands, reduce round trips)
pipe = r.pipeline()
pipe.set('foo', 'bar')
pipe.get('foo')
pipe.incr('counter')
results = pipe.execute()  # [True, b'bar', 1]

# Chained pipeline syntax
results = (r.pipeline()
    .set('foo', 'bar')
    .get('foo')
    .incr('counter')
    .execute())

# Transactional pipeline (atomic execution)
pipe = r.pipeline(transaction=True)
pipe.multi()  # Explicit MULTI command
pipe.set('a', '1')
pipe.set('b', '2')
pipe.execute()  # [True, True]

# Optimistic locking with WATCH
def increment_counter(pipe):
    current = pipe.get('counter')
    pipe.multi()
    pipe.set('counter', int(current or 0) + 1)

r.transaction(increment_counter, 'counter')
```

### Pub/Sub

See [PubSub Messaging](references/03-pubsub-streams.md) for detailed examples.

```python
r = redis.Redis()

# Subscribe to channels
pubsub = r.pubsub()
pubsub.subscribe('channel-1', 'channel-2')

# Listen for messages
message = pubsub.get_message(timeout=1)
# {'type': 'subscribe', 'channel': b'channel-1', 'data': 1}

# Publish message from another connection
r.publish('channel-1', 'Hello!')  # Returns number of recipients

# Pattern subscription
pubsub.psubscribe('news:*')

# Unsubscribe
pubsub.unsubscribe()
```

## Reference Files

This skill uses progressive disclosure. The main file above covers common operations. For detailed information, see:

- [`references/01-core-commands.md`](references/01-core-commands.md) - Complete Redis command reference (strings, hashes, lists, sets, sorted sets, streams, hyperloglogs, geo, bitmaps)
- [`references/02-pipelines-transactions.md`](references/02-pipelines-transactions.md) - Pipelines, transactions, WATCH/CAS, cluster pipelines
- [`references/03-pubsub-streams.md`](references/03-pubsub-streams.md) - Pub/Sub messaging, Redis Streams (XADD, XREAD, XGROUP, consumer groups)
- [`references/04-connections-clustering.md`](references/04-connections-clustering.md) - Connection types, pools, SSL/TLS, Redis Cluster, Sentinel, async clients
- [`references/05-lua-scripting.md`](references/05-lua-scripting.md) - Lua scripting with EVAL/EVALSHA, script registration, cluster mode limitations
- [`references/06-redis-modules.md`](references/06-redis-modules.md) - Redis modules: Bloom filters (BF/CF), JSON, Search (FT.), TimeSeries (TS.)
- [`references/07-resp3-features.md`](references/07-resp3-features.md) - RESP3 protocol, push notifications, client-side caching (CSC)
- [`references/08-opentelemetry.md`](references/08-opentelemetry.md) - Native OpenTelemetry integration, metric groups, configuration
- [`references/09-locking.md`](references/09-locking.md) - Distributed locks (redis.lock.FairLock), lock timeouts, extensions, releases
- [`references/10-error-handling.md`](references/10-error-handling.md) - Exception hierarchy, retry strategies, backoff policies, connection errors
- [`references/11-advanced-topics.md`](references/11-advanced-topics.md) - Multi-database clients, threading safety, module commands, advanced patterns

## Troubleshooting

### Connection Issues

```python
# Check connection with timeout
r = redis.Redis(host='localhost', port=6379, socket_timeout=5, socket_connect_timeout=5)
try:
    r.ping()
except redis.ConnectionError as e:
    print(f"Cannot connect: {e}")
except redis.TimeoutError as e:
    print(f"Connection timeout: {e}")
```

### Authentication Errors

```python
# Password authentication
r = redis.Redis(host='localhost', password='mypassword')

# AUTH with username (Redis 6.0+)
r = redis.Redis(host='localhost', username='myuser', password='mypassword')

# Handle auth errors
try:
    r.ping()
except redis.AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Cluster Errors

```python
from redis.cluster import RedisCluster

try:
    rc = RedisCluster(host='localhost', port=6379)
    rc.get('key')
except redis.ClusterDownError as e:
    print(f"Cluster is down: {e}")
except redis.MovedError as e:
    print(f"Key moved to slot {e.slot_id} at {e.node_addr}")
except redis.AskError as e:
    print(f"Ask redirection to {e.node_addr}")
```

### Retry Configuration

See [Error Handling and Retries](references/10-error-handling.md) for complete retry strategies.

```python
from redis import Redis, Retry
from redis.backoff import ExponentialBackoff

# Configure retries with exponential backoff
retry = Retry(ExponentialBackoff(), 3)
r = Redis(host='localhost', port=6379, retry=retry)
```

## Performance Tips

1. **Use connection pooling**: Default pool size is 10 connections. Adjust for high concurrency:
   ```python
   pool = redis.ConnectionPool(max_connections=50)
   r = redis.Redis(connection_pool=pool)
   ```

2. **Enable hiredis**: Install `redis[hiredis]` for faster response parsing (compiled C parser).

3. **Use pipelines**: Batch commands to reduce network round trips.

4. **Enable RESP3**: Use `protocol=3` for better performance and type preservation.

5. **Decode responses**: Set `decode_responses=True` to avoid manual bytes decoding.

6. **Reuse clients**: Redis client instances are thread-safe (except PubSub/Pipeline objects).

## Version Compatibility

| redis-py version | Python versions | Redis versions |
|-----------------|----------------|----------------|
| 7.4.x | 3.10 - 3.14 | 7.2 - 8.2 |
| 6.0.x | 3.8 - 3.13 | 7.2 - current |
| 5.0.x | 3.7 - 3.12 | 5.0 - 7.4 |

## Important Notes

- **Thread safety**: Redis client instances are thread-safe. Connection pooling handles concurrent access. However, PubSub and Pipeline objects should not be shared between threads.
- **Database selection**: Don't use SELECT command with shared clients. Create separate client instances for different databases.
- **Cluster mode limitations**: Multi-key commands require keys on same slot (use hash tags `{tag}`). Lua scripting has limited support in cluster mode.
- **RESP3 requirement**: Client-side caching and push notifications require `protocol=3`.
- **Async vs sync**: Use `redis.asyncio` for async applications. Don't mix sync and async clients.

## Resources

- **Official Documentation**: https://redis.readthedocs.io/en/latest/
- **GitHub Repository**: https://github.com/redis/redis-py
- **Redis Commands Reference**: https://redis.io/commands
- **Changelog**: https://github.com/redis/redis-py/releases
- **Issue Tracker**: https://github.com/redis/redis-py/issues
