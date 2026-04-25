# Schema Migrations

Comprehensive guide to managing RediSearch index schema changes using SchemaMigrator, migration files, and the `om` CLI in Redis OM Python v1.1.0.

## Overview

Redis OM provides two approaches for schema management:

1. **Migrator (legacy):** Automatic index creation from model definitions
2. **SchemaMigrator (recommended):** File-based migrations with version tracking and rollback support

## Basic Migration (Migrator)

The simplest approach for automatic index creation:

```python
from aredis_om import Migrator, HashModel, Field

class User(HashModel):
    username: str = Field(index=True)
    email: str = Field(index=True)
    age: int = Field(index=True, sortable=True)

# Create indexes for all models
async def startup():
    await Migrator().run()

# With custom connection
from aredis_om import get_redis_connection
redis_client = get_redis_connection()
await Migrator(conn=redis_client).run()

# Check if Redis modules are available
from aredis_om import has_redis_json, has_redisearch

if not has_redisearch():
    raise RuntimeError("RediSearch module not available")
if not has_redis_json():
    print("Warning: RedisJSON not available, using HashModel only")
```

### Migrator Options

```python
# Dry run (show what would be created)
await Migrator().run(dry_run=True)

# Verbose output
await Migrator().run(verbose=True)

# Custom key prefix
await Migrator(
    conn=redis_client,
    key_prefix="myapp:v2"
).run()
```

## SchemaMigrator (File-Based Migrations)

For production applications requiring version control and rollback capabilities.

### Creating Migration Files

Migration files are Python modules in a `schema-migrations` directory:

```
migrations/
└── schema-migrations/
    ├── __init__.py
    ├── 001_initial_schema.py
    └── 002_add_user_index.py
```

### Basic Migration Structure

```python
# migrations/schema-migrations/001_initial_schema.py
from aredis_om import BaseSchemaMigration, HashModel, Field
import abc

class CreateUsersIndex001(BaseSchemaMigration):
    """Create initial user index with basic fields."""
    
    migration_id = "001_create_users_index"
    
    async def up(self):
        """Apply migration - create index and models."""
        
        class User(HashModel):
            username: str = Field(index=True)
            email: str = Field(index=True)
            age: int = Field(index=True, sortable=True)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "user"

        # Create the index
        await User.create_index()
    
    async def down(self):
        """Rollback migration - delete index."""
        
        class User(HashModel):
            username: str = Field(index=True)
            email: str = Field(index=True)
            age: int = Field(index=True, sortable=True)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "user"

        # Delete the index
        await User.drop_index(delete_documents=True)
```

### Migration File Naming

- Use numeric prefixes for ordering: `001_`, `002_`, `003_`
- Include descriptive names: `001_initial_schema.py`, `002_add_fields.py`
- Migration ID should match file stem or be explicitly defined

### Running Migrations

```python
from aredis_om import SchemaMigrator

# Create migrator instance
migrator = SchemaMigrator(
    migrations_dir="path/to/migrations/schema-migrations"
)

# Run all pending migrations
count = await migrator.run(verbose=True)
print(f"Applied {count} migrations")

# Dry run (show what would be applied)
count = await migrator.run(dry_run=True, verbose=True)

# Limit to N migrations
count = await migrator.run(limit=2, verbose=True)
```

### Checking Migration Status

```python
status = await migrator.status()

print(f"Total migrations: {status['total_migrations']}")
print(f"Applied: {status['applied_count']}")
print(f"Pending: {status['pending_count']}")
print(f"Applied IDs: {status['applied_migrations']}")
print(f"Pending IDs: {status['pending_migrations']}")

# Example output:
# {
#     "total_migrations": 5,
#     "applied_count": 3,
#     "pending_count": 2,
#     "applied_migrations": ["001_initial", "002_add_users", "003_add_products"],
#     "pending_migrations": ["004_add_indexes", "005_update_schema"]
# }
```

### Rolling Back Migrations

```python
# Rollback specific migration
success = await migrator.rollback(
    migration_id="003_add_products",
    verbose=True
)

# Dry run rollback
success = await migrator.rollback(
    migration_id="003_add_products",
    dry_run=True,
    verbose=True
)

# Rollback last N migrations
count = await migrator.downgrade(steps=2, verbose=True)
print(f"Rolled back {count} migrations")

# Dry run downgrade
count = await migrator.downgrade(steps=1, dry_run=True, verbose=True)
```

## Migration Examples

### Adding New Fields to Index

```python
# migrations/schema-migrations/002_add_email_index.py
from aredis_om import BaseSchemaMigration, HashModel, Field

class AddEmailIndex002(BaseSchemaMigration):
    """Add email field to user index."""
    
    migration_id = "002_add_email_index"
    
    async def up(self):
        # Drop existing index
        await User.drop_index(delete_documents=False)
        
        # Recreate with new schema
        class User(HashModel):
            username: str = Field(index=True)
            email: str = Field(index=True)  # New field
            age: int = Field(index=True, sortable=True)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "user"

        await User.create_index()
    
    async def down(self):
        # Revert to original schema
        await User.drop_index(delete_documents=False)
        
        class User(HashModel):
            username: str = Field(index=True)
            # email removed
            age: int = Field(index=True, sortable=True)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "user"

        await User.create_index()
```

### Creating New Model Index

```python
# migrations/schema-migrations/003_create_products.py
from aredis_om import BaseSchemaMigration, JsonModel, Field
from typing import List

class CreateProductsIndex003(BaseSchemaMigration):
    """Create product index with full-text search."""
    
    migration_id = "003_create_products_index"
    
    async def up(self):
        class Product(JsonModel):
            name: str = Field(index=True, full_text_search=True)
            description: str = Field(index=True, full_text_search=True)
            price: float = Field(index=True, sortable=True)
            category: str = Field(index=True)
            tags: List[str] = Field(default_factory=list)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "product"

        await Product.create_index()
    
    async def down(self):
        class Product(JsonModel):
            name: str = Field(index=True, full_text_search=True)
            description: str = Field(index=True, full_text_search=True)
            price: float = Field(index=True, sortable=True)
            category: str = Field(index=True)
            tags: List[str] = Field(default_factory=list)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "product"

        await Product.drop_index(delete_documents=True)
```

### Adding Vector Index

```python
# migrations/schema-migrations/004_add_vector_search.py
from aredis_om import BaseSchemaMigration, JsonModel, Field, VectorFieldOptions

class AddVectorSearch004(BaseSchemaMigration):
    """Add vector field for similarity search."""
    
    migration_id = "004_add_vector_search"
    
    async def up(self):
        # Drop and recreate with vector field
        await Document.drop_index(delete_documents=False)
        
        vector_options = VectorFieldOptions.flat(
            type=VectorFieldOptions.TYPE.FLOAT32,
            dimension=768,
            distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
        )

        class Document(JsonModel):
            title: str = Field(index=True, full_text_search=True)
            content: str = Field(index=True, full_text_search=True)
            embeddings: list[float] = Field(
                default_factory=list,
                vector_options=vector_options
            )

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "document"

        await Document.create_index()
    
    async def down(self):
        # Revert to non-vector schema
        await Document.drop_index(delete_documents=False)
        
        class Document(JsonModel):
            title: str = Field(index=True, full_text_search=True)
            content: str = Field(index=True, full_text_search=True)

            class Meta:
                global_key_prefix = "myapp"
                model_key_prefix = "document"

        await Document.create_index()
```

## CLI Commands

Redis OM provides an `om` CLI for migration management:

```bash
# Run migrations
om migrate

# Show migration status
om migrate status

# Rollback last migration
om migrate rollback

# Dry run (show what would be applied)
om migrate --dry-run

# Verbose output
om migrate --verbose

# Limit to N migrations
om migrate --limit 2

# Custom migrations directory
om migrate --migrations-dir path/to/migrations
```

### CLI with Environment Variables

```bash
# Set Redis connection
export REDIS_OM_URL="redis://localhost:6379"

# Run migrations
om migrate

# Custom migrations directory
export REDIS_OM_MIGRATIONS_DIR="/app/migrations/schema-migrations"
om migrate
```

## Schema Detector (Legacy)

The `SchemaDetector` (alias: `Migrator`) automatically detects and creates indexes:

```python
from aredis_om import SchemaDetector, MigrationAction

detector = SchemaDetector()

# Detect schema changes
actions = await detector.detect()

# Actions can be:
# - MigrationAction.CREATE_INDEX
# - MigrationAction.UPDATE_INDEX
# - MigrationAction.NO_ACTION

for action, model in actions:
    if action == MigrationAction.CREATE_INDEX:
        print(f"Creating index for {model.__name__}")
        await model.create_index()
    elif action == MigrationAction.UPDATE_INDEX:
        print(f"Updating index for {model.__name__}")
        await model.drop_index(delete_documents=False)
        await model.create_index()
```

## Best Practices

### Development vs Production

**Development:**
```python
# Auto-create indexes on startup
from aredis_om import Migrator

async def startup():
    await Migrator().run()  # Quick, automatic
```

**Production:**
```python
# Use file-based migrations
from aredis_om import SchemaMigrator

async def startup():
    migrator = SchemaMigrator(migrations_dir="migrations/schema-migrations")
    await migrator.run(verbose=True)
```

### Migration Guidelines

1. **Version control migrations:** Commit migration files to git
2. **Make migrations idempotent:** Safe to run multiple times
3. **Test rollbacks:** Ensure `down()` reverses `up()` correctly
4. **Preserve data when possible:** Use `delete_documents=False`
5. **Document breaking changes:** Update application docs with schema changes
6. **Use descriptive migration IDs:** `001_add_users` not `001_a`

### Data Migration Patterns

When changing field types or structures:

```python
class MigrateUserData005(BaseSchemaMigration):
    """Migrate user data to new schema."""
    
    migration_id = "005_migrate_user_data"
    
    async def up(self):
        # 1. Create new index with updated schema
        await UserV2.create_index()
        
        # 2. Migrate existing data
        old_users = await User.find().all()
        for old_user in old_users:
            new_user = UserV2(
                username=old_user.username,
                email=old_user.email,
                # Transform data as needed
                created_at=old_user.created_at
            )
            await new_user.save()
        
        # 3. Optionally delete old index
        # await User.drop_index(delete_documents=True)
    
    async def down(self):
        # Reverse migration if needed
        pass
```

## Error Handling

```python
from aredis_om import SchemaMigrationError, MigrationError

try:
    await migrator.run(verbose=True)
except SchemaMigrationError as e:
    print(f"Schema migration error: {e}")

try:
    await migrator.rollback("003_add_products")
except NotImplementedError:
    print("Rollback not implemented for this migration")
except SchemaMigrationError as e:
    print(f"Rollback failed: {e}")
```

## Troubleshooting Migrations

### Index Already Exists

```python
# Force recreation
await User.drop_index(delete_documents=False)
await User.create_index()

# Or check before creating
if await User.index_exists():
    print("Index already exists")
else:
    await User.create_index()
```

### Module Not Available

```python
from aredis_om import has_redis_json, has_redisearch

if not has_redisearch():
    raise RuntimeError(
        "RediSearch module required. Use redis/redis-stack Docker image."
    )

if not has_redis_json():
    print("Warning: RedisJSON not available")
    # Fall back to HashModel only
```

### Migration Not Detected

Ensure migration files:
1. Are in correct directory (`schema-migrations/`)
2. Import `BaseSchemaMigration`
3. Define class inheriting from `BaseSchemaMigration`
4. Have `migration_id` attribute
5. Implement `up()` method (and `down()` for rollback support)
