# Model Types and Field Configuration

This reference covers HashModel, JsonModel, EmbeddedJsonModel, field types, and Pydantic validation in Redis OM Python v1.1.0.

## Model Base Classes

### HashModel

Stores data as Redis hashes. Best for simple, flat data structures with high-performance lookups.

**Characteristics:**
- Automatic ULID primary key generation (unless custom PK specified)
- Fields stored as hash fields (HSET/HGET)
- Supports field-level expiration (Redis 7.4+, redis-py 5.1.0+)
- Cannot store arrays/lists natively
- More memory efficient for simple documents

**Example:**
```python
from aredis_om import HashModel, Field
import datetime
from typing import Optional

class User(HashModel):
    username: str = Field(index=True)
    email: str = Field(index=True)
    age: Optional[int] = Field(default=None, index=True, sortable=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        index=True,
        sortable=True
    )

    class Meta:
        global_key_prefix = "myapp"
        model_key_prefix = "user"
```

**Key prefix format:** `myapp:user:<ulid>`

### JsonModel

Stores data as RedisJSON documents. Best for complex nested structures, arrays, and rich documents.

**Characteristics:**
- Automatic ULID primary key generation
- Full JSON document storage
- Supports nested objects and arrays
- Better for frequently changing schemas
- More flexible querying of nested fields

**Example:**
```python
from aredis_om import JsonModel, Field
from typing import List, Optional

class Product(JsonModel):
    name: str = Field(index=True, full_text_search=True)
    sku: str = Field(index=True)
    price: float = Field(index=True, sortable=True)
    tags: List[str] = Field(default_factory=list)  # Arrays only in JsonModel
    ratings: List[float] = Field(default_factory=list)
    metadata: Optional[dict] = None

    class Meta:
        global_key_prefix = "myapp"
        model_key_prefix = "product"
```

**Key prefix format:** `myapp:product:<ulid>`

### EmbeddedJsonModel

Used for nested/embedded models within JsonModel. Can be queried independently when marked with `index=True`.

**Example:**
```python
from aredis_om import EmbeddedJsonModel, Field

class Address(EmbeddedJsonModel):
    street: str
    city: str = Field(index=True)  # Queryable
    state: str = Field(index=True)
    zip_code: str = Field(index=True)
    country: str = Field(default="USA")

class Order(JsonModel):
    customer_name: str
    shipping_address: Address  # Embedded
    billing_address: Optional[Address] = None
```

**Querying embedded fields:**
```python
# Query by embedded field
boston_orders = await Order.find(
    Order.shipping_address.city == "Boston"
).all()

# Deep field access
order = await Order.get(pk)
city = order.shipping_address.city
```

## Field Types and Options

### Basic Field Configuration

```python
from aredis_om import Field

# Required indexed field (default behavior)
name: str = Field(index=True)

# Non-indexed field (faster writes, not queryable)
internal_notes: str = Field(index=False)

# Optional field with default
age: Optional[int] = Field(default=None, index=True)

# Sortable numeric field
price: float = Field(index=True, sortable=True)

# Full-text searchable field
description: str = Field(index=True, full_text_search=True)
```

### Field Options

| Option | Type | Description |
|--------|------|-------------|
| `index` | bool | Whether to create RediSearch index (default: True) |
| `sortable` | bool | Enable sorting on indexed field (default: False) |
| `full_text_search` | bool | Enable full-text search with stemming (default: False) |
| `default` | any | Default value for the field |
| `default_factory` | callable | Callable to generate default value |
| `primary_key` | bool | Mark field as primary key (default: False) |

### Data Type Support

**Strings:**
```python
name: str = Field(index=True)
email: str = Field(index=True)  # Use EmailStr for validation
```

**Numbers:**
```python
age: int = Field(index=True, sortable=True)
price: float = Field(index=True, sortable=True)
quantity: int = Field(default=0, index=True)
```

**Booleans:**
```python
is_active: bool = Field(default=True, index=True)
# Stored as "1"/"0" in Redis
```

**Dates and Datetimes:**
```python
import datetime

created_at: datetime.datetime = Field(
    default_factory=datetime.datetime.now,
    index=True,
    sortable=True
)

birth_date: datetime.date = Field(default=None)
# Stored as Unix timestamps (float) in Redis
```

**Lists (JsonModel only):**
```python
tags: List[str] = Field(default_factory=list)
scores: List[float] = Field(default_factory=list)
item_ids: List[str] = Field(default_factory=list)
```

**Embedded Models:**
```python
shipping_address: Address  # EmbeddedJsonModel instance
nested_data: Optional[Config] = None
```

**Custom Primary Keys:**
```python
class CacheEntry(HashModel):
    cache_key: str = Field(primary_key=True)  # Custom PK
    value: str

# Usage
entry = CacheEntry(cache_key="user:123:profile", value="...")
await entry.save()
retrieved = await CacheEntry.get("user:123:profile")
```

## Pydantic Validation

Redis OM models are fully compatible with Pydantic validators.

### Built-in Pydantic Types

```python
from pydantic import EmailStr, HttpUrl, IPvAnyAddress, PastDate

class Contact(JsonModel):
    email: EmailStr = Field(index=True)  # Validates email format
    website: Optional[HttpUrl] = None
    ip_address: Optional[IPvAnyAddress] = None
    birth_date: Optional[PastDate] = None  # Must be in the past
```

### Custom Validators (Pydantic v2)

```python
from pydantic import field_validator, model_validator

class Order(JsonModel):
    quantity: int
    price: float
    discount: float = 0.0

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @field_validator('discount')
    @classmethod
    def discount_must_be_valid(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Discount must be between 0 and 100')
        return v

    @model_validator(mode='after')
    def calculate_total(self):
        # Access multiple fields
        if self.quantity > 0 and self.price > 0:
            self.total = self.quantity * self.price * (1 - self.discount / 100)
        return self
```

### Pydantic v1 Compatibility

```python
from pydantic import validator

class Order(JsonModel):
    quantity: int
    price: float

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
```

## Model Metadata (Meta class)

Configure model behavior with the Meta inner class:

```python
class Product(JsonModel):
    name: str = Field(index=True)

    class Meta:
        # Global prefix for all models in application
        global_key_prefix = "myapp:v1"

        # Model-specific prefix (appears after global)
        model_key_prefix = "product"

        # Custom Redis database number (default: 0)
        database = redis_client  # Pass specific client

        # Mark as embedded-only (won't create separate index)
        embedded = True
```

**Key naming:** `{global_key_prefix}:{model_key_prefix}:{primary_key}`

## CRUD Operations

### Create

```python
# Single instance
user = User(username="alice", email="alice@example.com", age=30)
await user.save()

# With custom primary key
cache = CacheEntry(cache_key="session:abc123", value="data")
await cache.save()
```

### Read

```python
# By primary key
user = await User.get("01H5K8X9Y2Z3A4B5C6D7E8F9G0")

# Query with filters (see references/02-querying.md)
users = await User.find(User.age >= 30).all()

# Get first match
user = await User.find(User.username == "alice").first()

# Check existence
exists = await User.exists("pk-value")
```

### Update

```python
# Full update
user = await User.get(pk)
user.age = 31
user.bio = "Updated bio"
await user.save()

# Partial update (HashModel only, Redis 7.4+)
await User.update(pk, age=31, bio="Updated")

# Update with deep field syntax for nested models
await Order.update(pk, shipping_address__city="New York")
```

### Delete

```python
# Instance method
user = await User.get(pk)
await user.delete()

# Class method (direct delete by PK)
await User.delete(pk)

# Batch delete
pks = ["pk1", "pk2", "pk3"]
for pk in pks:
    await User.delete(pk)
```

## Expiration (TTL)

Set time-to-live on models:

```python
# Instance-level expiration
session = Session(user_id="123", token="abc")
await session.save()
await session.expire(3600)  # Expires in 1 hour

# With timedelta
from datetime import timedelta
await cache_entry.expire(timedelta(minutes=30))

# Remove expiration
await user.persist()

# Check remaining TTL
ttl = await user.ttl()  # Returns seconds until expiration, -1 if no TTL, -2 if not found
```

**Hash field expiration (Redis 7.4+):**
```python
# Requires redis-py >= 5.1.0 and Redis 7.4+
from aredis_om import supports_hash_field_expiration

if supports_hash_field_expiration():
    # Set expiration on individual hash fields
    await user.hexpire("temporary_field", 3600)
    ttl = await user.httl("temporary_field")
```

## Error Handling

```python
from aredis_om import NotFoundError, RedisModelError, QuerySyntaxError

try:
    user = await User.get("non-existent-pk")
except NotFoundError:
    print("User not found")

try:
    invalid = User(email="not-an-email")  # If using EmailStr
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    results = await User.find(User.nonexistent_field == "value").all()
except QuerySyntaxError as e:
    print(f"Query error: {e}")
```

## Best Practices

1. **Use HashModel for:** Simple flat data, high-performance key-value lookups, cache entries, sessions
2. **Use JsonModel for:** Complex nested documents, arrays/lists, frequently changing schemas, rich content
3. **Index only queryable fields:** Non-indexed fields write faster and use less memory
4. **Use sortable=True for numeric fields** you need to sort on
5. **Enable full_text_search** for natural language search fields
6. **Validate with Pydantic types** (EmailStr, HttpUrl) for data integrity
7. **Set appropriate TTLs** on temporary data (sessions, caches)
8. **Use custom primary keys** when you have natural unique identifiers
