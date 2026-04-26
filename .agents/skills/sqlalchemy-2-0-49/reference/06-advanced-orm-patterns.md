# Advanced ORM Patterns

## Hybrid Attributes

Hybrid attributes combine Python-level properties with SQL-level expressions, allowing the same attribute to work on both instances and class-level queries:

```python
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.inplace
    def _full_name_sql(self):
        return self.first_name + " " + self.last_name

# Works on instances
print(user.full_name)  # "John Doe"

# Works in queries
stmt = select(User).where(User.full_name == "John Doe")
```

## Column Properties

`column_property` computes a SQL expression that behaves like a column:

```python
from sqlalchemy.orm import column_property
from sqlalchemy import func

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # Computed property — not stored in database
    name_length = column_property(func.length(name))
```

## Association Proxy

The `association_proxy` provides convenient access to attributes through association objects:

```python
from sqlalchemy.orm import association_proxy

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    user_addresses: Mapped[list["UserAddress"]] = relationship(back_populates="user")
    # Proxy to access Address.email_address directly
    addresses = association_proxy("user_addresses", "address")

class UserAddress(Base):
    __tablename__ = "user_addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    user: Mapped[User] = relationship(back_populates="user_addresses")
    address: Mapped["Address"] = relationship(back_populates="user_addresses")
```

## Custom Types

### TypeDecorator

Create custom types that transform data between Python and SQL:

```python
from sqlalchemy import TypeDecorator, String
import json

class JsonEncoded(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JsonEncoded)
```

### Compiling Custom Types

For types that need different SQL representations per dialect:

```python
from sqlalchemy import TypeDecorator, String, Text

class LargeText(TypeDecorator):
    impl = Text
    cache_ok = True

    def bind_processor(self, dialect):
        if dialect.name == "oracle":
            return lambda value: value[:4000] if value else None
        return None

    def column_expression(self):
        return super().column_expression()
```

## Events

SQLAlchemy's event system allows hooking into internal operations:

### ORM Events

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

@event.listens_for(Session, "before_flush")
def receive_before_flush(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, "created_at"):
            obj.created_at = datetime.utcnow()

@event.listens_for(User, "before_insert")
def receive_before_insert(mapper, connection, target):
    target.created_at = datetime.utcnow()

@event.listens_for(User, "after_load")
def receive_after_load(target, context):
    # Called after object is loaded from database
    pass

@event.listens_for(Session, "after_commit")
def receive_after_commit(session):
    # Called after successful commit
    pass
```

### Core Events

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"Executing: {statement}")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    pass

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    # Called when a connection is checked out from the pool
    pass
```

## Validated Columns

`validated_column` adds Python-level validation to column access:

```python
from sqlalchemy.orm import validated_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = validated_column(
        type_=String(120),
        set_validation=lambda value: (
            value if "@" in value else (_ for _ in ()).throw(ValueError("Invalid email"))
        )
    )
```

## Declarative Configuration

### `__mapper_args__`

Fine-tune mapper configuration:

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    __mapper_args__ = {
        "primary_key": [id],  # custom PK columns
        "with_polymorphic": "*",  # load all polymorphic columns
        "polymorphic_on": "type",  # discriminator column
    }
```

### Single Table Inheritance

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "employee"}

class Manager(Employee):
    __mapper_args__ = {"polymorphic_identity": "manager"}
    department: Mapped[str] = mapped_column(String(50))

class Engineer(Employee):
    __mapper_args__ = {"polymorphic_identity": "engineer"}
    programming_language: Mapped[str] = mapped_column(String(50))
```

### Concrete Table Inheritance

```python
class Bird(Base):
    __mapper_args__ = {"polymorphic_abstract": True}

class FlyingBird(Bird):
    __tablename__ = "flying_birds"
    id: Mapped[int] = mapped_column(primary_key=True)
    speed: Mapped[int]

class SwimmingBird(Bird):
    __tablename__ = "swimming_birds"
    id: Mapped[int] = mapped_column(primary_key=True)
    depth: Mapped[int]
```

## Ordering List

`order_list` maintains ordered collections:

```python
from sqlalchemy.orm import order_list

class Chapter(Base):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int]
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    chapters: Mapped[list[Chapter]] = relationship(
        order_by=Chapter.position,
        collection_class=order_list(Chapter.position)
    )
```

## Mutable Composites

Track mutations in nested structures:

```python
from sqlalchemy.ext.mutable import Mutable, MutableList
import json

class JsonMutable(Mutable):
    @classmethod
    def coerce_cls(cls, target, key, value):
        if isinstance(value, (dict, list)):
            return MutableList.provide_type(JSON).coerce(target, key, value)
        return super().coerce_cls(target, key, value)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    settings: Mapped[dict] = mapped_column(JSON, mutable=True)
```

## Baked Queries

For frequently executed queries, `baked` queries cache the query construction process:

```python
from sqlalchemy.orm import baked_query

@baked_query
def get_active_users(session, min_age):
    return session.query(User).filter(
        User.active == True,
        User.age >= min_age
    )

# First call builds and caches, subsequent calls reuse
users = get_active_users(session, 18).all()
```

## Column Defaults and Server Defaults

```python
from sqlalchemy import func, text

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Python-side default (applied before INSERT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.utcnow()
    )

    # Server-side default (database generates value)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Python callable evaluated on insert
    def _gen_slug():
        return uuid.uuid4().hex

    slug: Mapped[str] = mapped_column(String(32), default=_gen_slug)

    # Server-side computed
    row_version: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), onupdate=lambda: func.now()
    )
```

## Eager Defaults

SQLAlchemy 2.0 supports `eager_defaults` which retrieves default values from the database after INSERT without requiring a separate round-trip:

```python
class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}
```

This is particularly useful when the database generates default values (via triggers, sequences, or server defaults) and you need those values available on the Python object immediately after flush.
