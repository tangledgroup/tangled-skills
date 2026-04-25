# Migration to SQLAlchemy 2.0 and Troubleshooting

## Migration from SQLAlchemy 1.x to 2.0

### Key Breaking Changes

#### 1. Query API Changes

**Before (1.x style):**
```python
# Old Query API - deprecated in 2.0
users = session.query(User).filter(User.age >= 18).all()
count = session.query(func.count(User.id)).scalar()
```

**After (2.0 style):**
```python
# New select() API - required in 2.0
from sqlalchemy import select

users = session.execute(
    select(User).where(User.age >= 18)
).scalars().all()

count = session.execute(
    select(func.count(User.id))
).scalar()
```

#### 2. Session API Changes

**Before (1.x):**
```python
# Old Session API
session = Session()
user = session.query(User).get(1)
```

**After (2.0):**
```python
# New Session API - use class_=Session
from sqlalchemy.orm import Session, sessionmaker

SessionLocal = sessionmaker(bind=engine, class_=Session)
session = SessionLocal()

user = session.get(User, 1)  # Same but requires new Session class
```

#### 3. Result Access Changes

**Before (1.x):**
```python
# Old result access
result = session.query(User).filter(...).all()
user = result[0]
```

**After (2.0):**
```python
# New result access with execute()
result = session.execute(select(User).where(...))
users = result.scalars().all()
user = users[0]

# Or get single scalar
count = session.execute(select(func.count())).scalar()
```

#### 4. Declarative Base Changes

**Before (1.x):**
```python
# Old declarative base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
```

**After (2.0):**
```python
# New declarative base - recommended
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

# Or with typed columns (2.0+)
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
```

### Migration Steps

#### Step 1: Update Imports

```python
# Replace old imports
from sqlalchemy.ext.declarative import declarative_base
# With new imports
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# Replace Query import
from sqlalchemy.orm import Query
# With select construct
from sqlalchemy import select
```

#### Step 2: Update Query Patterns

Create a migration helper:

```python
# Migration script to find old patterns
import re

def find_old_queries(file_path):
    with open(file_path) as f:
        content = f.read()
    
    # Find .query() usage
    queries = re.findall(r'session\.query\([^)]+\)', content)
    for q in queries:
        print(f"Found old query: {q}")
    
    # Find .filter() usage (should be .where())
    filters = re.findall(r'\.filter\([^)]+\)', content)
    for f in filters:
        print(f"Found filter (use where): {f}")
```

#### Step 3: Update Relationship Loading

**Before:**
```python
# Old eager loading
users = session.query(User).options(
    joinedload(User.posts),
    contains_eager(User.profile)
).all()
```

**After:**
```python
# New eager loading
from sqlalchemy.orm import selectinload, joinedload

stmt = (
    select(User)
    .options(
        selectinload(User.posts),
        joinedload(User.profile)
    )
)
users = session.execute(stmt).scalars().all()
```

#### Step 4: Update Bulk Operations

**Before:**
```python
# Old bulk insert
session.bulk_insert_mappings(User, [
    {"username": "alice"},
    {"username": "bob"}
])
```

**After (same, but note behavior changes):**
```python
# Bulk insert - no identity flush by default
session.bulk_insert_mappings(User, [
    {"username": "alice"},
    {"username": "bob"}
])

# For bulk update, use update() construct
from sqlalchemy import update

stmt = (
    update(User)
    .where(User.age >= 18)
    .values(status="adult")
)
session.execute(stmt)
```

### Common Migration Issues

#### Issue 1: AttributeError on Session

```python
# Error: 'Session' object has no attribute 'query'

# Solution: Use select() instead
# Bad
users = session.query(User).all()

# Good
from sqlalchemy import select
users = session.execute(select(User)).scalars().all()
```

#### Issue 2: Result Access Errors

```python
# Error: 'Result' object is not subscriptable

# Bad
result = session.execute(select(User))
user = result[0]  # Error!

# Good
result = session.execute(select(User))
user = result.scalars().first()
# or
users = result.scalars().all()
user = users[0]
```

#### Issue 3: Missing scalars() Call

```python
# Error: getting list of Row objects instead of model instances

# Bad - returns list of Row tuples
result = session.execute(select(User))
users = result.all()  # List of Rows

# Good - returns list of User instances
result = session.execute(select(User))
users = result.scalars().all()  # List of Users
```

## Troubleshooting Guide

### Common Errors and Solutions

#### IntegrityError (Constraint Violation)

```python
from sqlalchemy.exc import IntegrityError

try:
    session.add(user)
    session.commit()
except IntegrityError as e:
    session.rollback()
    
    # Check specific error
    if "unique constraint" in str(e.orig):
        print("Duplicate value detected")
    elif "foreign key constraint" in str(e.orig):
        print("Referenced object doesn't exist")
    
    raise
```

#### DetachedInstanceError

```python
# Error: Object is not attached to a session

# Problem
session1 = SessionLocal()
user = session1.get(User, 1)
session1.close()

session2 = SessionLocal()
user.username = "new"  # Error! User is detached
session2.commit()

# Solution 1: Use merge
session2.merge(user)
session2.commit()

# Solution 2: Keep session open
with SessionLocal() as session:
    user = session.get(User, 1)
    user.username = "new"
    # Auto-commits
```

#### FlushError

```python
from sqlalchemy.exc import FlushError

try:
    session.flush()
except FlushError as e:
    session.rollback()
    print(f"Flush failed: {e}")
    
    # Check for validation errors, constraint violations
    raise
```

#### StatementError (SQL Syntax)

```python
from sqlalchemy.exc import StatementError

try:
    session.execute(select(User).where(invalid_syntax))
except StatementError as e:
    print(f"SQL error: {e.statement}")
    print(f"Params: {e.params}")
    print(f"Origin: {e.orig}")
    
    # Enable echo=True on engine to see full SQL
    raise
```

#### OperationalError (Connection Issues)

```python
from sqlalchemy.exc import OperationalError

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except OperationalError as e:
    print(f"Connection failed: {e}")
    
    # Common causes:
    # - Database not running
    # - Wrong credentials
    # - Network issues
    # - Connection pool exhausted
    
    # Enable pool_pre_ping to catch stale connections
    engine = create_engine("...", pool_pre_ping=True)
```

### Performance Issues

#### N+1 Query Problem

**Symptom:** Many queries for simple operations

**Detection:**
```python
# Enable echo to see all queries
engine = create_engine("...", echo=True)

# Or use logging
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

**Solution - Use Eager Loading:**
```python
from sqlalchemy.orm import selectinload

# Bad - N+1 queries
users = session.execute(select(User)).scalars().all()
for user in users:
    print(user.username, [p.title for p in user.posts])  # Query per user!

# Good - 2 queries total
stmt = (
    select(User)
    .options(selectinload(User.posts))
)
users = session.execute(stmt).scalars().all()
for user in users:
    print(user.username, [p.title for p in user.posts])  # Posts already loaded!
```

#### Slow Queries

**Detection:**
```python
from sqlalchemy import event
import time

@event.listens_for(Engine, "before_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    conn.info['query_start'] = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def check_query_time(conn, cursor, statement, parameters, context, executemany):
    duration = (time.time() - conn.info.get('query_start', time.time())) * 1000
    
    if duration > 100:  # > 100ms
        print(f"SLOW QUERY ({duration:.2f}ms): {statement[:200]}")
```

**Solutions:**
1. Add indexes on filtered columns
2. Use select() only needed columns
3. Avoid SELECT * in production
4. Use connection pooling properly

#### Memory Issues with Large Result Sets

**Problem:** Loading millions of rows at once

**Solution - Use Streaming:**
```python
# Bad - loads all into memory
users = session.execute(select(User)).scalars().all()  # 1M users!

# Good - process in batches
result = session.execute(
    select(User).yield_per(1000)  # Stream 1000 at a time
)
for user in result.scalars():
    process(user)  # Process one at a time
```

### Connection Pool Issues

#### Pool Exhaustion

**Symptom:** `QueuePool limit of size X overflow Y reached`

**Solution:**
```python
# Increase pool size
engine = create_engine(
    "postgresql://...",
    pool_size=50,        # Increase base size
    max_overflow=50,     # Allow more overflow
    pool_timeout=30,     # Wait up to 30 seconds
    pool_recycle=3600    # Recycle stale connections
)

# Check for connection leaks
print(f"Checked out: {engine.pool.checkedout()}")
print(f"Overflow: {engine.pool.overflow()}")
```

#### Stale Connections

**Symptom:** `connection lost`, `server closed the connection`

**Solution:**
```python
# Enable pre-ping to test connections
engine = create_engine(
    "postgresql://...",
    pool_pre_ping=True,   # Test before use
    pool_recycle=3600     # Recycle after 1 hour
)
```

### Debugging Techniques

#### Enable SQL Logging

```python
# Simple echo mode
engine = create_engine("postgresql://...", echo=True)

# Detailed logging with timing
import logging
from sqlalchemy import engine_from_config

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

# Log pool events
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
```

#### Show Bound Parameters

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def log_parameters(conn, cursor, statement, parameters, context, executemany):
    print(f"SQL: {statement}")
    print(f"Params: {parameters}")
```

#### Profile Query Performance

```python
import cProfile
import pstats

def profile_queries():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run your code
    users = session.execute(select(User)).scalars().all()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

profile_queries()
```

## SQLAlchemy Glossary

### Core Terms

- **Engine**: Entry point for database connectivity, manages connection pool
- **Connection**: Single database connection from the pool
- **Result**: Container for query results with row access methods
- **MetaData**: Container for Table objects and schema definitions
- **Table**: Representation of a database table
- **Column**: Column definition with type and constraints
- **Select**: SQL SELECT statement construct
- **Dialect**: Database-specific implementation layer

### ORM Terms

- **Session**: Unit of Work manager for object persistence
- **Mapper**: Configuration linking Python class to database table
- **Identity Map**: Session's cache of loaded objects
- **Unit of Work**: Pattern tracking object changes for batch commit
- **Relationship**: Association between mapped classes
- **Eager Loading**: Pre-fetching related objects
- **Lazy Loading**: Loading relationships on first access
- **Cascade**: Operations that propagate to related objects

### General Terms

- **CRUD**: Create, Read, Update, Delete operations
- **DDL**: Data Definition Language (CREATE, ALTER, DROP)
- **DML**: Data Manipulation Language (INSERT, UPDATE, DELETE)
- **DBAPI**: Python Database API Specification (PEP 249)
- **Reflection**: Schema introspection from existing database
- **Binding**: Associating tables/classes with specific engines

## Best Practices Summary

### 1. Use Context Managers

```python
# Good
with SessionLocal() as session:
    user = User(username="alice")
    session.add(user)
    session.commit()

# Bad - manual cleanup needed
session = SessionLocal()
try:
    # ...
finally:
    session.close()
```

### 2. Keep Transactions Short

```python
# Good - quick transaction
with SessionLocal() as session:
    user = session.get(User, 1)
    user.username = "new"
    session.commit()  # Fast commit

# Bad - long transaction with external calls
with SessionLocal() as session:
    user = session.get(User, 1)
    process_external_api()  # Takes 5 seconds!
    send_email()  # Takes 2 seconds!
    user.username = "new"
    session.commit()  # Holds locks too long
```

### 3. Use Appropriate Eager Loading

```python
# Good - load what you need
stmt = (
    select(User)
    .options(selectinload(User.posts))
)

# Bad - over-eager loading
stmt = (
    select(User)
    .options(
        selectinload(User.posts).selectinload(Post.comments)
        .selectinload(Comment.replies)
        .selectinload(Reply.votes)
    )
)  # Massive query!
```

### 4. Handle Errors Properly

```python
from sqlalchemy.exc import SQLAlchemyError

try:
    with SessionLocal() as session:
        # ... operations
        session.commit()
except SQLAlchemyError as e:
    # Automatic rollback on exception
    logger.error(f"Database error: {e}")
    raise
```

## Next Steps

- [Best Practices](24-best-practices.md) - Comprehensive performance guide
- [Core Querying](04-core-querying.md) - Advanced query patterns
- [ORM Session](06-orm-session.md) - Transaction management
- [Engine Configuration](02-engine-connections.md) - Pool tuning
