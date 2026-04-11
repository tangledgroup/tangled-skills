# aiohttp WebSocket Guide

## Client WebSockets

### Basic Connection

```python
import aiohttp
import asyncio

async def websocket_client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://echo.websocket.org') as ws:
            # Send text message
            await ws.send_str("Hello, Server!")
            
            # Receive response
            msg = await ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(f"Received: {msg.data}")
            
            # Or use convenience method
            response = await ws.receive_str()
            print(f"Received: {response}")

asyncio.run(websocket_client())
```

### Connection Parameters

```python
async with session.ws_connect(
    'ws://example.com/socket',
    timeout=10,                    # Connection timeout
    receive_timeout=5,             # Message receive timeout
    autoclose=True,                # Send close frame on disconnect
    autoping=True,                 # Autorespond to ping frames
    heartbeat=30,                  # Send ping every 30 seconds
    compress=15,                   # Enable compression (0-15)
    max_msg_size=4*1024*1024,      # Max message size (4MB)
) as ws:
    ...
```

### Sending Messages

**Text messages:**
```python
await ws.send_str("Hello")
# Or with encoding
await ws.send_str("Привет", encoding='utf-8')
```

**Binary messages:**
```python
await ws.send_bytes(b'\x00\x01\x02\x03')
```

**JSON messages:**
```python
await ws.send_json({'event': 'message', 'data': 'value'})
```

### Receiving Messages

**Receive any message type:**
```python
msg = await ws.receive()

if msg.type == aiohttp.WSMsgType.TEXT:
    print(f"Text: {msg.data}")
elif msg.type == aiohttp.WSMsgType.BINARY:
    print(f"Binary: {msg.data}")
elif msg.type == aiohttp.WSMsgType.CLOSED:
    print("Connection closed")
elif msg.type == aiohttp.WSMsgType.ERROR:
    print(f"Error: {ws.exception()}")
```

**Receive with timeout:**
```python
try:
    msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
except asyncio.TimeoutError:
    print("No message received within 5 seconds")
```

**Convenience methods:**
```python
# Receive text (raises on non-text)
text = await ws.receive_str()

# Receive binary (raises on non-binary)
data = await ws.receive_bytes()

# Receive JSON (parses automatically)
data = await ws.receive_json()
```

### Message Types

- `WSMsgType.TEXT` - Text message received
- `WSMsgType.BINARY` - Binary message received
- `WSMsgType.CLOSED` - Connection closed
- `WSMsgType.CLOSING` - Closing frame sent
- `WSMsgType.CLOSE` - Close frame received
- `WSMsgType.PING` - Ping frame received
- `WSMsgType.PONG` - Pong frame received
- `WSMsgType.ERROR` - Error occurred

### Continuous Communication

```python
async def chat_client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://chat.example.com') as ws:
            # Send initial message
            await ws.send_json({'action': 'join', 'name': 'Alice'})
            
            # Receive messages in loop
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"{data['sender']}: {data['message']}")
                    
                    # Send reply
                    await ws.send_json({'action': 'ack'})
                
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print("Connection closed by server")
                    break
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
                    break

asyncio.run(chat_client())
```

### Reconnection Logic

```python
async def resilient_client(url, max_reconnects=5):
    for attempt in range(max_reconnects):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    print(f"Connected (attempt {attempt + 1})")
                    
                    while True:
                        msg = await ws.receive()
                        if msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        
        except aiohttp.ClientError as e:
            print(f"Connection failed: {e}")
            
            if attempt < max_reconnects - 1:
                wait_time = min(2 ** attempt, 30)  # Exponential backoff
                print(f"Reconnecting in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

## Server WebSockets

### Basic WebSocket Handler

```python
from aiohttp import web

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Process messages
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            # Echo text message
            await ws.send_str(f"Echo: {msg.data}")
        
        elif msg.type == web.WSMsgType.BINARY:
            # Echo binary message
            await ws.send_bytes(msg.data)
        
        elif msg.type == web.WSMsgType.CLOSED:
            print("Client disconnected")
            break
        
        elif msg.type == web.WSMsgType.ERROR:
            print(f"WebSocket error: {ws.exception()}")
            break
    
    return ws

app = web.Application()
app.add_routes([web.get('/ws', websocket_handler)])
web.run_app(app)
```

### Broadcasting to Multiple Clients

```python
from aiohttp import web
import asyncio

# Store connected clients
connected_clients = set()

async def broadcast(message):
    """Send message to all connected clients"""
    if connected_clients:
        await asyncio.gather(
            *[client.send_str(message) for client in connected_clients],
            return_exceptions=True
        )

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Add to connected clients
    connected_clients.add(ws)
    
    try:
        # Send welcome message
        await ws.send_str("Welcome! You are connected.")
        
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Broadcast to all clients
                await broadcast(f"User: {msg.data}")
            
            elif msg.type == web.WSMsgType.CLOSED:
                break
            
            elif msg.type == web.WSMsgType.ERROR:
                break
    
    finally:
        # Remove from connected clients
        connected_clients.discard(ws)
    
    return ws

app = web.Application()
app.add_routes([web.get('/ws', websocket_handler)])
```

### WebSocket with Authentication

```python
from aiohttp import web
import jwt

async def authenticated_websocket(request):
    # Check authorization header or query param
    token = request.query.get('token') or request.headers.get('Authorization')
    
    if not token:
        raise web.HTTPUnauthorized("Token required")
    
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        request['user'] = payload
    except jwt.InvalidTokenError:
        raise web.HTTPUnauthorized("Invalid token")
    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Send user-specific welcome
    username = request['user'].get('username', 'User')
    await ws.send_str(f"Welcome, {username}!")
    
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"You said: {msg.data}")
        elif msg.type == web.WSMsgType.CLOSED:
            break
    
    return ws
```

### Server-Sent Events (Alternative)

For one-way server-to-client streaming:

```python
from aiohttp import web

async def sse_handler(request):
    response = web.StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
    await response.prepare(request)
    
    try:
        for i in range(10):
            await response.write(f"data: {i}\n\n".encode())
            await asyncio.sleep(1)
        
        await response.write("data: [DONE]\n\n".encode())
    finally:
        await response.write_eof()
    
    return response
```

### Heartbeat/Ping-Pong

```python
async def websocket_with_heartbeat(request):
    ws = web.WebSocketResponse(
        heartbeat=30  # Auto-send ping every 30 seconds
    )
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == web.WSMsgType.PING:
            # Auto-responds with PONG if autoping=True (default)
            pass
        
        elif msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"Received: {msg.data}")
        
        elif msg.type == web.WSMsgType.CLOSED:
            break
    
    return ws
```

### Manual Ping/Pong

```python
async def manual_heartbeat(request):
    ws = web.WebSocketResponse(autoping=False)
    await ws.prepare(request)
    
    async def ping_loop():
        while True:
            try:
                await asyncio.sleep(30)
                await ws.ping()
            except:
                break
    
    ping_task = asyncio.create_task(ping_loop())
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.PING:
                await ws.pong(msg.data)
            
            elif msg.type == web.WSMsgType.TEXT:
                await ws.send_str(f"Echo: {msg.data}")
            
            elif msg.type == web.WSMsgType.CLOSED:
                break
    finally:
        ping_task.cancel()
        try:
            await ping_task
        except asyncio.CancelledError:
            pass
    
    return ws
```

### Compression

```python
# Server with compression
ws = web.WebSocketResponse(compress=15)  # Maximum compression
await ws.prepare(request)

# Client with compression  
async with session.ws_connect(url, compress=15) as ws:
    ...
```

### Handling Disconnections

```python
async def robust_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.ERROR:
                # Handle error gracefully
                print(f"WebSocket error: {ws.exception()}")
                break
            
            elif msg.type == web.WSMsgType.CLOSED:
                # Clean disconnection
                print("Client disconnected cleanly")
                break
            
            elif msg.type == web.WSMsgType.CLOSE:
                # Client sent close frame
                await ws.close()
                break
    
    except Exception as e:
        # Unexpected error
        print(f"Unexpected error: {e}")
    
    return ws
```
