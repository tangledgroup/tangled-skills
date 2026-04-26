# Serialization and Message Handling

## Builtin Serialization

PyZMQ provides convenience methods for JSON and pickle serialization directly on sockets. These are meant for convenience and demonstration — applications should usually define their own serialization for performance and safety.

### JSON

```python
sock.send_json({"key": "value"})
data = sock.recv_json()
```

`send_json()` serializes with `json.dumps()` and sends as UTF-8 encoded bytes. `recv_json()` receives bytes, decodes UTF-8, and deserializes with `json.loads()`.

### Pickle (use with caution)

```python
sock.send_pyobj(obj)
data = sock.recv_pyobj()
```

**Warning:** `recv_pyobj` grants the message sender arbitrary code execution on the receiver. Never use it on sockets that might receive messages from untrusted sources. Enable CURVE security or authenticate messages before deserializing.

### String Messages

```python
sock.send_string("hello", encoding="utf-8")
text = sock.recv_string(encoding="utf-8")
```

`send_string()` encodes the string to bytes (UTF-8 by default) before sending. `recv_string()` decodes received bytes back to a string.

## Custom Serialization with send_serialized / recv_serialized

For custom serialization, use `send_serialized()` and `recv_serialized()`:

```python
def my_serialize(obj) -> list[bytes]:
    return [msgpack.packb(obj)]

def my_deserialize(frames: list[bytes]) -> object:
    return msgpack.unpackb(frames[0], raw=False)

sock.send_serialized(my_obj, serialize=my_serialize)
data = sock.recv_serialized(my_deserialize)
```

The serialize function takes an object and returns a list of bytes (for multipart messages). The deserialize function takes a list of bytes frames and returns the reconstructed object.

## Multipart Messages

ZeroMQ messages consist of one or more "Frames" of bytes. Multipart messages preserve atomicity — all frames arrive together or not at all.

### Manual Multipart with SNDMORE

```python
sock.send(b"header", zmq.SNDMORE)
sock.send(b"body")
```

### Using send_multipart / recv_multipart

```python
sock.send_multipart([b"header", b"body"])
frames = sock.recv_multipart()  # [b"header", b"body"]
```

This is equivalent to:

```python
def json_dump_bytes(msg) -> list[bytes]:
    return [json.dumps(msg).encode("utf8")]

def json_load_bytes(frames: list[bytes]):
    return json.loads(frames[0].decode("utf8"))

sock.send_multipart(json_dump_bytes(msg))
data = json_load_bytes(sock.recv_multipart())
```

## Zero-Copy Sends

Objects implementing the Python buffer interface (NumPy arrays, `bytearray`, `memoryview`) can be sent without copying:

```python
import numpy as np

arr = np.zeros(1000000, dtype=np.float64)
sock.send(arr, copy=False)
```

**Copy threshold:** By default (64KB), messages below the `copy_threshold` are always copied because zero-copy overhead exceeds the benefit for small buffers. Set `sock.copy_threshold` or `zmq.COPY_THRESHOLD` to adjust.

## MessageTracker

When sending with `track=True`, a `MessageTracker` is returned to know when ZeroMQ has finished with the buffer:

```python
tracker = sock.send(large_buffer, copy=False, track=True)
if tracker:
    tracker.wait()  # block until sent
# now safe to modify large_buffer
```

The `MessageTracker.done` property is `True` when tracked frames are no longer in use by ØMQ. Tracking involves threadsafe communication (a `Queue`), so it has a modest overhead (~10s of µs per message).

**Note:** A Frame cannot be tracked after instantiation without tracking — it must be constructed with `track=True` from the start.

## Example: Signed and Compressed Pickle

Send compressed pickles with HMAC authentication to prevent arbitrary code execution:

```python
import hashlib
import hmac
import pickle
import zlib

def sign(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, digestmod=hashlib.sha256).digest()

def send_signed_zipped_pickle(socket, obj, flags=0, *, key, protocol=pickle.HIGHEST_PROTOCOL):
    p = pickle.dumps(obj, protocol)
    z = zlib.compress(p)
    signature = sign(key, z)
    return socket.send_multipart([signature, z], flags=flags)

def recv_signed_zipped_pickle(socket, flags=0, *, key):
    sig, z = socket.recv_multipart(flags)
    correct_sig = sign(key, z)
    if not hmac.compare_digest(sig, correct_sig):
        raise ValueError("invalid signature")
    p = zlib.decompress(z)
    return pickle.loads(p)
```

## Example: NumPy Arrays

Send NumPy arrays with zero-copy using multipart messages to carry dtype/shape metadata:

```python
import numpy as np

def send_array(socket, A: np.ndarray, flags=0, **kwargs):
    """Send a numpy array with metadata."""
    md = dict(dtype=str(A.dtype), shape=A.shape)
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, **kwargs)  # zero-copy

def recv_array(socket, flags=0, **kwargs) -> np.ndarray:
    """Receive a numpy array."""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, **kwargs)
    A = np.frombuffer(msg, dtype=md["dtype"])
    return A.reshape(md["shape"])
```

The metadata header is sent as JSON in the first frame, and the array data follows as a zero-copy buffer in the second frame.

## recv_into

Added in pyzmq 26.4. Receive directly into a pre-allocated buffer:

```python
buf = bytearray(4096)
n = sock.recv_into(buf)
# buf[:n] contains the received data
```

This avoids allocating a new bytes object for each receive, useful in high-throughput scenarios.
