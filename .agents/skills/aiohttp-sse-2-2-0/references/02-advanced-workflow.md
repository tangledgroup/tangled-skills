# Advanced Workflow

This reference covers advanced patterns including chat applications, graceful shutdown, custom response classes, and production-ready implementations.

## Multi-Client Chat Application

Complete example of a real-time chat using SSE for broadcasting messages to all connected clients.

### Architecture

```
Client → POST /message → Server → Broadcast via queues → All Clients (SSE)
```

### Implementation

```python
import asyncio
import json
from typing import Set

from aiohttp import web
from aiohttp_sse import sse_response

# App-level storage for client queues
channels = web.AppKey("channels", Set[asyncio.Queue[str]])


async def chat(request: web.Request) -> web.Response:
    """Serve the chat HTML page."""
    html = """
    <html>
      <head>
        <title>Chat</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
          .messages { overflow: scroll; height: 200px; }
          .sender { float: left; clear: left; width: 100px; margin-right: 10px; text-align: right; background: #ddd; }
          .message { float: left; }
        </style>
        <script>
          $(function(){
            var source = new EventSource("/subscribe");
            source.addEventListener('message', function(event) {
              var msg = JSON.parse(event.data);
              $('.messages').append(
                "<div class=sender>"+msg.sender+"</div>" +
                "<div class=message>"+msg.message+"</div>");
            });

            $('form').submit(function(e){
              e.preventDefault();
              $.post('/everyone', {
                sender: $('.name').text(),
                message: $('form .message').val()
              });
              $('form .message').val('');
            });
          });
        </script>
      </head>
      <body>
        <div class=messages></div>
        <span class=name>Anonymous</span>:
        <form>
          <input class="message" placeholder="Message..."/>
          <input type="submit" value="Send" />
        </form>
      </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


async def message(request: web.Request) -> web.Response:
    """Receive message and broadcast to all connected clients."""
    app = request.app
    data = await request.post()

    # Put message in each client's queue
    for queue in app[channels]:
        payload = json.dumps(dict(data))
        await queue.put(payload)
    
    return web.Response(text="OK")


async def subscribe(request: web.Request) -> web.StreamResponse:
    """SSE endpoint for clients to receive messages."""
    async with sse_response(request) as response:
        app = request.app
        queue: asyncio.Queue[str] = asyncio.Queue()
        
        # Register this client's queue
        app[channels].add(queue)
        print(f"Client joined. Total: {len(app[channels])}")
        
        try:
            while response.is_connected():
                # Wait for next message from queue
                payload = await queue.get()
                await response.send(payload)
                queue.task_done()
        finally:
            # Clean up on disconnect
            app[channels].remove(queue)
            print(f"Client left. Total: {len(app[channels])}")
    
    return response


if __name__ == "__main__":
    app = web.Application()
    app[channels] = set()

    app.router.add_route("GET", "/", chat)
    app.router.add_route("POST", "/everyone", message)
    app.router.add_route("GET", "/subscribe", subscribe)
    
    web.run_app(app, host="127.0.0.1", port=8080)
```

### Key Patterns

1. **Queue per client**: Each SSE connection gets its own `asyncio.Queue`
2. **Broadcast via iteration**: POST handler puts message in all queues
3. **Cleanup on disconnect**: Finally block removes queue from set
4. **JSON payload**: Use JSON for structured data (sender, message, timestamp)

## Graceful Shutdown

Production applications need to handle shutdown gracefully to avoid dropping messages and leaking resources.

### Complete Shutdown Example

```python
import asyncio
import json
import logging
from contextlib import suppress
from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, Optional, Set

from aiohttp import web
from aiohttp_sse import EventSourceResponse, sse_response
import weakref

# Use WeakSet to avoid memory leaks
streams_key = web.AppKey("streams_key", weakref.WeakSet["SSEResponse"])
worker_key = web.AppKey("worker_key", asyncio.Task[None])


class SSEResponse(EventSourceResponse):
    """Custom response with JSON serialization helper."""
    
    async def send_json(
        self,
        data: Dict[str, Any],
        id: Optional[str] = None,
        event: Optional[str] = None,
        retry: Optional[int] = None,
        json_dumps: Callable[[Any], str] = partial(json.dumps, indent=2),
    ) -> None:
        await self.send(json_dumps(data), id=id, event=event, retry=retry)


async def send_event(
    stream: SSEResponse,
    data: Dict[str, Any],
    event_id: str,
) -> None:
    """Send event with error handling."""
    try:
        await stream.send_json(data, id=event_id)
    except Exception:
        logging.exception("Exception when sending event: %s", event_id)


async def worker(app: web.Application) -> None:
    """Background task that broadcasts to all connected clients."""
    while True:
        now = datetime.now()
        
        # Prepare delay task first (fire-and-forget pattern)
        delay = asyncio.create_task(asyncio.sleep(1))
        
        # Send to all streams in parallel
        fs = []
        for stream in app[streams_key]:
            data = {
                "time": f"Server Time: {now}",
                "last_event_id": stream.last_event_id,
            }
            coro = send_event(stream, data, str(now.timestamp()))
            fs.append(coro)
        
        await asyncio.gather(*fs)
        await delay


async def on_startup(app: web.Application) -> None:
    """Initialize app state."""
    app[streams_key] = weakref.WeakSet[SSEResponse]()
    app[worker_key] = asyncio.create_task(worker(app))


async def clean_up(app: web.Application) -> None:
    """Clean up worker task on shutdown."""
    app[worker_key].cancel()
    with suppress(asyncio.CancelledError):
        await app[worker_key]


async def on_shutdown(app: web.Application) -> None:
    """Gracefully close all SSE connections."""
    waiters = []
    for stream in app[streams_key]:
        stream.stop_streaming()
        waiters.append(stream.wait())
    
    await asyncio.gather(*waiters, return_exceptions=True)
    app[streams_key].clear()


async def hello(request: web.Request) -> web.StreamResponse:
    """SSE endpoint with proper registration."""
    stream: SSEResponse = await sse_response(request, response_cls=SSEResponse)
    request.app[streams_key].add(stream)
    
    try:
        await stream.wait()
    finally:
        request.app[streams_key].discard(stream)
    
    return stream


async def index(_request: web.Request) -> web.Response:
    """HTML page."""
    html = """
    <html>
        <script>
            var source = new EventSource("/hello");
            source.addEventListener("message", event => {
                document.getElementById("response").innerText = event.data;
            });
        </script>
        <body>
            <h1>Live Updates:</h1>
            <pre id="response"></pre>
        </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


if __name__ == "__main__":
    app = web.Application()
    
    # Register lifecycle hooks
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.on_cleanup.append(clean_up)
    
    app.router.add_route("GET", "/hello", hello)
    app.router.add_route("GET", "/", index)
    
    web.run_app(app, host="127.0.0.1", port=8080)
```

### Shutdown Sequence

1. **on_shutdown**: Stop all streaming, wait for connections to close
2. **on_cleanup**: Cancel background worker tasks
3. **WeakSet**: Use weak references to avoid preventing garbage collection

## Custom Response Classes

Extend `EventSourceResponse` to add domain-specific methods:

```python
from aiohttp_sse import EventSourceResponse
import json


class JSONSSE(EventSourceResponse):
    """SSE response with built-in JSON serialization."""
    
    async def send_json(
        self,
        data: dict,
        event_type: str = "message",
        event_id: str = None,
    ):
        """Send data as JSON with automatic serialization."""
        json_data = json.dumps(data)
        await self.send(
            json_data,
            event=event_type,
            id=event_id
        )
    
    async def send_error(self, error_message: str):
        """Send error event."""
        await self.send_json(
            {"error": error_message},
            event_type="error"
        )


async def handler(request):
    from aiohttp_sse import sse_response
    
    async with sse_response(request, response_cls=JSONSSE) as resp:
        await resp.send_json({"status": "ok", "count": 42})
        await resp.send_error("Something went wrong")
    
    return resp
```

## Event-Driven Architecture

Use SSE with asyncio events for complex coordination:

```python
import asyncio
from aiohttp import web
from aiohttp_sse import sse_response


class EventBus:
    """Simple event bus for pub/sub pattern."""
    
    def __init__(self):
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
    
    def subscribe(self, channel: str) -> asyncio.Queue:
        """Subscribe to a channel, returns queue for receiving events."""
        if channel not in self._subscribers:
            self._subscribers[channel] = set()
        
        queue = asyncio.Queue()
        self._subscribers[channel].add(queue)
        return queue
    
    def unsubscribe(self, channel: str, queue: asyncio.Queue):
        """Unsubscribe from a channel."""
        self._subscribers[channel].discard(queue)
    
    async def publish(self, channel: str, data: str):
        """Publish event to all subscribers of a channel."""
        if channel not in self._subscribers:
            return
        
        for queue in self._subscribers[channel]:
            await queue.put(data)


# App setup
event_bus = EventBus()


async def subscribe_channel(request):
    """Subscribe to a specific channel."""
    channel = request.query.get("channel", "default")
    
    async with sse_response(request) as resp:
        queue = event_bus.subscribe(channel)
        
        try:
            while resp.is_connected():
                data = await queue.get()
                await resp.send(data, event=channel)
        finally:
            event_bus.unsubscribe(channel, queue)
    
    return resp


async def publish_event(request):
    """Publish an event to a channel."""
    data = await request.json()
    channel = data.get("channel", "default")
    message = data.get("message")
    
    await event_bus.publish(channel, message)
    return web.Response(text="Published")


app = web.Application()
app.router.add_route("GET", "/subscribe", subscribe_channel)
app.router.add_route("POST", "/publish", publish_event)
```

## Rate Limiting and Throttling

Prevent overwhelming clients with too many events:

```python
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    """Simple rate limiter for SSE connections."""
    
    def __init__(self, max_events: int = 100, window: timedelta = timedelta(minutes=1)):
        self.max_events = max_events
        self.window = window
        self._counts: Dict[int, list] = defaultdict(list)
    
    async def allow(self, connection_id: int) -> bool:
        """Check if event can be sent."""
        now = datetime.now()
        counts = self._counts[connection_id]
        
        # Remove old entries
        cutoff = now - self.window
        self._counts[connection_id] = [
            ts for ts in counts if ts > cutoff
        ]
        
        if len(self._counts[connection_id]) >= self.max_events:
            return False
        
        self._counts[connection_id].append(now)
        return True


limiter = RateLimiter(max_events=100, window=timedelta(minutes=1))


async def rate_limited_stream(request):
    async with sse_response(request) as resp:
        conn_id = id(resp)
        counter = 0
        
        while resp.is_connected():
            if await limiter.allow(conn_id):
                await resp.send(f"Event {counter}")
                counter += 1
            else:
                await resp.send("Rate limit reached, slowing down", event="warning")
            
            await asyncio.sleep(0.5)
    
    return resp
```

## Broadcasting to All Clients

Efficient pattern for sending to all connected clients:

```python
import weakref
from aiohttp import web
from aiohttp_sse import sse_response


class BroadcastManager:
    """Manage broadcast to all SSE connections."""
    
    def __init__(self):
        self._streams = weakref.WeakSet()
    
    def register(self, stream):
        self._streams.add(stream)
    
    def unregister(self, stream):
        self._streams.discard(stream)
    
    async def broadcast(self, data: str, event: str = "message"):
        """Send to all connected clients."""
        tasks = []
        for stream in self._streams:
            if stream.is_connected():
                tasks.append(stream.send(data, event=event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


broadcast = BroadcastManager()


async def handler(request):
    async with sse_response(request) as resp:
        broadcast.register(resp)
        try:
            await resp.wait()
        finally:
            broadcast.unregister(resp)
    
    return resp


async def admin_broadcast(request):
    """Admin endpoint to broadcast message."""
    data = await request.json()
    await broadcast.broadcast(data["message"])
    return web.Response(text="Broadcast sent")
