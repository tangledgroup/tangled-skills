# Advanced Server Topics

## Graceful Shutdown

### Using run_app (Simple)

```python
from aiohttp import web

async def handler(request):
    return web.Response(text="Hello")

app = web.Application()
app.add_routes([web.get('/', handler)])

# Automatic graceful shutdown on SIGINT/SIGTERM
web.run_app(app)
```

### Manual Shutdown Control

For more control over shutdown:

```python
from aiohttp import web
import asyncio

shutdown_event = asyncio.Event()

async def startup_handler(app):
    print("Starting up...")
    # Initialize resources

async def shutdown_handler(app):
    print("Shutdown requested, finishing current requests...")
    # Cleanup resources
    await shutdown_event.wait()

app = web.Application()
app.on_startup.append(startup_handler)
app.on_shutdown.append(shutdown_handler)

# Run with custom signals
from aiohttp.web_runner import AppRunner, TCPSite

async def run():
    runner = AppRunner(app)
    await runner.setup()
    
    site = TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    print("Server started on http://localhost:8080")
    
    # Wait for shutdown signal
    await shutdown_event.wait()
    
    print("Shutting down...")
    await runner.cleanup()

asyncio.run(run())
```

### Custom Signal Handling

```python
import signal
from aiohttp import web

async def handle_shutdown(app, sig):
    print(f"Received signal {sig}, shutting down gracefully...")
    
    # Allow time for current requests to complete
    await asyncio.sleep(5)
    
    # Force shutdown after timeout
    app.on_cleanup.append(lambda app: print("Forced cleanup"))

app = web.Application()

# Register signal handlers
loop = asyncio.get_event_loop()
for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(
        sig,
        lambda s=sig: asyncio.create_task(handle_shutdown(app, s))
    )

web.run_app(app)
```

## Application Runners

### AppRunner (Low-Level Control)

```python
from aiohttp import web
from aiohttp.web_runner import AppRunner, TCPSite, UnixSite

async def advanced_run():
    app = web.Application()
    
    # Create runner
    runner = AppRunner(app)
    await runner.setup()
    
    # TCP site
    tcp_site = TCPSite(runner, '0.0.0.0', 8080)
    await tcp_site.start()
    
    # Unix socket site (alternative)
    unix_site = UnixSite(runner, '/tmp/aiohttp.sock')
    await unix_site.start()
    
    print("Server running on http://0.0.0.0:8080 and unix:/tmp/aiohttp.sock")
    
    # Keep running...
    await asyncio.sleep(3600)
    
    # Cleanup
    await runner.cleanup()

asyncio.run(advanced_run())
```

### Multiple Sites/Hosts

```python
async def multi_host_server():
    app = web.Application()
    runner = AppRunner(app)
    await runner.setup()
    
    sites = [
        TCPSite(runner, 'localhost', 8080),
        TCPSite(runner, '127.0.0.1', 8081),
        UnixSite(runner, '/var/run/app.sock'),
    ]
    
    for site in sites:
        await site.start()
    
    print(f"Server running on {len(sites)} sites")
    
    # Wait forever or until shutdown
    await asyncio.Event().wait()

asyncio.run(multi_host_server())
```

### SSL Configuration

```python
import ssl
from aiohttp import web

# Create SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# With self-signed cert verification disabled (testing only)
ssl_context.verify_mode = ssl.CERT_NONE

app = web.Application()
web.run_app(app, ssl_context=ssl_context)
```

### Client Certificate Authentication

```python
import ssl
from aiohttp import web

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('server.crt', 'server.key')
ssl_context.load_verify_locations('ca.crt')
ssl_context.require_client_certificate = True

app = web.Application()
web.run_app(app, ssl_context=ssl_context)

# Access client cert in handler
async def handler(request):
    cert = request.tls_client_certificate
    if cert:
        subject = dict(cert.get_subject())
        print(f"Client: {subject}")
    
    return web.Response(text="Authenticated")
```

## Data Sharing

### Application State

```python
from aiohttp import web

async def init_db(app):
    # Initialize database connection
    app['db'] = await create_database_connection()

async def cleanup_db(app):
    # Close database connection
    db = app.get('db')
    if db:
        await db.close()

app = web.Application()
app.on_startup.append(init_db)
app.on_cleanup.append(cleanup_db)

async def handler(request):
    db = request.app['db']
    result = await db.query("SELECT * FROM users")
    return web.json_response(result)

app.add_routes([web.get('/users', handler)])
```

### Request Dictionary

Request acts as a dict for per-request data:

```python
# In middleware
async def auth_middleware(app, handler):
    async def middleware(request):
        token = request.headers.get('Authorization')
        user = validate_token(token)
        
        if user:
            request['user'] = user  # Store in request dict
        
        return await handler(request)
    return middleware

# In handler
async def handler(request):
    user = request.get('user')  # Retrieve from request dict
    if not user:
        raise web.HTTPUnauthorized()
    
    return web.json_response({'username': user['name']})
```

### Request Config Dict

For handler-specific configuration:

```python
async def handler(request):
    # Get config for this specific request
    max_size = request.config_dict.get('max_size', 1024)
    
    # Set config
    request.config_dict['processed'] = True
```

## Middleware Chaining

### Understanding the Chain

Middleware wraps handlers in layers:

```
Request -> Middleware A -> Middleware B -> Handler -> Response
         (outermost)     (inner)          (core)    (back out)
```

### Debugging Middleware Order

```python
async def debug_middleware(app, handler):
    async def middleware(request):
        print(f"[BEFORE] {request.method} {request.path}")
        
        response = await handler(request)
        
        print(f"[AFTER] Status: {response.status}")
        return response
    
    return middleware

app = web.Application(middlewares=[debug_middleware])
```

### Conditional Middleware

```python
def conditional_middleware(condition):
    async def factory(app, handler):
        async def middleware(request):
            if condition(request):
                # Add custom header when condition met
                request['custom_processed'] = True
            
            response = await handler(request)
            return response
        
        return middleware
    return factory

# Usage
app = web.Application(middlewares=[
    conditional_middleware(lambda r: r.path.startswith('/api'))
])
```

## Error Handling

### Global Exception Handler

```python
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

async def exception_handler(request, context):
    exc = context.get('exception')
    
    if isinstance(exc, ValueError):
        return web.json_response(
            {'error': 'Invalid input'},
            status=400
        )
    
    elif isinstance(exc, KeyError):
        return web.json_response(
            {'error': 'Missing field'},
            status=400
        )
    
    else:
        logger.error(f"Unhandled exception: {exc}")
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )

app = web.Application()
app.exception_handler(ValueError)(exception_handler)
```

### Error Pages

```python
async def error_404_handler(request):
    return web.Response(
        text="<h1>404 - Page Not Found</h1>",
        status=404,
        content_type='text/html'
    )

async def error_500_handler(request):
    return web.Response(
        text="<h1>500 - Internal Server Error</h1>",
        status=500,
        content_type='text/html'
    )

app = web.Application()
app.router.add_404_handler(error_404_handler)
# Custom 500 handled via exception handler
```

## Subapplications

### Creating Subapps

```python
from aiohttp import web

# API subapplication
api_app = web.Application()
api_app.add_routes([
    web.get('/users', get_users),
    web.post('/users', create_user),
    web.get('/posts', get_posts),
])

# Admin subapplication
admin_app = web.Application()
admin_app.add_routes([
    web.get('/dashboard', admin_dashboard),
    web.get('/settings', admin_settings),
])

# Main application with subapps
app = web.Application()
app.add_subapp('/api', api_app)
app.add_subapp('/admin', admin_app)

# URLs: /api/users, /admin/dashboard, etc.
```

### Subapp Middleware

```python
async def api_logger(app, handler):
    async def middleware(request):
        start = time.time()
        response = await handler(request)
        duration = time.time() - start
        print(f"API: {request.path} in {duration:.3f}s")
        return response
    return middleware

api_app = web.Application(middlewares=[api_logger])
app.add_subapp('/api', api_app)
```

### Subapp Access to Parent

```python
async def handler(request):
    # Access parent app state
    parent_db = request.app['db']  # From main app
    
    # Access subapp state
    subapp_config = request.match_info.get('subapp', {}).get('config')
```

## Signals Deep Dive

### Request Lifecycle Signals

```python
from aiohttp import web

async def on_request_start(request):
    request['start_time'] = time.time()

async def on_request_end(request, response):
    duration = time.time() - request['start_time']
    print(f"{request.path}: {duration:.3f}s")

async def on_response_prepare(request, response):
    response.headers['X-Powered-By'] = 'aiohttp'

app = web.Application()
app.on_request_start.append(on_request_start)
app.on_request_finish.append(on_request_end)
app.on_response_prepare.append(on_response_prepare)
```

### Connection Signals

```python
async def on_connection_made(request, transport):
    print(f"Connection from {request.transport.get_extra_info('peername')}")

async def on_connection_lost(request, exc):
    if exc:
        print(f"Connection lost with error: {exc}")
    else:
        print("Connection closed cleanly")

app.on_connection_made.append(on_connection_made)
app.on_connection_lost.append(on_connection_lost)
```

## Performance Tuning

### Connection Limits

```python
from aiohttp import web

app = web.Application(
    client_max_size=10**7,  # 10MB max request body
)

# Or configure runner
runner = AppRunner(app, handle_signals=True)
```

### Keep-Alive Settings

```python
from aiohttp.web_runner import TCPSite

site = TCPSite(
    runner,
    'localhost',
    8080,
    keepalive_timeout=30,  # Keep-alive timeout
)
```

### Request Timeout

```python
async def timeout_middleware(app, handler):
    async def middleware(request):
        try:
            return await asyncio.wait_for(
                handler(request),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            raise web.RequestTimeout()
    return middleware
```
