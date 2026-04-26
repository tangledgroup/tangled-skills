# Dialects and Drivers

The dialect system is how SQLAlchemy communicates with various databases. Each dialect handles database-specific SQL generation, type mapping, and connection management.

## Included Dialects

SQLAlchemy includes built-in support for five major database families:

- **PostgreSQL** — `postgresql://`
- **MySQL / MariaDB** — `mysql://`
- **SQLite** — `sqlite://`
- **Oracle** — `oracle://`
- **Microsoft SQL Server** — `mssql://`

## PostgreSQL

### Connection URLs

```python
# psycopg (synchronous, recommended)
engine = create_engine("postgresql+psycopg://user:pass@localhost/dbname")

# psycopg2 (legacy, still supported)
engine = create_engine("postgresql+psycopg2://user:pass@localhost/dbname")

# pg8000 (pure Python alternative)
engine = create_engine("postgresql+pg8000://user:pass@localhost/dbname")

# asyncpg (async)
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")
```

### PostgreSQL-Specific Features

```python
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, INSERT

# JSONB column
class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB)

# Array column
class Tags(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    values: Mapped[list[str]] = mapped_column(ARRAY(String))

# UUID column
class Entity(Base):
    __tablename__ = "entities"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

# UPSERT (ON CONFLICT DO UPDATE)
from sqlalchemy.dialects.postgresql import insert as pg_insert
stmt = pg_insert(users_table).values(name="spongebob", email="s@example.com")
stmt = stmt.on_conflict_do_update(
    index_elements=["email"],
    set_={"name": stmt.excluded.name}
)

# UPSERT (ON CONFLICT DO NOTHING)
stmt = stmt.on_conflict_do_nothing(index_elements=["email"])
```

### Supported Versions

PostgreSQL 9.6+ fully supported, 9+ best effort.

## MySQL and MariaDB

### Connection URLs

```python
# mysqlclient (recommended)
engine = create_engine("mysql+mysqldb://user:pass@localhost/dbname")

# PyMySQL (pure Python)
engine = create_engine("mysql+pymysql://user:pass@localhost/dbname")

# async — aiomysql
engine = create_async_engine("mysql+aiomysql://user:pass@localhost/dbname")

# async — asyncmy
engine = create_async_engine("mysql+asyncmy://user:pass@localhost/dbname")
```

### MySQL-Specific Features

```python
from sqlalchemy.dialects.mysql import INSERT, VARCHAR, TEXT

# MySQL-specific types
class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(TEXT)

# UPSERT (ON DUPLICATE KEY UPDATE)
from sqlalchemy.dialects.mysql import insert as mysql_insert
stmt = mysql_insert(users_table).values(name="spongebob", email="s@example.com")
stmt = stmt.on_duplicate_key_update(name=stmt.inserted.name)
```

### Supported Versions

MySQL 5.6+ / MariaDB 10+ fully supported, MySQL 5.0.2+ / MariaDB 5.0.2+ best effort.

## SQLite

### Connection URLs

```python
# In-memory
engine = create_engine("sqlite:///:memory:")

# File-based
engine = create_engine("sqlite:///path/to/database.db")

# Absolute path (important on Windows)
engine = create_engine("sqlite:////absolute/path/to/database.db")

# async — aiosqlite
engine = create_async_engine("sqlite+aiosqlite:///database.db")
```

### SQLite-Specific Notes

- Use `check_same_thread=False` for multi-threaded access (passed via connect_args)
- WAL mode for better concurrency: `?mode=rw&_journal_mode=WAL`
- UPSERT via `INSERT ... ON CONFLICT`:
  ```python
  stmt = insert(users_table).values(name="spongebob")
  stmt = stmt.on_conflict_do_update(
      index_elements=["name"],
      set_={"email": stmt.excluded.email}
  )
  ```

### Supported Versions

SQLite 3.12+ fully supported, 3.7.16+ best effort.

## Oracle

### Connection URLs

```python
# cx_Oracle
engine = create_engine("oracle+cx_oracle://user:pass@dsn")

# Thick mode (Oracle client installed)
engine = create_engine("oracle+cx_oracle://user:pass@host:port/service_name")
```

### Oracle-Specific Notes

- Sequence-based primary keys are common
- Uses `RETURNING` clause for insert primary key retrieval
- Case-sensitive identifiers by default (use quoted names)

### Supported Versions

Oracle 11+ fully supported, 9+ best effort.

## Microsoft SQL Server

### Connection URLs

```python
# pyodbc (recommended)
engine = create_engine(
    "mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server"
)

# pymssql (alternative)
engine = create_engine("mssql+pymssql://user:pass@host/dbname")
```

### MSSQL-Specific Notes

- Uses `OUTPUT INSERTED.*` for insert primary key retrieval
- Schema support via `schema` parameter on Table
- `IDENTITY` columns for auto-increment

### Supported Versions

SQL Server 2012+ fully supported, 2005+ best effort.

## URL Format Reference

General format: `dialect+driver://username:password@host:port/database?param=value`

Common URL parameters:
- `echo=True` — enable SQL logging
- `pool_size=N` — connection pool size
- `pool_recycle=N` — recycle connections after N seconds
- `pool_pre_ping=True` — test connections before use
- `connect_timeout=N` — connection timeout in seconds

## External Dialects

Many third-party databases provide SQLAlchemy dialects as separate packages:

- **Snowflake**: `snowflake-sqlalchemy`
- **BigQuery**: `sqlalchemy-bigquery`
- **CockroachDB**: `sqlalchemy-cockroachdb`
- **ClickHouse**: `clickhouse-sqlalchemy`
- **Redshift**: `sqlalchemy-redshift`
- **DynamoDB**: `pydynamodb`
- **MongoDB**: `pymongosql`
- **Elasticsearch**: `elasticsearch-dbapi`

External dialects are installed and used the same way as built-in dialects, with their own connection URL scheme.

## Database Introspection (Reflection)

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# List tables
tables = inspector.get_table_names()

# Get column info
columns = inspector.get_columns("users")
# Returns list of dicts: {name, type, nullable, default, ...}

# Get foreign keys
fks = inspector.get_foreign_keys("addresses")

# Get indexes
indexes = inspector.get_indexes("users")

# Get primary key
pk = inspector.get_pk_constraint("users")

# Reflect all tables
metadata = MetaData()
metadata.reflect(bind=engine)

# Reflect specific tables
metadata.reflect(bind=engine, only=["users", "addresses"])
```
