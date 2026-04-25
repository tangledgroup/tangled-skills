# Distributed Locking

redis-py provides distributed locking primitives using Redis for coordination across multiple processes or machines.

## Basic Lock Usage

### Creating and Acquiring Locks

```python
import redis
from redis.lock import Lock

r = redis.Redis()

# Create lock (not acquired yet)
lock = r.lock('mylock', timeout=10, blocking=True, blocking_timeout=5)

# Acquire lock
acquired = lock.acquire()
if acquired:
    try:
        # Critical section
        print("Lock acquired, doing work...")
    finally:
        lock.release()

# Or use context manager (recommended)
with r.lock('mylock', timeout=10, blocking=True) as lock:
    # Lock automatically acquired on entry, released on exit
    print("In critical section")
    # Do work here
# Lock automatically released here, even if exception occurs
```

### Lock Parameters

```python
import redis

r = redis.Redis()

lock = r.lock(
    'resource_name',           # Lock key name
    
    # Timeout settings
    timeout=10,                # Lock expiration in seconds (prevents deadlocks)
    blocking=False,            # Block until lock acquired?
    blocking_timeout=5,        # Max time to wait for lock (if blocking=True)
    
    # Lock identification
    lock_class=None,           # Custom lock class
    threading_local=True,      # Thread-local lock state
    
    # Redis connection
    blocking_step=0.1,         # Wait interval when blocking (seconds)
)

# Acquire with custom timeout
acquired = lock.acquire(timeout=30)  # Override default timeout
```

### Lock Context Manager

Context managers ensure locks are always released:

```python
import redis

r = redis.Redis()

# Basic context manager usage
with r.lock('mylock', timeout=10) as lock:
    # Lock acquired
    do_critical_work()
# Lock automatically released

# Even with exceptions, lock is released
try:
    with r.lock('mylock', timeout=10) as lock:
        do_work()
        raise ValueError("Something went wrong!")
except ValueError:
    pass
# Lock still released properly
```

## Lock Timeout and Renewal

### Automatic Timeout

Locks automatically expire to prevent deadlocks:

```python
import redis
import time

r = redis.Redis()

# Lock with 5 second timeout
with r.lock('mylock', timeout=5) as lock:
    print("Lock acquired")
    time.sleep(10)  # Sleep longer than timeout
    
# After 5 seconds, lock expires automatically
# Even if code is still running, other processes can acquire lock

# Check if lock is still held
with r.lock('mylock', timeout=5) as lock2:
    print("Second lock acquired (first one expired)")
```

### Lock Extension (Watchdog)

Extend lock automatically while holding it:

```python
import redis
from redis.lock import Lock

r = redis.Redis()

# Lock with automatic renewal (lock extends itself while held)
with r.lock(
    'mylock',
    timeout=10,           # Initial timeout
    blocking=True,
    thread_local=False     # Enable watchdog
) as lock:
    # Lock will automatically renew every timeout/3 seconds
    # As long as the owning thread is still running
    
    import time
    time.sleep(30)  # Lock extended automatically during sleep
    
print("Lock released (thread completed)")
```

### Manual Extension

Manually extend lock lifetime:

```python
import redis
import time

r = redis.Redis()

lock = r.lock('mylock', timeout=10)
lock.acquire()

try:
    # Do work for a while
    time.sleep(5)
    
    # Extend lock before it expires
    lock.extend()  # Extends by original timeout (10 seconds)
    
    time.sleep(5)
    lock.extend()  # Extend again
    
    time.sleep(5)
    # Lock still valid
    
finally:
    lock.release()
```

## Blocking and Non-Blocking Locks

### Non-Blocking Lock (Default)

Returns immediately whether acquired or not:

```python
import redis

r = redis.Redis()

# Try to acquire, don't wait
lock = r.lock('mylock', timeout=10, blocking=False)
acquired = lock.acquire()

if acquired:
    try:
        print("Lock acquired, doing work")
        do_work()
    finally:
        lock.release()
else:
    print("Could not acquire lock, doing alternative work")
    do_alternative_work()
```

### Blocking Lock

Wait until lock is available:

```python
import redis

r = redis.Redis()

# Wait up to 30 seconds for lock
lock = r.lock(
    'mylock',
    timeout=10,              # Lock expires after 10 seconds
    blocking=True,           # Block until acquired
    blocking_timeout=30,     # Wait up to 30 seconds
    blocking_step=0.5        # Check every 0.5 seconds
)

acquired = lock.acquire()
if acquired:
    try:
        print("Lock acquired after waiting")
        do_work()
    finally:
        lock.release()
else:
    print("Timeout waiting for lock")
```

### Context Manager with Blocking

```python
import redis

r = redis.Redis()

# Automatically wait for lock (up to blocking_timeout)
with r.lock('mylock', timeout=10, blocking=True, blocking_timeout=30) as lock:
    # Either acquired immediately or waited up to 30 seconds
    do_critical_work()

# If blocking_timeout expires, LockError is raised
```

## Fair Lock

FairLock ensures FIFO ordering (first come, first served):

```python
import redis
from redis.lock import FairLock

r = redis.Redis()

# Use FairLock instead of regular Lock
with r.lock('resource', lock_class=FairLock, timeout=10) as lock:
    # Locks are granted in order of request
    do_work_in_order()

# FairLock prevents lock starvation
# But has higher overhead than regular Lock
```

### FairLock vs Regular Lock

| Feature | Regular Lock | FairLock |
|---------|--------------|----------|
| Ordering | First to race wins | FIFO queue |
| Performance | Faster | Slower (queue management) |
| Starvation | Possible | Prevented |
| Use Case | General purpose | High contention, fairness critical |

## Lock Error Handling

### LockNotOwnedError

Raised when trying to release a lock owned by another client:

```python
import redis
from redis.lock import LockNotOwnedError

r = redis.Redis()

lock = r.lock('mylock', timeout=2)
lock.acquire()

try:
    import time
    time.sleep(3)  # Wait for lock to expire
    
    lock.release()  # Raises LockNotOwnedError
except LockNotOwnedError:
    print("Lock was not owned (expired or released by another)")
```

### LockError

General lock errors:

```python
import redis
from redis.lock import LockError

r = redis.Redis()

try:
    with r.lock('mylock', timeout=10, blocking=True, blocking_timeout=5) as lock:
        do_work()
except LockError as e:
    print(f"Lock error: {e}")
    # Could be timeout, connection error, etc.
```

### Retry Logic with Locks

Implement retry for lock acquisition:

```python
import redis
import time
from redis.lock import LockError

r = redis.Redis()

def acquire_with_retry(key, max_attempts=5, retry_delay=1):
    """Try to acquire lock with retries."""
    for attempt in range(max_attempts):
        try:
            lock = r.lock(key, timeout=30, blocking=True, blocking_timeout=5)
            if lock.acquire():
                return lock
        except LockError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    
    raise LockError(f"Failed to acquire lock after {max_attempts} attempts")

# Usage
try:
    with acquire_with_retry('critical_resource') as lock:
        do_critical_work()
except LockError:
    handle_failure()
```

## RedLock Algorithm

RedLock is a distributed locking algorithm for high availability across multiple Redis instances.

### Basic RedLock Usage

```python
import redis
from redis.lock import RedLock

# Connect to multiple Redis instances
clients = [
    redis.Redis(host='redis1.example.com', port=6379),
    redis.Redis(host='redis2.example.com', port=6379),
    redis.Redis(host='redis3.example.com', port=6379),
]

# Create RedLock (requires majority of instances)
lock = RedLock(
    clients,
    'resource_name',
    lock_timeout=10000,        # Lock timeout in milliseconds
    retry_time=100,            # Retry delay in milliseconds
    retries=3,                 # Number of retries per instance
    blocking_timeout=None,     # Max time to wait (None = forever)
)

# Acquire lock
with lock:
    # Lock acquired on majority of Redis instances
    do_critical_work()

# Lock automatically released on all instances
```

### RedLock Parameters

```python
from redis.lock import RedLock

lock = RedLock(
    clients,                    # List of Redis clients
    
    'resource_name',            # Lock name (same across all instances)
    
    # Timing (all in milliseconds)
    lock_timeout=10000,         # How long lock is valid
    retry_time=100,             # Wait between retries
    retries=3,                  # Retries per Redis instance
    
    # Blocking behavior
    blocking=True,              # Block until acquired?
    blocking_timeout=5000,      # Max wait time (ms)
    
    # Thread safety
    threading_local=True,       # Thread-local state
)

# Acquire with custom timeout
acquired = lock.acquire(blocking_timeout=10000)  # Wait up to 10 seconds
```

### RedLock Requirements

RedLock requires:
- **Majority consensus**: Lock acquired on majority of instances (N/2 + 1)
- **Clock synchronization**: Instances should have synchronized clocks
- **Independent failures**: Instances should fail independently

### RedLock vs Regular Lock

| Feature | Regular Lock | RedLock |
|---------|--------------|---------|
| Redis instances | Single | Multiple (3+ recommended) |
| Availability | Single point of failure | High availability |
| Performance | Faster | Slower (multiple round trips) |
| Complexity | Simple | Complex (consensus required) |
| Use Case | Single Redis, dev/test | Production, HA requirements |

## Lock Best Practices

### Always Use Timeouts

Prevent deadlocks with timeouts:

```python
import redis

r = redis.Redis()

# Good: Lock has timeout
with r.lock('resource', timeout=10) as lock:
    do_work()

# Bad: No timeout (can cause deadlock)
# with r.lock('resource') as lock:  # Don't do this!
#     do_work()
```

### Use Context Managers

Ensure locks are always released:

```python
import redis

r = redis.Redis()

# Good: Context manager ensures release
with r.lock('resource', timeout=10) as lock:
    do_work()
# Always released, even on exception

# Bad: Manual acquire/release (error-prone)
lock = r.lock('resource', timeout=10)
lock.acquire()
try:
    do_work()
finally:
    lock.release()  # Easy to forget!
```

### Keep Critical Sections Short

Minimize time holding locks:

```python
import redis

r = redis.Redis()

# Good: Only lock during actual critical section
data = fetch_data_from_cache()  # Outside lock

with r.lock('update_lock', timeout=5) as lock:
    # Short critical section
    update_database(data)

# Bad: Long operation inside lock
with r.lock('update_lock', timeout=5) as lock:
    data = fetch_data_from_cache()  # Slow, shouldn't be in lock
    process_data(data)              # Slow computation
    update_database(data)           # Only this needs locking
```

### Handle Lock Acquisition Failures

Gracefully handle when locks can't be acquired:

```python
import redis
from redis.lock import LockError

r = redis.Redis()

def process_with_lock(resource_id):
    """Process resource with lock, fallback if lock unavailable."""
    try:
        with r.lock(f'lock:{resource_id}', timeout=10, blocking=True, blocking_timeout=5) as lock:
            # Critical section
            return process_critical(resource_id)
            
    except LockError:
        # Lock not available, use alternative approach
        return process_non_critical(resource_id)

# Or queue for later processing
def process_or_queue(resource_id):
    try:
        with r.lock(f'lock:{resource_id}', timeout=10, blocking=False) as lock:
            return process_immediate(resource_id)
    except LockError:
        # Queue for retry later
        queue_for_retry(resource_id)
        return None
```

### Use Meaningful Lock Names

Make lock purposes clear:

```python
import redis

r = redis.Redis()

# Good: Descriptive lock names
with r.lock('order:processing:12345', timeout=30) as lock:
    process_order(12345)

with r.lock('user:profile:update:67890', timeout=10) as lock:
    update_profile(67890)

# Bad: Generic names
with r.lock('lock1', timeout=30) as lock:  # What does this lock?
    do_work()
```

### Monitor Lock Contention

Track lock performance:

```python
import redis
import time
from contextlib import contextmanager

r = redis.Redis()

@contextmanager
def monitored_lock(name, timeout=10):
    """Lock with timing and logging."""
    start = time.time()
    
    try:
        with r.lock(name, timeout=timeout) as lock:
            yield lock
    finally:
        duration = time.time() - start
        print(f"Lock '{name}' held for {duration:.3f}s")

# Usage
with monitored_lock('critical_resource', timeout=10) as lock:
    do_work()
```

## Lock Patterns

### Mutual Exclusion

Basic mutual exclusion pattern:

```python
import redis

r = redis.Redis()

def increment_counter(counter_name):
    """Thread-safe counter increment."""
    with r.lock(f'counter:{counter_name}', timeout=10) as lock:
        current = int(r.get(counter_name) or 0)
        r.set(counter_name, current + 1)
        return current + 1
```

### Resource Pool Management

Manage limited resources with locks:

```python
import redis

r = redis.Redis()

class ConnectionPool:
    def __init__(self, max_connections=10):
        self.r = redis.Redis()
        self.max_connections = max_connections
        self.lock_name = 'pool:connections'
    
    def acquire_connection(self):
        """Acquire connection from pool."""
        with r.lock(self.lock_name, timeout=5) as lock:
            current = int(r.get('pool:count') or 0)
            
            if current < self.max_connections:
                r.incr('pool:count')
                return create_connection()
            else:
                raise Exception("Pool exhausted")
    
    def release_connection(self, conn):
        """Release connection back to pool."""
        with r.lock(self.lock_name, timeout=5) as lock:
            close_connection(conn)
            r.decr('pool:count')
```

### Singleton Pattern

Distributed singleton using locks:

```python
import redis

r = redis.Redis()

class DistributedSingleton:
    def __init__(self, name):
        self.name = name
        self.instance = None
    
    def get_instance(self):
        """Get or create singleton instance."""
        # Check cache first (optimistic)
        cached = r.get(f'singleton:{self.name}')
        if cached:
            return deserialize(cached)
        
        # Lock and double-check
        with r.lock(f'singleton:lock:{self.name}', timeout=10) as lock:
            # Double-check after acquiring lock
            cached = r.get(f'singleton:{self.name}')
            if cached:
                return deserialize(cached)
            
            # Create instance
            self.instance = create_expensive_instance()
            r.setex(f'singleton:{self.name}', 3600, serialize(self.instance))
            
            return self.instance
```

### Rate Limiting with Locks

Implement rate limiting:

```python
import redis

r = redis.Redis()

class RateLimiter:
    def __init__(self, key_prefix, max_requests, window_seconds):
        self.r = redis.Redis()
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window = window_seconds
    
    def is_allowed(self, user_id):
        """Check if request is allowed under rate limit."""
        key = f'{self.key_prefix}:{user_id}'
        
        with r.lock(f'rate_limit:{key}', timeout=5) as lock:
            current = int(r.get(key) or 0)
            
            if current < self.max_requests:
                r.incr(key)
                r.expire(key, self.window)
                return True
            else:
                return False

# Usage
limiter = RateLimiter('api_requests', max_requests=100, window_seconds=3600)

if limiter.is_allowed('user:123'):
    process_request()
else:
    return "Rate limit exceeded"
```

## Cleanup and Debugging

### Check Active Locks

Find locks held in Redis:

```python
import redis

r = redis.Redis()

# Find all lock keys
lock_keys = r.keys('lock:*')
print(f"Active locks: {len(lock_keys)}")

for key in lock_keys:
    value = r.get(key)
    ttl = r.ttl(key)
    print(f"{key}: value={value}, ttl={ttl}")
```

### Force Release Lock

Emergency lock release (use with caution):

```python
import redis

r = redis.Redis()

# Dangerous: Only use if you're sure lock is orphaned
def force_release_lock(lock_name):
    """Force delete lock key (bypass normal release)."""
    r.delete(f'redis-lock:{lock_name}')
    print(f"Force released lock: {lock_name}")

# Better: Check if lock is stale before releasing
def safe_release_stale_lock(lock_name, max_age=3600):
    """Release lock only if it's older than max_age."""
    ttl = r.ttl(f'redis-lock:{lock_name}')
    
    if ttl < 0:  # Key doesn't exist
        return False
    
    if ttl > max_age:
        print(f"Lock {lock_name} is stale, releasing")
        r.delete(f'redis-lock:{lock_name}')
        return True
    
    return False
```

### Lock Monitoring Script

Monitor lock health:

```python
import redis
import time

r = redis.Redis()

def monitor_locks(interval=10):
    """Continuously monitor lock status."""
    while True:
        lock_keys = r.keys('redis-lock:*')
        
        print(f"\n[{time.strftime('%H:%M:%S')}] Active locks: {len(lock_keys)}")
        
        for key in lock_keys:
            ttl = r.ttl(key)
            owner = r.get(key)
            
            status = "OK" if ttl > 0 else "EXPIRED"
            print(f"  {key}: TTL={ttl}s, Owner={owner}, Status={status}")
        
        time.sleep(interval)

# Run monitor in background thread
# import threading
# monitor_thread = threading.Thread(target=monitor_locks, daemon=True)
# monitor_thread.start()
```
