# Security Best Practices

This document covers security considerations, best practices, and common vulnerabilities when using aiohttp-session for web applications.

## Session Fixation Prevention

**Session fixation** is an attack where an attacker sets a known session ID before a user authenticates, then uses that ID to hijack the authenticated session.

### The Vulnerability

```python
# ❌ VULNERABLE: Using get_session() in login handler
from aiohttp_session import get_session

async def login_handler(request):
    session = await get_session(request)  # Loads existing session
    
    # Attacker sets session ID beforehand
    # After successful login, attacker knows the session ID
    
    if validate_credentials(username, password):
        session['user_id'] = user.id
        session['authenticated'] = True
    
    return web.Response(text='Logged in')
```

### The Fix: Use new_session()

Always use `new_session()` in authentication handlers to generate a fresh session ID:

```python
# ✅ SECURE: Using new_session() in login handler
from aiohttp_session import new_session

async def login_handler(request):
    session = await new_session(request)  # Always creates new session
    
    if validate_credentials(username, password):
        session['user_id'] = user.id
        session['authenticated'] = True
        return web.Response(text='Logged in')
    
    return web.Response(text='Invalid credentials', status=401)
```

### When to Use new_session()

Use `new_session()` in these scenarios:
- ✅ Login/authentication handlers
- ✅ Privilege escalation (user gains admin rights)
- ✅ Password changes
- ✅ Email verification completion

Use `get_session()` for:
- ✅ Regular page views
- ✅ Reading existing session data
- ✅ Non-authentication operations

### Complete Login Example

```python
from aiohttp_session import new_session, get_session

async def login_handler(request):
    """Secure login with session fixation prevention."""
    
    # Always create new session for login
    session = await new_session(request)
    
    data = await request.post()
    username = data.get('username')
    password = data.get('password')
    
    # Validate credentials
    user = await authenticate(username, password)
    
    if not user:
        # Log failed attempt
        await log_failed_login(username, request.remote)
        return web.Response(text='Invalid credentials', status=401)
    
    # Store minimal user data in session
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    # Add login timestamp for monitoring
    import time
    session['last_login'] = time.time()
    
    # Optional: Track IP/user agent for anomaly detection
    session['login_ip'] = request.remote
    session['user_agent'] = request.headers.get('User-Agent', '')[:500]
    
    return web.Response(text='Login successful')

async def logout_handler(request):
    """Secure logout."""
    session = await get_session(request)
    
    # Log logout for audit trail
    if 'user_id' in session:
        await log_logout(session['user_id'])
    
    # Invalidate session
    session.invalidate()
    
    return web.Response(text='Logged out')
```

---

## Encryption Key Management

### Key Generation

Always use cryptographically secure random keys:

```python
# ✅ CORRECT: Using Fernet key generation
from cryptography.fernet import Fernet

# Generate once, save securely
key = Fernet.generate_key()
print(key.decode())  # Save this! e.g., to environment variable

# Key format: base64-encoded 32-byte string
# Example: "gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i="
```

```python
# ❌ WRONG: Weak keys
key = b'my-secret-key'  # Too short, not random
key = b'a' * 32         # Not random
key = os.urandom(16)    # Wrong length (need 32 bytes)
```

### Key Storage

**Production:** Store keys in environment variables or secret management systems:

```python
import os
from cryptography.fernet import Fernet

# Load from environment variable
fernet_key = os.environ['SESSION_ENCRYPTION_KEY']
fernet = Fernet(fernet_key)

storage = EncryptedCookieStorage(fernet)
```

**Docker/Kubernetes:** Use secrets:

```python
# Docker
docker run -e SESSION_ENCRYPTION_KEY="gJ5VxKjH8mN3pL2qR9sT1uV4wX6yZ0aB3cD5eF7gH9i=" myapp

# Kubernetes
# Use Kubernetes Secrets mounted as environment variables
```

**Cloud platforms:**
```python
# AWS
from botocore import client
key = secretsmanager.get_secret_value(SecretId='session-key')['SecretString']

# Azure
from azure.keyvault.secrets import SecretClient
key = secret_client.get_secret('session-key').value

# GCP
from google.cloud import secretmanager
key = secret_manager_client.access_secret_version(request).payload.data.decode()
```

### Key Rotation Strategy

Rotating encryption keys requires careful planning:

**Challenge:** Old sessions encrypted with old key become unreadable.

**Strategy 1: Dual-key approach (recommended)**

```python
from cryptography.fernet import MultiFernet, Fernet

# Create multiple Fernet instances
fernet_old = Fernet(os.environ['SESSION_KEY_OLD'])
fernet_new = Fernet(os.environ['SESSION_KEY_NEW'])

# MultiFernet tries each key for decryption, uses first for encryption
multi_fernet = MultiFernet([fernet_new, fernet_old])

storage = EncryptedCookieStorage(multi_fernet)
```

**Rotation process:**
1. Generate new key: `SESSION_KEY_NEW`
2. Deploy with both keys: `MultiFernet([new, old])`
3. New sessions use new key, old sessions still work
4. After session expiry period, remove old key

**Strategy 2: Redis/Memcached storage**

For server-side storage, simply invalidate all sessions:

```python
# For RedisStorage, can flush all session keys
import re

async def rotate_sessions(redis):
    # Delete all session keys
    cursor = 0
    while True:
        cursor, keys = await redis.scan(match="AIOHTTP_SESSION_*", count=100)
        if keys:
            await redis.delete(*keys)
        if cursor == 0:
            break
    
    # Users will get new sessions on next request
```

### Key Backup and Recovery

**Critical:** Lost encryption key = lost all user sessions

```python
# Store keys securely in multiple locations:
# 1. Environment variables (in memory only)
# 2. Secret management system (AWS Secrets Manager, Vault, etc.)
# 3. Encrypted backup file (offline storage)
# 4. Team emergency access procedure

# Document key rotation and recovery procedures
```

---

## Cookie Security Flags

Always use secure cookie flags in production:

### Recommended Configuration

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(
    secret_key=fernet_key,
    
    # Essential security flags
    secure=True,     # HTTPS only
    httponly=True,   # No JavaScript access
    samesite="Lax",  # CSRF protection
    
    # Optional: domain/path restrictions
    domain=".example.com",
    path="/"
)
```

### Flag Explanations

**secure=True:**
- Cookie only sent over HTTPS
- Prevents man-in-the-middle attacks
- Required for `samesite=None`

**httponly=True (default):**
- JavaScript cannot access cookie via `document.cookie`
- Prevents XSS-based session theft
- Keep enabled unless you have specific need to read cookie in JS

**samesite="Lax":**
- Cookie not sent on cross-site POST requests
- Prevents most CSRF attacks
- Allows cookie on top-level GET navigation (good UX)

**samesite="Strict":**
- Maximum CSRF protection
- Cookie never sent with cross-site requests
- May break legitimate cross-site links

### Development vs Production

```python
import os

is_production = os.environ.get('ENVIRONMENT') == 'production'

storage = EncryptedCookieStorage(
    secret_key=fernet_key,
    secure=is_production,  # False in dev for HTTP
    httponly=True,         # Always True
    samesite="Lax"
)
```

---

## Session Timeout and Expiration

### Implementing Session Timeouts

Use `max_age` to limit session lifetime:

```python
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# 30-minute session timeout
storage = EncryptedCookieStorage(
    secret_key=fernet_key,
    max_age=1800  # 30 minutes in seconds
)
```

### Inactivity Timeout

Implement inactivity tracking:

```python
import time
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    
    # Check last activity
    if 'last_activity' in session:
        inactive_seconds = time.time() - session['last_activity']
        
        if inactive_seconds > 1800:  # 30 minutes inactive
            # Session timeout
            session.invalidate()
            return web.Response(text='Session expired', status=401)
    
    # Update activity timestamp
    session['last_activity'] = time.time()
    session.changed()  # Mark as changed
    
    # Continue with request...
```

### Sliding Expiration

Refresh session lifetime on each request:

```python
from aiohttp_session import get_session

async def middleware(request, handler):
    response = await handler(request)
    
    # Extend session on each request
    session = await get_session(request)
    if not session.empty and 'user_id' in session:
        session.max_age = 3600  # Reset to 1 hour
    
    return response
```

### Absolute Expiration

Force logout after fixed time regardless of activity:

```python
import time
from aiohttp_session import get_session

async def check_session_expiration(request):
    session = await get_session(request)
    
    if 'created_at' in session:
        age = time.time() - session['created_at']
        
        if age > 86400:  # 24 hours absolute max
            session.invalidate()
            return web.Response(text='Session expired', status=401)
    
    return None  # Continue with request

# Add as middleware or check in each handler
```

---

## Session Data Security

### What to Store in Sessions

**Safe to store:**
- User ID (integer/UUID)
- Username (for display)
- Role/permissions
- Preferences (theme, language)
- Cart items (e-commerce)
- Temporary flags

**Never store:**
- Passwords (even hashed)
- Credit card numbers
- Social security numbers
- Full payment information
- API keys or secrets
- Sensitive PII (personal identifiable information)

```python
# ✅ SAFE
session['user_id'] = 12345
session['username'] = 'john_doe'
session['role'] = 'admin'
session['cart'] = [{'item_id': 1, 'qty': 2}]

# ❌ UNSAFE - NEVER DO THIS
session['password'] = password_hash      # Never store passwords
session['credit_card'] = '4111-1111-...' # Never store payment info
session['ssn'] = '123-45-6789'           # Never store PII
session['api_key'] = 'sk_live_...'       # Never store secrets
```

### Session Data Size Limits

**EncryptedCookieStorage:** Limited to ~3.5KB of session data (cookie size limit)

```python
import json

# Monitor session size
async def handler(request):
    session = await get_session(request)
    
    session['data'] = large_dataset
    
    # Check size before saving
    session_json = json.dumps(dict(session))
    if len(session_json) > 3000:  # ~3KB limit
        print(f"Warning: Session too large ({len(session_json)} bytes)")
        # Consider using RedisStorage instead
```

**Solution:** Use RedisStorage/MemcachedStorage for large session data.

### Data Validation

Validate session data on read to detect tampering:

```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    
    # Validate user_id is integer
    if 'user_id' in session:
        try:
            user_id = int(session['user_id'])
        except (ValueError, TypeError):
            # Corrupted or tampered data
            session.invalidate()
            return web.Response(text='Invalid session', status=401)
    
    # Validate role is allowed value
    if 'role' in session:
        allowed_roles = {'user', 'admin', 'moderator'}
        if session['role'] not in allowed_roles:
            session.pop('role')  # Remove invalid role
```

---

## Redis/Memcached Security

### Connection Security

**Redis with authentication:**

```python
from redis.asyncio import from_url
from aiohttp_session.redis_storage import RedisStorage

# Use authentication
redis = await from_url("redis://:password@localhost:6379")
storage = RedisStorage(redis)
```

**Redis over TLS:**

```python
redis = await from_url("rediss://:password@localhost:6380", ssl=True)
storage = RedisStorage(redis)
```

**Redis in private network:**

```python
# Use VPC/private subnet, no public access
# Firewall rules: Only allow app servers to connect
redis = await from_url("redis://redis.internal:6379")
storage = RedisStorage(redis)
```

### Data Encryption

Redis stores session data as JSON strings. Consider encryption at rest:

```python
from cryptography.fernet import Fernet
import json

# Custom encoder that encrypts before storing in Redis
fernet = Fernet(os.environ['REDIS_ENCRYPTION_KEY'])

def encrypted_dumps(obj):
    json_str = json.dumps(obj)
    return fernet.encrypt(json_str.encode()).decode()

def encrypted_loads(data):
    decrypted = fernet.decrypt(data.encode())
    return json.loads(decrypted.decode())

storage = RedisStorage(
    redis,
    encoder=encrypted_dumps,
    decoder=encrypted_loads
)
```

### Access Control

Limit Redis access to session keys only:

```python
# Redis ACL (Redis 6.0+)
# Create user with limited permissions
ACL SETUSER sessionsel on >password +@read +@write +@connection ~AIOHTTP_SESSION_*

# Now this user can only access session keys
redis = await from_url("redis://sessionsel:password@localhost:6379")
```

---

## Logging and Monitoring

### Security Event Logging

Log important session events:

```python
import logging
from aiohttp_session import get_session, new_session

logger = logging.getLogger('session_security')

async def login_handler(request):
    session = await new_session(request)
    
    if validate_credentials(username, password):
        session['user_id'] = user.id
        
        # Log successful login
        logger.info(
            'User login',
            extra={
                'user_id': user.id,
                'ip': request.remote,
                'user_agent': request.headers.get('User-Agent', '')[:200]
            }
        )
        
        return web.Response(text='Logged in')
    else:
        # Log failed attempt
        logger.warning(
            'Failed login attempt',
            extra={
                'username': username,
                'ip': request.remote
            }
        )
        return web.Response(text='Invalid', status=401)
```

### Anomaly Detection

Detect suspicious patterns:

```python
from aiohttp_session import get_session

async def check_anomalies(request):
    session = await get_session(request)
    
    # Check for IP change (possible session hijacking)
    if 'login_ip' in session and session['login_ip'] != request.remote:
        logger.warning(
            'Session IP mismatch',
            extra={
                'original_ip': session['login_ip'],
                'current_ip': request.remote,
                'user_id': session.get('user_id')
            }
        )
        # Optional: Invalidate session or require re-authentication
    
    # Check for user agent change
    if 'user_agent' in session:
        current_ua = request.headers.get('User-Agent', '')[:200]
        if session['user_agent'] != current_ua:
            logger.info('User agent changed for session')
```

### Rate Limiting

Prevent brute force attacks:

```python
from aiohttp_session import get_session
import time

async def rate_limited_login(request):
    session = await get_session(request)
    
    # Track failed attempts in session
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0
        session['lockout_until'] = 0
    
    # Check lockout
    if time.time() < session['lockout_until']:
        remaining = session['lockout_until'] - time.time()
        return web.Response(text='Too many attempts', status=429)
    
    if not validate_credentials(username, password):
        session['failed_attempts'] += 1
        
        if session['failed_attempts'] >= 5:
            # Lock out for 15 minutes
            session['lockout_until'] = time.time() + 900
        
        return web.Response(text='Invalid', status=401)
    
    # Reset on success
    session['failed_attempts'] = 0
    session['lockout_until'] = 0
    
    return web.Response(text='Logged in')
```

---

## Common Vulnerabilities and Fixes

### XSS (Cross-Site Scripting)

**Prevention:** `httponly=True` prevents JavaScript access to session cookie

```python
# Default is httponly=True, but be explicit
storage = EncryptedCookieStorage(key, httponly=True)
```

Also sanitize all user input rendered in HTML:

```python
from aiohttp import web
import html

async def handler(request):
    session = await get_session(request)
    username = session.get('username', 'Guest')
    
    # Escape HTML to prevent XSS
    safe_username = html.escape(username)
    
    return web.Response(text=f'<p>Hello, {safe_username}</p>')
```

### CSRF (Cross-Site Request Forgery)

**Prevention:** `samesite="Lax"` prevents most CSRF attacks

```python
storage = EncryptedCookieStorage(key, samesite="Lax")
```

Also implement CSRF tokens for state-changing operations:

```python
# Generate CSRF token in session
async def get_csrf_token(request):
    session = await get_session(request)
    
    if '_csrf_token' not in session:
        import secrets
        session['_csrf_token'] = secrets.token_hex(32)
    
    return session['_csrf_token']

# Validate CSRF token
async def validate_csrf(request):
    session = await get_session(request)
    form = await request.post()
    
    expected = session.get('_csrf_token')
    actual = form.get('csrf_token')
    
    if not expected or expected != actual:
        return False
    
    return True
```

### Clickjacking

**Prevention:** Use X-Frame-Options header

```python
async def frame_options_middleware(request, handler):
    response = await handler(request)
    response.headers['X-Frame-Options'] = 'DENY'
    return response

app = web.Application(middlewares=[frame_options_middleware])
```

### Session Hijacking

**Prevention:** Bind session to client characteristics

```python
async def bind_session(request):
    session = await get_session(request)
    
    # Store fingerprint on first access
    if 'fingerprint' not in session:
        import hashlib
        
        ua = request.headers.get('User-Agent', '')[:100]
        ip = request.remote or ''
        
        fingerprint = hashlib.sha256(f"{ua}:{ip}".encode()).hexdigest()[:16]
        session['fingerprint'] = fingerprint
    
    # Verify fingerprint on subsequent requests
    else:
        ua = request.headers.get('User-Agent', '')[:100]
        ip = request.remote or ''
        
        current_fingerprint = hashlib.sha256(f"{ua}:{ip}".encode()).hexdigest()[:16]
        
        if session['fingerprint'] != current_fingerprint:
            # Fingerprint mismatch - possible hijacking
            logger.warning('Session fingerprint mismatch')
            # Consider invalidating session
```

---

## Security Checklist

- [ ] Use `new_session()` in all authentication handlers
- [ ] Generate cryptographically secure encryption keys (32 bytes)
- [ ] Store keys in environment variables or secret management
- [ ] Set `secure=True` in production (HTTPS only)
- [ ] Keep `httponly=True` (default, prevent XSS cookie theft)
- [ ] Set `samesite="Lax"` for CSRF protection
- [ ] Implement session timeout with `max_age`
- [ ] Never store sensitive data (passwords, PII) in sessions
- [ ] Monitor session size for cookie-based storage
- [ ] Use Redis/Memcached authentication and TLS
- [ ] Log security events (logins, logouts, failures)
- [ ] Implement rate limiting for login endpoints
- [ ] Plan key rotation strategy before production
