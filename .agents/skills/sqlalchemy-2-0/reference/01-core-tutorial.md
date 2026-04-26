# Core Tutorial

## Engine and Connectivity

The `Engine` is the starting point of any SQLAlchemy application. It acts as a central source of connections to a particular database, providing both a factory and a connection pool.

### Creating an Engine

```python
from sqlalchemy import create_engine

# SQLite in-memory
engine = create_engine("sqlite:///:memory:", echo=True)

# PostgreSQL with psycopg driver
engine = create_engine("postgresql+psycopg://user:pass@localhost/dbname")

# MySQL with mysqlclient driver
engine = create_engine("mysql+mysqldb://user:pass@localhost/dbname")

# SQLite file-based
engine = create_engine("sqlite:///path/to/database.db")

# Oracle with cx_Oracle
engine = create_engine("oracle+cx_oracle://user:pass@dsn")

# MS SQL Server with pyodbc
engine = create_engine("mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server")
```

The connection URL format is `dialect+driver://username:password@host:port/database`. The dialect indicates the database type. The driver specifies the DBAPI module. If omitted, SQLAlchemy uses a default driver for the selected database.

### Engine Parameters

- `echo=True` — logs all SQL to stdout via Python logging (useful for debugging)
- `pool_size` — number of connections to keep in the pool
- `pool_recycle` — recycle connections after N seconds
- `pool_pre_ping` — test connections before use
- `isolation_level` — set default transaction isolation level

The Engine uses lazy initialization — it does not connect until first use.

### Connection and Context Managers

```python
from sqlalchemy import text

with engine.connect() as conn:
    # Automatically begins a transaction, commits on success, rolls back on exception
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())
    # Connection returned to pool on exit
```

The `Connection` object represents an active database transaction. When used as a context manager, it automatically handles commit/rollback and returns the connection to the pool.

### Result Objects

```python
result = conn.execute(text("SELECT id, name FROM users"))

# Iterate rows
for row in result:
    print(row.id, row.name)

# Fetch all
all_rows = result.all()

# Fetch first
first_row = result.first()

# Single scalar value
scalar_val = result.scalar()

# Exactly one scalar (raises if 0 or >1)
one_val = result.scalar_one()

# One or None (returns None if no rows)
maybe_val = result.scalar_one_or_none()

# Dict-like access via mappings()
for row in result.mappings():
    print(row["id"], row["name"])
```

### Text vs Expression Language

SQLAlchemy supports two modes of SQL construction:

**Raw SQL with `text()`**: For literal SQL strings. Parameters use `:name` syntax.

```python
from sqlalchemy import text

result = conn.execute(
    text("SELECT * FROM users WHERE name = :name AND age > :age"),
    {"name": "spongebob", "age": 25}
)
```

**SQL Expression Language**: Programmatic construction using Python objects. This is the preferred approach for type safety and portability.

```python
from sqlalchemy import select, Table, Column, Integer, String, MetaData

metadata = MetaData()
users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("email", String(120)),
)

stmt = select(users).where(users.c.name == "spongebob")
result = conn.execute(stmt)
```

## Database Metadata

### MetaData Collection

`MetaData` is a central registry for `Table` objects. It tracks all tables and their relationships, enabling proper DDL emission order based on foreign key dependencies.

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

metadata = MetaData()

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

addresses = Table("addresses", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("email", String(120), nullable=False),
)
```

### Creating and Dropping Tables

```python
# Create all tables (respects FK order)
metadata.create_all(engine)

# Drop all tables (reverse order)
metadata.drop_all(engine)

# Check if table exists
from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.has_table("users"))

# Reflect existing tables from database
metadata = MetaData()
metadata.reflect(bind=engine)
```

For production schema management, use [Alembic](https://alembic.sqlalchemy.org) which builds on SQLAlchemy for incremental migrations.

### Column Types

SQLAlchemy provides a comprehensive type system:

**Core types**: `Integer`, `String(length)`, `Text`, `Boolean`, `Float`, `Numeric(precision, scale)`, `Date`, `Time`, `DateTime`, `Interval`, `LargeBinary`, `JSON`, `UUID`

**Specialized types**: `Enum`, `PickleType`, `Indexable`, `Array` (PostgreSQL), `INET` (PostgreSQL), `MACADDR` (PostgreSQL), `ARRAY` (PostgreSQL)

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, func

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("bio", Text),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("metadata_json", JSON),
)
```

### Constraints

```python
from sqlalchemy import UniqueConstraint, CheckConstraint, PrimaryKeyConstraint

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(120), unique=True),
    Column("age", Integer, CheckConstraint("age >= 0")),
)

# Composite unique constraint
users.append_constraint(UniqueConstraint("name", "email"))
```

### Indexes

```python
from sqlalchemy import Index

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("email", String(120)),
    Index("ix_users_name", "name"),
    Index("ix_users_email_unique", "email", unique=True),
)
```

## Transactions

### Core Transaction Flow

```python
with engine.connect() as conn:
    # Transaction begins implicitly on first SQL
    conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "spongebob"})
    conn.commit()  # Explicit commit
    # On exception, context manager rolls back automatically
```

### Nested Transactions (Savepoints)

```python
with engine.begin() as conn:  # auto-commits on success
    conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "spongebob"})

    with conn.begin_nested():  # savepoint
        conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "sandy"})
        # If exception here, only sandy insert is rolled back
```

### Multiple Parameters (executemany)

```python
from sqlalchemy import insert

stmt = insert(users)
conn.execute(stmt, [
    {"name": "spongebob", "email": "spongebob@example.com"},
    {"name": "sandy", "email": "sandy@example.com"},
    {"name": "patrick", "email": "patrick@example.com"},
])
```

### Insert Returning Primary Key

```python
result = conn.execute(insert(users).values(name="squidward"), execution_options={"autocommit": True})
new_id = result.inserted_primary_key[0]
```

## Connection Pooling

SQLAlchemy includes a built-in connection pool with several strategies:

- `QueuePool` — default, fixed-size pool with wait queue
- `StaticPool` — single connection, no overflow (used for testing)
- `NullPool` — no pooling, creates/closes connections each time
- `SingletonThreadPool` — one connection per thread

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine("postgresql://...", pool_size=5, max_overflow=10)
# pool_size: number of persistent connections
# max_overflow: additional connections allowed beyond pool_size
```

To dispose all pooled connections:

```python
engine.dispose()
```
