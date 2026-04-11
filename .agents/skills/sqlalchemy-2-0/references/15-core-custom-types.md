# Core Custom Types and Type Engineering

## Introduction to Custom Types

SQLAlchemy's type system allows you to create custom types for handling specialized data, database-specific types, or application-specific transformations.

```python
from sqlalchemy.types import TypeDecorator

class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        return encrypt(value) if value else None
    
    def process_result_value(self, value, dialect):
        return decrypt(value) if value else None

Column("secret", EncryptedString(120))
```

## TypeDecorator Basics

### Simple Type Decorator

```python
from sqlalchemy.types import TypeDecorator, String

class IPAddress(TypeDecorator):
    """Store IP addresses as strings with validation"""
    impl = String
    cache_ok = True  # Important for performance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, length=45, **kwargs)  # IPv6 max length
    
    def process_bind_param(self, value, dialect):
        if value:
            # Validate IP address
            try:
                ip = ipaddress.ip_address(value)
                return str(ip)
            except ValueError as e:
                raise ValueError(f"Invalid IP address: {value}") from e
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            return ipaddress.ip_address(value)
        return None

# Usage
class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(IPAddress)  # Automatic validation
```

### Type with Dialect-Specific Behavior

```python
from sqlalchemy.types import TypeDecorator, DateTime

class ServerDateTime(TypeDecorator):
    """Use server's timezone for all datetime operations"""
    impl = DateTime
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        # Convert to UTC before sending to database
        if value and value.tzinfo:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    
    def process_result_value(self, value, dialect):
        # Assume database returns UTC, add timezone info
        if value:
            return value.replace(tzinfo=timezone.utc)
        return value
    
    def bind_expression(self, bindparam):
        # Optional: cast to timestamp in SQL
        return cast(bindparam, DateTime(timezone=True))

# Usage
class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(ServerDateTime)
```

## Composite Types

### Mutable Composite Types

```python
from sqlalchemy.ext.mutable import Mutable, mutable_composite
from sqlalchemy.types import TypeDecorator

class Point(Mutable):
    """Composite type for 2D points"""
    
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, (list, tuple)):
            return cls(*value)
        return value
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    # Store as JSON or two separate columns
    position = Column(mutable_composite(Point, 'position'))

# Usage - changes are automatically tracked
location = session.get(Location, 1)
location.position.x = 10  # Tracked!
location.position.y = 20  # Tracked!
session.commit()  # Both changes persisted
```

### Custom Composite with SQL Representation

```python
from sqlalchemy.types import TypeDecorator, CompoundType
from sqlalchemy.ext.compiler import compiles

class Range(CompoundType):
    """Represent a numeric range"""
    
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __repr__(self):
        return f"Range({self.start}, {self.end})"

class IntegerRange(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value:
            return f"[{value.start},{value.end}]"
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            start, end = value.strip("[]").split(",")
            return Range(int(start), int(end))
        return None

class PriceTier(Base):
    __tablename__ = "price_tiers"
    
    id = Column(Integer, primary_key=True)
    quantity_range = Column(IntegerRange)
    price = Column(Numeric(10, 2))
```

## JSON and Dictionary Types

### Custom JSON Types

```python
from sqlalchemy.types import TypeDecorator, JSON
import json

class EncryptedJSON(TypeDecorator):
    """Encrypt JSON data before storage"""
    impl = JSON
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value:
            # Encrypt the JSON string
            json_str = json.dumps(value)
            encrypted = encrypt(json_str)
            return encrypted
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            # Decrypt and parse JSON
            decrypted = decrypt(value)
            return json.loads(decrypted)
        return None

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(Integer, primary_key=True)
    preferences = Column(EncryptedJSON)
```

### Mutable Dictionary

```python
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.types import TypeDecorator

class SettingsDict(MutableDict):
    """Dictionary with automatic change tracking"""
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    settings = Column(SettingsDict.as_mutable(JSON))

# Usage - changes tracked automatically
user = session.get(User, 1)
user.settings["theme"] = "dark"  # Tracked!
user.settings["lang"] = "en"     # Tracked!
session.commit()  # Only changed keys updated
```

## Array Types

### PostgreSQL Array Type

```python
from sqlalchemy.dialects.postgresql import ARRAY

class TaggedPost(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    # Array of strings
    tags = Column(ARRAY(String))
    # Array of integers
    author_ids = Column(ARRAY(Integer))

# Usage
post = TaggedPost()
post.tags = ["python", "sqlalchemy", "orm"]
post.author_ids = [1, 2, 3]

# Query array contents
posts_with_python = session.execute(
    select(TaggedPost).where(TaggedPost.tags.contains(["python"]))
).scalars().all()

# Array slicing (PostgreSQL)
from sqlalchemy import func
first_tag = func.slice(TaggedPost.tags, 1, 1)
```

### Custom Array Type

```python
from sqlalchemy.types import TypeDecorator

class SortedArray(TypeDecorator):
    """Always store arrays in sorted order"""
    impl = String  # Store as comma-separated string
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value:
            return ",".join(str(x) for x in sorted(value))
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            return [int(x) for x in value.split(",")]
        return []

class ScoreBoard(Base):
    __tablename__ = "scoreboards"
    
    id = Column(Integer, primary_key=True)
    top_scores = Column(SortedArray)  # Always sorted
```

## Enum Types

### Python Enum with SQLAlchemy

```python
from enum import Enum
from sqlalchemy.types import TypeDecorator, String

class UserRole(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class PythonEnum(TypeDecorator):
    """Store Python Enum as string"""
    impl = String
    cache_ok = True
    
    def __init__(self, enum_type, *args, **kwargs):
        self.enum_type = enum_type
        super().__init__(*args, length=max(len(e.value) for e in enum_type), **kwargs)
    
    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_type):
            return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value:
            return self.enum_type(value)
        return None

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    role = Column(PythonEnum(UserRole))  # Type-safe enum

# Usage - type-safe!
user = User()
user.role = UserRole.ADMIN  # Enum value, not string
```

### Database-Specific Enum (PostgreSQL)

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
        name="order_status"
    ))

# Usage
order = Order()
order.status = "pending"  # String value validated by database
```

## UUID Types

### Custom UUID Type

```python
from sqlalchemy.types import TypeDecorator, String
import uuid

class GUID(TypeDecorator):
    """Platform-independent GUID type using UUID"""
    impl = String
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, length=32, **kwargs)
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value.hex  # Store as hex string
        return value
    
    def process_result_value(self, value, dialect):
        if value:
            return uuid.UUID(value)  # Return UUID object
        return None

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(200))

# Usage - automatic UUID generation
doc = Document(name="My Document")
session.add(doc)
session.flush()
print(doc.id)  # <UUID '...'>
```

## Date/Time Custom Types

### Timezone-Aware DateTime

```python
from sqlalchemy.types import TypeDecorator, DateTime
from datetime import datetime, timezone

class UTCDateTime(TypeDecorator):
    """Always store datetimes in UTC"""
    impl = DateTime
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value:
            # Convert to UTC if timezone-aware
            if value.tzinfo:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            # Assume UTC if naive
            return value
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            # Return timezone-aware datetime
            return value.replace(tzinfo=timezone.utc)
        return None

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(UTCDateTime, default=datetime.utcnow)
```

## Type Adaptation for Multiple Dialects

### Dialect-Specific Types

```python
from sqlalchemy.types import TypeDecorator, String, Text

class AdaptiveText(TypeDecorator):
    """Use VARCHAR for MySQL, TEXT for PostgreSQL"""
    impl = Text
    cache_ok = True
    
    def __init__(self, length=None, **kwargs):
        if length:
            # Use String with length for dialects that need it
            self.impl = String(length)
        super().__init__(**kwargs)
    
    def load_dialect_impl(self, dialect):
        # PostgreSQL: use TEXT
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import TEXT
            return TEXT()
        # MySQL: use LONGTEXT for large text
        elif dialect.name == "mysql":
            from sqlalchemy.dialects.mysql import LONGTEXT
            return LONGTEXT()
        # Default: use impl
        return self.impl

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    content = Column(AdaptiveText)  # Adapts to dialect
```

## Best Practices

### 1. Always Set cache_ok=True

```python
# Good - enables type caching for performance
class MyType(TypeDecorator):
    impl = String
    cache_ok = True  # Important!
    
    def process_bind_param(self, value, dialect):
        return transform(value)

# Bad - no caching, creates new type instances
class SlowType(TypeDecorator):
    impl = String
    # cache_ok defaults to False
    
    def process_bind_param(self, value, dialect):
        return transform(value)
```

### 2. Handle None Values Explicitly

```python
class SafeType(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None  # Always handle None!
        return transform(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None  # Always handle None!
        return parse(value)
```

### 3. Validate Input Data

```python
class ValidatedType(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        
        try:
            validated = validate(value)
            return transform(validated)
        except ValidationError as e:
            raise ValueError(f"Invalid value for {self.__class__.__name__}: {value}") from e
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return parse(value)
```

### 4. Document Type Behavior

```python
class PhoneNumber(TypeDecorator):
    """
    Store phone numbers in E.164 format (+1234567890).
    
    - Input: Various formats accepted (123-456-7890, +1 234 567 890, etc.)
    - Storage: Normalized E.164 format as string
    - Output: Python string in E.164 format
    
    Dialect support: All (stored as VARCHAR)
    """
    impl = String
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, length=20, **kwargs)  # Max E.164 length
    
    def process_bind_param(self, value, dialect):
        if not value:
            return None
        # Normalize using phonenumbers library
        parsed = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"Invalid phone number: {value}")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    
    def process_result_value(self, value, dialect):
        return value  # Already in E.164 format
```

## Next Steps

- [Dialects](16-dialects-overview.md) - Dialect-specific types
- [Core Schema](03-core-schema-types.md) - Using custom types in tables
- [ORM Mapping](05-orm-mapping.md) - Custom types with ORM models
- [Best Practices](24-best-practices.md) - Type performance considerations
