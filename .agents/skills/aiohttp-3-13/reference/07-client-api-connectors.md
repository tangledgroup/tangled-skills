# Client API: Connectors

Connectors manage connection pools and TCP/Unix socket connections for the HTTP client.

## BaseConnector

Base class for all connectors. Defines the interface for connection management.

```python
from aiohttp import BaseConnector

class BaseConnector:
    async def connect(self, request, traces, timeout):
        """Get a connection for the request"""
        pass
    
    async def close(self):
        """Close all connections"""
        pass
    
    def __len__(self):
        """Number of acquired connections"""
        pass
```

**Properties:**
- `limit` - Maximum number of simultaneous connections
- `limit_per_host` - Maximum connections per host
- `acquired` - Number of currently acquired connections

## TCPConnector (Default)

Manages TCP connections with connection pooling and keep-alive.

### Constructor Parameters

```python
from aiohttp import TCPConnector

connector = TCPConnector(
    # Connection limits
    limit=100,              # Max simultaneous connections (default: 100)
    limit_per_host=10,      # Max connections per host (default: 10)
    
    # Keep-alive settings
    keepalive_timeout=None,  # Timeout for keep-alive connections (default: None = use server hint)
    
    # DNS settings
    use_dns_cache=True,     # Enable DNS caching (default: True)
    ttl_dns_cache=300,      # DNS cache TTL in seconds (default: 300)
    local_addr=None,        # Local address to bind to
    
    # SSL settings
    ssl=True,               # SSL context or True/False (default: True)
    
    # Connection settings
    family=0,               # Socket family (default: 0 = AF_UNSPEC)
    flags=0,                # Socket flags for getaddrinfo
    resolver=None,          # Custom DNS resolver
    
    # Cleanup
    enable_cleanup_closed=True,  # Enable cleanup of closed sockets
    loop=None,              # Event loop (default: None = get_event_loop())
)
```

### Usage Examples

**Basic usage:**
```python
import aiohttp

async def example():
    connector = TCPConnector(limit=50)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('http://example.com') as resp:
            print(await resp.text())
```

**Disable SSL verification (testing only):**
```python
connector = TCPConnector(ssl=False)
session = aiohttp.ClientSession(connector=connector)
```

**Custom SSL context:**
```python
import ssl

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations('/path/to/ca-bundle.crt')

connector = TCPConnector(ssl=ssl_context)
session = aiohttp.ClientSession(connector=connector)
```

**Client certificate authentication:**
```python
ssl_context = ssl.create_default_context()
ssl_context.load_cert_chain('client.crt', 'client.key')

connector = TCPConnector(ssl=ssl_context)
```

**Bind to specific local address:**
```python
connector = TCPConnector(local_addr=('192.168.1.100', 0))
```

**Custom DNS resolver:**
```python
from aiohttp import Resolver

class CustomResolver(Resolver):
    async def resolve(self, host, port=0, family=socket.AF_INET):
        # Custom resolution logic
        return [{'hostname': host, 'host': '127.0.0.1', 'port': port, 'family': socket.AF_INET}]

connector = TCPConnector(resolver=CustomResolver())
```

### Connection Pool Behavior

- Connections are reused automatically within the keep-alive timeout
- Pool is per-host (based on host:port combination)
- Closed connections are removed from pool automatically
- `limit` controls total concurrent connections across all hosts
- `limit_per_host` controls connections to individual hosts

## UnixConnector

For Unix domain socket connections.

```python
from aiohttp import UnixConnector

connector = UnixConnector(
    path='/var/run/socket.sock',  # Path to Unix socket
    limit=100,                     # Connection limit
    limit_per_host=10,             # Per-host limit
    ssl=False,                     # SSL not typically used with Unix sockets
    timeout=aiohttp.ClientTimeout(),
)

async with aiohttp.ClientSession(connector=connector) as session:
    async with session.get('http://localhost/path') as resp:
        print(await resp.text())
```

## NamedPipeConnector (Windows)

For Windows named pipes.

```python
from aiohttp import NamedPipeConnector

connector = NamedPipeConnector(
    path='\\\\.\\pipe\\mypipe',  # Named pipe path
    limit=100,
)

async with aiohttp.ClientSession(connector=connector) as session:
    async with session.get('http://localhost/path') as resp:
        print(await resp.text())
```

## SSLConnector

Wrapper for SSL/TLS connections (alias for TCPConnector with SSL).

```python
from aiohttp import TCPConnector
import ssl

# Create SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.load_verify_locations('ca-certificates.crt')

# Use with TCPConnector
connector = TCPConnector(ssl=ssl_context)
```

## Connection Limits and Pooling

### Understanding Limits

```python
# limit: Total max connections across all hosts
# limit_per_host: Max connections to single host

connector = TCPConnector(
    limit=100,        # Can have 100 concurrent connections total
    limit_per_host=10 # But max 10 to any single host
)

# If you request 15 connections to example.com:
# - First 10 will be created immediately
# - Remaining 5 will wait until a connection is freed
```

### Sharing Connection Pools

```python
# Create shared connector
connector = TCPConnector(limit=100)

# Multiple sessions sharing same pool
session1 = aiohttp.ClientSession(connector=connector, connector_owner=False)
session2 = aiohttp.ClientSession(connector=connector, connector_owner=False)

# Close connector explicitly when done
await connector.close()
```

### Monitoring Connection Pool

```python
connector = TCPConnector(limit=50)

async def monitor_pool():
    async with aiohttp.ClientSession(connector=connector) as session:
        # Check acquired connections
        print(f"Acquired: {len(connector._acquired)}")
        
        # Make requests
        async with session.get('http://example.com') as resp:
            await resp.text()
        
        print(f"After request: {len(connector._acquired)} acquired")

asyncio.run(monitor_pool())
```

## Custom Connector

Create a custom connector for special use cases:

```python
from aiohttp import BaseConnector, TCPTransport

class CustomConnector(BaseConnector):
    async def _create_connection(self, req, timeout, traces):
        # Custom connection creation logic
        loop = self._loop
        host = req.url.host
        port = req.url.port or 80
        
        transport, protocol = await loop.create_connection(
            lambda: TCPProtocol(),
            host=host,
            port=port,
        )
        
        return transport, protocol
    
    async def close(self):
        # Custom cleanup logic
        await super().close()

connector = CustomConnector(limit=50)
```

## Common Issues

**Too many open files:**
```python
# Increase limit if making many concurrent requests
connector = TCPConnector(limit=1000, limit_per_host=100)
```

**Connection timeout:**
```python
from aiohttp import ClientTimeout

timeout = ClientTimeout(total=30, connect=5)
connector = TCPConnector()
session = aiohttp.ClientSession(connector=connector, timeout=timeout)
```

**DNS resolution failures:**
```python
# Disable DNS cache if having issues
connector = TCPConnector(use_dns_cache=False)

# Or use aiodns for async DNS resolution
pip install aiodns
connector = TCPConnector()  # Will use aiodns if installed
```
