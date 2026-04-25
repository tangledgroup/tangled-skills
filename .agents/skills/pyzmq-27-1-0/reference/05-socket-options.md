# Socket Options Reference

Complete reference for ZeroMQ socket options with configuration examples, performance tuning guidance, and use cases.

## Option Categories

Socket options are organized into these categories:

| Category | Purpose | Common Options |
|----------|---------|----------------|
| I/O Tuning | Buffer sizes, timeouts | SNDBUF, RCVBUF, SNDTIMEO, RCVTIMEO |
| Flow Control | Message limits | HWM, SNDHWM, RCVHWM |
| Connection | Reconnect behavior | RECONNECT_IVL, BACKLOG |
| Routing | Identity and addressing | ROUTING_ID, IDENTITY |
| Security | Authentication | MECHANISM, CURVE_* |
| Monitoring | Event tracking | socket.monitor() |

## I/O and Timing Options

### Buffer Sizes

```python
import zmq

socket = context.socket(zmq.DEALER)

# Set send buffer size (bytes)
socket.setsockopt(zmq.SNDBUF, 1024 * 1024)  # 1 MB

# Set receive buffer size (bytes)
socket.setsockopt(zmq.RCVBUF, 1024 * 1024)  # 1 MB

# Get current values
sndbuf = socket.getsockopt(zmq.SNDBUF)
rcvbuf = socket.getsockopt(zmq.RCVBUF)
```

**Note:** These options set the initial buffer size. ZeroMQ may adjust internally based on OS limits.

### Timeouts

```python
import zmq

socket = context.socket(zmq.REQ)

# Receive timeout in milliseconds (0 = infinite, default)
socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout

# Send timeout in milliseconds (0 = infinite, default)
socket.setsockopt(zmq.SNDTIMEO, 5000)  # 5 second timeout

# Usage with timeout
try:
    message = socket.recv()  # Will raise zmq.Again after 5 seconds
except zmq.Again:
    print("Receive timeout")

try:
    socket.send(b"data")  # Will raise zmq.Again after 5 seconds
except zmq.Again:
    print("Send timeout")

# Non-blocking mode (timeout = 0)
socket.setsockopt(zmq.RCVTIMEO, 0)
socket.setsockopt(zmq.SNDTIMEO, 0)
```

### Connection Timeout

```python
import zmq

socket = context.socket(zmq.REQ)

# Set connection timeout in milliseconds (ZMQ 4.1+)
socket.setsockopt(zmq.CONNECT_TIMEOUT, 10000)  # 10 second connect timeout

socket.connect("tcp://unreachable-host:5555")

# Connection will fail after 10 seconds instead of hanging indefinitely
```

## Flow Control Options

### High Water Mark (HWM)

HWM limits the number of outstanding messages to prevent memory exhaustion.

```python
import zmq

socket = context.socket(zmq.PUSH)

# Set high water mark for both send and receive (ZMQ 3.x)
socket.setsockopt(zmq.HWM, 1000)

# Or set separately (ZMQ 4.1+)
socket.setsockopt(zmq.SNDHWM, 1000)  # Max messages in send queue
socket.setsockopt(zmq.RCVHWM, 1000)  # Max messages in receive queue

# Get HWM values
sndhwm = socket.getsockopt(zmq.SNDHWM)
rcvhwm = socket.getsockopt(zmq.RCVHWM)

# Get legacy HWM (minimum of SNDHWM and RCVHWM)
hwm = socket.get_hwm()
```

**Behavior:**
- When send queue reaches HWM, sender blocks (or fails with timeout)
- Prevents fast producers from overwhelming slow consumers
- Critical for backpressure in pipeline patterns

### Maximum Message Size

```python
import zmq

socket = context.socket(zmq.DEALER)

# Set maximum message size in bytes (-1 = unlimited, default)
socket.setsockopt(zmq.MAXMSGSIZE, 10 * 1024 * 1024)  # 10 MB limit

# Or set at context level (ZMQ 4.1+)
context.setsockopt(zmq.MAX_MSGSZ, 10 * 1024 * 1024)

# Messages exceeding MAXMSGSIZE will fail with EMSGSIZE error
try:
    socket.send(b"x" * (11 * 1024 * 1024))  # 11 MB - too large!
except zmq.Again:
    print("Message too large")
```

## Connection and Reconnect Options

### Reconnect Intervals

```python
import zmq

socket = context.socket(zmq.DEALER)

# Initial reconnect interval in milliseconds (default: 1000ms)
socket.setsockopt(zmq.RECONNECT_IVL, 2000)  # Wait 2 seconds before reconnect

# Maximum reconnect interval (exponential backoff, default: 32000ms)
socket.setsockopt(zmq.RECONNECT_IVL_MAX, 60000)  # Max 60 seconds

# Reconnect behavior on failure (ZMQ 4.3+)
from zmq import ReconnectStop
socket.setsockopt(zmq.RECONNECT_STOP, ReconnectStop.CONN_REFUSED)  # Stop after connection refused
```

### Connection Backlog

```python
import zmq

socket = context.socket(zmq.ROUTER)

# Set maximum pending connections (default: depends on OS)
socket.setsockopt(zmq.BACKLOG, 128)  # Allow 128 pending connections

# Connections beyond backlog will be rejected until some are accepted
```

### Immediate Connection

```python
import zmq

socket = context.socket(zmq.DEALER)

# Don't wait for connections before sending (default: 0)
socket.setsockopt(zmq.IMMEDIATE, 1)

# With IMMEDIATE=0, socket won't send until at least one connection is established
# With IMMEDIATE=1, messages are queued even without connections

socket.connect("tcp://localhost:5564")
socket.send(b"message")  # Queued immediately with IMMEDIATE=1
```

## Routing and Identity Options

### Routing ID (DEALER/ROUTER)

```python
import zmq
import uuid

socket = context.socket(zmq.DEALER)

# Set routing identity for ROUTER to send replies
routing_id = str(uuid.uuid4()).encode('utf-8')
socket.setsockopt(zmq.ROUTING_ID, routing_id)

# Or use setsockopt_string
socket.setsockopt_string(zmq.ROUTING_ID, "client-123")

# Get current routing ID
current_id = socket.getsockopt(zmq.ROUTING_ID)
```

### Router Raw Mode

```python
import zmq

router = context.socket(zmq.ROUTER)

# Disable automatic identity framing (ZMQ 3.1+)
router.setsockopt(zmq.ROUTER_RAW, 1)

# With ROUTER_RAW=0 (default): received messages include identity frame
# With ROUTER_RAW=1: identity is separate, message frames are raw

dealer = context.socket(zmq.DEALER)
dealer.setsockopt(zmq.ROUTER_RAW, 1)  # Must match router setting
```

### Router Mandatory Mode

```python
import zmq

router = context.socket(zmq.ROUTER)

# Enable mandatory mode (ZMQ 3.2+)
router.setsockopt(zmq.ROUTER_MANDATORY, 1)

# In mandatory mode:
# - Send fails if no recipient available (instead of queuing)
# - Provides immediate feedback on delivery failures
# - Useful for request-reply where lost messages are unacceptable
```

### Router Handover

```python
import zmq

router = context.socket(zmq.ROUTER)

# Enable handover mode (ZMQ 4.1+)
router.setsockopt(zmq.ROUTER_HANDOVER, 1)

# In handover mode:
# - Each client gets one message at a time
# - Client must receive reply before getting next request
# - Enforces strict request-reply protocol over DEALER/ROUTER
```

### Router Notify

```python
import zmq
from zmq import RouterNotify

router = context.socket(zmq.ROUTER)

# Enable connection/disconnection notifications (ZMQ 4.2+)
router.setsockopt(zmq.ROUTER_NOTIFY, RouterNotify.CONNECT | RouterNotify.DISCONNECT)

while True:
    frames = router.recv_multipart()
    
    # First frame indicates event type
    if frames[0] == b'\x01':  # CONNECT
        identity = frames[1]
        print(f"Client connected: {identity}")
    elif frames[0] == b'\x02':  # DISCONNECT
        identity = frames[1]
        print(f"Client disconnected: {identity}")
    else:
        # Regular message
        identity, message = frames
        print(f"Message from {identity}: {message}")
```

## Pub/Sub Options

### Subscribe/Unsubscribe (SUB)

```python
import zmq

subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5565")

# Subscribe to topic prefix
subscriber.setsockopt_string(zmq.SUBSCRIBE, "news.")

# Subscribe to multiple topics
subscriber.setsockopt_string(zmq.SUBSCRIBE, "stock.")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "weather.")

# Unsubscribe from topic
subscriber.setsockopt_string(zmq.UNSUBSCRIBE, "weather.")

# Subscribe to all messages (empty string)
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

# Unsubscribe from all
subscriber.setsockopt_string(zmq.UNSUBSCRIBE, "")
```

### XPUB Verbose Mode

```python
import zmq

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5566")

# Enable verbose mode (send sub/unsub events)
xpub.setsockopt(zmq.XPUB_VERBOSE, 1)

# Even more verbose (include topic data in events)
xpub.setsockopt(zmq.XPUB_VERBOSER, 1)

# Receive subscription events
while True:
    event = xpub.recv()
    if event[0] == 1:  # Subscribe
        topic = event[1:]
        print(f"Subscriber subscribed to: {topic}")
    elif event[0] == 0:  # Unsubscribe
        topic = event[1:]
        print(f"Subscriber unsubscribed from: {topic}")
```

### XPUB Manual Mode

```python
import zmq

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5566")

# Enable manual subscription management
xpub.setsockopt(zmq.XPUB_MANUAL, 1)

# In manual mode:
# - XPUB doesn't automatically forward subscriptions to XSUB
# - You must explicitly send subscription commands
# - Gives you full control over message distribution

# Manually acknowledge subscription
subscription = xpub.recv()  # Receive sub event
xpub.send(subscription)     # Forward to XSUB to activate
```

### XPUB Welcome Message

```python
import zmq

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5567")

# Send welcome message to new subscribers (ZMQ 4.1+)
xpub.setsockopt_string(zmq.XPUB_WELCOME_MSG, "Welcome to the pub!")

# New XSUB sockets will receive this message upon connecting
```

### XPUB No Drop

```python
import zmq

xpub = context.socket(zmq.XPUB)
xpub.bind("tcp://*:5568")

# Don't drop messages when subscribers are slow (ZMQ 3.2+)
xpub.setsockopt(zmq.XPUB_NODROP, 1)

# With XPUB_NODROP=0 (default): messages with no subscribers are dropped
# With XPUB_NODROP=1: messages are queued even without subscribers
```

## TCP-Specific Options

### TCP Keepalive

```python
import zmq

socket = context.socket(zmq.DEALER)

# Enable TCP keepalive (default: 0 = disabled)
socket.setsockopt(zmq.TCP_KEEPALIVE, 1)

# Keepalive parameters (Linux only)
socket.setsockopt(zmq.TCP_KEEPALIVE_CNT, 5)      # Number of probes
socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 60)    # Idle time before probes (seconds)
socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 10)   # Interval between probes (seconds)
```

### IPv6 Support

```python
import zmq

socket = context.socket(zmq.DEALER)

# Enable IPv6 (ZMQ 3.2+)
socket.setsockopt(zmq.IPV6, 1)

# With IPV6=1: socket can bind to IPv6 addresses
# With IPV6=0: socket uses IPv4 only

socket.bind("tcp://[::1]:5569")  # IPv6 localhost
```

### IPv4 Only Mode

```python
import zmq

socket = context.socket(zmq.DEALER)

# Force IPv4 only (ZMQ 4.2+)
socket.setsockopt(zmq.IPV4ONLY, 1)

# Prevents binding to IPv6-mapped IPv4 addresses
```

### Bind to Device

```python
import zmq

socket = context.socket(zmq.DEALER)

# Bind to specific network interface (ZMQ 4.2+)
socket.setsockopt_string(zmq.BINDTODEVICE, "eth0")

socket.bind("tcp://*:5570")  # Will only listen on eth0
```

### TCP Accept Filter

```python
import zmq

socket = context.socket(zmq.ROUTER)

# Filter incoming connections by remote address (FreeBSD/Linux, ZMQ 4.2+)
socket.setsockopt_string(zmq.TCP_ACCEPT_FILTER, "192.168.1.*")

# Only accepts connections from 192.168.1.x addresses
```

## Multicast Options (RADIO/DISH)

```python
import zmq

radio = context.socket(zmq.RADIO)

# Set multicast group address
radio.setsockopt_string(zmq.MULTICAST_GROUP, "239.192.1.1")

# Set multicast hop limit (TTL)
radio.setsockopt(zmq.MULTICAST_HOPS, 4)

# Enable/disable multicast loopback
radio.setsockopt(zmq.MULTICAST_LOOP, 1)

# Maximum datagram size (ZMQ 4.3+)
radio.setsockopt(zmq.MULTICAST_MAXTPDU, 1024 * 1024)  # 1 MB
```

## Security Options

### Mechanism Selection

```python
import zmq

socket = context.socket(zmq.REQ)

# Set security mechanism
socket.setsockopt(zmq.MECHANISM, zmq.CURVE)  # or zmq.PLAIN, zmq.GSSAPI

# Check current mechanism
mechanism = socket.getsockopt(zmq.MECHANISM)
print(f"Mechanism: {mechanism}")  # 2 = CURVE
```

### Handshake Interval

```python
import zmq

socket = context.socket(zmq.DEALER)

# Set handshake timeout in milliseconds (ZMQ 4.1+)
socket.setsockopt(zmq.HANDSHAKE_IVL, 60000)  # 60 second handshake timeout

# Time to wait for protocol/security handshake to complete
```

## Metadata and QoS Options

### Message Metadata

```python
import zmq

socket = context.socket(zmq.DEALER)

# Attach metadata to messages (ZMQ 4.2+)
metadata = {b"priority": b"high", b"category": b"urgent"}
socket.setsockopt(zmq.METADATA, metadata)

# Metadata is sent with next message and can be retrieved on receiver
```

### Priority

```python
import zmq

socket = context.socket(zmq.DEALER)

# Set message priority (ZMQ 4.3+)
socket.setsockopt(zmq.PRIORITY, 10)  # Higher values = higher priority

# Messages with higher priority are sent first when multiple pending
```

### Conflation

```python
import zmq

socket = context.socket(zmq.PUB)

# Enable message conflation (ZMQ 3.2+)
socket.setsockopt(zmq.CONFLATE, 1)

# With CONFLATE=1: only the last message is kept in send queue
# Earlier messages are discarded if not sent yet
# Useful for sensor data where only latest value matters
```

## Performance Tuning Examples

### High-Throughput Configuration

```python
import zmq

context = zmq.Context()
context.setsockopt(zmq.IO_THREADS, 4)      # More I/O threads
context.setsockopt(zmq.MAX_SOCKETS, 4096)  # More sockets

socket = context.socket(zmq.DEALER)
socket.setsockopt(zmq.SNDBUF, 8 * 1024 * 1024)   # 8 MB send buffer
socket.setsockopt(zmq.RCVBUF, 8 * 1024 * 1024)   # 8 MB recv buffer
socket.setsockopt(zmq.SNDHWM, 10000)             # High water mark
socket.setsockopt(zmq.RCVHWM, 10000)
socket.setsockopt(zmq.MAXMSGSIZE, 64 * 1024 * 1024)  # 64 MB max message
socket.setsockopt(zmq.TCP_KEEPALIVE, 1)          # Keep connections alive
socket.setsockopt(zmq.IMMEDIATE, 1)              # Send without waiting for connect
```

### Low-Latency Configuration

```python
import zmq

context = zmq.Context()
context.setsockopt(zmq.IO_THREADS, 1)  # Single I/O thread reduces context switches

socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.SNDTIMEO, 100)   # Short timeouts for quick failure
socket.setsockopt(zmq.RCVTIMEO, 100)
socket.setsockopt(zmq.CONFLATE, 1)     # Drop old messages, keep only latest
socket.setsockopt(zmq.IMMEDIATE, 1)    # Don't wait for connection
```

### Reliable Delivery Configuration

```python
import zmq

context = zmq.Context()

socket = context.socket(zmq.DEALER)
socket.setsockopt(zmq.RECONNECT_IVL, 1000)     # Reconnect every second
socket.setsockopt(zmq.RECONNECT_IVL_MAX, 10000)  # Max 10 seconds
socket.setsockopt(zmq.SNDHWM, 1000)            # Limit queue to prevent memory issues
socket.setsockopt(zmq.RCVHWM, 1000)
socket.setsockopt(zmq.TCP_MAXRT, 10)           # Max TCP retries (ZMQ 4.2+)
```

## Option Reference Table

| Option | Type | Socket Types | Default | Description |
|--------|------|--------------|---------|-------------|
| AFFINITY | int64 | All | 0 | Subscription affinity bitmask |
| BACKLOG | int | Server sockets | OS default | Max pending connections |
| CONFLATE | int | PUB, PAIR | 0 | Keep only last message |
| CONNECT_ROUTING_ID | bytes | DEALER | - | Initial routing ID for connect |
| CONNECTIONS | int | All | - | Number of connections (read-only) |
| EVENTS | int | All | - | Socket events (read-only) |
| FD | int | All | - | File descriptor (read-only) |
| HWM | int | All | 1000 | High water mark |
| IDENTITY | bytes | ROUTER, DEALER | - | Socket identity |
| IMMEDIATE | int | All | 0 | Send before connections established |
| LAST_ENDPOINT | string | All | - | Last bound/connected endpoint (read-only) |
| MAXMSGSIZE | int64 | All | -1 | Maximum message size (-1 = unlimited) |
| MECHANISM | int | All | NULL | Security mechanism |
| MONITOR_SOCK | socket | All | - | Monitoring socket (read-only) |
| RCVMORE | int | All | - | More messages in multipart (read-only) |
| RCVBUF | int | All | OS default | Receive buffer size |
| RCVHWM | int | All | 1000 | Receive high water mark |
| RCVTIMEO | int | All | 0 | Receive timeout (ms) |
| RATE | int | PUB, XPUB | 1000 | Message rate (messages/sec) |
| RECONNECT_IVL | int | All | 1000 | Reconnect interval (ms) |
| RECONNECT_IVL_MAX | int | All | 32000 | Max reconnect interval (ms) |
| ROUTING_ID | bytes | DEALER | - | Routing identity |
| SNDBUF | int | All | OS default | Send buffer size |
| SNDHWM | int | All | 1000 | Send high water mark |
| SNDTIMEO | int | All | 0 | Send timeout (ms) |
| SOCKS_PROXY | string | All | - | SOCKS proxy address |
| TCP_KEEPALIVE | int | TCP sockets | 0 | Enable TCP keepalive |
| TYPE | int | All | - | Socket type (read-only) |
| USE_FD | int | IPC sockets | 0 | Pass FD over IPC |
| VMCI_BUFFER_SIZE | int64 | VMCI sockets | 1MB | VMCI buffer size |
| ZAP_DOMAIN | string | All | "" | Domain for ZAP authentication |
