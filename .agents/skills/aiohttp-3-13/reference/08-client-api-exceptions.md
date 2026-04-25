# Client API: Exceptions

Comprehensive reference for aiohttp client exceptions and error handling.

## Base Exceptions

### ClientError

Base class for all client-side errors.

```python
from aiohttp import ClientError

try:
    async with session.get(url) as resp:
        await resp.text()
except ClientError as e:
    print(f"Client error: {e}")
```

## HTTP Errors

### ClientResponseError

Raised when `raise_for_status()` is called on a response with 4xx or 5xx status.

```python
from aiohttp import ClientResponseError

try:
    async with session.get('http://example.com/notfound') as resp:
        resp.raise_for_status()  # Raises if status >= 400
except ClientResponseError as e:
    print(f"Status: {e.status}")
    print(f"Message: {e.message}")
    print(f"URL: {e.request_info.url}")
```

**Properties:**
- `status` - HTTP status code (int)
- `message` - Error message (str)
- `request_info` - RequestInfo object with request details
- `headers` - Response headers

### HTTPError

Base class for HTTP-related errors.

## Connection Errors

### ClientConnectorError

Raised when connection to server fails.

```python
from aiohttp import ClientConnectorError

try:
    async with session.get('http://nonexistent.domain') as resp:
        ...
except ClientConnectorError as e:
    print(f"Connection failed: {e}")
    print(f"Host: {e.host}")
    print(f"Port: {e.port}")
```

**Common causes:**
- Server not reachable
- DNS resolution failure
- Connection refused
- Firewall blocking

### ClientConnectorCertificateError

SSL certificate verification failed.

```python
from aiohttp import ClientConnectorCertificateError

try:
    async with session.get('https://self-signed.example.com') as resp:
        ...
except ClientConnectorCertificateError as e:
    print(f"Certificate error: {e}")
```

**Solutions:**
- Install proper CA certificates
- Use `ssl=False` for testing (not production)
- Provide custom SSL context with proper CA bundle

### ServerDisconnectedError

Server closed connection unexpectedly.

```python
from aiohttp import ServerDisconnectedError

try:
    async with session.get('http://example.com') as resp:
        data = await resp.read()  # Server disconnects here
except ServerDisconnectedError as e:
    print(f"Server disconnected: {e}")
```

## Timeout Errors

### ClientTimeout

Configuration class for timeouts (not an exception itself).

```python
from aiohttp import ClientTimeout

timeout = ClientTimeout(
    total=30,        # Total request timeout
    connect=5,       # Connection establishment timeout
    sock_connect=5,  # Socket connection timeout
    sock_read=10,    # Socket read timeout
)

session = aiohttp.ClientSession(timeout=timeout)
```

### ServerTimeoutError

Server took too long to respond.

```python
from aiohttp import ServerTimeoutError

try:
    async with session.get('http://slow-server.com', 
                          timeout=ClientTimeout(total=5)) as resp:
        await resp.text()
except ServerTimeoutError as e:
    print(f"Request timed out: {e}")
```

### SocketTimeoutError

Socket operation timed out.

```python
from aiohttp import SocketTimeoutError

try:
    async with session.get(url) as resp:
        data = await resp.read()  # Read timeout
except SocketTimeoutError as e:
    print(f"Socket timeout: {e}")
```

## Payload Errors

### ClientPayloadError

Error while sending request payload.

```python
from aiohttp import ClientPayloadError

try:
    async with session.post(url, data=large_data) as resp:
        ...
except ClientPayloadError as e:
    print(f"Payload error: {e}")
```

### InvalidURL

Invalid URL format.

```python
from aiohttp import InvalidURL

try:
    async with session.get('not-a-valid-url') as resp:
        ...
except InvalidURL as e:
    print(f"Invalid URL: {e}")
```

## Redirect Errors

### TooManyRedirects

Maximum redirect count exceeded.

```python
from aiohttp import TooManyRedirects

try:
    # Default max_redirects is 10
    async with session.get('http://redirect-loop.com') as resp:
        ...
except TooManyRedirects as e:
    print(f"Too many redirects: {e}")
    print(f"History: {len(e.history)} redirects")
```

**Increase redirect limit:**
```python
async with session.get(url, max_redirects=20) as resp:
    ...
```

## WebSocket Errors

### WSHandshakeError

WebSocket handshake failed.

```python
from aiohttp import WSHandshakeError

try:
    async with session.ws_connect('ws://example.com/socket') as ws:
        ...
except WSHandshakeError as e:
    print(f"WebSocket handshake failed: {e}")
    print(f"Status: {e.status}")
```

### WebSocketError

General WebSocket error.

```python
from aiohttp import WebSocketError

try:
    async with session.ws_connect(url) as ws:
        await ws.send_str("message")
except WebSocketError as e:
    print(f"WebSocket error: {e.code} - {e.message}")
```

## Data Errors

### ContentTypeError

Response content-type doesn't match expected type.

```python
from aiohttp import ContentTypeError

try:
    async with session.get('http://example.com/text') as resp:
        data = await resp.json()  # Raises if not JSON
except ContentTypeError as e:
    print(f"Content is not JSON: {e}")
```

**Disable content-type check:**
```python
data = await resp.json(content_type=None)
```

### InvalidJSON

JSON parsing failed.

```python
from aiohttp import InvalidJSON

try:
    async with session.get(url) as resp:
        data = await resp.json()  # Raises if invalid JSON
except InvalidJSON as e:
    print(f"Invalid JSON: {e}")
```

## Authentication Errors

### ClientHttpProxyError

HTTP proxy error.

```python
from aiohttp import ClientHttpProxyError

try:
    async with session.get(url, proxy='http://proxy:8080') as resp:
        ...
except ClientHttpProxyError as e:
    print(f"Proxy error: {e}")
```

## Request Info

### RequestInfo

Contains information about the request (not an exception).

```python
from aiohttp import RequestInfo

async def handler(request):
    info = request
    print(f"Method: {info.method}")
    print(f"URL: {info.url}")
    print(f"Headers: {dict(info.headers)}")
    print(f"Real URL: {info.real_url}")
```

**Properties:**
- `method` - HTTP method (str)
- `url` - Request URL (yarl.URL)
- `headers` - Request headers (CIMultiDictProxy)
- `real_url` - Original URL before redirects

## Comprehensive Error Handling

### Multi-Level Error Handling

```python
import asyncio
from aiohttp import (
    ClientError, ClientResponseError, ClientConnectorError,
    ServerTimeoutError, TooManyRedirects, WSHandshakeError
)

async def robust_request(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    # Check HTTP status
                    resp.raise_for_status()
                    
                    # Parse response
                    data = await resp.json()
                    return data
                    
        except ClientResponseError as e:
            # HTTP error (4xx, 5xx)
            if e.status in (429, 503):  # Rate limit or service unavailable
                wait_time = min(2 ** attempt, 30)
                print(f"Retrying after {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            else:
                print(f"HTTP error {e.status}: {e.message}")
                raise
                
        except ClientConnectorError as e:
            # Connection failed
            print(f"Connection failed, retrying...")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
            
        except ServerTimeoutError as e:
            # Timeout
            print(f"Request timed out, retrying...")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
            
        except TooManyRedirects as e:
            # Redirect loop - don't retry
            print(f"Too many redirects: {len(e.history)}")
            raise
            
        except ClientError as e:
            # Any other client error
            print(f"Client error: {e}")
            raise
    
    raise Exception("Max retries exceeded")

# Usage
try:
    data = await robust_request('http://api.example.com/data')
    print(f"Success: {data}")
except Exception as e:
    print(f"Failed after all retries: {e}")
```

### Error Handling with Logging

```python
import logging
from aiohttp import ClientError

logger = logging.getLogger(__name__)

async def logged_request(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()
                
    except ClientResponseError as e:
        logger.warning(f"HTTP {e.status} for {url}: {e.message}")
        raise
        
    except ClientConnectorError as e:
        logger.error(f"Cannot connect to {url}: {e}")
        raise
        
    except ServerTimeoutError as e:
        logger.warning(f"Timeout connecting to {url}: {e}")
        raise
        
    except ClientError as e:
        logger.error(f"Unexpected error for {url}: {e}")
        raise
```

### Custom Exception Handler

```python
from aiohttp import ClientResponseError

class ApiError(Exception):
    """Custom API error with context"""
    def __init__(self, status: int, message: str, url: str):
        self.status = status
        self.message = message
        self.url = url
        super().__init__(f"{status} {message} at {url}")

async def request_with_custom_errors(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise ApiError(resp.status, text, str(url))
                return await resp.json()
                
    except ClientResponseError as e:
        # Convert to custom error
        raise ApiError(e.status, e.message, str(url)) from e
```
