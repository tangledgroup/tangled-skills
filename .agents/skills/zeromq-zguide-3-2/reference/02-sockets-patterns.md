# ZeroMQ Sockets and Patterns

Complete reference for ZeroMQ socket API, messaging patterns, and core concepts from Chapter 2 of the ZGuide.

## The Socket API Overview

ZeroMQ presents a familiar socket-based API that hides message-processing complexity. Understanding the API is fundamental to using ZeroMQ effectively.

### Creating Contexts and Sockets

**Context Creation:**
```c
void *context = zmq_init (io_threads);
```

**Socket Creation:**
```c
void *socket = zmq_socket (context, type);
```

**Python Example:**
```python
import zmq

context = zmq.Context()  # Creates context with default io threads
socket = context.socket(zmq.REQ)  # Creates REQ socket
```

### Socket Lifecycle

1. **Initialize context**: `zmq_init()` or `zmq.Context()`
2. **Create socket**: `zmq_socket()` or `context.socket()`
3. **Bind or connect**: Establish communication endpoint
4. **Send/receive messages**: Core messaging operations
5. **Close socket**: `zmq_close()` when done
6. **Terminate context**: `zmq_term()` (optional, happens on process exit)

## Socket Types and Topology

ZeroMQ provides several socket types, each supporting specific communication patterns.

### REQ/REP - Request-Reply

**Pattern:** Simple request-reply between client and server

**Socket Behavior:**
- **REQ socket**: Must send, then receive, then send, then receive (strict alternation)
- **REP socket**: Must receive, then send, then receive, then send (strict alternation)

**Topology:** One-to-one or one-to-many (one REP, multiple REQs)

**Use Cases:**
- Client-server applications
- RPC-style communication
- Simple task distribution

**Example:**
```python
# Server (REP)
context = zmq.Context()
rep = context.socket(zmq.REP)
rep.bind("tcp://*:5555")

while True:
    request = rep.recv()
    reply = f"Response to {request}".encode()
    rep.send(reply)

# Client (REQ)
context = zmq.Context()
req = context.socket(zmq.REQ)
req.connect("tcp://localhost:5555")

req.send(b"Hello")
response = req.recv()
print(response)
```

### DEALER/ROUTER - Advanced Request-Reply

**Pattern:** Flexible request-reply with custom routing

**Socket Behavior:**
- **DEALER socket**: Sends/receives in any order, round-robin delivery
- **ROUTER socket**: Sends/receives in any order, manages client identities

**Topology:** Many-to-many with intelligent routing

**Use Cases:**
- Load balancing across workers
- Custom routing protocols
- Task distribution with priorities

**Key Difference from REQ/REP:**
- No strict send/receive alternation
- DEALER sends to next available peer (round-robin)
- ROUTER includes identity frames in messages

**Example:**
```python
# Router (server)
context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:5555")

while True:
    # Receive identity + delimiter + message
    identity = router.recv()
    delimiter = router.recv()
    request = router.recv()
    
    # Route back to same client
    router.send_multipart([identity, delimiter, b"Response"])

# Dealer (client)
context = zmq.Context()
dealer = context.socket(zmq.DEALER)
dealer.connect("tcp://localhost:5555")

dealer.send(b"Hello")
response = dealer.recv()
print(response)
```

### PUB/SUB - Publish-Subscribe

**Pattern:** One-to-many broadcasting with filtering

**Socket Behavior:**
- **PUB socket**: Broadcasts messages to all subscribers
- **SUB socket**: Receives messages matching subscription filters

**Topology:** One-to-many (one PUB, multiple SUBs) or many-to-many

**Use Cases:**
- Event broadcasting
- Stock tickers, sensor data
- News feeds, notifications

**Key Concepts:**
- Subscribers specify filter prefixes
- Messages before subscription are lost
- No acknowledgments (fire-and-forget)

**Example:**
```python
# Publisher
context = zmq.Context()
pub = context.socket(zmq.PUB)
pub.bind("tcp://*:5556")

import time
while True:
    pub.send_string(f"Update at {time.time()}")
    time.sleep(1)

# Subscriber
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all

while True:
    message = sub.recv_string()
    print(message)
```

### PUSH/PULL - Pipeline Pattern

**Pattern:** Fan-out work distribution and collection

**Socket Behavior:**
- **PUSH socket**: Distributes messages to PULL sockets (load-balanced)
- **PULL socket**: Receives messages from PUSH sockets

**Topology:** Linear pipeline or tree structure

**Use Cases:**
- Multi-stage processing pipelines
- Task distribution to workers
- Result collection from workers

**Key Concepts:**
- Automatic load balancing across PULL sockets
- No acknowledgments (fire-and-forget)
- Supports multi-stage pipelines

**Example:**
```python
# Ventilator (PUSH)
context = zmq.Context()
push = context.socket(zmq.PUSH)
push.bind("tcp://*:5557")

for i in range(100):
    push.send(f"Task {i}".encode())

# Worker (PULL)
context = zmq.Context()
pull = context.socket(zmq.PULL)
pull.connect("tcp://localhost:5557")

while True:
    task = pull.recv()
    print(f"Processing {task}")
```

### PAIR - Peer-to-Peer

**Pattern:** Simple 1:1 communication

**Socket Behavior:**
- **PAIR socket**: Sends and receives messages bidirectionally
- Symmetric behavior (both ends can send/receive)

**Topology:** Point-to-point only

**Use Cases:**
- Simple peer communication
- Thread-to-thread messaging within process
- IPC between processes on same machine

**Limitations:**
- Only works with 1:1 connections
- No routing or load balancing
- Best used with inproc:// or ipc:// transports

### XPUB/XSUB - Extended Pub-Sub

**Pattern:** Pub-sub with subscription management

**Socket Behavior:**
- **XPUB socket**: Publishes messages and manages subscriptions
- **XSUB socket**: Receives messages and sends subscription commands

**Topology:** Similar to PUB/SUB but with control channel

**Use Cases:**
- Pub-sub with subscriber awareness
- Last-value caching
- Slow subscriber detection

## Transport Protocols

### TCP Transport (tcp://)

Network communication over TCP protocol.

**Binding (server):**
```python
socket.bind("tcp://*:5555")      # All interfaces, port 5555
socket.bind("tcp://127.0.0.1:5555")  # localhost only
```

**Connecting (client):**
```python
socket.connect("tcp://localhost:5555")
socket.connect("tcp://192.168.1.100:5555")
```

**Key Points:**
- Supports IPv4 and IPv6
- Firewall considerations for production
- Reconnection is automatic

### IPC Transport (ipc://)

Local inter-process communication using Unix domain sockets.

**Usage:**
```python
socket.bind("ipc:///tmp/mysocket")
socket.connect("ipc:///tmp/mysocket")
```

**Key Points:**
- Faster than TCP for local communication
- Uses filesystem paths
- File permissions control access
- Not available on Windows (use tcp:// instead)

### Inproc Transport (inproc://)

Fastest transport for sockets within same process.

**Usage:**
```python
socket1 = context.socket(zmq.PUSH)
socket1.bind("inproc://mysocket")

socket2 = context.socket(zmq.PULL)
socket2.connect("inproc://mysocket")
```

**Key Points:**
- Fastest possible communication
- Only works within same process
- Useful for thread-to-thread messaging
- No network overhead

## Message Handling

### Sending Messages

**Simple Send:**
```python
socket.send(b"message")
socket.send_string("message")  # Python convenience
```

**Multipart Send:**
```python
# Python
socket.send_multipart([b"part1", b"part2", b"part3"])

# C
zmq_send(socket, "part1", 5, ZMQ_SNDMORE);
zmq_send(socket, "part2", 5, ZMQ_SNDMORE);
zmq_send(socket, "part3", 5, 0);  # Last part without SNDMORE
```

### Receiving Messages

**Simple Receive:**
```python
message = socket.recv()
string_message = socket.recv_string()  # Python convenience
```

**Multipart Receive:**
```python
# Python
parts = []
while True:
    part = socket.recv()
    parts.append(part)
    if not socket.getsockopt(zmq.RCVMORE):
        break

# C
do {
    zmq_recv(socket, buffer, size, 0);
    // Check ZMQ_RCVMORE option for more parts
} while (more);
```

### Message Options

**ZMQ_SNDMORE:** Flag to indicate more message frames follow

**ZMQ_RCVMORE:** Option to check if more frames are incoming

## Handling Multiple Sockets

### Using Poller

ZeroMQ provides polling mechanisms for handling multiple sockets.

**Python (zmq.Poller):**
```python
import zmq

context = zmq.Context()
socket1 = context.socket(zmq.SUB)
socket1.connect("tcp://localhost:5556")
socket1.setsockopt_string(zmq.SUBSCRIBE, "")

socket2 = context.socket(zmq.PULL)
socket2.connect("tcp://localhost:5557")

poller = zmq.Poller()
poller.register(socket1, zmq.POLLIN)
poller.register(socket2, zmq.POLLIN)

while True:
    sockets = dict(poller.poll())
    
    if socket1 in sockets:
        message = socket1.recv_string()
        print(f"From pub-sub: {message}")
    
    if socket2 in sockets:
        message = socket2.recv()
        print(f"From pipeline: {message}")
```

**C (zmq_poll):**
```c
zmq_pollitem_t items [] = {
    {task_socket, 0, ZMQ_POLLIN, 0},
    {weather_socket, 0, ZMQ_POLLIN, 0}
};

while (1) {
    zmq_poll (items, 2, 1000);  // Poll for up to 1 second
    
    if (items [0].revents & ZMQ_POLLIN) {
        // Process task_socket
    }
    
    if (items [1].revents & ZMQ_POLLIN) {
        // Process weather_socket
    }
}
```

### Socket Options for Polling

**Timeout:**
```python
socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
```

**Non-blocking:**
```python
socket.setsockopt(zmq.RCVTIMEO, 0)  # Return immediately if no message
```

## I/O Threads

ZeroMQ uses background I/O threads to handle network operations asynchronously.

### Configuring I/O Threads

**Default behavior:**
- Context creates 1 I/O thread by default
- Thread pool handles all socket I/O

**Custom configuration:**
```c
void *context = zmq_init (4);  // Create context with 4 I/O threads
```

```python
context = zmq.Context(4)  # 4 I/O threads
```

### When to Increase I/O Threads

- Many concurrent connections (100+)
- High message throughput requirements
- Multiple network interfaces
- CPU-bound applications (don't block I/O)

## Intermediaries and Proxies

### Built-in Proxy

ZeroMQ provides a built-in proxy for connecting PULL and PUSH sockets.

**Python:**
```python
import zmq

context = zmq.Context()

# Create frontend and backend sockets
frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5559")

backend = context.socket(zmq.DEALER)
backend.bind("tcp://*:5560")

# Start proxy
zmq.proxy(frontend, backend)
```

**Use Cases:**
- Request-reply brokers
- Message routing between different patterns
- Monitoring and inspection points

### Custom Intermediary

For more control, implement custom intermediary logic:

```python
import zmq

context = zmq.Context()
frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5559")

backend = context.socket(zmq.DEALER)
backend.bind("tcp://*:5560")

# Manual proxy loop
while True:
    zmq.poll([frontend, backend], 1000)
    
    if frontend.poll(0, zmq.POLLIN):
        # Route from frontend to backend
        message = []
        while True:
            frame = frontend.recv()
            message.append(frame)
            if not frontend.getsockopt(zmq.RCVMORE):
                break
        
        for i, frame in enumerate(message):
            more = zmq.SNDMORE if i < len(message) - 1 else 0
            backend.send(frame, more)
```

## Key Socket Properties

### ZMQ_IDENTITY

ROUTER sockets set identity automatically or manually:

```python
# Set custom identity
dealer.setsockopt(zmq.IDENTITY, b"MyClient")

# Get identity from ROUTER
identity = router.recv()  # First frame is identity
```

### ZMQ_SUBSCRIBE/ZMQ_UNSUBSCRIBE

SUB and XSUB sockets manage subscriptions:

```python
# Subscribe to topic prefix
sub.setsockopt_string(zmq.SUBSCRIBE, "A")  # Gets messages starting with "A"

# Unsubscribe
sub.setsockopt_string(zmq.UNSUBSCRIBE, "A")

# Subscribe to all
sub.setsockopt_string(zmq.SUBSCRIBE, "")
```

### ZMQ_RATE and ZMQ_RECOVERY_IVL

Rate limiting for pub-sub:

```python
pub.setsockopt(zmq.RATE, 100)  # 100 Kb/sec
pub.setsockopt(zmq.RECOVERY_IVL, 10000)  # 10 second recovery interval
```

## Best Practices

1. **Always close sockets** - Use try-finally or context managers
2. **Use appropriate socket types** - Match pattern to use case
3. **Configure timeouts** - Prevent indefinite blocking
4. **Handle multipart messages** - ZeroMQ uses frames internally
5. **Use pollers for multiple sockets** - Efficient I/O multiplexing
6. **Consider I/O thread count** - Tune for connection count
7. **Test reconnection behavior** - ZeroMQ handles it automatically

## Common Pitfalls

**REQ/REP Blocking:**
- Strict alternation can cause deadlocks
- Use DEALER/ROUTER for flexible patterns

**Pub-Sub Message Loss:**
- Messages sent before subscription are lost
- Consider last-value caching pattern

**TCP Connection Storm:**
- Many simultaneous connections can overwhelm server
- Use connection rate limiting if needed

**Identity Management:**
- ROUTER requires identity frames
- DEALER identities are automatic unless set manually

## Next Steps

- [Advanced Request-Reply](04-advanced-request-reply.md) - Load balancing patterns
- [Reliable Messaging](05-reliable-request-reply.md) - Fault tolerance
- [Advanced Pub-Sub](03-advanced-pubsub.md) - Subscriber management
- [Distributed Frameworks](08-distributed-framework.md) - Building complete systems
