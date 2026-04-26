# Architecture and Protocols

## MOPED — Message-Oriented Pattern for Elastic Design

A five-step process for growing working ZeroMQ architectures from rough ideas:

1. **Internalize the semantics** — learn socket patterns through practice
2. **Draw a rough architecture** — whiteboard the core problem, minimal boxes and arrows
3. **Decide on the contracts** — define APIs and protocols (unprotocols) before implementation
4. **Write a minimal end-to-end solution** — skeleton "Hello World" that tests the overall flow
5. **Solve one problem and repeat** — issue-driven development, test each change individually

Key principle: focus on contracts before implementations. Design APIs wearing the hat of the person who has to use them, not the person implementing them. You can always add functionality; removing complexity is much harder.

## Unprotocols

"Protocols without the goats" — lightweight protocol specifications built on ZeroMQ's framing layer. ZeroMQ handles framing, connections, and routing silently, making it surprisingly easy to write full protocol specs on top.

### How to Write Unprotocols

- Start simple, develop step-by-step
- Use clear, consistent language with short names
- Reuse existing concepts; avoid inventing new ones
- Implement as you build — use a hard language (C) to test
- Test on other people's implementations
- Cross-test rapidly: others' clients against your servers
- Be prepared to throw out and restart
- Use constructs independent of programming language and OS
- Solve large problems in layers, each an independent specification

### Using ABNF

Abstract Syntax Notation Format (ABNF) provides a concise way to define message structures. ZeroMQ RFCs use ABNF for protocol specifications.

### The Cheap or Nasty Pattern

A design pattern for error handling: either the operation is cheap enough to retry freely, or it's nasty enough that you need explicit error protocols. Most ZeroMQ operations fall into "cheap" — just retry.

## Serializing Your Data

ZeroMQ carries frames of bytes. You choose the serialization format:

### Options

- **ZeroMQ framing** — multipart messages with length-specified frames (built-in, no encoding)
- **String messages** — zero-terminated strings, simple but limited to text
- **Protocol Buffers** — Google's binary serialization, strong schema support
- **MessagePack** — compact binary format, simpler than protobuf
- **JSON** — human-readable, good for debugging, slower and larger
- **Handwritten binary** — fastest, most control, most error-prone

### Choosing Abstraction Level

Higher abstraction (JSON, protobuf) → easier development, more overhead. Lower abstraction (handwritten binary) → maximum performance, more bugs. Choose based on your throughput requirements and team expertise.

## Transferring Files

For file transfer over ZeroMQ:
- Break files into chunks and send as separate messages
- Use multipart messages for chunk headers + data
- Implement credit-based flow control for nonblocking transfers
- Track completion with sequence numbers

## State Machines

Build protocol servers and clients as state machines. Each state defines what messages are expected and what transitions are valid. This makes protocols robust and easier to debug.

Example: a simple request-reply server state machine:
```
IDLE → (receive request) → WORKING → (send reply) → IDLE
IDLE → (receive heartbeat) → IDLE
WORKING → (timeout) → IDLE
```

## Authentication Using SASL

ZeroMQ 3.x+ supports security via ZAP (ZeroMQ Authentication Protocol) and SASL:

- **NULL** — no authentication (default, for trusted networks)
- **PLAIN** — username/password authentication
- **CURVE** — public key cryptography (recommended for production)

### CURVE Security

Each peer has a public/private key pair. The server stores authorized client public keys. ZeroMQ handles encryption and authentication transparently:

```c
//  Server setup
zmq_setsockopt (server, ZMQ_CURVE_SERVER, &enabled, sizeof (enabled));
zmq_setsockopt (server, ZMQ_ZAP_DOMAIN, "global", 6);

//  Client setup
zcert_t *client_cert = zcert_new ();
zmq_setsockopt (client, ZMQ_CURVE_PUBLICKEY, zcert_publickey (client_cert), 32);
zmq_setsockopt (client, ZMQ_CURVE_SECRETKEY, zcert_secretkey (client_cert), 32);
zmq_setsockopt (client, ZMQ_CURVE_SERVERKEY, server_public_key, 32);
```

ZAP runs as a separate process that the ZeroMQ library calls to authenticate connections. It reads policy from a configuration file or implements custom logic.

## FileMQ — Large-Scale File Publishing

FileMQ is a protocol and implementation for reliable file distribution over ZeroMQ:

- Publishes entire directory trees
- Handles late joiners (catch-up mechanism)
- Credit-based flow control (nonblocking)
- Delivery notifications
- Symbolic link support
- Recovery from interruptions

### Architecture

```
Publisher → FileMQ server → FileMQ clients
```

The publisher monitors a directory tree and publishes changes. Clients maintain a local copy and sync incrementally. Uses pub-sub for change notifications and request-reply for file content transfer.

## Getting an Official Port Number

For protocols built on ZeroMQ, you can register official port numbers with IANA. This makes your protocol more legitimate and easier to deploy behind firewalls.
