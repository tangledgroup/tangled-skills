---
name: sqlalchemy-2-0
description: Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when building Python applications that require database connectivity, object-relational mapping, or programmatic SQL generation with support for PostgreSQL, MySQL, SQLite, Oracle, and MSSQL.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.0.49"
tags:
  - database
  - orm
  - sql
  - python
  - postgresql
  - mysql
  - sqlite
  - oracle
  - mssql
  - async
category: database
external_references:
  - https://docs.sqlalchemy.org/
  - https://github.com/sqlalchemy/sqlalchemy
---

# SQLAlchemy 2.0

## Overview

SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a set of well-known enterprise persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. Version 2.0 introduces a unified API where the ORM uses Core-style `select()` constructs, type-annotated declarative mappings with `Mapped` and `mapped_column()`, and equivalent transactional semantics between Core connections and ORM sessions.

SQLAlchemy is presented as two distinct APIs:

- **SQLAlchemy Core** — the foundational "database toolkit" providing connectivity management, SQL expression construction, result handling, and connection pooling
- **SQLAlchemy ORM** — optional object-relational mapping built on top of Core, providing declarative class mapping, the Session persistence framework, and relationship navigation

## When to Use

- Building Python applications that require database connectivity and CRUD operations
- Implementing object-relational mapping with declarative class definitions
- Constructing SQL queries programmatically without string concatenation
- Working with multiple database backends (PostgreSQL, MySQL, SQLite, Oracle, MSSQL)
- Building async database applications with `asyncio` support
- Performing schema migrations and DDL operations from Python
- Needing type-safe database access with PEP 484 annotations

## Core Concepts

### Two-Layer Architecture

SQLAlchemy has two layers. Core is the SQL expression language and database toolkit. ORM builds on Core to add object-relational mapping. You can use Core alone for lightweight SQL construction, or use ORM for full persistence.

### The Engine

Every SQLAlchemy application starts with an `Engine`, created via `create_engine()`. The Engine manages a connection pool and acts as the factory for database connections. It is configured with a URL string indicating the database dialect, driver, and connection details. The Engine uses lazy initialization — it does not connect until first use.

### Connection and Transactions

The `Connection` object represents an active database transaction. Use context managers (`with engine.connect() as conn`) for automatic cleanup. Results from queries are returned as `Result` objects that support iteration, `.scalar_one()`, `.first()`, and `.all()` accessors.

### Database Metadata

`MetaData` is a collection that stores `Table` and `Column` definitions. It serves as the central schema registry. `Table` objects represent database tables with their columns, constraints, and relationships. `Column` objects define individual fields with types and constraints. Use `MetaData.create_all(engine)` to emit DDL.

### The Session (ORM)

The `Session` is the ORM's persistence manager. It tracks objects through states: transient (new, not in session), pending (added but not flushed), persistent (associated with session and database row), detached (was persistent but session closed), and expired (attributes cleared after commit). Use `session.add()`, `session.commit()`, `session.rollback()`, and `session.close()` for lifecycle management.

### Declarative Mappings (ORM)

SQLAlchemy 2.0 uses PEP 484 type annotations with `Mapped` and `mapped_column()` for declarative class definitions. Classes subclass a `DeclarativeBase` to establish the mapping. The `relationship()` construct defines object graph navigation between mapped classes.

### Identity Map

The Session maintains an identity map — an in-memory store linking primary key identities to unique Python object instances. `session.get(Model, id)` retrieves from the identity map if present, otherwise emits a SELECT. This ensures one instance per database row within a session scope.

## Usage Examples

### Core: Engine and Basic Query

```python
from sqlalchemy import create_engine, select, text

engine = create_engine("sqlite:///example.db", echo=True)

# Raw SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE name = :name"), {"name": "spongebob"})
    for row in result:
        print(row)

# Expression language
from sqlalchemy import Table, Column, Integer, String, MetaData
metadata = MetaData()
users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("email", String(120)),
)

stmt = select(users).where(users.c.name == "spongebob")
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)
```

### ORM: Declarative Mapping and Session

```python
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]  # Optional via type annotation

    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")

engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

# CRUD operations
with Session(engine) as session:
    # Insert
    user = User(name="spongebob", fullname="Spongebob Squarepants")
    session.add(user)
    session.commit()

    # Query
    stmt = select(User).where(User.name == "spongebob")
    user = session.execute(stmt).scalar_one()

    # Update (unit of work — Session tracks changes automatically)
    user.fullname = "Spongebob Squarepants Sr."
    session.commit()

    # Delete
    session.delete(user)
    session.commit()
```

### ORM: Relationship Navigation and Loading Strategies

```python
from sqlalchemy.orm import selectinload, joinedload

# Eager load with selectin (solves N+1 problem)
stmt = select(User).options(selectinload(User.addresses))
users = session.scalars(stmt).all()
for user in users:
    print(user.name, [a.email_address for a in user.addresses])  # No extra queries

# Joined load for many-to-one
stmt = select(Address).options(joinedload(Address.user, innerjoin=True))
addresses = session.scalars(stmt).all()
```

### Async ORM

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

async_engine = create_async_engine("sqlite+aiosqlite:///example.db")
async_session = async_sessionmaker(async_engine)

async with async_session() as session:
    stmt = select(User).options(selectinload(User.addresses))
    result = await session.scalars(stmt)
    users = result.all()
```

## Advanced Topics

**Core Tutorial**: Engine, connections, metadata, and SQL expression language fundamentals → See [Core Tutorial](reference/01-core-tutorial.md)

**ORM Mapping and Session**: Declarative mappings, relationships, unit of work, identity map, cascades → See [ORM Mapping and Session](reference/02-orm-mapping-session.md)

**SQL Expression Language**: SELECT constructs, WHERE clauses, JOINs, subqueries, CTEs, functions, aggregations → See [SQL Expression Language](reference/03-sql-expression-language.md)

**AsyncIO Support**: AsyncEngine, AsyncSession, async drivers, concurrency patterns → See [AsyncIO Support](reference/04-asyncio-support.md)

**Dialects and Drivers**: Database-specific configurations for PostgreSQL, MySQL, SQLite, Oracle, MSSQL, and external dialects → See [Dialects and Drivers](reference/05-dialects-drivers.md)

**Advanced ORM Patterns**: Hybrid attributes, association proxy, events, custom types, column properties → See [Advanced ORM Patterns](reference/06-advanced-orm-patterns.md)
