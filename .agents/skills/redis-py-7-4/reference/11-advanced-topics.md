# Advanced Topics

Advanced redis-py features including multi-database clients, threading safety, AWS integration, credential providers, and complex patterns.

## Multi-Database Client (Active-Active)

Multi-database client for Redis Active-Active setups with automatic failover:

```python
from redis.client import MultiDatabaseRetryingClient
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

# Configure retry strategy
retry = Retry(ExponentialBackoff(), 3)

# Create multi-database client
client = MultiDatabaseRetryingClient(
    # List of Redis clients (typically replicas)
    clients=[
        redis.Redis(host='primary.example.com', port=6379),
        redis.Redis(host='replica1.example.com', port=6379),
        redis.Redis(host='replica2.example.com', port=6379),
    ],
    
    # Failover strategy
    retry=retry,
    
    # Health check interval
    health_check_interval=30,
    
    # Switch back to primary when healthy
    switch_back_to_primary=True,
)

# Use like regular Redis client
client.set('key', 'value')
result = client.get('key')

# Automatic failover if primary fails
```

### Active-Active Configuration

```python
from redis.client import MultiDatabaseRetryingClient

client = MultiDatabaseRetryingClient(
    clients=[
        redis.Redis(host='dc1-redis.example.com', port=6379, db=0),
        redis.Redis(host='dc2-redis.example.com', port=6379, db=0),
    ],
    
    # Failover behavior
    retry=Retry(ExponentialBackoff(), 5),
    
    # Health monitoring
    health_check_interval=10,  # Check every 10 seconds
    
    # Automatic recovery
    switch_back_to_primary=True,  # Return to primary when healthy
    switch_back_delay=60,         # Wait 60s before switching back
    
    # Write behavior
    write_to_all=False,  # If True, writes to all databases
)
```

### Failover Strategies

Different strategies for selecting databases:

```python
from redis.client import MultiDatabaseRetryingClient
from redis.multi_database import RoundRobinStrategy, RandomStrategy

# Round-robin reads across databases
client = MultiDatabaseRetryingClient(
    clients=[redis.Redis(host=f'replica{i}.com') for i in range(3)],
    read_strategy=RoundRobinStrategy()
)

# Random selection
client = MultiDatabaseRetryingClient(
    clients=[redis.Redis(host=f'replica{i}.com') for i in range(3)],
    read_strategy=RandomStrategy()
)
```

## Threading and Concurrency

### Thread Safety

Redis client instances are thread-safe:

```python
import redis
import threading

# Single client shared across threads (safe)
r = redis.Redis(host='localhost', port=6379)

def worker(thread_id):
    """Safe to use shared client from multiple threads."""
    for i in range(100):
        r.incr(f'counter:{thread_id}')
        value = r.get(f'counter:{thread_id}')
        print(f"Thread {thread_id}: {value}")

# Create multiple threads using same client
threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Connection Pool Thread Safety

Connection pools are thread-safe:

```python
import redis

# Shared connection pool (thread-safe)
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50
)

# Multiple clients sharing pool (efficient)
r1 = redis.Redis(connection_pool=pool)
r2 = redis.Redis(connection_pool=pool)

# Each thread gets its own connection from pool
def worker():
    r1.get('key')  # Gets connection from pool, returns after use
    r2.set('key', 'value')  # Different connection, same pool
```

### Non-Thread-Safe Objects

Some objects are NOT thread-safe:

```python
import redis

r = redis.Redis()

# NOT thread-safe: PubSub instances
pubsub = r.pubsub()
# Don't share pubsub between threads!

# NOT thread-safe: Pipeline instances  
pipe = r.pipeline()
# Don't share pipeline between threads!

# Thread-safe: Client instances
r.get('key')  # Safe from multiple threads
r.set('key', 'value')  # Safe from multiple threads
```

### Per-Thread Connections

Create per-thread connections for isolation:

```python
import redis
import threading

# Thread-local storage for Redis clients
local = threading.local()

def get_redis_client():
    """Get thread-local Redis client."""
    if not hasattr(local, 'redis'):
        local.redis = redis.Redis(host='localhost', port=6379)
    return local.redis

def worker():
    # Each thread gets its own client
    r = get_redis_client()
    r.set('thread_key', threading.current_thread().name)
    print(r.get('thread_key'))
```

## AWS Integration

### AWS Credential Provider

Use AWS credential providers for Redis authentication:

```python
from redis import Redis
from redis.credentials import CredentialProvider, BotoCredentialProvider

# Using boto3 credential provider
import boto3

boto_session = boto3.Session()
creds = boto_session.get_credentials()

provider = BotoCredentialProvider(creds)

r = Redis(
    host='redis-cluster.example.com',
    port=6379,
    credential_provider=provider
)

# Credentials automatically refreshed
r.set('key', 'value')
```

### AWS Secrets Manager Integration

Retrieve credentials from AWS Secrets Manager:

```python
import boto3
from redis import Redis
from redis.credentials import CredentialProvider

class SecretsManagerCredentialProvider(CredentialProvider):
    """Fetch credentials from AWS Secrets Manager."""
    
    def __init__(self, secret_arn, region='us-east-1'):
        self.secret_arn = secret_arn
        self.client = boto3.client('secretsmanager', region_name=region)
        self._credentials = None
    
    def get_credentials(self):
        """Get username and password from Secrets Manager."""
        if self._credentials is None:
            response = self.client.get_secret_value(SecretId=self.secret_arn)
            import json
            secret = json.loads(response['SecretString'])
            self._credentials = (secret['username'], secret['password'])
        
        return self._credentials

# Usage
provider = SecretsManagerCredentialProvider(
    secret_arn='arn:aws:secretsmanager:us-east-1:123456789:secret:redis-auth'
)

r = Redis(
    host='cluster.example.com',
    port=6379,
    credential_provider=provider
)
```

### AWS ElastiCache Integration

Connect to AWS ElastiCache:

```python
import redis
from redis import Retry
from redis.backoff import ExponentialBackoff

# ElastiCache connection with retry
r = redis.Redis(
    host='mycluster.cluster.xyz.us-east-1.cache.amazonaws.com',
    port=6379,
    password='my-password',
    ssl=True,  # ElastiCache requires SSL
    ssl_cert_reqs='required',
    
    # Retry configuration for cloud reliability
    retry=Retry(ExponentialBackoff(), 3),
    socket_timeout=5,
    socket_connect_timeout=5
)

# Health checks for cloud environment
r = redis.Redis(
    host='mycluster.cluster.xyz.us-east-1.cache.amazonaws.com',
    port=6379,
    ssl=True,
    health_check_interval=30,  # Important for cloud environments
)
```

## SSL/TLS Advanced Configuration

### Custom SSL Context

Create custom SSL context for advanced TLS configuration:

```python
import redis
import ssl

# Create custom SSL context
context = ssl.create_default_context()

# Configure TLS version
context.minimum_version = ssl.TLSVersion.TLSv1_2

# Load certificates
context.load_verify_locations('/path/to/ca-certificates.crt')

# Load client certificate for mutual TLS
context.load_cert_chain(
    certfile='/path/to/client-cert.pem',
    keyfile='/path/to/client-key.pem'
)

# Enable hostname verification
context.check_hostname = True

# Use custom context
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl_context=context
)
```

### Certificate Verification Options

Different certificate verification modes:

```python
import redis

# Strict verification (production)
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_ca_certs='/path/to/ca.crt',
    ssl_cert_reqs='required',  # Verify server certificate
    ssl_check_hostname=True    # Verify hostname matches certificate
)

# No verification (development only!)
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='none'  # Don't verify - insecure!
)

# Optional verification
r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_cert_reqs='optional'  # Verify if cert present, but don't fail if missing
)
```

### Mutual TLS (mTLS)

Two-way authentication with client certificates:

```python
import redis

r = redis.Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    
    # Server verifies client
    ssl_certfile='/path/to/client-cert.pem',
    ssl_keyfile='/path/to/client-key.pem',
    ssl_password='key-password',  # If key is encrypted
    
    # Client verifies server
    ssl_ca_certs='/path/to/ca.crt',
    ssl_cert_reqs='required',
    ssl_check_hostname=True
)
```

## Advanced Pub/Sub Patterns

### Pub/Sub with Message Queue

Implement message queue with Pub/Sub:

```python
import redis
import json
import threading
import time

class PubSubMessageQueue:
    def __init__(self, redis_client, channel_name):
        self.r = redis_client
        self.channel = channel_name
        self.pubsub = None
        self.running = False
        self.message_handlers = []
    
    def start(self):
        """Start message consumer."""
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe(self.channel)
        self.running = True
        
        while self.running:
            message = self.pubsub.get_message(timeout=1.0)
            
            if message and message['type'] == 'message':
                data = json.loads(message['data'].decode())
                
                for handler in self.message_handlers:
                    try:
                        handler(data)
                    except Exception as e:
                        print(f"Handler error: {e}")
    
    def stop(self):
        """Stop message consumer."""
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()
    
    def publish(self, data):
        """Publish message to queue."""
        self.r.publish(self.channel, json.dumps(data))
    
    def on_message(self, handler):
        """Register message handler."""
        self.message_handlers.append(handler)

# Usage
queue = PubSubMessageQueue(redis.Redis(), 'tasks')

@queue.on_message
def process_task(task):
    print(f"Processing: {task}")

# Start consumer in background thread
thread = threading.Thread(target=queue.start, daemon=True)
thread.start()

# Publish messages
queue.publish({'type': 'email', 'to': 'user@example.com'})
queue.publish({'type': 'notification', 'user_id': 123})

time.sleep(5)
queue.stop()
```

### Pattern-Based Routing

Route messages based on patterns:

```python
import redis

class MessageRouter:
    def __init__(self, redis_client):
        self.r = redis_client
        self.handlers = {}
        self.pubsub = None
    
    def subscribe(self, pattern, handler):
        """Subscribe to pattern with handler."""
        self.handlers[pattern] = handler
        if self.pubsub:
            self.pubsub.psubscribe(pattern)
    
    def start(self):
        """Start routing messages."""
        self.pubsub = self.r.pubsub()
        
        # Subscribe to all patterns
        for pattern in self.handlers.keys():
            self.pubsub.psubscribe(pattern)
        
        while True:
            message = self.pubsub.get_message(timeout=1.0)
            
            if message and message['type'] == 'pmessage':
                pattern = message['pattern'].decode()
                channel = message['channel'].decode()
                data = message['data']
                
                handler = self.handlers.get(pattern)
                if handler:
                    handler(channel, data)
    
    def publish(self, channel, data):
        """Publish to channel."""
        self.r.publish(channel, data)

# Usage
router = MessageRouter(redis.Redis())

@router.subscribe('user:*')
def handle_user_event(channel, data):
    print(f"User event on {channel}: {data}")

@router.subscribe('order:*')
def handle_order_event(channel, data):
    print(f"Order event on {channel}: {data")

router.publish('user:123', 'profile_updated')
router.publish('order:456', 'completed')
```

## Advanced Pipeline Patterns

### Batch Operations with Pipelines

Efficient batch processing:

```python
import redis

r = redis.Redis()

# Batch insert
def batch_insert(data_list):
    """Insert multiple items efficiently."""
    with r.pipeline() as pipe:
        for item in data_list:
            pipe.hset(f"entity:{item['id']}', mapping=item)
        
        results = pipe.execute()
        return results

# Batch update
def batch_update(items):
    """Update multiple items atomically."""
    with r.pipeline(transaction=True) as pipe:
        for item in items:
            pipe.hset(f"entity:{item['id']}", 'updated_at', item['timestamp'])
        
        pipe.execute()

# Batch delete
def batch_delete(ids):
    """Delete multiple keys efficiently."""
    keys = [f"entity:{id}" for id in ids]
    return r.delete(*keys)
```

### Pipeline with Error Recovery

Handle partial pipeline failures:

```python
import redis
from redis.exceptions import ResponseError

r = redis.Redis()

def safe_batch_operation(items):
    """Execute batch with error tracking."""
    results = []
    errors = []
    
    with r.pipeline(transaction=False) as pipe:
        for i, item in enumerate(items):
            try:
                pipe.hset(f"entity:{item['id']}", mapping=item)
                results.append({'index': i, 'status': 'queued'})
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        
        # Execute and collect results
        raw_results = pipe.execute()
    
    for i, result in enumerate(raw_results):
        if isinstance(result, Exception):
            results[i]['status'] = 'failed'
            results[i]['error'] = str(result)
        else:
            results[i]['status'] = 'success'
    
    return results, errors

# Usage
results, errors = safe_batch_operation(large_dataset)
print(f"Success: {sum(1 for r in results if r['status'] == 'success')}")
print(f"Errors: {len(errors)}")
```

## Lua Script Optimization

### Script Caching

Cache scripts for better performance:

```python
import redis

class ScriptCache:
    def __init__(self, redis_client):
        self.r = redis_client
        self.scripts = {}  # script_code -> Script object
    
    def get_script(self, code, name):
        """Get or create cached script."""
        if name not in self.scripts:
            self.scripts[name] = self.r.register_script(code)
        
        return self.scripts[name]

# Usage
cache = ScriptCache(redis.Redis())

# Register once, use many times
increment_script = cache.get_script(
    "return redis.call('INCR', KEYS[1])",
    'increment'
)

for i in range(1000):
    increment_script(keys=[f'counter:{i}'])
```

### Script Libraries

Organize scripts as reusable libraries:

```python
import redis

class RedisScripts:
    """Collection of Lua scripts for common operations."""
    
    def __init__(self, redis_client):
        self.r = redis_client
        self._scripts = {}
    
    def _register(self, name, code):
        """Register script if not already registered."""
        if name not in self._scripts:
            self._scripts[name] = self.r.register_script(code)
        return self._scripts[name]
    
    def atomic_increment(self, key, amount=1):
        """Atomically increment counter."""
        script = self._register(
            'atomic_increment',
            """
            local current = tonumber(redis.call('GET', KEYS[1]) or 0)
            redis.call('SET', KEYS[1], current + ARGV[1])
            return current + ARGV[1]
            """
        )
        return script(keys=[key], args=[amount])
    
    def check_and_set(self, key, expected, new_value):
        """Set value only if current matches expected."""
        script = self._register(
            'check_and_set',
            """
            if redis.call('GET', KEYS[1]) == ARGV[1] then
                redis.call('SET', KEYS[1], ARGV[2])
                return 1
            end
            return 0
            """
        )
        return script(keys=[key], args=[expected, new_value])

# Usage
scripts = RedisScripts(redis.Redis())

count = scripts.atomic_increment('visits', 1)
updated = scripts.check_and_set('status', 'pending', 'completed')
```

## Monitoring and Debugging

### Slow Log Analysis

Query and analyze Redis slow log:

```python
import redis

r = redis.Redis()

# Get slow log entries
entries = r.slowlog_get(100)  # Last 100 entries

for entry in entries:
    print(f"Command: {entry['command']}")
    print(f"Duration: {entry['duration']} microseconds")
    print(f"Client: {entry['client_info']}")
    print(f"Time: {entry['time']}")
    print("---")

# Get slow log length
length = r.slowlog_len()
print(f"Total entries: {length}")

# Reset slow log (careful in production!)
# r.slowlog_reset()
```

### Performance Monitoring

Monitor Redis performance metrics:

```python
import redis

r = redis.Redis()

def get_performance_metrics():
    """Get Redis performance statistics."""
    info = r.info('stats')
    
    return {
        'commands_processed': info['total_commands_processed'],
        'connections_received': info['total_connections_received'],
        'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec'],
        'rejected_connections': info['rejected_connections'],
        'keyspace_hits': info['keyspace_hits'],
        'keyspace_misses': info['keyspace_misses'],
        'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
                if (info['keyspace_hits'] + info['keyspace_misses']) > 0 else 0
    }

metrics = get_performance_metrics()
print(f"Hit rate: {metrics['hit_rate']:.2%}")
print(f"Ops/sec: {metrics['instantaneous_ops_per_sec']}")
```

### Client Information

Monitor connected clients:

```python
import redis

r = redis.Redis()

# Get all connected clients
clients = r.client_list()

for client in clients:
    print(f"ID: {client['id']}")
    print(f"Address: {client['addr']}")
    print(f"Name: {client['name']}")
    print(f"Age: {client['age']}s")
    print(f"Idle: {client['idle']}s")
    print(f"Commands: {client['cmd']}")
    print("---")

# Set client name for identification
r.client_setname('myapp-worker-1')

# Get current client name
name = r.client_getname()
print(f"Client name: {name}")
```

## Migration Patterns

### Blue-Green Deployment

Migrate between Redis instances:

```python
import redis

class RedisMigrator:
    def __init__(self, old_client, new_client):
        self.old = old_client
        self.new = new_client
    
    def migrate_key(self, key):
        """Migrate single key."""
        # Get type and value
        key_type = self.old.type(key)
        
        if key_type == b'string':
            value = self.old.get(key)
            ttl = self.old.ttl(key)
            self.new.set(key, value, ex=ttl if ttl > 0 else None)
            
        elif key_type == b'hash':
            data = self.old.hgetall(key)
            self.new.hmset(key, data)
            ttl = self.old.ttl(key)
            if ttl > 0:
                self.new.expire(key, ttl)
        
        # Handle other types...
    
    def migrate_pattern(self, pattern, batch_size=100):
        """Migrate keys matching pattern."""
        cursor = 0
        
        while True:
            cursor, keys = self.old.scan(cursor=cursor, match=pattern, count=batch_size)
            
            for key in keys:
                self.migrate_key(key)
            
            if cursor == 0:
                break

# Usage
old_redis = redis.Redis(host='old-redis.example.com')
new_redis = redis.Redis(host='new-redis.example.com')

migrator = RedisMigrator(old_redis, new_redis)
migrator.migrate_pattern('user:*')
```

### Data Backup and Restore

Backup Redis data:

```python
import redis
import json
import gzip
from datetime import datetime

def backup_database(r, filename=None):
    """Backup all keys to file."""
    if filename is None:
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.gz"
    
    data = {}
    cursor = 0
    
    while True:
        cursor, keys = r.scan(cursor=cursor, count=1000)
        
        for key in keys:
            key_type = r.type(key)
            ttl = r.ttl(key)
            
            if key_type == b'string':
                data[key.decode()] = {'type': 'string', 'value': r.get(key).decode(), 'ttl': ttl}
            elif key_type == b'hash':
                data[key.decode()] = {'type': 'hash', 'value': r.hgetall(key), 'ttl': ttl}
            # Handle other types...
        
        if cursor == 0:
            break
    
    with gzip.open(filename, 'wt') as f:
        json.dump(data, f)
    
    print(f"Backup saved to {filename}")

def restore_database(r, filename):
    """Restore keys from backup file."""
    with gzip.open(filename, 'rt') as f:
        data = json.load(f)
    
    for key, info in data.items():
        if info['type'] == 'string':
            r.set(key, info['value'], ex=info['ttl'] if info['ttl'] > 0 else None)
        elif info['type'] == 'hash':
            r.hmset(key, info['value'])
            if info['ttl'] > 0:
                r.expire(key, info['ttl'])
    
    print(f"Restored {len(data)} keys")
```

## Performance Optimization Tips

### Connection Pool Sizing

Optimize connection pool for workload:

```python
import redis

# For read-heavy workloads
read_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=100  # More connections for reads
)

# For write-heavy workloads
write_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50  # Fewer connections, more serialization
)

# For high concurrency
high_concurrency_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=200,
    health_check_interval=10  # More frequent health checks
)
```

### Pipeline Batch Sizing

Optimize pipeline batch sizes:

```python
import redis
import time

def find_optimal_batch_size(r, total_operations=10000):
    """Test different batch sizes to find optimal."""
    results = {}
    
    for batch_size in [10, 50, 100, 500, 1000]:
        start = time.time()
        
        operations_performed = 0
        while operations_performed < total_operations:
            with r.pipeline() as pipe:
                for _ in range(min(batch_size, total_operations - operations_performed)):
                    pipe.incr('test_counter')
                
                pipe.execute()
            
            operations_performed += batch_size
        
        duration = time.time() - start
        results[batch_size] = duration
    
    # Find fastest batch size
    optimal = min(results, key=results.get)
    print(f"Optimal batch size: {optimal} ({results[optimal]:.3f}s)")
    
    return optimal
```

### Memory Optimization

Reduce memory usage:

```python
import redis

r = redis.Redis(decode_responses=True)  # Use strings instead of bytes when possible

# Use efficient data structures
# Instead of many small keys, use hashes
r.hset('user:123', mapping={'name': 'Alice', 'email': 'alice@example.com'})
# Better than: r.set('user:123:name', ...), r.set('user:123:email', ...)

# Use pipelining to reduce network overhead
with r.pipeline() as pipe:
    for i in range(1000):
        pipe.set(f'key:{i}', f'value:{i}')
    pipe.execute()

# Enable RESP3 for better type handling
r = redis.Redis(protocol=3)

# Use client-side caching for frequently accessed data
from redis.cache import CacheConfig
r = redis.Redis(protocol=3, cache_config=CacheConfig(max_entries=10000))
```
