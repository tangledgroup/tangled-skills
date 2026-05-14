# RPC Framework

The `aiozmq.rpc` module provides a high-level Remote Procedure Call framework on top of ZeroMQ transports. It supports three communication patterns: request-reply, push-pull (pipeline), and publish-subscribe.

**Note**: The RPC module is optional and requires msgpack (`pip install msgpack-python>=0.4.0`).

## Request-Reply

The standard RPC pattern. Client calls a remote function on the server and waits for the returned value. If the remote function raises an exception, it propagates to the client side. Uses DEALER/ROUTER sockets.

### Basic Usage

```python
import asyncio
from aiozmq import rpc


class Handler(rpc.AttrHandler):

    @rpc.method
    def remote(self, arg1, arg2):
        return arg1 + arg2


@asyncio.coroutine
def go():
    server = yield from rpc.serve_rpc(
        Handler(), bind='tcp://127.0.0.1:5555'
    )
    client = yield from rpc.connect_rpc(
        connect='tcp://127.0.0.1:5555'
    )

    ret = yield from client.call.remote(1, 2)
    assert ret == 3

    server.close()
    client.close()
```

### serve_rpc

`aiozmq.rpc.serve_rpc(handler, *, bind=None, connect=None, loop=None, log_exceptions=False, exclude_log_exceptions=(), translation_table=None, timeout=None)`

Creates and binds an RPC server. Returns a `Service` instance.

- `handler` — an `AbstractHandler` (usually `AttrHandler`) that processes incoming calls
- `log_exceptions` (bool) — log exceptions from remote calls
- `exclude_log_exceptions` (sequence) — exception types to exclude from logging
- `translation_table` (dict) — custom value translators
- `timeout` (float) — server-side timeout for handling async calls; raises `asyncio.TimeoutError` if exceeded. Should be slightly longer than client-side timeout.

### connect_rpc

`aiozmq.rpc.connect_rpc(*, connect=None, bind=None, loop=None, error_table=None, timeout=None, translation_table=None)`

Creates and connects an RPC client. Returns an `RPCClient` instance.

- `error_table` (dict) — custom exception translators: `{exception_full_name: ExceptionClass}`
- `timeout` (float) — client-side timeout; raises `asyncio.TimeoutError` if exceeded. Late server responses are ignored after timeout.
- `translation_table` (dict) — custom value translators

### RPCClient

Returned by `connect_rpc()`. Inherits from `Service`.

- `client.call.ns.method(1, 2, 3)` — make remote call with positional args
- `client.call.ns.method(1, b=2, c=3)` — supports named parameters
- `client.with_timeout(1.5).call.func()` — override timeout for single call
- `with client.with_timeout(1.5) as new_client:` — context manager form for multiple calls
- `client.transport` — readonly property, the underlying `ZmqTransport`
- `client.close()` — stop serving
- `client.wait_closed()` — coroutine, wait until service is closed

## Push-Pull (Pipeline)

Fire-and-forget pattern. Client calls a remote function but does not wait for a result. Exceptions are only logged server-side. Uses PUSH/PULL sockets.

```python
import asyncio
from aiozmq import rpc


class Handler(rpc.AttrHandler):

    @rpc.method
    def remote(self):
        do_something(arg)


@asyncio.coroutine
def go():
    server = yield from rpc.serve_pipeline(
        Handler(), bind='tcp://127.0.0.1:5555'
    )
    client = yield from rpc.connect_pipeline(
        connect='tcp://127.0.0.1:5555'
    )

    ret = yield from client.notify.remote(1)
```

### serve_pipeline / connect_pipeline

Same parameters as `serve_rpc`/`connect_rpc` (without `timeout` on client side since there's no response to time out).

- `PipelineClient` — returned by `connect_pipeline()`. Use `client.notify.ns.method(args)` for fire-and-forget calls. Returns `None`.

## Publish-Subscribe

PubSub pattern with topic-based filtering. Server subscribes to topics; client publishes to specific topics. Uses PUB/SUB sockets.

```python
import asyncio
from aiozmq import rpc


class Handler(rpc.AttrHandler):

    @rpc.method
    def remote(self):
        do_something(arg)


@asyncio.coroutine
def go():
    server = yield from rpc.serve_pubsub(
        Handler(), subscribe='topic',
        bind='tcp://127.0.0.1:5555'
    )
    client = yield from rpc.connect_pubsub(
        connect='tcp://127.0.0.1:5555'
    )

    ret = yield from client.publish('topic').remote(1)
```

### serve_pubsub / connect_pubsub

`serve_pubsub()` adds a `subscribe` parameter (str, bytes, or iterable of str/bytes) to specify topic subscriptions.

- `PubSubClient` — returned by `connect_pubsub()`. Use `client.publish('topic').ns.method(args)` for topic-targeted calls. Returns `None`.

## Exception Translation at Client Side

When a remote server method raises an exception, it is serialized and re-raised on the client side:

```python
try:
    yield from client.call.func_raises_value_error()
except ValueError as exc:
    log.exception(exc)
```

Translation rules:
- Server sends full exception class name (`"package.subpackage.MyError"`) and constructor args
- All builtin exceptions are translated by default
- `NotFoundError` and `ParameterError` are translated by default
- Custom exceptions require an `error_table`:

```python
from mod1 import Error1
from pack.mod2 import Error2

error_table = {
    'mod1.Error1': Error1,
    'pack.mod2.Error2': Error2
}

client = yield from rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    error_table=error_table
)
```

- User-defined translators are searched first
- If no translation is found, `GenericError(exception_name, args)` is raised

## Signature Validation

Optional validation of remote call signatures using Python type annotations. Validation occurs server-side; errors propagate to client as `ParameterError`.

```python
class Handler(rpc.AttrHandler):

    @rpc.method
    def func(self, arg1: int, arg2) -> float:
        return arg1 + arg2
```

- Parameter `arg1` has annotation `int` — actual value is converted via `annotation(value)`
- Return annotation `float` validates the return value
- Unannotated parameters pass through as-is
- Annotation should be any callable accepting a single value and returning the validated value
- If annotation raises, the exception is sent to client wrapped in `ParameterError`

Custom validators:

```python
def int_or_none(val):
    if isinstance(val, int) or val is None:
        return val
    else:
        raise ValueError('bad value')


class Handler(rpc.AttrHandler):
    @rpc.method
    def func(self, arg: int_or_none):
        return arg
```

For complex validation, the [trafaret](https://github.com/Deepwalker/trafaret) library integrates well:

```python
import trafaret as t


class Handler(rpc.AttrHandler):
    @rpc.method
    def func(self, arg: t.Int | t.Null):
        return arg
```

## Value Translators

aiozmq.rpc uses msgpack for serialization. All JSON-compatible types pass through automatically. Additionally, all `list` objects are converted to `tuple` (tuples are hashable and can be dict keys).

For custom objects, register a translator at both server and client:

```python
import msgpack


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return (self.x, self.y) == (other.x, other.y)
        return NotImplemented


translation_table = {
    0: (Point,
        lambda value: msgpack.packb((value.x, value.y)),
        lambda binary: Point(*msgpack.unpackb(binary))),
}

server = yield from rpc.serve_rpc(
    ServerHandler(), bind='tcp://127.0.0.1:5555',
    translation_table=translation_table
)
client = yield from rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    translation_table=translation_table
)

ret = yield from client.call.remote(Point(1, 2))
assert ret == Point(1, 2)
```

Translation table format:
- Keys: integers in range [0, 127]. Use low numbers (0+) for custom translators.
- Values: tuples of `(translated_class, packer, unpacker)`
  - `translated_class` — the class to serialize
  - `packer` — callable(instance) → bytes
  - `unpacker` — callable(bytes) → instance
- Table is searched in ascending key order
- Be careful with ordering: placing `object` at position 0 would catch everything

**Warning**: Avoid using `pickle` for packers/unpackers. Pickle serializes entire object graphs, potentially sending large portions of your program over the network.

### Predefined Translators

| Ordinal | Class |
|---------|-------|
| 123 | datetime.tzinfo |
| 124 | datetime.timedelta |
| 125 | datetime.time |
| 126 | datetime.datetime |
| 127 | datetime.date |

pytz timezones work automatically via the `tzinfo` translator (ordinal 123) since they inherit from `datetime.tzinfo`. These use pickle internally, which is safe because datetime classes are terminal types with no foreign references.

## Logging Exceptions at Server Side

By default, aiozmq.rpc does not log exceptions from remote calls. Enable logging:

```python
server = yield from rpc.serve_rpc(
    handler, bind='tcp://127.0.0.1:7777',
    log_exceptions=True
)
```

To exclude expected exceptions from the log:

```python
server = yield from rpc.serve_rpc(
    handler, bind='tcp://127.0.0.1:7777',
    log_exceptions=True,
    exclude_log_exceptions=(MyError, OtherError)
)
```

Logs go to `aiozmq.rpc.logger` (a `logging.Logger` named `"aiozmq.rpc"`). Configure handlers as needed.

## RPC Handlers

### @rpc.method Decorator

Marks a function as an RPC endpoint handler. Supports type annotations for validation.

```python
@aiozmq.rpc.method
def remote(a: int, b: int) -> int:
    return a + b
```

### AbstractHandler

Base class for all RPC handlers. Must define `__getitem__(self, key)` which returns either a subhandler (another `AbstractHandler`) or a terminal function decorated by `@method`.

### AttrHandler

Subclass of `AbstractHandler` that does lookup via `getattr()`. This is the most common handler type.

```python
class ServerHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def remote_func(self, a: int, b: int) -> int:
        return a + b
```

### Nested Namespaces

Subhandlers are discovered through attribute access on the handler:

```python
class Handler(aiozmq.rpc.AttrHandler):
    def __init__(self, ident):
        self.ident = ident
        self.subhandler = SubHandler(self.ident, 'subident')

    @aiozmq.rpc.method
    def a(self):
        return (self.ident, 'a')


class SubHandler(aiozmq.rpc.AttrHandler):
    def __init__(self, ident, subident):
        self.ident = ident
        self.subident = subident

    @aiozmq.rpc.method
    def b(self):
        return (self.ident, self.subident, 'b')
```

Client calls: `client.call.a()` and `client.call.subhandler.b()`.

### Dict as Handler

A plain dict works as an RPC handler since it implements `__getitem__`:

```python
@aiozmq.rpc.method
def a():
    return 'a'

handlers_dict = {
    'a': a,
    'subnamespace': {'b': b}
}

server = yield from rpc.serve_rpc(handlers_dict, bind='tcp://*:*')
```

### Dynamic Handler

Custom `__getitem__` for dynamic routing:

```python
class DynamicHandler(aiozmq.rpc.AttrHandler):
    def __init__(self, namespace=()):
        self.namespace = namespace

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            return DynamicHandler(self.namespace + (key,))

    @aiozmq.rpc.method
    def func(self):
        return (self.namespace, 'val')
```

## RPC Exceptions

- `Error` — base class for all aiozmq.rpc exceptions
- `GenericError` — raised when remote exception cannot be translated. Has `exc_type` (string) and `arguments` (tuple) attributes.
- `NotFoundError` — raised when RPC method name not found on server (subclass of both `Error` and `LookupError`)
- `ParameterError` — raised when parameter substitution or signature validation fails (subclass of both `Error` and `ValueError`)
- `ServiceClosedError` — raised when accessing transport on a closed service

## Complete Examples

### RPC with Exception Translation

```python
import asyncio
import aiozmq.rpc


class CustomError(Exception):
    def __init__(self, val):
        self.val = val
        super().__init__(val)


exc_name = CustomError.__module__ + '.' + CustomError.__name__
error_table = {exc_name: CustomError}


class ServerHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def remote(self, val):
        raise CustomError(val)


@asyncio.coroutine
def go():
    server = yield from aiozmq.rpc.serve_rpc(
        ServerHandler(), bind='tcp://*:*'
    )
    server_addr = list(server.transport.bindings())[0]
    client = yield from aiozmq.rpc.connect_rpc(
        connect=server_addr, error_table=error_table
    )

    try:
        yield from client.call.remote('value')
    except CustomError as exc:
        assert exc.val == 'value'

    server.close()
    client.close()
```

### Publish-Subscribe with Exception Logging

```python
import asyncio
import aiozmq.rpc
from itertools import count


class Handler(aiozmq.rpc.AttrHandler):
    def __init__(self):
        self.connected = False

    @aiozmq.rpc.method
    def remote_func(self, step, a: int, b: int):
        self.connected = True
        print("HANDLER", step, a, b)


@asyncio.coroutine
def go():
    handler = Handler()
    subscriber = yield from aiozmq.rpc.serve_pubsub(
        handler, subscribe='topic',
        bind='tcp://127.0.0.1:*',
        log_exceptions=True
    )
    subscriber_addr = list(subscriber.transport.bindings())[0]

    publisher = yield from aiozmq.rpc.connect_pubsub(
        connect=subscriber_addr
    )

    for step in count(0):
        yield from publisher.publish('topic').remote_func(step, 1, 2)
        if handler.connected:
            break
        else:
            yield from asyncio.sleep(0.1)

    subscriber.close()
    yield from subscriber.wait_closed()
    publisher.close()
    yield from publisher.wait_closed()
```

### Pipeline (Notifier)

```python
import asyncio
import aiozmq.rpc
from itertools import count


class Handler(aiozmq.rpc.AttrHandler):
    def __init__(self):
        self.connected = False

    @aiozmq.rpc.method
    def remote_func(self, step, a: int, b: int):
        self.connected = True
        print("HANDLER", step, a, b)


@asyncio.coroutine
def go():
    handler = Handler()
    listener = yield from aiozmq.rpc.serve_pipeline(
        handler, bind='tcp://*:*'
    )
    listener_addr = list(listener.transport.bindings())[0]

    notifier = yield from aiozmq.rpc.connect_pipeline(
        connect=listener_addr
    )

    for step in count(0):
        yield from notifier.notify.remote_func(step, 1, 2)
        if handler.connected:
            break
        else:
            yield from asyncio.sleep(0.01)

    listener.close()
    yield from listener.wait_closed()
    notifier.close()
    yield from notifier.wait_closed()
```
