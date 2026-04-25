# more_itertools Reference

Additional utility functions beyond the standard itertools module. These provide common patterns for working with async iterables.

## Taking Functions

### `take(n: int, iterable: AnyIterable[T]) -> list[T]`

Return the first n items of iterable as a list. If there are fewer than n items, all available items are returned. n must be >= 0.

```python
from aioitertools.more_itertools import take

# Take first N items
first_two = await take(2, [1, 2, 3, 4, 5])
print(first_two)  # [1, 2]

# Take more than available (returns all)
all_items = await take(100, small_list)

# Take zero items (empty list)
empty = await take(0, large_iterator)
print(empty)  # []

# With async iterator
first_page = await take(20, paginated_results)
```

**Parameters:**
- `n`: Number of items to take (must be >= 0)
- `iterable`: Iterable or AsyncIterable of type T

**Returns:** `list[T]`

**Raises:** `ValueError` if n < 0

---

## Chunking Functions

### `chunked(iterable: AnyIterable[T], n: int) -> AsyncIterable[list[T]]`

Break iterable into chunks of length n. The last chunk may be shorter if total items not divisible by n.

```python
from aioitertools.more_itertools import chunked

# Process in batches of 100
async for chunk in chunked(large_dataset, n=100):
    await process_batch(chunk)  # chunk is a list of up to 100 items

# Example with exact division
async for chunk in chunked([1, 2, 3, 4, 5], n=2):
    ...  # [1,2], [3,4], [5]

# Use case: batch API requests
async for batch in chunked(user_ids, n=50):
    results = await fetch_users_batch(batch)
    await store_results(results)
```

**Parameters:**
- `iterable`: Iterable or AsyncIterable of type T
- `n`: Chunk size (must be > 0)

**Returns:** `AsyncIterable[list[T]]`

---

## Splitting Functions

### `before_and_after(predicate: Predicate[T], iterable: AnyIterable[T]) -> tuple[AsyncIterable[T], AsyncIterable[T]]`

Split iterator into two parts at the point where predicate first returns False. Returns tuple of (items_before_split, items_after_split).

**Important:** The first iterator must be fully consumed before the second iterator can generate valid results.

```python
from aioitertools.more_itertools import before_and_after

# Split string at first lowercase letter
it = iter("ABCdEfGhI")
uppercase, remainder = await before_and_after(str.isupper, it)

uppercase_str = ''.join([char async for char in uppercase])
print(uppercase_str)  # "ABC"

remainder_str = ''.join([char async for char in remainder])
print(remainder_str)  # "dEfGhI"

# Split log at error section
async def is_info_level(line):
    return line.startswith("INFO")

log_iter = read_log_file()
info_logs, error_logs = await before_and_after(is_info_level, log_iter)

# MUST consume info_logs first!
info_lines = [line async for line in info_logs]

# Now can safely consume error_logs
error_lines = [line async for line in error_logs]

# Async predicate example
async def is_valid_record(record):
    return await validate_record(record)

valid_iter, invalid_iter = await before_and_after(is_valid_record, records)
```

**Parameters:**
- `predicate`: Callable (sync or async) returning bool
- `iterable`: Iterable or AsyncIterable of type T

**Returns:** `tuple[AsyncIterable[T], AsyncIterable[T]]` - (items where predicate is True, remaining items starting from first False)

**Critical Note:** 
- The first returned iterator MUST be fully consumed before the second can produce valid results
- This is due to internal buffering: the split point isn't known until predicate returns False
- Attempting to read from the second iterator before exhausting the first will fail or produce incorrect results

---

## Common Patterns

### Batching with Progress Tracking

Combine `chunked` with progress tracking:

```python
from aioitertools.more_itertools import chunked
from aioitertools import enumerate

async def process_with_progress(items, batch_size=100):
    total = len(items) if hasattr(items, '__len__') else None
    batch_num = 0
    
    async for batch_num, chunk in enumerate(chunked(items, batch_size)):
        await process_batch(chunk)
        
        if total:
            processed = (batch_num + 1) * batch_size
            progress = min(processed / total, 1.0)
            print(f"Progress: {progress*100:.1f}%")
```

### Head and Tail Split

Use `take` and `before_and_after` to split iterables:

```python
from aioitertools.more_itertools import take, before_and_after
from aioitertools import islice

# Get first N and rest
async def head_and_tail(iterable, n):
    """Split into first n items and remainder."""
    head = await take(n, iterable)
    # Note: This consumes the iterator, so this pattern only works
    # if you can recreate the iterator or use tee()
    return head

# Better approach with tee for single-pass iterators
from aioitertools import tee

async def split_at_n(iterable, n):
    """Split async iterator at position n."""
    iter1, iter2 = tee(iterable, 2)
    head = await take(n, iter1)
    
    # Skip first n items from second iterator
    async def skip_n(itr, count):
        async for _ in islice(itr, count):
            pass
        async for item in itr:
            yield item
    
    tail = skip_n(iter2, n)
    return head, tail
```

### Conditional Processing with before_and_after

Process different sections of data differently:

```python
from aioitertools.more_itertools import before_and_after

async def process_csv_with_header(lines):
    """Process CSV where first section is header, rest is data."""
    
    async def is_header(line):
        return line.startswith("#") or "HEADER" in line.upper()
    
    header_iter, data_iter = await before_and_after(is_header, lines)
    
    # Process header section first (REQUIRED)
    headers = [line async for line in header_iter]
    parse_headers(headers)
    
    # Now process data section
    async for line in data_iter:
        record = parse_record(line)
        await store_record(record)
```

### Streaming Batches with Timeout

Process chunks with timeout handling:

```python
from aioitertools.more_itertools import chunked
import asyncio

async def process_with_timeout(items, batch_size=50, timeout=30):
    """Process items in batches with per-batch timeout."""
    
    try:
        async for chunk in asyncio.wait_for(
            anext(chunked(items, batch_size)),
            timeout=timeout
        ):
            await process_batch(chunk)
    except asyncio.TimeoutError:
        ...  # Handle timeout - batch took too long
```

## Comparison with Standard Itertools

| Function | Purpose | Equivalent Pattern |
|----------|---------|-------------------|
| `take(n, itr)` | Get first n items as list | `list(islice(itr, n))` |
| `chunked(itr, n)` | Split into fixed-size chunks | Manual loop with islice |
| `before_and_after(pred, itr)` | Split at predicate boundary | Manual state tracking |

## Implementation Notes

- `take`: Uses `islice` internally, efficient for large iterables
- `chunked`: Repeatedly calls `take`, maintains minimal buffering
- `before_and_after`: Uses asyncio.Future for transition signaling between iterators; requires careful consumption order
