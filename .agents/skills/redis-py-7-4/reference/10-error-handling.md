# Error Handling and Retries

Comprehensive guide to Redis exception handling, retry strategies, backoff policies, and connection error recovery.

## Exception Hierarchy

Understanding redis-py exceptions for proper error handling:

```
Exception
└── RedisError
    ├── ConnectionError (network-related)
    │   ├── AuthenticationError
    │   ├── AuthorizationError
    │   ├── BusyLoadingError
    │   └── NoPermissionError
    ├── TimeoutError
    ├── ResponseError (server errors)
    │   ├── DataError
    │   ├── InvalidResponse
    │   ├── PubSubError
    │   ├── WatchError
    │   ├── NoScriptError
    │   ├── OutOfMemoryError
    │   ├── ExecAbortError
    │   ├── ReadOnlyError
    │   └── ModuleError
    └── LockError (locking errors)
        └── LockNotOwnedError

RedisClusterException (cluster-specific)
├── ClusterError
│   └── ClusterDownError
├── AskError
├── TryAgainError
├── ClusterCrossSlotError
├── MovedError
└── MasterDownError
```

### Core Exceptions

```python
from redis.exceptions import (
    RedisError,           # Base exception for all Redis errors
    ConnectionError,      # Network connection failures
    TimeoutError,         # Operation timeout
    ResponseError,        # Server returned error response
    AuthenticationError,  # Wrong password/credentials
    AuthorizationError,   # ACL permission denied
    DataError,            # Invalid data type for command
    WatchError,           # WATCH key was modified
)

# Example: Catching specific exceptions
try:
    r.get('key')
except ConnectionError as e:
    print(f"Connection failed: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
except ResponseError as e:
    print(f"Server error: {e}")
except RedisError as e:
    # Catch-all for any Redis error
    print(f"Redis error: {e}")
```

### Connection Errors

Handle connection-related failures:

```python
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError

import redis

r = redis.Redis(host='localhost', port=6379)

try:
    r.ping()
except AuthenticationError as e:
    # Wrong password or credentials
    print(f"Authentication failed: {e}")
    # Retry with correct credentials
    
except ConnectionError as e:
    # Redis server not reachable
    print(f"Cannot connect: {e}")
    # Check server status, retry later
    
except TimeoutError as e:
    # Connection or read timeout
    print(f"Connection timed out: {e}")
    # Increase timeout or check network
```

### Response Errors

Handle Redis server errors:

```python
from redis.exceptions import ResponseError, DataError, OutOfMemoryError

import redis

r = redis.Redis()

try:
    # Command that might fail
    r.lpush('not_a_list', 'value')  # Key is string, not list
except DataError as e:
    # Wrong data type for operation
    print(f"Wrong type: {e}")
    
try:
    r.set('key', 'x' * (1024 * 1024 * 100))  # 100MB value
except OutOfMemoryError as e:
    # Redis out of memory
    print(f"Out of memory: {e}")
    
try:
    r.eval("return 1/0", 0)  # Lua script error
except ResponseError as e:
    # General server error
    print(f"Server error: {e}")
```

### Cluster Exceptions

Handle Redis Cluster-specific errors:

```python
from redis.exceptions import (
    ClusterDownError,
    MovedError,
    AskError,
    TryAgainError,
    ClusterCrossSlotError,
    MasterDownError
)

from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379)

try:
    rc.get('key')
except ClusterDownError as e:
    # Cluster is partially or fully down
    print(f"Cluster unavailable: {e}")
    
except MovedError as e:
    # Key moved to different node (client handles automatically)
    print(f"Key moved to slot {e.slot_id} at {e.host}:{e.port}")
    
except AskError as e:
    # Key being migrated, needs ASK redirection
    print(f"Ask redirection needed: {e.node_addr}")
    
except TryAgainError as e:
    # Cluster busy (resharding), retry later
    print("Cluster busy, will retry")
    
except ClusterCrossSlotError as e:
    # Multi-key command with keys on different slots
    print(f"Keys must be on same slot: {e}")
```

## Retry Strategies

### Built-in Retry Configuration

Configure retry behavior with the `Retry` class:

```python
from redis import Redis, Retry
from redis.backoff import ExponentialBackoff

# Basic retry configuration
retry = Retry(ExponentialBackoff(), 3)  # 3 retries with exponential backoff

r = Redis(
    host='localhost',
    port=6379,
    retry=retry
)

# Retry with custom errors to handle
from redis.exceptions import BusyLoadingError, ConnectionError

retry = Retry(
    ExponentialBackoff(),
    3,
    supported_errors=(BusyLoadingError, ConnectionError)
)

r = Redis(host='localhost', port=6379, retry=retry)
```

### Retry on Specific Errors

Configure which errors trigger retries:

```python
from redis import Redis, Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError

# Default: retries on ConnectionError and TimeoutError
retry = Retry(ExponentialBackoff(), 3)

# Custom: also retry on BusyLoadingError
retry = Retry(
    ExponentialBackoff(),
    3,
    supported_errors=(ConnectionError, TimeoutError, BusyLoadingError)
)

r = Redis(host='localhost', port=6379, retry=retry)

# Additional errors to retry on (beyond Retry's supported_errors)
r = Redis(
    host='localhost',
    port=6379,
    retry=retry,
    retry_on_error=[BusyLoadingError]  # Additional errors
)
```

### Cluster Retry Configuration

Cluster-specific retry settings:

```python
from redis.cluster import RedisCluster
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

# Cluster retry configuration
retry = Retry(ExponentialBackoff(), 6)

rc = RedisCluster(
    host='localhost',
    port=6379,
    retry=retry
    # cluster_error_retry_attempts is deprecated when retry is provided
)

# Cluster retries on:
# - TimeoutError
# - ConnectionError
# - ClusterDownError
# - SlotNotCoveredError
```

## Backoff Strategies

### No Backoff

Retry immediately without delay:

```python
from redis.backoff import NoBackoff
from redis.retry import Retry

retry = Retry(NoBackoff(), 3)  # 3 immediate retries

r = Redis(host='localhost', port=6379, retry=retry)
```

### Constant Backoff

Fixed delay between retries:

```python
from redis.backoff import ConstantBackoff
from redis.retry import Retry

# Wait 1 second between each retry
retry = Retry(ConstantBackoff(1), 5)  # 5 retries, 1 second apart

r = Redis(host='localhost', port=6379, retry=retry)
```

### Exponential Backoff

Exponentially increasing delays:

```python
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

# Base delay doubles each retry: 1s, 2s, 4s, 8s...
backoff = ExponentialBackoff(base=1, cap=60)  # Cap at 60 seconds

retry = Retry(backoff, 5)

r = Redis(host='localhost', port=6379, retry=retry)
```

### Exponential Backoff with Jitter (Recommended)

Prevents thundering herd with randomized delays:

```python
from redis.backoff import ExponentialWithJitterBackoff
from redis.retry import Retry

# Default backoff used by redis-py
backoff = ExponentialWithJitterBackoff(base=1, cap=10)

retry = Retry(backoff, 3)

r = Redis(host='localhost', port=6379, retry=retry)

# Delays are randomized between [base * 2^attempt, min(cap, base * 2^(attempt+1))]
```

### Custom Backoff Strategy

Implement custom backoff logic:

```python
from redis.backoff import Backoff
from redis.retry import Retry
import random

class LinearBackoff(Backoff):
    """Linearly increasing backoff."""
    
    def __init__(self, step=1, cap=30):
        self.step = step
        self.cap = cap
    
    def __call__(self, attempt):
        # delay = min(step * attempt, cap)
        return min(self.step * (attempt + 1), self.cap)

backoff = LinearBackoff(step=2, cap=30)  # 2s, 4s, 6s... capped at 30s
retry = Retry(backoff, 5)

r = Redis(host='localhost', port=6379, retry=retry)
```

## Manual Retry Implementation

### Simple Retry Loop

Manual retry with basic backoff:

```python
import redis
import time
from redis.exceptions import ConnectionError, TimeoutError

def get_with_retry(r, key, max_retries=3):
    """Get value with retry on connection errors."""
    for attempt in range(max_retries):
        try:
            return r.get(key)
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise  # Re-raise on last attempt
            
            # Exponential backoff
            delay = 2 ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            time.sleep(delay)

# Usage
r = redis.Redis(host='localhost', port=6379)
value = get_with_retry(r, 'mykey')
```

### Retry with Circuit Breaker

Prevent cascading failures:

```python
import redis
import time
from redis.exceptions import ConnectionError, TimeoutError

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def can_execute(self):
        """Check if operation is allowed."""
        if self.state == 'closed':
            return True
        
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
                return True
            return False
        
        return True  # half-open allows one test request
    
    def record_success(self):
        """Record successful operation."""
        self.failures = 0
        self.state = 'closed'
    
    def record_failure(self):
        """Record failed operation."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = 'open'

# Usage
cb = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
r = redis.Redis(host='localhost', port=6379)

def safe_redis_operation(operation, *args, **kwargs):
    """Execute Redis operation with circuit breaker."""
    if not cb.can_execute():
        raise Exception("Circuit breaker open, service unavailable")
    
    try:
        result = operation(*args, **kwargs)
        cb.record_success()
        return result
    except (ConnectionError, TimeoutError):
        cb.record_failure()
        raise

# Usage
try:
    value = safe_redis_operation(r.get, 'mykey')
except Exception as e:
    print(f"Operation failed: {e}")
```

### Retry with Fallback

Provide fallback when retries exhausted:

```python
import redis
import time
from redis.exceptions import ConnectionError, TimeoutError

def get_with_fallback(r, key, fallback_value=None, max_retries=3):
    """Get value with retry and fallback."""
    for attempt in range(max_retries):
        try:
            return r.get(key)
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                print(f"All retries exhausted, using fallback: {e}")
                return fallback_value
            
            delay = 2 ** attempt
            time.sleep(delay)
    
    return fallback_value

# Usage with cache fallback
r = redis.Redis(host='localhost', port=6379)
value = get_with_fallback(r, 'mykey', fallback_value=b'default-value')

# Usage with database fallback
def get_from_db(key):
    """Fallback to database if Redis unavailable."""
    return db.query(f"SELECT value FROM cache WHERE key = {key}")

value = get_with_fallback(r, 'mykey', fallback_value=get_from_db('mykey'))
```

## Connection Error Recovery

### Automatic Reconnection

redis-py automatically reconnects on connection errors:

```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    socket_timeout=5,
    retry_on_timeout=True  # Automatically retry on timeout
)

# Connection errors trigger automatic reconnection
try:
    r.get('key')
except redis.ConnectionError as e:
    # Only raised after all retries exhausted
    print(f"Failed after retries: {e}")
```

### Health Checks

Enable connection health monitoring:

```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    health_check_interval=30,  # Check every 30 seconds
    socket_timeout=5
)

# Connection pool sends PING to verify connections are alive
# Dead connections are automatically removed and replaced
```

### Connection Pool Recovery

Pool recovers from individual connection failures:

```python
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10,
    health_check_interval=30
)

r = redis.Redis(connection_pool=pool)

# If a connection fails, it's removed from pool
# New connection created on next request
try:
    r.get('key')
except redis.ConnectionError:
    # Connection will be recreated automatically
    pass

# Next operation uses fresh connection
result = r.get('key')  # Works with new connection
```

## Timeout Configuration

### Socket Timeouts

Configure connection and read timeouts:

```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    
    # Time to establish connection
    socket_connect_timeout=5,  # 5 seconds
    
    # Time to wait for response
    socket_timeout=5,          # 5 seconds
    
    # Retry on timeout errors
    retry_on_timeout=True
)
```

### Command-Specific Timeouts

Some commands support timeout parameters:

```python
import redis

r = redis.Redis()

# Blocking operations with timeout
result = r.blpop('mylist', timeout=5)  # Wait up to 5 seconds
result = r.brpop('mylist', timeout=10)
result = r.bzpopmin('zset', timeout=30)

# PubSub with timeout
pubsub = r.pubsub()
pubsub.subscribe('channel')
message = pubsub.get_message(timeout=5)  # None if no message in 5s

# Lock acquisition with timeout
lock = r.lock('mylock', blocking=True, blocking_timeout=10)
acquired = lock.acquire()  # Wait up to 10 seconds
```

### Handling Timeouts

Properly handle timeout exceptions:

```python
import redis
from redis.exceptions import TimeoutError

r = redis.Redis(socket_timeout=5)

try:
    result = r.blpop('mylist', timeout=30)
except TimeoutError as e:
    # Operation timed out (not connection timeout)
    print(f"Operation timed out: {e}")
    
# Connection timeout
try:
    r.get('key')
except TimeoutError as e:
    # Socket read/write timeout
    print(f"Connection timeout: {e}")
```

## Error Handling Best Practices

### Specific Exception Handling

Catch specific exceptions before general ones:

```python
import redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    ResponseError,
    RedisError
)

r = redis.Redis()

try:
    r.get('key')
except AuthenticationError as e:
    # Handle auth errors first (most specific)
    logger.error(f"Authentication failed: {e}")
    refresh_credentials()
    
except ConnectionError as e:
    # Network issues
    logger.warning(f"Connection error: {e}")
    retry_with_backoff()
    
except TimeoutError as e:
    # Timeout handling
    logger.warning(f"Timeout: {e}")
    increase_timeout()
    
except ResponseError as e:
    # Redis server errors
    logger.error(f"Redis error: {e}")
    handle_server_error(e)
    
except RedisError as e:
    # Catch-all for any other Redis error
    logger.error(f"Unexpected Redis error: {e}")
    raise
```

### Logging Errors

Log errors with context:

```python
import redis
import logging
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

r = redis.Redis()

def safe_operation(operation_name, func, *args, **kwargs):
    """Execute operation with error logging."""
    try:
        return func(*args, **kwargs)
    except RedisError as e:
        logger.error(
            f"{operation_name} failed",
            extra={
                'error_type': type(e).__name__,
                'error_message': str(e),
                'operation': operation_name,
                'args': args,
                'kwargs': kwargs
            }
        )
        raise

# Usage
try:
    result = safe_operation('GET', r.get, 'mykey')
except RedisError:
    # Error already logged
    handle_failure()
```

### Graceful Degradation

Provide fallback behavior on errors:

```python
import redis
from redis.exceptions import RedisError

class CacheWithFallback:
    def __init__(self, redis_client):
        self.r = redis_client
    
    def get(self, key, default=None):
        """Get from cache with graceful fallback."""
        try:
            value = self.r.get(key)
            return value if value is not None else default
        except RedisError as e:
            logger.warning(f"Cache miss due to error: {e}")
            return default
    
    def set(self, key, value, ex=None):
        """Set in cache, ignore errors."""
        try:
            self.r.set(key, value, ex=ex)
        except RedisError as e:
            logger.warning(f"Cache write failed: {e}")
            # Don't raise - operation can continue without cache

# Usage
cache = CacheWithFallback(redis.Redis())

user_data = cache.get(f'user:{user_id}', default={})
if not user_data:
    user_data = fetch_from_database(user_id)
    cache.set(f'user:{user_id}', serialize(user_data), ex=3600)
```

### Retry Only Idempotent Operations

Only retry operations that are safe to repeat:

```python
import redis
from redis.exceptions import ConnectionError

r = redis.Redis()

# Safe to retry (idempotent)
def safe_get(key):
    for attempt in range(3):
        try:
            return r.get(key)
        except ConnectionError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

# NOT safe to retry without care (non-idempotent)
def unsafe_incr(key):
    # INCR is not idempotent - retrying changes result!
    try:
        return r.incr(key)
    except ConnectionError:
        # Need special handling - check current value first
        current = r.get(key)
        if current is None:
            raise  # Can't determine if increment succeeded
        return int(current)
```

## Monitoring and Alerting

### Track Error Rates

Monitor Redis error rates:

```python
import redis
from redis.exceptions import RedisError
from collections import defaultdict
import time

class ErrorTracker:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.errors = defaultdict(list)  # error_type -> [timestamps]
    
    def record(self, error):
        """Record error with timestamp."""
        self.errors[type(error).__name__].append(time.time())
        self._cleanup_old()
    
    def _cleanup_old(self):
        """Remove errors outside window."""
        cutoff = time.time() - self.window_size
        for error_type in self.errors:
            self.errors[error_type] = [
                ts for ts in self.errors[error_type] if ts > cutoff
            ]
    
    def get_rate(self, error_type=None):
        """Get error rate per second."""
        if error_type:
            return len(self.errors[error_type]) / self.window_size
        else:
            total = sum(len(errors) for errors in self.errors.values())
            return total / self.window_size

# Usage
tracker = ErrorTracker()
r = redis.Redis()

try:
    r.get('key')
except RedisError as e:
    tracker.record(e)
    if tracker.get_rate() > 0.1:  # More than 0.1 errors/sec
        alert("High Redis error rate")
```

### Connection Pool Metrics

Monitor connection pool health:

```python
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=50)
r = redis.Redis(connection_pool=pool)

# Monitor pool usage
def get_pool_stats(pool):
    """Get connection pool statistics."""
    return {
        'max_connections': pool.max_connections,
        'available': len(pool._available_stack),
        'in_use': pool.max_connections - len(pool._available_stack),
        'usage_percent': (1 - len(pool._available_stack) / pool.max_connections) * 100
    }

stats = get_pool_stats(pool)
if stats['usage_percent'] > 90:
    alert("Connection pool nearly exhausted")
```
