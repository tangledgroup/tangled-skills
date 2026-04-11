# AsyncIO Support in SQLAlchemy 2.0

## Async Engine Creation

### Basic Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine

# PostgreSQL with asyncpg (recommended)
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True,
    pool_size=20,
    max_overflow=10
)

# MySQL with aiomysql
async_engine = create_async_engine(
    "mysql+aiomysql://user:password@localhost/dbname"
)

# SQLite (single-threaded)
async_engine = create_async_engine(
    "sqlite+aiosqlite:///database.db"
)
```

### Engine Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    
    # Pool settings
    pool_size=20,              # Base connection pool size
    max_overflow=10,           # Additional connections allowed
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Test connection before use
    
    # Echo settings
    echo=False,                # Log SQL statements
    echo_pool="debug",         # Log pool events
    
    # Connect args (passed to DBAPI)
    connect_args={
        "sslmode": "require",
        "statement_cache_size": 30
    }
)
```

### Async Session Factory

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)
```

## Async Connection Management

### Using Async Connections

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select

async def fetch_users():
    async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    
    async with async_engine.connect() as conn:
        result = await conn.execute(select(users))
        for row in result:
            print(row.username)

# Run the async function
asyncio.run(fetch_users())
```

### Connection Pool Management

```python
async def manage_pool():
    async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    
    # Get pool status
    pool = async_engine.pool
    print(f"Pool size: {pool.size()}")
    print(f"Checked out: {pool.checkedout()}")
    
    # Dispose pool (close all connections)
    await async_engine.dispose()
```

## Async Session Usage

### Basic CRUD Operations

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select

async def crud_operations():
    async with AsyncSessionLocal() as session:
        # CREATE
        user = User(username="alice", email="alice@example.com")
        session.add(user)
        await session.flush()  # Get generated ID
        print(f"Created user with ID: {user.id}")
        
        # READ
        result = await session.execute(
            select(User).where(User.id == user.id)
        )
        fetched_user = result.scalar_one()
        print(f"Fetched user: {fetched_user.username}")
        
        # UPDATE
        fetched_user.email = "newemail@example.com"
        await session.commit()
        
        # DELETE
        await session.delete(fetched_user)
        await session.commit()

asyncio.run(crud_operations())
```

### Transaction Management

```python
async def transaction_example():
    async with AsyncSessionLocal() as session:
        try:
            # Begin transaction (auto-commits on success)
            async with session.begin():
                user = User(username="alice")
                session.add(user)
                
                post = Post(title="Hello", author_id=user.id)
                session.add(post)
                
                # Auto-commits here if no exception
        
        except Exception as e:
            # Automatic rollback on exception
            print(f"Transaction failed: {e}")
            raise
```

### Nested Transactions (Savepoints)

```python
async def nested_transaction():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(username="alice")
            session.add(user)
            
            try:
                async with session.begin_nested():  # Savepoint
                    risky_operation()
            except Exception:
                # Rollback to savepoint only
                await session.rollback()
                print("Inner transaction rolled back")
            
            # Outer transaction can still commit
            await session.commit()
```

## Async Querying

### Basic Queries

```python
from sqlalchemy import select, func

async def query_examples():
    async with AsyncSessionLocal() as session:
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        # Get single user
        result = await session.execute(
            select(User).where(User.username == "alice")
        )
        user = result.scalar_one_or_none()
        
        # Get first match
        result = await session.execute(
            select(User).where(User.age >= 18)
        )
        adult_user = result.scalars().first()
        
        # Count
        result = await session.execute(
            select(func.count(User.id))
        )
        count = result.scalar()
        
        return users, user, adult_user, count
```

### Query with Joins

```python
async def query_with_joins():
    async with AsyncSessionLocal() as session:
        # Join query
        stmt = (
            select(User, Post)
            .join(Post, User.id == Post.author_id)
            .where(Post.title.like("%SQL%"))
        )
        
        result = await session.execute(stmt)
        for user, post in result:
            print(user.username, post.title)
```

### Bulk Operations

```python
async def bulk_operations():
    async with AsyncSessionLocal() as session:
        # Bulk insert
        users_data = [
            {"username": "user1", "email": "user1@example.com"},
            {"username": "user2", "email": "user2@example.com"},
        ]
        
        await session.bulk_insert_mappings(User, users_data)
        await session.commit()
        
        # Bulk update
        from sqlalchemy import update
        
        stmt = (
            update(User)
            .where(User.age >= 18)
            .values(status="adult")
        )
        
        result = await session.execute(stmt)
        print(f"Updated {result.rowcount} rows")
        await session.commit()
```

## Async Eager Loading

### Selectin Load

```python
from sqlalchemy.orm import selectinload

async def eager_load_selectin():
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .options(selectinload(User.posts))
        )
        
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        # Posts already loaded for all users
        for user in users:
            print(user.username, [p.title for p in user.posts])
```

### Joined Load

```python
from sqlalchemy.orm import joinedload

async def eager_load_joined():
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .options(joinedload(User.posts))
        )
        
        result = await session.execute(stmt)
        users = result.scalars().all()
```

### Multiple Relationships

```python
async def load_multiple_relationships():
    async with AsyncSessionLocal() as session:
        stmt = (
            select(User)
            .options(
                selectinload(User.posts).selectinload(Post.comments),
                joinedload(User.profile)
            )
        )
        
        result = await session.execute(stmt)
        users = result.scalars().all()
```

## Async Engine Patterns

### Application Setup

```python
from contextlib import asynccontextmanager

class Database:
    def __init__(self, url: str):
        self.url = url
        self.engine = None
        self.session_maker = None
    
    async def connect(self):
        self.engine = create_async_engine(
            self.url,
            echo=True,
            pool_size=20,
            max_overflow=10
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
    
    @asynccontextmanager
    async def session_scope(self):
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# Usage in FastAPI
db = Database("postgresql+asyncpg://user:pass@localhost/db")

@asynccontextmanager
async def lifespan(app):
    await db.connect()
    yield
    await db.disconnect()
```

### Dependency Injection (FastAPI)

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with db.session_scope() as session:
        yield session

@app.get("/users/")
async def list_users(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "username": u.username} for u in users]
```

## Async with ORM Models

### Model Definition (Same as Sync)

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(120))
```

### Async Repository Pattern

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.get(User, user_id)
        return result
    
    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update(self, user_id: int, user_data: dict) -> User | None:
        user = await self.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            return user
        return None
    
    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            return True
        return False
```

## Async Best Practices

### 1. Always Use Context Managers

```python
# Good
async with AsyncSessionLocal() as session:
    # ... work with session

# Bad - manual cleanup needed
session = AsyncSessionLocal()
try:
    # ...
finally:
    await session.close()
```

### 2. Batch Operations for Performance

```python
async def batch_insert():
    async with AsyncSessionLocal() as session:
        users = [User(username=f"user{i}") for i in range(1000)]
        
        # Add all at once
        session.add_all(users)
        await session.flush()  # Single flush
        
        # Or use bulk insert
        await session.bulk_insert_mappings(User, [
            {"username": f"user{i}"} for i in range(1000)
        ])
```

### 3. Use Connection Pooling Wisely

```python
async_engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=20,          # Match expected concurrent connections
    max_overflow=10,       # Allow burst capacity
    pool_recycle=3600,     # Prevent stale connections
    pool_pre_ping=True     # Verify connection health
)
```

### 4. Handle Timeouts

```python
import asyncio

async def query_with_timeout():
    try:
        async with AsyncSessionLocal() as session:
            result = await asyncio.wait_for(
                session.execute(select(User)),
                timeout=5.0  # 5 second timeout
            )
    except asyncio.TimeoutError:
        print("Query timed out")
        raise
```

## Platform Installation Notes

### Async Dependencies

SQLAlchemy async support requires `greenlet`:

```bash
# Install with async support (includes greenlet)
pip install "sqlalchemy[asyncio]"

# Or install manually
pip install sqlalchemy greenlet
```

### Database-Specific Drivers

**PostgreSQL:**
```bash
pip install asyncpg
```

**MySQL:**
```bash
pip install aiomysql
# or
pip install asyncmy  # Pure Python MySQL driver
```

**SQLite:**
```bash
pip install aiosqlite
```

### Apple M1/M2 Installation

```bash
# May need to install greenlet manually
pip install --upgrade pip
pip install "greenlet>=3.0.0"
pip install "sqlalchemy[asyncio]"
```

## Troubleshooting

### Common Issues

**1. Greenlet Import Error**

```python
# Error: No module named 'greenlet'

# Solution: Install greenlet
pip install greenlet
```

**2. Connection Pool Exhaustion**

```python
# Increase pool size
async_engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=50,
    max_overflow=20
)
```

**3. Event Loop Issues**

```python
# Ensure you're running in async context
asyncio.run(main_function())  # Not just main_function()
```

## Migration from Sync to Async

### Before (Sync)

```python
with SessionLocal() as session:
    user = session.get(User, 1)
    user.username = "new"
    session.commit()
```

### After (Async)

```python
async with AsyncSessionLocal() as session:
    user = await session.get(User, 1)
    user.username = "new"
    await session.commit()
```

## Next Steps

- [ORM Querying](09-orm-querying.md) - Advanced query patterns
- [ORM Relationships](08-orm-relationships.md) - Relationship configuration
- [Best Practices](24-best-practices.md) - Performance optimization
- [Dialects](16-dialects-overview.md) - Database-specific async features
