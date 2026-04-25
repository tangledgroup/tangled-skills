# ZeroMQ Protocols and Transports

This reference covers the ZMTP (ZeroMQ Messaging Transport Protocol) wire protocol, transport mechanisms, and message framing.

## ZMTP Protocol Overview

ZMTP (RFC 23) is the wire protocol used by ZeroMQ for communication between peers. It provides:

- **Message framing**: Clear boundaries between messages
- **Security**: Support for PLAIN and CURVE authentication
- **Heartbeating**: Detection of dead peers
- **Flow control**: Prevents fast senders from overwhelming receivers

### Protocol Layers

```
┌─────────────────────────────────┐
│         Application             │
├─────────────────────────────────┤
│      ZeroMQ Sockets             │
├─────────────────────────────────┤
│   ZMTP (Messaging Protocol)     │
├─────────────────────────────────┤
│  Transport (TCP, IPC, inproc)   │
├─────────────────────────────────┤
│      Network/OS Layer           │
└─────────────────────────────────┘
```

## ZMTP Command Types

All ZMTP communication uses commands with this structure:

```
[TYPE (1 byte)][LENGTH (variable)][DATA (variable)]
```

### Command Types

| Type | Name | Description |
|------|------|-------------|
| 0x00 | Hello | Initial handshake |
| 0x01 | Ready | Socket ready for messages |
| 0x02 | Welcome | Server accepts connection |
| 0x03 | Error | Protocol error |
| 0x04 | Data | Message frame |
| 0x05 | Ping | Heartbeat request |
| 0x06 | Pong | Heartbeat response |
| 0x07 | Leave | Closing connection |

### Hello Command

Sent by client to initiate connection:

```
[0x00][VERSION (1)][IDENTITY (N)]

Where:
- VERSION = Protocol version (3 for ZMTP/3.0)
- IDENTITY = Socket identity (can be empty)
```

Example Hello:
```
00 03 48 65 6C 6C 6F
 │  │  └─ "Hello" (identity)
 │  └─ Version 3
 └─ Command type (Hello)
```

### Data Command

Carries message frames:

```
[0x04][LENGTH (8 bytes, big-endian)][DATA (LENGTH bytes)]
```

Length is always 8 bytes even for small messages.

Example Data command sending "Hi":
```
04 00 00 00 00 00 00 00 02 48 69
 │  └─ Length: 2 (big-endian)
 │        └─ "Hi"
 └─ Command type (Data)
```

### Message Framing

Complete messages consist of multiple Data commands:

```
Message 1:
  [Data][Frame 1]
  [Data][Frame 2]
  [Data][Frame 3]

Message 2:
  [Data][Frame 1]
  [Data][Frame 2]
```

Each frame is a separate Data command. Receiving end reassembles frames into complete message.

### More Flag

Last frame of message has "more" flag cleared:

```
[More=1][Frame 1]  // More frames follow
[More=1][Frame 2]  // More frames follow
[More=0][Frame 3]  // Last frame
```

## Transport Protocols

### tcp:// (TCP/IP)

Standard TCP transport for network communication.

**Binding:**
```c
zmq_bind(socket, "tcp://*:5555");      // All interfaces
zmq_bind(socket, "tcp://192.168.1.1:5555");  // Specific interface
```

**Connecting:**
```c
zmq_connect(socket, "tcp://server.example.com:5555");
zmq_connect(socket, "tcp://192.168.1.100:5555");
```

**Options:**
- `ZMQ_IPC_FILTER`: Enable/disable IPC-level filtering
- `ZMQ_TCP_KEEPALIVE`: Enable TCP keepalive (0 or 1)
- `ZMQ_TCP_KEEPALIVE_CNT`: Keepalive probes before giving up
- `ZMQ_TCP_KEEPALIVE_IDLE`: Seconds of idle before keepalive
- `ZMQ_TCP_KEEPALIVE_INTVL`: Seconds between keepalive probes

**Characteristics:**
- Reliable, ordered delivery (TCP guarantees)
- Works across networks
- Subject to NAT/firewall restrictions
- Slower than IPC or inproc

### ipc:// (Unix Domain Sockets)

Fast local communication on Unix/Linux systems.

**Binding:**
```c
zmq_bind(socket, "ipc:///tmp/mysocket");
zmq_bind(socket, "ipc://@/tmp/mysocket");  // Abstract namespace (Linux only)
```

**Connecting:**
```c
zmq_connect(socket, "ipc:///tmp/mysocket");
```

**Options:**
- `ZMQ_IPC_FILTER`: Enable/disable filtering
- File permissions controlled by umask

**Characteristics:**
- Faster than TCP for local communication
- No network overhead
- Requires filesystem access
- Linux abstract namespace doesn't create file

### inproc:// (In-Process)

Fastest transport, for sockets within same process.

**Binding:**
```c
zmq_bind(socket1, "inproc://mysocket");
```

**Connecting:**
```c
zmq_connect(socket2, "inproc://mysocket");  // Must match exactly
```

**Characteristics:**
- Fastest transport (no copying)
- Only works within same process
- Endpoint name must match exactly
- Bind must happen before connect

### norm:// and epgm:// (Multicast)

Reliable multicast transports (requires NORM library).

**Binding:**
```c
zmq_bind(socket, "epgm://224.143.0.1:5556");
```

**Characteristics:**
- Efficient one-to-many distribution
- Requires network multicast support
- EPGM provides reliability over PGm
- Not available on all platforms

## Message Encoding

### Binary Format

ZeroMQ messages are binary by default:

```c
// Send binary data
uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
zmsg_t *msg = zmsg_new();
zmsg_addmem(msg, data, 4);
zmsg_send(&msg, socket);
```

### String Encoding

Strings are sent as UTF-8 encoded frames:

```c
// Send string (null-terminated)
zmsg_addstr(msg, "Hello World");  // Adds 11 bytes, no null terminator

// Receive string
const char *str = zmsg_popstr(msg);  // Returns null-terminated string
```

**Important**: String frames don't include null terminator in wire format.

### Z85 Encoding (RFC 32)

ASCII-safe encoding for binary data (e.g., identities, keys):

```c
// Encode binary to Z85 string (20 bytes -> 25 chars)
uint8_t binary[20] = {...};
char z85[26];
zmq_z85_encode(z85, binary, 20);

// Decode Z85 string to binary
uint8_t decoded[20];
zmq_z85_decode(decoded, z85);
```

**Use cases:**
- Socket identities (ROUTER/DEALER)
- CURVE public keys
- Logging binary data

### JSON Encoding

For structured data, use JSON:

```c
#include <jansson.h>

// Create JSON message
json_t *root = json_object();
json_object_set_new(root, "command", json_string("TASK"));
json_object_set_new(root, "id", json_integer(42));
json_object_set_new(root, "data", json_string("process this"));

// Serialize to string
char *json_str = json_dumps(root, JSON_ENCODE_ANY);

// Send as ZeroMQ message
zmsg_t *msg = zmsg_new();
zmsg_addstr(msg, json_str);
zmsg_send(&msg, socket);

// Cleanup
free(json_str);
json_decref(root);
```

## Heartbeating

ZMTP includes built-in heartbeating to detect dead peers.

### Configuration

```c
// Set heartbeat interval (milliseconds)
int interval = 10000;  // 10 seconds
zmq_setsockopt(socket, ZMQ_HEARTBEAT_IVL, &interval, sizeof(interval));

// Set heartbeat timeout
int timeout = 30000;   // 30 seconds
zmq_setsockopt(socket, ZMQ_HEARTBEAT_TIMEOUT, &timeout, sizeof(timeout));

// Set heartbeat retry count
int retries = 3;
zmq_setsockopt(socket, ZMQ_HEARTBEAT_RETRIES, &retries, sizeof(retries));
```

### Heartbeat Flow

```
Client                          Server
  |                               |
  |-------- Ping --------------->|
  |                               |
  |<------- Pong ----------------|
  |                               |
  | (no response for 30s)         |
  |                               |
  | Connection closed             |
```

If no Pong received within timeout, connection is closed.

## Flow Control

### High-Water Marks (HWM)

Prevent memory exhaustion by limiting queued messages:

```c
// Set HWM to 1000 messages
int hwm = 1000;
zmq_setsockopt(socket, ZMQ_SNDHWM, &hwm, sizeof(hwm));
zmq_setsockopt(socket, ZMQ_RCVHWM, &hwm, sizeof(hwm));
```

**Behavior when HWM reached:**
- **Sender**: Blocks on send() (default) or drops message
- **Receiver**: New messages rejected at sender

### Buffer Sizes

Control OS-level buffer sizes:

```c
// Set to 1MB
int bufsize = 1024 * 1024;
zmq_setsockopt(socket, ZMQ_SNDBUF, &bufsize, sizeof(bufsize));
zmq_setsockopt(socket, ZMQ_RCVBUF, &bufsize, sizeof(bufsize));
```

**Note**: OS may limit maximum buffer size.

## Connection Management

### Reconnection

ZeroMQ automatically reconnects on failure:

```c
// Set reconnection interval (milliseconds)
int interval = 1000;  // 1 second
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL, &interval, sizeof(interval));

// Set maximum reconnection interval (exponential backoff)
int max_interval = 32000;  // 32 seconds
zmq_setsockopt(socket, ZMQ_RECONNECT_IVL_MAX, &max_interval, sizeof(max_interval));

// Enable/disable automatic reconnection
int reconnect = 1;
zmq_setsockopt(socket, ZMQ_RECONNECTABLE, &reconnect, sizeof(reconnect));
```

### Connection Lifecycle

```
[Socket created]
     │
     ├─ bind() ──> [Listening] ──> [Accept connections]
     │
     └─ connect() ──> [Connecting] ──> [Connected]
                              │
                              ├─ [Error] ──> [Reconnecting...]
                              │
                              └─ [Closed] ──> [Socket closed]
```

### Monitoring Connection Events

```c
// Enable monitoring
zmq_socket_monitor(socket, "inproc://monitor", ZMQ_EVENT_ALL);

// Monitor socket in separate thread
void *monitor = zmq_socket(context, ZMQ_PAIR);
zmq_bind(monitor, "inproc://monitor");

while (1) {
    zevent_t *event = zevent_recv(monitor);
    int event_type = zevent_event(event);
    
    switch (event_type) {
        case ZMQ_EVENT_CONNECTED:
            printf("Connected\n");
            break;
        case ZMQ_EVENT_CONNECT_DELAYED:
            printf("Connection delayed, retrying...\n");
            break;
        case ZMQ_EVENT_CONNECTION_ERROR:
            printf("Connection error\n");
            break;
        case ZMQ_EVENT_DISCONNECTED:
            printf("Disconnected\n");
            break;
    }
    
    zevent_destroy(&event);
}
```

## Security Protocols

### ZMTP-PLAIN (RFC 24)

Simple username/password authentication.

**Wire format:**
```
Client -> Server: [Hello][Version][Empty Identity]
Server -> Client: [Welcome][Empty]
Client -> Server: [Login Request][Username][Password]
Server -> Client: [Login Response][Status][Empty or Error Message]
```

See [Security](05-security.md) for implementation details.

### ZMTP-CURVE (RFC 25)

Public-key authentication with encryption.

**Wire format:**
```
Client -> Server: [Hello][Version][Empty Identity][Curve Mechanism]
Server -> Client: [Welcome][Server Key]
Client -> Server: [Client Key][Nonce]
Server -> Client: [OK]
[All subsequent messages encrypted]
```

See [Security](05-security.md) for implementation details.

## Wire Protocol Example

Complete ZMTP exchange for sending "Hello":

```
=== Connection Setup ===
C -> S: 00 03              (Hello, version 3)
S -> C: 02                  (Welcome)
C -> S: 01                  (Ready)

=== Sending Message ===
C -> S: 04 00 00 00 00 00 00 00 05 48 65 6C 6C 6F  (Data, "Hello")

=== Receiving ===
S receives: "Hello" as single-frame message
```

Hex breakdown:
- `04`: Data command
- `00 00 00 00 00 00 00 05`: Length = 5 (big-endian)
- `48 65 6C 6C 6F`: "Hello" in ASCII

---

## See Also

- [Socket Patterns](01-socket-patterns.md) - How protocols support patterns
- [Security](05-security.md) - Authentication protocols
- [Performance](06-performance.md) - Protocol tuning
- [RFC 23/ZMTP](http://rfc.zeromq.org/spec:23/) - Full specification
