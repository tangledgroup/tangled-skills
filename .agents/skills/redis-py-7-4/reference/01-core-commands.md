# Redis Core Commands Reference

Complete reference for all Redis command categories supported by redis-py 7.4. Commands are exposed using raw Redis command names as methods on the client instance.

## String Commands

Strings are the basic data type in Redis. All values are binary-safe and can contain any bytes including null bytes.

### Basic Operations

```python
import redis
r = redis.Redis(decode_responses=True)

# SET - Set key value
r.set('key', 'value')                    # True
r.set('key', 'value', nx=True)           # True (only if not exists)
r.set('key', 'value', xx=True)           # None (only if exists)
r.set('key', 'value', ex=3600)           # True (expires in 1 hour)
r.set('key', 'value', px=3600000)        # True (expires in ms)
r.set('key', 'value', keepttl=True)      # True (keep existing TTL)

# MSET - Set multiple keys atomically
r.mset({'key1': 'value1', 'key2': 'value2'})  # True

# MSETNX - Set multiple keys only if not exist
r.msetnx({'key1': 'value1', 'key2': 'value2'})  # True/False

# GET - Get key value
r.get('key')                              # 'value' or None

# MGET - Get multiple keys
r.mget(['key1', 'key2', 'key3'])         # ['value1', 'value2', None]

# GETDEL - Get and delete atomically
r.getdel('key')                           # 'value' (or None)

# GETEX - Get with expiration options
r.getex('key')                            # 'value'
r.getex('key', ex=3600)                   # 'value' (set TTL)
r.getex('key', pxat=1234567890)           # 'value' (set absolute expiry)
r.getex('key', persist=True)              # 'value' (remove TTL)

# GETSET - Get and set atomically (deprecated, use SET with GETEX)
r.getset('key', 'newvalue')              # 'oldvalue'
```

### Conditional Operations

```python
# SETNX - Set if not exists
r.setnx('key', 'value')                  # 1 (set) or 0 (already exists)

# INCR/DECR - Increment/decrement integer
r.incr('counter')                        # 1
r.incrby('counter', 5)                   # 6
r.incrbyfloat('counter', 1.5)            # 7.5
r.decr('counter')                        # 6
r.decrby('counter', 2)                   # 4

# STRLEN - Get string length
r.set('key', 'hello')
r.strlen('key')                          # 5

# APPEND - Append to string
r.append('key', ' world')                # 11 (new length)
r.get('key')                             # 'hello world'

# SUBSTR - Get substring
r.substr('key', 0, 4)                    # 'hello'
```

### Bit Operations

```python
# GETBIT/SETBIT - Get/set bit at position
r.setbit('bitmap', 5, 1)                 # 0 (old value)
r.getbit('bitmap', 5)                    # 1

# BITCOUNT - Count set bits
r.set('key', '\xff\x00')
r.bitcount('key')                        # 8
r.bitcount('key', start=0, end=0)        # 8 (byte range)

# BITOP - Bitwise operations
r.set('key1', '\xff\x00')
r.set('key2', '\xf0\xf0')
r.bitop('AND', 'dest', 'key1', 'key2')   # 2 (length of result)
r.get('dest')                            # b'\xf0\x00'

# BITPOS - Find first bit with value
r.setbit('key', 5, 1)
r.bitpos('key', 1)                       # 5 (first 1-bit)
r.bitpos('key', 0)                       # 0 (first 0-bit)

# BF/CF Bloom/Cuckoo Filters - See Redis Modules reference
```

## Hash Commands

Hashes map fields to values, ideal for objects.

### Basic Operations

```python
import redis
r = redis.Redis(decode_responses=True)

# HSET - Set hash field(s)
r.hset('user:1', 'name', 'Alice')        # 1 (new fields created)
r.hset('user:1', mapping={'name': 'Bob', 'age': '30'})  # 2

# HSETNX - Set field only if not exists
r.hsetnx('user:1', 'name', 'Charlie')    # 0 (field exists)

# HGET - Get single field
r.hget('user:1', 'name')                 # 'Bob'

# HMGET - Get multiple fields
r.hmget('user:1', ['name', 'age'])       # ['Bob', '30']

# HGETALL - Get all fields
r.hgetall('user:1')                      # {'name': 'Bob', 'age': '30'}

# HDEL - Delete field(s)
r.hdel('user:1', 'age')                  # 1 (fields deleted)

# HEXISTS - Check if field exists
r.hexists('user:1', 'name')              # True

# HLEN - Get number of fields
r.hlen('user:1')                         # 1

# HKEYS - Get all field names
r.hkeys('user:1')                        # ['name']

# HVALS - Get all field values
r.hvals('user:1')                        # ['Bob']

# HINCRBY - Increment field by integer
r.hincrby('user:1', 'age', 1)            # 31

# HINCRBYFLOAT - Increment field by float
r.hincrbyfloat('score', 'points', 0.5)   # 10.5

# HSTRLEN - Get string length of field
r.hset('user:1', 'bio', 'Hello')
r.hstrlen('user:1', 'bio')               # 5

# HRANDFIELD - Get random field(s)
r.hrandfield('user:1')                   # 'name'
r.hrandfield('user:1', count=2)          # ['name']
r.hrandfield('user:1', count=2, withvalues=True)  # [['name', 'Bob']]

# HSCAN - Incremental iteration
cursor, fields = r.hscan('user:1', cursor=0, match='n*', count=10)
```

## List Commands

Lists are ordered collections of strings.

### Basic Operations

```python
import redis
r = redis.Redis(decode_responses=True)

# LPUSH - Push to left (head)
r.lpush('mylist', 'one')                 # 1 (length after push)
r.lpush('mylist', 'two', 'three')        # 3

# RPUSH - Push to right (tail)
r.rpush('mylist', 'four')                # 4

# LPUSHX/RPUSHX - Push only if exists
r.lpushx('mylist', 'five')               # 5 (if list exists)

# LPOP - Pop from left
r.lpop('mylist')                         # 'three'
r.lpop('mylist', count=2)                # ['two', 'one']

# RPOP - Pop from right
r.rpop('mylist')                         # 'four'
r.rpop('mylist', count=2)                # ['five', 'six']

# LMOVE - Pop and push between lists
r.lmove('source', 'dest', 'LEFT', 'RIGHT')  # 'value'

# BLMOVE - Blocking move (timeout in seconds)
r.blmove('source', 'dest', 'LEFT', 'RIGHT', timeout=5)

# LINSERT - Insert before/after pivot
r.rpush('mylist', 'a', 'b', 'c')
r.linsert('mylist', 'BEFORE', 'b', 'x')  # 4 (new length)

# LINDEX - Get by index
r.lindex('mylist', 0)                    # 'three' (first element)
r.lindex('mylist', -1)                   # 'four' (last element)

# LSET - Set element at index
r.lset('mylist', 0, 'first')             # OK

# LTRIM - Trim to range
r.ltrim('mylist', 0, 2)                  # OK (keep indices 0-2)

# LREM - Remove elements by value
r.lrem('mylist', 0, 'value')             # count removed (0=all, +n=from left, -n=from right)

# LEN - Get list length
r.llen('mylist')                         # 3

# LRANGE - Get range of elements
r.lrange('mylist', 0, -1)                # ['first', 'second', 'third']
r.lrange('mylist', 1, 2)                 # ['second', 'third']

# BLPOP/BRPOP - Blocking pop (timeout in seconds)
r.blpop('mylist', timeout=5)             # ('mylist', 'value') or None
r.brpop('mylist', timeout=5)             # ('mylist', 'value') or None

# BRPOPLPUSH - Pop from right, push to left (blocking)
r.brpoplpush('source', 'dest', timeout=5)  # 'value'

# LPOS - Find position of value
r.lpos('mylist', 'value')                # index or None
r.lpos('mylist', 'value', rank=2)        # 2nd occurrence
r.lpos('mylist', 'value', count=3)       # [indices...]
```

## Set Commands

Sets are unordered collections of unique strings.

### Basic Operations

```python
import redis
r = redis.Redis(decode_responses=True)

# SADD - Add member(s)
r.sadd('myset', 'one')                   # 1 (new members added)
r.sadd('myset', 'two', 'three')          # 2

# SMEMBERS - Get all members
r.smembers('myset')                      # {'one', 'two', 'three'}

# SREM - Remove member(s)
r.srem('myset', 'one')                   # 1 (members removed)

# SISMEMBER - Check membership
r.sismember('myset', 'two')              # True

# SCARD - Get cardinality (count)
r.scard('myset')                         # 2

# SPOP - Remove and return random member
r.spop('myset')                          # 'two'
r.spop('myset', count=2)                 # ['one']

# SRANDMEMBER - Get random member(s)
r.srandmember('myset')                   # 'value'
r.srandmember('myset', count=3)          # ['v1', 'v2', 'v3']

# SMOVE - Move member between sets
r.smeme('source', 'dest', 'member')      # True (moved) or False

# SINTER - Intersection
r.sinter('set1', 'set2')                 # {'common'}

# SINTERSTORE - Store intersection
r.sinterstore('result', 'set1', 'set2')  # count stored

# SUNION - Union
r.sunion('set1', 'set2')                 # {'all', 'members'}

# SUNIONSTORE - Store union
r.sunionstore('result', 'set1', 'set2')  # count stored

# SDIFF - Difference
r.sdiff('set1', 'set2')                  # {'in set1 only'}

# SDIFFSTORE - Store difference
r.sdiffstore('result', 'set1', 'set2')   # count stored

# SSCAN - Incremental iteration
cursor, members = r.sscan('myset', cursor=0, match='p*', count=10)
```

## Sorted Set Commands

Sorted sets (zsets) are sets with scores that determine ordering.

### Basic Operations

```python
import redis
r = redis.Redis(decode_responses=True)

# ZADD - Add member(s) with score(s)
r.zadd('leaderboard', {'alice': 100, 'bob': 200})  # 2 (new members)
r.zadd('leaderboard', {'alice': 150})              # 0 (updated existing)

# ZCARD - Get cardinality
r.zcard('leaderboard')                             # 2

# ZCOUNT - Count in score range
r.zcount('leaderboard', 0, 150)                    # 1

# ZINCRBY - Increment score
r.zincrby('leaderboard', 'alice', 10)              # 160.0

# ZSCORE - Get member score
r.zscore('leaderboard', 'alice')                   # 160.0

# ZMSCORE - Get multiple scores
r.zmscore('leaderboard', ['alice', 'bob'])         # [160.0, 200.0]

# ZREM - Remove member(s)
r.zrem('leaderboard', 'bob')                       # 1 (removed)

# ZREMRANGEBYRANK - Remove by rank range
r.zremrangebyrank('leaderboard', 0, 0)             # count removed

# ZREMRANGEBYSCORE - Remove by score range
r.zremrangebyscore('leaderboard', '-inf', 100)     # count removed

# ZREMRANGEBYLEX - Remove by lexicographic range
r.zremrangebylex('myzset', '(a', '[m')             # count removed

# ZRANGE - Get members by rank (with options)
r.zrange('leaderboard', 0, -1)                     # ['bob', 'alice'] (high to low)
r.zrange('leaderboard', 0, -1, withscores=True)    # [('bob', 200.0), ('alice', 160.0)]
r.zrange('leaderboard', 0, -1, desc=True)          # ['alice', 'bob'] (low to high)

# ZRANGEBYSCORE - Get members by score range
r.zrangebyscore('leaderboard', 0, 200)             # ['alice', 'bob']
r.zrangebyscore('leaderboard', 0, '+inf', start=0, num=10)

# ZRANGESTORE - Store range in new key
r.zrangestore('top3', 'leaderboard', 0, 2, 'INDEX')  # count stored

# ZREVRANGE - Get members by rank (reverse)
r.zrevrange('leaderboard', 0, -1)                  # ['bob', 'alice']

# ZREVRANGEBYSCORE - Get members by score range (reverse)
r.zrevrangebyscore('leaderboard', '+inf', 0)       # ['bob', 'alice']

# ZRANK - Get rank of member (low to high)
r.zrank('leaderboard', 'alice')                    # 1

# ZREVRANK - Get reverse rank (high to low)
r.zrevrank('leaderboard', 'alice')                 # 0

# ZINTERSTORE - Store intersection
r.zinterstore('result', ['set1', 'set2'])          # count stored
r.zinterstore('result', {'set1': 2, 'set2': 3}, aggregate='SUM')

# ZUNIONSTORE - Store union
r.zunionstore('result', ['set1', 'set2'])          # count stored

# ZPOPMIN/ZPOPMAX - Remove and return min/max members
r.zpopmin('leaderboard')                           # [('alice', 160.0)]
r.zpopmax('leaderboard', count=2)                  # [('bob', 200.0), ('charlie', 180.0)]

# ZSCAN - Incremental iteration
cursor, members = r.zscan('leaderboard', cursor=0, match='a*', count=10)
```

## Stream Commands

Redis Streams implement append-only logs with consumer groups.

See [PubSub and Streams](references/03-pubsub-streams.md) for detailed examples.

```python
import redis
r = redis.Redis(decode_responses=True)

# XADD - Append entry to stream
entry_id = r.xadd('mystream', {'field': 'value'})  # '1609872000000-0'

# XADD with options
r.xadd('mystream', {'data': 'test'}, maxlen=100, approximate=True)  # Trim to 100 entries

# XTRIM - Trim stream
r.xtrim('mystream', max_length=100, approximate=True)  # count trimmed

# XLEN - Get stream length
r.xlen('mystream')                                     # 5

# XREAD - Read entries from stream
r.xread({'mystream': '0'}, count=10, block=1000)       # Stream data

# XRANGE/XREVRANGE - Get entries by ID range
r.xrange('mystream', start='-', end='+', count=10)    # All entries (newest last)
r.xrevrange('mystream', start='+', end='-', count=10)  # Newest first

# XDEL - Delete entry(s)
r.xdel('mystream', 'entry-id-1', 'entry-id-2')        # count deleted

# XACK - Acknowledge processed entry
r.xack('mystream', 'mygroup', 'entry-id')             # count acknowledged

# XPENDING - Get pending entries (consumed but not acked)
r.xpending('mystream', 'mygroup')                     # Pending summary

# XAUTOCLAIM - Claim pending entries
r.xautoclaim('mystream', 'mygroup', 'consumer1', min_idle=3600000, start='0')

# XGROUP CREATE - Create consumer group
r.xgroup_create('mystream', 'mygroup', id='0')        # OK

# XGROUP SETID - Set group last ID
r.xgroup_setid('mystream', 'mygroup', id='entry-id')  # OK

# XREADGROUP - Read as consumer group
r.xreadgroup('mygroup', 'consumer1', streams={'mystream': '>'}, count=10, block=1000)

# XINFO - Stream/group/consumer information
r.xinfo_stream('mystream')                            # Stream info
r.xinfo_consumers('mystream', 'mygroup')              # Consumer list
r.xinfo_groups('mystream')                            # Group list
```

## HyperLogLog Commands

HyperLogLogs approximate cardinality with minimal memory.

```python
import redis
r = redis.Redis()

# PFADD - Add element(s) to HyperLogLog
r.pfadd('hll', 'element1')                           # 1 (new HLL created)
r.pfadd('hll', 'element2', 'element3')              # 0 (HLL exists)

# PFCOUNT - Get approximate cardinality
r.pfcount('hll')                                     # 3
r.pfcount('hll1', 'hll2', 'hll3')                    # Combined count

# PFMERGE - Merge multiple HyperLogLogs
r.pfmerge('dest', 'hll1', 'hll2', 'hll3')            # OK
```

## Geo Commands

Geospatial indexing using sorted sets.

```python
import redis
r = redis.Redis(decode_responses=True)

# GEOADD - Add location(s)
r.geoadd('cities', 13.361389, 38.115556, 'Palermo')  # 1 (added)
r.geoadd('cities', 15.087269, 37.502669, 'Catania')  # 1

# GEOPOS - Get coordinates
r.geopos('cities', 'Palermo')                        # [(13.361389, 38.115556)]

# GEODIST - Distance between locations
r.geodist('cities', 'Palermo', 'Catania')            # 166274.12 (meters)
r.geodist('cities', 'Palermo', 'Catania', unit='km') # 166.27

# GEOHASH - Get geohash string(s)
r.geohash('cities', 'Palermo', 'Catania')            # ['sxbp...', 'sxkw...']

# GEORADIUS - Radius search
results = r.georadius('cities', 15, 37, 20, 'km')    # [(city, dist, hash)]
r.georadius('cities', 15, 37, 20, 'km', withdist=True, withcoord=True, withhash=True)

# GEORADIUSBYMEMBER - Radius search from member
r.georadiusbymember('cities', 'Palermo', 200, 'km')  # [(city, dist)]

# GEOSEARCH - Search by location/radius/box
r.geosearch('cities', 15, 37, radius=200, unit='km') # ['Palermo', 'Catania']
r.geosearch('cities', 'Palermo', radius=200, unit='km', store='nearby')

# GEOSEARCHSTORE - Store search results
r.geosearchstore('nearby', 'cities', 15, 37, radius=200, unit='km')  # count stored
```

## Bitmap Commands (Module)

Bitmap operations on string values.

See [Redis Modules](references/06-redis-modules.md) for BITMAPS module commands.

## Key Commands

Operations that work on any key type.

```python
import redis
r = redis.Redis(decode_responses=True)

# EXISTS - Check if key exists
r.exists('key')                                     # 1 (or count of keys)

# DEL - Delete key(s)
r.delete('key')                                     # 1 (keys deleted)
r.delete('key1', 'key2', 'key3')                   # count deleted

# EXPIRE - Set expiration in seconds
r.expire('key', 3600)                               # True (TTL set)
r.expire('key', 3600, nx=True)                      # True (only if no TTL)

# PEXPIRE - Set expiration in milliseconds
r.pexpire('key', 3600000)                           # True

# EXPIREAT - Set absolute expiration (Unix timestamp)
r.expireat('key', 1609872000)                       # True

# PEXPIREAT - Set absolute expiration (Unix ms timestamp)
r.pexpireat('key', 1609872000000)                   # True

# TTL - Time to live in seconds
r.ttl('key')                                        # 3600 or -1 (no TTL) or -2 (doesn't exist)

# PTTL - Time to live in milliseconds
r.pttl('key')                                       # 3600000

# PERSIST - Remove expiration
r.persist('key')                                    # True (TTL removed)

# TYPE - Get key type
r.type('mystring')                                  # 'string'
r.type('mylist')                                    # 'list'

# RENAMENX - Rename only if new key doesn't exist
r.renamenx('old', 'new')                            # True/False

# MOVE - Move key to database
r.move('key', db=1)                                 # True (moved)

# RANDOMKEY - Return random key
r.random_key()                                      # 'some-key' or None

# SCAN - Incremental iteration
cursor, keys = r.scan(cursor=0, match='user:*', count=100)

# SORT - Sort list/set/zset values
r.sort('mylist', start=0, num=10, desc=True, alpha=True)

# DUMP/RESTORE - Serialize/deserialize key
data = r.dump('key')                                # Binary data
r.restore('newkey', 0, data)                        # OK

# UNLINK - Async delete (non-blocking)
r.unlink('key')                                     # count deleted

# FLUSHDB - Delete all keys in current database
r.flushdb()                                         # True

# FLUSHALL - Delete all keys in all databases
r.flushall()                                        # True

# WAIT - Wait for replication
r.wait(1, 1000)                                     # 1 (replicas reached)
```

## Object Commands

Object-level operations.

```python
import redis
r = redis.Redis(decode_responses=True)

# OBJECT ENCODING - Get internal encoding
r.object_encoding('key')                            # 'embstr' or 'listpack'

# OBJECT FREQ - Get LRU frequency counter
r.object_freq('key')                                # 5 (hits)

# OBJECT IDLETIME - Get idle time in seconds
r.object_idletime('key')                            # 3600

# OBJECT REFCOUNT - Get reference count
r.object_refcount('key')                            # 1
```

## Slow Log Commands

Query slow execution log.

```python
import redis
r = redis.Redis(decode_responses=True)

# SLOWLOG GET - Get slow log entries
entries = r.slowlog_get(10)                         # Last 10 entries

# SLOWLOG LEN - Get entry count
r.slowlog_len()                                     # 50

# SLOWLOG RESET - Clear slow log
r.slowlog_reset()                                   # OK
```

## Client Commands

Connection and client management.

```python
import redis
r = redis.Redis(decode_responses=True)

# CLIENT LIST - Get connected clients
clients = r.client_list()                           # List of client info dicts

# CLIENT INFO - Get current client info
info = r.client_info()                              # Client info dict

# CLIENT KILL - Kill client connection
r.client_kill('127.0.0.1:12345')                    # OK
r.client_kill(ip='127.0.0.1', port=12345, user='default')

# CLIENT PAUSE - Pause all clients
r.client_pause(1000)                                # OK (pause 1 second)
r.client_pause(1000, 'write')                       # OK (pause writes only)

# CLIENT UNPAUSE - Resume clients
r.client_unpause()                                  # OK

# CLIENT GETNAME - Get connection name
r.client_setname('myapp')                           # OK
name = r.client_getname()                           # 'myapp'

# CLIENT TRACKING - Enable client-side caching
r.client_tracking('on')                             # OK

# CLIENT UNBLOCK - Unblock blocked client
r.client_unblock('127.0.0.1:12345', error=True)     # 1 (unblocked)

# CLIENT REPLY - Control server replies
r.client_reply('ON')                                # OK
```

## Server Commands

Server-level operations and monitoring.

```python
import redis
r = redis.Redis(decode_responses=True)

# INFO - Get server information
info = r.info()                                     # Dict with all sections
info = r.info('memory')                             # Memory section only

# CONFIG GET/SET - Configuration management
config = r.config_get('*timeout*')                  # Dict of timeout settings
r.config_set({'maxmemory': '1gb', 'timeout': 0})    # OK

# CONFIG RESETSTAT - Reset statistics
r.config_resetstat()                                # OK

# CONFIG REWRITE - Rewrite config file
r.config_rewrite()                                  # OK

# BGSAVE - Background save RDB
r.bgsave()                                          # 'Background saving started'

# LASTSAVE - Get last save timestamp
timestamp = r.lastsave()                            # Unix timestamp

# SHUTDOWN - Shutdown server (dangerous!)
# r.shutdown()                                      # Connection closed

# DBSIZE - Get key count
count = r.dbsize()                                  # 1000

# PING - Test connection
r.ping()                                            # True or 'PONG'

# ECHO - Echo message
r.echo('hello')                                     # 'hello'

# TIME - Get server time
time = r.time()                                     # (seconds, microseconds)

# MODULE LIST - List loaded modules
modules = r.module_list()                           # List of module info dicts

# MODULE LOAD/UNLOAD - Load/unload module
r.module_load('/path/to/module.so')                 # OK
r.module_unload('modulename')                       # OK

# ACL LOG - Access control log
r.acl_log(10)                                       # Last 10 entries
r.acl_log_reset()                                   # OK

# DEBUG - Debug commands (use with caution!)
r.debug_object('key')                               # Object info
```

## Scripting Commands

Lua scripting support.

See [Lua Scripting](references/05-lua-scripting.md) for detailed examples.

```python
import redis
r = redis.Redis()

# EVAL - Execute Lua script
result = r.eval("return ARGV[1] .. KEYS[1]", 1, 'key', 'value')

# EVALSHA - Execute by SHA1 hash
sha = r.script_load("return ARGV[1]")
result = r.evalsha(sha, 1, 'key', 'value')

# SCRIPT EXISTS - Check if script exists
exists = r.script_exists('sha1hash')                # [True/False]

# SCRIPT FLUSH - Flush all scripts
r.script_flush()                                    # OK
r.script_flush('SYNC')                              # OK (sync flush)

# SCRIPT LOAD - Load script into cache
sha = r.script_load("return 'hello'")               # SHA1 hash
```

## Module Commands

Redis module support.

See [Redis Modules](references/06-redis-modules.md) for complete reference covering:

- **Bloom Filters**: `r.bf().create()`, `r.bf().add()`, `r.cf().reserve()`
- **JSON**: `r.json().set()`, `r.json().get()`, `r.json().mget()`
- **Search**: `r.ft().create_index()`, `r.ft().search()`, `r.ft().aggregate()`
- **TimeSeries**: `r.ts().create()`, `r.ts().add()`, `r.ts().range()`
