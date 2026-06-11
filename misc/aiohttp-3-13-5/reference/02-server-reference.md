# Server Reference

## Application and Router

### web.Application

The `Application` is a dict-like object that holds routes, middlewares, signals, and shared state.

```python
from aiohttp import web

app = web.Application()
app['db'] = database_connection  # dict-like storage
```

Use `AppKey` for type-safe keys:

```python
db_key = web.AppKey("db", Database)
app[db_key] = db_instance

async def handler(request: web.Request):
    db = request.app[db_key]  # reveal_type(db) -> Database
```

### Running the Application

```python
# Simple standalone
web.run_app(app, host='0.0.0.0', port=8080)

# With Unix socket
web.run_app(app, path='/tmp/app.sock')

# Async factory pattern
async def app_factory():
    await pre_init()
    app = web.Application()
    app.router.add_get('/', handler)
    return app

web.run_app(app_factory())
```

### run_app() Parameters

- `host` — Listen address (default: '127.0.0.1')
- `port` — Listen port
- `path` — Unix socket path
- `reuse_address` — Reuse address (True by default)
- `reuse_port` — Enable SO_REUSEPORT
- `handle_signals` — Handle SIGINT/SIGTERM (True by default)
- `access_log` — Access logger instance or None to disable
- `access_log_format` — Custom access log format string
- `handler_cancellation` — Cancel handler on client disconnect
- `shutdown_timeout` — Graceful shutdown timeout in seconds

### UrlDispatcher

The router manages route matching:

```python
# Add routes imperatively
app.router.add_get('/path', handler)
app.router.add_post('/path', handler)
app.router.add_route('*', '/path', handler)  # any method

# Route table with decorators
routes = web.RouteTableDef()

@routes.get('/get')
async def handle_get(request):
    ...

@routes.post('/post')
async def handle_post(request):
    ...

app.router.add_routes(routes)

# Named routes for URL building
app.router.add_resource(r'/{user}/info', name='user-info')
url = request.app.router['user-info'].url_for(user='john_doe')

# View all resources
for resource in app.router.resources():
    print(resource)

# View named resources
for name, resource in app.router.named_resources().items():
    print(name, resource)
```

### Variable Resources

Path variables use `{identifier}` syntax:

```python
@routes.get('/{name}')
async def variable_handler(request):
    return web.Response(text=f"Hello, {request.match_info['name']}")

# Default regex: [^{}/]+
# Custom regex:
web.get(r'/{name:\d+}', handler)  # matches only digits
```

## Request Object

### web.Request Properties

- `method` — HTTP method (str)
- `rel_url` — Relative URL (yarl.URL)
- `url` — Full URL (yarl.URL)
- `path` — Request path (str)
- `path_qs` — Path with query string (str)
- `query` — Query parameters as MultiDictProxy
- `headers` — Request headers as CIMultiDictProxy
- `content` — `StreamReader` for request body
- `match_info` — Route match result (for variable resources)
- `app` — The `Application` instance
- `config_dict` — ChainMap across nested apps and parent apps
- `is_keep_alive` — Whether keep-alive is enabled
- `remote` — Remote peer address
- `peername` — Socket peer name
- `host` — Request host
- `scheme` — Request scheme (http/https)
- `content_type` — Content-Type header content part
- `charset` — Character encoding from Content-Type
- `content_length` — Content-Length header value
- `if_modified_since` — If-Modified-Since as datetime
- `if_unmodified_since` — If-Unmodified-Since as datetime
- `if_match` — If-Match as tuple of ETag objects
- `if_none_match` — If-None-Match as tuple of ETag objects
- `http_range` — Range header as slice object

### Request Methods

- `await request.read()` — Read body as bytes
- `await request.text()` — Read body as text (decoded by charset or UTF-8)
- `await request.json(loads=json.loads)` — Parse JSON body
- `await request.post()` — Parse POST form data (returns MultiDictProxy)
- `await request.multipart()` — Return `MultipartReader` for multipart data
- `request.clone(method=..., rel_url=..., headers=...)` — Clone request with modifications
- `request.get_extra_info(name, default=None)` — Get transport extra info

## Response Classes

### web.Response

The most common response type. Sends complete body with Content-Length header:

```python
async def handler(request):
    return web.Response(text="Hello", status=200, content_type='text/plain')
```

Constructor parameters:
- `body` — Response body (bytes)
- `text` — Response body as text
- `status` — HTTP status code (200 by default)
- `reason` — HTTP reason phrase
- `headers` — Response headers (dict)
- `content_type` — Content-Type content part
- `charset` — Character encoding

### web.json_response()

Shortcut for JSON responses:

```python
async def handler(request):
    data = {'key': 'value'}
    return web.json_response(data)
```

### web.StreamResponse

For streaming large responses. Is a finite state machine — headers can only be set before `prepare()`:

```python
async def handler(request):
    resp = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'application/octet-stream'
    })
    await resp.prepare(request)
    await resp.write(b'data chunk 1')
    await resp.write(b'data chunk 2')
    await resp.write_eof()
    return resp
```

Key methods:
- `await prepare(request)` — Send headers, start response
- `await write(data)` — Write data chunk
- `await write_eof()` — End response
- `force_close()` — Disable keep-alive
- `enable_compression(force=None, strategy=None)` — Enable compression
- `enable_chunked_encoding()` — Enable chunked transfer encoding
- `set_cookie(name, value, *, path='/', expires=None, domain=None, max_age=None, secure=None, httponly=None, samesite=None, partitioned=None)`
- `del_cookie(name, *, path='/', domain=None)`

Properties:
- `prepared` — True after prepare() called
- `status` / `reason` — Response status
- `keep_alive` — Keep-alive enabled
- `compression` — Compression enabled
- `chunked` — Chunked encoding enabled
- `headers` — CIMultiDict for outgoing headers
- `cookies` — SimpleCookie for outgoing cookies

### web.FileResponse

Serve static files efficiently:

```python
async def handler(request):
    return web.FileResponse('/path/to/file.pdf')
```

### web.WebSocketResponse

Server-side WebSocket handling:

```python
async def handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            break
    return ws
```

Methods:
- `await prepare(request)` — Upgrade to WebSocket
- `await send_str(text)` — Send text message
- `await send_bytes(data)` — Send binary data
- `await send_json(obj)` — Send JSON message
- `await ping(data=None)` — Send ping
- `await pong(data=None)` — Send pong
- `await close(code=1000, message=b'')` — Close connection
- `await receive()` — Receive next message (must be called from handler task only)

Properties:
- `closed` — True if WebSocket is closed
- `closing` — True if closing handshake in progress
- `can_send` — True if send operations are allowed
- `can_receive` — True if receive operations are allowed
- `compressed` — Compression enabled
- `autoclose` — Auto-close on connection close (True by default)
- `autoping` — Auto-reply to pings with pong (True by default)

**Important**: Only the handler task may call `receive()`. Other tasks may send data. Parallel reads are forbidden.

## Class-Based Views

```python
class MyView(web.View):
    async def get(self):
        return web.Response(text="GET response")

    async def post(self):
        return web.Response(text="POST response")
    # Unimplemented methods return 405 Method Not Allowed

app.router.add_view('/path/to', MyView)
```

## Middlewares

Server middleware intercepts requests and responses:

```python
async def middleware(app, handler):
    async def middleware_handler(request):
        # Pre-request processing
        start = time.time()
        response = await handler(request)
        # Post-response processing
        elapsed = time.time() - start
        print(f"Request took {elapsed:.3f}s")
        return response
    return middleware_handler

app = web.Application(middlewares=[middleware])
```

### Middleware Factory Pattern

```python
def timing_middleware():
    async def middleware(app, handler):
        async def middleware_handler(request):
            start = time.time()
            response = await handler(request)
            elapsed = time.time() - start
            response.headers['X-Response-Time'] = str(elapsed)
            return response
        return middleware_handler
    return middleware

app = web.Application(middlewares=[timing_middleware()])
```

### Built-in Middleware

`web.normalize_path_middleware()` — Normalize path (strip trailing slashes, redirect).

## Signals

aiohttp provides signals for lifecycle events:

```python
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.on_cleanup.append(on_cleanup)
app.on_response_prepare.append(on_response_prepare)
app.on_response_end.append(on_response_end)
```

Available signals:
- `on_startup` — Application starting
- `on_shutdown` — Application shutting down
- `on_cleanup` — Application cleanup
- `on_response_prepare` — Before response is sent
- `on_response_end` — After response is sent
- `on_request_start` — Request received
- `on_request_finish` — Request processing finished
- `on_request_handler_error` — Handler error occurred

### Cleanup Context

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_cleanup_ctx(app):
    app['db'] = await create_db_pool()
    yield
    await app['db'].close()

app.cleanup_ctx.append(db_cleanup_ctx)
```

## Nested Applications

Similar to Flask blueprints or Django apps:

```python
sub_app = web.Application()
sub_app.router.add_get('/sub', sub_handler)

app = web.Application()
app.add_subapp('/api/', sub_app)
```

Access parent app config via `request.config_dict` (ChainMapProxy across all nested apps).

## Graceful Shutdown

```python
web.run_app(app, shutdown_timeout=60.0)
```

During shutdown:
- New connections are refused
- Existing connections complete or are cancelled after timeout
- Cleanup contexts run in reverse order
- Background tasks should be managed with `aiojobs` (not bare `asyncio.create_task()`)

### Handler Cancellation on Disconnect

```python
web.run_app(app, handler_cancellation=True)
```

When enabled, handler task is cancelled if client disconnects. Use `aiojobs.aiohttp.shield()` to protect critical operations:

```python
from aiojobs.aiohttp import shield

async def handler(request):
    await shield(request, write_to_db(request))
    return web.Response(text="OK")
```

Do not use bare `asyncio.shield()` — the shielded task won't be tracked during shutdown. Use `aiojobs` for background tasks:

```python
from aiojobs.aiohttp import setup, spawn

app = web.Application()
setup(app)  # Required before using spawn

async def handler(request):
    await spawn(request, background_task())
    return web.Response()
```

## HTTP Exceptions

aiohttp provides HTTP exception classes:

```python
from aiohttp import web, HttpProcessingError

raise web.HTTPNotFound(text="Resource not found")
raise web.HTTPBadRequest(text="Invalid input")
raise web.HTTPTemporaryRedirect(location='/new-path')
```

Available: `HTTPBadRequest`, `HTTPUnauthorized`, `HTTPForbidden`, `HTTPNotFound`, `HTTPMethodNotAllowed`, `HTTPNotAcceptable`, `HTTPConflict`, `HTTPGone`, `HTTPLengthRequired`, `HTTPPreconditionFailed`, `HTTPRequestEntityTooLarge`, `HTTPRequestURITooLarge`, `HTTPUnsupportedMediaType`, `HTTPRangeNotSatisfiable`, `HTTPExpectationFailed`, `HTTPUpgradeRequired`, `HTTPInternalServerError`, `HTTPNotImplemented`, `HTTPBadGateway`, `HTTPServiceUnavailable`, `HTTPGatewayTimeout`, `HTTPVariantAlsoNegotiates`, `HTTPInsufficientStorage`, `HTTPNotExtended`.

## Deployment Patterns

### Standalone

```python
web.run_app(app, host='0.0.0.0', port=8080)
```

Simple but single-process (does not utilize all CPU cores).

### Nginx + Supervisord

Run multiple aiohttp processes behind nginx reverse proxy:

Nginx config:
```nginx
http {
    upstream aiohttp {
        server unix:/tmp/app_1.sock fail_timeout=0;
        server unix:/tmp/app_2.sock fail_timeout=0;
    }
    server {
        listen 80;
        location / {
            proxy_pass http://aiohttp;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_redirect off;
            proxy_buffering off;
        }
        location /static {
            root /path/to/app/static;
        }
    }
}
```

Supervisord config:
```ini
[program:aiohttp]
numprocs = 4
process_name = app_%(process_num)s
command=/path/to/app.py --path=/tmp/app_%(process_num)s.sock
autostart = true
autorestart = true
```

### Nginx + Gunicorn

```bash
gunicorn my_app_module:my_web_app \
    --bind localhost:8080 \
    --worker-class aiohttp.GunicornWebWorker
```

For uvloop integration, use `aiohttp.GunicornUVLoopWebWorker`.

Application factory for Gunicorn:
```python
async def my_web_app():
    app = web.Application()
    app.router.add_get('/', index)
    return app
```

## Application Runners

Low-level runner API for fine-grained control:

```python
runner = web.AppRunner(app)
await runner.setup()
site = web.TCPSite(runner, 'localhost', 8080)
await site.start()
```

Site types:
- `TCPSite(runner, host, port)` — TCP socket
- `UnixSite(runner, path)` — Unix domain socket
- `NamedPipeSite(runner, path)` — Windows named pipe
- `SockSite(runner, sock)` — Pre-existing socket

Graceful shutdown:
```python
await runner.shutdown()
await runner.cleanup()
```

## Logging

aiohttp uses standard Python `logging` module. Loggers:

- `'aiohttp.access'` — Access logs
- `'aiohttp.client'` — Client logs
- `'aiohttp.internal'` — Internal logs
- `'aiohttp.server'` — Server error logs
- `'aiohttp.web'` — Web framework logs
- `'aiohttp.websocket'` — WebSocket logs

Minimal setup:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
web.run_app(app, port=5000)
```

### Access Log Format

Default format: `'%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'`

Format specifiers:
- `%%` — Literal percent sign
- `%a` — Remote IP address
- `%t` — Request start time
- `%P` — Process ID
- `%r` — First line of request
- `%s` — Response status code
- `%b` — Response size in bytes
- `%T` — Request processing time (seconds)
- `%Tf` — Processing time with fraction
- `%D` — Processing time in microseconds
- `%{FOO}i` — Request header FOO
- `%{FOO}o` — Response header FOO

Disable access logs: `web.run_app(app, access_log=None)`

Custom access logger:
```python
from aiohttp.abc import AbstractAccessLogger

class AccessLogger(AbstractAccessLogger):
    def log(self, request, response, time):
        self.logger.info(f'{request.remote} "{request.method} {request.path}" done in {time}s: {response.status}')

    @property
    def enabled(self):
        return self.logger.isEnabledFor(logging.INFO)
```

## Data Sharing Patterns

**No singletons** — aiohttp discourages global variables. Use `Application` and `Request` dict interfaces:

```python
# Application-level (shared across requests)
app[my_key] = shared_resource

# Request-level (per-request scope)
async def handler(request):
    request['processed'] = True

# Middleware storing data for handlers
async def auth_middleware(app, handler):
    async def middleware_handler(request):
        user = await authenticate(request)
        request['user'] = user
        return await handler(request)
    return middleware_handler
```
