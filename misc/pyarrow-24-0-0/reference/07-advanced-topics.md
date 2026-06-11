# Advanced Topics

## Contents

- Arrow Flight RPC
- Extension Types
- CUDA Integration
- C++ / Cython Interop
- Environment Variables

## Arrow Flight RPC

Arrow Flight is an RPC framework built on gRPC for high-performance data transfer over the network. Import via `pyarrow.flight`.

### Server

```python
import pyarrow.flight as flight
import pyarrow as pa

class MyFlightServer(flight.FlightServerBase):
    def list_flights(self, context, criteria):
        # Return available flights (datasets)
        info = flight.FlightInfo(...)
        yield info

    def do_get(self, context, ticket):
        # Serve data for a ticket
        table = pa.table({"x": [1, 2, 3]})
        with flight.RecordBatchWriter() as writer:
            yield flight.Result(table.to_batches())

# Start server
server = MyFlightServer("grpc://0.0.0.0:50051")
print(f"Listening on port {server.port}")
server.serve()  # Blocks until server stops
```

### Client

```python
# Connect to server
client = flight.connect("grpc://localhost:50051")

# List available flights
for flight_info in client.list_flights():
    print(flight_info)

# Download data
ticket = flight.Ticket(b"my-ticket")
reader = client.do_get(ticket)
table = reader.read_pandas()  # or reader.to_table()

# Upload data
info = flight.FlightInfo(...)
writer, _ = client.do_put(info)
writer.write_table(table)
writer.close()
```

### Options

```python
# Call with timeout and custom headers
options = flight.FlightCallOptions(
    timeout=30.0,  # seconds
    headers=[("X-Custom-Header", "value")],
)
reader = client.do_get(ticket, options=options)

# Cancel in-flight call
reader.cancel()

# Server-side cancellation check
if context.is_cancelled():
    break  # Stop processing
```

### TLS

```python
# Server with TLS
server = MyFlightServer("grpc+tls://0.0.0.0:50051",
    tls_cert_chain=cert_bytes,
    tls_private_key=key_bytes)

# Client with TLS
client = flight.connect(flight.Location.for_grpc_tls("localhost", 50051))
```

### Authentication

Flight supports user/password authentication via `FlightServerBase.authenticate()` and client-side `flight.ClientMiddleware`.

## Extension Types

Extension types allow custom data types that wrap existing Arrow types with custom Python semantics.

```python
import pyarrow as pa

class MyExtensionType(pa.ExtensionType):
    def __init__(self, storage):
        super().__init__(storage, "my.org/my-extension")

    def __arrow_ext_serialize__(self):
        return b""  # Serialize metadata for cross-process sharing

    @classmethod
    def __arrow_ext_deserialize__(cls, storage, payload):
        return cls(storage)

# Register the extension type
pa.register_extension_type(MyExtensionType(pa.int64()))

# Use in arrays
ext_arr = pa.ExtensionArray(MyExtensionType(pa.int64()), pa.array([1, 2, 3]))
```

UUID is a common built-in extension type example. Extension types preserve their identity through IPC serialization when registered on both ends.

## CUDA Integration

PyArrow supports GPU-accelerated operations via the `pyarrow.cuda` module (requires CUDA-enabled build).

```python
import pyarrow as pa
import pyarrow.cuda

# Transfer array to GPU
gpu_arr = pa.cuda.Buffer.from_host(pa.py_buffer(data))

# GPU memory pool
pool = pa.cuda.memory_pool()

# Zero-copy between CPU and GPU arrays
cpu_arr = pa.array([1, 2, 3])
# Use CUDA-specific operations via pyarrow.cuda module
```

CUDA integration requires PyArrow built with `-DARROW_CUDA=ON`. See the [CUDA Integration](https://arrow.apache.org/docs/python/integration/cuda.html) documentation for setup details.

## C++ / Cython Interop

PyArrow can be extended from C++ or Cython code for performance-critical operations.

### Cython

```cython
# mymodule.pyx
from libcpp.memory cimport shared_ptr
from pyarrow.lib cimport Array, Table, Schema
from pyarrow.lib cimport pyarrow_array_from_buffers

def process_table(table: Table):
    cdef shared_ptr[Array] arr = table.column(0).chunk(0)
    # Access C++ Arrow types directly
    ...
```

Build with `setup.py` using `Cython` and linking against Arrow C++ libraries.

### C Data Interface

The Arrow C Data Interface enables zero-copy data exchange between PyArrow and other native libraries:

```python
# Export from PyArrow
arr = pa.array([1, 2, 3])
# Access __arrow_c_array__ protocol for C interop
capsule = arr.__arrow_c_array__()
```

See the [C Data Interface](https://arrow.apache.org/docs/python/integration/extending.html) documentation for full details.

## Environment Variables

PyArrow behavior can be tuned via environment variables:

| Variable | Purpose |
|---|---|
| `ARROW_DEFAULT_MEMORY_POOL` | Memory pool backend (`mimalloc`, `jemalloc`, `system`) |
| `ARROW_IO_THREADS` | Number of threads for parallel I/O |
| `ARROW_DEBUG` | Enable debug logging |
| `ARROW_LOG_LEVEL` | Log verbosity (`info`, `warning`, `error`, `debug`) |
| `AWS_REGION` / `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 credentials |
| `PYARROW_IGNORE_TIMEZONE` | Ignore timezone mismatches in timestamp conversion |

See the [Environment Variables](https://arrow.apache.org/docs/python/env_vars.html) documentation for the complete list.
