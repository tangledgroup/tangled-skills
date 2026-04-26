# Reliable Messaging Patterns

## What is Reliability?

Reliability in ZeroMQ means handling failures gracefully: crashed peers, network partitions, slow consumers, and message loss. ZeroMQ's core patterns provide basic reliability (automatic reconnection, message queuing), but production systems need higher-level patterns built on top.

## The Lazy Pirate Pattern

Client-side reliability with retry logic. The client sends a request and waits for a reply with a timeout. If no reply arrives, it retries up to a maximum number of attempts.

```c
#define REPLY_WAIT 2000      // msecs
#define MAX_RETRIES 3

void *requester = zmq_socket (context, ZMQ_REQ);
zmq_connect (requester, "tcp://server:5555");

int retries = 0;
while (retries < MAX_RETRIES) {
    zmq_send (requester, "Hello", 5, 0);
    
    // Poll for reply with timeout
    struct zmq_pollitem_t items[] = { { requester, 0, ZMQ_POLLIN, 0 } };
    int rc = zmq_poll (items, 1, REPLY_WAIT * ZMQ_POLL_MSEC);
    
    if (rc > 0) {
        char buffer [255];
        zmq_recv (requester, buffer, sizeof (buffer), 0);
        // Process reply
        break;
    }
    
    retries++;
    fprintf (stderr, "Retry %d...\n", retries);
}
```

## The Simple Pirate Pattern

Server-side reliability using load balancing. Multiple workers connect to a single server using DEALER sockets. The server uses `zmq_poll()` to detect which workers are responsive and routes requests only to available workers.

Key insight: ROUTER sockets automatically detect when a worker disconnects (the pipe closes). When the worker reconnects, it gets a new identity, and the ROUTER creates a new pipe for it.

## The Paranoid Pirate Pattern

Adds heartbeating to detect crashed peers that don't close connections cleanly. Both client and server send periodic heartbeat messages:

```c
// Server sends heartbeat to all workers
while (true) {
    zmq_pollitem_t items[] = {
        { frontend, 0, ZMQ_POLLIN, 0 },
        { backend, 0, ZMQ_POLLIN, 0 }
    };
    
    // Handle heartbeats and regular messages
    // If no heartbeat received within threshold, consider peer dead
}
```

Heartbeat strategies:

- **One-way heartbeats**: Server sends pings, workers respond
- **Ping-pong heartbeats**: Both sides send and expect heartbeats
- **Threshold-based detection**: If N heartbeats missed, declare peer dead

## The Majordomo Pattern (MDP)

A service-oriented reliable queuing protocol. Provides:

- Service registration and discovery
- Request routing with worker load balancing
- Worker health monitoring via heartbeating
- Clean worker lifecycle management
- Protocol versioning

The Majordomo broker sits between clients and workers, managing the full request-reply lifecycle. Clients send requests to the broker; the broker routes to available workers and returns replies to the correct client.

Key protocol messages:

- **HELO** — Worker registers with broker
- **READY** — Worker signals it's ready for work
- **REPLY** — Worker sends reply (with envelope)
- **PIGGY** — Heartbeat piggybacked on REPLY
- **HELLO** — Client introduces itself to broker
- **REQUEST** — Client sends request
- **REPlying** — Broker forwards worker reply to client

## The Titanic Pattern

Disk-based disconnected reliability. Messages are persisted to disk before being sent, allowing recovery after crashes:

```c
// Write message to spool file before sending
FILE *spool = fopen ("spool.dat", "a");
fprintf (spool, "%s\n", message);
fflush (spool);

// Send via ZeroMQ
zmq_send (socket, message, strlen(message), 0);

// On recovery, replay spooled messages
```

Use cases: financial transactions, order processing, any scenario where message loss is unacceptable.

## The Binary Star Pattern

Primary-backup server failover. Two servers form a pair — one active, one standby. They exchange heartbeats over a PAIR connection. If the active server crashes, the standby takes over.

Preventing split-brain: Use a shared resource (file lock, database row) as an arbitrator. Only one server can hold the lock at a time.

```c
// Binary star state machine
typedef enum {
    STAR_SLEEPING,   // Standby, waiting for partner
    STAR_WORKING,    // Active, serving requests
    STAR_LEAVING     // Shutting down gracefully
} star_state_t;
```

## The Freelance Pattern

Brokerless reliable request-reply. Workers maintain a list of known clients and retry failed requests directly without a central broker:

- **Model 1**: Simple retry with failover — try next client in list
- **Model 2**: Shotgun approach — broadcast to all known clients
- **Model 3**: Complex tracking — maintain state per client per request

## Heartbeating Best Practices

- Set heartbeat interval to 1/3 of the expected timeout
- Use at least 3 missed heartbeats before declaring a peer dead
- Account for network latency and load when setting thresholds
- Implement graceful shutdown to avoid false heartbeating failures
- Consider using ZMQ_IMMEDIATE socket option to wait until all peers are connected

## Error Handling

**ETERM**: When `zmq_ctx_destroy()` is called, all subsequent operations on sockets in that context return ETERM. Check for this and handle gracefully:

```c
ssize_t bytes = zmq_recv (socket, buffer, sizeof(buffer), 0);
if (bytes == -1 && errno == ETERM) {
    // Context was destroyed, clean up
    break;
}
```

**EINTR**: Interrupted system calls. ZeroMQ handles this internally in most cases, but be aware when using `zmq_poll()` with very short timeouts.

**ENOTSUP**: Operation not supported by socket type (e.g., receiving on a PUB socket).

## Memory Leak Detection

ZeroMQ can report memory leaks via the `ZMQ_MAXMSGS` and `ZMQ_MESSAGE_SIZE` statistics. Use `zmq_getsockopt()` to monitor socket state:

```c
uint64_t msgs_in, msgs_out;
size_t optlen = sizeof (uint64_t);
zmq_getsockopt (socket, ZMQ_MSGS_IN_PROGRESS, &msgs_in, &optlen);
```

Clean shutdown sequence:

1. Stop sending messages
2. Close all sockets (`zmq_close()`)
3. Destroy context (`zmq_ctx_destroy()`)
4. Check for lingering messages via socket statistics
