# Advanced Messaging Patterns

This reference covers advanced messaging patterns built on top of basic socket types, including task queues, load balancing, pub-sub catchup, and device patterns.

## Task Queue Pattern

A task queue distributes work among multiple workers using PUSH/PULL sockets.

### Architecture

```
[Distributor (PUSH)] --> [Worker 1 (PULL)]
                        [Worker 2 (PULL)]
                        [Worker 3 (PULL)]
```

### Implementation

```c
// Task distributor
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    void *distributor = zmq_socket(context, ZMQ_PUSH);
    zmq_bind(distributor, "tcp://*:5557");
    
    printf("Sending tasks...\n");
    for (int task = 0; task < 25; task++) {
        zmsg_t *message = zmsg_new();
        zmsg_addstr(message, sprintf("Task %d", task));
        
        // Send to random worker (PUSH load balances)
        zmsg_send(&message, distributor);
        zmsg_destroy(&message);
        
        zmq_sleep(1);  // 1 second between tasks
    }
    
    zmq_close(distributor);
    zmq_term(context);
    return 0;
}

// Worker
int main(int argc, char *argv[]) {
    void *context = zmq_init(1);
    void *worker = zmq_socket(context, ZMQ_PULL);
    zmq_connect(worker, "tcp://localhost:5557");
    
    printf("Worker started\n");
    int tasks_done = 0;
    
    while (tasks_done < 10) {  // Process up to 10 tasks
        zmsg_t *message = zmsg_recv(worker);
        const char *task = zmsg_popstr(message);
        
        printf("Processing: %s\n", task);
        
        // Simulate variable work time (250-1000ms)
        int workload = 250 + (rand() % 8) * 125;
        zmq_sleep(workload / 1000.0);
        
        zmsg_destroy(&message);
        tasks_done++;
    }
    
    printf("Worker done, processed %d tasks\n", tasks_done);
    zmq_close(worker);
    zmq_term(context);
    return 0;
}
```

### Key Points

- PUSH automatically load-balances across workers (round-robin)
- Workers can start/stop dynamically
- No central coordination needed
- Tasks are distributed evenly by default

---

## Request-Reply with Load Balancing

Using DEALER/ROUTER for advanced request-reply with multiple workers.

### Architecture

```
[Client (DEALER)] --> [Load Balancer (ROUTER/DEALER)] --> [Worker 1 (DEALER)]
                                         --> [Worker 2 (DEALER)]
                                         --> [Worker 3 (DEALER)]
```

### Load Balancer Implementation

```c
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    
    // Socket to talk to clients
    void *frontend = zmq_socket(context, ZMQ_ROUTER);
    zmq_bind(frontend, "tcp://*:5559");
    
    // Socket to talk to workers
    void *backend = zmq_socket(context, ZMQ_DEALER);
    zmq_bind(backend, "tcp://*:5560");
    
    // Use zmq_proxy for automatic forwarding
    zmq_proxy(frontend, backend, NULL);
    
    // Cleanup handled by signal handler in production
    while (1) {
        zmq_sleep(3600);  // Run indefinitely
    }
    
    zmq_close(frontend);
    zmq_close(backend);
    zmq_term(context);
    return 0;
}
```

### Worker Implementation

```c
int main(void) {
    void *context = zmq_init(1);
    void *worker = zmq_socket(context, ZMQ_DEALER);
    zmq_connect(worker, "tcp://localhost:5560");
    
    printf("Worker connected\n");
    
    while (1) {
        // Wait for task from load balancer
        zmsg_t *request = zmsg_recv(worker);
        
        // Get client identity (first frame)
        zframe_t *identity = zmsg_pop(request);
        
        // Get actual request data
        const char *task = zmsg_popstr(request);
        printf("Task: %s\n", task);
        
        // Simulate work
        zmq_sleep(1);
        
        // Send reply back through load balancer
        zmsg_t *reply = zmsg_new();
        zmsg_pushframe(reply, identity);  // Client identity
        zmsg_addstr(reply, "Task completed");
        zmsg_send(&reply, worker);
        
        zmsg_destroy(&request);
    }
    
    zmq_close(worker);
    zmq_term(context);
    return 0;
}
```

### Key Points

- Load balancer routes requests to workers in round-robin
- Replies automatically routed back to correct client
- Workers can scale horizontally
- Single point of failure at load balancer (mitigate with redundancy)

---

## Pub-Sub with Catchup

Standard PUB/SUB doesn't retain messages for late subscribers. This pattern adds catchup using REQ/REP.

### Architecture

```
[Publisher] --> [PUB] --> [Subscriber (SUB)]
     |
     +--> [CATCHUP (REP)] <-- [Late Subscriber (REQ)]
```

### Publisher with Catchup

```c
#include <czmq.h>
#include <stdlib.h>

#define MAX_CATCHUP 1000  // Keep last 1000 messages

int main(void) {
    void *context = zmq_init(1);
    
    // Regular publisher
    void *publisher = zmq_socket(context, ZMQ_PUB);
    zmq_bind(publisher, "tcp://*:5556");
    
    // Catchup socket for late subscribers
    void *catchup = zmq_socket(context, ZMQ_REP);
    zmq_bind(catchup, "tcp://*:5557");
    
    // Message queue for catchup
    zlistx_t *message_queue = zlistx_new();
    zlistx_set_destructor(message_queue, (zlistx_destructor_t) zmsg_destroy);
    
    int sequence = 0;
    while (1) {
        // Create message
        zmsg_t *message = zmsg_new();
        zmsg_addstr(message, "Update");
        zmsg_addstr(message, sprintf("Sequence: %d", ++sequence));
        
        // Send to live subscribers
        zmsg_t *live_copy = zmsg_dup(message);
        zmsg_send(&live_copy, publisher);
        
        // Queue for catchup
        zlistx_add_end(message_queue, message);
        
        // Trim queue if too large
        while (zlistx_size(message_queue) > MAX_CATCHUP) {
            zmsg_t *old = zlistx_pop_head(message_queue);
            zmsg_destroy(&old);
        }
        
        zmq_sleep(1);
    }
    
    zlistx_destroy(&message_queue);
    zmq_close(publisher);
    zmq_close(catchup);
    zmq_term(context);
    return 0;
}
```

### Late Subscriber with Catchup

```c
int main(void) {
    void *context = zmq_init(1);
    
    // First, get catchup messages via REQ/REP
    void *catchup = zmq_socket(context, ZMQ_REQ);
    zmq_connect(catchup, "tcp://localhost:5557");
    
    // Request all catchup messages
    zmsg_t *request = zmsg_new();
    zmsg_addstr(request, "CATCHUP");
    zmsg_send(&request, catchup);
    
    // Receive queued messages
    int sequence = 0;
    while (1) {
        zmsg_t *reply = zmsg_recv(catchup);
        const char *type = zmsg_popstr(reply);
        
        if (strcmp(type, "DONE") == 0) {
            break;  // End of catchup
        }
        
        const char *data = zmsg_popstr(reply);
        printf("Catchup: %s\n", data);
        sequence++;
        
        zmsg_destroy(&reply);
    }
    
    printf("Received %d catchup messages\n", sequence);
    
    // Now subscribe to live updates
    void *subscriber = zmq_socket(context, ZMQ_SUB);
    zmq_connect(subscriber, "tcp://localhost:5556");
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0);
    
    // Process live messages
    while (1) {
        zmsg_t *message = zmsg_recv(subscriber);
        const char *data = zmsg_popstr(message);
        printf("Live: %s\n", data);
        zmsg_destroy(&message);
    }
    
    zmq_close(catchup);
    zmq_close(subscriber);
    zmq_term(context);
    return 0;
}
```

### Key Points

- Late subscribers first request historical data via REQ/REP
- Publisher maintains rolling window of recent messages
- After catchup, subscriber connects to live PUB stream
- Trade-off: memory usage for message retention

---

## Service Orchestration (Majordomo Protocol)

MDP provides a framework for building service-oriented architectures.

### Architecture

```
[Client] --> [MDP Broker] <-- [Service 1]
                    |
                    +--> [Service 2]
                    |
                    +--> [Service 3]
```

### MDP Message Format

```
[SERVICE_NAME][REQUEST_ID][MESSAGE]
```

### Simple Service Implementation

```c
#include <czmq.h>

void service_worker(void *socket, const char *service_name) {
    while (1) {
        zmsg_t *request = zmsg_recv(socket);
        
        // Parse MDP envelope
        const char *service = zmsg_popstr(request);
        const char *client_id = zmsg_popstr(request);
        const char *request_id = zmsg_popstr(request);
        const char *command = zmsg_popstr(request);
        
        printf("Service %s received: %s\n", service, command);
        
        // Build response
        zmsg_t *reply = zmsg_new();
        zmsg_addstr(reply, service_name);      // Service name
        zmsg_addstr(reply, client_id);          // Client ID
        zmsg_addstr(reply, request_id);         // Request ID
        zmsg_addstr(reply, "OK");               // Status
        zmsg_addstr(reply, "Response data");    // Response body
        
        zmsg_send(&reply, socket);
        
        zmsg_destroy(&request);
    }
}

int main(void) {
    void *context = zmq_init(1);
    void *service_socket = zmq_socket(context, ZMQ_DEALER);
    zmq_connect(service_socket, "tcp://localhost:5555");  // Broker
    
    service_worker(service_socket, "EXAMPLE");
    
    zmq_close(service_socket);
    zmq_term(context);
    return 0;
}
```

### Key Points

- Services register with broker and receive routed requests
- Broker handles service discovery and load balancing
- Standardized message envelope for interoperability
- See RFC 7/MDP for complete specification

---

## Device Pattern (zmq_proxy)

ZeroMQ provides built-in proxy functionality for building devices.

### Forwarder Device

```c
#include <czmq.h>

int main(void) {
    void *context = zmq_init(1);
    
    // Create sockets
    void *frontend = zmq_socket(context, ZMQ_ROUTER);
    zmq_bind(frontend, "tcp://*:5559");
    
    void *backend = zmq_socket(context, ZMQ_DEALER);
    zmq_bind(backend, "tcp://*:5560");
    
    // Create proxy (runs in current thread)
    zproxy_t *proxy = zproxy_new(frontend, backend, NULL);
    zproxy_set_terminate_on_null(proxy);  // Stop on null message
    
    // Run proxy (blocks)
    zproxy_start(proxy);
    
    // Cleanup
    zproxy_destroy(&proxy);
    zmq_close(frontend);
    zmq_close(backend);
    zmq_term(context);
    return 0;
}
```

### Custom Proxy with Logic

```c
int main(void) {
    void *context = zmq_init(1);
    
    void *frontend = zmq_socket(context, ZMQ_ROUTER);
    zmq_bind(frontend, "tcp://*:5559");
    
    void *backend = zmq_socket(context, ZMQ_DEALER);
    zmq_bind(backend, "tcp://*:5560");
    
    void *monitor = zmq_socket(context, ZMQ_PUB);
    zmq_bind(monitor, "tcp://*:5561");
    
    // Manual proxy with monitoring
    while (1) {
        zmq_pollitem_t items[] = {
            {frontend, 0, ZMQ_POLLIN, 0},
            {backend, 0, ZMQ_POLLIN, 0}
        };
        
        int rc = zmq_poll(items, 2, -1);
        if (rc == -1) break;
        
        if (items[0].revents & ZMQ_POLLIN) {
            // Forward frontend -> backend
            zmsg_t *message = zmsg_recv(frontend);
            
            // Log for monitoring
            zmsg_t *log = zmsg_dup(message);
            zmsg_send(&log, monitor);
            
            zmsg_send(&message, backend);
        }
        
        if (items[1].revents & ZMQ_POLLIN) {
            // Forward backend -> frontend
            zmsg_t *message = zmsg_recv(backend);
            zmsg_send(&message, frontend);
        }
    }
    
    zmq_close(frontend);
    zmq_close(backend);
    zmq_close(monitor);
    zmq_term(context);
    return 0;
}
```

### Key Points

- `zmq_proxy()` automatically forwards messages between sockets
- Custom proxies can add logging, filtering, transformation
- Use `zmq_proxy_destroy()` to stop proxy
- Null message terminates proxy (set with ZMQ_XREQ)

---

## Multicast Pattern

Using NORM (reliable multicast) or multicast-capable transports.

### Requirements

- Network must support IP multicast
- Use `tcp-mcast://` or `epgm://` transport
- Publisher uses PUB, subscribers use SUB

### Example

```c
// Publisher with multicast
void *pub = zmq_socket(context, ZMQ_PUB);
zmq_bind(pub, "epgm://224.143.0.1:5556");  // Multicast address

// Subscriber
void *sub = zmq_socket(context, ZMQ_SUB);
zmq_connect(sub, "epgm://224.143.0.1:5556");
zmq_setsockopt(sub, ZMQ_SUBSCRIBE, "", 0);
```

### Key Points

- Efficient for one-to-many distribution
- Reduces bandwidth compared to unicast
- Requires network infrastructure support
- EPGM (Extended PGm) provides reliability

---

## Best Practices

### Pattern Selection Guide

| Use Case | Recommended Pattern |
|----------|---------------------|
| Simple RPC | REQ/REP |
| Load-balanced workers | PUSH/PULL or DEALER/ROUTER |
| Event notification | PUB/SUB |
| Reliable pub-sub | PUB/SUB + catchup (REQ/REP) |
| Service architecture | MDP with DEALER/ROUTER |
| Simple 1:1 comms | PAIR (inproc only) |
| Building brokers | XPUB/XSUB or zmq_proxy |

### Common Pitfalls

1. **PUSH blocking**: If no PULL connected, PUSH blocks forever. Set `ZMQ_LINGER`.
2. **REQ state machine**: Must alternate send/recv strictly. Use DEALER for flexibility.
3. **SUB late subscription**: Subscribers miss messages before subscription. Use catchup pattern.
4. **ROUTER identity**: Always include identity as first frame when sending to ROUTER.
5. **Memory exhaustion**: Set HWM limits to prevent unbounded queue growth.

### Performance Tips

1. **Batch small messages**: Combine multiple logical messages into one send
2. **Use inproc for same-process**: Much faster than TCP or IPC
3. **Tune buffer sizes**: Increase ZMQ_SNDBUF/ZMQ_RCVBUF for high throughput
4. **Avoid unnecessary copies**: Use zframe_t for zero-copy when possible
5. **Connection pooling**: Reuse connections instead of creating new ones

---

## See Also

- [Socket Patterns](01-socket-patterns.md) - Basic socket types and behavior
- [Architecture](03-architecture.md) - How patterns work internally
- [Performance](06-performance.md) - Tuning for high throughput
- [FAQ](07-faq-troubleshooting.md) - Common pattern issues
