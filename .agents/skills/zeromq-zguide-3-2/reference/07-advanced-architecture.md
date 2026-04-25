# Advanced Architecture Using ZeroMQ

Comprehensive guide to advanced architectural patterns from Chapter 7 of the ZGuide, including service-oriented architecture, device patterns, and security considerations.

## Service-Oriented Architecture (SOA)

ZeroMQ enables building distributed systems using service-oriented architecture principles.

### SOA Fundamentals

**Key Concepts:**
- **Services**: Independent, loosely-coupled components
- **Contracts**: Well-defined interfaces between services
- **Discovery**: Services find each other dynamically
- **Messaging**: Asynchronous communication via ZeroMQ

### Basic Service Pattern

**Service Implementation:**
```python
import zmq
import json

class Service:
    def __init__(self, name, address):
        self.name = name
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
        
        # Route messages to handlers
        self.handlers = {}
    
    def register_handler(self, command, handler):
        """Register command handler"""
        self.handlers[command] = handler
    
    def run(self):
        """Main service loop"""
        print(f"Service {self.name} starting...")
        
        while True:
            if self.socket.poll(1000, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.socket.recv()
                    frames.append(frame)
                    if not self.socket.getsockopt(zmq.RCVMORE):
                        break
                
                client_id = frames[0]
                message = b''.join(frames[1:])
                
                try:
                    # Parse JSON request
                    request = json.loads(message.decode())
                    command = request['command']
                    params = request.get('params', {})
                    
                    # Route to handler
                    if command in self.handlers:
                        result = self.handlers[command](**params)
                        response = json.dumps({
                            'status': 'ok',
                            'result': result
                        }).encode()
                    else:
                        response = json.dumps({
                            'status': 'error',
                            'error': f'Unknown command: {command}'
                        }).encode()
                    
                    # Send response
                    self.socket.send_multipart([client_id, response])
                    
                except Exception as e:
                    error_response = json.dumps({
                        'status': 'error',
                        'error': str(e)
                    }).encode()
                    self.socket.send_multipart([client_id, error_response])

# Example service
service = Service("Calculator", "tcp://*:5555")

@service.register_handler('add')
def add_handler(a, b):
    return a + b

@service.register_handler('multiply')
def multiply_handler(a, b):
    return a * b

service.run()
```

**Service Client:**
```python
import zmq
import json
import uuid

class ServiceClient:
    def __init__(self, service_address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(service_address)
        
        # Set unique identity
        self.identity = f"Client-{uuid.uuid4().hex[:8]}".encode()
        self.socket.setsockopt(zmq.IDENTITY, self.identity)
    
    def request(self, command, **params):
        """Send request and receive response"""
        request = json.dumps({
            'command': command,
            'params': params
        }).encode()
        
        self.socket.send(request)
        response = self.socket.recv()
        
        result = json.loads(response.decode())
        
        if result['status'] == 'error':
            raise Exception(result['error'])
        
        return result['result']

# Usage
client = ServiceClient("tcp://localhost:5555")
print(client.request('add', a=5, b=3))       # 8
print(client.request('multiply', a=4, b=7))  # 28
```

## Device Patterns

ZeroMQ devices connect different socket types to create complex topologies.

### Built-in Proxy Device

**Simple Proxy:**
```python
import zmq

# Create proxy connecting frontend and backend
frontend = zmq.Context().socket(zmq.ROUTER)
frontend.bind("tcp://*:5559")

backend = zmq.Context().socket(zmq.DEALER)
backend.bind("tcp://*:5560")

# Run proxy (blocks indefinitely)
zmq.proxy(frontend, backend)
```

**Proxy with Monitor:**
```python
import zmq

frontend = zmq.Context().socket(zmq.ROUTER)
frontend.bind("tcp://*:5559")

backend = zmq.Context().socket(zmq.DEALER)
backend.bind("tcp://*:5560")

monitor = zmq.Context().socket(zmq.PAIR)
monitor.connect("inproc://monitor")

# Run proxy with monitor
zmq.proxy(frontend, backend, monitor)

# In another thread/process, receive monitor events
while True:
    event = monitor.recv_multipart()
    print(f"Proxy event: {event}")
```

### Custom Device Implementation

**Load-Balancing Device:**
```python
import zmq
from collections import deque

class LoadBalancingDevice:
    def __init__(self, frontend_addr, backend_addr):
        self.context = zmq.Context()
        
        self.frontend = self.context.socket(zmq.ROUTER)
        self.frontend.bind(frontend_addr)
        
        self.backend = self.context.socket(zmq.DEALER)
        self.backend.bind(backend_addr)
        
        # Track backend workers
        self.workers = deque()
    
    def run(self):
        """Main device loop"""
        print("Load balancer starting...")
        
        while True:
            zmq.poll([self.frontend, self.backend], 1000)
            
            # Handle frontend (client requests)
            if self.frontend.poll(0, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.frontend.recv()
                    frames.append(frame)
                    if not self.frontend.getsockopt(zmq.RCVMORE):
                        break
                
                client_id = frames[0]
                message = b''.join(frames[1:])
                
                # Route to next available worker
                if self.workers:
                    worker_id = self.workers.popleft()
                    self.backend.send_multipart([worker_id, client_id, message])
            
            # Handle backend (worker responses)
            if self.backend.poll(0, zmq.POLLIN):
                frames = []
                while True:
                    frame = self.backend.recv()
                    frames.append(frame)
                    if not self.backend.getsockopt(zmq.RCVMORE):
                        break
                
                worker_id = frames[0]
                
                if len(frames) >= 3:
                    # Worker response
                    client_id = frames[1]
                    response = frames[2]
                    
                    # Send to client
                    self.frontend.send_multipart([client_id, response])
                    
                    # Worker is available again
                    self.workers.append(worker_id)
                else:
                    # Worker registration
                    self.workers.append(worker_id)
                    print(f"Worker {worker_id} registered")

# Usage
device = LoadBalancingDevice("tcp://*:5559", "tcp://*:5560")
device.run()
```

## Security Considerations

### Authentication and Encryption

**CURVE Security Setup:**
```python
import zmq

# Generate server key pair
server_public, server_secret = zmq.curve_keypair()

# Generate client key pair
client_public, client_secret = zmq.curve_keypair()

print(f"Server public:  {zmq.utils.z85_encode(server_public)}")
print(f"Server secret:  {zmq.utils.z85_encode(server_secret)}")
print(f"Client public:  {zmq.utils.z85_encode(client_public)}")
print(f"Client secret:  {zmq.utils.z85_encode(client_secret)}")

# Server setup with CURVE
context = zmq.Context()
server = context.socket(zmq.ROUTER)
server.setsockopt(zmq.CURVE_SERVER, 1)
server.setsockopt(zmq.CERTIFICATE_PUBLIC, server_public)
server.setsockopt(zmq.CERTIFICATE_KEYPAIR, server_secret)
server.bind("tcp://*:5555")

# Client setup with CURVE
client = context.socket(zmq.DEALER)
client.setsockopt(zmq.IDENTITY, b"Client1")
client.setsockopt(zmq.CURVE_PUBLIC, client_public)
client.setsockopt(zmq.CERTIFICATE_KEYPAIR, client_secret)
client.setsockopt(zmq.CURVE_SERVERKEY, server_public)
client.connect("tcp://localhost:5555")
```

**GSSAPI Security (Kerberos):**
```python
import zmq

# Server with GSSAPI
server = context.socket(zmq.ROUTER)
server.setsockopt(zmq.GSSAPI_SERVER, 1)
server.setsockopt_string(zmq.GSSAPI_PRINCIPAL, "zeromq/server@EXAMPLE.COM")
server.bind("tcp://*:5555")

# Client with GSSAPI
client = context.socket(zmq.DEALER)
client.setsockopt(zmq.GSSAPI_PLAINTEXT, 0)  # Use encryption
client.connect("tcp://localhost:5555")
```

### Access Control

**Allow/Deny Lists:**
```python
import zmq

server = context.socket(zmq.ROUTER)

# Allow specific clients
server.setsockopt(zmq.CURVE_ALLOW, client_public_key_1)
server.setsockopt(zmq.CURVE_ALLOW, client_public_key_2)

# Or deny specific clients
server.setsockopt(zmq.CURVE_DENY, malicious_client_public_key)

server.bind("tcp://*:5555")
```

### Network Security

**Firewall Configuration:**
```bash
# Allow ZeroMQ traffic on specific ports
sudo iptables -A INPUT -p tcp --dport 5555 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5556 -j ACCEPT

# Using ufw
sudo ufw allow 5555/tcp
sudo ufw allow 5556/tcp
```

**Bind to Specific Interfaces:**
```python
# Only accept connections on localhost
socket.bind("tcp://127.0.0.1:5555")

# Only accept connections on specific interface
socket.bind("tcp://192.168.1.100:5555")

# Avoid binding to all interfaces in production
# socket.bind("tcp://*:5555")  # Dangerous in production!
```

## Multi-Threaded Architecture

### Thread-Safe Patterns

**One Socket Per Thread:**
```python
import zmq
import threading

class ThreadSafeService:
    def __init__(self):
        self.context = zmq.Context()
        self.threads = []
    
    def worker_thread(self, thread_id):
        """Each thread has its own socket"""
        socket = self.context.socket(zmq.DEALER)
        socket.connect("tcp://localhost:5555")
        socket.setsockopt(zmq.IDENTITY, f"Thread-{thread_id}".encode())
        
        print(f"Thread {thread_id} started")
        
        while True:
            if socket.poll(1000, zmq.POLLIN):
                task = socket.recv()
                print(f"Thread {thread_id} processing: {task}")
                
                # Process task
                result = f"Result from thread {thread_id}"
                socket.send(result.encode())
    
    def start(self, num_threads=4):
        """Start worker threads"""
        for i in range(num_threads):
            t = threading.Thread(target=self.worker_thread, args=(i,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)

# Usage
service = ThreadSafeService()
service.start()
```

**Inproc Socket for Thread Communication:**
```python
import zmq
import threading

class InprocCommunicator:
    def __init__(self):
        self.context = zmq.Context()
    
    def producer_thread(self, socket_name):
        """Producer thread"""
        socket = self.context.socket(zmq.PUSH)
        socket.bind(f"inproc://{socket_name}")
        
        for i in range(100):
            socket.send(f"Message {i}".encode())
        
        print("Producer done")
    
    def consumer_thread(self, socket_name):
        """Consumer thread"""
        socket = self.context.socket(zmq.PULL)
        socket.connect(f"inproc://{socket_name}")
        
        count = 0
        while count < 100:
            message = socket.recv()
            print(f"Consumer got: {message}")
            count += 1
    
    def run(self):
        """Run producer and consumer in separate threads"""
        socket_name = "mysocket"
        
        producer = threading.Thread(target=self.producer_thread, args=(socket_name,))
        consumer = threading.Thread(target=self.consumer_thread, args=(socket_name,))
        
        consumer.start()
        producer.start()
        
        producer.join()
        consumer.join()

# Usage
comm = InprocCommunicator()
comm.run()
```

## Scalability Patterns

### Horizontal Scaling

**Adding More Workers:**
```python
import zmq
import sys

def worker(worker_id):
    """Worker that can be scaled horizontally"""
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect("tcp://loadbalancer:5555")
    socket.setsockopt(zmq.IDENTITY, f"Worker-{worker_id}".encode())
    
    print(f"Worker {worker_id} ready")
    
    tasks_processed = 0
    while True:
        task = socket.recv()
        print(f"Worker {worker_id} processing: {task}")
        
        # Process task
        result = f"Result from worker {worker_id}"
        socket.send(result.encode())
        
        tasks_processed += 1
        
        if tasks_processed >= 100:
            print(f"Worker {worker_id} done")
            break

if __name__ == "__main__":
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    worker(worker_id)
```

**Deployment:**
```bash
# Start multiple workers on different machines
ssh worker1 "python worker.py 1"
ssh worker2 "python worker.py 2"
ssh worker3 "python worker.py 3"
# ... and so on
```

### Vertical Scaling

**Increasing I/O Threads:**
```python
import zmq

# Create context with more I/O threads for higher throughput
context = zmq.Context(16)  # 16 I/O threads

socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5555")

# Handle many concurrent connections efficiently
```

**Tuning Socket Options:**
```python
socket.setsockopt(zmq.IO_THREADS, 16)
socket.setsockopt(zmq.MAX_MSGSZ, 256 * 1024 * 1024)  # 256 MB max message
socket.setsockopt(zmq.SNDHWM, 10000)  # Send high water mark
socket.setsockopt(zmq.RCVHWM, 10000)  # Receive high water mark
```

## Monitoring and Observability

### Health Checking

**Heartbeat-Based Health Check:**
```python
import zmq
import time

class HealthMonitor:
    def __init__(self):
        self.context = zmq.Context()
        
        # Socket for receiving heartbeats
        self.heartbeat_socket = self.context.socket(zmq.PULL)
        self.heartbeat_socket.bind("tcp://*:5565")
        
        # Track last heartbeat from each service
        self.last_heartbeat = {}
    
    def check_health(self, timeout=30):
        """Check if all services are healthy"""
        current_time = time.time()
        unhealthy = []
        
        for service_id, last_seen in self.last_heartbeat.items():
            if current_time - last_seen > timeout:
                unhealthy.append(service_id)
        
        return {
            'healthy': len(self.last_heartbeat) - len(unhealthy),
            'unhealthy': len(unhealthy),
            'unhealthy_services': unhealthy
        }
    
    def run(self):
        """Main monitoring loop"""
        while True:
            if self.heartbeat_socket.poll(1000, zmq.POLLIN):
                heartbeat = self.heartbeat_socket.recv_multipart()
                service_id = heartbeat[0].decode()
                
                self.last_heartbeat[service_id] = time.time()
            
            # Log health status periodically
            health = self.check_health()
            print(f"Health status: {health}")
            
            time.sleep(5)

# Usage
monitor = HealthMonitor()
monitor.run()
```

**Service Heartbeat Sender:**
```python
import zmq
import time

class HeartbeatSender:
    def __init__(self, service_id, monitor_address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(monitor_address)
        
        self.service_id = service_id.encode()
    
    def send_heartbeat(self, interval=10):
        """Send periodic heartbeats"""
        while True:
            self.socket.send(self.service_id)
            time.sleep(interval)

# Usage in each service
sender = HeartbeatSender("service-1", "tcp://monitor:5565")
sender.send_heartbeat()
```

### Metrics Collection

**Performance Metrics:**
```python
import zmq
import time
from collections import defaultdict

class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'errors': 0
        })
    
    def record(self, operation, duration, error=False):
        """Record operation metrics"""
        if error:
            self.metrics[operation]['errors'] += 1
        else:
            self.metrics[operation]['count'] += 1
            self.metrics[operation]['total_time'] += duration
            self.metrics[operation]['min_time'] = min(
                self.metrics[operation]['min_time'], duration
            )
            self.metrics[operation]['max_time'] = max(
                self.metrics[operation]['max_time'], duration
            )
    
    def get_stats(self, operation):
        """Get statistics for an operation"""
        m = self.metrics[operation]
        count = m['count']
        
        if count == 0:
            return {
                'count': 0,
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'errors': m['errors'],
                'error_rate': 0
            }
        
        return {
            'count': count,
            'avg_time': m['total_time'] / count,
            'min_time': m['min_time'],
            'max_time': m['max_time'],
            'errors': m['errors'],
            'error_rate': m['errors'] / (count + m['errors'])
        }

# Usage in service
metrics = MetricsCollector()

def process_request(request):
    start = time.time()
    try:
        result = handle_request(request)
        metrics.record('request', time.time() - start)
        return result
    except Exception as e:
        metrics.record('request', time.time() - start, error=True)
        raise

# Periodically report stats
stats = metrics.get_stats('request')
print(f"Request stats: {stats}")
```

## Best Practices

1. **Use appropriate patterns** - Match pattern to use case
2. **Implement security early** - Don't add it later
3. **Design for failure** - Assume components will fail
4. **Monitor everything** - Visibility enables debugging
5. **Scale horizontally** - Add more machines, not bigger ones
6. **Keep services small** - Single responsibility principle
7. **Use versioning** - API versioning for compatibility

## Troubleshooting

### Common Architecture Issues

**Service Discovery Problems:**
- Use consistent naming conventions
- Implement service registration
- Consider using a discovery protocol (Consul, etcd)

**Load Balancing Issues:**
- Track worker health actively
- Implement proper backpressure
- Monitor queue depths

**Security Issues:**
- Always use authentication in production
- Bind to specific interfaces, not wildcards
- Keep keys secure and rotate periodically

## Next Steps

- [Distributed Frameworks](08-distributed-framework.md) - Complete system design
- [Reliable Request-Reply](05-reliable-request-reply.md) - Fault tolerance
- Official RFCs: https://rfc.zeromq.org/
