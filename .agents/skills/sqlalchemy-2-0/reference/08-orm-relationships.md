# ORM Relationships

## Relationship Fundamentals

### Basic One-to-Many

```python
from sqlalchemy.orm import relationship

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
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # Many posts belong to one user
    author = relationship("User", back_populates="posts")
```

**Usage:**
```python
# Create parent with children
user = User(username="alice")
post1 = Post(title="First Post", author=user)
post2 = Post(title="Second Post", author=user)

session.add(user)  # Posts automatically added via cascade
session.commit()

# Access relationship
print(user.posts)  # [Post, Post]
print(post1.author)  # User
```

### Many-to-Many Relationships

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
    username = Column(String(50))
    
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )
```

**Usage:**
```python
# Create and link
user = User(username="alice")
admin_role = Role(name="admin")
editor_role = Role(name="editor")

user.roles = [admin_role, editor_role]

session.add_all([user, admin_role, editor_role])
session.commit()

# Access relationships
print(user.roles)  # [Role, Role]
print(admin_role.users)  # [User, ...]
```

### One-to-One Relationships

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    
    # One user has one profile
    profile = relationship("UserProfile", uselist=False, back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text)
    
    # One profile belongs to one user
    user = relationship("User", uselist=False, back_populates="profile")
```

**Key:** `uselist=False` indicates single object, not collection.

## Relationship Configuration Options

### Cascade Options

Cascade controls how operations propagate to related objects:

```python
# Common cascade patterns
posts = relationship(
    "Post",
    cascade="all, delete-orphan",  # Full cascade
    back_populates="author"
)

# Individual cascade options:
# - "merge": merge() propagates
# - "expunge": expunge() propagates
# - "delete": delete() propagates
# - "save-update": add/flush propagates
# - "refresh-expire": refresh/expire propagates
# - "all": all of the above

# "delete-orphan": delete when removed from parent
posts = relationship(
    "Post",
    cascade="all, delete-orphan",
    back_populates="author"
)

# Usage:
user = session.get(User, 1)
del user.posts[0]  # Post marked for deletion
session.commit()   # Post deleted from database
```

### Lazy Loading Strategies

Control when relationships are loaded:

```python
from sqlalchemy.orm import lazyload

# "select" (default): Separate query on access
posts = relationship("Post", lazy="select")

# "joined": JOIN with parent query
posts = relationship("Post", lazy="joined")

# "subquery": Single IN subquery
posts = relationship("Post", lazy="subquery")

# "raiseload": Raise error if not loaded
posts = relationship("Post", lazy="raise")

# "dynamic": Return Query object (for large collections)
posts = relationship("Post", lazy="dynamic")

# "noload": Never load automatically
posts = relationship("Post", lazy="noload")
```

### Order By

Pre-order relationship results:

```python
# Order posts by creation date (newest first)
posts = relationship(
    "Post",
    order_by=Post.created_at.desc(),
    back_populates="author"
)

# Multiple columns
posts = relationship(
    "Post",
    order_by=[Post.created_at.desc(), Post.id.desc()],
    back_populates="author"
)
```

### Collection Classes

Use custom collection types:

```python
from sqlalchemy.orm import collection_class

# Use list (default)
posts = relationship("Post")  # Returns list

# Use set
tags = relationship(
    "Tag",
    secondary=post_tags,
    collection_class=set
)

# Use ordered dict
ordered_posts = relationship(
    "Post",
    collection_class=lambda: OrderedDict()
)

# Custom collection class
class PostCollection(list):
    def active(self):
        return [p for p in self if p.is_active]

posts = relationship(
    "Post",
    collection_class=PostCollection
)
```

### Primary and Secondary Join

Customize join conditions:

```python
# Custom primary join
active_posts = relationship(
    "Post",
    primaryjoin="and_(User.id == Post.author_id, Post.is_active == True)",
    backref="active_author"
)

# Many-to-many with custom joins
roles = relationship(
    "Role",
    secondary=user_roles,
    primaryjoin="User.id == user_roles.c.user_id",
    secondaryjoin="Role.id == user_roles.c.role_id",
    back_populates="users"
)

# Filter association table
active_roles = relationship(
    "Role",
    secondary=user_roles,
    primaryjoin="User.id == user_roles.c.user_id",
    secondaryjoin="and_(Role.id == user_roles.c.role_id, user_roles.c.active == True)",
    back_populates="active_users"
)
```

## Relationship Loading Strategies

### Eager Loading with Select

```python
from sqlalchemy.orm import selectinload, joinedload, subqueryload

# selectinload: Efficient IN query for relationships
stmt = (
    select(User)
    .options(selectinload(User.posts))
)

users = session.execute(stmt).scalars().all()
# Executes: SELECT user, then SELECT posts WHERE author_id IN (...)

# joinedload: JOIN with parent
stmt = (
    select(User)
    .options(joinedload(User.posts))
)

# subqueryload: Similar to selectinload but uses correlated subquery
stmt = (
    select(User)
    .options(subqueryload(User.posts))
)
```

### Loading Multiple Relationships

```python
from sqlalchemy.orm import selectinload, joinedload

# Load posts and their comments
stmt = (
    select(User)
    .options(
        selectinload(User.posts).selectinload(Post.comments),
        joinedload(User.profile)
    )
)

users = session.execute(stmt).scalars().all()

# Load with conditions
stmt = (
    select(User)
    .options(
        selectinload(User.posts).where(Post.is_published == True)
    )
)

# Load with ordering and limit
stmt = (
    select(User)
    .options(
        selectinload(User.posts)
        .order_by(Post.created_at.desc())
        .limit(5)
    )
)
```

### Deferred Loading

Load specific columns on demand:

```python
from sqlalchemy import deferred

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    # Large field loaded only when accessed
    biography = Column(Text, deferred=True)
    stats = Column(JSON, deferred=True)

# Load deferred columns explicitly
user = session.get(User, 1)
print(user.username)  # Fast - already loaded
print(user.biography)  # Triggers additional query

# Load specific deferred columns
from sqlalchemy import with_loader_criteria

stmt = (
    select(User)
    .options(load_only(User.id, User.username, User.biography))
)
```

## Self-Referential Relationships

### Parent-Child Hierarchy

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    
    # Self-referential: employee has a manager
    manager = relationship(
        "Employee",
        remote_side="Employee.id",
        backref="subordinates"
    )

# Usage
ceo = Employee(name="CEO")
manager = Employee(name="Manager", manager=ceo)
employee = Employee(name="Employee", manager=manager)

session.add_all([ceo, manager, employee])
session.commit()

print(ceo.subordinates)  # [manager]
print(employee.manager)  # ceo -> manager
```

### Many-to-Many Self-Reference

```python
# Peer relationships (e.g., friends)
friendships = Table(
    "friendships", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("friend_id", Integer, ForeignKey("users.id"))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    
    friends = relationship(
        "User",
        secondary=friendships,
        primaryjoin="User.id == friendships.c.user_id",
        secondaryjoin="User.id == friendships.c.friend_id",
        back_populates="friend_of"
    )
    
    friend_of = relationship(
        "User",
        secondary=friendships,
        primaryjoin="User.id == friendships.c.friend_id",
        secondaryjoin="User.id == friendships.c.user_id",
        back_populates="friends"
    )
```

## Association Objects

### Pattern for Extra Data

When you need to store data on the relationship itself:

```python
class UserPostAssociation(Base):
    __tablename__ = "user_posts"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    role = Column(String(50))  # Extra data: 'author', 'editor', etc.
    assigned_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    post_associations = relationship(
        "UserPostAssociation",
        back_populates="user"
    )
    
    # Convenience property for posts
    @property
    def posts(self):
        return [pa.post for pa in self.post_associations]

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    
    post_associations = relationship(
        "UserPostAssociation",
        back_populates="post"
    )

class UserPostAssociation(Base):
    # ... as above
    
    user = relationship("User", back_populates="post_associations")
    post = relationship("Post", back_populates="post_associations")
```

## Dynamic Relationships

### Query-Returning Relationships

For large collections, use `lazy="dynamic"`:

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    # Returns Query object instead of list
    posts = relationship(
        "Post",
        lazy="dynamic",
        backref="author"
    )

# Usage
user = session.get(User, 1)

# Must use query methods
post_count = user.posts.count()
first_post = user.posts.first()
recent_posts = user.posts.order_by(Post.created_at.desc()).limit(10).all()

# Can chain query methods
active_posts = user.posts.filter(Post.is_active == True).all()
```

## Backref vs back_populates

### Using backref (Auto-Create)

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", backref="author")

# SQLAlchemy automatically creates Post.author relationship
# Equivalent to:
# class Post(Base):
#     author = relationship("User", back_populates="posts")
```

### Using back_populates (Explicit)

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

# Both sides explicitly defined - recommended for clarity
```

### When to Use Each

- **backref**: Quick prototyping, simple relationships
- **back_populates**: Production code, complex configurations, clarity

## Relationship Best Practices

### 1. Choose Appropriate Cascade

```python
# Delete posts when user is deleted
posts = relationship("Post", cascade="all, delete-orphan")

# Don't cascade delete for many-to-many
roles = relationship("Role", secondary=user_roles)  # No cascade
```

### 2. Use Eager Loading Strategically

```python
# Avoid N+1 queries
stmt = select(User).options(selectinload(User.posts))

# But don't over-eager load
# Bad: Load everything always
# Good: Load what you need per query
```

### 3. Set Appropriate Lazy Strategy

```python
# Small collections: joinedload or selectinload
posts = relationship("Post", lazy="selectin")

# Large collections: dynamic
comments = relationship("Comment", lazy="dynamic")

# Optional relationships: default lazy is fine
profile = relationship("UserProfile", uselist=False)
```

### 4. Use Foreign Keys Explicitly

```python
# Good - explicit foreign key
author_id = Column(Integer, ForeignKey("users.id"))
author = relationship("User")

# Avoid - implicit foreign key inference
author = relationship("User")  # SQLAlchemy guesses
```

## Troubleshooting

### Greenlet Error in Relationships

```python
# Ensure greenlet is installed for async
pip install greenlet
```

### Relationship Not Loading

```python
# Check back_populates match
class User(Base):
    posts = relationship("Post", back_populates="author")  # Must match

class Post(Base):
    author = relationship("User", back_populates="posts")  # Must match
```

### Circular Import Issues

```python
# Use string references for forward declarations
posts = relationship("Post", back_populates="author")  # String, not Post
```

## Next Steps

- [ORM Querying](09-orm-querying.md) - Query patterns with relationships
- [Hybrid Attributes](10-orm-hybrid-attributes.md) - Property expressions
- [Extensions](11-orm-extensions.md) - Association proxy and more
- [Best Practices](24-best-practices.md) - Performance optimization
