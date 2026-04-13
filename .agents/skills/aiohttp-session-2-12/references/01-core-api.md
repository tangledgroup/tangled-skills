# Core API Reference

This document covers the core aiohttp-session API including session operations, middleware setup, and the Session class interface.

## Setup Functions

### `setup(app, storage)`

The recommended way to configure sessions in an aiohttp application.

**Signature:**
```python
def setup(app: web.Application, storage: AbstractStorage) -> None
```

**Parameters:**
- `app` - The aiohttp.web.Application instance
- `storage` - A session storage instance (SimpleCookieStorage, EncryptedCookieStorage, RedisStorage, etc.)

**Example:**
```python
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

app = web.Application()
setup(app, EncryptedCookieStorage(b'32-byte-secret-key-here-1234567890'))
```

**Note:** This function internally calls `session_middleware(storage)` and appends it to `app.middlewares`.

### `session_middleware(storage)`

Alternative way to create session middleware for manual configuration.

**Signature:**
```python
def session_middleware(storage: AbstractStorage) -> Middleware
```

**Example:**
```python
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

storage = EncryptedCookieStorage(b'32-byte-secret-key-here-1234567890')
app = web.Application(middlewares=[session_middleware(storage)])
```

## Session Access Functions

### `get_session(request)`

Retrieves the current session for a request, loading from storage if necessary.

**Signature:**
```python
async def get_session(request: web.Request) -> Session
```

**Behavior:**
- Loads existing session from storage based on cookie
- Creates new empty session if no valid cookie exists
- Caches session in request object for subsequent calls

**Example:**
```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    
    # Access session data like a dictionary
    username = session.get('username', 'guest')
    session['last_visit'] = time.time()
    
    return web.Response(text=f'Hello, {username}')
```

**Note:** Calling `get_session()` multiple times in the same request returns the cached session object.

### `new_session(request)`

Creates a new session regardless of existing cookies. **Critical for preventing session fixation attacks.**

**Signature:**
```python
async def new_session(request: web.Request) -> Session
```

**Behavior:**
- Always creates a fresh session with `session.new == True`
- Discards any existing session data
- Generates new session identity

**Example - Login Handler:**
```python
from aiohttp_session import new_session

async def login_handler(request):
    # Always use new_session() in login views!
    session = await new_session(request)
    
    # Verify credentials...
    if valid:
        session['user_id'] = user.id
        session['username'] = user.username
        return web.Response(text='Login successful')
    
    return web.Response(text='Invalid credentials', status=401)
```

**Security Note:** Never use `get_session()` in login handlers - attackers can set a known session ID before login, then predict the authenticated session.

## Session Class

The `Session` class is a `MutableMapping` (dict-like object) with additional methods for lifecycle management.

### Properties

#### `session.new` (bool, read-only)

Indicates if this is a newly created session.

```python
async def handler(request):
    session = await get_session(request)
    
    if session.new:
        # First time visitor
        session['visitor_type'] = 'new'
    else:
        # Returning visitor
        session['visitor_type'] = 'returning'
```

#### `session.identity` (optional, read-only)

The session identifier (cookie value or database key). Read-only; use `set_new_identity()` for new sessions.

```python
async def handler(request):
    session = await get_session(request)
    print(f"Session ID: {session.identity}")
```

#### `session.created` (int, read-only)

Unix timestamp when the session was created.

```python
import time
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    age_seconds = time.time() - session.created
    print(f"Session is {age_seconds:.0f} seconds old")
```

#### `session.empty` (bool, read-only)

True if the session contains no data.

```python
async def handler(request):
    session = await get_session(request)
    
    if session.empty:
        return web.Response(text='No session data')
```

#### `session.max_age` (int | None, read/write)

Maximum age of the session in seconds. Can be set dynamically.

```python
async def handler(request):
    session = await get_session(request)
    
    # Set session to expire in 30 minutes
    session.max_age = 1800
    
    # Note: This only affects future saves, existing cookies keep their expiry
```

### Methods

#### `session.changed()`

Manually mark the session as changed. Required when mutating nested mutable objects.

**When to call:**
- After modifying lists/dicts stored in session
- Not needed for direct assignments (`session[key] = value`)
- Safe to call even when unnecessary

**Example:**
```python
async def add_to_cart(request):
    session = await get_session(request)
    
    # Initialize cart if needed
    if 'cart' not in session:
        session['cart'] = []
    
    # Mutating the list requires changed()
    session['cart'].append({'product': 'widget', 'quantity': 1})
    session.changed()  # Mark as modified
    
    return web.Response(text='Added to cart')
```

**Why needed:** The session middleware can't detect mutations inside nested objects, only direct key assignments/deletions.

#### `session.invalidate()`

Clears all session data and marks session for deletion.

**Example - Logout Handler:**
```python
from aiohttp_session import get_session

async def logout_handler(request):
    session = await get_session(request)
    session.invalidate()  # Clears all data
    
    return web.Response(text='Logged out successfully')
```

**Behavior:**
- Empties all session data
- Marks session as changed (will be saved/deleted)
- Does not change session identity

#### `session.set_new_identity(identity)`

Changes the session identity. **Only allowed on new sessions.**

**Signature:**
```python
def set_new_identity(identity: Optional[Any]) -> None
```

**Example - User Login:**
```python
async def login_handler(request):
    session = await new_session(request)  # Must be new
    
    # Set custom identity (e.g., user ID)
    session.set_new_identity(f"user_{user_id}")
    session['username'] = username
    
    return web.Response(text='Logged in')
```

**Error:** Raises `RuntimeError` if called on non-new sessions.

### Dictionary Methods

Session supports all standard MutableMapping operations:

```python
async def handler(request):
    session = await get_session(request)
    
    # Set item
    session['key'] = 'value'
    
    # Get item (with default)
    value = session.get('key', 'default')
    
    # Check containment
    if 'key' in session:
        print('Key exists')
    
    # Delete item
    del session['key']
    
    # Pop item
    value = session.pop('key', None)
    
    # Iterate
    for key, value in session.items():
        print(f"{key}: {value}")
    
    # Length
    count = len(session)
    
    # Clear all
    session.clear()  # Alternative to invalidate()
```

## Session Data Constraints

### JSON Serialization Requirement

All session keys and values must be JSON-serializable when using built-in storage backends.

**Supported types:**
- `str` - Strings
- `int` / `float` - Numbers
- `bool` - Booleans (True/False)
- `None` - Null
- `list` - Arrays (with serializable elements)
- `dict` - Objects (with serializable keys/values)

**Example:**
```python
async def handler(request):
    session = await get_session(request)
    
    # Valid session data
    session['username'] = 'john'           # str
    session['age'] = 30                    # int
    session['score'] = 95.5                # float
    session['active'] = True               # bool
    session['metadata'] = None             # None
    session['tags'] = ['admin', 'user']    # list of str
    session['config'] = {'theme': 'dark'}  # dict
    
    return web.Response(text='OK')
```

**Invalid examples:**
```python
# Custom objects (will raise TypeError)
class User:
    pass

session['user'] = User()  # ERROR: Not JSON serializable

# Bytes (will raise TypeError)
session['data'] = b'binary'  # ERROR: Not JSON serializable

# datetime objects (will raise TypeError)
from datetime import datetime
session['timestamp'] = datetime.now()  # ERROR: Not JSON serializable
```

**Workaround - Custom Encoder/Decoder:**

See [Storage Backends](02-storage-backends.md) for custom encoder/decoder configuration.

## Middleware Behavior

The session middleware automatically:

1. **Loads session** from storage at request start (on first `get_session()` call)
2. **Saves session** at response end if `session._changed` is True
3. **Handles exceptions** - saves session even if handler raises HTTPException

**Request flow:**
```
Request arrives
    ↓
Middleware initializes (storage available in request)
    ↓
Handler calls get_session(request)
    ↓
Storage.load_session() called → Session object returned
    ↓
Handler modifies session
    ↓
Handler returns Response
    ↓
Middleware checks session._changed
    ↓
If changed: Storage.save_session() called
    ↓
Response sent to client
```

## Error Handling

### Missing Middleware Error

```python
async def handler(request):
    session = await get_session(request)  # RuntimeError if middleware not installed

# Raises: RuntimeError: "Install aiohttp_session middleware in your aiohttp.web.Application"
```

**Fix:** Ensure `setup(app, storage)` is called before adding routes.

### Invalid Storage Error

```python
from aiohttp_session import session_middleware

# Raises: RuntimeError: "Expected AbstractStorage got <class 'str'>"
middleware = session_middleware("invalid")  # Must be AbstractStorage instance
```

### Prepared Response Error

```python
async def handler(request):
    response = web.Response(text='OK')
    await response.prepare(request)  # Response already prepared
    
    session = await get_session(request)
    session['key'] = 'value'
    
    return response  # RuntimeError on middleware save attempt

# Raises: RuntimeError: "Cannot save session data into prepared response"
```

**Fix:** Modify session before calling `response.prepare()`.
