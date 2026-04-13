# Advanced Pub-Sub Patterns

Comprehensive guide to advanced publish-subscribe patterns from Chapter 5 of the ZGuide, including last-value caching, subscriber management, and tracing techniques.

## Pros and Cons of Pub-Sub

### Advantages

**Scalability:**
- Supports thousands of subscribers
- No server-side state tracking
- Fire-and-forget semantics

**Simplicity:**
- Simple API (publish and subscribe)
- Automatic message distribution
- Built-in topic filtering

**Flexibility:**
- Multiple publishers to multiple subscribers
- Dynamic subscription changes
- Works across network boundaries

### Disadvantages

**No Delivery Guarantees:**
- Messages sent before subscription are lost
- No acknowledgments or retries
- Slow subscribers fall behind indefinitely

**No Subscriber Awareness:**
- Publisher doesn't know subscriber count
- Can't detect slow or disconnected subscribers
- Difficult to implement flow control

## Pub-Sub Tracing (Espresso Pattern)

The Espresso pattern demonstrates how to capture and trace pub-sub traffic using XPUB/XSUB sockets.

### Implementation Overview

**Architecture:**
```
Publisher --> XPUB <--> Proxy <--> XSUB --> Subscriber
                      |
                      v
                  Listener (captures all traffic)
```

### Python Implementation

```python
import zmq
import threading
import time

def publisher():
    """Publisher sends random messages"""
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.connect("tcp://localhost:5563")
    
    import random
    for i in range(100):
        topic = random.choice(list("ABCDEFGHIJ"))
        message = f"{topic} {i}"
        pub.send_string(message)
        time.sleep(0.1)

def subscriber():
    """Subscriber receives and counts messages"""
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://localhost:5563")
    
    # Subscribe to topics A and B
    sub.setsockopt_string(zmq.SUBSCRIBE, "A")
    sub.setsockopt_string(zmq.SUBSCRIBE, "B")
    
    count = 0
    while count < 100:
        message = sub.recv_string()
        print(f"Subscriber got: {message}")
        count += 1

def listener():
    """Listener captures all pub-sub traffic"""
    context = zmq.Context()
    listener = context.socket(zmq.PAIR)
    listener.bind("inproc://monitor")
    
    while True:
        message = listener.recv_string()
        print(f"Listener captured: {message}")

def proxy():
    """Proxy connects pub-sub to listener"""
    context = zmq.Context()
    
    # Frontend connects to publishers/subscribers
    frontend = context.socket(zmq.XREP)
    frontend.bind("tcp://*:5563")
    
    # Backend connects to listener
    backend = context.socket(zmq.XREQ)
    backend.connect("inproc://monitor")
    
    # Run proxy
    zmq.proxy(frontend, backend)

# Start threads
pub_thread = threading.Thread(target=publisher)
sub_thread = threading.Thread(target=subscriber)
list_thread = threading.Thread(target=listener, daemon=True)

list_thread.start()
proxy_thread = threading.Thread(target=proxy, daemon=True)
proxy_thread.start()

pub_thread.start()
sub_thread.start()

pub_thread.join()
sub_thread.join()
```

### Key Concepts

**XPUB Socket:**
- Manages subscriptions automatically
- Sends subscription messages to XSUB
- Can be used for last-value caching

**XSUB Socket:**
- Receives subscription commands
- Forwards subscription changes to XPUB
- Enables subscriber tracking

## Last Value Caching (LVC)

Last Value Caching ensures new subscribers receive the most recent value for each topic, solving the "messages before subscription" problem.

### Problem Statement

Without LVC:
1. Publisher sends updates for topics A-J
2. Subscriber connects and subscribes to topic A
3. Subscriber misses all previous A updates
4. Subscriber only gets future A updates

With LVC:
1. Cache stores last value for each topic
2. New subscriber connects
3. Cache immediately sends last known values
4. Subscriber is up-to-date instantly

### Implementation

**Last Value Cache Server:**

```python
import zmq
import threading

class LastValueCache:
    def __init__(self):
        self.context = zmq.Context()
        
        # Frontend for publishers
        self.xpub = self.context.socket(zmq.XPUB)
        self.xpub.bind("tcp://*:5556")
        
        # Backend for subscribers
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("inproc://cache")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Store last values per topic
        self.cache = {}
        
    def run(self):
        """Main cache loop"""
        while True:
            # Wait for XPUB or subscriber messages
            zmq.poll([self.xpub, self.subscriber], 1000)
            
            # Handle subscription messages from XPUB
            if self.xpub.poll(0, zmq.POLLIN):
                msg = self.xpub.recv_multipart()
                # First frame is subscription command (SUB/UNSUB)
                # Second frame is topic prefix
                if len(msg) >= 2:
                    action = msg[0]
                    topic = msg[1]
                    
                    if action == b'\x01':  # Subscribe
                        print(f"New subscriber for: {topic}")
                        # Send cached value if exists
                        if topic in self.cache:
                            self.xpub.send_multipart([topic, self.cache[topic]])
            
            # Handle incoming messages from publishers
            if self.subscriber.poll(0, zmq.POLLIN):
                msg = self.subscriber.recv_multipart()
                if len(msg) >= 2:
                    topic = msg[0]
                    data = msg[1]
                    
                    # Update cache
                    self.cache[topic] = data
                    
                    # Forward to subscribers
                    self.xpub.send_multipart([topic, data])

# Usage
cache = LastValueCache()
cache.run()
```

**Pathological Publisher (for testing):**

```python
import zmq
import time
import random

context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.connect("tcp://localhost:5556")

# Send 1000 updates per topic initially
for i in range(1000):
    for topic in "ABCDEFGHIJ":
        publisher.send_multipart([topic.encode(), f"Update {i}".encode()])

print("Initial burst complete, sending slow updates...")

# Then one random update per second
while True:
    topic = random.choice(list("ABCDEFGHIJ"))
    publisher.send_multipart([topic.encode(), time.time().encode()])
    time.sleep(1)
```

**Subscriber with LVC:**

```python
import zmq
import time

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")

# Delay connection to simulate late arrival
print("Waiting 5 seconds before connecting...")
time.sleep(5)

# Subscribe to topic A
subscriber.setsockopt_string(zmq.SUBSCRIBE, "A")

print("Connected! Should receive cached value immediately.")

# Receive messages
for i in range(5):
    msg = subscriber.recv_multipart()
    topic = msg[0].decode()
    data = msg[1].decode()
    print(f"Topic {topic}: {data}")
```

### Key Implementation Details

**Subscription Detection:**
- XPUB sends subscription commands as messages
- First byte: 0x01 (subscribe) or 0x00 (unsubscribe)
- Remaining bytes: topic prefix

**Cache Update Strategy:**
- Store last value for each unique topic
- Forward new values to all subscribers
- Send cached value on new subscription

**Memory Considerations:**
- Cache grows with number of unique topics
- Implement TTL or max-size limits for production
- Consider periodic cache cleanup

## Slow Subscriber Detection (Suicidal Snail Pattern)

The Suicidal Snail pattern detects and handles slow subscribers that can't keep up with the publication rate.

### Problem Statement

Slow subscribers cause:
1. Network buffer buildup
2. Memory exhaustion on publisher
3. Delayed delivery to fast subscribers
4. System-wide performance degradation

### Implementation

**Publisher with Slow Subscriber Detection:**

```python
import zmq
import time
import signal
import sys

class PublisherWithDetection:
    def __init__(self):
        self.context = zmq.Context()
        
        # XPUB for subscriber management
        self.xpub = self.context.socket(zmq.XPUB)
        self.xpub.bind("tcp://*:5557")
        
        # Track subscribers
        self.subscribers = {}
        self.slow_subscribers = set()
        
    def run(self):
        """Main publisher loop with detection"""
        # Set up signal handler for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        
        while True:
            # Send test message
            self.xpub.send_string("Test")
            
            # Check subscriber status
            self.check_subscribers()
            
            time.sleep(1)
    
    def check_subscribers(self):
        """Check if subscribers are keeping up"""
        # XPUB sends subscription messages
        # If we don't see activity, subscriber may be slow
        
        # Implementation depends on specific detection strategy
        # Common approaches:
        # 1. Heartbeat messages from subscribers
        # 2. Acknowledgment tracking
        # 3. Network buffer monitoring
    
    def cleanup(self, signum, frame):
        """Clean shutdown"""
        print("\nShutting down...")
        self.xpub.close()
        self.context.term()
        sys.exit(0)

# Usage
publisher = PublisherWithDetection()
publisher.run()
```

**Subscriber with Heartbeat:**

```python
import zmq
import time

class HeartbeatSubscriber:
    def __init__(self, heartbeat_interval=5):
        self.context = zmq.Context()
        
        # SUB socket for data
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5557")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # PUB socket for heartbeats
        self.heartbeat = self.context.socket(zmq.PUB)
        self.heartbeat.connect("tcp://localhost:5558")
        
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat = time.time()
    
    def run(self):
        """Main subscriber loop"""
        while True:
            # Send heartbeat periodically
            if time.time() - self.last_heartbeat > self.heartbeat_interval:
                self.heartbeat.send_string(f"Alive at {time.time()}")
                self.last_heartbeat = time.time()
            
            # Receive messages with timeout
            if self.sub.poll(1000, zmq.POLLIN):
                message = self.sub.recv_string()
                print(f"Received: {message}")
                
                # Simulate slow processing
                time.sleep(2)  # Intentionally slow

# Usage
subscriber = HeartbeatSubscriber()
subscriber.run()
```

### Detection Strategies

**Heartbeat-based:**
1. Subscribers send periodic heartbeats
2. Publisher tracks last heartbeat time
3. Missing heartbeats indicate slow/dead subscribers

**Acknowledgment-based:**
1. Subscribers acknowledge received messages
2. Publisher tracks unacknowledged messages
3. Timeout triggers slow subscriber detection

**Network-based:**
1. Monitor TCP buffer usage
2. High buffer usage indicates slow subscriber
3. Trigger flow control or disconnection

## XPUB Subscription Management

XPUB sockets provide built-in subscription management capabilities.

### Subscription Message Format

When a SUB socket subscribes/unsubscribes, XPUB receives:

```
[0x01 or 0x00][topic-prefix-bytes...]
```

- **0x01**: Subscribe command
- **0x00**: Unsubscribe command
- **Following bytes**: Topic prefix (can be empty for all topics)

### Handling Subscriptions

```python
import zmq

context = zmq.Context()
xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5556")

# Enable subscription forwarding
xpub.setsockopt(zmq.XPUB_VERBOSE, 1)

while True:
    msg = xpub.recv_multipart()
    
    # First frame is subscription command
    cmd = msg[0]
    topic = msg[1] if len(msg) > 1 else b""
    
    if cmd == b'\x01':
        print(f"Subscribe to: {topic}")
    elif cmd == b'\x00':
        print(f"Unsubscribe from: {topic}")
    
    # Forward data messages (not subscription commands)
    # Implementation depends on use case
```

### XPUB Options

**ZMQ_XPUB_VERBOSE:**
- Sends subscription messages to application
- Default: disabled (subscriptions handled internally)

**ZMQ_XPUB_NODROP:**
- Don't drop messages when subscribers are slow
- Default: drop messages to prevent backlog

## Fanout Forwarder Pattern

For scenarios requiring message replication across multiple endpoints.

### Implementation

```python
import zmq
import threading

class FanoutForwarder:
    def __init__(self):
        self.context = zmq.Context()
        
        # Input socket (PULL from collectors)
        self.input = self.context.socket(zmq.PULL)
        self.input.bind("tcp://*:5559")
        
        # Output sockets (PUSH to workers)
        self.outputs = []
        for i in range(3):
            output = self.context.socket(zmq.PUSH)
            output.connect(f"tcp://localhost:556{i}")
            self.outputs.append(output)
    
    def run(self):
        """Forward messages to all outputs"""
        while True:
            message = self.input.recv()
            
            # Send to all outputs (fanout)
            for output in self.outputs:
                output.send(message)

# Usage
forwarder = FanoutForwarder()
forwarder.run()
```

## Pub-Sub Security Considerations

### Authentication

ZeroMQ provides CURVE security for pub-sub:

```python
import zmq

context = zmq.Context()

# Publisher with CURVE
publisher = context.socket(zmq.PUB)
publisher.setsockopt(zmq.CURVE_SERVER, 1)
publisher.setsockopt_string(zmq.CERTIFICATE_PUBLIC, "server-public-key")
publisher.setsockopt_string(zmq.CERTIFICATE_KEYPAIR, "server-keypair")
publisher.bind("tcp://*:5556")

# Subscriber with CURVE
subscriber = context.socket(zmq.SUB)
subscriber.setsockopt(zmq.CURVE_SECURITY, zmq.CURVE)
subscriber.setsockopt_string(zmq.CERTIFICATE_PUBLIC, "client-public-key")
subscriber.setsockopt_string(zmq.CERTIFICATE_KEYPAIR, "client-keypair")
subscriber.setsockopt_string(zmq.CURVE_SERVERKEY, "server-public-key")
subscriber.connect("tcp://localhost:5556")
```

### Rate Limiting

Prevent pub-sub abuse with rate limiting:

```python
publisher.setsockopt(zmq.RATE, 100000)  # 100 Kb/sec
publisher.setsockopt(zmq.RECOVERY_IVL, 10000)  # 10 second recovery
```

## Best Practices

1. **Use LVC for critical data** - Ensure new subscribers get current state
2. **Implement slow subscriber detection** - Prevent system degradation
3. **Monitor subscription counts** - Track active subscribers
4. **Use appropriate topic prefixes** - Enable efficient filtering
5. **Consider message size** - Large messages impact pub-sub performance
6. **Implement backpressure** - Prevent publisher overwhelm
7. **Test reconnection behavior** - Verify subscriber recovery

## Troubleshooting

### Common Issues

**Messages not received:**
- Check subscription prefix matches message topic
- Verify connection established before publishing
- Ensure XPUB_VERBOSE is set if handling subscriptions manually

**Memory growth:**
- Implement last-value cache size limits
- Monitor subscriber count and disconnect slow ones
- Use rate limiting on publishers

**Slow subscribers:**
- Implement Suicidal Snail pattern
- Add heartbeat monitoring
- Consider message dropping for critical paths

## Next Steps

- [Reliable Request-Reply](05-reliable-request-reply.md) - Fault tolerance patterns
- [Advanced Request-Reply](04-advanced-request-reply.md) - Load balancing
- [Distributed Frameworks](08-distributed-framework.md) - Complete system design
