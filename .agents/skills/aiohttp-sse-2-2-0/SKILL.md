---
name: aiohttp-sse-2-2-0
description: Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming endpoints that push data from server to clients using the EventSource API, implementing chat applications, live notifications, or continuous data feeds without WebSocket complexity.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - aiohttp
  - server-sent-events
  - sse
  - eventsource
  - streaming
  - asyncio
category: library
external_references:
  - https://github.com/aio-libs/aiohttp-sse
  - https://aiohttp-sse.readthedocs.io/
---

# aiohttp-sse 2.2.0

## Overview

**aiohttp-sse** provides Server-Sent Events (SSE) support for [aiohttp](https://github.com/aio-libs/aiohttp). It enables one-way real-time communication from server to client over HTTP using the `text/event-stream` content type and the browser's native `EventSource` API.

Unlike WebSockets, SSE is simpler — no handshake protocol, works over standard HTTP, supports automatic reconnection, and integrates cleanly with aiohttp's async architecture. The library provides `EventSourceResponse` (subclass of `aiohttp.web.StreamResponse`) and the convenience helper `sse_response()` for context-manager-based streaming.

Part of the official aio-libs family, requires aiohttp 3+ and Python 3.8–3.12.

## When to Use

- Building real-time push endpoints (live feeds, notifications, progress updates)
- Implementing chat applications with server-to-client messaging
- Streaming continuous data (timestamps, sensor readings, stock prices)
- Any scenario where one-way server-to-client streaming suffices and WebSocket complexity is unnecessary
- Migrating from polling-based architectures to event-driven streaming

## Core Concepts

### SSE Protocol

SSE uses the `text/event-stream` MIME type. The connection stays open and the server pushes discrete messages:

```
data: message payload\r\n
\r\n
```

Optional fields: `id:` for reconnection tracking, `event:` for named event types, `retry:` for reconnection timeout in milliseconds. Comments starting with `:` are used internally for pings.

### EventSourceResponse

The core class, `EventSourceResponse`, extends `aiohttp.web.StreamResponse`. It sets mandatory SSE headers automatically (`Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`). Manages a background ping task (default interval: 15 seconds).

### sse_response Helper

The `sse_response(request)` function creates an `EventSourceResponse`, prepares it, and returns an async context manager — the recommended pattern for most use cases:

```python
async with sse_response(request) as resp:
    await resp.send("hello")
```

### Connection Lifecycle

1. Client connects via `new EventSource("/endpoint")`
2. Server creates and prepares `EventSourceResponse`
3. Background ping task starts (keep-alive comments)
4. Server pushes events via `resp.send()`
5. Client disconnects or server calls `stop_streaming()`
6. Ping task cancelled, connection closes

Use `resp.is_connected()` to check if the stream is still active during loops.

## Installation / Setup

```bash
pip install aiohttp-sse
```

Requires aiohttp 3+ and Python 3.8–3.12. Includes full type hints (`py.typed`).

## Usage Examples

### Basic Streaming Endpoint

```python
import asyncio
from datetime import datetime
from aiohttp import web
from aiohttp_sse import sse_response


async def hello(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        while resp.is_connected():
            await resp.send(f"Server Time: {datetime.now()}")
            await asyncio.sleep(1)
    return resp


app = web.Application()
app.router.add_get("/stream", hello)
web.run_app(app, host="127.0.0.1", port=8080)
```

Client-side:

```javascript
const source = new EventSource("/stream");
source.addEventListener("message", event => console.log(event.data));
```

### Named Events with IDs

```python
async def handler(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        await resp.send("default message")
        await resp.send("login event", event="user_login", id="evt-001")
        await resp.send("data update", event="data_update", id="evt-002", retry=5000)
    return resp
```

### Multiline Data

Multiline data is split into separate `data:` lines automatically:

```python
await resp.send("line one\nline two\nline three")
```

### Custom Ping Interval

```python
async with sse_response(request) as resp:
    resp.ping_interval = 5.0  # ping every 5 seconds
    while resp.is_connected():
        await resp.send("tick")
        await asyncio.sleep(1)
```

### Accessing Last-Event-ID

```python
async with sse_response(request) as resp:
    last_id = resp.last_event_id  # None on first connection
    if last_id:
        print(f"Client reconnected from event {last_id}")
```

### Custom Response Class

```python
import json
from aiohttp_sse import EventSourceResponse, sse_response


class JsonSSE(EventSourceResponse):
    async def send_json(self, data: dict, **kwargs) -> None:
        await self.send(json.dumps(data), **kwargs)


async with sse_response(request, response_cls=JsonSSE) as resp:
    await resp.send_json({"status": "ok", "count": 42}, event="update")
```

## Advanced Topics

**API Reference**: Full API for EventSourceResponse and sse_response() → [API Reference](reference/01-api-reference.md)

**SSE Patterns**: Protocol details, browser client API, behavioral guidelines, chat patterns, graceful shutdown → [SSE Patterns](reference/02-sse-patterns.md)
