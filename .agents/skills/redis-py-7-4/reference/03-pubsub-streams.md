# PubSub Messaging and Redis Streams

Redis provides two messaging paradigms: traditional Pub/Sub for fire-and-forget messaging, and Streams for persistent, reliable message queues with consumer groups.

## Pub/Sub Overview

Pub/Sub implements a simple publish-subscribe pattern where clients subscribe to channels and receive messages published to those channels.

### Basic Publishing and Subscribing

```python
import redis
r = redis.Redis(decode_responses=True)

# Publisher (regular client)
r.publish('news', 'Breaking news!')  # Returns number of subscribers

# Subscriber (pubsub client)
pubsub = r.pubsub()
pubsub.subscribe('news', 'sports')    # Subscribe to channels
pubsub.psubscribe('alerts:*')         # Pattern subscription

# Listen for messages
message = pubsub.get_message(timeout=1)
# {'type': 'subscribe', 'channel': 'news', 'data': 1}

# Receive published message
message = pubsub.get_message()
# {'type': 'message', 'channel': 'news', 'data': 'Breaking news!'}
```

### Pattern Subscriptions

Pattern subscriptions match channels using glob-style patterns:

```python
import redis
r = redis.Redis(decode_responses=True)

pubsub = r.pubsub()
pubsub.psubscribe('news:*', 'alerts:urgent')

# Subscribe confirmation
message = pubsub.get_message()
# {'type': 'psubscribe', 'pattern': 'news:*', 'data': 1}

# Published message matching pattern
r.publish('news:world', 'World news')
message = pubsub.get_message()
# {'type': 'pmessage', 'pattern': 'news:*', 'channel': 'news:world', 'data': 'World news'}
```

### Message Types

PubSub messages are dictionaries with these keys:

| Key | Description | Values |
|-----|-------------|--------|
| type | Message type | 'subscribe', 'unsubscribe', 'psubscribe', 'punsubscribe', 'message', 'pmessage' |
| channel | Channel name | Bytes string (or None for pmessage) |
| pattern | Matching pattern | Bytes string (only for 'pmessage') or None |
| data | Message content | Published message or subscription count |

```python
import redis
r = redis.Redis(decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('mychannel')

# Subscribe confirmation
msg = pubsub.get_message()
print(msg['type'])    # 'subscribe'
print(msg['channel']) # 'mychannel'
print(msg['data'])    # 1 (number of subscriptions)

# Message received
r.publish('mychannel', 'Hello!')
msg = pubsub.get_message()
print(msg['type'])    # 'message'
print(msg['channel']) # 'mychannel'
print(msg['data'])    # 'Hello!'
```

### Callback Handlers

Register callbacks for automatic message handling:

```python
import redis
r = redis.Redis(decode_responses=True)

def news_handler(message):
    """Handle news channel messages."""
    print(f"News: {message['data']}")

def sports_handler(message):
    """Handle sports channel messages."""
    print(f"Sports: {message['data']}")

pubsub = r.pubsub()
pubsub.subscribe(**{
    'news': news_handler,
    'sports': sports_handler
})

# Subscribe confirmations (no handlers)
pubsub.get_message()  # {'type': 'subscribe', ...}
pubsub.get_message()  # {'type': 'subscribe', ...}

# Messages trigger handlers automatically
r.publish('news', 'Breaking news!')
message = pubsub.get_message()  # None (handler was called)
print(message)  # None - handler already processed it
```

### Ignoring Subscribe Messages

Skip subscription confirmation messages:

```python
import redis
r = redis.Redis(decode_responses=True)

# Ignore subscribe/unsubscribe confirmations
pubsub = r.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe('channel1', 'channel2')

# No subscribe messages to read, only actual published messages
message = pubsub.get_message(timeout=5)  # Waits for published message only
```

### Unsubscribing

```python
import redis
r = redis.Redis()

pubsub = r.pubsub()
pubsub.subscribe('channel1', 'channel2')
pubsub.psubscribe('alerts:*')

# Unsubscribe from specific channels
pubsub.unsubscribe('channel1')

# Unsubscribe all channels
pubsub.unsubscribe()

# Unsubscribe from pattern
pubsub.punsubscribe('alerts:*')

# Unsubscribe all patterns
pubsub.punsubscribe()
```

### PubSub in Separate Thread

Run pubsub listener in background thread:

```python
import redis
import threading
import time

r = redis.Redis(decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe('mychannel')

def listen():
    """Background listener function."""
    while True:
        message = pubsub.get_message(timeout=1)
        if message and message['type'] == 'message':
            print(f"Received: {message['data']}")
        
        # Check stop flag
        if stop_event.is_set():
            break

stop_event = threading.Event()
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

# Publish from main thread
time.sleep(1)
r.publish('mychannel', 'Hello from main thread!')

# Stop listener after 5 seconds
time.sleep(5)
stop_event.set()
listener_thread.join()
pubsub.close()
```

### PubSub Timeouts and Blocking

```python
import redis
r = redis.Redis(decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe('mychannel')

# Non-blocking (returns immediately)
message = pubsub.get_message(timeout=0)  # None if no message

# Blocking with timeout
message = pubsub.get_message(timeout=5)  # Wait up to 5 seconds
# Returns message dict or None if timeout

# Infinite blocking (use with caution)
# message = pubsub.get_message()  # Blocks forever until message arrives
```

### PubSub Limitations

- **No persistence**: Messages are delivered only to currently subscribed clients
- **No acknowledgment**: No confirmation that messages were received
- **No history**: Cannot retrieve past messages
- **Pattern limitations**: In cluster mode, pattern pubsub has slot hashing issues

For reliable messaging with persistence, use Redis Streams instead.

## Redis Streams

Streams provide persistent, append-only logs with consumer groups for reliable message processing.

### Creating and Appending to Streams

```python
import redis
r = redis.Redis(decode_responses=True)

# Append entry to stream (auto-generated ID)
entry_id = r.xadd('mystream', {'message': 'Hello', 'type': 'info'})
# '1609872000000-0' (timestamp-sequence)

# Append with custom ID
entry_id = r.xadd('mystream', '*', {'message': 'World', 'priority': 'high'})

# Multiple entries at once
r.xadd('mystream', {
    'field1': 'value1',
    'field2': 'value2',
    'field3': 'value3'
})

# Append with trimming (max 1000 entries)
r.xadd('mystream', {'data': 'test'}, maxlen=1000, approximate=True)
```

### Stream Entry IDs

Stream entry IDs have format: `timestamp-sequence`

```python
import redis
r = redis.Redis(decode_responses=True)

# Auto-generated ID (current time)
id1 = r.xadd('mystream', '*', {'data': 'auto'})
print(id1)  # '1609872000123-0'

# Custom ID (must be greater than last entry)
id2 = r.xadd('mystream', '1609872000200-0', {'data': 'custom'})

# Special IDs:
# '*' - Auto-generate ID
# '-' - Use ID of last entry (for trimming)
# '0' - Start from beginning
# '+' - End of stream
```

### Reading from Streams

```python
import redis
r = redis.Redis(decode_responses=True)

# Read all entries from start
result = r.xread({'mystream': '0'}, count=10)
# [[('mystream', [('1609872000000-0', {'message': 'Hello'})])]]

# Read from specific ID (exclusive)
result = r.xread({'mystream': '1609872000000-0'}, count=5)

# Read multiple streams
result = r.xread({
    'stream1': '0',
    'stream2': '0'
}, count=10)

# Blocking read (wait for new entries)
result = r.xread({'mystream': '0'}, count=5, block=5000)  # Wait up to 5 seconds

# Read latest N entries
result = r.xrevrange('mystream', '+', '-', count=10)
```

### Stream Range Queries

```python
import redis
r = redis.Redis(decode_responses=True)

# Get entries by ID range (inclusive)
entries = r.xrange('mystream', start='-', end='+')  # All entries
entries = r.xrange('mystream', '1609872000000-0', '1609872001000-0')

# Reverse range (newest first)
entries = r.xrevrange('mystream', '+', '-', count=10)  # Latest 10

# Range with filters
entries = r.xrange('mystream', '(', '1609872001000-0')  # Exclusive end

# Stream length
length = r.xlen('mystream')  # Number of entries
```

### Trimming Streams

Control stream size to prevent unbounded growth:

```python
import redis
r = redis.Redis(decode_responses=True)

# Trim to max length (exact)
trimmed = r.xtrim('mystream', max_length=1000)  # Count trimmed

# Trim with approximation (faster)
trimmed = r.xtrim('mystream', max_length=1000, approximate=True)

# Trim by time (keep entries from last hour)
import time
one_hour_ago = int((time.time() - 3600) * 1000)
trimmed = r.xtrim('mystream', minid=f'{one_hour_ago}-0')

# Trim during append (more efficient)
r.xadd('mystream', {'data': 'new'}, maxlen=1000, approximate=True)
```

### Deleting Entries

```python
import redis
r = redis.Redis(decode_responses=True)

# Delete specific entries
deleted = r.xdel('mystream', 'entry-id-1', 'entry-id-2')  # Count deleted

# Delete by range (using trim)
r.xtrim('mystream', minid='old-entry-id')
```

## Consumer Groups

Consumer groups enable multiple consumers to process stream entries, with automatic tracking of which entries each consumer has processed.

### Creating Consumer Groups

```python
import redis
r = redis.Redis(decode_responses=True)

# Create consumer group (start from beginning)
r.xgroup_create('mystream', 'mygroup', id='0')  # 'OK'

# Create group starting from latest entry
r.xgroup_create('mystream', 'mygroup', id='$')  # 'OK' (new entries only)

# Create group if not exists
r.xgroup_create('mystream', 'mygroup', id='0', mkstream=True)

# Set group ID (reset progress)
r.xgroup_setid('mystream', 'mygroup', id='entry-id')

# Destroy consumer group
r.xgroup_destroy('mystream', 'mygroup')  # True
```

### Reading as Consumer Group

```python
import redis
r = redis.Redis(decode_responses=True)

# Read new entries ( '>' means unread entries )
result = r.xreadgroup(
    groupname='mygroup',
    consumername='consumer1',
    streams={'mystream': '>'},
    count=10,
    block=1000  # Wait up to 1 second for entries
)

# Result format:
# [[('mystream', [
#     ('entry-id-1', {'field1': 'value1'}),
#     ('entry-id-2', {'field2': 'value2'})
#   ])]]

# Read pending entries (already delivered but not acked)
result = r.xreadgroup(
    groupname='mygroup',
    consumername='consumer1',
    streams={'mystream': 'id-of-last-read-entry'},
    count=10
)
```

### Acknowledging Entries

Mark entries as processed:

```python
import redis
r = redis.Redis(decode_responses=True)

# Acknowledge single entry
acked = r.xack('mystream', 'mygroup', 'entry-id-1')  # 1 (count acked)

# Acknowledge multiple entries
acked = r.xack('mystream', 'mygroup', 'id1', 'id2', 'id3')  # 3

# Entries must be acknowledged to remove from pending list
```

### Pending Entries

Track entries that were delivered but not yet acknowledged:

```python
import redis
r = redis.Redis(decode_responses=True)

# Get pending entry count and IDs
pending = r.xpending('mystream', 'mygroup')
# {'num_items': 5, 'first': 'entry-id-1', 'last': 'entry-id-5', 'consumers': {...}}

# Get detailed pending entries
details = r.xpending('mystream', 'mygroup', start='-', end='+', count=10)
# [
#   {'entry_id': 'entry-id-1', 'consumer': 'consumer1', 'delivery_time': 1609872000, 'delivery_count': 2},
#   ...
# ]

# Get pending for specific consumer
details = r.xpending('mystream', 'mygroup', start='-', end='+', count=10, consumer='consumer1')
```

### Claiming Pending Entries

Reassign pending entries to different consumers:

```python
import redis
r = redis.Redis(decode_responses=True)

# Claim entries idle for more than 60 seconds (60000 ms)
claimed = r.xautoclaim(
    'mystream',
    'mygroup',
    'consumer2',
    min_idle_time=60000,  # 60 seconds in milliseconds
    start='-'  # Start from beginning
)
# {'next_id': 'entry-id-5', 'entries': [...]}

# Claim specific entries
claimed = r.xclaim(
    'mystream',
    'mygroup',
    'consumer2',
    min_idle_time=60000,
    ids=['entry-id-1', 'entry-id-2']
)
# [('entry-id-1', {...}), ('entry-id-2', {...})]

# Claim with idle time override (force claim regardless of idle time)
claimed = r.xclaim(
    'mystream',
    'mygroup',
    'consumer2',
    min_idle_time=0,
    ids=['entry-id-1'],
    force=True
)
```

### Consumer Management

```python
import redis
r = redis.Redis(decode_responses=True)

# Get consumer group info
info = r.xinfo_groups('mystream')
# [
#   {'name': 'mygroup', 'consumers': 3, 'pending': 5, 'last-delivered-id': 'entry-id-100'},
#   ...
# ]

# Get consumer details
consumers = r.xinfo_consumers('mystream', 'mygroup')
# [
#   {'name': 'consumer1', 'pending': 2, 'idle': 3600000},
#   {'name': 'consumer2', 'pending': 3, 'idle': 1800000},
#   ...
# ]

# Delete consumer from group
r.xgroup_createconsumer('mystream', 'mygroup', 'newconsumer')
r.xgroup_delconsumer('mystream', 'mygroup', 'oldconsumer')  # Count pending entries lost
```

### Stream Information

```python
import redis
r = redis.Redis(decode_responses=True)

# Get stream metadata
info = r.xinfo_stream('mystream')
# {
#   'length': 1000,
#   'radix-tree-keys': 100,
#   'radix-tree-nodes': 50,
#   'last-generated-entry-id': '1609872000000-99',
#   'first-entry': ('1609872000000-0', {...}),
#   'last-entry': ('1609872000000-99', {...}),
#   'groups': 2
# }
```

## Complete Consumer Example

Full example of stream consumer with error handling:

```python
import redis
import json
import time
from datetime import datetime

r = redis.Redis(decode_responses=True)
STREAM_NAME = 'events'
GROUP_NAME = 'processors'
CONSUMER_NAME = f'worker-{datetime.now().strftime("%H%M%S")}'

# Ensure group exists
try:
    r.xgroup_create(STREAM_NAME, GROUP_NAME, id='0', mkstream=True)
except redis.ResponseError:
    pass  # Group already exists

def process_event(entry):
    """Process a single stream entry."""
    entry_id, fields = entry
    
    print(f"Processing {entry_id}: {fields}")
    
    # Your business logic here
    event_type = fields.get('type')
    payload = fields.get('payload')
    
    if event_type == 'user_created':
        handle_user_creation(json.loads(payload))
    elif event_type == 'order_placed':
        handle_order_placement(json.loads(payload))
    
    return True

def worker():
    """Main consumer loop."""
    print(f"Consumer {CONSUMER_NAME} started")
    
    while True:
        try:
            # Read new entries (blocking)
            result = r.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={STREAM_NAME: '>'},
                count=10,
                block=1000  # Wait up to 1 second
            )
            
            if not result:
                continue
            
            # Process each stream's entries
            for stream_name, entries in result[0]:
                for entry in entries:
                    try:
                        success = process_event(entry)
                        
                        if success:
                            # Acknowledge successful processing
                            r.xack(STREAM_NAME, GROUP_NAME, entry[0])
                            print(f"Acked {entry[0]}")
                        else:
                            print(f"Failed to process {entry[0]}, will retry")
                            
                    except Exception as e:
                        print(f"Error processing {entry[0]}: {e}")
                        # Don't ack - entry will be retried
                        
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except redis.ConnectionError as e:
            print(f"Connection error: {e}, retrying in 5 seconds")
            time.sleep(5)

if __name__ == '__main__':
    worker()
```

## Producer Example

Stream producer with batch operations:

```python
import redis
import json
import time
from datetime import datetime

r = redis.Redis(decode_responses=True)
STREAM_NAME = 'events'

def publish_event(event_type, payload, **metadata):
    """Publish event to stream."""
    entry_data = {
        'type': event_type,
        'payload': json.dumps(payload),
        'timestamp': datetime.now().isoformat(),
        **metadata
    }
    
    # Append with automatic trimming (keep 10000 entries)
    entry_id = r.xadd(
        STREAM_NAME,
        entry_data,
        maxlen=10000,
        approximate=True
    )
    
    print(f"Published {event_type} as {entry_id}")
    return entry_id

def publish_batch(events):
    """Publish multiple events efficiently."""
    pipe = r.pipeline()
    
    for event in events:
        entry_data = {
            'type': event['type'],
            'payload': json.dumps(event['payload']),
            'timestamp': datetime.now().isoformat()
        }
        
        # Use pipeline to batch xadd commands
        pipe.xadd(STREAM_NAME, entry_data)
    
    results = pipe.execute()
    return results

# Usage
publish_event('user_created', {'user_id': 123, 'name': 'Alice'})
publish_event('order_placed', {'order_id': 456, 'total': 99.99})

# Batch publish
events = [
    {'type': 'item_viewed', 'payload': {'item_id': 1}},
    {'type': 'item_viewed', 'payload': {'item_id': 2}},
    {'type': 'cart_added', 'payload': {'item_id': 3}}
]
publish_batch(events)
```

## Stream vs PubSub Comparison

| Feature | Pub/Sub | Streams |
|---------|---------|---------|
| Persistence | No | Yes |
| Consumer Groups | No | Yes |
| Message History | No | Yes (configurable) |
| Acknowledgments | No | Yes |
| Multiple Consumers | All get all messages | Each message to one consumer |
| Reliability | Best effort | Guaranteed delivery |
| Backpressure | None | Configurable trimming |
| Use Case | Real-time notifications, broadcasting | Task queues, event sourcing, logging |

## PubSub in Cluster Mode

Pub/Sub behavior differs in Redis Cluster:

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host='localhost', port=6379, decode_responses=True)

# Channel-based pubsub (uses hash slot)
pubsub = rc.pubsub()
pubsub.subscribe('mychannel')

# Pattern pubsub has limitations in cluster mode
# due to slot hashing - not recommended

# Pub/sub is tied to specific node based on channel hash
```

Cluster pubsub limitations:
- Pattern subscriptions (`PSUBSCRIBE`) have slot resolution issues
- Messages only delivered to subscribers on same node as publisher
- Use streams for reliable cluster messaging
