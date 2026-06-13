# Socket Types and Patterns

## The Socket API

Sockets have a life in four parts, like BSD sockets:

1. **Creating and destroying**: `zmq_socket()` to create, `zmq_close()` to destroy
2. **Configuring**: `zmq_setsockopt()` to set options, `zmq_getsockopt()` to check them
3. **Plugging into topology**: `zmq_bind()` (server side) and `zmq_connect()` (client side)
4. **Carrying data**: `zmq_msg_send()` / `zmq_send()` and `zmq_msg_recv()` / `zmq_recv()`

Sockets are always void pointers. Messages are structures — you pass addresses of messages to send/recv functions. Mnemonic: "In ZeroMQ, all your sockets belong to us", but messages are things you own in your code.

## Plugging Sockets into the Topology

To create a connection between two nodes, use `zmq_bind()` on one side and `zmq_connect()` on the other. The general rule:

- **Bind** = server, sitting on a well-known network address
- **Connect** = client, with unknown or arbitrary addresses

ZeroMQ connections differ from classic TCP:

- They go across arbitrary transports (inproc, ipc, tcp, pgm, epgm)
- One socket may have many outgoing and many incoming connections
- There is no `zmq_accept()` — bound sockets automatically accept connections
- Network connections happen in the background with automatic reconnection
- Application code cannot work with connections directly; they are encapsulated under the socket

You can start a client before the server. When the client does `zmq_connect()`, the connection exists and it can write messages immediately. When the server later does `zmq_bind()`, ZeroMQ starts delivering queued messages.

A server can bind to many endpoints using a single socket:

```c
zmq_bind (socket, "tcp://*:5555");
zmq_bind (socket, "tcp://*:9999");
zmq_bind (socket, "inproc://somename");
```

With most transports you cannot bind to the same endpoint twice. The ipc transport does allow one process to bind to an endpoint already used by another — meant for crash recovery.

## Transport Comparison

**tcp** — Disconnected TCP transport. Elastic, portable, fast enough for most cases. Does not require the endpoint to exist before connecting. Clients and servers can connect and bind at any time.

**ipc** — Disconnected inter-process transport. Not yet available on Windows. Use `.ipc` extension by convention. On UNIX, create endpoints with appropriate permissions so processes under different user IDs can share them.

**inproc** — Connected inter-thread signaling transport. Much faster than tcp or ipc. Server must bind before any client connects (fixed in ZeroMQ v4.0+).

**pgm / epgm** — Multicast transports for high fan-out ratios where 1-to-N unicast is impossible. PGM (Pragmatic General Multicast) and EPGM (Extended PGM).

## Sending and Receiving Messages

ZeroMQ's I/O model differs from classic TCP:

- Sockets carry messages (like UDP), not byte streams (like TCP)
- I/O happens in background threads — messages arrive in local input queues
- `zmq_send()` does not actually send the message to the connection. It queues the message for the I/O thread to send asynchronously
- `zmq_send()` does not block except in some exception cases
- The message is not necessarily sent when `zmq_send()` returns

Two APIs exist for messages:

1. **Simple API**: `zmq_send()` / `zmq_recv()` — one-liners, but `zmq_recv()` truncates to buffer size
2. **Rich API**: `zmq_msg_init()`, `zmq_msg_init_size()`, `zmq_msg_init_data()`, `zmq_msg_send()`, `zmq_msg_recv()`, `zmq_msg_close()` — richer but more complex

## Core Messaging Patterns

### Request-Reply (REQ/REP)

Connects clients to services. Remote procedure call and task distribution pattern. REQ sends a request, waits for a reply. REP receives a request, sends a reply. Strict alternation: send, recv, send, recv.

### Pub-Sub (PUB/SUB)

Connects publishers to subscribers. Data distribution pattern. PUB sends messages to all connected SUB sockets. SUB can filter by topic prefix. No back-chatter — subscribers cannot tell publishers anything. Publishers cannot know when subscribers connect or disconnect.

### Pipeline (PUSH/PULL)

Fan-out/fan-in pattern for parallel task distribution and collection. PUSH distributes messages in round-robin to multiple PULL sockets. Multiple PUSH sockets can feed a single PULL socket, which fair-queues from all inputs.

### Exclusive Pair (PAIR/PAIR)

Connects two sockets exclusively. For connecting two threads in a process. Not for general-purpose use between arbitrary nodes.

## Socket Type Combinations

Valid connect-bind pairs (either side can bind):

- PUB and SUB
- REQ and REP
- REQ and ROUTER (REQ inserts an extra null frame)
- DEALER and REP (REP assumes a null frame)
- DEALER and ROUTER
- DEALER and DEALER
- ROUTER and ROUTER
- PUSH and PULL
- PAIR and PAIR

Any other combination produces undocumented and unreliable results.

## DEALER and ROUTER Sockets

DEALER and ROUTER are the advanced sockets that replace REQ/REP in complex patterns:

- **DEALER** — Like REQ without the strict alternation requirement. Can send and receive freely. Strips identity frames from incoming messages and prepends them to outgoing messages.
- **ROUTER** — Routes messages based on identity addresses. Every message received has a leading identity frame (or frames for multi-hop). Every message sent must start with an identity address frame followed by the body.

## Multipart Messages

ZeroMQ supports multipart messages — messages composed of multiple frames. Use `zmq_msg_send()` with `ZMQ_SNDMORE` flag for all frames except the last:

```c
zmq_msg_init_size (&part1, 5);
memcpy (zmq_msg_data (&part1), "Hello", 5);
zmq_msg_send (&socket, &part1, ZMQ_SNDMORE);

zmq_msg_init_size (&part2, 5);
memcpy (zmq_msg_data (&part2), "World", 5);
zmq_msg_send (&socket, &part2, 0);  // no SNDMORE = last frame
```

## I/O Threads

One I/O thread (for all sockets) is sufficient for most applications. General rule: one I/O thread per gigabyte of data in or out per second.

```c
int io_threads = 4;
void *context = zmq_ctx_new ();
zmq_ctx_set (context, ZMQ_IO_THREADS, io_threads);
assert (zmq_getsockopt (context, ZMQ_IO_THREADS) == io_threads);
```

If using ZeroMQ for inter-thread communications only (no external socket I/O), you can set I/O threads to zero.

## High-Water Marks (HWM)

Each socket has a high-water mark that limits the number of pending messages. When HWM is reached, `zmq_send()` will either block or fail depending on the `ZMQ_SNDMORE` and socket options. This protects against memory overflow when a slow consumer cannot keep up.

Set via `zmq_setsockopt(socket, ZMQ_SNDHWM, &value, sizeof(value))` for send side, or `zmq_setsockopt(socket, ZMQ_RCVHWM, &value, sizeof(value))` for receive side.

## Built-In Proxy Function

ZeroMQ has a built-in proxy that forwards messages between sockets:

```c
zmq_proxy (frontend, backend, capture);
```

This creates a simple forwarder. With DEALER-ROUTER sockets it implements load balancing. With PUB-SUB it implements pub-sub forwarding. The capture socket (optional) receives copies of all messages for monitoring.

## Zero-Copy

ZeroMQ supports zero-copy message sending via `zmq_send()` with file descriptors. This allows transferring large data without copying it into user-space buffers:

```c
zmq_msg_init (&msg);
zmq_sendfd (socket, &msg, fd);
```

The receiving side uses `zmq_recvfd()` to get the file descriptor.
