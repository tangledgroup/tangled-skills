# Storage Backends

aiohttp-session provides five storage backends. All derive from `AbstractStorage` and share the same cookie configuration parameters (`cookie_name`, `domain`, `max_age`, `path`, `secure`, `httponly`, `samesite`, `encoder`, `decoder`).

## Common Cookie Parameters

Every storage accepts these keyword arguments:

- **`cookie_name`** (str, default `"AIOHTTP_SESSION"`): Name of the HTTP cookie
- **`domain`** (str or None): Cookie domain scope
- **`max_age`** (int or None): Maximum age in seconds; `None` = session cookie
- **`path`** (str, default `"/"`): Cookie path scope
- **`secure`** (bool or None): HTTPS-only flag
- **`httponly`** (bool, default `True`): Block JavaScript access
- **`samesite`** (str or None): CSRF protection (`"Lax"`, `"Strict"`, `"None"`)
- **`encoder`** (callable, default `json.dumps`): Custom serializer
- **`decoder`** (callable, default `json.loads`): Custom deserializer

## SimpleCookieStorage

Stores session data as plain, unencrypted JSON in the browser cookie.

```python
from aiohttp_session import setup, SimpleCookieStorage

setup(app, SimpleCookieStorage())
```

**Warning:** Never use this in production. The data is visible and modifiable by the client. Use only for testing and development.

## EncryptedCookieStorage (Fernet)

Stores session data encrypted with Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256). Data lives entirely in the cookie — no server-side storage needed.

```python
from cryptography.fernet import Fernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Generate a key (do this once, store securely)
key = Fernet.generate_key()  # Returns 32 bytes base64-encoded

setup(app, EncryptedCookieStorage(key))
```

The `secret_key` parameter accepts:
- `bytes` or `bytearray` of length 32 (will be base64-encoded internally)
- `str` that is already base64-encoded
- A pre-built `Fernet` instance

If decryption fails (e.g., key was rotated, cookie tampered), the storage logs a warning and creates a fresh session automatically.

**Requires:** `cryptography` library (`aiohttp-session[secure]`).

## NaClCookieStorage

Similar to EncryptedCookieStorage but uses NaCl's `SecretBox` (XSalsa20-Poly1305) instead of Fernet. Provides authenticated encryption with a different cryptographic primitive.

```python
from aiohttp_session import setup
from aiohttp_session.nacl_storage import NaClCookieStorage

key = os.urandom(32)  # 32-byte secret key
setup(app, NaClCookieStorage(key))
```

The `secret_key` must be exactly 32 bytes. On decryption failure, logs a warning and creates a fresh session.

**Requires:** `pynacl` library.

## RedisStorage

Stores JSON-encoded session data in Redis. Only the Redis key (a random UUID hex string) is kept in the browser cookie. The actual session payload lives server-side.

```python
import redis.asyncio as aioredis
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage

redis = await aioredis.from_url("redis://127.0.0.1:6379")
setup(app, RedisStorage(redis))
```

**How it works:**
- On first request (no cookie), generates a UUID via `key_factory` (default: `uuid.uuid4().hex`)
- Stores session data in Redis under key `{cookie_name}_{uuid}` (e.g., `AIOHTTP_SESSION_e33b57c7ec6e425eb626610f811ab6ae`)
- Sets the UUID as the cookie value
- On subsequent requests, reads the UUID from cookie, fetches data from Redis
- Session data is saved with `ex=session.max_age` for automatic expiry

**Requires:** `redis>=4.3` with asyncio support (`aiohttp-session[aioredis]`). The library uses `redis.asyncio.Redis` (the built-in async interface of redis-py 4.3+), not the separate `aioredis` package.

## MemcachedStorage

Stores session data in Memcached via `aiomcache`. Like RedisStorage, only the key UUID is in the cookie.

```python
import aiomcache
from aiohttp_session import setup
from aiohttp_session.memcached_storage import MemcachedStorage

mc = await aiomcache.Client('localhost', 11211)
setup(app, MemcachedStorage(mc))
```

**How it works:**
- Same UUID-in-cookie pattern as RedisStorage
- Stores data under key `{cookie_name}_{uuid}` (encoded as bytes)
- Handles Memcached's 30-day expiry limit: values over 30 days are converted to UNIX timestamps

Memcached's expiry rules:
- `max_age` of `None` → expire = 0 (never expire, session cookie behavior)
- `max_age` <= 30 days → use as-is in seconds
- `max_age` > 30 days → convert to absolute UNIX timestamp

**Requires:** `aiomcache` library (`aiohttp-session[aiomcache]`).

## Choosing a Backend

- **SimpleCookieStorage**: Testing only, never production
- **EncryptedCookieStorage**: Stateless deployment, no infrastructure needed, cookie size limits (~4KB), good for small session data
- **NaClCookieStorage**: Same as encrypted but with NaCl crypto primitives
- **RedisStorage**: Distributed deployments, large session data, automatic TTL via Redis `EXPIRE`
- **MemcachedStorage**: Distributed deployments where Memcached is already in use
