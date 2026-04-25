---
name: aiorwlock-1-5-1
description: Async read-write lock implementation for Python asyncio providing concurrent reader access and exclusive writer access. Use when building async applications requiring fine-grained synchronization where multiple readers can access shared data simultaneously but writers need exclusive access.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
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

## Overview

Async read-write lock implementation for Python asyncio providing concurrent reader access and exclusive writer access. Use when building async applications requiring fine-grained synchronization where multiple readers can access shared data simultaneously but writers need exclusive access.

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

## See Also

- [Advanced Usage and Examples](references/01-advanced-usage.md) - Complete examples, advanced patterns, and troubleshooting


## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
