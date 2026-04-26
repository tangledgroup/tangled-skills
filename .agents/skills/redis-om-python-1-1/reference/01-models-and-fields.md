# Models and Fields

## HashModel vs JsonModel

Choose `HashModel` for flat data structures. It stores data as Redis Hashes, which are inherently flat — no lists, sets, dicts, or embedded models.

Choose `JsonModel` when you need:
- Container types (lists, sets, dicts)
- Embedded models (nesting one model inside another)
- Deep field queries on nested data

```python
from redis_om import HashModel, JsonModel

# Flat data — use HashModel
class User(HashModel, index=True):
    name: str
    email: str
    age: int

# Nested data — use JsonModel
class Product(JsonModel, index=True):
    name: str
    tags: list[str]          # Container type requires JsonModel
    variants: list["Variant"]  # Embedded model requires JsonModel
```

## Field Definitions

Fields are defined using Python type annotations. Redis OM uses these for validation (via Pydantic), serialization to Redis, and deserialization from Redis.

```python
from typing import Optional
import datetime
from pydantic import EmailStr, StrictInt
from redis_om import HashModel, Field


class Customer(HashModel, index=True):
    first_name: str                          # Required string
    last_name: str                           # Required string
    email: EmailStr                          # Pydantic validator
    join_date: datetime.date                 # Date field
    age: StrictInt                           # Strict integer (no coercion)
    bio: Optional[str] = None                # Optional with None default
    status: str = "active"                   # Default value
```

### Optional Fields

Use `Optional[T]` to make a field optional. Without it, all fields are required.

```python
from typing import Optional
from redis_om import HashModel


class Customer(HashModel):
    name: str                    # Required
    bio: Optional[str] = None    # Optional, defaults to None
```

### Default Values

Assign a value to the field annotation for defaults. The default is saved to Redis on `save()`.

```python
class Customer(HashModel):
    name: str
    status: str = "active"       # Default value
```

## Validation

Redis OM uses Pydantic v2 for runtime validation. Every Redis OM model is a Pydantic model.

### Basic Type Validation

Type annotations enforce types automatically:

```python
from pydantic import ValidationError
from redis_om import HashModel


class Customer(HashModel):
    name: str
    age: int


# This fails — age must be an integer
try:
    Customer(name="John", age="thirty")
except ValidationError as e:
    print(e)  # Input should be a valid integer
```

### Pydantic Validators

Use any Pydantic validator as a field type:

```python
from pydantic import EmailStr, ValidationError
from redis_om import HashModel


class Customer(HashModel):
    name: str
    email: EmailStr


try:
    Customer(name="John", email="not-an-email")
except ValidationError as e:
    print(e)  # value is not a valid email address
```

Validation also runs on `save()`:

```python
customer = Customer(name="John", email="valid@email.com")
customer.save()

customer.email = "invalid"
try:
    customer.save()  # Raises ValidationError
except ValidationError:
    pass
```

### Strict Types

Pydantic's strict types reject coercion:

```python
from pydantic import StrictInt, StrictStr, StrictBool, StrictFloat, StrictBytes
from redis_om import HashModel


class Customer(HashModel):
    age: StrictInt           # Rejects "38" (string)
    name: StrictStr          # Rejects non-string types
    active: StrictBool       # Rejects 1/0 for boolean
```

## Model Configuration (Meta Class)

Configure Redis OM-specific settings using the `Meta` inner class:

```python
from redis_om import HashModel, get_redis_connection


redis = get_redis_connection(port=6380)


class Customer(HashModel):
    name: str

    class Meta:
        global_key_prefix = "myapp"           # Prefix for all Redis keys
        model_key_prefix = "customer"         # Prefix for this model's keys
        database = redis                      # Custom Redis connection
        encoding = "utf-8"                    # String encoding
        index_name = "myapp:customer:index"   # Custom RediSearch index name
```

### Meta Settings

- **global_key_prefix** — String prefix applied to every Redis key the model manages. Default: `""`.
- **model_key_prefix** — Prefix for the model's Redis keys and RediSearch index. Default: `"{module}.{class_name}"`.
- **primary_key_pattern** — Format string for Redis keys, accepting a `pk` argument. Default: `"{pk}"`.
- **database** — A `redis.asyncio.Redis` or `redis.Redis` client instance. Default: auto-created via `get_redis_connection()`.
- **primary_key_creator_cls** — Custom primary key creator class adhering to the `PrimaryKeyCreator` protocol. Default: `UlidPrimaryKey`.
- **index_name** — RediSearch index name for indexed models. Default: `"{global_key_prefix}:{model_key_prefix}:index"`.
- **embedded** — Whether the model is embedded (not included in migrations). Only for JsonModel. Default: `False`.
- **encoding** — Default string encoding passed to redis-py. Default: `"utf-8"`.

## Abstract Models

Create abstract base models to share configuration across subclasses:

```python
from abc import ABC
from redis_om import HashModel, get_redis_connection


redis = get_redis_connection(port=6380)


class BaseModel(HashModel, ABC):
    class Meta:
        global_key_prefix = "myapp"
        database = redis


class Customer(BaseModel):
    name: str

    class Meta:
        # Inherits global_key_prefix from BaseModel
        pass


class Order(BaseModel):
    product: str

    class Meta:
        # Can override individual settings
        database = get_redis_connection(port=6381)
```

Meta fields are inherited — subclasses only need to override what changes.

## Custom Primary Keys

By default, Redis OM generates ULIDs. Customize with `primary_key_creator_cls`:

```python
import uuid
from redis_om import HashModel


class UUIDv7PrimaryKey:
    @staticmethod
    def create_pk(*args, **kwargs) -> str:
        return str(uuid.uuid7())


class MyModel(HashModel):
    name: str

    class Meta:
        primary_key_creator_cls = UUIDv7PrimaryKey
```

Note: `uuid.uuid7()` requires Python 3.11+ or the `uuid6` backport library.

## Model-Level Indexing

Add `index=True` to the model class to enable RediSearch indexing for all fields:

```python
from redis_om import HashModel, Field


class Customer(HashModel, index=True):
    first_name: str               # Indexed (default)
    last_name: str                # Indexed (default)
    email: str                    # Indexed (default)
    age: int                      # Indexed (default)
```

### Excluding Fields from Indexing

Use `Field(index=False)` to exclude specific fields:

```python
class Customer(HashModel, index=True):
    first_name: str = Field(index=False)  # Not indexed
    last_name: str                        # Indexed
```

### Field Index Options

```python
class Customer(HashModel, index=True):
    last_name: str                          # TAG field (exact match, default)
    bio: str = Field(full_text_search=True) # TEXT field (full-text search)
    age: int = Field(sortable=True)         # NUMERIC field with sorting
    category: str = Field(case_sensitive=False)  # Case-insensitive TAG
```

### Automatic Field Type Mapping

Redis OM chooses the RediSearch field type based on Python type:

- `str` → TAG (exact matching)
- `str` with `full_text_search=True` → TEXT (full-text search)
- `int`, `float` → NUMERIC (range queries, sorting)
- `bool` → TAG
- `datetime` → NUMERIC (Unix timestamps since 1.0)
- Geographic types (`Coordinates`) → GEO

All field types support `sortable=True`.

## Vector Fields

Define vector fields for similarity search:

```python
from redis_om import JsonModel, Field, VectorFieldOptions


class Document(JsonModel, index=True):
    title: str = Field(index=True)
    content: str = Field(full_text_search=True)
    embedding: list[float] = Field(
        vector_options=VectorFieldOptions.flat(
            type=VectorFieldOptions.TYPE.FLOAT32,
            dimension=384,
            distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
        )
    )
```

### FLAT Algorithm (brute-force, small datasets)

```python
VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=768,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
    initial_cap=1000,
)
```

### HNSW Algorithm (approximate, large datasets)

```python
VectorFieldOptions.hnsw(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=768,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
    m=16,
    ef_construction=200,
    ef_runtime=10,
)
```

### Distance Metrics

- `COSINE` — Cosine similarity (most common for text embeddings)
- `L2` — Euclidean distance
- `IP` — Inner product

### Vector Data Types

- `FLOAT32` — 32-bit float (most common)
- `FLOAT64` — 64-bit float

## Embedded Models

Only `JsonModel` supports embedding. Set `embedded = True` in the child model's Meta:

```python
from redis_om import JsonModel, Field


class Address(JsonModel):
    street: str
    city: str = Field(index=True)
    zipcode: str
    country: str = "USA"

    class Meta:
        embedded = True


class Customer(JsonModel, index=True):
    name: str
    age: int
    address: Address  # Embedded Address model
```

Embedded models:
- Are stored as nested JSON within the parent document
- Can have their own indexed fields (included in the parent's index)
- Are not separately queryable — query through the parent model
- Are excluded from migrations that create/destroy indexes

## Saving and Loading Models

### Save

```python
# Sync
andrew.save()

# Async (aredis_om)
await andrew.save()
```

### Conditional Saves

```python
# Insert only (skip if exists)
result = await andrew.save(nx=True)

# Update only (skip if not exists)
result = await andrew.save(xx=True)
```

Returns `None` if the condition was not met.

### Get by Primary Key

```python
customer = await Customer.get(andrew.pk)
```

### Update Specific Fields

```python
await andrew.update(age=39, bio="Updated bio")
```

### Delete

```python
# Single delete
await Customer.delete(andrew.pk)

# Bulk delete
await Customer.delete_many([c1, c2, c3])
```

### List All Primary Keys

```python
async for pk in Customer.all_pks():
    print(pk)
```

## Configuring Pydantic

Every Redis OM model is a Pydantic model. Control Pydantic behavior via `model_config`:

```python
from pydantic import ConfigDict
from redis_om import HashModel


class Customer(HashModel):
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )
```

## Calling Raw Redis Commands

Access the underlying Redis client through `db()`:

```python
from redis_om import HashModel


class Demo(HashModel):
    some_field: str


redis_conn = Demo.db()
redis_conn.sadd("myset", "a", "b", "c")
print(redis_conn.sismember("myset", "b"))  # True
```

Or use `get_redis_connection()` directly:

```python
from redis_om import get_redis_connection

redis_conn = get_redis_connection()
redis_conn.set("hello", "world")
```

## Sync vs Async API

`redis_om` (sync) and `aredis_om` (async) share the same API:

```python
# Sync — redis_om
from redis_om import HashModel

class Customer(HashModel):
    name: str

c = Customer(name="John")
c.save()
result = Customer.find(Customer.name == "John").all()

# Async — aredis_om
from aredis_om import HashModel

class Customer(HashModel):
    name: str

c = Customer(name="John")
await c.save()
result = await Customer.find(Customer.name == "John").all()
```

The only difference is that `aredis_om` methods return coroutines requiring `await`.
