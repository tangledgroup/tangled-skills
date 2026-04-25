# Messaging Fundamentals

Core concepts for using pyzmq effectively, including Context and Socket lifecycle management, send/recv operations, message framing, and basic patterns.

## Context Management

The `Context` is the top-level object in pyzmq and should be created once per application or thread.

### Creating Contexts

```python
import zmq

# Default context (recommended for most cases)
context = zmq.Context()

# Context with custom configuration
context = zmq.Context(io_threads=4)  # Number of I/O threads

# Using context manager pattern
from contextlib import closing

with closing(zmq.Context()) as context:
    socket = context.socket(zmq.REQ)
    # ... use socket ...
# Context automatically terminated here
```

### Context Options

```python
import zmq

context = zmq.Context()

# Number of I/O threads (default: 1)
context.setsockopt(zmq.IO_THREADS, 4)

# Maximum number of sockets (default: 1024)
context.setsockopt(zmq.MAX_SOCKETS, 2048)

# Maximum message size in bytes (ZMQ 4.1+)
context.setsockopt(zmq.MAX_MSGSZ, 1024 * 1024 * 10)  # 10 MB

# Thread scheduling policy (POSIX only)
context.setsockopt(zmq.THREAD_SCHED_POLICY, zmq.THREAD_SCHED_OTHER)

# Get current values
io_threads = context.getsockopt(zmq.IO_THREADS)
max_sockets = context.getsockopt(zmq.MAX_SOCKETS)
```

### Context Lifecycle

```python
import zmq

context = zmq.Context()

# Create sockets
socket1 = context.socket(zmq.REQ)
socket2 = context.socket(zmq.PUB)

# Use sockets...

# Close individual sockets
socket1.close()
socket2.close()

# Terminate context (closes all remaining sockets)
context.term()

# Context can be destroyed forcefully
context.destroy()  # Force close all sockets and terminate
```

## Socket Fundamentals

### Creating Sockets

```python
import zmq

context = zmq.Context()

# Create socket by type constant
req_socket = context.socket(zmq.REQ)
rep_socket = context.socket(zmq.REP)

# Create socket by SocketType enum (type-safe)
from zmq import SocketType
pub_socket = context.socket(SocketType.PUB)
sub_socket = context.socket(SocketType.SUB)

# Check socket type
print(socket.getsockopt(zmq.TYPE))  # Returns socket type constant
```

### Binding and Connecting

```python
import zmq

context = zmq.Context()

# Server-side: bind to address
server = context.socket(zmq.ROUTER)
server.bind("tcp://*:5555")           # Listen on all interfaces
server.bind("tcp://127.0.0.1:5556")   # Listen on localhost only
server.bind("ipc:///tmp/server.ipc")   # Unix domain socket
server.bind("inproc://myserver")      # In-process communication

# Client-side: connect to address
client = context.socket(zmq.DEALER)
client.connect("tcp://localhost:5555")
client.connect("tcp://localhost:5556")  # Can connect to multiple addresses

# Get last bound/connected endpoint
last_endpoint = server.getsockopt_string(zmq.LAST_ENDPOINT)
# Returns: "tcp://0.0.0.0:5555"
```

### Transport Protocols

| Protocol | Example | Use Case |
|----------|---------|----------|
| `tcp://` | `tcp://*:5555` | Network communication (most common) |
| `ipc://` | `ipc:///tmp/app.ipc` | Same-machine communication (fastest local) |
| `inproc://` | `inproc://myapp` | Same-process communication (fastest) |
| `udp://` | `udp://*:5555` | Datagram-style messaging (NORM transport) |
| `tcp+tls://` | `tcp+tls://*:5555` | Encrypted TCP (requires OpenSSL) |

### Binding to Random Port

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)

# Bind to random available port
port = socket.bind_to_random_port("tcp://*")
print(f"Bound to port {port}")  # e.g., "Bound to port 45678"

# With address prefix
port = socket.bind_to_random_port("tcp://127.0.0.1")

# Get actual bound address
endpoint = socket.getsockopt_string(zmq.LAST_ENDPOINT)
print(endpoint)  # "tcp://0.0.0.0:45678"
```

## Send and Receive Operations

### Basic Send/Recv

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Send bytes (most efficient)
socket.send(b"Hello World")

# Receive bytes
message = socket.recv()
print(message)  # b"Response"

# Send string (UTF-8 encoded)
socket.send_string("Hello World")

# Receive string
response = socket.recv_string()
print(response)  # "Response"
```

### Send Flags

```python
import zmq

socket = context.socket(zmq.DEALER)

# Blocking send (default)
socket.send(b"data")

# Non-blocking send (raises zmq.Again if not ready)
try:
    socket.send(b"data", flags=zmq.DONTWAIT)
except zmq.Again:
    print("Socket not ready for sending")

# Send with SNDMORE flag for multipart messages
socket.send(b"frame1", flags=zmq.SNDMORE)
socket.send(b"frame2", flags=zmq.SNDMORE)
socket.send(b"frame3")  # Last frame without SNDMORE
```

### Receive Flags

```python
import zmq

socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE, "")

# Blocking receive (default)
message = socket.recv()

# Non-blocking receive
try:
    message = socket.recv(flags=zmq.DONTWAIT)
except zmq.Again:
    print("No message available")

# Receive with timeout (set via RCVTIMEO option)
socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
try:
    message = socket.recv()
except zmq.Again:
    print("Timeout - no message received")
```

### Multipart Messages

ZeroMQ messages can consist of multiple frames (multipart):

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.DEALER)

# Send multipart message
socket.send_multipart([b"frame1", b"frame2", b"frame3"])

# Equivalent manual approach
socket.send(b"frame1", flags=zmq.SNDMORE)
socket.send(b"frame2", flags=zmq.SNDMORE)
socket.send(b"frame3")  # Last frame

# Receive multipart message
frames = socket.recv_multipart()
print(frames)  # [b"frame1", b"frame2", b"frame3"]

# Receive multipart with strings
frames = socket.recv_multipart(copy=False)  # Zero-copy (don't duplicate data)

# Check if more frames coming
socket.recv(flags=zmq.DONTWAIT)
more = socket.getsockopt(zmq.RCVMORE)
if more:
    print("More frames in message")
```

### String and Unicode Handling

```python
import zmq

socket = context.socket(zmq.REQ)

# Send string with default UTF-8 encoding
socket.send_string("Hello 世界")

# Send string with custom encoding
socket.send_string("Hello", encoding="utf-8")
socket.send_string("Hola", encoding="latin-1")

# Receive string
message = socket.recv_string(encoding="utf-8")

# Handle encoding errors
message = socket.recv_string(encoding="utf-8", errors="replace")
message = socket.recv_string(encoding="utf-8", errors="ignore")
```

## Serialization Methods

### JSON Serialization

```python
import zmq
import json

socket = context.socket(zmq.REQ)

# Send JSON (automatic serialization)
data = {"name": "Alice", "age": 30, "items": [1, 2, 3]}
socket.send_json(data)

# Receive JSON (automatic deserialization)
received = socket.recv_json()
print(received)  # {'name': 'Alice', 'age': 30, 'items': [1, 2, 3]}

# Custom JSON encoding
socket.send_json(data, default=str)  # Convert non-serializable objects to strings
received = socket.recv_json(object_hook=lambda d: MyObject(**d))
```

### Python Object Serialization (Pickle)

```python
import zmq

socket = context.socket(zmq.REQ)

# Send Python object (pickle-based)
class MyClass:
    def __init__(self, value):
        self.value = value

obj = MyClass(42)
socket.send_pyobj(obj)

# Receive Python object
received_obj = socket.recv_pyobj()
print(received_obj.value)  # 42

# Warning: Pickle can execute arbitrary code - only use with trusted sources!
```

### Custom Serialization

```python
import zmq
import pickle
import hashlib

def send_serialized(socket, data):
    """Send data with checksum"""
    serialized = pickle.dumps(data)
    checksum = hashlib.md5(serialized).digest()
    socket.send_multipart([checksum, serialized])

def recv_serialized(socket):
    """Receive data with checksum verification"""
    frames = socket.recv_multipart()
    if len(frames) != 2:
        raise ValueError("Invalid message format")
    
    checksum, serialized = frames
    expected_checksum = hashlib.md5(serialized).digest()
    
    if checksum != expected_checksum:
        raise ValueError("Checksum mismatch - data corrupted")
    
    return pickle.loads(serialized)
```

### Message Tracker

Track when sent messages have been fully transmitted:

```python
import zmq

socket = context.socket(zmq.PUSH)

# Send with tracker
data = b"Important message" * 1000  # Large message
tracker = socket.send(data, tracking=True)

# Wait for message to be sent
tracker.wait()
print("Message fully transmitted")

# Check if done without blocking
if tracker.done:
    print("Message sent")
```

## Receive into Buffer (Zero-Copy)

```python
import zmq
import array

socket = context.socket(zmq.PULL)

# Pre-allocate buffer
buffer = array.array('B', bytes(1024 * 1024))  # 1 MB buffer

# Receive directly into buffer (zero-copy)
nbytes = socket.recv_into(buffer)
print(f"Received {nbytes} bytes")

# Using memoryview for partial receives
mv = memoryview(buffer)
nbytes = socket.recv_into(mv[:512])  # Receive into first 512 bytes only
```

## Socket Closing and Cleanup

### Proper Cleanup Pattern

```python
import zmq
from contextlib import contextmanager

@contextmanager
def create_socket(context, socket_type, *endpoints, **kwargs):
    """Create socket with automatic cleanup"""
    socket = context.socket(socket_type)
    
    # Bind or connect based on endpoint scheme
    for endpoint in endpoints:
        if endpoint.startswith(("tcp://*", "ipc://", "inproc://")):
            socket.bind(endpoint)
        else:
            socket.connect(endpoint)
    
    try:
        yield socket
    finally:
        socket.close()

# Usage
context = zmq.Context()
with create_socket(context, zmq.REQ, "tcp://localhost:5555") as socket:
    socket.send(b"Hello")
    response = socket.recv()
# Socket automatically closed here
```

### Force Close

```python
import zmq

socket = context.socket(zmq.REQ)

# Normal close (waits for pending operations)
socket.close()

# Force close with timeout (milliseconds)
context.destroy(linger=5000)  # Force close all sockets in 5 seconds

# Immediate force close
context.destroy(linger=0)  # May lose in-flight messages
```

## Common Pitfalls

### Don't Share Contexts Across Threads

```python
import zmq
import threading

# WRONG: Sharing context across threads
context = zmq.Context()

def worker():
    socket = context.socket(zmq.REQ)  # Unsafe!
    # ...

# RIGHT: One context per thread
def worker():
    context = zmq.Context()  # Thread-local context
    socket = context.socket(zmq.REQ)
    try:
        # ... use socket ...
    finally:
        socket.close()
        context.term()
```

### Always Check for More Frames

```python
import zmq

socket = context.socket(zmq.ROUTER)

# Receive multipart message properly
while True:
    frame = socket.recv(flags=zmq.DONTWAIT)
    more = socket.getsockopt(zmq.RCVMORE)
    
    # Process frame...
    
    if not more:
        break  # End of message
```

### Set Timeouts for Non-Blocking Behavior

```python
import zmq

socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout

try:
    response = socket.recv()
except zmq.Again:
    print("Request timed out")
    # Handle timeout (retry, failover, etc.)
```
