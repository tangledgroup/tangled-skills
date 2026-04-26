# Builtins

Async-compatible versions of Python builtin functions for iterables. These intentionally shadow their `builtins` counterparts, enabling use with both standard and async iterables without conditional logic.

## all

```python
async def all(itr: AnyIterable[MaybeAwaitable[Any]]) -> bool
```

Return `True` if all values are truthy, else `False`. Fully consumes the iterable and awaits any awaitable values.

```python
if await all(it):
    # all items passed
    ...
```

## any

```python
async def any(itr: AnyIterable[MaybeAwaitable[Any]]) -> bool
```

Return `True` if any value is truthy, else `False`. Fully consumes the iterable and awaits any awaitable values.

```python
if await any(it):
    # at least one item is truthy
    ...
```

## iter

```python
def iter(itr: AnyIterable[T]) -> AsyncIterator[T]
```

Get an async iterator from any mixed iterable. Returns async iterators directly, calls `__aiter__()` on async iterables, and wraps standard iterables in an async generator.

```python
# Wrap a sync range
async for value in iter(range(10)):
    ...

# Pass through an existing async iterator
ait = iter(some_async_iterable())
```

## next

```python
async def next(itr: AnyIterator[T], default: T2 = <missing>) -> Union[T, T2]
```

Return the next item from any mixed iterator. Calls `builtins.next()` on standard iterators and awaits `__anext__()` on async iterators. Supports an optional default value to avoid raising `StopAsyncIteration`.

```python
value = await next(it)

# With default
value = await next(it, None)
```

## list

```python
async def list(itr: AnyIterable[T]) -> list[T]
```

Consume a mixed iterable and return a list of items in order.

```python
items = await list(range(5))
# [0, 1, 2, 3, 4]
```

## tuple

```python
async def tuple(itr: AnyIterable[T]) -> tuple[T, ...]
```

Consume a mixed iterable and return a tuple of items in order.

```python
items = await tuple(range(5))
# (0, 1, 2, 3, 4)
```

## set

```python
async def set(itr: AnyIterable[T]) -> set[T]
```

Consume a mixed iterable and return a set of items (deduplicated).

```python
unique = await set([0, 1, 2, 3, 0, 1, 2, 3])
# {0, 1, 2, 3}
```

## enumerate

```python
async def enumerate(itr: AnyIterable[T], start: int = 0) -> AsyncIterator[tuple[int, T]]
```

Yield `(index, item)` pairs from a mixed iterable, starting at the given index.

```python
async for index, value in enumerate(data_stream(), start=1):
    print(f"Item {index}: {value}")
```

## map

```python
async def map(fn: Callable[[T], R], itr: AnyIterable[T]) -> AsyncIterator[R]
```

Apply a function or coroutine to each item of a mixed iterable. The function can be sync or async — `maybe_await` handles both.

```python
# Sync function
async for square in map(lambda x: x * x, range(10)):
    ...

# Async coroutine
async def fetch(url):
    return await http_get(url)

async for response in map(fetch, urls):
    process(response)
```

## max

```python
async def max(itr: AnyIterable[Orderable], *, key: Optional[Callable] = None, default: T = <missing>) -> Orderable
```

Return the largest item. Supports `key` function and `default` value for empty iterables.

```python
largest = await max(data_stream())
with_default = await max(empty_stream(), default=0)
by_length = await max(strings(), key=len)
```

## min

```python
async def min(itr: AnyIterable[Orderable], *, key: Optional[Callable] = None, default: T = <missing>) -> Orderable
```

Return the smallest item. Supports `key` function and `default` value for empty iterables.

```python
smallest = await min(data_stream())
with_default = await min(empty_stream(), default=0)
```

## sum

```python
async def sum(itr: AnyIterable[T], start: Optional[T] = None) -> T
```

Compute the sum of a mixed iterable. Default start is `0`.

```python
total = await sum(number_stream())
# 1024

with_offset = await sum(number_stream(), start=100)
```

## zip

```python
def zip(*itrs: AnyIterable[Any]) -> AsyncIterator[tuple[Any, ...]]
```

Yield tuples of items from mixed iterables until the shortest is consumed. Uses `asyncio.gather` internally to advance all iterators concurrently.

```python
a = [1, 2, 3]
b = async_gen()

async for x, y in zip(a, b):
    ...

# Multiple iterables
async for a, b, c in zip(i1, i2, i3):
    ...
```

Supports up to 6+ iterables with proper type overloads for 1-5 arguments.
