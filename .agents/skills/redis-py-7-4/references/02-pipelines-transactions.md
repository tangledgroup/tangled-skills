# Pipelines and Transactions

Pipelines batch multiple commands into single network round trips, dramatically improving throughput. Transactions provide atomic execution with optimistic locking via WATCH.

## Basic Pipelines

### Creating and Using Pipelines

```python
import redis
r = redis.Redis(decode_responses=True)

# Create pipeline
pipe = r.pipeline()

# Buffer commands (no network calls yet)
pipe.set('foo', 'bar')
pipe.get('foo')
pipe.incr('counter')
pipe.hset('user:1', 'name', 'Alice')

# Execute all buffered commands at once
results = pipe.execute()
# [True, 'bar', 1, 1]
```

### Chained Syntax

Pipelines return themselves for method chaining:

```python
results = (r.pipeline()
    .set('foo', 'bar')
    .get('foo')
    .incr('counter')
    .delete('oldkey')
    .execute())
# [True, 'bar', 1, 1]
```

### Context Manager Usage

Using pipelines as context managers ensures proper cleanup:

```python
with r.pipeline() as pipe:
    pipe.set('foo', 'bar')
    pipe.get('foo')
    results = pipe.execute()
# Pipeline automatically reset on exit
```

## Transactional Pipelines

Transactions ensure atomic execution using MULTI/EXEC.

### Basic Transactions

```python
import redis
r = redis.Redis(decode_responses=True)

# Create transactional pipeline (default behavior)
pipe = r.pipeline(transaction=True)

# Start transaction explicitly
pipe.multi()
pipe.set('a', '1')
pipe.set('b', '2')
pipe.incr('counter')

# Execute atomically
results = pipe.execute()
# [True, True, 42]
```

### Automatic Transaction Management

Transaction=True enables MULTI/EXEC automatically:

```python
with r.pipeline(transaction=True) as pipe:
    pipe.set('x', '10')
    pipe.set('y', '20')
    pipe.get('x')
    results = pipe.execute()
# [True, True, '10'] - wrapped in MULTI/EXEC automatically
```

### Disabling Transactions

Use transaction=False for batching without atomicity:

```python
pipe = r.pipeline(transaction=False)
pipe.set('a', '1')
pipe.get('a')
results = pipe.execute()  # No MULTI/EXEC, just batched commands
```

## Optimistic Locking with WATCH

WATCH implements optimistic locking by monitoring keys for changes.

### Basic WATCH Pattern

```python
import redis
from redis import WatchError

r = redis.Redis(decode_responses=True)

# Manual WATCH/MULTI/EXEC pattern
pipe = r.pipeline()
while True:
    try:
        # Start watching key
        pipe.watch('balance')
        
        # Read current value (immediate execution, not buffered)
        balance = int(pipe.get('balance') or 0)
        
        # Start transaction
        pipe.multi()
        
        # Buffer commands
        new_balance = balance - 100
        pipe.set('balance', new_balance)
        
        # Execute transaction
        pipe.execute()
        break  # Success
        
    except WatchError:
        # Key was modified, retry
        continue
    finally:
        pipe.reset()  # Important: release connection
```

### Using transaction() Helper

The `transaction()` method simplifies WATCH patterns:

```python
import redis
r = redis.Redis(decode_responses=True)

def withdraw_funds(pipe):
    """Transaction function that receives pipeline and watched keys."""
    balance = int(pipe.get('balance') or 0)
    
    if balance < 100:
        raise ValueError("Insufficient funds")
    
    pipe.multi()
    pipe.set('balance', balance - 100)
    pipe.incr('transaction_count')

# Execute with automatic retry on WatchError
try:
    r.transaction(withdraw_funds, 'balance')
except ValueError as e:
    print(f"Transaction failed: {e}")
```

### WATCH Multiple Keys

Watch multiple keys for compound operations:

```python
import redis
r = redis.Redis(decode_responses=True)

def atomic_transfer(pipe):
    """Transfer between two accounts atomically."""
    from_balance = int(pipe.get('account:from') or 0)
    to_balance = int(pipe.get('account:to') or 0)
    
    if from_balance < 100:
        raise ValueError("Insufficient funds")
    
    pipe.multi()
    pipe.set('account:from', from_balance - 100)
    pipe.set('account:to', to_balance + 100)

# Watch both keys
r.transaction(atomic_transfer, 'account:from', 'account:to')
```

### WATCH with Non-Blocking Get

Use `watch()` without blocking other operations:

```python
pipe = r.pipeline()
pipe.watch('key')

# These execute immediately (not buffered)
value1 = pipe.get('key')
value2 = pipe.exists('related_key')

# Now start buffering
pipe.multi()
pipe.set('key', 'new_value')
pipe.execute()
```

## Pipeline Error Handling

### Individual Command Failures

In transactional pipelines, errors abort the entire transaction:

```python
import redis
from redis import ResponseError

pipe = r.pipeline(transaction=True)
pipe.set('key', 'value')
pipe.eval('return 1/0', 0)  # Will fail
pipe.set('another', 'value')

try:
    results = pipe.execute()
except ResponseError as e:
    print(f"Transaction failed: {e}")
    # None of the commands were executed
```

### Non-Transactional Error Handling

In non-transactional pipelines, other commands continue:

```python
pipe = r.pipeline(transaction=False)
pipe.set('key1', 'value1')
pipe.eval('return 1/0', 0)  # Fails but others succeed
pipe.set('key2', 'value2')

results = pipe.execute()
# [True, ResponseError(...), True]
```

### Checking Results for Errors

```python
import redis
from redis import ResponseError

pipe = r.pipeline(transaction=False)
pipe.set('key1', 'value1')
pipe.eval('return 1/0', 0)
pipe.set('key2', 'value2')

results = pipe.execute()

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Command {i} failed: {result}")
    else:
        print(f"Command {i} succeeded: {result}")
```

## Cluster Pipelines

Cluster pipelines group commands by node and execute in parallel.

### Basic Cluster Pipeline

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# Commands are grouped by slot/node automatically
with rc.pipeline() as pipe:
    pipe.set('foo', 'value1')  # Slot A -> Node 1
    pipe.set('bar', 'value2')  # Slot B -> Node 2
    pipe.get('foo')            # Slot A -> Node 1
    pipe.get('bar')            # Slot B -> Node 2
    
    results = pipe.execute()
    # [True, True, 'value1', 'value2'] - order preserved
```

### Cluster Pipeline Limitations

- **Key-based commands only**: Non-key commands (PING, INFO) not supported
- **Automatic sharding**: Commands grouped by hash slot and executed in parallel
- **Read balancing**: Inherits cluster's read_from_replicas setting

### Transactional Cluster Pipelines

Cluster transactions require all keys on same slot:

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# Use hash tags to force same slot
with rc.pipeline(transaction=True) as pipe:
    pipe.set('{user}1:name', 'Alice')  # Same slot due to {user} tag
    pipe.set('{user}1:age', '30')      # Same slot
    pipe.hincrby('{user}1:stats', 'logins', 1)  # Same slot
    
    results = pipe.execute()
    # [True, True, 5]
```

### Cross-Slot Transaction Errors

```python
from redis.cluster import RedisCluster
from redis.exceptions import ClusterCrossSlotError

rc = RedisCluster(host='localhost', port=6379)

try:
    with rc.pipeline(transaction=True) as pipe:
        pipe.set('key1', 'value1')  # Different slot
        pipe.set('key2', 'value2')  # Different slot
        pipe.execute()
except ClusterCrossSlotError as e:
    print(f"Keys must be on same slot: {e}")
```

## Pipeline Performance

### Benchmark Comparison

```python
import redis
import time

r = redis.Redis()

# Without pipeline (N round trips)
start = time.time()
for i in range(1000):
    r.set(f'key{i}', f'value{i}')
no_pipeline_time = time.time() - start

# With pipeline (1 round trip)
start = time.time()
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f'key{i}', f'value{i}')
pipe.execute()
pipeline_time = time.time() - start

print(f"Without pipeline: {no_pipeline_time:.3f}s")
print(f"With pipeline: {pipeline_time:.3f}s")
print(f"Speedup: {no_pipeline_time/pipeline_time:.1f}x")
# Typical output: 50-100x speedup for batch operations
```

### Best Practices

1. **Batch related operations**: Group commands that must execute together
2. **Use context managers**: Ensures proper connection cleanup
3. **Avoid large pipelines**: Keep under 1000 commands to prevent memory issues
4. **Monitor pipeline size**: Track buffer usage for long-running operations
5. **Reuse pipelines**: Create once, execute multiple times if pattern repeats

```python
# Good: Reuse pipeline for repeated batches
pipe = r.pipeline()
for batch in data_batches:
    pipe.set(f'key{batch.id}', batch.value)
    if len(pipe.command_stack) >= 100:
        pipe.execute()
        pipe = r.pipeline()  # Create new pipeline

# Flush remaining commands
if pipe.command_stack:
    pipe.execute()
```

## Advanced Pipeline Patterns

### Watch with Retry Logic

```python
import redis
from redis import WatchError
import time

r = redis.Redis(decode_responses=True)

def atomic_increment_with_retry(key, increment=1, max_retries=5):
    """Increment with optimistic locking and retry."""
    for attempt in range(max_retries):
        try:
            def transaction(pipe):
                current = int(pipe.get(key) or 0)
                pipe.multi()
                pipe.set(key, current + increment)
            
            r.transaction(transaction, key)
            return True
            
        except WatchError:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            raise
    
    return False

# Usage
success = atomic_increment_with_retry('counter', increment=5)
```

### Conditional Pipeline Execution

```python
import redis
r = redis.Redis(decode_responses=True)

def conditional_update(pipe, key, condition_fn, update_fn):
    """Execute pipeline only if condition is met."""
    current_value = pipe.get(key)
    
    if not condition_fn(current_value):
        return False
    
    pipe.multi()
    update_fn(pipe, key, current_value)
    return True

# Example: Update only if value < 100
with r.pipeline() as pipe:
    should_update = conditional_update(
        pipe,
        'score',
        lambda v: int(v or 0) < 100,
        lambda p, k, v: p.set(k, int(v or 0) + 10)
    )
    
    if should_update:
        results = pipe.execute()
```

### Pipeline with Callbacks

```python
import redis
r = redis.Redis(decode_responses=True)

def process_with_callbacks(pipe, operations):
    """Execute operations with success/failure callbacks."""
    results = []
    
    for op in operations:
        result = op['func'](pipe, *op.get('args', []))
        results.append({
            'operation': op['name'],
            'result': result,
            'success': True
        })
    
    return results

# Define operations
operations = [
    {'name': 'set_key', 'func': lambda p, k, v: p.set(k, v), 'args': ['key1', 'value1']},
    {'name': 'get_key', 'func': lambda p, k: p.get(k), 'args': ['key1']},
    {'name': 'incr', 'func': lambda p, k: p.incr(k), 'args': ['counter']},
]

results = process_with_callbacks(r.pipeline(), operations)
```

### Atomic Counter with Threshold

```python
import redis
from redis import WatchError

r = redis.Redis(decode_responses=True)

def increment_if_below_threshold(key, increment, threshold):
    """Increment counter only if below threshold."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            def transaction(pipe):
                current = int(pipe.get(key) or 0)
                
                if current + increment > threshold:
                    raise ValueError("Would exceed threshold")
                
                pipe.multi()
                pipe.set(key, current + increment)
            
            r.transaction(transaction, key)
            return True
            
        except (WatchError, ValueError) as e:
            if attempt == max_retries - 1:
                raise
            continue
    
    return False

# Usage
try:
    increment_if_below_threshold('requests_today', 1, 1000)
except ValueError as e:
    print(f"Threshold exceeded: {e}")
```

## Pipeline Reset and Cleanup

### Manual Reset

```python
pipe = r.pipeline()
pipe.watch('key')
# ... operations ...
pipe.reset()  # Clear buffer and release connection
```

### Automatic Reset with Context Manager

```python
with r.pipeline() as pipe:
    pipe.set('key', 'value')
    # pipe.reset() called automatically on exit, even on exception
```

### Error Recovery

```python
import redis
from redis import ConnectionError

pipe = r.pipeline()

try:
    pipe.set('key', 'value')
    pipe.execute()
except ConnectionError:
    pipe.reset()  # Ensure connection returned to pool
    raise
```

## Monitoring Pipeline Performance

### Command Count Tracking

```python
import redis

r = redis.Redis()
pipe = r.pipeline()

# Track commands before execution
for i in range(100):
    pipe.set(f'key{i}', f'value{i}')

print(f"Commands buffered: {len(pipe.command_stack)}")
results = pipe.execute()
```

### Execution Time Measurement

```python
import redis
import time

r = redis.Redis()
pipe = r.pipeline()

# Buffer commands
for i in range(1000):
    pipe.set(f'key{i}', f'value{i}')

# Measure execution time
start = time.time()
results = pipe.execute()
duration = time.time() - start

print(f"Executed {len(results)} commands in {duration:.3f}s")
print(f"Throughput: {len(results)/duration:.0f} cmds/sec")
```
