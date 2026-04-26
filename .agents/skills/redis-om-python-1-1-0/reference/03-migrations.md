# Migrations

## Migration Types

Redis OM provides two types of migrations:

- **Schema migrations** (`om migrate`) — manage RediSearch index schema changes
- **Data migrations** (`om migrate-data`) — transform and update actual data

## CLI Commands

```bash
om migrate          # Schema migrations (file-based with rollback)
om migrate-data     # Data migrations (transformations)
```

## Schema Migrations

### Directory Layout

By default, Redis OM uses a root `migrations/` directory (configurable via `REDIS_OM_MIGRATIONS_DIR`). Within it:

- `schema-migrations/` — file-based schema migrations (RediSearch index snapshots)
- `data-migrations/` — data migration files

The CLI creates these directories on first use.

### Basic Usage

```bash
# Create a new schema migration snapshot from pending index changes
om migrate create add_sortable_on_user_name

# Review status
om migrate status

# Run schema migrations
om migrate run

# Override migrations directory
om migrate run --migrations-dir myapp/schema-migrations
```

### How File-Based Migration Works

1. **Detection** — auto-migrator detects index changes from model definitions
2. **Snapshot** — `om migrate create` writes a migration file capturing old/new index schemas
3. **Apply** — `om migrate run` executes migration files (drop/create indices) and records state
4. **Rollback** — `om migrate rollback <id>` restores previous index schema when available

### Example

```python
# Before: simple field
class User(HashModel, index=True):
    name: str = Field(index=True)

# After: add sortable
class User(HashModel, index=True):
    name: str = Field(index=True, sortable=True)
```

Running `om migrate` will drop the old index, create a new one with sortable support, and update the stored schema hash.

## Data Migrations

Data migrations handle transformations of actual data — format conversions, data fixes, value transformations.

### Basic Commands

```bash
# Check migration status
om migrate-data status

# Run pending migrations
om migrate-data run

# Dry run (preview changes)
om migrate-data run --dry-run

# Create new migration
om migrate-data create migration_name

# Verbose output
om migrate-data run --verbose

# Limit number of migrations to apply
om migrate-data run --limit 1
```

### Migration Status Output

```
Migration Status:
Total migrations: 2
Applied: 1
Pending: 1
Pending migrations:
- 002_normalize_user_emails
Applied migrations:
- 001_datetime_fields_to_timestamps
```

### Creating Custom Migrations

```bash
om migrate-data create normalize_emails
```

Creates a file like `migrations/20231201_143022_normalize_emails.py`:

```python
from redis_om.model.migrations.data_migrator import BaseMigration

class NormalizeEmailsMigration(BaseMigration):
    migration_id = "20231201_143022_normalize_emails"
    description = "Normalize all email addresses to lowercase"
    dependencies = []

    def up(self) -> None:
        """Apply the migration."""
        from myapp.models import User
        for user in User.find().all():
            if user.email:
                user.email = user.email.lower()
                user.save()

    def down(self) -> None:
        """Reverse the migration (optional)."""
        pass

    def can_run(self) -> bool:
        """Check if migration can run."""
        return True
```

### Migration Dependencies

Migrations can declare dependencies on other migrations:

```python
class AdvancedMigration(BaseMigration):
    migration_id = "003_advanced"
    dependencies = ["001_base", "002_normalize"]
```

Dependencies ensure migrations run in the correct order.

### Rollback Support

Data migrations support rollback through the `down()` method. Schema migrations support rollback via `om migrate rollback <id>`.

## Built-in Migrations

### Datetime Field Migration

Redis OM includes built-in data migrations for datetime field normalization. In version 1.1, datetime handling was updated:

- `datetime.datetime` values now round-trip as UTC-aware datetime values
- `datetime.date` values now store as midnight UTC instead of local-midnight timestamps

### Datetime Timezone Normalization in 1.1.0

This change is important if you have existing data from earlier releases:

- Existing `datetime.datetime` records still represent the same instant, but code expecting naive datetime values may need to handle UTC-aware values
- Existing `datetime.date` records written in a non-UTC environment may load as a different calendar day after upgrading
- Date equality queries may stop matching older records until data is re-saved or migrated

Run the built-in data migration to normalize timestamps:

```bash
om migrate-data run
```

## Advanced Usage

### Module-Based Migrations

For larger applications, organize migrations within a Python package module rather than a flat directory.

### Custom Migration Directory

Override the default migrations directory:

```bash
REDIS_OM_MIGRATIONS_DIR=myapp/migrations om migrate run
```

Or via environment variable `REDIS_OM_MIGRATIONS_DIR`.

### Programmatic Usage

Run migrations from code:

```python
from redis_om import Migrator
Migrator().run()
```

## Best Practices

### Schema Migrations

- Run `om migrate` after every model schema change
- Use file-based migrations (`om migrate create`) for production deployments
- Test migrations in a staging environment first

### Data Migrations

- Always implement `down()` for rollback capability
- Use `--dry-run` before applying data migrations to production
- Keep migrations idempotent when possible
- Add `can_run()` checks for conditional migrations

### Migration Strategy

- Schema migrations first, then data migrations
- Test with small datasets before full rollout
- Monitor migration status with `om migrate-data status`

### Error Handling

If a migration fails:

1. Check the error output for the specific failure
2. Fix the underlying issue (model definition, data inconsistency)
3. Retry with `om migrate run` or `om migrate-data run`
4. For schema migrations, use `om migrate rollback <id>` to revert
