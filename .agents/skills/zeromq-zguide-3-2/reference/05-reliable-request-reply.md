# Reliable Request-Reply Patterns

Comprehensive guide to reliable messaging patterns from Chapter 4 of the ZGuide, including fault tolerance, the Lazy Pirate pattern, and production-ready request-reply architectures.

## What is Reliability?

Reliability in distributed systems means handling failures gracefully:
- **Client failures**: Clients crash before sending or receiving messages
- **Server failures**: Servers crash during processing
- **Network failures**: Messages lost in transit
- **Timeout scenarios**: Operations taking too long

### ZeroMQ's Default Behavior

Basic ZeroMQ patterns provide:
- **No delivery guarantees** - Fire-and-forget semantics
- **Automatic reconnection** - But messages in flight are lost
- **No acknowledgments** - Sender doesn't know if message arrived
- **No retry logic** - Failed operations must be handled by application

## Designing Reliability

### Key Principles

1. **Expect failures** - Assume components will crash
2. **Implement timeouts** - Prevent indefinite blocking
3. **Add retry logic** - Recover from transient failures
4. **Track state** - Know what was sent and what was received
5. **Handle partial failures** - Some operations may succeed, others fail

### Reliability Tradeoffs

| Aspect | Basic Pattern | Reliable Pattern |
|--------|--------------|------------------|
| Complexity | Low | High |
| Performance | Maximum | Slightly reduced |
| Fault tolerance | None | Full |
| Message ordering | Guaranteed (REQ/REP) | Application-managed |
| Delivery guarantee | Best effort | Configurable |

## Client-Side Reliability (Lazy Pirate Pattern)

The Lazy Pirate pattern implements client-side reliability with timeout and retry logic.

### Problem Statement

Basic REQ socket issues:
1. Blocks indefinitely if server doesn't respond
2. No way to detect server failure
3. Cannot retry failed requests
4. Crashes if server is unavailable

### Lazy Pirate Client Implementation

**Python:**
```python
import zmq
import sys
import time

def lazy_pirate_client():
    """Client with timeout and retry logic"""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    
    # Set timeout to prevent indefinite blocking
    socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
    
    print("Connecting to servers...")
    
    request_number = 0
    failures = 0
    total_requests = 20
    
    while request_number < total_requests:
        print(f"Sending request {request_number}...")
        socket.send(b"Hello")
        
        # Wait for response with timeout
        try:
            message = socket.recv()
            print(f"Server replied: {message}")
            request_number += 1
            
            # Reset failure counter on success
            failures = 0
            
        except zmq.Again:
            # Timeout occurred
            failures += 1
            print(f"Server seems to be offline, retrying... ({failures} failures)")
            
            if failures > 5:
                print("Giving up...")
                break
            
            # Wait before retry
            time.sleep(2)
    
    socket.close()
    context.term()

if __name__ == "__main__":
    lazy_pirate_client()
```

**C:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zmq.h>

int main (void)
{
    void *context = zmq_init (1);
    void *requester = zmq_socket (context, ZMQ_REQ);
    zmq_connect (requester, "tcp://localhost:5555");
    
    int request_nbr = 0;
    int retries = 0;
    
    while (request_nbr < 20) {
        printf ("Connecting to servers...\n");
        
        // Send request
        zmq_send (requester, "Hello", 5, 0);
        
        // Wait for response with timeout
        zmq_setsockopt (requester, ZMQ_RCVMORE, &retries, sizeof(retries));
        
        char buffer [10];
        int rc = zmq_recv (requester, buffer, 10, ZMQ_DONTWAIT);
        
        if (rc == -1 && zmq_errno () == EAGAIN) {
            // Timeout - server not responding
            retries++;
            printf ("Server seems to be offline, retrying...\n");
            
            if (retries > 5) {
                printf ("Giving up...\n");
                break;
            }
            
            sleep (2);
        } else {
            // Got response
            printf ("Server replied: %s\n", buffer);
            request_nbr++;
            retries = 0;
        }
    }
    
    zmq_close (requester);
    zmq_term (context);
    return 0;
}
```

### Lazy Pirate Server Implementation

**Python:**
```python
import zmq
import time
import random

def lazy_pirate_server():
    """Server that simulates failures"""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    
    print("Server starting...")
    
    while True:
        # Receive request
        message = socket.recv()
        print(f"Received: {message}")
        
        # Simulate random slow processing or crash
        if random.randint(1, 5) == 1:
            print("Simulating slow response...")
            time.sleep(2)  # Slow response
        
        if random.randint(1, 10) == 1:
            print("Simulating crash!")
            break  # Server "crashes"
        
        # Send response
        socket.send(b"World")

if __name__ == "__main__":
    lazy_pirate_server()
```

### Key Implementation Details

**Timeout Configuration:**
```python
socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
socket.setsockopt(zmq.SNDTIMEO, 1000)  # 1 second send timeout
```

**Retry Logic:**
- Track failure count
- Give up after N consecutive failures
- Wait between retries to avoid thundering herd

**Reconnection:**
- ZeroMQ automatically reconnects
- But in-flight messages are lost
- Application must implement retry at message level

## Server-Side Reliability (Simple Pirate Pattern)

Server-side reliability focuses on graceful failure and recovery.

### Simple Pirate Queue

Basic work distribution without reliability:

```python
import zmq

def simple_pirate_queue():
    """Queue distributes tasks to workers"""
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5559")
    
    backend = context.socket(zmq.DEALER)
    backend.bind("tcp://*:5560")
    
    # Simple proxy
    zmq.proxy(frontend, backend)

def simple_pirate_worker():
    """Worker processes tasks"""
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect("tcp://localhost:5560")
    
    print("Worker ready...")
    
    while True:
        # Receive task (identity + message)
        frames = []
        while True:
            frame = socket.recv()
            frames.append(frame)
            if not socket.getsockopt(zmq.RCVMORE):
                break
        
        # Process task
        task = frames[0]  # First frame after identity
        print(f"Processing: {task}")
        
        # Send result back
        socket.send(b"Done")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "queue":
        simple_pirate_queue()
    else:
        simple_pirate_worker()
```

### Issues with Simple Pattern

1. **No failure detection** - Dead workers not detected
2. **Task loss** - Tasks sent to dead workers are lost
3. **No recovery** - Failed tasks aren't retried
4. **Resource waste** - Workers may process stale tasks

## Reliable Queuing (LRU Pattern)

The Last-Recently-Used (LRU) pattern implements reliable work distribution with worker registration and health checking.

### LRU Route Broker

```python
import zmq
import time
from collections import deque

class LruRouteBroker:
    def __init__(self):
        self.context = zmq.Context()
        
        # Frontend connects to clients (ROUTER)
        self.frontend = self.context.socket(zmq.ROUTER)
        self.frontend.bind("tcp://*:5559")
        
        # Backend connects to workers (DEALER)
        self.backend = self.context.socket(zmq.DEALER)
        self.backend.bind("tcp://*:5560")
        
        # Track worker state
        self.workers = {}  # identity -> last_heartbeat
        self.ready_queue = deque()  # Workers ready for tasks
        
        # Client tracking
        self.clients = {}  # identity -> pending_task
    
    def run(self):
        """Main broker loop"""
        print("Broker starting...")
        
        while True:
            zmq.poll([self.frontend, self.backend], 1000)
            
            # Handle frontend (clients)
            if self.frontend.poll(0, zmq.POLLIN):
                self.handle_frontend()
            
            # Handle backend (workers)
            if self.backend.poll(0, zmq.POLLIN):
                self.handle_backend()
    
    def handle_frontend(self):
        """Handle client messages"""
        frames = []
        while True:
            frame = self.frontend.recv()
            frames.append(frame)
            if not self.frontend.getsockopt(zmq.RCVMORE):
                break
        
        client_id = frames[0]
        message = b''.join(frames[1:])
        
        # Route to next ready worker
        if self.ready_queue:
            worker_id = self.ready_queue.popleft()
            
            # Send task to worker with client identity
            self.backend.send_multipart([worker_id, client_id, message])
            
            # Track pending task
            self.clients[client_id] = {
                'task': message,
                'worker': worker_id,
                'time': time.time()
            }
    
    def handle_backend(self):
        """Handle worker messages"""
        frames = []
        while True:
            frame = self.backend.recv()
            frames.append(frame)
            if not self.backend.getsockopt(zmq.RCVMORE):
                break
        
        worker_id = frames[0]
        
        if len(frames) >= 2:
            # Worker registration or heartbeat
            command = frames[1]
            
            if command == b'READY':
                # Worker is ready for tasks
                self.workers[worker_id] = time.time()
                self.ready_queue.append(worker_id)
                print(f"Worker {worker_id} registered")
            
            elif command == b'DONE':
                # Task completed, send result to client
                if len(frames) >= 4:
                    client_id = frames[2]
                    result = frames[3]
                    
                    self.frontend.send_multipart([client_id, result])
                    
                    # Remove from pending tasks
                    if client_id in self.clients:
                        del self.clients[client_id]
                    
                    # Worker is ready again
                else:
                    # Just heartbeat
                    self.workers[worker_id] = time.time()
        
        # Clean up dead workers
        self.cleanup_dead_workers()
    
    def cleanup_dead_workers(self):
        """Remove workers that haven't sent heartbeats"""
        current_time = time.time()
        dead_workers = []
        
        for worker_id, last_heartbeat in self.workers.items():
            if current_time - last_heartbeat > 30:  # 30 second timeout
                dead_workers.append(worker_id)
                print(f"Worker {worker_id} timed out")
        
        for worker_id in dead_workers:
            del self.workers[worker_id]
            # Remove from ready queue
            if worker_id in self.ready_queue:
                self.ready_queue.remove(worker_id)

# Usage
broker = LruRouteBroker()
broker.run()
```

### LRU Worker Implementation

```python
import zmq
import time
import sys
import random

def lru_worker():
    """Worker with heartbeat and task acknowledgment"""
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect("tcp://localhost:5560")
    
    # Set unique identity
    worker_id = f"Worker-{sys.argv[1]}".encode() if len(sys.argv) > 1 else b"Worker-1"
    socket.setsockopt(zmq.IDENTITY, worker_id)
    
    print(f"{worker_id} starting...")
    
    tasks_processed = 0
    
    while True:
        # Send READY signal
        socket.send_multipart([b'READY'])
        
        # Wait for task with timeout
        if socket.poll(1000, zmq.POLLIN):
            frames = []
            while True:
                frame = socket.recv()
                frames.append(frame)
                if not socket.getsockopt(zmq.RCVMORE):
                    break
            
            # Parse task (client_id + message)
            client_id = frames[0]
            task = frames[1] if len(frames) > 1 else b""
            
            print(f"{worker_id} processing task from {client_id}: {task}")
            
            # Simulate work
            time.sleep(0.5)
            
            # Simulate random crash
            if random.randint(1, 20) == 1:
                print(f"{worker_id} crashing!")
                break
            
            # Send result back
            socket.send_multipart([b'DONE', client_id, b'Result'])
            
            tasks_processed += 1
            
            if tasks_processed >= 10:
                print(f"{worker_id} done processing {tasks_processed} tasks")
                break
        else:
            # Timeout - send heartbeat
            socket.send_multipart([b'HEARTBEAT'])

if __name__ == "__main__":
    lru_worker()
```

### LRU Pattern Benefits

1. **Worker registration** - Broker knows which workers are available
2. **Health monitoring** - Heartbeats detect dead workers
3. **Task tracking** - Know which worker has which task
4. **Automatic recovery** - Dead workers removed, tasks can be retried
5. **Load balancing** - Round-robin across ready workers

## Client-Server Reliability (Full Pattern)

Complete reliable request-reply with both client and server reliability.

### Reliable Client

```python
import zmq
import time

class ReliableClient:
    def __init__(self, server_address="tcp://localhost:5559"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(server_address)
        
        # Set unique identity
        import uuid
        self.identity = f"Client-{uuid.uuid4().hex[:8]}".encode()
        self.socket.setsockopt(zmq.IDENTITY, self.identity)
        
        # Configure timeouts
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
        self.socket.setsockopt(zmq.SNDTIMEO, 5000)
    
    def request(self, message, retries=3):
        """Send request with retry logic"""
        for attempt in range(retries):
            try:
                print(f"Sending request (attempt {attempt + 1})...")
                self.socket.send(message)
                
                # Wait for response
                response = self.socket.recv()
                print(f"Got response: {response}")
                return response
                
            except zmq.Again:
                print(f"Timeout on attempt {attempt + 1}")
                
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retries exhausted")
                    return None
        
        return None
    
    def close(self):
        self.socket.close()
        self.context.term()

# Usage
client = ReliableClient()
response = client.request(b"Hello Server")
client.close()
```

### Reliable Server

```python
import zmq
import time
import random

class ReliableServer:
    def __init__(self, address="tcp://*:5559"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        
        # Track client state
        self.clients = {}
    
    def run(self):
        """Main server loop"""
        print("Server starting...")
        
        while True:
            if self.socket.poll(1000, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.socket.recv()
                    frames.append(frame)
                    if not self.socket.getsockopt(zmq.RCVMORE):
                        break
                
                client_id = frames[0]
                message = b''.join(frames[1:])
                
                print(f"Request from {client_id}: {message}")
                
                # Track client activity
                self.clients[client_id] = time.time()
                
                # Simulate processing (with occasional failure)
                if random.randint(1, 10) == 1:
                    print("Simulating slow processing...")
                    time.sleep(3)
                
                # Send response
                response = f"Response to {message}".encode()
                self.socket.send_multipart([client_id, response])
                
                # Clean up old client entries
                self.cleanup_old_clients()
    
    def cleanup_old_clients(self):
        """Remove clients that haven't communicated recently"""
        current_time = time.time()
        dead_clients = []
        
        for client_id, last_seen in self.clients.items():
            if current_time - last_seen > 60:  # 1 minute timeout
                dead_clients.append(client_id)
        
        for client_id in dead_clients:
            del self.clients[client_id]
            print(f"Client {client_id} removed (inactive)")

# Usage
server = ReliableServer()
server.run()
```

## Heartbeat Patterns

Heartbeats enable detection of dead peers without waiting for timeouts.

### Implementation

**Worker with Heartbeat:**
```python
import zmq
import time

class HeartbeatWorker:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect("tcp://localhost:5560")
        
        self.heartbeat_interval = 1  # Second
        self.last_heartbeat = 0
    
    def send_heartbeat(self):
        """Send periodic heartbeat"""
        current_time = time.time()
        
        if current_time - self.last_heartbeat > self.heartbeat_interval:
            self.socket.send_multipart([b'HEARTBEAT'])
            self.last_heartbeat = current_time
    
    def run(self):
        """Main worker loop"""
        while True:
            # Send heartbeat periodically
            self.send_heartbeat()
            
            # Wait for work with short timeout
            if self.socket.poll(500, zmq.POLLIN):
                task = self.socket.recv()
                print(f"Processing: {task}")
                
                # Process task
                time.sleep(0.5)
                
                # Send result
                self.socket.send(b"Done")
            else:
                # No work available, just heartbeat
                pass

# Usage
worker = HeartbeatWorker()
worker.run()
```

## Monitoring and Metrics

Track system health with metrics collection.

### Basic Metrics Collection

```python
import zmq
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.context = zmq.Context()
        
        # Monitor socket for ZeroMQ events
        monitor = self.context.socket(zmq.PUB)
        monitor.bind("tcp://*:5565")
        
        self.metrics = {
            'requests': 0,
            'responses': 0,
            'timeouts': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def record_request(self):
        self.metrics['requests'] += 1
    
    def record_response(self):
        self.metrics['responses'] += 1
    
    def record_timeout(self):
        self.metrics['timeouts'] += 1
    
    def get_stats(self):
        """Get current statistics"""
        uptime = time.time() - self.metrics['start_time']
        
        return {
            'uptime': uptime,
            'requests': self.metrics['requests'],
            'responses': self.metrics['responses'],
            'success_rate': (self.metrics['responses'] / max(1, self.metrics['requests'])) * 100,
            'timeouts': self.metrics['timeouts'],
            'errors': self.metrics['errors'],
            'throughput': self.metrics['responses'] / max(1, uptime)
        }

# Usage in broker
metrics = MetricsCollector()

# In request handling:
metrics.record_request()
# ... process ...
metrics.record_response()

# Print stats periodically
while True:
    time.sleep(10)
    print(metrics.get_stats())
```

## Best Practices

1. **Always implement timeouts** - Prevent indefinite blocking
2. **Use retry logic with limits** - Avoid infinite retry loops
3. **Track message state** - Know what was sent and acknowledged
4. **Implement heartbeats** - Detect dead peers quickly
5. **Monitor system metrics** - Track health and performance
6. **Test failure scenarios** - Verify recovery works correctly
7. **Log important events** - Enable debugging and auditing

## Troubleshooting

### Common Issues

**Timeouts not working:**
- Check timeout value is in milliseconds
- Verify socket option is set before connecting
- Use zmq.poll() for more control

**Worker not detected as dead:**
- Increase heartbeat frequency
- Reduce timeout threshold
- Check network connectivity

**Message ordering issues:**
- Use sequence numbers in messages
- Track message state explicitly
- Consider using REQ/REP for strict ordering

**Reconnection storms:**
- Implement exponential backoff
- Add random jitter to reconnection attempts
- Monitor connection rate

## Next Steps

- [Advanced Pub-Sub](03-advanced-pubsub.md) - Pub-sub reliability patterns
- [Distributed Frameworks](08-distributed-framework.md) - Complete system architecture
- [Advanced Architecture](07-advanced-architecture.md) - Large-scale patterns
