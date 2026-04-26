# WebSockets and SSE

WebSockets and Server-Sent Events (SSE) are supported via extensions in htmx 2.x. Both must be loaded as separate extension scripts before use.

## SSE Extension

Server-Sent Events provide a one-way communication channel from server to client. Install the SSE extension:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-sse@2.0.0/dist/sse.js"></script>
```

### Establishing an SSE Connection

Use `ext="sse"` and `hx-sse` to connect:

```html
<div hx-ext="sse" sse-connect="/stream">
    <div sse-swap="message">Waiting for messages...</div>
</div>
```

`sse-connect` opens the SSE connection to the given URL. `sse-swap` listens for events and swaps their content into the element.

### Event Types

By default, `sse-swap="message"` listens for events named "message". Specify a different event name:

```html
<div hx-ext="sse" sse-connect="/events">
    <div sse-swap="user-update">Waiting...</div>
    <div sse-swap="system-alert">Waiting...</div>
</div>
```

### Triggering Requests from SSE

Use `hx-trigger` with SSE event names to trigger AJAX requests:

```html
<div hx-ext="sse" sse-connect="/stream">
    <div hx-get="/update" hx-trigger="sse:notification" id="target">
        Ready
    </div>
</div>
```

When an SSE event named "notification" arrives, a GET request is issued to `/update`.

## WebSocket Extension

WebSockets provide full-duplex communication. Install the WS extension:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.0/dist/ws.js"></script>
```

### Establishing a WebSocket Connection

Use `hx-ext="ws"` and `ws-connect`:

```html
<div hx-ext="ws" ws-connect="/socket">
    <div>Chat messages appear here</div>
</div>
```

This opens a WebSocket connection. All htmx attributes on children of this element send their requests over the WebSocket instead of HTTP.

### Sending Messages

Any htmx-triggered request from a child element sends over the WebSocket:

```html
<div hx-ext="ws" ws-connect="/chat">
    <form hx-post="/chat" hx-trigger="submit">
        <input name="message">
        <button>Send</button>
    </form>
    <div id="messages"></div>
</div>
```

The form POST is sent as a WebSocket message. The response is swapped into the target.

### Configuration

- **`htmx.config.wsReconnectDelay`** — Default `full-jitter`. Controls reconnection delay strategy.
- **`htmx.config.wsBinaryType`** — Default `blob`. Type of binary data received over WebSocket.

## Choosing Between SSE and WebSockets

- Use **SSE** for server-to-client streaming (notifications, live updates, logs)
- Use **WebSockets** for bidirectional communication (chat, collaborative editing, real-time games)
- SSE works over standard HTTP and is simpler to implement on the server side
- WebSockets require a WebSocket-capable server but support client-initiated messages
