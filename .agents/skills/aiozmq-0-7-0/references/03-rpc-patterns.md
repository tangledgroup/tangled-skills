# aiozmq RPC Patterns

aiozmq provides three main RPC patterns beyond basic request-reply: Pipeline (push-pull) for fire-and-forget notifications, and Pub-Sub for broadcasting to multiple subscribers.

## Request-Reply Pattern

The standard RPC pattern with synchronous request/response semantics.

### Basic Example

```python
import asyncio
import aiozmq.rpc

class ServiceHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def compute(self, value: int) -> int:
        return value * 2

async def main():
    # Server
    server = await aiozmq.rpc.serve_rpc(
        ServiceHandler(),
        bind='tcp://*:5555'
    )
    
    # Client
    client = await aiozmq.rpc.connect_rpc(
        connect='tcp://127.0.0.1:5555'
    )
    
    # Synchronous call with response
    result = await client.call.compute(21)
    print(f"Result: {result}")  # Output: Result: 42
    
    client.close()
    server.close()

asyncio.run(main())
```

### Multiple Clients

```python
async def multi_client_example():
    server = await aiozmq.rpc.serve_rpc(
        ServiceHandler(),
        bind='tcp://*:5555'
    )
    
    # Create multiple clients
    clients = [
        await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5555')
        for _ in range(10)
    ]
    
    # All can make concurrent calls
    results = await asyncio.gather(*[
        client.call.compute(i) for i, client in enumerate(clients)
    ])
    
    print(f"Results: {results}")
    
    # Cleanup
    for client in clients:
        client.close()
        await client.wait_closed()
    
    server.close()
    await server.wait_closed()
```

### Load Balancing with DEALER/ROUTER

Request-Reply uses DEALER/ROUTER sockets internally, providing automatic load balancing:

```python
# Multiple backend servers
async def start_multiple_servers():
    handlers = [ServiceHandler() for _ in range(3)]
    servers = []
    
    for i, handler in enumerate(handlers):
        server = await aiozmq.rpc.serve_rpc(
            handler,
            bind=f'tcp://*:555{i}'
        )
        servers.append(server)
    
    return servers

# Client connects to one, can failover to others
async def resilient_client():
    endpoints = ['tcp://127.0.0.1:5550', 'tcp://127.0.0.1:5551', 'tcp://127.0.0.1:5552']
    
    for endpoint in endpoints:
        try:
            client = await aiozmq.rpc.connect_rpc(connect=endpoint)
            result = await client.call.compute(10)
            print(f"Success via {endpoint}: {result}")
            return
        except Exception as e:
            print(f"Failed {endpoint}: {e}")
            continue
```

## Pipeline (Push-Pull) Pattern

Fire-and-forget notifications without response. Useful for task distribution, logging, and event notification.

### Basic Pipeline

```python
import asyncio
import aiozmq.rpc

class TaskHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def process_task(self, task_id: str, data: str):
        """Receive and process a task (no return value)."""
        print(f"Processing {task_id}: {data}")
        # Simulate work
        asyncio.get_event_loop().call_later(
            0.1, lambda: print(f"Completed {task_id}")
        )

async def main():
    # Server (PULL side - receives notifications)
    listener = await aiozmq.rpc.serve_pipeline(
        TaskHandler(),
        bind='tcp://*:5556'
    )
    
    # Client (PUSH side - sends notifications)
    notifier = await aiozmq.rpc.connect_pipeline(
        connect='tcp://127.0.0.1:5556'
    )
    
    # Fire-and-forget calls (no await response)
    await notifier.notify.process_task("task-1", "Data A")
    await notifier.notify.process_task("task-2", "Data B")
    await notifier.notify.process_task("task-3", "Data C")
    
    await asyncio.sleep(0.5)  # Allow processing
    
    notifier.close()
    listener.close()

asyncio.run(main())
```

### Multiple Workers (Task Queue)

```python
async def task_queue_example():
    class WorkerHandler(aiozmq.rpc.AttrHandler):
        def __init__(self, worker_id: int):
            self.worker_id = worker_id
        
        @aiozmq.rpc.method
        def execute(self, job: dict):
            print(f"Worker {self.worker_id} executing: {job}")

    # Single listener accepts notifications
    handler = WorkerHandler(1)
    listener = await aiozmq.rpc.serve_pipeline(
        handler,
        bind='tcp://*:5557'
    )
    
    # Multiple notifiers can send tasks
    notifiers = [
        await aiozmq.rpc.connect_pipeline(connect='tcp://127.0.0.1:5557')
        for _ in range(5)
    ]
    
    # Send jobs from multiple sources
    for i, notifier in enumerate(notifiers):
        await notifier.notify.execute({"job_id": i, "data": f"Task {i}"})
    
    await asyncio.sleep(0.5)
    
    # Cleanup
    for n in notifiers:
        n.close()
    listener.close()
```

### Pipeline with Sub-handlers

Organize notifications by category:

```python
class LoggingHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def info(self, message: str):
        print(f"[INFO] {message}")
    
    @aiozmq.rpc.method
    def error(self, message: str):
        print(f"[ERROR] {message}")

async def structured_logging():
    listener = await aiozmq.rpc.serve_pipeline(
        LoggingHandler(),
        bind='tcp://*:5558'
    )
    
    notifier = await aiozmq.rpc.connect_pipeline(
        connect='tcp://127.0.0.1:5558'
    )
    
    # Call specific methods
    await notifier.notify.info("Application started")
    await notifier.notify.error("Database connection failed")
    
    notifier.close()
    listener.close()
```

## Publish-Subscribe Pattern

Broadcast messages to multiple subscribers with topic filtering.

### Basic Pub-Sub

```python
import asyncio
import aiozmq.rpc

class NewsHandler(aiozmq.rpc.AttrHandler):
    @aiozmq.rpc.method
    def broadcast(self, headline: str, content: str):
        print(f"Broadcasting: {headline} - {content}")

async def main():
    # Subscriber (server side - receives publications)
    subscriber = await aiozmq.rpc.serve_pubsub(
        NewsHandler(),
        subscribe='news',  # Topic filter
        bind='tcp://*:5559',
        log_exceptions=True
    )
    
    # Publisher (client side - sends to all subscribers)
    publisher = await aiozmq.rpc.connect_pubsub(
        connect='tcp://127.0.0.1:5559'
    )
    
    # Publish to specific topic
    await publisher.publish('news').broadcast(
        "Breaking News",
        "Something important happened!"
    )
    
    await asyncio.sleep(0.5)
    
    publisher.close()
    subscriber.close()

asyncio.run(main())
```

### Multiple Topics

```python
async def multi_topic_example():
    class MultiTopicHandler(aiozmq.rpc.AttrHandler):
        @aiozmq.rpc.method
        def update(self, topic: str, data: dict):
            print(f"[{topic}] {data}")

    # Subscribe to multiple topics
    subscriber = await aiozmq.rpc.serve_pubsub(
        MultiTopicHandler(),
        subscribe='sports',  # Can only specify one topic per subscriber
        bind='tcp://*:5560'
    )
    
    publisher = await aiozmq.rpc.connect_pubsub(
        connect='tcp://127.0.0.1:5560'
    )
    
    # Publish to different topics
    await publisher.publish('sports').update('sports', {'game': 'football'})
    await publisher.publish('news').update('news', {'headline': 'Election'})
    await publisher.publish('weather').update('weather', {'temp': 72})
    
    # Only 'sports' topic will be received
    
    await asyncio.sleep(0.5)
    
    publisher.close()
    subscriber.close()
```

### Multiple Subscribers

```python
async def fanout_example():
    class SubscriberHandler(aiozmq.rpc.AttrHandler):
        def __init__(self, name: str):
            self.name = name
        
        @aiozmq.rpc.method
        def receive(self, message: str):
            print(f"{self.name} received: {message}")

    # One publisher
    publisher = await aiozmq.rpc.connect_pubsub(
        connect='tcp://127.0.0.1:5561'
    )
    
    # Multiple subscribers on same topic
    subscribers = [
        await aiozmq.rpc.serve_pubsub(
            SubscriberHandler(f"Subscriber-{i}"),
            subscribe='all',
            bind=f'tcp://*:556{i}',
        )
        for i in range(3)
    ]
    
    # Actually, all subscribers need to connect to same publisher
    # This is a simplified example - real implementation would use
    # a central PUB socket
    
    await publisher.publish('all').receive("Broadcast message")
    
    await asyncio.sleep(0.5)
    
    publisher.close()
    for sub in subscribers:
        sub.close()
```

### Topic-Based Routing

```python
async def topic_routing():
    class RouterHandler(aiozmq.rpc.AttrHandler):
        @aiozmq.rpc.method
        def handle(self, data: str):
            print(f"Handling: {data}")
    
    # Create subscribers for different topics
    news_sub = await aiozmq.rpc.serve_pubsub(
        RouterHandler(),
        subscribe='news',
        bind='tcp://*:5562'
    )
    
    sports_sub = await aiozmq.rpc.serve_pubsub(
        RouterHandler(),
        subscribe='sports', 
        bind='tcp://*:5563'
    )
    
    # Publisher sends to both
    publisher = await aiozmq.rpc.connect_pubsub(
        connect='tcp://127.0.0.1:5562'  # Connect to news
    )
    
    await publisher.publish('news').handle("News update")
    
    # For sports, would need separate connection or use zmq.PUB directly
    
    await asyncio.sleep(0.5)
    
    publisher.close()
    news_sub.close()
    sports_sub.close()
```

## Pattern Comparison

| Feature | Request-Reply | Pipeline | Pub-Sub |
|---------|--------------|----------|---------|
| Socket Type | DEALER/ROUTER | PUSH/PULL | PUB/SUB |
| Response | Yes (await result) | No (fire-and-forget) | No (broadcast) |
| Use Case | RPC, queries | Task distribution, logging | Notifications, events |
| Client Access | `client.call.method()` | `client.notify.method()` | `client.publish('topic').method()` |
| Load Balancing | Automatic | N/A | Fan-out |
| Topic Filtering | No | No | Yes |

### When to Use Each Pattern

**Request-Reply:**
- Need response from server
- Synchronous operation semantics
- Query databases, call services
- Expect return values or errors

**Pipeline:**
- Fire-and-forget notifications
- Task distribution to workers
- Logging and monitoring
- Don't need confirmation

**Pub-Sub:**
- Broadcast to multiple recipients
- Event notification systems
- Topic-based message routing
- One-to-many communication

## Hybrid Patterns

### Request-Reply with Notifications

```python
async def hybrid_example():
    class HybridHandler(aiozmq.rpc.AttrHandler):
        @aiozmq.rpc.method
        def process(self, data: str) -> str:
            return f"Processed: {data}"
        
        @aiozmq.rpc.method
        def notify_progress(self, percent: int):
            print(f"Progress: {percent}%")

    # RPC server for main operations
    rpc_server = await aiozmq.rpc.serve_rpc(
        HybridHandler(),
        bind='tcp://*:5564'
    )
    
    # Pipeline for progress notifications
    progress_listener = await aiozmq.rpc.serve_pipeline(
        HybridHandler(),
        bind='tcp://*:5565'
    )
    
    # Client uses both
    rpc_client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5564')
    progress_notifier = await aiozmq.rpc.connect_pipeline(connect='tcp://127.0.0.1:5565')
    
    # Main operation
    result = await rpc_client.call.process("data")
    print(f"Result: {result}")
    
    # Progress updates
    await progress_notifier.notify.notify_progress(50)
    await progress_notifier.notify.notify_progress(100)
    
    # Cleanup
    rpc_client.close()
    progress_notifier.close()
    rpc_server.close()
    progress_listener.close()
```

## Complete Example: Distributed Task System

```python
import asyncio
import aiozmq.rpc
from typing import Dict, Any
from datetime import datetime

class TaskManager(aiozmq.rpc.AttrHandler):
    """Central task management with RPC and notifications."""
    
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self.results: Dict[str, dict] = {}
    
    @aiozmq.rpc.method
    def submit(self, task_id: str, payload: dict) -> bool:
        """Submit a new task (RPC)."""
        self.tasks[task_id] = {
            'payload': payload,
            'status': 'pending',
            'submitted_at': datetime.now().isoformat()
        }
        return True
    
    @aiozmq.rpc.method
    def get_status(self, task_id: str) -> dict:
        """Get task status (RPC)."""
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        task = self.tasks[task_id]
        return {
            'task_id': task_id,
            'status': task['status'],
            'submitted_at': task['submitted_at']
        }
    
    @aiozmq.rpc.method
    def get_result(self, task_id: str) -> dict:
        """Get completed task result (RPC)."""
        if task_id not in self.results:
            raise KeyError(f"Result {task_id} not ready")
        return self.results[task_id]

class TaskNotifier(aiozmq.rpc.AttrHandler):
    """Progress notifications via pipeline."""
    
    @aiozmq.rpc.method
    def task_started(self, task_id: str, worker: str):
        print(f"[{datetime.now().isoformat()}] Task {task_id} started by {worker}")
    
    @aiozmq.rpc.method
    def task_progress(self, task_id: str, percent: int, message: str):
        print(f"[{datetime.now().isoformat()}] Task {task_id}: {percent}% - {message}")
    
    @aiozmq.rpc.method
    def task_completed(self, task_id: str, worker: str, duration: float):
        print(f"[{datetime.now().isoformat()}] Task {task_id} completed by {worker} in {duration}s")

class Worker(aiozmq.rpc.AttrHandler):
    """Task worker that processes jobs."""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
    
    @aiozmq.rpc.method
    def execute(self, task_id: str, payload: dict):
        print(f"Worker {self.worker_id} executing {task_id}")
        # Simulate work
        for i in range(100):
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
        return {'result': f"Completed by worker {self.worker_id}"}

async def task_system():
    # Task manager (RPC)
    manager = await aiozmq.rpc.serve_rpc(
        TaskManager(),
        bind='tcp://*:5570',
        log_exceptions=True
    )
    
    # Progress notifications (Pipeline)
    notifier = await aiozmq.rpc.serve_pipeline(
        TaskNotifier(),
        bind='tcp://*:5571'
    )
    
    print(f"Task manager on {list(manager.transport.bindings())[0]}")
    print(f"Notifier on {list(notifier.transport.bindings())[0]}")
    
    # Submit task via RPC
    client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5570')
    progress = await aiozmq.rpc.connect_pipeline(connect='tcp://127.0.0.1:5571')
    
    # Submit
    await client.call.submit("task-001", {"data": "process this"})
    
    # Notify progress
    await progress.notify.task_started("task-001", "worker-1")
    await progress.notify.task_progress("task-001", 50, "Processing...")
    await progress.notify.task_completed("task-001", "worker-1", 2.5)
    
    # Check status
    status = await client.call.get_status("task-001")
    print(f"Task status: {status}")
    
    await asyncio.sleep(0.5)
    
    # Cleanup
    client.close()
    progress.close()
    manager.close()
    notifier.close()

asyncio.run(task_system())
```

## Troubleshooting Patterns

### Pipeline Not Receiving

Ensure server starts before client:

```python
# Correct order
listener = await aiozmq.rpc.serve_pipeline(handler, bind='tcp://*:5556')
notifier = await aiozmq.rpc.connect_pipeline(connect='tcp://127.0.0.1:5556')
```

### Pub-Sub Topic Mismatch

Topic must match exactly:

```python
# Server subscribes to 'news'
subscriber = await aiozmq.rpc.serve_pubsub(handler, subscribe='news', bind='tcp://*:5559')

# Client publishes to 'news' (must match)
await publisher.publish('news').method()  # Correct
await publisher.publish('News').method()  # Wrong - case sensitive
```

### Pattern Selection Errors

- Need response? Use Request-Reply
- Fire-and-forget? Use Pipeline  
- Broadcast to many? Use Pub-Sub
