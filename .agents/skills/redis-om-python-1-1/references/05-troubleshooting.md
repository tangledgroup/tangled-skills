# Troubleshooting Guide

Common issues and solutions when using Redis OM Python v1.1.0.

## Connection Issues

### Cannot Connect to Redis

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
Connection refused
Timeout connecting to Redis
```

**Solutions:**

1. **Verify Redis is running:**
```bash
# Check if Redis process is running
ps aux | grep redis

# Test connection
redis-cli ping
# Should return: PONG
```

2. **Check REDIS_OM_URL environment variable:**
```python
import os
print(os.environ.get("REDIS_OM_URL"))  # Should show your Redis URL

# Set correctly
export REDIS_OM_URL="redis://localhost:6379"
# Or for Redis Stack with authentication
export REDIS_OM_URL="redis://:password@localhost:6379"
```

3. **Use explicit connection:**
```python
from aredis_om import get_redis_connection

# Direct connection parameters
redis_client = get_redis_connection(
    host="localhost",
    port=6379,
    db=0,
    password="your_password",  # If authenticated
    decode_responses=True
)
```

4. **Verify Docker container:**
```bash
# Check if Redis Stack container is running
docker ps | grep redis

# Restart if needed
docker restart redis-stack

# Verify modules are loaded
docker exec redis-stack redis-cli MODULES LIST
# Should show: RediSearch and RedisJSON
```

### Module Not Found Errors

**Symptoms:**
```
ResponseError: Module RediSearch not found
ResponseError: Module RedisJSON not found
```

**Cause:** Using plain Redis instead of Redis Stack.

**Solution:** Use Redis Stack which includes RediSearch and RedisJSON:

```bash
# Docker (recommended)
docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack

# Or redis-stack-server for latest
docker run -d -p 6379:6379 redis/redis-stack-server:latest

# Verify modules
docker exec -it <container_id> redis-cli MODULES LIST
```

**Check module availability:**
```python
from aredis_om import has_redis_json, has_redisearch

print(f"RediSearch available: {has_redisearch()}")
print(f"RedisJSON available: {has_redis_json()}")

if not has_redisearch():
    raise RuntimeError(
        "RediSearch module not found. Please use Redis Stack instead of plain Redis."
    )
```

## Index Creation Issues

### Migrator Fails to Create Index

**Symptoms:**
```
ResponseError: Index creation failed
Index name already exists
```

**Solutions:**

1. **Drop existing index first:**
```python
from aredis_om import User

# Drop and recreate
await User.drop_index(delete_documents=False)  # Keep data
await User.create_index()

# Or force drop (deletes data too)
await User.drop_index(delete_documents=True)
await User.create_index()
```

2. **Check index name conflicts:**
```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection()
indexes = await redis_client.ft().info()
print(indexes)  # List all indexes

# Delete specific index
await redis_client.ft("myapp:user").dropindex()
```

3. **Use unique key prefixes:**
```python
class User(HashModel):
    username: str = Field(index=True)

    class Meta:
        global_key_prefix = "myapp:v2"  # Unique prefix
        model_key_prefix = "user"
```

### Index Creation Timeout

**Symptoms:**
```
TimeoutError: Index creation timed out
Operation timed out
```

**Solutions:**

1. **Increase timeout:**
```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection(socket_timeout=30)  # 30 seconds
```

2. **Check Redis server load:**
```bash
# Monitor Redis
redis-cli INFO stats

# Check memory usage
redis-cli INFO memory
```

## Query Errors

### Field Not Indexed

**Symptoms:**
```
QuerySyntaxError: Field is not indexed
ResponseError: Unknown field
```

**Cause:** Trying to query a field without `index=True`.

**Solution:** Add indexing to the field:

```python
# Before (not queryable)
class Product(HashModel):
    name: str  # Not indexed by default in some versions
    price: float = Field(index=True)

# After (queryable)
class Product(HashModel):
    name: str = Field(index=True)  # Now queryable
    price: float = Field(index=True)

# Recreate index
await Product.drop_index(delete_documents=False)
await Product.create_index()
```

### Invalid Query Syntax

**Symptoms:**
```
QuerySyntaxError: The field X does not exist on the model Y
QuerySyntaxError: Cannot query on non-indexed field
```

**Solutions:**

1. **Verify field names match exactly:**
```python
# Case-sensitive!
class User(HashModel):
    userName: str = Field(index=True)  # camelCase

# Wrong (wrong case)
await User.find(User.username == "alice").all()  # Error!

# Correct
await User.find(User.userName == "alice").all()
```

2. **Check nested field paths:**
```python
class Order(JsonModel):
    shipping_address: Address  # Embedded model

# Wrong (missing __)
await Order.find(Order.shipping_addresscity == "Boston").all()

# Correct (use __ for nested fields)
await Order.find(Order.shipping_address.city == "Boston").all()
```

### Sorting on Non-Sortable Field

**Symptoms:**
```
ResponseError: SORTABLE option is not set for field
```

**Cause:** Field doesn't have `sortable=True`.

**Solution:** Add sortable option and recreate index:

```python
class Product(HashModel):
    price: float = Field(index=True, sortable=True)  # Added sortable

# Recreate index
await Product.drop_index(delete_documents=False)
await Product.create_index()

# Now sorting works
results = await Product.find().sort_by("-price").all()
```

## Data Issues

### NotFoundError on Get

**Symptoms:**
```
NotFoundError: Primary key X was not found
```

**Solutions:**

1. **Check if record exists:**
```python
from aredis_om import NotFoundError

if await User.exists("pk-value"):
    user = await User.get("pk-value")
else:
    print("User does not exist")

# Or use try/except
try:
    user = await User.get("pk-value")
except NotFoundError:
    print("User not found")
```

2. **Verify primary key format:**
```python
# Check actual keys in Redis
from aredis_om import get_redis_connection

redis_client = get_redis_connection()
keys = await redis_client.keys("myapp:user:*")
print(keys)  # See actual key format

# Primary keys are ULIDs by default
user = User(username="test")
await user.save()
print(user.pk)  # e.g., "01H5K8X9Y2Z3A4B5C6D7E8F9G0"
```

### Data Not Persisting

**Symptoms:**
- Saved data disappears after restart
- Queries return empty results

**Solutions:**

1. **Verify save() was awaited:**
```python
# Wrong (not awaited)
user = User(username="test")
user.save()  # Missing await!

# Correct
user = User(username="test")
await user.save()  # Properly awaited
```

2. **Check Redis persistence:**
```bash
# Check Redis persistence config
docker exec redis-stack redis-cli CONFIG GET save

# Enable AOF for durability
docker exec redis-stack redis-cli CONFIG SET appendonly yes
```

3. **Verify connection to correct database:**
```python
# Check which DB you're connected to
from aredis_om import get_redis_connection

redis_client = get_redis_connection(db=0)  # Explicit DB number

# Keys might be in different DB
await redis_client.select(1)  # Switch to DB 1
keys = await redis_client.keys("*")
```

### DateTime/Date Conversion Issues

**Symptoms:**
- Dates stored as timestamps not converting back
- Wrong timezone on retrieved datetimes

**Solution:** Redis OM automatically converts datetime to Unix timestamps. Retrieved values should convert back automatically:

```python
import datetime
from aredis_om import HashModel, Field

class Event(HashModel):
    name: str = Field(index=True)
    event_date: datetime.date
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

# Save
event = Event(
    name="Conference",
    event_date=datetime.date(2024, 6, 15)
)
await event.save()

# Retrieve - should auto-convert back
retrieved = await Event.get(event.pk)
print(retrieved.event_date)  # datetime.date object
print(retrieved.created_at)  # datetime.datetime object (UTC)
```

**If conversion fails:** Ensure you're using the latest version and model fields are properly typed.

## Performance Issues

### Slow Queries

**Solutions:**

1. **Add indexes to queried fields:**
```python
# Slow (no index)
class Product(HashModel):
    category: str  # Not indexed

# Fast (with index)
class Product(HashModel):
    category: str = Field(index=True)
```

2. **Use pagination:**
```python
# Bad: loads all results
all_products = await Product.find().all()  # Could be thousands!

# Good: paginate
page_1 = await Product.find().page(0, 50).all()
page_2 = await Product.find().page(1, 50).all()
```

3. **Load only needed fields:**
```python
# Loads all fields
user = await User.get(pk)

# Loads only specific fields (faster)
user = await User.find(User.pk == pk).only("username", "email").first()
```

4. **Use first() for single results:**
```python
# Inefficient
results = await User.find(User.username == "alice").all()
user = results[0] if results else None

# Efficient
user = await User.find(User.username == "alice").first()
```

### High Memory Usage

**Solutions:**

1. **Check Redis memory:**
```bash
docker exec redis-stack redis-cli INFO memory
# Look for: used_memory_human
```

2. **Set maxmemory limit:**
```bash
docker exec redis-stack redis-cli CONFIG SET maxmemory 2gb
docker exec redis-stack redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

3. **Use appropriate data structures:**
- HashModel for simple flat data (more memory efficient)
- JsonModel for complex nested data (less efficient but flexible)

4. **Set TTL on temporary data:**
```python
session = Session(user_id="123", token="abc")
await session.save()
await session.expire(3600)  # Auto-delete after 1 hour
```

## Vector Search Issues

### KNN Query Returns No Results

**Symptoms:**
- KNN query returns empty list
- Similarity scores are all None

**Solutions:**

1. **Verify vector dimensions match:**
```python
# Indexed vectors must match query vector dimension
DIMENSIONS = 768

vector_options = VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=DIMENSIONS,  # Must be 768
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
)

class Document(JsonModel):
    embeddings: list[float] = Field(vector_options=vector_options)

# Query vector must also be 768 dimensions
query_vector = [0.1] * DIMENSIONS  # Must be 768 elements!
```

2. **Check vectors are actually stored:**
```python
docs = await Document.find().all()
for doc in docs:
    print(f"Vector length: {len(doc.embeddings)}")
    # Should match DIMENSIONS
```

3. **Verify vector packing:**
```python
import struct

def pack_vector(vector: list[float]) -> bytes:
    # Little-endian float32
    return struct.pack(f"<{len(vector)}f", *vector)

knn = KNNExpression(
    k=10,
    vector_field=Document.embeddings,
    score_field=Document.similarity_score,
    reference_vector=pack_vector(query_vector),  # Must pack!
)
```

### Vector Field Not Indexed

**Symptoms:**
```
ResponseError: Field is not a vector field
KNN query failed
```

**Solution:** Ensure vector_options is properly configured:

```python
# Wrong (no vector options)
class Document(JsonModel):
    embeddings: list[float] = Field(default_factory=list)

# Correct (with vector options)
vector_options = VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=768,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
)

class Document(JsonModel):
    embeddings: list[float] = Field(
        default_factory=list,
        vector_options=vector_options  # Required!
    )
```

## Geospatial Issues

### GeoFilter Returns No Results

**Solutions:**

1. **Verify coordinate format:**
```python
from pydantic_extra_types.coordinate import Coordinate

# Correct: latitude, longitude
nyc = Coordinate(latitude=40.7128, longitude=-74.0060)

# GeoFilter uses: longitude, latitude (note the swap!)
filter = GeoFilter(
    longitude=-74.0060,  # Longitude first
    latitude=40.7128,    # Latitude second
    radius=10,
    unit="mi"
)
```

2. **Check coordinate validity:**
```python
# Invalid coordinates will raise ValueError
filter = GeoFilter(
    longitude=200,  # Error! Must be -180 to 180
    latitude=40,
    radius=10,
    unit="mi"
)

# Valid
filter = GeoFilter(
    longitude=-74.0060,  # -180 to 180
    latitude=40.7128,    # -90 to 90
    radius=10,           # Must be positive
    unit="mi"
)
```

3. **Verify radius and units:**
```python
# Too small radius might return no results
filter = GeoFilter(
    longitude=-74.0060,
    latitude=40.7128,
    radius=0.001,  # Very small! Try larger
    unit="mi"
)

# Better
filter = GeoFilter(
    longitude=-74.0060,
    latitude=40.7128,
    radius=25,  # 25 mile radius
    unit="mi"
)
```

## Pydantic Validation Errors

### ValidationError on Model Creation

**Symptoms:**
```
pydantic.ValidationError: 1 validation error for User
email
  value is not a valid email address
```

**Solutions:**

1. **Use correct Pydantic types:**
```python
from pydantic import EmailStr

class User(HashModel):
    email: EmailStr  # Validates email format

# Valid
user = User(email="user@example.com")

# Invalid - will raise ValidationError
user = User(email="not-an-email")  # Error!
```

2. **Handle validation errors:**
```python
from pydantic import ValidationError

try:
    user = User(email="invalid")
except ValidationError as e:
    print(f"Validation failed: {e}")
    # e.errors() contains detailed error info
```

3. **Add custom validators:**
```python
from pydantic import field_validator

class User(HashModel):
    age: int
    
    @field_validator('age')
    @classmethod
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age cannot be negative')
        return v
```

## Common Configuration Issues

### Wrong Python Version

**Requirement:** Python 3.10-3.13

```bash
# Check version
python --version  # Should be 3.10+

# If too old, use pyenv or update
pyenv install 3.11.0
pyenv local 3.11.0
```

### Missing Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'aredis_om'
ImportError: cannot import name 'HashModel'
```

**Solution:** Install redis-om properly:

```bash
# Install with pip
pip install --upgrade redis-om

# Or with uv
uv add redis-om

# Verify installation
python -c "import aredis_om; print(aredis_om.__version__)"
```

### Import Path Confusion

Redis OM uses `aredis_om` (async) not `redis_om`:

```python
# Correct (async)
from aredis_om import HashModel, JsonModel, Field

# Incorrect
from redis_om import HashModel  # Wrong!
```

**Note:** Some examples in documentation may use `redis_om` - these should be `aredis_om` for async operations.

## Debugging Tips

### Enable Redis OM Logging

```python
import logging

# Enable debug logging
logging.getLogger("aredis_om").setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed logs of operations
```

### Inspect Redis Directly

```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection()

# List all keys
keys = await redis_client.keys("*")
print(f"Total keys: {len(keys)}")

# Get specific key
value = await redis_client.get("myapp:user:123")
print(f"Value: {value}")

# For JSON models
json_value = await redis_client.json().get("myapp:product:456")
print(f"JSON: {json_value}")

# Check index info
index_info = await redis_client.ft("myapp:user").info()
print(f"Index info: {index_info}")
```

### Test Connection and Modules

```python
from aredis_om import get_redis_connection, has_redis_json, has_redisearch

async def test_connection():
    redis_client = get_redis_connection()
    
    # Test basic connection
    ping = await redis_client.ping()
    print(f"Redis ping: {ping}")
    
    # Check modules
    print(f"RediSearch available: {has_redisearch()}")
    print(f"RedisJSON available: {has_redis_json()}")
    
    # List modules
    modules = await redis_client.module_list()
    print(f"Loaded modules: {modules}")

import asyncio
asyncio.run(test_connection())
```

## Getting Help

1. **Check documentation:** https://redis.github.io/redis-om-python/
2. **Review examples:** https://github.com/redis/redis-om-python/tree/main/examples
3. **Open issue:** https://github.com/redis/redis-om-python/issues
4. **Redis Discord:** Join Redis community for real-time help
