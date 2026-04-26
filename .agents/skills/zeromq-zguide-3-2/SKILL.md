---
name: zeromq-zguide-3-2
description: Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and distributed computing architectures. Use when building asynchronous message-driven applications, implementing request-reply patterns, pub-sub systems, load balancing, or designing scalable distributed systems with ZeroMQ/3.2+.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
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
external_references:
  - https://zguide.zeromq.org/
  - https://github.com/zeromq
---

# ZeroMQ ZGuide 3.2

## Overview

ZeroMQ (also known as ØMQ, 0MQ, or zmq) is an embeddable networking library that acts like a concurrency framework. It gives you sockets that carry atomic messages across various transports like in-process, inter-process, TCP, and multicast. You can connect sockets N-to-N with patterns like fan-out, pub-sub, task distribution, and request-reply. It's fast enough to be the fabric for clustered products. Its asynchronous I/O model gives you scalable multicore applications built as asynchronous message-processing tasks.

ZeroMQ is from [iMatix](http://www.imatix.com) and is LGPLv3 open source. The ZGuide ("The Guide") is written by Pieter Hintjens and 100+ contributors, with 60+ diagrams and 750 examples in 28 languages. This version covers ZeroMQ 3.2.

Key projects in the ZeroMQ ecosystem:

- **libzmq** — core engine in C++, implements ZMTP/3.1 (10,800+ stars)
- **czmq** — high-level C binding for ØMQ
- **pyzmq** — Python bindings (4,100+ stars)
- **cppzmq** — header-only C++ binding
- **netmq** — 100% native C# implementation
- **jeromq** — pure Java implementation
- **zeromq.js** — Node.js bindings
- **zmq.rs** — native Rust implementation
- **zyre** — framework for proximity-based peer-to-peer applications
- **majordomo** — service-oriented reliable queuing protocol
- **malamute** — ZeroMQ enterprise messaging broker

## When to Use

- Building asynchronous message-driven applications
- Implementing request-reply patterns (REQ/REP, DEALER/ROUTER)
- Creating pub-sub data distribution systems
- Designing load-balanced task distribution architectures
- Building scalable distributed systems with ZeroMQ 3.2+
- Working with multipart messages and message envelopes
- Implementing reliable messaging patterns (Pirate patterns, Majordomo)
- Designing peer-to-peer or proximity-based networking
- Creating custom protocols on top of ZeroMQ ("unprotocols")

## Core Concepts

**Sockets, not connections.** ZeroMQ presents a familiar socket API but hides message-processing engines underneath. Sockets have types that define routing semantics — you plug them together like construction toys to define your network architecture.

**Asynchronous I/O.** All I/O happens in background threads. Messages arrive in local input queues and are sent from local output queues. Your application code never blocks on network I/O (except in specific cases like REQ sockets).

**Messaging patterns.** ZeroMQ routes and queues messages according to precise recipes called *patterns*. The four core patterns are:

- **Request-reply** — clients to services (RPC, task distribution)
- **Pub-sub** — publishers to subscribers (data distribution)
- **Pipeline** — fan-out/fan-in (parallel task distribution and collection)
- **Exclusive pair** — two sockets exclusively (thread-to-thread)

**No broker.** ZeroMQ is "zero broker" — it provides the messaging fabric without requiring a central message broker. You can build brokers from ZeroMQ itself if needed.

**Transports.** ZeroMQ abstracts over multiple transports: `tcp` (disconnected TCP, elastic and portable), `ipc` (inter-process, UNIX only), `inproc` (in-process, fastest), `pgm` and `epgm` (multicast).

## Advanced Topics

**Basics**: Hello World, task distribution, context lifecycle, version reporting → [Basics](reference/01-basics.md)

**Sockets and Patterns**: Socket API, messaging patterns, multipart messages, proxies, polling, multithreading → [Sockets and Patterns](reference/02-sockets-and-patterns.md)

**Advanced Request-Reply**: Reply envelopes, ROUTER identities, load balancing, async client/server → [Advanced Request-Reply](reference/03-advanced-request-reply.md)

**Reliable Messaging**: Pirate patterns, heartbeating, Majordomo protocol, Binary Star failover → [Reliable Messaging](reference/04-reliable-messaging.md)

**Advanced Pub-Sub**: Espresso tracing, last-value caching, slow subscriber detection, Clone pattern → [Advanced Pub-Sub](reference/05-advanced-pub-sub.md)

**Architecture and Protocols**: MOPED design process, unprotocols, serialization, FileMQ, SASL auth → [Architecture and Protocols](reference/06-architecture-and-protocols.md)

**Distributed Computing**: Discovery, presence, peer-to-peer Harmony pattern, Zyre framework → [Distributed Computing](reference/07-distributed-computing.md)
