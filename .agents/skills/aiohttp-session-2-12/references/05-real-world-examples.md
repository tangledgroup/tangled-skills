# Real-World Examples

This document provides practical, production-ready examples from the aiohttp-session library demonstrating common patterns including flash messages, authentication decorators, and server-side storage setups.

## Basic Encrypted Cookie Session

The simplest example of using encrypted cookie sessions with aiohttp-session.

```python
import base64
import time

from aiohttp import web
from cryptography import fernet

from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage


async def handler(request: web.Request) -> web.Response:
    session = await get_session(request)
    
    # Track last visit timestamp
    last_visit = session["last_visit"] if "last_visit" in session else None
    session["last_visit"] = time.time()
    
    text = f"Last visited: {last_visit}"
    return web.Response(text=text)


def make_app() -> web.Application:
    app = web.Application()
    
    # Generate Fernet key and extract raw bytes
    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    
    setup(app, EncryptedCookieStorage(secret_key))
    app.router.add_get("/", handler)
    return app


web.run_app(make_app())
```

**Key points:**
- `Fernet.generate_key()` returns a base64-encoded key
- Decode with `base64.urlsafe_b64decode()` to get raw 32-byte key
- Session data persists across requests automatically
- Timestamp stored as Unix timestamp (float)

---

## Flash Messages Pattern

Implement flash messages (one-time notifications that persist across redirects) using session storage.

### Complete Implementation

```python
import base64
from typing import Awaitable, Callable, List, NoReturn, cast

from aiohttp import web
from aiohttp.typedefs import Handler
from cryptography import fernet

from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage


def flash(request: web.Request, message: str) -> None:
    """Add a flash message to be shown on the next request."""
    request.setdefault("flash_outgoing", []).append(message)


def get_messages(request: web.Request) -> List[str]:
    """Retrieve flash messages from the current request."""
    return cast(List[str], request.pop("flash_incoming"))


@web.middleware
async def flash_middleware(
    request: web.Request, handler: Handler
) -> web.StreamResponse:
    """
    Middleware that transfers flash messages from session to request.
    
    Must be installed AFTER aiohttp-session middleware.
    """
    session = await get_session(request)
    
    # Load flash messages from session into request
    request["flash_incoming"] = session.pop("flash", [])
    
    try:
        return await handler(request)
    finally:
        # Save new flash messages back to session
        session["flash"] = (
            request.get("flash_incoming", []) + 
            request.get("flash_outgoing", [])
        )


async def flash_handler(request: web.Request) -> NoReturn:
    """Page that sets a flash message and redirects."""
    flash(request, "You have just visited flash page")
    raise web.HTTPFound("/")


async def handler(request: web.Request) -> web.Response:
    """Main page that displays flash messages."""
    text = "No flash messages yet"
    messages = get_messages(request)
    
    if messages:
        text = f"Messages: {','.join(messages)}"
    
    return web.Response(text=text)


def make_app() -> web.Application:
    app = web.Application()
    
    # Generate encryption key
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    
    setup(app, EncryptedCookieStorage(secret_key))
    
    # Install flash middleware AFTER session middleware
    app.middlewares.append(flash_middleware)
    
    app.router.add_get("/", handler)
    app.router.add_get("/flash", flash_handler)
    return app


web.run_app(make_app())
```

### How It Works

1. **Setting a flash message:** Call `flash(request, "message")` in your handler
2. **Middleware stores it:** Flash middleware saves message to session in `finally` block
3. **Redirect happens:** User is redirected to another page
4. **Next request loads it:** Flash middleware pops message from session into request
5. **Display and consume:** Handler retrieves with `get_messages(request)` - message is gone after this request

### Usage in Templates

```python
async def success_page(request: web.Request) -> web.Response:
    messages = get_messages(request)
    
    html = "<html><body>"
    if messages:
        html += '<div class="alerts">'
        for msg in messages:
            html += f'<div class="alert">{msg}</div>'
        html += '</div>'
    html += "</body></html>"
    
    return web.Response(content_type="text/html", text=html)
```

### Flash Message Categories

Extend the pattern to support different message types:

```python
from typing import Dict, Tuple

# Type: (category, message)
FlashMessage = Tuple[str, str]
FlashMessages = List[FlashMessage]

def flash(request: web.Request, message: str, category: str = "info") -> None:
    """Add categorized flash message."""
    request.setdefault("flash_outgoing", []).append((category, message))

def get_messages(request: web.Request) -> FlashMessages:
    return cast(FlashMessages, request.pop("flash_incoming"))

@web.middleware
async def flash_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    session = await get_session(request)
    request["flash_incoming"] = session.pop("flash", [])
    try:
        return await handler(request)
    finally:
        session["flash"] = (
            request.get("flash_incoming", []) + 
            request.get("flash_outgoing", [])
        )

# Usage
flash(request, "Login successful!", category="success")
flash(request, "Invalid password", category="error")
flash(request, "Please verify your email", category="warning")
```

---

## Login Required Decorator

Protect routes with a decorator that checks for authentication and redirects to login if needed.

### Complete Implementation

```python
import base64
from http import HTTPStatus
from typing import Any, Awaitable, Callable

from aiohttp import web
from cryptography import fernet

from aiohttp_session import get_session, new_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Mock database (replace with actual database queries)
DATABASE = [
    ("admin", "admin"),
    ("user", "password"),
]

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]
user_key = web.AppKey("user", str)


def login_required(fn: _Handler) -> _Handler:
    """
    Decorator that requires user to be logged in.
    
    Redirects to login page if user is not authenticated.
    Stores user info in request.app for access in handler.
    """
    async def wrapped(
        request: web.Request, *args: Any, **kwargs: Any
    ) -> web.StreamResponse:
        app = request.app
        router = app.router

        session = await get_session(request)

        # Check if user is authenticated
        if "user_id" not in session:
            raise web.HTTPFound(router["login"].url_for())

        user_id = session["user_id"]
        
        # Load user from database (replace with actual DB query)
        user = DATABASE[user_id]
        
        # Store user in app for handler access
        app[user_key] = user
        
        return await fn(request, *args, **kwargs)

    return wrapped


@login_required
async def restricted_handler(request: web.Request) -> web.Response:
    """Protected endpoint - only accessible when logged in."""
    user = request.app[user_key]
    return web.Response(text=f"User {user} authorized")


# Login form template
LOGIN_TEMPLATE = """\
<html>
    <body>
        <form method="post" action="/login">
            <label>Name:</label><input type="text" name="name"/>
            <label>Password:</label><input type="password" name="password"/>
            <input type="submit" value="Login"/>
        </form>
    </body>
</html>"""


async def login_page(request: web.Request) -> web.Response:
    """Display login form."""
    return web.Response(content_type="text/html", text=LOGIN_TEMPLATE)


async def login_handler(request: web.Request) -> web.Response:
    """
    Process login form.
    
    CRITICAL: Uses new_session() to prevent session fixation attacks.
    See aiohttp-session#281 for details.
    """
    router = request.app.router
    form = await request.post()
    user_signature = (form["name"], form["password"])

    # Validate credentials (replace with actual authentication)
    try:
        user_id = DATABASE.index(user_signature)
        
        # Always use new_session() during login to prevent session fixation!
        session = await new_session(request)
        session["user_id"] = user_id
        
        # Redirect to protected page
        raise web.HTTPFound(router["restricted"].url_for())
        
    except ValueError:
        # Invalid credentials
        return web.Response(
            text="No such user", 
            status=HTTPStatus.FORBIDDEN
        )


def make_app() -> web.Application:
    app = web.Application()
    
    # Generate encryption key
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    
    setup(app, EncryptedCookieStorage(secret_key))
    
    # Register routes with names for URL generation
    app.router.add_get("/", restricted_handler, name="restricted")
    app.router.add_get("/login", login_page, name="login")
    app.router.add_post("/login", login_handler)
    
    return app


web.run_app(make_app())
```

### Key Security Features

**Session Fixation Prevention:**
```python
# ✅ CORRECT: Use new_session() in login handler
session = await new_session(request)
session["user_id"] = user_id

# ❌ VULNERABLE: Don't use get_session() in login
session = await get_session(request)  # Attacker can set session beforehand!
session["user_id"] = user_id
```

**Why it matters:**
- Without `new_session()`, attacker sets known session ID before login
- User logs in, session becomes authenticated with attacker-known ID
- Attacker uses that ID to hijack the session

### Enhanced Decorator with Flash Messages

```python
from typing import Optional

def login_required(
    fn: _Handler, 
    login_url: Optional[str] = None
) -> _Handler:
    """Enhanced decorator with custom login URL and flash messages."""
    async def wrapped(request: web.Request) -> web.StreamResponse:
        session = await get_session(request)
        
        if "user_id" not in session:
            # Store intended destination for redirect after login
            session["next_url"] = request.rel_url.path
            
            # Add flash message
            if hasattr(request, 'flash_outgoing'):
                flash(request, "Please log in to access this page")
            
            router = request.app.router
            raise web.HTTPFound(
                login_url or router["login"].url_for()
            )
        
        user_id = session["user_id"]
        user = await get_user_from_database(user_id)  # Replace with actual query
        request.app[user_key] = user
        
        return await fn(request)
    
    return wrapped
```

### Logout Handler

```python
async def logout_handler(request: web.Request) -> web.Response:
    """Secure logout that invalidates session."""
    session = await get_session(request)
    
    # Log logout for audit trail (optional)
    if "user_id" in session:
        await log_logout(session["user_id"], request.remote)
    
    # Invalidate session
    session.invalidate()
    
    # Add flash message
    if hasattr(request, 'flash'):
        flash(request, "You have been logged out")
    
    raise web.HTTPFound(request.app.router["login"].url_for())
```

---

## Redis Storage Setup

Use Redis for server-side session storage when you need to:
- Store large session data (beyond cookie size limits)
- Invalidate sessions centrally (e.g., force logout)
- Share sessions across multiple servers
- Persist sessions with controlled expiration

### Complete Implementation

```python
import time
from typing import AsyncIterator

from aiohttp import web
from redis import asyncio as aioredis

from aiohttp_session import get_session, setup
from aiohttp_session.redis_storage import RedisStorage


async def handler(request: web.Request) -> web.Response:
    session = await get_session(request)
    
    # Session data stored in Redis, only UUID in cookie
    last_visit = session["last_visit"] if "last_visit" in session else None
    session["last_visit"] = time.time()
    
    text = f"Last visited: {last_visit}"
    return web.Response(text=text)


async def redis_pool(app: web.Application) -> AsyncIterator[None]:
    """
    Application cleanup context for Redis connection.
    
    Creates Redis connection on startup, closes on shutdown.
    """
    redis_address = "redis://127.0.0.1:6379"
    
    async with aioredis.from_url(redis_address) as redis:
        storage = RedisStorage(redis)
        setup(app, storage)
        
        # Yield control while connection is active
        yield
    
    # Connection automatically closed after yield


def make_app() -> web.Application:
    app = web.Application()
    
    # Register cleanup context
    app.cleanup_ctx.append(redis_pool)
    
    app.router.add_get("/", handler)
    return app


web.run_app(make_app())
```

### Redis with Authentication

```python
async def redis_pool(app: web.Application) -> AsyncIterator[None]:
    """Redis connection with authentication."""
    redis_address = "redis://:password@127.0.0.1:6379/0"
    
    async with aioredis.from_url(
        redis_address,
        max_connections=10,
        health_check_interval=30
    ) as redis:
        storage = RedisStorage(redis, max_age=3600)  # 1 hour expiry
        setup(app, storage)
        yield


def make_app() -> web.Application:
    app = web.Application()
    app.cleanup_ctx.append(redis_pool)
    app.router.add_get("/", handler)
    return app
```

### Redis with TLS

```python
async def redis_pool(app: web.Application) -> AsyncIterator[None]:
    """Redis connection over TLS."""
    redis_address = "rediss://:password@redis.example.com:6380"
    
    async with aioredis.from_url(
        redis_address,
        ssl=True,
        ssl_ca_certs="/path/to/ca-cert.pem"
    ) as redis:
        storage = RedisStorage(redis)
        setup(app, storage)
        yield
```

### Manual Connection Management

Alternative to cleanup_ctx:

```python
import asyncio
from aiohttp import web
from redis import asyncio as aioredis
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage


async def make_app() -> web.Application:
    app = web.Application()
    
    # Create Redis connection
    redis = await aioredis.from_url("redis://127.0.0.1:6379")
    
    # Setup session storage
    storage = RedisStorage(redis, max_age=3600)
    setup(app, storage)
    
    app.router.add_get("/", handler)
    return app


async def cleanup_app(app: web.Application) -> None:
    """Close Redis connection on shutdown."""
    redis = app.get("redis")
    if redis:
        await redis.close()


app = asyncio.run(make_app())
app.on_cleanup.append(cleanup_app)
web.run_app(app)
```

---

## Memcached Storage Setup

Use Memcached for fast, in-memory session storage.

### Complete Implementation

```python
import asyncio
import time

import aiomcache
from aiohttp import web

from aiohttp_session import get_session, setup
from aiohttp_session.memcached_storage import MemcachedStorage


async def handler(request: web.Request) -> web.Response:
    session = await get_session(request)
    
    last_visit = session["last_visit"] if "last_visit" in session else None
    session["last_visit"] = time.time()
    
    text = f"Last visited: {last_visit}"
    return web.Response(text=text)


async def make_app() -> web.Application:
    app = web.Application()
    
    # Create Memcached client
    mc = aiomcache.Client("127.0.0.1", 11211)
    
    # Setup session storage with 1-hour expiry
    storage = MemcachedStorage(mc, max_age=3600)
    setup(app, storage)
    
    app.router.add_get("/", handler)
    return app


# Run application
loop = asyncio.get_event_loop()
app = loop.run_until_complete(make_app())
web.run_app(app)
```

### Memcached with Multiple Servers

```python
async def make_app() -> web.Application:
    app = web.Application()
    
    # Connect to multiple Memcached servers for load balancing
    mc = aiomcache.Client(
        [("server1.example.com", 11211), 
         ("server2.example.com", 11211)],
        retries=3,
        retry_delay=0.1
    )
    
    storage = MemcachedStorage(mc, max_age=1800)
    setup(app, storage)
    
    app.router.add_get("/", handler)
    return app
```

---

## Production Configuration Example

Complete production-ready setup with environment-based configuration.

```python
import os
import base64
from typing import Optional

from aiohttp import web
from cryptography import fernet

from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage


def get_session_key() -> bytes:
    """Get session encryption key from environment."""
    key = os.environ.get("SESSION_KEY")
    if not key:
        raise ValueError(
            "SESSION_KEY environment variable required. "
            "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key())'"
        )
    
    # Decode base64 key to raw bytes
    return base64.urlsafe_b64decode(key)


def get_max_age() -> Optional[int]:
    """Get session max age from environment."""
    age_str = os.environ.get("SESSION_MAX_AGE", "86400")  # Default: 24 hours
    return int(age_str) if age_str else None


def make_app() -> web.Application:
    app = web.Application()
    
    # Get configuration from environment
    secret_key = get_session_key()
    max_age = get_max_age()
    is_production = os.environ.get("ENVIRONMENT") == "production"
    
    # Configure storage with security settings
    storage = EncryptedCookieStorage(
        secret_key=secret_key,
        cookie_name="session",
        max_age=max_age,
        path="/",
        domain=".example.com" if is_production else None,
        secure=is_production,  # HTTPS only in production
        httponly=True,         # Always prevent JavaScript access
        samesite="Lax"         # CSRF protection
    )
    
    setup(app, storage)
    app.router.add_get("/", handler)
    return app


async def handler(request: web.Request) -> web.Response:
    session = await get_session(request)
    
    # Track user activity
    if "user_id" in session:
        session["last_activity"] = __import__("time").time()
    
    return web.Response(text="Hello!")


if __name__ == "__main__":
    import os
    
    # Development defaults
    if not os.environ.get("SESSION_KEY"):
        from cryptography.fernet import Fernet
        os.environ["SESSION_KEY"] = Fernet.generate_key().decode()
    
    web.run_app(make_app(), host="0.0.0.0", port=8080)
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate session key if not provided
ENV SESSION_KEY=""
ENV SESSION_MAX_AGE=86400
ENV ENVIRONMENT=production

CMD ["python", "app.py"]
```

Run with:
```bash
docker run -p 8080:8080 \
  -e SESSION_KEY="your-32-byte-base64-key-here" \
  -e SESSION_MAX_AGE=86400 \
  -e ENVIRONMENT=production \
  myapp
```

---

## Comparison: Cookie vs Server-Side Storage

| Feature | EncryptedCookieStorage | RedisStorage | MemcachedStorage |
|---------|----------------------|--------------|------------------|
| **Setup complexity** | Minimal | Moderate | Moderate |
| **External dependency** | None | Redis server | Memcached server |
| **Session size limit** | ~3.5KB (cookie limit) | ~1MB (Memcached limit) | ~1MB |
| **Invalidate single session** | No (must rotate keys) | Yes | Yes |
| **Horizontal scaling** | ✅ Built-in | ✅ Centralized | ✅ Centralized |
| **Session persistence** | Browser cookie lifetime | Configurable TTL | Configurable TTL |
| **Network latency** | None | +1 roundtrip | +1 roundtrip |
| **Single point of failure** | No | Yes (use cluster) | Yes (use pool) |

### When to Use Each

**EncryptedCookieStorage:**
- ✅ Most web applications
- ✅ Simple deployment, no external services
- ✅ Stateless scaling
- ❌ Limited to ~3.5KB session data
- ❌ Can't force logout remotely

**RedisStorage:**
- ✅ Large session data needed
- ✅ Need centralized session invalidation
- ✅ Multiple servers sharing sessions
- ✅ Session analytics/monitoring
- ❌ Requires Redis infrastructure
- ❌ Additional network latency

**MemcachedStorage:**
- ✅ Fast in-memory storage
- ✅ Already using Memcached for caching
- ✅ Large session data
- ❌ No persistence (data lost on restart)
- ❌ Less feature-rich than Redis
