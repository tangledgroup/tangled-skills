# SQLAlchemy 2.0 Architecture Overview

## Component Architecture

SQLAlchemy is organized into distinct layers that can be used individually or combined:

```
┌─────────────────────────────────────┐
│         ORM (Object Mapper)         │
│  - Declarative Mapping              │
│  - Session / Unit of Work           │
│  - Relationship Management          │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           Core (SQL Toolkit)        │
│  - SQL Expression Language          │
│  - Engine & Connection Pooling      │
│  - Schema Definition                │
│  - Type System                      │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          Dialect Layer              │
│  - PostgreSQL, MySQL, SQLite        │
│  - Oracle, MSSQL                    │
│  - DBAPI Integration                │
└─────────────────────────────────────┘
```

## Major Components

### Core Components

**Engine** (`sqlalchemy.Engine`)
- Entry point for all database operations
- Manages connection pool
- Handles dialect-specific communication
- Creates connections and executes SQL statements

**Connection** (`sqlalchemy.engine.Connection`)
- Represents single database connection
- Executes SQL statements
- Manages transaction context
- Returned from engine or used in context manager

**Result** (`sqlalchemy.engine.Result`)
- Container for query results
- Provides row access methods (scalar, rows, dicts)
- Supports iteration and indexing
- Works with both Core and ORM queries

**MetaData** (`sqlalchemy.MetaData`)
- Container for Table objects and schema constructs
- Tracks relationships between tables
- Used for reflection and schema generation
- Shared across related table definitions

### ORM Components

**Session** (`sqlalchemy.orm.Session`)
- Primary interface for ORM operations
- Implements Unit of Work pattern
- Tracks object state changes
- Manages transactions for persistence

**DeclarativeBase** (`sqlalchemy.orm.DeclarativeBase`)
- Base class for mapped classes
- Provides metadata container
- Enables declarative table definition
- Supports inheritance patterns

**Mapper** (`sqlalchemy.orm.Mapper`)
- Configuration object linking class to table
- Manages column-to-attribute mapping
- Handles relationship configuration
- Controls loading and persistence behavior

## Installation Guide

### Supported Platforms

- **cPython**: 3.7 and higher
- **PyPy**: Python-3 compatible versions

**Note**: SQLAlchemy 2.0 dropped support for Python 3.6 and below.

### Basic Installation

```bash
# Install latest stable version
pip install SQLAlchemy

# Install with async support (recommended)
pip install "sqlalchemy[asyncio]"

# Install specific version
pip install "SQLAlchemy>=2.0,<3.0"
```

### Installing Database Drivers

SQLAlchemy requires DBAPI drivers for each database:

**PostgreSQL:**
```bash
# Synchronous
pip install psycopg2-binary

# Async
pip install asyncpg
```

**MySQL/MariaDB:**
```bash
# Synchronous
pip install mysqlclient

# Async
pip install aiomysql
```

**SQLite:**
```bash
# Built into Python, no installation needed
# Optional: faster implementation
pip install sqlite-fts5
```

**Oracle:**
```bash
pip install cx_Oracle
```

**Microsoft SQL Server:**
```bash
# Using pyodbc
pip install pyodbc

# Or using pymssql
pip install pymssql
```

### Checking Installation

```python
import sqlalchemy
print(sqlalchemy.__version__)  # e.g., "2.0.49"

# Check async support
try:
    from sqlalchemy.ext.asyncio import create_async_engine
    print("AsyncIO support available")
except ImportError:
    print("AsyncIO support not available")
```

### Cython Extensions

SQLAlchemy includes optional Cython extensions for performance:

```bash
# Install with Cython (automatic if Cython available)
pip install SQLAlchemy

# Manual build from source
cd sqlalchemy-source
python setup.py build_ext --inplace
python setup.py install
```

**Benefits:**
- Faster result set processing
- Improved Core performance
- Minimal overhead for ORM operations

## Version Information

### Current Release

- **Version**: 2.0.49 (April 2026)
- **Status**: Stable, production-ready
- **Python Support**: 3.7+

### Version History Highlights

**SQLAlchemy 2.0:**
- New `select()` based query style for ORM
- DeclarativeBase as recommended mapping approach
- Improved async/await support
- Enhanced type system with Python typing
- Removed legacy Query API (use select() instead)

**SQLAlchemy 1.4:**
- Transitional release with 2.0 features
- Introduced new Session API
- Added async engine support
- Maintained backward compatibility

**SQLAlchemy 1.3 and earlier:**
- Legacy API style
- Session.query() based querying
- Classic declarative base

## Documentation Structure

### Tutorial Path (Recommended for New Users)

1. **Unified Tutorial**: Complete introduction to Core and ORM
2. **ORM Quick Start**: Brief ORM overview
3. **Core Documentation**: Deep dive into SQL toolkit
4. **ORM Documentation**: Advanced mapping and querying

### Reference Sections

**Core:**
- Engine Configuration: Connection setup and pooling
- Connections & Transactions: Transaction management
- Schema Definition: Tables, columns, constraints
- SQL Expression Language: Building queries
- Type System: Data types and customization
- Dialects: Database-specific features

**ORM:**
- Mapper Configuration: Class mapping options
- Session API: Persistence patterns
- Relationships: Object associations
- Querying Guide: ORM query patterns
- Extensions: Hybrid attributes, association proxy

### Code Examples

Working examples are included in the distribution at `orm/examples/`:

```python
# All examples use doctest format
# Can be run directly in Python interpreter

>>> from sqlalchemy import create_engine
>>> engine = create_engine("sqlite:///:memory:")
>>> # Examples continue...
```

## Key Terminology

**Core Terms:**
- **Engine**: Database connectivity manager
- **Connection**: Single database connection
- **Result**: Query result container
- **MetaData**: Schema definition container
- **Table**: Database table representation
- **Column**: Table column with type and constraints
- **Select**: SQL SELECT statement construct
- **Dialect**: Database-specific implementation

**ORM Terms:**
- **Session**: Unit of Work manager
- **Mapper**: Class-to-table mapping configuration
- **Identity Map**: Session's object cache
- **Unit of Work**: Transaction pattern for persistence
- **Relationship**: Association between mapped classes
- **Eager Loading**: Pre-fetching related objects
- **Lazy Loading**: On-demand loading of relationships

**General Terms:**
- **CRUD**: Create, Read, Update, Delete operations
- **DDL**: Data Definition Language (CREATE, ALTER)
- **DML**: Data Manipulation Language (INSERT, UPDATE, DELETE)
- **DBAPI**: Python Database API Specification (PEP 249)
- **Reflection**: Schema introspection from database

## Usage Patterns

### Core-Only Applications

For simple CRUD or when ORM overhead is unnecessary:

```python
from sqlalchemy import create_engine, select, insert, Table, Column, Integer, String, MetaData

engine = create_engine("postgresql://user:pass@localhost/db")

# Define schema
metadata = MetaData()
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50)),
)

# Insert data
with engine.connect() as conn:
    conn.execute(insert(users).values(username="alice"))
    conn.commit()

# Query data
with engine.connect() as conn:
    result = conn.execute(select(users).where(users.c.username == "alice"))
    row = result.first()
    print(row.username)
```

### ORM Applications

For object-oriented domain models:

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))

engine = create_engine("postgresql://user:pass@localhost/db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, class_=Session)

with SessionLocal() as session:
    user = User(username="alice")
    session.add(user)
    session.commit()
    
    user = session.query(User).first()
    print(user.username)
```

### Async Applications

For asynchronous I/O-bound applications:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession)

async def create_user():
    async with AsyncSessionLocal() as session:
        user = User(username="alice")
        session.add(user)
        await session.commit()
```

## Next Steps

After understanding the architecture:

1. **For Core Users**: Read [Engine Configuration](02-engine-connections.md) and [Schema Definition](03-core-schema-types.md)
2. **For ORM Users**: Read [ORM Mapping](05-orm-mapping.md) and [Session Management](06-orm-session.md)
3. **For Async Users**: Read [AsyncIO Support](07-orm-asyncio.md)
4. **For Migration**: Read [Migration Guide](21-migration-2-0.md)

## Common Pitfalls

### 1. Mixing 1.x and 2.0 Styles

**Avoid:**
```python
# Don't mix old and new styles
session.query(User).filter(...)  # Old style
select(User).where(...)          # New style - use this!
```

### 2. Forgetting to Commit

```python
# Objects won't persist without commit
with SessionLocal() as session:
    user = User(username="alice")
    session.add(user)
    # Missing: session.commit()
```

### 3. Not Using Context Managers

```python
# Bad: Manual connection management
conn = engine.connect()
try:
    # ...
finally:
    conn.close()

# Good: Context manager handles cleanup
with engine.connect() as conn:
    # ...
```

## Resources

- **Official Docs**: https://docs.sqlalchemy.org/en/20/
- **Unified Tutorial**: Start here for comprehensive introduction
- **Changelog**: Review version-specific changes
- **FAQ**: Common questions and answers
- **Examples**: Working code samples in distribution
