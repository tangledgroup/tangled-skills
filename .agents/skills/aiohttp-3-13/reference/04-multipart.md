# aiohttp Multipart Reference

## Client: Sending Multipart Forms

### Basic File Upload

```python
import aiohttp
import asyncio

async def upload_file():
    async with aiohttp.ClientSession() as session:
        # Single file upload
        with open('document.pdf', 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='document.pdf')
            
            async with session.post(
                'http://example.com/upload',
                data=data
            ) as resp:
                print(await resp.text())

asyncio.run(upload_file())
```

### Multiple Files

```python
async def upload_multiple_files():
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        
        # Add multiple files
        with open('photo1.jpg', 'rb') as f1:
            data.add_field('photos', f1, filename='photo1.jpg')
        
        with open('photo2.jpg', 'rb') as f2:
            data.add_field('photos', f2, filename='photo2.jpg')
        
        # Add regular form fields
        data.add_field('description', 'My photos')
        data.add_field('category', 'vacation')
        
        async with session.post(
            'http://example.com/upload',
            data=data
        ) as resp:
            result = await resp.json()
            return result

asyncio.run(upload_multiple_files())
```

### Custom Content-Type

```python
async def upload_with_content_type():
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        
        with open('document.pdf', 'rb') as f:
            data.add_field(
                'file',
                f,
                filename='document.pdf',
                content_type='application/pdf'  # Explicit type
            )
        
        async with session.post('http://example.com/upload', data=data) as resp:
            ...
```

### File from Bytes

```python
async def upload_from_bytes():
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        
        # Create file-like object from bytes
        import io
        file_bytes = b'Hello, World!'
        file_obj = io.BytesIO(file_bytes)
        
        data.add_field(
            'file',
            file_obj,
            filename='hello.txt',
            content_type='text/plain'
        )
        
        async with session.post('http://example.com/upload', data=data) as resp:
            ...
```

### FormData Constructor Options

```python
data = aiohttp.FormData(
    boundary=None,  # Custom MIME boundary (auto-generated if None)
)

# Add fields
data.add_field(
    name='file',           # Field name
    value=file_object,     # File-like object or bytes
    filename='doc.pdf',    # Filename in multipart
    content_type='application/pdf',  # MIME type (guessed from extension if None)
    headers=None,          # Additional headers for this part
)
```

### Content-Type Guessing

aiohttp guesses content-type from file extension:

```python
# Common mappings
'.txt' -> 'text/plain'
'.jpg' -> 'image/jpeg'
'.png' -> 'image/png'
'.pdf' -> 'application/pdf'
'.json' -> 'application/json'
'.html' -> 'text/html'
```

### Custom Headers per Field

```python
from email.message import EmailMessage

async def upload_with_headers():
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        
        # Create custom headers for this field
        headers = {
            'X-Custom-Header': 'value',
            'Content-Disposition': 'form-data; name="file"; filename="custom.txt"'
        }
        
        with open('data.txt', 'rb') as f:
            data.add_field('file', f, filename='data.txt', headers=headers)
        
        async with session.post('http://example.com/upload', data=data) as resp:
            ...
```

## Server: Receiving Multipart Forms

### Basic File Upload Handler

```python
from aiohttp import web

async def upload_handler(request):
    # Parse multipart form data
    data = await request.post()
    
    # Get file object
    file = data.get('file')
    
    if file:
        filename = file.filename
        content_type = file.content_type
        file_bytes = file.file.read()  # Read all bytes
        
        # Save to disk
        with open(f'uploads/{filename}', 'wb') as f:
            f.write(file_bytes)
        
        return web.json_response({
            'status': 'success',
            'filename': filename,
            'size': len(file_bytes)
        })
    
    return web.HTTPBadRequest("No file provided")

app = web.Application()
app.add_routes([web.post('/upload', upload_handler)])
```

### Streaming Large Files

```python
async def streaming_upload(request):
    reader = await request.multipart()
    
    while True:
        field = await reader.next()
        
        if not field:
            break
        
        # Process file in chunks
        filename = field.filename
        
        with open(f'uploads/{filename}', 'wb') as f:
            async for chunk in field.iter_chunked(8192):
                f.write(chunk)
        
        print(f"Uploaded: {filename}")
    
    return web.json_response({'status': 'success'})

app.add_routes([web.post('/upload', streaming_upload)])
```

### Multiple Files Handling

```python
async def multi_file_upload(request):
    data = await request.post()
    
    # Get all files with same field name
    files = data.getall('photos', [])
    
    uploaded_files = []
    for file in files:
        filename = file.filename
        content = file.file.read()
        
        # Save file
        path = f'uploads/{filename}'
        with open(path, 'wb') as f:
            f.write(content)
        
        uploaded_files.append({
            'filename': filename,
            'size': len(content),
            'content_type': file.content_type
        })
    
    return web.json_response({
        'status': 'success',
        'files': uploaded_files
    })
```

### Accessing Form Fields

```python
async def form_with_files(request):
    data = await request.post()
    
    # Regular form fields
    title = data.get('title')
    description = data.get('description')
    
    # File field
    file = data.get('attachment')
    if file:
        filename = file.filename
        content_type = file.content_type
    
    return web.json_response({
        'title': title,
        'files_received': 1 if file else 0
    })
```

### Multipart Field Object

Properties of `field` from multipart data:

- `name` - Field name (str)
- `filename` - Original filename (str or None)
- `content_type` - MIME type (str)
- `file` - File-like object (io.BytesIO)
- `headers` - Field headers (CIMultiDictProxy)

Methods:

```python
# Read all content
content = await field.read()

# Stream in chunks
async for chunk in field.iter_chunked(8192):
    process(chunk)

# Get as text
text = await field.text()
```

### File Validation

```python
ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

async def validated_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    
    if not field:
        raise web.HTTPBadRequest("No file provided")
    
    # Validate content type
    if field.content_type not in ALLOWED_TYPES:
        raise web.HTTPBadRequest(
            f"Invalid file type. Allowed: {ALLOWED_TYPES}"
        )
    
    # Validate size (streaming to avoid memory issues)
    total_size = 0
    temp_file = io.BytesIO()
    
    async for chunk in field.iter_chunked(8192):
        total_size += len(chunk)
        
        if total_size > MAX_SIZE:
            raise web.HTTPRequestEntityTooLarge(
                f"File too large. Max size: {MAX_SIZE} bytes"
            )
        
        temp_file.write(chunk)
    
    # Save validated file
    with open(f'uploads/{field.filename}', 'wb') as f:
        f.write(temp_file.getvalue())
    
    return web.json_response({'status': 'success'})
```

### Filename Sanitization

```python
import os
import re

def sanitize_filename(filename):
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-.]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100 - len(ext)] + ext
    
    return filename

async def safe_upload(request):
    data = await request.post()
    file = data.get('file')
    
    if file:
        safe_name = sanitize_filename(file.filename)
        
        with open(f'uploads/{safe_name}', 'wb') as f:
            f.write(file.file.read())
        
        return web.json_response({'filename': safe_name})
```

## Server-Side Multipart Response

### Creating Multipart Responses

```python
from aiohttp import web

async def multipart_response(request):
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'multipart/mixed; boundary="boundary"'
        }
    )
    await response.prepare(request)
    
    # Write parts
    await response.write(b'--boundary\r\n')
    await response.write(b'Content-Type: text/plain\r\n\r\n')
    await response.write(b'Part 1\r\n')
    
    await response.write(b'--boundary\r\n')
    await response.write(b'Content-Type: application/json\r\n\r\n')
    await response.write(b'{"key": "value"}\r\n')
    
    await response.write(b'--boundary--\r\n')
    await response.write_eof()
    
    return response
```

### Progress Tracking

```python
async def upload_with_progress(request):
    reader = await request.multipart()
    field = await reader.next()
    
    total_size = int(field.headers.get('Content-Length', 0))
    uploaded = 0
    
    with open(f'uploads/{field.filename}', 'wb') as f:
        async for chunk in field.iter_chunked(8192):
            f.write(chunk)
            uploaded += len(chunk)
            
            # Could emit progress via WebSocket or store in Redis
            progress = (uploaded / total_size * 100) if total_size else 0
            print(f"Upload progress: {progress:.1f}%")
    
    return web.json_response({'status': 'complete'})
```
