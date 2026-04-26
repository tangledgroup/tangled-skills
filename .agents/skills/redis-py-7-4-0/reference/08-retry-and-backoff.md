# Retry and Backoff

## Retry Configuration

Configure retry behavior with a `Retry` instance and backoff strategy:

```python
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis import Redis

retry = Retry(ExponentialBackoff(), 3)
r = Redis(host='localhost', port=6379, retry=retry)
```

Default retry (when no `retry` is provided):

- Backoff: `ExponentialWithJitterBackoff(base=1, cap=10)`
- Retries: 3
- Default retried errors: `ConnectionError`, `TimeoutError`, built-in `TimeoutError`

## Adding Custom Retryable Errors

Use `retry_on_error` to add additional exceptions to retry on:

```python
from redis.exceptions import BusyLoadingError, RedisError

retry = Retry(ExponentialBackoff(), 3)
r = Redis(
    host='localhost', port=6379,
    retry=retry,
    retry_on_error=[BusyLoadingError, RedisError]
)
```

## Backoff Strategies

Available backoff classes in `redis.backoff`:

**ConstantBackoff** — Fixed delay between retries:

```python
from redis.backoff import ConstantBackoff
backoff = ConstantBackoff(1.0)  # 1 second between retries
```

**ExponentialBackoff** — Exponentially increasing delay:

```python
from redis.backoff import ExponentialBackoff
backoff = ExponentialBackoff(base=0.008, cap=0.512)
```

**ExponentialWithJitterBackoff** — Exponential with random jitter (default):

```python
from redis.backoff import ExponentialWithJitterBackoff
backoff = ExponentialWithJitterBackoff(base=1, cap=10)
```

**FullJitterBackoff** — Full randomization within bounds:

```python
from redis.backoff import FullJitterBackoff
backoff = FullJitterBackoff(cap=0.512, base=0.008)
```

**EqualJitterBackoff** — Equal split between jitter and base:

```python
from redis.backoff import EqualJitterBackoff
backoff = EqualJitterBackoff(cap=0.512, base=0.008)
```

**DecorrelatedJitterBackoff** — AWS-style decorrelated jitter:

```python
from redis.backoff import DecorrelatedJitterBackoff
backoff = DecorrelatedJitterBackoff(cap=0.512, base=0.008)
```

**NoBackoff** — No delay between retries:

```python
from redis.backoff import NoBackoff
backoff = NoBackoff()
```

## Retry in Cluster Mode

Cluster retry works differently from standalone:

```python
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.cluster import RedisCluster

rc = RedisCluster(
    host='localhost', port=6379,
    retry=Retry(ExponentialBackoff(), 6)
)
```

In cluster mode, the retry object determines how many times to retry cluster-level operations (topology refresh, node reconnection). When a `ConnectionError` occurs:

1. The client triggers a cluster topology update
2. Removes the failed node from startup nodes
3. Re-initializes the cluster map
4. Retries the command up to the configured limit

The deprecated `cluster_error_retry_attempts` parameter is ignored when `retry` is provided.

## Customizing Supported Errors

Override which errors trigger retries:

```python
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError

retry = Retry(
    ExponentialBackoff(),
    retries=5,
    supported_errors=(ConnectionError, TimeoutError)
)
```
