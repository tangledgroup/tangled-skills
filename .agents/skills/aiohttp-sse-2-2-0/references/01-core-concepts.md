# Core Concepts

This reference covers the fundamental concepts of Server-Sent Events (SSE) and how aiohttp-sse implements them.

## What Are Server-Sent Events?

Server-Sent Events (SSE) is a standard protocol that allows servers to push data to clients over HTTP. Unlike WebSockets which provide bidirectional communication, SSE is optimized for one-way server-to-client streaming.

### Key Characteristics

- **Unidirectional**: Server sends, client receives
- **Automatic reconnection**: Clients automatically reconnect on disconnection
- **Text-based**: All data transmitted as UTF-8 text
- **Standard HTTP**: Uses regular HTTP connections (port 80/443)
- **Native browser support**: Built-in EventSource API in all modern browsers

### SSE vs WebSockets

| Feature | SSE | WebSockets |
|---------|-----|------------|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WebSocket (wss://) |
| Reconnection | Automatic | Manual implementation |
| Complexity | Simple | More complex |
| Browser Support | Native EventSource | Native WebSocket |
| Use Case | Notifications, feeds | Real-time games, chat |

## EventSource Protocol Format

SSE messages follow a specific text format:

```
event: message-type
id: 123
data: This is the event data
retry: 3000

```

### Field Descriptions

- **`data:`** - The payload (required). Can span multiple lines
- **`event:`** - Event type for client-side filtering (default: "message")
- **`id:`** - Event ID for reconnection tracking
- **`retry:`** - Reconnection delay in milliseconds
- **Empty line** - Terminates the message (required)

### Multi-line Data

Data fields can contain multiple lines:

```
data: Line 1
data: Line 2
data: Line 3

```

Client receives: `"Line 1\nLine 2\nLine 3"`

## aiohttp-sse Implementation

### EventSourceResponse Class

The core class for creating SSE responses:

```python
from aiohttp_sse import EventSourceResponse


async def handler(request):
    resp = EventSourceResponse()
    await resp.prepare(request)
    
    # Send events
    await resp.send("Hello")
    await resp.send("World", event="greeting")
    
    resp.stop_streaming()
    await resp.wait()
    return resp
```

### sse_response Helper Function

Convenient context manager wrapper:

```python
from aiohttp_sse import sse_response


async def handler(request):
    async with sse_response(request) as resp:
        await resp.send("Hello")
        await resp.send("World")
    return resp
```

The context manager automatically handles:
- Response preparation
- Ping task creation
- Cleanup on exit
- Error handling

### Automatic Headers

aiohttp-sse sets these headers automatically:

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**Important**: The `X-Accel-Buffering: no` header prevents Nginx from buffering the response, which is critical for SSE to work properly behind reverse proxies.

## Client-Side EventSource API

### Basic Connection

```javascript
var source = new EventSource('/stream');

source.addEventListener('message', (event) => {
    console.log('Received:', event.data);
});
```

### Handling Different Event Types

```javascript
var source = new EventSource('/notifications');

source.addEventListener('message', (event) => {
    console.log('Default message:', event.data);
});

source.addEventListener('alert', (event) => {
    alert(event.data);
});

source.addEventListener('update', (event) => {
    updateUI(event.data);
});
```

### Event Object Properties

Each event provides:

```javascript
source.addEventListener('message', (event) => {
    console.log(event.data);      // Message data (string)
    console.log(event.type);      // Event type (e.g., "message", "alert")
    console.log(event.lastEventId); // Last received event ID
});
```

### Reconnection Handling

EventSource automatically reconnects. Track connection state:

```javascript
var source = new EventSource('/stream');

source.addEventListener('open', () => {
    console.log('Connected');
});

source.addEventListener('error', (event) => {
    if (event.target.readyState === EventSource.CLOSED) {
        console.log('Connection closed permanently');
    } else {
        console.log('Reconnecting...');
    }
});
```

### Manual Reconnection with Last Event ID

Server can resume from last received event:

```javascript
var source = new EventSource('/stream');

source.addEventListener('error', () => {
    // On reconnect, send last event ID
    var lastId = source.lastEventId;
    source.close();
    
    // Reconnect with Last-Event-ID header
    source = new EventSource(`/stream?last_event_id=${lastId}`);
});
```

Server reads the ID:

```python
async def handler(request):
    async with sse_response(request) as resp:
        last_id = resp.last_event_id  # From Last-Event-ID header
        if last_id:
            print(f"Client reconnected from event {last_id}")
            # Resume streaming from last_id
```

## Ping Mechanism

aiohttp-sse sends periodic ping messages to keep connections alive:

```python
resp = EventSourceResponse()
resp.ping_interval = 30  # Send ping every 30 seconds (default: 15)
```

Pings appear as: `: ping` in the stream. Browsers ignore lines starting with `:`.

## Connection Lifecycle

### Server-Side States

1. **Created**: `EventSourceResponse()` instantiated
2. **Prepared**: `await resp.prepare(request)` - headers sent
3. **Streaming**: `await resp.send(data)` - sending events
4. **Stopped**: `resp.stop_streaming()` - ping task cancelled
5. **Waited**: `await resp.wait()` - connection closed

### Client-Side States (EventSource.readyState)

- `CONNECTING` (0): Establishing connection
- `OPEN` (1): Connection active, receiving events
- `CLOSED` (2): Connection terminated

## Text Encoding

All SSE data is UTF-8 encoded:

```python
async def unicode_handler(request):
    async with sse_response(request) as resp:
        await resp.send("Hello 世界 🌍")  # UTF-8 works automatically
    return resp
```

No manual encoding needed - aiohttp-sse handles it.

## Error Handling

### ConnectionResetError

Client disconnects during send:

```python
async def handler(request):
    async with sse_response(request) as resp:
        try:
            await resp.send("data")
        except ConnectionResetError:
            print("Client disconnected")
    return resp
```

### Automatic Cleanup

Context manager handles cleanup:

```python
async def handler(request):
    async with sse_response(request) as resp:
        while resp.is_connected():
            await resp.send("data")
            await asyncio.sleep(1)
    # Ping task automatically stopped here
    return resp
```
