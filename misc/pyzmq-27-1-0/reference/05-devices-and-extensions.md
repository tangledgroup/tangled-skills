# Devices, Proxies, and Extensions

## zmq.devices — Background Devices

Devices run ZeroMQ messaging patterns in background threads or processes. Unlike `zmq.proxy()` which takes existing Socket instances, the `Device` classes create sockets internally in the work thread (avoiding thread-safety issues).

### Device Classes

- **`Device`** — base class
- **`ThreadDevice`** — runs in a background thread (default daemon=True)
- **`ProcessDevice`** — runs in a background process

```python
from zmq.devices import ThreadDevice

dev = ThreadDevice(zmq.QUEUE, zmq.DEALER, zmq.ROUTER)
dev.bind_in("tcp://*:5555")
dev.bind_out("tcp://*:5556")
dev.start()
```

Configuration methods:
- `bind_in(addr)` / `bind_out(addr)` — bind sockets to addresses
- `bind_in_to_random_port(addr)` / `bind_out_to_random_port(addr)` — random port binding
- `connect_in(addr)` / `connect_out(addr)` — connect to remote addresses
- `setsockopt_in(opt, value)` / `setsockopt_out(opt, value)` — set socket options
- `start()` — start the device
- `join(timeout=None)` — wait for device to finish

### Proxy Devices

Proxy devices include a monitor socket (default PUB) that broadcasts all forwarded messages:

- **`Proxy`** / **`ThreadProxy`** / **`ProcessProxy`** — 3-socket proxy with monitoring
- **`ProxySteerable`** / **`ThreadProxySteerable`** / **`ProcessProxySteerable`** — steerable proxy with PAUSE/RESUME/TERMINATE control

```python
from zmq.devices import ThreadProxy

proxy = ThreadProxy(zmq.FORWARDER, zmq.PUB, zmq.SUB)
proxy.bind_in("tcp://*:5557")
proxy.bind_out("tcp://*:5558")
proxy.bind_mon("tcp://*:5559")  # monitor socket
proxy.start()
```

### Steerable Proxy

Added in pyzmq 18.0 (libzmq 4.1+). Send control messages to pause, resume, or terminate:

```python
from zmq.devices import ThreadProxySteerable

proxy = ThreadProxySteerable(zmq.FORWARDER, zmq.PUB, zmq.SUB)
proxy.bind_in("tcp://*:5557")
proxy.bind_out("tcp://*:5558")
proxy.bind_ctrl("tcp://*:5560")  # control socket
proxy.start()

# Control the proxy
ctrl = ctx.socket(zmq.REQ)
ctrl.connect("tcp://localhost:5560")
ctrl.send(b"PAUSE")    # suspend forwarding
ctrl.send(b"RESUME")   # resume forwarding
ctrl.send(b"TERMINATE")  # graceful shutdown
```

## zmq.proxy Functions

For simple inline proxy usage (not background threads):

```python
# Basic proxy — forwards messages between frontend and backend
zmq.proxy(frontend_socket, backend_socket)

# With capture socket — also sends messages to capture
zmq.proxy(frontend, backend, capture=monitor_socket)

# Steerable proxy (libzmq 4.1+)
zmq.proxy_steerable(frontend, backend, capture=monitor, control=ctrl_socket)
```

The `zmq.device()` function is deprecated since libzmq 3.2 / pyzmq 13.0 — use `zmq.proxy()` instead.

## zmq.log.handlers — Logging Over ZeroMQ

`PUBHandler` publishes Python logging messages over a PUB socket:

```python
import logging
from zmq.log.handlers import PUBHandler

handler = PUBHandler("tcp://127.0.0.1:12345")
handler.root_topic = "app"
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Log messages are broadcast with topics:
# root_topic + log_level + subtopics
logger.debug("subtopic::message details")
```

Or pass a pre-bound PUB socket:

```python
sock = ctx.socket(zmq.PUB)
sock.bind("inproc://log")
handler = PUBHandler(sock)
```

With `dictConfig`:

```python
from logging.config import dictConfig

socket = zmq.Context.instance().socket(zmq.PUB)
socket.connect("tcp://127.0.0.1:12345")
dictConfig({
    "version": 1,
    "handlers": {
        "zmq": {
            "class": "zmq.log.handlers.PUBHandler",
            "level": logging.DEBUG,
            "root_topic": "app",
            "interface_or_socket": socket,
        }
    },
    "root": {"level": "DEBUG", "handlers": ["zmq"]},
})
```

## zmq.ssh.tunnel — SSH Tunneling

Tunnel ZeroMQ connections over SSH for secure cross-machine communication:

```python
from zmq import ssh

# Tunnel a socket connection through an SSH server
ssh.tunnel_connection(sock, "tcp://10.0.1.2:5555", "server")
```

The `tunnel_connection()` function forwards a random localhost port to the real destination and connects the socket to the local URL. The SSH server can be specified as `"user@server:port"`. All SSH configuration (usernames, aliases, keys) is respected.

For connecting to a service only listening on localhost on a remote machine:

```python
ssh.tunnel_connection(sock, "tcp://127.0.0.1:5555", "10.0.1.2")
```

PyZMQ uses `pexpect` by default for SSH tunnels, with `paramiko` as a fallback (for Windows support).

## zmq.decorators — Decorator Syntax

Added in pyzmq 15.3. Use decorators instead of context managers for function-scoped contexts and sockets:

```python
from zmq.decorators import context, socket

@context()
@socket(zmq.PUSH)
def work(ctx, push):
    push.connect("tcp://server:5555")
    push.send(b"hello")

work()  # context and socket are created and cleaned up automatically
```

The `name` parameter controls the keyword argument name passed to the decorated function.

## zmq.utils — Utility Modules

- **`zmq.utils.jsonapi`** — JSON serialization utilities
- **`zmq.utils.monitor`** — Socket event monitoring (wrapper around `get_monitor_socket`)
- **`zmq.utils.z85`** — Z85 (ZeroMQ Base-85) encoding/decoding for binary data
- **`zmq.utils.win32`** — Windows-specific utilities

## zmq.green — gevent Compatibility

Import as `zmq.green` instead of `zmq` for gevent-compatible sockets:

```python
import zmq.green as zmq
```

All blocking operations become greenlet-aware, yielding to other greenlets instead of blocking the thread.
