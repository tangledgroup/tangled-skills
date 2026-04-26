---
name: aiozmq-0-7-0
description: Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks for building distributed applications with request-reply, push-pull, and pub-sub patterns. Use when building async Python applications requiring message-oriented middleware, remote procedure calls over ZeroMQ, or event-driven distributed systems with high-performance messaging.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.7.0"
tags:
  - zeromq
  - asyncio
  - rpc
  - messaging
  - distributed
  - streaming
category: messaging
external_references:
  - https://aiozmq.readthedocs.io/en/v0.7.0/
  - https://github.com/aio-libs/aiozmq
---

# aiozmq 0.7.0

## Overview

aiozmq provides ZeroMQ integration with Python asyncio (PEP 3156). It bridges the gap between ZeroMQ's high-performance messaging library and Python's async event loop, offering three layers of abstraction:

- **Core API** — Low-level `ZmqTransport` and `ZmqProtocol` for fine-grained control over ZeroMQ connections
- **Streams API** — High-level `ZmqStream` with `read()`/`write()` for convenient message passing
- **RPC Framework** — Full remote procedure call support with request-reply, push-pull (pipeline), and publish-subscribe patterns

The library works on Linux, macOS, and Windows. Windows has limited support: no `ipc://` endpoints and the deprecated `ZmqEventLoop` uses `select` rather than more efficient alternatives.

## When to Use

- Building distributed async applications with ZeroMQ messaging patterns
- Implementing remote procedure calls (RPC) over ZeroMQ transports
- Creating pub-sub, pipeline, or request-reply architectures in asyncio
- Integrating ZeroMQ sockets into existing asyncio event loops
- Monitoring ZeroMQ socket events asynchronously

## Installation / Setup

Install aiozmq with pip:

```bash
pip install aiozmq
```

Core requirements:
- Python 3.3+
- pyzmq 13.1+
- asyncio (built-in since Python 3.4)

The optional `aiozmq.rpc` submodule additionally requires msgpack:

```bash
pip install msgpack-python>=0.4.0
```

## Core Concepts

**ZeroMQ sockets** are the fundamental communication primitives. aiozmq supports all standard socket types: `REQ`, `REP`, `PUB`, `SUB`, `PAIR`, `DEALER`, `ROUTER`, `PULL`, `PUSH`, and others.

**Endpoints** are strings in the format `transport://address`. Common transports include:
- `tcp://` — TCP unicast (most common)
- `ipc://` — Local inter-process communication (Unix only)
- `inproc://` — In-process (inter-thread) communication
- `pgm://`, `epgm://` — Reliable multicast

**Bind vs Connect**: The `bind` side listens for incoming connections; the `connect` side initiates outbound connections. Both can accept a single string or an iterable of endpoint strings.

**Message format**: Messages are multipart — sent as tuples or lists of byte strings. Each frame in the tuple becomes a separate message part on the wire.

## Advanced Topics

**Core API (Transport/Protocol)**: Low-level ZeroMQ transport and protocol classes for custom connection handling → [Core API](reference/01-core-api.md)

**Streams API**: High-level stream-oriented interface with `read()`/`write()` and socket event monitoring → [Streams API](reference/02-streams-api.md)

**RPC Framework**: Remote procedure calls with request-reply, push-pull, and pub-sub patterns including exception translation, signature validation, and custom value translators → [RPC Framework](reference/03-rpc-framework.md)
