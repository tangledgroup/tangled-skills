# Client Reference

## ClientSession

The `ClientSession` is the primary client object. Create one per application, not per request.

### Constructor Parameters

- `base_url` — Base URL for relative requests (str or yarl.URL)
- `headers` — Default headers sent with every request (dict)
- `skip_auto_headers` — Headers to skip auto-generation for (set of str)
- `auth` — Default `BasicAuth` for all requests
- `json_serialize` — Custom JSON serializer callable (default: `json.dumps`)
- `json_serialize_bytes` — Custom bytes-returning JSON serializer (e.g., `orjson.dumps`)
- `request_class` — Custom `ClientRequest` subclass
- `response_class` — Custom `ClientResponse` subclass
- `ws_response_class` — Custom `ClientWebSocketResponse` subclass
- `version` — HTTP version, `HTTP/1.1` by default
- `cookie_jar` — Custom `CookieJar` instance (default: private jar per session)
- `connector_owner` — Close connector on session close (bool)
- `raise_for_status` — Auto-call `raise_for_status()` on each response (bool or callable)
- `timeout` — `ClientTimeout` settings (300s total, 30s connect by default)
- `auto_decompress` — Auto-decompress response body (True by default)
- `trust_env` — Trust environment proxy/netrc settings (False by default)
- `requote_redirect_url` — Apply URL requoting for redirects (True by default)
- `trace_configs` — List of `TraceConfig` instances for tracing
- `middlewares` — Sequence of middleware callables (added in 3.12)
- `read_bufsize` — Read buffer size in bytes (64 KiB by default)
- `max_line_size` / `max_field_size` / `max_headers` — Response limits
- `fallback_charset_resolver` — Callable for charset fallback when not specified

### Properties

- `closed` — True if session is closed (read-only)
- `connector` — The `BaseConnector` instance (read-only)
- `cookie_jar` — Session cookies (read-only)
- `timeout` — Default `ClientTimeout` instance (read-only)
- `headers` — HTTP headers sent with every request (read-only)

### Request Methods

All return async context managers yielding `ClientResponse`:

- `request(method, url, ...)` — Generic HTTP request
- `get(url, *, allow_redirects=True, **kwargs)` — GET request
- `post(url, *, data=None, **kwargs)` — POST request
- `put(url, *, data=None, **kwargs)` — PUT request
- `delete(url, **kwargs)` — DELETE request
- `head(url, **kwargs)` — HEAD request
- `options(url, **kwargs)` — OPTIONS request
- `patch(url, *, data=None, **kwargs)` — PATCH request
- `ws_connect(url, ...)` — WebSocket connection

### request() Parameters

- `params` — Query string parameters (dict, iterable of tuples, or str)
- `data` — Request body (FormData, dict, bytes, file-like object)
- `json` — JSON-serializable Python object (mutually exclusive with data)
- `cookies` — Per-request cookies (dict)
- `headers` — Per-request headers (dict)
- `auth` — Per-request `BasicAuth`
- `allow_redirects` — Follow redirects (True by default)
- `max_redirects` — Maximum redirect count (10 by default)
- `compress` — Compress request with deflate encoding
- `chunked` — Enable chunked transfer encoding (int for chunk size)
- `expect100` — Expect 100-continue response (False by default)
- `raise_for_status` — Override session's raise_for_status setting
- `read_until_eof` — Read until EOF if no Content-Length (True by default)
- `proxy` — Proxy URL (str or URL)
- `proxy_auth` — Proxy `BasicAuth`
- `timeout` — Override session timeout
- `ssl` — SSL validation mode (True, False, `Fingerprint`, `SSLContext`)
- `server_hostname` — Override certificate hostname matching
- `proxy_headers` — Headers to send to proxy
- `middlewares` — Per-request middleware override

### Response Object (ClientResponse)

- `status` — HTTP status code (int)
- `headers` — Response headers as `CIMultiDictProxy`
- `raw_headers` — Raw binary headers as tuple of tuples
- `cookies` — Response cookies from Set-Cookie headers
- `history` — Previous responses in redirect chain
- `url` — Final URL after redirects (yarl.URL)
- `content` — `StreamReader` for streaming body access

Methods:
- `await resp.text(encoding=None)` — Read body as text
- `await resp.read()` — Read body as bytes
- `await resp.json(content_type=None, loads=None)` — Parse JSON response
- `await resp.release()` — Release connection back to pool
- `resp.raise_for_status()` — Raise `ClientResponseError` for 4xx/5xx

### DigestAuthMiddleware

For HTTP digest authentication (RFC 7616):

```python
from aiohttp import ClientSession, DigestAuthMiddleware

digest_auth = DigestAuthMiddleware(login="user", password="password")
async with ClientSession(middlewares=(digest_auth,)) as session:
    async with session.get("https://example.com/protected") as resp:
        print(await resp.text())
```

Supports MD5, SHA, SHA-256, SHA-512 and their session variants. Automatically handles 401 challenge flow.

## Connectors

Connectors manage the connection pool between client and server.

### TCPConnector

Default connector for TCP connections:

```python
connector = aiohttp.TCPConnector(
    limit=100,           # Max connections in pool
    limit_per_host=10,   # Max connections per host
    enable_cleanup_closed=True,  # Clean up closed connections
    ssl=None,            # SSL context or True/False
    local_addr=('127.0.0.1', 0),  # Bind to specific local IP
)
async with aiohttp.ClientSession(connector=connector) as session:
    ...
```

### UnixConnector

For Unix domain sockets:

```python
connector = aiohttp.UnixConnector(path='/var/run/app.sock')
async with aiohttp.ClientSession(connector=connector) as session:
    ...
```

### Connection Pool Limits

- `limit` — Total connection pool size (0 for unlimited, default 100)
- `limit_per_host` — Per-host limit (default 100)
- Connections beyond the limit are queued and executed in FIFO order

## SSL/TLS Control

```python
# Default SSL verification
async with session.get('https://example.com', ssl=True) as resp: ...

# Skip SSL verification (not recommended for production)
async with session.get('https://example.com', ssl=False) as resp: ...

# Custom SSL context
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
async with session.get('https://example.com', ssl=ctx) as resp: ...

# Certificate fingerprint verification
fingerprint = aiohttp.Fingerprint(bytes.fromhex('ab:cd:...'))
async with session.get('https://example.com', ssl=fingerprint) as resp: ...
```

## Proxy Support

```python
# Direct proxy specification
async with session.get('https://example.com', proxy='http://proxy.example.com:8080') as resp: ...

# Proxy with authentication
proxy_auth = BasicAuth('user', 'pass')
async with session.get('https://example.com', proxy='http://proxy.example.com', proxy_auth=proxy_auth) as resp: ...

# Trust environment (uses HTTP_PROXY, HTTPS_PROXY env vars and ~/.netrc)
async with aiohttp.ClientSession(trust_env=True) as session:
    ...
```

## Cookie Management

### CookieJar

```python
# Strict mode (default) — rejects cookies from IP addresses per RFC 2109
jar = aiohttp.CookieJar(unsafe=False, quote_cookie=True)
session = aiohttp.ClientSession(cookie_jar=jar)

# Unsafe mode — accepts cookies from IP addresses (useful for testing)
jar = aiohttp.CookieJar(unsafe=True)
session = aiohttp.ClientSession(cookie_jar=jar)

# Disable cookie quoting
jar = aiohttp.CookieJar(quote_cookie=False)
session = aiohttp.ClientSession(cookie_jar=jar)

# Dummy jar — no cookie processing at all
jar = aiohttp.DummyCookieJar()
session = aiohttp.ClientSession(cookie_jar=jar)
```

### Setting Cookies

```python
# Per-session cookies
async with aiohttp.ClientSession(cookies={'name': 'value'}) as session:
    ...

# Cookies are shared between requests within the same session
async with aiohttp.ClientSession() as session:
    async with session.get("http://httpbin.org/cookies/set?my_cookie=my_value", allow_redirects=False) as resp:
        print(resp.cookies["my_cookie"].value)
    async with session.get("http://httpbin.org/cookies") as r:
        json_body = await r.json()  # my_cookie is included
```

## Client Tracing

Trace request lifecycle using `TraceConfig`:

```python
async def on_request_start(session, trace_config_ctx, params):
    print(f"Request started: {params.url}")

async def on_request_end(session, trace_config_ctx, params):
    print(f"Request ended: {params.response.status}")

trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)

async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
    ...
```

Available trace signals:
- `on_request_start` / `on_request_end` — Request lifecycle
- `on_request_chunk_sent` — Chunk sent
- `on_response_chunk_received` — Chunk received
- `on_request_exception` — Request error
- `on_request_redirect` — Redirect occurred
- `on_connection_queued_start/end` — Connection queueing
- `on_connection_create_start/end` — Connection creation
- `on_connection_reuseconn` — Connection reused
- `on_dns_resolve_host_start/end` — DNS resolution
- `on_dns_cache_hit/miss` — DNS cache status

Trace parameters classes: `TraceRequestStartParams`, `TraceRequestEndParams`, `TraceRequestChunkSentParams`, `TraceResponseChunkReceivedParams`, `TraceRequestExceptionParams`, `TraceRequestRedirectParams`.

## ClientTimeout

```python
from aiohttp import ClientTimeout

# Total timeout (request + response) and socket connect timeout
timeout = ClientTimeout(total=300, sock_connect=30)

# Per-request timeout override
async with session.get(url, timeout=ClientTimeout(total=10)) as resp:
    ...
```

## Client Exceptions

Exception hierarchy:

- `ClientError` — Base client exception
  - `ClientResponseError` — HTTP error response (4xx/5xx)
  - `ClientConnectorError` — Connection failure
    - `ClientConnectorSSLError` — SSL handshake failure
    - `ClientProxyConnectionError` — Proxy connection failure
  - `ClientPayloadError` — Malformed request payload
  - `InvalidURL` — Invalid URL format
  - `InvalidUrlClientError` — Client-side URL error
  - `RedirectClientError` — Redirect-related errors
  - `TooManyRedirects` — Exceeded max_redirects

## WebSocket Client

```python
async with session.ws_connect('wss://example.com/ws') as ws:
    # Send text message
    await ws.send_str('Hello')

    # Send binary data
    await ws.send_bytes(b'data')

    # Receive messages
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(msg.data)
        elif msg.type == aiohttp.WSMsgType.BINARY:
            print(msg.data)
        elif msg.type == aiohttp.WSMsgType.CLOSE:
            break
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break

    # Close connection
    await ws.close()
```

WebSocket message types: `WSMsgType.TEXT`, `WSMsgType.BINARY`, `WSMsgType.PING`, `WSMsgType.PONG`, `WSMsgType.CLOSE`, `WSMsgType.ERROR`, `WSMsgType.CLOSED`.

## Client Middleware Cookbook Patterns

### Retry Middleware

```python
async def retry_middleware(request, handler, retries=3):
    for attempt in range(retries):
        response = await handler(request)
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if e.status in (500, 502, 503, 504) and attempt < retries - 1:
                continue
            raise
        return response
    raise RuntimeError("Max retries exceeded")
```

### Token Refresh Middleware

```python
async def token_refresh_middleware(request, handler):
    response = await handler(request)
    if response.status == 401:
        # Refresh token and retry
        new_token = await refresh_access_token()
        request.headers["Authorization"] = f"Bearer {new_token}"
        response = await handler(request)
    return response
```

### Logging Middleware

```python
async def logging_middleware(request, handler):
    start = time.time()
    response = await handler(request)
    elapsed = time.time() - start
    print(f"{request.method} {request.url} -> {response.status} ({elapsed:.3f}s)")
    return response
```

Note: Middleware order matters. With `middlewares=(retry_mw, logging_mw)`, every retry is logged separately. Reversed order logs only once regardless of retries.
