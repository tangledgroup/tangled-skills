# htmx WebSockets and Server-Sent Events

This reference covers real-time communication using WebSockets and Server-Sent Events (SSE) in htmx 2.x.

## WebSocket Extension

The WebSocket extension enables bidirectional real-time communication.

### Basic Setup

```html
<!-- Load WebSocket extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>

<!-- Connect to WebSocket -->
<div hx-ws="connect:/ws">
    Connected to WebSocket
</div>
```

### Connection Modes

#### Manual Connection

Explicitly connect to a WebSocket:

```html
<div hx-ws="connect:/websocket-endpoint">
    Chat room
</div>
```

#### Connect with Protocol

Specify WebSocket protocol:

```html
<div hx-ws='connect:[/ws, "chat-protocol-v1"]'>
    Chat with protocol
</div>
```

#### Close Connection

Close WebSocket connection:

```html
<button hx-ws="close">
    Disconnect
</button>
```

### Sending Messages

Send messages via WebSocket:

```html
<!-- Send on form submit -->
<form hx-ws="send" 
      hx-disinherit="hx-target">
    <input name="message" placeholder="Type message...">
    <button type="submit">Send</button>
</form>

<!-- Send with custom event -->
<button hx-ws="send:typing"
        hx-vals='{"user": "john", "status": "typing"}'>
    Mark as Typing
</button>

<!-- Auto-send on input -->
<input name="search" 
       hx-ws="send:search"
       hx-trigger="keyup changed delay:300ms"
       placeholder="Search...">
```

### Receiving Messages

Handle incoming WebSocket messages:

```html
<!-- Container for WebSocket connections -->
<div hx-ws="connect:/chat">
    
    <!-- Display incoming messages -->
    <div id="chat-log">
        <div hx-trigger="ws-message"
             hx-swap="innerHTML">
            Messages appear here
        </div>
    </div>
    
    <!-- Trigger on specific message type -->
    <div hx-trigger='ws-[{"type": "system"}]'
         hx-swap="beforeend">
        System messages
    </div>
</div>
```

### Complete Chat Example

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/htmx.org/dist/htmx.min.js"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>
</head>
<body>
    <div hx-ws="connect:/chat" 
         id="chat-container">
        
        <!-- Message input -->
        <form hx-ws="send" 
              id="message-form">
            <input name="text" 
                   placeholder="Type a message..." 
                   required>
            <button type="submit">Send</button>
        </form>
        
        <!-- Message display -->
        <div id="messages">
            <div hx-trigger="ws-message"
                 hx-swap="beforeend">
                <!-- New messages appended here -->
            </div>
        </div>
        
        <!-- User list updates -->
        <div id="users">
            <div hx-trigger='ws-[{"type": "users"}]'
                 hx-swap="innerHTML">
                Connected users
            </div>
        </div>
    </div>
</body>
</html>
```

### Server Response Patterns

#### Return HTML for Messages

```python
# Flask example
@socketio.on('message')
def handle_message(data):
    message_html = f"""
    <div class="message">
        <strong>{data['user']}</strong>: {data['text']}
    </div>
    """
    return message_html
```

#### Broadcast to All Clients

```python
# Broadcast message to all connected clients
@socketio.on('chat_message')
def handle_chat_message(data):
    message_html = format_message(data)
    emit('message', message_html, broadcast=True)
```

### WebSocket Events

| Event | Description |
|-------|-------------|
| `ws-open` | WebSocket connection opened |
| `ws-error` | WebSocket error occurred |
| `ws-close` | WebSocket connection closed |
| `ws-message` | Message received from server |
| `ws-reconnect` | Reconnection attempt |

```javascript
// Handle WebSocket events
document.body.addEventListener('htmx:wsOpen', (event) => {
    console.log('WebSocket connected:', event.detail);
});

document.body.addEventListener('htmx:wsError', (event) => {
    console.error('WebSocket error:', event.detail);
});

document.body.addEventListener('htmx:wsClose', (event) => {
    console.log('WebSocket closed:', event.detail);
});
```

### Reconnection Behavior

htmx automatically attempts to reconnect:

```javascript
// Configure reconnection delay
htmx.config.wsReconnectDelay = 'full-jitter';

// Custom reconnection logic
htmx.config.wsReconnectDelay = function(ms) {
    return Math.min(ms * 2, 30000); // Max 30 seconds
};
```

**Reconnect on:**
- Abnormal closure
- Service restart
- Try again later

### WebSocket Options

```javascript
// Configure binary type
htmx.config.wsBinaryType = 'blob'; // or 'arraybuffer'

// Custom WebSocket factory
htmx.createWebSocket = function(url, protocols) {
    const ws = new WebSocket(url, protocols);
    ws.onopen = () => console.log('Connected');
    return ws;
};
```

## Server-Sent Events Extension

SSE provides one-way server-to-client streaming.

### Basic Setup

```html
<!-- Load SSE extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>

<!-- Connect to SSE endpoint -->
<div hx-sse-connect="/events">
    Listening for events
</div>
```

### Receiving Events

Handle SSE events:

```html
<!-- Connect to SSE stream -->
<div hx-sse-connect="/notifications">
    
    <!-- Trigger on any event -->
    <div hx-trigger="sse:"
         hx-swap="beforeend">
        Notifications
    </div>
    
    <!-- Trigger on specific event type -->
    <div hx-trigger="sse:new_message"
         hx-swap="beforeend">
        New messages
    </div>
    
    <!-- Multiple event types -->
    <div hx-trigger="sse:user_joined, sse:user_left"
         hx-swap="innerHTML">
        User activity
    </div>
</div>
```

### SSE with GET Requests

Trigger GET requests on SSE events:

```html
<div hx-sse-connect="/updates">
    
    <!-- Fetch content when event received -->
    <div hx-trigger="sse:new_content"
         hx-get="/fetch-content"
         hx-target="#content-area">
        Loading...
    </div>
    
    <!-- Process event data -->
    <div id="content-area"></div>
</div>
```

### Multiple SSE Connections

Connect to multiple SSE streams:

```html
<!-- First connection -->
<div hx-sse-connect="/chat-events">
    <div hx-trigger="sse:message"
         hx-swap="beforeend">
        Chat messages
    </div>
</div>

<!-- Second connection -->
<div hx-sse-connect="/notifications">
    <div hx-trigger="sse:alert"
         hx-swap="beforeend">
        Alerts
    </div>
</div>
```

### SSE Event Formats

#### Simple Event

```
event: message
data: Hello, World!
```

```html
<div hx-trigger="sse:message" 
     hx-swap="beforeend">
    Messages
</div>
```

#### JSON Data

```
event: update
data: {"user": "john", "action": "joined"}
```

```html
<div hx-trigger="sse:update"
     hx-get="/process-update"
     hx-swap="innerHTML">
    Updates
</div>
```

### SSE Server Implementation

#### Python/Flask Example

```python
from flask import Flask, Response

app = Flask(__name__)

@app.route('/events')
def events():
    def generate():
        while True:
            yield "event: update\n"
            yield f"data: {{'timestamp': {time.time()}}}\n\n"
            time.sleep(5)
    
    return Response(generate(), 
                    mimetype='text/event-stream')
```

#### Node.js Example

```javascript
app.get('/events', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    
    const sendEvent = (event, data) => {
        res.write(`event: ${event}\n`);
        res.write(`data: ${JSON.stringify(data)}\n\n`);
    };
    
    // Send initial event
    sendEvent('connected', { status: 'ok' });
    
    // Send periodic updates
    const interval = setInterval(() => {
        sendEvent('update', { time: new Date().toISOString() });
    }, 5000);
    
    // Cleanup on disconnect
    req.on('close', () => {
        clearInterval(interval);
    });
});
```

### SSE Reconnection

SSE automatically reconnects on disconnection:

```javascript
// Configure reconnection
htmx.createEventSource = function(url) {
    return new EventSource(url, {
        withCredentials: true
    });
};
```

### SSE Options

```javascript
// Custom EventSource factory
htmx.createEventSource = function(url) {
    const eventSource = new EventSource(url);
    eventSource.addEventListener('open', () => {
        console.log('SSE connected');
    });
    eventSource.addEventListener('error', (e) => {
        console.error('SSE error:', e);
    });
    return eventSource;
};
```

## Comparison: WebSocket vs SSE

| Feature | WebSocket | SSE |
|---------|-----------|-----|
| Direction | Bidirectional | Server-to-client only |
| Protocol | WebSocket (ws/wss) | HTTP Event Stream |
| Reconnection | Automatic | Automatic |
| Binary Data | Yes | No (text only) |
| Browser Support | Widely supported | Widely supported |
| Firewalls | May be blocked | Uses HTTP ports |
| Use Case | Real-time chat, gaming | Notifications, updates |

### When to Use WebSocket

- Bidirectional communication needed
- Low-latency requirements
- Binary data transmission
- Frequent client-to-server messages

### When to Use SSE

- Server pushes to clients
- Simple implementation preferred
- Better firewall compatibility
- One-way notifications

## Combined Example: Real-time Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/htmx.org/dist/htmx.min.js"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/ws.js"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
</head>
<body>
    <div id="dashboard">
        <!-- WebSocket for user interactions -->
        <div hx-ws="connect:/ws/dashboard">
            
            <!-- Live user count -->
            <div hx-trigger='ws-[{"type": "user_count"}]'
                 hx-swap="innerHTML">
                <span id="user-count">0</span> users online
            </div>
            
            <!-- Chat messages -->
            <form hx-ws="send" id="chat-form">
                <input name="message" placeholder="Chat...">
                <button type="submit">Send</button>
            </form>
            
            <div id="chat-messages">
                <div hx-trigger="ws-message"
                     hx-swap="beforeend">
                    Messages
                </div>
            </div>
        </div>
        
        <!-- SSE for system notifications -->
        <div hx-sse-connect="/sse/notifications">
            
            <!-- System alerts -->
            <div hx-trigger="sse:alert"
                 hx-swap="beforeend">
                Alerts
            </div>
            
            <!-- Periodic stats update -->
            <div hx-trigger="sse:stats"
                 hx-get="/api/stats"
                 hx-target="#stats-panel">
                Loading stats...
            </div>
            
            <div id="stats-panel"></div>
        </div>
    </div>
</body>
</html>
```

## Troubleshooting

### Connection Not Established

**Check:**
1. Extension loaded before htmx processes elements
2. WebSocket/SSE endpoint is accessible
3. Browser console for connection errors

```javascript
// Debug connections
htmx.logAll();

document.body.addEventListener('htmx:wsOpen', (e) => {
    console.log('WebSocket opened:', e.detail);
});

document.body.addEventListener('htmx:wsError', (e) => {
    console.error('WebSocket error:', e.detail);
});
```

### Messages Not Receiving

**Verify:**
1. Server is sending messages in correct format
2. Trigger selectors match event types
3. Target elements exist in DOM

### Reconnection Issues

```javascript
// Configure reconnection
htmx.config.wsReconnectDelay = 'full-jitter';

// Monitor reconnection attempts
document.body.addEventListener('htmx:wsReconnect', (e) => {
    console.log('Attempting to reconnect...');
});
```

## Next Steps

- [Extensions Guide](07-extensions.md) - All htmx extensions
- [Events and API Reference](08-events-api.md) - WebSocket/SSE events
- [Common Patterns](10-common-patterns.md) - Real-time UI patterns
