---
name: aiozmq-0-7-0
description: Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks for building distributed applications with request-reply, push-pull, and pub-sub patterns. Use when building async Python applications requiring message-oriented middleware, remote procedure calls over ZeroMQ, or event-driven distributed systems with high-performance messaging.
version: "0.7.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - zeromq
  - asyncio
  - rpc
  - messaging
  - distributed-systems
  - pyzmq
  - pubsub
  - request-reply
  - pipeline
category: messaging
required_environment_variables: []
compatibility:
  python: ">=3.6"
  platforms:
    - Linux
    - macOS
    - Windows (limited)
---

# aiozmq 0.7.0

ZeroMQ integration with Python asyncio (PEP 3156). Provides async transport-level APIs, stream abstractions, and a comprehensive RPC framework for building distributed applications using ZeroMQ messaging patterns.

## When to Use

- Building async Python applications requiring ZeroMQ message passing
- Implementing remote procedure calls (RPC) over ZeroMQ transports
- Creating request-reply, push-pull, or publish-subscribe architectures
- Integrating existing pyzmq code with asyncio event loops
- Building distributed systems with high-performance messaging
- Needing stream-based async/await interface for ZeroMQ sockets

## Setup

### Installation

```bash
# Core library (requires pyzmq)
pip install aiozmq

# With RPC support (requires msgpack)
pip install aiozmq[msgpack]
pip install "aiozmq[rpc]"
```

### Dependencies

- Python 3.6+
- ZeroMQ 3.2+
- pyzmq 13.1+ (not 17.1.2)
- msgpack-python 0.5.0+ (optional, for RPC)

### Platform Support

- **Linux**: Full support
- **macOS**: Full support  
- **Windows**: Limited support (no IPC endpoints, uses select-based event loop)

## Quick Start

### Simple Request-Reply with Streams

See [Streams API](references/01-streams-api.md) for detailed documentation.

```python
import asyncio
import aiozmq
import zmq

async def main():
    # Create ROUTER socket (server)
    router = await aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:5555'
    )
    
    # Create DEALER socket (client)
    dealer = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    
    # Send request
    msg = (b'data', b'ask', b'message')
    dealer.write(msg)
    
    # Router receives and echoes back
    received = await router.read()
    router.write(received)
    
    # Client receives response
    answer = await dealer.read()
    print(answer)
    
    dealer.close()
    router.close()

asyncio.run(main())
```

### Simple RPC Server and Client

See [RPC Framework](references/02-rpc-framework.md) for comprehensive guide.

```python
import asyncio
import aiozmq.rpc

class ServerHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    @aiozmq.rpc.method
    def greet(self, name: str) -> str:
        """Return greeting message."""
        return f"Hello, {name}!"

async def main():
    # Start RPC server
    server = await aiozmq.rpc.serve_rpc(
        ServerHandler(),
        bind='tcp://*:5555'
    )
    server_addr = list(server.transport.bindings())[0]
    print(f"Server listening on {server_addr}")
    
    # Connect RPC client
    client = await aiozmq.rpc.connect_rpc(
        connect=server_addr
    )
    
    # Call remote methods
    result = await client.call.add(1, 2)
    print(f"1 + 2 = {result}")
    
    greeting = await client.call.greet("World")
    print(greeting)
    
    server.close()
    await server.wait_closed()
    client.close()
    await client.wait_closed()

asyncio.run(main())
```

### Pipeline (Push-Pull) Pattern

See [Pipeline Pattern](references/03-rpc-patterns.md) for details.

```python
import asyncio
import aiozmq.rpc

class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def process(self, data: str):
        print(f"Processing: {data}")

async def main():
    # Server (pull side)
    listener = await aiozmq.rpc.serve_pipeline(
        Handler(),
        bind='tcp://*:5556'
    )
    
    # Client (push side)
    notifier = await aiozmq.rpc.connect_pipeline(
        connect='tcp://127.0.0.1:5556'
    )
    
    # Fire-and-forget notifications
    await notifier.notify.process("Task 1")
    await notifier.notify.process("Task 2")
    
    await asyncio.sleep(0.1)  # Allow processing
    
    listener.close()
    await listener.wait_closed()
    notifier.close()
    await notifier.wait_closed()

asyncio.run(main())
```

## Core Concepts

### Architecture Overview

aiozmq provides three abstraction layers:

1. **Core Layer** (`create_zmq_connection`, `ZmqTransport`, `ZmqProtocol`)
   - Low-level asyncio transport/protocol interface
   - Direct control over ZeroMQ socket lifecycle
   - See [Core API](references/04-core-api.md)

2. **Stream Layer** (`create_zmq_stream`, `ZmqStream`)
   - Higher-level async stream abstraction
   - `read()`/`write()` methods with backpressure
   - See [Streams API](references/01-streams-api.md)

3. **RPC Layer** (`serve_rpc`, `connect_rpc`, handlers)
   - Remote procedure call framework
   - Automatic serialization with msgpack
   - Method discovery and validation
   - See [RPC Framework](references/02-rpc-framework.md)

### Event Loop Integration

aiozmq works with standard asyncio event loops:

```python
import asyncio
import aiozmq

# Works with default event loop
async def main():
    stream = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    # ... use stream
```

For advanced scenarios, can use `ZmqEventLoop`:

```python
from aiozmq import ZmqEventLoop, ZmqEventLoopPolicy

# Set custom event loop policy
policy = ZmqEventLoopPolicy()
asyncio.set_event_loop_policy(policy)

loop = asyncio.get_event_loop()
# Now can use loop.create_zmq_connection() directly
```

See [Core API](references/04-core-api.md) for details.

## Reference Files

- [`references/01-streams-api.md`](references/01-streams-api.md) - Stream abstraction with read/write/drain, buffer limits, and flow control
- [`references/02-rpc-framework.md`](references/02-rpc-framework.md) - RPC framework fundamentals: handlers, methods, serialization, error handling
- [`references/03-rpc-patterns.md`](references/03-rpc-patterns.md) - RPC patterns: request-reply, pipeline (push-pull), pub-sub with examples
- [`references/04-core-api.md`](references/04-core-api.md) - Core transport/protocol API, ZmqEventLoop, low-level socket control
- [`references/05-advanced-topics.md`](references/05-advanced-topics.md) - Custom serialization, exception translation, monitoring, nested namespaces

## Common Patterns

### ZeroMQ Socket Types

aiozmq supports all ZeroMQ socket types:

| Socket Type | Pattern | Use Case |
|-------------|---------|----------|
| `REQ`/`REP` | Request-Reply | Simple RPC, client-server |
| `DEALER`/`ROUTER` | Request-Reply (advanced) | Many-to-many, load balancing |
| `PUSH`/`PULL` | Pipeline | Task distribution, fire-and-forget |
| `PUB`/`SUB` | Pub-Sub | Broadcasting, event notification |
| `PAIR` | Peer-to-peer | Simple bidirectional communication |

### Endpoint URIs

Supported transport schemes:

```python
# TCP (all platforms)
bind='tcp://127.0.0.1:5555'      # Bind to specific address
bind='tcp://*:5555'              # Bind to all interfaces
connect='tcp://127.0.0.1:5555'   # Connect to server

# In-process (Linux/macOS only)
bind='ipc:///tmp/mysocket'        # Unix domain socket
bind='inproc://myapp'            # Within same process

# Multicast (Linux with PGM support)
bind='pgm://239.100.1.1:5555'    # PGM multicast
```

## Troubleshooting

### Common Issues

**"Connection refused" errors**: Ensure server binds before client connects. ZeroMQ requires the binding endpoint to be ready.

```python
# Correct order
server = await aiozmq.create_zmq_stream(zmq.ROUTER, bind='tcp://*:5555')
addr = list(server.transport.bindings())[0]
client = await aiozmq.create_zmq_stream(zmq.DEALER, connect=addr)
```

**Message framing with DEALER/ROUTER**: These sockets add identity frames. Use tuple messages:

```python
# Router receives: [identity, *message_parts]
msg = await router.read()  # Returns tuple of byte strings
router.write(msg)  # Echo back same tuple
```

**RPC method not found**: Methods must be decorated with `@aiozmq.rpc.method`:

```python
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method  # Required!
    def my_method(self, arg):
        return arg
```

**Windows limitations**: IPC endpoints and some advanced features unavailable. Use TCP for cross-platform compatibility.

### Getting Bind Address

After binding with `*`, retrieve actual address:

```python
server = await aiozmq.create_zmq_stream(zmq.ROUTER, bind='tcp://*:5555')
actual_addr = list(server.transport.bindings())[0]
print(f"Bound to: {actual_addr}")  # e.g., 'tcp://127.0.0.1:5555'
```

### Resource Cleanup

Always close connections properly:

```python
stream.close()
# For RPC services, wait for cleanup
await service.wait_closed()
```

## See Also

- [ZeroMQ Documentation](https://zeromq.org/documentation/)
- [pyzmq Documentation](https://pyzmq.readthedocs.io/)
- [aiozmq GitHub](https://github.com/aio-libs/aiozmq)
- [aiozmq Documentation](https://aiozmq.readthedocs.io/en/v0.7.0/)
