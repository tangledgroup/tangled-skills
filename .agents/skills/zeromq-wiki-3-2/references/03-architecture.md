# ZeroMQ Internal Architecture

This reference covers the internal architecture of libzmq, including threading model, I/O threads, message scheduling, pipes, and object trees. Understanding internals helps with debugging, performance tuning, and writing bindings.

## Overview

ZeroMQ is designed to be:
- **Asynchronous**: All I/O is non-blocking, handled by background threads
- **Thread-safe**: Context is thread-safe, sockets are not (unless ZMQ_THREAD_SAFE)
- **Scalable**: Handles thousands of connections with minimal resources
- **Portable**: Works on Windows, Linux, macOS, and other platforms

## Threading Model

### Context and Socket Ownership

```c
// Context is shared across threads
void *context = zmq_init(1);

// Thread 1: Creates and owns socket1
void *socket1 = zmq_socket(context, ZMQ_PUSH);

// Thread 2: Creates and owns socket2
void *socket2 = zmq_socket(context, ZMQ_PULL);

// NEVER share sockets between threads!
// DO share context between threads
```

### Rules

1. **Context is thread-safe**: Multiple threads can call `zmq_socket()` on same context
2. **Sockets are NOT thread-safe**: Each socket must be used by exactly one thread
3. **One socket per thread**: Simplest pattern is one socket per worker thread
4. **Close before exit**: Always `zmq_close()` before thread terminates

### Multi-threaded Example

```c
#include <pthread.h>
#include <czmq.h>

typedef struct {
    void *context;
    void *socket;
} worker_args_t;

void *worker_thread(void *arg) {
    worker_args_t *args = (worker_args_t *) arg;
    void *socket = args->socket;
    
    // This thread exclusively owns this socket
    while (1) {
        zmsg_t *message = zmsg_recv(socket);
        // Process message...
        zmsg_destroy(&message);
    }
    
    zmq_close(socket);  // Clean up before exit
    return NULL;
}

int main(void) {
    void *context = zmq_init(1);
    
    // Create worker threads
    pthread_t workers[4];
    worker_args_t args[4];
    
    for (int i = 0; i < 4; i++) {
        args[i].context = context;
        args[i].socket = zmq_socket(context, ZMQ_PULL);
        zmq_connect(args[i].socket, "tcp://localhost:5557");
        
        pthread_create(&workers[i], NULL, worker_thread, &args[i]);
    }
    
    // Distributor in main thread
    void *distributor = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(distributor, "tcp://*:5557");
    
    // Send tasks...
    
    zmq_close(distributor);
    
    // Wait for workers and terminate context
    for (int i = 0; i < 4; i++) {
        pthread_join(workers[i], NULL);
    }
    
    zmq_term(context);
    return 0;
}
```

---

## I/O Threads

ZeroMQ uses background I/O threads to handle socket operations asynchronously.

### How It Works

1. **Application thread**: Calls `zmq_send()` or `zmq_recv()`
2. **I/O thread**: Actually performs network I/O
3. **Event loop**: Uses select/epoll/kqueue/ioctl based on platform

### Configuring I/O Threads

```c
// Default: 1 I/O thread
void *context = zmq_init(1);

// Custom: 4 I/O threads for high connection count
void *context = zmq_init(4);
```

### When to Increase I/O Threads

- Many connections (> 1000)
- High message rate (> 100K msg/sec)
- Multiple network interfaces
- Mixed TCP and IPC transports

### I/O Thread Behavior

Each I/O thread:
- Polls sockets for activity using platform-specific mechanism
- Accepts incoming connections
- Sends queued messages
- Receives incoming messages
- Handles reconnection logic
- Performs heartbeat/keepalive

---

## Object Trees

ZeroMQ uses a tree of objects to manage resources efficiently.

### Object Hierarchy

```
Context (zmq::context_t)
  │
  ├─ Socket (zmq::socket_t)
  │   │
  │   ├─ Session (zmq::session_t) - One per endpoint
  │   │   │
  │   │   ├─ Connection (zmq::connection_t) - One per peer
  │   │   │   │
  │   │   │   ├─ Transport (zmq::tcp_t, zmq::ipc_t, etc.)
  │   │   │   │
  │   │   │   └─ Pipe (zmq::pipe_t) - Bidirectional message channel
  │   │   │
  │   │   └─ Pipe (for outgoing messages)
  │   │
  │   └─ Reaper thread (cleanup)
  │
  └─ Socket 2, Socket 3, ...
```

### Reference Counting

All objects use reference counting:
- Context holds refs to all sockets
- Socket holds refs to all sessions
- Session holds refs to all connections
- When ref count reaches zero, object is destroyed

### The Reaper Thread

Each context has a reaper thread that:
- Cleans up closed sockets
- Frees resources
- Ensures no memory leaks
- Runs in background

```c
// When you close a socket, it's not immediately destroyed
zmq_close(socket);  // Marks socket for cleanup

// Reaper thread will actually destroy it shortly
// zmq_term() waits for reaper to finish
zmq_term(context);  // Blocks until all cleanup complete
```

---

## Pipes

Pipes are the fundamental message transport mechanism within ZeroMQ.

### Pipe Characteristics

- **Bidirectional**: Messages flow both ways
- **Asynchronous**: No blocking between sender and receiver
- **Ordered**: Messages arrive in send order (per pipe)
- **Flow-controlled**: HWM limits prevent memory exhaustion

### Pipe Architecture

```
[Socket A] <--> [Pipe] <--> [Socket B]
                │
          [Message Queue]
          (up to HWM messages)
```

### Message Flow

1. Application calls `zmsg_send()` on socket
2. Socket places message in outgoing pipe
3. I/O thread picks up message from pipe
4. Message serialized and sent over network
5. Peer receives, deserializes, places in incoming pipe
6. Application calls `zmsg_recv()` to get message

### Pipe Options

```c
// Set pipe HWM (high-water mark)
int hwm = 1000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));

// When pipe reaches HWM:
// - Sender blocks (default behavior)
// - Or message is dropped (if ZMQ_DROPPED set)
```

---

## Message Scheduling

ZeroMQ uses sophisticated scheduling to balance messages across connections.

### Per-Socket Scheduling

**PUSH/DEALER**: Round-robin across connected peers
```c
// PUSH socket with 3 PULL peers
// Messages sent: Peer1, Peer2, Peer3, Peer1, Peer2, ...
```

**ROUTER**: Fair scheduling based on identity
```c
// ROUTER receives from multiple DEALER peers
// Processes one message per peer in rotation
// Prevents one busy peer from starving others
```

**PUB**: Multicast to all subscribers
```c
// Single send replicates to all SUB sockets
// Efficient at network level (single packet per interface)
```

### Affinity and Routing

DEALER/ROUTER can use message framing for custom routing:

```c
// DEALER sends with routing hints
zmsg_t *msg = zmsg_new();
zmsg_addstr(msg, "WORKER1");  // Route to specific worker
zmsg_addstr(msg, "task data");
zmsg_send(&dealer, msg);
```

---

## Message Structure

### zmsg_t (High-level API)

czmq provides `zmsg_t` for safe message handling:

```c
// Create message
zmsg_t *msg = zmsg_new();

// Add string frames
zmsg_addstr(msg, "Frame 1");
zmsg_addstr(msg, "Frame 2");

// Add binary frame
uint8_t data[] = {0x01, 0x02, 0x03};
zmsg_addmem(msg, data, 3);

// Send message
zmsg_send(&msg, socket);  // msg set to NULL after send

// Receive message
zmsg_t *msg = zmsg_recv(socket);

// Read frames (pop removes from head)
const char *frame1 = zmsg_popstr(msg);
const char *frame2 = zmsg_popstr(msg);

// Destroy message
zmsg_destroy(&msg);
```

### Multi-Frame Messages

ZeroMQ messages can have multiple frames:

```
[FRAME_1][FRAME_2][FRAME_3]...
```

Each frame is independent and can be different sizes.

**ROUTER/DEALER special case**: First frame is identity (for ROUTER) or routing hint (for DEALER).

### zframe_t (Low-level Frame Access)

For zero-copy operations:

```c
// Create frame from buffer
zframe_t *frame = zframe_new("Hello", 5);

// Get raw data (don't modify!)
uint8_t *data = zframe_data(frame);
size_t size = zframe_size(frame);

// Convert to string
const char *str = zframe_strdata(frame);

// Destroy frame
zframe_destroy(&frame);
```

---

## Global State

ZeroMQ maintains minimal global state for portability.

### Thread-Local Storage

Each thread has:
- Error code (`zmq_errno()`)
- Poll FD (for `zmq_poller`)
- Signal handling state

### Context State

Each context has:
- I/O thread pool
- Reaper thread
- Socket list
- Scheduler state

### No Global Locks

ZeroMQ avoids global locks for scalability:
- Each socket has its own lock
- Operations on different sockets don't block each other
- Context uses lock-free data structures where possible

---

## Concurrency Patterns

### Pattern 1: One Socket Per Thread

Simplest and most common pattern:

```c
// Main thread creates context
void *context = zmq_init(1);

// Each worker thread gets its own socket
void *socket = zmq_socket(context, ZMQ_PULL);
// Use socket exclusively in this thread
```

### Pattern 2: Socket Multiplexing (zmq_poll)

Single thread handling multiple sockets:

```c
zmq_pollitem_t items[] = {
    {socket1, 0, ZMQ_POLLIN, 0},
    {socket2, 0, ZMQ_POLLIN, 0},
    {socket3, 0, ZMQ_POLLOUT, 0}
};

int ready = zmq_poll(items, 3, 1000);  // 1 second timeout
if (ready > 0) {
    if (items[0].revents & ZMQ_POLLIN) {
        // socket1 has data
    }
    if (items[1].revents & ZMQ_POLLIN) {
        // socket2 has data
    }
}
```

### Pattern 3: Multi-Threaded Frontend/Backend

Separate threads for different responsibilities:

```c
// Thread 1: Network I/O
void *network_socket = zmq_socket(context, ZMQ_ROUTER);
zmq_bind(network_socket, "tcp://*:5559");

// Thread 2: Application logic
void *app_socket = zmq_socket(context, ZMQ_DEALER);
zmq_connect(app_socket, "inproc://backend");

// Thread 3: Proxy between them
zmq_proxy(network_socket, app_socket, NULL);
```

---

## Performance Considerations

### Memory Usage

- **Context**: ~10KB base + I/O thread stack
- **Socket**: ~5KB per socket
- **Connection**: ~2KB per connection
- **Message**: Frame size + overhead (~64 bytes per frame)

### Scaling Limits

| Resource | Typical Limit | Notes |
|----------|---------------|-------|
| Sockets per context | 10,000+ | Memory bound |
| Connections per socket | 1,000+ | I/O threads matter |
| Messages/sec | 1M+ | Depends on message size |
| Threads | CPU cores × 2 | Diminishing returns |

### Tuning for Performance

```c
// Increase I/O threads for many connections
void *context = zmq_init(4);

// Increase buffer sizes
int buf_size = 1024 * 1024;  // 1MB
zmq_setsockopt(socket, ZMQ_SNDBUF, &buf_size, sizeof(buf_size));
zmq_setsockopt(socket, ZMQ_RCVBUF, &buf_size, sizeof(buf_size));

// Increase HWM for bursty traffic
int hwm = 10000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));

// Reduce reconnection delay for resilience
int reconnect = 100;  // 100ms
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &reconnect, sizeof(reconnect));
```

---

## Debugging Internals

### Socket Monitoring

ZeroMQ can emit monitoring events:

```c
// Enable socket monitoring
void *monitor = zmq_socket(context, ZMQ_PAIR);
zmq_connect(monitor, "inproc://monitor");

zmq_socket_monitor(socket, "inproc://monitor", ZMQ_EVENT_ALL);

// Monitor thread
while (1) {
    zevent_t *event = zevent_recv(monitor);
    printf("Event: %d\n", zevent_event(event));
    zevent_destroy(&event);
}
```

### Common Events

- `ZMQ_EVENT_CONNECTED`: Connection established
- `ZMQ_EVENT_CONNECT_DELAYED`: Reconnect in progress
- `ZMQ_EVENT_CONNECT_RETRIED`: Reconnect retry
- `ZMQ_EVENT_LISTENING`: Socket started listening
- `ZMQ_EVENT_BIND_FAILED`: Bind failed
- `ZMQ_EVENT_ACCEPTED`: Incoming connection accepted
- `ZMQ_EVENT_ACCEPTED`: Connection closed

### Verbose Logging

```c
// Enable verbose logging (development only)
zsys_set_verbose(1);

// Set log to file
zsys_set_logfile("zmq.log");

// Set log level
zsys_set_log_level(ZLOG_LEVEL_DEBUG);
```

---

## See Also

- [Socket Patterns](01-socket-patterns.md) - How sockets use this architecture
- [Messaging Patterns](02-messaging-patterns.md) - Architectural patterns
- [Performance](06-performance.md) - Tuning based on internals
- [Troubleshooting](07-faq-troubleshooting.md) - Debugging architectural issues
