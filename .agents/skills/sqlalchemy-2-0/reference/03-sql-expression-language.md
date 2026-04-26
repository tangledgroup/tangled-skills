# SQL Expression Language

## SELECT Statements

The `select()` function is the primary construct for building queries. It uses a generative API where each method returns a new immutable object with added state.

### Basic SELECT

```python
from sqlalchemy import select

# Select all columns from a table
stmt = select(users_table)

# Select specific columns
stmt = select(users_table.c.name, users_table.c.email)

# With ORM entities
stmt = select(User)
stmt = select(User.name, User.fullname)
```

### WHERE Clause

```python
from sqlalchemy import and_, or_

# Simple condition
stmt = select(User).where(User.name == "spongebob")

# Multiple conditions (AND)
stmt = select(User).where(
    User.name == "sandy",
    User.fullname == "Sandy Cheeks"
)

# Explicit AND/OR
stmt = select(User).where(
    and_(User.name == "sandy", User.age > 25)
)

stmt = select(User).where(
    or_(User.name == "sandy", User.name == "patrick")
)

# filter_by for simple equality (ORM only)
stmt = select(User).filter_by(name="spongebob")
```

### Operators

Standard Python operators generate SQL expressions: `==`, `!=`, `<`, `<=`, `>`, `>=`, `in_()`, `not_in_()`, `like()`, `ilike()`, `startswith()`, `endswith()`, `contains()`, `is_()`, `isnot()`

```python
stmt = select(User).where(
    (User.name.like("s%")) &
    (User.age > 25) &
    (User.status.in_(["active", "pending"]))
)
```

### JOINs

```python
# Implicit ON clause from foreign key
stmt = select(User.name, Address.email_address).join_from(User, Address)

# Explicit ON clause
stmt = select(Address.email_address).select_from(User).join(
    Address, User.id == Address.user_id
)

# Using relationship for ON clause (ORM)
stmt = select(Address.email_address).select_from(User).join(User.addresses)

# LEFT OUTER JOIN
stmt = select(User).outerjoin(Address)
# or
stmt = select(User).join(Address, isouter=True)

# FULL OUTER JOIN
stmt = select(User).join(Address, full=True)
```

### ORDER BY, GROUP BY, HAVING

```python
from sqlalchemy import func

# Order by
stmt = select(User).order_by(User.name.desc())
stmt = select(User).order_by(User.name.asc(), User.fullname.desc())

# Aggregate with GROUP BY
stmt = select(
    Address.user_id,
    func.count(Address.id).label("addr_count")
).group_by(Address.user_id)

# HAVING
stmt = select(
    Address.user_id,
    func.count(Address.id).label("addr_count")
).group_by(Address.user_id).having(func.count(Address.id) > 2)
```

### Subqueries and CTEs

```python
# Scalar subquery
subq = select(func.count(User.id)).scalar_subquery()
stmt = select(subq.label("total_users"))

# Common Table Expression (CTE)
cte = select(User.name).where(User.active == True).cte("active_users")
stmt = select(cte).where(cte.c.name.like("s%"))

# Recursive CTE
parts = Table("parts", metadata,
    Column("part", String),
    Column("sub_part", String),
    Column("quantity", Integer),
)

recursive_cte = select(parts.c.part, parts.c.sub_part, parts.c.quantity).cte(
    "resolved_parts", recursive=True
)
recursive_cte = recursive_cte.union_select(
    select(parts.c.part, parts.c.sub_part, parts.c.quantity).where(
        parts.c.part == recursive_cte.c.sub_part
    )
)
```

### EXISTS

```python
from sqlalchemy import exists

stmt = select(User).where(
    exists().where(Address.user_id == User.id)
)
```

### UNION, INTERSECT, EXCEPT

```python
stmt1 = select(User.name).where(User.active == True)
stmt2 = select(User.name).where(User.role == "admin")
union_stmt = stmt1.union(stmt2)
union_all_stmt = stmt1.union_all(stmt2)
intersect_stmt = stmt1.intersect(stmt2)
except_stmt = stmt1.except_(stmt2)
```

## INSERT Statements

```python
from sqlalchemy import insert

# Single row
stmt = insert(users_table).values(name="spongebob", email="sponge@example.com")
result = conn.execute(stmt)
new_id = result.inserted_primary_key[0]

# Multiple rows
stmt = insert(users_table)
conn.execute(stmt, [
    {"name": "sandy", "email": "sandy@example.com"},
    {"name": "patrick", "email": "patrick@example.com"},
])

# Insert with default values
stmt = insert(users_table).values(name="squidward")

# Conditional insert (upsert pattern)
from sqlalchemy import insert
stmt = insert(users_table).values(name="spongebob", email="new@example.com")
stmt = stmt.on_conflict_do_update(
    index_elements=["email"],
    set_={"name": stmt.excluded.name}
)
```

## UPDATE Statements

```python
from sqlalchemy import update

# Simple update
stmt = update(users_table).where(users_table.c.id == 1).values(name="new_name")
result = conn.execute(stmt)
print(result.rowcount)  # number of rows affected

# Update with expression
stmt = update(users_table).where(
    users_table.c.name.like("%old%")
).values(
    name=users_table.c.name.replace("old", "new")
)

# ORM bulk update
from sqlalchemy import update
stmt = update(User).where(User.status == "inactive").values(status="archived")
session.execute(stmt)
```

## DELETE Statements

```python
from sqlalchemy import delete

# Simple delete
stmt = delete(users_table).where(users_table.c.id == 1)
result = conn.execute(stmt)
print(result.rowcount)

# ORM bulk delete
stmt = delete(User).where(User.status == "temp")
session.execute(stmt)
```

## SQL Functions

```python
from sqlalchemy import func

# Aggregate functions
stmt = select(func.count(User.id))
stmt = select(func.sum(User.age), func.avg(User.age))
stmt = select(func.max(User.created_at))

# String functions
stmt = select(func.lower(User.name))
stmt = select(func.concat(User.name, " ", User.fullname))

# Date functions
stmt = select(func.current_timestamp())
stmt = select(func.date(User.created_at))

# Custom function with return type
from sqlalchemy import func, String
custom_fn = func.my_function("arg").type(String)
```

### Window Functions

```python
from sqlalchemy import func, over

# Running count
row_num = func.row_number().over(order_by=User.created_at)
stmt = select(User.name, row_num.label("rn"))

# Partitioned window
rank = func.rank().over(partition_by=User.department_id, order_by=User.salary.desc())
stmt = select(Employee.name, rank.label("dept_rank"))
```

## Type Coercion and Casting

```python
from sqlalchemy import cast, type_coerce

# SQL CAST
stmt = select(cast(User.created_at, String).label("date_str"))

# Python-side type hint (no SQL emitted)
stmt = select(type_coerce("2024-01-01", DateTime))
```

## Text and Literal Expressions

```python
from sqlalchemy import text, literal_column

# Raw SQL fragment
stmt = select(text("'constant'"), users_table.c.name)

# Labeled column expression
expr = literal_column("json_data->>'field'").label("field_value")
stmt = select(expr, users_table.c.id)
```

## Aliases

```python
from sqlalchemy import alias

# Table alias
user_alias = alias(users_table)
stmt = select(users_table.c.name, user_alias.c.name).select_from(
    users_table.join(user_alias, users_table.c.manager_id == user_alias.c.id)
)

# ORM entity alias
from sqlalchemy.orm import aliased
user_alias = aliased(User)
stmt = select(User.name, user_alias.name).where(
    User.manager_id == user_alias.id
)
```
