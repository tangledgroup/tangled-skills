# Sockets and Patterns

## The Socket API

ZeroMQ sockets have a life in four parts:

1. **Creating/destroying** — `zmq_socket()`, `zmq_close()`
2. **Configuring** — `zmq_setsockopt()`, `zmq_getsockopt()`
3. **Plugging into topology** — `zmq_bind()`, `zmq_connect()`
4. **Carrying data** — `zmq_msg_send()`, `zmq_msg_recv()` (or `zmq_send()`/`zmq_recv()` for byte arrays)

Sockets are always void pointers. Messages are structures (`zmq_msg_t`). You pass sockets as-is, but pass addresses of messages in all message functions.

### Bind vs Connect

- **`zmq_bind()`** — the server sits on a well-known endpoint
- **`zmq_connect()`** — the client connects to that endpoint

ZeroMQ connections differ from TCP:
- One socket may have many outgoing and incoming connections
- No `zmq_accept()` — bound sockets auto-accept
- Network connection happens in background with automatic reconnection
- Client can `connect()` before server `bind()` — messages queue until connected
- A single socket can bind to multiple endpoints across different transports

```c
zmq_bind (socket, "tcp://*:5555");
zmq_bind (socket, "tcp://*:9999");
zmq_bind (socket, "inproc://somename");
```

## Transports

- **`tcp`** — disconnected TCP, elastic, portable, fast enough for most cases. Works across machines.
- **`ipc`** — inter-process, disconnected like tcp. Does not work on Windows. Use `.ipc` extension by convention.
- **`inproc`** — in-process (inter-thread), connected signaling transport. Much faster than tcp/ipc. Before ZeroMQ 4.0: server must bind before client connects.
- **`pgm`/`epgm`** — multicast transports for high fan-out ratios.

## Core Messaging Patterns

### Request-Reply (REQ + REP)

Connects clients to services. RPC and task distribution pattern. REQ sends, then waits for reply (strict send/receive ping-pong). REP reads request, sends reply (strict recv/send cycle).

```c
//  Server
void *responder = zmq_socket (context, ZMQ_REP);
zmq_bind (responder, "tcp://*:5555");

//  Client
void *requester = zmq_socket (context, ZMQ_REQ);
zmq_connect (requester, "tcp://localhost:5555");
```

### Pub-Sub (PUB + SUB)

Data distribution pattern. Publisher sends to all subscribers. Subscriber sets filters with `ZMQ_SUBSCRIBE`. Messages sent before subscriber connects are lost (no back-chatter).

```c
//  Publisher
void *publisher = zmq_socket (context, ZMQ_PUB);
zmq_bind (publisher, "tcp://*:5556");

//  Subscriber
void *subscriber = zmq_socket (context, ZMQ_SUB);
zmq_connect (subscriber, "tcp://localhost:5556");
zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE, "10001", 5);
```

### Pipeline (PUSH + PULL)

Fan-out/fan-in pattern for parallel task distribution. PUSH distributes messages to connected PULL sockets in round-robin fashion. PULL fair-queues from all connected PUSH sockets.

```c
//  Ventilator (pushes work)
void *sender = zmq_socket (context, ZMQ_PUSH);
zmq_bind (sender, "tcp://*:5555");

//  Worker (pulls work)
void *receiver = zmq_socket (context, ZMQ_PULL);
zmq_connect (receiver, "tcp://localhost:5555");
```

### Exclusive Pair (PAIR + PAIR)

Connects two sockets exclusively. For inter-thread communication within a process.

## Valid Socket Combinations

- PUB ↔ SUB
- REQ ↔ REP
- REQ ↔ ROUTER (REQ inserts extra null frame)
- DEALER ↔ REP (REP assumes null frame)
- DEALER ↔ ROUTER
- DEALER ↔ DEALER
- ROUTER ↔ ROUTER
- PUSH ↔ PULL
- PAIR ↔ PAIR

Any other combination produces undocumented and unreliable results.

## Working with Messages

### Simple API (byte arrays)

```c
//  Send
zmq_send (socket, "Hello", 5, 0);

//  Receive (truncates to buffer size — use carefully)
char buffer [256];
int size = zmq_recv (socket, buffer, 255, 0);
```

### Message API (zmq_msg_t)

For arbitrary message sizes:

```c
zmq_msg_t message;
zmq_msg_init (&message);
zmq_msg_recv (socket, &message, 0);
//  Access content: zmq_msg_data(), zmq_msg_size()
zmq_msg_close (&message);
```

Rules for `zmq_msg_t`:
- Create with `zmq_msg_init()` or `zmq_msg_init_size()`
- Release with `zmq_msg_close()` — drops a reference
- After sending, ØMQ clears the message (size set to zero)
- Cannot send same message twice
- For copying: use `zmq_msg_copy()` (copies reference, not data)
- Do not use `zmq_msg_init_data()` (zero-copy) unless you've read the man pages carefully

### Multipart Messages

Multipart messages are series of frames with a "more" bit. Send each frame with `ZMQ_SNDMORE` flag except the last:

```c
//  Send multipart message (two frames)
zmq_send (socket, "Hello", 5, ZMQ_SNDMORE);
zmq_send (socket, "World", 5, 0);

//  Receive multipart message
while (1) {
    zmq_msg_t message;
    zmq_msg_init (&message);
    zmq_msg_recv (socket, &message, 0);
    //  Process frame...
    if (!zmq_msg_more (&message))
        break;
    zmq_msg_close (&message);
}
```

Lexicon: a message can be one or more parts (frames). Each part is a `zmq_msg_t`. ZeroMQ delivers all parts or none.

## Handling Multiple Sockets

### Using zmq_poll

```c
zmq_pollitem_t items [] = {
    { .socket = socket1, .fd = 0, .events = ZMQ_POLLIN, .revents = 0 },
    { .socket = socket2, .fd = 0, .events = ZMQ_POLLIN, .revents = 0 }
};
zmq_poll (items, 2, -1);  //  Wait indefinitely

if (items [0].revents & ZMQ_POLLIN) {
    //  socket1 has input
}
if (items [1].revents & ZMQ_POLLIN) {
    //  socket2 has input
}
```

### Nonblocking Reads (ZMQ_DONTWAIT)

```c
while (1) {
    int size = zmq_recv (socket, msg, 255, ZMQ_DONTWAIT);
    if (size != -1) {
        //  Process message
    } else {
        break;  //  EAGAIN — no more messages
    }
}
s_sleep (1);  //  No activity, sleep briefly
```

## Intermediaries and Proxies

ZeroMQ's built-in proxy function bridges two sockets:

```c
void *frontend = zmq_socket (context, ZMQ_XSUB);
zmq_connect (frontend, "tcp://localhost:5559");
void *backend = zmq_socket (context, ZMQ_XPUB);
zmq_bind (backend, "tcp://*:5560");
zmq_proxy (frontend, backend, NULL);
```

With a capture socket for tracing (Espresso pattern):
```c
zmq_proxy (frontend, backend, capture_socket);
```

## High-Water Marks (HWM)

HWM protects against memory overflow by limiting internal queues:

```c
int hwm = 1000;
zmq_setsockopt (socket, ZMQ_SNDHWM, &hwm, sizeof (hwm));
zmq_setsockopt (socket, ZMQ_RCVHWM, &hwm, sizeof (hwm));
```

When the output queue hits HWM, `zmq_send()` blocks (or drops messages with `ZMQ_DONTROUTABLE` in newer versions).

## Multithreading with ZeroMQ

- Contexts are shared across threads — create one context per process
- Sockets are NOT thread-safe — do not share sockets between threads
- Move a socket to another thread using `zmq_socket()` in the new thread
- Use PAIR sockets over `inproc` transport for signaling between threads

```c
//  Thread signaling with PAIR
void *signal = zmq_socket (context, ZMQ_PAIR);
zmq_bind (signal, "inproc://signal");
//  In another thread:
void *receiver = zmq_socket (context, ZMQ_PAIR);
zmq_connect (receiver, "inproc://signal");
```

## Handling Errors and Interrupts

- `zmq_errno()` returns the last error code
- `EAGAIN` — no message available (with `ZMQ_DONTWAIT`)
- `ETERM` — context was terminated
- `EFSM` — bad state for REQ/REP socket (e.g., send without prior receive)
- Handle Ctrl-C by setting up signal handler and checking with `zmq_poll()` timeout

## Zero-Copy

The `zmq_msg_init_data()` API allows zero-copy message passing, where the message data lives in your application's memory. This is advanced usage — understand normal messaging thoroughly before attempting zero-copy.
