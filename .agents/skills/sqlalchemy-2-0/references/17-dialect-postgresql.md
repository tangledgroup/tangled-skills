# PostgreSQL Dialect

## Overview

PostgreSQL is one of the most feature-rich databases supported by SQLAlchemy, offering advanced data types, indexing options, and query capabilities.

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:password@localhost:5432/dbname",
    echo=True,
    pool_pre_ping=True
)
```

## Installation

```bash
# Synchronous driver (recommended)
pip install psycopg2-binary  # Binary package (easiest)
# or
pip install psycopg2         # Requires PostgreSQL development headers

# Async driver
pip install asyncpg

# Additional extensions
pip install sqlalchemy-psycopg2  # Extra features
```

## Connection Strings

### Standard Format

```python
# Basic connection
engine = create_engine("postgresql://user:pass@localhost/dbname")

# With port
engine = create_engine("postgresql://user:pass@localhost:5432/dbname")

# With query parameters
engine = create_engine(
    "postgresql://user:pass@localhost/dbname?sslmode=require"
)
```

### Connection Parameters

```python
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    connect_args={
        "sslmode": "require",           # SSL mode (disable, allow, require, verify-ca, verify-full)
        "sslcert": "/path/to/cert.pem", # Client certificate
        "sslkey": "/path/to/key.pem",   # Client private key
        "sslrootcert": "/path/to/ca.pem", # CA certificate
        "connect_timeout": 10,          # Connection timeout in seconds
        "application_name": "myapp"     # Application name for pg_stat_activity
    }
)
```

### Unix Socket Connections

```python
# Connect via Unix socket
engine = create_engine(
    "postgresql://user:pass@/var/run/postgresql/dbname"
)

# Or with host parameter
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    connect_args={"host": "/var/run/postgresql"}
)
```

## Advanced Data Types

### JSON and JSONB

```python
from sqlalchemy.dialects.postgresql import JSON, JSONB

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    # JSON - text storage, slower
    metadata_json = Column(JSON)
    # JSONB - binary storage, faster, indexable
    metadata_jsonb = Column(JSONB)

# Query JSONB by key
docs = session.execute(
    select(Document).where(
        Document.metadata_jsonb["author"].as_string() == "John"
    )
).scalars().all()

# Query nested keys
docs = session.execute(
    select(Document).where(
        Document.metadata_jsonb["profile"]["age"].as_integer() > 18
    )
).scalars().all()

# JSONB containment
docs = session.execute(
    select(Document).where(
        Document.metadata_jsonb.contains({"status": "active"})
    )
).scalars().all()

# Update JSONB field
stmt = (
    update(Document)
    .where(Document.id == 1)
    .values(metadata_jsonb=jsonb_set(metadata_jsonb, ["author"], "Jane"))
)
```

### HSTORE (Key-Value Store)

```python
from sqlalchemy.dialects.postgresql import HSTORE

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    # HSTORE - native key-value type
    config = Column(HSTORE)

# Query HSTORE
settings = session.execute(
    select(Settings).where(
        Settings.config["theme"] == "dark"
    )
).scalars().all()

# Update HSTORE field
stmt = (
    update(Settings)
    .where(Settings.id == 1)
    .values(config=hstore_append(config, "lang", "en"))
)
```

### Arrays

```python
from sqlalchemy.dialects.postgresql import ARRAY

class TaggedPost(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    # Array of strings
    tags = Column(ARRAY(String))
    # Array of integers
    scores = Column(ARRAY(Integer))
    # Multi-dimensional array
    matrix = Column(ARRAY(ARRAY(Integer)))

# Query with containment
posts = session.execute(
    select(TaggedPost).where(TaggedPost.tags.contains(["python"]))
).scalars().all()

# Query with overlap (any common elements)
posts = session.execute(
    select(TaggedPost).where(TaggedPost.tags.overlap(["python", "sql"]))
).scalars().all()

# Array indexing (1-based in PostgreSQL)
first_tag = TaggedPost.tags[0]  # Compiles to tags[1]

# Array slicing
first_three_tags = func.slice(TaggedPost.tags, 1, 3)
```

### UUID

```python
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Document(Base):
    __tablename__ = "documents"
    
    # UUID with Python UUID object
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # UUID as string
    ref_id = Column(UUID(as_uuid=False))

# Usage - automatic UUID generation
doc = Document()
session.add(doc)
session.flush()
print(doc.id)  # <UUID '...'>

# Query by UUID
doc = session.execute(
    select(Document).where(Document.id == uuid.uuid4())
).scalar_one_or_none()
```

### Full-Text Search

```python
from sqlalchemy.dialects.postgresql import TSVECTOR, TSQUERY, regexp_match

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    # Full-text search vector
    search_vector = Column(TSVECTOR)

# Generate search vector from columns
from sqlalchemy import event

@event.listens_for(Article, "before_insert")
def set_search_vector(mapper, connection, target):
    target.search_vector = func.to_tsvector(
        'english', 
        func.concat(target.title, ' ', target.content)
    )

# Full-text search query
articles = session.execute(
    select(Article).where(
        Article.search_vector.match("sqlalchemy & python")
    ).order_by(
        func.ts_rank(Article.search_vector, "sqlalchemy & python").desc()
    )
).scalars().all()

# Phrase search
articles = session.execute(
    select(Article).where(
        Article.search_vector.match('"sqlalchemy"')  # Exact phrase
    )
).scalars().all()

# Prefix search
articles = session.execute(
    select(Article).where(
        Article.search_vector.match("python:*")  # Words starting with "python"
    )
).scalars().all()
```

### Range Types

```python
from sqlalchemy.dialects.postgresql import INT4RANGE, NUMRANGE, DATERANGE, TSRANGE

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    # Integer range
    attendee_count_range = Column(INT4RANGE)
    # Numeric range (prices)
    price_range = Column(NUMRANGE)
    # Date range
    date_range = Column(DATERANGE)

# Query with range operators
events = session.execute(
    select(Event).where(
        Event.date_range.contains(func.current_date())
    )
).scalars().all()

# Range containment
events = session.execute(
    select(Event).where(
        Event.date_range.contained_by(daterange("2024-01-01", "2024-12-31"))
    )
).scalars().all()

# Range overlap
events = session.execute(
    select(Event).where(
        Event.date_range.overlaps(daterange("2024-06-01", "2024-06-30"))
    )
).scalars().all()
```

### ENUM Types

```python
from sqlalchemy.dialects.postgresql import ENUM

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    # PostgreSQL native ENUM type
    status = Column(ENUM(
        "pending", "processing", "shipped", "delivered",
        name="order_status"  # Enum type name in database
    ))

# Create ENUM type first (do this once during migration)
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered')"))
    conn.commit()
```

## Indexing Features

### GIN Indexes (JSONB, Arrays)

```python
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import GIN

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    metadata = Column(JSONB)
    tags = Column(ARRAY(String))
    
    # GIN index for JSONB (fast containment queries)
    __table_args__ = (
        Index("idx_documents_metadata", "metadata", postgresql_using="gin"),
        # GIN index for arrays
        Index("idx_documents_tags", "tags", postgresql_using="gin"),
    )
```

### GiST Indexes (Full-Text, Geometric)

```python
from sqlalchemy.dialects.postgresql import GIST

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    search_vector = Column(TSVECTOR)
    
    # GiST index for full-text search
    __table_args__ = (
        Index("idx_articles_search", "search_vector", postgresql_using="gist"),
    )
```

### Partial Indexes

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    is_active = Column(Boolean)
    
    # Index only active users (smaller, faster)
    __table_args__ = (
        Index(
            "idx_users_active_email",
            "email",
            postgresql_where=is_active == True
        ),
    )
```

### Expression Indexes

```python
from sqlalchemy import Index, func

class User(Base):
    __tablename__ = "users"
    
    username = Column(String)
    email = Column(String)
    
    # Index on lower() for case-insensitive searches
    __table_args__ = (
        Index("idx_users_lower_username", func.lower("username")),
        Index("idx_users_lower_email", func.lower("email")),
    )

# Query uses expression index automatically
users = session.execute(
    select(User).where(func.lower(User.username) == "alice")
).scalars().all()
```

## PostgreSQL-Specific Operations

### UPSERT (ON CONFLICT)

```python
from sqlalchemy.dialects.postgresql import insert

# Basic upsert
stmt = (
    insert(Users)
    .values(username="alice", email="alice@example.com")
    .on_conflict_do_update(
        index_elements=[Users.c.username],  # Conflict target
        set_=dict(  # Values to update
            email="alice@example.com",
            updated_at=func.now()
        )
    )
)

# Upsert with WHERE clause
stmt = (
    insert(Users)
    .values(username="alice", login_count=1)
    .on_conflict_do_update(
        index_elements=[Users.c.username],
        set_=dict(login_count=Users.c.login_count + 1),
        where=Users.c.is_active == True  # Only update if active
    )
)

# Upsert, do nothing
stmt = (
    insert(Users)
    .values(username="alice", email="alice@example.com")
    .on_conflict_do_nothing(index_elements=[Users.c.username])
)
```

### RETURNING Clause

```python
from sqlalchemy import insert, update, delete

# Insert with returning
result = session.execute(
    insert(Users)
    .values(username="alice", email="alice@example.com")
    .returning(Users.c.id, Users.c.username)
)
new_id, username = result.fetchone()

# Update with returning
result = session.execute(
    update(Users)
    .where(Users.id == 1)
    .values(email="new@example.com")
    .returning(Users.c.id, Users.c.email)
)

# Delete with returning
result = session.execute(
    delete(Users)
    .where(Users.id == 1)
    .returning(Users.c.username)
)
```

### CTEs (Common Table Expressions)

```python
from sqlalchemy import cte, union_all

# Recursive CTE for hierarchical data
# Base case: root categories
root_categories = (
    select(Categories.id, Categories.name, Categories.parent_id, literal(0).label("depth"))
    .where(Categories.parent_id.is_(None))
)

# Recursive case
child_categories = (
    select(
        Categories.id,
        Categories.name,
        Categories.parent_id,
        cte("category_tree").c.depth + 1
    )
    .where(Categories.parent_id == cte("category_tree").c.id)
)

# Combine into recursive CTE
category_tree = root_categories.union_all(child_categories).cte(
    "category_tree",
    recursive=True
)

stmt = select(category_tree).order_by(category_tree.c.depth)
```

### Materialized Views

```python
from sqlalchemy import text, MaterializedView

# Create materialized view
with engine.connect() as conn:
    conn.execute(text("""
        CREATE MATERIALIZED VIEW active_user_stats AS
        SELECT 
            u.id,
            u.username,
            COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON p.user_id = u.id
        WHERE u.is_active = true
        GROUP BY u.id, u.username
    """))
    conn.commit()

# Query materialized view
stats = session.execute(
    text("SELECT * FROM active_user_stats")
).all()

# Refresh materialized view
with engine.connect() as conn:
    conn.execute(text("REFRESH MATERIALIZED VIEW active_user_stats"))
```

## Best Practices

### 1. Use JSONB Over JSON

```python
# Good - JSONB is faster and indexable
metadata = Column(JSONB)

# Avoid - JSON is slower, not indexable
metadata = Column(JSON)
```

### 2. Index Frequently Queried JSONB Keys

```python
# Create GIN index for specific keys
__table_args__ = (
    Index(
        "idx_metadata_author",
        func.jsonb_path_probe(metadata, '$.author'),
        postgresql_using="gin"
    ),
)
```

### 3. Use COPY for Bulk Inserts

```python
import csv
from io import StringIO

# Fast bulk insert using PostgreSQL COPY
with engine.connect() as conn:
    with conn.begin():
        data = StringIO()
        writer = csv.writer(data)
        writer.writerow(["username", "email"])  # Header
        writer.writerow(["alice", "alice@example.com"])
        writer.writerow(["bob", "bob@example.com"])
        
        conn.execute(
            text("COPY users (username, email) FROM STDIN WITH CSV HEADER"),
            parameters=(data.getvalue(),)
        )
```

### 4. Leverage Advisory Locks for Concurrency Control

```python
from sqlalchemy import text

with engine.connect() as conn:
    with conn.begin():
        # Acquire advisory lock
        conn.execute(text("SELECT pg_advisory_xact_lock(12345)"))
        
        try:
            # Critical section
            process_critical_operation()
        finally:
            pass  # Lock released at transaction end
```

## Troubleshooting

### Connection Issues

```python
# Enable detailed logging
engine = create_engine(
    "postgresql://...",
    echo=True,
    pool_pre_ping=True  # Test connections before use
)

# Check connection parameters
import psycopg2
try:
    conn = psycopg2.connect("postgresql://user:pass@localhost/db")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Unicode Issues

```python
# Ensure UTF-8 encoding
engine = create_engine(
    "postgresql://...",
    connect_args={"client_encoding": "UTF8"}
)

# Or set at database level
with engine.connect() as conn:
    conn.execute(text("SET client_encoding = 'UTF8'"))
```

## Next Steps

- [Dialects Overview](16-dialects-overview.md) - Cross-dialect patterns
- [MySQL Dialect](18-dialect-mysql.md) - MySQL comparison
- [Custom Types](15-core-custom-types.md) - PostgreSQL-specific types
- [Best Practices](24-best-practices.md) - PostgreSQL optimization
