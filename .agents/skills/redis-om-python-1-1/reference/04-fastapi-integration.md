# FastAPI Integration

## Introduction

Redis OM was designed to integrate with FastAPI. Every Redis OM model is also a Pydantic model, so models work directly as request body validators and appear in auto-generated OpenAPI documentation.

## Concepts

### Every Redis OM Model is a Pydantic Model

A Redis OM model can be used:

- As a request body validator in FastAPI route handlers
- In the auto-generated API documentation (Swagger UI, ReDoc)
- For response serialization via `model_dump()` or JSON responses

### Cache vs Data

Redis works well as both a durable data store and a cache, but optimal configurations differ. Best practice is to use separate Redis instances:

- **Data instance** — tuned for durability, used by Redis OM models
- **Cache instance** — tuned for performance, used by fastapi-cache or similar

## Example Application

```python
import datetime
from typing import Optional
import redis
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import EmailStr
from redis_om import HashModel, NotFoundError, get_redis_connection

# Separate Redis instances
REDIS_DATA_URL = "redis://localhost:6380"
REDIS_CACHE_URL = "redis://localhost:6381"

class Customer(HashModel):
    first_name: str
    last_name: str
    email: EmailStr
    join_date: datetime.date
    age: int
    bio: Optional[str]

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize cache and Redis OM connection
    r = redis.asyncio.from_url(
        REDIS_CACHE_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(r), prefix="fastapi-cache")

    Customer.Meta.database = get_redis_connection(
        url=REDIS_DATA_URL, decode_responses=True
    )
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)

@app.post("/customer")
async def save_customer(customer: Customer):
    return await customer.save()

@app.get("/customers")
async def list_customers():
    return {"customers": list(Customer.all_pks())}

@app.get("/customer/{pk}")
@cache(expire=10)
async def get_customer(pk: str, request: Request, response: Response):
    try:
        return await Customer.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Customer not found")
```

### Key Points

- The `lifespan` context manager initializes both the cache backend and Redis OM connection on startup
- `Customer` is used directly as a Pydantic request body schema in `save_customer`
- `@cache(expire=10)` from fastapi-cache caches individual customer lookups for 10 seconds
- The data Redis instance (6380) stores model data; the cache Redis instance (6381) handles HTTP response caching
- `NotFoundError` is caught and converted to an HTTP 404

## Async Support

Redis OM supports async operations throughout. Use `await` with:

- `model.save()`
- `Model.get(pk)`
- `Model.find().all()`
- `Model.find().first()`
- `Model.find().count()`
- `Model.delete(pk)`

Sync versions are also available by omitting `await`.

## Testing

For testing, you can override the database connection per model:

```python
from redis_om import get_redis_connection

# Use a test Redis instance
Customer.Meta.database = get_redis_connection(url="redis://localhost:6399")
```

Or set `REDIS_OM_URL` environment variable in tests.
