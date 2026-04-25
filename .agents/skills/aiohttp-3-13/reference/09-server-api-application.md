# Server API: Application

Complete reference for the aiohttp web.Application class and application management.

## Application Class

Main container for web applications, holding routes, middlewares, and configuration.

### Constructor

```python
from aiohttp import web

app = web.Application(
    # Middleware
    middlewares=None,  # List of middleware factories
    
    # Configuration
    handler_args=None,       # Extra args for handlers
    client_max_size=1024*1024,  # Max request body size (1MB default)
    
    # Routing
    router=None,             # Custom router instance
    logger=None,             # Custom logger
    
    # State management
    state=None,              # Initial state dict
    heartbeat=None,          # Heartbeat interval (seconds)
)
```

### Basic Usage

```python
from aiohttp import web

app = web.Application()

async def handler(request):
    return web.Response(text="Hello")

app.router.add_get('/', handler)
web.run_app(app)
```

## Application Properties

### router

Access to the application's router:

```python
app = web.Application()

# Add routes
app.router.add_get('/users', get_users)
app.router.add_post('/users', create_user)

# Access route table
for route in app.router.routes():
    print(f"{route.method} {route.path}")
```

### middlewares

List of middleware functions:

```python
async def logger(app, handler):
    async def middleware(request):
        # ... logging logic
        return await handler(request)
    return middleware

app = web.Application(middlewares=[logger])

# Access middlewares
print(f"Middleware count: {len(app.middlewares)}")
```

### state

Application-wide state dictionary:

```python
app = web.Application()

# Set state
app['db_connection'] = None
app['config'] = {'debug': True}

# Access in handlers
async def handler(request):
    debug_mode = request.app['config']['debug']
    return web.json_response({'debug': debug_mode})
```

## Lifecycle Signals

### on_startup

Fired when application starts:

```python
async def init_resources(app):
    print("Initializing database...")
    app['db'] = await create_database()
    
    print("Loading cache...")
    app['cache'] = await init_cache()

app.on_startup.append(init_resources)
```

### on_shutdown

Fired when shutdown begins:

```python
async def cleanup_resources(app):
    print("Closing database connections...")
    db = app.get('db')
    if db:
        await db.close()

app.on_shutdown.append(cleanup_resources)
```

### on_cleanup

Fired after shutdown completes:

```python
async def final_cleanup(app):
    print("Final cleanup complete")
    # Log metrics, send notifications, etc.

app.on_cleanup.append(final_cleanup)
```

### Request/Response Signals

```python
# Before request handling
async def on_request_start(request):
    request['start_time'] = time.time()

app.on_request_start.append(on_request_start)

# After request handled
async def on_request_finish(request, response):
    duration = time.time() - request.get('start_time', 0)
    print(f"Request took {duration}s")

app.on_request_finish.append(on_request_finish)

# Before response sent
async def on_response_prepare(request, response):
    response.headers['X-Powered-By'] = 'aiohttp'

app.on_response_prepare.append(on_response_prepare)

# On exception
async def on_request_exception(request, context):
    exc = context.get('exception')
    print(f"Request exception: {exc}")

app.on_request_exception.append(on_request_exception)
```

### Connection Signals

```python
async def on_connection_made(request, transport):
    peer = transport.get_extra_info('peername')
    print(f"Connection from {peer}")

app.on_connection_made.append(on_connection_made)

async def on_connection_lost(request, exc):
    if exc:
        print(f"Connection lost with error: {exc}")

app.on_connection_lost.append(on_connection_lost)
```

## Subapplications

### Creating Subapps

```python
from aiohttp import web

# API subapplication
api_app = web.Application()
api_app.router.add_get('/users', get_users)
api_app.router.add_post('/users', create_user)

# Admin subapplication
admin_app = web.Application()
admin_app.router.add_get('/dashboard', dashboard)
admin_app.router.add_get('/settings', settings)

# Main application
app = web.Application()
app.add_subapp('/api', api_app)
app.add_subapp('/admin', admin_app)

# URLs: /api/users, /admin/dashboard, etc.
```

### Subapp with Middleware

```python
async def api_middleware(app, handler):
    async def middleware(request):
        print(f"API request: {request.path}")
        return await handler(request)
    return middleware

api_app = web.Application(middlewares=[api_middleware])
app.add_subapp('/api', api_app)
```

### Accessing Parent App from Subapp

```python
async def init_parent(app):
    app['shared_db'] = await create_db()

async def subapp_handler(request):
    # Access parent app state
    db = request.app['shared_db']
    return web.json_response({'status': 'ok'})

# Parent app
app = web.Application()
app.on_startup.append(init_parent)

# Subapp
subapp = web.Application()
subapp.router.add_get('/', subapp_handler)

app.add_subapp('/sub', subapp)
```

## Configuration Management

### Using app['key'] for Config

```python
async def load_config(app):
    import json
    with open('config.json') as f:
        app['config'] = json.load(f)

app.on_startup.append(load_config)

async def handler(request):
    api_key = request.app['config']['api_key']
    return web.json_response({'api_key_set': bool(api_key)})
```

### Using FrozenList for Immutable Config

```python
from aiohttp import FrozenList

async def init_app(app):
    # Create immutable list of allowed origins
    cors_origins = FrozenList(['https://example.com', 'https://app.example.com'])
    cors_origins.freeze()  # Make immutable
    app['cors_origins'] = cors_origins
```

## Error Handlers

### Custom 404 Handler

```python
async def custom_404_handler(request):
    return web.Response(
        text="<h1>Page Not Found</h1>",
        status=404,
        content_type='text/html'
    )

app.router.add_404_handler(custom_404_handler)
```

### Custom Exception Handler

```python
async def handle_value_error(request, context):
    exc = context.get('exception')
    return web.json_response(
        {'error': 'Invalid input', 'detail': str(exc)},
        status=400
    )

app.exception_handler(ValueError)(handle_value_error)
```

### Multiple Exception Handlers

```python
async def handle_key_error(request, context):
    return web.json_response({'error': 'Missing field'}, status=400)

async def handle_type_error(request, context):
    return web.json_response({'error': 'Wrong type'}, status=400)

app.exception_handler(KeyError)(handle_key_error)
app.exception_handler(TypeError)(handle_type_error)
```

## Application Runners

### Using run_app (Simple)

```python
web.run_app(
    app,
    host='0.0.0.0',      # Host to bind
    port=8080,           # Port to bind
    path=None,           # Unix socket path
    sock=None,           # Pre-created socket
    shutdown_timeout=60, # Graceful shutdown timeout
    keepalive_timeout=30,# Keep-alive timeout
    ssl_context=None,    # SSL context for HTTPS
    print=lambda x: None,# Custom print function
)
```

### Using AppRunner (Advanced)

```python
from aiohttp import web
from aiohttp.web_runner import AppRunner, TCPSite, UnixSite

async def advanced_run():
    app = web.Application()
    
    # Create runner
    runner = AppRunner(app)
    await runner.setup()
    
    # Create sites
    tcp_site = TCPSite(runner, '0.0.0.0', 8080)
    unix_site = UnixSite(runner, '/tmp/app.sock')
    
    # Start sites
    await tcp_site.start()
    await unix_site.start()
    
    print("Server running on http://0.0.0.0:8080 and unix:/tmp/app.sock")
    
    # Keep running...
    await asyncio.Event().wait()
    
    # Cleanup
    await runner.cleanup()

asyncio.run(advanced_run())
```

### Multiple Hosts

```python
runner = AppRunner(app)
await runner.setup()

sites = [
    TCPSite(runner, 'localhost', 8080),
    TCPSite(runner, '127.0.0.1', 8081),
]

for site in sites:
    await site.start()
```

## SSL/TLS Configuration

### Self-Signed Certificate

```python
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

web.run_app(app, ssl_context=ssl_context)
```

### With CA Bundle

```python
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('server.crt', 'server.key')
ssl_context.load_verify_locations('ca-bundle.crt')

web.run_app(app, ssl_context=ssl_context)
```

### Client Certificate Authentication

```python
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('server.crt', 'server.key')
ssl_context.load_verify_locations('client-ca.crt')
ssl_context.require_client_certificate = True

web.run_app(app, ssl_context=ssl_context)
```

## Application Factory Pattern

### Creating Apps as Factories

```python
def create_app(config_path: str) -> web.Application:
    app = web.Application()
    
    # Load configuration
    with open(config_path) as f:
        config = json.load(f)
    
    app['config'] = config
    
    # Setup routes
    setup_routes(app)
    
    # Setup middleware
    setup_middleware(app)
    
    return app

# Usage
app = create_app('config.json')
web.run_app(app)
```

### With Dependency Injection

```python
class Container:
    def __init__(self):
        self.db = None
        self.cache = None
    
    async def init(self):
        self.db = await create_database()
        self.cache = await create_cache()
    
    async def shutdown(self):
        if self.db:
            await self.db.close()

container = Container()

async def init_app(app):
    await container.init()
    app['container'] = container

async def cleanup_app(app):
    await container.shutdown()

app = web.Application()
app.on_startup.append(init_app)
app.on_cleanup.append(cleanup_app)

async def handler(request):
    db = request.app['container'].db
    # Use db...
```

## Best Practices

### Initialize Resources on Startup

```python
async def init_all(app):
    # Database
    app['db'] = await init_database(app['config']['db_url'])
    
    # Cache
    app['cache'] = await init_cache()
    
    # External API clients
    app['api_client'] = APIClient(app['config']['api_key'])

app.on_startup.append(init_all)
```

### Cleanup Resources on Shutdown

```python
async def cleanup_all(app):
    tasks = []
    
    if 'db' in app:
        tasks.append(app['db'].close())
    
    if 'cache' in app:
        tasks.append(app['cache'].close())
    
    await asyncio.gather(*tasks, return_exceptions=True)

app.on_cleanup.append(cleanup_all)
```

### Graceful Shutdown with Active Requests

```python
shutdown_event = asyncio.Event()

async def track_requests(app):
    app['active_requests'] = 0

async def on_request_start(request):
    request.app['active_requests'] += 1

async def on_request_finish(request, response):
    request.app['active_requests'] -= 1
    if request.app['active_requests'] == 0:
        shutdown_event.set()

app.on_startup.append(track_requests)
app.on_request_start.append(on_request_start)
app.on_request_finish.append(on_request_finish)
```
