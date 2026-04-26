# Advanced Request-Reply Patterns

## The Reply Envelope

A reply envelope packages data with a return address without touching the data itself. This enables general-purpose intermediaries (proxies, brokers) that create, read, and remove addresses regardless of message payload.

The envelope formally consists of: zero or more reply addresses, followed by an empty frame (delimiter), followed by the message body (zero or more frames).

### Simple Envelope (REQ → REP)

REQ creates a minimal envelope: empty delimiter frame + message body (two frames total). REP strips the envelope up to and including the delimiter, saves it, and passes the body to the application.

```
REQ sends:  [empty delimiter] [message body]
REP sees:   [strips envelope] → delivers "Hello" to app
```

### Extended Envelope (with ROUTER-DEALER proxy)

When a ROUTER-DEALER proxy sits between REQ and REP, each ROUTER adds its connection identity as an address frame:

```
REQ sends via ROUTER-DEALER proxy to REP:
  [ROUTER identity] [empty delimiter] [message body]

REP strips entire envelope (identity + delimiter), saves it, delivers body.
On reply, REP wraps with saved envelope → DEALER forwards → ROUTER uses
identity frame to find the correct connection → REQ strips delimiter → app gets reply.
```

## Socket Types in Request-Reply

### REQ (Synchronous Client)

- Sends empty delimiter frame before message data
- Strict send-then-receive cycle (finite state machine)
- Load-balances across multiple peers (round-robin)
- Cannot initiate without receiving first after a send
- Returns `EFSM` error if used out of sequence

### REP (Synchronous Server)

- Reads and saves all identity frames up to empty delimiter
- Strict receive-then-send cycle
- Fair-queues from multiple peers
- Replies always go to the peer that made the last request

### DEALER (Asynchronous Client)

- Oblivious to reply envelope — treats it as multipart message
- Distributes sent messages among all connections (like PUSH)
- Fair-queues received messages from all connections (like PULL)
- Can talk to multiple REP servers asynchronously
- When talking to REP: must send empty frame with MORE flag first, then body

### ROUTER (Asynchronous Server)

- Creates unique identities for each connection
- Prepends identity frame to every received message
- Uses first frame of sent message as routing identity
- Asynchronous — can handle multiple clients in parallel
- Maintains hash table mapping identities to connections

## Request-Reply Combinations

### REQ → REP
Basic synchronous pattern. Client must initiate. Server cannot respond without prior request (`EFSM` error).

### DEALER → REP
Asynchronous client to synchronous server. DEALER must emulate the envelope:
```c
//  Sending from DEALER to REP
zmq_send (dealer, "", 0, ZMQ_SNDMORE);  //  Empty frame with MORE
zmq_send (dealer, "Hello", 5, 0);        //  Body

//  Receiving at DEALER from REP
char buffer [256];
int size = zmq_recv (dealer, buffer, 255, 0);
if (size == 0) {
    //  Empty delimiter — receive actual body
    size = zmq_recv (dealer, buffer, 255, 0);
}
```

### REQ → ROUTER
Asynchronous server to synchronous client. ROUTER reads identity frame, empty frame, then data frame. Can process multiple clients in parallel.

```c
//  ROUTER server processing REQ clients
while (1) {
    //  Get next client identity
    char *identity = s_recv (router);
    //  Skip empty delimiter
    char *delimiter = s_recv (router);
    free (delimiter);
    //  Get request body
    char *request = s_recv (router);

    //  Send reply back to same client
    s_sendmore (router, identity);
    s_sendmore (router, "");           //  Empty delimiter
    s_send (router, "World");
    free (identity);
    free (request);
}
```

### DEALER → ROUTER
Fully asynchronous. Both sides handle envelopes manually. Most flexible combination.

### DEALER → DEALER and ROUTER → ROUTER
Valid for building multi-hop proxy chains.

### Invalid Combinations
- REQ → REQ, REQ → DEALER, REP → REP, REP → ROUTER

## Identities and Addresses

ROUTER invents a random identity for each connection (5 bytes in ZeroMQ 3.x+, UUID in 2.x). You can set a custom identity:

```c
zmq_setsockopt (socket, ZMQ_IDENTITY, "Client-A", 8);
```

When receiving on ROUTER, the first frame is always the peer's identity. Use it as a hash key to track peers.

## Load Balancing Pattern

ROUTER broker distributes work to workers in round-robin fashion:

### ROUTER Broker + REQ Workers
```c
//  Broker (load balancer)
void *backend = zmq_socket (context, ZMQ_ROUTER);
zmq_bind (backend, "tcp://*:5556");

//  Worker
void *worker = zmq_socket (context, ZMQ_REQ);
zmq_connect (worker, "tcp://localhost:5556");
```

### ROUTER Broker + DEALER Workers
DEALER workers are more efficient — no envelope overhead.

## Asynchronous Client/Server Pattern

Using DEALER on both sides for full async communication:

```c
//  Async client
void *client = zmq_socket (context, ZMQ_DEALER);
zmq_setsockopt (client, ZMQ_IDENTITY, "Client-1", 8);
zmq_connect (client, "tcp://localhost:5555");

//  Async server
void *server = zmq_socket (context, ZMQ_ROUTER);
zmq_bind (server, "tcp://*:5555");

//  Server loop — poll for requests
while (1) {
    //  Receive client identity
    char *identity = s_recv (server);
    //  Receive request
    char *request = s_recv (server);

    //  Process and reply
    s_sendmore (server, identity);
    s_send (server, "Response");

    free (identity);
    free (request);
}
```

## Inter-Broker Routing

For scaling across clusters, brokers federate using a hierarchical topology:

- Each cluster has a frontend ROUTER (accepts client requests) and backend DEALER (connects to workers)
- Clusters connect via UP/DOWN sockets between leaf and cloud brokers
- Leaf broker connects to local workers and forwards unknown requests to cloud
- Cloud broker federates multiple leaf brokers

This creates a scalable, fault-tolerant architecture where each cluster can operate independently while still being part of the larger network.

## Building a High-Level API

The CZMQ library (czmq) provides a higher-level API wrapping raw ZeroMQ:

- `zsock_new_req()`, `zsock_new_rep()` — create configured sockets
- `zstr_send()`, `zstr_recv()` — send/receive string messages
- `zframe_send()`, `zframe_recv()` — send/receive single frames
- `zmsg_send()`, `zmsg_recv()` — send/receive multipart messages
- `zpoller_new()` — convenient polling across multiple sockets

These abstractions reduce boilerplate and common errors while maintaining ZeroMQ's performance characteristics.
