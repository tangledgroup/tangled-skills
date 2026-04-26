# Pub/Sub and Streams

## Pub/Sub

Subscribe to channels:

```python
r = redis.Redis()
p = r.pubsub()
p.subscribe('my-channel', 'another-channel')

# Read messages
message = p.get_message()
# {'pattern': None, 'type': 'subscribe', 'channel': b'my-channel', 'data': 1}
```

Publish to a channel:

```python
r.publish('my-channel', 'hello world')
```

Pattern-based subscription (glob-style):

```python
p.psubscribe('news:*')
message = p.get_message()
# {'pattern': b'news:*', 'type': 'psubscribe', 'channel': None, 'data': 1}
```

Unsubscribe:

```python
p.unsubscribe('my-channel')
p.punsubscribe('news:*')
```

Ignore subscribe confirmations:

```python
message = p.get_message(ignore_subscribe_messages=True)
```

Listen loop:

```python
for message in p.listen():
    if message['type'] == 'message':
        print(message['data'])
```

## Redis Streams

Add entries to a stream with `xadd`:

```python
from time import time

r.xadd('mystream', {'field1': 'value1', 'ts': str(time())})
# b'1692345678901-0'
```

Read entries with `xread`:

```python
# Read from the beginning (0)
entries = r.xread(streams={'mystream': 0}, count=10)

# Read only new entries ($)
entries = r.xread(streams={'mystream': '$'}, block=5000, count=1)

# Read from a specific ID
entries = r.xread(streams={'mystream': '1692345678901-0'}, count=5)
```

Read multiple streams:

```python
entries = r.xread(
    streams={'stream1': 0, 'stream2': 0},
    count=1
)
for stream_name, stream_entries in entries:
    for msg_id, fields in stream_entries:
        print(f"{stream_name}: {msg_id} -> {fields}")
```

Get stream length:

```python
length = r.xlen('mystream')
```

Delete entries:

```python
r.xdel('mystream', '1692345678901-0')
```

Trim stream to max length:

```python
r.xadd('mystream', {'data': 'value'}, maxlen=1000, approximate=True)
```

## Stream Consumer Groups

Create a consumer group:

```python
r.xgroup_create('mystream', 'mygroup', id='0', mkstream=True)
```

Read from a consumer group:

```python
entries = r.xreadgroup(
    groupname='mygroup',
    consumername='consumer1',
    streams={'mystream': '>'},  # '>' = only new entries
    count=10
)
```

Acknowledge processed messages:

```python
r.xack('mystream', 'mygroup', '1692345678901-0')
```

Read pending (unacknowledged) messages:

```python
pending = r.xpending('mystream', 'mygroup')
```

Claim messages from another consumer (for failover):

```python
claimed = r.xclaim(
    'mystream', 'mygroup', 'consumer2',
    min_idle_time=60000,  # 60 seconds
    message_ids=['1692345678901-0']
)
```
