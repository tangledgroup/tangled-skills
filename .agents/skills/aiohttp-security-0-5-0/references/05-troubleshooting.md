# Troubleshooting Guide

Common issues and solutions when working with aiohttp-security.

## Setup Issues

### "Security subsystem is not initialized"

**Error:**
```
HTTP 500 Internal Server Error
Security subsystem is not initialized, call aiohttp_security.setup(...) first
```

**Cause:** `setup()` was not called before making security API calls.

**Solution:**
```python
# Ensure setup is called during app initialization
async def make_app():
    app = web.Application()
    
    # Setup MUST be called before adding routes that use security
    identity_policy = SessionIdentityPolicy()
    authz_policy = MyAuthorizationPolicy()
    setup(app, identity_policy, authz_policy)
    
    # Now add routes
    app.router.add_get('/protected', protected_handler)
    
    return app
```

---

### "SessionIdentityPolicy requires aiohttp_session"

**Error:**
```
ImportError: SessionIdentityPolicy requires `aiohttp_session`
```

**Cause:** `aiohttp-session` package is not installed.

**Solution:**
```bash
pip install aiohttp-security[session]
# or
pip install aiohttp-session
```

---

### "Please install PyJWT"

**Error:**
```
RuntimeError: Please install `PyJWT`
```

**Cause:** `PyJWT` package is not installed when using `JWTIdentityPolicy`.

**Solution:**
```bash
pip install PyJWT
```

---

## Authentication Issues

### Identity Returns None After Login

**Symptom:** User logs in successfully but `authorized_userid()` returns `None` on next request.

**Common Causes:**

1. **Session not configured properly:**
```python
# Wrong: Session middleware not set up
app = web.Application()
setup(app, SessionIdentityPolicy(), authz_policy)

# Correct: Setup session first
from aiohttp_session import setup as setup_session, EncryptedCookieStorage
app = web.Application()
setup_session(app, EncryptedCookieStorage(secret_key))
setup(app, SessionIdentityPolicy(), authz_policy)
```

2. **Using SimpleCookieStorage in production:**
```python
# Wrong: SimpleCookieStorage is insecure and may not work properly
storage = SimpleCookieStorage()

# Correct: Use encrypted storage
from cryptography.fernet import Fernet
fernet_key = Fernet.generate_key()  # Save this key!
secret_key = base64.urlsafe_b64decode(fernet_key)
storage = EncryptedCookieStorage(secret_key)
```

3. **Identity not stored correctly:**
```python
# Make sure you're actually calling remember()
async def login_handler(request):
    if await check_credentials(username, password):
        response = web.HTTPFound('/dashboard')
        await remember(request, response, identity)  # This line is crucial!
        raise response
```

---

### Cookie Not Persisting Across Requests

**Symptom:** User logs in but gets logged out on page refresh.

**Checklist:**

1. **Verify cookie is set:**
```python
async def debug_handler(request):
    cookies = dict(request.cookies)
    return web.json_response({"cookies": cookies})
```

2. **Check cookie attributes:**
   - Domain matches your site
   - Path is correct (usually `/`)
   - Secure flag set if using HTTPS
   - Not blocked by browser privacy settings

3. **Ensure middleware order:**
```python
# Session middleware should be added to app
from aiohttp_session import session_middleware, EncryptedCookieStorage

storage = EncryptedCookieStorage(secret_key)
app = web.Application(middlewares=[session_middleware(storage)])
```

---

## Authorization Issues

### Anonymous User Gets HTTPUnauthorized

**Symptom:** `check_permission()` raises `HTTPUnauthorized` even for valid users.

**Cause:** User is not authenticated (no identity stored).

**Solution:**
```python
async def protected_handler(request):
    # Check if user is anonymous first
    if await is_anonymous(request):
        return web.Response(text="Please log in", status=401)
    
    # Then check permission
    if await permits(request, 'read'):
        return web.Response(text="You can read")
    
    return web.Response(text="No permission", status=403)
```

---

### Permission Always Returns False

**Symptom:** `permits()` always returns `False` even for authenticated users.

**Debug Steps:**

1. **Check identity is being identified:**
```python
async def debug_handler(request):
    policy = request.app[IDENTITY_KEY]
    identity = await policy.identify(request)
    return web.json_response({"identity": identity})
```

2. **Verify authorization policy logic:**
```python
class DebugAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        print(f"permits called: identity={identity}, permission={permission}")
        # Your logic here
        return True  # Temporarily return True to test
    
    async def authorized_userid(self, identity):
        print(f"authorized_userid called: identity={identity}")
        return identity
```

3. **Check for None identity:**
```python
class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        # Handle None explicitly
        if identity is None:
            print("Anonymous user - no permissions")
            return False
        
        # Your permission logic
        return permission in self.user_permissions.get(identity, [])
```

---

### HTTPForbidden vs HTTPUnauthorized

**Understanding the difference:**

| Status | Meaning | When Raised |
|--------|---------|-------------|
| 401 Unauthorized | User not authenticated | `check_authorized()` when anonymous |
| 403 Forbidden | User authenticated but no permission | `check_permission()` when lacks permission |

**Example:**
```python
async def handler(request):
    try:
        await check_permission(request, 'admin')
        return web.Response(text="Admin panel")
    except web.HTTPUnauthorized:
        # User not logged in
        return web.Response(text="Please log in", status=401)
    except web.HTTPForbidden:
        # User logged in but not admin
        return web.Response(text="Access denied", status=403)
```

---

## JWT Issues

### "Invalid authorization scheme"

**Error:**
```
InvalidAuthorizationScheme: Invalid authorization scheme. Should be `Bearer <token>`
```

**Cause:** Authorization header format is incorrect.

**Solution:**
```python
# Client must send:
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Not just the token:
headers = {"Authorization": "eyJhbGciOiJIUzI1NiIs..."}  # Wrong!
```

---

### JWT Token Expires Too Quickly

**Symptom:** User gets logged out after short time.

**Solution:** Increase token expiration when creating JWT:

```python
from datetime import datetime, timedelta


async def login_handler(request):
    if await check_credentials(username, password):
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(days=7),  # 7 days
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return web.json_response({"token": token})
```

---

### JWT Token Signature Invalid

**Error:**
```
jwt.exceptions.InvalidSignatureError
```

**Cause:** Secret key mismatch between token creation and validation.

**Solution:**
```python
# Use the SAME secret for both encoding and decoding
SECRET_KEY = "your-super-secret-key"  # Store in env var, not code!

# When creating token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# When validating (in JWTIdentityPolicy)
policy = JWTIdentityPolicy(secret=SECRET_KEY, algorithm="HS256")
```

---

## Database Issues

### Permission Check Fails with SQLAlchemy

**Symptom:** Async session errors or permission checks fail.

**Common Issues:**

1. **Session not properly closed:**
```python
# Use async context manager
async with self.db_session() as sess:
    result = await sess.scalar(stmt)
# Session automatically closed
```

2. **Missing relationships:**
```python
# Load related permissions
stmt = sa.select(User).options(
    selectinload(User.permissions)
).where(User.username == identity)

async with self.db_session() as sess:
    user = await sess.scalar(stmt)
    
# Now user.permissions is loaded
```

3. **Transaction not committed:**
```python
# Use begin() context for writes
async with self.db_session.begin() as sess:
    sess.add(new_user)
# Automatically commits
```

---

## Performance Issues

### Slow Permission Checks

**Symptom:** Each request takes too long due to database queries.

**Solutions:**

1. **Cache user permissions:**
```python
from functools import lru_cache


class CachedAuthPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session):
        self.db_session = db_session
        self._permission_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def permits(self, identity, permission, context=None):
        cache_key = (identity, permission)
        
        if cache_key in self._permission_cache:
            cached_time, result = self._permission_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return result
        
        # Query database
        result = await self._check_permission_db(identity, permission)
        
        # Cache result
        self._permission_cache[cache_key] = (time.time(), result)
        
        return result
```

2. **Use connection pooling:**
```python
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,
    max_overflow=20
)
```

---

### Memory Leak with Sessions

**Symptom:** Memory usage grows over time.

**Cause:** Sessions not expiring or being cleaned up.

**Solution:**
```python
# Set session expiration
from aiohttp_session import setup as setup_session, EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key,
    cookie_name='SESSION',
    ttl=86400  # Session expires after 24 hours
)
setup_session(app, storage)

# Or use Redis with TTL
from aiohttp_session.redis_storage import RedisStorage

storage = RedisStorage('redis://localhost:6379', ttl=86400)
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('aiohttp_security')
logger.setLevel(logging.DEBUG)
```

### Add Debug Handler

```python
async def debug_auth_handler(request):
    """Debug endpoint to check authentication state"""
    info = {
        "anonymous": await is_anonymous(request),
        "user_id": await authorized_userid(request),
        "has_read": await permits(request, 'read'),
        "has_write": await permits(request, 'write'),
        "has_admin": await permits(request, 'admin'),
    }
    
    # Check session contents
    try:
        from aiohttp_session import get_session
        session = await get_session(request)
        info["session"] = dict(session)
    except:
        pass
    
    return web.json_response(info)


# Add to app
app.router.add_get('/debug-auth', debug_auth_handler)
```

### Test Permissions Directly

```python
async def test_permissions():
    """Test authorization policy directly"""
    policy = MyAuthorizationPolicy()
    
    # Test authorized_userid
    user_id = await policy.authorized_userid("test_identity")
    print(f"User ID: {user_id}")
    
    # Test permits
    for permission in ['read', 'write', 'admin']:
        result = await policy.permits("test_identity", permission)
        print(f"Permission '{permission}': {result}")
```

## Best Practices Checklist

- [ ] Use encrypted session storage in production
- [ ] Store secrets in environment variables, not code
- [ ] Validate all user input before authentication
- [ ] Use HTTPS for all authenticated endpoints
- [ ] Implement rate limiting on login endpoints
- [ ] Set reasonable session/token expiration times
- [ ] Log authentication failures (for security monitoring)
- [ ] Use opaque identities (UUIDs), not database IDs
- [ ] Handle None identity gracefully in authorization policy
- [ ] Test with both authenticated and anonymous users
