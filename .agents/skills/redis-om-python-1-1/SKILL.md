---
name: redis-om-python-1-1
description: A skill for using Redis OM Python v1.1, an object mapping library that provides declarative models, automatic secondary-index generation, and fluent query APIs for Redis with RediSearch and RedisJSON modules. Use when building Python applications requiring ORM-like abstractions for Redis, full-text search capabilities, geospatial queries, vector similarity search (KNN), or complex nested document storage.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "1.1.0"
tags:
  - redis
  - orm
  - object-mapping
  - pydantic
  - redi-search
  - redis-json
  - vector-search
category: database
external_references:
  - https://redis.github.io/redis-om-python/
  - https://github.com/redis/redis-om-python
---

# Redis OM Python 1.1

## Overview

Redis OM Python is a modern object mapping library for Redis that provides high-level abstractions to model and query Redis data with Python. Built on Pydantic v2 for robust data validation, it supports both async and sync operations through two parallel modules: `redis_om` (sync) and `aredis_om` (async).

Key capabilities include declarative model definitions backed by Redis Hashes or JSON documents, automatic RediSearch index management, Django-ORM-like query syntax, full-text search, embedded models, vector similarity search with KNN expressions, and seamless FastAPI integration.

## When to Use

- Building Python applications that require ORM-like abstractions for Redis
- Implementing full-text search on Redis data using RediSearch
- Storing and querying nested/complex documents with RedisJSON
- Adding vector similarity search for AI/ML applications
- Building FastAPI APIs with Redis as the data layer
- Migrating from field-by-field indexing (0.x) to model-level indexing (1.0+)

## Requirements

- Python 3.10 or higher
- Pydantic v2
- redis-py 4.2.0 or higher
- Redis 8 (recommended, includes Search and JSON built-in) or Redis Stack

## Installation / Setup

Install with pip or uv:

```bash
pip install redis-om
# or
uv add redis-om
```

Start Redis with Search and JSON capabilities:

```bash
# Redis 8 (recommended — Search and JSON built-in)
docker run -d -p 6379:6379 redis:8

# Redis Stack (alternative, includes RedisInsight on port 8001)
docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack
```

Configure the connection with the `REDIS_OM_URL` environment variable:

```bash
export REDIS_OM_URL="redis://:password@localhost:6379/0"
```

Supported URL schemes: `redis://`, `rediss://` (SSL), `unix://` (Unix socket). Indexing only works on Redis logical database 0.

## Core Concepts

- **HashModel** — Stores data as flat Redis Hashes. Does not support container types (list, set, dict) or embedded models. Use for simple, flat data structures.
- **JsonModel** — Stores data as JSON documents via RedisJSON. Supports container types, embedded models, and nested field queries. Use for complex or hierarchical data.
- **EmbeddedJsonModel** — A model designed to be nested inside a JsonModel. Set `embedded = True` in its Meta class.
- **Model-level indexing** — In 1.0+, add `index=True` to the model class (not individual fields) to enable RediSearch indexing for all fields by default.
- **Pydantic validation** — Every Redis OM model is also a Pydantic model, so all Pydantic validators (`EmailStr`, `Pattern`, etc.) work directly as field type annotations.
- **Automatic primary keys** — Models generate ULID primary keys automatically before saving, without contacting Redis.
- **Sync vs async** — `redis_om` provides synchronous APIs; `aredis_om` provides async/await-compatible APIs. They share the same API surface.

## Usage Examples

Basic model definition and CRUD:

```python
from typing import Optional
import datetime
from pydantic import EmailStr
from redis_om import HashModel, Field


class Customer(HashModel, index=True):
    first_name: str
    last_name: str
    email: EmailStr
    join_date: datetime.date
    age: int = Field(sortable=True)
    bio: Optional[str] = None


# Create
andrew = Customer(
    first_name="Andrew",
    last_name="Brookins",
    email="andrew@example.com",
    join_date=datetime.date.today(),
    age=38,
)

# Primary key is available before saving
print(andrew.pk)  # '01FJM6PH661HCNNRC884H6K30C'

# Save
andrew.save()

# Set TTL
andrew.expire(120)

# Retrieve by primary key
customer = Customer.get(andrew.pk)

# Update specific fields
andrew.update(age=39, bio="Updated bio")

# Delete
Customer.delete(andrew.pk)
```

Embedded models with JsonModel:

```python
from redis_om import JsonModel, Field


class Address(JsonModel):
    street: str
    city: str = Field(index=True)
    state: str = Field(index=True)
    country: str = "USA"

    class Meta:
        embedded = True


class Customer(JsonModel, index=True):
    name: str
    age: int
    address: Address
```

Run migrations to create RediSearch indexes:

```bash
om migrate
```

Or programmatically:

```python
from redis_om import SchemaMigrator

SchemaMigrator().run()
```

## Advanced Topics

**Models and Fields**: HashModel vs JsonModel, field types, Meta configuration, abstract models, custom primary keys → See [Models and Fields](reference/01-models-and-fields.md)

**Making Queries**: Expression operators, combining expressions, sorting, pagination, field projection, bulk operations, vector search → See [Making Queries](reference/02-making-queries.md)

**Migrations**: Schema migrations, data migrations, CLI commands, custom migration classes, rollback → See [Migrations](reference/03-migrations.md)

**FastAPI Integration**: Using Redis OM models as Pydantic schemas in FastAPI, async patterns, caching with separate Redis instances → See [FastAPI Integration](reference/04-fastapi-integration.md)
