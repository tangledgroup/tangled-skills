# Custom Storages

You can implement custom session backends by extending `AbstractStorage`. This is useful for integrating with databases not covered by the built-in storages (PostgreSQL, MongoDB, SQLite, etc.).

## AbstractStorage Base Class

All storages derive from `AbstractStorage`, which provides cookie handling helpers and requires implementing two abstract methods.

```python
class AbstractStorage:
    def __init__(
        self,
        *,
        cookie_name: str = "AIOHTTP_SESSION",
        domain: Optional[str] = None,
        max_age: Optional[int] = None,
        path: str = "/",
        secure: Optional[bool] = None,
        httponly: bool = True,
        samesite: Optional[str] = None,
        encoder: Callable[[object], str] = json.dumps,
        decoder: Callable[[str], Any] = json.loads,
    ) -> None:
        ...
```

### Required Methods to Implement

#### `async load_session(request) -> Session`

Called by the middleware on each request. Loads session data from your backend and returns a `Session` instance.

- Read the cookie value using `self.load_cookie(request)`
- If no cookie exists, return a new empty session: `Session(None, data=None, new=True, max_age=self.max_age)`
- If cookie exists, fetch data from your backend, decode it, and return `Session(identity, data=data_dict, new=False, max_age=self.max_age)`
- On errors (missing key, corrupt data), return a fresh session

#### `async save_session(request, response, session) -> None`

Called by the middleware when the response is being generated and the session was modified. Saves session data to your backend and sets the cookie.

- Use `self._get_session_data(session)` to get the serializable dict: `{"created": timestamp, "session": {...data...}}`
- Serialize with `self._encoder()`
- Store in your backend
- Set the cookie using `self.save_cookie(response, cookie_value, max_age=session.max_age)`
- To clear the cookie (e.g., on session.invalidate()), pass empty string: `self.save_cookie(response, "", max_age=session.max_age)`

### Helper Methods Available

**`self.load_cookie(request) -> str | None`**

Returns the raw cookie value from the request, or `None` if not present. Uses `self._cookie_name` internally.

**`self.save_cookie(response, cookie_data, *, max_age=None)`**

Sets the session cookie on the response with appropriate parameters (domain, path, secure, httponly, samesite). If `cookie_data` is empty string, deletes the cookie instead.

**`self._get_session_data(session) -> dict`**

Returns the serializable data structure: `{"created": session.created, "session": session._mapping}`. Returns `{}` if session is empty.

**`async self.new_session() -> Session`**

Creates a fresh empty session. Useful for login flows or when you need to start over.

### Properties Available

- **`self.cookie_name`**: The configured cookie name
- **`self.max_age`**: Maximum age in seconds (or `None`)
- **`self.cookie_params`**: Dict of all cookie parameters
- **`self._encoder`**: The serializer callable
- **`self._decoder`**: The deserializer callable

## Example: Custom Database Storage

```python
import json
from aiohttp import web
from aiohttp_session import AbstractStorage, Session


class DatabaseStorage(AbstractStorage):
    """Stores sessions in a custom database."""

    def __init__(self, db_pool, **kwargs):
        super().__init__(**kwargs)
        self._db = db_pool

    async def load_session(self, request: web.Request) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data=None, new=True, max_age=self.max_age)

        # Fetch from database
        row = await self._db.fetchrow(
            "SELECT data FROM sessions WHERE session_id = $1", cookie
        )
        if row is None:
            return Session(None, data=None, new=True, max_age=self.max_age)

        try:
            data = self._decoder(row['data'])
        except (json.JSONDecodeError, KeyError):
            return Session(None, data=None, new=True, max_age=self.max_age)

        return Session(cookie, data=data, new=False, max_age=self.max_age)

    async def save_session(
        self, request: web.Request,
        response: web.StreamResponse,
        session: Session
    ) -> None:
        if session.empty:
            self.save_cookie(response, "", max_age=session.max_age)
            return

        session_id = session.identity or str(uuid.uuid4().hex)
        data_str = self._encoder(self._get_session_data(session))

        # Upsert into database
        await self._db.execute(
            "INSERT INTO sessions (session_id, data, expires_at) "
            "VALUES ($1, $2, NOW() + INTERVAL $3) "
            "ON CONFLICT (session_id) DO UPDATE SET data = $2",
            session_id, data_str, f"{session.max_age} seconds"
        )

        self.save_cookie(response, session_id, max_age=session.max_age)
```

## Example: Using a Custom Key Factory

For Redis and Memcached storages, you can customize the key generation:

```python
import hashlib
from aiohttp_session.redis_storage import RedisStorage

def custom_key_factory():
    """Generate keys with a prefix for namespace isolation."""
    return f"sess:{uuid.uuid4().hex}"

storage = RedisStorage(redis_pool, key_factory=custom_key_factory)
```
