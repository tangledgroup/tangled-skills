# Builtins Reference

Async-compatible versions of Python builtin functions for iterables. These functions intentionally shadow their builtins counterparts, enabling use with both standard iterables and async iterables without conditional logic.

## Boolean Functions

### `all(itr: AnyIterable[MaybeAwaitable[Any]]) -> bool`

Return True if all values are truthy in a mixed iterable, else False. The iterable will be fully consumed and any awaitables will automatically be awaited.

```python
from aioitertools import all

# Check all items in async iterable
if await all(async_iterator):
    ...  # All items are truthy

# Works with mixed iterables
if await all([True, True, await some_check(), True]):
    ...
```

**Parameters:**
- `itr`: Iterable, AsyncIterable, or mix of Awaitable items

**Returns:** `bool`

---

### `any(itr: AnyIterable[MaybeAwaitable[Any]]) -> bool`

Return True if any value is truthy in a mixed iterable, else False. The iterable will be fully consumed and any awaitables will automatically be awaited.

```python
from aioitertools import any

# Check if any item is truthy
if await any(async_iterator):
    ...  # At least one item is truthy
```

**Parameters:**
- `itr`: Iterable, AsyncIterable, or mix of Awaitable items

**Returns:** `bool`

---

## Iterator Functions

### `iter(itr: AnyIterable[T]) -> AsyncIterator[T]`

Get an async iterator from any mixed iterable. Async iterators are returned directly, async iterables return their async iterator, and standard iterables are wrapped in an async generator yielding each item in order.

```python
from aioitertools import iter

# Convert sync iterable to async iterator
async for value in iter(range(10)):
    ...  # 0, 1, 2, ..., 9

# Async iterators passed through unchanged
async_iterator = iter(async_gen)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

### `next(itr: AnyIterator[T]) -> T`

Return the next item of any mixed iterator. Calls `builtins.next()` on standard iterators, and awaits `itr.__anext__()` on async iterators.

```python
from aioitertools import next

# Get next item (raises StopAsyncIteration if exhausted)
value = await next(iterator)

# With default value
value = await next(iterator, "default_value")
```

**Parameters:**
- `itr`: Iterator or AsyncIterator
- `default` (optional): Default value if iterator exhausted

**Returns:** T or default type

---

## Collection Functions

### `list(itr: AnyIterable[T]) -> list[T]`

Consume a mixed iterable and return a list of items in order.

```python
from aioitertools import list

# Convert async iterable to list
items = await list(async_generator())
print(items)  # [0, 1, 2, 3, 4]
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `list[T]`

---

### `tuple(itr: AnyIterable[T]) -> tuple[T, ...]`

Consume a mixed iterable and return a tuple of items in order.

```python
from aioitertools import tuple

# Convert async iterable to tuple
items = await tuple(async_generator())
print(items)  # (0, 1, 2, 3, 4)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `tuple[T, ...]`

---

### `set(itr: AnyIterable[T]) -> set[T]`

Consume a mixed iterable and return a set of items (duplicates removed).

```python
from aioitertools import set

# Convert to set (removes duplicates)
unique_items = await set([0, 1, 2, 3, 0, 1, 2, 3])
print(unique_items)  # {0, 1, 2, 3}
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `set[T]`

---

## Enumeration Functions

### `enumerate(itr: AnyIterable[T], start: int = 0) -> AsyncIterator[tuple[int, T]]`

Consume a mixed iterable and yield the current index and item.

```python
from aioitertools import enumerate

# Enumerate with default start
async for index, value in enumerate(async_iterator):
    ...  # (0, item1), (1, item2), ...

# Enumerate with custom start
async for index, value in enumerate(async_iterator, start=1):
    ...  # (1, item1), (2, item2), ...
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `start`: Starting index (default: 0)

**Returns:** `AsyncIterator[tuple[int, T]]`

---

## Transformation Functions

### `map(fn: Callable[[T], R], itr: AnyIterable[T]) -> AsyncIterator[R]`

Apply function to each item in iterable. Function can be sync or async (coroutine). Results are yielded as they're computed.

```python
from aioitertools import map

# Sync function
async for square in map(lambda x: x * x, range(10)):
    ...  # 0, 1, 4, 9, ...

# Async function (auto-awaited)
async def fetch(url):
    response = await aiohttp.get(url)
    return await response.json()

async for data in map(fetch, URL_LIST):
    ...  # Results yielded as they complete

# Mixed sync/async iterables
async for result in map(process, sync_list):
    ...
```

**Parameters:**
- `fn`: Callable (sync or async) taking T, returning R
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[R]`

---

### `filter(predicate: Predicate[T], itr: AnyIterable[T]) -> AsyncIterator[T]`

Yield items from iterable where predicate returns True. Predicate can be sync or async.

```python
from aioitertools import filter

# Sync predicate
async for even in filter(lambda x: x % 2 == 0, range(10)):
    ...  # 0, 2, 4, 6, 8

# Async predicate
async def is_valid(item):
    return await check_item(item)

async for valid in filter(is_valid, items):
    ...  # Only valid items
```

**Parameters:**
- `predicate`: Callable (sync or async) returning bool
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`

---

### `zip(*itrs: AnyIterable[Any]) -> AsyncIterator[tuple[Any, ...]]`

Aggregate items from multiple iterables into tuples. Stops when shortest iterable exhausted.

```python
from aioitertools import zip

# Zip sync and async iterables
async for a, b in zip(sync_list, async_generator()):
    ...  # (item1_a, item1_b), (item2_a, item2_b), ...

# Zip multiple iterables
async for a, b, c in zip(iter1, iter2, iter3):
    ...  # (a1, b1, c1), (a2, b2, c2), ...
```

**Parameters:**
- `*itrs`: One or more Iterables or AsyncIterables

**Returns:** `AsyncIterator[tuple[Any, ...]]`

---

## Aggregation Functions

### `sum(itr: AnyIterable[float], start: float = 0) -> float`

Sum all items in iterable, starting from initial value.

```python
from aioitertools import sum

# Sum numbers
total = await sum(async_number_iterator)

# With starting value
total = await sum(async_number_iterator, start=100)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of numeric type
- `start`: Initial value (default: 0)

**Returns:** Numeric type

---

### `min(itr: AnyIterable[T], *, key: KeyFunction[T] = None, default: T = None) -> T`

Return smallest item in iterable. Raises ValueError if empty (unless default provided).

```python
from aioitertools import min

# Simple minimum
smallest = await min(async_number_iterator)

# With key function
shortest = await min(strings, key=len)

# With default for empty iterator
first = await min(maybe_empty_iterator, default="fallback")
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `key` (optional): Key function for comparison
- `default` (optional): Default if iterator empty

**Returns:** T

---

### `max(itr: AnyIterable[T], *, key: KeyFunction[T] = None, default: T = None) -> T`

Return largest item in iterable. Raises ValueError if empty (unless default provided).

```python
from aioitertools import max

# Simple maximum
largest = await max(async_number_iterator)

# With key function
longest = await max(strings, key=len)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `key` (optional): Key function for comparison
- `default` (optional): Default if iterator empty

**Returns:** T

---

## Ordering Functions

### `sorted(itr: AnyIterable[T], *, key: KeyFunction[T] = None, reverse: bool = False) -> list[T]`

Sort items from iterable and return as list. Consumes entire iterable first.

```python
from aioitertools import sorted

# Simple sort
numbers = await sorted(async_number_iterator)

# With key function
sorted_by_length = await sorted(strings, key=len)

# Reverse order
descending = await sorted(numbers, reverse=True)
```

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T
- `key` (optional): Key function for sorting
- `reverse` (optional): Sort in descending order

**Returns:** `list[T]`

---

### `reversed(itr: AnyIterable[T]) -> AsyncIterator[T]`

Yield items from iterable in reverse order. Consumes entire iterable first, then yields in reverse.

```python
from aioitertools import reversed

# Reverse iteration
async for item in reversed(async_iterator):
    ...  # Items in reverse order
```

**Note:** This function consumes the entire iterable before yielding any items.

**Parameters:**
- `itr`: Iterable or AsyncIterable of type T

**Returns:** `AsyncIterator[T]`
