# Contextlib Library

The `asyncstdlib.contextlib` module implements Python's `contextlib` for async iterables and async context managers.

## AbstractContextManager

```python
class AbstractContextManager
```

Abstract base class for asynchronous context managers. Use to check whether an object is an async context manager. Classes inheriting from it must implement `__aenter__`; the default returns the context manager itself. Added in version 1.1.0.

## ContextDecorator

```python
class ContextDecorator
```

Base class to turn an async context manager into a decorator. When decorating a function, the context manager is automatically entered on await:

```python
class MyContext(ContextDecorator):
    async def __aenter__(self):
        print("entering")
        return self

    async def __aexit__(self, *exc):
        print("exiting")

@MyContext()
async def func():
    print("running...")
```

The context manager can still be used in `async with` statements. Since functions are decorated with an existing instance, implement `_recreate_cm(self) -> Self` if the context is not safe to enter multiple times or concurrently.

## contextmanager

```python
@contextmanager(func: (...) -> async iter T) -> (...) -> async with T
async with contextmanager(func: (...) -> async iter T)(...) as :T
```

Decorator for an async generator function that creates an async context manager. The generator should `yield` once — the body of the context manager executes at the yield point. If `yield` provides a value, it becomes the context value.

```python
from asyncstdlib import contextmanager

@contextmanager
async def managed_resource(*args, **kwargs):
    # __aenter__ logic
    resource = await acquire(*args, **kwargs)
    try:
        yield resource  # context value
    finally:
        # __aexit__ logic
        await release(resource)
```

If an exception ends the context block, it is re-raised at the `yield` via `athrow()`. Wrap `yield` in a `try` statement to handle it. The created context manager is a `ContextDecorator` and can also be used as a decorator (added 3.12.2).

## closing

```python
async with closing(thing: AC) as :AC
```

Create an async context manager that calls `await thing.aclose()` on exit. Useful for safe cleanup of objects that need reliable cleanup but do not support the context manager protocol, such as async iterators holding resources:

```python
import asyncstdlib as a

async with a.closing(a.iter(something)) as async_iter:
    async for element in async_iter:
        ...
```

## nullcontext

```python
async with nullcontext(enter_result: T) as :T
```

An async context manager that only returns `enter_result`. A neutral placeholder where an async context manager is semantically required but not meaningful:

```python
async def safe_fetch(source):
    if not isinstance(source, AsyncIterator):
        acm = a.closing(a.iter(source))
    else:
        acm = a.nullcontext(source)
    async with acm as async_iter:
        ...
```

## ExitStack

```python
class ExitStack
```

Context manager emulating several nested context managers. Once entered, `enter_context()` can programmatically enter further context managers. On unwind, managers are exited in LIFO order. Unlike `contextlib.AsyncExitStack`, this is **async neutral** — no separate methods for sync vs async arguments. Added in version 1.1.0.

### enter_context

```python
await enter_context(cm: (async) with T) -> T
```

Enter a context manager and register it for exit on stack unwind. Equivalent to using `cm` in an `async with` statement — if `cm` only supports `with`, it is silently promoted.

```python
# Instead of:
async with cm_a as value_a, cm_b as value_b:
    ...

# Programmatically:
async with a.ExitStack() as stack:
    value_a = await stack.enter_context(cm_a)
    value_b = await stack.enter_context(cm_b)
    ...
```

If `__aenter__` throws, the context is not registered for exit (same as `async with`).

### callback

```python
callback(callback: T as (*args, **kwargs) -> None, *args, **kwargs) -> T
```

Register an arbitrary callback invoked on stack unwind. Callbacks are async neutral and do not receive exception details. Method returns the callback unchanged, usable as a decorator.

### push

```python
push(exit: T as {.__aexit__}) -> T
push(exit: T as {.__exit__}) -> T
push(exit: T as (Type[BaseException], BaseException, traceback) -> (await) bool) -> T
```

Register a callback with the standard `__aexit__` signature. Normalizations applied: if `exit` has `__aexit__`, use it; if `exit` has `__exit__`, use it and treat as async. Callbacks receive exception details and may suppress by returning `True`. Returns `exit` unchanged.

Note: `push` only registers the exit handler — it does **not** enter the context manager. Use `enter_context()` to both enter and register.

### pop_all

```python
pop_all() -> ExitStack
```

Transfer all registered callbacks to a new `ExitStack`. Neither calling this method nor closing the original stack invokes these callbacks. Callbacks added after `pop_all()` are unaffected.

### aclose

```python
await aclose() -> None
```

Immediately unwind the context stack. Unlike `contextlib.ExitStack.close()`, this method is async and follows the `aclose` naming convention. Added in version 1.1.0.
