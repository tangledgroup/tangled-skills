# RPC Framework

## Overview

The `aiozmq.rpc` submodule provides three RPC patterns built on ZeroMQ:

- **Request-Reply (RPC)** — `serve_rpc()` / `connect_rpc()` using ROUTER/DEALER sockets
- **Pipeline** — `serve_pipeline()` / `connect_pipeline()` using PUSH/PULL sockets (fire-and-forget with async results)
- **Pub-Sub** — `serve_pubsub()` / `connect_pubsub()` using SUB/PUB sockets (topic-based method calls)

All three patterns use msgpack for serialization and support custom value translators.

## Installation

RPC requires msgpack:

```bash
pip install aiozmq[rpc]
```

## Handler Classes

### AttrHandler

Base class for RPC handlers that resolves method names via attribute lookup:

```python
import aiozmq.rpc

class MyHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def add(self, a: int, b: int) -> int:
        return a + b

    @aiozmq.rpc.method
    async def greet(self, name: str) -> str:
        return f"Hello, {name}!"
```

Methods must be decorated with `@aiozmq.rpc.method` to expose them as RPC endpoints. Both sync and async methods are supported.

### AbstractHandler

For custom dispatch logic, implement `AbstractHandler` by providing `__getitem__(key)`. This allows dict-based or other lookup strategies:

```python
class DictHandler(aiozmq.rpc.AbstractHandler):
    def __init__(self):
        self._methods = {}

    def register(self, name, func):
        self._methods[name] = func

    def __getitem__(self, key):
        return self._methods[key]
```

### Nested Handlers (Subhandlers)

Handlers can be nested via attribute access. The RPC dispatcher traverses dot-separated names:

```python
class SubHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def sub_method(self, x):
        return x * 2

class MainHandler(aiozmq.rpc.AttrHandler):
    math = SubHandler()

    @aiozmq.rpc.method
    def main_method(self, y):
        return y + 1
```

Client calls: `await client.call.math.sub_method(5)` and `await client.call.main_method(3)`.

## Request-Reply (RPC)

### Server

```python
async def serve_rpc(
    handler,
    *,
    connect=None,
    bind=None,
    loop=None,
    translation_table=None,
    log_exceptions=False,
    exclude_log_exceptions=(),
    timeout=None
)
```

Returns a `Service` instance. Uses `zmq.ROUTER` socket on the server side.

- `handler` — Instance implementing `AbstractHandler` (usually `AttrHandler`)
- `bind` / `connect` — Endpoint(s)
- `log_exceptions` — Log exceptions from remote calls
- `exclude_log_exceptions` — Exception classes to skip in logging
- `timeout` — Timeout for server-side async method execution

### Client

```python
async def connect_rpc(
    *,
    connect=None,
    bind=None,
    loop=None,
    error_table=None,
    translation_table=None,
    timeout=None
)
```

Returns an `RPCClient` instance. Uses `zmq.DEALER` socket.

- `timeout` — Timeout for individual RPC calls. Raises `asyncio.TimeoutError` if exceeded
- `error_table` — Custom exception translator table

### Client Usage

```python
client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5555')
result = await client.call.add(1, 2)
result = await client.call.math.sub_method(5)
client.close()
```

The `call` property provides dynamic attribute access for method invocation.

### Context Manager

`RPCClient` supports the context manager protocol:

```python
async with await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5555') as client:
    result = await client.call.add(1, 2)
```

### Timeout Override

```python
client_with_timeout = client.with_timeout(5.0)  # 5 second timeout
```

## Pipeline Pattern

Pipeline uses PUSH/PULL sockets for fire-and-forget style calls where the server processes requests asynchronously.

```python
# Server
server = await aiozmq.rpc.serve_pipeline(
    MyHandler(), bind='tcp://127.0.0.1:5556'
)

# Client
client = await aiozmq.rpc.connect_pipeline(connect='tcp://127.0.0.1:5556')
await client.call.process_task(task_data)
client.close()
```

## Pub-Sub Pattern

Pub-Sub uses PUB/SUB sockets for topic-based method dispatch.

```python
# Server (subscriber)
server = await aiozmq.rpc.serve_pubsub(
    MyHandler(),
    subscribe='topic1',
    bind='tcp://127.0.0.1:5557'
)

# Client (publisher)
client = await aiozmq.rpc.connect_pubsub(connect='tcp://127.0.0.1:5557')
await client.call('topic1', 'method_name', args, kwargs)
client.close()
```

## Error Handling

### Server-Side Errors

When a server method raises an exception, it is serialized and sent to the client. The client receives:

- `NotFoundError` — Method not found in handler namespace
- `ParametersError` — Arguments don't match method signature
- `GenericError` — All other unhandled exceptions (preserves type, args, repr)

### Custom Error Translation

Register custom error translators on the client:

```python
error_table = {
    'myapp.errors.ValidationError': MyValidationError,
}

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    error_table=error_table
)
```

## Custom Value Translators

Translation tables allow custom serialization for specific types:

```python
translation_table = {
    datetime: lambda dt: dt.isoformat(),
    'datetime': lambda s: datetime.fromisoformat(s),
}

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    translation_table=translation_table
)
```

## Service Interface

All server and client instances implement `asyncio.AbstractServer`:

- `transport` — Property returning the underlying `ZmqTransport`
- `close()` — Close the service
- `wait_closed()` — Coroutine that completes when the service is fully closed

## RPC Protocol Wire Format

The RPC protocol uses msgpack for serialization with a binary header containing:

- Process ID and random prefix (for routing)
- Request ID (32-bit counter)
- Timestamp
- Error flag

Messages are sent as multipart ZMQ frames: `[header, method_name, args, kwargs]` for requests and `[header, result_or_error]` for responses.

## Breaking Changes in 1.0.0

- **Removed annotation-based conversion functions** — Python type annotations on RPC methods are used only for signature validation, not as automatic type converters
- **Dropped Python 3.5** — Minimum supported version is Python 3.6
