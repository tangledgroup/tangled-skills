# AsyncIO Support in SQLAlchemy 2.0

Complete guide to asynchronous database operations using SQLAlchemy's asyncio extension, including async engines, sessions, connections, events, and advanced patterns.

**Version Added:** 1.4  
**Requires:** Python 3.7+, `greenlet` library

## Table of Contents

1. [Platform Installation Notes](#platform-installation-notes)
2. [Core Concepts](#core-concepts)
3. [Async Engine Creation and Configuration](#async-engine-creation-and-configuration)
4. [Async Connection Management](#async-connection-management)
5. [Async Session API](#async-session-api)
6. [Preventing Implicit IO](#preventing-implicit-io)
7. [Running Synchronous Code Under Asyncio](#running-synchronous-code-under-asyncio)
8. [Events with Asyncio](#events-with-asyncio)
9. [Multiple Event Loops](#multiple-event-loops)
10. [Async Scoped Session](#async-scoped-session)
11. [Inspector with Asyncio](#inspector-with-asyncio)
12. [Result Set API](#result-set-api)
13. [API Reference](#api-reference)

---

## Platform Installation Notes

### Greenlet Dependency

The asyncio extension requires the `greenlet` library for context switching between async and sync code:

```bash
# Install SQLAlchemy with async support (includes greenlet)
pip install "sqlalchemy[asyncio]"

# Or install manually
pip install sqlalchemy greenlet
```

### Platform-Specific Installation

**Pre-built wheels available for:**
- x86_64, aarch64, ppc64le, amd64, win32

**Platforms requiring source build (Apple M1/M2, etc.):**
```bash
# Ensure Python dev libraries are installed
# Then install with extra to force greenlet installation
pip install "sqlalchemy[asyncio]"

# Or upgrade pip and install greenlet explicitly
pip install --upgrade pip
pip install "greenlet>=3.0.0"
pip install "sqlalchemy[asyncio]"
```

### Database-Specific Async Drivers

**PostgreSQL (recommended):**
```bash
pip install asyncpg
```

**MySQL:**
```bash
pip install aiomysql
# or pure Python alternative
pip install asyncmy
```

**SQLite:**
```bash
pip install aiosqlite
```

---

## Core Concepts

### Async Engine Architecture

The `AsyncEngine` is an asyncio proxy for the synchronous `Engine`. It provides:
- Asynchronous connection management via `AsyncConnection`
- Connection pooling with async-aware queues
- Transparent adaptation between sync SQLAlchemy internals and async drivers

### Key Components

| Component | Description |
|-----------|-------------|
| `AsyncEngine` | Async proxy for `Engine`, manages connection pool |
| `AsyncConnection` | Async proxy for `Connection`, executes statements |
| `AsyncSession` | Async ORM session with awaitable methods |
| `async_sessionmaker` | Factory for creating `AsyncSession` instances |
| `async_scoped_session` | Task-local session management |
| `AsyncAttrs` | Mixin for awaitable attribute access |

### Important Warnings

1. **Single Session Per Task**: A single `AsyncSession` instance is **not safe** for use in multiple concurrent tasks. Each task should have its own session.

2. **No Implicit IO**: Async code must avoid lazy loading and expired attribute access that would trigger implicit database calls.

3. **Engine Disposal**: Always explicitly dispose async engines created in function scope to prevent garbage collection warnings:
   ```python
   await engine.dispose()
   ```

---

## Async Engine Creation and Configuration

### Basic Engine Creation

```python
from sqlalchemy.ext.asyncio import create_async_engine

# PostgreSQL with asyncpg (recommended for production)
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True
)

# MySQL with aiomysql
async_engine = create_async_engine(
    "mysql+aiomysql://user:password@localhost/dbname"
)

# SQLite (single-threaded, file-based)
async_engine = create_async_engine(
    "sqlite+aiosqlite:///database.db"
)

# MySQL with asyncmy (pure Python)
async_engine = create_async_engine(
    "mysql+asyncmy://user:password@localhost/dbname"
)
```

### Engine Configuration Options

```python
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    
    # Connection Pool Settings
    pool_size=20,              # Base number of connections
    max_overflow=10,           # Additional connections beyond pool_size
    pool_recycle=3600,         # Recycle connections after 1 hour (seconds)
    pool_pre_ping=True,        # Test connection before use (recommended)
    pool_timeout=30,           # Seconds to wait for available connection
    
    # Pool Class (default: QueuePool)
    # poolclass=NullPool,     # No pooling (for shared event loops)
    # poolclass=SingletonPool, # Single persistent connection
    
    # Echo and Logging
    echo=False,                # Log SQL statements to stderr
    echo_pool="debug",         # Log pool events ("debug" or "warning")
    
    # Execution Options
    # execution_options={"isolation_level": "READ COMMITTED"}
    
    # Connect Arguments (passed to DBAPI driver)
    connect_args={
        "sslmode": "require",
        "statement_cache_size": 30,
        "connect_timeout": 10
    },
    
    # Custom async connection creator (advanced)
    # async_creator=my_custom_connection_function
)
```

### Engine from Configuration Dictionary

```python
from sqlalchemy.ext.asyncio import async_engine_from_config

# Load configuration from environment or config file
config = {
    "sqlalchemy.url": "postgresql+asyncpg://user:pass@localhost/db",
    "sqlalchemy.pool_size": "20",
    "sqlalchemy.max_overflow": "10"
}

async_engine = async_engine_from_config(config)

# With custom prefix
async_engine = async_engine_from_config(config, prefix="db.")
```

### Async Engine Properties and Methods

```python
# Access underlying sync engine (for events, reflection)
sync_engine = async_engine.sync_engine

# Get dialect information
print(async_engine.name)    # e.g., "postgresql"
print(async_engine.driver)  # e.g., "asyncpg"

# Access connection pool
pool = async_engine.pool
print(pool.size())          # Total pool size
print(pool.checkedout())    # Currently checked out connections

# Get/set execution options
engine_with_options = async_engine.execution_options(
    isolation_level="READ COMMITTED"
)
options = async_engine.get_execution_options()

# Clear compiled SQL cache
async_engine.clear_compiled_cache()

# Dispose of connection pool (must await!)
await async_engine.dispose()
```

---

## Async Connection Management

### Using Async Connections

#### Context Manager Pattern (Recommended)

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, text

async def fetch_data():
    async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    
    # Connection with automatic transaction management
    async with async_engine.connect() as conn:
        result = await conn.execute(select(users))
        for row in result:
            print(row.username)
    
    # Dispose engine when done
    await async_engine.dispose()

asyncio.run(fetch_data())
```

#### Begin Pattern (Explicit Transaction)

```python
async def insert_data():
    async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    
    # Begin explicit transaction (auto-commits on success)
    async with async_engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO users (username) VALUES (:name)"),
            {"name": "alice"}
        )
        # Auto-commits here if no exception
    
    await async_engine.dispose()
```

### AsyncConnection Methods

#### Execute Statements

```python
from sqlalchemy import text, select

async def execute_examples():
    async with async_engine.connect() as conn:
        # Raw SQL
        result = await conn.execute(text("SELECT * FROM users"))
        
        # Core SELECT
        result = await conn.execute(select(users).where(users.c.id == 1))
        
        # Get first row
        row = await conn.scalar(text("SELECT COUNT(*) FROM users"))
        
        # Get all rows as list
        rows = result.fetchall()
```

#### Streaming Results (Server-Side Cursors)

```python
from sqlalchemy import select

async def stream_large_result():
    async with async_engine.connect() as conn:
        # Use stream() for server-side cursor (memory efficient)
        async_result = await conn.stream(select(users))
        
        # Async iteration
        async for row in async_result:
            print(row.username)
        
        # Or fetch in batches
        batch = await async_result.fetchmany(100)
```

#### Transaction Control

```python
async def transaction_control():
    async with async_engine.connect() as conn:
        # Begin explicit transaction
        async with conn.begin() as trans_conn:
            await trans_conn.execute(text("INSERT INTO ..."))
            # Auto-commits
        
        # Nested transaction (savepoint)
        async with conn.begin() as outer:
            try:
                async with conn.begin_nested() as inner:
                    await inner.execute(text("RISKY OPERATION"))
            except Exception:
                # Rolls back to savepoint only
                await outer.rollback()
```

#### Connection Properties and Methods

```python
async def connection_info():
    async with async_engine.connect() as conn:
        # Access underlying sync connection
        sync_conn = conn.sync_connection
        
        # Check transaction state
        print(conn.in_transaction())          # bool
        print(conn.in_nested_transaction())   # bool
        
        # Get current transaction
        trans = conn.get_transaction()
        nested_trans = conn.get_nested_transaction()
        
        # Access dialect and engine
        dialect = conn.dialect
        engine = conn.sync_engine
        
        # Close connection manually (if not using context manager)
        await conn.aclose()  # Async close
        conn.close()         # Sync close (also works)
```

#### Running Synchronous Code on Connection

```python
from sqlalchemy import MetaData

async def run_sync_on_connection():
    meta = MetaData()
    
    async with async_engine.connect() as conn:
        # Run synchronous DDL operations
        await conn.run_sync(meta.create_all)
        await conn.run_sync(meta.drop_all)
        
        # Custom sync function
        def create_tables_sync(connection):
            meta.create_all(bind=connection)
            return "done"
        
        result = await conn.run_sync(create_tables_sync)
        print(result)  # "done"
```

---

## Async Session API

### Creating Async Sessions

#### Using async_sessionmaker (Recommended)

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,      # Don't auto-flush on queries
    autocommit=False,     # Manual commit required
    expire_on_commit=False  # Don't expire objects after commit (recommended for async)
)

# Usage
async def use_session():
    async with AsyncSessionLocal() as session:
        # Work with session
        result = await session.execute(select(User))
        users = result.scalars().all()
```

#### Direct Instantiation

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def direct_session():
    async_session = AsyncSession(
        bind=async_engine,
        expire_on_commit=False
    )
    
    try:
        async with async_session.begin():
            # Work with session
            pass
    finally:
        await async_session.close()
```

### Basic CRUD Operations

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

async def crud_operations():
    async with AsyncSessionLocal() as session:
        # CREATE
        user = User(username="alice", email="alice@example.com")
        session.add(user)
        
        # Flush to get generated IDs without committing
        await session.flush()
        print(f"Created user with ID: {user.id}")
        
        # READ - Get by primary key
        fetched_user = await session.get(User, user.id)
        
        # READ - Execute query
        result = await session.execute(
            select(User).where(User.username == "alice")
        )
        user = result.scalar_one()
        
        # UPDATE
        user.email = "newemail@example.com"
        await session.commit()
        
        # Access attribute after commit (expire_on_commit=False allows this)
        print(user.email)
        
        # DELETE
        await session.delete(user)
        await session.commit()
```

### Transaction Management with Sessions

```python
async def transaction_patterns():
    # Pattern 1: Using begin() context manager
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(username="alice")
            session.add(user)
            # Auto-commits on success, auto-rollback on exception
    
    # Pattern 2: Manual commit/rollback
    async with AsyncSessionLocal() as session:
        try:
            user = User(username="bob")
            session.add(user)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    
    # Pattern 3: Nested transactions (savepoints)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(username="charlie")
            session.add(user)
            
            try:
                async with session.begin_nested():  # Savepoint
                    await risky_operation(session)
            except Exception:
                await session.rollback()  # Rollback to savepoint only
                print("Inner operation failed, continuing...")
            
            # Outer transaction can still commit
            await session.commit()
```

### Session Methods Reference

#### Object Persistence

```python
async def persistence_methods():
    async with AsyncSessionLocal() as session:
        # Add objects
        session.add(user)
        session.add_all([user1, user2, user3])
        
        # Delete objects
        await session.delete(user)
        
        # Flush changes to database (without commit)
        await session.flush()
        
        # Commit transaction
        await session.commit()
        
        # Rollback transaction
        await session.rollback()
```

#### Object Retrieval

```python
async def retrieval_methods():
    async with AsyncSessionLocal() as session:
        # Get by primary key (awaitable)
        user = await session.get(User, 1)
        
        # Get exactly one or raise exception
        user = await session.get_one(User, 1)
        
        # Execute query
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        # Get first scalar value
        count = await session.scalar(select(func.count(User.id)))
        
        # Get all scalars
        ids = await session.scalars(select(User.id))
```

#### Object State Management

```python
async def state_management():
    async with AsyncSessionLocal() as session:
        # Refresh object from database
        await session.refresh(user)
        
        # Refresh specific attributes only
        await session.refresh(user, attribute_names=["email", "username"])
        
        # Force load lazy relationships
        await session.refresh(user, attribute_names=["posts"])
        
        # Expire object attributes (force reload on access)
        await session.expire(user)
        await session.expire_all()
        
        # Remove object from session
        session.expunge(user)
        session.expunge_all()
```

#### Session State Inspection

```python
async def inspect_session():
    async with AsyncSessionLocal() as session:
        # Transaction state
        print(session.in_transaction())          # bool
        print(session.in_nested_transaction())   # bool
        
        # Get current transactions
        trans = session.get_transaction()
        nested_trans = session.get_nested_transaction()
        
        # Identity map (all loaded objects)
        identity_map = session.identity_map
        
        # Modified objects
        dirty = session.dirty      # Objects with changes
        new = session.new          # Newly added objects
        deleted = session.deleted  # Marked for deletion
        
        # Check if session is active
        print(session.is_active)
        
        # Check if specific object is modified
        print(session.is_modified(user))
```

#### Advanced Session Methods

```python
async def advanced_methods():
    async with AsyncSessionLocal() as session:
        # Merge detached object into session
        merged = await session.merge(detached_user)
        
        # Get identity key for object
        key = session.identity_key(User, 1)
        
        # Get session for specific object
        obj_session = session.object_session(user)
        
        # Execute with specific bind
        result = await session.execute(
            select(User),
            execution_options={"isolation_level": "SERIALIZABLE"}
        )
        
        # Get connection for current bind
        conn = await session.connection()
        
        # Run synchronous function in greenlet
        def sync_query(s):
            return s.query(User).filter_by(id=1).first()
        
        user = await session.run_sync(sync_query)
```

### Async Session Properties

```python
async def session_properties():
    async with AsyncSessionLocal() as session:
        # Access underlying sync session
        sync_session = session.sync_session
        
        # Configure autoflush behavior
        session.autoflush = True  # Auto-flush on queries
        
        # Use no_autoflush context manager
        with session.no_autoflush:
            # Queries won't trigger flush here
            result = await session.execute(select(User))
```

---

## Preventing Implicit IO

### The Problem

Async sessions cannot handle implicit database calls (lazy loading, expired attributes) because they would occur outside of an awaitable context.

### Solution 1: AsyncAttrs Mixin (Recommended for New Code)

Added in SQLAlchemy 2.0.13, this mixin makes all attributes awaitable:

```python
from __future__ import annotations
from typing import List
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship

# Mix into base class
class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    posts: Mapped[List[Post]] = relationship()

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

# Usage - access relationships as awaitables
async def use_async_attrs():
    async with AsyncSessionLocal() as session:
        user = await session.get(User, 1)
        
        # Load relationship explicitly with await
        for post in await user.awaitable_attrs.posts:
            print(post.title)
```

### Solution 2: Eager Loading

Use eager loading strategies to load relationships upfront:

```python
from sqlalchemy.orm import selectinload, joinedload

async def eager_loading_examples():
    async with AsyncSessionLocal() as session:
        # Selectin load (IN clause - efficient for many parents)
        stmt = (
            select(User)
            .options(selectinload(User.posts))
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        # Joined load (JOIN - efficient for few parents)
        stmt = (
            select(User)
            .options(joinedload(User.posts))
        )
        
        # Nested eager loading
        stmt = (
            select(User)
            .options(
                selectinload(User.posts).selectinload(Post.comments),
                joinedload(User.profile)
            )
        )
```

### Solution 3: Write-Only Relationships

For large collections that are only written, never read:

```python
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # Write-only - never loaded automatically
    posts: Mapped[List[Post]] = relationship(
        lazy="write_only"
    )

# Query explicitly when needed
async def query_write_only():
    async with AsyncSessionLocal() as session:
        user = await session.get(User, 1)
        
        # Can't access user.posts directly
        # Must query explicitly
        result = await session.execute(
            select(Post).where(Post.user_id == user.id)
        )
        posts = result.scalars().all()
```

### Solution 4: lazy="raise"

Prevent accidental lazy loading by raising an error:

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[List[Post]] = relationship(lazy="raise")
```

### Solution 5: Explicit Refresh

Force-load specific attributes including lazy relationships:

```python
async def explicit_refresh():
    async with AsyncSessionLocal() as session:
        user = await session.get(User, 1)
        
        # Force load the 'posts' relationship
        await session.refresh(user, attribute_names=["posts"])
        
        # Now posts are loaded
        print(user.posts)
```

### Additional Guidelines

1. **Set expire_on_commit=False**: Prevents attributes from expiring after commit:
   ```python
   AsyncSessionLocal = async_sessionmaker(
       engine, 
       expire_on_commit=False  # Recommended for async
   )
   ```

2. **Initialize empty collections**: When creating objects with relationships:
   ```python
   user = User(username="alice", posts=[])  # Empty list prevents lazy load on flush
   ```

3. **Avoid `all` cascade**: Use explicit cascade options instead:
   ```python
   # Bad - includes refresh-expire
   relationship(Post, cascade="all")
   
   # Good - explicit options
   relationship(Post, cascade="save-update, merge, delete-orphan")
   ```

4. **Use refresh() instead of expire()**: `expire()` can cause implicit IO:
   ```python
   # Prefer
   await session.refresh(user)
   
   # Avoid (may trigger lazy loads)
   await session.expire(user)
   ```

---

## Running Synchronous Code Under Asyncio

### AsyncSession.run_sync() Method

Run traditional synchronous SQLAlchemy code within an async context using greenlets:

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

def sync_query_function(session):
    """Traditional sync ORM code - can use Query API, lazy loading, etc."""
    # Legacy Query API works here
    users = session.query(User).filter_by(active=True).all()
    
    # Lazy loading works here
    for user in users:
        print(user.username, [p.title for p in user.posts])  # Lazy loads OK
    
    # Return value to async context
    return users

async def use_run_sync():
    async with AsyncSessionLocal() as session:
        # Run sync function in greenlet
        users = await session.run_sync(sync_query_function)
        
        # Can also pass arguments
        def get_user_by_id(s, user_id):
            return s.query(User).filter_by(id=user_id).first()
        
        user = await session.run_sync(get_user_by_id, 123)
```

### Use Cases for run_sync()

1. **Legacy Code Migration**: Gradually migrate sync code to async
2. **Complex Queries**: Use Query API temporarily during migration
3. **Third-Party Libraries**: Call libraries that expect sync sessions

### Connection-Level run_sync()

```python
async def connection_run_sync():
    async with async_engine.connect() as conn:
        # Run sync DDL
        await conn.run_sync(Base.metadata.create_all)
        
        # Custom sync function
        def setup_tables(conn):
            conn.execute(text("CREATE TEMPORARY TABLE temp_data"))
            return "done"
        
        result = await conn.run_sync(setup_tables)
```

---

## Events with Asyncio

### Event Registration Strategies

SQLAlchemy events work with async components by registering on the underlying sync objects:

#### 1. Instance-Level Events (using .sync_* attributes)

```python
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

# Register on sync_engine for instance-level events
@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_connection, connection_record):
    print("New connection:", dbapi_connection)

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_execute(conn, cursor, statement, params, context, executemany):
    print("Executing:", statement)

# For connections
async def use_connection():
    async with engine.connect() as conn:
        @event.listens_for(conn.sync_connection, "before_execute")
        def log_execute(c, stmt, params):
            print("Statement:", stmt)
```

#### 2. Class-Level Events (using sync classes)

```python
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event

# Register on Session class for all AsyncSession instances
@event.listens_for(Session, "before_commit")
def before_commit(session):
    print("About to commit!")

@event.listens_for(Session, "after_commit")
def after_commit(session):
    print("Committed!")

@event.listens_for(Session, "after_flush")
def after_flush(session, flush_context):
    print("Flushed objects:", session.dirty)
```

#### 3. SessionMaker-Level Events

```python
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import event

# Create sync sessionmaker as base
sync_maker = sessionmaker()

# Create async sessionmaker with sync base
async_maker = async_sessionmaker(sync_session_class=sync_maker)

# Register events on sync_maker
@event.listens_for(sync_maker, "before_commit")
def before_commit(session):
    print("Before commit from sessionmaker event")

# Usage
async def use_session():
    async_session = async_maker()
    await async_session.commit()  # Triggers event
```

### Event Examples

#### Core Events on AsyncEngine

```python
import asyncio
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

# Connect event (instance level)
@event.listens_for(engine.sync_engine, "connect")
def my_on_connect(dbapi_con, connection_record):
    print("New DBAPI connection:", dbapi_con)
    cursor = dbapi_con.cursor()
    cursor.execute("SELECT 'execute from event'")
    print(cursor.fetchone()[0])

# Before execute event (class level - all engines)
@event.listens_for(Engine, "before_execute")
def my_before_execute(conn, clauseelement, multiparams, params, execution_options):
    print("Before execute!")

async def go():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()

asyncio.run(go())
```

#### ORM Events on AsyncSession

```python
import asyncio
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
session = AsyncSession(engine)

# Before commit (instance level)
@event.listens_for(session.sync_session, "before_commit")
def my_before_commit(session):
    print("Before commit!")
    
    # Can use sync API in event handler
    connection = session.connection()
    result = connection.execute(text("SELECT 'from event'"))
    print(result.first())

# After commit (class level)
@event.listens_for(Session, "after_commit")
def my_after_commit(session):
    print("After commit!")

async def go():
    await session.execute(text("SELECT 1"))
    await session.commit()
    await session.close()
    await engine.dispose()

asyncio.run(go())
```

### Using Awaitable-Only Driver Methods in Events

Some driver methods (e.g., asyncpg's `set_type_codec`) are awaitable-only. Use `run_async()` in event handlers:

```python
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

@event.listens_for(engine.sync_engine, "connect")
def register_custom_types(dbapi_connection, *args):
    # dbapi_connection is an AdaptedConnection
    # Use run_async() to call awaitable driver methods
    dbapi_connection.run_async(
        lambda connection: connection.set_type_codec(
            "uuid",
            encoder=lambda x: str(x),
            decoder=lambda x: uuid.UUID(x),
            schema="pg_catalog"
        )
    )
```

---

## Multiple Event Loops

### Important Warning

Do not share the same `AsyncEngine` across different event loops when using the default pool implementation.

### Proper Engine Disposal Between Loops

```python
async def loop1():
    engine = create_async_engine("postgresql+asyncpg://...")
    # Use engine...
    await engine.dispose()  # Must dispose before reusing in different loop

async def loop2():
    # Create new engine or reuse after dispose
    engine = create_async_engine("postgresql+asyncpg://...")
```

### Using NullPool for Shared Engines

If you must share an engine across event loops, disable pooling:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# NullPool creates new connection each time, safe for multiple loops
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    poolclass=NullPool
)
```

---

## Async Scoped Session

### Overview

The `async_scoped_session` provides task-local session management similar to `scoped_session` for threads.

**Note:** SQLAlchemy generally recommends passing sessions directly rather than using scoped sessions, as scoped sessions rely on mutable global state.

### Basic Usage

```python
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker
)

# Create session factory
async_session_factory = async_sessionmaker(
    some_async_engine,
    expire_on_commit=False
)

# Create scoped session with task-based scope
AsyncScopedSession = async_scoped_session(
    async_session_factory,
    scopefunc=current_task  # Key sessions by current task
)

# Use like a regular session
some_async_session = AsyncScopedSession()
```

### Complete Example with Proper Cleanup

```python
import asyncio
from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine
)

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

AsyncScopedSession = async_scoped_session(
    async_sessionmaker(engine, expire_on_commit=False),
    scopefunc=current_task
)

async def task1():
    # Session is automatically scoped to this task
    AsyncScopedSession.add(User(username="alice"))
    await AsyncScopedSession.commit()
    
    # IMPORTANT: Remove session from registry when done
    await AsyncScopedSession.remove()

async def task2():
    # Different task gets different session
    AsyncScopedSession.add(User(username="bob"))
    await AsyncScopedSession.commit()
    await AsyncScopedSession.remove()

# Run concurrent tasks
asyncio.run(asyncio.gather(task1(), task2()))
```

### Scoped Session Methods

```python
async def scoped_session_methods():
    # Add objects
    AsyncScopedSession.add(user)
    AsyncScopedSession.add_all([user1, user2])
    
    # Transaction management
    await AsyncScopedSession.commit()
    await AsyncScopedSession.rollback()
    
    # Begin context managers
    async with AsyncScopedSession.begin():
        # Auto-commits or rollbacks
        pass
    
    async with AsyncScopedSession.begin_nested():
        # Savepoint
        pass
    
    # Query execution
    result = await AsyncScopedSession.execute(select(User))
    
    # Object retrieval
    user = await AsyncScopedSession.get(User, 1)
    
    # Session state
    print(AsyncScopedSession.dirty)
    print(AsyncScopedSession.new)
    print(AsyncScopedSession.deleted)
    
    # Cleanup
    await AsyncScopedSession.remove()   # Remove current task's session
    AsyncScopedSession.close()          # Close current session
    AsyncScopedSession.close_all()      # Close all sessions
    AsyncScopedSession.reset()          # Rollback and close
    
    # Expire objects
    await AsyncScopedSession.expire(user)
    await AsyncScopedSession.expire_all()
    
    # Refresh objects
    await AsyncScopedSession.refresh(user)
```

### Warning: Scope Function Requirements

1. **Must be idempotent**: The `scopefunc` is called multiple times per task
2. **Must be lightweight**: Don't create state or establish callbacks
3. **Must call remove()**: Always call `await AsyncScopedSession.remove()` in the outermost awaitable to prevent memory leaks

---

## Inspector with Asyncio

SQLAlchemy's `Inspector` for schema reflection is synchronous but can be used in async contexts via `run_sync()`:

```python
import asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

def use_inspector(conn):
    """Synchronous function using Inspector"""
    inspector = inspect(conn)
    
    # Get schema information
    table_names = inspector.get_table_names()
    view_names = inspector.get_view_names()
    
    # Get column information
    columns = inspector.get_columns("users")
    
    # Get foreign keys
    fk_constraints = inspector.get_foreign_keys("users")
    
    # Get indexes
    indexes = inspector.get_indexes("users")
    
    return {
        "tables": table_names,
        "columns": columns,
        "foreign_keys": fk_constraints,
        "indexes": indexes
    }

async def inspect_schema():
    async with engine.connect() as conn:
        schema_info = await conn.run_sync(use_inspector)
        print(schema_info)

asyncio.run(inspect_schema())
```

---

## Result Set API

### AsyncResult (from Core execute())

```python
from sqlalchemy import select

async def async_result_methods():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        
        # Fetch all rows
        all_rows = await result.fetchall()
        
        # Fetch one row
        first_row = await result.fetchone()
        
        # Fetch first row or None
        first_or_none = await result.first()
        
        # Fetch many rows
        batch = await result.fetchmany(100)
        
        # Get as scalars (first column of each row)
        scalars_result = result.scalars()
        all_scalars = await scalars_result.fetchall()
        
        # Get single scalar
        single_scalar = await result.scalar()
        
        # Get exactly one or raise
        one_row = await result.one()
        one_or_none = await result.one_or_none()
        
        # Get as mappings (dict-like)
        mappings_result = result.mappings()
        all_mappings = await mappings_result.fetchall()
        
        # Get as tuples
        tuples_result = result.tuples()
        all_tuples = await tuples_result.fetchall()
        
        # Column information
        keys = result.keys()
        columns = await result.columns()
        
        # Close result
        await result.close()
```

### AsyncScalarResult

```python
async def scalar_result():
    async with AsyncSessionLocal() as session:
        scalars = await session.scalars(select(User.id))
        
        # Get all
        all_ids = await scalars.all()
        
        # Get first
        first_id = await scalars.first()
        
        # Get one or None
        one_id = await scalars.one_or_none()
        
        # Iterate (buffered)
        for id_value in scalars:
            print(id_value)
```

### AsyncMappingResult

```python
async def mapping_result():
    async with AsyncSessionLocal() as session:
        mappings = await session.execute(
            select(User).with_only_columns(User.id, User.username)
        ).mappings()
        
        # Get as list of dicts
        all_users = await mappings.all()
        for user_dict in all_users:
            print(user_dict["id"], user_dict["username"])
```

### Streaming Results

```python
async def streaming_results():
    async with async_engine.connect() as conn:
        # Use stream() for server-side cursor
        async_result = await conn.stream(select(User))
        
        # Async iteration (memory efficient)
        async for row in async_result:
            print(row.username)
        
        # Or use yield_per for client-side batching
        result = await session.execute(
            select(User).yield_per(100)
        )
```

---

## API Reference

### create_async_engine()

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    url,                    # str or URL - Database URL with async driver
    **kwargs                # Same kwargs as create_engine()
)
```

**Parameters:**
- `url`: Database URL (e.g., `"postgresql+asyncpg://user:pass@localhost/db"`)
- `async_creator`: Async callable returning driver connection (advanced)
- All standard `create_engine()` parameters apply

### async_engine_from_config()

```python
from sqlalchemy.ext.asyncio import async_engine_from_config

engine = async_engine_from_config(
    configuration,  # dict with database config
    prefix="sqlalchemy.",  # Optional prefix for keys
    **kwargs
)
```

### AsyncEngine Methods

| Method | Description |
|--------|-------------|
| `async with engine.begin() as conn` | Connection with auto-begin transaction |
| `async with engine.connect() as conn` | Connection without transaction |
| `await engine.dispose()` | Dispose connection pool |
| `engine.clear_compiled_cache()` | Clear SQL compilation cache |
| `engine.execution_options(**opt)` | Return engine with execution options |
| `engine.get_execution_options()` | Get current execution options |
| `await engine.raw_connection()` | Get raw DBAPI connection |

**Properties:**
- `engine.sync_engine`: Underlying sync Engine
- `engine.dialect`: Dialect instance
- `engine.driver`: Driver name
- `engine.name`: Dialect name
- `engine.pool`: Connection pool
- `engine.echo`: Echo setting

### AsyncConnection Methods

| Method | Description |
|--------|-------------|
| `await conn.execute(stmt)` | Execute statement, return Result |
| `await conn.stream(stmt)` | Execute with server-side cursor |
| `await conn.scalar(stmt)` | Get single scalar value |
| `await conn.scalars(stmt)` | Get ScalarResult |
| `async with conn.begin()` | Begin transaction context |
| `async with conn.begin_nested()` | Begin savepoint |
| `await conn.run_sync(func)` | Run sync function in greenlet |
| `await conn.commit()` | Commit transaction |
| `await conn.rollback()` | Rollback transaction |
| `await conn.aclose()` | Close connection (async) |

**Properties:**
- `conn.sync_connection`: Underlying sync Connection
- `conn.sync_engine`: Underlying sync Engine
- `conn.dialect`: Dialect instance
- `conn.in_transaction()`: bool - in transaction?
- `conn.in_nested_transaction()`: bool - in savepoint?

### AsyncSession Methods

| Method | Description |
|--------|-------------|
| `await session.get(Class, id)` | Get object by primary key |
| `await session.get_one(Class, id)` | Get exactly one or raise |
| `await session.execute(stmt)` | Execute statement |
| `await session.scalar(stmt)` | Get single scalar |
| `await session.scalars(stmt)` | Get ScalarResult |
| `session.add(obj)` | Add object to session |
| `session.add_all(list)` | Add multiple objects |
| `await session.delete(obj)` | Mark object for deletion |
| `await session.flush()` | Flush pending changes |
| `await session.commit()` | Commit transaction |
| `await session.rollback()` | Rollback transaction |
| `await session.refresh(obj)` | Refresh object from DB |
| `await session.expire(obj)` | Expire object attributes |
| `session.expunge(obj)` | Remove object from session |
| `await session.merge(obj)` | Merge detached object |
| `await session.run_sync(func)` | Run sync function |
| `async with session.begin()` | Begin transaction context |

**Properties:**
- `session.sync_session`: Underlying sync Session
- `session.identity_map`: All loaded objects
- `session.dirty`: Modified objects
- `session.new`: Newly added objects
- `session.deleted`: Objects marked for deletion
- `session.is_active`: bool - session active?

### async_sessionmaker

```python
from sqlalchemy.ext.asyncio import async_sessionmaker

SessionLocal = async_sessionmaker(
    bind=engine,              # AsyncEngine instance
    class_=AsyncSession,      # Session class (default: AsyncSession)
    autoflush=False,          # Auto-flush on queries?
    autocommit=False,         # Auto-commit after flush?
    expire_on_commit=False,   # Expire after commit? (False recommended)
    sync_session_class=None   # Sync sessionmaker for events
)

# Usage
async with SessionLocal() as session:
    # Work with session
    pass

# Or with begin
async with SessionLocal().begin() as session:
    # Auto-commits
    pass
```

### async_scoped_session

```python
from sqlalchemy.ext.asyncio import async_scoped_session

ScopedSession = async_scoped_session(
    session_factory,   # async_sessionmaker instance
    scopefunc=current_task  # Function to scope sessions (required)
)

# Usage - acts like AsyncSession
await ScopedSession.add(user)
await ScopedSession.commit()

# Cleanup (important!)
await ScopedSession.remove()
```

### AsyncAttrs Mixin

```python
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[List[Post]] = relationship()

# Usage
user = await session.get(User, 1)
for post in await user.awaitable_attrs.posts:
    print(post.title)
```

---

## Best Practices Summary

1. **Always use context managers** for sessions and connections
2. **Set expire_on_commit=False** to avoid expiration issues
3. **Use AsyncAttrs mixin** or eager loading to prevent implicit IO
4. **One session per task** - never share sessions across concurrent tasks
5. **Explicitly dispose engines** created in function scope: `await engine.dispose()`
6. **Use selectinload** for most eager loading scenarios
7. **Call remove()** when using async_scoped_session to prevent memory leaks
8. **Use pool_pre_ping=True** to detect stale connections
9. **Run sync code with run_sync()** when needed, not in event handlers
10. **Register events on sync_* attributes** or sync classes

---

## Troubleshooting

### Common Issues

**1. Greenlet Import Error**
```
ModuleNotFoundError: No module named 'greenlet'
```
**Solution:** `pip install "sqlalchemy[asyncio]"`

**2. Event Loop Closed Error**
```
RuntimeError: Event loop is closed
```
**Solution:** Ensure you call `await engine.dispose()` before engine goes out of scope

**3. Task Attached to Different Loop**
```
RuntimeError: Task <...> got Future attached to a different loop
```
**Solution:** Don't share AsyncEngine across event loops, or use NullPool

**4. Implicit IO Error**
```
RuntimeError: Cannot launch sync DBAPI call from greenlet
```
**Solution:** Use eager loading, AsyncAttrs, or run_sync()

**5. Memory Leak with Scoped Session**
**Solution:** Always call `await AsyncScopedSession.remove()` in outermost awaitable

---

## Related Documentation

- [ORM Mapping](05-orm-mapping.md) - Declarative mapping details
- [ORM Relationships](08-orm-relationships.md) - Relationship configuration
- [ORM Querying](09-orm-querying.md) - Query patterns and eager loading
- [Engine Connections](02-engine-connections.md) - Sync engine details
- [Best Practices](24-best-practices.md) - Performance optimization
