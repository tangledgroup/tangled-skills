# ORM Mapping Configuration

## Declarative Base

### Basic Setup

SQLAlchemy 2.0 recommends using `DeclarativeBase` for ORM mapping:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass

# All models inherit from Base
class User(Base):
    __tablename__ = "users"
    # ... columns and relationships
```

### Customizing the Base

```python
from sqlalchemy.orm import DeclarativeBase, registry
from sqlalchemy import MetaData

# Custom metadata with naming conventions
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Create base with custom metadata
Base = declarative_base(metadata=metadata)

# Or use DeclarativeBase with registry
my_registry = registry(metadata=metadata)

class Base(my_registry.generate_base()):
    pass
```

### Common Base Classes

**With Common Columns:**
```python
from sqlalchemy import Column, Integer, DateTime, func
from datetime import datetime

class TimestampedBase(Base):
    __abstract__ = True  # Don't create table for this class
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class User(TimestampedBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    # inherits created_at and updated_at
```

**With Soft Delete:**
```python
class SoftDeleteBase(Base):
    __abstract__ = True
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime)

class Post(SoftDeleteBase):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
```

## Table and Column Mapping

### Basic Column Definition

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Column Options

**Primary Key:**
```python
# Single primary key
id = Column(Integer, primary_key=True)

# Composite primary key
class Assignment(Base):
    __tablename__ = "assignments"
    
    student_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, primary_key=True)
    grade = Column(String(2))
```

**Nullable and Default:**
```python
# Required field
email = Column(String(120), nullable=False)

# Optional field with default
nickname = Column(String(50), default="Anonymous")

# Server default
created_at = Column(DateTime, server_default=func.now())

# Python default (set before insert)
uuid = Column(String(36), default=lambda: str(uuid.uuid4()))
```

**Index and Unique:**
```python
# Single column index
username = Column(String(50), unique=True, index=True)

# Multiple column index
class Event(Base):
    __tablename__ = "events"
    
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    __table_args__ = (
        Index("ix_events_dates", "start_date", "end_date"),
    )
```

### Table Options

**Schema:**
```python
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
```

**Table Arguments:**
```python
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    
    __table_args__ = (
        Index("ix_posts_title", "title"),
        {"extend_existing": True}  # For reflection scenarios
    )
```

**Comment (Dialect-Specific):**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    __table_args__ = {
        "comment": "User accounts table"  # PostgreSQL, MySQL
    }
```

## Relationship Mapping

### Basic Relationships

**One-to-Many:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    
    # One user has many posts
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Many posts belong to one user
    author = relationship("User", back_populates="posts")
```

**Many-to-Many:**
```python
# Association table
user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id"))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    users = relationship("User", secondary=user_roles, back_populates="roles")
```

**One-to-One:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    profile = relationship("UserProfile", uselist=False, back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text)
    user = relationship("User", uselist=False, back_populates="profile")
```

### Relationship Options

**Cascade Options:**
```python
# Cascade operations to related objects
posts = relationship(
    "Post",
    cascade="all, delete-orphan",  # Propagate all operations
    back_populates="author"
)

# Common cascade patterns:
# - "all": All save/update/delete operations
# - "delete": Delete cascades to children
# - "delete-orphan": Orphaned objects are deleted
# - "merge": Merge state propagates
# - "expunge": Expunge cascades
# - "refresh-expire": Refresh/expire cascades
```

**Lazy Loading Strategies:**
```python
from sqlalchemy.orm import lazyload, joinedload, subqueryload

# Lazy loading (default) - loads on access
posts = relationship("Post", lazy="select")

# Select - separate query when accessed
posts = relationship("Post", lazy="select")

# Joinedload equivalent at relationship level
posts = relationship("Post", lazy="joined")

# Subquery load - single IN query
posts = relationship("Post", lazy="subquery")

# Eager - always load with parent
posts = relationship("Post", lazy="raise")  # Raise error if not loaded

# Dynamic - returns Query object
posts = relationship("Post", lazy="dynamic")
```

**Order By:**
```python
# Pre-order relationship results
posts = relationship(
    "Post",
    order_by=Post.created_at.desc(),
    back_populates="author"
)
```

**Primary and Secondary Join:**
```python
# Custom join conditions
posts = relationship(
    "Post",
    primaryjoin="and_(User.id == Post.user_id, Post.deleted == False)",
    back_populates="author"
)

# For many-to-many with association table columns
roles = relationship(
    "Role",
    secondary=user_roles,
    primaryjoin="User.id == user_roles.c.user_id",
    secondaryjoin="Role.id == user_roles.c.role_id",
    back_populates="users"
)
```

## Inheritance Mapping

### Single Table Inheritance

All classes share one table with discriminator column:

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    employee_type = Column(String(50), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": employee_type,
        "polymorphic_identity": "employee"
    }

class Engineer(Employee):
    __tablename__ = "engineers"  # Not used in single table
    
    programming_language = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer"
    }

class Manager(Employee):
    __tablename__ = "managers"  # Not used in single table
    
    department = Column(String(100))
    
    __mapper_args__ = {
        "polymorphic_identity": "manager"
    }
```

**Querying:**
```python
# Get all employees (all types)
employees = session.query(Employee).all()

# Get specific type only
engineers = session.query(Engineer).all()

# Polymorphic loading
employees = session.query(Employee).options(
    polymorphic_load(EagerLoad)  # Load all subclasses
).all()
```

### Joined Table Inheritance

Each class has its own table with foreign key to parent:

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    employee_type = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_on": employee_type,
        "polymorphic_identity": "employee"
    }

class Engineer(Employee):
    __tablename__ = "engineers"
    
    id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    programming_language = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer"
    }

class Manager(Employee):
    __tablename__ = "managers"
    
    id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    department = Column(String(100))
    
    __mapper_args__ = {
        "polymorphic_identity": "manager"
    }
```

### Concrete Table Inheritance

Each class has its own complete table:

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    employee_type = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_on": employee_type,
        "polymorphic_identity": "employee"
    }

class Engineer(Base):  # Not inheriting from Employee
    __tablename__ = "engineers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    employee_type = Column(String(50), default="engineer")
    programming_language = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer"
    }
```

### Abstract Base Classes

For shared columns without mapping:

```python
class TimestampedMixin(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class User(TimestampedMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    # Inherits created_at and updated_at columns
```

## Advanced Mapping

### Mapped Columns

Using the `mapped_column` shortcut:

```python
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer

class User(Base):
    __tablename__ = "users"
    
    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), unique=True)
    email = mapped_column(String(120), index=True)
```

### Hybrid Attributes

For properties that work both on instances and in queries:

```python
from sqlalchemy.orm import declared_attr, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = "users"
    
    id = mapped_column(Integer, primary_key=True)
    first_name = mapped_column(String(50))
    last_name = mapped_column(String(50))
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @full_name.expression
    @classmethod
    def full_name(cls):
        return cls.first_name + " " + cls.last_name

# Use in queries
users = session.query(User).filter(User.full_name.like("John %")).all()

# Use on instances
user = users[0]
print(user.full_name)  # Works on instance too
```

### Declared Attributes

For reusable column/relationship definitions:

```python
class BaseMixin(Base):
    __abstract__ = True
    
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)

class User(BaseMixin):
    __tablename__ = "users"
    
    # Inherits id and created_at automatically
    username = Column(String(50))
```

### Composite Types

For multi-column attributes:

```python
from sqlalchemy import CompositeType, TypeDecorator

class Point(CompositeType):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        return cls(*value)

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    point = Column(Point(Integer, Integer))
```

## Mapping to Existing Tables

### Using Core Table Definitions

```python
from sqlalchemy import Table, Column, Integer, String, MetaData

# Define table in Core
metadata = MetaData()
users_table = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50)),
)

# Map ORM class to existing table
class User(Base):
    __table__ = users_table
```

### Reflection with ORM

```python
from sqlalchemy import inspect

# Reflect tables into metadata
metadata = MetaData()
metadata.reflect(bind=engine)

# Generate ORM classes from reflected tables
Base = declarative_base(metadata=metadata)

# Or use automap (see Automap extension)
```

## Model Validation

### Python-Level Validation

```python
from sqlalchemy import event

@event.listens_for(User, "before_insert")
def validate_user_before_insert(mapper, connection, target):
    if not target.email or "@" not in target.email:
        raise ValueError("Invalid email address")
    
    if len(target.username) < 3:
        raise ValueError("Username must be at least 3 characters")
```

### Column-Level Validation

```python
from sqlalchemy import CheckConstraint

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    
    __table_args__ = (
        CheckConstraint("age >= 0", name="ck_user_age_non_negative"),
    )
```

## Best Practices

1. **Use `DeclarativeBase`** for new projects
2. **Set `nullable=False`** for required fields
3. **Use meaningful relationship names** (singular/plural appropriately)
4. **Configure cascade carefully** to avoid unintended deletions
5. **Add indexes** on foreign keys and frequently queried columns
6. **Use abstract base classes** for shared columns
7. **Choose appropriate inheritance strategy** for your use case
8. **Document complex relationships** with comments

## Async Support with AsyncAttrs

For async applications, mix `AsyncAttrs` into your base class to enable awaitable attribute access:

```python
from __future__ import annotations
from typing import List
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship

class Base(AsyncAttrs, DeclarativeBase):
    """Base class with async support"""
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    posts: Mapped[List["Post"]] = relationship()

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

### Using AsyncAttrs

The `AsyncAttrs` mixin provides the `awaitable_attrs` accessor for loading relationships without implicit IO:

```python
async def load_user_with_posts():
    async with AsyncSessionLocal() as session:
        user = await session.get(User, 1)
        
        # Load relationship explicitly (prevents implicit lazy loading)
        for post in await user.awaitable_attrs.posts:
            print(post.title)
```

### Benefits of AsyncAttrs

1. **Prevents Implicit IO**: No accidental lazy loading that would fail in async context
2. **Type-Safe**: Works with Python 2.0 style type annotations
3. **Simple API**: Just prefix attribute access with `awaitable_attrs`
4. **Added in 2.0.13**: Available in all recent SQLAlchemy 2.0 versions

### Alternative Approaches

If not using AsyncAttrs, you must use:
- **Eager loading** (`selectinload`, `joinedload`)
- **Write-only relationships** (`lazy="write_only"`)
- **Explicit refresh** for specific attributes

See [AsyncIO Support](07-orm-asyncio.md) for complete async patterns.

## Next Steps

- [ORM Session](06-orm-session.md) - Using the Session for persistence
- [ORM Relationships](08-orm-relationships.md) - Advanced relationship patterns
- [ORM Querying](09-orm-querying.md) - Querying mapped objects
- [Hybrid Attributes](10-orm-hybrid-attributes.md) - Property expressions
- [AsyncIO Support](07-orm-asyncio.md) - Complete async/await guide
