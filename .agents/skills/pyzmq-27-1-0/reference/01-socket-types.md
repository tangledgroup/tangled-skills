# Socket Types and Messaging Patterns

## Overview

ZeroMQ defines multiple socket types that implement specific messaging patterns. Each type has defined behavior for sending and receiving messages. Sockets are created from a Context:

```python
sock = ctx.socket(zmq.PUSH)
```

In pyzmq 26+, `zmq.Context` and `zmq.Socket` are Generics for typing purposes. Use resolved types to exclude async subclasses:

```python
ctx: zmq.Context[zmq.Socket[bytes]] = zmq.Context()
sock: zmq.Socket[bytes] = ctx.socket(zmq.PUSH)
```

## Socket Types

### REQ — Request

Sends requests and receives replies in strict alternating order. Blocks on `send` if no reply was received, blocks on `recv` if no request was sent. Pairs with REP or ROUTER.

```python
req = ctx.socket(zmq.REQ)
req.connect("tcp://server:5555")
req.send(b"request")
reply = req.recv()
```

### REP — Reply

Receives requests and sends replies in strict alternating order. Blocks on `recv` if no request was received, blocks on `send` if no reply was pending. Pairs with REQ or DEALER.

```python
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5555")
msg = rep.recv()
rep.send(b"reply")
```

### DEALER — Asymmetric Request

Improved version of REQ. Sends and receives messages without strict ordering. Automatically prepends and strips identity frames. Pairs with ROUTER or REP.

```python
dealer = ctx.socket(zmq.DEALER)
dealer.identity = b"worker-1"
dealer.connect("tcp://broker:5555")
```

### ROUTER — Asymmetric Reply

Improved version of REP. Routes messages to specific peers using identity frames. The first frame of a received message is the identity of the sender. When sending, the first frame specifies the destination peer's identity.

```python
router = ctx.socket(zmq.ROUTER)
router.bind("tcp://*:5556")
frames = router.recv_multipart()  # [identity, empty, msg]
router.send_multipart([frames[0], b"reply"])
```

### PUB — Publisher

Sends messages to all connected subscribers. Messages are dropped if no subscribers are connected. Zero-copy send is supported.

```python
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5557")
pub.send_string("event data")
```

### SUB — Subscriber

Receives messages from a publisher, filtered by subscription topics. By default receives nothing — must call `subscribe()` first.

```python
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5557")
sub.subscribe(b"news.")   # prefix match
# or
sub.setsockopt(zmq.SUBSCRIBE, b"")  # receive all
msg = sub.recv_string()
```

- `subscribe(topic)` — start receiving messages starting with topic
- `unsubscribe(topic)` — stop receiving messages starting with topic

### PUSH — Pipeline Output

Sends messages in round-robin fashion to connected PULL sockets.

```python
push = ctx.socket(zmq.PUSH)
push.bind("tcp://*:5558")
push.send_multipart([b"task", b"data"])
```

### PULL — Pipeline Input

Receives messages in round-robin fashion from connected PUSH sockets.

```python
pull = ctx.socket(zmq.PULL)
pull.connect("tcp://localhost:5558")
msg = pull.recv()
```

### PAIR — Private One-to-One

Simple point-to-point communication between exactly two endpoints. No routing or load-balancing logic. Messages sent to a PAIR socket go directly to the connected peer.

```python
a = ctx.socket(zmq.PAIR)
a.bind("inproc://channel")
b = ctx.socket(zmq.PAIR)
b.connect("inproc://channel")
a.send(b"hello")
print(b.recv())
```

### STREAM — Bi-directional

Designed for protocol development. Sends and receives messages with peer addresses. The first frame of a received message is the peer's address. Use `send_multicast` to send to all connected peers.

### XPUB — Extended Publisher

Extended PUB that notifies on subscribe/unsubscribe events. First byte of notification indicates subscribe (0x01) or unsubscribe (0x00), followed by the topic.

```python
xpub = ctx.socket(zmq.XPUB)
xpub.bind("tcp://*:5559")
# enable immediate subscriber notifications
xpub.setsockopt(zmq.XPUB_VERBOSE, 1)
```

### XSUB — Extended Subscriber

Extended SUB that sends subscribe/unsubscribe messages to XPUB.

### SURVEYOR — Survey Initiator

Sends survey questions and collects replies within a configurable deadline (`zmq.SNDTIMEO`). Pairs with RESPONDENT.

### RESPONDENT — Survey Responder

Receives survey questions and sends replies. Pairs with SURVEYOR.

## Send/Receive Methods

### Single Frame

```python
sock.send(data, flags=0, copy=True, track=False)
data = sock.recv(flags=0, copy=True, track=False)
```

### Multipart Messages

ZeroMQ messages consist of one or more frames. Use `send_multipart`/`recv_multipart` for multi-frame messages:

```python
sock.send_multipart([b"header", b"body"])
frames = sock.recv_multipart()  # [b"header", b"body"]
```

### Flags

- `zmq.NOBLOCK` — non-blocking operation, raises `zmq.Again` if not ready
- `zmq.DONTWAIT` — alias for NOBLOCK
- `zmq.SNDMORE` — more frames follow (for manual multipart)

### Copy and Track

- `copy=True` (default) — data is copied into ZeroMQ's internal buffer
- `copy=False` — zero-copy send using Python buffer interface
- `track=True` — return a `MessageTracker` to know when ZeroMQ is done with the buffer

```python
tracker = sock.send(large_buffer, copy=False, track=True)
tracker.wait()  # block until ZeroMQ has sent the data
# now safe to modify large_buffer
```

## Context Managers

### Context and Socket as Context Managers

```python
with zmq.Context() as ctx:
    with ctx.socket(zmq.PUSH) as sock:
        sock.connect(url)
        sock.send_multipart([b"message"])
    # socket closed on exit
# context terminated on exit
```

When a Context is used as a context manager or deleted without explicit `term()`, it calls `destroy()` which closes all remaining sockets. This prevents hangs from `term()` when sockets are left open.

### Bind/Connect as Context Managers

Added in pyzmq 20:

```python
with sock.connect(url):
    sock.send_multipart([b"message"])
# socket.disconnect(url) called on exit
```

Binding to port 0 as a context manager (pyzmq 26+):

```python
with sock.bind("tcp://127.0.0.1:0"):
    actual_url = sock.last_endpoint  # e.g. "tcp://127.0.0.1:45678"
```

## Socket Options

Common socket options (set as attributes or via `setsockopt`):

- `hwm` — High Water Mark, max messages queued
- `linger` — Timeout for pending messages on close (0 = drop, -1 = forever)
- `identity` — Binary identity of the socket
- `sndbuf`/`rcvbuf` — OS send/receive buffer sizes
- `sndtimeo`/`rcvtimeo` — Send/receive timeouts in milliseconds (0 = non-blocking, -1 = infinite)
- `affinity` — I/O thread affinity bitmask
- `rate` — Maximum send rate for multicast transports
- `recover` — Recovery interval for multicast

```python
sock.hwm = 1000
sock.linger = 0
sock.rcvtimeo = 5000  # 5 second timeout
```

## Polling

The `zmq.Poller` monitors multiple sockets for events:

```python
poller = zmq.Poller()
poller.register(sock1, zmq.POLLIN)
poller.register(sock2, zmq.POLLOUT)

# returns list of (socket, event) tuples
events = dict(poller.poll(timeout=1000))  # timeout in ms
if sock1 in events:
    msg = sock1.recv()
```

Poll events: `zmq.POLLIN` (readable), `zmq.POLLOUT` (writable), `zmq.POLLERR` (error).

## Copy Threshold

Added in pyzmq 17. The `copy_threshold` controls the size below which messages are always copied:

```python
sock.copy_threshold = 65536  # default: 64KB
# or globally:
zmq.COPY_THRESHOLD = 32768
```

Zero-copy has nontrivial overhead for small messages. The default of 64KB balances performance for typical message sizes.
