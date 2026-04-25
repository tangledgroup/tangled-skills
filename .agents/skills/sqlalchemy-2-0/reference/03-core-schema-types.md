# Core Schema Definition and Types

## Table Definition

### Basic Table Structure

Tables are defined using the `Table` construct with columns and constraints:

```python
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

# Create metadata container
metadata = MetaData()

# Define a table
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True, nullable=False),
    Column("email", String(120), unique=True, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

# Define related table
posts = Table(
    "posts", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("content", Text),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
)
```

### Metadata Management

**Shared Metadata:**
```python
metadata = MetaData()

users = Table("users", metadata, ...)
posts = Table("posts", metadata, ...)
comments = Table("comments", metadata, ...)

# All tables share the same metadata object
print(metadata.tables.keys())  # ['users', 'posts', 'comments']
```

**Automatic Naming:**
```python
# Use naming conventions
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)
```

**Reflecting Existing Tables:**
```python
metadata = MetaData()

# Reflect all tables in database
metadata.reflect(bind=engine)

# Reflect specific tables
metadata.reflect(bind=engine, only=["users", "posts"])

# Reflect with schema
metadata.reflect(bind=engine, schema="public")
```

### Column Definition

**Basic Columns:**
```python
Column("id", Integer, primary_key=True)
Column("name", String(50), nullable=False)
Column("description", Text)
Column("price", Numeric(10, 2))
Column("active", Boolean, default=True)
Column("created", DateTime, server_default=func.now())
```

**Auto-Increment:**
```python
# Integer primary keys auto-increment by default
Column("id", Integer, primary_key=True)

# Explicit autoincrement
Column("id", Integer, autoincrement=True)

# Disable autoincrement
Column("id", Integer, primary_key=True, autoincrement=False)
```

**Default Values:**
```python
from sqlalchemy import func
from datetime import datetime

# Python default (set before insert)
Column("created_at", DateTime, default=datetime.utcnow)

# Server default (set by database)
Column("created_at", DateTime, server_default=func.now())

# Callable default
Column("uuid", String(36), default=lambda: str(uuid.uuid4()))

# Use CurrentDateTime for automatic timestamps
from sqlalchemy import CurrentDateTime
Column("updated_at", DateTime, default=CurrentDateTime(), onupdate=CurrentDateTime())
```

**Computed Columns:**
```python
from sqlalchemy import Computed

# Generated always as identity
Column("full_name", Computed("first_name || ' ' || last_name"))

# Stored generated column
Column("age_years", Computed("EXTRACT(YEAR FROM age)"), persisted=True)
```

## Data Types

### Built-in Types

**String Types:**
```python
String(50)           # Variable length string
Text                # Large text
Unicode(50)         # Unicode string
UnicodeText         # Large unicode text
LargeBinary         # Binary data
```

**Numeric Types:**
```python
Integer             # Standard integer
SmallInteger        # Small integer (typically 2 bytes)
BigInteger          # Large integer
Numeric(10, 2)      # Fixed precision decimal
Float               # Floating point
Float(precision=53) # High precision float
```

**Boolean Type:**
```python
Boolean             # True/False value
```

**Date and Time Types:**
```python
Date                # Date only
Time                # Time only
DateTime            # Date and time
Interval            # Time interval
```

**Binary Types:**
```python
LargeBinary         # Large binary data
```

**JSON Types:**
```python
from sqlalchemy.dialects.postgresql import JSONB  # PostgreSQL JSONB
from sqlalchemy import JSON                       # Generic JSON
```

### Type Configuration

**Custom Display Name:**
```python
Column("name", String(50).with_variant(String(100), "mysql"))
```

**Collation:**
```python
Column("name", String(50).with_variant(String(50, collation="utf8mb4_unicode_ci"), "mysql"))
```

**Custom Types:**
```python
from sqlalchemy import TypeDecorator

class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        return encrypt(value) if value else None
    
    def process_result_value(self, value, dialect):
        return decrypt(value) if value else None

Column("secret", EncryptedString(120))
```

### Type Adaptation

**Dialect-Specific Types:**
```python
from sqlalchemy import String, Integer

# Type adapts to dialect
Column("name", String(50))  # VARCHAR(50) in most dialects

# Force specific type per dialect
Column("id", Integer().with_variant(BigInteger, "mysql"))
```

**Implicit Adaptation:**
```python
# Python types can be used directly (limited support)
Column("value", type_=str)  # Becomes String
Column("count", type_=int)  # Becomes Integer
```

## Constraints

### Primary Key

```python
# Single column primary key
Column("id", Integer, primary_key=True)

# Composite primary key
Table(
    "scores", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("game_id", Integer, primary_key=True),
    Column("score", Integer)
)

# Named primary key
PrimaryConstraint(
    Column("id", Integer),
    name="pk_users"
)
```

### Foreign Key

```python
# Basic foreign key
Column("user_id", Integer, ForeignKey("users.id"))

# Multiple foreign keys in one column
Column("start_date", Date, ForeignKey("events.start_date"))
Column("end_date", Date, ForeignKey("events.end_date"))

# Composite foreign key
ForeignKeyConstraint(
    ["city_id", "street_id"],
    ["addresses.city_id", "addresses.street_id"],
    name="fk_locations"
)

# Foreign key with options
Column(
    "user_id", Integer,
    ForeignKey(
        "users.id",
        ondelete="CASCADE",
        onupdate="SET NULL",
        name="fk_posts_user_id"
    )
)
```

### Unique Constraint

```python
# Single column unique
Column("email", String(120), unique=True)

# Multiple column unique
UniqueConstraint("first_name", "last_name", name="uq_names")

# Named unique constraint
Column("username", String(50), UniqueConstraint(name="uq_username"))
```

### Check Constraint

```python
# Simple check
CheckConstraint("age >= 18", name="ck_adults_only")

# Column-based check
CheckConstraint("quantity > 0", name="ck_positive_quantity")

# Complex expression
from sqlalchemy import and_
CheckConstraint(
    and_(Column("start_date") < Column("end_date")),
    name="ck_date_range"
)
```

### Indexes

**Basic Index:**
```python
Index("ix_users_username", "username")

# On table definition
users = Table(
    "users", metadata,
    Column("username", String(50)),
    Index("ix_users_username", "username")
)

# Unique index
Index("ix_users_email_unique", "email", unique=True)
```

**Composite Index:**
```python
Index("ix_users_name", "first_name", "last_name")
```

**Functional Index:**
```python
from sqlalchemy import func

Index(
    "ix_users_lower_name",
    func.lower("username")
)

# PostgreSQL expression index
Index(
    "ix_posts_active",
    "active",
    postgresql_where=Column("active") == True
)
```

**Dialect-Specific Indexes:**
```python
# PostgreSQL GIN index for JSONB
from sqlalchemy.dialects.postgresql import GIN

Index(
    "ix_data_json",
    Column("data", JSONB),
    postgresql_using="gin"
)

# MySQL FULLTEXT index
from sqlalchemy.dialects.mysql import FULLTEXT

Index(
    "ix_posts_content_ft",
    Column("content"),
    mysql_using="fulltext"
)
```

## Table Options

### Schema Qualification

```python
# Table in specific schema
users = Table(
    "users", metadata,
    schema="public",
    # ... columns
)

# Cross-schema foreign key
Column("user_id", Integer, ForeignKey("public.users.id"))
```

### Temporary Tables

```python
# Create temporary table
temp_data = Table(
    "temp_data", metadata,
    Column("id", Integer, primary_key=True),
    tempfile=True,  # PostgreSQL temporary table
)

# Or use WITH clause for CTEs
from sqlalchemy import cte

base_cte = users.cte("active_users")
stmt = select(base_cte).where(base_cte.c.active == True)
```

### Conditional Creation

```python
# Create table if not exists
if not inspect(engine).has_table("users"):
    users.create(engine)

# Drop and recreate
users.drop(engine, checkfirst=True)
users.create(engine)

# Create all tables in metadata
metadata.create_all(engine)

# Drop all tables
metadata.drop_all(engine)
```

### Table Comments

```python
# Add table comment (dialect-dependent)
users = Table(
    "users", metadata,
    # ... columns
)

# PostgreSQL: Use COMMENT ON
with engine.connect() as conn:
    conn.execute(text("COMMENT ON TABLE users IS 'User accounts'"))
```

## Advanced Schema Features

### Inheritance Tables

**Single Table Inheritance:**
```python
class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_type = Column(String(50))
    __mapper_args__ = {
        "polymorphic_on": employee_type,
        "polymorphic_identity": "employee"
    }

class Manager(Employee):
    __tablename__ = "managers"
    id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    department = Column(String(50))
    __mapper_args__ = {
        "polymorphic_identity": "manager"
    }
```

### Hybrid Tables (Core + ORM)

```python
# Define table in Core
users_table = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

# Map ORM class to existing table
class User(Base):
    __table__ = users_table
```

### Dynamic Schema

```python
# Create tables dynamically
def create_table_for_model(model_name, columns):
    table = Table(
        model_name, metadata,
        *columns
    )
    return table

# Use in application
dynamic_table = create_table_for_model("temp_data", [
    Column("id", Integer, primary_key=True),
    Column("value", String(100)),
])
```

## Reflection (Introspection)

### Reflecting Tables

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# Get all table names
tables = inspector.get_table_names(schema="public")

# Get specific table columns
columns = inspector.get_columns("users")
for col in columns:
    print(col["name"], col["type"], col["primary_key"])

# Get foreign keys
fks = inspector.get_foreign_keys("posts")

# Get indexes
indexes = inspector.get_indexes("users")

# Get constraints
constraints = inspector.get_unique_constraints("users")
```

### Reflecting with Options

```python
# Reflect only specific columns
metadata = MetaData()
metadata.reflect(
    bind=engine,
    only=["users", "posts"],
    extend_existing=True,  # Add to existing table definitions
    replace_existing=False  # Don't replace existing definitions
)
```

## DDL Execution

### Programmatic DDL

```python
from sqlalchemy import event, DDL

# Create index after table creation
@event.listens_for(metadata, "after_create")
def create_indexes(target, connection, **kw):
    DDL("CREATE INDEX ix_special ON users (email)").execute(connection)

# Drop index before table drop
@event.listens_for(metadata, "before_drop")
def drop_indexes(target, connection, **kw):
    DDL("DROP INDEX ix_special").execute(connection)
```

### Inline DDL

```python
from sqlalchemy.schema import CreateIndex, DropIndex

# Create index programmatically
create_idx = CreateIndex(
    Index("ix_users_email", "users", "email")
)

with engine.connect() as conn:
    conn.execute(create_idx)
```

## Best Practices

1. **Use naming conventions** for consistent constraint names
2. **Define indexes** for foreign keys and frequently queried columns
3. **Use appropriate types** (e.g., Numeric for money, not Float)
4. **Set nullable=False** for required fields
5. **Use server_default** for database-managed defaults
6. **Document constraints** with meaningful names
7. **Consider reflection** for existing databases
8. **Use metadata naming conventions** for automatic constraint naming

## Common Patterns

### Audit Columns

```python
from sqlalchemy import func

audit_cols = [
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
]

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    *audit_cols,
)
```

### Soft Delete Pattern

```python
soft_delete_cols = [
    Column("is_deleted", Boolean, default=False),
    Column("deleted_at", DateTime),
]

# Add to all tables that support soft delete
posts = Table(
    "posts", metadata,
    Column("id", Integer, primary_key=True),
    *soft_delete_cols,
)

# Query excludes deleted
active_posts = posts.where(posts.c.is_deleted == False)
```

### Multi-tenancy Pattern

```python
tenant_cols = [
    Column("tenant_id", Integer, nullable=False, index=True),
]

# Add to all tenant-aware tables
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    *tenant_cols,
)

# Always filter by tenant
stmt = select(users).where(users.c.tenant_id == current_tenant_id)
```

## Next Steps

- [Core Querying](04-core-querying.md) - Execute SELECT, INSERT, UPDATE, DELETE
- [ORM Mapping](05-orm-mapping.md) - Map Python classes to tables
- [Reflection](13-core-reflection.md) - Advanced introspection techniques
- [Custom Types](15-core-custom-types.md) - Create custom type adapters
