# Dialects Overview

## What is a Dialect?

A dialect is SQLAlchemy's abstraction layer that translates generic SQL operations into database-specific syntax and behavior. Each supported database has its own dialect implementation.

```python
from sqlalchemy import create_engine

# Different dialects for different databases
postgresql = create_engine("postgresql://user:pass@localhost/db")
mysql = create_engine("mysql+pymysql://user:pass@localhost/db")
sqlite = create_engine("sqlite:///database.db")
oracle = create_engine("oracle://user:pass@host:1521/SID")
mssql = create_engine("mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server")
```

## Dialect Architecture

### Dialect Components

```
┌─────────────────────────────────────┐
│       SQLAlchemy Core/ORM           │
│         (Generic SQL)               │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           Dialect Layer             │
│  - Type Compiler                    │
│  - SQL Compiler                     │
│  - DBAPI Wrapper                    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         DBAPI Driver                │
│  (psycopg2, pymysql, etc.)          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│        Database Server              │
│  (PostgreSQL, MySQL, etc.)          │
└─────────────────────────────────────┘
```

### Dialect Selection

```python
# Explicit dialect selection
engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/db"  # psycopg2 driver
)

engine = create_engine(
    "mysql+aiomysql://user:pass@localhost/db"  # aiomysql for async
)

# Default driver (auto-selected)
engine = create_engine("postgresql://user:pass@localhost/db")  # Uses psycopg2 by default
```

## Dialect-Specific Features

### PostgreSQL-Specific

```python
from sqlalchemy.dialects.postgresql import (
    JSONB, ARRAY, HSTORE, UUID,
    TSVECTOR, TSQUERY, CITEXT,
    INSERT as PG_INSERT
)

# JSONB column
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(JSONB)  # Binary JSON with indexing
    metadata = Column(HSTORE)  # Key-value store
    search_vector = Column(TSVECTOR)  # Full-text search
    title = Column(CITEXT)  # Case-insensitive text

# UPSERT (ON CONFLICT)
stmt = (
    PG_INSERT(Users)
    .values(id=1, username="alice")
    .on_conflict_do_update(
        index_elements=[Users.c.username],
        set_=dict(updated_at=func.now())
    )
)

# Array operations
class TaggedPost(Base):
    __tablename__ = "posts"
    
    tags = Column(ARRAY(String))

# Query with array containment
posts = session.execute(
    select(TaggedPost).where(TaggedPost.tags.contains(["python"]))
).scalars().all()

# JSONB queries
docs = session.execute(
    select(Document).where(Document.content["author"].as_string() == "John")
).scalars().all()

# Full-text search
docs = session.execute(
    select(Document).where(
        Document.search_vector.match("sqlalchemy & python")
    )
).scalars().all()
```

### MySQL-Specific

```python
from sqlalchemy.dialects.mysql import (
    ENUM, SET, YEAR, DATE, DATETIME, TIMESTAMP,
    TEXT, MEDIUMTEXT, LONGTEXT,
    NCHAR, NVARCHAR, NATIONAL,
    INSERT as MYSQL_INSERT
)

# ENUM column
class Order(Base):
    __tablename__ = "orders"
    
    status = Column(ENUM(
        "pending", "processing", "shipped", "delivered",
        name="order_status"
    ))

# SET column (multiple values)
class Permissions(Base):
    __tablename__ = "permissions"
    
    flags = Column(SET("read", "write", "execute", "delete"))

# TEXT variants
class Article(Base):
    __tablename__ = "articles"
    
    short_text = Column(TEXT)       # Up to 64KB
    medium_text = Column(MEDIUMTEXT)  # Up to 16MB
    long_text = Column(LONGTEXT)   # Up to 4GB

# UPSERT (ON DUPLICATE KEY UPDATE)
stmt = (
    MYSQL_INSERT(Users)
    .values(id=1, username="alice")
    .on_duplicate_key_update(
        updated_at=func.now()
    )
)

# Generated columns
class Product(Base):
    __tablename__ = "products"
    
    price = Column(DECIMAL(10, 2))
    tax_rate = Column(DECIMAL(3, 2))
    total_price = Column(
        DECIMAL(10, 2),
        generated_expression=price * (1 + tax_rate)
    )

# Full-text search
class Post(Base):
    __tablename__ = "posts"
    
    content = Column(TEXT, mysql_fulltext=True)

posts = session.execute(
    select(Post).where(
        Post.content.match("sqlalchemy", boolean_mode=True)
    )
).scalars().all()
```

### SQLite-Specific

```python
from sqlalchemy.dialects.sqlite import (
    JSON, REGEXP, WITHOUTROWID,
    INSERT as SQLITE_INSERT
)

# JSON column (SQLite 3.9+)
class Settings(Base):
    __tablename__ = "settings"
    
    preferences = Column(JSON)

# Query JSON
settings = session.execute(
    select(Settings).where(
        Settings.preferences["theme"].as_string() == "dark"
    )
).scalars().all()

# WITHOUT ROWID tables (faster for certain workloads)
class Config(Base):
    __tablename__ = "config"
    
    key = Column(String, primary_key=True)
    value = Column(String)
    
    __table_args__ = {"sqlite_without_rowid": True}

# UPSERT (INSERT OR REPLACE)
stmt = (
    SQLITE_INSERT(Config)
    .values(key="theme", value="dark")
    .on_conflict_do_update(
        set_=dict(value="dark")
    )
)

# Regular expression (requires extension)
from sqlalchemy import text

users = session.execute(
    select(User).where(text("username REGEXP :pattern")),
    {"pattern": "^a.*"}
).scalars().all()

# Temporary tables
temp_table = Table(
    "temp_data", metadata,
    Column("id", Integer, primary_key=True),
    Column("value", String),
    sqlite_persistent=False  # Session-scoped temp table
)
```

### Oracle-Specific

```python
from sqlalchemy.dialects.oracle import (
    BLOB, CLOB, NCLOB, RAW,
    DATE, TIMESTAMP, INTERVAL,
    VARCHAR, NVARCHAR2,
    INSERT as ORACLE_INSERT
)

# Large objects
class Document(Base):
    __tablename__ = "documents"
    
    binary_data = Column(BLOB)  # Binary large object
    text_data = Column(CLOB)    # Character large object
    unicode_data = Column(NCLOB)  # National character large object

# INTERVAL types
class Event(Base):
    __tablename__ = "events"
    
    start_time = Column(TIMESTAMP)
    duration = Column(INTERVAL(day_precision=2, second_precision=2))

# Sequence (Oracle uses sequences instead of autoincrement)
from sqlalchemy import Sequence

class User(Base):
    __tablename__ = "users"
    
    id = Column(
        Integer,
        Sequence("user_seq"),
        primary_key=True
    )

# MERGE statement (UPSERT)
stmt = (
    ORACLE_INSERT(Users)
    .values(id=1, username="alice")
    .on_conflict_do_update(
        index_elements=[Users.c.id],
        set_=dict(username="alice")
    )
)

# Hierarchical queries (CONNECT BY)
from sqlalchemy import text

employees = session.execute(
    text("""
        SELECT id, name, manager_id, LEVEL
        FROM employees
        START WITH manager_id IS NULL
        CONNECT BY PRIOR id = manager_id
    """)
).all()
```

### MSSQL-Specific

```python
from sqlalchemy.dialects.mssql import (
    DATETIME2, DATETIMEOFFSET, UNIQUEIDENTIFIER,
    NVARCHAR, NTEXT, XML, GEOMETRY, GEOGRAPHY,
    INSERT as MSSQL_INSERT
)

# Unique identifier (UUID)
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)

# Datetime with higher precision
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    timestamp = Column(DATETIME2)  # Higher precision than DATETIME
    timezone_aware = Column(DATETIMEOFFSET)  # With timezone

# XML column
class Config(Base):
    __tablename__ = "configs"
    
    xml_data = Column(XML)

# Spatial types
class Location(Base):
    __tablename__ = "locations"
    
    geometry = Column(GEOMETRY)  # Planar coordinates
    geography = Column(GEOGRAPHY)  # Ellipsoidal (lat/lon)

# TOP clause (instead of LIMIT)
from sqlalchemy import top

stmt = (
    select(User)
    .order_by(User.created_at.desc())
    .limit(10)  # Compiles to TOP 10 for MSSQL
)

# OUTPUT clause (RETURNING equivalent)
stmt = (
    MSSQL_INSERT(Users)
    .values(username="alice")
    .returning(Users.c.id, Users.c.username)
)

# Table-valued parameters (requires TVP type registration)
# Advanced feature for bulk operations
```

## Dialect Configuration

### Connection Parameters

```python
# PostgreSQL with SSL
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    connect_args={
        "sslmode": "require",
        "sslcert": "/path/to/cert.pem",
        "sslkey": "/path/to/key.pem"
    }
)

# MySQL with charset and timeout
engine = create_engine(
    "mysql+pymysql://user:pass@localhost/db",
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30
    }
)

# Oracle with service name
engine = create_engine(
    "oracle://user:pass@host:1521/SERVICE_NAME",
    connect_args={
        "encoding": "UTF-8",
        "nencoding": "UTF-8"
    }
)

# MSSQL with authentication
engine = create_engine(
    "mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server",
    connect_args={
        "trusted_connection": "yes",  # Windows auth
        "encrypt": "yes",
        "trust_server_certificate": "yes"
    }
)
```

### Dialect-Specific Options

```python
# PostgreSQL
engine = create_engine(
    "postgresql://...",
    # Enable row-level security
    execution_options={"isolation_level": "SERIALIZABLE"},
    # Use server-side cursors for large result sets
    server_side_cursors=True
)

# MySQL
engine = create_engine(
    "mysql://...",
    # Use named pipes or sockets
    connect_args={"unix_socket": "/var/run/mysqld/mysqld.sock"},
    # Enable autocommit mode
    autocommit=True
)

# SQLite
engine = create_engine(
    "sqlite:///db.db",
    # Allow multiple threads to access database
    connect_args={"check_same_thread": False},
    # Use WAL mode for better concurrency
    echo=False
)

# Set SQLite pragma after connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
```

## Dialect Detection and Selection

### Runtime Dialect Information

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost/db")

# Get dialect information
dialect = engine.dialect
print(dialect.name)  # "postgresql"
print(dialect.driver)  # "psycopg2"
print(dialect.server_version_info)  # (14, 2, 0)

# Check for specific features
if dialect.supports_sane_rowcount:
    print("Row count is reliable")

if dialect.supports_sane_multi_rowcount:
    print("Multi-row operations supported")

if dialect.supports_native_decimal:
    print("Native DECIMAL type supported")
```

### Conditional Dialect Usage

```python
from sqlalchemy import create_engine, text

engine = create_engine(database_url)

# Use dialect-specific SQL when needed
if engine.dialect.name == "postgresql":
    stmt = text("SELECT NOW()")
elif engine.dialect.name == "mysql":
    stmt = text("SELECT NOW()")
elif engine.dialect.name == "sqlite":
    stmt = text("SELECT datetime('now')")
else:
    stmt = text("SELECT CURRENT_TIMESTAMP")

result = session.execute(stmt)
```

## Best Practices

### 1. Use Generic Types When Possible

```python
# Good - works across all dialects
from sqlalchemy import String, Text, Integer, DateTime

class User(Base):
    username = Column(String(50))
    bio = Column(Text)

# Avoid - dialect-specific unless necessary
from sqlalchemy.dialects.postgresql import JSONB  # PostgreSQL only!
```

### 2. Use Type Variants for Cross-Dialect Support

```python
from sqlalchemy import String, Text

class Article(Base):
    # Use VARCHAR with length for MySQL, TEXT for others
    content = Column(
        Text().with_variant(String(65535), "mysql")
    )
```

### 3. Test on Target Dialect

```python
# Always test your application on the actual production dialect
# Some features may behave differently:
# - String length limits
# - Integer size limits  
# - Boolean representation
# - NULL handling in GROUP BY
# - Default value behavior
```

### 4. Handle Dialect-Specific Errors

```python
from sqlalchemy.exc import DatabaseError

try:
    session.commit()
except DatabaseError as e:
    if engine.dialect.name == "postgresql":
        # Handle PostgreSQL-specific error codes
        if e.orig.pgcode == "23505":  # Unique violation
            handle_unique_violation(e)
    elif engine.dialect.name == "mysql":
        # Handle MySQL-specific error codes
        if e.orig.args[0] == 1062:  # Duplicate entry
            handle_duplicate_entry(e)
```

## Next Steps

- [PostgreSQL Dialect](17-dialect-postgresql.md) - Detailed PostgreSQL features
- [MySQL Dialect](18-dialect-mysql.md) - MySQL/MariaDB specifics
- [SQLite Dialect](19-dialect-sqlite.md) - SQLite configuration
- [Oracle and MSSQL](20-dialect-oracle-mssql.md) - Enterprise databases
