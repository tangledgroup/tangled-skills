---
name: zeromq-wiki-3-2
description: A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and best practices. Use when building distributed applications, implementing messaging patterns like REQ/REP, PUB/SUB, PUSH/PULL, designing multi-threaded architectures, working with ZMTP protocol, CURVE security, or understanding ØMQ internals for performance tuning and troubleshooting.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - messaging
  - sockets
  - distributed-systems
  - zero-mq
  - zmq
  - pub-sub
  - request-reply
  - pipeline
  - networking
  - protocols
category: messaging
external_references:
  - http://wiki.zeromq.org
  - https://github.com/zeromq
---
## Overview
A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and best practices. Use when building distributed applications, implementing messaging patterns like REQ/REP, PUB/SUB, PUSH/PULL, designing multi-threaded architectures, working with ZMTP protocol, CURVE security, or understanding ØMQ internals for performance tuning and troubleshooting.

A comprehensive toolkit for the ZeroMQ (ØMQ) messaging library, covering socket patterns, transport protocols, security mechanisms, architecture internals, and best practices for building distributed applications.

## When to Use
- Designing distributed applications with asynchronous messaging
- Implementing socket patterns: REQ/REP, PUB/SUB, PUSH/PULL, PAIR, DEALER/ROUTER
- Building multi-threaded applications with ØMQ's thread-safe sockets
- Working with ZMTP protocol for interoperability
- Implementing security with ZMTP-PLAIN or ZMTP-CURVE authentication
- Tuning performance and understanding ØMQ internals
- Troubleshooting messaging issues in distributed systems
- Writing language bindings for ZeroMQ
- Understanding Majordomo Protocol (MDP) for service orchestration

## Usage Examples
### Basic REQ/REP Pattern

See [Socket Patterns](reference/01-socket-patterns.md) for detailed explanation and examples.

```c
// Server (REP)
void *socket = zmq_socket(ctx, ZMQ_REP);
zmq_bind(socket, "tcp://*:5555");

// Client (REQ)
void *socket = zmq_socket(ctx, ZMQ_REQ);
zmq_connect(socket, "tcp://server:5555");
```

### Basic PUB/SUB Pattern

Refer to [Messaging Patterns](reference/02-messaging-patterns.md) for complex scenarios.

```c
// Publisher
void *pub = zmq_socket(ctx, ZMQ_PUB);
zmq_bind(pub, "tcp://*:5556");

// Subscriber  
void *sub = zmq_socket(ctx, ZMQ_SUB);
zmq_connect(sub, "tcp://server:5556");
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "topic", 5);
```

## Core Concepts
ZeroMQ provides a **socket library** that replaces standard sockets (BSD sockets) with sockets that implement various messaging patterns out of the box. Key concepts:

- **Asynchronous I/O**: ØMQ handles all network I/O asynchronously using I/O threads
- **Thread-safe sockets**: Sockets cannot be shared between threads, but context can be
- **Multiple transports**: TCP, IPC, inproc (in-process), NORM (reliable multicast)
- **No central daemon**: Pure peer-to-peer communication, no broker required
- **Message framing**: Automatic message boundaries unlike TCP streams

See [Architecture Overview](reference/03-architecture.md) for deep dive into internals.

## Socket Types and Patterns
| Socket Type | Pairs With | Pattern | Use Case |
|-------------|------------|---------|----------|
| REQ | REP | Request-Reply | RPC, client-server |
| REP | REQ | Request-Reply | RPC, client-server |
| PUB | SUB | Publish-Subscribe | Event notification, broadcasting |
| SUB | PUB | Publish-Subscribe | Event notification, filtering |
| PUSH | PULL | Pipeline | Task distribution, load balancing |
| PULL | PUSH | Pipeline | Task collection, aggregation |
| DEALER | ROUTER | Request-Reply (advanced) | Load balancing, routing |
| ROUTER | DEALER | Request-Reply (advanced) | Message routing, addressing |
| PAIR | PAIR | Peer-to-Peer | Simple 1:1 communication |
| XSUB | XPUB | Ext. Pub-Sub | Internal use by proxies |
| XPUB | XSUB | Ext. Pub-Sub | Internal use by proxies |

See [Socket Patterns](reference/01-socket-patterns.md) for detailed RFC specifications.

## Transport Protocols
### tcp:// (TCP/IP)
- Standard TCP transport over IP networks
- Supports both bind and connect operations
- Example: `tcp://*:5555` (bind), `tcp://server:5555` (connect)

### ipc:// (Unix Domain Sockets)
- Fast local communication on Unix/Linux
- Uses filesystem paths as endpoints
- Example: `ipc:///tmp/mysocket`

### inproc:// (In-Process)
- Fastest transport, for sockets in same process
- Requires exact endpoint name match
- Example: `inproc://myinternal`

See [Transport Protocols](reference/04-protocols.md) for ZMTP wire protocol details.

## Security
ZeroMQ supports authentication through the ZMTP (ZeroMQ Messaging Transport Protocol):

### ZMTP-PLAIN (Username/Password)
Simple username and password authentication. See [Security Guide](reference/05-security.md).

```c
// Set credentials on client
zmq_setsockopt(socket, ZMQ_PLAIN_USERNAME, "user", 4);
zmq_setsockopt(socket, ZMQ_PLAIN_PASSWORD, "pass", 4);
```

### ZMTP-CURVE (Public Key Cryptography)
End-to-end encryption using Curve25519 for key exchange and AES-128-CBC for message encryption.

```c
// Generate key pair
zmq_curve_public(keypair, secret_key);

// Configure server
zmq_curve_keypair(server, "secret", "public");
zmq_setsockopt(server, ZMQ_CURVE_SERVER, &yes, 1);

// Configure client
zmq_curve_public(client_secret, client_public);
zmq_curve_keypair(client, server_public, client_public, client_secret);
```

See [ZMTP-CURVE RFC](reference/05-security.md) for complete specification.

## Advanced Topics
## Advanced Topics

- [Socket Patterns](reference/01-socket-patterns.md)
- [Messaging Patterns](reference/02-messaging-patterns.md)
- [Architecture](reference/03-architecture.md)
- [Protocols](reference/04-protocols.md)
- [Security](reference/05-security.md)
- [Performance](reference/06-performance.md)
- [Faq Troubleshooting](reference/07-faq-troubleshooting.md)

## API Reference
The ZeroMQ C API is documented in RFC 8/MMI and the official API reference:
- **Context**: `zmq_init()`, `zmq_term()`
- **Sockets**: `zmq_socket()`, `zmq_close()`
- **Endpoints**: `zmq_bind()`, `zmq_connect()`, `zmq_unbind()`
- **Messaging**: `zmq_send()`, `zmq_recv()`, `zmq_sendmsg()`, `zmq_recvmsg()`
- **Options**: `zmq_setsockopt()`, `zmq_getsockopt()`

See [Socket Patterns](reference/01-socket-patterns.md) for API examples and [Architecture Overview](reference/03-architecture.md) for threading guidelines.

## Troubleshooting
### Messages Not Being Received
1. Check that PUB/SUB topics match exactly (including trailing bytes)
2. Verify SUB socket has `ZMQ_SUBSCRIBE` set before connecting
3. Ensure endpoint addresses match (bind vs connect)
4. Check firewall rules for TCP ports

### Performance Issues
1. Increase `ZMQ_SNDBUF` and `ZMQ_RCVBUF` socket options
2. Tune `ZMQ_LINGER` to prevent blocked closes
3. Use `inproc://` for same-process communication
4. Consider message batching for small messages

See [FAQ and Troubleshooting](reference/07-faq-troubleshooting.md) for more common issues.

### Common Pitfalls

**Blocking send on PUSH socket**: If all PULL sockets disconnect, PUSH will block. Set `ZMQ_LINGER` to prevent hangs.

**REQ socket state machine**: REQ must alternate send/recv strictly. Use DEALER for flexible patterns.

**SUB socket late subscription**: SUB sockets miss messages published before subscription. Consider catchup mechanisms.

## Community and Resources
- **Official Guide (ZGuide)**: http://zguide.zeromq.org - Hundreds of worked examples
- **API Reference**: http://api.zeromq.org - Complete C API documentation
- **RFCs**: http://rfc.zeromq.org - Protocol specifications
- **Wiki**: http://wiki.zeromq.org - Community documentation
- **GitHub**: https://github.com/zeromq - Source code and issues
- **Mailing lists**: See [Community Resources](reference/07-faq-troubleshooting.md)

## Related Skills
Consider using with:
- `cryptography-46` for implementing custom encryption layers
- `sqlalchemy-2-0` for persistent message storage
- `aiohttp-3-13` for HTTP bridges to ØMQ backends

