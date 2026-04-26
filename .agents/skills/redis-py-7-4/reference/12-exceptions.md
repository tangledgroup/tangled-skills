# Exceptions

## Core Exception Hierarchy

All redis-py exceptions are in `redis.exceptions`:

**Connection errors:**

- `ConnectionError` — Failed to connect to Redis
- `TimeoutError` — Command timed out
- `BusyLoadingError` — Server is loading a dataset (RDB/AOF)
- `AuthenticationError` — AUTH failed
- `AuthenticationWrongNumberOfArgsError` — Wrong args for AUTH
- `AuthorizationError` — ACL authorization denied

**Cluster errors:**

- `ClusterError` — Generic cluster error
- `ClusterDownError` — Cluster is partially down (uncovered hash slots)
- `AskError` — Slot migration in progress, client should redirect
- `TryError` — Similar to ASK for slot imports
- `MovingError` — Slot has moved to another node
- `ClusterCrossSlotError` — Multi-key command with keys on different slots
- `MasterDownError` — Link with master is down

**Pipeline/transaction errors:**

- `WatchError` — WATCHed key was modified, transaction aborted
- `ExecAbortError` — EXEC failed (e.g., script error)
- `CrossSlotTransactionError` — Transaction keys span multiple slots in cluster
- `InvalidPipelineStack` — Unexpected response length on pipeline

**Lock errors:**

- `LockError` — Error acquiring or releasing a lock
- `LockNotOwnedError` — Trying to release a lock not owned by this instance

**Data errors:**

- `DataError` — Client-side data validation error
- `InvalidResponse` — Unexpected response from server
- `ResponseError` — Redis returned an error response
- `NoScriptError` — EVALSHA called but script not in cache

**Other:**

- `ChildDeadlockedError` — Child process deadlocked after fork()
- `RedisError` — Base class for all Redis errors
- `ExternalAuthProviderError` — External auth provider returned an error

## Handling Common Errors

Connection retry with backoff:

```python
from redis import Redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError

r = Redis(
    host='localhost', port=6379,
    retry=Retry(ExponentialBackoff(), 3),
    retry_on_error=[ConnectionError, TimeoutError]
)
```

Handling WATCH conflicts:

```python
from redis import WatchError

with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch('counter')
            value = int(pipe.get('counter') or 0)
            pipe.multi()
            pipe.set('counter', value + 1)
            pipe.execute()
            break
        except WatchError:
            continue  # Retry on conflict
```

Cluster topology changes:

```python
from redis.exceptions import ClusterDownError, AskError

try:
    rc.get('mykey')
except (ClusterDownError, AskError) as e:
    # Cluster is reorganizing — retry after brief delay
    import time
    time.sleep(0.1)
    rc.get('mykey')
```

Lock contention:

```python
from redis.exceptions import LockError, LockNotOwnedError

try:
    with r.lock('resource', timeout=10, blocking_timeout=5) as lock:
        do_critical_work()
except LockError:
    # Could not acquire lock within timeout
    handle_failure()
```
