# IPC and Memory

## Contents

- IPC Streaming Format
- IPC File Format
- Feather Format
- Buffers
- Memory Pools
- NativeFile I/O
- Compressed Streams

## IPC Streaming Format

Arrow's streaming format sends an arbitrary-length sequence of RecordBatches. Must be processed sequentially — no random access.

```python
import pyarrow as pa

schema = pa.schema([("x", pa.int64()), ("y", pa.string())])
batch = pa.RecordBatch.from_arrays(
    [pa.array([1, 2, 3]), pa.array(["a", "b", "c"])], schema=schema
)

# Write stream to in-memory buffer
sink = pa.BufferOutputStream()
with pa.ipc.new_stream(sink, schema) as writer:
    for _ in range(5):
        writer.write_batch(batch)

buf = sink.getvalue()  # Complete stream as byte buffer

# Read stream back
with pa.ipc.open_stream(buf) as reader:
    print(reader.schema)     # Schema available without reading batches
    batches = [b for b in reader]  # Iterate all batches
```

When the input source supports zero-copy reads (memory map, `BufferReader`), returned batches share memory with no allocation.

## IPC File Format

File format supports random access — seek to any RecordBatch by index.

```python
# Write file
sink = pa.BufferOutputStream()
with pa.ipc.new_file(sink, schema) as writer:
    for _ in range(10):
        writer.write_batch(batch)

buf = sink.getvalue()

# Read with random access
with pa.ipc.open_file(buf) as reader:
    num_batches = reader.num_record_batches  # 10
    b = reader.get_batch(3)                   # Direct access to batch 3

# Read as pandas DataFrame
with pa.ipc.open_file(buf) as reader:
    df = reader.read_pandas()
```

## Feather Format

Feather is the IPC file format with a convenient API. Use `pyarrow.feather`.

```python
import pyarrow.feather as feather

feather.write_feather(table, "data.feather", compression="lz4")
table = feather.read_feather("data.feather", columns=["x", "y"])
```

## Buffers

`pyarrow.Buffer` wraps contiguous memory. All Arrow data is stored in buffers. Buffers are immutable and support zero-copy slicing.

```python
import pyarrow as pa

# From Python bytes (zero-copy view)
buf = pa.py_buffer(b"hello world")
buf.size  # 11

# As memoryview (zero-copy)
mv = memoryview(buf)

# Convert to Python bytes (copies data)
data = buf.to_pybytes()

# Allocate resizable buffer from memory pool
buf = pa.allocate_buffer(1024, resizable=True)
buf.resize(2048)
```

## Memory Pools

All Arrow memory allocations go through a `MemoryPool`. Track and control memory usage.

```python
# Check total allocated memory
pa.total_allocated_bytes()

# Default memory pool
pool = pa.default_memory_pool()
pool.backend_name  # e.g., 'mimalloc', 'jemalloc'

# Host memory pool (system allocator)
host_pool = pa.host_memory_pool()

# Use specific pool in operations
arr = pa.array([1, 2, 3], type=pa.int64(), memory_pool=host_pool)

# Track allocations
buf = pa.allocate_buffer(1024, resizable=True)
pa.total_allocated_bytes()  # includes the 1024 bytes
del buf
pa.total_allocated_bytes()  # freed
```

## NativeFile I/O

`NativeFile` is the base class for Arrow's file-like objects. Preferable to Python file objects as they avoid GIL acquisition and support zero-copy I/O.

### Available Types

| Class | Purpose |
|---|---|
| `OSFile` | OS file descriptors |
| `MemoryMappedFile` | Memory-mapped files (zero-copy reads) |
| `BufferReader` | Read from Buffer as file |
| `BufferOutputStream` | Write to in-memory Buffer |
| `PythonFile` | Wrap Python file objects |
| `CompressedInputStream` | On-the-fly decompression |
| `CompressedOutputStream` | On-the-fly compression |

### High-Level API

```python
# Input stream from various sources
stream = pa.input_stream("data.arrow")        # OSFile
stream = pa.input_stream(buf)                  # BufferReader
stream = pa.input_stream("data.arrow.gz")      # auto-decompress

# Output stream
with pa.output_stream("data.arrow") as stream:
    stream.write(b"some data")

# Write with compression
with pa.CompressedOutputStream("data.arrow.gz", "gzip") as out:
    pq.write_table(table, out)

# Memory-mapped file (zero-copy reads)
mapped = pa.memory_map("large_file.arrow")
reader = pa.ipc.open_file(mapped)
```

### Filesystem Integration

```python
from pyarrow import fs

local = fs.LocalFileSystem()
with local.open_output_stream("test.arrow") as f:
    with pa.RecordBatchFileWriter(f, table.schema) as writer:
        writer.write_table(table)
```

## Compressed Streams

On-the-fly compression/decompression without intermediate files.

```python
# Write compressed
with pa.CompressedOutputStream("data.arrow.zstd", "zstd") as out:
    with pa.ipc.new_file(out, schema) as writer:
        writer.write_batch(batch)

# Read compressed (auto-detected by extension)
stream = pa.input_stream("data.arrow.zstd")
with pa.ipc.open_stream(stream) as reader:
    for batch in reader:
        process(batch)
```

Supported compression codecs: `gzip`, `bz2`, `zstd`, `lz4`, `snappy`.
