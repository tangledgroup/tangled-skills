# AsyncIO Support

SQLAlchemy 2.0 provides native asyncio support through the `sqlalchemy.ext.asyncio` extension. This enables non-blocking database operations using async drivers.

## Async Engine

```python
from sqlalchemy.ext.asyncio import create_async_engine

# SQLite with aiosqlite
async_engine = create_async_engine("sqlite+aiosqlite:///example.db", echo=True)

# PostgreSQL with asyncpg
async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")

# MySQL with aiomysql
async_engine = create_async_engine("mysql+aiomysql://user:pass@localhost/dbname")
```

The async engine wraps a synchronous engine internally. Access the sync engine via `async_engine.sync_engine`.

## Async Connection

```python
from sqlalchemy import text

async with async_engine.connect() as conn:
    result = await conn.execute(text("SELECT version()"))
    print(result.scalar())
    # auto-commits on success, rolls back on exception
```

Async connections support the same context manager pattern. Use `await` for all I/O operations.

## Async Session

```python
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

async_session = async_sessionmaker(async_engine)

async with async_session() as session:
    # Insert
    user = User(name="spongebob")
    session.add(user)
    await session.commit()

    # Query
    stmt = select(User).where(User.name == "spongebob")
    result = await session.execute(stmt)
    user = result.scalar_one()

    # With eager loading
    stmt = select(User).options(selectinload(User.addresses))
    users = (await session.scalars(stmt)).all()
```

### Key Async Session Methods

All I/O methods require `await`:
- `await session.add(obj)` — add object
- `await session.commit()` — commit transaction
- `await session.rollback()` — rollback transaction
- `await session.execute(stmt)` — execute statement
- `await session.scalars(stmt)` — scalar result
- `await session.get(Model, id)` — get by primary key
- `await session.close()` — close session

Non-I/O methods are synchronous:
- `session.add_all([obj1, obj2])` — batch add (no I/O)
- `session.dirty` — collection of dirty objects
- `session.new` — collection of pending objects

## Async Drivers

Supported async DBAPIs:

- **PostgreSQL**: `asyncpg` (`postgresql+asyncpg://`)
- **MySQL/MariaDB**: `aiomysql` (`mysql+aiomysql://`), `asyncmy` (`mysql+asyncmy://`)
- **SQLite**: `aiosqlite` (`sqlite+aiosqlite://`)

Each requires its own driver package installed separately.

## Concurrency Patterns

### Using AsyncSession with Concurrent Tasks

```python
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

async_session = async_sessionmaker(async_engine)

async def fetch_user(user_id):
    async with async_session() as session:
        user = await session.get(User, user_id)
        return user

# Run multiple queries concurrently
users = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3),
)
```

Each `async_session()` call creates an independent session with its own connection.

### Preventing Implicit I/O

Lazy loading does not work with AsyncSession because it requires implicit I/O. Use eager loading strategies:

```python
# BAD — lazy load won't work in async
user = await session.get(User, 1)
print(user.addresses)  # LazyLoadError!

# GOOD — use selectinload
stmt = select(User).options(selectinload(User.addresses))
user = (await session.scalars(stmt)).first()
print(user.addresses)  # already loaded
```

Configure relationships to prevent lazy loading:

```python
addresses: Mapped[list["Address"]] = relationship(
    back_populates="user",
    lazy="raise"  # raises error if accessed without eager load
)
```

### Running Synchronous Operations in Async

For operations that require synchronous execution (e.g., DDL):

```python
async with async_engine.connect() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## Async Events

Event listeners for async engines use `@listens_for` with `asyncio=True`:

```python
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

@event.listens_for(AsyncEngine, "connect")
async def do_connect(dbapi_connection, connection_record):
    # Custom async setup
    pass

@event.listens_for(AsyncEngine, "close")
async def do_close(dbapi_connection, connection_record):
    # Custom async cleanup
    pass
```

## Async Inspector

```python
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine("sqlite+aiosqlite:///example.db")

async with async_engine.connect() as conn:
    from sqlalchemy import inspect
    insp = await inspect(conn)
    tables = await insp.get_table_names()
    columns = await insp.get_columns("users")
```

## Migration Considerations

When migrating from sync to async:

1. Replace `create_engine()` with `create_async_engine()`
2. Replace `Session` with `AsyncSession`
3. Add `await` to all I/O methods
4. Replace lazy loading with eager loading strategies
5. Use async-compatible drivers
6. DDL operations use `run_sync()`
