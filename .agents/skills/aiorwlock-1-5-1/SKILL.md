---
name: aiorwlock-1-5-1
description: Async read-write lock implementation for Python asyncio providing concurrent reader access and exclusive writer access. Use when building async applications requiring fine-grained synchronization where multiple readers can access shared data simultaneously but writers need exclusive access.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - asyncio
  - concurrency
  - synchronization
  - read-write-lock
  - python
category: development
required_environment_variables: []
---

# aiorwlock-1.5.1

Async read-write lock for Python asyncio that maintains a pair of associated locks: one for read-only operations and one for writing. Multiple reader tasks can hold the read lock simultaneously, while the write lock is exclusive. Ideal for scenarios where data is frequently read but infrequently modified.

## When to Use

- Building async applications requiring concurrent access to shared resources
- Implementing caches or collections that are read more often than written
- Needing fine-grained synchronization in asyncio event loops
- Requiring multiple readers but exclusive writer access patterns
- Migrating from threading.RWLock to async equivalents

## Installation

```bash
pip install aiorwlock==1.5.1
```

**Requirements:** Python 3.9+

## Quick Start

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    # Acquire reader lock - multiple coroutines can hold simultaneously
    async with rwlock.reader_lock:
        print('Reading shared data')
        await asyncio.sleep(0.1)

    # Acquire writer lock - exclusive access
    async with rwlock.writer_lock:
        print('Writing to shared data')
        await asyncio.sleep(0.1)


asyncio.run(main())
```

## Core Concepts

### Reader-Writer Semantics

The RWLock provides two separate lock objects:

- **`reader_lock`** (or `reader`): Shared lock for read operations. Multiple tasks can hold this lock simultaneously.
- **`writer_lock`** (or `writer`): Exclusive lock for write operations. Only one task can hold this lock at a time.

### Lock Behavior

| Scenario | Reader Lock | Writer Lock |
|----------|-------------|-------------|
| No locks held | Available | Available |
| One reader holds | Available to other readers | Blocked |
| Multiple readers hold | Available to other readers | Blocked |
| Writer holds | Blocked | Blocked (unless same task) |

### Recursion Support

**Reader lock:** Supports recursive acquisition by the same task. A task holding the reader lock can acquire it again multiple times.

**Writer lock:** Supports recursive acquisition by the same task. A task holding the writer lock can acquire it again.

**Cross-lock recursion:** A task holding the writer lock can acquire the reader lock, but **cannot upgrade** from reader to writer (raises `RuntimeError`).

## Usage Patterns

### Basic Read-Write Pattern

```python
import asyncio
import aiorwlock


class SharedCache:
    def __init__(self):
        self._data = {}
        self._rwlock = aiorwlock.RWLock()

    async def get(self, key):
        """Read operation - multiple concurrent readers allowed"""
        async with self._rwlock.reader_lock:
            return self._data.get(key)

    async def set(self, key, value):
        """Write operation - exclusive access required"""
        async with self._rwlock.writer_lock:
            self._data[key] = value

    async def update_all(self, new_data):
        """Complex write operation"""
        async with self._rwlock.writer_lock:
            self._data.clear()
            self._data.update(new_data)


# Usage
cache = SharedCache()

async def readers():
    for i in range(5):
        value = await cache.get('key')
        print(f'Reader {i}: {value}')


async def writer():
    await asyncio.sleep(0.1)
    await cache.set('key', 'new_value')


asyncio.run(asyncio.gather(readers(), writer()))
```

### Manual Acquire/Release

For more control over lock lifecycle:

```python
import aiorwlock


async def controlled_access():
    rwlock = aiorwlock.RWLock()

    # Manual acquire
    await rwlock.reader_lock.acquire()
    try:
        # Critical section
        process_data()
    finally:
        # Always release in finally block
        rwlock.reader_lock.release()
```

### Low-Level API

Direct access to core methods:

```python
import aiorwlock


async def low_level_usage():
    rwlock = aiorwlock.RWLock()

    # Acquire reader lock
    await rwlock.reader_lock.acquire()
    try:
        # Check lock status
        if rwlock.reader_lock.locked:
            print('Reader lock is held')

        # Recursive acquisition (allowed)
        await rwlock.reader_lock.acquire()
    finally:
        # Must release same number of times
        rwlock.reader_lock.release()
        rwlock.reader_lock.release()

    # Acquire writer lock
    await rwlock.writer_lock.acquire()
    try:
        if rwlock.writer_lock.locked:
            print('Writer lock is held')
    finally:
        rwlock.writer_lock.release()
```

### Writer Priority Pattern

When writers should not starve behind continuous readers:

```python
import asyncio
import aiorwlock


async def writer_priority_example():
    rwlock = aiorwlock.RWLock()
    read_count = 0
    write_count = 0

    async def reader(reader_id):
        nonlocal read_count
        for _ in range(10):
            async with rwlock.reader_lock:
                read_count += 1
                await asyncio.sleep(0.01)  # Simulate read work

    async def writer(writer_id):
        nonlocal write_count
        for _ in range(5):
            async with rwlock.writer_lock:
                write_count += 1
                await asyncio.sleep(0.02)  # Simulate write work

    # Start readers and writers concurrently
    await asyncio.gather(
        *[reader(i) for i in range(3)],
        *[writer(i) for i in range(2)]
    )

    print(f'Reads: {read_count}, Writes: {write_count}')
```

## Performance Configuration

### Fast Path Mode

By default, RWLock yields control after acquiring the lock to allow other waiting tasks to proceed. This prevents starvation but adds overhead.

**Enable fast mode for minor speedup** when you're certain your locked code contains context switches (`await`, `async with`, `async for`):

```python
import aiorwlock


# Fast path - no automatic yield after acquire
rwlock = aiorwlock.RWLock(fast=True)


# Default mode - yields after acquire (safer)
rwlock_safe = aiorwlock.RWLock(fast=False)  # or just RWLock()
```

**When to use `fast=True`:**
- Locked sections contain `await` statements
- You need maximum performance
- You understand the starvation implications

**When to use default (`fast=False`):**
- Locked sections may not have context switches
- You want safer, more predictable behavior
- Writer starvation is a concern

## Advanced Patterns

### Reader-to-Writer Transition

Cannot upgrade from reader to writer directly. Must release and re-acquire:

```python
import aiorwlock


async def safe_upgrade_pattern():
    rwlock = aiorwlock.RWLock()

    # Read first
    async with rwlock.reader_lock:
        value = await read_data()

    # Release reader lock, then acquire writer lock
    # Cannot do: await rwlock.writer_lock.acquire() while holding reader
    async with rwlock.writer_lock:
        await write_data(value)


# This raises RuntimeError:
async def unsafe_upgrade():
    rwlock = aiorwlock.RWLock()

    async with rwlock.reader_lock:
        # This will raise RuntimeError
        await rwlock.writer_lock.acquire()  # Cannot upgrade!
```

### Writer-to-Reader Transition

Allowed - writer can acquire reader lock (nested):

```python
import aiorwlock


async def writer_to_reader():
    rwlock = aiorwlock.RWLock()

    async with rwlock.writer_lock:
        await write_data()

        # This is allowed - same task can acquire reader while holding writer
        async with rwlock.reader_lock:
            read_result = await read_data()


asyncio.run(writer_to_reader())
```

### Multiple Concurrent Readers

Demonstrating true concurrent reads:

```python
import asyncio
import aiorwlock


async def concurrent_readers_demo():
    rwlock = aiorwlock.RWLock()
    active_readers = []

    async def reader(reader_id):
        async with rwlock.reader_lock:
            active_readers.append(reader_id)
            print(f'Reader {reader_id} acquired lock. Active readers: {len(active_readers)}')
            await asyncio.sleep(0.1)
            active_readers.remove(reader_id)

    # Launch 5 readers simultaneously
    await asyncio.gather(*[reader(i) for i in range(5)])


asyncio.run(concurrent_readers_demo())
# Output shows multiple readers holding lock simultaneously
```

### Event Loop Compatibility

RWLock binds to the event loop where it's first used. Creating locks outside async functions is supported in v1.4.0+:

```python
import asyncio
import aiorwlock


# Lock can be created outside async context (v1.4.0+)
rwlock = aiorwlock.RWLock()


async def task1():
    async with rwlock.reader_lock:
        await process_data()


async def task2():
    async with rwlock.writer_lock:
        await update_data()


# Both tasks use same lock instance
asyncio.run(asyncio.gather(task1(), task2()))
```

**Note:** Lock must be used with the same event loop. Cross-event-loop usage raises `RuntimeError`.

## Error Handling

### Common Errors

**Releasing unacquired lock:**

```python
import aiorwlock


async def release_error():
    rwlock = aiorwlock.RWLock()

    # Raises RuntimeError: Cannot release an un-acquired lock
    try:
        rwlock.reader_lock.release()
    except RuntimeError as e:
        print(f'Error: {e}')
```

**Task mismatch (acquire in one task, release in another):**

```python
import asyncio
import aiorwlock


async def task_mismatch_error():
    rwlock = aiorwlock.RWLock()

    async def acquirer():
        await rwlock.reader_lock.acquire()
        # Cannot transfer to another task for release

    async def releaser():
        # Raises RuntimeError if called from different task
        rwlock.reader_lock.release()

    await acquirer()
    try:
        await releaser()
    except RuntimeError as e:
        print(f'Error: {e}')
```

**Reader-to-writer upgrade attempt:**

```python
import aiorwlock


async def upgrade_error():
    rwlock = aiorwlock.RWLock()

    async with rwlock.reader_lock:
        # Raises RuntimeError: Cannot upgrade RWLock from read to write
        try:
            await rwlock.writer_lock.acquire()
        except RuntimeError as e:
            print(f'Error: {e}')
```

### Cancellation Safety

RWLock handles cancellation properly. If a task is cancelled while waiting for or holding a lock, the lock state is cleaned up correctly:

```python
import asyncio
import aiorwlock


async def cancellation_safe():
    rwlock = aiorwlock.RWLock()

    async def cancellable_reader():
        try:
            async with rwlock.reader_lock:
                await asyncio.sleep(10)  # Will be cancelled
        except asyncio.CancelledError:
            print('Reader cancelled, lock released properly')
            raise

    task = asyncio.create_task(cancellable_reader())
    await asyncio.sleep(0.1)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    # Lock is available for other tasks
    async with rwlock.writer_lock:
        print('Writer acquired lock after reader cancellation')


asyncio.run(cancellation_safe())
```

## Status Inspection

### Check Lock State

```python
import aiorwlock


async def inspect_locks():
    rwlock = aiorwlock.RWLock()

    print(rwlock)  # <RWLock: <ReaderLock: [unlocked]> <WriterLock: [unlocked]>>

    async with rwlock.reader_lock:
        print(rwlock.reader_lock.locked)  # True
        print(rwlock.writer_lock.locked)  # False
        print(rwlock)  # Shows locked status

    async with rwlock.writer_lock:
        print(rwlock.writer_lock.locked)  # True
        print(rwlock.reader_lock.locked)  # False
```

## Troubleshooting

### Writer Starvation

**Symptom:** Writers never acquire lock despite being queued.

**Cause:** Continuous stream of readers keeps acquiring the reader lock before writers can proceed.

**Solution:** Ensure reader operations contain `await` statements to yield control:

```python
# Bad - no yield point
async def bad_reader():
    async with rwlock.reader_lock:
        result = compute_heavy()  # No await, blocks writers


# Good - yields control
async def good_reader():
    async with rwlock.reader_lock:
        result = await compute_heavy_async()  # Yields to event loop
```

### Deadlock Prevention

**Rule 1:** Always release locks in the same task that acquired them.

**Rule 2:** Never upgrade from reader to writer without releasing first.

**Rule 3:** Use consistent lock ordering when holding multiple locks.

**Rule 4:** Set timeouts for long-held locks in production code:

```python
import asyncio


async def timed_lock_acquire(lock, timeout):
    """Acquire lock with timeout"""
    async def _acquire():
        await lock.acquire()

    try:
        await asyncio.wait_for(_acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        print(f'Failed to acquire lock within {timeout}s')
        raise
    finally:
        try:
            lock.release()
        except RuntimeError:
            pass  # Lock was never acquired


async def safe_operation():
    rwlock = aiorwlock.RWLock()

    async with timed_lock_acquire(rwlock.writer_lock, timeout=5.0):
        await critical_operation()
```

### Cross-Event-Loop Issues

**Symptom:** `RuntimeError: RWLock is bound to a different event loop`

**Cause:** Lock created in one event loop context, used in another.

**Solution:** Create locks within the same event loop context where they'll be used:

```python
# Bad - lock may bind to wrong loop
rwlock = aiorwlock.RWLock()  # Created outside async context


async def worker():
    # If called from different loop, raises RuntimeError
    async with rwlock.reader_lock:
        pass


# Good - create lock within the async context
async def main():
    rwlock = aiorwlock.RWLock()  # Binds to current loop

    async with rwlock.reader_lock:
        await process()


asyncio.run(main())
```

## Version Information

```python
import aiorwlock

print(aiorwlock.__version__)  # '1.5.1'
```

### Version 1.5.1 Changes (2026-02-20)

- Fixed cross-event-loop race condition in lock acquisition
- Fixed deadlock that could occur when tasks are cancelled
- Implemented `__slots__` for memory efficiency

### Python Version Support

- Python 3.9, 3.10, 3.11, 3.12, 3.13

## References

- **Source:** https://github.com/aio-libs/aiorwlock
- **Documentation:** https://github.com/aio-libs/aiorwlock/blob/v1.5.1/README.rst
- **Changelog:** https://github.com/aio-libs/aiorwlock/blob/v1.5.1/CHANGES.rst
- **Tests:** https://github.com/aio-libs/aiorwlock/tree/v1.5.1/tests
- **License:** Apache-2.0
