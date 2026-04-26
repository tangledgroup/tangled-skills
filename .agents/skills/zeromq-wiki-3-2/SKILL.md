---
name: zeromq-wiki-3-2
description: A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and best practices. Use when building distributed applications, implementing messaging patterns like REQ/REP, PUB/SUB, PUSH/PULL, designing multi-threaded architectures, working with ZMTP protocol, CURVE security, or understanding ØMQ internals for performance tuning and troubleshooting.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.2.0"
tags:
  - zeromq
  - messaging
  - distributed-systems
  - networking
  - sockets
  - patterns
category: messaging-library
external_references:
  - http://wiki.zeromq.org
  - https://github.com/zeromq
---

# ZeroMQ (ØMQ) 3.2

## Overview

ZeroMQ (ØMQ, pronounced "zero-em-queue") is a lightweight messaging kernel that extends standard socket interfaces with features traditionally provided by specialized messaging middleware. It provides an abstraction of asynchronous message queues, multiple messaging patterns, message filtering (subscriptions), seamless access to multiple transport protocols, and more — all in a tiny library.

Key characteristics:

- Connects code in any language, on any platform
- Carries messages across inproc, IPC, TCP, TIPC, and multicast (PGM/EPGM)
- Implements smart patterns: pub-sub, push-pull, request-reply, and router-dealer
- High-speed asynchronous I/O engines in a tiny library (~10k lines of C++)
- Backed by a large and active open source community
- Supports every modern language through bindings
- Builds any architecture: centralized, distributed, small, or large
- Free software (LGPL) with full commercial support available

ZeroMQ is not a neutral carrier — it imposes its own framing on transport protocols. It presents a familiar socket-based API while hiding message-processing engines underneath. The result is that "Message Oriented Middleware" becomes "Extra Spicy Sockets."

## When to Use

- Building distributed applications that need reliable messaging between components
- Implementing messaging patterns (request-reply, pub-sub, pipeline, exclusive pair)
- Designing multi-threaded architectures with message-passing concurrency
- Working with the ZMTP protocol for cross-language interoperability
- Adding CURVE security (encryption and authentication) to ZeroMQ applications
- Understanding ØMQ internals for performance tuning and troubleshooting
- Building load-balancing brokers, service-oriented architectures, or peer-to-peer networks
- Creating high-performance data distribution systems
- Migrating from traditional socket-based networking to pattern-based messaging

## Core Concepts

**Context**: The global state object for ZeroMQ. Created via `zmq_ctx_new()`, destroyed via `zmq_ctx_destroy()`. All sockets belong to a context. ZeroMQ has no global variables — the context prevents issues when the library is linked multiple times.

**Sockets**: Like BSD sockets but with built-in routing behavior. Sockets have types that define messaging patterns (REQ, REP, PUB, SUB, PUSH, PULL, DEALER, ROUTER, PAIR). Created via `zmq_socket()`, destroyed via `zmq_close()`.

**Messages**: Length-specified binary data. ZeroMQ messages are frames, not byte streams. For very small messages (≤30 bytes by default), data is stored directly in the `zmq_msg_t` structure on the stack — no heap allocation. Larger messages use reference-counted heap buffers.

**Transports**: ZeroMQ abstracts over multiple transports:
- `inproc://` — inter-thread (fastest, connected)
- `ipc://` — inter-process (disconnected, not on Windows)
- `tcp://` — TCP/IP network (disconnected, elastic, portable)
- `pgm://` — PGM multicast (for high fan-out ratios)
- `epgm://` — EPGM multicast (extended PGM)

**Patterns**: ZeroMQ routes and queues messages according to precise recipes called patterns. These are hard-coded into the library and implemented by pairs of sockets with matching types. The four core patterns are:
1. Request-reply (REQ/REP, REQ/ROUTER, DEALER/REP, DEALER/ROUTER)
2. Pub-sub (PUB/SUB)
3. Pipeline (PUSH/PULL)
4. Exclusive pair (PAIR/PAIR)

**I/O Threads**: ZeroMQ does all I/O in background threads. One I/O thread per gigabyte of throughput is the general rule. Set via `zmq_ctx_set(context, ZMQ_IO_THREADS, n)` before creating sockets.

## Advanced Topics

**Socket Types and Patterns**: Complete reference for REQ, REP, DEALER, ROUTER, PUB, SUB, PUSH, PULL, PAIR, XPUB, XSUB → [Socket Types and Patterns](reference/01-socket-types-and-patterns.md)

**Messaging Architecture**: Internal architecture of libzmq including concurrency model, object trees, reaper thread, message scheduling, and pipes → [Internal Architecture](reference/02-internal-architecture.md)

**ZMTP Protocol**: ZeroMQ Message Transport Protocol (ZMTP 3.0) specification, framing, security mechanisms, and version negotiation → [ZMTP Protocol](reference/03-zmtp-protocol.md)

**Security and CURVE**: CURVE encryption/authentication, ZAP authentication protocol, GSSAPI support, and libcurve reference implementation → [Security and CURVE](reference/04-security-and-curve.md)

**Reliable Messaging Patterns**: Lazy Pirate, Simple Pirate, Paranoid Pirate, Majordomo, Titanic, Binary Star, and Freelance patterns for production reliability → [Reliable Messaging Patterns](reference/05-reliable-messaging-patterns.md)

**Advanced Pub-Sub and Architecture**: Espresso tracing, Suicidal Snail detection, Clone pattern for state distribution, FileMQ, and distributed computing frameworks → [Advanced Pub-Sub and Architecture](reference/06-advanced-pubsub-and-architecture.md)

**Ecosystem and Bindings**: CZMQ high-level C binding, language bindings (pyzmq, jzmq, rbzmq, etc.), Zyre P2P framework, and community projects → [Ecosystem and Bindings](reference/07-ecosystem-and-bindings.md)
