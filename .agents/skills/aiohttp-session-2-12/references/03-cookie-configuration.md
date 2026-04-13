# Cookie Configuration Reference

This document covers all cookie-related configuration options available in aiohttp-session storage backends, including security flags, domain settings, and expiration controls.

## Cookie Parameters Overview

All storage backends support the same cookie configuration parameters through the `AbstractStorage` base class:

```python
class AbstractStorage:
    def __init__(
        self,
        *,
        cookie_name: str = "AIOHTTP_SESSION",  # Name of the session cookie
        domain: Optional[str] = None,           # Cookie domain scope
        max_age: Optional[int] = None,          # Cookie lifetime in seconds
        path: str = "/",                        # URL path scope
        secure: Optional[bool] = None,          # HTTPS-only flag
        httponly: bool = True,                  # JavaScript access restriction
        samesite: Optional[str] = None,         # CSRF protection level
        encoder: Callable = json.dumps,         # Data serializer
        decoder: Callable = json.loads,         # Data deserializer
    )
```

---

## cookie_name

**Default:** `"AIOHTTP_SESSION"`

The name of the HTTP cookie used to store session data or session identifier.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Custom cookie name
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    cookie_name="myapp_session"
)
```

### Considerations

**Cookie name conventions:**
- Use descriptive names: `session`, `sess_id`, `user_session`
- Prefix with application name: `myapp_session`, `api_session`
- Avoid conflicting with other cookies in your application

**Impact on Redis/Memcached storage:**
- Cookie name becomes part of the storage key
- Example: `cookie_name="myapp_session"` → Redis key: `myapp_session_{uuid}`

### Multiple Applications

When running multiple applications on the same domain, use unique cookie names:

```python
# App 1
setup(app1, EncryptedCookieStorage(key1, cookie_name="app1_session"))

# App 2
setup(app2, EncryptedCookieStorage(key2, cookie_name="app2_session"))
```

---

## domain

**Default:** `None` (current domain only)

Restricts the cookie to a specific domain and its subdomains.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Current domain only (default)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    domain=None
)

# Specific domain and subdomains
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    domain=".example.com"  # Note the leading dot
)

# Exact domain only (no subdomains)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    domain="api.example.com"
)
```

### Use Cases

**Single application:**
```python
# Default (None) is fine for most applications
storage = EncryptedCookieStorage(secret_key=key)
```

**Shared session across subdomains:**
```python
# User can access www.example.com, api.example.com, app.example.com with same session
storage = EncryptedCookieStorage(
    secret_key=key,
    domain=".example.com"  # Leading dot includes all subdomains
)
```

**Microservices architecture:**
```python
# Separate sessions for API and frontend
api_storage = EncryptedCookieStorage(key1, domain="api.example.com")
web_storage = EncryptedCookieStorage(key2, domain="www.example.com")
```

### Browser Behavior

| Domain Setting | Example Request | Cookie Sent? |
|---------------|-----------------|--------------|
| `None` | `app.example.com` | ✅ Yes |
| `None` | `www.app.example.com` | ❌ No |
| `.example.com` | `example.com` | ✅ Yes |
| `.example.com` | `app.example.com` | ✅ Yes |
| `.example.com` | `www.app.example.com` | ✅ Yes |
| `api.example.com` | `api.example.com` | ✅ Yes |
| `api.example.com` | `www.api.example.com` | ❌ No |

---

## path

**Default:** `"/"` (entire domain)

Restricts the cookie to a specific URL path and its subpaths.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Entire domain (default)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    path="/"
)

# Specific path only
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    path="/admin"
)

# API-only sessions
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    path="/api"
)
```

### Use Cases

**Single application (default):**
```python
# Session available everywhere
storage = EncryptedCookieStorage(secret_key=key, path="/")
```

**Admin panel isolation:**
```python
# Separate session for admin area
admin_storage = EncryptedCookieStorage(
    secret_key=admin_key,
    path="/admin"
)
```

**Multiple apps on same domain:**
```python
# Shop app at /shop
shop_storage = EncryptedCookieStorage(key1, path="/shop")

# Blog app at /blog  
blog_storage = EncryptedCookieStorage(key2, path="/blog")
```

### Browser Behavior

| Path Setting | Request URL | Cookie Sent? |
|-------------|-------------|--------------|
| `/` | `/` | ✅ Yes |
| `/` | `/any/path` | ✅ Yes |
| `/admin` | `/admin` | ✅ Yes |
| `/admin` | `/admin/users` | ✅ Yes |
| `/admin` | `/` | ❌ No |
| `/admin` | `/shop` | ❌ No |
| `/api` | `/api/v1/users` | ✅ Yes |
| `/api` | `/webpage` | ❌ No |

---

## max_age

**Default:** `None` (browser session cookie)

Maximum age of the cookie in seconds. After this time, the cookie expires automatically.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Browser session cookie (expires on browser close)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    max_age=None
)

# 30 minutes
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    max_age=1800
)

# 24 hours
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    max_age=86400
)

# 7 days
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    max_age=604800
)
```

### Per-Session max_age

Override the default `max_age` for individual sessions:

```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    
    # Short-lived session (15 minutes)
    session.max_age = 900
    
    # Or reset to default (None = browser session)
    session.max_age = None
```

### Security Recommendations

**High-security applications (banking, admin):**
```python
# 15-30 minute sessions
storage = EncryptedCookieStorage(key, max_age=900)  # 15 minutes
```

**Standard web applications:**
```python
# 24-hour sessions
storage = EncryptedCookieStorage(key, max_age=86400)  # 24 hours
```

**Long-lived applications (social media):**
```python
# 30-day sessions
storage = EncryptedCookieStorage(key, max_age=2592000)  # 30 days
```

### Behavior by Storage Type

**EncryptedCookieStorage / NaClCookieStorage:**
- Cookie expires after `max_age` seconds
- Token TTL also enforced (creates new session if expired)

**RedisStorage / MemcachedStorage:**
- Cookie expires after `max_age` seconds
- Server-side data also expires after `max_age` seconds
- Redis key expiration automatically set

**SimpleCookieStorage:**
- Cookie expires after `max_age` seconds only

### Age-Based Session Reset

Sessions older than `max_age` are automatically reset:

```python
storage = EncryptedCookieStorage(key, max_age=3600)  # 1 hour

# If cookie is > 1 hour old, session is treated as new
async def handler(request):
    session = await get_session(request)
    
    if session.new:
        # Either brand new user OR old expired session
        pass
```

---

## secure

**Default:** `None` (treated as `False`)

Restricts cookie to HTTPS connections only.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Insecure (default, for development)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    secure=False
)

# HTTPS only (production recommended)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    secure=True
)
```

### Environment-Based Configuration

```python
import os

is_production = os.environ.get('ENVIRONMENT') == 'production'

storage = EncryptedCookieStorage(
    secret_key=key,
    secure=is_production  # True in production, False in dev
)
```

### Recommendations

**Development:**
```python
secure=False  # Allow HTTP for local development
```

**Production:**
```python
secure=True  # Always use HTTPS in production
```

**Behind reverse proxy:**
```python
# If using nginx/AWS ALB, set secure=True
# Proxy handles HTTPS termination
storage = EncryptedCookieStorage(key, secure=True)
```

### Browser Behavior

| secure Setting | Protocol | Cookie Sent? |
|---------------|----------|--------------|
| `False` | HTTP | ✅ Yes |
| `False` | HTTPS | ✅ Yes |
| `True` | HTTP | ❌ No |
| `True` | HTTPS | ✅ Yes |

---

## httponly

**Default:** `True` (recommended)

Prevents JavaScript access to the cookie via `document.cookie`.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# JavaScript cannot access cookie (default, recommended)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    httponly=True
)

# JavaScript can access cookie (not recommended)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    httponly=False
)
```

### Security Impact

**httponly=True (default):**
- ✅ Protects against XSS cookie theft
- ✅ Cookie only accessible by HTTP requests
- ❌ Cannot read cookie value in JavaScript

**httponly=False:**
- ❌ Vulnerable to XSS attacks stealing session
- ✅ Can access cookie in JavaScript (rarely needed)

### When to Use httponly=False

Rare legitimate use cases:
```python
# Custom frontend session management
storage = EncryptedCookieStorage(key, httponly=False)

# Frontend needs to check session existence
# document.cookie contains session info
```

**Recommendation:** Keep `httponly=True` unless you have a specific requirement.

---

## samesite

**Default:** `None` (browser default, typically "Lax")

Controls whether cookie is sent with cross-origin requests. CSRF protection mechanism.

### Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Lax: No cross-site POST, allowed on top-level GET (recommended)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    samesite="Lax"
)

# Strict: Never sent with cross-site requests (maximum CSRF protection)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    samesite="Strict"
)

# None: Always sent (requires secure=True)
storage = EncryptedCookieStorage(
    secret_key=b'32-byte-secret-key-here-1234567890',
    samesite="None",
    secure=True  # REQUIRED when samesite=None
)
```

### Behavior Comparison

| SameSite Value | Cross-site GET | Cross-site POST | CSRF Protection | UX Impact |
|---------------|----------------|-----------------|-----------------|-----------|
| `Lax` (recommended) | ✅ Yes (top-level) | ❌ No | Good | Minimal |
| `Strict` | ❌ No | ❌ No | Maximum | Breaks some links |
| `None` | ✅ Yes | ✅ Yes | None | Best for cross-site |
| `None` + `secure=False` | ❌ Invalid | ❌ Invalid | - | Browser rejects |

### Use Cases

**Standard web application:**
```python
# Good CSRF protection, minimal UX impact
storage = EncryptedCookieStorage(key, samesite="Lax")
```

**High-security application:**
```python
# Maximum CSRF protection
storage = EncryptedCookieStorage(key, samesite="Strict")
```

**Cross-origin embedded application:**
```python
# Cookie sent when app embedded in iframe on different domain
storage = EncryptedCookieStorage(
    key, 
    samesite="None", 
    secure=True  # REQUIRED!
)
```

### Browser Support

- Chrome 80+, Firefox 80+, Safari 14+: Full support
- Older browsers: May ignore SameSite attribute
- `samesite=None` requires `secure=True` in all modern browsers

---

## expires

**Automatically calculated from max_age**

The absolute expiration timestamp is automatically generated when `max_age` is set. No manual configuration needed.

```python
# Setting max_age automatically sets expires header
storage = EncryptedCookieStorage(key, max_age=3600)

# Cookie will have:
# Set-Cookie: AIOHTTP_SESSION=...; Expires=Thu, 13-Apr-2024 17:00:00 GMT
```

---

## Complete Configuration Examples

### Production Web Application

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=os.environ['SESSION_KEY'],  # 32-byte key from env
    cookie_name="myapp_session",
    domain=".example.com",      # Share across subdomains
    path="/",                   # Entire domain
    max_age=86400,              # 24 hours
    secure=True,                # HTTPS only
    httponly=True,              # No JavaScript access
    samesite="Lax"              # CSRF protection
)
```

### High-Security Admin Panel

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=os.environ['ADMIN_SESSION_KEY'],
    cookie_name="admin_session",
    domain="admin.example.com",  # Specific domain only
    path="/",
    max_age=900,                 # 15 minutes
    secure=True,
    httponly=True,
    samesite="Strict"            # Maximum CSRF protection
)
```

### API with Cross-Origin Access

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=os.environ['API_SESSION_KEY'],
    cookie_name="api_session",
    domain="api.example.com",
    path="/",
    max_age=3600,                # 1 hour
    secure=True,                 # Required for samesite=None
    httponly=True,
    samesite="None"              # Allow cross-origin requests
)
```

### Development Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=b'development-key-not-for-production-1234',  # Dev key
    cookie_name="dev_session",
    domain=None,              # Current domain only
    path="/",
    max_age=None,             # Browser session cookie
    secure=False,             # Allow HTTP
    httponly=True,            # Still protect from XSS
    samesite="Lax"
)
```

### Multi-Environment Setup

```python
import os

env = os.environ.get('ENVIRONMENT', 'development')

if env == 'production':
    storage = EncryptedCookieStorage(
        secret_key=os.environ['SESSION_KEY'],
        max_age=86400,
        secure=True,
        httponly=True,
        samesite="Lax",
        domain=".example.com"
    )
else:
    storage = EncryptedCookieStorage(
        secret_key=b'development-key-not-for-production-1234',
        max_age=None,
        secure=False,
        httponly=True,
        samesite="Lax"
    )
```

---

## Cookie Attributes Reference Table

| Parameter | Default | Type | Description | Security Impact |
|-----------|---------|------|-------------|-----------------|
| `cookie_name` | `"AIOHTTP_SESSION"` | str | Cookie name | None |
| `domain` | `None` | str \| None | Domain scope | Prevents cross-domain access |
| `max_age` | `None` | int \| None | Lifetime in seconds | Limits session duration |
| `path` | `"/"` | str | URL path scope | Isolates by path |
| `secure` | `None` (False) | bool \| None | HTTPS only | Prevents MITM attacks |
| `httponly` | `True` | bool | No JavaScript access | Prevents XSS cookie theft |
| `samesite` | `None` | str \| None | CSRF protection level | Prevents CSRF attacks |

---

## Troubleshooting Cookie Issues

### Cookie Not Being Set

**Check:**
1. Storage is properly configured: `setup(app, storage)`
2. Response not prepared before session modification
3. No conflicting cookie names in application

```python
# Debug: Print response headers
async def handler(request):
    session = await get_session(request)
    session['test'] = 'value'
    
    response = web.Response(text='OK')
    print(response.headers)  # Check Set-Cookie header
    return response
```

### Cookie Sent but Session Empty

**Possible causes:**
1. Wrong encryption key (EncryptedCookieStorage)
2. Redis/Memcached data expired or deleted
3. Cookie domain/path mismatch

**Debug EncryptedCookieStorage:**
```python
# Check if decryption works
from cryptography.fernet import Fernet

cookie_value = request.cookies.get('AIOHTTP_SESSION')
try:
    decrypted = fernet.decrypt(cookie_value.encode())
    print(f"Decrypted: {decrypted}")
except InvalidToken:
    print("Invalid token - wrong key or corrupted cookie")
```

### Cookie Size Issues (EncryptedCookieStorage)

**Symptoms:** Session data lost after certain size

**Cause:** Cookies limited to ~4KB total

**Solutions:**
1. Use RedisStorage/MemcachedStorage for large sessions
2. Reduce session data stored
3. Implement session data cleanup

```python
# Check session size
import json
session_data = json.dumps(dict(session))
print(f"Session size: {len(session_data)} bytes")
```
