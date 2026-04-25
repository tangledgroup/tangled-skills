# aiozmq Core API

The core API provides low-level asyncio transport and protocol abstractions for ZeroMQ, giving fine-grained control over socket lifecycle, message handling, and event loop integration.

## create_zmq_connection

The fundamental coroutine for creating ZeroMQ connections at the transport/protocol level.

### Basic Usage

```python
import asyncio
import aiozmq
import zmq

class MyProtocol(aiozmq.ZmqProtocol):
    """Custom protocol implementing message handling."""
    
    def __init__(self):
        self.transport = None
        self.messages = []
    
    def connection_made(self, transport):
        """Called when connection is established."""
        self.transport = transport
        print("Connection established")
    
    def msg_received(self, msg):
        """Called when message arrives."""
        self.messages.append(msg)
        print(f"Received: {msg}")
    
    def connection_lost(self, exc):
        """Called when connection closes."""
        print(f"Connection lost: {exc}")
        self.transport = None

async def main():
    # Create connection with custom protocol
    transport, protocol = await aiozmq.create_zmq_connection(
        MyProtocol,  # Protocol factory (callable returning protocol instance)
        zmq.DEALER,  # Socket type
        connect='tcp://127.0.0.1:5555'  # Connect to endpoint
    )
    
    # Send message
    transport.write((b'frame1', b'frame2'))
    
    await asyncio.sleep(1)
    
    # Cleanup
    transport.close()

asyncio.run(main())
```

### Parameters

```python
async def create_zmq_connection(
    protocol_factory,  # Callable returning ZmqProtocol instance
    zmq_type,          # Socket type (zmq.REQ, zmq.ROUTER, etc.)
    *,
    bind=None,         # Endpoint(s) to bind (str or list)
    connect=None,      # Endpoint(s) to connect (str or list)
    zmq_sock=None,     # Pre-existing pyzmq socket (optional)
    loop=None          # Event loop (defaults to asyncio.get_event_loop())
):
```

### Bind vs Connect

```python
# Server binds to accept connections
server_transport, server_protocol = await aiozmq.create_zmq_connection(
    MyProtocol,
    zmq.ROUTER,
    bind='tcp://*:5555'  # Listen on all interfaces
)

# Client connects to server
client_transport, client_protocol = await aiozmq.create_zmq_connection(
    MyProtocol,
    zmq.DEALER,
    connect='tcp://127.0.0.1:5555'  # Connect to specific address
)
```

### Multiple Endpoints

```python
# Bind to multiple endpoints
transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol,
    zmq.ROUTER,
    bind=[
        'tcp://*:5555',           # TCP on all interfaces
        'ipc:///tmp/mysocket',     # Unix domain socket
    ]
)

# Connect with redundancy/failover
transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol,
    zmq.DEALER,
    connect=[
        'tcp://server1:5555',
        'tcp://server2:5555',
    ]
)
```

### Using Existing Socket

```python
import zmq

# Create pyzmq socket manually with custom options
context = zmq.Context()
sock = context.socket(zmq.ROUTER)
sock.setsockopt(zmq.IDENTITY, b'myserver')
sock.setsockopt(zmq.LINGER, 0)

# Wrap with aiozmq transport
transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol,
    zmq.ROUTER,
    bind='tcp://*:5555',
    zmq_sock=sock  # Reuse existing socket
)
```

## ZmqTransport Interface

The transport handles low-level socket operations and provides access to ZeroMQ functionality.

### Writing Messages

```python
# Write single-frame message
transport.write(b'hello')

# Write multi-frame message (tuple of byte strings)
transport.write((b'identity', b'frame1', b'frame2'))

# DEALER/ROUTER require multi-frame for identities
router_write(
    (client_identity, b'message part 1', b'message part 2')
)
```

### Bind and Connect Operations

```python
# Initial bind
transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol, zmq.ROUTER, bind='tcp://*:5555'
)

# Dynamic bind (add more endpoints)
await transport.bind('ipc:///tmp/extra')

# Dynamic connect (add more connections)
await transport.connect('tcp://backup-server:5555')

# Check current bindings
for addr in transport.bindings():
    print(f"Bound to: {addr}")

# Check current connections
for addr in transport.connections():
    print(f"Connected to: {addr}")
```

### Unbind and Disconnect

```python
# Remove specific endpoint
await transport.unbind('tcp://127.0.0.1:5555')

# Disconnect from endpoint
await transport.disconnect('tcp://backup-server:5555')
```

### Get Extra Info

```python
# Access underlying socket
zmq_socket = transport.get_extra_info('socket')

# Get peer address (for connected sockets)
peer_addr = transport.get_extra_info('peer_addr')

# Custom extra info with default
info = transport.get_extra_info('custom_key', 'default_value')
```

### Close Transport

```python
# Close and cleanup
transport.close()

# Check if closed
if transport.is_closing():
    print("Transport is closing")
```

## ZmqProtocol Interface

The protocol handles message callbacks and connection lifecycle events.

### Required Methods

```python
class MyProtocol(aiozmq.ZmqProtocol):
    """Base protocol to subclass."""
    
    def connection_made(self, transport):
        """Called when socket is ready.
        
        Args:
            transport: ZmqTransport instance for this connection
        """
        self.transport = transport
    
    def msg_received(self, msg):
        """Called when message arrives.
        
        Args:
            msg: Tuple of byte strings (message frames)
        """
        pass
    
    def connection_lost(self, exc):
        """Called when connection closes.
        
        Args:
            exc: Exception if error occurred, None for clean close
        """
        self.transport = None
    
    def event_received(self, event):
        """Called when socket event occurs (optional).
        
        Args:
            event: SocketEvent namedtuple (event, value, endpoint)
        """
        pass
```

### Message Format

Messages are always tuples of byte strings:

```python
def msg_received(self, msg):
    # Single frame message
    if len(msg) == 1:
        data = msg[0]
    
    # Multi-frame message (common with DEALER/ROUTER)
    identity, *frames = msg
    
    # DEALER receives all frames
    all_frames = list(msg)
    
    # ROUTER first frame is client identity
    if self.socket_type == zmq.ROUTER:
        client_id = msg[0]
        message = msg[1:]
```

### Event Monitoring

```python
from aiozmq import SocketEvent

def event_received(self, event):
    """Handle socket events.
    
    event.event: Integer event type (zmq.EVENT_CONNECTED, etc.)
    event.value: Event value (often error code or additional info)
    endpoint: Endpoint string where event occurred
    """
    print(f"Event {event.event} on {event.endpoint}: {event.value}")
    
    # Common events
    if event.event == zmq.EVENT_CONNECTED:
        print(f"Connected to {event.endpoint}")
    elif event.event == zmq.EVENT_CONNECT_DELAYED:
        print(f"Connection delayed to {event.endpoint}")
    elif event.event == zmq.EVENT_DISCONNECTED:
        print(f"Disconnected from {event.endpoint}")
    elif event.event == zmq.EVENT_MONITOR_STOPPED:
        print("Monitoring stopped")
```

## ZmqEventLoop

Custom event loop integrating ZeroMQ polling with asyncio.

### Creating and Using

```python
from aiozmq import ZmqEventLoop, ZmqEventLoopPolicy
import zmq

# Create custom event loop
loop = ZmqEventLoop()

# Or set as policy
policy = ZmqEventLoopPolicy()
asyncio.set_event_loop_policy(policy)
loop = asyncio.get_event_loop()

# Use create_zmq_connection directly on loop
async def main():
    transport, protocol = await loop.create_zmq_connection(
        MyProtocol,
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    
    # ... use connection

loop.run_until_complete(main())
loop.close()
```

### Custom ZMQ Context

```python
import zmq

# Create custom context with options
context = zmq.Context()
context.setsockopt(zmq.IO_THREADS, 2)
context.setsockopt(zmq.MAX_SOCKETS, 1024)

# Use with event loop
loop = ZmqEventLoop(zmq_context=context)
```

### Limitations on Windows

- Uses select-based polling (not IOCP)
- No subprocess support
- Slower than ProactorEventLoop
- No IPC endpoints

## Exception Handling

### Error Policy

By default, exceptions in protocol methods are logged:

```python
class MyProtocol(aiozmq.ZmqProtocol):
    def msg_received(self, msg):
        # If this raises, exception is logged but connection continues
        risky_operation()
```

### Connection Errors

```python
async def robust_connection():
    try:
        transport, protocol = await aiozmq.create_zmq_connection(
            MyProtocol,
            zmq.DEALER,
            connect='tcp://nonexistent:5555'
        )
    except OSError as e:
        print(f"Connection failed: {e}")
```

### Protocol Exception Handling

```python
class RobustProtocol(aiozmq.ZmqProtocol):
    def msg_received(self, msg):
        try:
            self.process_message(msg)
        except Exception as e:
            # Handle gracefully, don't crash connection
            print(f"Error processing message: {e}")
    
    def connection_lost(self, exc):
        if exc is None:
            print("Clean disconnect")
        else:
            print(f"Error disconnect: {exc}")
```

## Complete Examples

### Echo Server with Core API

```python
import asyncio
import aiozmq
import zmq

class EchoProtocol(aiozmq.ZmqProtocol):
    def __init__(self):
        self.transport = None
    
    def connection_made(self, transport):
        self.transport = transport
        print("Echo server ready")
    
    def msg_received(self, msg):
        # Echo back all messages
        print(f"Received: {msg}")
        self.transport.write(msg)
    
    def connection_lost(self, exc):
        print(f"Connection lost: {exc}")
        self.transport = None

async def echo_server():
    transport, protocol = await aiozmq.create_zmq_connection(
        EchoProtocol,
        zmq.ROUTER,
        bind='tcp://*:5555'
    )
    
    print(f"Echo server on {list(transport.bindings())[0]}")
    
    # Keep running
    await asyncio.sleep(3600)

async def echo_client():
    class ClientProtocol(aiozmq.ZmqProtocol):
        def __init__(self, queue):
            self.transport = None
            self.queue = queue
        
        def connection_made(self, transport):
            self.transport = transport
        
        def msg_received(self, msg):
            self.queue.put_nowait(msg)
        
        def connection_lost(self, exc):
            self.transport = None
    
    queue = asyncio.Queue()
    transport, protocol = await aiozmq.create_zmq_connection(
        lambda: ClientProtocol(queue),
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    
    # Send messages
    for i in range(5):
        msg = (b'message', str(i).encode())
        transport.write(msg)
        
        # Wait for echo
        response = await queue.get()
        print(f"Echo: {response}")
    
    transport.close()

async def main():
    server = asyncio.create_task(echo_server())
    
    await asyncio.sleep(0.5)
    
    await echo_client()
    
    server.cancel()

asyncio.run(main())
```

### Request-Reply with Core API

```python
import asyncio
import aiozmq
import zmq

class RepProtocol(aiozmq.ZmqProtocol):
    def __init__(self, handler):
        self.transport = None
        self.handler = handler
    
    def connection_made(self, transport):
        self.transport = transport
    
    def msg_received(self, msg):
        # Process request and send reply
        request = b''.join(msg).decode()
        response = self.handler(request)
        self.transport.write(response.encode())
    
    def connection_lost(self, exc):
        self.transport = None

class ReqProtocol(aiozmq.ZmqProtocol):
    def __init__(self, queue):
        self.transport = None
        self.queue = queue
    
    def connection_made(self, transport):
        self.transport = transport
    
    def msg_received(self, msg):
        self.queue.put_nowait(msg)
    
    def connection_lost(self, exc):
        self.transport = None

def request_handler(request):
    return f"Response to: {request}"

async def main():
    # Server
    server_transport, _ = await aiozmq.create_zmq_connection(
        lambda: RepProtocol(request_handler),
        zmq.REP,
        bind='tcp://*:5556'
    )
    
    # Client
    queue = asyncio.Queue()
    client_transport, _ = await aiozmq.create_zmq_connection(
        lambda: ReqProtocol(queue),
        zmq.REQ,
        connect='tcp://127.0.0.1:5556'
    )
    
    # Make requests
    for i in range(3):
        client_transport.write(f"Request {i}".encode())
        response = await queue.get()
        print(f"{response[0].decode()}")
    
    client_transport.close()
    server_transport.close()

asyncio.run(main())
```

### Socket Event Monitor

```python
import asyncio
import aiozmq
import zmq

class MonitoredProtocol(aiozmq.ZmqProtocol):
    def __init__(self):
        self.transport = None
    
    def connection_made(self, transport):
        self.transport = transport
        print("Connection established")
    
    def msg_received(self, msg):
        print(f"Message: {msg}")
    
    def event_received(self, event):
        """Monitor socket events."""
        event_names = {
            zmq.EVENT_CONNECTED: 'CONNECTED',
            zmq.EVENT_CONNECT_DELAYED: 'CONNECT_DELAYED',
            zmq.EVENT_CONNECT_RETRIED: 'CONNECT_RETRIED',
            zmq.EVENT_LISTENING: 'LISTENING',
            zmq.EVENT_BIND_FAILED: 'BIND_FAILED',
            zmq.EVENT_ACCEPTED: 'ACCEPTED',
            zmq.EVENT_ACCEPT_FAILED: 'ACCEPT_FAILED',
            zmq.EVENT_CLOSED: 'CLOSED',
            zmq.EVENT_CLOSE_FAILED: 'CLOSE_FAILED',
            zmq.EVENT_DISCONNECTED: 'DISCONNECTED',
        }
        name = event_names.get(event.event, f'UNKNOWN({event.event})')
        print(f"Event: {name} on {event.endpoint}")
    
    def connection_lost(self, exc):
        print(f"Connection lost: {exc}")

async def main():
    # Server with monitoring
    server_transport, _ = await aiozmq.create_zmq_connection(
        MonitoredProtocol,
        zmq.ROUTER,
        bind='tcp://*:5557'
    )
    
    # Client with monitoring
    client_transport, _ = await aiozmq.create_zmq_connection(
        MonitoredProtocol,
        zmq.DEALER,
        connect='tcp://127.0.0.1:5557'
    )
    
    await asyncio.sleep(1)
    
    # Send message
    client_transport.write((b'test',))
    
    await asyncio.sleep(0.5)
    
    client_transport.close()
    server_transport.close()

asyncio.run(main())
```

## Migration Guide

### From pyzmq Polling

```python
# Old: Manual polling with pyzmq
import zmq
from zmq import poller

socket = context.socket(zmq.DEALER)
poller = poller.Poller()
poller.register(socket, zmq.POLLIN)

while True:
    events = dict(poller.poll(timeout=1000))
    if socket in events:
        msg = socket.recv_multipart()
        # Process message

# New: Async with aiozmq
class Protocol(aiozmq.ZmqProtocol):
    def msg_received(self, msg):
        # Automatically called when message arrives
        process_message(msg)

transport, protocol = await aiozmq.create_zmq_connection(
    Protocol, zmq.DEALER, connect='tcp://*:5555'
)
```

### From Synchronous Code

```python
# Old: Synchronous pyzmq
socket = context.socket(zmq.REQ)
socket.connect('tcp://server:5555')
socket.send(b'request')
response = socket.recv()

# New: Async aiozmq
class Protocol(aiozmq.ZmqProtocol):
    def __init__(self, future):
        self.transport = None
        self.future = future
    
    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(b'request')
    
    def msg_received(self, msg):
        self.future.set_result(msg)
        self.transport.close()

future = asyncio.Future()
transport, protocol = await aiozmq.create_zmq_connection(
    lambda: Protocol(future),
    zmq.REQ,
    connect='tcp://server:5555'
)
response = await future
```

## Best Practices

1. **Use streams for most cases**: Core API is powerful but streams are simpler
2. **Handle connection_lost properly**: Clean up resources in this callback
3. **Don't block in callbacks**: Use asyncio tasks for long operations
4. **Close transports explicitly**: Prevent resource leaks
5. **Use event monitoring for debugging**: Track connection state changes
6. **Set socket options before binding**: Configure via zmq_sock parameter
