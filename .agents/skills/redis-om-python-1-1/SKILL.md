---
name: redis-om-python-1-1
description: A skill for using Redis OM Python v1.1, an object mapping library that
  provides declarative models, automatic secondary-index generation, and fluent query
  APIs for Redis with RediSearch and RedisJSON modules. Use when building Python applications
  requiring ORM-like abstractions for Redis, full-text search capabilities, geospatial
  queries, vector similarity search (KNN), or complex nested document storage.
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

# Redis OM Python 1.1.0

## Overview

Redis OM Python is an object mapping library that brings declarative models, automatic secondary-index generation, and fluent query APIs to Redis. It builds on Pydantic for data validation and uses RediSearch and RedisJSON modules for rich querying, full-text search, embedded models, and vector similarity search.

Key capabilities:

- **HashModel** — flat key-value storage via Redis Hashes
- **JsonModel** — nested document storage via RedisJSON, with embedded model support
- **Fluent find() queries** — expression-based querying with AND/OR/NOT, pattern matching, collection operators, and vector search
- **Automatic RediSearch index management** — indexes created and maintained through migrations
- **Pydantic validation** — every Redis OM model is a Pydantic model, supporting EmailStr, Pattern, constrained types, and custom validators
- **Async and sync APIs** — both `await model.save()` and `model.save()` are supported
- **Vector similarity search** — KNN queries with FLAT or HNSW algorithms
- **FastAPI integration** — models double as Pydantic schemas for request validation and OpenAPI docs
- **File-based migrations** — schema snapshots and data transformation pipelines with rollback support

Requires Python 3.10+ and redis-py 4.2.0+.

## When to Use

Use Redis OM Python when:

- Building Python applications that need Redis as a primary data store with ORM-like abstractions
- You need full-text search, geospatial queries, or vector similarity search on top of Redis
- You want declarative data models with automatic validation (Pydantic) and automatic index management
- Storing nested documents with embedded models (requires JsonModel + RedisJSON)
- Integrating Redis-backed models into FastAPI applications
- You need both async and sync Redis access from the same codebase

Do not use Redis OM when:

- You only need simple key-value caching (use redis-py directly)
- You require relational features like foreign keys or transactions across models
- Your Redis deployment lacks the Search module (find() queries and indexing won't work)

## Core Concepts

### HashModel vs JsonModel

**HashModel** stores data as Redis Hashes — flat key-value pairs. It cannot store container types (lists, dicts, sets) or embedded models. Use it for simple, flat records.

**JsonModel** stores data as JSON documents via RedisJSON. It supports lists, dicts, and embedded models. Use it when you need nested data structures, list indexing, or model embedding.

### Indexing

Adding `index=True` to a model class tells Redis OM to create a RediSearch index for that model. This enables the `find()` query interface. Without indexing, you can still save, get, and delete models by primary key, but cannot run expression-based queries.

Fields are indexed automatically when the model is indexed. Use `Field(index=False)` to exclude specific fields, or `Field(full_text_search=True)` for text search on string fields.

### Pydantic Integration

Every Redis OM model is a Pydantic model. Type annotations drive both validation and serialization. You can use any Pydantic validator (EmailStr, Pattern, constr, etc.) as field types. The `model_config` attribute accepts standard Pydantic `ConfigDict` settings.

### Connection Configuration

By default, Redis OM connects to `redis://@localhost:6379`. Override with the `REDIS_OM_URL` environment variable or set `database` on the model's Meta class. Indexing only works on Redis logical database 0.

## Installation / Setup

Install with pip or uv:

```bash
pip install redis-om
# or
uv add redis-om
```

Start Redis with Search and JSON capabilities:

```bash
# Redis 8 (includes Search and JSON built-in)
docker run -d -p 6379:6379 redis:8

# Redis Stack (alternative, includes all modules + RedisInsight UI)
docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack
```

Set the connection URL if Redis runs elsewhere:

```bash
export REDIS_OM_URL="redis://:password@host:6379/0"
```

Supported URL schemes: `redis://`, `rediss://` (SSL), `unix://` (Unix socket).

## Advanced Topics

**Models and Fields**: HashModel vs JsonModel, field types, validation, default values, CRUD operations, Meta configuration, abstract models → See [Models and Fields](reference/01-models-and-fields.md)

**Making Queries**: find() expressions, comparison/string/collection operators, AND/OR/NOT logic, pagination, sorting, field projection, bulk operations, vector search, async iteration → See [Making Queries](reference/02-making-queries.md)

**Migrations**: File-based schema migrations with rollback, data migrations, CLI commands (`om migrate`, `om migrate-data`), datetime normalization in 1.1 → See [Migrations](reference/03-migrations.md)

**FastAPI Integration**: Using Redis OM models as Pydantic schemas, dual Redis instances (cache vs data), lifespan setup, caching with fastapi-cache → See [FastAPI Integration](reference/04-fastapi-integration.md)
