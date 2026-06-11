# Ecosystem and Bindings

## Project Structure

ZeroMQ is a collection of projects built around the core library:

**Core**: `libzmq` — The ZeroMQ core engine in C++, implementing ZMTP/3.1. Licensed under LGPL.

**Bindings**: ~50 individual projects creating higher-level APIs or mapping the low-level API into other languages. There are no "official" bindings — the community decides by usage and contribution.

**Reimplementations**: Native stacks that offer identical APIs and speak the same ZMTP protocol as libzmq:
- **JeroMQ** — Pure Java implementation of ZeroMQ
- **NetMQ** — 100% native C# implementation (derived from JeroMQ)

**High-level libraries**: Projects that build on bindings to provide higher abstractions.

## CZMQ — High-Level C Binding

CZMQ (`github.com/zeromq/czmq`) provides a high-level C API wrapping libzmq. Licensed under MPL 2.0.

Key modules:

- **zactor** — Simple actor framework for spawning background tasks
- **zauth** — Authentication for ZeroMQ security mechanisms
- **zbeacon** — LAN discovery and presence using UDP broadcasts
- **zcert / zcertstore** — CURVE security certificate management
- **zchunk** — Memory chunk operations
- **zclock** — Millisecond clocks and delays
- **zconfig** — Configuration file parsing (ZPL format, RFC 4)
- **zdigest** — Hashing functions (SHA-1)
- **zdir / zdir_patch / zfile** — File system operations
- **zframe** — Working with single message frames
- **zgossip** — Decentralized configuration management
- **zhash / zhashx** — Generic hash containers
- **ziflist** — Network interface enumeration
- **zlist / zlistx** — Generic list containers
- **zmsg** — Multipart message API
- **zsock** — High-level socket API
- **zstr** — String message helpers
- **zloop / zpoller** — Event loop and socket polling

### CZMQ Usage Example

```c
#include <czmq.h>

int main (void) {
    // High-level socket creation
    zsock_t *server = zsock_new_rep ("tcp://*:5555");
    
    while (!zsys_interrupted) {
        zstr_t *request = zstr_recv (server);
        printf ("Received: %s\n", zstr_str (request));
        zstr_send (server, "World");
        zstr_destroy (&request);
    }
    
    zsock_destroy (&server);
    return 0;
}
```

## Language Bindings

### PyZMQ (Python)

One of the first and most mature community projects. Provides both low-level (`zmq`) and high-level APIs with asyncio support:

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    socket.send(b"World")
```

### JeroMQ (Java)

Pure Java implementation — no JNI, no native library. Implements ZMTP 3.1 natively. Drop-in replacement for jzmq in many cases.

### cppzmq (C++)

Header-only C++ binding for libzmq. Provides type-safe wrappers:

```cpp
#include <zmq.hpp>

zmq::context_t context(1);
zmq::socket_t socket(context, zmq::socket_type::rep);
socket.bind("tcp://*:5555");

std::string request;
zmq::message_t msg;
socket.recv(&msg);
```

### Other Notable Bindings

- **rbzmq** — Ruby binding
- **php-zmq** — PHP extension
- **erlzmq** — Erlang binding
- **clrzmq** — CLR (.NET & Mono) binding
- **fszmq** — F# binding
- **lzmq** — Lua binding
- **cljzmq** — Clojure binding
- **zmtp** — ZMTP protocol reference implementations

## Zyre — Peer-to-Peer Framework

Zyre (`github.com/zeromq/zyre`) is an open-source framework for proximity-based peer-to-peer applications. It solves:

- **Discovery**: UDP beaconing to find peers on the local network
- **Presence**: Tracking when peers come and go
- **Connectivity**: Automatic peer-to-peer connections
- **Point-to-point messaging**: Direct messages between named peers
- **Group messaging**: Pub-sub to all peers in the cluster
- **Configuration**: Decentralized key-value store via gossip protocol

```c
#include <zyre.h>

zyre_t *node = zyre_new ();
zyre_set_name (node, "my-node");
zyre_start (node);

// Join a group
zyre_join (node, "my-group");

// Send message to group
zyre_whisper (node, "peer-name", "Hello");
zyre_shout (node, "my-group", "Broadcast");
```

## FileMQ — Publish-Subscribe File Service

FileMQ (`github.com/zeromq/filemq`) is a publish-subscribe file service based on ZeroMQ:

- Publishes files to subscribers
- Handles file stability and delivery notifications
- Supports symbolic links
- Recovery for late joiners
- Designed for large-scale content distribution

## RFC Project

The ZeroMQ RFC project (`github.com/zeromq/rfc`) contains formal specifications:

**Stable RFCs**:
- RFC 4: ZPL — Configuration file format
- RFC 21: CLASS — C Language Style for Scalability
- RFC 23: ZMTP 3.0 — Message Transport Protocol
- RFC 24: ZMTP NULL and PLAIN mechanisms
- RFC 25: ZMTP CURVE mechanism
- RFC 26: CurveZMQ specification
- RFC 27: ZAP — ZeroMQ Authentication Protocol
- RFC 28: REQ/REP socket semantics
- RFC 29: PUB/SUB socket semantics
- RFC 30: PUSH/PULL socket semantics
- RFC 31: PAIR socket semantics
- RFC 32: Z85 — Base85 encoding

**Draft RFCs**:
- RFC 33: ZHTTP — HTTP protocol for ZeroMQ
- RFC 34: SRPZMQ — Secure Remote Password
- RFC 35: FILEMQ protocol
- RFC 37: ZMTP (newer draft)
- RFC 38: ZMTP-GSSAPI
- RFC 46: DAFKA — Distributed Apache Kafka Alternative
- RFC 51: P2P — Peer-to-peer pattern

## Community and Process

ZeroMQ uses the **C4 process** (Collective Code Construction Contract) for contributions:

- No committers — only projects and contributors
- Patches are merged, not people
- Two independent approvals required for patch acceptance
- No branches — single trunk development
- Project owners can be replaced by community vote
- Licensing under LGPL for libzmq, MPL 2.0 for CZMQ

The ZeroMQ Guide (zguide.zeromq.org) provides comprehensive tutorials with examples in 28+ languages, covering basics through advanced distributed computing patterns.
