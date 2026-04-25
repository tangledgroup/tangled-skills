# The Itertools Library

The `asyncstdlib.itertools` library implements Python's itertools module for async iterables.

## Infinite Iterators

### `async for item in cycle(iterable)`

Indefinitely iterate over an iterable, recycling items.

```python
import asyncstdlib as a

# Cycle through values indefinitely
counter = 0
async for i, value in a.enumerate(a.cycle(["A", "B", "C"])):
    print(value)  # A, B, C, A, B, C, ...
    counter += 1
    if counter >= 10:
        break

# Use with zip to repeat pattern
async for pair in a.zip(a.cycle([1, 2, 3]), ["a", "b", "c", "d", "e"]):
    print(pair)  # (1,'a'), (2,'b'), (3,'c'), (1,'d'), (2,'e')
```

**Notes:**
- Lazily exhausts iterable on first pass, then recalls from internal buffer
- Subsequent passes provide items immediately without original delays
- All items are stored in memory
- Terminates immediately if iterable is empty

## Iterator Merging

### `async for item in chain(*iterables)`

Chain multiple iterables together.

```python
import asyncstdlib as a

# Chain sync and async iterables
async for item in a.chain([1, 2, 3], async_range(4, 7), ["a", "b"]):
    print(item)  # 1, 2, 3, 4, 5, 6, 'a', 'b'

# Chain from iterable of iterables
async def get_batches():
    yield [1, 2, 3]
    yield [4, 5, 6]
    yield [7, 8, 9]

async for item in a.chain.from_iterable(get_batches()):
    print(item)  # 1, 2, 3, 4, 5, 6, 7, 8, 9
```

### `async for item in chain.from_iterable(iterable)`

Chain iterables from a single iterable of iterables.

```python
import asyncstdlib as a

async def matrix():
    yield [1, 2, 3]
    yield [4, 5, 6]
    yield [7, 8, 9]

# Flatten the matrix
flat = await a.list(a.chain.from_iterable(matrix()))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### `async for item in zip_longest(*iterables, fillvalue=None)`

Zip iterables, filling missing values with fillvalue.

```python
import asyncstdlib as a

# Fill missing values
async for pair in a.zip_longest([1, 2, 3], ["a", "b"], fillvalue="NONE"):
    print(pair)  # (1,'a'), (2,'b'), (3,'NONE')

# Merge dictionaries with different keys
async def dict_items(d):
    for k, v in d.items():
        yield k, v

dict1 = {"a": 1, "b": 2}
dict2 = {"b": 20, "c": 30}

merged = await a.dict(
    a.zip_longest(dict_items(dict1), dict_items(dict2), fillvalue=(None, None))
)
```

## Iterator Filtering

### `async for item in compress(data, selectors)`

Filter data based on boolean selector iterable.

```python
import asyncstdlib as a

data = [1, 2, 3, 4, 5, 6, 7, 8]
selectors = [True, False, True, False, True, False, True, False]

async for item in a.compress(data, selectors):
    print(item)  # 1, 3, 5, 7
```

### `async for item in dropwhile(predicate, iterable)`

Drop items while predicate is true, then return rest.

```python
import asyncstdlib as a

async def is_negative(x):
    return x < 0

data = [-1, -2, -3, 0, 1, 2, 3]

async for item in a.dropwhile(is_negative, data):
    print(item)  # 0, 1, 2, 3 (drops -1, -2, -3)
```

### `async for item in filterfalse(predicate, iterable)`

Return items where predicate is false (opposite of filter).

```python
import asyncstdlib as a

async def is_even(x):
    return x % 2 == 0

data = [1, 2, 3, 4, 5, 6]

# Get odd numbers
async for item in a.filterfalse(is_even, data):
    print(item)  # 1, 3, 5
```

### `async for item in takewhile(predicate, iterable)`

Take items while predicate is true, then stop.

```python
import asyncstdlib as a

async def is_positive(x):
    return x > 0

data = [1, 2, 3, -1, 2, 3]

# Stop at first non-positive
async for item in a.takewhile(is_positive, data):
    print(item)  # 1, 2, 3 (stops before -1)
```

### `async for item in islice(iterable, start, stop, step)`

Slice an async iterable.

```python
import asyncstdlib as a

data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Basic slice
async for item in a.islice(data, 3, 7):
    print(item)  # 3, 4, 5, 6

# With step
async for item in a.islice(data, None, None, 2):
    print(item)  # 0, 2, 4, 6, 8

# From start
async for item in a.islice(data, 5):
    print(item)  # 0, 1, 2, 3, 4
```

## Iterator Transforming

### `async for item in accumulate(iterable, function=add, initial=None)`

Running reduction (cumulative sum by default).

```python
import asyncstdlib as a
from operator import mul

# Running sum (default)
data = [1, 2, 3, 4, 5]
async for total in a.accumulate(data):
    print(total)  # 1, 3, 6, 10, 15

# Running product
async for product in a.accumulate(data, function=mul):
    print(product)  # 1, 2, 6, 24, 120

# With initial value
async for total in a.accumulate(data, initial=10):
    print(total)  # 10, 11, 13, 16, 20, 25

# Version changed: 3.13.2 - initial=None means no initial value
```

### `async for item in starmap(function, iterable)`

Apply function to argument tuples from iterable.

```python
import asyncstdlib as a
from operator import mul

# Function takes multiple arguments
async def power(base, exp):
    return base ** exp

args = [(2, 3), (3, 2), (4, 1)]
async for result in a.starmap(power, args):
    print(result)  # 8, 9, 4

# Equivalent to:
# async for args_tuple in args:
#     result = await power(*args_tuple)
```

## Iterator Splitting

### `iterators = tee(iterable, n=2, *, lock=None)`

Split one iterator into multiple independent iterators.

```python
import asyncstdlib as a

# Split into two iterators
sensor_data = get_sensor_stream()
previous, current = a.tee(sensor_data, n=2)

# Advance one iterator
await a.anext(previous)

# Compute derivative (difference between consecutive values)
derivative = a.map(operator.sub, previous, current)

async for diff in derivative:
    print(diff)

# Use as context manager to ensure cleanup
async with a.tee(sensor_data, n=2) as (iter1, iter2):
    async for item in iter1:
        process1(item)
    async for item in iter2:
        process2(item)
```

**With lock for concurrency safety:**

```python
from asyncio import Lock

# If underlying iterator is not concurrency-safe, provide a lock
async with a.tee(sensor_data, n=2, lock=Lock()) as (iter1, iter2):
    # Safe concurrent access
    await gather(consume(iter1), consume(iter2))
```

**Notes:**
- All iterators share the same items from the original iterable
- Items are buffered until all iterators have yielded them
- Works lazily and can handle infinite iterables (if all advance)
- `tee` of a `tee` shares buffers with parent, siblings, and children
- Returns custom type (not tuple) with `aclose()` method

**Version added:** `lock` parameter added in version 3.10.5.
**Version changed:** Buffer sharing improved in version 3.13.2.

### `async for (a, b) in pairwise(iterable)`

Yield overlapping pairs of consecutive items.

```python
import asyncstdlib as a

data = [1, 2, 3, 4, 5]

async for first, second in a.pairwise(data):
    print(first, second)  # (1,2), (2,3), (3,4), (4,5)

# Compute differences between consecutive values
async for diff in a.map(operator.sub, 
                        a.tee(a.pairwise(data))[0],
                        a.tee(a.pairwise(data))[1]):
    print(diff)
```

**Version added:** 3.10.0

### `async for batch in batched(iterable, n, strict=False)`

Batch items into tuples of length n.

```python
import asyncstdlib as a

data = [1, 2, 3, 4, 5, 6, 7]

# Batch into groups of 3
async for batch in a.batched(data, 3):
    print(batch)  # (1,2,3), (4,5,6), (7,)

# Strict mode - raises ValueError if last batch incomplete
try:
    async for batch in a.batched(data, 3, strict=True):
        print(batch)
except ValueError:
    print("Last batch incomplete!")

# Use case: process items in batches
async def process_batch(items):
    await db.insert_many(items)

async for batch in a.batched(large_dataset, 100):
    await process_batch(batch)
```

**Version added:** 3.11.0
**Version added:** `strict` parameter added in version 3.13.0.

### `async for (key, group_iter) in groupby(iterable, key=None)`

Group consecutive items with the same key.

```python
import asyncstdlib as a

# Group by first character
async def get_words():
    yield "apple"
    yield "application"
    yield "banana"
    yield "blueberry"
    yield "cherry"

async for letter, group in a.groupby(get_words(), key=lambda w: w[0]):
    words = await a.list(group)
    print(letter, words)
    # 'a' ['apple', 'application']
    # 'b' ['banana', 'blueberry']
    # 'c' ['cherry']

# Groups are consecutive - same key can appear multiple times
data = [1, 1, 2, 2, 1]  # Note: 1 appears in two groups
async for key, group in a.groupby(data):
    items = await a.list(group)
    print(key, items)
    # 1 [1, 1]
    # 2 [2, 2]
    # 1 [1]
```

**Important:**
- Groups are consecutive with respect to the original iterable
- Previous groups are no longer accessible if groupby advances
- Not safe to concurrently advance groupby and its group iterators
- Unlike sync version, sorting beforehand defeats lazy evaluation advantage

## Usage Patterns

### Sliding window

```python
import asyncstdlib as a

async def sliding_window(iterable, window_size):
    """Create sliding window of fixed size"""
    iterators = a.tee(iterable, window_size)
    
    # Advance each iterator by its index
    for i, it in enumerate(iterators):
        for _ in range(i):
            await a.anext(it)
    
    # Zip to get windows
    async for window in a.zip(*iterators):
        yield window

# Usage
async for window in sliding_window([1, 2, 3, 4, 5], 3):
    print(window)  # (1,2,3), (2,3,4), (3,4,5)
```

### Running statistics

```python
import asyncstdlib as a

async def running_average(iterable):
    """Compute running average"""
    for total, count in a.accumulate(
        a.zip(iterable, a.iter([1] * 1000)),  # Count items
        lambda tc, xc: (tc[0] + xc[0], tc[1] + xc[1])
    ):
        yield total / count

async for avg in running_average(data_stream):
    print(f"Running average: {avg}")
```

### Chunked processing

```python
import asyncstdlib as a

async def process_in_chunks(stream, chunk_size):
    """Process stream in fixed-size chunks"""
    async for chunk in a.batched(stream, chunk_size):
        await process_chunk(list(chunk))

# Process 1000 items at a time
await process_in_chunks(large_stream, 1000)
```

### Event deduplication

```python
import asyncstdlib as a

async def deduplicate_consecutive(event_stream):
    """Remove consecutive duplicate events"""
    async for event_type, group in a.groupby(event_stream):
        # Yield only one instance of each consecutive group
        yield event_type

# Process only when event type changes
async for event_type in deduplicate_consecutive(events):
    await handle_event_type_change(event_type)
```

## Notes

- All functions are **async neutral** - work with both sync and async iterables
- Functions automatically detect iterable type and handle appropriately
- Mixed sync/async iterables supported
- Most functions are lazy and work with infinite iterables (when appropriate)
