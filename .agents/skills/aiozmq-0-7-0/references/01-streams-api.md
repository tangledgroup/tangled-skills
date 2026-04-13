# aiozmq Streams API

The `ZmqStream` abstraction provides a high-level async interface for ZeroMQ sockets with familiar `read()`/`write()` methods, automatic flow control, and backpressure support.

## Creating Streams

### Basic Usage

```python
import asyncio
import aiozmq
import zmq

async def main():
    # Create a stream with bind (server/listener)
    server = await aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:5555'
    )
    
    # Create a stream with connect (client/initiator)
    client = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
```

### Multiple Endpoints

```python
# Bind to multiple endpoints
server = await aiozmq.create_zmq_stream(
    zmq.ROUTER,
    bind=['tcp://*:5555', 'ipc:///tmp/server']
)

# Connect with redundancy
client = await aiozmq.create_zmq_stream(
    zmq.DEALER,
    connect=['tcp://server1:5555', 'tcp://server2:5555']
)
```

### Using Existing Socket

```python
import zmq

# Create pyzmq socket manually
context = zmq.Context()
sock = context.socket(zmq.ROUTER)
sock.setsockopt(zmq.IDENTITY, b'myserver')

# Wrap with aiozmq stream
stream = await aiozmq.create_zmq_stream(
    zmq.ROUTER,
    bind='tcp://*:5555',
    zmq_sock=sock  # Reuse existing socket
)
```

## Stream Operations

### Writing Messages

```python
async def write_examples(stream):
    # Write single frame (bytes)
    stream.write(b'hello')
    
    # Write multi-frame message (tuple of bytes)
    stream.write((b'frame1', b'frame2', b'frame3'))
    
    # For flow control, await drain after write
    stream.write(b'large_message')
    await stream.drain()  # Wait for buffer to flush
```

### Reading Messages

```python
async def read_examples(stream):
    # Read returns tuple of byte strings (frames)
    msg = await stream.read()
    
    # Single frame message
    if len(msg) == 1:
        data = msg[0]
    
    # Multi-frame message
    identity, *frames = msg
    print(f"From {identity}: {frames}")
    
    # Read with timeout
    try:
        await asyncio.wait_for(stream.read(), timeout=5.0)
    except asyncio.TimeoutError:
        print("No message within 5 seconds")
```

### Reading Socket Events

```python
from aiozmq import create_zmq_connection
import zmq

async def monitor_socket():
    # Create stream with event monitoring
    stream = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555',
        events_backlog=100  # Keep last 100 events
    )
    
    # Read socket events (connects, disconnects, etc.)
    event = await stream.read_event()
    print(f"Event: {event.event} on {event.endpoint}")
```

## Flow Control

### Write Buffer Limits

```python
# Set write buffer limits (defaults: high=64KB, low=16KB)
stream = await aiozmq.create_zmq_stream(
    zmq.DEALER,
    connect='tcp://127.0.0.1:5555',
    high_write=128*1024,  # 128KB
    low_write=32*1024     # 32KB
)

# Or set dynamically
stream.transport.set_write_buffer_limits(high=65536, low=16384)
```

### Read Buffer Limits

```python
# Set read buffer limits
stream = await aiozmq.create_zmq_stream(
    zmq.ROUTER,
    bind='tcp://*:5555',
    high_read=256*1024,  # 256KB
    low_read=64*1024     # 64KB
)

# Dynamic adjustment
stream.set_read_buffer_limits(high=131072, low=32768)
```

### Using drain() for Backpressure

```python
async def producer(stream):
    for i in range(1000):
        data = create_large_message(i)
        stream.write(data)
        
        # Wait if write buffer fills up
        await stream.drain()
        
        print(f"Sent message {i}")

async def consumer(stream):
    while True:
        try:
            msg = await asyncio.wait_for(stream.read(), timeout=1.0)
            process(msg)
        except asyncio.TimeoutError:
            break
```

## Stream Properties and Methods

### Transport Access

```python
stream = await aiozmq.create_zmq_stream(zmq.DEALER, connect='tcp://*:5555')

# Access underlying transport
transport = stream.transport

# Get bound addresses
addresses = list(transport.bindings())

# Get connected addresses  
connections = list(transport.connections())

# Dynamic bind/connect
await transport.bind('tcp://*:5556')
await transport.connect('tcp://server2:5555')

# Get socket options
sock_type = transport.getsockopt(zmq.TYPE)
```

### Extra Info

```python
# Get additional connection info
stream = await aiozmq.create_zmq_stream(zmq.DEALER, connect='tcp://127.0.0.1:5555')

# Access transport extra info
peer_addr = stream.get_extra_info('peer_addr')
sock = stream.get_extra_info('socket')
```

### Closing Streams

```python
async def cleanup(stream):
    # Soft close - drain pending writes
    stream.close()
    
    # For RPC services, wait for full cleanup
    # await service.wait_closed()
```

## Exceptions

### ZmqStreamClosed

```python
from aiozmq import ZmqStreamClosed

async def robust_reader(stream):
    while True:
        try:
            msg = await stream.read()
            process(msg)
        except ZmqStreamClosed:
            print("Stream closed gracefully")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
```

### Handling Connection Loss

```python
async def monitor_connection(stream):
    try:
        while True:
            msg = await stream.read()
            # Process message
    except asyncio.CancelledError:
        print("Operation cancelled")
    finally:
        stream.close()
```

## Complete Examples

### DEALER-ROUTER Chat

```python
import asyncio
import aiozmq
import zmq

async def router_handler():
    router = await aiozmq.create_zmq_stream(
        zmq.ROUTER,
        bind='tcp://127.0.0.1:5555'
    )
    
    clients = {}
    
    while True:
        try:
            msg = await router.read()
            identity, *message = msg
            
            # Register new clients
            if identity not in clients:
                clients[identity] = True
                print(f"Client connected: {identity}")
            
            # Broadcast to all clients
            for client_id in clients:
                router.write((client_id, *message))
                await router.drain()
                
        except Exception as e:
            print(f"Router error: {e}")
            break
    
    router.close()

async def client(client_name):
    dealer = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    
    # Send messages
    for i in range(5):
        msg = (f"Message {i} from {client_name}".encode())
        dealer.write(msg)
        await dealer.drain()
        await asyncio.sleep(0.5)
    
    # Receive responses
    for _ in range(3):
        try:
            response = await asyncio.wait_for(dealer.read(), timeout=2.0)
            print(f"Received: {response}")
        except asyncio.TimeoutError:
            break
    
    dealer.close()

async def main():
    router_task = asyncio.create_task(router_handler())
    
    await asyncio.sleep(0.5)  # Let router start
    
    client1 = asyncio.create_task(client("Alice"))
    client2 = asyncio.create_task(client("Bob"))
    
    await asyncio.gather(client1, client2)
    await asyncio.sleep(0.5)
    
    router_task.cancel()

asyncio.run(main())
```

### PUB-SUB with Streams

```python
import asyncio
import aiozmq
import zmq

async def publisher():
    pub = await aiozmq.create_zmq_stream(
        zmq.PUB,
        bind='tcp://*:5556'
    )
    
    topics = ['news', 'sports', 'weather']
    counter = 0
    
    while counter < 10:
        for topic in topics:
            message = (topic.encode(), f"{counter}: {topic} update".encode())
            pub.write(message)
            await pub.drain()
            counter += 1
        await asyncio.sleep(0.5)
    
    pub.close()

async def subscriber(topic_filter):
    sub = await aiozmq.create_zmq_stream(
        zmq.SUB,
        connect='tcp://127.0.0.1:5556'
    )
    
    # Set subscription filter
    sub.transport.setsockopt(zmq.SUBSCRIBE, topic_filter.encode())
    
    print(f"Subscribed to: {topic_filter}")
    
    for _ in range(5):
        try:
            topic, message = await asyncio.wait_for(sub.read(), timeout=2.0)
            print(f"[{topic.decode()}] {message.decode()}")
        except asyncio.TimeoutError:
            break
    
    sub.close()

async def main():
    pub_task = asyncio.create_task(publisher())
    
    await asyncio.sleep(0.5)
    
    sub1 = asyncio.create_task(subscriber("news"))
    sub2 = asyncio.create_task(subscriber("sports"))
    
    await pub_task
    await asyncio.gather(sub1, sub2)

asyncio.run(main())
```

## Best Practices

1. **Always drain after critical writes**: Use `await stream.drain()` for important messages
2. **Set appropriate buffer limits**: Tune based on message size and frequency
3. **Handle ZmqStreamClosed**: Gracefully handle stream closure in readers
4. **Use timeouts**: Prevent indefinite blocking with `asyncio.wait_for()`
5. **Close streams properly**: Always call `stream.close()` in finally blocks
6. **Monitor events for debugging**: Use `read_event()` to track socket state changes

## Migration from Core API

If migrating from `create_zmq_connection`:

```python
# Old: Core API with custom protocol
class MyProtocol(aiozmq.ZmqProtocol):
    def msg_received(self, msg):
        self.queue.put_nowait(msg)

transport, protocol = await aiozmq.create_zmq_connection(
    MyProtocol, zmq.DEALER, connect='tcp://*:5555'
)

# New: Stream API
stream = await aiozmq.create_zmq_stream(
    zmq.DEALER, connect='tcp://*:5555'
)
msg = await stream.read()
```
