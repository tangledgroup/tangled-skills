---
name: pyzmq-27-1-0
description: Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await integration, security mechanisms, and distributed computing architectures. Use when building Python applications requiring high-performance messaging, pub/sub systems, request-reply patterns, load balancing, or inter-process communication with ZeroMQ's decentralized architecture.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - zeromq
  - zmq
  - messaging
  - networking
  - sockets
  - pubsub
  - rpc
  - asyncio
  - distributed-systems
  - python
category: networking
external_references:
  - https://pyzmq.readthedocs.io/
  - https://github.com/zeromq/pyzmq
---

# PyZMQ 27.1.0

## Overview

PyZMQ is the Python bindings for ØMQ (ZeroMQ), a lightweight and fast messaging library. It provides both low-level Cython/CFFI bindings to libzmq and higher-level "batteries included" extensions including asyncio support, ZAP authentication, device proxies, SSH tunneling, logging handlers, and serialization helpers.

PyZMQ 27.x supports Python ≥ 3.9 (including PyPy via CFFI) and libzmq ≥ 3.2.2 (including 4.x). Binary wheels ship with libzmq 4.3.5 bundled with CURVE support via libsodium. Version 27.1.0 restored the prior behavior of `zmq.DRAFT_API` to reflect actual draft API availability requiring both libzmq and pyzmq built with drafts enabled.

Key features:
- Full libzmq 3.x/4.x API coverage with no code changes across versions
- Native asyncio support via `zmq.asyncio` (Futures/Awaitables)
- Tornado IOLoop integration via `zmq.eventloop.zmqstream.ZMQStream`
- gevent compatibility via `zmq.green`
- ZAP authentication with NULL, PLAIN, CURVE, and GSSAPI security levels
- Built-in JSON/pickle serialization helpers (`send_json`, `recv_json`, etc.)
- Context manager support for `Context`, `Socket`, `bind()`, and `connect()`
- Socket options as Python attributes (e.g., `sock.hwm = 10`)
- Decorator syntax for context/socket lifecycle via `zmq.decorators`
- SSH tunneling via `zmq.ssh.tunnel`
- Background device/proxy threads via `zmq.devices`
- Logging handlers via `zmq.log.handlers`

## When to Use

- Building Python applications with ZeroMQ messaging patterns (REQ/REP, PUB/SUB, PUSH/PULL, DEALER/ROUTER)
- Integrating ZeroMQ sockets with asyncio coroutines
- Implementing distributed systems with message-based communication
- Setting up ZAP authentication for secure ZeroMQ connections
- Running background proxy devices in threads or processes
- Tunneling ZeroMQ connections over SSH
- Publishing Python logging output over ZeroMQ PUB sockets
- Sending NumPy arrays or other buffer-interface objects with zero-copy

## Core Concepts

### Context and Socket Model

Every ZeroMQ application starts with a `Context`, which manages resources and creates `Socket` instances:

```python
import zmq

ctx = zmq.Context()          # create a context
sock = ctx.socket(zmq.PUSH)  # create a socket of a given type
```

For most single-process applications, use the global singleton:

```python
ctx = zmq.Context.instance()
```

### Thread Safety

`Context` objects are thread-safe and can be shared across threads. `Socket` objects are NOT thread-safe — create sockets per-thread. Sharing sockets across threads without locks risks uncatchable C-level crashes.

### Socket Options as Attributes

Socket options can be set and read as Python attributes (case-insensitive):

```python
sock = ctx.socket(zmq.DEALER)
sock.identity = b"dealer"
sock.hwm = 10
print(sock.events)  # current events
print(sock.fd)      # file descriptor
```

Default options can also be set on the Context, affecting all subsequently created sockets:

```python
ctx.linger = 0
rep = ctx.socket(zmq.REP)  # inherits linger=0
```

### Addressing

ZeroMQ uses URI-style addresses: `protocol://interface:port`. Supported protocols include `tcp`, `udp`, `pgm`, `epgm`, `inproc`, and `ipc`.

```python
sock.bind("tcp://127.0.0.1:5555")
sock.connect("tcp://remote-host:5555")
```

Binding to port 0 binds to a random available port. The actual URL is available via `socket.last_endpoint`.

## Usage Examples

### Basic Request-Reply Pattern

```python
import zmq

# Server (REP)
ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5555")
while True:
    msg = rep.recv()
    print(f"Received: {msg}")
    rep.send(b"World")

# Client (REQ)
ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect("tcp://localhost:5555")
req.send(b"Hello")
reply = req.recv()
print(f"Reply: {reply}")
```

### Basic Pub-Sub Pattern

```python
import zmq

# Publisher
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")
for i in range(10):
    pub.send_string(f"event {i}")

# Subscriber
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.subscribe(b"")  # subscribe to all
for _ in range(10):
    msg = sub.recv_string()
    print(f"Got: {msg}")
```

### Asyncio Example

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

## Advanced Topics

**Socket Types and Messaging Patterns**: Complete reference of all ZeroMQ socket types (REQ, REP, PUB, SUB, PUSH, PULL, DEALER, ROUTER, PAIR, STREAM, XPUB, XSUB, SURVEYOR, RESPONDENT) with pairing rules and flow semantics → [Socket Types and Messaging Patterns](reference/01-socket-types.md)

**AsyncIO and Event Loop Integration**: Native asyncio support via `zmq.asyncio`, Tornado ZMQStream callbacks, gevent compatibility via `zmq.green`, and Poller usage → [AsyncIO and Event Loop Integration](reference/02-asyncio-and-eventloops.md)

**Security and Authentication**: ZAP authenticator with NULL, PLAIN, CURVE, and GSSAPI security levels; certificate management; allow/deny policies; `zmq.auth.thread` and `zmq.auth.asyncio` → [Security and Authentication](reference/03-security-and-auth.md)

**Serialization and Message Handling**: Built-in JSON/pickle helpers, multipart messages, custom serialization with `send_serialized`/`recv_serialized`, zero-copy NumPy array transfer, MessageTracker for non-copying sends → [Serialization and Message Handling](reference/04-serialization.md)

**Devices, Proxies, and Extensions**: Background devices (`ThreadDevice`, `ProcessDevice`), proxy functions (`zmq.proxy`, `zmq.proxy_steerable`), steerable proxies with PAUSE/RESUME/TERMINATE control, logging handlers, SSH tunneling, decorators → [Devices, Proxies, and Extensions](reference/05-devices-and-extensions.md)

**Draft APIs and Advanced Configuration**: DRAFT socket types (CLIENT/SERVER, RADIO/DISH), building with draft support, context shadowing, `bind_to_random_port`, socket monitoring → [Draft APIs and Advanced Configuration](reference/06-draft-and-advanced.md)
