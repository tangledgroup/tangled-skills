# Real-time Communication: SSE and WebSockets

## Server-Sent Events (SSE)

SSE provides one-way server-to-client streaming. Ideal for notifications, live updates, and real-time data feeds.

### Installation

Include the SSE extension:

```html
<script src="/path/to/htmx.min.js"></script>
<script src="/path/to/ext/sse.js"></script>
```

### Connecting to SSE Stream

Use `hx-sse:connect` to establish connection:

```html
<!-- Connect to SSE endpoint -->
<div hx-sse:connect="/events/stream">
  <!-- Event listeners go here -->
</div>
```

Connection persists for page lifetime. htmx automatically reconnects on disconnect.

### Listening for Events

Use `hx-sse:swap` to listen for specific events and swap content:

```html
<div hx-sse:connect="/events/stream">
  <!-- Listen for 'message' event -->
  <div id="messages" hx-sse:swap="message"></div>
  
  <!-- Listen for 'notification' event -->
  <div id="notifications" hx-sse:swap="notification"></div>
  
  <!-- Listen for 'tick' event -->
  <div id="clock" hx-sse:swap="tick"></div>
</div>
```

Each `hx-sse:swap` element receives content when its named event fires.

### Server-Side Format

Server sends events in SSE format:

```
event: message
data: <div class="msg">New message received!</div>

event: notification
data: <div class="alert">You have a notification</div>

event: tick
data: <span id="clock">12:34:56</span>
```

Or simple data without event name (uses `message` event):

```
data: <p>Simple update</p>
```

### Full Example

```html
<!DOCTYPE html>
<html>
<head>
  <script src="/htmx.min.js"></script>
  <script src="/ext/sse.js"></script>
</head>
<body>
  <div hx-sse:connect="/api/events">
    <!-- Chat messages -->
    <div id="chat" hx-sse:swap="chat_message">
      <p>Waiting for messages...</p>
    </div>
    
    <!-- User count -->
    <div id="users" hx-sse:swap="user_count">
      <span>0 users online</span>
    </div>
    
    <!-- System notifications -->
    <div id="system" hx-sse:swap="system_alert"></div>
  </div>
  
  <form hx-post="/api/chat/message" hx-swap="none">
    <input name="message" placeholder="Type message...">
    <button type="submit">Send</button>
  </form>
</body>
</html>
```

Server (Express.js example):

```javascript
app.get('/api/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  const sendEvent = (eventName, data) => {
    res.write(`event: ${eventName}\n`);
    res.write(`data: ${data}\n\n`);
  };
  
  // Send initial user count
  sendEvent('user_count', '<span>1 user online</span>');
  
  // Broadcast to all connected clients
  const broadcast = (eventName, data) => {
    app.get('/api/events').req.socket?.write(`event: ${eventName}\ndata: ${data}\n\n`);
  };
  
  req.on('close', () => {
    // Client disconnected
  });
});

app.post('/api/chat/message', (req, res) => {
  const message = req.body.message;
  broadcast('chat_message', `<div class="msg">${message}</div>`);
  res.send('OK');
});
```

### SSE with Authentication

Include tokens in connection:

```html
<!-- Token in URL -->
<div hx-sse:connect='/events/stream?token=${localStorage.getItem("authToken")}'">
  <div id="updates" hx-sse:swap="update"></div>
</div>

<!-- Token in headers -->
<div hx-sse:connect="/events/stream"
     hx-sse:headers='{"Authorization": "Bearer " + localStorage.getItem("token")}'>
  <div id="updates" hx-sse:swap="update"></div>
</div>
```

### Reconnection Behavior

htmx automatically reconnects with exponential backoff:

- Initial delay: 1 second
- Maximum delay: 30 seconds
- Reconnects indefinitely until page unload

Customize reconnection:

```javascript
htmx.config.sseReconnectDelay = 'full-jitter'; // or 'fast-smooth'
```

### Triggering Requests from SSE

Use SSE events to trigger htmx requests:

```html
<div hx-sse:connect="/events">
  <!-- When 'refresh' event fires, reload data -->
  <div id="data" 
       hx-get="/api/data" 
       hx-trigger="sse:refresh"
       hx-sse:swap="update">
    Loading...
  </div>
</div>
```

Server sends:

```
event: refresh
```

Client triggers `hx-get` request automatically.

## WebSockets

WebSockets provide bidirectional real-time communication. Ideal for chat, collaborative editing, and live gaming.

### Installation

Include the WebSocket extension:

```html
<script src="/path/to/htmx.min.js"></script>
<script src="/path/to/ext/ws.js"></script>
```

### Connecting to WebSocket

Use `hx-ws:connect` to establish connection:

```html
<!-- Connect to WebSocket endpoint -->
<div hx-ws:connect="ws://example.com/socket">
  <!-- WebSocket event listeners go here -->
</div>

<!-- With authentication token -->
<div hx-ws:connect='ws://example.com/socket?token=${localStorage.getItem("token")}'>
  <div id="chat" hx-ws:send="message"></div>
</div>
```

### Sending Messages

Use `hx-ws:send` to send data over WebSocket:

```html
<!-- Send on form submit -->
<form hx-post="" hx-ws:send="message">
  <input name="text" placeholder="Type message...">
  <button type="submit">Send</button>
</form>

<!-- Send on button click -->
<button hx-post="" hx-ws:send="click">Click Me</button>

<!-- Auto-send with debounce -->
<input hx-post="" 
       hx-ws:send="message" 
       hx-trigger="input changed delay:500ms">
```

The `hx-ws:send` value is the event name sent to server.

### Receiving Messages

Listen for WebSocket messages using `hx-trigger`:

```html
<div hx-ws:connect="ws://example.com/socket">
  <!-- Listen for 'message' events -->
  <div id="chat" 
       hx-trigger="ws:message" 
       hx-on::ws:message='(evt) => {
         document.getElementById("chat").innerHTML += evt.detail.data;
       }'>
    Chat messages appear here
  </div>
  
  <!-- Listen for 'notification' events -->
  <div id="notifications" hx-trigger="ws:notification"></div>
</div>
```

### Full Chat Example

```html
<!DOCTYPE html>
<html>
<head>
  <script src="/htmx.min.js"></script>
  <script src="/ext/ws.js"></script>
</head>
<body>
  <div hx-ws:connect="ws://example.com/chat">
    <!-- Messages container -->
    <div id="messages" class="chat-messages">
      <p>Connected to chat</p>
    </div>
    
    <!-- Input form -->
    <form hx-post="" 
          hx-ws:send="chat_message"
          hx-swap="none">
      <input name="message" 
             placeholder="Type a message..." 
             autofocus>
      <button type="submit">Send</button>
    </form>
  </div>
  
  <script>
    // Handle incoming messages
    document.body.addEventListener('ws:chat_message', function(evt) {
      const messages = document.getElementById('messages');
      messages.innerHTML += `<div class="message">${evt.detail.data}</div>`;
      messages.scrollTop = messages.scrollHeight;
    });
    
    // Handle connection events
    document.body.addEventListener('htmx:wsOpen', function(evt) {
      console.log('WebSocket connected');
    });
    
    document.body.addEventListener('htmx:wsError', function(evt) {
      console.error('WebSocket error:', evt.detail.error);
    });
    
    document.body.addEventListener('htmx:wsClose', function(evt) {
      console.log('WebSocket closed');
    });
  </script>
</body>
</html>
```

### WebSocket Events

htmx fires these WebSocket-specific events:

| Event | Fires | Details |
|-------|-------|---------|
| `htmx:wsOpen` | On connection open | `socket`, `error` |
| `htmx:wsError` | On error | `socket`, `error` |
| `htmx:wsClose` | On close | `socket`, `error`, `event` |
| `ws:<message-name>` | On message received | `data`, `socket` |

### WebSocket with JSON

Send and receive JSON data:

```html
<form hx-post="" 
      hx-ws:send="user_action"
      hx-headers='{"Content-Type": "application/json"}'
      hx-encoding="application/json">
  <input name="action" value="like">
  <input name="targetId" value="123">
  <button type="submit">Like</button>
</form>
```

Server receives JSON object: `{ "action": "like", "targetId": "123" }`

### Reconnection Behavior

WebSocket automatically reconnects on disconnect with exponential backoff. Customize:

```javascript
htmx.config.wsReconnectDelay = 'full-jitter';
```

### Binary Data

Send and receive binary data:

```javascript
// Server sets binary type
socket.binaryType = 'arraybuffer';

// Send binary
const blob = new Blob([binaryData], { type: 'application/octet-stream' });
htmx.trigger(element, 'ws:binary', { data: blob });
```

## Comparing SSE vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WebSocket |
| Reconnection | Automatic | Automatic |
| Binary Support | No | Yes |
| Browser Support | Wide | Wide |
| Use Case | Notifications, feeds | Chat, collaboration, gaming |

### When to Use SSE

- One-way server-to-client updates
- Simple implementation needed
- HTTP infrastructure already in place
- Notifications, live scores, status updates

### When to Use WebSocket

- Bidirectional communication required
- Low-latency interactions
- Binary data transfer
- Chat, real-time collaboration, gaming

## Combining SSE/WebSocket with Regular htmx

Real-time features work alongside standard htmx requests:

```html
<div hx-sse:connect="/events">
  <!-- Real-time notifications -->
  <div id="notifications" hx-sse:swap="notification"></div>
  
  <!-- Regular htmx form still works -->
  <form hx-post="/submit" hx-swap="outerHTML">
    <input name="data">
    <button type="submit">Submit</button>
  </form>
</div>
```

## Debugging Real-time Connections

### Enable Logging

```javascript
htmx.config.logAll = true;
```

### Monitor Connection State

```javascript
// SSE connection
document.body.addEventListener('htmx:sseOpen', (evt) => {
  console.log('SSE connected:', evt.detail.eventSource);
});

document.body.addEventListener('htmx:sseError', (evt) => {
  console.error('SSE error:', evt.detail.error);
});

document.body.addEventListener('htmx:sseClose', (evt) => {
  console.log('SSE closed');
});

// WebSocket connection
document.body.addEventListener('htmx:wsOpen', (evt) => {
  console.log('WebSocket connected:', evt.detail.socket);
});

document.body.addEventListener('htmx:wsError', (evt) => {
  console.error('WebSocket error:', evt.detail.error);
});

document.body.addEventListener('htmx:wsClose', (evt) => {
  console.log('WebSocket closed');
});
```

### Browser DevTools

- **Network tab**: Filter by WS or EventSource
- **Console**: Check for htmx logs and errors
- **Application tab**: Monitor Service Worker if used

## Migration from htmx 2.x

### SSE Changes

**htmx 2:**
```html
<div hx-sse-connect="/events">
  <div hx-sse-swaps="message" id="messages"></div>
</div>
```

**htmx 4:**
```html
<div hx-sse:connect="/events">
  <div hx-sse:swap="message" id="messages"></div>
</div>
```

Attribute name changes:
- `hx-sse-connect` → `hx-sse:connect`
- `hx-sse-swaps` → `hx-sse:swap`

### WebSocket Changes

**htmx 2:**
```html
<div hx-ws-connect="ws://example.com">
  <div hx-ws-send="message" id="chat"></div>
</div>
```

**htmx 4:**
```html
<div hx-ws:connect="ws://example.com">
  <div hx-ws:send="message" id="chat"></div>
</div>
```

Attribute name changes:
- `hx-ws-connect` → `hx-ws:connect`
- `hx-ws-send` → `hx-ws:send`

### Event Name Changes

**htmx 2:**
- `htmx:sseOpen` → Still `htmx:sseOpen`
- `htmx:wsOpen` → Still `htmx:wsOpen`

Event names unchanged, but message events now use `ws:<name>` pattern.
