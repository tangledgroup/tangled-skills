# aiozmq RPC Framework

The RPC framework provides a high-level abstraction for remote procedure calls over ZeroMQ, with automatic serialization, method discovery, type validation, and exception handling.

## Core Concepts

### Handler Classes

Handlers define the methods available for remote invocation:

```python
import aiozmq.rpc

class MyHandler(aiozmq.rpc.AttrHandler):
    """Base class for attribute-based RPC handlers."""
    
    @aiozmq.rpc.method
    def add(self, a: int, b: int) -> int:
        """Add two numbers. Type hints are used for validation."""
        return a + b
    
    @aiozmq.rpc.method  
    def greet(self, name: str, greeting: str = "Hello") -> str:
        """Greet someone with optional custom greeting."""
        return f"{greeting}, {name}!"
    
    # This method won't be accessible via RPC (no decorator)
    def local_only(self):
        pass
```

### Method Decorator

The `@aiozmq.rpc.method` decorator:
- Marks methods as RPC endpoints
- Extracts function signature for validation
- Enables automatic serialization/deserialization

```python
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    async def async_method(self, data: str) -> str:
        """Async methods are fully supported."""
        await asyncio.sleep(1)
        return f"Processed: {data}"
    
    @aiozmq.rpc.method
    def sync_method(self, data: str) -> str:
        """Sync methods work too."""
        return f"Result: {data}"
```

## Starting RPC Services

### Request-Reply Server

```python
import asyncio
import aiozmq.rpc

class CalculatorHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def add(self, a: float, b: float) -> float:
        return a + b
    
    @aiozmq.rpc.method
    def multiply(self, a: float, b: float) -> float:
        return a * b

async def start_server():
    server = await aiozmq.rpc.serve_rpc(
        CalculatorHandler(),
        bind='tcp://*:5555',
        log_exceptions=True  # Log errors from remote calls
    )
    
    addr = list(server.transport.bindings())[0]
    print(f"RPC Server listening on {addr}")
    
    # Keep running...
    await asyncio.sleep(3600)
```

### Request-Reply Client

```python
async def use_client():
    client = await aiozmq.rpc.connect_rpc(
        connect='tcp://127.0.0.1:5555',
        timeout=5.0  # Call timeout in seconds
    )
    
    # Call remote methods
    result = await client.call.add(10, 20)
    print(f"10 + 20 = {result}")
    
    product = await client.call.multiply(5, 6)
    print(f"5 * 6 = {product}")
    
    client.close()
    await client.wait_closed()
```

## Advanced Server Options

### Exception Logging

```python
server = await aiozmq.rpc.serve_rpc(
    handler,
    bind='tcp://*:5555',
    log_exceptions=True,  # Log all exceptions
    exclude_log_exceptions=(ValueError,)  # Don't log ValueError
)
```

### Custom Serialization

```python
import msgpack

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Define custom type translators
translation_table = {
    0: (
        Point,  # Target class
        lambda obj: msgpack.packb((obj.x, obj.y)),  # Pack function
        lambda data: Point(*msgpack.unpackb(data))   # Unpack function
    ),
}

server = await aiozmq.rpc.serve_rpc(
    handler,
    bind='tcp://*:5555',
    translation_table=translation_table
)
```

### Call Timeout

```python
# Server-side timeout for long-running calls
server = await aiozmq.rpc.serve_rpc(
    handler,
    bind='tcp://*:5555',
    timeout=30.0  # Max 30 seconds per call
)
```

## Advanced Client Options

### Error Translation

Translate server exceptions to client-side types:

```python
class CustomServerError(Exception):
    pass

# Map server exception types to client types
error_table = {
    'mymodule.MyError': CustomServerError,
    'builtins.ValueError': ValueError,
}

client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    error_table=error_table
)

try:
    await client.call.risky_operation()
except CustomServerError as e:
    print(f"Server error: {e}")
```

### Client Timeout

```python
client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    timeout=5.0  # All calls timeout after 5 seconds
)

try:
    result = await client.call.slow_method()
except asyncio.TimeoutError:
    print("Call timed out")
```

### Custom Serialization (Client)

```python
client = await aiozmq.rpc.connect_rpc(
    connect='tcp://127.0.0.1:5555',
    translation_table=translation_table,  # Same as server
    error_table=error_table
)

# Send custom objects
point = Point(10, 20)
result = await client.call.process_point(point)
```

## Calling Remote Methods

### Basic Calls

```python
client = await aiozmq.rpc.connect_rpc(connect='tcp://*:5555')

# Positional arguments
result = await client.call.add(1, 2)

# Keyword arguments  
result = await client.call.greet(name="World")

# Mixed arguments
result = await client.call.greet("World", greeting="Hola")
```

### Error Handling

```python
from aiozmq.rpc import NotFoundError, ParametersError, GenericError

try:
    # Method doesn't exist
    await client.call.nonexistent_method()
except NotFoundError as e:
    print(f"Method not found: {e}")

try:
    # Wrong arguments
    await client.call.add("not", "numbers")
except ParametersError as e:
    print(f"Invalid parameters: {e}")

try:
    # Server raised exception
    await client.call.will_fail()
except GenericError as e:
    print(f"Server error: {e.exc_type} - {e.arguments}")
```

### Type Validation

RPC methods validate arguments against type hints:

```python
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def process(self, value: int, name: str = "default") -> str:
        return f"{name}: {value}"

# Client side validation happens server-side
await client.call.process(42)           # OK
await client.call.process(42, "test")   # OK  
await client.call.process("not int")    # Raises ParametersError
await client.call.process()             # Raises ParametersError (missing required)
```

## Alternative Handler Types

### Dict Handler

Use dict for dynamic method lookup:

```python
async def handle_add(a: int, b: int):
    return a + b

async def handle_subtract(a: int, b: int):
    return a - b

# Dict-based handler
handler = {
    'add': handle_add,
    'subtract': handle_subtract,
}

server = await aiozmq.rpc.serve_rpc(handler, bind='tcp://*:5555')
```

### Dynamic Handler

Implement `__getitem__` for custom lookup:

```python
class DynamicHandler(aiozmq.rpc.AbstractHandler):
    def __init__(self):
        self.methods = {}
    
    def __getitem__(self, key):
        # Custom lookup logic
        if key in self.methods:
            return self.methods[key]
        raise KeyError(key)
    
    def register(self, name, func):
        self.methods[name] = func

handler = DynamicHandler()
handler.register('add', lambda a, b: a + b)
```

### Nested Namespaces

Organize methods in namespaces:

```python
class MathHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def add(self, a: int, b: int) -> int:
        return a + b

class StringHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method  
    def upper(self, text: str) -> str:
        return text.upper()

# Nested handler
root_handler = {
    'math': MathHandler(),
    'string': StringHandler(),
}

server = await aiozmq.rpc.serve_rpc(root_handler, bind='tcp://*:5555')

# Client calls with namespace
client = await aiozmq.rpc.connect_rpc(connect='tcp://*:5555')
result = await client.call.math.add(1, 2)        # Calls math.add
result = await client.call.string.upper("hi")    # Calls string.upper
```

## Service Lifecycle

### Starting and Stopping

```python
async def manage_lifecycle():
    # Start server
    server = await aiozmq.rpc.serve_rpc(
        MyHandler(),
        bind='tcp://*:5555'
    )
    
    print(f"Server started on {list(server.transport.bindings())[0]}")
    
    # Server runs...
    await asyncio.sleep(60)
    
    # Graceful shutdown
    server.close()
    await server.wait_closed()  # Wait for cleanup
    
    print("Server stopped")
```

### Dynamic Bind/Connect

```python
server = await aiozmq.rpc.serve_rpc(handler, bind='tcp://*:5555')

# Add more endpoints dynamically
await server.transport.bind('ipc:///tmp/myrpc')

# Check current bindings
for addr in server.transport.bindings():
    print(f"Bound to: {addr}")
```

### Client Connection Management

```python
async def robust_client():
    client = await aiozmq.rpc.connect_rpc(
        connect='tcp://server1:5555'
    )
    
    try:
        while True:
            result = await client.call.get_data()
            process(result)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        await client.wait_closed()
```

## Complete Example: Task Queue

```python
import asyncio
import aiozmq.rpc
from typing import Dict, Any

class TaskQueueHandler(aiozmq.rpc.AttrHandler):
    def __init__(self):
        self.tasks: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
    
    @aiozmq.rpc.method
    def submit_task(self, task_id: str, data: str) -> bool:
        """Submit a new task."""
        self.tasks[task_id] = data
        return True
    
    @aiozmq.rpc.method
    def get_task(self, task_id: str) -> str:
        """Get task data for processing."""
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks.pop(task_id)
    
    @aiozmq.rpc.method
    def store_result(self, task_id: str, result: str) -> bool:
        """Store task result."""
        self.results[task_id] = result
        return True
    
    @aiozmq.rpc.method
    def get_result(self, task_id: str) -> str:
        """Get completed task result."""
        if task_id not in self.results:
            raise KeyError(f"Result {task_id} not ready")
        return self.results.pop(task_id)

async def queue_server():
    server = await aiozmq.rpc.serve_rpc(
        TaskQueueHandler(),
        bind='tcp://*:5557',
        log_exceptions=True
    )
    print(f"Task queue on {list(server.transport.bindings())[0]}")
    await asyncio.sleep(3600)

async def worker(worker_id: int):
    client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5557')
    
    while True:
        try:
            # Try to get a task (polling)
            task_id = f"task_{worker_id}_{asyncio.get_event_loop().time()}"
            
            # In real scenario, would have dedicated "get_next_task" method
            await asyncio.sleep(1)
            
        except KeyError:
            # No tasks available
            await asyncio.sleep(0.5)
            continue
        finally:
            # Keep connection alive
            pass
    
    client.close()
    await client.wait_closed()

async def main():
    server_task = asyncio.create_task(queue_server())
    
    await asyncio.sleep(0.5)
    
    # Start workers
    workers = [asyncio.create_task(worker(i)) for i in range(3)]
    
    await asyncio.sleep(10)
    
    for w in workers:
        w.cancel()
    
    server_task.cancel()

asyncio.run(main())
```

## Troubleshooting

### Method Not Found

Ensure methods are decorated:

```python
class Handler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method  # Required!
    def my_method(self):
        pass
```

### Serialization Errors

Check translation_table matches on both sides:

```python
# Server and client must have matching tables
translation_table = {0: (MyClass, pack_func, unpack_func)}

server = await aiozmq.rpc.serve_rpc(handler, translation_table=translation_table)
client = await aiozmq.rpc.connect_rpc(translation_table=translation_table)
```

### Timeout Issues

Adjust timeouts based on operation complexity:

```python
# Server timeout for long operations
server = await aiozmq.rpc.serve_rpc(handler, timeout=60.0)

# Client timeout for calls
client = await aiozmq.rpc.connect_rpc(timeout=30.0)
```
