---
name: sqlalchemy-2-0
description: Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when building Python applications that require database connectivity, object-relational mapping, or programmatic SQL generation with support for PostgreSQL, MySQL, SQLite, Oracle, and MSSQL.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - database
  - orm
  - sql
  - python
  - postgresql
  - mysql
  - sqlite
  - async
category: database
required_environment_variables:
  - name: DATABASE_URL
    prompt: "Enter your database connection URL (e.g., postgresql://user:pass@localhost/dbname)"
    help: "Database URL in format: dialect+driver://username:password@host:port/database"
    required_for: "database connectivity"

external_references:
  - https://docs.sqlalchemy.org/
  - https://github.com/sqlalchemy/sqlalchemy
---
## Overview
Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when building Python applications that require database connectivity, object-relational mapping, or programmatic SQL generation with support for PostgreSQL, MySQL, SQLite, Oracle, and MSSQL.

Complete toolkit for working with databases in Python using SQLAlchemy 2.0, including the Core SQL Expression Language and Object Relational Mapper (ORM). Supports synchronous and asynchronous operations across PostgreSQL, MySQL, SQLite, Oracle, and Microsoft SQL Server.

## When to Use
- Building Python applications requiring database connectivity
- Implementing object-relational mapping for domain models
- Constructing SQL queries programmatically with type safety
- Migrating from SQLAlchemy 1.x to 2.0 style
- Working with async/await database operations
- Needing database-agnostic code with dialect-specific features
- Building CRUD operations with transaction management
- Implementing complex queries with joins, aggregations, and subqueries

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Quick Setup
```bash
# Install SQLAlchemy with async support
pip install "sqlalchemy[asyncio]"

# Install database drivers as needed
pip install psycopg2-binary  # PostgreSQL
pip install mysqlclient      # MySQL
pip install aiomysql         # MySQL async
pip install asyncpg          # PostgreSQL async
```

## Architecture Overview
SQLAlchemy consists of two main components:

- **Core**: Foundational SQL toolkit with engine, connection pooling, SQL Expression Language, and schema definition
- **ORM**: Object Relational Mapper built on Core for mapping Python classes to database tables

See [Architecture Details](reference/01-architecture-overview.md) for comprehensive component breakdown.

## Usage Examples
### Basic Engine Creation

```python
from sqlalchemy import create_engine

# Synchronous engine
engine = create_engine("postgresql://user:pass@localhost/dbname")

# With connection pooling options
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)

# Async engine
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname"
)
```

See [Engine Configuration](reference/02-engine-connections.md) for complete options.

### Defining Models (ORM)

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    
    # Relationship to posts
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Back-reference to user
    author = relationship("User", back_populates="posts")
```

See [ORM Mapping Guide](reference/05-orm-mapping.md) for complete mapping options.

### Session Management

```python
from sqlalchemy.orm import sessionmaker, Session

# Create session factory
SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)

# Use session in context manager
with SessionLocal() as session:
    # Create
    user = User(username="alice", email="alice@example.com")
    session.add(user)
    session.commit()
    
    # Read
    user = session.query(User).filter_by(username="alice").first()
    
    # Update
    user.email = "newemail@example.com"
    session.commit()
    
    # Delete
    session.delete(user)
    session.commit()
```

See [Session Management](reference/06-orm-session.md) for transaction patterns.

### Core SELECT Queries

```python
from sqlalchemy import select

# Basic select
stmt = select(User).where(User.username == "alice")
result = session.execute(stmt)
user = result.scalar_one()

# Select specific columns
stmt = select(User.id, User.username).where(User.age > 18)

# Join queries
stmt = (
    select(User, Post)
    .join(Post, User.id == Post.user_id)
    .where(Post.title.like("%SQL%"))
)

# Aggregations
from sqlalchemy import func

stmt = select(func.count(User.id), func.avg(User.age))
```

See [Core Querying](reference/04-core-querying.md) for complete query guide.

### Async Operations

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, AsyncAttrs

# Models with AsyncAttrs support
class Base(AsyncAttrs, DeclarativeBase):
    pass

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,
    pool_size=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession,
    expire_on_commit=False  # Recommended for async
)

async def get_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.age > 18)
        )
        users = result.scalars().all()
        return users
```

See [AsyncIO Support](reference/07-orm-asyncio.md) for comprehensive async patterns including:
- Async engine and session configuration
- Preventing implicit IO with AsyncAttrs and eager loading
- Running sync code under asyncio with run_sync()
- Events with async engines and sessions
- Async scoped sessions for task-local management
- Streaming results and result set API

## Advanced Topics
## Advanced Topics

- [Architecture Overview](reference/01-architecture-overview.md)
- [Engine Connections](reference/02-engine-connections.md)
- [Core Schema Types](reference/03-core-schema-types.md)
- [Core Querying](reference/04-core-querying.md)
- [Orm Mapping](reference/05-orm-mapping.md)
- [Orm Session](reference/06-orm-session.md)
- [Orm Asyncio](reference/07-orm-asyncio.md)
- [Orm Relationships](reference/08-orm-relationships.md)
- [Orm Querying](reference/09-orm-querying.md)
- [Orm Hybrid Attributes](reference/10-orm-hybrid-attributes.md)
- [Orm Extensions](reference/11-orm-extensions.md)
- [Core Sql Expressions](reference/12-core-sql-expressions.md)
- [Core Reflection](reference/13-core-reflection.md)
- [Core Events](reference/14-core-events.md)
- [Core Custom Types](reference/15-core-custom-types.md)
- [Dialects Overview](reference/16-dialects-overview.md)
- [Dialect Postgresql](reference/17-dialect-postgresql.md)
- [Migration And Troubleshooting](reference/18-migration-and-troubleshooting.md)
- [Best Practices](reference/19-best-practices.md)

## Common Patterns
### N+1 Query Problem Solution

```python
# BAD: Causes N+1 queries
users = session.query(User).all()
for user in users:
    print(user.username, [p.title for p in user.posts])  # Query per user!

# GOOD: Use joinedload
from sqlalchemy.orm import joinedload

users = session.query(User).options(
    joinedload(User.posts)
).all()
for user in users:
    print(user.username, [p.title for p in user.posts])  # Posts already loaded
```

### Transaction Management

```python
# Using context manager (recommended)
with SessionLocal() as session:
    try:
        session.add(user)
        session.commit()
    except:
        session.rollback()
        raise

# Manual rollback on error
session = SessionLocal()
try:
    session.add(user)
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()
```

### Bulk Operations

```python
# Bulk insert (faster, no identity flush)
session.bulk_insert_mappings(User, [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
])

# Bulk update
session.query(User).filter(
    User.username.in_(["user1", "user2"])
).update({"email": "updated@example.com"})
```

## Troubleshooting
### Common Issues

- **ConnectionPoolError**: Check pool_size and max_overflow settings
- **StatementError**: Verify SQL syntax and column names
- **DetachedInstanceError**: Ensure object is attached to active session
- **FlushError**: Check for constraint violations before commit

See [Troubleshooting Guide](reference/18-migration-and-troubleshooting.md) for detailed solutions.

### Enable Echo for Debugging

```python
# Log all SQL statements
engine = create_engine("postgresql://...", echo=True)

# Or use logging
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

## Key Concepts
- **Engine**: Entry point for database connectivity, manages connection pool
- **Connection**: Represents single database connection from pool
- **Session**: ORM interface for transactional persistence (unit of work)
- **Metadata**: Container for table definitions and schema objects
- **DeclarativeBase**: Base class for ORM model classes
- **Relationship**: Defines associations between mapped classes
- **Select**: Construct for building SELECT statements
- **Result**: Container for query results with row access

See [Glossary](reference/18-migration-and-troubleshooting.md#sqlalchemy-glossary) for complete terminology.

## Performance Tips
1. Use connection pooling appropriately for your workload
2. Prefer `select()` over legacy `Query` API in 2.0
3. Use eager loading (joinedload, subqueryload) to avoid N+1 queries
4. Consider bulk operations for large data imports
5. Use async engine for I/O-bound applications
6. Index foreign keys and frequently queried columns

See [Best Practices](reference/19-best-practices.md) for comprehensive guidance.

