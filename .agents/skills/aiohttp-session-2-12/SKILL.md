---
name: aiohttp-session-2-12
description: Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends including encrypted cookies (Fernet/NaCl), Redis, and Memcached for persistent user state management. Use when building aiohttp.web applications that require session-based authentication, shopping carts, user preferences, or any per-request user-specific data persistence.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.12.0"
tags:
  - aiohttp
  - sessions
  - web
  - async
  - storage
  - cookies
  - redis
  - memcached
  - encryption
category: development
external_references:
  - https://github.com/aio-libs/aiohttp-session
  - https://aiohttp-session.readthedocs.io/
---

# aiohttp-session 2.12

## Overview

aiohttp-session provides server-side session support for `aiohttp.web` applications. It gives every HTTP request access to a dict-like `Session` object that persists user-specific data across requests. The library supports multiple storage backends — from simple plaintext cookies (testing only) to Fernet-encrypted cookies, NaCl-encrypted cookies, Redis, and Memcached — letting you choose the right trade-off between security, performance, and infrastructure complexity.

The session is integrated as aiohttp middleware, automatically loading on request and saving on response. Session data is stored in an HTTP cookie named `AIOHTTP_SESSION` by default (configurable via `cookie_name`).

## When to Use

- Building aiohttp.web applications that need per-user state across requests
- Implementing session-based authentication flows
- Storing shopping cart contents, user preferences, or form draft data
- Migrating from framework-provided sessions to a lightweight asyncio-compatible alternative
- Needing encrypted cookie sessions without server-side storage
- Requiring distributed session storage via Redis or Memcached for multi-instance deployments

## Core Concepts

**Session**: A dict-like (`MutableMapping`) object representing user state valid for a period of continual activity. Retrieved via `await get_session(request)` — never instantiated directly.

**Storage**: The backend responsible for persisting and loading session data. All storages derive from `AbstractStorage` and implement `load_session()` and `save_session()`. Every storage uses an HTTP cookie to store at least the session key; some (cookie-based) store all data in the cookie itself.

**Middleware**: The session system works as aiohttp middleware, registered via `setup(app, storage)`. It attaches the storage to each request and automatically saves changed sessions on response.

**Session Lifecycle**: On each request, the middleware loads the session from storage. If the handler modifies it (via `__setitem__`, `del`, or explicit `session.changed()`), the session is serialized and saved when the response is generated.

## Installation / Setup

Install with pip:

```bash
pip install aiohttp-session
```

Optional extras for specific backends:

- `aiohttp-session[secure]` — Fernet-encrypted cookies (requires `cryptography`)
- `aiohttp-session[aioredis]` — Redis storage (requires `redis>=4.3` with asyncio support)
- `aiohttp-session[aiomcache]` — Memcached storage (requires `aiomcache`)

## Usage Examples

### Basic Setup with Encrypted Cookies

```python
import time
from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage


async def handler(request):
    session = await get_session(request)
    last_visit = session.get('last_visit')
    session['last_visit'] = time.time()
    return web.Response(text=f'Last visited: {last_visit}')


def make_app():
    app = web.Application()
    # Generate a 32-byte key: Fernet.generate_key() or use os.urandom(32)
    secret = b'Thirty  two  length  bytes  key.'
    setup(app, EncryptedCookieStorage(secret))
    app.router.add_get('/', handler)
    return app


web.run_app(make_app())
```

### Using Session Properties

```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)

    # Check if this is a brand new session
    if session.new:
        session['visit_count'] = 0
    else:
        session['visit_count'] = session.get('visit_count', 0) + 1

    # Session creation timestamp (UNIX epoch)
    print(f'Session created at: {session.created}')

    # Invalidate (clear all data and set clearing cookie)
    # session.invalidate()

    return web.Response(text=f'Visit #{session["visit_count"]}')
```

### Calling `changed()` for Mutable Values

```python
async def handler(request):
    session = await get_session(request)
    if 'items' not in session:
        session['items'] = []

    # Mutating a nested list — session doesn't auto-detect this
    session['items'].append('new-item')
    session.changed()  # Required! Tell the session it was modified

    # Direct assignment auto-tracks changes:
    session['count'] = len(session['items'])  # No .changed() needed

    return web.Response(text='OK')
```

### Preventing Session Fixation with `new_session()`

```python
from aiohttp_session import new_session

async def login(request):
    # Always use new_session() in login views to prevent session fixation
    session = await new_session(request)
    assert session.new is True  # Guaranteed fresh session

    # Now safely store authenticated user data
    session['user_id'] = 'authenticated-user-123'
    return web.Response(text='Logged in')
```

### Custom Cookie Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=b'Thirty  two  length  bytes  key.',
    cookie_name='MY_APP_SESSION',   # Custom cookie name
    max_age=3600,                    # 1 hour expiry
    path='/app/',                    # Cookie path scope
    secure=True,                     # HTTPS only
    httponly=True,                   # No JavaScript access
    samesite='Lax',                 # CSRF protection
)
```

## Advanced Topics

**Session Object API**: Properties, methods, and the `changed()`/`invalidate()` lifecycle → [Session Reference](reference/01-session-reference.md)

**Storage Backends**: Detailed guide to all five storage implementations — SimpleCookie, EncryptedCookie (Fernet), NaCl, Redis, and Memcached → [Storage Backends](reference/02-storage-backends.md)

**AbstractStorage and Custom Storages**: Building custom session backends by extending `AbstractStorage` with `load_session()` and `save_session()` → [Custom Storages](reference/03-custom-storages.md)

**Middleware Internals and Third-Party Extensions**: How the middleware works, request/response flow, and community extensions for MongoDB, DynamoDB, and Firestore → [Middleware and Extensions](reference/04-middleware-and-extensions.md)
