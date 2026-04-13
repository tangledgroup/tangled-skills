# ZeroMQ Socket Patterns

This reference covers all ZeroMQ socket types and their corresponding messaging patterns as defined in the official RFCs.

## REQ/REP Pattern (RFC 28)

The Request-Reply pattern is the simplest messaging pattern, implementing RPC-style communication.

### Socket Behavior

**REQ Socket (Requester):**
- Must alternate `send()` and `recv()` calls strictly
- First operation must be `send()`, second must be `recv()`, etc.
- Automatically attaches identity to outgoing messages
- Blocks on send until previous reply received (prevents message loss)

**REP Socket (Replier):**
- Must alternate `recv()` and `send()` calls strictly
- First operation must be `recv()`, second must be `send()`, etc.
- Strips identity from incoming messages before delivering
- Blocks on recv until request available

### Basic Example

```c
// Server (REP)
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    void *server = zmq_socket(context, ZMQ_REP);
    zmq_bind(server, "tcp://*:5555");
    
    while (1) {
        zmsg_t *request = zmsg_recv(server);
        zmsg_print(request);
        zmsg_destroy(&request);
        
        zmsg_t *reply = zmsg_new();
        zmsg_addstr(reply, "Hello from server");
        zmsg_send(&reply, server);
    }
    
    zmq_close(server);
    zmq_term(context);
    return 0;
}

// Client (REQ)
int main(void) {
    void *context = zmq_init(1);
    void *client = zmq_socket(context, ZMQ_REQ);
    zmq_connect(client, "tcp://localhost:5555");
    
    // Send request
    zmsg_t *request = zmsg_new();
    zmsg_addstr(request, "Hello from client");
    zmsg_send(&request, client);
    
    // Receive reply
    zmsg_t *reply = zmsg_recv(client);
    zmsg_print(reply);
    zmsg_destroy(&reply);
    
    zmq_close(client);
    zmq_term(context);
    return 0;
}
```

### Message Framing

REQ automatically prepends a delimiter frame between requests:
```
[DELIMITER][REQUEST_DATA]
```

REP automatically strips the identity and delimiter from incoming messages.

### Limitations

- Strict send/recv alternation prevents flexible workflows
- No native support for multiple concurrent requests
- Single failure point if server crashes

For more flexibility, use DEALER/ROUTER pattern instead.

---

## PUB/SUB Pattern (RFC 29)

The Publish-Subscribe pattern implements one-to-many message distribution with filtering.

### Socket Behavior

**PUB Socket (Publisher):**
- Sends messages to all connected subscribers
- No tracking of connected subscribers (fire-and-forget)
- Messages are multicast efficiently
- Cannot receive messages

**SUB Socket (Subscriber):**
- Receives messages from publisher
- Can filter by topic prefix (multiple subscriptions allowed)
- By default, receives no messages until subscription set
- Late subscribers miss earlier messages (no catchup)

### Basic Example

```c
// Publisher
int main(void) {
    void *context = zmq_init(1);
    void *publisher = zmq_socket(context, ZMQ_PUB);
    zmq_bind(publisher, "tcp://*:5556");
    
    for (int i = 0; i < 100; i++) {
        zmsg_t *message = zmsg_new();
        zmsg_addstr(message, "Weather");  // Topic
        zmsg_addstr(message, sprintf("Temp: %dF", 50 + rand() % 50));
        zmsg_send(&message, publisher);
        zmsg_destroy(&message);
        
        zmq_sleep(1);  // 1 second
    }
    
    zmq_close(publisher);
    zmq_term(context);
    return 0;
}

// Subscriber
int main(void) {
    void *context = zmq_init(1);
    void *subscriber = zmq_socket(context, ZMQ_SUB);
    zmq_connect(subscriber, "tcp://localhost:5556");
    
    // Subscribe to topic (must be done before connecting for best results)
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "Weather", 7);
    
    while (1) {
        zmsg_t *message = zmsg_recv(subscriber);
        const char *topic = zmsg_popstr(message);
        const char *content = zmsg_popstr(message);
        
        printf("%s: %s\n", topic, content);
        
        zmsg_destroy(&message);
    }
    
    zmq_close(subscriber);
    zmq_term(context);
    return 0;
}
```

### Topic Filtering

SUB sockets filter messages based on topic prefixes:

```c
// Subscribe to all messages (empty prefix)
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "", 0);

// Subscribe to specific topic
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Weather", 7);

// Subscribe to multiple topics
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Weather", 7);
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Stocks", 6);

// Unsubscribe (use zero-length topic)
zmq_setsockopt(sub, ZMQ_UNSUBSCRIBE, "Weather", 7);
```

**Important**: Topic filtering is prefix-based. Subscribing to "Wea" matches "Weather".

### Message Format

Messages are multi-frame: `[TOPIC][DATA_FRAME_1][DATA_FRAME_2]...`

The topic is the first frame, followed by data frames.

### Limitations

- No acknowledgment or delivery guarantee
- Late subscribers miss earlier messages
- No built-in catchup mechanism
- Publisher doesn't know subscriber count

For reliable delivery, combine with REQ/REP catchup pattern (see messaging-patterns.md).

---

## PUSH/PULL Pattern (RFC 30)

The Pipeline pattern implements task distribution and collection.

### Socket Behavior

**PUSH Socket:**
- Sends messages to PULL sockets
- Load balances across connected PULL sockets (round-robin)
- Cannot receive messages
- Blocks if no PULL sockets are connected

**PULL Socket:**
- Receives messages from PUSH sockets
- Load balances incoming messages (each PULL gets subset)
- Cannot send messages
- Acts as sink in pipeline

### Basic Example (Task Queue)

```c
// Task distributor (PUSH)
int main(void) {
    void *context = zmq_init(1);
    void *distributor = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(distributor, "tcp://*:5557");
    
    for (int i = 0; i < 1000; i++) {
        zmsg_t *task = zmsg_new();
        zmsg_addstr(task, sprintf("Task #%d", i));
        zmsg_send(&task, distributor);
        zmsg_destroy(&task);
    }
    
    zmq_close(distributor);
    zmq_term(context);
    return 0;
}

// Worker (PULL)
int main(void) {
    void *context = zmq_init(1);
    void *worker = zmq_socket(context, ZMQ_PULL);
    zmq_connect(worker, "tcp://localhost:5557");
    
    int task_count = 0;
    while (task_count < 100) {  // Process 100 tasks
        zmsg_t *task = zmsg_recv(worker);
        const char *task_data = zmsg_popstr(task);
        
        printf("Processing: %s\n", task_data);
        zmq_sleep(1);  // Simulate work
        
        zmsg_destroy(&task);
        task_count++;
    }
    
    zmq_close(worker);
    zmq_term(context);
    return 0;
}
```

### Multi-Stage Pipelines

PUSH/PULL can be chained for multi-stage processing:

```
[PUSH] -> [PULL/DEALER] -> [ROUTER/PUSH] -> [PULL]
  Stage 1      Stage 2          Stage 3       Stage 4
```

### Limitations

- No feedback from PULL to PUSH (one-way only)
- PUSH blocks if no PULL connected (set ZMQ_LINGER to prevent hangs)
- No message acknowledgment
- Messages can be reordered across workers

For bidirectional communication, use DEALER/ROUTER instead.

---

## DEALER/ROUTER Pattern

Advanced request-reply pattern with flexible messaging and explicit addressing.

### Socket Behavior

**DEALER Socket:**
- Sends messages in round-robin fashion to peers
- Can send without receiving (unlike REQ)
- Automatically prepends identity to outgoing messages
- Flexible send/recv ordering (no strict alternation)

**ROUTER Socket:**
- Receives messages with peer identity as first frame
- Sends messages to specific peer by addressing
- Must include peer identity as first frame when sending
- Can handle multiple concurrent conversations

### Basic Example

```c
// Server (ROUTER)
int main(void) {
    void *context = zmq_init(1);
    void *server = zmq_socket(context, ZMQ_ROUTER);
    zmq_bind(server, "tcp://*:5558");
    
    while (1) {
        zmsg_t *request = zmsg_recv(server);
        
        // First frame is client identity
        zframe_t *identity = zmsg_pop(request);
        const char *client_id = zframe_strdata(identity);
        zframe_destroy(&identity);
        
        // Get actual request
        const char *request_data = zmsg_popstr(request);
        printf("Client %s said: %s\n", client_id, request_data);
        
        // Send reply (must include identity first)
        zmsg_t *reply = zmsg_new();
        zmsg_pushframe(reply, identity);  // Client identity
        zmsg_addstr(reply, "Reply from server");
        zmsg_send(&reply, server);
        
        zmsg_destroy(&request);
    }
    
    zmq_close(server);
    zmq_term(context);
    return 0;
}

// Client (DEALER)
int main(void) {
    void *context = zmq_init(1);
    void *client = zmq_socket(context, ZMQ_DEALER);
    zmq_connect(client, "tcp://localhost:5558");
    
    // Send request
    zmsg_t *request = zmsg_new();
    zmsg_addstr(request, "Hello from client");
    zmsg_send(&request, client);
    zmsg_destroy(&request);
    
    // Receive reply (identity is automatically stripped)
    zmsg_t *reply = zmsg_recv(client);
    const char *reply_data = zmsg_popstr(reply);
    printf("Server said: %s\n", reply_data);
    zmsg_destroy(&reply);
    
    zmq_close(client);
    zmq_term(context);
    return 0;
}
```

### Message Framing for ROUTER

ROUTER messages always include identity as first frame:
```
[IDENTITY][MESSAGE_FRAME_1][MESSAGE_FRAME_2]...
```

When sending to ROUTER, you must include the target's identity.

### Advantages Over REQ/REP

- No strict send/recv alternation
- Multiple concurrent requests possible
- Explicit addressing for routing
- Better for load-balanced architectures

See [Messaging Patterns](02-messaging-patterns.md) for load balancing examples.

---

## PAIR Socket (RFC 31)

Simple peer-to-peer socket for 1:1 communication.

### Socket Behavior

**PAIR Socket:**
- Only works with other PAIR sockets
- Behaves like traditional TCP socket
- Must have exactly one peer connected
- Supports both send and receive
- No message framing or addressing

### Use Cases

- Simple 1:1 communication within process (inproc)
- Communication over IPC on same machine
- Not recommended for TCP (use REQ/REP instead)

### Example

```c
// Sender
void *socket = zmq_socket(context, ZMQ_PAIR);
zmq_bind(socket, "inproc://mysocket");

// Receiver (must be in same process for inproc)
void *socket2 = zmq_socket(context, ZMQ_PAIR);
zmq_connect(socket2, "inproc://mysocket");
```

### Limitations

- Only one peer allowed
- No multicast or load balancing
- Limited to simple scenarios
- Not suitable for network communication

---

## XPUB/XSUB Sockets

Extended PUB/SUB sockets for building message brokers and proxies.

### Socket Behavior

**XPUB Socket:**
- Like PUB but can receive subscription messages from SUB peers
- Sends subscription/unsubscription notifications
- Used in broker architectures

**XSUB Socket:**
- Like SUB but can send subscriptions to XPUB
- Receives subscription confirmation messages
- Used in broker architectures

### Use Cases

- Building custom message brokers
- Implementing catchup mechanisms for PUB/SUB
- Creating proxy patterns (see zmq_proxy)

---

## Socket Options

### Common Options

```c
// Set socket option
int value = 1;
zmq_setsockopt(socket, ZMQ_OPTION, &value, sizeof(value));

// Get socket option  
int recv_buffer_size;
size_t optlen = sizeof(recv_buffer_size);
zmq_getsockopt(socket, ZMQ_RCVBUF, &recv_buffer_size, &optlen);
```

### Important Options

| Option | Description | Typical Value |
|--------|-------------|---------------|
| ZMQ_LINGER | Timeout for outstanding messages on close | 0 (immediate) |
| ZMQ_BACKLOG | Max pending connections | 100 |
| ZMQ_SNDBUF | Send buffer size | 1MB |
| ZMQ_RCVBUF | Receive buffer size | 1MB |
| ZMQ_SNDHWM | High-water mark for sends | 1000 |
| ZMQ_RCVHWM | High-water mark for receives | 1000 |
| ZMQ_IDENTITY | Socket identity (for ROUTER) | binary data |
| ZMQ_RATE | Send rate limit (messages/sec) | 1000 |
| ZMQ_RECOVERY_MSEC | Recovery interval after disconnect | 10000 |
| ZMQ_RECONNECT_IVL | Reconnect interval | 1000 |
| ZMQ_RECONNECT_IVL_MAX | Max reconnect interval | 32000 |

### High-Water Marks (HWM)

HWM prevents memory exhaustion by limiting queued messages:

```c
// Set HWM to 1000 messages
int hwm = 1000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
```

When HWM is reached:
- **Sender HWM**: Blocks send() or drops messages (based on ZMQ_DROPPED)
- **Receiver HWM**: New messages are rejected at sender

---

## Best Practices

1. **Always check return values**: zmq functions return -1 on error
2. **Set ZMQ_LINGER**: Prevent blocked closes in production
3. **Use appropriate HWM**: Prevent memory exhaustion under load
4. **Handle EAGAIN**: Non-blocking sockets may return EAGAIN
5. **Close sockets before terminating context**: zmq_close() before zmq_term()
6. **Don't share sockets between threads**: Share context instead
7. **Use zmq_strerror()**: Convert error codes to strings

### Error Handling

```c
if (zmq_send(socket, message, len, 0) == -1) {
    printf("Send error: %s\n", zmq_strerror(zmq_errno()));
}
```

---

## See Also

- [Messaging Patterns](02-messaging-patterns.md) - Advanced pattern combinations
- [Architecture](03-architecture.md) - How sockets work internally
- [Protocols](04-protocols.md) - ZMTP wire protocol details
- [Security](05-security.md) - Authentication and encryption
