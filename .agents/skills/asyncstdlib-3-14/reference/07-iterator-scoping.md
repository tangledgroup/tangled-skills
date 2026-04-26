# Iterator Scoping

Cleanup of async resources is special because `aclose()` may require an active event loop. Since asynchronous iterators can hold resources indefinitely, they should be cleaned up deterministically whenever possible (see PEP 533).

asyncstdlib defaults to deterministic cleanup but provides tools to explicitly manage iterator lifetime.

## Cleanup in asyncstdlib

All asyncstdlib async iterators that work on other iterators assume sole ownership of the passed-in iterators. Passed-in async iterators are guaranteed to be `aclose()`d as soon as the asyncstdlib iterator itself is cleaned up. This provides a resource-safe default for exhausting iterators.

```python
import asyncio
import asyncstdlib as a

async def async_squares(i=0):
    """Provide an infinite stream of squared numbers"""
    while True:
        await asyncio.sleep(0.1)
        yield i**2
        i += 1

async def main():
    async_iter = async_squares()
    # zip closes async_iter when done
    async for i, s in a.zip(range(5), async_iter):
        print(f"{i}: {s}")
    # async_iter is now closed
    assert await a.anext(async_iter, "Closed!") == "Closed!"

asyncio.run(main())
```

For consistency, every asyncstdlib async iterator performs such cleanup. This may be unexpected for utilities usually applied multiple times (like `islice`). Use explicit scoping to manage lifetime.

## Scoping async iterator lifetime

Use `scoped_iter()` to create an async iterator guaranteed to `aclose()` at the end of an `async with` block, but not before:

```python
import asyncio
import asyncstdlib as a

async def async_squares(i=0):
    while True:
        await asyncio.sleep(0.1)
        yield i**2
        i += 1

async def main():
    async with a.scoped_iter(async_squares()) as async_iter:
        # Reuse the same iterator across multiple operations
        async for s in a.islice(async_iter, 3):
            print(f"1st Batch: {s}")
        async for s in a.islice(async_iter, 3):
            print(f"2nd Batch: {s}")
        async for s in a.islice(async_iter, 3):
            print(f"3rd Batch: {s}")
    # Iterator is closed after the block
    assert await a.anext(async_iter, "Closed!") == "Closed!"

asyncio.run(main())
```

Scoped iterators are the go-to approach for managing iterator lifetimes. For cases where lifetime does not correspond to a well-defined lexical scope, use `borrow()` instead.

## Borrowing

`borrow()` creates a wrapper that prevents closing the underlying iterator. The original owner remains responsible for cleanup:

```python
import asyncstdlib as a

async def process_partial(iterable):
    # Borrow to prevent islice from closing the source
    borrowed = a.borrow(iterable)
    async for item in a.islice(borrowed, 5):
        yield item
    # Source iterator remains open for further use
```

## Key patterns

- **Exhaust once**: Pass iterable directly — asyncstdlib closes it on completion
- **Reuse in a block**: Use `scoped_iter()` — closes at block end, borrowed inside
- **Pass to unknown code**: Use `borrow()` — prevents premature closing
- **Nested reuse**: `scoped_iter()` is safe to nest — inner scopes defer to outermost
