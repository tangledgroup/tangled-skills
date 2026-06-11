# Advanced Pub-Sub Patterns

## Pros and Cons of Pub-Sub

Pub-sub addresses multicast/group messaging. PUB sends each message to "all of many" (vs PUSH/DEALER which rotate to "one of many").

**Trade-offs for scalability:**
- No back-chatter — subscribers don't talk back to publishers
- Publishers can't tell when subscribers connect or disconnect
- Subscribers can't control publisher rate — full-speed only
- Maps cleanly to PGM multicast protocol (handled by network switch)

**Failure cases:**
- Subscribers join late → miss earlier messages
- Slow subscribers → queues build up and overflow
- Subscribers crash/restart → lose received data
- Network overload → data dropped (specifically for PGM)

## Pub-Sub Tracing — Espresso Pattern

Use `zmq_proxy()` with a capture socket to trace all messages flowing through a pub-sub network:

```c
//  Main thread sets up proxy with capture
void *xsub = zmq_socket (context, ZMQ_XSUB);
zmq_connect (xsub, "tcp://localhost:6000");
void *xpub = zmq_socket (context, ZMQ_XPUB);
zmq_bind (xpub, "tcp://*:6001");
void *capture = zmq_socket (context, ZMQ_PAIR);
zmq_bind (capture, "inproc://listener");

//  Start listener thread to read captured messages
//  ...

zmq_proxy (xsub, xpub, capture);
```

XPUB/XSUB are raw versions of PUB/SUB that expose subscription messages (subscribe/unsubscribe events) to the application. Useful for tracking subscriber state.

## Last Value Caching (LVC)

ZeroMQ 3.x+ supports `ZMQ_CONFLATE` socket option — the socket keeps only the last received message and sends it to new subscribers:

```c
void *publisher = zmq_socket (context, ZMQ_PUB);
int conflate = 1;
zmq_setsockopt (publisher, ZMQ_CONFLATE, &conflate, sizeof (conflate));
zmq_bind (publisher, "tcp://*:5556");
```

When a new subscriber connects, it immediately receives the last published message. Useful for status/telemetry data where only the latest value matters.

## Slow Subscriber Detection — Suicidal Snail Pattern

Subscribers that can't keep up with the publisher cause queue overflow and eventual message loss. The Suicidal Snail pattern has slow subscribers detect their own slowness and take action:

```c
//  Subscriber measures its throughput
uint64_t start = zclock_now ();
int count = 0;
while (1) {
    char *update = s_recv (subscriber);
    if (!update) break;
    count++;
    free (update);

    //  Check throughput every N messages
    if (count % CHECK_RATE == 0) {
        uint64_t elapsed = zclock_now () - start;
        if (elapsed > MAX_ELAPSED) {
            printf ("E: I am too slow, exiting\n");
            break;
        }
        start = zclock_now ();
        count = 0;
    }
}
```

## High-Speed Subscribers — Black Box Pattern

For very high message rates, use a pipeline architecture where subscribers run as separate processes connected via PUSH/PULL:

- Publisher sends to XPUB
- Proxy forwards to multiple subscriber processes
- Each subscriber process handles its own rate limiting
- Uses inproc transport for fastest internal communication

## Reliable Pub-Sub — Clone Pattern

The Clone pattern builds a shared key-value store using pub-sub for updates and request-reply for snapshots:

### Architecture

```
Client 1 ──┐
Client 2 ──┼── REQ/REP → Server (holds authoritative state)
Client 3 ──┘
              │
              ├── PUB → all clients (state updates)
```

1. Client connects and requests initial state snapshot via REQ/REP
2. Server sends full state snapshot
3. Server publishes incremental updates via PUB
4. Client applies updates to local copy

### Representing State as Key-Value Pairs

State is a set of key-value pairs organized in a tree structure. Keys use path-like notation (`/node/child/key`). Updates are sent as `[key] [value]` messages.

### Getting Out-of-Band Snapshot

When a new client joins:
1. Client sends snapshot request via REQ socket
2. Server replies with full state (all key-value pairs)
3. Client then subscribes to PUB for incremental updates

### Republishing Updates

Clients can act as relays — when they receive an update, they can republish it to other clients, creating a decentralized update mesh.

### Working with Subtrees

Clients can subscribe to subtrees using prefix matching:
```c
zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE, "/node1/", 7);
```

This receives all updates for keys starting with `/node1/`.

### Adding Binary Star for Reliability

Combine Clone pattern with Binary Star failover:
- Primary server holds authoritative state
- Backup server maintains synchronized copy
- On primary failure, backup takes over
- Clients reconnect to new primary

## Pub-Sub Message Envelopes

For routing pub-sub messages to specific handlers within an application, use multipart messages with a topic envelope:

```c
//  Publisher sends topic + content
zmq_send (publisher, "A", 1, ZMQ_SNDMORE);
zmq_send (publisher, "Content for topic A", 19, 0);

//  Subscriber filters on first frame
zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE, "A", 1);
```

## Using Reactors

For complex pub-sub servers handling multiple sockets and timeouts, use a reactor pattern (event loop) instead of manual polling. CZMQ provides `zloop` for this purpose:

```c
zloop_t *loop = zloop_new ();
zloop_reader (loop, subscriber, handle_subscription, NULL);
zloop_reader (loop, requester, handle_request, NULL);
zloop_timer (loop, HEARTBEAT_INTERVAL, 0, heartbeat_tick, NULL);
zloop_start (loop);
zloop_destroy (&loop);
```
