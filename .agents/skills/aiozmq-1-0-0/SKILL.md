---
name: aiozmq-1-0-0
description: Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks (request-reply, pipeline, pub-sub). Use when building async Python applications requiring message-oriented middleware, remote procedure calls over ZeroMQ, or event-driven distributed systems with high-performance messaging.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - zeromq
  - asyncio
  - rpc
  - messaging
  - distributed
  - streaming
category: messaging
external_references:
  - https://aiozmq.readthedocs.io/
  - https://github.com/aio-libs/aiozmq
---

# aiozmq 1.0.0

## Overview

aiozmq provides ZeroMQ integration with Python asyncio (PEP 3156). It bridges the gap between ZeroMQ's high-performance messaging library and Python's async event loop, offering three layers of abstraction:

- **Core API** — Low-level `ZmqTransport` and `ZmqProtocol` for fine-grained control over ZeroMQ connections
- **Streams API** — High-level `ZmqStream` with `read()`/`write()` for convenient message passing
- **RPC Framework** — Full remote procedure call support with request-reply, push-pull (pipeline), and publish-subscribe patterns

Unlike `zmq.asyncio` (built into pyzmq), aiozmq works with any asyncio event loop including `uvloop`. It uses epoll natively rather than the internal ZMQ Poller, making it suitable for web servers handling thousands of concurrent TCP connections alongside ZeroMQ sockets.

## When to Use

- Building async Python applications requiring ZeroMQ messaging with proper event loop integration
- Implementing RPC over ZeroMQ with request-reply, pipeline, or pub-sub patterns
- Integrating ZeroMQ with aiohttp or other async web frameworks
- Needing uvloop compatibility (zmq.asyncio cannot use uvloop)
- Building distributed systems where ZMQ sockets share the event loop with many regular TCP sockets

## Core Concepts

### Why aiozmq Over zmq.asyncio?

`zmq.asyncio` replaces the base event loop with a custom `ZmqEventLoop` built on `zmq.Poller`. This has two disadvantages:

1. Cannot combine with other loop implementations like `uvloop`
2. The internal ZMQ Poller is slow with thousands of regular TCP sockets

aiozmq works with epoll natively and cooperates with any event loop. It is the recommended choice when ZeroMQ shares an event loop with many non-ZMQ sockets (e.g., aiohttp web servers).

### Supported Python Versions

Python 3.6+ (dropped Python 3.5 support in 1.0.0). Tested on Python 3.9, 3.10, and 3.11.

### Dependencies

- **pyzmq** >= 13.1 (excluding 17.1.2)
- **msgpack** >= 0.5.0 (required for `aiozmq.rpc` submodule only, install with `pip install aiozmq[rpc]`)
- **libzmq** >= 3.0

### Installation

```bash
pip install aiozmq          # core + streams
pip install aiozmq[rpc]     # includes msgpack for RPC support
```

## Advanced Topics

**Transport and Protocol API**: Low-level ZmqTransport and ZmqProtocol interfaces → [Transport & Protocol](reference/01-transport-protocol.md)

**Streams API**: High-level read/write abstraction over ZeroMQ sockets → [Streams API](reference/02-streams.md)

**RPC Framework**: Request-reply, pipeline, and pub-sub RPC patterns with AttrHandler → [RPC Framework](reference/03-rpc-framework.md)

**Event Monitoring and CLI**: Socket event monitoring and aiozmq proxy tools → [Monitoring & CLI](reference/04-monitoring-cli.md)
