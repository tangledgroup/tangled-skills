# Core Events and Instrumentation

## Introduction to Events

SQLAlchemy's event system allows you to hook into various operations throughout the library lifecycle, enabling custom behavior, logging, validation, and instrumentation.

```python
from sqlalchemy import event, Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(f"Executing: {statement}")
```

## Engine Events

### Connection Events

```python
from sqlalchemy import event, create_engine

# Called before a connection is created
@event.listens_for(create_engine("postgresql://..."), "connect")
def receive_connect(dbapi_connection, connection_record):
    print(f"New connection created: {dbapi_connection}")
    # Configure connection (set session variables, etc.)
    cursor = dbapi_connection.cursor()
    cursor.execute("SET timezone = 'UTC'")
    cursor.close()

# Called when connection is returned to pool
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    print(f"Connection checked out: {dbapi_connection}")

# Called when connection is returned to pool
@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    print(f"Connection returned to pool: {dbapi_connection}")

# Called when connection is invalidated
@event.listens_for(engine, "invalidation")
def receive_invalidation(dbapi_connection, connection_record, exception):
    print(f"Connection invalidated: {exception}")
```

### Execution Events

```python
from sqlalchemy import event

# Before SQL execution
@event.listens_for(engine, "before_cursor_execute")
def before_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"Before execute: {statement[:100]}...")
    # Log query, add timing, etc.

# After SQL execution
@event.listens_for(engine, "after_cursor_execute")
def after_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"After execute: {cursor.rowcount} rows affected")
    
# Before reflection
@event.listens_for(engine, "before_reflect")
def before_reflection(inspector, table, include_indexes, **kw):
    print(f"Reflecting table: {table.name if table else 'all'}")

# After reflection
@event.listens_for(engine, "after_reflect")
def after_reflection(inspector, table, **kw):
    print(f"Finished reflecting: {table.name if table else 'all'}")
```

### DDL Events

```python
from sqlalchemy import event, DDL

# Table creation
@event.listens_for(Table, "after_create")
def after_table_create(target, connection, **kw):
    print(f"Table created: {target.name}")
    
    # Execute additional DDL
    if target.name == "users":
        connection.execute(
            DDL("CREATE INDEX idx_users_email ON users (email)")
        )

# Table drop
@event.listens_for(Table, "before_drop")
def before_table_drop(target, connection, **kw):
    print(f"About to drop table: {target.name}")

# Metadata-level events
@event.listens_for(MetaData, "after_create")
def after_metadata_create(target, connection, **kw):
    print("All tables created")
    
    # Create indexes that depend on multiple tables
    connection.execute(DDL("CREATE INDEX ..."))

@event.listens_for(MetaData, "before_drop")
def before_metadata_drop(target, connection, **kw):
    print("About to drop all tables")
```

## Session Events

### Flush Events

```python
from sqlalchemy.orm import Session, events

# Before flush starts
@events.listens_for(Session, "before_flush")
def receive_before_flush(session, flush_context, instances):
    print(f"Before flush: {len(instances)} instances to flush")
    
    # Validate instances before flushing
    for instance in instances:
        if hasattr(instance, 'validate'):
            instance.validate()

# After flush completes
@events.listens_for(Session, "after_flush")
def receive_after_flush(session, flush_context):
    print("Flush completed successfully")

# After flush starts (before individual operations)
@events.listens_for(Session, "after_flush_start")
def receive_after_flush_start(session, flush_context):
    print("Starting flush operations")

# Before commit
@events.listens_for(Session, "before_commit")
def receive_before_commit(session):
    print("About to commit transaction")
    
    # Add timestamps before commit
    for instance in session.new | session.dirty:
        if hasattr(instance, 'updated_at'):
            instance.updated_at = datetime.utcnow()

# After commit
@events.listens_for(Session, "after_commit")
def receive_after_commit(session):
    print("Transaction committed successfully")

# After rollback
@events.listens_for(Session, "after_rollback")
def receive_after_rollback(session):
    print("Transaction rolled back")
```

### Instance Events

```python
from sqlalchemy.orm import events

# Before insert
@events.listens_for(User, "before_insert")
def receive_before_insert(mapper, connection, target):
    print(f"About to insert user: {target.username}")
    
    # Auto-set values
    if not target.id:
        target.id = generate_uuid()

# After insert
@events.listens_for(User, "after_insert")
def receive_after_insert(mapper, connection, target):
    print(f"User inserted with ID: {target.id}")

# Before update
@events.listens_for(User, "before_update")
def receive_before_update(mapper, connection, target):
    print(f"About to update user: {target.username}")
    
    # Track changes
    target.updated_at = datetime.utcnow()

# After update
@events.listens_for(User, "after_update")
def receive_after_update(mapper, connection, target):
    print(f"User updated: {target.username}")

# Before delete
@events.listens_for(User, "before_delete")
def receive_before_delete(mapper, connection, target):
    print(f"About to delete user: {target.username}")
    
    # Soft delete instead
    target.is_deleted = True
    target.deleted_at = datetime.utcnow()
    raise FlushError("Converted to soft delete")  # Stop hard delete

# After delete
@events.listens_for(User, "after_delete")
def receive_after_delete(mapper, connection, target):
    print(f"User deleted: {target.username}")
```

### Load Events

```python
from sqlalchemy.orm import events

# Before loader executes query
@events.listens_for(Session, "before_get")
def receive_before_get(session, key, identity_key, **kw):
    print(f"About to load: {identity_key}")

# After object loaded
@events.listens_for(User, "load")
def receive_load(context):
    user = context.instance
    print(f"User loaded: {user.username}")
    
    # Post-load processing
    if hasattr(user, 'process_after_load'):
        user.process_after_load()

# After refresh
@events.listens_for(User, "refresh")
def receive_refresh(context):
    user = context.instance
    print(f"User refreshed: {user.username}")
```

## Mapper Events

### Configuration Events

```python
from sqlalchemy.orm import events

# When mapper is configured
@events.listens_for(User, "config")
def receive_config(mapper, class_):
    print(f"Mapper configured for: {class_.__name__}")

# Before mapper is set up
@events.listens_for(User, "before_configure")
def receive_before_configure():
    print("About to configure all mappers")

# After all mappers configured
@events.listens_for("configure", "after_configured")
def receive_after_configured():
    print("All mappers configured")
```

### Collection Events

```python
from sqlalchemy.orm import events

# When relationship collection is assigned
@events.listens_for(User.posts, "collection_append")
def receive_append(target, value, initiator):
    print(f"Post added to user {target.username}: {value.title}")

@events.listens_for(User.posts, "collection_remove")
def receive_remove(target, value, initiator):
    print(f"Post removed from user {target.username}: {value.title}")

@events.listens_for(User.posts, "collection_set")
def receive_set(target, value, initiator):
    print(f"Posts collection set for user {target.username}")
```

## Pool Events

### Connection Pool Monitoring

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool

# When new connection created
@event.listens_for(Pool, "connect")
def log_connect(dbapi_connection, connection_record):
    print(f"Pool: New connection created")
    
    # Track connection creation time
    connection_record.info['created_at'] = datetime.utcnow()

# When connection checked out
@event.listens_for(Pool, "checkout")
def log_checkout(dbapi_connection, connection_record, connection_proxy):
    print(f"Pool: Connection checked out")
    
    # Track usage
    if 'checkout_count' not in connection_record.info:
        connection_record.info['checkout_count'] = 0
    connection_record.info['checkout_count'] += 1

# When connection returned to pool
@event.listens_for(Pool, "checkin")
def log_checkin(dbapi_connection, connection_record):
    print(f"Pool: Connection returned")
    
    # Validate connection before returning
    try:
        dbapi_connection.cursor().execute("SELECT 1")
    except:
        # Connection invalid, will be discarded
        pass

# When connection invalidated
@event.listens_for(Pool, "invalidate")
def log_invalidate(dbapi_connection, connection_record, exception):
    print(f"Pool: Connection invalidated due to: {exception}")

# When pool is cleared
@event.listens_for(Pool, "clear")
def log_clear(pool, connection_record):
    print(f"Pool: Pool being cleared")
```

## Instrumentation for Debugging

### Query Logging

```python
from sqlalchemy import event
import logging
import time

logging.basicConfig()
logger = logging.getLogger("sqlalchemy.query")
logger.setLevel(logging.INFO)

@event.listens_for(Engine, "before_cursor_execute")
def log_queries(conn, cursor, statement, parameters, context, executemany):
    start = time.time()
    
    # Store start time on connection for after event
    conn.info.setdefault('query_start', {})
    conn.info['query_start'][id(cursor)] = (start, statement)

@event.listens_for(Engine, "after_cursor_execute")
def log_query_timing(conn, cursor, statement, parameters, context, executemany):
    if id(cursor) in conn.info.get('query_start', {}):
        start, original_stmt = conn.info['query_start'].pop(id(cursor))
        duration = (time.time() - start) * 1000  # ms
        
        if duration > 100:  # Log slow queries (>100ms)
            logger.warning(
                f"Slow query ({duration:.2f}ms): {statement[:200]}..."
            )
```

### Performance Monitoring

```python
from sqlalchemy import event
from collections import defaultdict
import statistics

query_stats = defaultdict(list)

@event.listens_for(Engine, "before_cursor_execute")
def track_query_start(conn, cursor, statement, parameters, context, executemany):
    conn.info['query_start_time'] = time.time()
    conn.info['query_statement'] = statement

@event.listens_for(Engine, "after_cursor_execute")
def track_query_end(conn, cursor, statement, parameters, context, executemany):
    if 'query_start_time' in conn.info:
        duration = (time.time() - conn.info['query_start_time']) * 1000
        stmt_type = statement.split()[0].upper()
        
        query_stats[stmt_type].append(duration)
        
        # Print stats periodically
        if len(query_stats[stmt_type]) % 100 == 0:
            durations = query_stats[stmt_type]
            print(f"{stmt_type}: "
                  f"avg={statistics.mean(durations):.2f}ms, "
                  f"max={max(durations):.2f}ms, "
                  f"min={min(durations):.2f}ms")
```

### Validation Hooks

```python
from sqlalchemy.orm import events
from sqlalchemy.exc import FlushError

@events.listens_for(User, "before_insert")
def validate_user_before_insert(mapper, connection, target):
    """Validate user before inserting"""
    errors = []
    
    if not target.username or len(target.username) < 3:
        errors.append("Username must be at least 3 characters")
    
    if not target.email or "@" not in target.email:
        errors.append("Invalid email address")
    
    if target.age and (target.age < 0 or target.age > 150):
        errors.append("Invalid age")
    
    if errors:
        raise FlushError(f"Validation failed: {'; '.join(errors)}")

@events.listens_for(Order, "before_insert")
def validate_order_total(mapper, connection, target):
    """Ensure order total matches items"""
    calculated_total = sum(item.total for item in target.items)
    
    if abs(target.total - calculated_total) > 0.01:
        raise FlushError(
            f"Order total mismatch: {target.total} vs {calculated_total}"
        )
```

## Best Practices

### 1. Use Events Sparingly

```python
# Good - specific, targeted event usage
@event.listens_for(User, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.utcnow()

# Avoid - too many events creating overhead
# Don't add logging/validation to every operation unless needed
```

### 2. Remove Event Listeners When Done

```python
from sqlalchemy import event

def setup_listeners(engine):
    @event.listens_for(engine, "before_cursor_execute")
    def debug_log(conn, cursor, statement, parameters, context, executemany):
        print(f"DEBUG: {statement}")
    
    return debug_log

# Later, remove the listener
debug_func = setup_listeners(engine)
event.remove(engine, "before_cursor_execute", debug_func)
```

### 3. Handle Exceptions Carefully

```python
@event.listens_for(Session, "before_flush")
def safe_validation(session, flush_context, instances):
    try:
        for instance in instances:
            validate_instance(instance)
    except Exception as e:
        # Log but don't break normal operation
        logger.error(f"Validation warning: {e}")
        # Don't raise - let flush continue
```

### 4. Use Events for Cross-Cutting Concerns

```python
# Good use case: auditing
@events.listens_for(User, "before_update")
def audit_user_changes(mapper, connection, target):
    if target.pk_set():
        # Get old state
        old_state = session.query(User).get(target.id)
        
        # Log changes
        audit_log(
            entity="User",
            entity_id=target.id,
            old_values=old_state.to_dict(),
            new_values=target.to_dict()
        )
```

## Next Steps

- [Custom Types](15-core-custom-types.md) - Type-level events
- [Best Practices](24-best-practices.md) - Event performance considerations
- [Dialects](16-dialects-overview.md) - Dialect-specific events
- [Troubleshooting](23-troubleshooting-faq.md) - Debugging event issues
