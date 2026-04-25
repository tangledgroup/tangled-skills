# Connections and Clustering

Complete guide to Redis connection types, connection pooling, SSL/TLS authentication, Redis Cluster mode, Sentinel high availability, and async clients.

## Basic Connection Types

### Standalone Redis Client

```python
import redis

# Default connection (localhost:6379, db 0)
r = redis.Redis()

# Specify host and port
r = redis.Redis(host='localhost', port=6379)

# Specify database
r = redis.Redis(db=1)

# All parameters
r = redis.Redis(
    host='redis.example.com',
    port=6379,
    db=0,
    password='secret',
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    encoding='utf-8',
    encoding_errors='strict',
    decode_responses=False,
    connection_pool=None
)
```

### Connection URL

Use Redis URL scheme for concise configuration:

```python
import redis

# Basic URL
r = redis.from_url('redis://localhost:6379/0')

# With password
r = redis.from_url('redis://:password@localhost:6379/0')

# With username and password (Redis 6.0+)
r = redis.from_url('redis://username:password@localhost:6379/0')

# TLS connection
r = redis.from_url('rediss://localhost:6380')

# With query parameters
r = redis.from_url(
    'redis://localhost:6379/0?socket_timeout=5&decode_responses=true'
)

# Supported query parameters:
# - db=<int> - Database number
# - password=<str> - Password
# - socket_timeout=<float> - Socket timeout in seconds
# - socket_connect_timeout=<float> - Connection timeout
# - socket_keepalive=<bool> - Enable TCP keepalive
# - socket_keepalive_options=<list> - Keepalive options
# - retry_on_timeout=<bool> - Retry on timeout
# - encoding=<str> - Character encoding
# - decode_responses=<bool> - Auto-decode responses to str
# - health_check_interval=<int> - Health check interval (seconds)
# - max_connections=<int> - Max pool connections
```

### Connection Parameters Reference

```python
import redis

r = redis.Redis(
    # Server location
    host='localhost',           # Hostname or IP
    port=6379,                  # Port number
    unix_socket_path=None,      # Unix socket path (alternative to host:port)
    
    # Authentication
    password=None,              # Password for AUTH command
    username=None,              # Username for Redis 6.0+ ACL
    
    # Database selection
    db=0,                       # Database number (0-15)
    
    # Encoding
    encoding='utf-8',           # Character encoding
    encoding_errors='strict',   # Error handling: 'strict', 'replace', 'ignore'
    decode_responses=False,     # Auto-decode bytes to str
    
    # Timeouts
    socket_timeout=5,           # Socket read timeout (seconds)
    socket_connect_timeout=5,   # Connection timeout (seconds)
    retry_on_timeout=False,     # Retry on timeout errors
    
    # Connection management
    connection_pool=None,       # Custom connection pool
    health_check_interval=30,   # Health check interval (0 = disabled)
    max_connections=None,       # Max connections in pool
    
    # TCP options
    socket_keepalive=False,     # Enable TCP keepalive
    socket_keepalive_options=None,  # Keepalive options (list of tuples)
    
    # SSL/TLS
    ssl=False,                  # Enable TLS
    ssl_keyfile=None,           # Path to client private key
    ssl_certfile=None,          # Path to client certificate
    ssl_ca_certs=None,          # Path to CA certificate(s)
    ssl_ca_path=None,           # Path to CA directory
    ssl_cert_reqs='required',   # Certificate requirements: 'none', 'optional', 'required'
    ssl_check_hostname=False,   # Verify hostname in certificate
    ssl_password=None,          # Password for encrypted private key
    
    # Protocol
    protocol=2,                 # RESP protocol version (2 or 3)
    
    # Redis-specific
    redis_connect_func=None,    # Custom connection function
    credential_provider=None,   # AWS credential provider
)
```

## Connection Pools

Connection pools manage a pool of reusable connections.

### Default Pool

Each Redis client instance gets its own connection pool:

```python
import redis

# Each client has separate pool
r1 = redis.Redis()  # Pool 1
r2 = redis.Redis()  # Pool 2 (different from r1)

# Share pool between clients
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)  # Same pool as r1
```

### Creating Custom Pools

```python
import redis

# Basic pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50  # Default is 10
)

# Pool with authentication
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    password='secret',
    username='default'
)

# Unix socket pool
pool = redis.UnixDomainSocketConnectionPool(
    unix_socket_path='/var/run/redis/redis.sock',
    db=0,
    password='secret'
)

# TLS pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6380,
    ssl=True,
    ssl_cert_reqs='required',
    ssl_ca_certs='/path/to/ca.crt'
)

# Use pool with client
r = redis.Redis(connection_pool=pool)
```

### Pool Configuration

```python
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    
    # Pool size
    max_connections=100,        # Max connections in pool
    
    # Connection behavior
    connection_kwargs={
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True
    },
    
    # Health checks
    health_check_interval=30,   # Check every 30 seconds
    retry_on_timeout=True,
    
    # Authentication
    password='secret',
    username='default',
    
    # Database
    db=0,
    
    # Encoding
    encoding='utf-8',
    decode_responses=False
)

# Get pool statistics
print(f"Pool size: {pool.max_connections}")
print(f"Available connections: {len(pool._available_stack)}")
```

### Pool Cleanup

```python
import redis

pool = redis.ConnectionPool(host='localhost', port=6379)

# Clear all connections (useful before shutdown)
pool.reset()

# Get connection from pool
connection = pool.get_connection('_')

# Return connection to pool
pool.release_connection(connection)

# Close pool (called automatically on garbage collection)
pool.disconnect()
```

## SSL/TLS Connections

Secure connections using TLS/SSL.

### Basic TLS Connection

```python
import redis

# Enable TLS with minimal configuration
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True
)

# Using URL scheme
r = redis.from_url('rediss://redis.example.com:6380')
```

### TLS with Certificate Verification

```python
import redis

# Verify server certificate against CA
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_ca_certs='/path/to/ca-certificates.crt',
    ssl_cert_reqs='required'  # Strict verification
)

# Using connection pool
pool = redis.ConnectionPool(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_ca_certs='/path/to/ca-bundle.crt',
    ssl_cert_reqs='required'
)
r = redis.Redis(connection_pool=pool)
```

### TLS with Client Certificates (Mutual TLS)

```python
import redis

# Client certificate authentication
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_certfile='/path/to/client-cert.pem',      # Client certificate
    ssl_keyfile='/path/to/client-key.pem',        # Client private key
    ssl_ca_certs='/path/to/ca-certificates.crt',  # CA for server verification
    ssl_cert_reqs='required',
    ssl_check_hostname=True                       # Verify hostname
)

# With password-encrypted private key
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_certfile='/path/to/client-cert.pem',
    ssl_keyfile='/path/to/encrypted-key.pem',
    ssl_password='key-password',
    ssl_ca_certs='/path/to/ca-certificates.crt'
)
```

### TLS with Custom Verification

```python
import redis
import ssl

# Create custom SSL context
context = ssl.create_default_context()
context.load_verify_locations('/path/to/ca-cert.pem')
context.check_hostname = True
context.require_minimum_version = ssl.TLSVersion.TLSv1_2

# Use custom context
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl_context=context
)
```

### TLS Connection Pool

```python
import redis

pool = redis.ConnectionPool(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_ca_certs='/path/to/ca.crt',
    ssl_certfile='/path/to/client-cert.pem',
    ssl_keyfile='/path/to/client-key.pem',
    max_connections=50
)

r = redis.Redis(connection_pool=pool)
```

## Unix Socket Connections

Use Unix sockets for local connections (faster than TCP).

```python
import redis

# Unix socket connection
r = redis.Redis(
    unix_socket_path='/var/run/redis/redis.sock',
    db=0,
    password='secret'
)

# With encoding
r = redis.Redis(
    unix_socket_path='/var/run/redis/redis.sock',
    decode_responses=True
)

# Unix socket connection pool
pool = redis.UnixDomainSocketConnectionPool(
    unix_socket_path='/var/run/redis/redis.sock',
    db=0,
    password='secret',
    max_connections=50
)

r = redis.Redis(connection_pool=pool)
```

## Redis Cluster Mode

Redis Cluster provides horizontal scaling through sharding and high availability.

### Basic Cluster Connection

```python
from redis.cluster import RedisCluster

# Connect using single node for discovery
rc = RedisCluster(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Connect from URL
rc = RedisCluster.from_url('redis://localhost:6379')

# Connect with multiple startup nodes
from redis.cluster import ClusterNode

nodes = [
    ClusterNode('localhost', 6379),
    ClusterNode('localhost', 6380),
    ClusterNode('localhost', 6381)
]

rc = RedisCluster(startup_nodes=nodes, decode_responses=True)
```

### Cluster Connection Parameters

```python
from redis.cluster import RedisCluster

rc = RedisCluster(
    # Startup nodes (at least one required for cluster discovery)
    startup_nodes=[ClusterNode('localhost', 6379)],
    
    # Authentication
    password='secret',
    username='default',
    
    # Connection settings
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    
    # Cluster-specific settings
    skip_full_coverage_check=False,  # Require all slots covered
    reinitialize_steps=10,           # Reinitialize after N MOVED errors
    cluster_error_retry_attempts=3,  # Retry attempts on cluster errors
    
    # Read from replicas
    read_from_replicas=False,        # Send reads to replicas
    load_balancing_strategy=None,    # Custom load balancing strategy
    
    # Protocol
    protocol=2,                      # RESP version (2 or 3)
    
    # Encoding
    decode_responses=True,
    encoding='utf-8',
    
    # Cluster topology refresh
    retry=Retry(ExponentialBackoff(), 3),
    
    # Health checks
    health_check_interval=30
)
```

### Cluster Node Discovery

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379)

# Get all nodes in cluster
nodes = rc.get_nodes()
for node in nodes:
    print(f"{node.name}: {node.host}:{node.port} ({node.server_type})")

# Get primary nodes only
primaries = rc.get_primaries()
for primary in primaries:
    print(f"Primary: {primary.name}")

# Get replica nodes only
replicas = rc.get_replicas()
for replica in replicas:
    print(f"Replica: {replica.name}")

# Get specific node by host:port
node = rc.get_node(host='localhost', port=6379)
print(node)

# Get default node (randomly selected primary)
default_node = rc.get_default_node()
print(default_node)

# Set default node explicitly
rc.set_default_node(node)
```

### Cluster Slot Information

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379)

# Get slot to node mapping
slots = rc.nodes_cache  # Dict: slot_id -> [node_list]

# Get key's hash slot
slot = rc.keyslot(b'mykey')
print(f"Key 'mykey' maps to slot {slot}")

# Calculate which node handles a key
def get_node_for_key(rc, key):
    slot = rc.keyslot(key)
    return rc.nodes_cache[slot][0]  # First node in slot

node = get_node_for_key(rc, b'mykey')
print(f"Key handled by: {node.name}")
```

### Cluster Operations

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# Basic operations (automatically routed to correct node)
rc.set('key1', 'value1')
rc.get('key1')

# Multi-key commands require keys on same slot
# Use hash tags to force same slot
rc.mset('{user}1:name', 'Alice', '{user}1:age', '30')
rc.mget('{user}1:name', '{user}1:age')

# Non-atomic multi-key (splits across slots)
rc.mset_nonatomic('key1', 'v1', 'key2', 'v2')
rc.mget_nonatomic('key1', 'key2')

# Cluster-specific commands with target nodes
from redis.cluster import RedisCluster as RC

# Execute on all primaries
rc.ping(target_nodes=RC.PRIMARIES)

# Execute on all replicas
rc.info(target_nodes=RC.REPLICAS)

# Execute on all nodes
rc.flushdb(target_nodes=RC.ALL_NODES)

# Execute on random node
rc.ping(target_nodes=RC.RANDOM)
```

### Cluster Read from Replicas

Enable read scaling by routing reads to replicas:

```python
from redis.cluster import RedisCluster

# Round-robin reads between primary and replicas
rc = RedisCluster(
    host='localhost',
    port=6379,
    read_from_replicas=True
)

# Read commands distributed across primaries and replicas
rc.get('key')  # May go to replica
rc.set('key', 'value')  # Always goes to primary

# Custom load balancing strategy
class CustomLoadBalancer:
    def get_nodes(self, command_args, nodes_cache):
        # Custom logic for node selection
        return [primary]  # Example: always use primary

rc = RedisCluster(
    host='localhost',
    port=6379,
    load_balancing_strategy=CustomLoadBalancer()
)
```

### Cluster Error Handling

```python
from redis.cluster import RedisCluster
from redis.exceptions import (
    ClusterDownError,
    MovedError,
    AskError,
    TryAgainError,
    ClusterCrossSlotError
)

rc = RedisCluster(host='localhost', port=6379)

try:
    rc.get('key')
except ClusterDownError as e:
    # Cluster is partially or fully down
    print(f"Cluster down: {e}")
    
except MovedError as e:
    # Key moved to different node (client will redirect automatically)
    print(f"Key moved to slot {e.slot_id} at {e.host}:{e.port}")
    
except AskError as e:
    # Key being migrated, needs ASK redirection
    print(f"Ask redirection to {e.host}:{e.port}")
    
except TryAgainError as e:
    # Cluster busy, retry later
    print("Cluster busy, retrying...")
    
except ClusterCrossSlotError as e:
    # Multi-key command with keys on different slots
    print("Keys must be on same slot for this operation")
```

## Redis Sentinel

Sentinel provides high availability with automatic failover.

### Basic Sentinel Connection

```python
from redis.sentinel import Sentinel

# Connect to Sentinels
sentinel = Sentinel(
    [('localhost', 26379), ('localhost', 26380)],
    socket_timeout=0.1,
    sentinel_kwargs={'password': 'sentinel-password'}
)

# Get master connection
master = sentinel.master_for(
    'mymaster',
    db=0,
    password='redis-password',
    socket_timeout=5
)

# Get replica connection
replica = sentinel.slave_for(
    'mymaster',
    db=0,
    password='redis-password',
    socket_timeout=5
)

# Use master for writes
master.set('key', 'value')

# Use replica for reads
value = replica.get('key')
```

### Sentinel Connection Parameters

```python
from redis.sentinel import Sentinel

sentinel = Sentinel(
    # Sentinel nodes (list of (host, port) tuples)
    [('sentinel1.example.com', 26379),
     ('sentinel2.example.com', 26379),
     ('sentinel3.example.com', 26379)],
    
    # Sentinel connection settings
    socket_timeout=0.1,
    socket_connect_timeout=0.1,
    retry_on_timeout=True,
    
    # Sentinel authentication
    sentinel_kwargs={
        'password': 'sentinel-password',
        'username': 'sentinel-user'
    },
    
    # SSL for Sentinel connections
    ssl=False,
    ssl_ca_certs=None,
    
    # Discovery settings
    min_other_sentinels=0,  # Min sentinels to see master as valid
    sentinel_down_after=0,  # Time before marking sentinel down
)
```

### Getting Master and Replica Connections

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([('localhost', 26379)])

# Master connection (for writes)
master = sentinel.master_for(
    service_name='mymaster',
    db=0,
    password='redis-password',
    socket_timeout=5,
    decode_responses=True
)

# Replica connection (for reads)
replica = sentinel.slave_for(
    service_name='mymaster',
    db=0,
    password='redis-password',
    socket_timeout=5,
    decode_responses=True
)

# Read/Write pattern
master.set('key', 'value')  # Write to master
replica.get('key')          # Read from replica (eventual consistency)
```

### Sentinel Discovery

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([('localhost', 26379)])

# Discover master
master_addr = sentinel.discover_master('mymaster')
print(f"Master at: {master_addr}")  # ('127.0.0.1', 6379)

# Discover replicas
replica_addrs = sentinel.discover_slaves('mymaster')
for addr in replica_addrs:
    print(f"Replica at: {addr}")

# Get sentinel state
state = sentinel.sentinel_master('mymaster')
print(state)  # Dict with master info

# Get slave list
slaves = sentinel.sentinel_slaves('mymaster')
for slave in slaves:
    print(slave)
```

### Sentinel Failover Handling

Sentinel clients automatically detect and handle failovers:

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([('localhost', 26379)])

# Client automatically discovers new master after failover
while True:
    try:
        master = sentinel.master_for('mymaster', socket_timeout=5)
        master.set('key', 'value')
        print("Successfully wrote to master")
    except Exception as e:
        print(f"Error: {e}, will retry...")
        # Next iteration will discover new master
```

### Sentinel with SSL

```python
from redis.sentinel import Sentinel

# SSL for both Sentinel and Redis connections
sentinel = Sentinel(
    [('localhost', 26379)],
    ssl=True,
    ssl_ca_certs='/path/to/ca.crt',
    sentinel_kwargs={
        'ssl': True,
        'ssl_ca_certs': '/path/to/ca.crt'
    }
)

master = sentinel.master_for(
    'mymaster',
    ssl=True,
    ssl_ca_certs='/path/to/ca.crt'
)
```

## Async Clients

Asynchronous Redis clients using asyncio.

### Basic Async Client

```python
import redis.asyncio as redis
import asyncio

async def main():
    # Create async client
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # All operations are coroutines (await required)
    await r.set('key', 'value')
    result = await r.get('key')
    print(result)  # 'value'
    
    # Close connection when done
    await r.close()

# Run async code
asyncio.run(main())
```

### Async Client from URL

```python
import redis.asyncio as redis
import asyncio

async def main():
    # From URL
    r = await redis.from_url('redis://localhost:6379/0', decode_responses=True)
    
    await r.set('key', 'value')
    result = await r.get('key')
    
    await r.close()

asyncio.run(main())
```

### Async Connection Pool

```python
import redis.asyncio as redis

# Create async connection pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50
)

# Use pool with multiple clients
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)
```

### Async Pipelines

```python
import redis.asyncio as redis
import asyncio

async def main():
    r = redis.Redis(decode_responses=True)
    
    # Async pipeline
    async with r.pipeline() as pipe:
        await pipe.set('foo', 'bar')
        await pipe.get('foo')
        await pipe.incr('counter')
        
        results = await pipe.execute()
        print(results)  # [True, 'bar', 1]
    
    await r.close()

asyncio.run(main())
```

### Async Pub/Sub

```python
import redis.asyncio as redis
import asyncio

async def listen_for_messages():
    r = redis.Redis(decode_responses=True)
    pubsub = r.pubsub()
    
    await pubsub.subscribe('mychannel')
    
    try:
        while True:
            message = await pubsub.get_message(timeout=1.0)
            if message and message['type'] == 'message':
                print(f"Received: {message['data']}")
    finally:
        await pubsub.unsubscribe()
        await r.close()

async def publish_messages():
    r = redis.Redis(decode_responses=True)
    
    for i in range(5):
        await r.publish('mychannel', f'Message {i}')
        await asyncio.sleep(1)
    
    await r.close()

# Run both concurrently
async def main():
    listener = asyncio.create_task(listen_for_messages())
    await publish_messages()
    await asyncio.sleep(2)
    listener.cancel()

asyncio.run(main())
```

### Async Cluster Client

```python
import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
import asyncio

async def main():
    # Async cluster client
    rc = RedisCluster(
        host='localhost',
        port=6379,
        decode_responses=True
    )
    
    # All operations are async
    await rc.set('key', 'value')
    result = await rc.get('key')
    print(result)
    
    # Close when done
    await rc.close()

asyncio.run(main())
```

### Async Sentinel Client

```python
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel
import asyncio

async def main():
    # Async sentinel
    sentinel = Sentinel([('localhost', 26379)])
    
    # Get master connection
    master = await sentinel.master_for('mymaster', decode_responses=True)
    
    await master.set('key', 'value')
    result = await master.get('key')
    
    await master.close()
    await sentinel.close()

asyncio.run(main())
```

### Async Context Managers

```python
import redis.asyncio as redis
import asyncio

async def main():
    # Client as context manager (auto-closes)
    async with redis.Redis(host='localhost', port=6379) as r:
        await r.set('key', 'value')
        result = await r.get('key')
    
    # Pipeline as context manager
    async with redis.Redis() as r:
        async with r.pipeline() as pipe:
            await pipe.set('a', '1')
            await pipe.set('b', '2')
            results = await pipe.execute()

asyncio.run(main())
```

### Async Streaming (XREADGROUP)

```python
import redis.asyncio as redis
import asyncio

async def consume_stream():
    r = redis.Redis(decode_responses=True)
    
    # Create consumer group if not exists
    try:
        await r.xgroup_create('mystream', 'mygroup', id='0', mkstream=True)
    except redis.ResponseError:
        pass  # Already exists
    
    while True:
        # Read new entries (blocking)
        result = await r.xreadgroup(
            groupname='mygroup',
            consumername='consumer1',
            streams={'mystream': '>'},
            count=10,
            block=1000
        )
        
        if result:
            for stream_name, entries in result[0]:
                for entry_id, fields in entries:
                    print(f"Processing {entry_id}: {fields}")
                    
                    # Acknowledge after processing
                    await r.xack('mystream', 'mygroup', entry_id)

asyncio.run(consume_stream())
```

## Connection Health Checks

Monitor connection health automatically:

```python
import redis

# Enable health checks (every 30 seconds by default)
r = redis.Redis(
    host='localhost',
    port=6379,
    health_check_interval=30  # Seconds between checks
)

# Health check sends PING command to verify connection is alive
# Failed connections are automatically removed from pool and replaced
```

## Connection Timeouts and Retries

```python
import redis
from redis import Retry
from redis.backoff import ExponentialBackoff

# Configure timeouts and retries
r = redis.Redis(
    host='localhost',
    port=6379,
    socket_timeout=5,              # Read timeout
    socket_connect_timeout=5,      # Connection timeout
    retry_on_timeout=True,         # Retry on timeout
    
    # Custom retry strategy
    retry=Retry(ExponentialBackoff(), 3)  # 3 retries with exponential backoff
)

# Custom retry with specific errors
from redis.exceptions import BusyLoadingError, ConnectionError

retry = Retry(
    ExponentialBackoff(),
    3,
    supported_errors=(BusyLoadingError, ConnectionError)
)

r = redis.Redis(host='localhost', port=6379, retry=retry)
```
