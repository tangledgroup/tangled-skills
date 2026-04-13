# RESP3 Protocol Features

RESP3 (Redis Serialization Protocol version 3) provides improved performance, new data types, push notifications, and client-side caching.

## Enabling RESP3

Enable RESP3 by setting `protocol=3` in connection parameters:

```python
import redis

# Sync client with RESP3
r = redis.Redis(host='localhost', port=6379, protocol=3)
r.ping()  # Returns PONG with type information

# From URL
r = redis.from_url('redis://localhost:6379?protocol=3')

# Async client with RESP3
import redis.asyncio as redis

r = redis.Redis(host='localhost', port=6379, protocol=3)
await r.ping()

# Cluster with RESP3
from redis.cluster import RedisCluster

rc = RedisCluster(
    host='localhost',
    port=6379,
    protocol=3  # Enable RESP3 for cluster
)

# Sentinel with RESP3
from redis.sentinel import Sentinel

sentinel = Sentinel([('localhost', 26379)])
master = sentinel.master_for('mymaster', protocol=3)
```

## RESP3 Response Types

RESP3 preserves data types instead of converting everything to strings/bytes.

### Native Python Types

With RESP3, Redis responses map directly to Python types:

```python
import redis

r = redis.Redis(protocol=3, decode_responses=True)

# Boolean responses
r.set('key', 'value')  # True (not b'OK')
r.exists('nonexistent')  # 0

# Float responses
r.incrbyfloat('counter', 1.5)  # 1.5 (float, not b'1.5')

# Null responses
r.get('nonexistent')  # None (not False or empty bytes)

# Map responses (from HGETALL)
r.hset('user', 'name', 'Alice', 'age', '30')
result = r.hgetall('user')  # {'name': 'Alice', 'age': '30'} (dict, not list)

# Array of mixed types
r.mget('string_key', 'numeric_key', 'nonexistent')
# ['value', 42, None] (preserved types)
```

### Type Preservation Examples

```python
import redis

r = redis.Redis(protocol=3)

# HASH commands return dicts instead of flat lists
r.hset('user:1', mapping={'name': 'Alice', 'age': '30'})
result = r.hgetall('user:1')
print(type(result))  # <class 'dict'> (RESP2 would be list)

# MGET returns proper None for missing keys
result = r.mget(['exists', 'missing'])
print(result)  # [b'value', None]

# INCRBYFLOAT returns float
r.set('float_key', '0')
result = r.incrbyfloat('float_key', 1.5)
print(type(result))  # <class 'int'> or <class 'float'>

# XREAD returns structured data
r.xadd('mystream', {'field': 'value'})
result = r.xread({'mystream': '0'})
print(type(result[0][1][0]))  # Tuple of (entry_id, dict)
```

### Comparison: RESP2 vs RESP3

```python
import redis

# RESP2 client
r2 = redis.Redis(protocol=2)
r2.hset('user', 'name', 'Alice')
result2 = r2.hgetall('user')
print(result2)  # [b'name', b'Alice'] (flat list)

# RESP3 client
r3 = redis.Redis(protocol=3)
r3.hset('user', 'name', 'Alice')
result3 = r3.hgetall('user')
print(result3)  # {b'name': b'Alice'} (dict)

# Type checking in RESP3
print(type(result3))  # <class 'dict'>
print(isinstance(result3, dict))  # True
```

## Push Notifications

RESP3 supports push notifications for server-initiated messages.

### Default Push Handler

By default, push notifications are logged:

```python
import redis

r = redis.Redis(protocol=3)

# Server sends push notification (e.g., from CLIENT TRACKING)
# Default handler logs the message
r.ping()  # May trigger push if tracking enabled
```

### Custom Push Handler

Register custom function to handle push notifications:

```python
import redis

def my_push_handler(message):
    """Custom push notification handler."""
    print(f"Push received: {message}")
    
    # Handle different push types
    if message.get('type') == 'invalidate':
        # Client-side cache invalidation
        keys = message.get('keys', [])
        print(f"Cache invalidated for keys: {keys}")
        
    elif message.get('type') == 'message':
        # Server message
        print(f"Server message: {message.get('data')}")

# Create connection with custom handler
r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    push_handler_func=my_push_handler
)

# Or set on existing client
r.push_handler_func = my_push_handler
```

### Push Notification Types

Common push notification types:

```python
import redis

def comprehensive_push_handler(message):
    """Handle all push notification types."""
    
    msg_type = message.get('type')
    
    if msg_type == 'invalidate':
        # Client-side caching invalidation
        # Keys that were invalidated
        keys = message.get('keys', [])
        handle_cache_invalidation(keys)
        
    elif msg_type == 'message':
        # Generic server message
        data = message.get('data')
        log_server_message(data)
        
    elif msg_type == 'disconnected':
        # Connection disconnected
        reconnect()
        
    else:
        # Unknown push type
        print(f"Unknown push type: {msg_type}, data: {message}")

r = redis.Redis(protocol=3, push_handler_func=comprehensive_push_handler)
```

### PubSub with Push Handler

PubSub messages can use push notifications:

```python
import redis

def pubsub_push_handler(message):
    """Handle PubSub messages via push notifications."""
    if message.get('type') == 'message':
        channel = message.get('channel')
        data = message.get('data')
        print(f"Message on {channel}: {data}")

r = redis.Redis(protocol=3, push_handler_func=pubsub_push_handler)
pubsub = r.pubsub()
pubsub.subscribe('mychannel')

# Messages may arrive via push notifications instead of get_message()
```

## Client-Side Caching (CSC)

Client-side caching allows Redis to notify clients when cached values become stale.

### Basic CSC Usage

Enable client-side caching with default configuration:

```python
import redis
from redis.cache import CacheConfig

r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,  # RESP3 required
    cache_config=CacheConfig()
)

# Use client normally - caching is automatic
r.set('key', 'value')
result1 = r.get('key')  # Stored in client cache
result2 = r.get('key')  # Retrieved from client cache (faster)

# Server invalidates cache when key changes
r.set('key', 'new_value')  # Client cache invalidated
result3 = r.get('key')     # Fetched from server, re-cached
```

### Cache Configuration

Configure cache behavior:

```python
import redis
from redis.cache import CacheConfig, EvictionPolicy

config = CacheConfig(
    # Cache size limit (number of keys)
    max_entries=10000,
    
    # Eviction policy when cache is full
    eviction_policy=EvictionPolicy.LRU,  # LRU, LFU, FIFO
    
    # TTL for cached entries (seconds, 0 = use server TTL)
    ttl=300,
    
    # Negative caching (cache miss results)
    negative_cache_ttl=60,
    
    # Track all keys or only explicitly requested
    track_all_keys=False,
)

r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    cache_config=config
)
```

### Custom Cache Implementation

Implement custom cache backend:

```python
import redis
from redis.cache import CacheInterface, CacheEntry

class CustomCache(CacheInterface):
    """Custom cache implementation."""
    
    def __init__(self, max_entries=10000):
        self.max_entries = max_entries
        self.cache = {}
        self.access_order = []
        
    def get(self, key):
        """Get entry from cache."""
        if key in self.cache:
            # Update access order (for LRU)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
        
    def put(self, key, value, ttl=None):
        """Add entry to cache."""
        if key in self.cache:
            self.access_order.remove(key)
            
        # Evict if at capacity
        while len(self.cache) >= self.max_entries and self.access_order:
            lru_key = self.access_order.pop(0)
            self.cache.pop(lru_key, None)
            
        self.cache[key] = CacheEntry(value=value, ttl=ttl)
        self.access_order.append(key)
        
    def delete(self, key):
        """Remove entry from cache."""
        self.cache.pop(key, None)
        if key in self.access_order:
            self.access_order.remove(key)
            
    def clear(self):
        """Clear entire cache."""
        self.cache.clear()
        self.access_order.clear()

# Use custom cache
r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    cache=CustomCache(max_entries=5000)
)
```

### Cache Statistics

Monitor cache performance:

```python
import redis
from redis.cache import CacheConfig

r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    cache_config=CacheConfig()
)

# Perform operations
for i in range(100):
    r.get(f'key:{i}')

# Get cache from client
cache = r.connection_pool.cache

if cache:
    print(f"Cache size: {len(cache)}")
    print(f"Max entries: {cache.max_entries}")
    
    # Note: Cache implementation details vary by version
```

### CSC with Cluster and Sentinel

Client-side caching works with cluster and sentinel:

```python
import redis
from redis.cache import CacheConfig
from redis.cluster import RedisCluster

# Cluster with CSC
rc = RedisCluster(
    host='localhost',
    port=6379,
    protocol=3,
    cache_config=CacheConfig()
)

# Sentinel with CSC
from redis.sentinel import Sentinel

sentinel = Sentinel([('localhost', 26379)])
master = sentinel.master_for(
    'mymaster',
    protocol=3,
    cache_config=CacheConfig()
)
```

### Cache Invalidation

Redis server automatically invalidates cached entries:

```python
import redis
from redis.cache import CacheConfig

r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    cache_config=CacheConfig()
)

# Set and cache value
r.set('key', 'value1')
result1 = r.get('key')  # Cached

# Modify on server (invalidates client cache)
r.set('key', 'value2')

# Next read fetches from server (cache was invalidated)
result2 = r.get('key')  # 'value2' (from server)

# Delete also invalidates
r.delete('key')
result3 = r.get('key')  # None (from server, cache invalidated)
```

### CSC Limitations

- **RESP3 required**: Must use `protocol=3`
- **Single connection**: Cache is per-connection, not shared across clients
- **Server support**: Requires Redis 6.0+ with CLIENT TRACKING support
- **Sync only**: Currently only supported in synchronous clients (not async)
- **Key tracking overhead**: Server must track which keys each client accesses

## RESP3 Performance Benefits

### Reduced Parsing Overhead

RESP3 reduces type conversion overhead:

```python
import redis
import time

# RESP2 - everything is bytes, requires parsing
r2 = redis.Redis(protocol=2)
start = time.time()
for i in range(1000):
    result = r2.hgetall('user')  # Returns list, must convert to dict
resp2_time = time.time() - start

# RESP3 - native types, no conversion needed
r3 = redis.Redis(protocol=3)
start = time.time()
for i in range(1000):
    result = r3.hgetall('user')  # Returns dict directly
resp3_time = time.time() - start

print(f"RESP2: {resp2_time:.4f}s")
print(f"RESP3: {resp3_time:.4f}s")
print(f"Speedup: {resp2_time/resp3_time:.2f}x")
```

### Memory Efficiency

RESP3 can reduce memory usage by avoiding intermediate representations:

```python
import redis

# RESP2 creates intermediate byte strings
r2 = redis.Redis(protocol=2)
result2 = r2.mget(['key1', 'key2', 'key3'])
# [b'value1', b'value2', None] - all bytes except None

# RESP3 preserves types directly
r3 = redis.Redis(protocol=3)
result3 = r3.mget(['key1', 'key2', 'key3'])
# May preserve original types without conversion
```

## Migration from RESP2 to RESP3

### Code Compatibility

Most code works with both protocols. Key differences:

```python
import redis

# Hash commands return different types
r2 = redis.Redis(protocol=2)
r3 = redis.Redis(protocol=3)

r2.hset('user', 'name', 'Alice')
r3.hset('user', 'name', 'Alice')

resp2_result = r2.hgetall('user')  # [b'name', b'Alice'] (list)
resp3_result = r3.hgetall('user')  # {b'name': b'Alice'} (dict)

# If your code expects list, update to handle dict:
# Old: for i in range(0, len(result), 2): key, value = result[i], result[i+1]
# New: for key, value in result.items(): ...

# Check type before processing
result = r.hgetall('user')
if isinstance(result, dict):
    # RESP3
    name = result.get(b'name')
else:
    # RESP2
    name = result[result.index(b'name') + 1] if b'name' in result else None
```

### Gradual Migration Strategy

```python
import redis

# 1. Test with RESP3 in development
r = redis.Redis(protocol=3)

# 2. Update type expectations
def get_user_data(r):
    result = r.hgetall('user:1')
    
    # Handle both RESP2 and RESP3
    if isinstance(result, list):
        # RESP2 format
        return dict(zip(result[::2], result[1::2]))
    else:
        # RESP3 format (already a dict)
        return result

# 3. Monitor for type-related errors
# 4. Roll out to production when confident
```

### Type-Safe Code for RESP3

Write code that works optimally with RESP3:

```python
import redis
from typing import Dict, Optional, List, Union

r = redis.Redis(protocol=3, decode_responses=True)

def get_user(r: redis.Redis, user_id: str) -> Dict[str, any]:
    """Get user data - expects dict return from hgetall."""
    result = r.hgetall(f'user:{user_id}')
    
    # With RESP3, result is already a dict
    if isinstance(result, dict):
        return result
    else:
        # Fallback for RESP2
        return dict(zip(result[::2], result[1::2]))

def get_multiple_keys(r: redis.Redis, keys: List[str]) -> List[Optional[str]]:
    """Get multiple keys - handles None properly."""
    results = r.mget(keys)
    
    # With RESP3, missing keys are None (not False or empty bytes)
    return [str(val) if val is not None else None for val in results]

def increment_float(r: redis.Redis, key: str, amount: float) -> float:
    """Increment float - returns actual float type."""
    result = r.incrbyfloat(key, amount)
    
    # With RESP3, result is already a float
    if isinstance(result, (int, float)):
        return float(result)
    else:
        # Fallback for RESP2 (bytes)
        return float(result)
```

## Debugging RESP3 Issues

### Check Protocol Version

Verify which protocol is being used:

```python
import redis

r = redis.Redis(host='localhost', port=6379, protocol=3)

# Check connection info
info = r.info('client')
print(info)

# Test response types
r.set('test', 'value')
result = r.hgetall('nonexistent')
print(f"Empty hash type: {type(result)}")  # Should be <class 'dict'>

# If you get list instead of dict, RESP3 not enabled
```

### Response Type Inspection

Inspect response types to verify RESP3 behavior:

```python
import redis

r = redis.Redis(protocol=3)

# Test various commands and check return types
tests = [
    ('set', lambda: r.set('key', 'value')),
    ('get', lambda: r.get('key')),
    ('hgetall', lambda: r.hgetall('hash')),
    ('mget', lambda: r.mget(['key', 'missing'])),
    ('incrbyfloat', lambda: r.incrbyfloat('float_key', 1.5)),
]

for name, func in tests:
    result = func()
    print(f"{name}: {type(result).__name__} = {result}")
```

### Fallback Handling

Handle servers that don't support RESP3:

```python
import redis
from redis.exceptions import ResponseError

def create_client_with_fallback(host, port):
    """Try RESP3, fall back to RESP2 if not supported."""
    
    # Try RESP3 first
    try:
        r = redis.Redis(host=host, port=port, protocol=3)
        r.ping()
        
        # Verify RESP3 is working
        r.hset('test', 'key', 'value')
        result = r.hgetall('test')
        
        if isinstance(result, dict):
            print("Using RESP3")
            return r
        else:
            print("RESP3 not supported, falling back to RESP2")
            
    except ResponseError as e:
        print(f"RESP3 error: {e}, falling back to RESP2")
    
    # Fall back to RESP2
    r = redis.Redis(host=host, port=port, protocol=2)
    print("Using RESP2")
    return r

r = create_client_with_fallback('localhost', 6379)
```

## Best Practices

### When to Use RESP3

**Use RESP3 when:**
- Running Redis 6.0+ (for full feature support)
- Need better performance for hash/map operations
- Want client-side caching capabilities
- Need push notifications for cache invalidation
- Building new applications (no legacy concerns)

**Stick with RESP2 when:**
- Supporting older Redis versions (< 6.0)
- Code heavily depends on specific response types
- Can't modify type-handling code
- Running in restricted environments

### Performance Monitoring

```python
import redis
from redis.cache import CacheConfig
import time

r = redis.Redis(
    host='localhost',
    port=6379,
    protocol=3,
    cache_config=CacheConfig()
)

# Benchmark with caching
keys = [f'key:{i}' for i in range(100)]

# Populate data
for key in keys:
    r.set(key, f'value:{key}')

# First pass (cache cold)
start = time.time()
for key in keys:
    r.get(key)
cold_time = time.time() - start

# Second pass (cache warm)
start = time.time()
for key in keys:
    r.get(key)
warm_time = time.time() - start

print(f"Cold cache: {cold_time:.4f}s")
print(f"Warm cache: {warm_time:.4f}s")
print(f"Cache speedup: {cold_time/warm_time:.2f}x")
```
