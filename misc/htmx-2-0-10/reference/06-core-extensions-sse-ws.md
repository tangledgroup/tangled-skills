# Core Extensions: SSE and WebSockets

Real-time communication extensions for htmx.

## Server-Sent Events (SSE) Extension

Uni-directional server-to-client streaming over HTTP. Lightweight alternative to WebSockets; works through proxies and firewalls easily. Cannot send messages to the server after connection is established.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-sse@2.2.4"></script>
<body hx-ext="sse">
```

Or via npm: `npm install htmx-ext-sse`

### Attributes

| Attribute | Description |
|-----------|-------------|
| `sse-connect="<url>"` | URL of the SSE server (EventSource endpoint) |
| `sse-swap="<message-name>"` | Name of SSE event to swap into the DOM |
| `sse-close="<message-name>"` | Close connection when this message is received |

### Basic Usage

```html
<div hx-ext="sse" sse-connect="/chatroom" sse-swap="message">
  Contents updated in real time
</div>
```

### Connecting with Parameters

SSE works like any HTTP request — pass parameters via query string:

```html
<div hx-ext="sse" sse-connect="/updates?friends=true&format=detailed"></div>
```

### Named Events

Server sends:
```
event: EventName
data: <div>Content to swap in.</div>
```

Client listens:
```html
<div hx-ext="sse" sse-connect="/events" sse-swap="EventName"></div>
```

The event name must match exactly. Browsers only listen for explicitly named events.

### Unnamed Events

Unnamed messages use the default name `message`:
```html
<div hx-ext="sse" sse-connect="/events" sse-swap="message"></div>
```

No catch-all option exists — you must specify `sse-swap="message"`.

### Multiple Events

```html
<!-- Multiple events on same element -->
<div hx-ext="sse" sse-connect="/server" sse-swap="event1,event2"></div>

<!-- Different elements, same source -->
<div hx-ext="sse" sse-connect="/server">
  <div sse-swap="event1"></div>
  <div sse-swap="event2"></div>
</div>
```

### Trigger HTTP Callbacks from SSE

Use `hx-trigger="sse:<event_name>"` to fire AJAX requests when SSE events arrive:

```html
<div hx-ext="sse" sse-connect="/event_stream">
  <div hx-get="/chatroom" hx-trigger="sse:chatter">
    Updates when 'chatter' event fires
  </div>
</div>
```

### Automatic Reconnection

Browser reconnects automatically on SSE disconnect. The extension adds exponential-backoff reconnection logic on top for reliability.

### SSE Events

| Event | Timing | Detail |
|-------|--------|--------|
| `htmx:sseOpen` | Connection established | `elt`, `source` (EventSource) |
| `htmx:sseError` | Connection error | `error`, `source` |
| `htmx:sseBeforeMessage` | Before swap | `elt` — cancelable via `preventDefault()` |
| `htmx:sseMessage` | After swap | `elt` |
| `htmx:sseClose` | Connection closed | `elt`, `type` (nodeMissing/nodeReplaced/message) |

```javascript
document.body.addEventListener('htmx:sseBeforeMessage', function(e) {
  // Do something before data is swapped in
});
```

### Migration from hx-sse

| Old | New |
|-----|-----|
| `hx-sse=""` | `hx-ext="sse"` |
| `hx-sse="connect:<url>"` | `sse-connect="<url>"` |
| `hx-sse="swap:<EventName>"` | `sse-swap="<EventName>"` |
| `hx-trigger="sse:<EventName>"` | No change |

---

## WebSocket Extension

Bi-directional real-time communication. Supports sending and receiving messages, automatic reconnection with full-jitter backoff, and message queuing.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.4"></script>
<body hx-ext="ws">
```

Or via npm: `npm install htmx-ext-ws`

### Attributes

| Attribute | Description |
|-----------|-------------|
| `ws-connect="<url>"` | WebSocket URL (auto-prefixes ws/wss from page scheme) |
| `ws-send` | Send form data as JSON to nearest WebSocket on trigger |

### Configuration

```javascript
htmx.config.createWebSocket = function(url) { return new WebSocket(url); };
htmx.config.wsBinaryType = 'blob'; // or 'arraybuffer'
htmx.config.wsReconnectDelay = function(retryCount) { return retryCount * 1000; };
```

### Basic Usage

```html
<div hx-ext="ws" ws-connect="/chatroom">
  <div id="notifications"></div>
  <div id="chat_room">...</div>
  <form ws-send>
    <input name="chat_message" />
  </form>
</div>
```

### Receiving Messages

Content sent from the WebSocket server is parsed as HTML and swapped using OOB logic (by `id`):

```html
<!-- Server sends: -->
<form id="form">...</form>
<!-- Interpreted as hx-swap-oob="true" by default -->

<div id="notifications" hx-swap-oob="beforeend">
  New message received
</div>

<div id="chat_room" hx-swap-oob="morphdom">
  ...morphed content...
</div>
```

### Sending Messages

`ws-send` serializes form values as JSON and sends to the nearest enclosing WebSocket. Includes a `HEADERS` field with standard htmx headers.

```html
<form ws-send>
  <input name="action" value="join" />
  <input name="room" value="general" />
</form>
```

### Automatic Reconnection

Reconnects on `Abnormal Closure`, `Service Restart`, or `Try Again Later` using full-jitter exponential backoff. Customize via `htmx.config.wsReconnectDelay`.

Messages are queued in memory when socket is not `OPEN` and sent when connection restores.

### Socket Wrapper API

Exposed in all WebSocket events as `detail.socketWrapper`:

| Method/Property | Description |
|-----------------|-------------|
| `send(message, fromElt)` | Send safely (queues if not open) |
| `sendImmediately(message, fromElt)` | Send regardless of state (may fail) |
| `queue` | Array of pending messages |

```javascript
document.body.addEventListener('htmx:wsOpen', function(evt) {
  const wrapper = evt.detail.socketWrapper;
  wrapper.send(JSON.stringify({ type: 'ping' }));
});
```

### WebSocket Events

| Event | Timing | Cancelable | Detail |
|-------|--------|------------|--------|
| `htmx:wsConnecting` | Connection attempt | No | `event.type` |
| `htmx:wsOpen` | Connected | No | `elt`, `event`, `socketWrapper` |
| `htmx:wsClose` | Closed | No | `elt`, `event`, `socketWrapper` |
| `htmx:wsError` | Error | No | `elt`, `error`, `socketWrapper` |
| `htmx:wsBeforeMessage` | Message received | Yes | `elt`, `message`, `socketWrapper` |
| `htmx:wsAfterMessage` | After processing | No | `elt`, `message`, `socketWrapper` |
| `htmx:wsConfigSend` | Before sending | Yes | `parameters`, `headers`, `messageBody`, `elt`, `socketWrapper` |
| `htmx:wsBeforeSend` | Just before send | Yes | `elt`, `message`, `socketWrapper` |
| `htmx:wsAfterSend` | After send | No | `elt`, `message`, `socketWrapper` |

### Custom Message Format

Override default JSON serialization via `htmx:wsConfigSend`:

```javascript
document.body.addEventListener('htmx:wsConfigSend', function(evt) {
  // Send as MessagePack instead of JSON
  evt.detail.messageBody = msgpack.encode(evt.detail.parameters);
});
```

### Migration from hx-ws

| Old | New |
|-----|-----|
| `hx-ws=""` | `hx-ext="ws"` |
| `hx-ws="connect:<url>"` | `ws-connect="<url>"` |
| `hx-ws="send"` | `ws-send` |
