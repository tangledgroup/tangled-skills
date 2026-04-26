# Draft APIs and Advanced Configuration

## DRAFT Socket Types

libzmq 4.2+ introduced unstable DRAFT APIs including new socket types. These are not supported in pre-built wheels and require compiling pyzmq from source with draft support enabled.

### Building with Draft Support

1. Build libzmq with drafts enabled:

```bash
./configure --prefix=/usr/local --enable-drafts
make -j && make install
sudo ldconfig
```

2. Build pyzmq with draft flag:

```bash
export ZMQ_PREFIX=/usr/local
export ZMQ_DRAFT_API=1
export LDFLAGS="${LDFLAGS:-} -Wl,-rpath,$ZMQ_PREFIX/lib"
pip install -v pyzmq --no-binary pyzmq
```

The `--no-binary` flag forces compilation from source. `ZMQ_PREFIX` is only needed if libzmq is installed outside default search paths.

### DRAFT Socket Types

- **CLIENT / SERVER** — Scalable request-reply pattern (alternative to REQ/REP)
- **RADIO / DISH** — Scalable publish-subscribe with automatic subscriber tracking (alternative to PUB/SUB)
- **GATHER / SCATTER** — Scalable pipeline pattern
- **SURVEYOR / RESPONDENT** — Survey pattern

### Checking Draft Availability

In pyzmq 27.1.0, `zmq.DRAFT_API` was restored to represent actual availability — both libzmq and pyzmq must be built with drafts enabled:

```python
if zmq.DRAFT_API:
    client = ctx.socket(zmq.CLIENT)
```

In pyzmq 23–27.0, `zmq.DRAFT_API` was a synonym for `zmq.has("draft")`, which only checked libzmq.

## Context Shadowing

Added in pyzmq 25. Shadow an existing Context to create a sync/async view of the same underlying libzmq context:

```python
# Shadow another Context
async_ctx = zmq.asyncio.Context(sync_ctx)

# Or using the classmethod
ctx2 = zmq.Context.shadow(ctx1)
```

This is useful for mixing sync and async code that shares the same ZeroMQ resources.

## Socket Shadowing

Similarly, sockets can be shadowed:

```python
sync_sock = zmq.Socket(async_sock)
async_sock = zmq.asyncio.Socket(sync_sock)
```

## Random Port Binding

Bind to a random available port within a range:

```python
port = sock.bind_to_random_port(
    "tcp://127.0.0.1",
    min_port=49152,
    max_port=65536,
    max_tries=100
)
print(f"Bound to port {port}")
```

Raises `zmq.ZMQBindError` if `max_tries` is reached without success.

## Socket Monitoring

Get a PAIR socket that receives socket events:

```python
mon_sock = sock.get_monitor_socket(
    events=zmq.EVENT_ALL,
    addr=None  # default: inproc
)

# Monitor socket receives [event_value, event_string] multipart messages
event_val, event_str = mon_sock.recv_multipart()
```

Events include: `CONNECTED`, `CONNECT_DELAYED`, `CONNECT_RETRIED`, `LISTENING`, `BIND_FAILED`, `ACCEPTED`, `ACCEPT_FAILED`, `CLOSED`, `CLOSE_FAILED`, `DISCONNECTED`, `HANDSHAKE_OK`, `HANDSHAKE_FAILED`, `HANDSHAKE_FAILED_NO_DETAIL`, `HANDSHAKE_FAILED_PROTOCOL`, `HANDSHAKE_FAILED_AUTH`.

Disable monitoring with `sock.disable_monitor()`.

## Context Options

Set context-wide options:

```python
ctx = zmq.Context(io_threads=4)
ctx.set(zmq.IO_THREADS, 4)
ctx.set(zmq.MAX_SOCKETS, 1024)
io_threads = ctx.get(zmq.IO_THREADS)
```

Available options depend on libzmq version. Common options:
- `zmq.IO_THREADS` — number of I/O threads
- `zmq.MAX_SOCKETS` — maximum number of sockets

Default socket options can be set on the Context:

```python
ctx.setsockopt(zmq.LINGER, 0)
# all new sockets from this context inherit linger=0
```

## libzmq Constants as Enums

Added in pyzmq 23. libzmq constants are available as Python enums:

```python
from zmq import SocketType, EventLoop
for st in SocketType:
    print(st.name, st.value)
```

## Platform Support

### Python Versions

- CPython ≥ 3.9 (including free-threaded 3.14t)
- PyPy via CFFI backend

### libzmq Versions

- libzmq ≥ 3.2.2 (stable), including 4.x
- Binary wheels ship with libzmq 4.3.5 + libsodium (CURVE support)
- libzmq 3.0–3.1 are not supported (no stable release)

### Wheel Platforms

- Linux: musllinux_1_2 (Alpine 3.13+), manylinux glibc 2.28+
- macOS, Windows (including ARM64)
- Android wheels added in 27.0.1
- CPython 3.12 stable ABI wheel (works with CPython 3.14+)

### Building from Source

```bash
pip install --no-binary=pyzmq pyzmq
```

Requires Cython ≥ 3.0 for the pure-Python mode backend. For PyPy, CFFI is used instead of Cython.

Set `PYZMQ_BACKEND=cffi` to force CFFI backend on CPython (for testing).

## Error Handling

Common pyzmq exceptions:

- **`zmq.Again`** — resource temporarily unavailable (non-blocking operation)
- **`zmq.ContextTerminated`** — context was terminated during blocking operation
- **`zmq.ZMQBindError`** — bind failed
- **`zmq.ZMQError`** — general ZeroMQ error
- **`zmq.ZMQVersionError`** — API version mismatch

```python
import zmq

try:
    msg = sock.recv(zmq.NOBLOCK)
except zmq.Again:
    print("No message available")
except zmq.ContextTerminated:
    print("Context was terminated")
```

## Version Information

Check runtime versions:

```python
import zmq

print(zmq.__version__)          # pyzmq version, e.g. "27.1.0"
print(zmq.zmq_version())        # libzmq version, e.g. "4.3.5"
print(zmq.pyzmq_version())      # full pyzmq version info
```

Check feature availability:

```python
if zmq.has("draft"):
    print("Draft APIs available")
if zmq.has("gssapi"):
    print("GSSAPI authentication available")
```
