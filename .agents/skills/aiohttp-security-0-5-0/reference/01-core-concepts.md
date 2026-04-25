# Core Concepts

This document explains the fundamental concepts of aiohttp-security: authentication, authorization, identity management, and the security workflow.

## Authentication vs Authorization

### Authentication

**Authentication** is the process of verifying who a user is. It confirms the user's identity through credentials (username/password, tokens, etc.).

In aiohttp-security:
- You implement your own authentication mechanism
- Authentication results in an **identity string**
- The identity is stored via an Identity Policy (session, cookie, JWT)

```python
# Example: Custom authentication
async def check_credentials(username: str, password: str) -> bool:
    """Your custom authentication logic"""
    user = await db.get_user(username)
    if user and verify_password(password, user.hashed_password):
        return True
    return False
```

### Authorization

**Authorization** is the process of determining what an authenticated user can do. It checks permissions for specific actions or resources.

In aiohttp-security:
- Implemented via `AbstractAuthorizationPolicy`
- Defines which identities have which permissions
- Checked using `check_permission()` or `permits()`

```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        """Check if identity has the permission"""
        user_permissions = {
            "alice": ["read", "write", "delete"],
            "bob": ["read"]
        }
        return identity in user_permissions and permission in user_permissions[identity]
```

## Identity Management

### What is an Identity?

An **identity** is a string that uniquely identifies a user across requests. It's shared between the browser and server.

**Best practices for identities:**
- Use random UUIDs or hashes, not database primary keys
- Don't use usernames or emails directly (privacy concern)
- Should be opaque to clients

```python
# Good: Random identity
import uuid
identity = str(uuid.uuid4())  # "550e8400-e29b-41d4-a716-446655440000"

# Bad: Database ID (exposes internal structure)
identity = str(user.id)  # "123"

# Bad: Username (privacy leak)
identity = user.username  # "alice@example.com"
```

### Identity Lifecycle

1. **Authentication**: User provides credentials → you verify them
2. **Remember**: Store identity in session/cookie via `remember()`
3. **Identify**: On subsequent requests, extract identity via policy's `identify()`
4. **Authorize**: Check permissions using `permits()` or `check_permission()`
5. **Forget**: Clear identity on logout via `forget()`

```python
# 1. Authenticate and remember
async def login_handler(request):
    if await check_credentials(username, password):
        identity = str(uuid.uuid4())
        response = web.HTTPFound('/dashboard')
        await remember(request, response, identity)
        raise response

# 2. Identify on subsequent requests (automatic via policy)
async def protected_handler(request):
    user_id = await authorized_userid(request)  # Extracts identity, maps to user
    # ...

# 3. Forget on logout
async def logout_handler(request):
    response = web.HTTPFound('/')
    await forget(request, response)
    raise response
```

## Security Workflow

### Complete Flow Diagram

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   User     │────▶│  Authenticate│────▶│  Identity      │
│  Browser   │     │  (your code) │     │  Policy        │
└─────────────┘     └──────────────┘     │  remember()    │
         ▲                              └────────────────┘
         │                                       │
         │                              ┌────────▼────────┐
         │     ┌────────────────┐      │  Session/Cookie │
         └────│  Identify on   │◀─────│  or JWT Token   │
              │  each request  │      └────────────────┘
              └────────────────┘
                     │
                     ▼
              ┌────────────────┐
              │ Authorization  │
              │ Policy         │
              │ permits()      │
              └────────────────┘
```

### Step-by-Step Workflow

1. **User visits app**: Anonymous, no identity stored
2. **User submits credentials**: POST to `/login` with username/password
3. **You authenticate**: Verify credentials against database/API
4. **Create identity**: Generate UUID or use existing user identifier
5. **Remember identity**: Call `remember(request, response, identity)`
6. **Store in session/cookie**: Identity Policy handles storage
7. **Redirect to dashboard**: User now "logged in"
8. **Subsequent requests**: Browser sends cookie/session token
9. **Identify automatically**: Policy extracts identity from request
10. **Check permissions**: Call `check_permission(request, 'read')`
11. **Authorize or deny**: HTTP 200 OK or HTTP 403 Forbidden

## Permission System

### Permission Types

Permissions can be:
- **Strings**: Simple permission names like `'read'`, `'write'`, `'admin'`
- **Enums**: Type-safe permissions using Python enums

```python
# String permissions (simple)
await check_permission(request, 'admin')

# Enum permissions (type-safe)
class Permission(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'

await check_permission(request, Permission.WRITE)
```

### Context Parameter

The `context` parameter allows passing additional data to permission checks:

```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        # Example: Resource-based permissions
        if context and 'resource_id' in context:
            resource = await get_resource(context['resource_id'])
            return resource.owner_id == identity or has_admin_permission(identity)
        return False

# Usage
await check_permission(request, 'edit', context={'resource_id': 123})
```

### Anonymous User Handling

Anonymous users (not logged in) have `identity=None`:

```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        # identity is None for anonymous users
        if identity is None:
            return False  # or True for public permissions
        
        # Check permissions for authenticated users
        return permission in get_user_permissions(identity)
```

## Key Design Decisions

### Why Separate Identity from User ID?

- **Security**: Identities can be rotated without changing user records
- **Privacy**: Opague identities don't expose internal IDs
- **Flexibility**: Same identity policy works with different auth backends

### Why Custom Authorization Policy?

- **Flexibility**: Different apps have different permission models
- **Backend agnostic**: Works with databases, APIs, config files
- **Context-aware**: Can check permissions based on resource ownership

### Why Multiple Identity Policies?

- **Sessions**: Best for traditional web apps with server-side state
- **Cookies**: Simple, stateless (but less secure)
- **JWT**: Stateless, good for APIs and microservices

## Common Patterns

### Public vs Protected Routes

```python
# Public route (no auth required)
async def public_handler(request):
    return web.Response(text="Everyone can see this")

# Protected route (requires login)
async def protected_handler(request):
    await check_authorized(request)  # Raises HTTPUnauthorized if anonymous
    return web.Response(text="Only logged-in users")

# Permission-protected route
async def admin_handler(request):
    await check_permission(request, 'admin')  # Raises HTTPForbidden if no permission
    return web.Response(text="Admin only")
```

### Role-Based Access Control (RBAC)

```python
class RBACPolicy(AbstractAuthorizationPolicy):
    def __init__(self):
        # Define roles and their permissions
        self.role_permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'editor': ['read', 'write'],
            'viewer': ['read']
        }
        # Map users to roles
        self.user_roles = {
            'alice_identity': 'admin',
            'bob_identity': 'editor'
        }
    
    async def authorized_userid(self, identity):
        return identity if identity in self.user_roles else None
    
    async def permits(self, identity, permission, context=None):
        role = self.user_roles.get(identity)
        if not role:
            return False
        return permission in self.role_permissions.get(role, [])
```

### Resource-Based Access Control

```python
class ResourcePolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        # Check if user owns the resource
        if context and 'resource' in context:
            resource = context['resource']
            if resource.owner_id == await self.get_user_id(identity):
                return True
        
        # Fall back to global permissions
        return await self.has_global_permission(identity, permission)
```
