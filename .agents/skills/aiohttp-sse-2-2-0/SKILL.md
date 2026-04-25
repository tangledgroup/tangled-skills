---
name: aiohttp-sse-2-2-0
description: Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming endpoints that push data from server to clients using the EventSource API, implementing chat applications, live notifications, or continuous data feeds without WebSocket complexity.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - aiohttp
  - sse
  - server-sent-events
  - streaming
  - real-time
  - eventsource
  - websockets-alternative
category: development
external_references:
  - https://github.com/hallazzang/aiohttp-sse
  - https://aiohttp-sse.readthedocs.io/
---
## Overview
Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming endpoints that push data from server to clients using the EventSource API, implementing chat applications, live notifications, or continuous data feeds without WebSocket complexity.

## When to Use
- Building real-time notification systems that push updates from server to client
- Creating live data feeds (stock prices, sensor data, logs)
- Implementing chat applications with simple broadcast patterns
- Streaming long-running computation results to clients
- Providing auto-updating dashboards or monitoring interfaces
- Needing simpler alternative to WebSockets for one-way communication

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.## Overview

Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming endpoints that push data from server to clients using the EventSource API, implementing chat applications, live notifications, or continuous data feeds without WebSocket complexity.

A Python library providing Server-Sent Events (SSE) support for aiohttp applications. Enables servers to push real-time data to clients over HTTP using the EventSource API without the complexity of WebSockets.

## Installation / Setup
Install the library:

```bash
pip install aiohttp-sse
```

**Requirements:**
- Python 3.8+
- aiohttp >= 3.0

## Usage Examples
### Basic SSE Endpoint

Create a simple endpoint that streams server time every second:

```python
import asyncio
from datetime import datetime
from aiohttp import web
from aiohttp_sse import sse_response


async def hello(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        while resp.is_connected():
            data = f"Server Time : {datetime.now()}"
            await resp.send(data)
            await asyncio.sleep(1)
    return resp


app = web.Application()
app.router.add_route("GET", "/hello", hello)
web.run_app(app, host="127.0.0.1", port=8080)
```

### Client-Side Consumption

Connect using the browser's native EventSource API:

```html
<script>
    var eventSource = new EventSource("/hello");
    eventSource.addEventListener("message", event => {
        document.getElementById("response").innerText = event.data;
    });
</script>
<div id="response"></div>
```

See [Core Concepts](reference/01-core-concepts.md) for detailed SSE protocol explanation.

## Common Operations
### Sending Events with Custom Types

Send typed events that clients can handle differently:

```python
async def notifications(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        await resp.send("New message received", event="message")
        await resp.send("User joined chat", event="user_join")
        await resp.send("System maintenance scheduled", event="alert")
    return resp
```

Client handles different event types:

```javascript
var source = new EventSource("/notifications");

source.addEventListener("message", (event) => {
    console.log("Message:", event.data);
});

source.addEventListener("user_join", (event) => {
    console.log("User joined:", event.data);
});

source.addEventListener("alert", (event) => {
    alert(event.data);
});
```

### Event IDs for Reconnection

Use event IDs to track position and handle reconnections:

```python
async def stream_with_ids(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        event_id = 1
        while resp.is_connected():
            await resp.send(f"Event data {event_id}", id=str(event_id))
            event_id += 1
            await asyncio.sleep(1)
    return resp
```

See [Advanced Workflow](reference/02-advanced-workflow.md) for reconnection patterns using `last_event_id`.

### Retry Configuration

Set reconnection time for clients:

```python
async def config_retry(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        # Client will retry after 3000ms (3 seconds) on disconnection
        await resp.send("Initial data", retry=3000)
        await resp.send("More data")
    return resp
```

### Checking Connection Status

Monitor if client is still connected:

```python
async def conditional_stream(request: web.Request) -> web.StreamResponse:
    async with sse_response(request) as resp:
        counter = 0
        while resp.is_connected() and counter < 100:
            await resp.send(f"Update {counter}")
            counter += 1
            await asyncio.sleep(0.5)
        
        if resp.is_connected():
            await resp.send("Stream completed normally")
        else:
            print("Client disconnected early")
    return resp
```

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Advanced Workflow](reference/02-advanced-workflow.md)
- [Api Reference](reference/03-api-reference.md)
- [Troubleshooting](reference/04-troubleshooting.md)

## Troubleshooting
### Connection Issues

If clients aren't receiving events:

1. Verify `Content-Type: text/event-stream` header is set (automatic with aiohttp-sse)
2. Check that server isn't buffering responses (`X-Accel-Buffering: no` header helps with Nginx)
3. Ensure async context manager is used properly with `async with`

### Memory Leaks in Chat Apps

When building multi-client applications, use weak references to avoid memory leaks:

```python
import weakref
from aiohttp import web

streams_key = web.AppKey("streams_key", weakref.WeakSet)

async def on_startup(app):
    app[streams_key] = weakref.WeakSet()
```

See [Advanced Workflow](reference/02-advanced-workflow.md) for complete chat example with proper cleanup.

### Client Disconnection Handling

Use `is_connected()` to detect when clients disconnect:

```python
async def handler(request):
    async with sse_response(request) as resp:
        try:
            while resp.is_connected():
                await resp.send("data")
                await asyncio.sleep(1)
        except ConnectionResetError:
            print("Client disconnected")
    return resp
```

