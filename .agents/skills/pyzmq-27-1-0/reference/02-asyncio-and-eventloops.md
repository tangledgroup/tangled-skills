# AsyncIO and Event Loop Integration

## zmq.asyncio — Native asyncio Support

Added in pyzmq 15.0. The `zmq.asyncio` module provides Context, Socket, and Poller subclasses that return `asyncio.Future` objects from blocking methods, enabling use with `async/await`.

### Basic Usage

```python
import asyncio
import zmq
from zmq.asyncio import Context

ctx = Context.instance()

async def worker():
    sock = ctx.socket(zmq.PULL)
    sock.bind("tcp://*:5557")
    msg = await sock.recv_multipart()
    print(f"Received: {msg}")
    await sock.send_multipart([b"done"])

asyncio.run(worker())
```

### Async Socket Methods

The following methods return awaitables instead of blocking:

- `recv()` / `recv_multipart()` — returns `Awaitable[bytes]` or `Awaitable[list[bytes]]`
- `send()` / `send_multipart()` — returns `Awaitable[MessageTracker | None]`
- `poll()` — returns `Awaitable[int]`

### Async Poller

```python
from zmq.asyncio import Poller

async def poll_multiple():
    poller = Poller()
    poller.register(sock1, zmq.POLLIN)
    poller.register(sock2, zmq.POLLIN)

    events = await poller.poll(timeout=1000)
    for socket, event in events:
        if event & zmq.POLLIN:
            msg = await socket.recv()
```

### Shadowing Sync/Async Contexts and Sockets

Added in pyzmq 25. Create an async copy of a sync context or vice versa:

```python
sync_ctx = zmq.Context()
async_ctx = zmq.asyncio.Context(sync_ctx)  # shadows the same underlying libzmq context

async_sock = async_ctx.socket(zmq.PUSH)
sync_sock = zmq.Socket(async_sock)  # sync view of the same socket
```

Previously required: `zmq.Context.shadow(async_ctx.underlying)`.

## Tornado IOLoop and ZMQStream

PyZMQ adapts Tornado's `IOStream` into `ZMQStream` for callback-based message handling with the Tornado event loop. `zmq.asyncio` sockets work in Tornado applications without special handling.

### Creating a ZMQStream

```python
from zmq.eventloop.zmqstream import ZMQStream

sock = ctx.socket(zmq.REP)
sock.bind("tcp://localhost:12345")
stream = ZMQStream(sock)
```

### on_recv() — Register Receive Callback

The primary method for using ZMQStream. Registers a callback fired with each received multipart message:

```python
def echo(msg):
    stream.send_multipart(msg)

stream.on_recv(echo)
```

The callback always receives multipart messages (list of bytes), even if length is 1. Pass `copy=False` to receive tracked `Frame` objects instead of bytes.

### on_recv_stream() — Callback with Stream Reference

Like `on_recv()` but passes both the stream and message to the callback, enabling a single handler for multiple streams:

```python
def handle(stream, msg):
    stream.send_multipart(msg)

stream1.on_recv_stream(handle)
stream2.on_recv_stream(handle)
```

### on_send() — Register Send Callback

Register a callback called after each send completes:

```python
def on_sent(msg):
    print("Sent:", msg)

stream.on_send(on_sent)
```

### flush() — Pull Pending Events

Pull messages off the event queue to enforce priority ordering:

```python
stream.flush(zmq.POLLIN, limit=10)  # flush up to 10 recv events
```

### Pausing and Resuming Processing

Set the callback to `None` to pause processing:

```python
stream.on_recv(None)   # pause
stream.on_recv(echo)   # resume
```

## zmq.green — gevent Compatibility

PyZMQ ships with a gevent-compatible API as `zmq.green`. Instead of importing `zmq` directly:

```python
import zmq.green as zmq
```

Any calls that would have blocked the current thread now only block the current green thread. This is accomplished by ensuring the non-blocking flag is set before any blocking operation and polling the ØMQ file descriptor internally to trigger needed events.

`Socket.send/recv` and `zmq.Poller` are gevent-aware. In pyzmq ≥ 2.2.0.2, `green.device` and `green.eventloop` are also gevent-friendly.

## zmq.Poller — Edge-Triggered File Descriptor

As of pyzmq 17, integrating with event loops works without pre-configuration using an edge-triggered file descriptor. The `fileno()` method returns a read-only edge-triggered file descriptor for both read and write events:

```python
fd = sock.fileno()
# Important: consume all available events when triggered,
# otherwise the read event will not trigger again
```

## Integrating with Custom Event Loops

For custom event loop integration, register the socket's file descriptor:

```python
poller = zmq.Poller()
poller.register(sock, zmq.POLLIN)
events = poller.poll(timeout=5000)
```

The Poller can also be used to drive the ZAP authenticator when not using `zmq.auth.thread` or `zmq.auth.asyncio`.
