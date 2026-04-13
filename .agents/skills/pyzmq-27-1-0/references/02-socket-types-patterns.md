# Socket Types and Patterns

Complete reference for all 19 ZeroMQ socket types with usage patterns, pairing rules, and practical examples.

## Socket Type Overview

| Socket Type | Pairs With | Pattern | Description |
|-------------|------------|---------|-------------|
| `REQ` | `REP` | Request-Reply | Basic client-server messaging |
| `REP` | `REQ` | Request-Reply | Simple request handling |
| `DEALER` | `ROUTER` | Loose Req-Rep | Flexible load balancing |
| `ROUTER` | `DEALER` | Loose Req-Rep | Routing with identity frames |
| `PUB` | `SUB` | Publish-Subscribe | One-to-many broadcasting |
| `SUB` | `PUB` | Publish-Subscribe | Filtered message subscription |
| `PUSH` | `PULL` | Pipeline | Sequential task distribution |
| `PULL` | `PUSH` | Pipeline | Work item consumption |
| `XPUB` | `XSUB` | Ext. Pub-Sub | Advanced pub/sub with sub messages |
| `XSUB` | `XPUB` | Ext. Pub-Sub | Subscription forwarding |
| `PAIR` | `PAIR` | Peer-to-Peer | Simple in-process communication |
| `STREAM` | - | Custom | Raw stream processing |
| `SERVER` | `CLIENT` | Req-Rep (v3) | Modern request-reply |
| `CLIENT` | `SERVER` | Req-Rep (v3) | Modern client socket |
| `RADIO` | `DISH` | Broadcast (v4) | One-to-many UDP multicast |
| `DISH` | `RADIO` | Broadcast (v4) | Multicast reception |
| `GATHER` | `SCATTER` | Tree (v4) | Upward tree aggregation |
| `SCATTER` | `GATHER` | Tree (v4) | Downward tree distribution |
| `CHANNEL` | - | Gossip (v4) | Peer-to-peer gossip protocol |

## Request-Reply Pattern

### Basic REQ/REP

The simplest messaging pattern for client-server communication.

```python
import zmq

context = zmq.Context()

# Server: REP socket
server = context.socket(zmq.REP)
server.bind("tcp://*:5555")

while True:
    # Receive request
    request = server.recv_string()
    print(f"Received: {request}")
    
    # Process and send reply
    response = f"Processed: {request}"
    server.send_string(response)

# Client: REQ socket (separate process)
client = context.socket(zmq.REQ)
client.connect("tcp://localhost:5555")

# Strict request-reply protocol
for i in range(5):
    client.send_string(f"Request {i}")
    response = client.recv_string()  # Blocks until reply
    print(f"Response: {response}")
```

**Key Points:**
- REQ socket must send before receiving
- REP socket must receive before sending
- Strict alternation enforced by protocol
- Automatic reconnection on failure

### DEALER/ROUTER (Flexible Request-Reply)

More flexible than REQ/REP, allows multiple clients and servers.

```python
import zmq
import json
import uuid

context = zmq.Context()

# Server: ROUTER socket
server = context.socket(zmq.ROUTER)
server.bind("tcp://*:5555")

while True:
    # Receive multipart message [identity, request]
    identity, request = server.recv_multipart()
    request_str = request.decode('utf-8')
    
    # Process request
    response = f"Handled by server: {request_str}"
    
    # Send reply with routing identity
    server.send_multipart([identity, response.encode('utf-8')])

# Client: DEALER socket (separate process)
client = context.socket(zmq.DEALER)
client.setsockopt_string(zmq.IDENTITY, str(uuid.uuid4()))
client.connect("tcp://localhost:5555")

for i in range(5):
    client.send_string(f"Task {i}")
    response = client.recv_string()
    print(f"Got: {response}")
```

**Key Points:**
- DEALER distributes messages round-robin to connected ROUTERs
- ROUTER includes identity frame in all received messages
- Must preserve and return identity for replies
- No strict send/recv alternation required

### SERVER/CLIENT (Modern Request-Reply)

ZeroMQ 3.0+ simplified request-reply sockets.

```python
import zmq

context = zmq.Context()

# Server socket
server = context.socket(zmq.SERVER)
server.bind("tcp://*:5555")

while True:
    # Automatically handles identity framing
    client_id, message = server.recv_multipart()
    print(f"Client {client_id}: {message.decode()}")
    
    # Reply (identity handled automatically)
    server.send_multipart([client_id, b"Response"])

# Client socket
client = context.socket(zmq.CLIENT)
client.connect("tcp://localhost:5555")

client.send_string("Hello")
response = client.recv_string()
print(f"Server replied: {response}")
```

**Key Points:**
- CLIENT automatically manages identity
- SERVER automatically handles routing frames
- Cleaner API than DEALER/ROUTER for simple request-reply
- Supports multiple servers with automatic failover

## Publish-Subscribe Pattern

### Basic PUB/SUB

One-to-many message distribution with filtering.

```python
import zmq
import time

context = zmq.Context()

# Publisher
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

# Subscriber 1 (separate process)
subscriber1 = context.socket(zmq.SUB)
subscriber1.connect("tcp://localhost:5556")
subscriber1.setsockopt_string(zmq.SUBSCRIBE, "")  # All messages

# Subscriber 2 with filter (separate process)
subscriber2 = context.socket(zmq.SUB)
subscriber2.connect("tcp://localhost:5556")
subscriber2.setsockopt_string(zmq.SUBSCRIBE, "news.")  # Only news.* topics

# Publisher sends messages
for i in range(10):
    publisher.send_string(f"news.update {i}")
    publisher.send_string(f"ads.banner {i}")
    time.sleep(0.1)

# Subscribers receive filtered messages
# subscriber1 gets all, subscriber2 gets only news.*
```

**Key Points:**
- SUB sockets receive only subscribed topics (empty string = all)
- Messages sent before SUB connects are lost
- Multiple subscriptions supported
- Publisher has no knowledge of subscribers

### Topic-Based Publishing

```python
import zmq
import json

publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

# Send messages with topics
messages = [
    ("stock.nasdaq.aapl", {"price": 178.35, "change": 1.2}),
    ("stock.nasdaq.googl", {"price": 141.80, "change": -0.5}),
    ("news.tech", {"headline": "AI breakthrough announced"}),
]

for topic, data in messages:
    # Multipart: [topic, payload]
    publisher.send_string(topic)
    publisher.send_json(data)

# Subscriber with specific topics
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "stock.nasdaq.")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "news.")

while True:
    topic = subscriber.recv_string()
    payload = subscriber.recv_json()
    print(f"{topic}: {payload}")
```

### XPUB/XSUB (Extended Pub-Sub)

Advanced pub/sub with subscription acknowledgment.

```python
import zmq

context = zmq.Context()

# XPUB socket (publisher side)
xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5557")

# Enable verbose mode to see subscribe/unsubscribe events
xpub.setsockopt(zmq.XPUB_VERBOSE, 1)

# XSUB socket (subscriber side)
xsub = context.socket(zmq.XSUB)
xsub.connect("tcp://localhost:5557")

# Subscribe to topics
xsub.send(b"+stock.")  # Subscribe
xsub.send(b"-news.")   # Unsubscribe

# XPUB receives subscription events
while True:
    event = xpub.recv()
    if event[0] == 1:  # Subscribe
        topic = event[1:]
        print(f"Subscriber interested in: {topic}")
    elif event[0] == 0:  # Unsubscribe
        topic = event[1:]
        print(f"Subscriber not interested in: {topic}")
```

**Key Points:**
- XPUB receives subscription/unsubscription events
- First byte indicates subscribe (1) or unsubscribe (0)
- Useful for monitoring active subscriptions
- Supports manual subscription management with `XPUB_MANUAL` option

## Pipeline Pattern

### PUSH/PULL Pipeline

Sequential task distribution across multiple stages.

```python
import zmq
import time
import random

context = zmq.Context()

# Stage 1: Task generator (PUSH)
generator = context.socket(zmq.PUSH)
generator.connect("tcp://localhost:5558")

# Stage 2: Worker pool (PULL/PUSH)
worker_in = context.socket(zmq.PULL)
worker_in.bind("tcp://*:5558")
worker_out = context.socket(zmq.PUSH)
worker_out.connect("tcp://localhost:5559")

# Stage 3: Collector (PULL)
collector = context.socket(zmq.PULL)
collector.bind("tcp://*:5559")

# Generator sends tasks
for i in range(100):
    generator.send_string(f"Task {i}")
    time.sleep(0.01)

# Worker processes tasks (run in separate thread/process)
while True:
    task = worker_in.recv_string(flags=zmq.DONTWAIT)
    if task:
        # Process task
        result = f"Result of {task}"
        worker_out.send_string(result)

# Collector receives results
for i in range(100):
    result = collector.recv_string()
    print(f"Completed: {result}")
```

**Key Points:**
- PUSH distributes messages round-robin to PULL sockets
- No acknowledgments (fire-and-forget)
- Multiple workers can share same input queue
- Messages may be lost if no PULL socket is connected

### Multicast Pipeline with Monitored Queue

```python
import zmq
from zmq.devices import monitored_queue

context = zmq.Context()

# Create input and output sockets
input_socket = context.socket(zmq.PUSH)
output_socket = context.socket(zmq.PULL)

# Start monitored queue device
monitored_queue(
    zmq.QUEUE,
    input_socket,
    output_socket,
    monitor_address="tcp://*:5560"
)

# Monitor the queue (separate process)
monitor = context.socket(zmq.SUB)
monitor.connect("tcp://localhost:5560")
monitor.setsockopt_string(zmq.SUBSCRIBE, "")

# Receive queue statistics
stats = monitor.recv_json()
print(f"Queue stats: {stats}")
```

## Peer-to-Peer Pattern

### PAIR Socket (In-Process Only)

Simple bidirectional communication for in-process use.

```python
import zmq

context = zmq.Context()

# Create PAIR sockets
socket1 = context.socket(zmq.PAIR)
socket2 = context.socket(zmq.PAIR)

# Connect via inproc transport (one must bind first)
socket1.bind("inproc://mychannel")
socket2.connect("inproc://mychannel")

# Bidirectional communication
socket1.send_string("Hello from 1")
response = socket2.recv_string()
print(f"Socket2 received: {response}")

socket2.send_string("Reply from 2")
reply = socket1.recv_string()
print(f"Socket1 received: {reply}")
```

**Key Points:**
- Only works with `inproc://` transport
- Both sides can send and receive
- Simple alternative to DEALER/ROUTER for in-process comms
- Limited to same process

### CHANNEL Socket (Gossip Protocol)

ZeroMQ 4.3+ peer-to-peer gossip for decentralized applications.

```python
import zmq

context = zmq.Context()

# Create peer nodes
node1 = context.socket(zmq.CHANNEL)
node2 = context.socket(zmq.CHANNEL)
node3 = context.socket(zmq.CHANNEL)

# Configure gossip parameters
node1.setsockopt(zmq.HEARTBEAT_IVL, 1000)  # Heartbeat interval (ms)
node1.setsockopt(zmq.HEARTBEAT_TTL, 3000)  # Time-to-live (ms)

# Bind and connect in mesh topology
node1.bind("tcp://*:5561")
node2.connect("tcp://localhost:5561")
node2.connect("tcp://localhost:5562")  # Will bind after connection
node3.connect("tcp://localhost:5561")

# Send message (propagates to all connected peers)
node1.send_string("Gossip message")

# Receive messages from any peer
while True:
    sender, message = node2.recv_multipart()
    print(f"From {sender}: {message.decode()}")
```

**Key Points:**
- Automatic message propagation to all peers
- Built-in heartbeat for connection monitoring
- Decentralized topology (no central coordinator)
- Suitable for gossip protocols and distributed state

## Broadcast Pattern (ZeroMQ 4.3+)

### RADIO/DISH (UDP Multicast)

Efficient one-to-many broadcasting over UDP.

```python
import zmq

context = zmq.Context()

# Radio socket (broadcaster)
radio = context.socket(zmq.RADIO)
radio.bind("udp://*:5562")
radio.setsockopt_string(zmq.MULTICAST_GROUP, "239.192.1.1")
radio.setsockopt(zmq.MULTICAST_HOPS, 2)

# Dish socket (receiver 1)
dish1 = context.socket(zmq.DISH)
dish1.bind("udp://*@5562")
dish1.setsockopt_string(zmq.MULTICAST_GROUP, "239.192.1.1")

# Dish socket (receiver 2)
dish2 = context.socket(zmq.DISH)
dish2.bind("udp://*@5562")
dish2.setsockopt_string(zmq.MULTICAST_GROUP, "239.192.1.1")

# Broadcast message
radio.send_string("Broadcast to all DISH sockets")

# Receive broadcasts
message = dish1.recv_string()
print(f"Dish1: {message}")

message = dish2.recv_string()
print(f"Dish2: {message}")
```

**Key Points:**
- Uses UDP multicast for efficiency
- No connection required between RADIO and DISH
- Group-based addressing via MULTICAST_GROUP
- Messages may be lost (UDP is unreliable)

## Tree Pattern (ZeroMQ 4.3+)

### SCATTER/GATHER (Hierarchical Distribution)

Tree-based message distribution and aggregation.

```python
import zmq

context = zmq.Context()

# Root node (SCATTER)
root = context.socket(zmq.SCATTER)
root.bind("tcp://*:5563")

# Intermediate nodes (SCATTER/GATHER)
intermediate1 = context.socket(zmq.SCATTER)
intermediate1.connect("tcp://localhost:5563")
intermediate1.bind("tcp://*:5564")

intermediate2 = context.socket(zmq.SCATTER)
intermediate2.connect("tcp://localhost:5563")
intermediate2.bind("tcp://*:5565")

# Leaf nodes (GATHER)
leaf1 = context.socket(zmq.GATHER)
leaf1.connect("tcp://localhost:5564")

leaf2 = context.socket(zmq.GATHER)
leaf2.connect("tcp://localhost:5565")

# Broadcast from root to all leaves
root.send_string("Message to all leaves")

# Aggregate from leaves to root
leaf1.send_string("Result from leaf1")
leaf2.send_string("Result from leaf2")

# Root receives aggregated results
result1 = root.recv_string()
result2 = root.recv_string()
```

**Key Points:**
- SCATTER distributes to all connected GATHER sockets
- GATHER aggregates from multiple children
- Hierarchical topology for efficient distribution
- Useful for distributed computing trees

## STREAM Socket (Custom Protocols)

Raw stream processing for custom protocols.

```python
import zmq

context = zmq.Context()

# Create STREAM socket
stream = context.socket(zmq.STREAM)
stream.bind("tcp://*:5566")

# Connect and send raw bytes
client = context.socket(zmq.STREAM)
client.connect("tcp://localhost:5566")

# Send with peer address included
client.send_multipart([b"\x00\x01\x02\x03", b"Hello"])

# Receive with peer address
peer_addr, message = stream.recv_multipart()
print(f"From {peer_addr.hex()}: {message.decode()}")

# Send reply to specific peer
stream.send_multipart([peer_addr, b"Response"])
```

**Key Points:**
- Includes peer address in each message
- No built-in messaging pattern
- Suitable for implementing custom protocols
- Manual handling of framing and routing
