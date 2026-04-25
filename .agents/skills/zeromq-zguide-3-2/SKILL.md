---
name: zeromq-zguide-3-2
description: Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and distributed computing architectures. Use when building asynchronous message-driven applications, implementing request-reply patterns, pub-sub systems, load balancing, or designing scalable distributed systems with ZeroMQ/3.2+.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - zeromq
  - zmq
  - messaging
  - sockets
  - distributed-systems
  - pub-sub
  - request-reply
  - load-balancing
  - asynchronous
category: messaging
required_environment_variables: []
---

# ZeroMQ ZGuide 3.2

## Overview

Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and distributed computing architectures. Use when building asynchronous message-driven applications, implementing request-reply patterns, pub-sub systems, load balancing, or designing scalable distributed systems with ZeroMQ/3.2+.

Comprehensive toolkit for ZeroMQ version 3.2 based on the official ZGuide documentation. Covers basic through advanced messaging patterns, socket types, reliability mechanisms, and distributed computing architectures with examples in 28+ languages including C, C++, Java, Python, Go, Node.js, Erlang, and more.

## When to Use

- Building asynchronous message-driven applications
- Implementing request-reply communication patterns
- Creating pub-sub broadcasting systems
- Designing load-balanced worker architectures
- Building reliable messaging with fault tolerance
- Implementing distributed computing frameworks
- Needing language-agnostic messaging solutions
- Working with TCP, IPC, or inproc transports

## Quick Start

### Hello World Request-Reply

Basic request-reply pattern demonstrating ZeroMQ's core functionality:

**Server (REP socket):**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    print(f"Received: {message}")
    socket.send(b"World")
```

**Client (REQ socket):**
```python
import zmq

context = zmq.Context()
socket = socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

for i in range(10):
    socket.send(b"Hello")
    message = socket.recv()
    print(f"Received: {message}")
```

See [Basics](references/01-basics.md) for detailed explanation and multi-language examples.

### Publishing Weather Updates

Basic pub-sub pattern for broadcasting messages:

**Publisher:**
```python
import zmq
import time

context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

while True:
    publisher.send_string(f"Random weather update {time.time()}")
    time.sleep(1)
```

**Subscriber:**
```python
import zmq

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all

while True:
    message = subscriber.recv_string()
    print(f"Received: {message}")
```

Refer to [Pub-Sub Patterns](references/03-advanced-pubsub.md) for advanced techniques.

## Core Concepts Overview

### Socket Types

ZeroMQ provides these socket types for different communication patterns:

| Socket Type | Pattern | Description |
|-------------|---------|-------------|
| REQ/REP | Request-Reply | Basic client-server messaging |
| DEALER/ROUTER | Advanced R-R | Custom routing, load balancing |
| PUB/SUB | Publish-Subscribe | One-to-many broadcasting |
| PUSH/PULL | Pipeline | Fan-out work distribution |
| PAIR | Peer-to-Peer | Simple 1:1 communication |
| XPUB/XSUB | Extended Pub-Sub | Subscription management |

See [Sockets and Patterns](references/02-sockets-patterns.md) for complete API reference.

### Transport Protocols

- **tcp://** - TCP transport for network communication
- **ipc://** - IPC sockets for local inter-process communication
- **inproc://** - In-process sockets for fastest communication within same process

## Reference Files

This skill uses progressive disclosure to manage complexity:

- [`references/01-basics.md`](references/01-basics.md) - Getting started, Hello World examples in 28+ languages, basic concepts
- [`references/02-sockets-patterns.md`](references/02-sockets-patterns.md) - Complete socket API, messaging patterns, multipart messages, poller usage
- [`references/03-advanced-pubsub.md`](references/03-advanced-pubsub.md) - Advanced pub-sub patterns, last value caching, slow subscriber detection
- [`references/04-advanced-request-reply.md`](references/04-advanced-request-reply.md) - ROUTER/DEALER sockets, load balancing, custom routing strategies
- [`references/05-reliable-request-reply.md`](references/05-reliable-request-reply.md) - Fault tolerance, Lazy Pirate pattern, reliable queuing, LRU routing
- [`references/06-community.md`](references/06-community.md) - ZeroMQ community resources, bindings, extensions, and ecosystem tools
- [`references/07-advanced-architecture.md`](references/07-advanced-architecture.md) - Service-oriented architecture, device patterns, security considerations
- [`references/08-distributed-framework.md`](references/08-distributed-framework.md) - Building distributed computing frameworks, task queues, worker pools

## Common Patterns Quick Reference

### Request-Reply (REQ/REP)
- Simple client-server pattern
- REQ sends request, waits for reply
- REP receives request, sends reply
- See [Basics](references/01-basics.md)

### Load Balancing (DEALER/ROUTER)
- Router distributes work to multiple dealers
- Round-robin or custom routing strategies
- Identity frames manage client connections
- See [Advanced Request-Reply](references/04-advanced-request-reply.md)

### Publish-Subscribe (PUB/SUB)
- Publisher broadcasts to all subscribers
- Subscribers filter by topic prefix
- Fire-and-forget, no acknowledgments
- See [Advanced Pub-Sub](references/03-advanced-pubsub.md)

### Pipeline (PUSH/PULL)
- Push distributes work to pull sockets
- Supports multi-stage pipelines
- Automatic load balancing across pulls
- See [Sockets and Patterns](references/02-sockets-patterns.md)

## Troubleshooting

### Common Issues

**Connection failures:**
- Ensure server binds before client connects
- Check firewall rules for tcp:// ports
- Verify bind/connect addresses match

**Message ordering:**
- REQ/REP guarantees request-reply pairing
- PUB/SUB does not guarantee delivery order
- Use multipart messages for complex protocols

**Blocking operations:**
- Use zmq_poll() for non-blocking I/O
- Set socket timeouts with ZMQ_RCVTIMEO/ZMQ_SNDTIMEO
- Consider using DEALER instead of REQ for more control

See [Reliable Request-Reply](references/05-reliable-request-reply.md) for fault tolerance patterns.

### Best Practices

1. **Always close sockets** - Use try-finally or context managers
2. **Use appropriate timeouts** - Prevent indefinite blocking
3. **Handle multipart messages** - ZeroMQ uses frames internally
4. **Consider reliability needs** - Basic REQ/REP vs. Lazy Pirate pattern
5. **Monitor slow subscribers** - Implement Suicidal Snail pattern for pub-sub

## Language Support

ZeroMQ provides official and community bindings for 28+ languages:

- **C/C++** - Reference implementation, 100% coverage
- **Java** - Complete API coverage, 100% examples
- **Python** - pyzmq binding, extensive examples
- **Go** - gzmq and other bindings
- **Node.js** - nanomsg and other implementations
- **Erlang/Elixir** - zeromq and erlpipe
- **C#/.NET** - NetMQ and other bindings
- **Rust** - zmq and async-zmq crates

See [Community Resources](references/06-community.md) for binding details.

## Version Compatibility

This skill covers ZeroMQ 3.2 API. Key differences from 2.x:

- New socket types: DEALER, ROUTER, XPUB, XSUB
- Improved security with CURVE encryption
- Better Windows support
- Enhanced monitoring capabilities

For ZeroMQ 4.x features (gossip, vector transport), see official documentation.

## Additional Resources

- **Official Website**: https://zeromq.org/
- **ZGuide Online**: https://zguide.zeromq.org/
- **GitHub Repository**: https://github.com/zeromq/libzmq
- **API Documentation**: https://api.zeromq.org/
- **Mailing List**: zeromq-dev@lists.zeromq.org

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/zeromq-zguide-3-2/`). All paths are relative to this directory.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
