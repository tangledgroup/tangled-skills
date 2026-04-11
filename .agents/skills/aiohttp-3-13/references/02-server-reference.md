# aiohttp Server Reference

## Application

The main web application object that holds routes, middlewares, and configuration.

### Creating an Application

```python
from aiohttp import web

# Basic application
app = web.Application()

# With middleware
async def logger(app, handler):
    async def middleware(request):
        # ... logging logic
        return await handler(request)
    return middleware

app = web.Application(middlewares=[logger])

# With configuration
app = web.Application(client_max_size=10**6)  # 1MB max request size
```

### Application Properties

- `app.router` - RouteTable instance for routing
- `app.middlewares` - List of middleware functions
- `app.on_startup` - Signal fired on startup
- `app.on_shutdown` - Signal fired on shutdown
- `app.on_cleanup` - Signal fired on cleanup
- `app.state` - Dict for application-wide data sharing

### Application Lifecycle Signals

```python
from aiohttp import web

async def startup_handler(app):
    print("Starting up...")
    # Initialize database connections, etc.

async def shutdown_handler(app):
    print("Shutting down...")
    # Close connections, cleanup resources

app = web.Application()
app.on_startup.append(startup_handler)
app.on_shutdown.append(shutdown_handler)
```

## Routing

### Adding Routes

**Method 1: add_routes (recommended)**
```python
from aiohttp import web

async def handle_get(request):
    return web.Response(text="GET")

async def handle_post(request):
    return web.Response(text="POST")

app = web.Application()
app.add_routes([
    web.get('/', handle_get),
    web.post('/create', handle_post),
    web.put('/{id}', handle_put),
    web.patch('/{id}', handle_patch),
    web.delete('/{id}', handle_delete),
    web.head('/check', handle_head),
    web.options('/cors', handle_options),
])
```

**Method 2: RouteTableDef with decorators**
```python
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text="Home")

@routes.post('/users')
async def create_user(request):
    data = await request.json()
    return web.json_response({'id': 123, **data})

@routes.get('/users/{user_id}')
async def get_user(request):
    user_id = request.match_info['user_id']
    return web.json_response({'id': user_id})

app = web.Application()
app.add_routes(routes)
```

### Route Matching

**Path parameters:**
```python
@routes.get('/users/{user_id}')
async def get_user(request):
    user_id = request.match_info['user_id']  # String

@routes.get('/users/{user_id:\\d+}')  # Regex pattern
async def get_user(request):
    user_id = request.match_info['user_id']  # Only matches digits
```

**Multiple parameters:**
```python
@routes.get('/{year}/{month}/{day}')
async def get_article(request):
    year = request.match_info['year']
    month = request.match_info['month']
    day = request.match_info['day']
```

### Static Files

```python
# Serve files from directory
app.router.add_static('/static', path='/var/www/static')

# With custom index file
app.router.add_static('/static', '/var/www/static', name='static')

# Access via URL: http://localhost:8080/static/css/style.css
```

### View Classes

```python
from aiohttp import web

class UserView(web.View):
    async def get(self):
        return web.json_response({'method': 'GET'})
    
    async def post(self):
        data = await self.request.json()
        return web.json_response({'created': True})
    
    async def put(self):
        return web.json_response({'updated': True})
    
    async def delete(self):
        return web.json_response({'deleted': True})

app.router.add_view('/users', UserView)
```

## Request Object (`web.Request`)

### Properties

- `method` - HTTP method (str, e.g., 'GET')
- `url` - Full URL (yarl.URL)
- `rel_url` - Relative URL (yarl.URL)
- `path` - Request path (str)
- `query` - Query parameters (MultiDictProxy)
- `headers` - Request headers (CIMultiDictProxy)
- `cookies` - Cookies (MultiDictProxy)
- `content` - StreamReader for request body
- `match_info` - Route match info (dict with path params)
- `app` - Application instance
- `config_dict` - Request configuration
- `tls_client_certificate` - Client SSL certificate (if any)

### Accessing Data

**Query parameters:**
```python
async def handler(request):
    # Get single value
    page = request.query.get('page', '1')
    
    # Get all as dict-like object
    params = dict(request.query)
    
    # Check existence
    if 'search' in request.query:
        search_term = request.query['search']
```

**Headers:**
```python
async def handler(request):
    # Case-insensitive access
    user_agent = request.headers.get('User-Agent')
    content_type = request.headers.get('Content-Type')
    
    # Check existence
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
```

**Cookies:**
```python
async def handler(request):
    session_id = request.cookies.get('session_id')
    theme = request.cookies.get('theme', 'light')
```

**Path parameters:**
```python
@routes.get('/users/{user_id}/posts/{post_id}')
async def get_post(request):
    user_id = request.match_info['user_id']
    post_id = request.match_info['post_id']
```

**Request body:**
```python
async def handler(request):
    # JSON body
    data = await request.json()
    
    # Form data (application/x-www-form-urlencoded)
    data = await request.post()
    
    # Raw bytes
    body = await request.read()
    
    # Streaming
    async for chunk in request.content.iter_chunked(8192):
        process(chunk)
```

## Response Objects

### web.Response

Basic HTTP response:

```python
async def handler(request):
    return web.Response(
        text="Hello, World!",
        status=200,
        content_type='text/plain',
        headers={'X-Custom': 'value'}
    )
```

### web.json_response

JSON response (recommended for APIs):

```python
async def handler(request):
    data = {'name': 'John', 'age': 30, 'active': True}
    
    return web.json_response(
        data,
        status=201,
        headers={'X-Request-ID': 'abc-123'},
        dumps=lambda x: json.dumps(x, indent=2)  # Custom serializer
    )
```

### web.FileResponse

Serve files:

```python
async def handler(request):
    return web.FileResponse('/path/to/file.pdf')

# With custom filename and content-type
return web.FileResponse(
    '/path/to/file.pdf',
    filename='document.pdf',
    content_type='application/pdf'
)
```

### web.StreamResponse

Streaming response:

```python
async def handler(request):
    response = web.StreamResponse(
        status=200,
        headers={'Content-Type': 'text/plain'}
    )
    await response.prepare(request)
    
    for i in range(100):
        await response.write(f"{i}\n".encode())
    
    return response
```

### web.Response Redirects

```python
# Temporary redirect (302)
return web.HTTPFound('/new-location')

# Permanent redirect (301)
return web.HTTPMoved Permanently('/new-location')

# With custom status
return web.Response(
    status=307,
    headers={'Location': '/new-location'}
)
```

### Error Responses

```python
# Using built-in exception classes
raise web.HTTPNotFound("Resource not found")
raise web.HTTPBadRequest("Invalid request")
raise web.HTTPUnauthorized("Authentication required")
raise web.HTTPForbidden("Access denied")
raise web.HTTPInternalServerError("Server error")

# Or return with status code
return web.Response(status=404, text="Not Found")
```

## Middleware

### Creating Middleware

Middleware wraps request handling:

```python
async def middleware_factory(app, handler):
    async def middleware(request):
        # Before request
        start_time = time.time()
        
        # Call next handler
        response = await handler(request)
        
        # After response
        duration = time.time() - start_time
        response.headers['X-Response-Time'] = str(duration)
        
        return response
    
    return middleware

app = web.Application(middlewares=[middleware_factory])
```

### Common Middleware Patterns

**Logging:**
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def logging_middleware(app, handler):
    async def middleware(request):
        start = datetime.now()
        response = await handler(request)
        duration = (datetime.now() - start).total_seconds()
        
        logger.info(
            f"{request.method} {request.path} "
            f"status={response.status} time={duration:.3f}s"
        )
        return response
    
    return middleware
```

**CORS:**
```python
async def cors_middleware(app, handler):
    async def middleware(request):
        if request.method == 'OPTIONS':
            # Pre-flight request
            return web.Response(
                status=204,
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )
        
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    return middleware
```

**Authentication:**
```python
async def auth_middleware(app, handler):
    async def middleware(request):
        token = request.headers.get('Authorization')
        
        if not token or not validate_token(token):
            raise web.HTTPUnauthorized("Invalid token")
        
        # Attach user info to request
        request['user'] = decode_token(token)
        
        return await handler(request)
    
    return middleware
```

**Error handling:**
```python
async def error_middleware(app, handler):
    async def middleware(request):
        try:
            return await handler(request)
        except ValueError as e:
            return web.HTTPBadRequest(text=str(e))
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return web.HTTPInternalServerError(text="Internal server error")
    
    return middleware
```

### Accessing Middleware in Handlers

Request acts as a dict for data sharing:

```python
# In middleware
request['custom_data'] = {'key': 'value'}

# In handler
data = request.get('custom_data')
```

## Signals

Application lifecycle signals for hooks:

```python
from aiohttp import web

# Request/response signals
app.on_response_prepare.append(handler)  # Before response sent
app.on_request_start.append(handler)     # When request received
app.on_request_finish.append(handler)    # After request handled
app.on_request_exception.append(handler) # On exception

# Connection signals
app.on_connection_made.append(handler)   # Client connected
app.on_connection_lost.append(handler)   # Client disconnected

# Startup/shutdown signals
app.on_startup.append(handler)           # App starting
app.on_shutdown.append(handler)          # App shutting down
app.on_cleanup.append(handler)           # After shutdown
```

### Signal Handlers

```python
from aiohttp.web import Request, Response

async def on_request_start_handler(request):
    request['start_time'] = time.time()

async def on_request_finish_handler(request):
    duration = time.time() - request['start_time']
    print(f"Request took {duration}s")

app.on_request_start.append(on_request_start_handler)
app.on_request_finish.append(on_request_finish_handler)
```

## Running the Application

### Basic Usage

```python
from aiohttp import web

async def handler(request):
    return web.Response(text="Hello")

app = web.Application()
app.add_routes([web.get('/', handler)])

web.run_app(app)  # Defaults to localhost:8080
```

### Custom Host and Port

```python
web.run_app(app, host='0.0.0.0', port=8000)
```

### Multiple Hosts

```python
web.run_app(app, hosts=['localhost', '127.0.0.1'], port=8080)
```

### SSL/TLS

```python
web.run_app(
    app,
    ssl_context=ssl_context  # ssl.SSLContext instance
)

# Or with cert/key files
web.run_app(
    app,
    ssl_context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH),
)
# Then load_cert_chain on the context
```

### Production Runner

For production, consider using a process manager:

```bash
# With gunicorn (using aiohttp worker)
pip install gunicorn gunicorn[aiohttp]
gunicorn -k aiohttp.worker.GunicornWorker app:app

# Or use uvicorn with httpx
```
