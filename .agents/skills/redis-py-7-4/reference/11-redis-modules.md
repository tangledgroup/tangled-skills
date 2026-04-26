# Redis Modules

## Accessing Module Commands

Module commands are accessed through namespace methods on the `Redis` client:

```python
import redis
r = redis.Redis()

# Bloom filter
r.bf().create('bloom', 0.01, 1000)
r.bf().add('bloom', 'foo')

# Cuckoo filter
r.cf().create('cuckoo', 1000)
r.cf().add('cuckoo', 'filter')

# Count-Min Sketch
r.cms().initbydim('dim', 1000, 5)
r.cms().incrby('dim', ['foo'], [5])
r.cms().info('dim')

# TopK
r.topk().reserve('mytopk', 3, 50, 4, 0.9)
r.topk().info('mytopk')
```

## RedisBloom (Probabilistic Data Structures)

### Bloom Filter (`r.bf()`)

Space-efficient membership testing:

```python
# Create with 1% error rate, capacity for 1000 items
r.bf().create('myfilter', 0.01, 1000)

# Add items
r.bf().add('myfilter', 'item1')
r.bf().madd('myfilter', 'item2', 'item3')

# Check existence (may have false positives, never false negatives)
r.bf().exists('myfilter', 'item1')   # 1
r.bf().mexists('myfilter', 'item1', 'unknown')  # [1, 0]

# Info
r.bf().info('myfilter')
```

Commands: `add`, `madd`, `exists`, `mexists`, `create`, `reserve`, `insert`, `info`, `card`, `scandump`, `loadchunk`.

### Cuckoo Filter (`r.cf()`)

Like Bloom filters but supports deletion:

```python
r.cf().create('mycf', 1000)
r.cf().add('mycf', 'item')
r.cf().exists('mycf', 'item')  # 1
r.cf().delete('mycf', 'item')   # 1
```

Commands: `add`, `addnx`, `exists`, `del`, `info`, `reserve`, `scandump`, `loadchunk`.

### Count-Min Sketch (`r.cms()`)

Frequency estimation:

```python
r.cms().initbydim('mysketch', 1000, 5)
r.cms().incrby('mysketch', ['item1'], [1])
count = r.cms().query('mysketch', 'item1')
```

### TopK (`r.topk()`)

Track most frequent items:

```python
r.topk().reserve('mytopk', 3, 50, 4, 0.9)
r.topk().add('mytopk', 'item1')
items = r.topk().list('mytopk')
```

## RedisJSON

Store and query JSON documents:

```python
# Set a JSON document
r.json().set('doc:', '$', {'name': 'John', 'age': 30})

# Get the document
data = r.json().get('doc:', '$')

# Update a field
r.json().set('doc:', '$.age', 31)

# Get a specific field
age = r.json().get('doc:', '$.age')
```

## RediSearch

Full-text search and indexing:

```python
from redis.commands.search.field import TextField
from redis.commands.search.query import Query
from redis.commands.search.index_definition import IndexDefinition

# Create index
r.ft().create_index(
    (TextField('name'), TextField('lastname')),
    definition=IndexDefinition(prefix=['test:']),
)

# Add documents
r.hset('test:1', mapping={'name': 'James', 'lastname': 'Brown'})

# Search with default DIALECT 2
query = Query('@name:James')
result = r.ft().search(query)

# Explicit dialect
result = r.ft().search(Query('@name:James').dialect(1))
```

Default search dialect is 2 from redis-py 6.0+. Override with `.dialect(n)`.

## RedisTimeSeries

Time series data storage:

```python
# Create a time series
r.ts().create('sensor:temp', retention_msecs=3600000)

# Add samples
r.ts().add('sensor:temp', 1234567890, 25.5)
r.ts().add('sensor:temp', '*', 26.0)  # '*' = current timestamp

# Query range
range_data = r.ts().range('sensor:temp', from_timestamp=1234567890, to_timestamp=1234567900)

# Get latest value
latest = r.ts().get('sensor:temp')
```

## Multi-Dialect for Search

```python
from redis.commands.search.query import Query

# Default dialect 2
q = Query('@field:value')

# Override to dialect 1
q = Query('@field:value').dialect(1)

# Use latest dialect
q = Query('@field:value').dialect(3)
```
