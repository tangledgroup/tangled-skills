# Basics

## Hello World Request-Reply

The fundamental ZeroMQ pattern: a client sends "Hello" to a server, which replies with "World".

**Server (C):**
```c
#include <zmq.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

int main (void)
{
    void *context = zmq_ctx_new ();
    void *responder = zmq_socket (context, ZMQ_REP);
    int rc = zmq_bind (responder, "tcp://*:5555");
    assert (rc == 0);

    while (1) {
        char buffer [10];
        zmq_recv (responder, buffer, 10, 0);
        printf ("Received Hello\n");
        sleep (1);          //  Pretend to do some work
        zmq_send (responder, "World", 5, 0);
    }
    return 0;
}
```

**Client (C):**
```c
#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>

int main (void)
{
    void *context = zmq_ctx_new ();
    void *requester = zmq_socket (context, ZMQ_REQ);
    zmq_connect (requester, "tcp://localhost:5555");

    int request_nbr;
    for (request_nbr = 0; request_nbr != 10; request_nbr++) {
        char buffer [10];
        printf ("Sending Hello %d...\n", request_nbr);
        zmq_send (requester, "Hello", 5, 0);
        zmq_recv (requester, buffer, 10, 0);
        printf ("Received World %d\n", request_nbr);
    }
    zmq_close (requester);
    zmq_ctx_destroy (context);
    return 0;
}
```

**Client (Python):**
```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

for request in range(10):
    socket.send(b"Hello")
    message = socket.recv()
    print(f"Received {message}")
```

**Client (C++):**
```cpp
#include <zmq.hpp>
#include <string>
#include <iostream>

int main () {
    zmq::context_t context (1);
    zmq::socket_t requester (context, ZMQ_REQ);
    requester.connect ("tcp://localhost:5555");

    for (int request_nbr = 0; request_nbr != 10; request_nbr++) {
        std::cout << "Sending Hello " << request_nbr << std::endl;
        zmq::message_t request (5);
        memcpy (request.data (), "Hello", 5);
        requester.send (request);

        zmq::message_t reply;
        requester.recv (&reply);
        std::cout << "Received World "
                  << std::string (static_cast<char*>(reply.data()), reply.size())
                  << std::endl;
    }
    return 0;
}
```

## A Note on Strings

ZeroMQ does not know about strings. It sends and receives frames of bytes, which may or may not hold text. If you want to send text, use zero-terminated strings and always allow one extra byte in the receiving buffer for the terminator.

## Task Distribution (Parallel Pipeline)

The parallel pipeline pattern distributes tasks from a ventilator to multiple workers via a task queue (fair queuer), and collects results through a separate pipeline.

**Ventilator (C):**
```c
#include "zhelpers.h"
#include <stdio.h>
#include <stdlib.h>

int main (void)
{
    void *context = zmq_ctx_new ();
    void *sender = zmq_socket (context, ZMQ_PUSH);
    zmq_bind (sender, "tcp://*:5555");

    printf ("Press Enter when the workers are ready: ");
    getchar ();
    printf ("Sending tasks to workers...\n");

    //  The first message is "0" and acts as a start signal
    zmq_send (sender, "0", 1, 0);

    int total_msec = 0;
    for (int task_nbr = 0; task_nbr < 100; task_nbr++) {
        int workload;
        workload = randof (100) + 1;
        total_msec += workload;
        char string [10];
        sprintf (string, "%d", workload);
        zmq_send (sender, string, strlen(string), 0);
    }
    printf ("Total expected cost: %d msec\n", total_msec);

    zmq_close (sender);
    zmq_ctx_destroy (context);
    return 0;
}
```

**Worker (C):**
```c
#include "zhelpers.h"
#include <stdio.h>

int main (void)
{
    void *context = zmq_ctx_new ();
    void *receiver = zmq_socket (context, ZMQ_PULL);
    zmq_connect (receiver, "tcp://localhost:5555");

    while (1) {
        char *string = s_recv (receiver);
        if (!string) break;
        int workload = atoi (string);
        s_sleep (workload);
        free (string);
    }
    zmq_close (receiver);
    zmq_ctx_destroy (context);
    return 0;
}
```

Workers connect to the ventilator's PUSH socket. ZeroMQ fair-queues incoming messages so each worker gets roughly equal work.

## Getting the Context Right

The context is the most important object in ZeroMQ. It sits between your application and the underlying I/O threads. Every context has one or more background I/O threads. The general rule of thumb: allow one I/O thread per gigabyte of data in or out per second.

```c
int io_threads = 4;
void *context = zmq_ctx_new ();
zmq_ctx_set (context, ZMQ_IO_THREADS, io_threads);
assert (zmq_ctx_get (context, ZMQ_IO_THREADS) == io_threads);
```

## Making a Clean Exit

To shut down cleanly:
```c
zmq_close (socket);      //  Close all sockets first
zmq_ctx_destroy (context);  //  Then destroy the context
```

When you destroy the context, it closes any remaining open sockets. Setting `ZMQ_LINGER` to 0 on a socket before closing it means ZeroMQ will not wait for pending messages:

```c
int linger = 0;
zmq_setsockopt (socket, ZMQ_LINGER, &linger, sizeof (linger));
zmq_close (socket);
```

## Version Reporting

Check the ZeroMQ version at runtime:
```c
int major, minor, patch;
zmq_version (&major, &minor, &patch);
printf ("Current ZeroMQ version is %d.%d.%d\n", major, minor, patch);
```

## Key Differences from TCP Sockets

- ZeroMQ sockets carry **messages** (length-specified binary data), not byte streams
- I/O happens in **background threads** — messages arrive in local queues
- Sockets have **one-to-N routing** built-in according to socket type
- `zmq_send()` **queues** the message for async delivery — it does not block (except in exception cases)
- ZeroMQ **automatically reconnects** peers as they come and go
- No `zmq_accept()` — bound sockets automatically accept connections

## Upgrading from ZeroMQ 2.2 to 3.2

Key incompatible changes:
- `zmq_init()` replaced by `zmq_ctx_new()`
- `zmq_term()` replaced by `zmq_ctx_destroy()`
- Security model changed: ZAP (ZeroMQ Authentication Protocol) replaces the old security API
- Identity mechanism changed from UUID to random 5-byte identity
- New socket types: XPUB, XSUB, STREAM

## Getting the Examples

```bash
git clone --depth=1 https://github.com/imatix/zguide.git
```

Examples are organized by language in the `examples/` subdirectory. All examples are licensed under MIT/X11.
