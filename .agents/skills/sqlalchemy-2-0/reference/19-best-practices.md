# SQLAlchemy 2.0 Best Practices

## Application Architecture

### Recommended Project Structure

```
myapp/
├── __init__.py
├── models.py           # ORM model definitions
├── database.py         # Engine and session setup
├── repositories/       # Data access layer
│   ├── __init__.py
│   ├── user_repository.py
│   └── post_repository.py
├── services/           # Business logic layer
│   ├── __init__.py
│   └── user_service.py
└── api/               # API endpoints (if applicable)
    └── users.py
```

### Database Module Setup

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from contextlib import contextmanager
import os

class Base(DeclarativeBase):
    pass

# Create engine with production settings
engine = create_engine(
    os.getenv("DATABASE_URL", "postgresql://localhost/dev"),
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    echo=os.getenv("DEBUG") == "true"
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

@contextmanager
def get_session():
    """Context manager for session lifecycle"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# For dependency injection (FastAPI, etc.)
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
```

### Model Definition Best Practices

```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """Mixin for created_at and updated_at"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships with explicit lazy loading
    posts = relationship("Post", back_populates="author", lazy="selectin")
    profile = relationship("UserProfile", uselist=False, back_populates="user", lazy="joined")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

## Query Patterns

### Repository Pattern

```python
# repositories/user_repository.py
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from typing import Optional, List
from models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with posts loaded"""
        return self.session.get(User, user_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def get_active_users(self, limit: int = 100) -> List[User]:
        """Get active users with posts eagerly loaded"""
        stmt = (
            select(User)
            .where(User.is_active == True)
            .options(selectinload(User.posts))
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
    
    def create(self, username: str, email: str) -> User:
        """Create new user"""
        user = User(username=username, email=email)
        self.session.add(user)
        self.session.flush()  # Get ID without committing
        return user
    
    def update_email(self, user_id: int, new_email: str) -> Optional[User]:
        """Update user email"""
        user = self.get_by_id(user_id)
        if user:
            user.email = new_email
            return user
        return None
    
    def delete(self, user_id: int) -> bool:
        """Soft delete user"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False
```

### Service Layer Pattern

```python
# services/user_service.py
from repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from typing import Optional

class UserService:
    def __init__(self, session: Session):
        self.repo = UserRepository(session)
    
    def register_user(self, username: str, email: str) -> Optional[User]:
        """Register new user with validation"""
        # Check if user exists
        existing = self.repo.get_by_username(username)
        if existing:
            raise ValueError("Username already exists")
        
        # Validate email
        if "@" not in email:
            raise ValueError("Invalid email address")
        
        # Create user
        return self.repo.create(username, email)
    
    def get_user_posts(self, user_id: int):
        """Get user with their posts"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.posts))
        )
        return self.session.execute(stmt).scalar_one_or_none()
```

## Performance Optimization

### Connection Pool Tuning

```python
# Small application (< 10 concurrent users)
engine = create_engine(
    "postgresql://...",
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)

# Medium application (10-100 concurrent users)
engine = create_engine(
    "postgresql://...",
    pool_size=20,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

# Large application (100+ concurrent users)
engine = create_engine(
    "postgresql://...",
    pool_size=50,
    max_overflow=50,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=30
)

# Read-heavy application (separate read replicas)
read_engine = create_engine("postgresql://replica/db", pool_size=20)
write_engine = create_engine("postgresql://primary/db", pool_size=10)
```

### Query Optimization

#### 1. Select Only Needed Columns

```python
# Bad - loads all columns
users = session.execute(select(User)).scalars().all()

# Good - only needed columns
from sqlalchemy import select
stmt = select(User.id, User.username, User.email)
result = session.execute(stmt)
```

#### 2. Use Indexes Strategically

```python
from sqlalchemy import Index

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)  # FK index
    title = Column(String(200), index=True)  # Frequently searched
    created_at = Column(DateTime, index=True)  # Ordered by date
    status = Column(String(20), index=True)  # Filtered often
    
    # Composite index for common query pattern
    __table_args__ = (
        Index("ix_posts_author_created", "author_id", "created_at.desc"),
    )
```

#### 3. Avoid N+1 Queries

```python
# Bad - N+1 queries
users = session.execute(select(User)).scalars().all()
total_posts = 0
for user in users:
    total_posts += len(user.posts)  # Query per user!

# Good - single query with JOIN
from sqlalchemy import func
stmt = (
    select(func.sum(func.count(Post.id)))
    .join(Post, User.id == Post.author_id)
    .correlate(User)
    .scalar_subquery()
)

# Or eager load if you need the posts
from sqlalchemy.orm import selectinload
stmt = (
    select(User)
    .options(selectinload(User.posts))
)
users = session.execute(stmt).scalars().all()
```

#### 4. Batch Large Operations

```python
# Bad - one commit per object
for i in range(10000):
    user = User(username=f"user{i}")
    session.add(user)
    session.commit()  # 10,000 commits!

# Good - batch commits
batch_size = 500
for i in range(10000):
    user = User(username=f"user{i}")
    session.add(user)
    
    if i % batch_size == 0:
        session.commit()

session.commit()  # Final commit
```

### Async Performance

```python
# Use async for I/O-bound operations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession)

async def fetch_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()
```

## Security Best Practices

### Parameterized Queries (Always!)

```python
# Good - parameterized (SQLAlchemy does this automatically)
stmt = select(User).where(User.username == username_param)
result = session.execute(stmt, {"username_param": user_input})

# Bad - string formatting (NEVER DO THIS!)
# stmt = text(f"SELECT * FROM users WHERE username = '{user_input}'")  # SQL injection!
```

### ORM Prevents Most SQL Injection

```python
# SQLAlchemy automatically parameterizes
user = session.execute(
    select(User).where(User.username == user_input)
).scalar_one_or_none()

# Even with raw text, use parameters
result = session.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": user_input}
)
```

### Validate Input Data

```python
from sqlalchemy.orm import events

@events.listens_for(User, "before_insert")
def validate_user_data(mapper, connection, target):
    """Validate data before insert"""
    if not target.username or len(target.username) < 3:
        raise ValueError("Username must be at least 3 characters")
    
    if not target.email or "@" not in target.email:
        raise ValueError("Invalid email address")
```

## Testing Best Practices

### In-Memory SQLite for Tests

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

@pytest.fixture
def engine():
    """Create in-memory SQLite database for tests"""
    return create_engine(
        "sqlite:///:memory:",
        echo=True,
        future=True
    )

@pytest.fixture
def session(engine):
    """Create test session"""
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine, class_=Session)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def user(session):
    """Create test user"""
    from models import User
    user = User(username="testuser", email="test@example.com")
    session.add(user)
    session.commit()
    return user
```

### Test Queries

```python
def test_get_user_by_username(session, user):
    from sqlalchemy import select
    
    stmt = select(User).where(User.username == "testuser")
    result = session.execute(stmt).scalar_one_or_none()
    
    assert result is not None
    assert result.username == "testuser"

def test_create_user(service):
    user = service.register_user("newuser", "new@example.com")
    
    assert user.username == "newuser"
    assert user.email == "new@example.com"
```

## Monitoring and Observability

### Query Logging in Production

```python
import logging
from sqlalchemy import event

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("sqlalchemy.slow_queries")
logger.setLevel(logging.WARNING)

@event.listens_for(Engine, "after_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    if hasattr(conn, 'info') and 'query_start' in conn.info:
        duration = (time.time() - conn.info['query_start']) * 1000
        
        if duration > 100:  # Log queries > 100ms
            logger.warning(
                f"Slow query ({duration:.2f}ms): {statement[:200]}..."
            )

@event.listens_for(Engine, "before_cursor_execute")
def track_query_start(conn, cursor, statement, parameters, context, executemany):
    conn.info['query_start'] = time.time()
```

### Health Checks

```python
def check_database_health(engine):
    """Check database connectivity and performance"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1"))
            
            # Check connection pool status
            pool_status = {
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow()
            }
            
            return {"status": "healthy", "pool": pool_status}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Common Anti-Patterns to Avoid

### 1. Loading All Data

```python
# Bad - loads entire table
all_users = User.query.all()
for user in all_users:
    process(user)

# Good - paginate or stream
result = session.execute(
    select(User).yield_per(100)
)
for user in result.scalars():
    process(user)
```

### 2. Using ORM for Bulk Operations

```python
# Bad - slow, loads objects into memory
users = session.execute(select(User)).scalars().all()
for user in users:
    user.status = "inactive"
session.commit()

# Good - direct SQL update
from sqlalchemy import update
stmt = (
    update(User)
    .where(User.age >= 65)
    .values(status="senior")
)
session.execute(stmt)
session.commit()
```

### 3. Keeping Sessions Open Too Long

```python
# Bad - session holds locks during external calls
session = SessionLocal()
user = session.get(User, 1)
external_api_call()  # Takes 5 seconds!
send_email()  # Takes 2 seconds!
user.username = "new"
session.commit()
session.close()

# Good - short transactions
with SessionLocal() as session:
    user = session.get(User, 1)

external_api_call()  # No session open
send_email()  # No session open

with SessionLocal() as session:
    user = session.get(User, 1)
    user.username = "new"
    # Auto-commits quickly
```

### 4. Ignoring Error Handling

```python
# Bad - no error handling
user = User(username="test")
session.add(user)
session.commit()  # If this fails, session is in bad state

# Good - proper error handling
try:
    with SessionLocal() as session:
        user = User(username="test")
        session.add(user)
        session.commit()
except SQLAlchemyError as e:
    logger.error(f"Failed to create user: {e}")
    raise
```

## Summary Checklist

- [ ] Use context managers for sessions
- [ ] Enable pool_pre_ping in production
- [ ] Set appropriate pool_size and max_overflow
- [ ] Use eager loading strategically (selectinload)
- [ ] Select only needed columns
- [ ] Add indexes on filtered/joined columns
- [ ] Batch large operations
- [ ] Use async for I/O-bound applications
- [ ] Validate input data
- [ ] Handle errors with proper rollback
- [ ] Keep transactions short
- [ ] Monitor slow queries
- [ ] Test with in-memory SQLite
- [ ] Use repository pattern for data access
- [ ] Separate business logic from data access

## Next Steps

- [Architecture Overview](01-architecture-overview.md) - Component design
- [Engine Configuration](02-engine-connections.md) - Pool settings
- [ORM Querying](09-orm-querying.md) - Query patterns
- [Migration Guide](18-migration-and-troubleshooting.md) - Upgrade from 1.x
