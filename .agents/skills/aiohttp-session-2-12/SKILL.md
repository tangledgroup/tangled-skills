---
name: aiohttp-session-2-12
description: A skill for implementing server-side sessions in aiohttp web applications using aiohttp-session 2.12.1, providing multiple storage backends including encrypted cookies, Redis, and Memcached for persistent user state management. Use when building aiohttp.web applications that require session-based authentication, shopping carts, user preferences, or any per-request user-specific data persistence.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - aiohttp
  - sessions
  - web
  - async
  - storage
  - cookies
  - redis
  - encryption
category: development
required_environment_variables: []
---

# aiohttp-session-2-12

A comprehensive toolkit for implementing server-side sessions in aiohttp web applications using the aiohttp-session 2.12.1 library. Provides multiple storage backends including encrypted cookies, Redis, Memcached, and NaCl encryption for secure user state management across HTTP requests.

## When to Use

Load this skill when:
- Building aiohttp.web applications requiring session-based authentication or user state persistence
- Implementing shopping carts, user preferences, or per-request user-specific data
- Choosing between cookie-based vs server-side session storage backends
- Configuring encrypted sessions with Fernet or NaCl encryption
- Setting up Redis or Memcached-backed sessions for distributed applications
- Migrating from older aiohttp-session versions or other session libraries

## Setup

### Installation

Install the base package:

```bash
pip install aiohttp-session
```

Install with optional dependencies for specific storage backends:

```bash
# Encrypted cookie storage (Fernet encryption)
pip install 'aiohttp-session[secure]'

# Redis storage
pip install 'aiohttp-session[aioredis]'

# Memcached storage
pip install 'aiohttp-session[aiomcache]'

# NaCl encrypted cookies
pip install pynacl
```

### Basic Configuration

Setup sessions in an aiohttp application:

```python
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

def make_app():
    app = web.Application()
    
    # Generate or use a pre-existing 32-byte key
    secret_key = b'Thirty  two  length  bytes  key.'  # Exactly 32 bytes
    
    setup(app, EncryptedCookieStorage(secret_key))
    
    app.router.add_get('/handler', handler)
    return app

web.run_app(make_app())
```

See [Core API](references/01-core-api.md) for detailed session operations and [Storage Backends](references/02-storage-backends.md) for all available storage options.

## Quick Start

### Using Encrypted Cookie Sessions

The recommended approach for most applications:

```python
from cryptography.fernet import Fernet
from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

async def handler(request):
    session = await get_session(request)
    
    # Check if user has visited before
    if 'visit_count' in session:
        session['visit_count'] += 1
    else:
        session['visit_count'] = 1
    
    return web.Response(text=f'You have visited {session["visit_count"]} times')

def make_app():
    app = web.Application()
    
    # Generate a proper Fernet key (32 bytes, base64-encoded)
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)
    
    setup(app, EncryptedCookieStorage(fernet))
    app.router.add_get('/', handler)
    return app

web.run_app(make_app())
```

See [Core API](references/01-core-api.md) for session methods and best practices.

### Using Redis Sessions

For distributed applications or large session data:

```python
import asyncio
from redis.asyncio import from_url
from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.redis_storage import RedisStorage

async def make_app():
    app = web.Application()
    
    # Connect to Redis
    redis = await from_url("redis://localhost:6379", decode_responses=False)
    
    setup(app, RedisStorage(redis))
    
    async def handler(request):
        session = await get_session(request)
        session['user_data'] = {'name': 'John', 'role': 'admin'}
        return web.Response(text='Session saved to Redis')
    
    app.router.add_get('/', handler)
    return app

asyncio.run(make_app())
```

See [Storage Backends](references/02-storage-backends.md) for Redis configuration options.

## Common Operations

### Reading and Writing Session Data

```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    
    # Set values (automatically marks session as changed)
    session['username'] = 'john_doe'
    session['preferences'] = {'theme': 'dark', 'language': 'en'}
    
    # Read values
    username = session.get('username', 'guest')
    
    # Check if key exists
    if 'cart_items' in session:
        items = session['cart_items']
    
    return web.Response(text=f'Hello, {username}')
```

### Session Lifecycle Management

```python
from aiohttp_session import get_session, new_session

async def login_handler(request):
    # Always use new_session() in login views to prevent session fixation
    session = await new_session(request)
    session['user_id'] = 12345
    session['logged_in'] = True
    return web.Response(text='Logged in')

async def logout_handler(request):
    session = await get_session(request)
    session.invalidate()  # Clear all session data
    return web.Response(text='Logged out')
```

### Working with Mutable Session Data

```python
async def cart_handler(request):
    session = await get_session(request)
    
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    # Mutating a list requires calling changed()
    session['cart'].append({'item': 'widget', 'qty': 2})
    session.changed()  # Mark session as modified
    
    return web.Response(text='Item added to cart')
```

## Reference Files

- [`references/01-core-api.md`](references/01-core-api.md) - Session class methods, get_session/new_session functions, middleware setup
- [`references/02-storage-backends.md`](references/02-storage-backends.md) - All 5 storage implementations with configuration options and examples
- [`references/03-cookie-configuration.md`](references/03-cookie-configuration.md) - Cookie parameters (domain, path, secure, httponly, samesite, max_age)
- [`references/04-security-best-practices.md`](references/04-security-best-practices.md) - Session fixation prevention, encryption setup, security hardening

## Troubleshooting

### Common Issues

**Session not persisting between requests:**
- Verify `setup(app, storage)` is called before adding routes
- Ensure the storage backend is properly initialized (Redis connection, valid encryption key)
- Check browser is accepting cookies (cookie name defaults to `AIOHTTP_SESSION`)

**EncryptedCookieStorage decryption errors:**
- Secret key must be exactly 32 bytes for Fernet encryption
- Use `Fernet.generate_key()` to create a valid key
- Key rotation requires migrating existing sessions

**Redis connection errors:**
- Ensure redis-py >= 4.3 is installed (`pip install 'aiohttp-session[aioredis]'`)
- Redis URL must be in format: `redis://host:port/db`
- Check Redis server is running and accessible

**Session data not serializing:**
- Session values must be JSON-serializable (dict, list, str, int, float, bool, None)
- For custom objects, implement custom encoder/decoder functions
- Use `json.dumps(obj)` to test serializability before storing in session

See [Storage Backends](references/02-storage-backends.md) for backend-specific troubleshooting and [Security Best Practices](references/04-security-best-practices.md) for security-related issues.
