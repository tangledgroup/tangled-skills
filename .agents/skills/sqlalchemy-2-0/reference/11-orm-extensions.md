# ORM Extensions

## Overview of ORM Extensions

SQLAlchemy provides several extensions that enhance the ORM's functionality:

- **Association Proxy**: Delegate relationship access to collection attributes
- **Automap**: Generate mapped classes from reflected tables
- **Mutable**: Track changes in composite types
- **AsyncIO**: Asynchronous session and engine support

## Association Proxy Extension

### Basic Usage

Association proxy allows you to treat a collection of related objects as a simple Python collection:

```python
from sqlalchemy.orm import association_proxy

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

class PostTagAssociation(Base):
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    
    # Relationship to association objects
    post_tags = relationship("PostTagAssociation", back_populates="post")
    
    # Proxy to tag names (not Tag objects)
    tag_names = association_proxy(
        "post_tags", 
        "tag",
        creator=lambda tag_name: PostTagAssociation(
            tag=Tag(name=tag_name)
        )
    )

class PostTagAssociation(Base):
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag")

# Usage - works like a simple list of strings
post = Post(title="My Post")
post.tag_names = ["python", "sqlalchemy", "orm"]

session.add(post)
session.commit()

# Access as simple list
print(post.tag_names)  # ['python', 'sqlalchemy', 'orm']
```

### Advanced Proxy Configuration

```python
from sqlalchemy.orm import association_proxy

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    roles = relationship("UserRole", back_populates="user")
    
    # Proxy with custom creator
    role_names = association_proxy(
        "roles",
        "role_name",
        creator=lambda name: UserRole(role_name=name)
    )
    
    # Read-only proxy
    role_ids = association_proxy("roles", "role_id", creator=None)

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_name = Column(String(50), primary_key=True)
    role_id = Column(Integer)
    
    user = relationship("User", back_populates="roles")

# Usage
user = User()
user.role_names = ["admin", "editor"]  # Creates UserRole objects
print(user.role_ids)  # [1, 2] - read-only access to IDs
```

### Proxy with Collections

```python
from sqlalchemy.orm import association_proxy
from collections import OrderedDict

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    
    comments = relationship("Comment", order_by="Comment.id")
    
    # Proxy to comment authors as ordered set
    author_ids = association_proxy(
        "comments",
        "author_id",
        collection_class=OrderedDict
    )

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)

# Usage
post = Post()
# author_ids will maintain order of comment creation
```

## Automap Extension

### Basic Automap

Automatically generate mapped classes from existing database schema:

```python
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

# Create engine and reflect tables
engine = create_engine("postgresql://user:pass@localhost/db")
Base = automap_base()

# Reflect tables into Base
Base.prepare(engine, reflect=True)

# Access generated classes
User = Base.classes.users  # Auto-generated from 'users' table
Post = Base.classes.posts  # Auto-generated from 'posts' table

# Use like normal ORM classes
Session = sessionmaker(bind=engine)
session = Session()

user = session.get(User, 1)
print(user.username)

# Relationships are auto-detected based on foreign keys
for post in user.posts:
    print(post.title)
```

### Customizing Automap Classes

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship

Base = automap_base()

# Reflect with customizations
Base.prepare(
    engine,
    reflect=True,
    # Add custom relationships
    classes={
        'users': type('User', (Base,), {
            'posts': relationship('Post', back_populates='author')
        }),
        'posts': type('Post', (Base,), {
            'author': relationship('User', back_populates='posts')
        })
    }
)

# Or use inheritance to add methods
class UserMixin:
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

Base = automap_base()
Base.prepare(
    engine,
    reflect=True,
    inherit={'users': UserMixin}  # Add mixin to users class
)

User = Base.classes.users
user = session.get(User, 1)
print(user.full_name)  # Available from mixin
```

### Selective Reflection

```python
from sqlalchemy.ext.automap import automap_base

Base = automap_base()

# Reflect only specific tables
Base.prepare(
    engine,
    reflect=True,
    only=['users', 'posts', 'comments']
)

# Reflect with schema
Base.prepare(
    engine,
    reflect=True,
    schema='public'
)

# Exclude certain tables
Base.prepare(
    engine,
    reflect=True,
    extends={'users': lambda cls: hasattr(cls, 'password')}  # Custom filter
)
```

## Mutable Extension

### Tracking Composite Types

The Mutable extension helps track changes in composite types (like dictionaries or custom objects):

```python
from sqlalchemy.ext.mutable import Mutable, MutableDict
from sqlalchemy import Column, Integer

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    # JSON column that tracks changes
    preferences = Column(MutableDict.as_mutable(JSON))

# Usage
user = session.get(User, 1)
user.preferences["theme"] = "dark"  # Tracked as change
user.preferences["lang"] = "en"     # Tracked as change

session.commit()  # All changes persisted
```

### Custom Mutable Types

```python
from sqlalchemy.ext.mutable import Mutable, mutable_composite
from sqlalchemy import Column, Integer

class Point(Mutable):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, cls):
            return value
        return cls(*value)
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    point = Column(mutable_composite(Point, 'point'))

# Usage
location = Location()
location.point = Point(10, 20)
session.add(location)
session.flush()

# Modify tracked object
location.point.x = 15  # Tracked as change
session.commit()  # Change persisted
```

### Mutable List

```python
from sqlalchemy.ext.mutable import MutableList, MutableList
from sqlalchemy import Column, Integer

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    tags = Column(MutableList.as_mutable(JSON))

# Usage
user = session.get(User, 1)
user.tags.append("python")  # Tracked
user.tags.remove("java")    # Tracked

session.commit()  # Changes persisted
```

## AsyncIO Extension (Detailed)

See [AsyncIO Support](07-orm-asyncio.md) for comprehensive async usage.

### Key Components

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

# Create async engine
async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession
)

# Use in async context
async def get_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == 1))
        return result.scalar_one()
```

## Other Extensions

### Composite Types

For multi-column attributes:

```python
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator, CompoundType

class IPRange(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value:
            return f"{value.start}-{value.end}"
        return None
    
    def process_result_value(self, value, dialect):
        if value:
            start, end = value.split("-")
            return IPRange(int(start), int(end))
        return None

class IPAddress:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Network(Base):
    __tablename__ = "networks"
    
    id = Column(Integer, primary_key=True)
    ip_range = Column(IPRange)
```

### Dynamic Delayed Loading

For very large collections:

```python
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    # Returns Query object for lazy evaluation
    posts = relationship(
        "Post",
        lazy="dynamic",
        backref="author"
    )

# Usage - must use query methods
user = session.get(User, 1)
post_count = user.posts.count()
first_post = user.posts.first()
recent_posts = user.posts.order_by(Post.created_at.desc()).limit(10).all()
```

## Extension Best Practices

### 1. Use Association Proxy for Simple Collections

```python
# Good - clean API
class Post(Base):
    tag_names = association_proxy("post_tags", "tag_name")

post.tag_names = ["python", "sql"]  # Simple list of strings

# Instead of:
post.post_tags = [
    PostTag(tag=Tag(name="python")),
    PostTag(tag=Tag(name="sql"))
]
```

### 2. Use Automap for Legacy Databases

```python
# Good - quick integration with existing schema
Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users  # Auto-mapped

# Then create new models normally for new features
class Profile(Base):
    __tablename__ = "profiles"  # New table
    # ... define columns
```

### 3. Use Mutable for Complex Types

```python
# Good - automatic change tracking
from sqlalchemy.ext.mutable import MutableDict

class User(Base):
    settings = Column(MutableDict.as_mutable(JSON))

user.settings["theme"] = "dark"  # Automatically tracked
session.commit()  # Only changed settings updated
```

### 4. Use Dynamic for Large Collections

```python
# Good - efficient for thousands of items
class User(Base):
    logs = relationship("Log", lazy="dynamic")

# Query only what you need
recent_logs = user.logs.order_by(Log.timestamp.desc()).limit(100).all()
error_logs = user.logs.filter(Log.level == "ERROR").all()
```

## Troubleshooting Extensions

### Association Proxy Not Working

```python
# Problem: Missing creator function
tag_names = association_proxy("post_tags", "tag")  # Can't create!

# Solution: Add creator
tag_names = association_proxy(
    "post_tags",
    "tag",
    creator=lambda tag_name: PostTag(tag=Tag(name=tag_name))
)
```

### Automap Relationships Not Detected

```python
# Problem: Foreign key not properly defined in database

# Solution: Define relationship manually
Base.prepare(
    engine,
    reflect=True,
    classes={
        'users': type('User', (Base.classes.users,), {
            'posts': relationship('Post')
        })
    }
)
```

### Mutable Not Tracking Changes

```python
# Problem: Replacing entire object instead of modifying
user.preferences = {"theme": "dark"}  # Not tracked!

# Solution: Modify in place
user.preferences["theme"] = "dark"  # Tracked
```

## Next Steps

- [Core SQL Expressions](12-core-sql-expressions.md) - Advanced expression building
- [Dialects](16-dialects-overview.md) - Database-specific features
- [Best Practices](24-best-practices.md) - Performance optimization
- [Migration Guide](21-migration-2-0.md) - Upgrading from SQLAlchemy 1.x
