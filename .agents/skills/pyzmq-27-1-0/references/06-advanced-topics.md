# Advanced Topics

Deep dive into advanced pyzmq features including devices, proxies, monitoring, serialization formats, and performance optimization techniques.

## Devices and Proxies

### Built-in Devices

ZeroMQ devices connect sockets together without application code. Deprecated in favor of explicit patterns but still available.

```python
import zmq

context = zmq.Context()

# Create sockets to connect via device
input_socket = context.socket(zmq.PULL)
output_socket = context.socket(zmq.PUSH)

# Forwarder device (PULL -> PUSH)
zmq.device(zmq.FORWARDER, input_socket, output_socket)

# Queue device (PULL -> PUSH with FIFO ordering)
zmq.device(zmq.QUEUE, input_socket, output_socket)

# Streamer device (PUB -> PUB for fanout)
zmq.device(zmq.STREAMER, input_socket, output_socket)
```

**Note:** Devices run in the calling thread and block. Use `ThreadDevice` or implement manually with Poller for non-blocking operation.

### Proxy Pattern

Proxy forwards messages between two sockets with optional monitoring.

```python
import zmq

context = zmq.Context()

# Frontend socket (receives client requests)
frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5571")

# Backend socket (sends to workers)
backend = context.socket(zmq.DEALER)
backend.connect("tcp://localhost:5572")

# Start proxy in background thread
zmq.proxy(frontend, backend)

# Or use proxy with monitoring
monitor = context.socket(zmq.PAIR)
monitor.bind("inproc://proxy-monitor")
zmq.proxy(frontend, backend, monitor)
```

### Steerable Proxy

Proxy that can be started/stopped via control socket.

```python
import zmq

context = zmq.Context()

frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5573")

backend = context.socket(zmq.DEALER)
backend.connect("tcp://localhost:5574")

# Control socket for starting/stopping proxy
control = context.socket(zmq.PAIR)
control.connect("inproc://proxy-control")

# Start steerable proxy (returns control socket)
ctrl_socket = zmq.proxy_steerable(frontend, backend)

# Send command to stop proxy
ctrl_socket.send(b"stop")

# Or bind control socket explicitly
zmq.proxy_steerable(frontend, backend, control)
```

### Device Classes (Thread/Process-based)

```python
import zmq.devices as devices

# Thread-based forwarder
forwarder = devices.ThreadForwarder(
    input_socket,
    output_socket,
    copy=True  # Copy messages between threads
)
forwarder.start()
# forwarder.join()  # Wait for completion

# Process-based proxy (runs in separate process)
proxy = devices.ProcessProxy(
    frontend_socket,
    backend_socket,
    monitor_socket=None
)
proxy.start()
# proxy.join()

# Monitored queue with statistics
monitored = devices.MonitoredQueue(
    input_socket,
    output_socket,
    monitor_address="tcp://*:5575"
)
monitored.start()
```

## Socket Monitoring

Monitor socket events for debugging, metrics, and connection tracking.

### Basic Monitoring

```python
import zmq
from zmq.utils import monitor

context = zmq.Context()
socket = context.socket(zmq.DEALER)

# Enable monitoring on inproc socket
monitor_socket = socket.get_monitor_socket(
    events=zmq.EVENT_ALL,  # Monitor all events
    address="inproc://monitor"
)

# Connect to monitor socket
monitor = context.socket(zmq.PAIR)
monitor.connect("inproc://monitor")

socket.bind("tcp://*:5576")

# Parse and handle monitoring events
while True:
    try:
        event, value, address = monitor.parse_monitor_message(
            monitor.recv_multipart()
        )
        
        print(f"Event: {event.name}")
        print(f"  Value: {value}")
        print(f"  Address: {address}")
        
    except zmq.Again:
        continue

# Disable monitoring when done
socket.disable_monitor()
```

### Event Tracking Class

```python
import zmq
from enum import IntEnum
from datetime import datetime

class ConnectionTracker:
    """Track socket connections and disconnections"""
    
    def __init__(self, socket):
        self.socket = socket
        self.context = socket.context
        self.connections = {}
        
        # Enable monitoring
        monitor_socket = socket.get_monitor_socket(
            events=zmq.EVENT_CONNECTED | 
                  zmq.EVENT_DISCONNECTED |
                  zmq.EVENT_CONNECT_DELAYED |
                  zmq.EVENT_CONNECT_RETRIED,
            address="inproc://tracker"
        )
        
        self.monitor = self.context.socket(zmq.PAIR)
        self.monitor.connect("inproc://tracker")
    
    def process_events(self):
        """Process pending monitoring events"""
        while True:
            try:
                event, value, address = zmq.utils.monitor.parse_monitor_message(
                    self.monitor.recv_multipart(flags=zmq.DONTWAIT)
                )
                
                timestamp = datetime.now().isoformat()
                
                if event == zmq.EVENT_CONNECTED:
                    print(f"[{timestamp}] Connected to {address}")
                    self.connections[address] = {"status": "connected", "time": timestamp}
                
                elif event == zmq.EVENT_DISCONNECTED:
                    print(f"[{timestamp}] Disconnected from {address}")
                    if address in self.connections:
                        del self.connections[address]
                
                elif event == zmq.EVENT_CONNECT_DELAYED:
                    print(f"[{timestamp}] Connection delayed to {address}")
                
                elif event == zmq.EVENT_CONNECT_RETRIED:
                    print(f"[{timestamp}] Retry connecting to {address}, waited {value}ms")
                
            except zmq.Again:
                break
    
    def get_connections(self):
        """Return dict of active connections"""
        return self.connections.copy()

# Usage
socket = context.socket(zmq.DEALER)
tracker = ConnectionTracker(socket)
socket.connect("tcp://localhost:5577")

# Periodically check for events
import time
for _ in range(10):
    time.sleep(1)
    tracker.process_events()

print(f"Active connections: {tracker.get_connections()}")
```

### Monitoring Events Reference

| Event | Constant | Description |
|-------|----------|-------------|
| PROTOCOL_ERROR_ZMTP_UNSPECIFIED | 1 | Unspecified ZMTP protocol error |
| PROTOCOL_ERROR_ZAP_UNSPECIFIED | 2 | Unspecified ZAP error |
| CONNECTED | 4 | Socket connected successfully |
| CONNECT_DELAYED | 8 | Connection delayed, will retry |
| CONNECT_RETRIED | 16 | Reconnect timeout expired |
| LISTENING | 32 | Bind successful, listening |
| BIND_FAILED | 64 | Bind failed |
| ACCEPTED | 128 | Client accepted successfully |
| ACCEPT_FAILED | 256 | Accept failed |
| CLOSED | 512 | Socket closed |
| CLOSE_FAILED | 1024 | Close failed |
| DISCONNECTED | 2048 | Peer disconnected |
| MONITOR_STOPPED | 4096 | Monitoring stopped |
| HANDSHAKE_FAILED_NO_DETAIL | 8192 | Handshake failed, no detail |
| HANDSHAKE_SUCCEEDED | 16384 | Handshake succeeded |
| HANDSHAKE_FAILED_PROTOCOL | 32768 | Protocol error during handshake |
| HANDSHAKE_FAILED_AUTH | 65536 | Authentication failed |

## Serialization Formats

### Message Serialization Options

PyZMQ supports multiple serialization methods:

| Method | Format | Pros | Cons |
|--------|--------|------|------|
| Raw bytes | Binary | Fastest, no overhead | Manual parsing required |
| String | UTF-8 text | Human-readable | Limited to text data |
| JSON | JSON | Language-independent | Slower, text-only |
| PyObj | Pickle | Python objects | Security risk, Python-only |
| Custom | Any format | Full control | Implementation complexity |

### Protocol Buffers with ZeroMQ

```python
import zmq
# import protobuf_message_pb2 as pb  # Generated from .proto file

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5578")

# Create protobuf message
# message = pb.MyMessage()
# message.id = 123
# message.name = "Alice"
# message.tags.extend(["tag1", "tag2"])

# Serialize and send
# data = message.SerializeToString()
# socket.send(data)

# Receive and deserialize
# response_data = socket.recv()
# response = pb.MyResponse()
# response.ParseFromString(response_data)

# print(f"Response: {response}")
```

### MessagePack with ZeroMQ

```python
import zmq
import msgpack

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5579")

# Send complex Python data
data = {
    "id": 123,
    "name": "Alice",
    "scores": [95.5, 87.3, 92.1],
    "metadata": {"level": 5, "active": True}
}

# Serialize with MessagePack (more compact than JSON)
packed = msgpack.packb(data, use_bin_type=True)
socket.send(packed)

# Receive and deserialize
response_packed = socket.recv()
response = msgpack.unpackb(response_packed, raw=False)

print(f"Response: {response}")
```

### Custom Serialization with Framing

```python
import zmq
import hashlib
import json

class FramedMessage:
    """Custom message framing with checksum"""
    
    @staticmethod
    def create(data, msg_type="request"):
        """Create framed message"""
        # Serialize payload
        payload = json.dumps(data).encode('utf-8')
        
        # Calculate checksum
        checksum = hashlib.md5(payload).hexdigest().encode('utf-8')
        
        # Create frame: [type, checksum, length, payload]
        frame = [
            msg_type.encode('utf-8'),
            checksum,
            payload.ljust(4, b'\x00')[:4],  # Length as 4 bytes
            payload
        ]
        
        return frame
    
    @staticmethod
    def receive(socket):
        """Receive and validate framed message"""
        frames = socket.recv_multipart()
        
        if len(frames) < 4:
            raise ValueError("Invalid frame format")
        
        msg_type, checksum, length_bytes, payload = frames
        
        # Verify checksum
        received_checksum = hashlib.md5(payload).hexdigest().encode('utf-8')
        if checksum != received_checksum:
            raise ValueError("Checksum mismatch - data corrupted")
        
        # Deserialize payload
        data = json.loads(payload.decode('utf-8'))
        
        return msg_type.decode('utf-8'), data

# Usage
socket = context.socket(zmq.DEALER)

# Send framed message
frame = FramedMessage.create({"action": "process", "data": [1, 2, 3]})
socket.send_multipart(frame)

# Receive framed message
msg_type, data = FramedMessage.receive(socket)
print(f"{msg_type}: {data}")
```

### Zero-Copy Serialization

```python
import zmq
import array
import mmap

context = zmq.Context()
socket = context.socket(zmq.PUSH)

# Use pre-allocated buffer for zero-copy sends
buffer_size = 1024 * 1024  # 1 MB
buffer = bytearray(buffer_size)

# Fill buffer with data (simulating large dataset)
data_to_send = b"Hello World " * 65536  # ~1 MB
buffer[:len(data_to_send)] = data_to_send

# Send without copying data
socket.send(buffer[:len(data_to_send)], copy=False)

# For receives, use recv_into with pre-allocated buffer
recv_socket = context.socket(zmq.PULL)
recv_buffer = bytearray(buffer_size)

nbytes = recv_socket.recv_into(recv_buffer)
received_data = bytes(recv_buffer[:nbytes])  # Copy only what was received
```

## Performance Optimization

### Benchmarking Message Throughput

```python
import zmq
import time

def benchmark_throughput(socket_type_pair, num_messages=10000):
    """Benchmark message throughput for socket pair"""
    context = zmq.Context()
    
    # Create socket pair
    push = context.socket(zmq.PUSH)
    push.bind("inproc://benchmark")
    
    pull = context.socket(zmq.PULL)
    pull.connect("inproc://benchmark")
    
    # Warm up
    push.send(b"x" * 1024)
    pull.recv()
    
    # Benchmark
    start_time = time.perf_counter()
    
    for _ in range(num_messages):
        push.send(b"x" * 1024)
        pull.recv()
    
    end_time = time.perf_counter()
    
    elapsed = end_time - start_time
    messages_per_sec = num_messages / elapsed
    mb_per_sec = (num_messages * 1024) / (elapsed * 1024 * 1024)
    
    print(f"Throughput: {messages_per_sec:.0f} msg/sec, {mb_per_sec:.2f} MB/sec")
    
    push.close()
    pull.close()

# Run benchmark
benchmark_throughput(("PUSH", "PULL"))
```

### Profiling Socket Operations

```python
import zmq
import cProfile
import pstats
from io import StringIO

def profile_socket_operations():
    """Profile socket send/recv operations"""
    context = zmq.Context()
    
    push = context.socket(zmq.PUSH)
    push.bind("inproc://profile")
    
    pull = context.socket(zmq.PULL)
    pull.connect("inproc://profile")
    
    def work():
        for _ in range(1000):
            push.send(b"test message")
            pull.recv()
    
    # Profile the work function
    profiler = cProfile.Profile()
    profiler.enable()
    
    work()
    
    profiler.disable()
    
    # Print stats
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    print(stream.getvalue())

profile_socket_operations()
```

### Memory Usage Monitoring

```python
import zmq
import tracemalloc

def monitor_memory_usage():
    """Monitor memory usage during socket operations"""
    tracemalloc.start()
    
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.bind("inproc://memory-test")
    
    # Send many messages
    for i in range(10000):
        socket.send(f"Message {i}".encode(), flags=zmq.DONTWAIT)
    
    # Check memory usage
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()

monitor_memory_usage()
```

### Connection Pooling

```python
import zmq
from contextlib import contextmanager
from typing import List, Optional

class SocketPool:
    """Connection pool for ZeroMQ sockets"""
    
    def __init__(self, socket_type, endpoints: List[str], pool_size: int = 10):
        self.socket_type = socket_type
        self.endpoints = endpoints
        self.pool_size = pool_size
        self.context = zmq.Context()
        self._pool = []
        self._locked = False
    
    def _create_socket(self):
        """Create and configure a new socket"""
        socket = self.context.socket(self.socket_type)
        
        # Configure socket options
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.setsockopt(zmq.SNDTIMEO, 5000)
        socket.setsockopt(zmq.HWM, 1000)
        
        # Connect to endpoints (load balance across them)
        for endpoint in self.endpoints:
            socket.connect(endpoint)
        
        return socket
    
    def initialize(self):
        """Pre-create sockets in pool"""
        for _ in range(self.pool_size):
            self._pool.append(self._create_socket())
    
    @contextmanager
    def acquire(self, timeout: Optional[int] = None):
        """Acquire socket from pool"""
        if not self._pool:
            # Create on-demand if pool exhausted
            socket = self._create_socket()
        else:
            socket = self._pool.pop()
        
        try:
            yield socket
        finally:
            # Return to pool (limit pool size)
            if len(self._pool) < self.pool_size:
                self._pool.append(socket)
            else:
                socket.close()
    
    def close(self):
        """Close all sockets in pool"""
        for socket in self._pool:
            socket.close()
        self.context.term()

# Usage
pool = SocketPool(
    zmq.REQ,
    ["tcp://server1:5555", "tcp://server2:5555"],
    pool_size=20
)
pool.initialize()

with pool.acquire() as socket:
    socket.send_string("Hello")
    response = socket.recv_string()
    print(response)

pool.close()
```

## SSH Tunneling

Tunnel ZeroMQ connections through SSH for secure communication across networks.

```python
import zmq
from zmq.ssh.tunnel import ssh_tunnel

# Create SSH tunnel
tunnel = ssh_tunnel(
    "user@remote.host",      # SSH destination
    5555,                     # Local port to forward
    5555,                     # Remote port
    ssh_options={
        "port": 22,
        "key_filename": "/path/to/private/key",
        "timeout": 10
    }
)

# Start tunnel (blocks until connection established)
tunnel.start()

# Now connect to local port, traffic goes through SSH tunnel
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")  # Goes through SSH tunnel

socket.send_string("Hello through SSH")
response = socket.recv_string()
print(response)

# Stop tunnel when done
tunnel.stop()
```

## In-Process Communication

Optimize performance with inproc transport for same-process communication.

```python
import zmq

context = zmq.Context()

# Create inproc sockets (fastest transport, no network overhead)
publisher = context.socket(zmq.PUB)
publisher.bind("inproc://myapp")

subscriber1 = context.socket(zmq.SUB)
subscriber1.connect("inproc://myapp")
subscriber1.setsockopt_string(zmq.SUBSCRIBE, "")

subscriber2 = context.socket(zmq.SUB)
subscriber2.connect("inproc://myapp")
subscriber2.setsockopt_string(zmq.SUBSCRIBE, "news.")

# Publish messages
publisher.send_string("news.breaking Major announcement")
publisher.send_string("ads.banner Special offer")

# Subscribers receive (order not guaranteed)
msg1 = subscriber1.recv_string()
msg2 = subscriber1.recv_string()

msg3 = subscriber2.recv_string(flags=zmq.DONTWAIT)  # Only news.*
```

## Shadow Sockets

Wrap existing C/FFI sockets in Python objects.

```python
import zmq

context = zmq.Context()

# Create a regular socket first
original_socket = context.socket(zmq.DEALER)
original_socket.bind("tcp://*:5580")

# Get the underlying C socket pointer
c_socket = original_socket.underlying

# Create shadow socket (Python wrapper around C socket)
shadow_socket = context.shadow(zmq.DEALER, c_socket)

# Both sockets refer to same underlying connection
# Use shadow_socket for Python API, original for C API

# Close original - shadow becomes invalid
original_socket.close()
```
