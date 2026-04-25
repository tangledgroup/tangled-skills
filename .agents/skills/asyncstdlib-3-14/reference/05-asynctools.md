# The Asynctools Library

The `asyncstdlib.asynctools` library provides utilities for safe async iterator handling and sync/async integration.

## Iterator Lifetime

### `borrowed = borrow(iterator)`

Borrow an async iterator, preventing it from being closed.

```python
import asyncstdlib as a

async def process_stream(stream):
    # Borrow prevents aclose() from closing underlying iterator
    borrowed = a.borrow(stream)
    
    # Pass to multiple consumers safely
    await consumer1(borrowed)
    await consumer2(borrowed)
    
    # Original owner is responsible for cleanup

async def consumer(iterator):
    async for item in iterator:
        process(item)

# Usage
stream = create_expensive_stream()
await process_stream(stream)
# stream still usable - not closed by consumers
```

**Supports:** `asend()` and `athrow()` if underlying iterator supports them.

**Notes:**
- Borrowed iterator's `aclose()` only closes the borrowed wrapper, not underlying iterator
- Original owner assures to close the iterator as needed
- Supports both `AsyncIterator` and `AsyncGenerator` types

### `async with scoped_iter(iterable) as async_iter`

Context manager providing an async iterator with automatic cleanup.

```python
import asyncstdlib as a
from collections import deque

async def head_tail(iterable, leading=5, trailing=5):
    """Provide first and last items from iterable"""
    async with a.scoped_iter(iterable) as async_iter:
        # Iterator is borrowed - won't be closed prematurely
        
        # Get leading items
        for item in a.islice(async_iter, leading):
            yield item
        
        # Get trailing items
        tail = deque(maxlen=trailing)
        for item in async_iter:  # Continue from where we left off
            tail.append(item)
    
    # Iterator automatically closed here
    for item in tail:
        yield item

# Usage
async for item in head_tail(large_dataset, 10, 10):
    process(item)
```

**Nested scoping:**

```python
import asyncstdlib as a

async def outer(iterable):
    async with a.scoped_iter(iterable) as iter1:
        # Use iterator
        await a.anext(iter1)
        
        # Pass to inner function - nested scoped_iter is safe
        await inner(iter1)
    
    # Iterator closed here (outermost scope)

async def inner(iterator):
    async with a.scoped_iter(iterator) as iter2:
        # iter2 won't close underlying iterator
        # Inner scope forfeits closing to outer scope
        async for item in iter2:
            process(item)
```

**Equivalent to:** `closing(iter(iterable))` with borrowing.

## Async Transforming

### `await sync(callable, *args, **kwargs)`

Run a sync callable in an async context.

```python
import asyncstdlib as a

def sync_computation(x, y):
    return x + y

# Run sync function in async context
result = await a.sync(sync_computation, 2, 3)  # 5

# With keyword arguments
def configure(option1, option2="default"):
    return f"{option1}:{option2}"

result = await a.sync(configure, "value", option2="custom")  # "value:custom"
```

**Use case:** Integrating existing sync code into async programs without blocking.

### `async for item in any_iter(iterable)`

Convert any iterable (sync or async) to async iterator with unified interface.

```python
import asyncstdlib as a

async def process_any_data(data):
    """Handle both sync and async iterables transparently"""
    async for item in a.any_iter(data):
        await handle(item)

# Works with sync list
await process_any_data([1, 2, 3])

# Works with async generator
async def async_data():
    yield 1
    yield 2
    yield 3

await process_any_data(async_data())

# Works with async iterable from library
await process_any_data(database.query_results())
```

**Benefits:**
- Write functions that accept both sync and async iterables
- No need to check type or provide separate code paths
- Automatically handles conversion

### `await await_each(coroutine_factory, iterable)`

Run a coroutine for each item in an iterable, awaiting each before next.

```python
import asyncstdlib as a
import asyncio

async def process_with_delay(item):
    """Process item with rate limiting"""
    await process(item)
    await asyncio.sleep(0.1)  # Rate limit: 10 items/second

data = [1, 2, 3, 4, 5]

# Process sequentially with delays
await a.await_each(process_with_delay, data)

# Contrast with gather (parallel):
# await gather(*(process_with_delay(item) for item in data))
```

**Use case:** Rate-limited processing where items must be handled sequentially.

### `apply(callable, args)`

Apply a callable to an iterable of arguments.

```python
import asyncstdlib as a

async def add(x, y):
    return x + y

args = [(1, 2), (3, 4), (5, 6)]

# Apply function to each argument tuple
results = await a.list(a.map(add, a.starmap(lambda t: t, args)))

# Or use directly with starmap
async for result in a.starmap(add, args):
    print(result)  # 3, 7, 11
```

## Usage Patterns

### Safe stream processing

```python
import asyncstdlib as a

async def safe_process_stream(stream):
    """Process stream with guaranteed cleanup"""
    async with a.scoped_iter(stream) as iterator:
        try:
            async for item in iterator:
                await process(item)
        except Exception:
            # Stream will be closed even on error
            raise
        finally:
            # Stream automatically closed by scoped_iter
            log("Stream processing complete")

# No resource leaks even with early exit or exceptions
```

### Multi-consumer streams

```python
import asyncstdlib as a

async def fan_out(stream, *consumers):
    """Send same stream to multiple consumers"""
    # Create independent iterators for each consumer
    iterators = a.tee(stream, len(consumers))
    
    # Borrow to prevent premature closing
    borrowed_iterators = [a.borrow(it) for it in iterators]
    
    # Run all consumers concurrently
    await gather(*[consumer(it) for it in borrowed_iterators])
    
    # Original stream owner closes when done

async def consumer(iterator):
    async for item in iterator:
        await process(item)
```

### Adaptive processing

```python
import asyncstdlib as a

async def adaptive_processor(data_source):
    """Process data, handling both sync and async sources"""
    # Automatically handles sync or async input
    async for item in a.any_iter(data_source):
        if is_expensive(item):
            # Run expensive operation in async context
            result = await a.sync(expensive_sync_op, item)
        else:
            result = await quick_async_op(item)
        
        await store(result)

# Works with database cursor (sync)
await adaptive_processor(db.execute("SELECT ..."))

# Works with async API
await adaptive_processor(fetch_from_api())
```

### Rate-limited batch processing

```python
import asyncstdlib as a
import asyncio

async def rate_limited_batch_process(items, batch_size, delay):
    """Process items in batches with rate limiting"""
    async for batch in a.batched(items, batch_size):
        # Process entire batch
        batch_list = list(batch)
        await process_batch(batch_list)
        
        # Rate limit between batches
        await asyncio.sleep(delay)

# Process 100 items at a time, with 0.5s delay between batches
await rate_limited_batch_process(large_stream, 100, 0.5)
```

### Iterator lifecycle management

```python
import asyncstdlib as a

class StreamProcessor:
    def __init__(self, stream):
        self.stream = stream
    
    async def process_with_cleanup(self):
        """Guaranteed cleanup even on errors"""
        async with a.scoped_iter(self.stream) as iterator:
            # Safe to pass iterator around
            borrowed = a.borrow(iterator)
            
            # Process with multiple stages
            filtered = self.filter_stage(borrowed)
            transformed = self.transform_stage(filtered)
            
            async for item in transformed:
                await self.store(item)
        
        # All iterators closed automatically

    def filter_stage(self, iterator):
        return a.filter(self.should_include, iterator)

    def transform_stage(self, iterator):
        return a.map(self.transform, iterator)
```

## Glossary Terms

### Borrowing

Borrowing an async iterator means using it without taking responsibility for closing it. The original owner assures to close the iterator when appropriate.

```python
import asyncstdlib as a

async def owner():
    stream = create_stream()
    
    # Borrow for temporary use
    borrowed = a.borrow(stream)
    await temporary_use(borrowed)
    
    # Owner closes when done
    await stream.aclose()

async def temporary_use(iterator):
    # Can use but aclose() won't close underlying stream
    async for item in iterator:
        process(item)
```

### Async Neutral

A function is async neutral if it works seamlessly with both sync and async arguments, automatically detecting and handling each appropriately.

```python
import asyncstdlib as a

# all functions are async neutral
await a.all([True, True, True])           # Sync list
await a.all(async_true_generator())       # Async generator
await a.all(a.iter(sync_callable))        # Converted to async

# zip works with mixed sync/async iterables
async for pair in a.zip(sync_list, async_iterator):
    process(pair)
```

## Notes

- All functions designed for safe async iterator handling
- `scoped_iter` and `borrow` work together for complex iterator lifecycles
- Nested `scoped_iter` calls are safe - only outermost closes underlying iterator
- Functions integrate sync code into async programs without blocking event loop
- No event loop specific code - works with asyncio, trio, and any async framework
