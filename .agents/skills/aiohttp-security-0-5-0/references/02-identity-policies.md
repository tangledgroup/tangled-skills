# Identity Policies

Identity policies manage how user identities are stored and retrieved across requests. aiohttp-security provides three built-in identity policies, each suited for different use cases.

## SessionIdentityPolicy (Recommended)

Uses `aiohttp-session` to store identities server-side or in encrypted cookies. This is the most secure and flexible option for production applications.

### Installation

```bash
pip install aiohttp-security[session]
```

### Setup

```python
from aiohttp import web
from aiohttp_session import setup as setup_session, EncryptedCookieStorage
from aiohttp_security import SessionIdentityPolicy, setup
from cryptography.fernet import Fernet


async def make_app():
    app = web.Application()
    
    # Generate a secret key (do this once and store securely)
    fernet_key = Fernet.generate_key()  # Save this!
    secret_key = base64.urlsafe_b64decode(fernet_key)
    
    # Setup encrypted session storage
    storage = EncryptedCookieStorage(secret_key, cookie_name='SESSION')
    setup_session(app, storage)
    
    # Setup security with session identity policy
    identity_policy = SessionIdentityPolicy(session_key='AIOHTTP_SECURITY')
    setup(app, identity_policy, MyAuthorizationPolicy())
    
    return app
```

### Configuration Options

```python
# Default session key
policy = SessionIdentityPolicy()  # Uses 'AIOHTTP_SECURITY'

# Custom session key
policy = SessionIdentityPolicy(session_key='MY_APP_IDENTITY')
```

### Usage Example

```python
from aiohttp_session import get_session
from aiohttp_security import remember, forget, authorized_userid


async def login_handler(request):
    """Authenticate user and store identity in session"""
    post_data = await request.post()
    username, password = post_data.get('username'), post_data.get('password')
    
    if await check_credentials(username, password):
        # Generate secure identity (UUID recommended)
        import uuid
        identity = str(uuid.uuid4())
        
        # Optionally store mapping in your database
        await db.store_session(identity, username)
        
        # Remember identity in session
        response = web.HTTPFound('/dashboard')
        await remember(request, response, identity)
        raise response
    
    return web.Response(text="Invalid credentials", status=401)


async def dashboard_handler(request):
    """Access protected resource"""
    user_id = await authorized_userid(request)
    
    if user_id:
        # Get user info from database
        user = await db.get_user_by_id(user_id)
        return web.Response(text=f"Welcome, {user.name}!")
    
    return web.Response(text="Please log in", status=401)


async def logout_handler(request):
    """Clear identity from session"""
    response = web.HTTPFound('/')
    await forget(request, response)
    raise response
```

### Session Storage Options

aiohttp-session supports multiple storage backends:

```python
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_session.memcached_storage import MemcachedStorage


# Encrypted cookies (recommended for most apps)
storage = EncryptedCookieStorage(secret_key, cookie_name='SESSION')
setup_session(app, storage)

# Redis (for distributed sessions)
storage = RedisStorage('redis://localhost:6379')
setup_session(app, storage)

# Memcached
storage = MemcachedStorage('localhost:11211')
setup_session(app, storage)
```

**Warning**: Never use `SimpleCookieStorage` in production - it's insecure and only for testing.

## CookiesIdentityPolicy

Stores identity directly in HTTP cookies. Simple but less secure - suitable for demos or low-security applications.

### Setup

```python
from aiohttp import web
from aiohttp_security import CookiesIdentityPolicy, setup


async def make_app():
    app = web.Application()
    
    # No additional setup needed
    identity_policy = CookiesIdentityPolicy()
    setup(app, identity_policy, MyAuthorizationPolicy())
    
    return app
```

### Configuration Options

```python
# Default settings
policy = CookiesIdentityPolicy()
# Cookie name: 'AIOHTTP_SECURITY'
# Max age: 30 days (30 * 24 * 3600 seconds)


# Custom max age
policy = CookiesIdentityPolicy()
# Then set in remember() call:
await remember(request, response, identity, max_age=3600)  # 1 hour
```

### Usage Example

```python
from aiohttp_security import remember, forget


async def login_handler(request):
    """Store identity directly in cookie"""
    if await check_credentials(username, password):
        identity = username  # Not recommended for production!
        
        response = web.HTTPFound('/dashboard')
        await remember(request, response, identity, max_age=86400)  # 24 hours
        raise response
    
    return web.Response(text="Invalid", status=401)


async def protected_handler(request):
    """Cookie is automatically read on each request"""
    user_id = await authorized_userid(request)
    # ...
```

### Security Considerations

**Pros:**
- Simple setup, no additional dependencies
- Stateless - works across multiple servers

**Cons:**
- Identity visible in cookie (should be opaque UUID anyway)
- No encryption by default
- Limited to ~4KB per cookie
- Client can delete cookies

**Recommendation**: Only use for development or when combined with HTTPS and opaque identities.

## JWTIdentityPolicy

Uses JSON Web Tokens (JWT) for stateless authentication. Ideal for APIs, mobile apps, and microservices.

### Installation

```bash
pip install aiohttp-security PyJWT
```

### Setup

```python
from aiohttp import web
from aiohttp_security import JWTIdentityPolicy, setup


async def make_app():
    app = web.Application()
    
    # Secret key for signing tokens (keep secure!)
    secret_key = "your-super-secret-key-change-in-production"
    
    identity_policy = JWTIdentityPolicy(
        secret=secret_key,
        algorithm="HS256",  # HMAC with SHA-256
        key="user_id"       # Key in JWT payload containing identity
    )
    
    setup(app, identity_policy, MyAuthorizationPolicy())
    
    return app
```

### Configuration Options

```python
# Basic setup
policy = JWTIdentityPolicy(secret="your-secret")


# Custom algorithm and key
policy = JWTIdentityPolicy(
    secret="your-secret",
    algorithm="HS256",  # or "RS256" for RSA
    key="sub"           # Use 'sub' (subject) claim instead of custom key
)
```

### Creating JWT Tokens

JWTIdentityPolicy doesn't create tokens - you need to create them during authentication:

```python
import jwt
from datetime import datetime, timedelta


async def login_handler(request):
    """Authenticate and return JWT token"""
    if await check_credentials(username, password):
        # Create JWT token
        payload = {
            "user_id": user.id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=24),  # Expires in 24h
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            secret_key,
            algorithm="HS256"
        )
        
        return web.json_response({"token": token})
    
    return web.json_response({"error": "Invalid credentials"}, status=401)
```

### Using JWT Tokens

Client includes token in Authorization header:

```python
# Client sends request with token
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}


async def protected_handler(request):
    """Token automatically validated and identity extracted"""
    # JWTIdentityPolicy.identify() handles:
    # 1. Extracting token from Authorization header
    # 2. Validating signature
    # 3. Checking expiration
    # 4. Returning identity from payload
    
    user_id = await authorized_userid(request)
    
    if user_id:
        return web.json_response({"data": "protected"})
    
    # JWTIdentityPolicy raises InvalidAuthorizationScheme for bad tokens
    # or returns None for missing/invalid tokens
    return web.json_response({"error": "Unauthorized"}, status=401)
```

### Error Handling

```python
from aiohttp_security.jwt_identity import InvalidAuthorizationScheme


async def protected_handler(request):
    try:
        user_id = await authorized_userid(request)
        if user_id:
            return web.json_response({"data": "protected"})
        
        return web.json_response({"error": "Invalid token"}, status=401)
    
    except InvalidAuthorizationScheme:
        # Token format is wrong (not "Bearer <token>")
        return web.json_response(
            {"error": "Missing or malformed Authorization header"},
            status=401
        )
```

### JWT Best Practices

1. **Use HTTPS**: Always transmit tokens over encrypted connections
2. **Short expiration**: Set reasonable token lifetimes (1-24 hours)
3. **Secure secret**: Store signing secrets securely, never in code
4. **Token refresh**: Implement refresh tokens for long-lived sessions
5. **Validate claims**: Check `exp`, `iss`, `aud` claims as needed

## Custom Identity Policy

Create custom identity policies by implementing `AbstractIdentityPolicy`:

```python
from aiohttp_security.abc import AbstractIdentityPolicy


class HeaderIdentityPolicy(AbstractIdentityPolicy):
    """Extract identity from custom header"""
    
    async def identify(self, request):
        return request.headers.get('X-User-Identity')
    
    async def remember(self, request, response, identity, **kwargs):
        # Set custom header (for internal services)
        response.headers['X-User-Identity'] = identity
    
    async def forget(self, request, response):
        # Remove header
        if 'X-User-Identity' in response.headers:
            del response.headers['X-User-Identity']


# Usage
setup(app, HeaderIdentityPolicy(), MyAuthorizationPolicy())
```

## Policy Comparison

| Feature | Session | Cookie | JWT |
|---------|---------|--------|-----|
| **Storage** | Server-side or encrypted cookie | Plain cookie | Client-side token |
| **Security** | High (encrypted) | Medium | High (signed) |
| **Stateless** | No (server storage) | Yes | Yes |
| **Scalability** | Good (with Redis) | Excellent | Excellent |
| **Token size** | Small (session ID) | Small (identity) | Large (full payload) |
| **Revocation** | Easy (delete session) | Hard | Requires blacklist |
| **Best for** | Web apps | Simple demos | APIs, mobile |

## Migration Guide

### From Cookies to Sessions

```python
# Before: CookiesIdentityPolicy
from aiohttp_security import CookiesIdentityPolicy
policy = CookiesIdentityPolicy()


# After: SessionIdentityPolicy
from aiohttp_session import setup as setup_session, EncryptedCookieStorage
from aiohttp_security import SessionIdentityPolicy

setup_session(app, EncryptedCookieStorage(secret_key))
policy = SessionIdentityPolicy()
```

### From Sessions to JWT

```python
# Before: SessionIdentityPolicy
from aiohttp_security import SessionIdentityPolicy, remember
policy = SessionIdentityPolicy()

async def login(request):
    response = web.HTTPFound('/dashboard')
    await remember(request, response, identity)
    raise response


# After: JWTIdentityPolicy
from aiohttp_security import JWTIdentityPolicy
import jwt

policy = JWTIdentityPolicy(secret="your-secret", key="user_id")

async def login(request):
    token = jwt.encode({"user_id": identity, "exp": ...}, secret, algorithm="HS256")
    return web.json_response({"token": token})
```
