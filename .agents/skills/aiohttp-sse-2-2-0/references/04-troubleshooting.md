# Troubleshooting

Common issues, debugging techniques, and best practices for aiohttp-sse applications.

## Connection Issues

### Events Not Reaching Client

**Symptoms:** Client connects but never receives events.

**Possible causes and solutions:**

1. **Server buffering (Nginx)**
   
   If using Nginx as reverse proxy, add:
   
   ```nginx
   location /sse {
       proxy_pass http://backend;
       proxy_buffering off;  # Critical!
       proxy_cache off;
       
       # SSE-specific headers
       proxy_set_header Connection "";
       proxy_http_version 1.1;
   }
   ```
   
   aiohttp-sse sets `X-Accel-Buffering: no` automatically, but explicit Nginx config helps.

2. **Async context not awaited**
   
   Ensure you're using `async with`:
   
   ```python
   # WRONG - events won't be sent
   def handler(request):
       resp = sse_response(request)
       resp.send("data")  # Never executed
       return resp
   
   # CORRECT
   async def handler(request):
       async with sse_response(request) as resp:
           await resp.send("data")  # Properly awaited
       return resp
   ```

3. **Loop exits too early**
   
   Check that your streaming loop continues:
   
   ```python
   # WRONG - sends once and exits
   async def handler(request):
       async with sse_response(request) as resp:
           await resp.send("data")
       return resp
   
   # CORRECT - keeps sending while connected
   async def handler(request):
       async with sse_response(request) as resp:
           while resp.is_connected():
               await resp.send("data")
               await asyncio.sleep(1)
       return resp
   ```

### Client Cannot Connect

**Symptoms:** EventSource constructor fails or immediately errors.

**Debug steps:**

1. **Check server response headers**
   
   Use browser DevTools Network tab to verify:
   - Status code is 200
   - `Content-Type: text/event-stream`
   - No CORS errors in console
   
   ```javascript
   var source = new EventSource('/stream');
   source.addEventListener('error', (event) => {
       console.error('SSE Error:', event);
       console.log('Ready state:', source.readyState);
   });
   ```

2. **Verify endpoint route**
   
   Ensure the route is registered:
   
   ```python
   app.router.add_route("GET", "/stream", handler)
   # NOT: app.router.add_get("/stream", handler)  # aiohttp 3.x uses add_route
   ```

3. **Check for middleware interference**
   
   Some middleware may close connections or modify headers. Test without middleware first.

## Memory Leaks

### Growing Memory in Chat Applications

**Symptoms:** Memory usage increases over time with multiple clients.

**Cause:** Strong references to disconnected clients prevent garbage collection.

**Solution:** Use `weakref.WeakSet` for tracking connections:

```python
import weakref
from aiohttp import web

# WRONG - causes memory leak
app[connections] = set()  # Regular set holds strong references

# CORRECT - WeakSet allows GC of disconnected clients
app[connections] = weakref.WeakSet()
```

**Complete pattern:**

```python
streams_key = web.AppKey("streams_key", weakref.WeakSet["EventSourceResponse"])


async def on_startup(app):
    app[streams_key] = weakref.WeakSet()


async def handler(request):
    async with sse_response(request) as resp:
        app[streams_key].add(resp)
        try:
            await resp.wait()
        finally:
            app[streams_key].discard(resp)
    return resp
```

### Queue Accumulation

**Symptoms:** Memory grows in pub/sub applications.

**Cause:** Queues not cleaned up on disconnect.

**Solution:** Always remove queues in finally block:

```python
async def subscribe(request):
    queue = asyncio.Queue()
    app[queues].add(queue)
    
    try:
        async with sse_response(request) as resp:
            while resp.is_connected():
                item = await queue.get()
                await resp.send(item)
    finally:
        app[queues].remove(queue)  # Critical cleanup
```

## Performance Issues

### Slow Event Delivery

**Symptoms:** Events take seconds to reach clients.

**Solutions:**

1. **Reduce ping interval**
   
   Default 15-second ping may be too long for some proxies:
   
   ```python
   resp = EventSourceResponse()
   resp.ping_interval = 5  # More frequent pings
   ```

2. **Avoid blocking operations in send loop**
   
   ```python
   # WRONG - blocks the event loop
   async def handler(request):
       async with sse_response(request) as resp:
           while resp.is_connected():
               data = heavy_computation()  # Blocks!
               await resp.send(str(data))
       
   # CORRECT - run blocking code in executor
   async def handler(request):
       loop = asyncio.get_event_loop()
       async with sse_response(request) as resp:
           while resp.is_connected():
               data = await loop.run_in_executor(None, heavy_computation)
               await resp.send(str(data))
   ```

3. **Batch sends efficiently**
   
   ```python
   # Inefficient - many small writes
   for item in items:
       await resp.send(item)
       await asyncio.sleep(0.01)
   
   # Better - batch into single message
   batch = "\n".join(items)
   await resp.send(batch)
   ```

### High CPU Usage

**Symptoms:** Server CPU spikes with many connected clients.

**Causes and solutions:**

1. **Too-frequent pings**
   
   ```python
   # Bad - ping every second with 1000 clients = 1000 writes/sec
   resp.ping_interval = 1
   
   # Better - default 15 seconds is usually fine
   resp.ping_interval = 15
   ```

2. **Inefficient broadcast**
   
   ```python
   # Bad - sequential sends
   for stream in streams:
       await stream.send(data)  # Waits for each
   
   # Better - parallel sends
   tasks = [stream.send(data) for stream in streams if stream.is_connected()]
   await asyncio.gather(*tasks, return_exceptions=True)
   ```

## Error Handling

### Client Disconnect During Send

**Symptoms:** `ConnectionResetError` exceptions in logs.

**Solution:** Catch and handle gracefully:

```python
async def handler(request):
    async with sse_response(request) as resp:
        try:
            while resp.is_connected():
                await resp.send("data")
                await asyncio.sleep(1)
        except ConnectionResetError:
            logging.info("Client disconnected")
            return resp
```

**Note:** Context manager handles cleanup automatically, so just return.

### Background Task Errors

**Symptoms:** Worker tasks crash and stop broadcasting.

**Solution:** Use `return_exceptions=True` with gather:

```python
async def broadcast(data):
    tasks = [stream.send(data) for stream in streams]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Log errors but continue
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f"Stream {i} error: {result}")
```

### Reconnection Storms

**Symptoms:** All clients reconnect simultaneously after outage.

**Solution:** Add exponential backoff on client side:

```javascript
var source = new EventSource('/stream');

let reconnectDelay = 1000;
source.addEventListener('error', () => {
    source.close();
    
    setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000); // Max 30s
        source = new EventSource('/stream');
    }, reconnectDelay);
});

source.addEventListener('open', () => {
    reconnectDelay = 1000; // Reset on successful connect
});
```

## Debugging Techniques

### Enable Request Logging

Log all SSE activity:

```python
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sse')


async def handler(request):
    logger.info(f"Client connected: {request.remote}")
    
    async with sse_response(request) as resp:
        event_count = 0
        try:
            while resp.is_connected():
                await resp.send(f"Event {event_count}")
                event_count += 1
                logger.debug(f"Sent event {event_count} to {request.remote}")
                await asyncio.sleep(1)
        except ConnectionResetError:
            logger.info(f"Client disconnected after {event_count} events")
    
    return resp
```

### Monitor Active Connections

Track connection count in real-time:

```python
from aiohttp import web
import weakref


class ConnectionTracker:
    def __init__(self):
        self._connections = weakref.WeakSet()
    
    def add(self, conn):
        self._connections.add(conn)
    
    def remove(self, conn):
        self._connections.discard(conn)
    
    @property
    def count(self):
        return len(self._connections)


tracker = ConnectionTracker()


async def handler(request):
    async with sse_response(request) as resp:
        tracker.add(resp)
        try:
            await resp.wait()
        finally:
            tracker.remove(resp)
    return resp


async def stats(request):
    return web.json_response({
        "active_connections": tracker.count
    })


app.router.add_get("/stats", stats)
```

### Test with curl

Test SSE endpoint without browser:

```bash
# Basic test
curl -N http://localhost:8080/stream

# Should see events streaming in real-time
# Press Ctrl+C to disconnect
```

**Expected output:**
```
data: Event 0

data: Event 1

data: Event 2

: ping

data: Event 3
```

### Test with Python Client

Create a test client script:

```python
import asyncio
import aiohttp


async def test_sse():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8080/stream') as resp:
            async for line in resp.content.iter_any():
                print(f"Received: {line}")


asyncio.run(test_sse())
```

## Best Practices

### Always Use Context Manager

Prevents resource leaks:

```python
# Recommended
async with sse_response(request) as resp:
    await resp.send("data")

# Avoid manual cleanup unless necessary
resp = EventSourceResponse()
await resp.prepare(request)
try:
    await resp.send("data")
finally:
    resp.stop_streaming()
    await resp.wait()
```

### Validate retry Parameter

Ensure retry is integer:

```python
await resp.send("data", retry=3000)  # OK - integer
await resp.send("data", retry="3000")  # TypeError!
```

### Handle JSON Serialization Errors

When sending JSON:

```python
import json


async def send_json_safe(resp, data):
    try:
        json_str = json.dumps(data)
        await resp.send(json_str)
    except (TypeError, ValueError) as e:
        logging.error(f"JSON serialization failed: {e}")
        await resp.send(f"Error: {str(e)}", event="error")
```

### Set Reasonable Timeouts

Prevent infinite streams in development:

```python
async def handler(request):
    async with sse_response(request) as resp:
        start = asyncio.get_event_loop().time()
        
        while resp.is_connected():
            # Timeout after 1 hour
            if asyncio.get_event_loop().time() - start > 3600:
                await resp.send("Session expired", event="timeout")
                break
            
            await resp.send("data")
            await asyncio.sleep(1)
    
    return resp
```

### Document Event Contract

Clearly document what events clients can expect:

```python
"""
SSE Event Types:
- message: Regular message data (JSON: {"text": "...", "sender": "..."})
- error: Error notification (JSON: {"error": "message"})
- heartbeat: Keepalive ping (no data)
- update: System updates (JSON: {"type": "...", "payload": {...}})
"""
