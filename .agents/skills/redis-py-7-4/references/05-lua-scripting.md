# Lua Scripting

Redis supports executing Lua scripts atomically on the server. redis-py provides convenient abstractions for script registration, caching, and execution.

## Basic Lua Scripting

### EVAL Command

Execute Lua script directly:

```python
import redis
r = redis.Redis(decode_responses=True)

# Simple script with KEYS and ARGV
result = r.eval(
    "return KEYS[1] .. ARGV[1]",  # Lua code
    1,                             # Number of keys
    'mykey',                       # KEY[1]
    'value'                        # ARGV[1]
)
print(result)  # 'mykeyvalue'

# Script with Redis commands
result = r.eval(
    """
    local value = redis.call('GET', KEYS[1])
    return tonumber(value) + tonumber(ARGV[1])
    """,
    1,
    'counter',
    '5'
)
```

### EVALSHA Command

Execute script by SHA1 hash (more efficient for repeated execution):

```python
import redis
r = redis.Redis(decode_responses=True)

# First, load script to get its SHA1
sha = r.script_load(
    "return redis.call('GET', KEYS[1])"
)
print(f"Script SHA: {sha}")

# Execute using SHA (faster than sending full script)
result = r.evalsha(
    sha,        # Script hash
    0,          # Number of keys
    'mykey'     # KEY[1]
)

# Check if script exists
exists = r.script_exists(sha)
print(f"Script exists: {exists}")

# Flush all scripts (careful in production!)
r.script_flush()
```

## Script Objects

redis-py provides `Script` objects for easier script management.

### Registering Scripts

```python
import redis
r = redis.Redis(decode_responses=True)

# Define Lua script
multiply_script = """
local value = redis.call('GET', KEYS[1])
value = tonumber(value)
return value * tonumber(ARGV[1])
"""

# Register script (loads into Redis cache automatically)
multiply = r.register_script(multiply_script)

# Execute registered script
r.set('counter', '10')
result = multiply(keys=['counter'], args=[5])
print(result)  # 50
```

### Script Object Features

Script objects handle caching and NOSCRIPT errors automatically:

```python
import redis
r = redis.Redis(decode_responses=True)

# Register script
increment_script = """
local current = redis.call('GET', KEYS[1])
current = tonumber(current) or 0
redis.call('SET', KEYS[1], current + 1)
return current + 1
"""

incr = r.register_script(increment_script)

# First execution (loads script if needed)
result = incr(keys=['mycounter'], args=[])
print(result)  # 1

# Subsequent executions use cached script
result = incr(keys=['mycounter'], args=[])
print(result)  # 2
```

### Script with Multiple Keys and Args

```python
import redis
r = redis.Redis(decode_responses=True)

# Script with multiple keys and arguments
atomic_transfer_script = """
-- KEYS[1] = from_account, KEYS[2] = to_account
-- ARGV[1] = amount

local amount = tonumber(ARGV[1])
local from_balance = tonumber(redis.call('GET', KEYS[1]) or 0)

if from_balance < amount then
    return -1  -- Insufficient funds
end

redis.call('DECRBY', KEYS[1], amount)
redis.call('INCRBY', KEYS[2], amount)
return 1  -- Success
"""

transfer = r.register_script(atomic_transfer_script)

# Execute transfer
result = transfer(
    keys=['account:alice', 'account:bob'],
    args=[100]  # Transfer 100
)
print(result)  # 1 (success) or -1 (insufficient funds)
```

### Script Error Handling

```python
import redis
from redis.exceptions import NoScriptError, ResponseError

r = redis.Redis(decode_responses=True)

# Register script that might error
error_script = """
if tonumber(ARGV[1]) < 0 then
    error("Negative value not allowed")
end
return ARGV[1]
"""

validate = r.register_script(error_script)

try:
    result = validate(keys=[], args=['-5'])
except ResponseError as e:
    print(f"Script error: {e}")

# NoScriptError occurs if script was flushed from Redis cache
try:
    result = validate(keys=[], args=['10'])
except NoScriptError:
    # Script will be reloaded automatically by redis-py
    print("Script not cached, reloading...")
```

## Scripts in Pipelines

Execute scripts within pipelines for batching:

```python
import redis
r = redis.Redis(decode_responses=True)

# Register script
get_and_incr = r.register_script("""
local value = redis.call('GET', KEYS[1])
redis.call('INCR', KEYS[1])
return tonumber(value) or 0
""")

# Use in pipeline
with r.pipeline() as pipe:
    pipe.set('counter', '10')
    
    # Execute script in pipeline (pass pipeline as client)
    get_and_incr(keys=['counter'], args=[], client=pipe)
    get_and_incr(keys=['counter'], args=[], client=pipe)
    
    results = pipe.execute()
    print(results)  # [True, 10, 11]
```

## Scripts with Different Clients

Execute registered scripts on different Redis clients:

```python
import redis

# Register script on first client
r1 = redis.Redis(host='redis1.example.com')
script = r1.register_script("return redis.call('GET', KEYS[1])")

# Execute on different client
r2 = redis.Redis(host='redis2.example.com')
result = script(keys=['key'], args=[], client=r2)

# Script is loaded into r2's Redis server automatically
```

## Common Lua Script Patterns

### Atomic Check-and-Set

```python
import redis
r = redis.Redis(decode_responses=True)

check_and_set = r.register_script("""
-- Only set if current value matches expected
if redis.call('GET', KEYS[1]) == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1  -- Success
else
    return 0  -- Value changed
end
""")

# Usage
result = check_and_set(
    keys=['status'],
    args=['pending', 'completed']
)
if result:
    print("Status updated successfully")
else:
    print("Status changed by another client")
```

### Atomic Decrement with Minimum

```python
import redis
r = redis.Redis(decode_responses=True)

decrement_with_min = r.register_script("""
local current = tonumber(redis.call('GET', KEYS[1]) or 0)
local decrement = tonumber(ARGV[1])
local minimum = tonumber(ARGV[2])

if current - decrement < minimum then
    return -1  -- Would go below minimum
end

redis.call('DECRBY', KEYS[1], decrement)
return 1  -- Success
""")

# Usage: Decrement inventory, but not below 0
r.set('inventory:item123', '10')
result = decrement_with_min(
    keys=['inventory:item123'],
    args=[5, 0]  # Decrement by 5, minimum 0
)
```

### Queue with Maximum Size

```python
import redis
r = redis.Redis(decode_responses=True)

bounded_queue_push = r.register_script("""
-- Push to list but maintain maximum size
redis.call('RPUSH', KEYS[1], ARGV[1])
redis.call('LTRIM', KEYS[1], -ARGV[2], -1)
return redis.call('LLEN', KEYS[1])
""")

# Usage: Add to queue, keep max 100 items
queue_size = bounded_queue_push(
    keys=['myqueue'],
    args=['new_item', 100]
)
print(f"Queue size: {queue_size}")
```

### Rate Limiter

```python
import redis
r = redis.Redis(decode_responses=True)

rate_limiter = r.register_script("""
-- Token bucket rate limiter
-- KEYS[1] = rate limit key
-- ARGV[1] = max requests, ARGV[2] = window seconds, ARGV[3] = current timestamp

local max_requests = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Get current count
local current = tonumber(redis.call('GET', KEYS[1]) or 0)

if current >= max_requests then
    return 0  -- Rate limited
end

-- Check if window expired
local window_start = redis.call('HGET', KEYS[1] .. ':window', 'start')
if not window_start or now - tonumber(window_start) > window then
    -- Reset window
    redis.call('SET', KEYS[1], 1)
    redis.call('HSET', KEYS[1] .. ':window', 'start', now)
else
    -- Increment counter
    redis.call('INCR', KEYS[1])
end

-- Set expiry on key
redis.call('EXPIRE', KEYS[1], window + 1)

return 1  -- Allowed
""")

# Usage: Allow max 10 requests per minute
import time
result = rate_limiter(
    keys=['rate_limit:user123'],
    args=[10, 60, int(time.time())]
)
if result:
    print("Request allowed")
else:
    print("Rate limited")
```

### Distributed Lock (Simple)

```python
import redis
import time
r = redis.Redis(decode_responses=True)

acquire_lock = r.register_script("""
-- Try to acquire lock
if redis.call('SETNX', KEYS[1], ARGV[1]) then
    redis.call('EXPIRE', KEYS[1], ARGV[2])
    return 1  -- Acquired
else
    return 0  -- Already locked
end
""")

release_lock = r.register_script("""
-- Release lock only if we own it
if redis.call('GET', KEYS[1]) == ARGV[1] then
    redis.call('DEL', KEYS[1])
    return 1  -- Released
else
    return 0  -- Not owned
end
""")

# Usage
lock_key = 'mylock'
lock_value = f'{time.time()}-{id(threading.current_thread())}'
ttl = 60  # 60 seconds

if acquire_lock(keys=[lock_key], args=[lock_value, ttl]):
    try:
        # Critical section
        print("Lock acquired, doing work...")
    finally:
        release_lock(keys=[lock_key], args=[lock_value])
```

### Sorted Set Leaderboard Update

```python
import redis
r = redis.Redis(decode_responses=True)

update_score = r.register_script("""
-- Update player score and get new rank
local player = KEYS[1]
local score = tonumber(ARGV[1])

redis.call('ZADD', 'leaderboard', score, player)

-- Keep only top 100
redis.call('ZREMRANGEBYRANK', 'leaderboard', 0, -101)

-- Get player's rank (1-based)
local rank = redis.call('ZREVRANK', 'leaderboard', player)
return rank + 1
""")

# Usage
rank = update_score(
    keys=['player:123'],
    args=[1500]  # New score
)
print(f"Player rank: #{rank}")
```

## Cluster Mode Scripting

Lua scripting in Redis Cluster has limitations.

### Supported Operations

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# EVAL/EVALSHA with keys on same slot (using hash tags)
result = rc.eval(
    "return redis.call('GET', KEYS[1])",
    1,
    '{user}123:score'  # Hash tag ensures consistent slot
)

# SCRIPT EXISTS (checks all primaries)
exists = rc.script_exists('sha1hash')
print(f"Script exists on all nodes: {all(exists)}")

# SCRIPT FLUSH (flushes all primaries)
rc.script_flush()

# SCRIPT LOAD (loads to all primaries)
sha = rc.script_load("return 'hello'")
```

### Cluster Limitations

- **Keys must be on same slot**: Use hash tags `{tag}` for multi-key scripts
- **No EVAL_RO/EVALSHA_RO**: Read-only eval commands not supported
- **SCRIPT EXISTS returns list**: One boolean per primary node
- **No scripting in pipelines**: Pipeline scripting not supported in cluster mode

### Zero-Key Scripts in Cluster

Scripts with no keys are sent to a random primary:

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# Script with 0 keys (sent to random primary)
result = rc.eval(
    "return 'hello'",
    0  # No keys
)

# SCRIPT LOAD sends to all primaries
sha = rc.script_load("return redis.call('PING')")
```

## Script Performance Tips

### Use EVALSHA for Repeated Execution

```python
import redis
r = redis.Redis()

# Load script once
sha = r.script_load("return redis.call('GET', KEYS[1])")

# Use SHA for subsequent calls (less data transfer)
result = r.evalsha(sha, 1, 'mykey')
```

### Register Script for Automatic Caching

```python
import redis
r = redis.Redis()

# Script object handles NOSCRIPT and reloading automatically
script = r.register_script("return redis.call('GET', KEYS[1])")

# Just call like a function
result = script(keys=['mykey'], args=[])
```

### Batch Scripts in Pipelines

```python
import redis
r = redis.Redis()

script = r.register_script("return redis.call('INCR', KEYS[1])")

with r.pipeline() as pipe:
    for i in range(100):
        script(keys=[f'key:{i}'], args=[], client=pipe)
    
    results = pipe.execute()  # All scripts executed in one round trip
```

## Debugging Scripts

### Test Script Locally

Use `rlua` or Redis CLI to test scripts:

```bash
# Using redis-cli
redis-cli EVAL "return redis.call('GET', KEYS[1])" 1 mykey

# Using rlua (Redis Lua debugger)
rlua -e "redis.call('GET', 'mykey')"
```

### Add Debug Output to Scripts

```python
import redis
r = redis.Redis(decode_responses=True)

debug_script = r.register_script("""
-- Debug: print values (visible in Redis slow log)
redis.call('LOG', 'Debug: KEYS[1] = ' .. KEYS[1])

local value = redis.call('GET', KEYS[1])
return value
""")

result = debug_script(keys=['mykey'], args=[])
```

### Check Script Cache

```python
import redis
r = redis.Redis()

# Load script
sha = r.script_load("return 'test'")

# Check if cached
exists = r.script_exists(sha)
print(f"Script cached: {exists[0]}")

# Flush and verify
r.script_flush()
exists = r.script_exists(sha)
print(f"After flush: {exists[0]}")  # False
```

## Security Considerations

### Validate Script Inputs

```python
import redis
r = redis.Redis(decode_responses=True)

# Always validate inputs before passing to script
def safe_increment(key, amount):
    # Validate amount is a positive integer
    if not isinstance(amount, int) or amount <= 0:
        raise ValueError("Amount must be positive integer")
    
    return r.eval(
        "return redis.call('INCRBY', KEYS[1], ARGV[1])",
        1, key, amount
    )
```

### Limit Script Execution Time

Long-running scripts block Redis. Set timeouts:

```python
import redis
r = redis.Redis(socket_timeout=5)  # 5 second timeout

# Scripts should complete within socket_timeout
# Consider using BRPOP/BLPOP with short timeouts instead of blocking calls
```

### Avoid Dangerous Commands in Scripts

Don't use these commands in scripts:
- `FLUSHALL`, `FLUSHDB` - Data deletion
- `DEBUG` - Debug commands
- `CONFIG` - Configuration changes
- `SHUTDOWN` - Server shutdown

Redis itself restricts some commands in scripts, but be cautious.
