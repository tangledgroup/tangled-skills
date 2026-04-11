# ORM Session Management

## Session Basics

### Creating a Session

```python
from sqlalchemy.orm import sessionmaker, Session

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,  # Use new Session API in 2.0
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# Create session instance
session = SessionLocal()

# Use with context manager (recommended)
with SessionLocal() as session:
    # Session automatically closes on exit
    user = User(username="alice")
    session.add(user)
    session.commit()
```

### Session Factory Options

```python
SessionLocal = sessionmaker(
    bind=engine,                    # Database engine
    class_=Session,                 # Session class to use
    autoflush=True,                 # Flush before operations (default: True)
    autocommit=False,               # Auto-commit after each statement (default: False)
    expire_on_commit=True,          # Expire attributes after commit (default: True)
    bindkey="main",                 # For multiple bindings
    info={"connection_string": url} # Custom metadata
)
```

## Adding Objects

### Single Object

```python
# Create and add
user = User(username="alice", email="alice@example.com")
session.add(user)
session.commit()

# Get generated ID
print(user.id)  # Available after flush/commit
```

### Multiple Objects

```python
# Add multiple individually
user1 = User(username="alice")
user2 = User(username="bob")
session.add_all([user1, user2])
session.commit()

# Or add one by one
session.add(user1)
session.add(user2)
session.commit()
```

### Bulk Insert (No Identity Flush)

```python
# Fast bulk insert without individual object tracking
users_data = [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
]

session.bulk_insert_mappings(User, users_data)
session.commit()

# Note: Objects are not in session, no identity map
```

## Querying Objects

### Basic Queries

```python
from sqlalchemy import select

# Get all users
users = session.execute(select(User)).scalars().all()

# Filter by condition
user = session.execute(
    select(User).where(User.username == "alice")
).scalar_one_or_none()

# Get first match
user = session.execute(
    select(User).where(User.age >= 18)
).scalars().first()

# Count
count = session.execute(
    select(func.count(User.id))
).scalar()
```

### Query with Specific Columns

```python
# Select specific attributes
result = session.execute(
    select(User.id, User.username).where(User.active == True)
)
for user_id, username in result:
    print(user_id, username)
```

### Eager Loading

See [ORM Querying](09-orm-querying.md) for detailed eager loading patterns.

## Updating Objects

### Modify and Commit

```python
# Get object
user = session.execute(
    select(User).where(User.username == "alice")
).scalar_one()

# Modify attributes
user.email = "newemail@example.com"
user.last_login = datetime.utcnow()

# Commit changes
session.commit()
```

### Bulk Update

```python
from sqlalchemy import update

# Update multiple rows at once
stmt = (
    update(User)
    .where(User.age >= 18)
    .values(status="adult")
)

result = session.execute(stmt)
print(f"Updated {result.rowcount} rows")
session.commit()
```

### Programmatic Updates

```python
# Update with dictionary
user_dict = {"email": "new@example.com", "status": "active"}
session.query(User).filter_by(id=1).update(user_dict)
session.commit()
```

## Deleting Objects

### Single Object

```python
# Get and delete
user = session.execute(
    select(User).where(User.username == "alice")
).scalar_one()

session.delete(user)
session.commit()
```

### Bulk Delete

```python
from sqlalchemy import delete

# Delete matching rows
stmt = delete(User).where(User.is_active == False)
result = session.execute(stmt)
print(f"Deleted {result.rowcount} users")
session.commit()
```

### Cascade Deletes

```python
# If cascade="delete-orphan" is set on relationship
# Deleting parent deletes children automatically

user = session.get(User, 1)
session.delete(user)  # Also deletes all user.posts if configured
session.commit()
```

## Transaction Management

### Context Manager (Recommended)

```python
with SessionLocal() as session:
    try:
        user = User(username="alice")
        session.add(user)
        
        post = Post(title="Hello", author_id=user.id)
        session.add(post)
        
        session.commit()  # Commits automatically on successful exit
    except Exception:
        session.rollback()  # Automatic rollback on exception
        raise
```

### Manual Transaction Control

```python
session = SessionLocal()
try:
    user = User(username="alice")
    session.add(user)
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()
```

### Nested Transactions (Savepoints)

```python
with SessionLocal() as session:
    with session.begin_nested():  # Creates savepoint
        user = User(username="alice")
        session.add(user)
        
        try:
            # If this fails, only inner transaction rolls back
            risky_operation()
        except Exception:
            session.rollback()  # Rollback to savepoint
            raise
    
    # Outer transaction can still commit
    session.commit()
```

### Two-Phase Commits

```python
with SessionLocal() as session:
    with session.begin_twophase():
        user = User(username="alice")
        session.add(user)
        # prepare() called automatically
        # commit() completes two-phase commit
```

## Session State Management

### Object States

SQLAlchemy tracks object state:

- **Transient**: Not associated with session, no primary key
- **Pending**: Added to session, not yet flushed
- **Persistent**: In database, associated with session
- **Detached**: Was persistent, but not associated with session
- **Deleted**: Marked for deletion, will be deleted on commit

```python
from sqlalchemy.orm import obj_state, object_session

user = User(username="alice")  # Transient
print(obj_state(user).transient)  # True

session.add(user)  # Pending
print(obj_state(user).pending)  # True

session.flush()  # Persistent
print(obj_state(user).persistent)  # True

session.expunge(user)  # Detached
print(obj_state(user).detached)  # True
```

### Expire and Refresh

```python
# Expire object attributes (reload on access)
session.expire(user)
print(user.username)  # Triggers reload from database

# Refresh specific object
session.refresh(user)  # Reload all attributes

# Refresh specific attributes
session.refresh(user, ["username", "email"])

# Expire on commit
SessionLocal = sessionmaker(expire_on_commit=True)  # Default
```

### Detach and Reattach

```python
# Detach from session
session.expunge(user)

# Detach all objects
session.expunge_all()

# Reattach detached object (make persistent)
session.add(user)  # Adds as pending

# Merge detached object (returns copy in session)
merged_user = session.merge(user)
```

## Session Identity Map

### Identity Map Behavior

```python
# Same object returned for same primary key
user1 = session.get(User, 1)
user2 = session.get(User, 1)

print(user1 is user2)  # True - same instance

# Query also returns same instance
user3 = session.execute(select(User).where(User.id == 1)).scalar_one()
print(user1 is user3)  # True
```

### Clearing Identity Map

```python
# Remove specific object from identity map
session.expunge(user)

# Clear entire identity map
session.clear()

# Clear on commit (optional)
SessionLocal = sessionmaker(expire_on_commit=True)
```

## Advanced Session Patterns

### Session Binding

```python
# Bind engine at creation
SessionLocal = sessionmaker(bind=engine)

# Bind later
session = SessionLocal()
session.bind = engine

# Multiple bindings
class User(Base):
    __bind_key__ = "users_db"

class Post(Base):
    __bind_key__ = "posts_db"

SessionLocal = sessionmaker(
    binds={
        User: users_engine,
        Post: posts_engine,
    }
)
```

### Scoped Sessions (Thread-Local)

```python
from sqlalchemy.orm import scoped_session, sessionmaker

# Thread-local session factory
ScopedSession = scoped_session(sessionmaker(bind=engine))

# Get session for current thread
session = ScopedSession()

# Use session
user = User(username="alice")
session.add(user)
session.commit()

# Remove when done
ScopedSession.remove()
```

### Session Events

```python
from sqlalchemy.orm import events

@events.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    print(f"About to flush {len(instances)} instances")

@events.listens_for(Session, "after_flush")
def after_flush(session, flush_context):
    print("Flush completed")

@events.listens_for(Session, "before_commit")
def before_commit(session):
    print("About to commit")

@events.listens_for(Session, "after_commit")
def after_commit(session):
    print("Commit successful")
```

## Async Session

### Creating Async Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Using Async Session

```python
import asyncio

async def create_user():
    async with AsyncSessionLocal() as session:
        user = User(username="alice")
        session.add(user)
        await session.commit()
        
        # Query
        result = await session.execute(
            select(User).where(User.username == "alice")
        )
        user = result.scalar_one()
        return user

# Run async function
user = asyncio.run(create_user())
```

### Async Transaction Management

```python
async def transfer_funds():
    async with AsyncSessionLocal() as session:
        try:
            # Start transaction
            async with session.begin():
                sender = await session.get(User, 1)
                receiver = await session.get(User, 2)
                
                sender.balance -= 100
                receiver.balance += 100
                
                # Auto-commits on successful exit
        except Exception:
            # Automatic rollback
            raise
```

## Session Performance

### Optimize Flush Behavior

```python
# Disable autoflush for bulk operations
session.autoflush = False

try:
    # Add many objects without flushing
    for i in range(1000):
        session.add(User(username=f"user{i}"))
    
    # Single flush at end
    session.flush()
    session.commit()
finally:
    session.autoflush = True
```

### Batch Commits

```python
# Commit in batches for large imports
batch_size = 1000
for i, user_data in enumerate(users_data):
    user = User(**user_data)
    session.add(user)
    
    if i % batch_size == 0:
        session.commit()
        print(f"Committed {i} users")

session.commit()  # Final commit
```

### No-Emit Loaders

```python
# Don't load relationships for bulk queries
from sqlalchemy.orm import selectinload

users = session.execute(
    select(User).options(noload(User.posts))
).scalars().all()
```

## Common Patterns

### Get or Create

```python
def get_or_create_user(session, username):
    user = session.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    
    if not user:
        user = User(username=username)
        session.add(user)
        session.flush()  # Get ID without committing
    
    return user
```

### Upsert Pattern

```python
from sqlalchemy import insert

stmt = (
    insert(User)
    .values(username="alice", email="alice@example.com")
    .on_conflict_do_update(
        index_elements=[User.username],
        set_=dict(email="alice@example.com", updated_at=func.now())
    )
)

session.execute(stmt)
session.commit()
```

### Unit of Work Pattern

```python
def process_order(session, order_data):
    """Single transaction for entire order processing"""
    with session.begin():  # Auto-commits or rollbacks
        order = Order(**order_data)
        session.add(order)
        
        for item in order_data["items"]:
            order_item = OrderItem(order=order, **item)
            session.add(order_item)
        
        # All or nothing - rollback on any error
        return order
```

## Troubleshooting

### Detached Instance Error

```python
# Problem: Object not in session
session.expunge(user)
user.username = "new"  # Won't be tracked

# Solution: Reattach object
session.add(user)  # Or use merge
session.merge(user)
```

### FlushError

```python
# Problem: Constraint violation during flush

# Solution: Catch and handle
try:
    session.flush()
except IntegrityError as e:
    session.rollback()
    print(f"Data integrity error: {e.orig}")
```

### Session Not Committed

```python
# Problem: Changes not visible to other connections

# Solution: Commit or flush
session.commit()  # Commit and keep objects bound
# or
session.flush()   # Sync to DB but keep transaction open
```

## Best Practices

1. **Use context managers** for automatic session cleanup
2. **Keep transactions short** to reduce lock contention
3. **Use `begin()`** for explicit transaction boundaries
4. **Set `expire_on_commit=False`** for read-heavy applications
5. **Batch large operations** to avoid memory issues
6. **Use async sessions** for I/O-bound applications
7. **Handle exceptions** with proper rollback
8. **Close sessions** in finally blocks or use context managers

## Next Steps

- [ORM Relationships](08-orm-relationships.md) - Advanced relationship patterns
- [ORM Querying](09-orm-querying.md) - Query strategies and eager loading
- [AsyncIO Support](07-orm-asyncio.md) - Complete async patterns
- [Best Practices](24-best-practices.md) - Performance optimization
