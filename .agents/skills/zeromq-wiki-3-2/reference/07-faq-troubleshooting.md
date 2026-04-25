# ZeroMQ FAQ and Troubleshooting

This reference covers frequently asked questions, common issues, debugging techniques, and solutions for ZeroMQ applications.

## Frequently Asked Questions

### What is ZeroMQ?

ZeroMQ (ØMQ) is a **high-performance asynchronous messaging library** that provides sockets implementing various messaging patterns. Unlike traditional messaging systems, it requires no central broker and works directly between processes.

**Key characteristics:**
- No daemon or broker required
- Multiple transports: TCP, IPC, inproc, NORM
- Built-in patterns: REQ/REP, PUB/SUB, PUSH/PULL
- Thread-safe context, non-thread-safe sockets
- Supports millions of messages per second

### What is NOT ZeroMQ?

ZeroMQ is **not**:
- A message queue (no persistence)
- A guaranteed delivery system (fire-and-forget by default)
- A replacement for RPC frameworks (though it can implement RPC)
- A database or cache

### When Should I Use ZeroMQ?

**Good fits:**
- High-performance messaging between services
- Load-balanced task distribution
- Event notification systems
- Real-time data distribution
- Multi-threaded applications needing IPC

**Not a good fit:**
- Message persistence required (use Redis, RabbitMQ)
- Guaranteed delivery critical (use Kafka, Pulsar)
- Complex routing rules (use NATS, Apache Service Fabric)
- Simple configuration preferred (use gRPC for RPC)

### Which Socket Pattern Should I Use?

| Use Case | Recommended Pattern |
|----------|---------------------|
| Simple RPC | REQ/REP |
| Load-balanced workers | PUSH/PULL or DEALER/ROUTER |
| Event broadcasting | PUB/SUB |
| Reliable pub-sub | PUB/SUB + catchup mechanism |
| Service orchestration | MDP (Majordomo Protocol) |
| Simple 1:1 communication | PAIR (inproc only) |
| Building brokers | XPUB/XSUB or zmq_proxy |

### How Do I Handle Connection Failures?

ZeroMQ automatically handles reconnection:

```c
// Configure reconnection behavior
int reconnect_interval = 1000;  // 1 second
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &reconnect_interval, sizeof(reconnect_interval));

int max_reconnect = 32000;  // Max 32 seconds (exponential backoff)
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL_MAX, &max_reconnect, sizeof(max_reconnect));

// Monitor connection events
zmq_socket_monitor(socket, "inproc://monitor", 
    ZMQ_EVENT_CONNECTED | ZMQ_EVENT_DISCONNECTED);
```

**Key points:**
- ZeroMQ reconnects automatically in background
- Use monitoring to detect failures
- Set appropriate timeouts for your use case

---

## Common Issues and Solutions

### Issue: Messages Not Being Received

#### Symptom
Subscriber not receiving messages from publisher.

#### Causes and Solutions

**1. Subscription not set before connecting**
```c
// Wrong: Subscribe after connect
zmq_connect(sub, "tcp://server:5556");
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "topic", 5);  // Too late!

// Correct: Subscribe before or immediately after connect
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "topic", 5);
zmq_connect(sub, "tcp://server:5556");
```

**2. Topic mismatch**
```c
// Publisher sends with topic
zmsg_addstr(msg, "Weather Update");  // 14 characters

// Subscriber filters on wrong prefix
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Weather", 7);  // Matches!
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Weather Upd", 11);  // Also matches!
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "Stocks", 6);  // Won't match
```

**3. Publisher started before subscriber**
Messages sent before subscriber connects are lost (no catchup).

**Solution:** Implement catchup mechanism using REQ/REP for late subscribers.

#### Debug Steps
1. Verify subscription prefix matches message topic exactly
2. Check publisher is actually sending (add logging)
3. Use `zmq_socket_monitor()` to verify connection established
4. Try with empty subscription (`zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "", 0)`)

---

### Issue: PUSH Socket Blocks Forever

#### Symptom
Application hangs on `zmq_send()` to PUSH socket.

#### Cause
No PULL sockets are connected to receive messages.

#### Solutions

**1. Set ZMQ_LINGER to allow graceful close**
```c
int linger = 0;  // Close immediately, drop pending messages
zmq_setsockopt(push_socket, ZMQ_LINGER, &linger, sizeof(linger));
```

**2. Use zmq_poll() with timeout**
```c
zmq_pollitem_t item = {push_socket, 0, ZMQ_POLLOUT, 0};
int ready = zmq_poll(&item, 1, 1000);  // 1 second timeout

if (ready > 0 && item.revents & ZMQ_POLLOUT) {
    zmq_send(socket, msg, len, 0);
} else {
    printf("No receivers available, dropping message\n");
}
```

**3. Ensure PULL sockets start before PUSH**
In task queue pattern, start workers before distributor.

---

### Issue: REQ Socket Deadlocks

#### Symptom
REQ socket hangs after sending request.

#### Cause
REQ socket requires strict alternation: send → recv → send → recv

```c
// Wrong: Two sends in a row
zmq_send(req, request1, len, 0);
zmq_send(req, request2, len, 0);  // Blocks! Must recv first.

// Correct: Alternate send/recv
zmq_send(req, request1, len, 0);
zmq_recv(req, reply1, &len, 0);
zmq_send(req, request2, len, 0);
zmq_recv(req, reply2, &len, 0);
```

#### Solution
Use DEALER socket for flexible send/recv patterns:
```c
void *dealer = zmq_socket(context, ZMQ_DEALER);
// Can send multiple times without receiving
```

---

### Issue: Memory Growth Over Time

#### Symptom
Application memory usage increases continuously.

#### Causes and Solutions

**1. Not destroying messages**
```c
// Wrong: Memory leak
zmsg_t *msg = zmsg_recv(socket);
process_message(msg);
// Forgot to destroy!

// Correct
zmsg_t *msg = zmsg_recv(socket);
process_message(msg);
zmsg_destroy(&msg);  // Always destroy received messages
```

**2. HWM too high or not set**
```c
// Set reasonable HWM to prevent unbounded growth
int hwm = 1000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
```

**3. Slow consumer causing backlog**
Monitor and alert on queue depth:
```c
// Check for dropped messages
uint64_t dropped;
size_t len = sizeof(dropped);
zmq_getsockopt(socket, ZMQ_DROPPED, &dropped, &len);
if (dropped > 0) {
    printf("Warning: %lu messages dropped due to slow consumer\n", dropped);
}
```

---

### Issue: Connection Refused or Timeout

#### Causes and Solutions

**1. Server not started yet**
```c
// Client should handle reconnection gracefully
int reconnect = 1000;  // Retry every second
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &reconnect, sizeof(reconnect));
```

**2. Wrong address or port**
```c
// Verify server is binding to correct address
zmq_bind(server, "tcp://*:5555");  // All interfaces

// Client connects to matching address
zmq_connect(client, "tcp://server-hostname:5555");
```

**3. Firewall blocking port**
Check firewall rules for ZeroMQ ports.

**4. Binding to wrong interface**
```c
// Bind to specific interface instead of *
zmq_bind(server, "tcp://192.168.1.100:5555");
```

---

## Debugging Techniques

### Enable Verbose Logging

```c
// Set log level (development only)
zsys_set_log_level(ZLOG_LEVEL_DEBUG);

// Log to file
zsys_set_logfile("zeromq_debug.log");

// Log to stdout
zsys_set_log_identity("MyApp");
```

### Socket Monitoring

Monitor all socket events:

```c
void setup_monitoring(void *socket) {
    // Create monitor socket in same process
    zmq_socket_monitor(socket, "inproc://monitor", ZMQ_EVENT_ALL);
}

void monitor_thread(void *context) {
    void *monitor = zmq_socket(context, ZMQ_PAIR);
    zmq_bind(monitor, "inproc://monitor");
    
    while (1) {
        zevent_t *event = zevent_recv(monitor);
        
        printf("Event: %d ", zevent_event(event));
        
        switch (zevent_event(event)) {
            case ZMQ_EVENT_CONNECTED:
                printf("Connected to %s\n", zevent_address(event));
                break;
            case ZMQ_EVENT_CONNECT_DELAYED:
                printf("Connection delayed, will retry\n");
                break;
            case ZMQ_EVENT_CONNECT_RETRIED:
                printf("Reconnection attempted\n");
                break;
            case ZMQ_EVENT_LISTENING:
                printf("Socket listening on %s\n", zevent_address(event));
                break;
            case ZMQ_EVENT_BIND_FAILED:
                printf("Bind failed: %s\n", zevent_address(event));
                break;
            case ZMQ_EVENT_ACCEPTED:
                printf("Accepted connection from %s\n", zevent_address(event));
                break;
            case ZMQ_EVENT_ACCEPTED_FAIL:
                printf("Accept failed for %s\n", zevent_address(event));
                break;
            case ZMQ_EVENT_CLOSED:
                printf("Connection closed\n");
                break;
            case ZMQ_EVENT_CLOSE_FAILED:
                printf("Close failed\n");
                break;
            case ZMQ_EVENT_DISCONNECTED:
                printf("Disconnected from %s\n", zevent_address(event));
                break;
            default:
                printf("Unknown event\n");
        }
        
        zevent_destroy(&event);
    }
}
```

### Message Tracing

Add sequence numbers to trace message flow:

```c
static uint64_t msg_counter = 0;

zmsg_t *create_traced_message(const char *content) {
    zmsg_t *msg = zmsg_new();
    
    // Add trace header
    msg_counter++;
    struct timeval tv;
    gettimeofday(&tv, NULL);
    
    zmsg_addstr(msg, sprintf("MSG-%06lu-%ld-%ld", 
        msg_counter, tv.tv_sec, tv.tv_usec));
    zmsg_addstr(msg, content);
    
    return msg;
}

void print_message_trace(zmsg_t *msg) {
    const char *trace = zmsg_popstr(msg);
    printf("[%s] Message received\n", trace);
    // Process rest of message...
}
```

### Performance Profiling

Measure latency and throughput:

```c
#include <time.h>

double get_time_ms(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

void benchmark_roundtrip(void *socket, int iterations) {
    double start = get_time_ms();
    
    for (int i = 0; i < iterations; i++) {
        zmsg_t *msg = zmsg_new();
        zmsg_addstr(msg, "ping");
        zmsg_send(&msg, socket);
        
        zmsg_t *reply = zmsg_recv(socket);
        zmsg_destroy(&reply);
    }
    
    double elapsed = get_time_ms() - start;
    printf("Roundtrip: %.3f ms avg (%.0f msg/s)\n", 
        elapsed / iterations, iterations / (elapsed / 1000.0));
}
```

---

## Error Handling

### Check All Return Values

```c
// Always check return values
void *context = zmq_init(1);
if (!context) {
    perror("zmq_init failed");
    exit(1);
}

void *socket = zmq_socket(context, ZMQ_REQ);
if (!socket) {
    perror("zmq_socket failed");
    zmq_term(context);
    exit(1);
}

int rc = zmq_connect(socket, "tcp://server:5555");
if (rc != 0) {
    printf("zmq_connect failed: %s\n", zmq_strerror(rc));
}
```

### Common Error Codes

| Error | Code | Meaning | Solution |
|-------|------|---------|----------|
| Success | 0 | Operation succeeded | - |
| Invalid argument | EINVAL | Invalid socket option or value | Check option name/value |
| Resource unavailable | EAGAIN | Non-blocking op would block | Retry or use blocking mode |
| Protocol error | EPROTO | Message protocol violation | Check message framing |
| Connection refused | ECONNREFUSED | No server listening | Start server, check address |
| Operation timed out | ETIMEDOUT | Operation exceeded timeout | Increase timeout or investigate |
| Bad file descriptor | EBADF | Socket closed or invalid | Recreate socket |
| No memory | ENOMEM | Out of memory | Reduce HWM, check memory usage |

### Error Handling Pattern

```c
typedef struct {
    void *context;
    void *socket;
    bool running;
} app_state_t;

app_state_t *create_app(void) {
    app_state_t *state = calloc(1, sizeof(app_state_t));
    
    state->context = zmq_init(1);
    if (!state->context) {
        perror("Failed to create context");
        free(state);
        return NULL;
    }
    
    state->socket = zmq_socket(state->context, ZMQ_DEALER);
    if (!state->socket) {
        perror("Failed to create socket");
        zmq_term(state->context);
        free(state);
        return NULL;
    }
    
    int rc = zmq_connect(state->socket, "tcp://server:5555");
    if (rc != 0) {
        printf("Warning: connect failed: %s\n", zmq_strerror(rc));
        // Continue anyway, ZeroMQ will retry
    }
    
    state->running = true;
    return state;
}

void destroy_app(app_state_t *state) {
    if (!state) return;
    
    state->running = false;
    
    if (state->socket) {
        zmq_close(state->socket);
    }
    
    if (state->context) {
        zmq_term(state->context);
    }
    
    free(state);
}
```

---

## Community Resources

### Official Documentation

- **ZGuide (The Guide)**: http://zguide.zeromq.org - Hundreds of worked examples
- **API Reference**: http://api.zeromq.org - Complete C API documentation  
- **RFCs**: http://rfc.zeromq.org - Protocol specifications
- **Wiki**: http://wiki.zeromq.org - Community documentation

### Mailing Lists and Forums

- **zeromq-dev**: Development discussions (GitHub issues)
- **zeromq-users**: User questions and help
- **Stack Overflow**: Tag `[zeromq]` for questions

### Code Repositories

- **libzmq (core)**: https://github.com/zeromq/libzmq
- **czmq (C wrapper)**: https://github.com/zeromq/czmq
- **Language bindings**: https://github.com/zeromq

### Books

- "ZeroMQ: Messaging for Complex Applications" by Pieter Hintjens (O'Reilly)
- Available as free PDF from ZGuide website

---

## See Also

- [Socket Patterns](01-socket-patterns.md) - Pattern-specific troubleshooting
- [Messaging Patterns](02-messaging-patterns.md) - Advanced pattern issues
- [Architecture](03-architecture.md) - Understanding internals for debugging
- [Security](05-security.md) - Authentication troubleshooting
- [Performance](06-performance.md) - Performance issue diagnosis
