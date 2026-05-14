# Streams API

The Streams API (new in version 0.6) provides a high-level, convenient interface on top of the core `ZmqTransport`/`ZmqProtocol`. Instead of writing custom protocol classes, you get a `ZmqStream` with simple `read()` and `write()` methods.

## create_zmq_stream

`aiozmq.create_zmq_stream()` is a coroutine wrapper around `create_zmq_connection()` that returns a `ZmqStream` instance.

```python
import asyncio
import aiozmq
import zmq

@asyncio.coroutine
def go():
    router = yield from aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:*'
    )

    addr = list(router.transport.bindings())[0]
    dealer = yield from aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect=addr
    )

    for i in range(10):
        msg = (b'data', b'ask', str(i).encode('utf-8'))
        dealer.write(msg)
        data = yield from router.read()
        router.write(data)
        answer = yield from dealer.read()
        print(answer)

    dealer.close()
    router.close()
```

Parameters:

- `zmq_type` (int) — ZeroMQ socket type (`zmq.REQ`, `zmq.REP`, `zmq.PUB`, `zmq.SUB`, `zmq.DEALER`, `zmq.ROUTER`, `zmq.PULL`, `zmq.PUSH`, etc.)
- `bind` (str or iterable of strings) — endpoints for accepting connections
- `connect` (str or iterable of strings) — endpoints for initiating connections
- `zmq_sock` (zmq.Socket) — pre-existing zmq socket
- `loop` (asyncio.AbstractEventLoop) — optional event loop
- `high_read` (int) — high-watermark for reading, `None` for no limit
- `low_read` (int) — low-watermark for reading, `None` for no limit
- `high_write` (int) — high-watermark for writing, `None` for no limit
- `low_write` (int) — low-watermark for writing, `None` for no limit
- `events_backlog` (int) — backlog size for monitoring events, 100 by default. `None` for unlimited. Oldest events are discarded when backlog is exceeded. (new in 0.7)

Returns: `ZmqStream` instance.

## ZmqStream

The `ZmqStream` class provides a stream-oriented interface for sending and receiving ZeroMQ messages.

### Methods

- `write(msg)` — write multipart message into the socket. `msg` is a sequence (tuple or list) of byte frames.
- `read()` — coroutine, read one multipart message from the wire. Returns tuple of bytes. Raises `ZmqStreamClosed` if stream was closed.
- `drain()` — coroutine, wait until write buffer is flushed. Use pattern: `stream.write(data); yield from stream.drain()`. Blocks when transport buffer is full (protocol paused), continues immediately when nothing to wait for.
- `close()` — close the stream and underlying ZeroMQ socket.
- `at_closing()` — return `True` if buffer is empty and `feed_closing()` was called.
- `exception()` — get any stream exception.
- `get_extra_info(name, default=None)` — return optional transport info (same as `asyncio.BaseTransport.get_extra_info()`).

### Socket Event Monitoring (new in 0.7)

- `read_event()` — coroutine, read one ZeroMQ monitoring event. Raises `ZmqStreamClosed` if stream was closed. Monitoring must be enabled first via `stream.transport.enable_monitor()`.

```python
@asyncio.coroutine
def monitor_stream(stream):
    try:
        while True:
            event = yield from stream.read_event()
            print(event)
    except aiozmq.ZmqStreamClosed:
        pass
```

### Internal Methods (not for direct use)

- `set_exception(exc)` — set the stream exception.
- `set_transport(transport)` — set the transport.
- `set_read_buffer_limits(high=None, low=None)` — set read buffer limits.
- `feed_closing()` — feed socket closing signal.
- `feed_msg(msg)` — feed message to stream's internal buffer, resuming waiting operations.
- `feed_event(event)` — feed socket event to stream's internal buffer.

### Transport Property

- `stream.transport` — the underlying `ZmqTransport` instance, accessible for low-level operations like `enable_monitor()`, `bind()`, `connect()`, etc.

## ZmqStreamClosed Exception

Raised by `read()` and `read_event()` when called on a closed stream.

```python
try:
    msg = yield from stream.read()
except aiozmq.ZmqStreamClosed:
    print("Stream was closed")
```

## Stream-Level Socket Event Monitor Example

```python
import asyncio
import aiozmq
import zmq


@asyncio.coroutine
def monitor_stream(stream):
    try:
        while True:
            event = yield from stream.read_event()
            print(event)
    except aiozmq.ZmqStreamClosed:
        pass


@asyncio.coroutine
def go():
    router = yield from aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:*'
    )
    addr = list(router.transport.bindings())[0]

    dealer = yield from aiozmq.create_zmq_stream(zmq.DEALER)

    # Enable monitoring before connecting
    yield from dealer.transport.enable_monitor()

    # Start monitoring task
    asyncio.Task(monitor_stream(dealer))

    yield from dealer.transport.connect(addr)

    for i in range(10):
        msg = (b'data', b'ask', str(i).encode('utf-8'))
        dealer.write(msg)
        data = yield from router.read()
        router.write(data)
        answer = yield from dealer.read()
        print(answer)

    router.close()
    dealer.close()


def main():
    asyncio.get_event_loop().run_until_complete(go())
    print("DONE")


if __name__ == '__main__':
    main()
```

## When to Use Streams vs Core API

Use **Streams API** when:
- You want simple `read()`/`write()` message passing
- You need quick request-reply or echo patterns
- You want socket event monitoring with minimal boilerplate
- Your use case fits the stream abstraction

Use **Core API** when:
- You need fine-grained control over protocol callbacks
- You need custom connection lifecycle handling
- You require non-standard message processing logic
- You are building a higher-level framework on top of aiozmq
