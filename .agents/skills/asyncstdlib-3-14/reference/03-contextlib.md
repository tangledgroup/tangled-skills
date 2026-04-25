# The Contextlib Library

The `asyncstdlib.contextlib` library implements Python's contextlib module for async context managers.

## Context Managers

### `AbstractContextManager`

Abstract base class for asynchronous context managers.

```python
from asyncstdlib.contextlib import AbstractContextManager

# Check if object is an async context manager
if isinstance(obj, AbstractContextManager):
    async with obj as resource:
        use(resource)

# Create custom async context manager
class MyContext(AbstractContextManager):
    async def __aenter__(self):
        # Setup code
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup code
        pass
```

**Version added:** 1.1.0

### `ContextDecorator`

Base class to turn an async context manager into a decorator.

```python
from asyncstdlib.contextlib import ContextDecorator

class TimingContext(ContextDecorator):
    def __init__(self, name):
        self.name = name
    
    async def __aenter__(self):
        print(f"Starting {self.name}")
        self.start = asyncio.get_event_loop().time()
        return self
    
    async def __aexit__(self, *exc):
        elapsed = asyncio.get_event_loop().time() - self.start
        print(f"Finished {self.name} in {elapsed:.2f}s")

# Use as context manager
async with TimingContext("operation"):
    await do_work()

# Use as decorator (automatically enters context)
@TimingContext("operation")
async def my_function():
    await do_work()
```

**Important:** Since functions are decorated with an existing context manager instance, the same instance is entered and exited on every call. If the context is not safe to be entered multiple times concurrently, implement `_recreate_cm(self) -> Self` to create a copy.

### `@contextmanager(func)`

Create an async context manager from an async generator function.

```python
from asyncstdlib.contextlib import contextmanager

@contextmanager
async def transaction(db):
    """Database transaction with rollback on error"""
    await db.begin()
    try:
        yield db  # Context value
        await db.commit()
    except Exception:
        await db.rollback()
        raise

# Usage
async with transaction(database) as db:
    await db.execute("INSERT INTO users VALUES (...)")
    await db.execute("UPDATE stats SET count = count + 1")
# Automatically commits or rolls back
```

**With yield value:**

```python
@contextmanager
async def timed_operation(name):
    """Context manager that yields elapsed time"""
    start = asyncio.get_event_loop().time()
    try:
        yield  # Execute context block
    finally:
        elapsed = asyncio.get_event_loop().time() - start
        print(f"{name} took {elapsed:.2f}s")

async with timed_operation("fetch") as _:
    await fetch_data()
```

**As decorator:**

```python
from asyncstdlib.contextlib import contextmanager

@contextmanager
async def lock_resource(name):
    async with locks[name]:
        yield

@lock_resource("database")
async def update_database():
    # Automatically acquires and releases lock
    await db.update(...)
```

**Version added:** Context manager is a `ContextDecorator` since version 3.12.2.

### `async with closing(thing) as thing`

Create an async context manager that calls `aclose()` on exit.

```python
import asyncstdlib as a

# Ensure async iterator is properly closed
async with a.closing(a.iter(large_dataset)) as async_iter:
    async for item in async_iter:
        if should_stop():
            break  # Iterator still closed properly

# Use with any object having aclose() method
async with a.closing(async_file) as file:
    data = await file.read()
```

**See also:** `scoped_iter()` for safer iterator handling.

### `async with nullcontext(enter_result) as enter_result`

Create a no-op async context manager (neutral element).

```python
import asyncstdlib as a

def get_context(source):
    """Return appropriate context manager based on source type"""
    if not isinstance(source, AsyncIterator):
        return a.closing(a.iter(source))
    else:
        return a.nullcontext(source)  # No cleanup needed

async with get_context(data_source) as iterator:
    async for item in iterator:
        process(item)

# Prevent closing existing context manager
existing_cm = await acquire_context()
async with a.nullcontext(existing_cm) as cm:
    use(cm)
# existing_cm is NOT closed
```

**Use cases:**
- Optional context managers with neutral default
- Preventing closure of existing context managers
- Conditional context management without code duplication

## ExitStack

### `class ExitStack`

Context manager for managing multiple nested contexts programmatically.

```python
from asyncstdlib.contextlib import ExitStack

async with ExitStack() as stack:
    # Enter multiple contexts programmatically
    conn1 = await stack.enter_context(connect_db("primary"))
    conn2 = await stack.enter_context(connect_db("replica"))
    
    # All contexts exited in LIFO order when stack unwinds
# conn2 closed first, then conn1
```

**Dynamic number of contexts:**

```python
from asyncstdlib.contextlib import ExitStack

async def process_multiple_sources(sources):
    async with ExitStack() as stack:
        connections = []
        for source in sources:
            conn = await stack.enter_context(connect(source))
            connections.append(conn)
        
        # Process all connections
        for conn in connections:
            await conn.process()
    
    # All connections closed automatically
```

### `await enter_context(cm)`

Enter a context manager and register it for exit.

```python
from asyncstdlib.contextlib import ExitStack

async with ExitStack() as stack:
    # Equivalent to: async with cm_a as value_a, cm_b as value_b:
    value_a = await stack.enter_context(cm_a)
    value_b = await stack.enter_context(cm_b)
    
    use(value_a, value_b)
```

**Async neutral:** Works with both sync and async context managers. Sync context managers are automatically promoted.

### `callback = callback(func, *args)` / `push(callable)`

Register cleanup callbacks (similar to `defer` in other languages).

```python
from asyncstdlib.contextlib import ExitStack

async with ExitStack() as stack:
    # Register simple callback
    stack.push(async def log_cleanup(): await log("Cleanup complete"))
    
    # Register callback with arguments
    async def close_file(handle, mode):
        await handle.close(mode)
    
    file_handle = await open_file("data.txt")
    stack.callback(close_file, file_handle, "write")
    
    # Callbacks executed in LIFO order on exit
```

**Practical example:**

```python
from asyncstdlib.contextlib import ExitStack

async def atomic_operation():
    async with ExitStack() as stack:
        # Acquire resources
        lock = await stack.enter_context(acquire_lock())
        connection = await stack.enter_context(get_connection())
        
        # Register cleanup
        temp_file = await create_temp()
        stack.push(async def cleanup_temp(path): await remove(path), temp_file)
        
        try:
            # Do work
            await process_data(connection)
        except Exception:
            # All resources cleaned up even on error
            raise
```

### `await pop_all()`

Pop all registered callbacks and context managers without executing them.

```python
from asyncstdlib.contextlib import ExitStack

async with ExitStack() as stack:
    await stack.enter_context(context1)
    stack.callback(cleanup1)
    
    # Remove all without executing
    await stack.pop_all()
    
    # context1 and cleanup1 will NOT be executed
```

### `await aclose()`

Close the ExitStack, executing all registered callbacks and exiting all contexts.

```python
from asyncstdlib.contextlib import ExitStack

stack = ExitStack()
async with stack:
    await stack.enter_context(context1)
    stack.callback(cleanup1)

# Equivalent to explicit close
stack = ExitStack()
await stack.__aenter__()
try:
    await stack.enter_context(context1)
finally:
    await stack.aclose()
```

## Usage Patterns

### Conditional context management

```python
from asyncstdlib.contextlib import ExitStack, nullcontext

async def process_with_optional_logging(data, enable_logging=False):
    context = LoggingContext() if enable_logging else nullcontext(None)
    
    async with context:
        await process(data)
```

### Resource pooling

```python
from asyncstdlib.contextlib import ExitStack

class ResourcePool:
    def __init__(self, *resources):
        self.resources = resources
    
    async def use_all(self):
        async with ExitStack() as stack:
            acquired = [
                await stack.enter_context(resource.acquire())
                for resource in self.resources
            ]
            await self.process(acquired)
```

### Transaction management

```python
from asyncstdlib.contextlib import contextmanager

@contextmanager
async def nested_transactions(*databases):
    """Manage transactions across multiple databases"""
    async with ExitStack() as stack:
        connections = [
            await stack.enter_context(db.connect())
            for db in databases
        ]
        
        # Begin all transactions
        for conn in connections:
            await conn.begin()
        
        try:
            yield connections
            # Commit all
            for conn in connections:
                await conn.commit()
        except Exception:
            # Rollback all
            for conn in connections:
                await conn.rollback()
            raise
```

### Deferred cleanup

```python
from asyncstdlib.contextlib import ExitStack

async def process_with_cleanup():
    async with ExitStack() as stack:
        # Setup
        temp_dir = await create_temp_dir()
        stack.push(async def remove_dir(path): await shutil.rmtree(path), temp_dir)
        
        # Register multiple cleanup steps
        logger = await get_logger()
        stack.callback(logger.flush)
        stack.callback(logger.close)
        
        # Do work - all cleanup happens automatically
        await do_work(temp_dir)
```

## Notes

- `ExitStack` is **async neutral** - works with both sync and async context managers
- Unlike `contextlib.AsyncExitStack`, there are no separate methods for sync vs async arguments
- Contexts and callbacks are exited in LIFO (last-in, first-out) order
- All context managers entered via `enter_context()` are guaranteed to be exited
- Callbacks registered via `callback()` or `push()` are guaranteed to be called
