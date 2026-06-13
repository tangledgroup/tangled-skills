# Transport and Protocol API

## ZmqTransport

`ZmqTransport` extends `asyncio.BaseTransport` with ZeroMQ-specific operations. It is obtained via `create_zmq_connection()` or through `ZmqStream.transport`.

### Message Operations

- `write(data)` — Write a multipart message (iterable of bytes). Non-blocking; buffers data for async sending
- `abort()` — Close transport immediately, losing buffered data

### Socket Options

- `getsockopt(option)` — Get ZeroMQ socket option (e.g., `zmq.SUBSCRIBE`, `zmq.TYPE`)
- `setsockopt(option, value)` — Set ZeroMQ socket option

### Flow Control

- `set_write_buffer_limits(high=None, low=None)` — Set high/low watermarks for write flow control
- `get_write_buffer_limits()` — Return current write buffer limits
- `get_write_buffer_size()` — Return current write buffer size
- `pause_reading()` — Pause receiving; no data passed to `msg_received()` until `resume_reading()`
- `resume_reading()` — Resume receiving

### Endpoint Management

- `bind(endpoint)` — Bind transport to endpoint (async). Returns bound endpoint with wildcards resolved
- `unbind(endpoint)` — Unbind from endpoint
- `bindings()` — Return immutable set of bound endpoints
- `connect(endpoint)` — Connect to endpoint (async). For TCP, use IP address not DNS name
- `disconnect(endpoint)` — Disconnect from endpoint
- `connections()` — Return immutable set of connected endpoints

### SUB-Specific Operations

- `subscribe(value)` — Add message filter on SUB transport. Empty `b''` subscribes to all
- `unsubscribe(value)` — Remove one instance of a message filter
- `subscriptions()` — Return immutable set of active subscriptions

### Socket Monitoring

- `enable_monitor(events=None)` — Enable socket event monitoring (coroutine). Requires libzmq >= 4 and pyzmq >= 14.4. Default monitors all events (`zmq.EVENT_ALL`)
- `disable_monitor()` — Stop the socket event monitor

## ZmqProtocol

`ZmqProtocol` extends `asyncio.BaseProtocol` with ZeroMQ-specific callbacks.

### Callbacks

- `msg_received(data)` — Called when a multipart message arrives. `data` is a tuple of bytes with at least one item
- `event_received(event)` — Called when socket monitoring is enabled and an event occurs. `event` is a `SocketEvent` namedtuple with fields: `event` (int), `value` (int), `endpoint` (str)
- `connection_made(transport)` — Called when connection is established
- `connection_lost(exc)` — Called when connection is lost

## create_zmq_connection()

```python
async def create_zmq_connection(
    protocol_factory,
    zmq_type,
    *,
    bind=None,
    connect=None,
    zmq_sock=None,
    loop=None
)
```

Creates a ZeroMQ connection endpoint. Returns `(transport, protocol)` pair.

- `protocol_factory` — Callable returning a `ZmqProtocol` instance
- `zmq_type` — ZeroMQ socket type constant (`zmq.REQ`, `zmq.REP`, `zmq.PUB`, `zmq.SUB`, `zmq.PAIR`, `zmq.DEALER`, `zmq.ROUTER`, `zmq.PULL`, `zmq.PUSH`, etc.)
- `bind` — String or iterable of endpoint strings for accepting connections
- `connect` — String or iterable of endpoint strings for connecting to peers
- `zmq_sock` — Optional pre-existing `zmq.Socket` instance
- `loop` — Optional event loop (defaults to `asyncio.get_event_loop()`)

### Endpoint Formats

- `tcp://address` — Unicast TCP transport
- `inproc://name` — In-process (inter-thread) communication
- `ipc://path` — Local inter-process communication
- `pgm://address`, `epgm://address` — Reliable multicast via PGM

## ZmqEventLoop

For legacy use, aiozmq provides `ZmqEventLoop` which extends `SelectorEventLoop` with a `create_zmq_connection()` method. It manages its own `zmq.Context` and closes all sockets on `close()`.

```python
loop = aiozmq.ZmqEventLoop(zmq_context=my_context)
asyncio.set_event_loop(loop)
transport, protocol = await loop.create_zmq_connection(
    MyProtocol, zmq.DEALER, bind='tcp://127.0.0.1:5555'
)
```

Note: `ZmqEventLoop` is not required for normal usage. `create_zmq_connection()` works with the default event loop via the loopless transport implementation.

## ZmqSelector

Custom selector that integrates ZeroMQ sockets into the standard asyncio selector mechanism, enabling proper epoll integration on Linux.
