# aiohttp Client Reference

## ClientSession

The recommended interface for making HTTP requests. Encapsulates a connection pool and supports keepalives by default.

### Constructor Parameters

```python
ClientSession(
    base_url=None,           # Base URL for relative requests
    connector=None,          # Connection pool instance
    cookies=None,            # Dict of cookies
    headers=None,            # Default headers (dict or CIMultiDict)
    skip_auto_headers=None,  # Headers to skip auto-generation
    auth=None,               # BasicAuth instance
    json_serialize=json.dumps,  # JSON serializer callable
    version=HttpVersion11,   # HTTP version
    cookie_jar=None,         # AbstractCookieJar instance
    connector_owner=True,    # Close connector on session close
    raise_for_status=False,  # Auto-raise HTTP errors
    timeout=sentinel,        # ClientTimeout instance
    auto_decompress=True,    # Auto-decompress responses
    trust_env=False,         # Read proxies from env vars
    requote_redirect_url=True,  # Requote redirect URLs
    trace_configs=None,      # Tracing configurations
    middlewares=(),          # Request middlewares
    read_bufsize=2**16,      # Read buffer size
    max_line_size=8190,      # Max HTTP line size
    max_field_size=8190,     # Max header field size
    max_headers=128,         # Max number of headers
)
```

### Base URL Support (3.8+)

Use `base_url` for relative URLs:

```python
session = ClientSession(base_url="http://api.example.com/v1/")

# Relative URL - joins with base
await session.get("/users")  # http://api.example.com/v1/users

# Absolute URL - overrides base
await session.get("https://other.com/api")  # https://other.com/api
```

**Note:** If base_url has a path, it must end with `/`. Relative URLs should not have leading `/` unless you want to override the path.

### HTTP Methods

All standard HTTP methods are available:

```python
async with session.get(url) as resp:        # GET
    ...

async with session.post(url, data=data) as resp:  # POST
    ...

async with session.put(url, data=data) as resp:   # PUT
    ...

async with session.patch(url, data=data) as resp: # PATCH
    ...

async with session.delete(url) as resp:     # DELETE
    ...

async with session.head(url) as resp:       # HEAD
    ...

async with session.options(url) as resp:    # OPTIONS
    ...
```

### Request Parameters

**Query parameters:**
```python
params = {'key1': 'value1', 'key2': 'value2'}
async with session.get('http://example.com/search', params=params) as resp:
    # GET http://example.com/search?key1=value1&key2=value2
    ...
```

**JSON data:**
```python
async with session.post(
    'http://api.example.com/users',
    json={'name': 'John', 'age': 30}
) as resp:
    # Automatically sets Content-Type: application/json
    data = await resp.json()
```

**Form data:**
```python
data = {'username': 'user', 'password': 'pass'}
async with session.post('http://example.com/login', data=data) as resp:
    # Content-Type: application/x-www-form-urlencoded
    ...
```

**Raw bytes:**
```python
async with session.post(
    'http://example.com/upload',
    data=b'binary data here'
) as resp:
    ...
```

**Multipart form data:** See [Multipart Reference](04-multipart.md)

### Headers

**Set default headers:**
```python
headers = {
    'Authorization': 'Bearer token123',
    'X-Custom-Header': 'value'
}
session = ClientSession(headers=headers)
```

**Per-request headers:**
```python
async with session.get(
    url,
    headers={'X-Request-ID': 'abc-123'}
) as resp:
    ...
```

**Skip auto-generated headers:**
```python
session = ClientSession(
    skip_auto_headers=['User-Agent', 'Accept-Encoding']
)
```

### Authentication

**Basic Auth:**
```python
from aiohttp import BasicAuth

auth = BasicAuth('username', 'password')
session = ClientSession(auth=auth)  # Applied to all requests

# Or per-request
async with session.get(url, auth=BasicAuth('user', 'pass')) as resp:
    ...
```

**Bearer Token:**
```python
headers = {'Authorization': 'Bearer your-token-here'}
session = ClientSession(headers=headers)
```

### Timeouts

Use `ClientTimeout` to configure timeouts:

```python
from aiohttp import ClientTimeout

# All timeouts in seconds
timeout = ClientTimeout(
    total=30,        # Total request timeout
    connect=5,       # Connection timeout
    sock_connect=5,  # Socket connection timeout
    sock_read=10,    # Socket read timeout
)

session = ClientSession(timeout=timeout)
```

**Per-request timeout:**
```python
async with session.get(url, timeout=ClientTimeout(total=10)) as resp:
    ...
```

### Response Object (`ClientResponse`)

**Properties:**
- `status` - HTTP status code (int)
- `headers` - Response headers (CIMultiDictProxy)
- `url` - Final URL after redirects (yarl.URL)
- `history` - List of previous responses if redirected
- `content` - StreamReader for streaming response body

**Methods:**
```python
# Get response as text
text = await resp.text(encoding='utf-8')

# Parse JSON
data = await resp.json(content_type=None)  # content_type=None skips validation

# Stream chunks
async for chunk in resp.content.iter_chunked(8192):
    process(chunk)

# Read all bytes
data = await resp.read()

# Raise exception for 4xx/5xx status
resp.raise_for_status()

# Access cookies
for name, cookie in resp.cookies.items():
    print(f"{name}: {cookie.value}")
```

### Connection Management

**TCPConnector (default):**
```python
from aiohttp import TCPConnector

connector = TCPConnector(
    limit=100,              # Max simultaneous connections
    limit_per_host=10,      # Max connections per host
    keepalive_timeout=30,   # Keep-alive timeout
    use_dns_cache=True,     # Enable DNS caching
    enable_cleanup_closed=True,  # Cleanup closed sockets
)

session = ClientSession(connector=connector)
```

**Sharing connection pool:**
```python
connector = TCPConnector(limit=100)

# Multiple sessions sharing same pool
session1 = ClientSession(connector=connector, connector_owner=False)
session2 = ClientSession(connector=connector, connector_owner=False)

# Close connector explicitly when done
await connector.close()
```

**SSL/TLS:**
```python
import ssl

# Disable SSL verification (testing only!)
session = ClientSession(connector=TCPConnector(ssl=False))

# Custom SSL context
ssl_context = ssl.create_default_context(cafile='/path/to/certs.pem')
session = ClientSession(connector=TCPConnector(ssl=ssl_context))

# Client certificates
ssl_context = ssl.create_default_context()
ssl_context.load_cert_chain('client.crt', 'client.key')
session = ClientSession(connector=TCPConnector(ssl=ssl_context))
```

### Proxies

**HTTP Proxy:**
```python
session = ClientSession(proxy='http://proxy.example.com:8080')

# Per-request proxy
async with session.get(url, proxy='http://proxy:8080') as resp:
    ...
```

**Proxy with authentication:**
```python
from aiohttp import BasicAuth

proxy_auth = BasicAuth('proxy_user', 'proxy_pass')
session = ClientSession(
    proxy='http://proxy.example.com:8080',
    proxy_auth=proxy_auth
)
```

**SOCKS Proxy:**
```python
# Requires: pip install aiohttp-socks
from aiohttp_socks import SocksConnector

connector = SocksConnector(
    rdns=True,  # Resolve DNS on remote side
    socks_ver=5,  # SOCKS5
    host='socks.example.com',
    port=1080,
)
session = ClientSession(connector=connector)
```

**Trust environment proxies:**
```python
# Read HTTP_PROXY, HTTPS_PROXY, NO_PROXY from environment
session = ClientSession(trust_env=True)
```

### Streaming Large Responses

```python
async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(path, 'wb') as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
```

### Request Middleware

```python
async def log_request(session, request_kwargs):
    print(f"Request: {request_kwargs.get('method')} {request_kwargs.get('url')}")
    return None  # Return None to proceed, or Response to short-circuit

session = ClientSession(middlewares=[log_request])
```

### Error Handling

**HTTP errors:**
```python
try:
    async with session.get(url) as resp:
        resp.raise_for_status()  # Raises HTTPError for 4xx/5xx
except aiohttp.HTTPError as e:
    print(f"HTTP error: {e.status}")
```

**Connection errors:**
```python
try:
    async with session.get(url) as resp:
        ...
except aiohttp.ClientConnectorError as e:
    print(f"Connection failed: {e}")
except aiohttp.ServerTimeoutError as e:
    print(f"Server timed out: {e}")
except aiohttp.ClientPayloadError as e:
    print(f"Payload error: {e}")
```

**Automatic retry:**
```python
async def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as resp:
                return await resp.text()
        except aiohttp.ClientError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Cookies

**Set cookies:**
```python
cookies = {'session_id': 'abc123', 'theme': 'dark'}
session = ClientSession(cookies=cookies)
```

**Cookie jar sharing:**
```python
from aiohttp import CookieJar

jar = CookieJar()
session1 = ClientSession(cookie_jar=jar)
session2 = ClientSession(cookie_jar=jar)  # Shares cookies
```

**Disable cookies:**
```python
from aiohttp import DummyCookieJar

session = ClientSession(cookie_jar=DummyCookieJar())
```

### Redirects

**Control redirects:**
```python
# Disable redirects (allow_redirects defaults to True)
async with session.get(url, allow_redirects=False) as resp:
    ...

# Limit redirect count
async with session.get(url, max_redirects=5) as resp:
    history = resp.history  # List of redirected responses
```

### JSON Handling

**Custom JSON serializer:**
```python
import json

def custom_serialize(obj):
    return json.dumps(obj, default=str)  # Custom default handler

session = ClientSession(json_serialize=custom_serialize)
```

**Parse response JSON:**
```python
# With content-type validation (default)
data = await resp.json()

# Without content-type validation
data = await resp.json(content_type=None)

# With custom encoding
data = await resp.json(encoding='utf-8')
```
