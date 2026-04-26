# Builtins Library

The `asyncstdlib.builtins` module implements Python's built-in functions for async callables and async iterables. All functions accept `(async) iter T` arguments — meaning both sync and async iterables are accepted (async neutral).

## Iterator Reducing

### anext

```python
await anext(iterable: async iter T[, default: T]) -> T
```

Retrieve the next item from an async iterator. Raises `StopAsyncIteration` if exhausted and no default is given. This function is **not** async neutral — the iterator must be a true async iterator (supporting `__anext__()`).

```python
async_iter = a.iter([1, 2, 3])
first = await a.anext(async_iter)  # 1
last = await a.anext(empty_iter, "nope")  # "nope"
```

### all

```python
await all(iterable: (async) iter T) -> bool
```

Return `True` if none of the elements of the async iterable are false. Short-circuits on first false value.

### any

```python
await any(iterable: (async) iter T) -> bool
```

Return `True` if at least one element of the async iterable is true. Short-circuits on first true value.

### max / min

```python
await max(iterable: (async) iter T, *, key: (T) -> Any = None, default: T) -> T
await min(iterable: (async) iter T, *, key: (T) -> Any = None, default: T) -> T
```

Return the largest/smallest item from an async iterable. The `key` argument may be a regular or async callable and defaults to identity. Raises `ValueError` if iterable is empty and no `default` is provided.

The two-or-more-arguments variant (`max(a, b, c)`) is not supported — use the builtin instead.

```python
largest = await a.max(get_async_data(), key=lambda x: x.score)
smallest = await a.min(get_async_data(), default=0)
```

### sum

```python
await sum(iterable: (async) iter T, start: T = 0) -> T
```

Sum of `start` and all elements in the async iterable.

## Iterator Transforming

### iter

```python
async for :T in iter(iterable: (async) iter T)
```

Convert any iterable (sync or async) into an async iterator. Supports three protocols: `__aiter__()`, `__iter__()`, and sequence protocol via `__getitem__()`. When a sentinel is given, subject must be an `(async) callable` — produces values via `await subject()` until a value equals the sentinel.

```python
async for item in a.iter(sync_list):
    ...

# Sentinel form: call until sentinel value
async for line in a.iter(read_line_async, sentinel=""):
    process(line)
```

### filter

```python
async for :T in filter(function: (T) -> (await) bool, iterable: (async) iter T)
```

Async iterator of elements filtered by an `(async)` callable. Equivalent to `(element async for element in iterable if await func(element))`. Both function and iterable may be sync or async.

### zip

```python
async for :(T, ...) in zip(*iterables: (async) iter T, strict: bool = True)
```

Aggregate elements from multiple async iterables into tuples. Exhausted when the shortest iterable is exhausted. `strict=True` (default since 3.10.0) raises `ValueError` if iterables have unequal lengths.

```python
async for name, score in a.zip(names_iter, scores_iter):
    print(f"{name}: {score}")
```

### map

```python
async for :R in map(function: (T, ...) -> (await) R, iterable: (async) iter T, ..., /, strict: bool = True)
```

Apply an `(async)` function to items from one or more async iterables. Equivalent to `(await function(*args) async for args in zip(iterables))`. For `n` iterables, `function` must take `n` positional arguments. `strict=True` (default since 3.14.0) raises `ValueError` on unequal lengths.

```python
async def fetch(url):
    return await http.get(url)

results = await a.list(a.map(fetch, urls))
```

### enumerate

```python
async for :(int, T) in enumerate(iterable: (async) iter T, start=0)
```

Yield `(index, element)` pairs from an async iterable. Count begins at `start` and increments by 1.

## Standard Types

### list / dict / set / tuple

```python
await list(iterable: (async) iter T = ()) -> [T, ...]
await dict(iterable: (async) iter (str, T) = ()) -> {str: T, ...}
await set(iterable: (async) iter T = ()) -> {T, ...}
await tuple(iterable: (async) iter T = ()) -> (T, ...)
```

Collect an async iterable into the corresponding standard type. Equivalent to the matching list/dict/set/tuple comprehension over `async for`.

### sorted

```python
await sorted(iterable: (async) iter T, *, key: (T) -> (await) Any = None, reverse: bool = False) -> [T, ...]
```

Sort items from an async iterable into a new list. The `key` may be an async callable. Actual sorting is synchronous — very large iterables may block the event loop. Worst-case O(n log n). Added in version 3.9.0.

```python
items = await a.sorted(async_data(), key=lambda x: await get_priority(x))
```
