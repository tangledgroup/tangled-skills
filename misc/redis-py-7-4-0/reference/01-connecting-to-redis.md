# Connecting to Redis

## Basic Connection

Connect to a local Redis instance on the default port:

```python
import redis
r = redis.Redis()
r.ping()  # True
```

Specify host, port, and database:

```python
r = redis.Redis(host='localhost', port=6379, db=0)
```

Decode responses as strings instead of bytes:

```python
r = redis.Redis(decode_responses=True)
r.set('foo', 'bar')
r.get('foo')  # 'bar' (str, not b'bar')
```

## URL Connection

Use `from_url()` with standard Redis URL schemes:

```python
# TCP connection
r = redis.from_url('redis://localhost:6379/0')

# SSL-wrapped TCP
r = redis.from_url('rediss://localhost:6379/0')

# Unix socket
r = redis.from_url('unix:///path/to/socket.sock?db=0')

# With authentication
r = redis.from_url('redis://username:password@localhost:6379/0')

# With RESP3 protocol
r = redis.from_url('redis://localhost:6379?protocol=3')
```

Query string options are cast to appropriate Python types. Boolean arguments accept `"True"`/`"False"` or `"Yes"`/`"No"`.

## Connection Pools

Each `Redis` instance creates its own pool by default. Create shared pools explicitly:

```python
# Shared pool — multiple clients share the same pool
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)

# Exclusive ownership — pool closes when Redis client closes
pool = redis.ConnectionPool.from_url('redis://localhost')
r = redis.Redis.from_pool(pool)
```

## SSL/TLS Connections

Enable SSL with `ssl=True`:

```python
import redis
r = redis.Redis(host='localhost', port=6666, ssl=True, ssl_cert_reqs='none')
```

With client certificates and CA verification:

```python
import os
r = redis.Redis(
    host='localhost', port=6666,
    ssl=True,
    ssl_certfile='/path/to/client-cert.pem',
    ssl_keyfile='/path/to/client-key.pem',
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca-cert.pem',
)
```

Enforce minimum TLS version:

```python
import ssl
r = redis.Redis(
    host='localhost', port=6666,
    ssl=True,
    ssl_min_version=ssl.TLSVersion.TLSv1_3,
    ssl_cert_reqs='none',
)
```

OCSP validation (requires `redis[ocsp]` extras):

```python
r = redis.Redis(
    host='localhost', port=6666,
    ssl=True,
    ssl_validate_ocsp=True,
)
```

Full SSL parameters available on `redis.Redis`:

- `ssl_keyfile` — Path to client private key
- `ssl_certfile` — Path to client certificate
- `ssl_cert_reqs` — Certificate requirement level (`'none'`, `'required'`, or `ssl.VerifyMode`)
- `ssl_ca_certs` — Path to CA certificate bundle
- `ssl_ca_path` — Path to CA directory
- `ssl_ca_data` — In-memory CA certificate data
- `ssl_check_hostname` — Verify hostname matches certificate
- `ssl_password` — Password for encrypted key file
- `ssl_min_version` — Minimum TLS version
- `ssl_ciphers` — Allowed cipher suites

## Credential Providers

For dynamic credential management (e.g., AWS Secrets Manager):

```python
# Simple username/password provider
creds = redis.UsernamePasswordCredentialProvider('username', 'password')
r = redis.Redis(host='localhost', port=6379, credential_provider=creds)
```

Custom credential provider implementing `get_credentials()`:

```python
from typing import Tuple
import redis

class CustomProvider(redis.CredentialProvider):
    def __init__(self, username: str):
        self.username = username

    def get_credentials(self) -> Tuple[str, str]:
        # Fetch credentials from external source
        return self.username, "fetched_password"

r = redis.Redis(host='localhost', credential_provider=CustomProvider('user1'))
```

## Connection Parameters Summary

Key parameters for `redis.Redis()`:

- `host` — Redis server hostname (default: `'localhost'`)
- `port` — Redis server port (default: `6379`)
- `db` — Database number (default: `0`)
- `password` — Authentication password
- `username` — ACL username
- `socket_timeout` — Socket timeout in seconds
- `socket_connect_timeout` — Connection timeout
- `socket_keepalive` — Enable TCP keepalive
- `decode_responses` — Auto-decode responses to strings
- `max_connections` — Maximum pool size
- `health_check_interval` — Interval for connection health checks
- `retry_on_timeout` — Retry on timeout errors
- `client_name` — Client identifier visible in `CLIENT LIST`
- `protocol` — RESP protocol version (2 or 3, default 3 from v8.0+)
