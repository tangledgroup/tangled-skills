# Workers and Customization

## Contents
- Worker Architecture (Pre-fork Model)
- Worker Types
- Scaling and Tuning
- ASGI Worker
- Dirty Arbiters
- Custom Applications
- Control Interface (gunicornc)

---

## Worker Architecture (Pre-fork Model)

Gunicorn uses a **pre-fork worker model**:

- **Arbiter (Master)** — Orchestrates the worker pool. Listens for signals to adjust workers, restart on failure, or reload config. Never touches individual client sockets.
- **Worker Pool** — Each worker handles requests independently. Worker type determines concurrency model (sync, threaded, greenlets, asyncio).
- **Signal Communication** — `TTIN`/`TTOU` adjust worker count. `CHLD` triggers restart of crashed workers. `HUP` reloads configuration.

---

## Worker Types

### Decision Guide

| Scenario | Recommended Worker |
|----------|-------------------|
| Simple app behind nginx | `sync` (default) |
| Need keep-alive or moderate concurrency | `gthread` |
| WebSockets, streaming, long-polling | `gevent` or ASGI |
| FastAPI, Starlette, async framework | `asgi` |
| Native Tornado app | `tornado` |

### sync (Default)

Handles one request at a time per worker. Simple and predictable. No keep-alive support — requires a buffering proxy (nginx) for production.

```bash
gunicorn myapp:app --workers 4
```

### gthread

Thread pool per worker process. Supports keep-alive. Good balance of concurrency and simplicity. Threads share memory (lower footprint than extra workers).

```bash
gunicorn myapp:app -k gthread --workers 4 --threads 4
```

### gevent

Greenlet-based async worker. Handles thousands of concurrent connections. Supports keep-alive, WebSockets, long-polling. May require patches for some libraries (e.g., `psycogreen` for Psycopg).

```bash
pip install gunicorn[gevent]
gunicorn myapp:app -k gevent --workers 4 --worker-connections 1000
```

### asgi

Native asyncio support for FastAPI, Starlette, Quart. Full async/await with lifespan protocol and WebSocket support.

```bash
gunicorn myapp:app --worker-class asgi --workers 4
```

### tornado

Designed for Tornado's async framework. Not recommended for general WSGI use.

```bash
pip install gunicorn[tornado]
gunicorn myapp:app -k tornado
```

---

## Scaling and Tuning

### Worker Count

Start with `(2 * CPU_CORES) + 1`. Adjust under load using `TTIN`/`TTOU` signals:

```bash
kill -TTIN $masterpid   # increment workers
kill -TTOU $masterpid   # decrement workers
```

**Don't over-scale:** Gunicorn typically needs only 4-12 workers for heavy traffic. Too many workers waste resources and reduce throughput.

### Thread Count (gthread)

Combine workers and threads for the best of both worlds:

```bash
gunicorn myapp:app -k gthread --workers 4 --threads 2
```

- **Threads** share memory → lower footprint
- **Workers** isolate failures → better fault tolerance

### Connection Limits (async workers)

```bash
gunicorn myapp:app --worker-class asgi --worker-connections 2000
```

### Memory Leak Mitigation

Restart workers periodically:

```python
max_requests = 1000
max_requests_jitter = 200  # stagger restarts
```

### Timeout Tuning

```python
timeout = 30           # kill silent workers
graceful_timeout = 30  # time for graceful shutdown
keepalive = 2          # keep-alive timeout (1-5 range)
```

---

## ASGI Worker

### Configuration

```python
# gunicorn.conf.py
worker_class = "asgi"
workers = 4
worker_connections = 1000
asgi_loop = "auto"       # uvloop if available, else asyncio
asgi_lifespan = "auto"   # auto-detect lifespan support
```

### Event Loop

| Value | Description |
|-------|-------------|
| `auto` | Use uvloop if available, otherwise asyncio (default) |
| `asyncio` | Python's built-in asyncio |
| `uvloop` | uvloop (must be installed: `pip install uvloop`) |

### Lifespan Protocol

Allows startup/shutdown hooks for database connections, caches, background tasks:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")  # initialization
    yield
    print("Shutting down...")  # cleanup

app = FastAPI(lifespan=lifespan)
```

### WebSocket Support

Works out of the box with ASGI worker:

```python
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute

async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

app = Starlette(routes=[WebSocketRoute("/ws", websocket_endpoint)])
```

### Fast HTTP Parser

Install optional C extension for high throughput:

```bash
pip install gunicorn[fast]
gunicorn myapp:app --worker-class asgi --http-parser fast
```

### Framework Compatibility

Tested with Django+Channels, FastAPI, Starlette, Quart, Litestar, BlackSheep (98% test pass rate).

---

## Dirty Arbiters

Dirty Arbiters provide a separate process pool for long-running, blocking operations (ML inference, heavy computation) without blocking HTTP workers. Inspired by Erlang's dirty schedulers.

### Architecture

```
Main Arbiter
├── HTTP Workers (normal request handling)
└── Dirty Arbiter
    ├── Dirty Worker 1: [MLApp, ImageApp]
    ├── Dirty Worker 2: [MLApp, ImageApp]
    └── Dirty Worker 3: [MLApp]  # per-app allocation
```

### Configuration

```python
# gunicorn.conf.py
dirty_apps = [
    "myapp.ml:MLApp",           # All workers load this
    "myapp.images:ImageApp",    # All workers load this
    "myapp.heavy:HugeModel:2",  # Only 2 workers load this
]
dirty_workers = 3
dirty_timeout = 300
dirty_threads = 1
dirty_graceful_timeout = 30
```

### Creating a DirtyApp

```python
from gunicorn.dirty import DirtyApp

class MLApp(DirtyApp):
    workers = 2  # Optional: limit to N workers

    def __init__(self):
        self.models = {}

    def init(self):
        """Called once at worker startup — load resources here."""
        self.models['default'] = load_model('base-model')

    def __call__(self, action, *args, **kwargs):
        method = getattr(self, action, None)
        if method is None:
            raise ValueError(f"Unknown action: {action}")
        return method(*args, **kwargs)

    def inference(self, model_name, input_text):
        model = self.models.get(model_name)
        return model.predict(input_text)

    def close(self):
        """Cleanup on shutdown."""
        pass
```

### Using from HTTP Workers

**Sync workers:**

```python
from gunicorn.dirty import get_dirty_client

def my_view(request):
    client = get_dirty_client()
    result = client.execute("myapp.ml:MLApp", "inference", "default", request.data)
    return result
```

**Async (ASGI) workers:**

```python
from gunicorn.dirty import get_dirty_client_async

async def my_view(request):
    client = await get_dirty_client_async()
    result = await client.execute_async("myapp.ml:MLApp", "inference", "default", request.data)
    return result
```

### Streaming

Return generators from dirty app actions for streaming responses:

```python
class LLMApp(DirtyApp):
    def generate(self, prompt):
        for token in self.generator(prompt, stream=True):
            yield token["generated_text"]
```

**Sync client:**

```python
client = get_dirty_client()
for chunk in client.stream("myapp.llm:LLMApp", "generate", prompt):
    yield chunk
```

**Async client:**

```python
client = await get_dirty_client_async()
async for chunk in client.stream_async("myapp.llm:LLMApp", "generate", prompt):
    yield chunk
```

### Stash (Shared State)

Shared state between dirty workers via message passing to the arbiter (like Erlang ETS):

```python
from gunicorn.dirty import stash

# Store
stash.put("sessions", "user:123", {"name": "Alice"})

# Retrieve
user = stash.get("sessions", "user:123")

# Dict-like interface
sessions = stash.table("sessions")
sessions["user:456"] = {"name": "Bob"}
```

### Error Handling

```python
from gunicorn.dirty.errors import (
    DirtyError,
    DirtyTimeoutError,
    DirtyConnectionError,
    DirtyAppError,
    DirtyAppNotFoundError,
    DirtyNoWorkersAvailableError,
)

try:
    result = client.execute("myapp.ml:MLApp", "inference", data)
except DirtyTimeoutError:
    # Operation timed out
    pass
except DirtyNoWorkersAvailableError as e:
    # No workers have this app loaded
    print(f"No workers for: {e.app_path}")
```

---

## Custom Applications

### Subclassing BaseApplication

Run Gunicorn programmatically from Python:

```python
import multiprocessing
import gunicorn.app.base

def handler_app(environ, start_response):
    response_body = b'Works fine'
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [response_body]

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {k: v for k, v in self.options.items()
                  if k in self.cfg.settings and v is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == '__main__':
    options = {
        'bind': '127.0.0.1:8080',
        'workers': (multiprocessing.cpu_count() * 2) + 1,
    }
    StandaloneApplication(handler_app, options).run()
```

### Using Server Hooks in Custom Apps

```python
def pre_fork(server, worker):
    print(f"pre-fork server {server} worker {worker}", file=sys.stderr)

options = {
    "bind": "127.0.0.1:8080",
    "workers": 4,
    "pre_fork": pre_fork,
}
```

### Direct WSGI App Usage

Run Gunicorn from Python at runtime (useful for rolling deploys or PEX builds):

```bash
python -m gunicorn.app.wsgiapp exampleapi:app --bind=0.0.0.0:8081 --workers=4
```

---

## Control Interface (gunicornc)

Runtime management of Gunicorn via Unix socket control interface.

### Quick Start

```bash
# Start Gunicorn with control socket enabled (default in 25.1+)
gunicorn app:app

# Connect interactively
gunicornc
```

### Commands

| Command | Description |
|---------|-------------|
| `status` | Show server and worker status |
| `workers` | List workers with details |
| `reload` | Graceful reload (SIGHUP equivalent) |
| `shutdown` | Graceful shutdown |
| `scale N` | Set worker count to N |
| `dirty-status` | Show dirty arbiter/worker status |
| `dirty-scale N` | Set dirty worker count |

### Configuration

```python
# gunicorn.conf.py
control_socket = "/tmp/gunicorn.ctl"  # Custom path
control_socket_mode = 0o660            # Group access
# control_socket_disable = True        # Disable entirely
```

### Scripting

```bash
# Non-interactive commands
gunicornc status
gunicornc reload
gunicornc scale 8
```