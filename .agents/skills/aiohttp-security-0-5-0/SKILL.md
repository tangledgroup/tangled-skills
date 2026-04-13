---
name: aiohttp-security-0-5-0
description: A skill for implementing authentication and authorization in aiohttp.web applications using aiohttp-security 0.5.0, providing identity policies (cookies, sessions, JWT) and custom authorization policies with permission-based access control.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - aiohttp
  - authentication
  - authorization
  - security
  - identity
  - permissions
  - sessions
  - jwt
  - cookies
category: web-security
required_environment_variables: []
---

# aiohttp-security-0.5.0

A comprehensive toolkit for implementing authentication and authorization in `aiohttp.web` applications using the `aiohttp-security` library (version 0.5.0). Provides identity policies for user sessions (cookies, aiohttp-session, JWT) and a flexible authorization policy system for permission-based access control.

## When to Use

- Building async web APIs with aiohttp that require user authentication
- Implementing session-based or token-based authentication
- Creating role-based or permission-based access control systems
- Protecting routes and resources based on user identity
- Integrating JWT tokens for stateless authentication
- Building applications with database-backed user authorization

## Setup

### Installation

```bash
# Basic installation (cookie support)
pip install aiohttp-security

# With session support (recommended for production)
pip install aiohttp-security[session]

# For JWT support
pip install aiohttp-security PyJWT
```

### Dependencies

- **Required**: `aiohttp>=3.9`
- **Optional**: `aiohttp-session` (for SessionIdentityPolicy)
- **Optional**: `PyJWT` (for JWTIdentityPolicy)

## Quick Start

### Basic Authentication with Sessions

See [Session-Based Auth](references/01-session-auth.md) for a complete working example.

```python
from aiohttp import web
from aiohttp_session import setup as setup_session, SimpleCookieStorage
from aiohttp_security import (SessionIdentityPolicy, remember, forget,
                              check_permission, setup)
from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        # Return user_id if identity is valid, None otherwise
        return identity if identity in ["alice", "bob"] else None

    async def permits(self, identity, permission, context=None):
        # Define permissions for each user
        permissions = {"alice": ["read", "write"], "bob": ["read"]}
        return identity in permissions and permission in permissions[identity]


async def make_app():
    app = web.Application()
    
    # Setup session middleware
    setup_session(app, SimpleCookieStorage())
    
    # Setup security policies
    policy = SessionIdentityPolicy()
    setup(app, policy, MyAuthPolicy())
    
    # Add routes
    app.router.add_get('/', handler_root)
    app.router.add_post('/login', handler_login)
    app.router.add_post('/logout', handler_logout)
    app.router.add_get('/protected', handler_protected)
    
    return app


async def handler_login(request):
    response = web.HTTPFound('/')
    await remember(request, response, 'alice')  # Store identity in session
    raise response


async def handler_protected(request):
    await check_permission(request, 'write')  # Raises HTTPForbidden if no permission
    return web.Response(text="You have write access!")


if __name__ == '__main__':
    web.run_app(make_app(), port=9000)
```

## Core Concepts

### Identity vs Authorization

- **Identity**: A string that identifies the user (stored in cookies/sessions/JWT). Should be a random UUID, not database IDs or usernames.
- **Authorization**: The process of checking what permissions an identity has access to.

See [Core Concepts](references/01-core-concepts.md) for detailed explanation.

### Identity Policies

Three built-in identity policies:

| Policy | Storage | Use Case |
|--------|---------|----------|
| `SessionIdentityPolicy` | aiohttp-session | Production applications (recommended) |
| `CookiesIdentityPolicy` | HTTP cookies | Simple demos, stateless scenarios |
| `JWTIdentityPolicy` | Bearer token | Stateless APIs, microservices |

See [Identity Policies](references/02-identity-policies.md) for implementation details.

### Authorization Policy

Create custom authorization by implementing `AbstractAuthorizationPolicy`:

```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity: str) -> str | None:
        """Return user_id if identity is valid, None otherwise"""
        pass
    
    async def permits(self, identity: str | None, permission: str, 
                     context: dict | None = None) -> bool:
        """Return True if identity has the permission"""
        pass
```

See [Authorization Policies](references/03-authorization-policies.md) for examples.

## Common Operations

### Login/Remember User

```python
async def handler_login(request):
    # Authenticate user (e.g., check credentials)
    if await check_credentials(username, password):
        response = web.HTTPFound('/dashboard')
        await remember(request, response, user_identity)
        raise response
    return web.Response(text="Invalid credentials", status=401)
```

### Logout/Forget User

```python
async def handler_logout(request):
    response = web.HTTPFound('/')
    await forget(request, response)  # Clears session/cookie
    raise response
```

### Check Permissions

```python
# Raises HTTPUnauthorized if not logged in
# Raises HTTPForbidden if no permission
await check_permission(request, 'admin')

# Or check without raising exceptions
if await permits(request, 'read'):
    return web.Response(text="You can read")
```

See [API Reference](references/04-api-reference.md) for all functions.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Authentication vs authorization, identity management
- [`references/02-identity-policies.md`](references/02-identity-policies.md) - Session, Cookie, and JWT identity policies
- [`references/03-authorization-policies.md`](references/03-authorization-policies.md) - Custom authorization with database and dictionary backends
- [`references/04-api-reference.md`](references/04-api-reference.md) - Complete API documentation with examples

## Troubleshooting

### Common Issues

**"Security subsystem is not initialized"**
- Ensure `setup(app, identity_policy, authz_policy)` is called before adding routes

**SessionIdentityPolicy ImportError**
- Install aiohttp-session: `pip install aiohttp-session`

**JWTIdentityPolicy RuntimeError**
- Install PyJWT: `pip install PyJWT`

**Anonymous user gets HTTPUnauthorized**
- This is expected behavior - anonymous users have no identity
- Use `is_anonymous(request)` to check before requiring auth

See [Troubleshooting Guide](references/05-troubleshooting.md) for more issues.

## Best Practices

1. **Use random identities**: Store UUIDs or hashes in sessions, not database IDs
2. **Encrypt session cookies**: Use `EncryptedCookieStorage` in production
3. **Validate permissions server-side**: Never trust client-side permission checks
4. **Handle None gracefully**: `permits()` returns False for anonymous users by default
5. **Use context parameter**: Pass additional data to `permits()` for fine-grained control

## Version Compatibility

- **aiohttp**: >= 3.9
- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Type annotations**: Full type hints included (version 0.5.0+)
