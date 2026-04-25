# ZeroMQ Performance and Tuning

This reference covers performance benchmarks, tuning parameters, scalability considerations, and optimization techniques for ZeroMQ applications.

## Performance Characteristics

### Throughput Benchmarks

Typical message throughput (messages per second):

| Transport | Message Size | Throughput | Latency |
|-----------|--------------|------------|---------|
| inproc:// | 64 bytes | 1,000,000+ | < 10 µs |
| ipc:// | 64 bytes | 500,000+ | ~50 µs |
| tcp:// (localhost) | 64 bytes | 200,000+ | ~100 µs |
| tcp:// (LAN) | 64 bytes | 50,000+ | ~500 µs |
| tcp:// (WAN) | 64 bytes | 10,000+ | > 1 ms |

**Notes:**
- Throughput decreases with larger message sizes
- CURVE authentication adds ~10-20% overhead
- Multiple I/O threads improve throughput for many connections

### Latency Characteristics

| Operation | Typical Latency |
|-----------|-----------------|
| inproc send/recv | 5-10 µs |
| ipc send/recv | 20-50 µs |
| tcp localhost | 50-100 µs |
| tcp LAN (1Gbps) | 200-500 µs |
| tcp WAN (10ms RTT) | 10-50 ms |

---

## Tuning Parameters

### Socket Options for Performance

```c
// Optimize socket for high throughput
void optimize_socket(void *socket, int mode) {
    if (mode == ZMQ_PUSH || mode == ZMQ_PULL || 
        mode == ZMQ_PUB || mode == ZMQ_SUB) {
        
        // Increase buffer sizes
        int bufsize = 16 * 1024 * 1024;  // 16MB
        zmq_setsockopt(socket, ZMQ_SNDBUF, &bufsize, sizeof(bufsize));
        zmq_setsockopt(socket, ZMQ_RCVBUF, &bufsize, sizeof(bufsize));
        
        // Increase HWM for bursty traffic
        int hwm = 10000;
        zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
        zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
        
        // Reduce reconnection delay for resilience
        int reconnect = 100;
        zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &reconnect, sizeof(reconnect));
        int max_reconnect = 1000;
        zmq_setsockopt(socket, ZMQ_RECONNECT_IVL_MAX, &max_reconnect, sizeof(max_reconnect));
    }
}
```

### Buffer Size Tuning

**ZMQ_SNDBUF/ZMQ_RCVBUF:**
- Controls OS-level socket buffer size
- Larger buffers = higher throughput but more memory
- Default: typically 128KB-1MB depending on OS
- Recommended: 1-16MB for high-throughput applications

```c
// Test different buffer sizes
int sizes[] = {128*1024, 1*1024*1024, 8*1024*1024, 16*1024*1024};
for (int i = 0; i < 4; i++) {
    int bufsize = sizes[i];
    zmq_setsockopt(socket, ZMQ_SNDBUF, &bufsize, sizeof(bufsize));
    zmq_setsockopt(socket, ZMQ_RCVBUF, &bufsize, sizeof(bufsize));
    // Run benchmark...
}
```

**ZMQ_SNDHWM/ZMQ_RCVHWM:**
- Controls application-level message queue size
- Prevents memory exhaustion from slow peers
- Default: 1000 messages
- Recommended: 1000-10000 depending on use case

```c
// Low latency: lower HWM
int hwm = 100;  // Messages drop if receiver too slow

// High throughput: higher HWM  
int hwm = 10000;  // Buffer more messages in flight
```

### I/O Thread Configuration

```c
// Default: 1 I/O thread
void *context = zmq_init(1);

// High connection count: more I/O threads
void *context = zmq_init(4);  // 4 I/O threads

// Very high connection count (>10,000)
void *context = zmq_init(8);  // 8 I/O threads
```

**Guidelines:**
- 1-100 connections: 1 I/O thread sufficient
- 100-1000 connections: 2-4 I/O threads
- 1000-10,000 connections: 4-8 I/O threads
- >10,000 connections: Consider architecture changes

---

## Optimization Techniques

### Message Batching

Combine multiple logical messages into single send:

```c
// Instead of sending 100 small messages:
for (int i = 0; i < 100; i++) {
    zmsg_t *msg = zmsg_new();
    zmsg_addstr(msg, sprintf("Message %d", i));
    zmsg_send(&msg, socket);
}

// Batch into single message:
zmsg_t *batch = zmsg_new();
for (int i = 0; i < 100; i++) {
    zmsg_addstr(batch, sprintf("Message %d", i));
}
zmsg_send(&batch, socket);
```

**Benefits:**
- Reduces system calls
- Better network utilization
- Lower CPU overhead

**Trade-off:**
- Increased latency for individual messages
- More complex receive logic

### Zero-Copy Messaging

Use `zframe_t` for zero-copy operations:

```c
// Create frame without copying data
uint8_t *data = malloc(1024);
// Fill data...
zframe_t *frame = zframe_wrap(data, 1024);  // Wraps, doesn't copy

zmsg_t *msg = zmsg_new();
zmsg_append(msg, &frame);  // Frame appended without copy
zmsg_send(&msg, socket);

// Frame and data freed automatically after send
```

### Connection Pooling

Reuse connections instead of creating new ones:

```c
// Bad: Creating new connection for each request
void bad_request(void) {
    void *context = zmq_init(1);
    void *socket = zmq_socket(context, ZMQ_REQ);
    zmq_connect(socket, "tcp://server:5555");
    
    // Send request, receive reply...
    
    zmq_close(socket);
    zmq_term(context);  // Expensive!
}

// Good: Reuse connection across requests
void *shared_context = zmq_init(1);
void *pooled_socket = zmq_socket(shared_context, ZMQ_DEALER);
zmq_connect(pooled_socket, "tcp://server:5555");

void good_request(void) {
    // Use pooled socket directly
    zmsg_t *msg = zmsg_new();
    zmsg_send(&msg, pooled_socket);
    zmsg_t *reply = zmsg_recv(pooled_socket);
}
```

### Asynchronous Processing

Use I/O threads effectively:

```c
// Main thread: Only application logic
void *app_socket = zmq_socket(context, ZMQ_ROUTER);
zmq_bind(app_socket, "inproc://backend");

// I/O threads handle network via proxy
void *net_socket = zmq_socket(context, ZMQ_DEALER);
zmq_bind(net_socket, "tcp://*:5555");

zmq_proxy(net_socket, app_socket, NULL);
```

### Transport Selection

Choose appropriate transport for use case:

```c
// Same process: inproc (fastest)
zmq_bind(socket1, "inproc://internal");
zmq_connect(socket2, "inproc://internal");

// Same machine: ipc (fast)
zmq_bind(socket, "ipc:///tmp/app");
zmq_connect(socket, "ipc:///tmp/app");

// Different machines: tcp (universal)
zmq_bind(socket, "tcp://*:5555");
zmq_connect(socket, "tcp://server:5555");

// One-to-many: epgm (if available)
zmq_bind(socket, "epgm://224.143.0.1:5556");
```

---

## Scalability Patterns

### Horizontal Scaling with Load Balancing

```
[Client] --> [Load Balancer (ROUTER)] --> [Worker 1]
                                    --> [Worker 2]
                                    --> [Worker N]
```

```c
// Load balancer
void *frontend = zmq_socket(context, ZMQ_ROUTER);
zmq_bind(frontend, "tcp://*:5559");

void *backend = zmq_socket(context, ZMQ_DEALER);
zmq_bind(backend, "tcp://*:5560");

zmq_proxy(frontend, backend, NULL);  // Automatic load balancing
```

**Scaling characteristics:**
- Linear scaling up to ~100 workers per load balancer
- Add more load balancers for >100 workers
- Use consistent hashing for stateful workloads

### Sharding by Key

Distribute messages by key to ensure ordering:

```c
// Client sends with routing key
zmsg_t *msg = zmsg_new();
zmsg_addstr(msg, "USER_123");  // Key determines worker
zmsg_addstr(msg, "process this");
zmsg_send(&dealer, msg);

// Load balancer routes by key (custom logic)
zmsg_t *request = zmsg_recv(frontend);
const char *identity = zmsg_popstr(request);
const char *key = zmsg_popstr(request);

// Hash key to select worker
int worker_id = hash(key) % num_workers;
// Route to specific worker...
```

### Fan-Out with PUB/SUB

Scale publishers with multiple subscribers:

```c
// Single publisher, many subscribers
void *publisher = zmq_socket(context, ZMQ_PUB);
zmq_bind(publisher, "tcp://*:5556");

// Start 100+ subscriber processes
// Each connects independently
void *subscriber = zmq_socket(context, ZMQ_SUB);
zmq_connect(subscriber, "tcp://server:5556");
```

**Scaling characteristics:**
- Single publisher can handle 1000+ subscribers
- Use multiple publishers for >1000 subscribers
- Consider multicast (epgm) for very large scale

---

## Performance Monitoring

### Socket Statistics

Track message rates and errors:

```c
// Get socket statistics
long long value;
size_t vlen = sizeof(value);

zmq_getsockopt(socket, ZMQ_RCVMORE, &value, &vlen);
printf("Messages in queue: %lld\n", value);

// Track send/receive rates with timestamps
struct {
    time_t last_check;
    uint64_t sent;
    uint64_t received;
} stats = {0};

void update_stats(void *socket) {
    long long sent, received;
    size_t len = sizeof(sent);
    
    zmq_getsockopt(socket, ZMQ_MSGS_SENT, &sent, &len);
    zmq_getsockopt(socket, ZMQ_MSGS_RECEIVED, &received, &len);
    
    time_t now = time(NULL);
    double seconds = difftime(now, stats.last_check);
    
    if (seconds > 0) {
        printf("Send rate: %.0f msg/s\n", (sent - stats.sent) / seconds);
        printf("Recv rate: %.0f msg/s\n", (received - stats.received) / seconds);
    }
    
    stats.last_check = now;
    stats.sent = sent;
    stats.received = received;
}
```

### Connection Monitoring

Monitor connection health:

```c
zmq_socket_monitor(socket, "inproc://monitor", ZMQ_EVENT_ALL);

void *monitor = zmq_socket(context, ZMQ_PAIR);
zmq_bind(monitor, "inproc://monitor");

while (1) {
    zevent_t *event = zevent_recv(monitor);
    
    switch (zevent_event(event)) {
        case ZMQ_EVENT_CONNECTED:
            log_metric("connections.active", +1);
            break;
        case ZMQ_EVENT_DISCONNECTED:
            log_metric("connections.active", -1);
            log_metric("connections.errors", +1);
            break;
        case ZMQ_EVENT_CONNECT_DELAYED:
            log_metric("connections.retries", +1);
            break;
    }
    
    zevent_destroy(&event);
}
```

### Latency Measurement

Measure end-to-end latency:

```c
// Sender adds timestamp
zmsg_t *msg = zmsg_new();
struct timeval tv;
gettimeofday(&tv, NULL);
uint64_t timestamp = tv.tv_sec * 1000000 + tv.tv_usec;
zmsg_addmem(msg, &timestamp, sizeof(timestamp));
zmsg_addstr(msg, "payload");
zmsg_send(&msg, socket);

// Receiver calculates latency
zmsg_t *reply = zmsg_recv(socket);
uint8_t *ts_data = zmsg_popframe(reply);
uint64_t send_time = *(uint64_t *) ts_data;

gettimeofday(&tv, NULL);
uint64_t recv_time = tv.tv_sec * 1000000 + tv.tv_usec;

double latency_us = (recv_time - send_time);
printf("Latency: %.2f ms\n", latency_us / 1000.0);
```

---

## Common Performance Issues

### Issue: High CPU Usage

**Causes:**
- Too many small messages
- Inefficient polling (short timeout)
- Excessive logging

**Solutions:**
```c
// Batch messages instead of sending one at a time
// Increase poll timeout
zmq_poll(items, nitems, 100);  // 100ms instead of 1ms
// Reduce log level in production
zsys_set_log_level(ZLOG_LEVEL_ERROR);
```

### Issue: Memory Growth

**Causes:**
- HWM too high or not set
- Message accumulation (slow consumer)
- Memory leaks (not destroying messages)

**Solutions:**
```c
// Set appropriate HWM
int hwm = 1000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));

// Always destroy received messages
zmsg_t *msg = zmsg_recv(socket);
// Process...
zmsg_destroy(&msg);  // Don't forget!

// Monitor memory usage
struct rusage usage;
getrusage(RUSAGE_SELF, &usage);
printf("Max RSS: %ld KB\n", usage.ru_maxrss);
```

### Issue: Connection Timeouts

**Causes:**
- Network latency > heartbeat timeout
- Firewall dropping packets
- Server overloaded

**Solutions:**
```c
// Increase heartbeat interval for high-latency networks
int heartbeat = 30000;  // 30 seconds
zmq_setsockopt(socket, ZMQ_HEARTBEAT_IVL, &heartbeat, sizeof(heartbeat));

// Increase timeout
int timeout = 60000;  // 60 seconds
zmq_setsockopt(socket, ZMQ_HEARTBEAT_TIMEOUT, &timeout, sizeof(timeout));

// Reduce reconnect delay for faster recovery
int reconnect = 500;
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &reconnect, sizeof(reconnect));
```

### Issue: Message Loss

**Causes:**
- HWM reached, messages dropped
- Connection closed during send
- Not checking return values

**Solutions:**
```c
// Check send return value
int sent = zmq_send(socket, msg, len, 0);
if (sent == -1) {
    printf("Send failed: %s\n", zmq_strerror(zmq_errno()));
}

// Use ZMQ_DROPPED to detect dropped messages
uint64_t dropped;
size_t len = sizeof(dropped);
zmq_getsockopt(socket, ZMQ_DROPPED, &dropped, &len);
if (dropped > 0) {
    printf("Warning: %lu messages dropped\n", dropped);
}

// Set ZMQ_LINGER to prevent blocked closes
int linger = 0;
zmq_setsockopt(socket, ZMQ_LINGER, &linger, sizeof(linger));
```

---

## Benchmarking Tools

### Simple Throughput Test

```c
#include <czmq.h>
#include <time.h>

void throughput_test(void) {
    void *context = zmq_init(1);
    
    void *push = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(push, "inproc://test");
    
    void *pull = zmq_socket(context, ZMQ_PULL);
    zmq_connect(pull, "inproc://test");
    
    // Warmup
    for (int i = 0; i < 1000; i++) {
        zmsg_t *msg = zmsg_new();
        zmsg_addstr(msg, "test");
        zmsg_send(&msg, push);
        zmsg_t *recv = zmsg_recv(pull);
        zmsg_destroy(&recv);
    }
    
    // Benchmark
    clock_t start = clock();
    int count = 100000;
    
    for (int i = 0; i < count; i++) {
        zmsg_t *msg = zmsg_new();
        zmsg_addstr(msg, "test");
        zmsg_send(&msg, push);
        zmsg_t *recv = zmsg_recv(pull);
        zmsg_destroy(&recv);
    }
    
    double elapsed = (double)(clock() - start) / CLOCKS_PER_SEC;
    printf("Throughput: %.0f msg/s\n", count / elapsed);
    
    zmq_close(push);
    zmq_close(pull);
    zmq_term(context);
}
```

---

## See Also

- [Architecture](03-architecture.md) - How internals affect performance
- [Protocols](04-protocols.md) - Transport performance characteristics
- [FAQ](07-faq-troubleshooting.md) - Performance troubleshooting
