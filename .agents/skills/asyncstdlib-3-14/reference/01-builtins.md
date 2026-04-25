# The Builtins Library

The `asyncstdlib.builtins` library implements Python's built-in functions for async callables and iterables.

## Iterator Reducing

### `await anext(iterable)`

Get the next item from an async iterable.

```python
import asyncstdlib as a

async_iter = a.iter([1, 2, 3])
first = await a.anext(async_iter)  # 1
second = await a.anext(async_iter)  # 2

# With default value (no StopAsyncIteration if exhausted)
value = await a.anext(async_iter, default=None)
```

**Raises:** `StopAsyncIteration` if iterable is exhausted and no default provided.

### `await all(iterable)`

Return True if all elements in async iterable are truthy.

```python
async def is_positive(x):
    return x > 0

result = await a.all(a.map(is_positive, [1, 2, 3]))  # True
result = await a.all(a.map(is_positive, [1, -1, 3]))  # False
```

### `await any(iterable)`

Return True if any element in async iterable is truthy.

```python
async def is_negative(x):
    return x < 0

result = await a.any(a.map(is_negative, [1, 2, -3]))  # True
result = await a.any(a.map(is_negative, [1, 2, 3]))   # False
```

### `await min(iterable)` / `await max(iterable)`

Get minimum or maximum value from async iterable.

```python
async def get_values():
    yield 3
    yield 1
    yield 4
    yield 1
    yield 5

minimum = await a.min(get_values())  # 1
maximum = await a.max(get_values())  # 5

# With key function
async def get_strings():
    yield "apple"
    yield "pie"
    yield "a"

shortest = await a.min(get_strings(), key=len)  # "a"
```

### `await sum(iterable, start=0)`

Sum elements from async iterable.

```python
async def get_numbers():
    yield 1
    yield 2
    yield 3

total = await a.sum(get_numbers())        # 6
total = await a.sum(get_numbers(), start=10)  # 16
```

## Iterator Transforming

### `async for item in iter(iterable)`

Convert any iterable (sync or async) to an async iterator.

```python
# Sync iterable -> async iterator
async for item in a.iter([1, 2, 3]):
    print(item)

# With sentinel value
async def read_until_eof(stream):
    async for line in a.iter(stream.readline, sentinel=""):
        process(line)
```

**Raises:** `TypeError` if subject does not support any iteration protocol.

### `async for item in filter(function, iterable)`

Filter elements using an async predicate function.

```python
async def is_even(x):
    return x % 2 == 0

async for even in a.filter(is_even, [1, 2, 3, 4, 5, 6]):
    print(even)  # 2, 4, 6
```

Equivalent to: `(element async for element in iterable if await func(element))`

### `async for item in map(function, *iterables, strict=True)`

Apply an async function to items from one or more iterables.

```python
async def square(x):
    return x * x

async for result in a.map(square, [1, 2, 3, 4]):
    print(result)  # 1, 4, 9, 16

# Multiple iterables - function receives one item from each
async def add(x, y):
    return x + y

async for result in a.map(add, [1, 2, 3], [10, 20, 30]):
    print(result)  # 11, 22, 33

# Strict mode (default True) - raises ValueError if iterables not equal length
async for pair in a.map(add, [1, 2], [10, 20, 30], strict=False):
    print(pair)  # 11, 22 (stops at shortest)
```

**Version added:** `strict` parameter added in version 3.14.0.

### `async for (index, item) in enumerate(iterable, start=0)`

Enumerate items from async iterable with running count.

```python
async for idx, item in a.enumerate(["a", "b", "c"]):
    print(idx, item)  # 0 a, 1 b, 2 c

async for idx, item in a.enumerate(["a", "b", "c"], start=1):
    print(idx, item)  # 1 a, 2 b, 3 c
```

### `async for (item1, item2, ...) in zip(*iterables, strict=True)`

Aggregate elements from multiple iterables into tuples.

```python
# Basic zip - stops at shortest iterable
async for pair in a.zip([1, 2, 3], ["a", "b"]):
    print(pair)  # (1, 'a'), (2, 'b')

# Strict mode (default True) - enforces equal length
try:
    async for pair in a.zip([1, 2], [3, 4, 5], strict=True):
        print(pair)
except ValueError:
    print("Iterables not equal length!")

# Non-strict mode - stops at shortest
async for pair in a.zip([1, 2], [3, 4, 5], strict=False):
    print(pair)  # (1, 3), (2, 4)
```

**Version added:** `strict` parameter added in version 3.10.0.

## Standard Types

### `await dict(iterable)`

Create a dictionary from async iterable of key-value pairs.

```python
async def get_pairs():
    yield ("a", 1)
    yield ("b", 2)
    yield ("c", 3)

data = await a.dict(get_pairs())  # {"a": 1, "b": 2, "c": 3}
```

### `await list(iterable)`

Convert async iterable to list.

```python
async def get_items():
    yield 1
    yield 2
    yield 3

items = await a.list(get_items())  # [1, 2, 3]
```

### `await set(iterable)`

Convert async iterable to set.

```python
async def get_items():
    yield 1
    yield 2
    yield 2
    yield 3

unique = await a.set(get_items())  # {1, 2, 3}
```

### `await tuple(iterable)`

Convert async iterable to tuple.

```python
async def get_items():
    yield 1
    yield 2
    yield 3

result = await a.tuple(get_items())  # (1, 2, 3)
```

### `await sorted(iterable, key=None, reverse=False)`

Sort items from async iterable.

```python
async def get_numbers():
    yield 3
    yield 1
    yield 4
    yield 1
    yield 5

sorted_asc = await a.sorted(get_numbers())      # [1, 1, 3, 4, 5]
sorted_desc = await a.sorted(get_numbers(), reverse=True)  # [5, 4, 3, 1, 1]

# With key function
async def get_strings():
    yield "apple"
    yield "pie"
    yield "a"

sorted_by_len = await a.sorted(get_strings(), key=len)  # ["a", "pie", "apple"]
```

## Usage Patterns

### Combining multiple operations

```python
import asyncstdlib as a

async def process_data():
    # Filter -> Map -> Reduce pattern
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    async def is_even(x):
        return x % 2 == 0
    
    async def square(x):
        return x * x
    
    async def add(x, y):
        return x + y
    
    # Sum of squares of even numbers
    result = await a.reduce(
        add,
        a.map(square, a.filter(is_even, a.iter(data)))
    )
    print(result)  # 4 + 16 + 36 + 64 + 100 = 220
```

### Async comprehensions alternative

```python
# Traditional async comprehension
result = [x async for x in a.filter(is_even, data)]

# Using asyncstdlib functions
result = await a.list(a.filter(is_even, data))
```

### Processing multiple streams

```python
import asyncstdlib as a

async def merge_streams(stream1, stream2):
    """Process two streams in parallel"""
    async for item1, item2 in a.zip(stream1, stream2):
        await process_pair(item1, item2)

async def combine_with_index(stream):
    """Add index to each item"""
    async for idx, item in a.enumerate(stream):
        await handle_with_index(idx, item)
```

## Notes

- All functions are **async neutral** - they work with both sync and async iterables/callables
- Functions automatically detect whether arguments are async or sync and handle appropriately
- Mixed sync/async iterables are supported (e.g., `zip(sync_list, async_iterable)`)
- No event loop specific code - works with asyncio, trio, and any async framework
