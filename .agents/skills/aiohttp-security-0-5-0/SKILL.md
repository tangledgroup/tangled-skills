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

`aiohttp_security` provides identity and authorization for `aiohttp.web` applications. It is part of the [aio-libs](https://github.com/aio-libs) project and leverages Python's asyncio for asynchronous processing.

The library separates concerns into two abstract policies:

- **Identity Policy** — handles remembering, identifying, and forgetting a user's identity (authentication persistence via cookies, sessions, or JWT).
- **Authorization Policy** — maps identities to user IDs and checks permissions (developer-implemented per application).

It ships with three built-in identity policies (`CookiesIdentityPolicy`, `SessionIdentityPolicy`, `JWTIdentityPolicy`) and expects developers to implement their own authorization policy tailored to the application's access control needs.

## When to Use

- Building aiohttp.web applications that require user authentication and route-level authorization
- Implementing login/logout flows with session or cookie-based identity persistence
- Protecting endpoints with permission-based access control
- Integrating JWT bearer token authentication into aiohttp applications
- Building custom authorization logic backed by databases, LDAP, or other user stores

## Core Concepts

### Identity

A session-wide string that identifies the user between browser and server. It is recommended to use a random string such as a UUID or hash rather than database primary keys, usernames, or emails. The identity is stored client-side (cookie) or server-side (session storage).

### Userid

The user's persistent identifier — typically their login name or email. Retrieved from the identity via the authorization policy's `authorized_userid()` method.

### Permission

A string (or enum) representing an access right required to reach a resource. Permissions have no required composition — developers define whatever permission names make sense for their application (e.g., `"read"`, `"write"`, `"admin"`).

### Authentication vs Authorization

- **Authentication** confirms who the user is (identity verification). In aiohttp_security, the developer implements authentication logic; the library only requires that it results in an identity string.
- **Authorization** checks what the authenticated user is allowed to do (permission checking via the authorization policy).

## Installation / Setup

Install with basic cookie-based support:

```bash
pip install aiohttp-security
```

With `aiohttp-session` support for server-side sessions:

```bash
pip install aiohttp-security[session]
```

For JWT identity policy, also install PyJWT:

```bash
pip install PyJWT
```

### Dependencies

- `aiohttp>=3.9` (required)
- `aiohttp-session` (optional, for `SessionIdentityPolicy`)
- `PyJWT` (optional, for `JWTIdentityPolicy`)
- Python 3.9+

## Usage Examples

### Basic Setup with Session Identity

The most common pattern uses `SessionIdentityPolicy` with a custom authorization policy:

```python
from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import check_permission, is_anonymous, remember, forget, setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        """Return user_id for the given identity, or None if unknown."""
        # Look up user by identity in your database/store
        # Return str(user_id) if found, None otherwise
        pass

    async def permits(self, identity, permission, context=None):
        """Return True if identity has the permission, else False."""
        # Check permissions from your database/store
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

> **Warning:** Never use `SimpleCookieStorage` in production. Use `EncryptedCookieStorage` or `RedisStorage` instead.

### Login Handler

After authenticating a user (e.g., verifying credentials against a database), call `remember()` to persist their identity:

```python
async def handler_login(request):
    # 1. Extract and validate credentials from request
    data = await request.post()
    username = data.get('username')
    password = data.get('password')

    # 2. Verify credentials (developer responsibility)
    if not await verify_credentials(username, password):
        return web.Response(text="Invalid credentials", status=401)

    # 3. Remember the user's identity and redirect
    redirect_response = web.HTTPFound('/')
    await remember(request, redirect_response, username)
    raise redirect_response
```

### Logout Handler

Use `forget()` to clear the user's identity:

```python
async def handler_logout(request):
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    raise redirect_response
```

### Protecting Routes with Permissions

Use `check_permission()` to enforce access control on routes:

```python
async def handler_protected(request):
    await check_permission(request, 'admin')
    return web.Response(text="You have admin access!")
```

`check_permission()` raises:

- `HTTPUnauthorized` if the user is not authenticated (anonymous)
- `HTTPForbidden` if the user is authenticated but lacks the permission

### Checking Authentication Without Permissions

Use `check_authorized()` when you only need to ensure the user is logged in, without checking specific permissions:

```python
from aiohttp_security import check_authorized

async def handler_account(request):
    userid = await check_authorized(request)
    return web.Response(text=f"Welcome, {userid}!")
```

### Checking Anonymous Status

Use `is_anonymous()` to conditionally render content based on login state:

```python
async def handler_root(request):
    is_logged = not await is_anonymous(request)
    return web.Response(
        text=f"You are {'logged in' if is_logged else 'anonymous'}",
        content_type='text/html'
    )
```

### Getting the Current User ID

Use `authorized_userid()` to retrieve the current user's ID without raising exceptions:

```python
from aiohttp_security import authorized_userid

async def handler_profile(request):
    userid = await authorized_userid(request)
    if userid is None:
        return web.Response(text="Not logged in", status=401)
    return web.Response(text=f"User ID: {userid}")
```

### Direct Permission Checking

Use `permits()` to check permissions programmatically without raising exceptions:

```python
from aiohttp_security import permits

async def handler_dashboard(request):
    can_edit = await permits(request, 'edit')
    can_delete = await permits(request, 'delete')
    return web.json_response({
        "can_edit": can_edit,
        "can_delete": can_delete,
    })
```

## API Reference

### Public API Functions

**`setup(app, identity_policy, autz_policy)`**

Register security policies on an `aiohttp.web.Application`. Must be called before any request handling.

- `app` — the `web.Application` instance
- `identity_policy` — an `AbstractIdentityPolicy` instance (e.g., `SessionIdentityPolicy()`)
- `autz_policy` — an `AbstractAuthorizationPolicy` instance (developer-implemented)

**`remember(request, response, identity, **kwargs)`**

Store the user's identity in the response (sets cookie, session entry, etc.). Call this after successful authentication.

- `request` — the current `web.Request`
- `response` — a `web.StreamResponse` to modify
- `identity` — a string identifying the user (use UUID or hash, not plain usernames)
- `**kwargs` — forwarded to the identity policy (e.g., `max_age` for cookies)

**`forget(request, response)`**

Remove the user's identity from the response (clears cookie/session). Call this on logout.

**`authorized_userid(request)` → `Optional[str]`**

Return the current user's ID or `None` if anonymous. Does not raise exceptions.

**`permits(request, permission, context=None)` → `bool`**

Check if the current user has a given permission. Returns `True` or `False`. Permissions can be strings or enums.

**`is_anonymous(request)` → `bool`**

Return `True` if the current request has no authenticated identity.

**`check_authorized(request)` → `str`**

Raise `HTTPUnauthorized` if the user is anonymous; otherwise return the user's ID. Use at the top of handlers that require any logged-in user.

**`check_permission(request, permission, context=None)`**

Raise `HTTPUnauthorized` if anonymous, `HTTPForbidden` if the user lacks the permission. Use to protect routes declaratively.

### Abstract Policies

**`AbstractIdentityPolicy`** — base class for identity policies. Three methods to implement:

- `identify(request)` → `Optional[str]` — extract identity from the request (cookie, session, header)
- `remember(request, response, identity, **kwargs)` — persist identity into the response
- `forget(request, response)` — remove identity from subsequent requests

**`AbstractAuthorizationPolicy`** — base class for authorization policies. Two methods to implement:

- `authorized_userid(identity)` → `Optional[str]` — return the user ID for a given identity, or `None`
- `permits(identity, permission, context=None)` → `bool` — check if an identity has a permission

### Built-in Identity Policies

**`SessionIdentityPolicy(session_key='AIOHTTP_SECURITY')`**

Stores identity in `aiohttp-session`. Requires `aiohttp_session` package. Most commonly used for production applications.

**`CookiesIdentityPolicy()`**

Stores identity directly in an HTTP cookie named `AIOHTTP_SECURITY`. Default max_age is 30 days. Intended for demonstration purposes only — not secure for production use.

- Constructor accepts no arguments
- `remember()` accepts optional `max_age` parameter to override the default 30-day expiry

**`JWTIdentityPolicy(secret, algorithm='HS256', key='login')`**

Reads identity from the `Authorization: Bearer <token>` header. Requires `PyJWT`. Stateless — `remember()` and `forget()` are no-ops since JWT is bearer-token based.

- `secret` — signing secret for JWT verification
- `algorithm` — JWT algorithm (default: `"HS256"`)
- `key` — the claim key within the decoded JWT to extract as identity (default: `"login"`)

Raises `InvalidAuthorizationScheme` if the `Authorization` header does not use the `Bearer` scheme.

## Advanced Usage

### Database-Backed Authorization Policy

For real applications, authorization policies typically query a database. Here is a pattern using SQLAlchemy async:

```python
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(256), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String(256))
    is_superuser: Mapped[bool] = mapped_column(default=False)
    permissions = relationship("Permission", cascade="all, delete")


class Permission(Base):
    __tablename__ = "permissions"
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(sa.String(64), primary_key=True)


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session: async_sessionmaker[AsyncSession]):
        self.dbsession = db_session

    async def authorized_userid(self, identity: str) -> str | None:
        async with self.dbsession() as sess:
            user_id = await sess.scalar(
                sa.select(User.id).where(User.username == identity)
            )
        return str(user_id) if user_id else None

    async def permits(self, identity: str | None, permission: str,
                      context: dict | None = None) -> bool:
        if identity is None:
            return False
        async with self.dbsession() as sess:
            user = await sess.scalar(
                sa.select(User)
                .options(selectinload(User.permissions))
                .where(User.username == identity)
            )
        if user is None:
            return False
        if user.is_superuser:
            return True
        return any(p.name == permission for p in user.permissions)
```

### Enum-Based Permissions

Permissions can be enums instead of plain strings, which provides type safety:

```python
from enum import Enum

class Permissions(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        # permission is a Permissions enum member
        allowed_permissions = await db.get_user_permissions(identity)
        return permission in allowed_permissions

# Usage:
await check_permission(request, Permissions.ADMIN)
```

### Complete Application Setup with Database

```python
async def init_app() -> web.Application:
    app = web.Application()

    # Database setup
    db_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app["db_session"] = async_sessionmaker(db_engine, expire_on_commit=False)

    # Initialize database with tables and seed data
    await init_db(db_engine, app["db_session"])

    # Session middleware
    setup_session(app, SimpleCookieStorage())

    # Security policies
    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(app["db_session"])
    )

    # Register routes
    handlers = WebHandlers()
    handlers.configure(app)

    return app
```

### Password Verification Pattern

Use a library like `passlib` or `bcrypt` for credential verification:

```python
from passlib.hash import sha256_crypt

async def check_credentials(db_session, username: str, password: str) -> bool:
    async with db_session() as sess:
        hashed_pw = await sess.scalar(
            sa.select(User.password).where(User.username == username)
        )
    if hashed_pw is None:
        return False
    return sha256_crypt.verify(password, hashed_pw)
```

### Identity Best Practices

- Use random strings (UUIDs, hashes) as identity values — never expose database IDs or emails in cookies/sessions
- The identity string travels between browser and server; treat it as an opaque token
- Map identities to userids server-side through the authorization policy's `authorized_userid()` method
