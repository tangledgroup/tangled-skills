# Engine and Connection Management

## Engine Creation

### Basic Engine Setup

The Engine is the primary entry point for all SQLAlchemy database operations:

```python
from sqlalchemy import create_engine

# SQLite (in-memory)
engine = create_engine("sqlite:///:memory:")

# SQLite (file-based)
engine = create_engine("sqlite:///path/to/database.db")

# PostgreSQL
engine = create_engine("postgresql://username:password@localhost/dbname")

# MySQL
engine = create_engine("mysql+pymysql://username:password@localhost/dbname")

# Oracle
engine = create_engine("oracle://username:password@hostname:1521/SID")

# Microsoft SQL Server
engine = create_engine("mssql+pyodbc://username:password@hostname/databasename?driver=ODBC+Driver+17+for+SQL+Server")
```

### Connection URL Formats

**General Format:**
```
dialect[+driver]://username:password@host[:port]/database[?query_params]
```

**Examples with Parameters:**
```python
# PostgreSQL with SSL
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    connect_args={"sslmode": "require"}
)

# MySQL with charset
engine = create_engine("mysql://user:pass@localhost/db?charset=utf8mb4")

# SQLite with check_same_thread=False
engine = create_engine(
    "sqlite:///db.db",
    connect_args={"check_same_thread": False}
)
```

### Echo and Logging

Enable SQL logging for debugging:

```python
# Simple echo mode
engine = create_engine("postgresql://...", echo=True)

# Advanced logging with Python logging
import logging
from logging import getLogger

logging.basicConfig()
logger = getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

engine = create_engine("postgresql://...", echo=False)
```

## Connection Pooling

### Pool Configuration

SQLAlchemy uses connection pools by default for stateful databases:

```python
from sqlalchemy import create_engine

# Default pool settings (PostgreSQL, MySQL, etc.)
engine = create_engine("postgresql://user:pass@localhost/db")
# - pool_size: 5 (default)
# - max_overflow: 10 (default)
# - pool_recycle: 0 (no recycle)
# - pool_pre_ping: False

# Custom pool settings
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,          # Number of connections to keep open
    max_overflow=10,       # Additional connections beyond pool_size
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connection before use
)
```

### Pool Size Guidelines

**Small Applications:**
```python
engine = create_engine(
    "postgresql://...",
    pool_size=5,
    max_overflow=10
)
```

**Medium Applications:**
```python
engine = create_engine(
    "postgresql://...",
    pool_size=20,
    max_overflow=20
)
```

**Large Applications:**
```python
engine = create_engine(
    "postgresql://...",
    pool_size=50,
    max_overflow=50,
    pool_recycle=3600
)
```

### Pool Events and Monitoring

```python
from sqlalchemy.event import listen
from sqlalchemy.pool import Pool

def log_connect(dbapi_conn, connection_record):
    print(f"New connection created: {dbapi_conn}")

def log_checkout(dbapi_conn, connection_record, connection_proxy):
    print(f"Connection checked out from pool")

# Listen to pool events
listen(engine.pool, 'connect', log_connect)
listen(engine.pool, 'checkout', log_checkout)

# Pool status
print(f"Pool size: {engine.pool.size()}")
print(f"Checked out: {engine.pool.checkedout()}")
print(f"Overflow: {engine.pool.overflow()}")
```

### Static Pool (Single Connection)

For testing or simple scripts:

```python
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///db.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # No pooling, single connection
)
```

### Null Pool (No Pooling)

For stateless connections or when external pooling is used:

```python
from sqlalchemy.pool import NullPool

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=NullPool,  # Create/close connection per use
)
```

## Connection Management

### Using Connections

**Context Manager (Recommended):**
```python
with engine.connect() as conn:
    result = conn.execute(select(users))
    for row in result:
        print(row.username)
# Connection automatically returned to pool
```

**Manual Management:**
```python
conn = engine.connect()
try:
    result = conn.execute(select(users))
    for row in result:
        print(row.username)
finally:
    conn.close()  # Returns to pool
```

### Executing SQL Statements

**Raw SQL:**
```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    rows = result.fetchall()
```

**Parameterized Queries:**
```python
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE username = :name"),
        {"name": "alice"}
    )
```

**Using Core Constructs:**
```python
from sqlalchemy import select

stmt = select(users).where(users.c.username == "alice")
with engine.connect() as conn:
    result = conn.execute(stmt)
    user = result.scalar_one()
```

## Transactions

### Transaction Basics

SQLAlchemy follows DBAPI transaction model:

```python
with engine.connect() as conn:
    with conn.begin():  # Starts transaction
        conn.execute(insert(users).values(username="alice"))
        conn.execute(insert(users).values(username="bob"))
    # Commit happens automatically on successful exit
```

### Explicit Transaction Control

```python
with engine.connect() as conn:
    trans = conn.begin()  # Start transaction
    try:
        conn.execute(insert(users).values(username="alice"))
        trans.commit()  # Explicit commit
    except:
        trans.rollback()  # Explicit rollback
        raise
```

### Nested Transactions (Savepoints)

```python
with engine.connect() as conn:
    with conn.begin():  # Outer transaction
        conn.execute(insert(users).values(username="alice"))
        
        with conn.begin_nested():  # Savepoint
            conn.execute(insert(posts).values(title="Post 1"))
            # If this fails, only inner part rolls back
    
    # Outer transaction commits both
```

### Transaction Isolation Levels

**PostgreSQL:**
```python
from sqlalchemy.dialects import postgresql

engine = create_engine(
    "postgresql://...",
    isolation_level="READ COMMITTED"  # or REPEATABLE READ, SERIALIZABLE
)
```

**MySQL:**
```python
engine = create_engine(
    "mysql://...",
    isolation_level="READ COMMITTED"
)
```

### Two-Phase Commits

For distributed transactions:

```python
with engine.connect() as conn:
    with conn.begin_twophase():
        conn.execute(insert(users).values(username="alice"))
        # prepare() called automatically
        # commit() completes two-phase commit
```

## Result Objects

### Accessing Query Results

**Scalar Values:**
```python
result = conn.execute(select(func.count(users.id)))
count = result.scalar()  # First value from first row

# Or with validation
count = result.scalar_one()  # Raises if not exactly one result
```

**Row Objects:**
```python
result = conn.execute(select(users))

# Iterate rows
for row in result:
    print(row.id, row.username)

# Access by index
row = result.first()
print(row[0], row[1])  # id, username

# Access by name
print(row.id, row.username)

# Access by dict
print(row["id"], row["username"])
```

**Fetch Methods:**
```python
result = conn.execute(select(users))

row = result.first()        # First row or None
row = result.one()          # Exactly one row (raises if 0 or >1)
row = result.scalar()       # First column of first row
rows = result.all()         # All rows as list
rows = result.fetchmany(10) # Next 10 rows
```

### Result Proxies

**Mapped Results:**
```python
from sqlalchemy.orm import from_returning

result = conn.execute(
    insert(users).returning(users.c.id, users.c.username)
)
for id_, username in result:
    print(id_, username)
```

**Dict Results:**
```python
from sqlalchemy import RowMapping

result = conn.execute(select(users)).mappings()
for row in result:
    print(row["username"])
    
# Or with one()
user = conn.execute(select(users).where(...)).mappings().one()
print(user["username"])
```

## Async Engine

### Creating Async Engine

```python
from sqlalchemy.ext.asyncio import create_async_engine

# PostgreSQL with asyncpg
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,
    pool_size=20,
    max_overflow=10
)

# MySQL with aiomysql
async_engine = create_async_engine(
    "mysql+aiomysql://user:pass@localhost/db"
)
```

### Async Connection Management

```python
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

async def fetch_users():
    async with async_engine.connect() as conn:
        result = await conn.execute(select(users))
        for row in result:
            print(row.username)

# Run async function
asyncio.run(fetch_users())
```

### Async Transactions

```python
async def create_user(username):
    async with async_engine.connect() as conn:
        async with conn.begin():  # Async transaction
            await conn.execute(
                insert(users).values(username=username)
            )
            # Auto-commits on successful exit
```

## Engine Disposal

### Proper Cleanup

```python
# Engine goes out of scope
engine = create_engine("postgresql://...")
# ... use engine ...
engine.dispose()  # Close all pooled connections

# Or use context manager pattern in applications
from contextlib import contextmanager

@contextmanager
def get_engine():
    engine = create_engine("postgresql://...")
    try:
        yield engine
    finally:
        engine.dispose()
```

### Pool Disposal

```python
# Dispose pool without destroying engine
engine.pool.dispose()

# Clear specific connections
engine.pool.clear()
```

## Common Patterns

### Connection Testing

```python
def test_connection(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connection successful")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
```

### Health Check with Pre-Ping

```python
engine = create_engine(
    "postgresql://...",
    pool_pre_ping=True  # Test connection before using
)
```

### Connection Pool Warm-up

```python
def warm_up_pool(engine, num_connections=5):
    """Pre-populate connection pool"""
    connections = []
    for _ in range(num_connections):
        conn = engine.connect()
        connections.append(conn)
    
    for conn in connections:
        conn.close()  # Returns to pool, now warmed up
```

## Troubleshooting

### Pool Exhaustion

**Symptom:** `QueuePool limit of size X overflow Y reached`

**Solution:**
```python
engine = create_engine(
    "postgresql://...",
    pool_size=20,          # Increase pool size
    max_overflow=30,       # Allow more overflow
    pool_timeout=30,       # Wait up to 30 seconds
    pool_recycle=3600,     # Recycle stale connections
)
```

### Stale Connections

**Symptom:** `connection lost` or `server closed the connection`

**Solution:**
```python
engine = create_engine(
    "postgresql://...",
    pool_pre_ping=True,    # Test before use
    pool_recycle=3600,     # Recycle after 1 hour
)
```

### Connection Leaks

**Detection:**
```python
# Check pool status
print(f"Checked out: {engine.pool.checkedout()}")
print(f"Overflow: {engine.pool.overflow()}")

# If high, connections not being returned
```

**Solution:** Always use context managers:
```python
# Good
with engine.connect() as conn:
    # ...

# Bad - connection may not be returned
conn = engine.connect()
# ... missing conn.close()
```

## Best Practices

1. **Use context managers** for all connections
2. **Enable pool_pre_ping** in production to catch stale connections
3. **Set pool_recycle** based on your database's timeout settings
4. **Monitor pool metrics** in production applications
5. **Use appropriate pool size** for your workload
6. **Dispose engines** when shutting down applications
7. **Use async engine** for I/O-bound applications

## Next Steps

- [Schema Definition](03-core-schema-types.md) - Define tables and columns
- [Core Querying](04-core-querying.md) - Execute SQL statements
- [ORM Session](06-orm-session.md) - ORM transaction management
- [Dialects](16-dialects-overview.md) - Database-specific features
