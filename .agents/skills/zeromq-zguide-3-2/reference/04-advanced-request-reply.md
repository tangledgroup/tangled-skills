# Advanced Request-Reply Patterns

Comprehensive guide to advanced request-reply patterns from Chapter 3 of the ZGuide, including DEALER/ROUTER sockets, load balancing, and custom routing strategies.

## The Request-Reply Mechanisms

### REQ/REP Limitations

Basic REQ/REP sockets have strict constraints:
- **Strict alternation**: Must send-receive-send-receive in order
- **No flexibility**: Can't send multiple requests before receiving replies
- **Single peer**: Each REQ connects to one REP at a time
- **Blocking behavior**: Limited control over timing

### DEALER/ROUTER Advantages

Advanced sockets provide more flexibility:
- **Any order**: Send and receive in any sequence
- **Multiple peers**: Connect to many endpoints simultaneously
- **Custom routing**: Control message distribution logic
- **Identity management**: Built-in client identification

## Exploring ROUTER Sockets

ROUTER sockets manage multiple client connections with automatic identity handling.

### Identity Frames

Every message from a ROUTER includes an identity frame:

```
[identity][delimiter][message-parts...]
```

**Receiving with ROUTER:**
```python
import zmq

context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:5555")

while True:
    # First frame is client identity
    identity = router.recv()
    
    # Second frame is message delimiter (for REQ compatibility)
    delimiter = router.recv()
    
    # Third+ frames are actual message
    request = router.recv()
    
    print(f"From {identity}: {request}")
    
    # Route back to same client
    router.send_multipart([identity, delimiter, b"Response"])
```

### Setting Custom Identities

DEALER sockets can use custom identities:

```python
import zmq

context = zmq.Context()
dealer = context.socket(zmq.DEALER)
dealer.connect("tcp://localhost:5555")

# Set custom identity (must be unique per connection)
dealer.setsockopt(zmq.IDENTITY, b"MyClient123")

# Send messages
dealer.send(b"Hello from custom identity client")
response = dealer.recv()
print(response)
```

**ROUTER side:**
```python
import zmq

context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:5555")

while True:
    # Receive multipart message
    frames = []
    while True:
        frame = router.recv()
        frames.append(frame)
        if not router.getsockopt(zmq.RCVMORE):
            break
    
    # First frame is identity
    identity = frames[0]
    message = b''.join(frames[1:])
    
    print(f"Client {identity} sent: {message}")
    
    # Send response
    router.send_multipart([identity, b"Response"])
```

## The Load Balancing Pattern

Load balancing distributes work evenly across multiple workers.

### Round-Robin Load Balancing

DEALER sockets automatically distribute messages in round-robin fashion.

**Ventilator (work distributor):**
```python
import zmq
import time

context = zmq.Context()
ventilator = context.socket(zmq.DEALER)
ventilator.bind("tcp://*:5000")

print("Sending tasks...")
for i in range(100):
    ventilator.send(f"Task {i}".encode())
    time.sleep(0.1)
```

**Workers (task processors):**
```python
import zmq
import time
import sys

context = zmq.Context()
worker = context.socket(zmq.DEALER)
worker.connect("tcp://localhost:5000")

# Set identity for this worker
worker.setsockopt(zmq.IDENTITY, f"Worker-{sys.argv[1]}".encode())

print(f"Worker {sys.argv[1]} starting...")

tasks_processed = 0
while True:
    task = worker.recv()
    print(f"Worker {sys.argv[1]} processing: {task}")
    
    # Simulate work
    time.sleep(0.5)
    
    tasks_processed += 1
    
    if tasks_processed >= 10:  # Process 10 tasks then exit
        print(f"Worker {sys.argv[1]} done, processed {tasks_processed} tasks")
        break
```

### Key Points

**Round-Robin Distribution:**
- DEALER sends to next worker in rotation
- Automatic load balancing across workers
- No central coordination needed

**Identity Management:**
- Each worker needs unique identity
- ROUTER uses identity to route responses
- Identities are byte strings, must be unique

## Router-to-REQ Pattern

Connecting ROUTER sockets to REQ sockets requires handling the identity frame.

### Problem Statement

REQ sockets automatically add identity frames, but ROUTER expects them explicitly:

```
REQ sends: [implicit-identity][message]
ROUTER receives: [identity][message]
```

### Solution: Message Wrapping

**Worker (REQ socket):**
```python
import zmq

context = zmq.Context()
worker = context.socket(zmq.REQ)
worker.connect("tcp://localhost:5555")

print("Worker ready...")

for i in range(10):
    worker.send(b"Ready")
    task = worker.recv()
    print(f"Processing: {task}")
    
    # Send result back
    worker.send(b"Done")
```

**Ventilator (ROUTER socket):**
```python
import zmq
import time

context = zmq.Context()
ventilator = context.socket(zmq.ROUTER)
ventilator.bind("tcp://*:5555")

print("Connecting to workers...")

# Track connected workers
workers = []

for i in range(5):
    # Receive worker identity
    identity = ventilator.recv()
    workers.append(identity)
    print(f"Worker {identity} connected")

print("Distributing tasks...")

# Round-robin distribution
worker_index = 0
for task_num in range(100):
    # Select next worker
    worker = workers[worker_index % len(workers)]
    
    # Send task with identity frame
    ventilator.send_multipart([worker, b"", f"Task {task_num}".encode()])
    
    worker_index += 1
    
    # Receive result (identity + delimiter + message)
    identity = ventilator.recv()
    delimiter = ventilator.recv()
    result = ventilator.recv()
    
    print(f"Worker {identity} completed task")

print("All tasks distributed")
```

### Key Implementation Details

**Identity Frame:**
- First frame sent to ROUTER is the target identity
- Empty frame (delimiter) maintains REQ compatibility
- Message follows delimiter

**Worker Tracking:**
- Store worker identities as they connect
- Use round-robin or custom selection logic
- Handle worker disconnection gracefully

## Router-to-DEALER Pattern

When both sides use DEALER/ROUTER, identity management is more straightforward.

### Implementation

**Workers (DEALER sockets):**
```python
import zmq
import sys
import time

context = zmq.Context()
worker = context.socket(zmq.DEALER)
worker.connect("tcp://localhost:5555")

# Set custom identity
worker.setsockopt(zmq.IDENTITY, f"Worker-{sys.argv[1]}".encode())

print(f"Worker {sys.argv[1]} ready")

tasks_done = 0
while True:
    task = worker.recv()
    print(f"Worker {sys.argv[1]} processing: {task}")
    
    # Simulate work
    time.sleep(0.5)
    
    # Send result back
    worker.send(f"Result from Worker-{sys.argv[1]}".encode())
    
    tasks_done += 1
    if tasks_done >= 10:
        print(f"Worker {sys.argv[1]} done")
        break
```

**Ventilator (ROUTER socket):**
```python
import zmq
import time

context = zmq.Context()
ventilator = context.socket(zmq.ROUTER)
ventilator.bind("tcp://*:5555")

print("Starting task distribution...")

# Send tasks in round-robin fashion
for i in range(100):
    ventilator.send(f"Task {i}".encode())
    time.sleep(0.1)

# Collect results
results_received = 0
while results_received < 100:
    # Receive result with identity
    identity = ventilator.recv()
    result = ventilator.recv()
    
    print(f"Got result from {identity}: {result}")
    results_received += 1

print("All results collected")
```

## Custom Routing Strategies

Beyond round-robin, implement custom routing logic.

### Priority-Based Routing

Route messages based on priority levels:

```python
import zmq
import heapq

class PriorityRouter:
    def __init__(self):
        self.context = zmq.Context()
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind("tcp://*:5555")
        
        # Priority queues per worker capability
        self.workers = {}  # identity -> capabilities
        self.priority_queue = []  # heap of (priority, task)
    
    def register_worker(self, identity, capabilities):
        """Worker registers with capabilities"""
        self.workers[identity] = capabilities
        print(f"Worker {identity} registered with capabilities: {capabilities}")
    
    def route_task(self, task, priority, required_capability=None):
        """Route task to appropriate worker"""
        # Add to priority queue
        heapq.heappush(self.priority_queue, (priority, task))
        
        # Find suitable worker
        if required_capability:
            suitable = [w for w, caps in self.workers.items() 
                       if required_capability in caps]
        else:
            suitable = list(self.workers.keys())
        
        if suitable:
            worker = suitable[0]  # Simple selection
            self.router.send_multipart([worker, task])
            print(f"Routed {task} to {worker}")
    
    def run(self):
        """Main router loop"""
        while True:
            if self.router.poll(1000, zmq.POLLIN):
                # Handle worker registration or results
                frames = []
                while True:
                    frame = self.router.recv()
                    frames.append(frame)
                    if not self.router.getsockopt(zmq.RCVMORE):
                        break
                
                identity = frames[0]
                message = frames[1] if len(frames) > 1 else b""
                
                if message == b"REGISTER":
                    # Next frame contains capabilities
                    caps = frames[2].decode() if len(frames) > 2 else ""
                    self.register_worker(identity, caps)
                else:
                    print(f"Result from {identity}: {message}")

# Usage
router = PriorityRouter()
router.run()
```

### Least-Connections Routing

Route to worker with fewest active connections:

```python
import zmq
from collections import defaultdict

class LeastConnectionsRouter:
    def __init__(self):
        self.context = zmq.Context()
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind("tcp://*:5555")
        
        # Track active connections per worker
        self.active_connections = defaultdict(int)
        self.workers = set()
    
    def select_worker(self):
        """Select worker with least active connections"""
        if not self.workers:
            return None
        
        # Find worker with minimum active connections
        min_connections = min(self.active_connections[w] for w in self.workers)
        suitable = [w for w in self.workers 
                   if self.active_connections[w] == min_connections]
        
        import random
        return random.choice(suitable)  # Random among tied workers
    
    def run(self):
        """Main router loop"""
        while True:
            if self.router.poll(1000, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.router.recv()
                    frames.append(frame)
                    if not self.router.getsockopt(zmq.RCVMORE):
                        break
                
                identity = frames[0]
                message = frames[1] if len(frames) > 1 else b""
                
                # Track new worker connections
                if identity not in self.workers:
                    self.workers.add(identity)
                    print(f"New worker connected: {identity}")
                
                # Decrement active connections (task completed)
                self.active_connections[identity] -= 1
                
                # Send next task to least-connected worker
                worker = self.select_worker()
                if worker:
                    task = b"New-Task"
                    self.active_connections[worker] += 1
                    self.router.send_multipart([worker, task])

# Usage
router = LeastConnectionsRouter()
router.run()
```

## Handling Worker Failures

Gracefully handle worker disconnection and failure.

### Timeout-Based Detection

```python
import zmq
import time

class FaultTolerantRouter:
    def __init__(self, timeout=30):
        self.context = zmq.Context()
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind("tcp://*:5555")
        
        self.workers = {}  # identity -> last_seen_time
        self.timeout = timeout
    
    def is_worker_alive(self, identity):
        """Check if worker is still active"""
        if identity not in self.workers:
            return False
        
        last_seen = self.workers[identity]
        return (time.time() - last_seen) < self.timeout
    
    def cleanup_dead_workers(self):
        """Remove dead workers from tracking"""
        dead_workers = []
        
        for identity, last_seen in self.workers.items():
            if not self.is_worker_alive(identity):
                dead_workers.append(identity)
                print(f"Worker {identity} timed out, removing")
        
        for identity in dead_workers:
            del self.workers[identity]
    
    def run(self):
        """Main router loop with failure detection"""
        while True:
            # Check for dead workers periodically
            self.cleanup_dead_workers()
            
            if self.router.poll(1000, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.router.recv()
                    frames.append(frame)
                    if not self.router.getsockopt(zmq.RCVMORE):
                        break
                
                identity = frames[0]
                
                # Update last seen time
                self.workers[identity] = time.time()
                
                if identity not in self.workers:
                    self.workers[identity] = time.time()
                    print(f"New worker: {identity}")
                
                # Process message and route response
                # ... implementation depends on use case

# Usage
router = FaultTolerantRouter(timeout=30)
router.run()
```

## Multipart Message Handling

Advanced patterns often require complex multipart messages.

### Building Multipart Messages

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.DEALER)

# Method 1: send_multipart (Python)
socket.send_multipart([b"frame1", b"frame2", b"frame3"])

# Method 2: Multiple send calls with SNDMORE
socket.send(b"frame1", zmq.SNDMORE)
socket.send(b"frame2", zmq.SNDMORE)
socket.send(b"frame3")  # Last frame without SNDMORE

# Method 3: Mixed content
socket.send_multipart([
    b"header",
    b"",  # Delimiter
    {"key": "value"}.encode(),  # JSON payload
    b"footer"
])
```

### Parsing Multipart Messages

```python
import zmq

context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:5555")

while True:
    if router.poll(1000, zmq.POLLIN):
        # Receive all frames
        frames = []
        while True:
            frame = router.recv()
            frames.append(frame)
            if not router.getsockopt(zmq.RCVMORE):
                break
        
        # Parse based on protocol
        identity = frames[0]
        
        if len(frames) >= 3:
            delimiter = frames[1]
            message = frames[2]
            
            # Additional frames if present
            extra_frames = frames[3:] if len(frames) > 3 else []
            
            print(f"From {identity}: {message}")
            if extra_frames:
                print(f"Extra frames: {extra_frames}")
```

## Best Practices

1. **Always handle identity frames** - ROUTER requires explicit identity management
2. **Use unique identities** - Each connection needs distinct identifier
3. **Implement timeout handling** - Detect and handle worker failures
4. **Track worker state** - Monitor connections for load balancing
5. **Handle multipart carefully** - ZeroMQ uses frames internally
6. **Consider message ordering** - DEALER/ROUTER don't guarantee order
7. **Test reconnection behavior** - Verify worker recovery works

## Common Pitfalls

**Identity Confusion:**
- ROUTER identity is first frame, not metadata
- Must include identity when sending to ROUTER
- Empty delimiter needed for REQ compatibility

**Blocking Issues:**
- DEALER/ROUTER don't have strict alternation
- Can still block if buffer fills up
- Use polling for non-blocking operations

**Worker Tracking:**
- Workers can disconnect without notice
- Implement heartbeat or timeout detection
- Clean up dead worker entries

## Next Steps

- [Reliable Request-Reply](05-reliable-request-reply.md) - Fault tolerance patterns
- [Distributed Frameworks](08-distributed-framework.md) - Complete system design
- [Advanced Architecture](07-advanced-architecture.md) - Large-scale patterns
