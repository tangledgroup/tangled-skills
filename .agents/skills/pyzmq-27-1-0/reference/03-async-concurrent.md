# Async and Concurrent Operations

Comprehensive guide to using pyzmq with asyncio, threading, multiprocessing, and polling mechanisms for concurrent I/O operations.

## Asyncio Integration

PyZMQ provides native asyncio support through `zmq.asyncio` module (Python 3.7+).

### Basic Async Socket Usage

```python
import asyncio
import zmq.asyncio

async def simple_worker():
    """Basic async worker using REP socket"""
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    await socket.bind("tcp://*:5555")
    
    print("Worker started, waiting for requests...")
    
    try:
        while True:
            # Async receive (non-blocking)
            request = await socket.recv_string()
            print(f"Received: {request}")
            
            # Simulate processing
            await asyncio.sleep(0.1)
            
            # Async send
            response = f"Processed: {request}"
            await socket.send_string(response)
    finally:
        await socket.close()
        context.term()

# Run the worker
# asyncio.run(simple_worker())
```

### Async Client-Server Example

```python
import asyncio
import zmq.asyncio

async def server():
    """Async ROUTER server handling multiple clients"""
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.ROUTER)
    await socket.bind("tcp://*:5556")
    
    while True:
        # Receive multipart [identity, message]
        identity, message = await socket.recv_multipart()
        client_id = identity.decode('utf-8')
        
        print(f"Client {client_id}: {message.decode()}")
        
        # Send reply with identity
        response = f"Server received your message: {message.decode()}"
        await socket.send_multipart([identity, response.encode()])

async def client(client_id):
    """Async DEALER client"""
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.DEALER)
    await socket.connect("tcp://localhost:5556")
    
    for i in range(3):
        await socket.send_string(f"Message {i} from {client_id}")
        response = await socket.recv_string()
        print(f"{client_id} got: {response}")
        await asyncio.sleep(0.1)
    
    await socket.close()

async def main():
    """Run server and multiple clients concurrently"""
    # Start server in background
    server_task = asyncio.create_task(server())
    
    # Run multiple clients concurrently
    clients = [client(f"Client-{i}") for i in range(3)]
    await asyncio.gather(*clients)
    
    # Cancel server after clients done
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

# asyncio.run(main())
```

### Async Polling with Poller

```python
import asyncio
import zmq.asyncio

async def multi_socket_handler():
    """Handle multiple sockets with async Poller"""
    context = zmq.asyncio.Context()
    
    # Create multiple sockets
    socket1 = context.socket(zmq.PULL)
    await socket1.bind("tcp://*:5557")
    
    socket2 = context.socket(zmq.SUB)
    await socket2.connect("tcp://localhost:5558")
    await socket2.setsockopt_string(zmq.SUBSCRIBE, "")
    
    # Create async poller
    poller = zmq.asyncio.Poller()
    poller.register(socket1, zmq.POLLIN)
    poller.register(socket2, zmq.POLLIN)
    
    while True:
        # Wait for events (async)
        events = await poller.poll(timeout=1000)
        
        for socket, event in events:
            if event & zmq.POLLIN:
                if socket == socket1:
                    message = await socket.recv_string()
                    print(f"PULL received: {message}")
                elif socket == socket2:
                    message = await socket.recv_string()
                    print(f"SUB received: {message}")

# asyncio.run(multi_socket_handler())
```

### Async Context Manager

```python
import asyncio
import zmq.asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_zmq_socket(context, socket_type, *endpoints):
    """Async context manager for sockets"""
    socket = context.socket(socket_type)
    
    for endpoint in endpoints:
        if endpoint.startswith(("tcp://*", "ipc://", "inproc://")):
            await socket.bind(endpoint)
        else:
            await socket.connect(endpoint)
    
    try:
        yield socket
    finally:
        await socket.close()

async def example():
    context = zmq.asyncio.Context()
    
    async with async_zmq_socket(context, zmq.REQ, "tcp://localhost:5559") as socket:
        await socket.send_string("Hello")
        response = await socket.recv_string()
        print(response)

# asyncio.run(example())
```

## Threading Models

### One Context Per Thread

ZeroMQ contexts are not thread-safe. Create one context per thread.

```python
import zmq
import threading
import queue

def worker_thread(thread_id, work_queue, result_queue):
    """Worker thread with its own context"""
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://localhost:5560")
    
    try:
        while True:
            # Check for shutdown signal
            try:
                task = work_queue.get(timeout=1)
                if task is None:  # Shutdown signal
                    break
                
                # Receive and process task from ZMQ
                message = socket.recv_string(flags=zmq.DONTWAIT)
                result = f"Thread {thread_id} processed: {message}"
                result_queue.put(result)
                
            except zmq.Again:
                continue
            except queue.Empty:
                continue
    finally:
        socket.close()
        context.term()

# Create work and result queues
work_queue = queue.Queue()
result_queue = queue.Queue()

# Start worker threads
threads = []
for i in range(4):
    t = threading.Thread(target=worker_thread, args=(i, work_queue, result_queue))
    t.start()
    threads.append(t)

# Main thread sends tasks via ZMQ
context = zmq.Context()
push_socket = context.socket(zmq.PUSH)
push_socket.connect("tcp://localhost:5560")

for i in range(20):
    push_socket.send_string(f"Task {i}")
    work_queue.put(i)  # Signal worker to process

# Shutdown workers
for _ in threads:
    work_queue.put(None)

for t in threads:
    t.join()

# Collect results
while not result_queue.empty():
    print(result_queue.get())
```

### Thread-Safe Socket Wrapper

```python
import zmq
import threading
from typing import Optional

class ThreadSafeSocket:
    """Wrapper providing thread-safe socket access per thread"""
    
    def __init__(self, socket_type, *endpoints):
        self.socket_type = socket_type
        self.endpoints = endpoints
        self._local = threading.local()
        self._lock = threading.Lock()
    
    def _get_socket(self):
        """Get or create thread-local socket"""
        if not hasattr(self._local, 'socket'):
            with self._lock:
                if not hasattr(self._local, 'socket'):
                    context = zmq.Context()
                    socket = context.socket(self.socket_type)
                    
                    for endpoint in self.endpoints:
                        if endpoint.startswith(("tcp://*", "ipc://")):
                            socket.bind(endpoint)
                        else:
                            socket.connect(endpoint)
                    
                    self._local.socket = socket
                    self._local.context = context
        
        return self._local.socket, self._local.context
    
    def send_string(self, data: str) -> None:
        socket, _ = self._get_socket()
        socket.send_string(data)
    
    def recv_string(self, timeout: Optional[int] = None) -> str:
        socket, _ = self._get_socket()
        if timeout:
            socket.setsockopt(zmq.RCVTIMEO, timeout)
        return socket.recv_string()
    
    def close(self):
        """Close thread-local socket"""
        if hasattr(self._local, 'socket'):
            self._local.socket.close()
            self._local.context.term()

# Usage (safe across threads)
shared_socket = ThreadSafeSocket(zmq.PUSH, "tcp://localhost:5561")

def worker():
    shared_socket.send_string("Message from thread")

# Multiple threads can use shared_socket safely
```

## Polling Mechanisms

### zmq.Poller (Synchronous)

Efficiently monitor multiple sockets for I/O events.

```python
import zmq

context = zmq.Context()

# Create sockets to monitor
frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5562")

backend = context.socket(zmq.DEALER)
backend.connect("tcp://localhost:5563")

# Create poller
poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN | zmq.POLLOUT)

# Poll for events
while True:
    # Wait up to 1 second for events
    events = poller.poll(timeout=1000)
    
    if not events:
        print("Timeout - no events")
        continue
    
    for socket, event in events:
        if socket == frontend:
            if event & zmq.POLLIN:
                identity, message = frontend.recv_multipart()
                print(f"Frontend received: {message.decode()}")
                
                # Forward to backend
                backend.send_multipart([b"worker", message])
            
            if event & zmq.POLLOUT:
                print("Frontend ready for sending")
        
        elif socket == backend:
            if event & zmq.POLLIN:
                worker_id, result = backend.recv_multipart()
                print(f"Backend received from {worker_id}: {result.decode()}")
                
                # Send back to frontend
                frontend.send_multipart([identity, result])
```

### Poll Events

| Event | Constant | Description |
|-------|----------|-------------|
| `zmq.POLLIN` | 1 | Data available to read |
| `zmq.POLLOUT` | 2 | Socket ready for writing |
| `zmq.POLLERR` | 8 | Error condition |
| `zmq.POLLPRI` | 4 | High-priority data |

### Advanced Polling Patterns

```python
import zmq

context = zmq.Context()

# Socket with timeout
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5564")
socket.setsockopt(zmq.RCVTIMEO, 1000)

# Method 1: Using poller for multiple sockets
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

sockets = dict(poller.poll(500))  # 500ms timeout

if socket in sockets and sockets[socket] & zmq.POLLIN:
    message = socket.recv_string()
    print(f"Received: {message}")
else:
    print("No message or timeout")

# Method 2: Using socket.poll() for single socket
events = socket.poll(timeout=500, flags=zmq.POLLIN)

if events & zmq.POLLIN:
    message = socket.recv_string()
    print(f"Received: {message}")

# Method 3: Non-blocking with DONTWAIT
try:
    message = socket.recv(flags=zmq.DONTWAIT)
    print(f"Received: {message.decode()}")
except zmq.Again:
    print("No message available")
```

### Select Helper Function

```python
import zmq

context = zmq.Context()

socket1 = context.socket(zmq.PULL)
socket1.bind("tcp://*:5565")

socket2 = context.socket(zmq.SUB)
socket2.connect("tcp://localhost:5566")
socket2.setsockopt_string(zmq.SUBSCRIBE, "")

# Use zmq.select for simple polling
readable, _, _ = zmq.select(
    [socket1, socket2],  # Sockets to read from
    [],                   # Sockets to write to
    [],                   # Sockets to monitor for errors
    timeout=1.0           # Timeout in seconds
)

for socket in readable:
    if socket == socket1:
        message = socket.recv_string()
        print(f"socket1: {message}")
    elif socket == socket2:
        message = socket.recv_string()
        print(f"socket2: {message}")
```

## Multiprocessing

### Shared Context Pattern (Not Recommended)

ZeroMQ contexts cannot be shared across processes. Each process needs its own context.

```python
import zmq
import multiprocessing as mp

def worker_process(task_queue, result_queue):
    """Worker process with independent context"""
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://localhost:5567")
    
    try:
        while True:
            task = task_queue.get()
            if task is None:  # Shutdown signal
                break
            
            message = socket.recv_string(flags=zmq.DONTWAIT)
            result = f"Process {mp.current_process().name}: {message}"
            result_queue.put(result)
            
    finally:
        socket.close()
        context.term()

if __name__ == '__main__':
    task_queue = mp.Queue()
    result_queue = mp.Queue()
    
    # Start worker processes
    processes = []
    for i in range(4):
        p = mp.Process(target=worker_process, args=(task_queue, result_queue))
        p.start()
        processes.append(p)
    
    # Send tasks via ZMQ
    context = zmq.Context()
    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("tcp://localhost:5567")
    
    for i in range(20):
        push_socket.send_string(f"Task {i}")
        task_queue.put(i)
    
    # Shutdown workers
    for _ in processes:
        task_queue.put(None)
    
    for p in processes:
        p.join()
    
    # Collect results
    while not result_queue.empty():
        print(result_queue.get())
```

### Using multiprocessing.Pool with ZMQ

```python
import zmq
from multiprocessing import Pool, current_process

def process_task(args):
    """Task function that creates its own ZMQ context"""
    task_id, endpoint = args
    process_name = current_process().name
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(endpoint)
    
    socket.send_string(f"Task {task_id} from {process_name}")
    response = socket.recv_string()
    
    socket.close()
    context.term()
    
    return task_id, response

if __name__ == '__main__':
    # Setup REP server
    context = zmq.Context()
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5568")
    
    # Process tasks in parallel
    tasks = [(i, "tcp://localhost:5568") for i in range(10)]
    
    with Pool(processes=4) as pool:
        results = pool.map(process_task, tasks)
    
    for task_id, response in results:
        print(f"Task {task_id}: {response}")
```

## Performance Considerations

### Thread vs Process vs Asyncio

| Model | Best For | Pros | Cons |
|-------|----------|------|------|
| Threading | I/O-bound tasks | Low overhead, shared memory | GIL limits CPU parallelism |
| Multiprocessing | CPU-bound tasks | True parallelism | Higher memory usage, IPC overhead |
| Asyncio | High concurrency I/O | Single-threaded, no GIL issues | Complex error handling, blocking code breaks async |

### Optimal Configuration

```python
import zmq

# For high-throughput applications
context = zmq.Context()

# Increase I/O threads for more concurrent connections
context.setsockopt(zmq.IO_THREADS, 4)

# Increase socket limit
context.setsockopt(zmq.MAX_SOCKETS, 4096)

# Tune socket buffers
socket = context.socket(zmq.DEALER)
socket.setsockopt(zmq.SNDBUF, 1024 * 1024)   # 1 MB send buffer
socket.setsockopt(zmq.RCVBUF, 1024 * 1024)   # 1 MB receive buffer

# Set high water mark to prevent memory exhaustion
socket.setsockopt(zmq.SNDHWM, 1000)  # Max 1000 messages in send queue
socket.setsockopt(zmq.RCVHWM, 1000)  # Max 1000 messages in recv queue

# Disable Nagle's algorithm for lower latency
socket.setsockopt(zmq.IMMEDIATE, 1)
```

### Zero-Copy Optimization

```python
import zmq
import array

socket = context.socket(zmq.PUSH)

# Pre-allocate buffer for zero-copy receives
buffer = bytearray(1024 * 1024)  # 1 MB buffer

# Receive directly into buffer (avoids memory copy)
nbytes = socket.recv_into(buffer)
data = bytes(buffer[:nbytes])  # Create bytes from received portion

# Use copy=False for multipart messages
frames = socket.recv_multipart(copy=False)
# frames contain zero-copy views of data
```
