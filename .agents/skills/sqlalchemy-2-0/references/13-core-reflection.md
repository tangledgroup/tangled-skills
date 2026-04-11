# Core Reflection (Schema Introspection)

## Introduction to Reflection

Reflection allows SQLAlchemy to introspect existing database schemas and create Python representations of tables, columns, constraints, and other schema objects.

```python
from sqlalchemy import create_engine, MetaData, inspect

engine = create_engine("postgresql://user:pass@localhost/db")
metadata = MetaData()

# Reflect all tables
metadata.reflect(bind=engine)

# Access reflected tables
users = metadata.tables["users"]
print(users.columns.keys())  # ['id', 'username', 'email', ...]
```

## Basic Reflection

### Reflect All Tables

```python
from sqlalchemy import MetaData, create_engine

engine = create_engine("postgresql://user:pass@localhost/db")
metadata = MetaData()

# Reflect all tables in default schema
metadata.reflect(bind=engine)

# Access tables
for name, table in metadata.tables.items():
    print(f"Table: {name}")
    for col in table.columns:
        print(f"  - {col.name}: {col.type}")
```

### Reflect Specific Tables

```python
# Reflect only specific tables
metadata.reflect(
    bind=engine,
    only=["users", "posts", "comments"]
)

# Or use extends_existing to add to existing metadata
metadata = MetaData()
users = Table("users", metadata, autoload_with=engine)
posts = Table("posts", metadata, autoload_with=engine)
```

### Reflect with Schema

```python
# Reflect tables from specific schema
metadata.reflect(
    bind=engine,
    schema="public"  # PostgreSQL schema
)

# Multiple schemas
for schema in ["public", "analytics"]:
    metadata.reflect(bind=engine, schema=schema, only=["users"])
```

## Inspector API

### Using Inspector for Detailed Introspection

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# Get all table names
tables = inspector.get_table_names(schema="public")
print(tables)  # ['users', 'posts', 'comments']

# Get view names
views = inspector.get_view_names(schema="public")

# Get schema names
schemas = inspector.get_schema_names()

# Check if table exists
has_users = inspector.has_table("users", schema="public")
```

### Inspecting Columns

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# Get column information
columns = inspector.get_columns("users", schema="public")

for col in columns:
    print(f"Name: {col['name']}")
    print(f"  Type: {col['type']}")
    print(f"  Primary Key: {col['primary_key']}")
    print(f"  Autoincrement: {col['autoincrement']}")
    print(f"  Nullable: {col['nullable']}")
    print(f"  Default: {col['default']}")
    print(f"  Comment: {col.get('comment')}")
```

### Inspecting Foreign Keys

```python
# Get foreign key constraints
fks = inspector.get_foreign_keys("posts", schema="public")

for fk in fks:
    print(f"Constraint: {fk['name']}")
    print(f"  Columns: {fk['columns']}")
    print(f"  Referenced Table: {fk['referred_table']}")
    print(f"  Referenced Schema: {fk['referred_schema']}")
    print(f"  Referenced Columns: {fk['referred_columns']}")
    print(f"  On Delete: {fk.get('ondelete')}")
    print(f"  On Update: {fk.get('onupdate')}")
```

### Inspecting Indexes

```python
# Get index information
indexes = inspector.get_indexes("users", schema="public")

for idx in indexes:
    print(f"Index: {idx['name']}")
    print(f"  Columns: {idx['columns']}")
    print(f"  Unique: {idx['unique']}")
    print(f"  Primary: {idx['primary'] if 'primary' in idx else False}")
    print(f"  Expression: {idx.get('expression')}")
    print(f"  Dialect Options: {idx.get('dialect_options')}")
```

### Inspecting Constraints

```python
# Get unique constraints
unique_constraints = inspector.get_unique_constraints("users", schema="public")

for uc in unique_constraints:
    print(f"Constraint: {uc['name']}")
    print(f"  Columns: {uc['columns']}")

# Get check constraints (dialect-dependent)
check_constraints = inspector.get_check_constraints("users", schema="public")

# Get primary key
pk_columns = inspector.get_pk_constraint("users", schema="public")
print(f"Primary Key: {pk_columns['columns']}")
```

## Advanced Reflection

### Reflect with Options

```python
metadata.reflect(
    bind=engine,
    only=["users", "posts"],           # Specific tables
    schema="public",                    # Specific schema
    extend_existing=True,               # Add to existing Table objects
    replace_existing=False,             # Don't replace existing definitions
    resolve_fks=True,                   # Resolve foreign keys to other reflected tables
)
```

### Partial Reflection with autoload_with

```python
from sqlalchemy import Table, Column, MetaData

metadata = MetaData()

# Reflect table during definition
users = Table(
    "users",
    metadata,
    autoload_with=engine  # Automatically reflect from database
)

# Mix reflected and manual columns
posts = Table(
    "posts",
    metadata,
    Column("extra_column", String),  # Manual column
    autoload_with=engine,            # Plus reflected columns
    extend_existing=True             # Don't overwrite manual columns
)
```

### Reflecting Specific Column Types

```python
from sqlalchemy import Table, MetaData
from sqlalchemy.types import TypeDecorator

# Custom type handling during reflection
class CustomJSON(TypeDecorator):
    impl = Text
    cache_ok = True

metadata = MetaData()

# Reflect with type coercion
users = Table(
    "users",
    metadata,
    autoload_with=engine
)

# Access reflected column with custom type
if "preferences" in users.columns:
    users.columns["preferences"].type = CustomJSON()
```

## Dynamic Schema Discovery

### Discover All Schemas and Tables

```python
from sqlalchemy import inspect

inspector = inspect(engine)

for schema in inspector.get_schema_names():
    print(f"\nSchema: {schema}")
    
    tables = inspector.get_table_names(schema=schema)
    for table_name in tables:
        print(f"  Table: {table_name}")
        
        columns = inspector.get_columns(table_name, schema=schema)
        for col in columns:
            print(f"    - {col['name']}: {col['type']}")
```

### Filter Tables by Pattern

```python
import re

inspector = inspect(engine)

# Find all tables matching pattern
pattern = re.compile(r"^user_.*")
matching_tables = [
    t for t in inspector.get_table_names()
    if pattern.match(t)
]

print("User-related tables:", matching_tables)
```

### Discover Table Relationships

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# Build relationship map
relationships = {}

for table in inspector.get_table_names():
    fks = inspector.get_foreign_keys(table)
    
    for fk in fks:
        ref_table = fk['referred_table']
        if ref_table not in relationships:
            relationships[ref_table] = []
        
        relationships[ref_table].append({
            'child_table': table,
            'columns': fk['columns'],
            'referenced_columns': fk['referred_columns']
        })

# Print relationships
for parent, children in relationships.items():
    print(f"{parent} is referenced by:")
    for child_info in children:
        print(f"  - {child_info['child_table']}")
```

## Reflection for Migration

### Compare Schemas

```python
from sqlalchemy import MetaData, inspect, create_engine

# Reflect current database schema
db_metadata = MetaData()
db_metadata.reflect(bind=engine)

# Define expected schema
expected_metadata = MetaData()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    # ... more columns

expected_metadata.create_all(engine)  # Create expected structure

# Compare
db_tables = set(db_metadata.tables.keys())
expected_tables = set(expected_metadata.tables.keys())

missing_tables = expected_tables - db_tables
extra_tables = db_tables - expected_tables

print(f"Missing tables: {missing_tables}")
print(f"Extra tables: {extra_tables}")
```

### Generate Create Scripts

```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable

engine = create_engine("postgresql://user:pass@localhost/db")
metadata = MetaData()

# Reflect table
users = Table("users", metadata, autoload_with=engine)

# Generate CREATE statement
create_stmt = CreateTable(users).compile(engine)
print(create_stmt)

# For all tables
for table in metadata.tables.values():
    print(CreateTable(table).compile(engine))
```

### Export Schema to Dictionary

```python
from sqlalchemy import inspect

def export_schema(engine, schema="public"):
    inspector = inspect(engine)
    schema_dict = {}
    
    for table_name in inspector.get_table_names(schema=schema):
        table_info = {
            "columns": [],
            "primary_key": [],
            "foreign_keys": [],
            "indexes": []
        }
        
        # Columns
        for col in inspector.get_columns(table_name, schema):
            table_info["columns"].append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "primary_key": col["primary_key"],
                "default": col.get("default")
            })
        
        # Primary key
        pk = inspector.get_pk_constraint(table_name, schema)
        table_info["primary_key"] = pk["columns"]
        
        # Foreign keys
        for fk in inspector.get_foreign_keys(table_name, schema):
            table_info["foreign_keys"].append({
                "columns": fk["columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"]
            })
        
        # Indexes
        for idx in inspector.get_indexes(table_name, schema):
            table_info["indexes"].append({
                "name": idx["name"],
                "columns": idx["columns"],
                "unique": idx["unique"]
            })
        
        schema_dict[table_name] = table_info
    
    return schema_dict

# Export and save
schema = export_schema(engine)
import json
with open("schema.json", "w") as f:
    json.dump(schema, f, indent=2)
```

## Reflection Best Practices

### 1. Use extend_existing for Incremental Updates

```python
# Good - preserves existing definitions
metadata.reflect(
    bind=engine,
    extend_existing=True,
    replace_existing=False
)

# Then add new columns programmatically if needed
if "new_column" not in users.columns:
    users.append_column(Column("new_column", String))
```

### 2. Reflect Only What You Need

```python
# Good - selective reflection
metadata.reflect(
    bind=engine,
    only=["users", "posts", "comments"]  # Specific tables
)

# Better - use autoload_with for single tables
users = Table("users", metadata, autoload_with=engine)
```

### 3. Handle Dialect-Specific Features

```python
# PostgreSQL-specific reflection
if engine.dialect.name == "postgresql":
    # Reflect with schema
    metadata.reflect(bind=engine, schema="public")
    
    # Get comments (PostgreSQL specific)
    comments = inspector.get_table_comment("users", "public")
```

### 4. Cache Reflection Results

```python
from sqlalchemy import inspect
import json
from datetime import datetime

REFLECTION_CACHE = "schema_cache.json"
CACHE_TIMEOUT = 3600  # 1 hour

def get_cached_reflection(engine):
    try:
        with open(REFLECTION_CACHE) as f:
            cache = json.load(f)
        
        if datetime.now().timestamp() - cache["timestamp"] < CACHE_TIMEOUT:
            return cache["schema"]
    except FileNotFoundError:
        pass
    
    # Refresh cache
    inspector = inspect(engine)
    schema = export_schema(engine)
    
    cache = {
        "timestamp": datetime.now().timestamp(),
        "schema": schema
    }
    
    with open(REFLECTION_CACHE, "w") as f:
        json.dump(cache, f)
    
    return schema
```

## Troubleshooting Reflection

### Table Not Found

```python
# Problem: Table exists but not reflected

# Solution 1: Check schema
metadata.reflect(bind=engine, schema="public")  # Explicit schema

# Solution 2: Check table name case sensitivity
users = Table("users", metadata, autoload_with=engine)
# Try: users = Table('"Users"', metadata, autoload_with=engine)
```

### Foreign Keys Not Resolved

```python
# Problem: FK columns don't reference other columns

# Solution: Resolve FKs explicitly
metadata.reflect(
    bind=engine,
    resolve_fks=True  # Enable FK resolution
)
```

### Type Mismatches

```python
# Problem: Reflected type doesn't match expected

# Solution: Use custom type coercion
from sqlalchemy.types import TypeDecorator

class CustomType(TypeDecorator):
    impl = String
    cache_ok = True

users = Table("users", metadata, autoload_with=engine)
users.columns["custom_col"].type = CustomType()
```

## Next Steps

- [Dialects](16-dialects-overview.md) - Database-specific reflection features
- [Custom Types](15-core-custom-types.md) - Type handling during reflection
- [Migration Guide](21-migration-2-0.md) - Schema migration patterns
- [Best Practices](24-best-practices.md) - Reflection in production
