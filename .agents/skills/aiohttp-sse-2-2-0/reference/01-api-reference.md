# aiohttp-sse API Reference

## Contents
- EventSourceResponse
- sse_response()

## EventSourceResponse

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

## sse_response()

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
