# Middleware and Extensions

## How the Middleware Works

The session middleware is registered via `setup(app, storage)` which is a shortcut for:

```python
app.middlewares.append(session_middleware(storage))
```

You can also pass the middleware directly to the Application constructor:

```python
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(b'Thirty  two  length  bytes  key.')
app = web.Application(middlewares=[session_middleware(storage)])
```

### Request/Response Flow

1. **Request arrives**: Middleware stores the storage instance on `request[STORAGE_KEY]`
2. **Handler executes**: Handler calls `await get_session(request)` which lazily loads from storage
3. **Handler modifies session**: Direct `__setitem__`/`__delitem__` auto-mark changed; mutable in-place edits require explicit `session.changed()`
4. **Response generated**: Middleware intercepts the response
5. **Session saved**: If `session._changed` is True, calls `storage.save_session(request, response, session)`
6. **Response returned**: Cookie is set (or cleared) by the storage's `save_cookie()` method

### Important Behaviors

- The middleware stores the session on `request[SESSION_KEY]` after first load, so repeated `get_session()` calls within a single request return the same instance
- If the response is already prepared (`response.prepared`), saving fails with `RuntimeError` — do not use sessions with pre-prepared responses
- WebSocket and streaming responses bypass session saving (detected by checking if response is `web.Response` subclass)
- HTTP exceptions are properly handled — session is saved before re-raising

## Third-Party Extensions

The aiohttp-session ecosystem includes community-maintained storage backends:

**aiohttp-session-mongo** — MongoDB storage backend
- Repository: https://github.com/alexpantyukhin/aiohttp-session-mongo
- Uses Motor (async MongoDB driver) for persistence

**aiohttp-session-dynamodb** — AWS DynamoDB storage backend
- Repository: https://github.com/alexpantyukhin/aiohttp-session-dynamodb
- Uses aioboto3 for async DynamoDB operations

**aiohttp-session-firestore** — Google Cloud Firestore storage backend
- Repository: https://github.com/dcgudeman/aiohttp-session-firestore
- Uses the async Firestore client library

## Security Considerations

### Session Fixation

Always use `new_session()` in login handlers. This creates a fresh session with a new identity, preventing attackers from pre-setting a session ID before authentication:

```python
from aiohttp_session import new_session

async def login(request):
    session = await new_session(request)  # Fresh session, prevents fixation
    session['user_id'] = user.id
```

### Cookie Security Flags

For production deployments, configure cookie security parameters:

```python
storage = EncryptedCookieStorage(
    secret_key=key,
    secure=True,       # Only send over HTTPS
    httponly=True,     # Block JavaScript access (default True)
    samesite='Lax',    # CSRF protection
    max_age=3600,      # 1 hour expiry
)
```

- **`secure=True`**: Cookie only sent over HTTPS connections
- **`httponly=True`**: Prevents JavaScript from reading the cookie (default)
- **`samesite='Lax'`** or `'Strict'`: Mitigates CSRF attacks by restricting cross-site cookie sending
- **`max_age`**: Limits session lifetime; `None` creates a session cookie that expires on browser close

### Key Rotation

For EncryptedCookieStorage, if you rotate the Fernet key, old cookies will fail decryption. The storage handles this gracefully — it logs a warning and creates a fresh session. Users lose their session data but are not blocked.

### Session Data Size

Cookie-based storages (SimpleCookie, EncryptedCookie, NaCl) are limited by browser cookie size limits (~4KB per cookie). Fernet encryption adds overhead (~50% size increase). For larger session data, use Redis or Memcached storage.
