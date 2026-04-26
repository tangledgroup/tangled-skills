# Distributed Locking

## Basic Usage

The `Lock` class provides a shared, distributed lock using Redis:

```python
r = redis.Redis()
lock = r.lock('my-resource', timeout=10)
```

Parameters:

- `name` — Lock identifier (Redis key name)
- `timeout` — Maximum time the lock is held (seconds). After this, it auto-releases.
- `sleep` — Time between acquisition attempts (default: 0.1s)
- `blocking` — Whether to wait for the lock (default: `True`)
- `blocking_timeout` — Max time to wait for acquisition (seconds)

## Acquiring and Releasing

```python
lock = r.lock('my-resource', timeout=10, blocking_timeout=5)
acquired = lock.acquire()
if acquired:
    try:
        # Critical section
        do_work()
    finally:
        lock.release()
```

Non-blocking mode — returns immediately:

```python
lock = r.lock('my-resource', blocking=False)
if lock.acquire():
    try:
        do_work()
    finally:
        lock.release()
else:
    # Lock not available
    pass
```

## Context Manager

Recommended pattern for automatic release:

```python
with r.lock('my-resource', timeout=10, blocking_timeout=5) as lock:
    # Lock is acquired — do work here
    do_work()
# Lock automatically released on exit (even on exception)
```

## Extending Lock Time

Add more time to an active lock:

```python
lock.extend(additional_time=30)  # Add 30 seconds to existing TTL
lock.extend(additional_time=60, replace_ttl=True)  # Replace TTL with 60s
```

## Checking Lock State

```python
lock.locked()   # True if any process holds this lock
lock.owned()    # True if THIS lock instance holds it
```

## Reacquiring

Reset the TTL back to the original timeout:

```python
lock.reacquire()
```

## Token-Based Locks

Specify a custom token instead of auto-generated UUID:

```python
lock = r.lock('my-resource', timeout=10)
lock.acquire(token='my-custom-token')
```

The token must be a bytes object or an encodable string.
