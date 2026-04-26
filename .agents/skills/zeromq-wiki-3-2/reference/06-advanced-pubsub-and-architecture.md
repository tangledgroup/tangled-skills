# Advanced Pub-Sub and Architecture

## Pros and Cons of Pub-Sub

PUB sends each message to "all of many", whereas PUSH and DEALER rotate messages to "one of many". You cannot simply replace PUSH with PUB or vice versa.

Pub-sub is aimed at scalability — large volumes of data sent rapidly to many recipients. To achieve this, pub-sub eliminates back-chatter:

- Publishers cannot tell when subscribers are connected
- Subscribers cannot control the publisher's message rate
- Publishers cannot detect when subscribers disappear

This means ZeroMQ pub-sub will lose messages when a subscriber is connecting, when network failures occur, or if the subscriber cannot keep up. The upside is simplicity and clean mapping to multicast protocols.

## Pub-Sub Tracing (Espresso Pattern)

Monitor a pub-sub network by adding a trace subscriber that receives copies of all messages:

```c
// Publisher sends to both production SUB and trace SUB
zmq_send (pub_socket, topic_msg, ZMQ_SNDMORE);
zmq_send (pub_socket, data_msg, 0);

// Trace subscriber uses XPUB/XSUB proxy with capture socket
zmq_proxy (frontend, backend, capture);
// Messages flowing through the proxy are also sent to 'capture'
```

## Last Value Caching

For subscribers that join late, a last-value cache ensures they get the most recent state for each topic. Implemented by maintaining a cache of the last message per topic and replaying it when new subscribers connect:

```c
// On XPUB socket, subscription events are received
zmq_msg_init (&event);
zmq_msg_recv (xpub_socket, &event, 0);

// First byte: 0x01 = subscribe, 0x00 = unsubscribe
if (zmq_msg_data (&event)[0] == 0x01) {
    // Replay last cached value for this topic
    char *topic = (char *)zmq_msg_data (&event) + 1;
    send_cached_value (subscriber, topic);
}
```

## Slow Subscriber Detection (Suicidal Snail Pattern)

Detect and disconnect slow subscribers to protect the publisher:

```c
// Publisher monitors subscriber high-water marks
// When a subscriber's queue fills up, detect and disconnect
uint64_t hwm;
size_t optlen = sizeof (uint64_t);
zmq_getsockopt (pub_socket, ZMQ_SNDHWM, &hwm, &optlen);

// If approaching HWM, the publisher should consider dropping slow subscribers
```

## High-Speed Subscribers (Black Box Pattern)

For high-throughput subscribers that process messages asynchronously:

1. Subscriber receives messages into a local queue
2. Background thread processes messages from the queue
3. Main thread continues receiving without blocking

This decouples receive rate from processing rate, preventing message loss due to slow processing.

## Reliable Pub-Sub (Clone Pattern)

Builds a shared key-value store using pub-sub for state distribution:

1. **Centralized vs Decentralized**: Centralized has one server distributing state; decentralized uses peer-to-peer sync
2. **Key-value representation**: State is represented as key-value pairs, sent as pub-sub messages with topic = key
3. **Out-of-band snapshot**: New clients request a full snapshot via a separate REQ/REP channel
4. **Republishing updates**: Clients can republish state changes to propagate updates
5. **Subtree support**: Hierarchical keys allow partial subscriptions
6. **Ephemeral values**: Time-to-live on values for automatic expiration

The Clone pattern combines:
- PUB/SUB for incremental state distribution
- REQ/REP for initial snapshot transfer
- Binary Star for server reliability

## Message-Oriented Pattern for Elastic Design

Steps for designing with ZeroMQ:

1. **Internalize the semantics** — Understand what each socket type does
2. **Draw a rough architecture** — Sketch the topology
3. **Decide on contracts** — Define message formats and protocols
4. **Write a minimal end-to-end solution** — Get something working
5. **Solve one problem and repeat** — Iterate, adding reliability, performance, etc.

## Unprotocols

ZeroMQ community uses "unprotocols" — informal protocol specifications that are precise enough to implement but flexible enough to evolve:

- Use ABNF (Augmented Backus-Naur Form) for formal grammar
- Define message frames clearly
- Specify error handling
- Version protocols explicitly
- Start simple, add complexity only when needed

## Serializing Your Data

ZeroMQ carries binary blobs — serialization is your responsibility. Options:

- **Handwritten binary**: Maximum performance, most work
- **Protocol Buffers / FlatBuffers**: Code generation, cross-language
- **MessagePack / CBOR**: Compact binary, no code generation needed
- **JSON**: Human-readable, slower, larger
- **ZPL format**: ZeroMQ's own configuration file format (RFC 4)

## Transferring Files

For file transfer over ZeroMQ:

1. Send file metadata (name, size, hash) as a multipart message
2. Stream file content in chunks
3. Verify with hash on receipt

For large-scale file publishing, use **FileMQ** — a publish-subscribe file service based on ZeroMQ that handles file stability, delivery notifications, symbolic links, and recovery for late joiners.

## State Machines

ZeroMQ applications naturally map to state machines:

- Each socket interaction changes state
- `zmq_poll()` drives the state machine by detecting which sockets have activity
- Use a reactor pattern (like CZMQ's `zloop`) to simplify event-driven code

```c
// Simple reactor pattern
typedef struct {
    void *socket;
    zmq_handler_t handler;
    void *arg;
} reactor_entry_t;

void run_reactor (reactor_entry_t *entries, int count) {
    zmq_pollitem_t items [count];
    for (int i = 0; i < count; i++) {
        items[i].socket = entries[i].socket;
        items[i].events = ZMQ_POLLIN;
    }
    
    while (true) {
        zmq_poll (items, count, -1);
        for (int i = 0; i < count; i++) {
            if (items[i].revents & ZMQ_POLLIN) {
                entries[i].handler (entries[i].socket, entries[i].arg);
            }
        }
    }
}
```

## Large-Scale Architecture Patterns

### Benevolent Tyrant

One central coordinator manages all workers. Simple to implement, but the coordinator is a single point of failure. Use with Binary Star pattern for reliability.

### Federation

Multiple clusters, each with its own coordinator. Clusters connect to a higher-level federation layer. Good for geographic distribution.

### Peering

Equal peers form a mesh network. No central coordination. More complex but more resilient. Zyre framework implements this pattern.

### Scattering and Gathering

Split work across multiple nodes (scatter), collect results (gather). Implemented with PUSH/PULL for scattering and PULL/PUSH for gathering.

## Getting Official Port Numbers

For production ZeroMQ applications, register port numbers with IANA. Common conventions:

- Use ports above 50000 for ephemeral connections
- Document well-known service ports in configuration
- Use environment variables for endpoint configuration
- Support both bind and connect directions where possible
