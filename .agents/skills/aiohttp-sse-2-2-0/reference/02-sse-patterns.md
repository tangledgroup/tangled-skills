# SSE Patterns and Advanced Usage

## Contents
- Event Source Protocol Details
- Browser Client API
- Behavioral Guidelines
- Chat Application Pattern
- Graceful Shutdown

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

## Chat Application Pattern

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

## Graceful Shutdown

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
