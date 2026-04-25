---
name: aioitertools-0-13
description: Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python applications that need to process iterables with familiar itertools-style functions, work with both standard and async iterables interchangeably, or consume async data streams with functional patterns.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - asyncio
  - python
  - itertools
  - async-iterators
  - generators
category: development

external_references:
  - https://github.com/pythonicdave/aioitertools
  - https://aioitertools.readthedocs.io/
---
## Overview
Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python applications that need to process iterables with familiar itertools-style functions, work with both standard and async iterables interchangeably, or consume async data streams with functional patterns.

## When to Use
- Processing async data streams with familiar itertools patterns (chain, map, filter, zip)
- Converting between sync and async iterables without manual wrapping
- Building async generators that need functional composition
- Working with mixed iterables (some sync, some async) in the same pipeline
- Consuming futures or awaitables concurrently with `as_completed` or `gather`
- Needing itertools functionality in async Python applications

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python applications that need to process iterables with familiar itertools-style functions, work with both standard and async iterables interchangeably, or consume async data streams with functional patterns.

Async-compatible versions of Python's `itertools`, `builtins`, and additional utility functions for AsyncIO and mixed-type iterables. The library shadows standard library functions to provide asynchronous equivalents that work seamlessly with both standard iterators and async iterators, enabling a unified interface for processing iterable objects.

## Installation / Setup
aioitertools requires Python 3.9 or newer. Install from PyPI:

```bash
pip install aioitertools
```

No environment variables or configuration required.

## Usage Examples
### Basic Usage with Builtins

The library shadows standard builtins to provide async-compatible versions:

```python
from aioitertools import iter, next, map, zip, all, any

# Convert sync iterable to async iterator
async for item in iter(range(10)):
    ...  # 0, 1, 2, ..., 9

# Get next item from mixed iterator
first_item = await next(some_iterator)

# Map coroutines over data (auto-awaits results)
async def fetch(url):
    response = await aiohttp.request(url)
    return response.json()

async for result in map(fetch, URL_LIST):
    ...  # Results yielded as they complete

# Zip multiple iterables (sync or async)
async for a, b in zip(sync_list, async_generator()):
    ...

# Check conditions on mixed iterables
if await all(async_iterable):
    ...
    
if await any(mixed_iterable):
    ...
```

See [Builtins Reference](reference/01-builtins.md) for complete function documentation.

### Working with itertools Functions

All standard `itertools` functions are available as async generators:

```python
from aioitertools import chain, islice, combinations, groupby

# Chain multiple iterables together
async for value in chain([1, 2, 3], async_gen(), [7, 8, 9]):
    ...  # 1, 2, 3, ..., 7, 8, 9

# Slice async iterables
async for value in islice(async_generator(), 2, 10, 2):
    ...  # Items at indices 2, 4, 6, 8

# Generate combinations (consumes entire iterable first)
async for combo in combinations(range(4), 3):
    ...  # (0,1,2), (0,1,3), (0,2,3), (1,2,3)

# Group by key function (can be coroutine)
async def is_upper(char):
    return char.isupper()

async for key, group in groupby("AaBBcC", is_upper):
    async for item in group:
        ...  # Process grouped items
```

See [itertools Reference](reference/02-itertools.md) for complete function documentation.

### Concurrent Execution with asyncio Module

The `aioitertools.asyncio` module provides enhanced concurrent execution utilities:

```python
from aioitertools.asyncio import as_completed, gather, as_generated

# Yield results as futures complete (without awaiting each one)
futures = [fetch_url(url) for url in URLs]
async for result in as_completed(futures, timeout=30):
    ...  # Process results as they arrive

# Gather with concurrency limit
results = await gather(
    *coroutine_list,
    limit=5,  # Max 5 concurrent tasks
    return_exceptions=False
)

# Merge multiple async generators into one stream
gen1 = async_generator_1()
gen2 = async_generator_2()
async for value in as_generated([gen1, gen2]):
    ...  # Values from both generators intermixed
```

See [asyncio Module Reference](reference/03-asyncio.md) for details.

### Additional Utilities

The `more_itertools` module provides extra utilities:

```python
from aioitertools.more_itertools import take, chunked, before_and_after

# Take first N items as list
first_five = await take(5, async_iterator)

# Break into chunks of size N
async for chunk in chunked(large_iterable, n=100):
    ...  # Process each chunk (list of up to 100 items)

# Split iterator at predicate boundary
it = iter("ABCdEfGhI")
uppercase, remainder = await before_and_after(str.isupper, it)
uppercase_str = ''.join([c async for c in uppercase])  # "ABC"
remainder_str = ''.join([c async for c in remainder])  # "dEfGhI"
```

See [more_itertools Reference](reference/04-more-itertools.md) for details.

## Key Concepts
### Mixed Iterable Support

All functions accept both standard iterables and async iterables:

```python
# All of these work identically:
async for x in map(process, sync_list):          # Sync iterable
async for x in map(process, async_gen()):        # Async generator
async for x in map(process, async_iterable):     # AsyncIterable
async for x in map(fetch_coroutine, url_list):   # Coroutine function
```

### Automatic Await Handling

Functions automatically await coroutine results:

```python
async def fetch_and_parse(url):
    response = await aiohttp.get(url)
    return await response.json()

# Results are auto-awaited and yielded
async for data in map(fetch_and_parse, URLs):
    process(data)  # data is already parsed JSON, not a coroutine
```

### Lazy Evaluation

Most functions are lazy async generators:

```python
# Nothing consumed until iteration starts
chained = chain(gen1(), gen2(), gen3())

# Items yielded one at a time
async for item in chained:
    ...  # gen2() not started until gen1() exhausted
```

Exception: `combinations`, `permutations`, `product` consume entire input first.

## Advanced Topics
## Advanced Topics

- [Builtins](reference/01-builtins.md)
- [Itertools](reference/02-itertools.md)
- [Asyncio](reference/03-asyncio.md)
- [More Itertools](reference/04-more-itertools.md)

## Troubleshooting
### "TypeError: 'X' object is not async iterable"

Ensure you're using `await` with async functions:

```python
# Wrong:
result = map(async_func, items)  # Returns async generator, not results

# Correct:
async for result in map(async_func, items):
    ...
```

### "RuntimeError: This event loop is already running"

When using `before_and_after` or creating futures in synchronous code, ensure you're in an async context. Use `asyncio.create_task()` instead of manually creating futures.

### Combining sync and async functions

Use the library's automatic detection - it handles both:

```python
# Both work:
async for x in map(sync_function, items):       # sync function called directly
async for x in map(async_coroutine, items):     # coroutine auto-awaited
```

### Performance considerations

- Functions that consume entire iterables first (`combinations`, `permutations`, `product`) will buffer all input in memory
- Use `islice` to limit consumption of large iterables
- `gather` with `limit` parameter controls memory usage for concurrent operations
- `as_completed` and `as_generated` provide streaming results without buffering

