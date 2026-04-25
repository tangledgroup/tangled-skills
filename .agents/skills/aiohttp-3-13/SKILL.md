---
name: aiohttp-3-13
description: Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent HTTP requests in Python.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - async
  - http
  - python
  - web-server
  - http-client
  - websocket
category: web-development
required_environment_variables: []
---

# aiohttp-3-13 Skill

## Overview

Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent HTTP requests in Python.


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent HTTP requests in Python.

Asynchronous HTTP Client/Server for Python asyncio (version 3.13.x). Supports building async web servers, REST APIs, and making concurrent HTTP requests with connection pooling, WebSockets, middleware, and streaming.

## When to Use

- Building async web applications or REST APIs in Python
- Making concurrent HTTP requests from Python applications
- Implementing WebSocket clients or servers
- Working with streaming HTTP responses/requests
- Needing connection pooling and keep-alive for performance
- Building microservices with async Python

## Setup

### Installation

```bash
# Basic installation
pip install aiohttp

# With DNS speedups (recommended)
pip install aiodns

# All speedups in one command
pip install aiohttp[speedups]
```

### Prerequisites

- Python 3.8+ with asyncio support
- Optional: `aiodns` for faster DNS resolution
- Optional: `Brotli` for compression speedups

## Quick Start

### Client: Make HTTP Requests

See [Client Reference](references/01-client-reference.md) for detailed API documentation.

```python
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get') as resp:
            print(f"Status: {resp.status}")
            print(f"Content-type: {resp.headers['content-type']}")
            html = await resp.text()
            print(f"Body: {html[:100]}...")

asyncio.run(main())
```

**Key points:**
- Reuse `ClientSession` for multiple requests (connection pooling)
- Don't create a session per request - use one per application
- Use async/await with context managers

### Server: Build Web Applications

See [Server Reference](references/02-server-reference.md) for detailed API documentation.

```python
from aiohttp import web

async def hello(request):
    return web.Response(text="Hello, world")

async def main():
    app = web.Application()
    app.add_routes([web.get('/', hello)])
    web.run_app(app)

if __name__ == '__main__':
    asyncio.run(main())
```

**Alternative with route decorators:**

```python
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes(routes)
web.run_app(app)
```

### WebSocket Communication

See [WebSocket Guide](references/03-websockets.md) for detailed examples.

**Client WebSocket:**
```python
import aiohttp
import asyncio

async def ws_client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://echo.websocket.org') as ws:
            await ws.send_str("Hello")
            resp = await ws.receive_str()
            print(f"Received: {resp}")

asyncio.run(ws_client())
```

**Server WebSocket:**
```python
from aiohttp import web

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            break
    
    return ws

app = web.Application()
app.add_routes([web.get('/ws', websocket_handler)])
web.run_app(app)
```

## Common Operations

### POST Requests with JSON

```python
async def post_json():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://httpbin.org/post',
            json={'key': 'value', 'number': 42}
        ) as resp:
            data = await resp.json()
            return data
```

### File Upload (Multipart)

See [Multipart Reference](references/04-multipart.md) for details.

```python
async def upload_file():
    async with aiohttp.ClientSession() as session:
        with open('document.pdf', 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='document.pdf', content_type='application/pdf')
            
            async with session.post('http://example.com/upload', data=data) as resp:
                print(await resp.text())
```

### Request Timeout Configuration

```python
from aiohttp import ClientTimeout

async def request_with_timeout():
    timeout = ClientTimeout(total=30, connect=5, sock_read=10)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get('http://example.com') as resp:
            return await resp.text()
```

### Custom Headers and Cookies

```python
async def custom_headers():
    headers = {'X-Custom-Header': 'value', 'Authorization': 'Bearer token123'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get('http://api.example.com') as resp:
            return await resp.json()

async def with_cookies():
    cookies = {'session_id': 'abc123', 'user_pref': 'dark'}
    
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get('http://example.com') as resp:
            return await resp.text()
```

### Server Middleware

See [Advanced Server Topics](references/05-advanced-server.md) for details.

```python
from aiohttp import web
from datetime import datetime

async def timing_middleware(app, handler):
    async def middleware(request):
        start = datetime.now()
        response = await handler(request)
        duration = (datetime.now() - start).total_seconds()
        response.headers['X-Response-Time'] = str(duration)
        return response
    return middleware

app = web.Application(middlewares=[timing_middleware])
```

## Reference Files

### Index & Overview

- [`references/00-api-index.md`](references/00-api-index.md) - Complete API index with all components mapped to reference files

### Client API

- [`references/01-client-reference.md`](references/01-client-reference.md) - Client overview, sessions, requests, responses
- [`references/07-client-api-connectors.md`](references/07-client-api-connectors.md) - TCPConnector, UnixConnector, connection pooling
- [`references/08-client-api-exceptions.md`](references/08-client-api-exceptions.md) - All client exceptions and error handling patterns

### Server API

- [`references/02-server-reference.md`](references/02-server-reference.md) - Server overview, request/response objects
- [`references/09-server-api-application.md`](references/09-server-api-application.md) - Application class, lifecycle, subapps, runners
- [`references/10-server-api-routing.md`](references/10-server-api-routing.md) - RouteTableDef, path params, static files, views

### Core APIs

- [`references/11-api-streams.md`](references/11-api-streams.md) - StreamReader, StreamWriter, chunked transfer
- [`references/12-api-data-structures.md`](references/12-api-data-structures.md) - FrozenList, ChainMapProxy, CIMultiDict, MultiDict, URL

### Advanced Topics

- [`references/03-websockets.md`](references/03-websockets.md) - WebSocket client and server examples
- [`references/04-multipart.md`](references/04-multipart.md) - Multipart form data, file uploads/downloads
- [`references/05-advanced-server.md`](references/05-advanced-server.md) - Middleware, signals, graceful shutdown
- [`references/06-tracing.md`](references/06-tracing.md) - Client and server tracing for monitoring/debugging

## Troubleshooting

### Common Issues

**Connection pool exhausted:**
- Reuse `ClientSession` instead of creating per request
- Increase connector limits: `TCPConnector(limit=100)`

**Timeout errors:**
- Use `ClientTimeout` to configure timeouts explicitly
- Increase `sock_connect` for slow networks

**SSL certificate errors:**
- Use `ssl=False` for testing (not production)
- Install proper certificates or use `ssl_context`

**Memory issues with large responses:**
- Use streaming: `async with session.get(url) as resp: async for chunk in resp.content.iter_chunked(8192): ...`

**Event loop errors:**
- Always run async code with `asyncio.run()` or in existing event loop
- Don't mix blocking and async code

See [Advanced Server Topics](references/05-advanced-server.md) for graceful shutdown and logging configuration.

### Important Notes

1. **Session reuse**: Create one `ClientSession` per application, not per request
2. **Always await**: All aiohttp methods are coroutines and must be awaited
3. **Context managers**: Use `async with` for sessions and responses to ensure cleanup
4. **Connection pooling**: Enabled by default, improves performance significantly
5. **Keep-alive**: Enabled by default, reuse TCP connections
6. **Base URL**: Use `base_url` parameter in ClientSession for relative URLs
7. **Auto-decompression**: Enabled by default for gzip/deflate/brotli


## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.

