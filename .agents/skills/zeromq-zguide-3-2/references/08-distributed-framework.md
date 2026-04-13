# Building Distributed Computing Frameworks

Comprehensive guide to building distributed computing frameworks from Chapter 8 of the ZGuide, including task queues, worker pools, and complete system architectures.

## Framework Overview

A distributed computing framework provides:
- **Task distribution** - Workload spreading across workers
- **Result collection** - Gathering outputs from workers
- **Fault tolerance** - Handling worker failures gracefully
- **Scalability** - Adding/removing workers dynamically
- **Monitoring** - Tracking system health and performance

## Task Queue Architecture

### Basic Task Queue

**Task Ventilator (Producer):**
```python
import zmq
import time

class TaskVentilator:
    def __init__(self, address="tcp://*:5557"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(address)
    
    def send_task(self, task_data):
        """Send a task to workers"""
        self.socket.send(task_data.encode())
    
    def send_batch(self, tasks):
        """Send batch of tasks"""
        for task in tasks:
            self.send_task(task)
            time.sleep(0.01)  # Small delay between tasks

# Usage
ventilator = TaskVentilator()
for i in range(100):
    ventilator.send_task(f"Task-{i}")
```

**Task Worker (Consumer):**
```python
import zmq
import time
import sys

class TaskWorker:
    def __init__(self, worker_id, address="tcp://localhost:5557"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(address)
        
        self.worker_id = worker_id
        self.tasks_processed = 0
    
    def process_task(self, task):
        """Process a single task (override for custom logic)"""
        # Simulate work
        time.sleep(0.1)
        return f"Result for {task}"
    
    def run(self, max_tasks=None):
        """Main worker loop"""
        print(f"Worker {self.worker_id} starting...")
        
        while True:
            task = self.socket.recv().decode()
            
            # Process task
            result = self.process_task(task)
            
            self.tasks_processed += 1
            
            print(f"Worker {self.worker_id}: Processed {task}")
            
            if max_tasks and self.tasks_processed >= max_tasks:
                print(f"Worker {self.worker_id} done ({self.tasks_processed} tasks)")
                break

# Usage
worker = TaskWorker(sys.argv[1] if len(sys.argv) > 1 else "1")
worker.run(max_tasks=25)
```

### Enhanced Task Queue with Results

**Task Queue with Result Collection:**
```python
import zmq
import json
import uuid

class TaskQueueWithResults:
    def __init__(self):
        self.context = zmq.Context()
        
        # Frontend: receive tasks from clients
        self.frontend = self.context.socket(zmq.ROUTER)
        self.frontend.bind("tcp://*:5559")
        
        # Backend: distribute to workers
        self.backend = self.context.socket(zmq.DEALER)
        self.backend.bind("tcp://*:5560")
        
        # Track pending tasks
        self.pending_tasks = {}  # task_id -> (client_id, task_data)
    
    def run(self):
        """Main queue loop"""
        print("Task queue starting...")
        
        while True:
            zmq.poll([self.frontend, self.backend], 1000)
            
            # Handle client requests
            if self.frontend.poll(0, zmq.POLLIN):
                self.handle_client()
            
            # Handle worker results
            if self.backend.poll(0, zmq.POLLIN):
                self.handle_worker()
    
    def handle_client(self):
        """Handle incoming task from client"""
        frames = []
        while True:
            frame = self.frontend.recv()
            frames.append(frame)
            if not self.frontend.getsockopt(zmq.RCVMORE):
                break
        
        client_id = frames[0]
        task_data = b''.join(frames[1:])
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Store pending task
        self.pending_tasks[task_id] = (client_id, task_data)
        
        # Send to worker with task ID
        self.backend.send_multipart([task_id.encode(), task_data])
        
        print(f"Task {task_id} queued for client {client_id}")
    
    def handle_worker(self):
        """Handle result from worker"""
        frames = []
        while True:
            frame = self.backend.recv()
            frames.append(frame)
            if not self.backend.getsockopt(zmq.RCVMORE):
                break
        
        task_id = frames[0].decode()
        result = b''.join(frames[1:])
        
        # Find client for this task
        if task_id in self.pending_tasks:
            client_id, _ = self.pending_tasks.pop(task_id)
            
            # Send result to client
            self.frontend.send_multipart([client_id, result])
            
            print(f"Task {task_id} completed, result sent to {client_id}")
        else:
            print(f"Warning: Unknown task ID {task_id}")

# Usage
queue = TaskQueueWithResults()
queue.run()
```

## Worker Pool Management

### Dynamic Worker Pool

**Worker Pool Manager:**
```python
import zmq
import threading
import time
from collections import defaultdict

class WorkerPoolManager:
    def __init__(self, num_workers=4):
        self.context = zmq.Context()
        
        # Socket for receiving tasks from clients
        self.client_socket = self.context.socket(zmq.ROUTER)
        self.client_socket.bind("tcp://*:5559")
        
        # Socket for communicating with workers
        self.worker_socket = self.context.socket(zmq.DEALER)
        self.worker_socket.bind("tcp://*:5560")
        
        # Track workers
        self.workers = {}  # worker_id -> info
        self.ready_workers = []  # List of ready worker IDs
        
        # Start worker threads
        self.threads = []
        for i in range(num_workers):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker_thread(self, worker_id):
        """Simulated worker thread"""
        # In real implementation, workers would be separate processes
        worker_name = f"Worker-{worker_id}"
        
        # Register with manager
        self.workers[worker_name] = {
            'id': worker_id,
            'status': 'ready',
            'tasks_completed': 0
        }
        self.ready_workers.append(worker_name)
        
        print(f"{worker_name} registered")
    
    def select_worker(self):
        """Select next available worker (round-robin)"""
        if not self.ready_workers:
            return None
        
        worker = self.ready_workers.pop(0)
        return worker
    
    def mark_worker_ready(self, worker_id):
        """Mark worker as ready for new tasks"""
        if worker_id not in self.ready_workers:
            self.ready_workers.append(worker_id)
    
    def run(self):
        """Main pool manager loop"""
        print("Worker pool manager starting...")
        
        while True:
            zmq.poll([self.client_socket, self.worker_socket], 1000)
            
            # Handle client requests
            if self.client_socket.poll(0, zmq.POLLIN):
                self.handle_client_request()
            
            # Handle worker messages
            if self.worker_socket.poll(0, zmq.POLLIN):
                self.handle_worker_message()
    
    def handle_client_request(self):
        """Handle task submission from client"""
        frames = []
        while True:
            frame = self.client_socket.recv()
            frames.append(frame)
            if not self.client_socket.getsockopt(zmq.RCVMORE):
                break
        
        client_id = frames[0]
        task_data = b''.join(frames[1:])
        
        # Select worker
        worker_id = self.select_worker()
        
        if worker_id:
            # Send task to worker with client ID for routing response
            self.worker_socket.send_multipart([worker_id, client_id, task_data])
            
            # Mark worker as busy (removed from ready list)
        else:
            # No workers available, queue the request
            print("No workers available, queuing request")
    
    def handle_worker_message(self):
        """Handle messages from workers"""
        frames = []
        while True:
            frame = self.worker_socket.recv()
            frames.append(frame)
            if not self.worker_socket.getsockopt(zmq.RCVMORE):
                break
        
        worker_id = frames[0].decode()
        
        if len(frames) >= 3:
            # Task result
            client_id = frames[1]
            result = frames[2]
            
            # Send result to client
            self.client_socket.send_multipart([client_id, result])
            
            # Mark worker as ready
            self.mark_worker_ready(worker_id)
            
            # Update stats
            if worker_id in self.workers:
                self.workers[worker_id]['tasks_completed'] += 1
        else:
            # Heartbeat or registration
            print(f"Worker {worker_id} heartbeat")

# Usage
pool = WorkerPoolManager(num_workers=4)
pool.run()
```

## Complete Framework Example

### Majordomo-Style Framework

**Protocol Definition:**
```python
import json
import uuid
from enum import Enum

class ServiceCommand(Enum):
    INIT = "INIT"
    TASK = "TASK"
    RESULT = "RESULT"
    ERROR = "ERROR"
    HEARTBEAT = "HEARTBEAT"

def create_message(command, body=None, service=None):
    """Create protocol message"""
    return {
        'id': str(uuid.uuid4()),
        'command': command.value,
        'service': service,
        'body': body or {}
    }

def serialize_message(msg):
    """Serialize message to JSON"""
    return json.dumps(msg).encode()

def deserialize_message(data):
    """Deserialize message from JSON"""
    return json.loads(data.decode())
```

**Service Framework:**
```python
import zmq
import threading
import time

class ServiceFramework:
    def __init__(self, service_name, address="tcp://localhost:5560"):
        self.service_name = service_name
        self.context = zmq.Context()
        
        # Socket for receiving requests from broker
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)
        
        # Set identity to service name
        self.socket.setsockopt(zmq.IDENTITY, service_name.encode())
        
        # Command handlers
        self.handlers = {}
    
    def register_handler(self, command, handler):
        """Register command handler"""
        self.handlers[command] = handler
    
    def handle_init(self, msg):
        """Handle initialization request"""
        return {'status': 'ready'}
    
    def handle_heartbeat(self, msg):
        """Handle heartbeat request"""
        return {'status': 'alive', 'service': self.service_name}
    
    def process_message(self, msg):
        """Process incoming message"""
        command = msg.get('command')
        
        # Built-in handlers
        if command == ServiceCommand.INIT.value:
            result = self.handle_init(msg)
        elif command == ServiceCommand.HEARTBEAT.value:
            result = self.handle_heartbeat(msg)
        else:
            # Custom handlers
            if command in self.handlers:
                result = self.handlers[command](msg)
            else:
                result = {'error': f'Unknown command: {command}'}
        
        return result
    
    def run(self):
        """Main service loop"""
        print(f"Service {self.service_name} starting...")
        
        # Send INIT to broker
        init_msg = create_message(ServiceCommand.INIT, service=self.service_name)
        self.socket.send(serialize_message(init_msg))
        
        while True:
            if self.socket.poll(1000, zmq.POLLIN):
                try:
                    # Receive message
                    data = self.socket.recv()
                    msg = deserialize_message(data)
                    
                    # Process message
                    result = self.process_message(msg)
                    
                    # Send result back
                    response = create_message(
                        ServiceCommand.RESULT,
                        body=result,
                        service=self.service_name
                    )
                    self.socket.send(serialize_message(response))
                    
                except Exception as e:
                    error_response = create_message(
                        ServiceCommand.ERROR,
                        body={'error': str(e)},
                        service=self.service_name
                    )
                    self.socket.send(serialize_message(error_response))

# Example service implementation
class CalculatorService(ServiceFramework):
    def __init__(self):
        super().__init__("Calculator")
        
        # Register custom handlers
        self.register_handler('add', self.handle_add)
        self.register_handler('multiply', self.handle_multiply)
    
    def handle_add(self, msg):
        """Handle add command"""
        a = msg['body'].get('a', 0)
        b = msg['body'].get('b', 0)
        return {'result': a + b}
    
    def handle_multiply(self, msg):
        """Handle multiply command"""
        a = msg['body'].get('a', 0)
        b = msg['body'].get('b', 0)
        return {'result': a * b}

# Usage
service = CalculatorService()
service.run()
```

**Broker Implementation:**
```python
import zmq
import threading
from collections import defaultdict

class ServiceBroker:
    def __init__(self):
        self.context = zmq.Context()
        
        # Frontend: client connections
        self.frontend = self.context.socket(zmq.ROUTER)
        self.frontend.bind("tcp://*:5559")
        
        # Backend: service connections
        self.backend = self.context.socket(zmq.DEALER)
        self.backend.bind("tcp://*:5560")
        
        # Track registered services
        self.services = {}  # service_name -> capabilities
        
        # Route requests to services
        self.routes = defaultdict(list)  # command -> [service_names]
    
    def register_service(self, service_name, commands):
        """Register a service with its available commands"""
        self.services[service_name] = commands
        
        # Add to routes
        for command in commands:
            self.routes[command].append(service_name)
        
        print(f"Service {service_name} registered with commands: {commands}")
    
    def select_service(self, command):
        """Select a service for a command (round-robin)"""
        if command not in self.routes or not self.routes[command]:
            return None
        
        services = self.routes[command]
        
        # Round-robin selection
        service = services.pop(0)
        services.append(service)
        
        return service
    
    def run(self):
        """Main broker loop"""
        print("Broker starting...")
        
        while True:
            zmq.poll([self.frontend, self.backend], 1000)
            
            # Handle client requests
            if self.frontend.poll(0, zmq.POLLIN):
                self.handle_client()
            
            # Handle service responses
            if self.backend.poll(0, zmq.POLLIN):
                self.handle_service()
    
    def handle_client(self):
        """Handle request from client"""
        frames = []
        while True:
            frame = self.frontend.recv()
            frames.append(frame)
            if not self.frontend.getsockopt(zmq.RCVMORE):
                break
        
        client_id = frames[0]
        data = b''.join(frames[1:])
        
        try:
            msg = deserialize_message(data)
            command = msg.get('command')
            
            # Select appropriate service
            service_name = self.select_service(command)
            
            if service_name:
                # Forward to service
                msg['client_id'] = client_id.decode()
                self.backend.send(serialize_message(msg))
            else:
                # No service available
                error_response = create_message(
                    ServiceCommand.ERROR,
                    body={'error': f'No service for command: {command}'},
                    service=None
                )
                self.frontend.send_multipart([client_id, serialize_message(error_response)])
        
        except Exception as e:
            error_response = create_message(
                ServiceCommand.ERROR,
                body={'error': str(e)},
                service=None
            )
            self.frontend.send_multipart([client_id, serialize_message(error_response)])
    
    def handle_service(self):
        """Handle response from service"""
        data = self.backend.recv()
        msg = deserialize_message(data)
        
        # Route back to client
        if 'client_id' in msg:
            client_id = msg.pop('client_id').encode()
            self.frontend.send_multipart([client_id, serialize_message(msg)])

# Usage
broker = ServiceBroker()
broker.run()
```

**Client Implementation:**
```python
import zmq

class ServiceClient:
    def __init__(self, broker_address="tcp://localhost:5559"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(broker_address)
        
        import uuid
        self.identity = f"Client-{uuid.uuid4().hex[:8]}".encode()
        self.socket.setsockopt(zmq.IDENTITY, self.identity)
    
    def request(self, command, body=None):
        """Send request and receive response"""
        msg = create_message(command, body=body or {})
        
        self.socket.send(serialize_message(msg))
        response = self.socket.recv()
        
        result = deserialize_message(response)
        
        if result.get('command') == ServiceCommand.ERROR.value:
            raise Exception(result['body'].get('error'))
        
        return result.get('body', {})

# Usage
client = ServiceClient()

# Call calculator service
result = client.request('add', {'a': 5, 'b': 3})
print(f"5 + 3 = {result['result']}")

result = client.request('multiply', {'a': 4, 'b': 7})
print(f"4 * 7 = {result['result']}")
```

## Performance Optimization

### Message Batching

**Batch Processing:**
```python
import zmq
import time

class BatchProcessor:
    def __init__(self, batch_size=100):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect("tcp://localhost:5557")
        
        self.batch_size = batch_size
    
    def process_batch(self, tasks):
        """Process a batch of tasks"""
        results = []
        for task in tasks:
            result = self.process_single(task)
            results.append(result)
        return results
    
    def process_single(self, task):
        """Process single task (override for custom logic)"""
        time.sleep(0.01)  # Simulate work
        return f"Result for {task}"
    
    def run(self):
        """Main processing loop with batching"""
        batch = []
        
        while True:
            if self.socket.poll(100, zmq.POLLIN):
                task = self.socket.recv().decode()
                batch.append(task)
                
                # Process when batch is full
                if len(batch) >= self.batch_size:
                    results = self.process_batch(batch)
                    print(f"Processed batch of {len(results)} tasks")
                    batch = []
            else:
                # Process remaining tasks on timeout
                if batch:
                    results = self.process_batch(batch)
                    print(f"Processed remaining {len(results)} tasks")
                    batch = []

# Usage
processor = BatchProcessor(batch_size=50)
processor.run()
```

### Connection Pooling

**Connection Pool:**
```python
import zmq
from queue import Queue

class ConnectionPool:
    def __init__(self, pool_size=10, address="tcp://localhost:5559"):
        self.address = address
        self.pool = Queue(maxsize=pool_size)
        
        # Pre-create connections
        for _ in range(pool_size):
            context = zmq.Context()
            socket = context.socket(zmq.DEALER)
            socket.connect(address)
            self.pool.put((context, socket))
    
    def acquire(self):
        """Acquire connection from pool"""
        return self.pool.get()
    
    def release(self, context, socket):
        """Release connection back to pool"""
        self.pool.put((context, socket))
    
    def close(self):
        """Close all connections"""
        while not self.pool.empty():
            context, socket = self.pool.get()
            socket.close()
            context.term()

# Usage
pool = ConnectionPool(pool_size=10)

# Use connection
context, socket = pool.acquire()
try:
    socket.send(b"Request")
    response = socket.recv()
    print(f"Response: {response}")
finally:
    pool.release(context, socket)

# Cleanup
pool.close()
```

## Monitoring and Metrics

### Comprehensive Monitoring

**Metrics Dashboard:**
```python
import zmq
import time
from collections import defaultdict
from datetime import datetime

class MetricsDashboard:
    def __init__(self):
        self.context = zmq.Context()
        
        # Socket for receiving metrics
        self.metrics_socket = self.context.socket(zmq.PULL)
        self.metrics_socket.bind("tcp://*:5570")
        
        # Aggregate metrics
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'errors': 0,
            'samples': []
        })
    
    def record_metric(self, metric_name, value, error=False):
        """Record a metric (called from services)"""
        if error:
            self.metrics[metric_name]['errors'] += 1
        else:
            self.metrics[metric_name]['count'] += 1
            self.metrics[metric_name]['total_time'] += value
            self.metrics[metric_name]['samples'].append(value)
            
            # Keep only last 1000 samples
            if len(self.metrics[metric_name]['samples']) > 1000:
                self.metrics[metric_name]['samples'] = \
                    self.metrics[metric_name]['samples'][-1000:]
    
    def get_statistics(self, metric_name):
        """Get statistics for a metric"""
        m = self.metrics[metric_name]
        samples = m['samples']
        
        if not samples:
            return {
                'count': 0,
                'avg': 0,
                'min': 0,
                'max': 0,
                'p95': 0,
                'p99': 0,
                'errors': m['errors']
            }
        
        sorted_samples = sorted(samples)
        
        return {
            'count': m['count'],
            'avg': m['total_time'] / m['count'],
            'min': min(samples),
            'max': max(samples),
            'p95': sorted_samples[int(len(sorted_samples) * 0.95)],
            'p99': sorted_samples[int(len(sorted_samples) * 0.99)],
            'errors': m['errors']
        }
    
    def print_dashboard(self):
        """Print metrics dashboard"""
        print("\n" + "="*60)
        print("METRICS DASHBOARD -", datetime.now().strftime("%H:%M:%S"))
        print("="*60)
        
        for metric_name, stats in self.get_all_stats().items():
            print(f"\n{metric_name}:")
            print(f"  Count: {stats['count']}")
            print(f"  Avg: {stats['avg']:.3f}s")
            print(f"  Min/Max: {stats['min']:.3f}s / {stats['max']:.3f}s")
            print(f"  P95/P99: {stats['p95']:.3f}s / {stats['p99']:.3f}s")
            print(f"  Errors: {stats['errors']}")
        
        print("="*60 + "\n")
    
    def get_all_stats(self):
        """Get statistics for all metrics"""
        return {name: self.get_statistics(name) for name in self.metrics}
    
    def run(self, interval=10):
        """Run dashboard update loop"""
        while True:
            time.sleep(interval)
            self.print_dashboard()

# Usage in services
dashboard = MetricsDashboard()

# In service code:
start = time.time()
try:
    result = process_request(request)
    dashboard.record_metric('request_time', time.time() - start)
except Exception as e:
    dashboard.record_metric('request_time', time.time() - start, error=True)
```

## Best Practices

1. **Use appropriate patterns** - Match architecture to requirements
2. **Implement proper error handling** - Fail gracefully
3. **Monitor everything** - Visibility enables optimization
4. **Design for scale** - Consider horizontal scaling from start
5. **Keep services independent** - Loose coupling enables flexibility
6. **Version your protocols** - Enable evolution without breaking changes
7. **Test failure scenarios** - Verify recovery works correctly

## Troubleshooting

### Common Issues

**Worker Not Receiving Tasks:**
- Check connection addresses match
- Verify worker registered with broker
- Monitor network connectivity

**Tasks Stuck in Queue:**
- Check worker health and availability
- Monitor queue depth
- Verify task serialization/deserialization

**Performance Degradation:**
- Profile individual components
- Check for blocking operations
- Monitor resource usage (CPU, memory, network)

## Next Steps

- [Advanced Architecture](07-advanced-architecture.md) - Large-scale patterns
- [Reliable Request-Reply](05-reliable-request-reply.md) - Fault tolerance
- Official documentation: https://zguide.zeromq.org/
