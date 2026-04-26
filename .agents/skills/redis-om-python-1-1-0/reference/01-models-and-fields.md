# Models and Fields

## HashModel vs JsonModel

**HashModel** stores data as Redis Hashes — flat key-value pairs. Cannot store container types (lists, dicts, sets) or embedded models. Use for simple flat records.

**JsonModel** stores data as JSON documents via the RedisJSON module. Supports lists, dicts, and embedded models. Use when you need nested data structures, list field indexing, or model embedding.

Rule of thumb: if you need to embed a model inside another model, use JsonModel. Otherwise HashModel is simpler and sufficient.

## Creating Models

Subclass `HashModel` or `JsonModel` and define fields with Python type annotations:

```python
from redis_om import HashModel

class Customer(HashModel):
    first_name: str
    last_name: str
    email: str
    age: int
```

## Fields

### With HashModel

HashModel does not support container types: sets, lists, dicts, other Redis OM models, or Pydantic models. These will be rejected because Redis Hashes are flat.

### With JsonModel

JsonModel supports all Python types including `List[str]`, `Dict[str, Any]`, and nested models. Values are serialized via Pydantic's JSON encoding.

```python
from typing import List
from redis_om import JsonModel, Field

class Order(JsonModel):
    product: str
    quantity: int

class Customer(JsonModel):
    name: str
    orders: List[Order] = []
```

### Default Values

Assign a value to a field for defaults:

```python
from redis_om import HashModel

class Customer(HashModel):
    first_name: str
    last_name: str
    bio: str = "No bio yet"
```

### Optional Fields

Use `Optional[T] = None` for optional fields:

```python
from typing import Optional
from redis_om import HashModel

class Customer(HashModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None
```

## Validation

Redis OM uses Pydantic for runtime validation based on type annotations.

### Basic Type Validation

Type annotations like `str`, `int`, `datetime.date` are enforced automatically:

```python
import datetime
from pydantic import EmailStr
from redis_om import HashModel

class Customer(HashModel):
    first_name: str
    email: EmailStr
    age: int
    join_date: datetime.date
```

### Complex Validation

Use Pydantic validators like `EmailStr`, `Pattern`, and constrained types:

```python
from pydantic import ValidationError

try:
    Customer(
        first_name="Andrew",
        email="Not an email address!",
        age=38,
        join_date=datetime.date.today()
    )
except ValidationError as e:
    print(e)
    # 1 validation error for Customer
    # email: value is not a valid email address
```

Validation also fires on `save()` if you mutate a field to an invalid value.

### Constrained Values

Pydantic constrained types work directly:

```python
from pydantic import constr
from redis_om import HashModel

class UsernameModel(HashModel):
    username: constr(min_length=3, max_length=20)
```

## Saving and Loading Models

### Saving

Call `save()` on a model instance. Both sync and async are supported:

```python
andrew = Customer(first_name="Andrew", last_name="Smith")
await andrew.save()  # Async
# andrew.save()      # Sync
```

### Conditional Saves

Use `nx=True` (insert-only) or `xx=True` (update-only):

```python
# Only save if key does NOT exist
result = await andrew.save(nx=True)

# Only save if key already exists
result = await andrew.save(xx=True)
```

Returns `None` if the condition was not met, otherwise returns the model.

### Getting by Primary Key

```python
customer = await Customer.get(andrew.pk)
```

### Automatic Primary Keys

Models generate ULIDs automatically without contacting Redis:

```python
andrew = Customer(first_name="Andrew", last_name="Smith")
print(andrew.pk)
# > '01FJM6PH661HCNNRC884H6K30C'
```

The ID is available before saving.

### Updating Models

Update specific fields on an instance:

```python
await andrew.update(age=39, bio="Updated bio")
```

### Deleting Models

Delete by primary key or in bulk:

```python
await Customer.delete(andrew.pk)
# Or delete multiple:
await Customer.delete_many([customer1, customer2, customer3])
```

### Expiring Models

Set a TTL (time to live) on a model instance:

```python
andrew.expire(120)  # Expires in 120 seconds
```

### Listing All Primary Keys

```python
async for pk in Customer.all_pks():
    print(pk)
```

## Configuring Models

### Meta Object

Configure Redis OM-specific settings via the `Meta` inner class:

```python
from redis_om import HashModel

class Customer(HashModel):
    first_name: str
    last_name: str

    class Meta:
        global_key_prefix = "customer-dashboard"
```

### Meta Settings

- `global_key_prefix` — string prefix applied to every Redis key the model manages (default: `""`)
- `model_key_prefix` — prefix for the model's Redis Hash/JSON key and RediSearch index name (default: `"{module}.{class_name}"`)
- `primary_key_pattern` — format string for Redis keys, accepts `{pk}` (default: `"{pk}"`)
- `database` — a `redis.asyncio.Redis` or `redis.Redis` client instance
- `primary_key_creator_cls` — class implementing the `PrimaryKeyCreator` protocol
- `index_name` — RediSearch index name for indexed models
- `embedded` — whether this model is embedded in a parent (default: `False`, JsonModel only)
- `encoding` — string encoding for Redis (default: `"utf-8"`)

### Abstract Models

Create abstract base classes by mixing in `ABC`:

```python
from abc import ABC
from redis_om import HashModel

class BaseModel(HashModel, ABC):
    class Meta:
        global_key_prefix = "my-application"

class Customer(BaseModel):
    first_name: str
    last_name: str
```

`Customer` inherits `global_key_prefix` from `BaseModel`. Abstract models cannot be instantiated.

### Meta Object Inheritance

Subclasses inherit parent Meta settings and can override individual fields:

```python
from redis_om import HashModel, get_redis_connection

class BaseModel(HashModel, ABC):
    class Meta:
        global_key_prefix = "customer-dashboard"
        database = get_redis_connection(port=6380)

class Customer(BaseModel):
    first_name: str

    class Meta:
        database = get_redis_connection(port=6381)
```

`Customer` inherits `global_key_prefix` but uses a different database.

### Custom Primary Key Creators

Replace the default ULID generator:

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

Note: `uuid.uuid7()` requires Python 3.11+ or a backport like `uuid6`.

### Configuring Pydantic

Use `model_config` with Pydantic's `ConfigDict`:

```python
from pydantic import ConfigDict
from redis_om import HashModel

class Customer(HashModel):
    first_name: str

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )
```

## Model-Level Indexing

Add `index=True` to the model class to enable RediSearch indexing:

```python
from redis_om import HashModel

class Customer(HashModel, index=True):
    first_name: str
    last_name: str
    email: str
    age: int
```

All fields are indexed automatically.

### Excluding Fields from Indexing

```python
from redis_om import HashModel, Field

class Customer(HashModel, index=True):
    first_name: str = Field(index=False)  # Not indexed
    last_name: str                               # Indexed (default)
    email: str                                   # Indexed (default)
```

### Field-Specific Index Options

```python
from redis_om import HashModel, Field

class Customer(HashModel, index=True):
    last_name: str                               # TAG (default, exact matching)
    bio: str = Field(full_text_search=True)      # TEXT (full-text search)
    age: int = Field(sortable=True)              # NUMERIC, sortable
    category: str = Field(case_sensitive=False)  # TAG, case-insensitive
```

### Field Index Types

Python types map to RediSearch field types automatically:

- `str` → TAG (exact matching, default)
- `str` with `full_text_search=True` → TEXT (full-text search)
- `int`, `float` → NUMERIC (range queries, sorting)
- `bool` → TAG
- `datetime` → NUMERIC (stored as Unix timestamps)
- Geographic types → GEO

All indexed field types support sorting when marked with `sortable=True`.

### Running Migrations

Create indexes for indexed models:

```bash
om migrate
```

Or programmatically:

```python
from redis_om import Migrator
Migrator().run()
```

## Vector Fields

Define vector fields using `VectorFieldOptions`:

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

### Vector Algorithm Options

**FLAT** — brute-force search, best for smaller datasets:

```python
vector_options=VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=768,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
    initial_cap=1000,
)
```

**HNSW** — approximate search, best for larger datasets:

```python
vector_options=VectorFieldOptions.hnsw(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=768,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
    m=16,
    ef_construction=200,
    ef_runtime=10,
)
```

### Distance Metrics

- `COSINE` — cosine similarity (most common for text embeddings)
- `L2` — Euclidean distance
- `IP` — inner product

### Vector Data Types

- `FLOAT32` — 32-bit floating point (most common)
- `FLOAT64` — 64-bit floating point

## Embedded Models (JsonModel Only)

JsonModel supports embedding models within other models:

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
    address: Address
```

Embedded models must have `embedded = True` in their Meta class. They are stored as nested JSON within the parent document, can have their own indexed fields (included in the parent's index), and are not separately queryable — query through the parent model using dot notation like `Customer.address.city`.
