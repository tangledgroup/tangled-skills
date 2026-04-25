---
name: redis-om-python-1-1
description: A skill for using Redis OM Python v1.1.0, an object mapping library that provides declarative models, automatic secondary-index generation, and fluent query APIs for Redis with RediSearch and RedisJSON modules. Use when building Python applications requiring ORM-like abstractions for Redis, full-text search capabilities, geospatial queries, vector similarity search (KNN), or complex nested document storage.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - redis
  - orm
  - pydantic
  - redisearch
  - redisjson
  - vector-search
  - geospatial
category: database
required_environment_variables:
  - name: REDIS_OM_URL
    prompt: "Redis connection URL (e.g., redis://localhost:6379)"
    help: "Connection string for Redis Stack instance with RediSearch and RedisJSON modules enabled"
    required_for: "full functionality"

external_references:
  - https://redis-om.readthedocs.io/
  - https://github.com/redis/redis-om-python
---
## Overview
A skill for using Redis OM Python v1.1.0, an object mapping library that provides declarative models, automatic secondary-index generation, and fluent query APIs for Redis with RediSearch and RedisJSON modules. Use when building Python applications requiring ORM-like abstractions for Redis, full-text search capabilities, geospatial queries, vector similarity search (KNN), or complex nested document storage.

Redis OM Python provides high-level abstractions for modeling and querying Redis data using Pydantic-based models. It supports both hash-based storage (HashModel) and JSON document storage (JsonModel), with automatic RediSearch index generation, full-text search, geospatial queries, vector similarity search, and schema migrations.

## When to Use
- Building Python applications requiring Redis as a data store with ORM-like abstractions
- Implementing full-text search capabilities using RediSearch
- Storing complex nested documents with JSON model support
- Performing geospatial queries (radius searches around coordinates)
- Implementing vector similarity search for embeddings (KNN)
- Needing automatic secondary index generation from model definitions
- Using Pydantic validation for data integrity
- Requiring schema migration management for RediSearch indexes

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Installation

```bash
# Install with pip
pip install redis-om

# Or using uv
uv add redis-om
```

**Dependencies:**
- Python 3.10-3.13
- redis>=4.2.0,<8.0.0
- pydantic>=2.0.0,<3.0.0
- python-ulid (for auto-generated primary keys)
- hiredis (C-based Redis protocol parser)

### Starting Redis Stack

Redis OM requires Redis with RediSearch and RedisJSON modules:

```bash
# Using Docker (recommended)
docker run -p 6379:6379 -p 8001:8001 redis/redis-stack

# Access Redis Insight GUI at http://localhost:8001
```

### Connection Configuration

**Option 1: Environment variable**
```bash
export REDIS_OM_URL="redis://localhost:6379"
```

**Option 2: Direct connection**
```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection()
# Or with custom parameters
redis_client = get_redis_connection(host="localhost", port=6379, db=0)
```

## Usage Examples
### Basic HashModel Example

HashModel stores data as Redis hashes - ideal for flat, simple data structures:

```python
import datetime
from typing import Optional
from pydantic import EmailStr
from aredis_om import HashModel, Field

class Customer(HashModel):
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    email: EmailStr = Field(index=True)
    age: int = Field(index=True, sortable=True)
    bio: Optional[str] = Field(default=None, index=True, full_text_search=True)
    join_date: datetime.date
    is_active: bool = Field(default=True, index=True)

# Create and save
customer = Customer(
    first_name="Andrew",
    last_name="Brookins",
    email="andrew@example.com",
    age=38,
    bio="Python developer",
    join_date=datetime.date.today(),
)
await customer.save()

# Retrieve by primary key
retrieved = await Customer.get(customer.pk)

# Query with filters
results = await Customer.find(
    (Customer.age >= 30) & (Customer.is_active == True)
).all()

# Full-text search
results = await Customer.find(Customer.bio % "developer").all()

# Sort and paginate
results = await Customer.find().sort_by("-age").page(0, 10).all()

# Delete
await customer.delete()
```

### Basic JsonModel Example

JsonModel stores data as JSON documents - ideal for nested structures and arrays:

```python
from typing import List, Optional
from aredis_om import JsonModel, Field, EmbeddedJsonModel

class Address(EmbeddedJsonModel):
    street: str
    city: str = Field(index=True)
    state: str = Field(index=True)
    zip_code: str

class Order(JsonModel):
    order_id: str = Field(primary_key=True)
    customer_name: str = Field(index=True)
    shipping_address: Address  # Embedded model
    items: List[str]  # Arrays only work in JsonModel
    total: float = Field(index=True, sortable=True)
    status: str = Field(default="pending", index=True)

# Create with nested data
order = Order(
    order_id="ORD-001",
    customer_name="Alice",
    shipping_address=Address(
        street="123 Main St",
        city="Boston",
        state="MA",
        zip_code="02101"
    ),
    items=["product-1", "product-2"],
    total=99.99
)
await order.save()

# Query embedded fields
orders = await Order.find(
    Order.shipping_address.city == "Boston"
).all()

# Query by status
pending = await Order.find(Order.status == "pending").all()
```

### Running Migrations

Before using models, create RediSearch indexes:

```python
from aredis_om import Migrator

# Run migrations to create indexes
await Migrator().run()

# With custom connection
await Migrator(conn=redis_client).run()
```

## Advanced Topics
## Advanced Topics

- [Model Types](reference/01-model-types.md)
- [Querying](reference/02-querying.md)
- [Advanced Features](reference/03-advanced-features.md)
- [Schema Migrations](reference/04-schema-migrations.md)
- [Troubleshooting](reference/05-troubleshooting.md)

## Troubleshooting
**Module not found errors:** Ensure Redis Stack (not plain Redis) is running with RediSearch and RedisJSON modules.

**Index creation fails:** Check that `Migrator().run()` is called before querying.

**Connection errors:** Verify REDIS_OM_URL or connection parameters are correct.

See [Troubleshooting Guide](reference/05-troubleshooting.md) for detailed solutions.

