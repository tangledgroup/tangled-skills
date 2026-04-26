---
name: aiohttp-sse-2-2-0
description: Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming endpoints that push data from server to clients using the EventSource API, implementing chat applications, live notifications, or continuous data feeds without WebSocket complexity.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.2.0"
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

Unlike WebSockets, SSE is simpler — it requires no handshake protocol, works over standard HTTP, supports automatic reconnection, and integrates cleanly with aiohttp's async architecture. The library provides `EventSourceResponse`, a subclass of `aiohttp.web.StreamResponse`, and the convenience helper `sse_response()` for context-manager-based streaming.

The library is part of the official aio-libs family and requires aiohttp 3+.

## When to Use

- Building real-time push endpoints (live feeds, notifications, progress updates)
- Implementing chat applications with server-to-client messaging
- Streaming continuous data (timestamps, sensor readings, stock prices)
- Any scenario where one-way server-to-client streaming suffices and WebSocket complexity is unnecessary
- Migrating from polling-based architectures to event-driven streaming

## Core Concepts

### SSE Protocol

SSE uses the `text/event-stream` MIME type. The connection stays open and the server pushes discrete messages formatted as:

```
data: message payload\r\n
\r\n
```

Optional fields enrich each message:

- **`id:`** — Event ID for client-side `lastEventId` tracking and reconnection
- **`event:`** — Named event type (dispatched to matching `addEventListener` handlers)
- **`retry:`** — Reconnection timeout in milliseconds

Comments starting with `:` are ignored by the browser and used internally for pings.

### EventSourceResponse

The core class, `EventSourceResponse`, extends `aiohttp.web.StreamResponse`. It sets the mandatory SSE headers automatically:

- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`
- `X-Accel-Buffering: no` (disables nginx buffering)

It manages a background ping task that periodically sends `: ping\r\n\r\n` to keep the connection alive. The default ping interval is 15 seconds.

### sse_response Helper

The `sse_response(request)` function creates an `EventSourceResponse`, prepares it against the request, and returns an async context manager. This is the recommended pattern for most use cases:

```python
async with sse_response(request) as resp:
    await resp.send("hello")
```

On exit from the context manager, streaming is stopped automatically.

### Connection Lifecycle

1. Client connects via `new EventSource("/endpoint")`
2. Server creates and prepares `EventSourceResponse`
3. Background ping task starts (sends keep-alive comments)
4. Server pushes events via `resp.send()`
5. Client disconnects or server calls `stop_streaming()`
6. Ping task is cancelled, connection closes

Use `resp.is_connected()` to check if the stream is still active during loops.

## Installation / Setup

Install with pip:

```bash
pip install aiohttp-sse
```

Requires aiohttp 3+ and Python 3.8–3.12 (as of v2.2.0). The library includes full type hints (`py.typed`).

## Usage Examples

### Basic Streaming Endpoint

Stream the current server time every second:

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

Client-side JavaScript:

```javascript
const source = new EventSource("/stream");
source.addEventListener("message", event => {
    console.log(event.data);
});
```

### Sending Named Events with IDs

Use the `event`, `id`, and `retry` parameters of `send()`:

```python
async def handler(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        await resp.send("default message")
        await resp.send("login event", event="user_login", id="evt-001")
        await resp.send("data update", event="data_update", id="evt-002", retry=5000)
    return resp
```

The `event` parameter lets clients subscribe to specific event types:

```javascript
source.addEventListener("user_login", event => {
    console.log("User logged in:", event.data);
});

source.addEventListener("data_update", event => {
    console.log("Data updated:", event.data);
});
```

### Multiline Data

Multiline data is split into separate `data:` lines automatically:

```python
await resp.send("line one\nline two\nline three")
```

Produces:

```
data: line one
data: line two
data: line three

```

### Custom Ping Interval

Adjust the ping interval (in seconds, supports float):

```python
async def handler(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        resp.ping_interval = 5.0  # ping every 5 seconds
        while resp.is_connected():
            await resp.send("tick")
            await asyncio.sleep(1)
    return resp
```

### Accessing Last-Event-ID

Read the client's `Last-Event-Id` header to support resumption after reconnection:

```python
async def handler(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        last_id = resp.last_event_id  # None on first connection
        if last_id:
            print(f"Client reconnected from event {last_id}")
        await resp.send("resumed", id="evt-100")
    return resp
```

### Manual Response (Without Context Manager)

For fine-grained control, create `EventSourceResponse` directly:

```python
from aiohttp_sse import EventSourceResponse


async def handler(request: web.Request) -> web.StreamResponse:
    resp = EventSourceResponse()
    await resp.prepare(request)
    await resp.send("message 1")
    await resp.send("message 2", event="custom", id="1")

    # Later, from another task:
    # resp.stop_streaming()

    await resp.wait()
    return resp
```

### Custom Response Class

Subclass `EventSourceResponse` to add helper methods, then pass it via `response_cls`:

```python
import json
from aiohttp_sse import EventSourceResponse, sse_response


class JsonSSE(EventSourceResponse):
    async def send_json(self, data: dict, **kwargs) -> None:
        await self.send(json.dumps(data), **kwargs)


async def handler(request: web.Request) -> web.StreamResponse:
    async with sse_response(request, response_cls=JsonSSE) as resp:
        await resp.send_json({"status": "ok", "count": 42}, event="update")
    return resp
```

### Chat Application Pattern

Broadcast messages to all connected SSE clients using `asyncio.Queue`:

```python
import asyncio
import json

from aiohttp import web
from aiohttp_sse import sse_response

channels: set[asyncio.Queue[str]] = set()


async def subscribe(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        queue: asyncio.Queue[str] = asyncio.Queue()
        channels.add(queue)
        try:
            while resp.is_connected():
                payload = await queue.get()
                await resp.send(payload)
        finally:
            channels.discard(queue)
    return resp


async def broadcast(request: web.Request) -> web.Response:
    data = await request.post()
    payload = json.dumps(dict(data))
    for q in channels:
        await q.put(payload)
    return web.Response()


app = web.Application()
app.router.add_get("/subscribe", subscribe)
app.router.add_post("/broadcast", broadcast)
```

### Graceful Shutdown

Track SSE responses and stop them cleanly on shutdown:

```python
import asyncio
import weakref

from aiohttp import web
from aiohttp_sse import EventSourceResponse, sse_response

streams = weakref.WeakSet[EventSourceResponse]()


async def on_shutdown(app: web.Application) -> None:
    for stream in streams:
        stream.stop_streaming()
    await asyncio.gather(
        *(stream.wait() for stream in streams),
        return_exceptions=True,
    )


async def handler(request: web.Request) -> web.StreamResponse:
    resp = await sse_response(request)
    streams.add(resp)
    try:
        while resp.is_connected():
            await resp.send("heartbeat")
            await asyncio.sleep(1)
        await resp.wait()
    finally:
        streams.discard(resp)
    return resp


app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_get("/stream", handler)
```

## API Reference

### EventSourceResponse

**Constructor:**

```python
EventSourceResponse(
    status: int = 200,
    reason: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
    sep: Optional[str] = None,
)
```

- `status` — HTTP status code (default: 200)
- `reason` — Reason phrase
- `headers` — Additional headers to merge
- `sep` — Line separator (default: `"\r\n"`)

**Methods:**

- `async send(data, id=None, event=None, retry=None)` — Send an SSE message. `data` is the payload string. `id` sets the event ID. `event` names the event type. `retry` sets reconnection timeout in milliseconds (must be int). Raises `ConnectionResetError` if the client disconnected.

- `async prepare(request)` — Prepare the response and start the ping task. Called automatically by `sse_response()`.

- `async wait()` — Await until streaming stops (ping task completes or is cancelled). Call after `stop_streaming()` to ensure clean shutdown. Raises `RuntimeError` if called before `prepare()`.

- `stop_streaming()` — Cancel the ping task and signal end of streaming. Raises `RuntimeError` if called before `prepare()`.

- `is_connected()` — Return `True` if response is prepared and ping task is running (connection alive).

**Properties:**

- `ping_interval` — Get/set the ping interval in seconds (int or float, must be >= 0). Default: 15.

- `last_event_id` — Read the client's `Last-Event-Id` header value. Returns `None` if not present. Raises `RuntimeError` if accessed before `prepare()`.

**Constants:**

- `DEFAULT_PING_INTERVAL = 15`
- `DEFAULT_SEPARATOR = "\r\n"`
- `DEFAULT_LAST_EVENT_HEADER = "Last-Event-Id"`

**Not supported:**

- `enable_compression()` raises `NotImplementedError` (compression is incompatible with SSE streaming).

### sse_response()

```python
sse_response(
    request: Request,
    *,
    status: int = 200,
    reason: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
    sep: Optional[str] = None,
    response_cls: type[EventSourceResponse] = EventSourceResponse,
) -> _ContextManager[EventSourceResponse]
```

Creates an `EventSourceResponse` (or custom subclass), prepares it against the request, and returns an async context manager. On exit, calls `stop_streaming()` and `wait()`.

The `response_cls` parameter must be a subclass of `EventSourceResponse`; passing an unrelated class raises `TypeError`.

## Event Source Protocol Details

### Message Format

Each SSE message follows this structure:

```
id: <event-id>\r\n
event: <event-type>\r\n
data: <payload-line-1>\r\n
data: <payload-line-2>\r\n
retry: <milliseconds>\r\n
\r\n
```

- Blank line (`\r\n`) terminates each message
- `data:` prefix is required and can appear multiple times for multiline payloads
- Internal line separators in data are split into separate `data:` lines
- The library strips line separators from `id` and `event` values

### Ping Mechanism

The background ping task sends `: ping\r\n\r\n` at the configured interval. Messages starting with `:` are treated as comments by browsers and ignored — they serve only to keep the connection alive against idle timeouts (proxies, load balancers, etc.).

If a `ConnectionResetError` or `RuntimeError` occurs during ping writing, the ping task exits cleanly.

### HTTP Method Support

SSE works with any HTTP method (GET, POST, PUT, DELETE, PATCH). While GET is conventional, the library imposes no restriction.

## Browser Client API

The browser's native `EventSource` interface handles SSE connections:

```javascript
const source = new EventSource("/stream");

// Default "message" events
source.onmessage = event => console.log(event.data);

// Named events
source.addEventListener("update", event => {
    console.log("Update:", event.data, "ID:", event.lastEventId);
});

// Connection events
source.onopen = () => console.log("Connected");
source.onerror = () => console.log("Error — will auto-reconnect");

// Manual close
source.close();
```

The `EventSource` API automatically:

- Reconnects on failure (with `retry:` delay if specified)
- Sends `Last-Event-Id` header on reconnection
- Dispatches events to matching listeners by name
- Falls back to `onmessage` for unnamed events

## Behavioral Guidelines

### Prefer sse_response() Over Manual Construction

Use `sse_response(request)` as the default pattern — it handles preparation, context management, and cleanup automatically. Only use manual `EventSourceResponse()` construction when you need explicit lifecycle control (e.g., tracking streams across tasks).

### Always Check is_connected() in Loops

When streaming in a loop, guard with `while resp.is_connected()` to avoid sending to closed connections:

```python
async with sse_response(request) as resp:
    while resp.is_connected():
        await resp.send(data)
        await asyncio.sleep(1)
```

### Handle ConnectionResetError

When using manual construction, wrap `send()` in try/except for `ConnectionResetError`:

```python
try:
    await resp.send(data)
except ConnectionResetError:
    resp.stop_streaming()
```

### Use weakref.WeakSet for Stream Tracking

When maintaining a collection of active SSE responses, use `weakref.WeakSet` to avoid memory leaks — disconnected streams will be garbage-collected automatically.

### Set ping_interval Appropriately

Reduce `ping_interval` when behind aggressive proxies or load balancers with short idle timeouts (e.g., set to 5–10 seconds). The default 15 seconds works for most direct connections.
