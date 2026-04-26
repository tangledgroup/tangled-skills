# Pipelines and Transactions

## Basic Pipeline

Pipelines buffer multiple commands and send them in a single round-trip, dramatically reducing network latency:

```python
r = redis.Redis()
pipe = r.pipeline()
pipe.set('foo', 'bar')
pipe.get('bing')
results = pipe.execute()
# [True, b'baz']
```

Chaining syntax — each buffered command returns the pipeline:

```python
pipe.set('foo', 'bar').sadd('faz', 'baz').incr('auto_number').execute()
# [True, True, 6]
```

## Context Manager

Use `with` for automatic cleanup:

```python
with r.pipeline() as pipe:
    pipe.set('key1', 'val1')
    pipe.set('key2', 'val2')
    results = pipe.execute()
```

## Transactions (MULTI/EXEC)

By default, pipelines wrap commands in `MULTI`/`EXEC` for atomic execution. Disable with `transaction=False`:

```python
# Atomic transaction (default)
pipe = r.pipeline(transaction=True)

# Batching only — no MULTI/EXEC
pipe = r.pipeline(transaction=False)
```

## WATCH for Optimistic Locking

`WATCH` monitors keys before a transaction. If any watched key changes, the transaction is canceled and `WatchError` is raised:

```python
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch('SEQUENCE-KEY')
            current_value = pipe.get('SEQUENCE-KEY')
            next_value = int(current_value) + 1
            pipe.multi()  # Start buffering with MULTI
            pipe.set('SEQUENCE-KEY', next_value)
            pipe.execute()
            break
        except redis.WatchError:
            continue  # Retry on conflict
```

When using `WATCH`, the pipeline binds to a single connection. Always call `reset()` to return it to the pool (automatic when used as a context manager).

## Transaction Helper

`Redis.transaction()` handles WATCH retry boilerplate:

```python
def client_side_incr(pipe):
    current_value = pipe.get('SEQUENCE-KEY')
    next_value = int(current_value) + 1
    pipe.multi()
    pipe.set('SEQUENCE-KEY', next_value)

result = r.transaction(client_side_incr, 'SEQUENCE-KEY')
# [True]
```

The callable receives the pipeline as its first argument, followed by keys to WATCH. Always call `pipe.multi()` before write commands in the callable.

## Pipelines in Cluster Mode

Cluster pipelines group commands by node and execute in parallel:

```python
rc = redis.cluster.RedisCluster()
with rc.pipeline() as pipe:
    pipe.set('foo', 'v1').set('bar', 'v2').execute()
```

Responses maintain insertion order. Only key-based commands are supported in cluster pipelines.
