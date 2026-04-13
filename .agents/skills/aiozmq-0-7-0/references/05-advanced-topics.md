# aiozmq Advanced Topics

This reference covers advanced aiozmq features: custom serialization, exception translation, nested namespaces, monitoring, and production patterns.

## Custom Serialization

### Understanding the Translation Table

aiozmq uses msgpack for serialization. For custom types, define a translation table:

```python
import msgpack
import aiozmq.rpc

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

# Translation table format:
# type_id: (class, pack_func, unpack_func)
translation_table = {
    0: (
        Point,  # Target class
        lambda obj: msgpack.packb((obj.x, obj.y)),  # Pack to bytes
        lambda data: Point(*msgpack.unpackb(data))   # Unpack from bytes
    ),
}

class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def reflect(self, point: Point) -> Point:
        return point

# Both server and client need same table
server = await aiozmq.rpc.serve_rpc(
    Handler(),
    bind='tcp://*:5555',
    translation_table=translation_table
)

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    translation_table=translation_table
)

# Now can send custom objects
result = await client.call.reflect(Point(10, 20))
assert result == Point(10, 20)
```

### Multiple Custom Types

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Circle:
    def __init__(self, radius):
        self.radius = radius

translation_table = {
    0: (Point,
        lambda p: msgpack.packb(('point', p.x, p.y)),
        lambda d: Point(*msgpack.unpackb(d)[1:])),
    
    1: (Rectangle,
        lambda r: msgpack.packb(('rect', r.width, r.height)),
        lambda d: Rectangle(*msgpack.unpackb(d)[1:])),
    
    2: (Circle,
        lambda c: msgpack.packb(('circle', c.radius)),
        lambda d: Circle(msgpack.unpackb(d)[1])),
}

class GeometryHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def process_shape(self, shape) -> str:
        if isinstance(shape, Point):
            return f"Point at ({shape.x}, {shape.y})"
        elif isinstance(shape, Rectangle):
            return f"Rectangle {shape.width}x{shape.height}"
        elif isinstance(shape, Circle):
            return f"Circle radius {shape.radius}"
```

### Nested Custom Objects

```python
class Address:
    def __init__(self, street, city, zip_code):
        self.street = street
        self.city = city
        self.zip_code = zip_code

class Person:
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address  # Nested Address object

translation_table = {
    0: (Address,
        lambda a: msgpack.packb((a.street, a.city, a.zip_code)),
        lambda d: Address(*msgpack.unpackb(d))),
    
    1: (Person,
        lambda p: msgpack.packb((p.name, p.age, p.address)),
        lambda d: Person(msgpack.unpackb(d)[0], msgpack.unpackb(d)[1], None)),  # Address handled separately
}

# Note: Nested objects may need special handling
```

### DateTime Serialization

```python
from datetime import datetime, date

translation_table = {
    0: (datetime,
        lambda dt: msgpack.packb(dt.isoformat().encode()),
        lambda d: datetime.fromisoformat(msgpack.unpackb(d).decode())),
    
    1: (date,
        lambda d: msgpack.packb(d.isoformat().encode()),
        lambda d: date.fromisoformat(msgpack.unpackb(d).decode())),
}

class TimeHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def current_time(self) -> datetime:
        return datetime.now()
    
    @aiozmq.rpc.method
    def schedule(self, dt: datetime) -> str:
        return f"Scheduled for {dt}"
```

## Exception Translation

### Server-Side Exceptions

By default, server exceptions become `GenericError` on client:

```python
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def risky(self, value: int):
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

client = await aiozmq.rpc.connect_rpc(connect='tcp://*:5555')

try:
    await client.call.risky(-1)
except aiozmq.rpc.GenericError as e:
    print(f"Generic error: {e.exc_type} - {e.arguments}")
    # Output: Generic error: builtins.ValueError - ('Value must be positive',)
```

### Custom Exception Mapping

Map server exceptions to client-side types:

```python
class BusinessError(Exception):
    """Custom business logic error."""
    pass

class ValidationError(Exception):
    """Validation failed."""
    pass

# Error table maps fully-qualified exception names to local classes
error_table = {
    'mymodule.BusinessError': BusinessError,
    'builtins.ValueError': ValidationError,
    'builtins.KeyError': KeyError,
}

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    error_table=error_table
)

try:
    await client.call.risky(-1)
except ValidationError as e:
    print(f"Validation failed: {e}")

try:
    await client.call.custom_error()
except BusinessError as e:
    print(f"Business error: {e}")
```

### Custom Exception Classes

Define matching exceptions on both sides:

```python
# Shared module with exception definitions
# errors.py
class TaskNotFoundError(Exception):
    pass

class TaskCompletedError(Exception):
    pass

# Server
from errors import TaskNotFoundError

class TaskHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def get_task(self, task_id: str):
        if task_id not in self.tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self.tasks[task_id]

# Client  
from errors import TaskNotFoundError

error_table = {
    'errors.TaskNotFoundError': TaskNotFoundError,
}

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://*:5555',
    error_table=error_table
)

try:
    task = await client.call.get_task("nonexistent")
except TaskNotFoundError as e:
    print(f"Task not found: {e}")
```

### Automatic Error Table

aiozmq provides helper to build error table:

```python
from aiozmq.rpc.util import _fill_error_table

# Creates default mapping for common exceptions
default_error_table = _fill_error_table()

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://*:5555',
    error_table=default_error_table
)
```

## Nested Namespaces

### Basic Namespace Structure

Organize methods in hierarchical namespaces:

```python
class MathHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def add(self, a: int, b: int) -> int:
        return a + b
    
    @aiozmq.rpc.method
    def subtract(self, a: int, b: int) -> int:
        return a - b

class StringHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def upper(self, text: str) -> str:
        return text.upper()
    
    @aiozmq.rpc.method
    def lower(self, text: str) -> str:
        return text.lower()

# Create namespace hierarchy
root_handler = {
    'math': MathHandler(),
    'string': StringHandler(),
}

server = await aiozmq.rpc.serve_rpc(root_handler, bind='tcp://*:5555')

# Client calls with namespace prefix
client = await aiozmq.rpc.connect_rpc(connect='tcp://*:5555')

result = await client.call.math.add(10, 5)          # Calls MathHandler.add
result = await client.call.string.upper("hello")    # Calls StringHandler.upper
```

### Deep Nesting

Three or more levels of nesting:

```python
class UserAuthHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def login(self, username: str, password: str) -> str:
        return "token123"
    
    @aiozmq.rpc.method
    def logout(self, token: str) -> bool:
        return True

class UserProfileHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def get_name(self, user_id: int) -> str:
        return "John Doe"
    
    @aiozmq.rpc.method
    def get_email(self, user_id: int) -> str:
        return "john@example.com"

class UserHandler(aiozmq.rpc.AttrHandler):
    pass  # Namespace container

# Deep structure
user_handler = UserHandler()
user_handler.auth = UserAuthHandler()
user_handler.profile = UserProfileHandler()

root_handler = {
    'user': user_handler,
}

server = await aiozmq.rpc.serve_rpc(root_handler, bind='tcp://*:5555')

# Client calls
client = await aiozmq.rpc.connect_rpc(connect='tcp://*:5555')

token = await client.call.user.auth.login("john", "secret")
name = await client.call.user.profile.get_name(123)
```

### Dict-Based Namespaces

Use dicts for dynamic namespace creation:

```python
async def handle_add(a: int, b: int):
    return a + b

async def handle_multiply(a: int, b: int):
    return a * b

async def handle_upper(text: str):
    return text.upper()

# Dict-based namespaces
root_handler = {
    'math': {
        'add': handle_add,
        'multiply': handle_multiply,
    },
    'string': {
        'upper': handle_upper,
    },
}

server = await aiozmq.rpc.serve_rpc(root_handler, bind='tcp://*:5555')
```

### Dynamic Namespace Lookup

Implement custom `__getitem__` for dynamic routing:

```python
class RouterHandler(aiozmq.rpc.AbstractHandler):
    def __init__(self):
        self.namespaces = {}
    
    def __getitem__(self, key):
        """Dynamic namespace lookup."""
        if key not in self.namespaces:
            raise KeyError(f"Namespace '{key}' not found")
        return self.namespaces[key]
    
    def register_namespace(self, name, handler):
        self.namespaces[name] = handler

# Usage
router = RouterHandler()
router.register_namespace('users', UserHandler())
router.register_namespace('orders', OrderHandler())

server = await aiozmq.rpc.serve_rpc(router, bind='tcp://*:5555')
```

## Socket Monitoring

### Event Types

ZeroMQ provides socket event notifications:

```python
from aiozmq import SocketEvent
import zmq

EVENT_NAMES = {
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
    zmq.EVENT_MONITOR_STOPPED: 'MONITOR_STOPPED',
}

class MonitoredProtocol(aiozmq.ZmqProtocol):
    def event_received(self, event: SocketEvent):
        name = EVENT_NAMES.get(event.event, f'UNKNOWN({event.event})')
        print(f"[{name}] endpoint={event.endpoint}, value={event.value}")
```

### Monitoring with Streams

```python
import aiozmq
import zmq

async def monitor_connection():
    stream = await aiozmq.create_zmq_stream(
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555',
        events_backlog=100  # Keep last 100 events
    )
    
    # Read events concurrently with messages
    async def event_reader():
        while True:
            try:
                event = await stream.read_event()
                print(f"Event: {event}")
            except aiozmq.ZmqStreamClosed:
                break
    
    event_task = asyncio.create_task(event_reader())
    
    # Use stream normally
    for i in range(5):
        stream.write((f"message {i}".encode(),))
        await stream.drain()
        await asyncio.sleep(0.5)
    
    event_task.cancel()
    stream.close()
```

### Connection Health Monitoring

```python
class HealthMonitor:
    def __init__(self):
        self.connected = False
        self.last_event = None
        self.event_count = 0
    
    def on_event(self, event):
        self.last_event = event
        self.event_count += 1
        
        if event.event == zmq.EVENT_CONNECTED:
            self.connected = True
            print(f"Connected to {event.endpoint}")
        elif event.event == zmq.EVENT_DISCONNECTED:
            self.connected = False
            print(f"Disconnected from {event.endpoint}")
        elif event.event == zmq.EVENT_CONNECT_DELAYED:
            print(f"Connection delayed to {event.endpoint}")

class MonitoredProtocol(aiozmq.ZmqProtocol):
    def __init__(self, monitor):
        self.transport = None
        self.monitor = monitor
    
    def connection_made(self, transport):
        self.transport = transport
    
    def event_received(self, event):
        self.monitor.on_event(event)
    
    def msg_received(self, msg):
        # Process message
        pass

async def main():
    monitor = HealthMonitor()
    transport, protocol = await aiozmq.create_zmq_connection(
        lambda: MonitoredProtocol(monitor),
        zmq.DEALER,
        connect='tcp://127.0.0.1:5555'
    )
    
    await asyncio.sleep(5)
    
    print(f"Connected: {monitor.connected}")
    print(f"Events: {monitor.event_count}")
    
    transport.close()
```

## Production Patterns

### Connection Pooling

```python
from collections import deque
import asyncio

class ConnectionPool:
    def __init__(self, endpoint, max_size=10):
        self.endpoint = endpoint
        self.max_size = max_size
        self.available = deque()
        self.in_use = set()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            if self.available:
                client = self.available.popleft()
            elif len(self.in_use) < self.max_size:
                client = await aiozmq.rpc.connect_rpc(connect=self.endpoint)
            else:
                # Wait for available connection
                waiters = asyncio.Future()
                # Implement waiting logic...
                await waiters
                return await self.acquire()
            
            self.in_use.add(client)
            return client
    
    async def release(self, client):
        async with self.lock:
            self.in_use.discard(client)
            self.available.append(client)
    
    async def close_all(self):
        async with self.lock:
            for client in self.available:
                client.close()
                await client.wait_closed()
            for client in self.in_use:
                client.close()
                await client.wait_closed()
            self.available.clear()
            self.in_use.clear()

# Usage
pool = ConnectionPool('tcp://server:5555', max_size=20)

async def worker():
    client = await pool.acquire()
    try:
        result = await client.call.process(data)
        return result
    finally:
        await pool.release(client)
```

### Retry with Exponential Backoff

```python
import asyncio

async def call_with_retry(client, method_name, *args, max_retries=5, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            method = getattr(client.call, method_name)
            return await method(*args)
        except (aiozmq.rpc.ServiceClosedError, ConnectionResetError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s")
            await asyncio.sleep(delay)
    
    raise RuntimeError("Max retries exceeded")

# Usage
result = await call_with_retry(client, 'process', data)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if asyncio.get_event_loop().time() - self.last_failure > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise CircuitOpenError("Circuit is open")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failures = 0
        self.state = 'closed'
    
    def on_failure(self):
        self.failures += 1
        self.last_failure = asyncio.get_event_loop().time()
        if self.failures >= self.failure_threshold:
            self.state = 'open'

class CircuitOpenError(Exception):
    pass

# Usage
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

async def resilient_call(client, method_name, *args):
    method = getattr(client.call, method_name)
    return await breaker.call(method, *args)
```

### Request Timeout and Cancellation

```python
async def call_with_timeout(client, method_name, timeout, *args):
    try:
        method = getattr(client.call, method_name)
        return await asyncio.wait_for(method(*args), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"Call to {method_name} timed out after {timeout}s")
        raise

async def call_with_cancellation(client, method_name, *args):
    token = asyncio.current_task()
    
    try:
        method = getattr(client.call, method_name)
        return await method(*args)
    except asyncio.CancelledError:
        print("Call was cancelled")
        raise

# Usage with timeout
result = await call_with_timeout(client, 'slow_method', 5.0)

# Usage with cancellation
task = asyncio.create_task(call_with_cancellation(client, 'long_running'))
await asyncio.sleep(2)
task.cancel()
```

### Logging and Metrics

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rpc')

class LoggingHandler(aiozmq.rpc.AttrHandler):
    def __init__(self, base_handler):
        self.base_handler = base_handler
        self.metrics = {
            'calls': {},
            'errors': 0,
            'total_time': 0,
        }
    
    @aiozmq.rpc.method
    def any_method(self, *args, **kwargs):
        """This won't work - need to wrap differently."""
        pass

# Better approach: wrapper
class MetricsWrapper:
    def __init__(self, handler):
        self.handler = handler
    
    async def call(self, method_name, *args, **kwargs):
        start = datetime.now()
        try:
            method = getattr(self.handler, method_name)
            result = await method(*args, **kwargs) if asyncio.iscoroutinefunction(method) else method(*args, **kwargs)
            
            duration = (datetime.now() - start).total_seconds()
            self.metrics['calls'][method_name] = self.metrics['calls'].get(method_name, 0) + 1
            self.metrics['total_time'] += duration
            
            logger.info(f"{method_name} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            logger.error(f"{method_name} failed: {e}")
            raise

# Usage with server-side logging
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def process(self, data: str):
        logger.info(f"Processing: {data}")
        return f"Processed: {data}"

server = await aiozmq.rpc.serve_rpc(
    Handler(),
    bind='tcp://*:5555',
    log_exceptions=True
)
```

## Troubleshooting Advanced Features

### Serialization Issues

```python
# Problem: Type not recognized
class CustomType:
    pass

# Error: TypeError: Cannot serialize CustomType

# Solution: Add to translation table
translation_table = {
    0: (CustomType, pack_func, unpack_func),
}
```

### Namespace Resolution

```python
# Problem: Method not found in namespace
client.call.math.add(1, 2)  # NotFoundError

# Debug: Check namespace structure
root_handler = {'math': MathHandler()}  # Correct
# Not: root_handler = MathHandler()  # Missing namespace level
```

### Event Monitoring Not Working

```python
# Problem: event_received not called

# Solution: Ensure protocol implements the method
class Protocol(aiozmq.ZmqProtocol):
    def event_received(self, event):  # Must implement
        print(event)
```
