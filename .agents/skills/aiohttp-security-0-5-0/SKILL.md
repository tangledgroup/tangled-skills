---
name: aiohttp-security-0-5-0
description: Authentication and authorization toolkit for aiohttp.web applications providing identity policies (cookies, sessions, JWT) and custom authorization with permission-based access control. Use when building aiohttp.web applications requiring session-based authentication, protecting routes with permission checks, implementing login/logout flows, or integrating JWT bearer tokens.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - aiohttp
  - authentication
  - authorization
  - identity-policy
  - permission
  - session
  - jwt
  - security
category: web-framework
external_references:
  - https://github.com/aio-libs/aiohttp-security
  - https://aiohttp-security.readthedocs.io/
---

# aiohttp-security 0.5.0

## Overview

`aiohttp_security` provides identity and authorization for `aiohttp.web` applications. Part of the [aio-libs](https://github.com/aio-libs) project, it separates concerns into two abstract policies:

- **Identity Policy** — handles remembering, identifying, and forgetting a user's identity (authentication persistence via cookies, sessions, or JWT).
- **Authorization Policy** — maps identities to user IDs and checks permissions (developer-implemented per application).

Ships with three built-in identity policies (`CookiesIdentityPolicy`, `SessionIdentityPolicy`, `JWTIdentityPolicy`) and expects developers to implement their own authorization policy.

## When to Use

- Building aiohttp.web applications requiring user authentication and route-level authorization
- Implementing login/logout flows with session or cookie-based identity persistence
- Protecting endpoints with permission-based access control
- Integrating JWT bearer token authentication into aiohttp applications
- Building custom authorization logic backed by databases, LDAP, or other user stores

## Core Concepts

### Identity

A session-wide string identifying the user between browser and server. Use random strings (UUIDs, hashes) rather than database IDs, usernames, or emails. Stored client-side (cookie) or server-side (session storage).

### Userid

The user's persistent identifier — typically their login name or email. Retrieved from the identity via the authorization policy's `authorized_userid()` method.

### Permission

A string (or enum) representing an access right required to reach a resource. Developers define whatever permission names make sense (e.g., `"read"`, `"write"`, `"admin"`).

### Authentication vs Authorization

- **Authentication** confirms who the user is (identity verification). Developer implements; library requires it results in an identity string.
- **Authorization** checks what the authenticated user is allowed to do (permission checking via authorization policy).

## Installation / Setup

```bash
pip install aiohttp-security          # basic cookie support
pip install aiohttp-security[session] # with aiohttp-session support
pip install PyJWT                     # for JWT identity policy
```

Requires `aiohttp>=3.9`, Python 3.9+. Optional: `aiohttp-session`, `PyJWT`.

## Usage Examples

### Basic Setup with Session Identity

Most common pattern uses `SessionIdentityPolicy` with a custom authorization policy:

```python
from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import check_permission, is_anonymous, remember, forget, setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        """Return user_id for the given identity, or None if unknown."""
        pass

    async def permits(self, identity, permission, context=None):
        """Return True if identity has the permission, else False."""
        return False


async def make_app():
    middleware = session_middleware(SimpleCookieStorage())
    app = web.Application(middlewares=[middleware])
    app.add_routes([
        web.get('/', handler_root),
        web.get('/login', handler_login),
        web.get('/logout', handler_logout),
        web.get('/protected', handler_protected),
    ])
    setup_security(app, SessionIdentityPolicy(), MyAuthorizationPolicy())
    return app
```

> **Warning:** Never use `SimpleCookieStorage` in production. Use `EncryptedCookieStorage` or `RedisStorage`.

### Login Handler

```python
async def handler_login(request):
    data = await request.post()
    username, password = data.get('username'), data.get('password')
    if not await verify_credentials(username, password):
        return web.Response(text="Invalid credentials", status=401)
    redirect_response = web.HTTPFound('/')
    await remember(request, redirect_response, username)
    raise redirect_response
```

### Logout Handler

```python
async def handler_logout(request):
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    raise redirect_response
```

### Protecting Routes with Permissions

```python
async def handler_protected(request):
    await check_permission(request, 'admin')
    return web.Response(text="You have admin access!")
```

`check_permission()` raises `HTTPUnauthorized` if anonymous, `HTTPForbidden` if lacking the permission.

### Checking Authentication Without Permissions

```python
from aiohttp_security import check_authorized

async def handler_account(request):
    userid = await check_authorized(request)
    return web.Response(text=f"Welcome, {userid}!")
```

### Checking Anonymous Status

```python
async def handler_root(request):
    is_logged = not await is_anonymous(request)
    return web.Response(text=f"You are {'logged in' if is_logged else 'anonymous'}")
```

### Getting the Current User ID

```python
from aiohttp_security import authorized_userid

async def handler_profile(request):
    userid = await authorized_userid(request)
    if userid is None:
        return web.Response(text="Not logged in", status=401)
    return web.Response(text=f"User ID: {userid}")
```

### Direct Permission Checking

```python
from aiohttp_security import permits

async def handler_dashboard(request):
    can_edit = await permits(request, 'edit')
    can_delete = await permits(request, 'delete')
    return web.json_response({"can_edit": can_edit, "can_delete": can_delete})
```

## Advanced Topics

**API Reference**: Public API functions, abstract policies, built-in identity policies → [API Reference](reference/01-api-reference.md)

**Advanced Patterns**: Database-backed authorization, enum permissions, complete app setup, password verification, identity best practices → [Advanced Patterns](reference/02-advanced-patterns.md)
