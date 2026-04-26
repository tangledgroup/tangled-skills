# Async Support

## Basic Async Client

Import from `redis.asyncio` — all commands are coroutine functions:

```python
import redis.asyncio as redis

client = redis.Redis()
print(await client.ping())  # True
await client.aclose()  # Explicit disconnect required
```

**Important:** Async clients require explicit `aclose()` to disconnect. There is no asyncio destructor magic method.

## Connection Patterns

Using `from_url` with async:

```python
import redis.asyncio as redis

r = await redis.from_url('redis://localhost')
await r.ping()
await r.aclose()
```

Shared connection pool:

```python
pool = redis.ConnectionPool.from_url('redis://localhost')
client1 = redis.Redis(connection_pool=pool)
client2 = redis.Redis(connection_pool=pool)

await client1.aclose()
await client2.aclose()
await pool.aclose()  # Close pool explicitly when shared
```

Exclusive pool ownership:

```python
pool = redis.ConnectionPool.from_url('redis://localhost')
client = redis.Redis.from_pool(pool)
await client.aclose()  # Pool closes automatically
```

RESP3 with async (default from redis-py 8.0+):

```python
client = redis.Redis(protocol=3)
await client.ping()
await client.aclose()
```

## Async Pipelines

Async pipelines buffer commands and execute atomically:

```python
import redis.asyncio as redis

r = await redis.from_url('redis://localhost')
async with r.pipeline(transaction=True) as pipe:
    ok1, ok2 = await (pipe.set('key1', 'value1')
                      .set('key2', 'value2')
                      .execute())
    assert ok1 and ok2
await r.aclose()
```

Non-transactional pipeline (batching without atomicity):

```python
async with r.pipeline(transaction=False) as pipe:
    results = await pipe.get('key1').get('key2').execute()
```

## Async Pub/Sub

Subscribe to channels:

```python
import asyncio
import redis.asyncio as redis

STOPWORD = "STOP"

async def reader(pubsub):
    while True:
        message = await pubsub.get_message(
            ignore_subscribe_messages=True, timeout=None
        )
        if message is not None:
            print(f"Received: {message}")
            if message['data'].decode() == STOPWORD:
                break

r = await redis.from_url('redis://localhost')
async with r.pubsub() as pubsub:
    await pubsub.subscribe('channel:1', 'channel:2')
    task = asyncio.create_task(reader(pubsub))
    await r.publish('channel:1', 'Hello')
    await r.publish('channel:1', STOPWORD)
    await task
await r.aclose()
```

Pattern-based subscription (glob-style):

```python
async with r.pubsub() as pubsub:
    await pubsub.psubscribe('channel:*')
```

## Context Managers

Use `async with` for pipelines and pubsub to ensure proper cleanup:

```python
async with r.pipeline() as pipe:
    await pipe.set('foo', 'bar').execute()

async with r.pubsub() as pubsub:
    await pubsub.subscribe('my-channel')
```
