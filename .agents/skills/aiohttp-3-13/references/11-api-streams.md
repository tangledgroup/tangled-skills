# API: Streams

Complete reference for aiohttp streaming API including StreamReader and StreamWriter.

## StreamReader

Read data from incoming streams (request bodies, response bodies).

### Accessing StreamReader

```python
# From client response
async with session.get(url) as resp:
    stream = resp.content  # StreamReader
    
# From server request
async def handler(request):
    stream = request.content  # StreamReader
```

### Reading Methods

#### read(n)

Read up to n bytes:

```python
async def read_data(stream):
    # Read all data
    data = await stream.read()
    
    # Read up to 1024 bytes
    chunk = await stream.read(1024)
    
    # Read exactly until EOF
    all_data = await stream.read(-1)
```

#### readany()

Read next available data portion:

```python
async def read_available(stream):
    # Returns immediately if data is in buffer
    data = await stream.readany()
    
    while data:
        process(data)
        data = await stream.readany()
```

#### readexactly(n)

Read exactly n bytes (raises on EOF):

```python
from asyncio import IncompleteReadError

async def read_header(stream):
    try:
        # Read exactly 4 bytes for length prefix
        length_data = await stream.readexactly(4)
        length = int.from_bytes(length_data, 'big')
        
        # Read exact amount
        payload = await stream.readexactly(length)
        
    except IncompleteReadError as e:
        partial = e.partial  # Get partially read data
        raise
```

#### readline()

Read until newline:

```python
async def read_lines(stream):
    while True:
        line = await stream.readline()
        if not line:
            break
        print(line.decode().strip())
```

#### readchunk()

Read next chunk with metadata:

```python
async def read_chunks(stream):
    while True:
        chunk, eof = await stream.readchunk()
        if eof:
            break
        process(chunk)
```

### Iteration Methods

#### iter_chunked(size)

Iterate over chunks of specified size:

```python
async def process_large_response(stream):
    async for chunk in stream.iter_chunked(8192):
        # Process 8KB chunks
        write_to_file(chunk)
```

#### iter_any()

Iterate over all available data:

```python
async def process_as_available(stream):
    async for chunk in stream.iter_any():
        # Process each chunk as it arrives
        handle_chunk(chunk)
```

#### iter_lines()

Iterate over lines:

```python
async def process_lines(stream):
    async for line in stream.iter_lines():
        print(line.decode())
```

### Utility Methods

#### any_wait_eof()

Wait until EOF is reached:

```python
async def wait_for_completion(stream):
    await stream.any_wait_eof()
    print("Stream completed")
```

#### at_eof()

Check if at end of stream:

```python
async def check_stream(stream):
    if await stream.at_eof():
        print("No more data")
    else:
        data = await stream.readany()
```

#### feed_data(data)

Feed data into stream (for testing):

```python
# Typically used internally or in tests
stream.feed_data(b'hello')
stream.feed_data(b' world')
data = await stream.read()  # b'hello world'
```

#### feed_eof()

Signal end of stream:

```python
stream.feed_data(b'final data')
stream.feed_eof()

# Now read() will return remaining data then empty bytes
```

### Stream Properties

- `total_bytes` - Total bytes received
- `exception()` - Get exception if stream errored
- `set_exception(exc)` - Set exception on stream

## StreamWriter

Write data to outgoing streams.

### Basic Usage

```python
from aiohttp import web

async def streaming_handler(request):
    response = web.StreamResponse(
        status=200,
        headers={'Content-Type': 'text/plain'}
    )
    await response.prepare(request)
    
    async with response.writer() as writer:
        for i in range(100):
            await writer.write(f"{i}\n".encode())
            await asyncio.sleep(0.1)
    
    return response
```

### Write Methods

#### write(data)

Write bytes to stream:

```python
async def write_data(writer):
    await writer.write(b'Hello')
    await writer.write(b' ')
    await writer.write(b'World')
```

#### writelines(lines)

Write multiple lines at once:

```python
async def write_lines(writer):
    lines = [b'Line 1\n', b'Line 2\n', b'Line 3\n']
    await writer.writelines(lines)
```

### Drain and Flush

#### drain()

Wait until data is written:

```python
async def ensure_written(writer):
    await writer.write(b'Important data')
    await writer.drain()  # Wait for write to complete
```

#### flush()

Flush stream buffer:

```python
async def flush_output(writer):
    await writer.write(b'Real-time data')
    await writer.flush()  # Send immediately
```

### Chunked Transfer Encoding

```python
async def chunked_response(request):
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'application/octet-stream',
            'Transfer-Encoding': 'chunked'
        }
    )
    await response.prepare(request)
    
    async with response.writer() as writer:
        for chunk in generate_chunks():
            await writer.write(chunk)
    
    return response
```

## Streaming Large Files

### Client: Download in Chunks

```python
async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(path, 'wb') as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total:
                        progress = downloaded / total * 100
                        print(f"Download: {progress:.1f}%")
```

### Server: Stream File Upload

```python
async def upload_handler(request):
    # Get content length
    length = request.content_length or 0
    
    with open('upload.bin', 'wb') as f:
        written = 0
        async for chunk in request.content.iter_chunked(8192):
            f.write(chunk)
            written += len(chunk)
            
            # Could emit progress via WebSocket here
    
    return web.json_response({
        'status': 'success',
        'size': written
    })
```

## Real-time Streaming

### Server-Sent Events (SSE)

```python
async def sse_handler(request):
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
    await response.prepare(request)
    
    try:
        for i in range(100):
            # SSE format
            event = f"data: {{\"value\": {i}}}\n\n".encode()
            await response.write(event)
            await response.drain()
            await asyncio.sleep(1)
        
        # Send completion
        await response.write(b"data: [DONE]\n\n")
        
    except ConnectionResetError:
        # Client disconnected
        pass
    finally:
        await response.write_eof()
    
    return response
```

### Progressive Data Streaming

```python
async def progressive_search(request):
    query = request.query.get('q', '')
    
    response = web.StreamResponse(
        status=200,
        headers={'Content-Type': 'application/json'}
    )
    await response.prepare(request)
    
    async with response.writer() as writer:
        # Stream results as they're found
        async for result in search_generator(query):
            data = json.dumps(result).encode()
            await writer.write(data + b'\n')
            await writer.drain()
    
    return response
```

## Binary Streaming

### Reading Binary Data

```python
async def read_binary_stream(stream):
    # Read binary header
    header = await stream.readexactly(8)
    magic = header[:4]
    length = int.from_bytes(header[4:], 'big')
    
    # Read payload
    payload = await stream.readexactly(length)
    
    return magic, payload
```

### Writing Binary Data

```python
async def write_binary_stream(writer):
    # Write length-prefixed data
    data = b'Binary content here'
    
    # Write length (4 bytes, big-endian)
    length = len(data).to_bytes(4, 'big')
    await writer.write(length)
    
    # Write data
    await writer.write(data)
```

## Error Handling with Streams

### Timeout Handling

```python
async def read_with_timeout(stream):
    try:
        data = await asyncio.wait_for(
            stream.read(1024),
            timeout=5.0
        )
        return data
    except asyncio.TimeoutError:
        print("Read timed out")
        raise
```

### Incomplete Read Handling

```python
from asyncio import IncompleteReadError

async def safe_read(stream, expected_length):
    try:
        data = await stream.readexactly(expected_length)
        return data
    except IncompleteReadError as e:
        # Handle partial read
        partial = e.partial
        print(f"Only received {len(partial)} of {expected_length} bytes")
        return partial
```

### Connection Lost Handling

```python
async def robust_stream_read(stream):
    try:
        async for chunk in stream.iter_chunked(8192):
            if not chunk:
                break
            process(chunk)
            
    except aiohttp.ServerDisconnectedError:
        print("Client disconnected")
    except ConnectionResetError:
        print("Connection reset")
```

## Stream Examples

### HTTP Proxy Streaming

```python
async def proxy_handler(request):
    target_url = request.query.get('url')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(target_url) as resp:
            # Create streaming response
            response = web.StreamResponse(
                status=resp.status,
                headers=dict(resp.headers)
            )
            await response.prepare(request)
            
            # Stream from upstream to client
            async for chunk in resp.content.iter_chunked(8192):
                await response.write(chunk)
                await response.drain()
            
            return response
```

### Video Streaming

```python
async def video_stream(request):
    video_path = request.match_info['video_id']
    
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'video/mp4',
            'Accept-Ranges': 'bytes'
        }
    )
    await response.prepare(request)
    
    # Handle range requests
    range_header = request.headers.get('Range')
    start, end = parse_range(range_header) if range_header else (0, None)
    
    with open(video_path, 'rb') as f:
        f.seek(start)
        
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            
            if end and f.tell() >= end:
                break
                
            await response.write(chunk)
            await response.drain()
    
    return response
```
