# ZeroMQ Basics

This reference covers fundamental ZeroMQ concepts, getting started, and basic patterns from Chapter 1 of the ZGuide.

## ZeroMQ Overview

ZeroMQ (also known as ØMQ, 0MQ, or zmq) looks like an embeddable networking library but acts like a concurrency framework. It provides sockets that carry atomic messages across various transports like in-process, inter-process, TCP, and multicast. You can connect sockets N-to-N with patterns like fan-out, pub-sub, task distribution, and request-reply.

### Key Characteristics

- **Fast enough** to be the fabric for clustered products
- **Asynchronous I/O model** for scalable multicore applications
- **Multiple language APIs** (28+ languages supported)
- **Cross-platform** - runs on most operating systems
- **LGPLv3 open source** from iMatix

### The Zen of Zero

The Ø in ZeroMQ represents tradeoffs and minimalism:
- **Zero broker** - no middleware required
- **Zero latency** (as close as possible)
- **Zero administration** - simple deployment
- **Zero cost** - free and open source
- **Zero waste** - efficient resource usage

ZeroMQ adds power by removing complexity rather than exposing new functionality.

## Getting Started

### Installation

Install ZeroMQ development libraries for your platform:

**Debian/Ubuntu:**
```bash
sudo apt-get install libzmq3-dev
```

**macOS (Homebrew):**
```bash
brew install zeromq
```

**Arch Linux:**
```bash
sudo pacman -S zeromq
```

### Language Bindings

Install language-specific bindings:

**Python (pyzmq):**
```bash
pip install pyzmq
```

**Node.js (nanomsg):**
```bash
npm install nanomsg
```

**Go (go-zmq):**
```bash
go get github.com/pebbe/zmq4
```

**Java (JZMQ):**
```bash
# Download from https://github.com/zeromq/jzmq
```

### Version Reporting

Check your ZeroMQ version:

```c
#include <stdio.h>
#include <zmq.h>

int main ()
{
    int major, minor, patch;
    zmq_version (&major, &minor, &patch);
    printf ("Current ZeroMQ version is %d.%d.%d\n", major, minor, patch);
    return 0;
}
```

```python
import zmq
print(f"Current ZeroMQ version is {zmq.version()}")
```

## Hello World Example

The canonical request-reply pattern demonstrates ZeroMQ's core functionality.

### Request-Reply Pattern Overview

- **REP socket** (server): Binds to port, receives requests, sends replies
- **REQ socket** (client): Connects to server, sends requests, waits for replies
- **Transport**: tcp:// for network communication

### Server Implementation (Multiple Languages)

**C:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zmq.h>

int main (void)
{
    void *context = zmq_init (1);
    void *responder = zmq_socket (context, ZMQ_REP);
    zmq_bind (responder, "tcp://*:5555");
    
    while (1) {
        char buffer [10];
        zmq_recv (responder, buffer, 10, 0);
        printf ("Received Hello\n");
        zmq_send (responder, "World", 5, 0);
    }
    return 0;
}
```

**Python:**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    print(f"Received: {message}")
    socket.send(b"World")
```

**Java:**
```java
public class HelloServer {
    public static void main(String[] args) {
        ZContext context = new ZContext();
        Socket socket = context.createSocket(ZMQ.REP);
        socket.bind("tcp://*:5555");
        
        while (true) {
            Message message = socket.recvMsg();
            System.out.println("Received Hello");
            message.send(socket);
        }
    }
}
```

**Go:**
```go
package main

import (
    "fmt"
    "github.com/pebbe/zmq4"
)

func main() {
    ctx, _ := zmq4.NewContext(1)
    socket, _ := ctx.NewSocket(zmq4.REP)
    socket.Bind("tcp://*:5555")
    
    for {
        msg, _ := socket.RecvMsgBytes()
        fmt.Println("Received Hello")
        socket.Send([]byte("World"), 0)
    }
}
```

### Client Implementation (Multiple Languages)

**C:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zmq.h>

int main (void)
{
    void *context = zmq_init (1);
    void *requester = zmq_socket (context, ZMQ_REQ);
    zmq_connect (requester, "tcp://localhost:5555");
    
    int request;
    for (request = 0; request < 10; request++) {
        printf ("Sending Hello %d...\n", request);
        zmq_send (requester, "Hello", 5, 0);
        
        char buffer [10];
        zmq_recv (requester, buffer, 10, 0);
        printf ("Received World %d\n", request);
    }
    return 0;
}
```

**Python:**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

for i in range(10):
    print(f"Sending Hello {i}...")
    socket.send(b"Hello")
    message = socket.recv()
    print(f"Received {message}")
```

**JavaScript (Node.js):**
```javascript
var zmq = require('zmq');
var sock = zmq.socket('req');

sock.connect("tcp://localhost:5555");

for (var i = 0; i < 10; i++) {
    console.log('Sending Hello ' + i + '...');
    sock.send('Hello', function (err) {
        sock.recv(function (err, message) {
            console.log('Received ' + message.toString());
        });
    });
}
```

### Important Notes

**Socket Lifecycle:**
- Always close sockets when done: `zmq_close(socket)`
- Terminate context: `zmq_term(context)`
- Use try-finally or context managers for cleanup

**String Handling:**
- ZeroMQ works with byte arrays, not strings
- String messages must be null-terminated in C
- Use proper encoding (UTF-8 recommended)

**Connection Timing:**
- Server should bind before client connects
- ZeroMQ handles reconnection automatically
- Connection is asynchronous - may take time to establish

## Publishing Weather Updates

Basic pub-sub pattern for broadcasting messages to multiple subscribers.

### Publisher Implementation

**Python:**
```python
import zmq
import time
import random

context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

while True:
    # Generate random weather update
    zipcode = random.randint(0, 99999)
    temperature = random.randint(-80, 80)
    humidity = random.randint(0, 100)
    
    # Send as string with topic (zipcode)
    update = f"{zipcode} {temperature} {humidity}"
    publisher.send_string(update)
    time.sleep(1)
```

**C:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zmq.h>

int main (void)
{
    void *context = zmq_init (1);
    void *publisher = zmq_socket (context, ZMQ_PUB);
    zmq_bind (publisher, "tcp://*:5556");
    
    while (1) {
        int zipcode, temperature, humidity;
        zipcode = rand() % 100000;
        temperature = rand() % 200 - 100;
        humidity = rand() % 100;
        
        char buffer [32];
        sprintf (buffer, "%05d%d%02d", zipcode, temperature, humidity);
        zmq_send (publisher, buffer, strlen(buffer), 0);
        
        sleep(1);
    }
    return 0;
}
```

### Subscriber Implementation

**Python:**
```python
import zmq
import time

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")

# Subscribe to all updates (empty string matches everything)
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

print("Collecting updates from weather server...")
for i in range(100):
    string = subscriber.recv_string()
    zipcode, temperature, humidity = string.split()
    print(f"Zipcode {zipcode}: temp={temperature}°C, humidity={humidity}%")
```

**JavaScript (Node.js):**
```javascript
var zmq = require('zmq');
var sub = zmq.socket('sub');

sub.connect("tcp://localhost:5556");
sub.subscribe("");  // Subscribe to all topics

console.log("Collecting updates from weather server...");
var count = 0;
sub.on('message', function (topic, message) {
    var parts = message.toString().split(' ');
    console.log("Zipcode " + parts[0] + ": temp=" + parts[1] + " humidity=" + parts[2]);
    count++;
    if (count >= 100) sub.close();
});
```

### Pub-Sub Key Concepts

**Topic Filtering:**
- Subscribers can filter by topic prefix
- Empty subscribe string matches all messages
- Topic is the message prefix before the first space

**Fire-and-Forget:**
- PUB does not track subscribers
- Messages sent before subscriber connects are lost
- No acknowledgments or delivery guarantees

**Multiple Transports:**
- Can bind to multiple transports simultaneously
- Subscribers can connect to different transports
- Example: `bind("tcp://*:5556")` and `bind("ipc://weather")`

## Multipart Messages

ZeroMQ messages consist of one or more frames. This enables complex protocols.

### Sending Multipart Messages

**Python:**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.DEALER)
socket.connect("tcp://localhost:5555")

# Send multipart message
socket.send_multipart([b"Hello", b"", b"World"])
```

**C:**
```c
// Send multipart message
zmq_send (socket, "Hello", 5, ZMQ_SNDMORE);
zmq_send (socket, "", 1, ZMQ_SNDMORE);
zmq_send (socket, "World", 5, 0);
```

### Receiving Multipart Messages

**Python:**
```python
# Receive multipart message
parts = []
while True:
    part = socket.recv()
    parts.append(part)
    if not socket.getsockopt(zmq.RCVMORE):
        break

print(f"Received {len(parts)} parts")
for i, part in enumerate(parts):
    print(f"Part {i}: {part}")
```

**C:**
```c
// Receive multipart message
char buffer [10];
int more;
size_t size;

do {
    size = zmq_recv (socket, buffer, 10, 0);
    // Process buffer...
    
    size = sizeof (more);
    zmq_getsockopt (socket, ZMQ_RCVMORE, &more, &size);
} while (more);
```

## Key Takeaways

1. **ZeroMQ provides socket-like API** but with advanced messaging patterns
2. **Request-reply is the simplest pattern** - REQ/REP sockets
3. **Pub-sub enables broadcasting** - PUB sends, SUB receives with filtering
4. **Messages are byte arrays** - handle strings carefully in each language
5. **Server binds, client connects** - follow this pattern consistently
6. **Close sockets properly** - use cleanup patterns for resources
7. **Multipart messages enable protocols** - frame-based message structure

## Next Steps

- [Sockets and Patterns](02-sockets-patterns.md) - Complete socket API reference
- [Advanced Request-Reply](04-advanced-request-reply.md) - DEALER/ROUTER patterns
- [Reliable Messaging](05-reliable-request-reply.md) - Fault tolerance patterns
- [Advanced Pub-Sub](03-advanced-pubsub.md) - Last value cache, subscriber management
