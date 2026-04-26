# Contextlib Library

The `asyncstdlib.contextlib` library implements Python's `contextlib` for (async) iterables and (async) context managers.

## Context Managers

### AbstractContextManager

An abstract base class for asynchronous context managers. Use to check whether an object is an async context manager. A class inheriting from it must implement `__aenter__`; the default returns the context manager itself. Added in version 1.1.0.

### ContextDecorator

Base class to turn an async context manager into a decorator as well. When a function is decorated with an instance, the context manager is automatically entered on `await`. The same instance is entered and exited on every call — if not safe for multiple/concurrent entry, implement `_recreate_cm() -> Self` to create a copy.

```python
import asyncstdlib as a
from typing import Any

class MyDecorator(a.ContextDecorator):
    async def __aenter__(self) -> Any:
        print("entering")
        return self

    async def __aexit__(self, *exc):
        print("exiting")

@MyDecorator()
async def func():
    print("running...")
```

### contextmanager

Create an async context manager from an async generator function. The generator should `yield` once — the body of the context executes at that point. If `yield` provides a value, it becomes the context value. Exceptions from the context block are re-raised at the `yield` via `athrow()`. Wrap `yield` in `try/except` to handle exceptions.

The created context manager is a `ContextDecorator` and can also be used as a decorator (added in 3.12.2).

```python
from asyncstdlib import contextmanager

@contextmanager
async def managed_resource(*args):
    resource = await acquire(*args)
    try:
        yield resource
    finally:
        await release(resource)

# As async with
async with managed_resource("db") as conn:
    await conn.query("SELECT 1")

# As decorator
@managed_resource("db")
async def work(conn):
    await conn.query("SELECT 1")
```

### closing

Create an async context manager that guarantees `await thing.aclose()` on exit. Useful for objects needing reliable cleanup without supporting the context manager protocol, such as async iterators holding resources.

```python
import asyncstdlib as a

async with a.closing(a.iter(something)) as async_iter:
    async for element in async_iter:
        process(element)
# aclose() called automatically
```

### nullcontext

Create an async context manager that only returns `enter_result`. Serves as a placeholder where an async context manager is semantically required but not meaningful.

```python
import asyncstdlib as a

async def safe_fetch(source):
    if not isinstance(source, AsyncIterator):
        acm = a.closing(a.iter(source))
    else:
        acm = a.nullcontext(source)
    async with acm as async_iter:
        async for item in async_iter:
            process(item)
```

### ExitStack

Context manager emulating several nested context managers. Once entered, `enter_context()` programmatically enters further context managers. On unwind, managers are exited in LIFO order. Primary use-case: dynamically sized or optional context managers. Also supports arbitrary cleanup callbacks via `push()` and `callback()`.

Unlike `contextlib.AsyncExitStack`, this is async neutral — no separate methods for sync vs async arguments. Added in version 1.1.0.

```python
import asyncstdlib as a

# Programmatically enter context managers
async with a.ExitStack() as stack:
    conn_a = await stack.enter_context(cm_a)
    conn_b = await stack.enter_context(cm_b)
    # Register cleanup callback
    stack.callback(lambda: print("cleanup"))
    # Register exit handler
    stack.push(my_exit_handler)
```

Methods:
- `enter_context(cm)` — enter context manager, register for exit on success. Async neutral — accepts both sync and async context managers.
- `callback(cb, *args, **kwargs)` — register arbitrary cleanup callback. Returns the callback unchanged (usable as decorator). Does not receive exception details.
- `push(exit)` — register callback with standard `__aexit__` signature. Normalizes objects with `__aexit__`, `__exit__`, or plain callables. Returns exit unchanged.
- `pop_all()` — transfer all callbacks to a new ExitStack. Original stack no longer invokes them.
- `aclose()` — immediately unwind the context stack (async, unlike `close()` in stdlib).
