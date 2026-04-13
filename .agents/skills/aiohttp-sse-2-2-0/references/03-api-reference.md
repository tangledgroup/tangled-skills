# API Reference

Complete documentation of the aiohttp-sse v2.2.0 API including all classes, methods, and parameters.

## EventSourceResponse

Main class for creating Server-Sent Events responses. Inherits from `aiohttp.web.StreamResponse`.

### Constructor

```python
EventSourceResponse(
    *,
    status: int = 200,
    reason: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
    sep: Optional[str] = None
)
```

**Parameters:**
- `status` - HTTP status code (default: 200)
- `reason` - Status reason phrase (optional)
- `headers` - Additional HTTP headers to set (optional)
- `sep` - Line separator for SSE format (default: "\r\n")

**Example:**
```python
resp = EventSourceResponse(
    status=200,
    headers={"X-Custom-Header": "value"}
)
```

### send()

Send an SSE event to the client.

```python
await response.send(
    data: str,
    id: Optional[str] = None,
    event: Optional[str] = None,
    retry: Optional[int] = None
) -> None
```

**Parameters:**
- `data` - The event payload (required). Can contain newlines.
- `id` - Event ID for reconnection tracking. Client receives this in `event.lastEventId`.
- `event` - Event type name. Default is "message". Used with `addEventListener('type', ...)`.
- `retry` - Reconnection time in milliseconds. Must be an integer.

**Raises:**
- `TypeError` - If `retry` is not an integer
- `ConnectionResetError` - If client disconnected during send

**Examples:**

Basic message:
```python
await resp.send("Hello, World!")
# Output: data: Hello, World!\r\n\r\n
```

With event type:
```python
await resp.send("User logged in", event="user_event")
# Output: event: user_event\r\ndata: User logged in\r\n\r\n
```

With event ID:
```python
await resp.send("Update 42", id="42")
# Output: id: 42\r\ndata: Update 42\r\n\r\n
```

With retry:
```python
await resp.send("Initial data", retry=5000)
# Output: data: Initial data\r\nretry: 5000\r\n\r\n
```

All parameters:
```python
await resp.send(
    data="Full event",
    id="evt_123",
    event="notification",
    retry=3000
)
# Output: id: evt_123\r\nevent: notification\r\ndata: Full event\r\nretry: 3000\r\n\r\n
```

Multi-line data:
```python
await resp.send("Line 1\nLine 2\nLine 3")
# Output: data: Line 1\r\ndata: Line 2\r\ndata: Line 3\r\n\r\n
```

### prepare()

Prepare the response and send HTTP headers to the client.

```python
await response.prepare(request: BaseRequest) -> Optional[AbstractStreamWriter]
```

**Parameters:**
- `request` - The aiohttp web.Request object

**Returns:**
- `AbstractStreamWriter` if preparation succeeded, `None` otherwise

**Raises:**
- `asyncio.CancelledError` - If client disconnected before preparation

**Example:**
```python
resp = EventSourceResponse()
await resp.prepare(request)
# Now safe to call send()
await resp.send("data")
```

**Note:** When using `sse_response()` context manager, `prepare()` is called automatically.

### is_connected()

Check if the connection is still active.

```python
response.is_connected() -> bool
```

**Returns:**
- `True` if response is prepared and ping task is running
- `False` if not prepared, or ping task is done/cancelled

**Example:**
```python
async with sse_response(request) as resp:
    while resp.is_connected():
        await resp.send("data")
        await asyncio.sleep(1)
    # Loop exits when client disconnects
```

### wait()

Wait for the connection to close.

```python
await response.wait() -> None
```

**Raises:**
- `RuntimeError` - If response was not started (prepare() not called)
- `asyncio.CancelledError` - If ping task was cancelled

**Example:**
```python
resp = EventSourceResponse()
await resp.prepare(request)

# Run other tasks while waiting
async with asyncio.TaskGroup() as tg:
    tg.create_task(resp.wait())
    tg.create_task(send_periodic_data(resp))
```

### stop_streaming()

Stop the ping task and prepare for shutdown.

```python
response.stop_streaming() -> None
```

**Raises:**
- `RuntimeError` - If response was not started

**Example:**
```python
resp = EventSourceResponse()
await resp.prepare(request)

# Send some data
await resp.send("final message")

# Stop streaming
resp.stop_streaming()
await resp.wait()  # Wait for cleanup
```

### last_event_id

Property to access the Last-Event-ID header from the client.

```python
response.last_event_id -> Optional[str]
```

**Returns:**
- The value of the `Last-Event-ID` request header, or `None` if not present

**Raises:**
- `RuntimeError` - If response was not prepared

**Example:**
```python
async with sse_response(request) as resp:
    last_id = resp.last_event_id
    if last_id:
        print(f"Client reconnected from event {last_id}")
        # Resume streaming from last_id
```

### ping_interval

Property to get or set the ping interval in seconds.

```python
response.ping_interval -> float
```

**Default:** 15 seconds

**Constraints:**
- Must be int or float
- Must be >= 0

**Raises:**
- `TypeError` - If value is not int or float
- `ValueError` - If value is negative

**Examples:**
```python
resp = EventSourceResponse()
resp.ping_interval = 30  # Ping every 30 seconds
print(resp.ping_interval)  # 30

# Invalid values
resp.ping_interval = "10"  # TypeError
resp.ping_interval = -5    # ValueError
```

**Note:** Pings are sent as `: ping` which browsers ignore but keep the connection alive.

### enable_compression()

Not implemented - raises NotImplementedError.

```python
response.enable_compression(force: Union[bool, ContentCoding, None] = False) -> None
```

**Raises:**
- `NotImplementedError` - Always

SSE streams should not be compressed as they're sent in real-time chunks.

## sse_response()

Context manager helper function for creating SSE responses.

### Signature

```python
def sse_response(
    request: Request,
    *,
    status: int = 200,
    reason: Optional[str] = None,
    headers: Optional[Mapping[str, str]] = None,
    sep: Optional[str] = None,
    response_cls: Type[EventSourceResponse] = EventSourceResponse
) -> _ContextManager[EventSourceResponse]
```

**Parameters:**
- `request` - The aiohttp web.Request object (required)
- `status` - HTTP status code (default: 200)
- `reason` - Status reason phrase (optional)
- `headers` - Additional HTTP headers (optional)
- `sep` - Line separator for SSE format (default: "\r\n")
- `response_cls` - Response class to instantiate (default: EventSourceResponse)

**Returns:**
- Async context manager yielding an EventSourceResponse (or subclass)

**Raises:**
- `TypeError` - If `response_cls` is not a subclass of EventSourceResponse

### Basic Usage

```python
from aiohttp_sse import sse_response


async def handler(request):
    async with sse_response(request) as resp:
        await resp.send("Hello")
        await resp.send("World")
    return resp
```

### With Custom Headers

```python
async def handler(request):
    async with sse_response(
        request,
        headers={"X-Custom-Header": "value"}
    ) as resp:
        await resp.send("data")
    return resp
```

### With Custom Response Class

```python
class MySSE(EventSourceResponse):
    async def send_json(self, data):
        await self.send(json.dumps(data))


async def handler(request):
    async with sse_response(
        request,
        response_cls=MySSE
    ) as resp:
        await resp.send_json({"key": "value"})
    return resp
```

## Constants

### DEFAULT_PING_INTERVAL

Default ping interval in seconds.

```python
EventSourceResponse.DEFAULT_PING_INTERVAL = 15
```

### DEFAULT_SEPARATOR

Default line separator for SSE format.

```python
EventSourceResponse.DEFAULT_SEPARATOR = "\r\n"
```

### DEFAULT_LAST_EVENT_HEADER

Name of the header containing last event ID from client.

```python
EventSourceResponse.DEFAULT_LAST_EVENT_HEADER = "Last-Event-Id"
```

## Automatic Headers

EventSourceResponse automatically sets these headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Type` | `text/event-stream` | Identifies SSE stream |
| `Cache-Control` | `no-cache` | Prevents caching |
| `Connection` | `keep-alive` | Maintains connection |
| `X-Accel-Buffering` | `no` | Disables Nginx buffering |

### Custom Headers

Add custom headers via constructor or sse_response():

```python
# Constructor
resp = EventSourceResponse(headers={
    "X-Custom-Header": "value",
    "X-Another": "data"
})

# Context manager
async with sse_response(
    request,
    headers={"X-Custom": "value"}
) as resp:
    await resp.send("data")
```

## Type Hints

All public APIs are fully typed. Import types for custom implementations:

```python
from aiohttp_sse import EventSourceResponse
from aiohttp.web import StreamResponse, Request
from typing import Optional, Mapping


async def custom_handler(
    request: Request,
    response: EventSourceResponse
) -> StreamResponse:
    await response.send("data")
    return response
```

## Error Types

### RuntimeError

Raised when operations are performed before response is prepared:

```python
resp = EventSourceResponse()

await resp.wait()  # RuntimeError: Response is not started
resp.stop_streaming()  # RuntimeError: Response is not started
_ = resp.last_event_id  # RuntimeError: EventSource request must be prepared first
```

### TypeError

Raised for invalid argument types:

```python
resp = EventSourceResponse()

await resp.send("data", retry="10")  # TypeError: retry argument must be int
resp.ping_interval = "15"  # TypeError: ping interval must be int or float

async with sse_response(request, response_cls=str):
    ...  # TypeError: response_cls must be subclass of EventSourceResponse
```

### ValueError

Raised for invalid value ranges:

```python
resp = EventSourceResponse()
resp.ping_interval = -1  # ValueError: ping interval must be greater then 0
```

### ConnectionResetError

Raised when client disconnects during send:

```python
async with sse_response(request) as resp:
    try:
        await resp.send("data")
    except ConnectionResetError:
        print("Client disconnected")
```

## Version Information

```python
from aiohttp_sse import __version__

print(__version__)  # "2.2.0"
```
