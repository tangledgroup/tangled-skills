# Streaming and Multipart

## Streaming API

aiohttp uses streams for retrieving request/response bodies. Both `web.BaseRequest.content` and `ClientResponse.content` are `StreamReader` instances.

### StreamReader Methods

```python
# Read up to n bytes (or all if n=-1)
data = await stream.read(n=-1)

# Read next available chunk
data = await stream.readany()

# Read exactly n bytes (raises IncompleteReadError on EOF)
data = await stream.readexactly(n)

# Read one line (terminated by \n)
line = await stream.readline()

# Read until separator
data = await stream.readuntil(separator=b'\n')

# Read a chunk as received from server
data, end_of_chunk = await stream.readchunk()
```

### Asynchronous Iteration

```python
# Default: iterate over lines
async for line in response.content:
    print(line)

# Iterate over chunks with size limit
async for data in response.content.iter_chunked(1024):
    print(data)

# Iterate over available data in intake order
async for data in response.content.iter_any():
    print(data)

# Iterate over raw HTTP chunks
async for data, end_of_http_chunk in response.content.iter_chunks():
    print(data)
```

### Helper Methods

- `stream.exception()` — Get exception from reading
- `stream.at_eof()` — True if buffer empty and EOF reached
- `stream.read_nowait(n)` — Non-blocking read from buffer
- `stream.unread_data(data)` — Push data back to buffer head
- `await stream.wait_eof()` — Wait for EOF
- `stream.total_raw_bytes` — Total raw bytes downloaded (before decompression)

### Streaming Response to File

```python
with open(filename, 'wb') as fd:
    async for chunk in resp.content.iter_chunked(chunk_size):
        fd.write(chunk)
```

### Streaming Upload

```python
# File-like object (auto-streamed)
with open('massive-body', 'rb') as f:
    await session.post(url, data=f)

# Async generator
async def file_sender(file_name):
    async with aiofiles.open(file_name, 'rb') as f:
        chunk = await f.read(64 * 1024)
        while chunk:
            yield chunk
            chunk = await f.read(64 * 1024)

async with session.post(url, data=file_sender('huge_file')) as resp:
    ...
```

## Multipart

aiohttp supports full-featured multipart reader and writer, designed for streaming processing.

### Reading Multipart Responses

```python
async with aiohttp.request(...) as resp:
    reader = aiohttp.MultipartReader.from_response(resp)

    while True:
        part = await reader.next()
        if part is None:
            break

        # Filter by content type
        if part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'application/json':
            metadata = await part.json()
            continue

        # Check filename
        if part.filename != 'secret.txt':
            continue  # Skipping reads remaining data to void

        # Read raw binary (decode=False)
        filedata = await part.read(decode=False)

        # Decode later if needed
        filedata = part.decode(filedata)
        break
```

Key points:
- `reader.next()` returns `BodyPartReader` for simple parts, or nested `MultipartReader` for nested multipart
- Returns `None` when no more parts remain
- Skipping a part (continuing loop) automatically drains its content
- Multipart format is recursive — supports deeply nested body parts

### BodyPartReader Methods

- `await part.text()` — Read as text (auto-decodes gzip/deflate/base64/quoted-printable)
- `await part.json()` — Parse as JSON
- `await part.form()` — Parse as url-encoded form data
- `await part.read(decode=True)` — Read raw binary
- `await part.read_chunk(size=-1)` — Read in chunks
- `part.decode(data)` — Apply decoding to raw data
- `part.filename` — Extracted filename from Content-Disposition
- `part.headers` — Body part headers

### Writing Multipart Requests

```python
with aiohttp.MultipartWriter('mixed') as mpwriter:
    # Text data (default: text/plain; charset=utf-8)
    mpwriter.append('hello')

    # Binary data (default: application/octet-stream)
    mpwriter.append(b'aiohttp')

    # With custom headers
    mpwriter.append(io.BytesIO(b'GIF89a...'), {'CONTENT-TYPE': 'image/gif'})

    # JSON helper
    mpwriter.append_json({'test': 'passed'})

    # Form data helper
    mpwriter.append_form([('key', 'value')])

    # Nested multipart
    with aiohttp.MultipartWriter('related') as subwriter:
        subwriter.append('nested content')
    mpwriter.append(subwriter)

# Send the multipart writer
await session.post('http://example.com', data=mpwriter)
```

### File Handling in Multipart

```python
part = root.append(open(__file__, 'rb'))
# Content-Type auto-detected via mimetypes module
# Content-Disposition includes file basename

# Override filename
part.set_content_disposition('attachment', filename='secret.txt')

# Set custom headers
part.headers[aiohttp.hdrs.CONTENT_ID] = 'X-12345'

# Content-Encoding is applied automatically on serialization
part.headers[aiohttp.hdrs.CONTENT_ENCODING] = 'gzip'
```

### MJPEG Streaming Example

```python
my_boundary = 'some-boundary'
response = web.StreamResponse(
    status=200,
    headers={'Content-Type': f'multipart/x-mixed-replace;boundary={my_boundary}'}
)

while True:
    frame = get_jpeg_frame()
    with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
        mpwriter.append(frame, {'Content-Type': 'image/jpeg'})
        await mpwriter.write(response, close_boundary=False)
```

Note: `close_boundary=False` prevents the closing `--boundary--` from being appended, allowing continuous streaming.

## FormData

For simple multipart form submissions:

```python
data = aiohttp.FormData()
data.add_field('file',
               open('report.xls', 'rb'),
               filename='report.xls',
               content_type='application/vnd.ms-excel')
data.add_field('description', 'My report')

await session.post(url, data=data)
```

Dictionary shorthand (auto-form-encoded or multipart):

```python
files = {'file': open('report.xls', 'rb')}
await session.post(url, data=files)
```

## Compression

### Response Decompression

Client automatically decompresses `gzip` and `deflate` transfer-encodings. Enable brotli support by installing `Brotli` or `brotlicffi`. Enable zstd by installing `backports.zstd` (Python >= 3.14 has built-in support).

Disable auto-decompression:

```python
async with aiohttp.ClientSession(auto_decompress=False) as session:
    ...

# Per-request override
async with session.get(url, auto_decompress=False) as resp:
    ...
```

### Server Compression

```python
resp = web.StreamResponse()
await resp.prepare(request)
resp.enable_compression()  # Auto-selects based on Accept-Encoding
resp.enable_compression(force=web.ContentCoding.gzip)  # Force gzip
await resp.write(b'data')
await resp.write_eof()
```

### Uploading Pre-compressed Data

```python
import zlib

data = zlib.compress(my_data)
headers = {'Content-Encoding': 'deflate'}
async with session.post(url, data=data, headers=headers):
    ...
```

## Content-Disposition and ETag

### ContentDisposition

```python
from aiohttp import ContentDisposition, ContentDispositionType

disp = ContentDisposition(
    disposition_type=ContentDispositionType.INLINE,
    filename='report.pdf'
)
```

### ETag

For conditional requests:

```python
# Server-side
etag = 'unique-tag-value'
resp.headers['ETag'] = etag

# Client checks request.if_match and request.if_none_match properties
```

## Common Data Structures

### FrozenList

Mutable list that can be frozen (becomes immutable):

```python
from aiohttp import FrozenList

fl = FrozenList([1, 2, 3])
fl.append(4)
fl.freeze()
# fl.append(5)  # Would raise RuntimeError
```

### ChainMapProxy

Immutable chain of mappings (used by `request.config_dict`):

```python
from aiohttp import ChainMapProxy

proxy = ChainMapProxy([{'a': 1}, {'b': 2}])
print(proxy['a'])  # 1
print(proxy['b'])  # 2
```
