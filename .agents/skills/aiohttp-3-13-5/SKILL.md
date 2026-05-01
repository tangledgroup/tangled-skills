---
name: aiohttp-3-13-5
description: Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent HTTP requests in Python.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.13.5"
tags:
  - http
  - async
  - client
  - server
  - websocket
  - aiohttp
category: library
external_references:
  - https://docs.aiohttp.org/en/stable/
  - https://github.com/aio-libs/aiohttp
---

# aiohttp 3.13

## Overview

aiohttp is a comprehensive async HTTP client/server framework for Python built on top of `asyncio`. It provides both an HTTP client and an HTTP server, supporting WebSockets, streaming, middleware, signals, connection pooling, and more. Current stable version is 3.13.5.

Key features:
- Full-featured async HTTP client with connection pooling and keep-alive
- Async HTTP server with pluggable routing, middlewares, and signals
- WebSocket support on both client and server sides
- Streaming request/response bodies via `StreamReader`
- Multipart reader/writer for file uploads and complex payloads
- Client middleware for request/response interception
- Server middleware and signal system
- Built-in test utilities (`TestClient`, `TestServer`, `AioHTTPTestCase`)
- Gunicorn worker support (`aiohttp.GunicornWebWorker`)

Dependencies: `attrs`, `multidict`, `yarl`. Optional: `aiodns` (faster DNS), `Brotli` or `brotlicffi` (brotli compression, min v1.2).

## Changes Since 3.13.0

**3.13.5** (2026-03-31): Skipped duplicate singleton header check in lax mode (default for response parsing).

**3.13.4** (2026-03-28): Added `max_headers` parameter to limit headers read from a response. Added `dns_cache_max_size` parameter to `TCPConnector`. Fixed server hanging on mismatched chunked transfer encoding. Fixed access log DST timestamps. Fixed `RuntimeError` with GunicornWebWorker on Python >=3.14. Fixed TLS connection error with `ClientTimeout(total=0)`. Restored synchronous `BodyPartReader.decode()` (new async `decode_iter()` available). Upgraded llhttp to 3.9.1.

**3.13.3** (2026-01-03): Security release. Fixed proxy authorization headers not passing on connection reuse (407 errors). Fixed multipart reading with empty body parts. Fixed WebSocket continuation frame parser exception. Brotli/brotlicffi min version now 1.2 with 32MiB decompression limit. Moved dependency metadata to `pyproject.toml` (PEP 621).

**3.13.2** (2025-10-28): Fixed cookie parser to continue on malformed cookies. Fixed netrc credential loading from default `~/.netrc`. Fixed WebSocket compressed sends to be cancellation-safe.

**3.13.1** (2025-10-17): `AppRunner` config options now available in `run_app()`. Switched to `backports.zstd` for Python <3.14. Fixed `Content-Type` parsing for invalid syntax. Fixed Python 3.14 support without zstd. Fixed blocking I/O in event loop with netrc auth. Fixed sub-application routing via `.add_domain()`.

## When to Use

- Building async web applications and REST APIs in Python
- Making concurrent HTTP requests from Python with connection pooling
- Implementing WebSocket servers or clients
- Creating high-performance microservices with asyncio
- Streaming large file uploads/downloads without loading into memory
- Building async middleware for request/response processing
- Testing aiohttp-based applications with built-in test utilities

## Core Concepts

**`ClientSession`**: The primary client object. Reuse a single session per application — never create one per request. Sessions manage connection pools, cookies, and keep-alive.

```python
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://python.org') as response:
            print("Status:", response.status)
            html = await response.text()
```

**`web.Application`**: The primary server object. Holds routes, middlewares, signals, and shared state via dict-like interface.

```python
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    return web.Response(text=f"Hello, {name}")

app = web.Application()
app.add_routes([web.get('/', handle), web.get('/{name}', handle)])

if __name__ == '__main__':
    web.run_app(app)
```

**`async/await` pattern**: All aiohttp operations are coroutines. Use `async with` for sessions and responses to ensure proper cleanup.

**Connection pooling**: Sessions maintain a connection pool internally. Connection reuse and keep-alive are enabled by default, improving performance for repeated requests to the same host.

## Installation / Setup

Install via pip:

```bash
pip install aiohttp
```

For speedups (recommended):

```bash
pip install aiohttp[speedups]
```

This includes `aiodns` (faster DNS resolution) and `Brotli` (brotli compression support).

Enable Python development mode during development for stricter parsing and additional checks:

```bash
python -X dev your_app.py
```

## Usage Examples

### Client — Basic Requests

```python
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        # GET request
        async with session.get('https://httpbin.org/get') as resp:
            print(resp.status)
            data = await resp.json()

        # POST with JSON body
        async with session.post('https://httpbin.org/post', json={'key': 'value'}) as resp:
            print(await resp.json())

        # POST with form data
        payload = {'key1': 'value1', 'key2': 'value2'}
        async with session.post('https://httpbin.org/post', data=payload) as resp:
            print(await resp.text())

asyncio.run(main())
```

### Client — Query Parameters

```python
params = {'key1': 'value1', 'key2': 'value2'}
async with session.get('https://httpbin.org/get', params=params) as resp:
    pass  # URL becomes https://httpbin.org/get?key1=value1&key2=value2
```

### Client — Response Reading

```python
# Text response
text = await resp.text()
text_custom_encoding = await resp.text(encoding='windows-1251')

# Binary response
data = await resp.read()

# JSON response
json_data = await resp.json()

# Streaming large responses
with open(filename, 'wb') as fd:
    async for chunk in resp.content.iter_chunked(chunk_size):
        fd.write(chunk)
```

### Client — Authentication

```python
from aiohttp import BasicAuth

auth = BasicAuth(login="user", password="pass")
async with aiohttp.ClientSession(auth=auth) as session:
    async with session.get("https://httpbin.org/basic-auth/user/pass") as resp:
        print(await resp.text())
```

### Client — File Upload

```python
# Simple file upload
files = {'file': open('report.xls', 'rb')}
await session.post(url, data=files)

# With explicit filename and content type
data = aiohttp.FormData()
data.add_field('file',
               open('report.xls', 'rb'),
               filename='report.xls',
               content_type='application/vnd.ms-excel')
await session.post(url, data=data)

# Streaming upload (large files)
with open('massive-body', 'rb') as f:
    await session.post('https://httpbin.org/post', data=f)
```

### Server — Routing

```python
from aiohttp import web

app = web.Application()

# Imperative style
app.router.add_get('/', handle_get)
app.router.add_post('/submit', handle_post)

# Route table (Flask-like decorators)
routes = web.RouteTableDef()

@routes.get('/get')
async def handle_get(request):
    ...

@routes.post('/post')
async def handle_post(request):
    ...

app.router.add_routes(routes)

# Variable routes
app.router.add_get(r'/{name:\d+}', handler)  # custom regex

# Named routes for URL building
@routes.get('/root', name='root')
async def handler(request):
    url = request.app.router['root'].url_for().with_query({"a": "b"})
```

### Server — Class-Based Views

```python
class MyView(web.View):
    async def get(self):
        return await get_resp(self.request)

    async def post(self):
        return await post_resp(self.request)

app.router.add_view('/path/to', MyView)
```

### Server — JSON Response

```python
async def handler(request):
    data = {'some': 'data'}
    return web.json_response(data)
```

### Server — Form Handling

```python
async def do_login(request):
    data = await request.post()
    login = data['login']
    password = data['password']
```

### Server — WebSocket

```python
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            break
    return ws
```

### Server — Static Files

```python
app.add_routes([web.static('/static', '/path/to/static/folder')])

# With directory listing
web.static('/prefix', path_to_folder, show_index=True)

# With cache busting
web.static('/prefix', path_to_folder, append_version=True)
```

### Server — Data Sharing

```python
# Application-level storage (use AppKey for type safety)
db_key = web.AppKey("db", Database)
app[db_key] = database_instance

async def handler(request):
    db = request.app[db_key]
    # use db...

# Request-level storage
async def handler(request):
    request['processed'] = True

# Cross-application config lookup (nested apps)
async def handler(request):
    data = request.config_dict[my_key]  # searches parent apps too
```

### Client — Middleware

```python
async def auth_middleware(req: aiohttp.ClientRequest, handler: aiohttp.ClientHandlerType) -> aiohttp.ClientResponse:
    req.headers["Authorization"] = get_auth_header()
    return await handler(req)

async with aiohttp.ClientSession(middlewares=(auth_middleware,)) as session:
    async with session.get("https://example.com") as resp:
        ...

# Middleware chaining follows onion pattern:
# middleware1 (pre) -> middleware2 (pre) -> request -> middleware2 (post) -> middleware1 (post)
```

### Client — Timeouts

```python
from aiohttp import ClientTimeout

timeout = ClientTimeout(total=300, sock_connect=30)
async with aiohttp.ClientSession(timeout=timeout) as session:
    ...
```

### Testing with pytest

```python
from aiohttp import web

async def test_hello(aiohttp_client):
    app = web.Application()
    app.router.add_get('/', hello_handler)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello, world' in text
```

### Testing with unittest

```python
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web

class MyAppTestCase(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        app.router.add_get('/', self.hello)
        return app

    async def test_example(self):
        async with self.client.request("GET", "/") as resp:
            self.assertEqual(resp.status, 200)
```

## Advanced Topics

**Client API**: Session configuration, connectors, SSL/proxy support, tracing, cookie management → [Client Reference](reference/01-client-reference.md)

**Server API**: Application runners, middlewares, signals, graceful shutdown, nested applications, deployment patterns → [Server Reference](reference/02-server-reference.md)

**Streaming and Multipart**: StreamReader API, multipart reader/writer, file streaming → [Streaming and Multipart](reference/03-streaming-multipart.md)
