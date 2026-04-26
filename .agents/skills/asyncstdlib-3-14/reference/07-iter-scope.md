# Iterator Scoping Guide

## Cleanup Semantics

Cleanup of async resources is special — `aclose()` may require an active event loop. Since asynchronous iterators can hold resources indefinitely, they should be cleaned up deterministically whenever possible (see PEP 533).

asyncstdlib defaults to **deterministic cleanup** but provides tools to explicitly manage iterator lifetime.

## Ownership Model

All asyncstdlib async iterators that work on other iterators assume **sole ownership** of the iterators passed to them. Passed-in async iterators are guaranteed to be `aclose()`d as soon as the asyncstdlib iterator itself is cleaned up. This provides a resource-safe default for the most common operation of exhausting iterators.

```python
import asyncio
import asyncstdlib as a

async def async_squares(i=0):
    """Provide an infinite stream of squared numbers."""
    while True:
        await asyncio.sleep(0.1)
        yield i ** 2
        i += 1

async def main():
    async_iter = async_squares()
    # Loop until done — takewhile will aclose() the underlying iterator
    async for i, sq in a.enumerate(a.takewhile(lambda x: x < 100, async_iter)):
        print(sq)
    # async_iter is now closed by takewhile
```

## Non-Exhausting Utilities

Non-exhausting utilities like `dropwhile()`, `takewhile()`, and `islice()` may close the underlying iterator before all items are consumed. This can be unexpected:

```python
async def data():
    for i in range(10):
        yield i

it = data()
# takewhile stops at first item >= 5, then closes `it`
taken = await a.list(a.takewhile(lambda x: x < 5, it))
# taken = [0, 1, 2, 3, 4]
# `it` is now closed — cannot continue from where takewhile stopped
```

## Managing Lifetime Explicitly

### Use scoped_iter for Controlled Scope

When you need to pass an iterator to multiple functions or use it in multiple places within a block, use `scoped_iter()`:

```python
async with a.scoped_iter(iterable) as async_iter:
    # Pass safely — inner calls won't close the underlying iterator
    first_batch = await a.list(a.islice(async_iter, 5))
    second_batch = await a.list(a.islice(async_iter, 5))
# Iterator is closed here when scope exits
```

### Use borrow to Prevent Closing

When passing an iterator to a function that would normally take ownership, wrap it with `borrow()`:

```python
async def process(data):
    filtered = a.filter(predicate, data)
    # Pass without losing ownership
    count = await a.sum(a.map(to_value, a.borrow(filtered)))
    # Continue using filtered
    remaining = await a.list(filtered)
    return count, remaining
```

### Combining scoped_iter and borrow

`scoped_iter()` automatically borrows the iterator it creates. Nested `scoped_iter()` calls on the same iterator are safe — inner scopes forfeit closing in favor of the outermost scope:

```python
async def outer(iterable):
    async with a.scoped_iter(iterable) as it:
        await inner(it)  # Safe — inner scoped_iter won't close
        # Continue using it
        async for item in it:
            ...

async def inner(it):
    async with a.scoped_iter(it) as scoped:
        # Uses the same underlying iterator
        async for item in scoped:
            ...
    # Does NOT close the original — outer scope retains ownership
```

## Glossary

- **Async neutral** — Types that support either regular or asynchronous implementation. For example, an async neutral iterable may provide both `for _ in iterable` and `async for _ in iterable`.
- **Borrowing** — When borrowing an object that needs explicit cleanup (like an async iterator), the original owner guarantees cleanup but prevents the temporary owner from closing it.
- **Borrowed object** — An object passed to a temporary owner with the guarantee that the original owner will handle cleanup.
