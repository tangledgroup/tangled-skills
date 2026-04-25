# asyncio Module Reference

The `aioitertools.asyncio` module provides enhanced concurrent execution utilities built on top of Python's asyncio. These functions offer more convenient APIs for common async patterns.

Import as: `from aioitertools import asyncio as ait_asyncio`

## Completion-Based Functions

### `as_completed(aws: Iterable[Awaitable[T]], *, timeout: float = None) -> AsyncIterator[T]`

Run awaitables concurrently and yield results as they complete. Unlike `asyncio.as_completed`, this yields actual results (not futures), eliminating the need to await each item.

```python
from aioitertools.asyncio import as_completed

# Yield results as futures complete
futures = [fetch_url(url) for url in URLs]
async for result in as_completed(futures):
    ...  # Process result immediately (already awaited)

# With timeout (cancels remaining on timeout)
try:
    async for result in as_completed(futures, timeout=30):
        ...  # Process results within 30 seconds
except asyncio.TimeoutError:
    ...  # Handle timeout
```

**Parameters:**
- `aws`: Iterable of Awaitable objects (coroutines, tasks, futures)
- `timeout` (optional): Maximum time in seconds; cancels remaining awaitables on timeout

**Returns:** `AsyncIterator[T]`

**Raises:** `asyncio.TimeoutError` if timeout exceeded

---

### `as_generated(iterables: Iterable[AsyncIterable[T]], *, return_exceptions: bool = False) -> AsyncIterable[T]`

Yield results from multiple async iterables in the order they're produced. Creates separate tasks to drain each iterable and merges results into a single stream.

```python
from aioitertools.asyncio import as_generated

# Merge multiple async generators
async def generator(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

gen1 = generator(10)
gen2 = generator(12)

# Values yielded as they're produced (intermixed)
async for value in as_generated([gen1, gen2]):
    ...  # Process values from both generators

# With exception handling
async for value in as_generated(generators, return_exceptions=True):
    if isinstance(value, Exception):
        ...  # Handle exception
    else:
        ...  # Process value
```

**Parameters:**
- `iterables`: Iterable of AsyncIterable objects
- `return_exceptions` (optional): If True, yield exceptions instead of raising

**Returns:** `AsyncIterable[T]` (or `AsyncIterable[Union[T, Exception]]` if return_exceptions=True)

**Behavior:**
- If `return_exceptions=False` (default): First exception raises and cancels all pending tasks
- If `return_exceptions=True`: Exceptions yielded as values, continues until all iterables exhausted

---

## Gathering Functions

### `gather(*args: Awaitable[T], return_exceptions: bool = False, limit: int = -1) -> list[Any]`

Like `asyncio.gather` but with concurrency limiting. All results are buffered and returned as a list in the order of input awaitables.

```python
from aioitertools.asyncio import gather

# Gather with concurrency limit
futures = [fetch_url(url) for url in URLs]
results = await gather(*futures, limit=5)
...  # Process all results (max 5 concurrent requests)

# With exception handling
results = await gather(
    *futures,
    limit=10,
    return_exceptions=True  # Exceptions in results list instead of raising
)

# Cancel propagates to all pending tasks
try:
    results = await gather(*long_running_tasks, limit=3)
except asyncio.CancelledError:
    ...  # All pending tasks also cancelled
```

**Parameters:**
- `*args`: Awaitable objects (coroutines, tasks, futures)
- `return_exceptions` (optional): If True, exceptions stored in results instead of raising
- `limit` (optional): Maximum concurrent tasks (-1 = unlimited)

**Returns:** `list[Any]` (results in same order as input awaitables)

**Note:** If cancelled, all internally created pending tasks are also cancelled.

---

### `gather_iter(itr: AnyIterable[MaybeAwaitable[T]], return_exceptions: bool = False, limit: int = -1) -> list[T]`

Wrapper around `gather` to handle gathering an iterable instead of `*args`. Values don't have to be awaitable (sync values passed through).

```python
from aioitertools.asyncio import gather_iter

# Gather from async iterable
async def get_futures():
    for url in URLs:
        yield fetch_url(url)

results = await gather_iter(get_futures(), limit=5)

# Mix of sync and async values
mixed = [1, fetch_async(), 3, fetch_async2()]
results = await gather_iter(mixed)
...  # [1, result1, 3, result2]
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of Awaitable or non-Awaitable values
- `return_exceptions` (optional): If True, exceptions stored in results
- `limit` (optional): Maximum concurrent tasks (-1 = unlimited)

**Returns:** `list[T]`

---

## Usage Patterns

### Rate-Limited Concurrent Processing

Use `gather` with limit for rate-limited API calls:

```python
from aioitertools.asyncio import gather

async def fetch_with_retry(url):
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(0.5 * (attempt + 1))

# Fetch all URLs with max 10 concurrent requests
urls = get_all_urls()
results = await gather(
    *(fetch_with_retry(url) for url in urls),
    limit=10,
    return_exceptions=False
)
```

### Streaming Results as Completed

Use `as_completed` when you want to process results immediately:

```python
from aioitertools.asyncio import as_completed

async def process_result(result):
    ...  # Store or forward result immediately

futures = [fetch_and_parse(url) for url in URLs]
async for result in as_completed(futures, timeout=60):
    await process_result(result)  # Process as soon as available
```

### Merging Multiple Data Streams

Use `as_generated` to merge multiple async data sources:

```python
from aioitertools.asyncio import as_generated

async def read_log_file(filename):
    async with aiofiles.open(filename) as f:
        async for line in f:
            yield parse_line(line)

# Merge multiple log files into single stream
log_files = ["app.log", "error.log", "access.log"]
streams = [read_log_file(f) for f in log_files]

async for log_entry in as_generated(streams):
    await process_log_entry(log_entry)  # Process from all files intermixed
```

### Concurrency Control with Timeout

Combine `as_completed` with timeout for bounded concurrent operations:

```python
from aioitertools.asyncio import as_completed

async def health_check(service):
    start = asyncio.get_event_loop().time()
    try:
        response = await check_service(service)
        return {"service": service, "status": "ok", "latency": asyncio.get_event_loop().time() - start}
    except Exception as e:
        return {"service": service, "status": "failed", "error": str(e)}

services = get_all_services()
checks = [health_check(s) for s in services]

results = []
try:
    async for result in as_completed(checks, timeout=5):
        results.append(result)
except asyncio.TimeoutError:
    ...  # Some checks didn't complete in time

print(f"Completed {len(results)} of {len(services)} checks")
```

## Comparison with Standard asyncio

| Function | aioitertools Version | Standard asyncio |
|----------|---------------------|------------------|
| `as_completed` | Yields actual results (auto-awaited) | Yields futures (must await each) |
| `gather` | Supports `limit` parameter | No concurrency limiting |
| N/A | `as_generated` for AsyncIterables | No equivalent |
| N/A | `gather_iter` for iterables | Must use `*args` unpacking |

## Key Differences

1. **Auto-awaiting**: `as_completed` yields results, not futures
2. **Concurrency limiting**: `gather` supports `limit` parameter
3. **Iterable support**: `gather_iter` accepts iterables directly
4. **Stream merging**: `as_generated` merges multiple async iterators
5. **Exception handling**: Consistent `return_exceptions` parameter across functions
