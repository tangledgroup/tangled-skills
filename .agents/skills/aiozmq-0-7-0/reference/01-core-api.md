# Core API

The core API provides `create_zmq_connection()`, `ZmqTransport`, and `ZmqProtocol` — the lowest-level aiozmq primitives for building custom ZeroMQ integrations.

## create_zmq_connection

`aiozmq.create_zmq_connection()` is a coroutine that creates a ZeroMQ connection, returning a `(transport, protocol)` pair.

```python
import asyncio
import aiozmq
import zmq

@asyncio.coroutine
def go():
    transport, protocol = yield from aiozmq.create_zmq_connection(
        lambda: MyProtocol(),
        zmq.ROUTER,
        bind='tcp://127.0.0.1:*'
    )
```

Parameters:

- `protocol_factory` (callable) — a factory that instantiates a `ZmqProtocol` object
- `zmq_type` (int) — socket type (`zmq.REQ`, `zmq.REP`, `zmq.PUB`, `zmq.SUB`, `zmq.DEALER`, `zmq.ROUTER`, `zmq.PULL`, `zmq.PUSH`, etc.)
- `bind` (str or iterable of strings) — endpoints for accepting connections
- `connect` (str or iterable of strings) — endpoints for initiating connections
- `zmq_sock` (zmq.Socket) — a pre-existing zmq socket to wrap
- `loop` (asyncio.AbstractEventLoop) — optional event loop, `None` for default

You can defer bind/connect by calling `transport.bind()` and `transport.connect()` later.

## ZmqTransport

`ZmqTransport` implements `asyncio.BaseTransport`. You never create it directly — you receive it from `create_zmq_connection()`.

### Connection Management

- `bind(endpoint)` — coroutine, bind transport to endpoint. Returns bound endpoint string (resolves wildcards).
- `unbind(endpoint)` — coroutine, unbind from endpoint.
- `bindings()` — return immutable set of currently bound endpoints.
- `connect(endpoint)` — coroutine, connect to endpoint. For TCP, use IP addresses not DNS names. Use `loop.getaddrinfo(host, port)` for DNS resolution.
- `disconnect(endpoint)` — coroutine, disconnect from endpoint.
- `connections()` — return immutable set of currently connected endpoints.

### Data Operations

- `write(data)` — write multipart message (iterable of bytes). Non-blocking, buffers data.
- `close()` — close transport, flushes buffer asynchronously.
- `abort()` — close immediately, buffered data is lost.
- `pause_reading()` / `resume_reading()` — control incoming data flow.

### Write Buffer Control

- `get_write_buffer_limits()` — return `(low, high)` watermarks.
- `set_write_buffer_limits(high=None, low=None)` — set write buffer limits controlling `pause_writing()`/`resume_writing()`.
- `get_write_buffer_size()` — current write buffer size.

### Socket Options

- `getsockopt(option)` — get ZeroMQ socket option (e.g., `zmq.TYPE`, `zmq.SUBSCRIBE`).
- `setsockopt(option, value)` — set ZeroMQ socket option.

### SUB Transport Methods

- `subscribe(value)` — add message filter on SUB transport. Empty bytes (`b''`) subscribes to all messages. aiozmq deduplicates subscriptions automatically (unlike raw ZeroMQ).
- `unsubscribe(value)` — remove one instance of a message filter.
- `subscriptions()` — return immutable set of active subscriptions.

### Socket Event Monitoring (new in 0.7)

- `enable_monitor(events=None)` — coroutine, enable socket event monitoring. Events are passed to protocol's `event_received()` method. Requires libzmq >= 4 and pyzmq >= 14.4. If no events specified, monitors all (`zmq.EVENT_ALL`).
- `disable_monitor()` — coroutine, stop the socket event monitor.

### Extra Info

- `get_extra_info(key, default=None)` — supports key `"zmq_socket"` to get the underlying `zmq.Socket` instance.

## ZmqProtocol

`ZmqProtocol` derives from `asyncio.BaseProtocol`. Subclass it to handle messages and connection lifecycle.

```python
class MyProtocol(aiozmq.ZmqProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def msg_received(self, msg):
        # msg is a tuple of bytes frames
        print("Received:", msg)

    def connection_lost(self, exc):
        print("Connection lost:", exc)

    def event_received(self, event):
        # Socket monitoring event (namedtuple: event, value, endpoint)
        print("Socket event:", event.event, event.value, event.endpoint)
```

Methods to implement:

- `connection_made(transport)` — called when connection is established.
- `msg_received(msg)` — called for each incoming multipart message. `msg` is a tuple of bytes with at least one item.
- `connection_lost(exc)` — called when connection is lost or closed. `exc` is `None` if cleanly closed.
- `pause_writing()` — called when write buffer exceeds high-water mark.
- `resume_writing()` — called when write buffer drops below low-water mark.
- `event_received(event)` — called when socket monitoring event occurs (new in 0.7). Event is a namedtuple with fields: `event` (int code), `value` (int value), `endpoint` (str endpoint).

## Exception Policy

All `zmq.ZMQError` exceptions are translated to `OSError` (or descendants) following PEP 3151. The `errno` and `strerror` are borrowed from the underlying `ZMQError`. `InterruptedError` (EINTR) is handled internally and never raised publicly.

```python
# Internal translation pattern
try:
    return self._zmq_sock.getsockopt(option)
except zmq.ZMQError as exc:
    raise OSError(exc.errno, exc.strerror)
```

## Version Info

- `aiozmq.version` — text version string.
- `aiozmq.version_info` — namedtuple `(major, minor, micro, releaselevel, serial)` for programmatic comparison.

## Deprecated: ZmqEventLoop and ZmqEventLoopPolicy

Since version 0.5, aiozmq works with any standard asyncio event loop. The dedicated `ZmqEventLoop` and `ZmqEventLoopPolicy` are deprecated but still available for backward compatibility.

```python
# Deprecated approach (still works)
import asyncio
import aiozmq

asyncio.set_event_loop_policy(aiozmq.ZmqEventLoopPolicy())
loop = asyncio.get_event_loop()
```

`ZmqEventLoop` accepts an optional `zmq_context` parameter to use a specific ZeroMQ context instead of the global `zmq.Context.instance()`.

## Complete Core-Level Example

DEALER-ROUTER pair implemented at core level:

```python
import asyncio
import aiozmq
import zmq


class ZmqDealerProtocol(aiozmq.ZmqProtocol):
    transport = None

    def __init__(self, queue, on_close):
        self.queue = queue
        self.on_close = on_close

    def connection_made(self, transport):
        self.transport = transport

    def msg_received(self, msg):
        self.queue.put_nowait(msg)

    def connection_lost(self, exc):
        self.on_close.set_result(exc)


class ZmqRouterProtocol(aiozmq.ZmqProtocol):
    transport = None

    def __init__(self, on_close):
        self.on_close = on_close

    def connection_made(self, transport):
        self.transport = transport

    def msg_received(self, msg):
        self.transport.write(msg)

    def connection_lost(self, exc):
        self.on_close.set_result(exc)


@asyncio.coroutine
def go():
    router_closed = asyncio.Future()
    dealer_closed = asyncio.Future()

    router, _ = yield from aiozmq.create_zmq_connection(
        lambda: ZmqRouterProtocol(router_closed),
        zmq.ROUTER,
        bind='tcp://127.0.0.1:*'
    )
    addr = list(router.bindings())[0]

    queue = asyncio.Queue()
    dealer, _ = yield from aiozmq.create_zmq_connection(
        lambda: ZmqDealerProtocol(queue, dealer_closed),
        zmq.DEALER,
        connect=addr
    )

    for i in range(10):
        msg = (b'data', b'ask', str(i).encode('utf-8'))
        dealer.write(msg)
        answer = yield from queue.get()
        print(answer)

    dealer.close()
    yield from dealer_closed
    router.close()
    yield from router_closed


def main():
    asyncio.get_event_loop().run_until_complete(go())
    print("DONE")


if __name__ == '__main__':
    main()
```
