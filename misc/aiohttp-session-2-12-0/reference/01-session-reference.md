# Session Reference

## Class: `Session`

The `Session` class is a `MutableMapping[str, Any]` — it supports all standard dictionary operations (`__getitem__`, `__setitem__`, `__delitem__`, `__len__`, `__iter__`, `__contains__`) plus session-specific attributes and methods.

**Never create Session instances directly.** Always retrieve them via `await get_session(request)` or `await new_session(request)`.

## Attributes

### `session.new` (bool, read-only)

Whether this is a brand-new session. `True` on first creation, `False` when loaded from persisted data.

```python
async def handler(request):
    session = await get_session(request)
    if session.new:
        print("First visit")
    else:
        print("Returning visitor")
```

### `session.created` (int, read-only)

UNIX timestamp of when the session was first created. Returns the value from `time.time()` at initial access.

### `session.identity` (str or None, read-only)

The client's identity — typically a cookie name or database key. For cookie-based storages this is `None`. For Redis/Memcached it holds the UUID key used to look up session data in the backend store.

To change identity, use `session.set_new_identity()` (only on new sessions).

### `session.empty` (bool, read-only)

Whether the session contains no data keys. Returns `True` when the internal mapping is empty.

### `session.max_age` (int or None, get/set)

Maximum age in seconds for the session data. `None` means a session cookie that lasts until the browser closes. When set on the storage constructor, this value propagates to new sessions.

```python
# Set max_age per-session
session.max_age = 1800  # 30 minutes
```

## Methods

### `session.changed()`

Mark the session as modified. Call this after mutating a mutable value stored in the session (e.g., appending to a list or modifying a nested dict). The session auto-tracks direct `__setitem__` and `__delitem__` calls, but has no way to detect in-place mutations of stored objects.

```python
# Mutation not auto-detected:
session['cart'].append(item)
session.changed()  # Required

# Direct assignment is auto-tracked:
session['count'] = 5  # No .changed() needed
```

There is no harm in calling `changed()` even when unnecessary — call it when in doubt.

### `session.invalidate()`

Clear all session data and mark the session as changed. This dumps all stored keys and triggers a clearing cookie on save. Use this for logout flows.

```python
async def logout(request):
    session = await get_session(request)
    session.invalidate()
    return web.Response(text='Logged out')
```

### `session.set_new_identity(identity)`

Change the session's identity key. Only allowed on new sessions (`session.new` must be `True`). Raises `RuntimeError` if called on an existing session.

## Getting Sessions

### `await get_session(request) -> Session`

Retrieve the current session from the request. Loads from storage if not yet loaded. Returns the same instance for repeated calls within a single request.

```python
from aiohttp_session import get_session

async def handler(request):
    session = await get_session(request)
    session['key'] = 'value'
```

Raises `RuntimeError` if the session middleware is not installed.

### `await new_session(request) -> Session`

Create a fresh session regardless of whether a cookie exists. The returned session always has `session.new == True`.

**Security warning:** Always use `new_session()` in login views to guard against Session Fixation attacks. An attacker could set a known session ID before the user logs in, then hijack the authenticated session.

```python
from aiohttp_session import new_session

async def login(request):
    session = await new_session(request)
    assert session.new is True
    session['user_id'] = 'auth-123'
```

## Data Serialization

Keys and values in the session must be JSON-serializable when using the included storage backends. Supported types include strings, lists, dicts, tuples, integers, floats, booleans, and `None`. Placing non-serializable objects (e.g., datetime, UUID, custom classes) will raise an error during serialization.

Custom encoders/decoders can be passed to the storage constructor to handle special types:

```python
import json
from datetime import datetime

def encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return json.default(obj)

storage = EncryptedCookieStorage(
    secret_key=b'Thirty  two  length  bytes  key.',
    encoder=encoder,
)
```
