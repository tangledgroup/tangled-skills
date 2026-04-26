# ORM Mapping and Session

## Declarative Base

All ORM mappings start with a `DeclarativeBase` class. This establishes the `MetaData` collection and `registry` for mapper configuration.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

The `Base.metadata` attribute provides access to the underlying `MetaData` collection. Use `Base.metadata.create_all(engine)` to emit DDL.

## Declaring Mapped Classes

SQLAlchemy 2.0 uses PEP 484 type annotations with `Mapped` and `mapped_column()`:

```python
from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]  # nullable via Optional type

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")
```

### Mapping Details

- `__tablename__` — sets the database table name. Without it, the class is not mapped to a table
- `Mapped[T]` — indicates an attribute is mapped. The type `T` determines the SQL type (e.g., `int` → `Integer`, `str` → `String`)
- `mapped_column()` — configures column options like `primary_key`, `nullable`, `default`, `server_default`
- Simple columns can use annotation alone: `email_address: Mapped[str]` creates a `String` column
- `Optional[T]` or `T | None` marks the column as nullable
- The ORM auto-generates `__init__()` accepting mapped attribute names as keyword arguments

### Legacy Column Style (Still Supported)

```python
from sqlalchemy import Column, Integer

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # old style, still works
    name = Column(String(50))
```

`mapped_column()` is a drop-in replacement for `Column` in declarative mappings and provides better IDE/type-checker support.

## Relationships

### One-to-Many / Many-to-One

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="addresses")
```

`back_populates` links the two sides of the relationship so that changes on one side automatically synchronize to the other.

### Many-to-Many

Use an association table:

```python
association_table = Table(
    "user_group", Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    groups: Mapped[list["Group"]] = relationship(secondary=association_table, back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    users: Mapped[list[User]] = relationship(secondary=association_table, back_populates="groups")
```

### Self-Referential Relationships

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))
    manager: Mapped["Employee | None"] = relationship(remote_side="Employee.id")
    subordinates: Mapped[list["Employee"]] = relationship(back_populates="manager")
```

### Relationship Cascade Options

```python
# Default cascade: "save-update, merge"
# Common patterns:
relationship(back_populates="user", cascade="all, delete-orphan")
# "all" = save-update, merge, refresh-expire, expunge, delete
# "delete-orphan" = delete child when removed from parent collection
```

## Session Operations

### Creating a Session

```python
from sqlalchemy.orm import Session, sessionmaker

# Direct creation
session = Session(engine)

# Recommended: use sessionmaker for configuration
SessionFactory = sessionmaker(bind=engine)
session = SessionFactory()

# Context manager (auto-closes on exit)
with Session(engine) as session:
    # ... operations
    pass  # auto-close, rollback uncommitted
```

### Inserting Objects (Unit of Work)

```python
user = User(name="spongebob", fullname="Spongebob Squarepants")
session.add(user)
# Object is now "pending" — not yet in database
session.commit()
# Transaction committed, object has primary key assigned
print(user.id)  # auto-generated PK
```

Objects go through states: **transient** (new, not in session) → **pending** (added to session, not flushed) → **persistent** (flushed to database) → **detached** (session closed).

### Flushing

The Session accumulates changes and emits SQL during a "flush" operation. Flush occurs automatically before any SELECT query (autoflush) and during `commit()`. Manual flush:

```python
session.flush()  # pushes pending changes to DB, transaction still open
```

### Updating Objects

The Session tracks attribute changes via the unit of work pattern:

```python
user = session.get(User, 1)
user.fullname = "Spongebob Squarepants Sr."
# Session marks object as "dirty"
session.commit()  # emits UPDATE automatically
```

### Deleting Objects

```python
user = session.get(User, 1)
session.delete(user)
session.commit()  # emits DELETE
```

### Bulk Operations

For large-scale operations without ORM overhead:

```python
from sqlalchemy import insert, update, delete

# Bulk insert (bypasses unit of work)
session.execute(insert(User), [
    {"name": "user1"}, {"name": "user2"}, {"name": "user3"}
])

# Bulk update
session.execute(
    update(User).where(User.name.like("%old%")).values(name=lambda c: c.name.replace("old", "new"))
)

# Bulk delete
session.execute(delete(User).where(User.name == "temp_user"))
```

## Querying with the ORM

### Basic Queries

```python
from sqlalchemy import select

# Select all
stmt = select(User)
users = session.scalars(stmt).all()

# With filter
stmt = select(User).where(User.name == "spongebob")
user = session.execute(stmt).scalar_one()

# Multiple conditions
stmt = select(User).where(
    (User.name == "sandy") | (User.fullname == "Sandy Cheeks")
)

# Using filter_by for simple equality
stmt = select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants")
```

### Accessing Results

```python
result = session.execute(select(User))

# Row objects
for row in result:
    user = row[0]  # or row.User

# Scalar access (first column of each row)
users = session.scalars(select(User)).all()

# Single result
user = session.scalars(select(User).where(User.id == 1)).one()
user = session.scalars(select(User).where(User.id == 999)).one_or_none()

# Column projections
names = session.scalars(select(User.name)).all()
```

### Get by Primary Key

```python
user = session.get(User, 1)
# Returns from identity map if present, otherwise emits SELECT
```

## Loader Strategies

SQLAlchemy provides several strategies for loading related objects to avoid the N+1 query problem:

### Lazy Loading (Default)

Related objects are loaded on first access. Simple but can cause N+1 queries:

```python
user = session.get(User, 1)
print(user.addresses)  # emits SELECT here
```

### Selectin Load

Loads related objects in a separate query using `IN` clause. Best for collections:

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.addresses))
users = session.scalars(stmt).all()
for user in users:
    print(user.addresses)  # already loaded, no extra query
```

### Joined Load

Uses a JOIN to load related objects in the same query. Best for many-to-one:

```python
from sqlalchemy.orm import joinedload

stmt = select(Address).options(joinedload(Address.user, innerjoin=True))
addresses = session.scalars(stmt).all()
```

### Raiseload

Prevents loading entirely, raises `LazyLoadError` on access:

```python
from sqlalchemy.orm import raiseload

stmt = select(User).options(raiseload(User.addresses))
```

### Configuring Default Loading

Set the default loading strategy at the relationship level:

```python
addresses: Mapped[list["Address"]] = relationship(
    back_populates="user", lazy="selectin"
)
```

## Session Lifecycle

### Commit and Rollback

```python
with Session(engine) as session:
    user = User(name="spongebob")
    session.add(user)
    session.commit()  # commits transaction, expires object attributes

    # After commit, accessing attributes triggers reload (unless expire_on_commit=False)
    print(user.name)  # emits SELECT to refresh

session.rollback()  # rolls back, expires all objects
session.close()  # releases connection, expunges all objects
```

### Expire on Commit

By default, `session.commit()` expires all object attributes so they reload from the database on next access. Disable with:

```python
session = Session(engine, expire_on_commit=False)
# Objects retain their state after commit
```

### Detached Instances

When a session is closed, all objects become detached. Accessing expired attributes on detached instances raises `DetachedInstanceError`:

```python
with Session(engine) as session:
    user = session.get(User, 1)

# Outside context manager, session is closed
print(user.name)  # DetachedInstanceError if name was expired

# Re-attach to a new session
with Session(engine) as session:
    session.add(user)
    print(user.name)  # reloads from database
```

## Declarative Dataclasses

SQLAlchemy supports native Python dataclass integration:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, DeclarativeBaseNoMeta

class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

This provides `__init__` with positional arguments, `__repr__`, and `__eq__` automatically.
