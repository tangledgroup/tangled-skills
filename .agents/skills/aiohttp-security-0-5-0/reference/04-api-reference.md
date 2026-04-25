# API Reference

Complete reference for all aiohttp-security functions, classes, and methods.

## Setup Functions

### `setup(app, identity_policy, autz_policy)`

Setup aiohttp application with security policies.

**Parameters:**
- `app` (`aiohttp.web.Application`): The aiohttp application instance
- `identity_policy` (`AbstractIdentityPolicy`): Identity policy instance (e.g., `SessionIdentityPolicy()`)
- `autz_policy` (`AbstractAuthorizationPolicy`): Authorization policy instance

**Example:**
```python
from aiohttp import web
from aiohttp_security import setup, SessionIdentityPolicy


async def make_app():
    app = web.Application()
    
    identity_policy = SessionIdentityPolicy()
    authz_policy = MyAuthorizationPolicy()
    
    setup(app, identity_policy, authz_policy)
    
    return app
```

**Raises:**
- `ValueError`: If policies are not subclasses of required abstract classes

---

## Authentication Functions

### `async remember(request, response, identity, **kwargs)`

Remember an identity in the response (e.g., store in cookie or session).

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `response` (`aiohttp.web.StreamResponse`): Response to modify (e.g., redirect)
- `identity` (`str`): The identity string to remember
- `**kwargs`: Policy-specific arguments (e.g., `max_age` for cookies)

**Example:**
```python
async def login_handler(request):
    if await check_credentials(username, password):
        response = web.HTTPFound('/dashboard')
        await remember(request, response, user_identity)
        raise response
```

**Raises:**
- `ValueError`: If identity is not a string
- `HTTPInternalServerError`: If security subsystem not initialized

---

### `async forget(request, response)`

Forget a previously remembered identity (logout).

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `response` (`aiohttp.web.StreamResponse`): Response to modify

**Example:**
```python
async def logout_handler(request):
    response = web.HTTPFound('/')
    await forget(request, response)
    raise response
```

---

## Authorization Functions

### `async authorized_userid(request)`

Retrieve the authorized user ID from the request.

**Returns:**
- `str | None`: The user ID if authenticated, `None` if anonymous or invalid identity

**Example:**
```python
async def dashboard_handler(request):
    user_id = await authorized_userid(request)
    
    if user_id:
        user = await db.get_user(user_id)
        return web.Response(text=f"Welcome, {user.name}!")
    
    return web.Response(text="Please log in", status=401)
```

---

### `async permits(request, permission, context=None)`

Check if the user has a specific permission.

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `permission` (`str` or `Enum`): The permission to check
- `context` (`any`, optional): Additional context for permission check

**Returns:**
- `bool`: `True` if user has permission, `False` otherwise

**Example:**
```python
async def edit_handler(request):
    if await permits(request, 'edit'):
        return web.Response(text="You can edit")
    
    return web.Response(text="No edit permission", status=403)


# With enum permissions
from enum import Enum

class Permission(Enum):
    READ = 'read'
    WRITE = 'write'

if await permits(request, Permission.WRITE):
    # User has write permission
    pass


# With context
if await permits(request, 'delete', context={'resource_id': 123}):
    # User can delete resource 123
    pass
```

**Raises:**
- `ValueError`: If permission is not a string or Enum

---

### `async is_anonymous(request)`

Check if the user is anonymous (not authenticated).

**Returns:**
- `bool`: `True` if user is anonymous, `False` if authenticated

**Example:**
```python
async def index_handler(request):
    if await is_anonymous(request):
        return web.Response(text="Please log in to continue", status=401)
    
    return web.Response(text="Welcome back!")
```

---

## Permission Checkers (Raise Exceptions)

### `async check_authorized(request)`

Require that the user is authenticated. Raises exception for anonymous users.

**Returns:**
- `str`: The authorized user ID if successful

**Raises:**
- `aiohttp.web.HTTPUnauthorized`: If user is anonymous

**Example:**
```python
async def protected_handler(request):
    await check_authorized(request)  # Raises HTTPUnauthorized if anonymous
    
    # User is authenticated - proceed
    return web.Response(text="Protected content")
```

---

### `async check_permission(request, permission, context=None)`

Require that the user has a specific permission. Raises exceptions for unauthorized or forbidden access.

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `permission` (`str` or `Enum`): Required permission
- `context` (`any`, optional): Additional context

**Raises:**
- `aiohttp.web.HTTPUnauthorized`: If user is anonymous
- `aiohttp.web.HTTPForbidden`: If user is authenticated but lacks permission

**Example:**
```python
async def admin_handler(request):
    await check_permission(request, 'admin')
    # Only users with 'admin' permission reach here
    return web.Response(text="Admin panel")


async def edit_handler(request):
    try:
        await check_permission(request, 'edit')
        return web.Response(text="Editing allowed")
    except web.HTTPUnauthorized:
        return web.Response(text="Please log in", status=401)
    except web.HTTPForbidden:
        return web.Response(text="No edit permission", status=403)
```

**Note:** When permission is rejected, the HTTP 403 response includes a reason message: `"User does not have 'permission_name' permission"` (version 0.5.0+)

---

## Abstract Base Classes

### `AbstractIdentityPolicy`

Base class for identity policies. Implement these methods:

#### `async identify(request) -> str | None`

Extract the claimed identity from the request.

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object

**Returns:**
- `str | None`: The identity string or `None` if no identity found

**Example:**
```python
class MyIdentityPolicy(AbstractIdentityPolicy):
    async def identify(self, request):
        return request.cookies.get('MY_IDENTITY_COOKIE')
```

---

#### `async remember(request, response, identity, **kwargs)`

Store the identity in the response (cookie, session, header).

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `response` (`aiohttp.web.StreamResponse`): Response to modify
- `identity` (`str`): The identity to store
- `**kwargs`: Policy-specific arguments

**Example:**
```python
async def remember(self, request, response, identity, **kwargs):
    max_age = kwargs.get('max_age', 86400)
    response.set_cookie('MY_IDENTITY', identity, max_age=max_age)
```

---

#### `async forget(request, response)`

Remove the identity from the response.

**Parameters:**
- `request` (`aiohttp.web.Request`): The request object
- `response` (`aiohttp.web.StreamResponse`): Response to modify

**Example:**
```python
async def forget(self, request, response):
    response.del_cookie('MY_IDENTITY')
```

---

### `AbstractAuthorizationPolicy`

Base class for authorization policies. Implement these methods:

#### `async authorized_userid(identity) -> str | None`

Get the user ID for an identity.

**Parameters:**
- `identity` (`str`): The identity string

**Returns:**
- `str | None`: The user ID or `None` if identity is invalid

**Example:**
```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        user = await db.get_user_by_identity(identity)
        return str(user.id) if user else None
```

---

#### `async permits(identity, permission, context=None) -> bool`

Check if an identity has a permission.

**Parameters:**
- `identity` (`str | None`): The identity (None for anonymous users)
- `permission` (`str` or `Enum`): The permission to check
- `context` (`any`, optional): Additional context

**Returns:**
- `bool`: `True` if permission granted, `False` otherwise

**Example:**
```python
async def permits(self, identity, permission, context=None):
    if identity is None:
        return False
    
    user = await self.get_user(identity)
    return permission in user.permissions
```

---

## Built-in Identity Policies

### `SessionIdentityPolicy(session_key='AIOHTTP_SECURITY')`

Store identity in aiohttp-session.

**Parameters:**
- `session_key` (`str`): Key in session dictionary (default: `'AIOHTTP_SECURITY'`)

**Requirements:**
- `aiohttp-session` must be installed and configured

**Example:**
```python
from aiohttp_session import setup as setup_session, EncryptedCookieStorage
from aiohttp_security import SessionIdentityPolicy


async def make_app():
    app = web.Application()
    
    # Setup session first
    setup_session(app, EncryptedCookieStorage(secret_key))
    
    # Then setup security
    policy = SessionIdentityPolicy(session_key='MY_APP_IDENTITY')
    setup(app, policy, MyAuthPolicy())
    
    return app
```

---

### `CookiesIdentityPolicy()`

Store identity directly in HTTP cookie.

**Configuration:**
- Cookie name: `'AIOHTTP_SECURITY'`
- Default max age: 30 days (30 * 24 * 3600 seconds)

**Example:**
```python
from aiohttp_security import CookiesIdentityPolicy


async def make_app():
    app = web.Application()
    
    policy = CookiesIdentityPolicy()
    setup(app, policy, MyAuthPolicy())
    
    return app


# Custom max age
async def login_handler(request):
    response = web.HTTPFound('/dashboard')
    await remember(request, response, identity, max_age=3600)  # 1 hour
    raise response
```

**Warning:** Not recommended for production - use `SessionIdentityPolicy` with encrypted cookies instead.

---

### `JWTIdentityPolicy(secret, algorithm='HS256', key='login')`

Extract identity from JWT token in Authorization header.

**Parameters:**
- `secret` (`str`): Secret key for verifying token signature
- `algorithm` (`str`): JWT algorithm (default: `'HS256'`)
- `key` (`str`): Key in JWT payload containing identity (default: `'login'`)

**Requirements:**
- `PyJWT` must be installed

**Example:**
```python
from aiohttp_security import JWTIdentityPolicy


async def make_app():
    app = web.Application()
    
    policy = JWTIdentityPolicy(
        secret="your-secret-key",
        algorithm="HS256",
        key="user_id"  # Expect {"user_id": "..."} in JWT payload
    )
    setup(app, policy, MyAuthPolicy())
    
    return app
```

**Client Usage:**
```python
# Client sends: Authorization: Bearer <jwt_token>
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."}
```

**Raises:**
- `InvalidAuthorizationScheme`: If Authorization header doesn't start with "Bearer "
- `RuntimeError`: If PyJWT is not installed

---

## Exceptions

### `InvalidAuthorizationScheme`

Raised by `JWTIdentityPolicy` when the Authorization header format is invalid.

**Inherits from:** `ValueError`, `jwt.exceptions.PyJWTError`

**Example:**
```python
from aiohttp_security.jwt_identity import InvalidAuthorizationHandler


async def protected_handler(request):
    try:
        user_id = await authorized_userid(request)
        return web.json_response({"user_id": user_id})
    except InvalidAuthorizationScheme:
        return web.json_response(
            {"error": "Invalid Authorization header format"},
            status=401
        )
```

---

## Type Hints

All functions and classes include full type annotations (version 0.5.0+):

```python
from aiohttp_security import (
    remember,
    forget,
    authorized_userid,
    permits,
    is_anonymous,
    check_authorized,
    check_permission,
)
from aiohttp_security.abc import (
    AbstractIdentityPolicy,
    AbstractAuthorizationPolicy,
)
from aiohttp_security.session_identity import SessionIdentityPolicy
from aiohttp_security.cookies_identity import CookiesIdentityPolicy
from aiohttp_security.jwt_identity import JWTIdentityPolicy
```

## Deprecated APIs

The following decorators are deprecated (since version 0.3.0):

- `login_required` - Use `check_authorized()` instead
- `has_permission` - Use `check_permission()` instead

**Migration:**
```python
# Before (deprecated)
@login_required
async def handler(request):
    pass


# After (recommended)
async def handler(request):
    await check_authorized(request)
    pass
```
