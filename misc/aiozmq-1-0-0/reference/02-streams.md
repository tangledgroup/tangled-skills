# Streams API

## Overview

The streams API provides a high-level `read()`/`write()` abstraction over ZeroMQ sockets, similar to `asyncio.open_connection()`. It wraps `ZmqTransport` in a `ZmqStream` object with flow control and buffering.

## create_zmq_stream()

```python
async def create_zmq_stream(
    zmq_type,
    *,
    bind=None,
    connect=None,
    loop=None,
    zmq_sock=None,
    high_read=None,
    low_read=None,
    high_write=None,
    low_write=None,
    events_backlog=100
)
```

Returns a `ZmqStream` instance.

- `zmq_type` — ZeroMQ socket type constant
- `bind` / `connect` — Endpoint strings (same as `create_zmq_connection`)
- `high_read` / `low_read` — High/low watermarks for the read buffer
- `high_write` / `low_write` — High/low watermarks for write flow control
- `events_backlog` — Maximum queued monitoring events (default 100). Oldest events are discarded when exceeded

## ZmqStream

### Methods

- `write(msg)` — Write a multipart message (iterable of bytes)
- `close()` — Close the stream and underlying transport
- `drain()` — Coroutine. Flush the write buffer. Use after `write()` when flow control matters
- `transport` — Property returning the underlying `ZmqTransport`
- `get_extra_info(name, default=None)` — Delegate to transport's `get_extra_info()`
- `exception()` — Return any exception from the stream

### Reading Messages

```python
async def handler(stream):
    while True:
        msg = await stream.read()  # returns tuple of bytes (multipart)
        # process msg...
        stream.write(msg)          # echo back
        await stream.drain()
```

`read()` is an async method that returns the next multipart message as a tuple of bytes.

### Flow Control

When the write buffer exceeds `high_write`, `pause_writing()` is called on the protocol. Use `await stream.drain()` to wait until the buffer drops below `low_write`:

```python
stream.write(large_message)
await stream.drain()  # waits if buffer is full
```

### Buffer Limits

Set read buffer limits via constructor parameters:

```python
stream = await aiozmq.create_zmq_stream(
    zmq.DEALER,
    bind='tcp://127.0.0.1:5555',
    high_read=100,    # pause reading at 100 messages
    low_read=10,      # resume reading at 10 messages
    high_write=65536, # pause writing at 64KB
    low_write=16384,  # resume writing at 16KB
)
```

## ZmqStreamProtocol

Internal helper class that adapts between `ZmqProtocol` and `ZmqStream`. Normally you don't need to use this directly — `create_zmq_stream()` creates it automatically.

## ZmqStreamClosed

Exception raised when operations are attempted on a closed stream.

## Example: Dealer-Router Pattern

```python
import asyncio
import aiozmq
import zmq

async def go():
    router = await aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:*'
    )
    addr = list(router.transport.bindings())[0]

    dealer = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect=addr
    )

    for i in range(10):
        msg = (b'data', b'ask', str(i).encode('utf-8'))
        dealer.write(msg)
        data = await router.read()
        router.write(data)
        answer = await dealer.read()
        print(answer)

    dealer.close()
    router.close()

asyncio.run(go())
```

## Monitoring Events With Streams

When `enable_monitor()` is called on the transport, monitoring events are queued and can be read via the stream's event queue. Events are `SocketEvent` namedtuples with `event`, `value`, and `endpoint` fields. The `events_backlog` parameter controls the maximum number of queued events.
