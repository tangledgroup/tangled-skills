---
name: aiorwlock-1-5-1
description: Async read-write lock for Python asyncio providing concurrent reader access and exclusive writer access. Use when building async applications requiring fine-grained synchronization where multiple readers can access shared data simultaneously but writers need exclusive access.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - asyncio
  - concurrency
  - synchronization
  - read-write-lock
category: library
external_references:
  - https://github.com/aio-libs/aiorwlock
  - https://pypi.org/project/aiorwlock/
---

# aiorwlock 1.5.1

## Overview

`aiorwlock` is a read-write lock implementation for Python's `asyncio`. An `RWLock` maintains a pair of associated locks — one for read-only (shared) operations and one for writing (exclusive). The read lock may be held simultaneously by multiple reader tasks, so long as no writer holds the lock. The write lock is exclusive and blocks all other readers and writers.

Whether a read-write lock improves performance over a mutual exclusion lock depends on the read-to-write ratio. Collections that are initially populated and then frequently read but infrequently modified are ideal candidates. If updates become frequent, the data spends most of its time exclusively locked with little concurrency gain.

**Important:** The task that acquires the lock must be the same task that releases it. Locking from one task and releasing from another raises `RuntimeError`.

Implementation is based on [Python issue 8800](http://bugs.python.org/issue8800). A formal TLA+ specification of the lock protocol is included in the repository.

## When to Use

- Building async applications with shared data that is read frequently but written rarely
- Implementing caches, registries, or configuration stores accessed by multiple async tasks
- Protecting data structures where concurrent reads are safe but writes need exclusivity
- Replacing `asyncio.Lock` when read-heavy workloads would benefit from concurrent reader access

## Core Concepts

### RWLock

The main class. Created with an optional `fast` parameter:

```python
import aiorwlock

rwlock = aiorwlock.RWLock()           # default: safe mode
rwlock = aiorwlock.RWLock(fast=True)  # fast path, no context switch on acquire
```

### Reader Lock (`reader_lock` / `reader`)

Shared access. Multiple tasks can hold the reader lock simultaneously. Accessed via `rwlock.reader_lock` or `rwlock.reader` (aliases).

### Writer Lock (`writer_lock` / `writer`)

Exclusive access. Only one task can hold the writer lock, and no readers are allowed while a writer holds the lock. Accessed via `rwlock.writer_lock` or `rwlock.writer` (aliases).

### Fast Mode

By default, `RWLock` switches context (yields) on every lock acquisition. This ensures fairness — other waiting tasks get a chance to acquire the lock even if the current holder has no `await` points.

Set `fast=True` to skip this yield for a minor speedup. Use only when you are certain your locked code contains context switch points (`await`, `async with`, `async for`).

### Event Loop Binding

The lock binds itself to the event loop of the first task that acquires it. If another event loop tries to use the same lock, a `RuntimeError` is raised. The lock can be created outside an async function (since v1.4.0) but must only be used within a single event loop.

## Usage Examples

### Context Manager (Recommended)

The idiomatic approach using `async with`:

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    # Multiple readers can hold the lock simultaneously
    async with rwlock.reader_lock:
        print("inside reader lock")
        await asyncio.sleep(0.1)

    # Writer gets exclusive access
    async with rwlock.writer_lock:
        print("inside writer lock")
        await asyncio.sleep(0.1)


asyncio.run(main())
```

### Manual Acquire/Release

Use `try/finally` to ensure the lock is always released:

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    # Reader lock
    await rwlock.reader_lock.acquire()
    try:
        print("inside reader lock")
        await asyncio.sleep(0.1)
    finally:
        rwlock.reader_lock.release()

    # Writer lock
    await rwlock.writer_lock.acquire()
    try:
        print("inside writer lock")
        await asyncio.sleep(0.1)
    finally:
        rwlock.writer_lock.release()


asyncio.run(main())
```

### Nested Locking (Writer then Reader)

A task holding the writer lock can also acquire the reader lock:

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    async with rwlock.writer_lock:
        # Writer holds exclusive access
        async with rwlock.reader_lock:
            # Reader also acquired by same task (reentrant)
            pass
        # Reader released, writer still held


asyncio.run(main())
```

### Upgrade from Read to Write Is Not Allowed

Attempting to acquire the writer lock while holding the reader lock raises `RuntimeError`:

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    async with rwlock.reader_lock:
        try:
            await rwlock.writer_lock.acquire()  # raises RuntimeError
        except RuntimeError as e:
            print(f"Cannot upgrade: {e}")


asyncio.run(main())
```

### Checking Lock State

Both reader and writer locks expose a `locked` property:

```python
import aiorwlock

rwlock = aiorwlock.RWLock()

print(rwlock.reader_lock.locked)   # False
print(rwlock.writer_lock.locked)   # False
```

### Concurrent Readers, Exclusive Writers

Multiple readers run concurrently; writers get exclusive access:

```python
import asyncio
import aiorwlock


async def reader(lock, name):
    async with lock.reader_lock:
        print(f"{name}: reading")
        await asyncio.sleep(0.1)


async def writer(lock, name):
    async with lock.writer_lock:
        print(f"{name}: writing")
        await asyncio.sleep(0.1)


async def main():
    rwlock = aiorwlock.RWLock()

    # Five readers run concurrently
    await asyncio.gather(*(reader(rwlock, f"R{i}") for i in range(5)))

    # Writers run one at a time
    await asyncio.gather(*(writer(rwlock, f"W{i}") for i in range(3)))


asyncio.run(main())
```

### Recursion Support

Both reader and writer locks support reentrant acquisition by the same task:

```python
import asyncio
import aiorwlock


async def main():
    rwlock = aiorwlock.RWLock()

    # Recursive reader lock
    async with rwlock.reader_lock:
        async with rwlock.reader_lock:
            print("nested reader lock")

    # Recursive writer lock
    async with rwlock.writer_lock:
        async with rwlock.writer_lock:
            print("nested writer lock")


asyncio.run(main())
```

Each acquisition must be matched by a release.

## API Reference

### `RWLock(*, fast: bool = False)`

Create a read-write lock.

- `fast` — When `True`, skip the context switch after acquiring the lock for a minor speedup. Default is `False` (safe mode with fairness guarantee).

### Properties

- `rwlock.reader_lock` — `_ReaderLock` instance for shared (read) access. Alias: `rwlock.reader`.
- `rwlock.writer_lock` — `_WriterLock` instance for exclusive (write) access. Alias: `rwlock.writer`.

### `_ReaderLock`

- `locked` (property, `bool`) — `True` if the reader lock is currently held by any task.
- `acquire()` (coroutine) — Acquire the reader lock. Blocks if a writer holds the lock. Supports reentrant acquisition by the same task.
- `release()` — Release one level of reader lock. Raises `RuntimeError` if called without holding the lock.
- Supports `async with` context manager protocol (`__aenter__`, `__aexit__`).
- Does not support synchronous `with` (raises `RuntimeError` — use `async with`).

### `_WriterLock`

- `locked` (property, `bool`) — `True` if the writer lock is currently held.
- `acquire()` (coroutine) — Acquire the writer lock. Blocks if any reader or writer holds the lock. Supports reentrant acquisition by the same task. Raises `RuntimeError` if called while the same task holds the reader lock (upgrade not supported).
- `release()` — Release one level of writer lock. Raises `RuntimeError` if called without holding the lock.
- Supports `async with` context manager protocol (`__aenter__`, `__aexit__`).
- Does not support synchronous `with` (raises `RuntimeError` — use `async with`).

## Behavior Details

### Writer Priority

When the lock becomes free, waiting writers are woken up before waiting readers. This prevents writer starvation in read-heavy workloads.

### Cancellation Safety

If a task is cancelled while waiting to acquire the lock, the lock state remains consistent. Other waiters will proceed normally. Since v1.5.1, cross-event-loop race conditions and cancellation-related deadlocks are fixed.

### Event Loop Constraints

- The lock can be created outside an async function (lazy loop evaluation since v1.4.0).
- Once a task acquires the lock, it binds to that task's event loop.
- Using the lock from a different event loop raises `RuntimeError` with the message "is bound to a different event loop".

### Version History Highlights

- **1.5.1** (2026-02-20) — Fixed cross-event-loop race condition, fixed cancellation deadlock, added `__slots__`.
- **1.4.0** (2024-01-20) — Lazy loop evaluation (lock can be created outside async context), Python 3.11/3.12 support.
- **1.3.0** (2022-01-18) — Dropped deprecated `loop` parameter from constructor.
- **1.2.0** (2021-11-09) — Fixed rare concurrent writes bug.
- **1.0.0** (2020-12-31) — Fix cancellation during acquire, deprecate explicit `loop` argument.
