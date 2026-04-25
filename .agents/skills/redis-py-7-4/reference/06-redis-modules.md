# Redis Modules

Redis modules extend Redis functionality. redis-py provides clients for popular modules: RedisBloom (probabilistic data structures), RedisJSON, RediSearch, and RedisTimeSeries.

## Module Installation

Install optional dependencies for module support:

```bash
pip install redis  # Core client (includes module commands)
```

Most module commands work with the base `redis` package. Some modules have dedicated packages:

```bash
# Dedicated packages (alternative to built-in support)
pip install redisvl  # Vector search, embeddings
pip install redisinsight-py  # Redis Insight integration
```

## RedisBloom Module

Probabilistic data structures: Bloom filters, Cuckoo filters, Count-Min Sketch, TopK.

### Bloom Filters (BF)

Bloom filters provide space-efficient membership testing with false positives but no false negatives.

```python
import redis
r = redis.Redis(decode_responses=True)

# Get Bloom filter client
bf = r.bf()

# Create bloom filter
# Error rate: probability of false positives (0.01 = 1%)
# Capacity: expected number of items
bf.create('mybloom', error_rate=0.01, capacity=1000)

# Add items
bf.add('mybloom', 'item1')      # True (new item added)
bf.add('mybloom', 'item2')      # True
bf.add('mybloom', 'item1')      # False (already exists)

# Check membership
bf.exists('mybloom', 'item1')   # True (definitely or probably)
bf.exists('mybloom', 'item999') # False (definitely not in set)

# Add multiple items
bf.madd('mybloom', 'a', 'b', 'c')  # [True, True, True]

# Check multiple items
bf.mexists('mybloom', 'a', 'z')    # [True, False]

# Reserve space without adding items
bf.reserve('mybloom2', error_rate=0.001, capacity=10000)

# Get information
info = bf.info('mybloom')
print(info)  # {'size': ..., 'number_of_items': ..., 'capacity': ...}
```

### Cuckoo Filters (CF)

Cuckoo filters support deletion and have similar properties to Bloom filters.

```python
import redis
r = redis.Redis(decode_responses=True)

cf = r.cf()

# Create cuckoo filter
cf.create('mycuckoo', capacity=1000)

# Add items
cf.add('mycuckoo', 'item1')     # True (added)
cf.add('mycuckoo', 'item2')     # True

# Check membership
cf.exists('mycuckoo', 'item1')  # True
cf.exists('mycuckoo', 'missing')  # False

# Delete items (not possible with Bloom filters!)
cf.delete('mycuckoo', 'item1')  # True (deleted)
cf.exists('mycuckoo', 'item1')  # False

# Add or update item
cf.addnx('mycuckoo', 'item2')   # False (already exists)

# Get information
info = cf.info('mycuckoo')
print(info)  # {'size': ..., 'number_of_items': ...}
```

### Count-Min Sketch (CMS)

Count-Min Sketch estimates frequency of items.

```python
import redis
r = redis.Redis(decode_responses=True)

cms = r.cms()

# Initialize by dimensions
# Width and depth affect accuracy
cms.initbydim('mycms', width=1000, depth=5)

# Or initialize by probability
cms.initbyprob('mycms2', error_rate=0.001, probability=0.99)

# Increment counters
cms.incrby('mycms', ['item1'], [5])  # [5] (new count after increment)
cms.incrby('mycms', ['item1', 'item2'], [3, 10])  # [8, 10]

# Query counts (approximate)
count = cms.query('mycms', 'item1')  # [8]
counts = cms.query('mycms', ['item1', 'item2', 'missing'])  # [8, 10, 0]

# Get information
info = cms.info('mycms')
print(info)  # {'width': 1000, 'depth': 5, 'count': ...}
```

### TopK

TopK maintains list of most frequent items.

```python
import redis
r = redis.Redis(decode_responses=True)

topk = r.topk()

# Reserve TopK structure
# k: number of top items to track
# width, depth: CMS parameters for counting
# decay: exponential decay factor (0.0 = no decay)
topk.reserve('mytopk', k=3, width=50, depth=4, decay=0.9)

# Add items with frequencies
topk.add('mytopk', 'item1')
topk.add('mytopk', 'item1')
topk.add('mytopk', 'item2')
topk.add('mytopk', 'item3')
topk.add('mytopk', 'item3')
topk.add('mytopk', 'item3')

# Query top items
top_items = topk.query('mytopk', 'item1', 'item2', 'item4')
print(top_items)  # [True, True, False] (in top K or not)

# Get all top items with counts
info = topk.info('mytopk')
print(info)  # {'list': [...], 'sketch': {...}}
```

## RedisJSON Module

Store and query JSON documents natively.

### Basic JSON Operations

```python
import redis
import json
r = redis.Redis(decode_responses=True)

# Get JSON client
json_client = r.json()

# Set JSON document (root path '.')
doc = {
    'name': 'Alice',
    'age': 30,
    'email': 'alice@example.com',
    'addresses': [
        {'city': 'New York', 'zip': '10001'},
        {'city': 'Boston', 'zip': '02101'}
    ],
    'active': True
}

json_client.set('user:1', '.', doc)

# Get entire document
result = json_client.get('user:1')
print(result)  # Full JSON document as Python dict

# Get specific field
name = json_client.get('user:1', '$.name')
print(name)  # ['Alice'] (JSONPath returns list)

# Get with legacy path (non-JSONPath)
name = json_client.get('user:1', '.name')
print(name)  # 'Alice' (direct value)

# Update field
json_client.set('user:1', '.age', 31)

# Append to array
json_client.arrappend('user:1', '.addresses', {'city': 'Chicago', 'zip': '60601'})

# Get array length
length = json_client.arrlen('user:1', '.addresses')
print(length)  # 3

# Delete field
json_client.delete('user:1', '.email')

# Check if key exists
exists = json_client.exists('user:1')
print(exists)  # True

# Get type of path
type_ = json_client.type('user:1', '.addresses')
print(type_)  # 'array'
```

### JSONPath Queries

RedisJSON uses JSONPath for querying nested structures:

```python
import redis
r = redis.Redis(decode_responses=True)

json_client = r.json()

# Complex document
doc = {
    'store': {
        'books': [
            {'title': 'Book 1', 'price': 10.99, 'category': 'fiction'},
            {'title': 'Book 2', 'price': 15.99, 'category': 'non-fiction'},
            {'title': 'Book 3', 'price': 8.99, 'category': 'fiction'}
        ]
    }
}

json_client.set('library', '.', doc)

# JSONPath queries (prefix with $)
# Get all book titles
titles = json_client.get('library', '$.store.books[*].title')
print(titles)  # ['Book 1', 'Book 2', 'Book 3']

# Get fiction books
fiction = json_client.get('library', '$.store.books[?(@.category=="fiction")]')
print(fiction)

# Get book prices
prices = json_client.get('library', '$.store.books[*].price')
print(prices)  # [10.99, 15.99, 8.99]

# Update all book prices (10% increase)
json_client.numincrby('library', '$.store.books[*].price', 1.1)

# Get books with price > 10
expensive = json_client.get('library', '$.store.books[?(@.price>10)]')
```

### JSON MGET and MSET

Batch operations on multiple keys:

```python
import redis
r = redis.Redis(decode_responses=True)

json_client = r.json()

# Set multiple documents
json_client.mset(
    ('user:1', '.', {'name': 'Alice', 'age': 30}),
    ('user:2', '.', {'name': 'Bob', 'age': 25}),
    ('user:3', '.', {'name': 'Charlie', 'age': 35})
)

# Get multiple documents
results = json_client.mget(['user:1', 'user:2', 'user:3'], '.')
print(results)  # [doc1, doc2, doc3]

# Get specific field from multiple documents
names = json_client.mget(['user:1', 'user:2'], '.name')
print(names)  # ['Alice', 'Bob']
```

### JSON Debug and Memory

```python
import redis
r = redis.Redis(decode_responses=True)

json_client = r.json()

# Get memory usage (bytes)
memory = json_client.memory('user:1')
print(f"Memory: {memory} bytes")

# Get memory for specific path
memory = json_client.memory('user:1', '.addresses')

# Clear entire document
json_client.clear('user:1')  # Clears all values

# Clear specific field
json_client.clear('user:1', '.addresses')  # Sets to empty array []
```

## RediSearch Module

Full-text search and indexing.

### Creating Indexes

```python
import redis
from redis.commands.search.field import TextField, NumericField, TagField, GeoField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

r = redis.Redis(decode_responses=True)
ft = r.ft()

# Define schema
schema = (
    TextField('title', weight=5.0),           # Full-text field with high weight
    TextField('description'),                 # Full-text field
    TagField('category'),                     # Exact match field (comma-separated)
    NumericField('price'),                    # Numeric range queries
    GeoField('location'),                     # Geospatial queries
)

# Create index
ft.create_index(schema, definition=IndexDefinition(prefix=['doc:'], index_type=IndexType.HASH))

# Or create without definition (uses default prefix 'idx:')
ft.create_index(schema, index_name='products')
```

### Adding Documents

```python
import redis
r = redis.Redis(decode_responses=True)

# Add documents using hash fields
r.hset('doc:1', mapping={
    'title': 'Redis Guide',
    'description': 'Complete guide to Redis database',
    'category': 'database,programming',
    'price': 29.99,
    'location': '-0.441,51.499'  # London (lon,lat)
})

r.hset('doc:2', mapping={
    'title': 'Python Tutorial',
    'description': 'Learn Python programming',
    'category': 'programming',
    'price': 39.99,
    'location': '-0.127,51.507'
})

# Documents with prefix 'doc:' are automatically indexed
```

### Searching

```python
import redis
from redis.commands.search.query import Query
r = redis.Redis(decode_responses=True)
ft = r.ft()

# Simple search
query = Query("Redis database")
result = ft.search(query)

print(f"Found {result.total} results")
for doc in result.docs:
    print(f"- {doc.title}: {doc.score:.4f}")

# Search with filters
query = (Query("Python")
    .filter_by_price(20, 50)           # Price between 20 and 50
    .sort_by('price', asc=True)        # Sort by price ascending
    .paging(0, 10)                     # Pagination (offset, num)
    .return_fields('title', 'price'))  # Return specific fields

result = ft.search(query)

# Search with tag filter
query = Query("@category:{programming}")
result = ft.search(query)

# Geo search
query = Query("*").nearby(-0.441, 51.499, 100, 'km')  # Within 100km of London
result = ft.search(query)

# Highlight matches
query = Query("Redis").highlight('*')
result = ft.search(query)
for doc in result.docs:
    print(doc.title)  # Title with <b> tags around matches
```

### Advanced Queries

```python
from redis.commands.search.query import Query

# Phrase search (exact phrase)
query = Query('"Redis database"')

# Fuzzy search (allows typos)
query = Query("Redis~")  # Finds "Redis" even with typo

# Wildcard search
query = Query("Python*")  # Starts with "Python"

# Boolean operators
query = Query("(Redis OR MongoDB) AND database")

# Field-specific search
query = Query("@title:Redis @category:{programming}")

# Numeric range
query = Query("*").filter_by_price(0, 50)

# Geo filter
query = Query("*").filter_by_location(-0.441, 51.499, 50, 'km')

# Aggregation
query = Query("*").aggregate(
    group_by('@category',
        reduce_count_as('count'),
        reduce_avg('price', 'avg_price')
    )
)
result = ft.search(query)
```

### Index Management

```python
import redis
from redis.commands.search.field import TextField
r = redis.Redis(decode_responses=True)
ft = r.ft()

# Get index info
info = ft.info()
print(f"Docs: {info.num_docs}, Size: {info.index_size}")

# Alias for index
ft.create_alias('myindex', 'alias_name')

# Drop index (and all data!)
ft.drop_index(delete_documents=True)  # Also delete indexed documents

# Stopwords
ft.stopwords_add('free', 'cheap')     # Add stopwords
ft.stopwords_delete('free')           # Remove stopword
stopwords = ft.stopwords_list()       # List all stopwords

# Synonyms
ft.synupdate(1, 'car', 'automobile', 'vehicle')  # Add synonym group
```

## RedisTimeSeries Module

Time-series data storage and querying.

### Creating Time Series

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Create time series
# Retention: max age in milliseconds (0 = unlimited)
# Duplicate policy: 'BLOCK', 'FIRST', 'LAST', 'MIN', 'MAX'
key = ts.create('temperature:sensor1', retention_msecs=86400000, duplicate_policy='LAST')

# Or create with unlabeled properties
key = ts.create('cpu:usage', labels=[('host', 'server1'), ('dc', 'us-east')])

# Create without overriding existing
ts.create('memory:usage', overwrite=False)
```

### Adding Data Points

```python
import redis
import time
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Add single data point (timestamp in milliseconds, value)
timestamp = int(time.time() * 1000)
ts.add('temperature', timestamp, 23.5)

# Add with auto timestamp (*)
ts.add('temperature', '*', 24.0)

# Add multiple fields
ts.add('sensors', '*', {'temp': 23.5, 'humidity': 65, 'pressure': 1013})

# Add with retention override
ts.add('temperature', timestamp, 23.5, retention_msecs=3600000)

# Increment value (for counters)
ts.incrby('requests', 1, timestamp=int(time.time() * 1000))

# Decrement value
ts.decrby('requests', 1, timestamp=int(time.time() * 1000))
```

### Querying Time Series

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Range query (timestamp range)
results = ts.range('temperature', 0, '-')  # From beginning to now
for sample in results:
    print(f"{sample.timestamp}: {sample.value}")

# Reverse range (newest first)
results = ts.revrange('temperature', '-', int(time.time() * 1000))

# Range with count limit
results = ts.range('temperature', '-', '+', count=100)  # Latest 100 points

# Count query (number of samples in range)
count = ts.count('temperature', 0, '-')
print(f"Total samples: {count}")

# Get first and last values
first = ts.first('temperature')
last = ts.last('temperature')
print(f"First: {first}, Last: {last}")

# Info about time series
info = ts.info('temperature')
print(f"Samples: {info.samples}, Retention: {info.retention_time}")
```

### Aggregation

Aggregate data over time windows:

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Aggregate with average (1 hour buckets)
results = ts.range(
    'temperature',
    0, '+',
    aggregation=('avg', 3600000)  # Type, bucket size in ms
)

# Supported aggregations: avg, min, max, sum, range, count, first, last, range
results = ts.range(
    'temperature',
    0, '+',
    aggregation=('max', 86400000)  # Daily maximum
)

# Aggregate with filter (query multiple series)
results = ts.mrange(
    0, '+',
    filters=[('host', 'server1')],
    aggregation=('avg', 3600000)
)

# Multi-range query with labels
results = ts.mrange(
    '-', '+',
    filters=[('dc', 'us-east'), ('type', 'temperature')]
)
```

### Multi-Series Queries

Query multiple time series by labels:

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Create series with labels
ts.create('temp:sensor1', labels=[('room', 'kitchen'), ('type', 'temperature')])
ts.create('temp:sensor2', labels=[('room', 'bedroom'), ('type', 'temperature')])
ts.create('humid:sensor1', labels=[('room', 'kitchen'), ('type', 'humidity')])

# Query all kitchen sensors
results = ts.mrange(
    '-', '+',
    filters=[('room', 'kitchen')]
)

# Query all temperature sensors
results = ts.mrange(
    '-', '+',
    filters=[('type', 'temperature')]
)

# Query with multiple label conditions (AND)
results = ts.mrange(
    '-', '+',
    filters=[('room', 'kitchen'), ('type', 'temperature')]
)

# Query with OR conditions
results = ts.mrange(
    '-', '+',
    filters=[('room', 'kitchen'), ('room', 'bedroom')]
)
```

### Downsampling

Create compressed rules for long-term storage:

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Create source series
ts.create('temperature:raw')

# Create downsampled series (1-minute averages)
ts.createrule(
    'temperature:raw',           # Source key
    'temperature:1m',            # Destination key
    'avg',                       # Aggregation type
    60000                        # Bucket size (60 seconds in ms)
)

# Create hourly downsample
ts.createrule(
    'temperature:1m',
    'temperature:1h',
    'avg',
    3600000  # 1 hour
)

# Delete rule
ts.deleterule('temperature:raw', 'temperature:1m')
```

### Alter Time Series

Modify existing series:

```python
import redis
r = redis.Redis(decode_responses=True)

ts = r.ts()

# Add label to existing series
ts.alter('temperature', labels=[('host', 'server1'), ('room', 'kitchen')])

# Update retention policy
ts.alter('temperature', retention_msecs=604800000)  # 7 days

# Change duplicate policy
ts.alter('temperature', duplicate_policy='MIN')

# Delete series
ts.delete('temperature', 0, int(time.time() * 1000))  # Delete range

# Delete entire series
ts.deletekey('temperature')
```

## Module Command Discovery

Discover available module commands:

```python
import redis
r = redis.Redis(decode_responses=True)

# List loaded modules
modules = r.module_list()
for module in modules:
    print(f"Module: {module['name']} v{module['ver']}")

# Get all commands (including module commands)
commands = r.command()
for name, info in commands.items():
    if 'bf.' in name.lower() or 'json.' in name.lower():
        print(f"{name}: {info.get('arity', 0)} args")
```

## Error Handling with Modules

```python
import redis
from redis.exceptions import ResponseError

r = redis.Redis(decode_responses=True)

try:
    # Module command that might fail
    r.bf().create('mybloom')
except ResponseError as e:
    if 'unknown command' in str(e).lower():
        print("RedisBloom module not loaded")
    else:
        raise

try:
    r.json().set('key', '.', {'data': 'value'})
except ResponseError as e:
    if 'ERR unknown command' in str(e):
        print("RedisJSON module not available")
    else:
        raise
```

## Performance Considerations

### Bloom Filter Tuning

```python
import redis
r = redis.Redis()

bf = r.bf()

# Error rate vs capacity tradeoff
# Lower error rate = more memory usage
bf.create('strict', error_rate=0.0001, capacity=10000)   # Very strict, more memory
bf.create('relaxed', error_rate=0.01, capacity=10000)    # More false positives, less memory

# Choose based on use case:
# - Authentication: 0.000001 (very low false positive rate)
# - Caching: 0.01 (higher false positive acceptable)
# - Rate limiting: 0.001 (balanced)
```

### Time Series Optimization

```python
import redis
r = redis.Redis()

ts = r.ts()

# Use appropriate retention policies
ts.create('metrics:raw', retention_msecs=86400000)        # Keep raw data 1 day
ts.create('metrics:1h', retention_msecs=2592000000)       # Keep hourly 30 days

# Use downsample rules to reduce storage
ts.createrule('metrics:raw', 'metrics:1h', 'avg', 3600000)

# Use labels for efficient querying
ts.create('cpu', labels=[('host', 'server1'), ('dc', 'us-east')])
# Query by label instead of mrange over all keys
```

### RediSearch Optimization

```python
import redis
from redis.commands.search.field import TextField, TagField
r = redis.Redis(decode_responses=True)

ft = r.ft()

# Use TagField for exact match fields (faster than TextField)
schema = (
    TextField('title'),           # Full-text search
    TagField('category'),         # Exact match (comma-separated values)
    TagField('author'),           # Exact match
    NumericField('price'),        # Range queries
)

# Add stopwords for common words
ft.stopwords_add('the', 'a', 'an', 'and')

# Use filters instead of text search when possible
query = Query("*").filter_by_price(0, 100)  # Faster than "@price:(0 TO 100)"
```
