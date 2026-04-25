# Troubleshooting and Error Handling

Comprehensive guide to diagnosing and resolving common pyzmq issues, error handling patterns, debugging techniques, and performance problems.

## Common Errors and Solutions

### Connection Errors

#### ECONNREFUSED - Connection Refused

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)

try:
    socket.connect("tcp://localhost:5555")
    socket.send(b"Hello", flags=zmq.DONTWAIT)
except zmq.ZMQError as e:
    if e.errno == zmq.ECONNREFUSED:
        print("Connection refused - server not running or wrong port")
        # Solutions:
        # 1. Check if server is running
        # 2. Verify port number matches bind address
        # 3. Check firewall rules
```

**Solutions:**
- Ensure server has bound to the expected address before client connects
- Check for typos in endpoint addresses (`tcp://localhost:5555` vs `tcp://127.0.0.1:5555`)
- Verify no firewall is blocking the port
- Use `netstat -an | grep 5555` to check if port is listening

#### ETIMEDOUT - Connection Timeout

```python
import zmq

socket = context.socket(zmq.REQ)

# Set connection timeout (ZMQ 4.1+)
socket.setsockopt(zmq.CONNECT_TIMEOUT, 5000)  # 5 seconds

try:
    socket.connect("tcp://unreachable-host:5555")
    # Wait for operation that requires connection
    socket.send(b"test", flags=zmq.DONTWAIT)
except zmq.Again:
    print("Connection timed out or not ready")
```

**Solutions:**
- Check network connectivity to host
- Verify host is reachable (`ping hostname`)
- Increase `CONNECT_TIMEOUT` for slow networks
- Use multiple endpoints for failover

#### EADDRINUSE - Address Already in Use

```python
import zmq

socket = context.socket(zmq.REP)

try:
    socket.bind("tcp://*:5555")
except zmq.ZMQError as e:
    if e.errno == zmq.EADDRINUSE:
        print("Port 5555 already in use")
        # Solutions:
        # 1. Use different port
        # 2. Wait for previous binding to release
        # 3. Use bind_to_random_port()
        
# Alternative: bind to random available port
port = socket.bind_to_random_port("tcp://*")
print(f"Bound to port {port}")
```

### Message Errors

#### EMSGSIZE - Message Too Large

```python
import zmq

socket = context.socket(zmq.DEALER)
socket.setsockopt(zmq.MAXMSGSIZE, 1024 * 1024)  # 1 MB limit

try:
    large_message = b"x" * (2 * 1024 * 1024)  # 2 MB - exceeds limit
    socket.send(large_message)
except zmq.ZMQError as e:
    if e.errno == zmq.EMSGSIZE:
        print("Message too large")
        # Solutions:
        # 1. Increase MAXMSGSIZE
        # 2. Split message into chunks
        # 3. Compress data before sending

# Chunked sending example
def send_chunked(socket, data, chunk_size=1024 * 1024):
    """Send large data in chunks"""
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        is_last = i + chunk_size >= len(data)
        flag = zmq.SNDMORE if not is_last else 0
        socket.send(chunk, flags=flag)
```

#### EAGAIN - Operation Would Block

```python
import zmq

socket = context.socket(zmq.PUSH)
socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking mode

try:
    message = socket.recv()
except zmq.Again:
    print("No message available (non-blocking)")
    # This is expected in non-blocking mode
    # Solutions:
    # 1. Use Poller to check if data available
    # 2. Set timeout instead of DONTWAIT
    # 3. Use async/await pattern

# Using Poller instead
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

events = dict(poller.poll(timeout=1000))
if socket in events and events[socket] & zmq.POLLIN:
    message = socket.recv()  # Safe to recv - data available
else:
    print("Timeout - no message")
```

### Resource Errors

#### ENOMEM - Out of Memory

```python
import zmq

context = zmq.Context()

# Configure memory limits
context.setsockopt(zmq.MAX_MSGSZ, 10 * 1024 * 1024)  # Max 10 MB messages

socket = context.socket(zmq.PULL)
socket.setsockopt(zmq.RCVHWM, 1000)  # Limit queue to 1000 messages
socket.setsockopt(zmq.SNDHWM, 1000)

try:
    # Operation that might exhaust memory
    message = socket.recv()
except zmq.ZMQError as e:
    if e.errno == zmq.ENOBUFS:  # Similar to ENOMEM in ZMQ
        print("Out of memory or buffer space")
        # Solutions:
        # 1. Reduce HWM values
        # 2. Process messages faster
        # 3. Add more consumers
```

#### ETERM - Context Terminated

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Terminate context (closes all sockets)
context.term()

try:
    socket.send(b"Hello")  # Socket no longer valid
except zmq.ZMQError as e:
    if e.errno == zmr.ETERM:
        print("Context terminated - socket invalid")
        # Solution: recreate context and socket
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
```

#### EFSM - Bad State (Finite State Machine Error)

```python
import zmq

# REQ/REP sockets have strict state machines
req_socket = context.socket(zmq.REQ)
rep_socket = context.socket(zmq.REP)

# Wrong: REP trying to send before receiving
try:
    rep_socket.send(b"Response")  # EFSM - must recv first!
except zmq.ZMQError as e:
    if e.errno == zmq.EFSM:
        print("Bad state - wrong operation for socket type")

# Correct: REP must receive before sending
message = rep_socket.recv()
rep_socket.send(b"Response")  # OK now
```

**Common EFSM scenarios:**
- REP socket sends without receiving first
- REQ socket receives without sending first  
- Multiple sends/receives in wrong order
- Solution: Use DEALER/ROUTER for flexible messaging

## Error Handling Patterns

### Try-Except with Specific Errors

```python
import zmq

def safe_send(socket, data, timeout=5000):
    """Send message with comprehensive error handling"""
    socket.setsockopt(zmq.SNDTIMEO, timeout)
    
    try:
        socket.send(data)
        return True, None
        
    except zmq.Again:
        return False, "Send timeout"
        
    except zmq.ZMQError as e:
        error_map = {
            zmq.EFSM: "Invalid socket state",
            zmq.EMSGSIZE: "Message too large",
            zmq.ENOBUFS: "Out of buffer space",
            zmq.ETERM: "Context terminated",
            zmq.ECONNREFUSED: "Connection refused",
        }
        return False, error_map.get(e.errno, f"ZMQ error {e.errno}")
        
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

# Usage
success, error = safe_send(socket, b"Hello")
if not success:
    print(f"Send failed: {error}")
```

### Retry with Exponential Backoff

```python
import zmq
import time
import random

def send_with_retry(socket, data, max_retries=5, base_delay=1.0):
    """Send with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            socket.send(data, flags=zmq.DONTWAIT)
            return True
            
        except zmq.Again:
            if attempt == max_retries - 1:
                return False
            
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
            
        except zmq.ZMQError as e:
            if e.errno in (zmq.ECONNREFUSED, zmq.ENETUNREACH):
                # Transient error - retry
                continue
            else:
                # Permanent error - don't retry
                return False
    
    return False

# Usage
if send_with_retry(socket, b"Important message"):
    print("Message sent successfully")
else:
    print("Failed to send after retries")
```

### Context Manager for Resource Management

```python
import zmq
from contextlib import contextmanager

@contextmanager
def managed_socket(context, socket_type, *endpoints, **options):
    """Context manager for socket lifecycle"""
    socket = context.socket(socket_type)
    
    # Apply options
    for key, value in options.items():
        if key.endswith("STRING"):
            socket.setsockopt_string(key, value)
        else:
            socket.setsockopt(key, value)
    
    # Bind or connect
    for endpoint in endpoints:
        if endpoint.startswith(("tcp://*", "ipc://", "inproc://")):
            socket.bind(endpoint)
        else:
            socket.connect(endpoint)
    
    try:
        yield socket
    finally:
        # Ensure clean shutdown
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()

# Usage
context = zmq.Context()

with managed_socket(
    context, zmq.REQ, 
    "tcp://localhost:5555",
    rcvtimeo=5000, sndtimeo=5000
) as socket:
    socket.send(b"Hello")
    response = socket.recv()
    
# Socket automatically closed even if exception occurs
```

### Circuit Breaker Pattern

```python
import zmq
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing - reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for ZeroMQ connections"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout)
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit OPEN after {self.failure_count} failures")
    
    def can_proceed(self):
        """Check if operation should proceed"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("Circuit HALF_OPEN - testing recovery")
                return True
            return False
            
        # HALF_OPEN - allow one test request
        return True

# Usage with socket operations
circuit_breaker = CircuitBreaker()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def make_request(data):
    if not circuit_breaker.can_proceed():
        raise Exception("Circuit breaker OPEN - rejecting request")
    
    try:
        socket.send(data)
        response = socket.recv(timeout=5000)
        circuit_breaker.record_success()
        return response
    except zmq.ZMQError:
        circuit_breaker.record_failure()
        raise

# Test circuit breaker
for i in range(10):
    try:
        response = make_request(b"Request")
        print(f"Request {i}: Success")
    except Exception as e:
        print(f"Request {i}: Failed - {e}")
```

## Debugging Techniques

### Enable Verbose Logging

```python
import zmq
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
zmq_logger = logging.getLogger("zmq")
zmq_logger.setLevel(logging.DEBUG)

# Create socket with monitoring for debug info
socket = context.socket(zmq.DEALER)
monitor_socket = socket.get_monitor_socket(
    events=zmq.EVENT_ALL,
    address="inproc://debug-monitor"
)

# Connect monitor
monitor = context.socket(zmq.PAIR)
monitor.connect("inproc://debug-monitor")

# Log all monitoring events
while True:
    try:
        event, value, addr = zmq.utils.monitor.parse_monitor_message(
            monitor.recv_multipart(flags=zmq.DONTWAIT)
        )
        zmq_logger.debug(f"Socket event: {event.name}, addr={addr}")
    except zmq.Again:
        break
```

### Socket State Inspection

```python
import zmq

def inspect_socket(socket):
    """Print comprehensive socket state"""
    print(f"Socket Type: {zmq.socket_type_name(socket.getsockopt(zmq.TYPE))}")
    print(f"Closed: {socket.closed}")
    
    # I/O settings
    print(f"\nI/O Settings:")
    print(f"  SNDBUF: {socket.getsockopt(zmq.SNDBUF)}")
    print(f"  RCVBUF: {socket.getsockopt(zmq.RCVBUF)}")
    print(f"  SNDTIMEO: {socket.getsockopt(zmq.SNDTIMEO)}")
    print(f"  RCVTIMEO: {socket.getsockopt(zmq.RCVTIMEO)}")
    
    # Flow control
    print(f"\nFlow Control:")
    print(f"  SNDHWM: {socket.getsockopt(zmq.SNDHWM)}")
    print(f"  RCVHWM: {socket.getsockopt(zmq.RCVHWM)}")
    
    # Connection info
    try:
        last_endpoint = socket.getsockopt_string(zmq.LAST_ENDPOINT)
        print(f"\nLast Endpoint: {last_endpoint}")
    except:
        pass
    
    # Security
    mechanism = socket.getsockopt(zmq.MECHANISM)
    print(f"\nSecurity Mechanism: {mechanism}")

# Usage
socket = context.socket(zmq.DEALER)
socket.bind("tcp://*:5555")
inspect_socket(socket)
```

### Message Flow Tracing

```python
import zmq
from functools import wraps

def trace_messages(socket, name="Socket"):
    """Wrap socket to trace all messages"""
    original_send = socket.send
    original_recv = socket.recv
    original_send_multipart = socket.send_multipart
    original_recv_multipart = socket.recv_multipart
    
    @wraps(original_send)
    def traced_send(data, **kwargs):
        print(f"[{name}] SEND: {len(data)} bytes")
        if isinstance(data, bytes) and len(data) < 100:
            print(f"  Content: {data}")
        return original_send(data, **kwargs)
    
    @wraps(original_recv)
    def traced_recv(**kwargs):
        result = original_recv(**kwargs)
        print(f"[{name}] RECV: {len(result)} bytes")
        if len(result) < 100:
            print(f"  Content: {result}")
        return result
    
    @wraps(original_send_multipart)
    def traced_send_multipart(messages, **kwargs):
        print(f"[{name}] SEND_Multipart: {len(messages)} frames")
        for i, msg in enumerate(messages):
            print(f"  Frame {i}: {len(msg)} bytes")
        return original_send_multipart(messages, **kwargs)
    
    @wraps(original_recv_multipart)
    def traced_recv_multipart(**kwargs):
        result = original_recv_multipart(**kwargs)
        print(f"[{name}] RECV_Multipart: {len(result)} frames")
        for i, msg in enumerate(result):
            print(f"  Frame {i}: {len(msg)} bytes")
        return result
    
    socket.send = traced_send
    socket.recv = traced_recv
    socket.send_multipart = traced_send_multipart
    socket.recv_multipart = traced_recv_multipart
    
    return socket

# Usage
socket = context.socket(zmq.DEALER)
socket = trace_messages(socket, "Worker")
socket.bind("tcp://*:5556")
```

## Performance Debugging

### Identify Blocking Operations

```python
import zmq
import time

def profile_socket_operations(socket, name="Socket"):
    """Profile send/recv operations to find blocking calls"""
    
    original_recv = socket.recv
    
    def timed_recv(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = original_recv(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > 0.1:  # Log operations taking > 100ms
                print(f"[{name}] RECV took {elapsed*1000:.0f}ms")
            return result
        except zmq.Again:
            elapsed = time.perf_counter() - start
            print(f"[{name}] RECV timeout after {elapsed*1000:.0f}ms")
            raise
    
    socket.recv = timed_recv
    return socket

# Usage
socket = context.socket(zmq.PULL)
socket = profile_socket_operations(socket, "Puller")
```

### Monitor Queue Depths

```python
import zmq

def check_socket_queues(socket):
    """Check send/receive queue depths"""
    # These are estimates - actual implementation varies by libzmq version
    try:
        # Get current HWM settings
        sndhwm = socket.getsockopt(zmq.SNDHWM)
        rcvhwm = socket.getsockopt(zmq.RCVHWM)
        
        print(f"Send HWM: {sndhwm}")
        print(f"Recv HWM: {rcvhwm}")
        
        # Check if send queue is full (try non-blocking send)
        try:
            socket.send(b"test", flags=zmq.DONTWAIT)
            print("Send queue: Not full")
        except zmq.Again:
            print("Send queue: FULL - backpressure active!")
            
    except Exception as e:
        print(f"Could not check queues: {e}")

# Usage in monitoring loop
while True:
    check_socket_queues(socket)
    time.sleep(5)
```

## Common Pitfalls and Solutions

### Memory Leaks

**Problem:** Sockets not properly closed, contexts not terminated

**Solution:**
```python
import zmq
from contextlib import closing

# Use context managers
with closing(zmq.Context()) as context:
    with closing(context.socket(zmq.REQ)) as socket:
        socket.connect("tcp://localhost:5555")
        # ... use socket ...
# Automatically cleaned up

# Or use try/finally
context = zmq.Context()
socket = None
try:
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    # ... use socket ...
finally:
    if socket:
        socket.close()
    context.term()
```

### Deadlocks in Request-Reply

**Problem:** REQ/REP sockets blocking due to strict protocol

**Solution:**
```python
# Use DEALER/ROUTER for flexible messaging
dealer = context.socket(zmq.DEALER)
router = context.socket(zmq.ROUTER)

# Or set timeouts on REQ/REP
req = context.socket(zmq.REQ)
req.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
```

### Message Ordering Issues

**Problem:** Messages arriving out of order in pub/sub or pipeline

**Solution:**
```python
# Use ROUTER/DEALER with explicit sequencing
socket = context.socket(zmq.ROUTER)

def send_ordered(socket, identity, messages):
    """Send messages with sequence numbers"""
    for i, msg in enumerate(messages):
        socket.send_multipart([identity, str(i).encode(), msg])

def receive_ordered(socket):
    """Reconstruct ordered message stream"""
    buffer = {}
    next_expected = 0
    
    while True:
        identity, seq, msg = socket.recv_multipart()
        seq_num = int(seq)
        
        buffer[seq_num] = msg
        
        # Yield messages in order
        while next_expected in buffer:
            yield identity, buffer.pop(next_expected)
            next_expected += 1
```

### Race Conditions in Multi-Threaded Code

**Problem:** Sharing sockets or contexts across threads

**Solution:**
```python
import zmq
import threading

# WRONG - sharing context
context = zmq.Context()
def worker():
    socket = context.socket(zmq.REQ)  # Unsafe!

# RIGHT - thread-local context
def worker():
    context = zmq.Context()  # New context per thread
    socket = context.socket(zmq.REQ)
    try:
        # ... use socket ...
    finally:
        socket.close()
        context.term()

# Or use thread-safe wrapper (see async-concurrent.md)
```

## Diagnostic Checklist

When troubleshooting ZeroMQ issues, check these items:

1. **Connection Issues:**
   - [ ] Server bound before client connects?
   - [ ] Endpoint addresses match exactly?
   - [ ] Firewall allowing traffic?
   - [ ] Correct protocol (tcp://, ipc://, inproc://)?

2. **Message Flow:**
   - [ ] Socket types compatible (REQ↔REP, PUB↔SUB)?
   - [ ] SUB sockets have subscriptions set?
   - [ ] No EFSM errors (wrong send/recv order)?
   - [ ] HWM not causing backpressure?

3. **Timeouts:**
   - [ ] RCVTIMEO/SNDTIMEO set appropriately?
   - [ ] Using Poller for non-blocking I/O?
   - [ ] CONNECT_TIMEOUT set for unreliable networks?

4. **Resources:**
   - [ ] Sockets closed after use?
   - [ ] Context terminated at shutdown?
   - [ ] HWM values appropriate for workload?
   - [ ] No memory leaks in long-running processes?

5. **Security:**
   - [ ] Authentication configured if needed?
   - [ ] CURVE keys match on both ends?
   - [ ] ZAP handler running if using ZAP?

6. **Performance:**
   - [ ] IO_THREADS sufficient for load?
   - [ ] Buffer sizes appropriate?
   - [ ] Using inproc:// for same-process communication?
   - [ ] Zero-copy where possible?
