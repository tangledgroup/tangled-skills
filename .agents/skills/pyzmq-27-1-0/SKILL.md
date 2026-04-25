---
name: pyzmq-27-1-0
description: Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await integration, security mechanisms, and distributed computing architectures. Use when building Python applications requiring high-performance messaging, pub/sub systems, request-reply patterns, load balancing, or inter-process communication with ZeroMQ's decentralized architecture.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
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
required_environment_variables: []

external_references:
  - https://pyzmq.readthedocs.io/
  - https://github.com/zeromq/pyzmq
---
## Overview
Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await integration, security mechanisms, and distributed computing architectures. Use when building Python applications requiring high-performance messaging, pub/sub systems, request-reply patterns, load balancing, or inter-process communication with ZeroMQ's decentralized architecture.

Complete toolkit for using pyzmq (Python bindings for ZeroMQ/ØMQ) version 27.x, providing type-safe access to ZeroMQ's high-performance messaging library with support for all socket types, security mechanisms, asyncio integration, and advanced patterns for distributed computing.

PyZMQ works with Python 3.9+ and PyPy via CFFI. Binary distributions (wheels on PyPI) ship with libzmq 4.3.5 built with default configuration and CURVE support provided by libsodium.

## When to Use
- Building high-performance message-passing systems in Python
- Implementing pub/sub, request-reply, or pipeline patterns
- Creating distributed applications requiring decentralized architecture
- Integrating ZeroMQ with asyncio for non-blocking I/O
- Needing secure messaging with CURVE, PLAIN, or GSSAPI authentication
- Building load-balanced services with DEALER/ROUTER sockets
- Implementing custom transport protocols or network architectures
- Requiring cross-language interoperability (ZeroMQ supports 40+ languages)

## Installation / Setup
### Installation

```bash
# Recommended: install from PyPI (includes bundled libzmq)
pip install pyzmq>=27.1.0

# Alternative: build from source with system libzmq
pip install --no-binary :all: pyzmq

# For development with latest features
pip install git+https://github.com/zeromq/pyzmq.git
```

### Prerequisites

- Python 3.9 or higher (or PyPy 3.9+)
- No external dependencies when using wheels (libzmq bundled)
- Optional: libsodium for CURVE security (included in wheels)

### Version Checking

```python
import zmq

# Check libzmq version
print(zmq.zmq_version())           # e.g., "4.3.5"
print(zmq.zmq_version_info())      # e.g., (4, 3, 5)

# Check pyzmq version  
print(zmq.pyzmq_version())         # e.g., "27.1.0"
print(zmq.pyzmq_version_info())    # e.g., (27, 1, 0)

# Check feature availability
print(zmq.has("libzmq-4.1"))       # True if libzmq >= 4.1
```

## Usage Examples
### Basic Request-Reply Pattern

See [Messaging Fundamentals](reference/01-messaging-fundamentals.md) for detailed explanation.

```python
import zmq

# Create context (singleton for the application)
context = zmq.Context()

# Backend worker: REP socket
worker = context.socket(zmq.REP)
worker.bind("tcp://*:5555")

# Frontend client: REQ socket  
client = context.socket(zmq.REQ)
client.connect("tcp://localhost:5555")

# Send request
client.send(b"Hello")

# Receive response
response = worker.recv()
print(response)  # b"Hello"

# Send reply
worker.send(b"World")

# Cleanup
client.close()
worker.close()
context.term()
```

### Pub/Sub Pattern

Refer to [Socket Types and Patterns](reference/02-socket-types-patterns.md) for complex scenarios.

```python
import zmq

context = zmq.Context()

# Publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

# Subscriber  
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

# Publish message
publisher.send_string("Hello, World!")

# Receive message
message = subscriber.recv_string()
print(message)  # "Hello, World!"
```

### Asyncio Integration

See [Async and Concurrent Operations](reference/03-async-concurrent.md) for advanced patterns.

```python
import asyncio
import zmq.asyncio

async def worker():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    await socket.bind("tcp://*:5555")
    
    while True:
        message = await socket.recv_string()
        print(f"Received: {message}")
        await socket.send_string(f"Processed: {message}")

# asyncio.run(worker())
```

## Advanced Topics
## Advanced Topics

- [Messaging Fundamentals](reference/01-messaging-fundamentals.md)
- [Socket Types Patterns](reference/02-socket-types-patterns.md)
- [Async Concurrent](reference/03-async-concurrent.md)
- [Security Authentication](reference/04-security-authentication.md)
- [Socket Options](reference/05-socket-options.md)
- [Advanced Topics](reference/06-advanced-topics.md)
- [Troubleshooting](reference/07-troubleshooting.md)

## Core Concepts Overview
### Context and Socket Lifecycle

1. **Create Context**: One `Context` per application (thread-local)
2. **Create Sockets**: Multiple sockets per context
3. **Bind or Connect**: Establish endpoints
4. **Send/Receive**: Message exchange
5. **Close**: Clean up resources

```python
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://server:5555")
# ... use socket ...
socket.close()  # Closes socket
context.term()  # Terminates context (closes all sockets)
```

### Message Types

- **Bytes**: Raw binary data (`send(b"data")`, `recv()`)
- **Strings**: UTF-8 encoded (`send_string("text")`, `recv_string()`)
- **JSON**: Automatic serialization (`send_json(obj)`, `recv_json()`)
- **Python objects**: Pickle-based (`send_pyobj(obj)`, `recv_pyobj()`)
- **Multipart**: Frame sequences (`send_multipart([b"frame1", b"frame2"])`)

### Blocking vs Non-Blocking

```python
# Blocking (default) - waits for operation to complete
socket.send(b"data")

# Non-blocking with timeout (milliseconds)
socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
try:
    message = socket.recv()
except zmq.Again:
    print("Timeout - no message received")

# Non-blocking with DONTWAIT flag
try:
    message = socket.recv(flags=zmq.DONTWAIT)
except zmq.Again:
    print("No message available")
```

## Troubleshooting
Common issues and solutions are documented in [Troubleshooting Guide](reference/07-troubleshooting.md). Key points:

- **Connection errors**: Check bind/connect addresses match, verify ports not in use
- **Message ordering**: Use ROUTER/DEALER with routing IDs for guaranteed delivery
- **Blocking operations**: Set timeouts or use Poller for non-blocking I/O
- **Security failures**: Verify CURVE keys match, check ZAP configuration
- **Resource leaks**: Always close sockets and terminate contexts

### Error Handling

```python
import zmq

try:
    socket.send(b"data", flags=zmq.DONTWAIT)
except zmq.Again:
    print("Socket not ready for sending")
except zmq.ZMQError as e:
    print(f"ZMQ error {e.errno}: {e.strerror}")
```

### Resource Cleanup

```python
# Use context manager pattern for automatic cleanup
from contextlib import contextmanager

@contextmanager
def zmq_socket(context, socket_type):
    socket = context.socket(socket_type)
    try:
        yield socket
    finally:
        socket.close()

# Or use try/finally
context = zmq.Context()
try:
    socket = context.socket(zmq.REQ)
    # ... use socket ...
finally:
    socket.close()
    context.term()
```

## Additional Resources
- [ZeroMQ Guide](https://zguide.zeromq.org/) - Comprehensive tutorial with Python examples
- [PyZMQ Documentation](https://pyzmq.readthedocs.io/) - Official API reference
- [ZeroMQ wiki](https://github.com/zeromq/libzmq/wiki) - Best practices and patterns
- [PyZMQ GitHub](https://github.com/zeromq/pyzmq) - Source code and examples

## Important Notes
1. **One context per thread**: Contexts are not thread-safe; create one per thread
2. **Sockets are not thread-safe**: Don't share sockets across threads
3. **Blocking by default**: Set timeouts or use Poller for non-blocking I/O
4. **Message framing**: ZeroMQ messages are frames; use multipart for complex data
5. **Security opt-in**: Security mechanisms must be explicitly configured
6. **Connection establishment**: Connect can happen before bind (asynchronous)
7. **HWM backpressure**: High Water Mark limits queue sizes to prevent memory exhaustion

