# Core Querying with SQLAlchemy 2.0

## SELECT Statements

### Basic Select

```python
from sqlalchemy import select

# Select all columns
stmt = select(users)
result = session.execute(stmt)
rows = result.all()

# Select specific columns
stmt = select(users.c.id, users.c.username)
result = session.execute(stmt)

# With alias
user_alias = users.alias("u")
stmt = select(user_alias.c.id, user_alias.c.username)
```

### Filtering with WHERE

```python
from sqlalchemy import and_, or_, not_

# Simple filter
stmt = select(users).where(users.c.username == "alice")

# Multiple conditions with AND
stmt = select(users).where(
    and_(
        users.c.age >= 18,
        users.c.active == True
    )
)

# OR conditions
stmt = select(users).where(
    or_(
        users.c.username == "alice",
        users.c.username == "bob"
    )
)

# NOT condition
stmt = select(users).where(not_(users.c.banned == True))

# IN clause
stmt = select(users).where(
    users.c.id.in_([1, 2, 3, 4, 5])
)

# BETWEEN
stmt = select(users).where(
    users.c.age.between(18, 65)
)

# LIKE patterns
stmt = select(users).where(
    users.c.username.like("a%")  # Starts with 'a'
)

stmt = select(users).where(
    users.c.email.ilike("%@gmail.com")  # Case-insensitive
)

# IS NULL / IS NOT NULL
stmt = select(users).where(users.c.middle_name.is_(None))
stmt = select(users).where(users.c.middle_name.isnot(None))
```

### ORDER BY and Sorting

```python
from sqlalchemy import desc, asc

# Single column sort
stmt = select(users).order_by(users.c.username)

# Descending order
stmt = select(users).order_by(desc(users.c.created_at))

# Multiple columns
stmt = select(users).order_by(
    users.c.last_name,
    asc(users.c.first_name)
)

# Random order (dialect-specific)
from sqlalchemy import func
stmt = select(users).order_by(func.random())  # PostgreSQL/SQLite
```

### LIMIT and OFFSET

```python
# Limit results
stmt = select(users).limit(10)

# Pagination
stmt = select(users).limit(20).offset(40)  # Page 3 (0-indexed)

# Limit with ordering
stmt = select(users).order_by(users.c.created_at.desc()).limit(10)
```

### DISTINCT

```python
# Distinct rows
stmt = select(users).distinct()

# Distinct on specific columns
stmt = select(users.c.username).distinct()

# PostgreSQL DISTINCT ON
from sqlalchemy import distinct
stmt = select(distinct(on=[users.c.id]).select(users))
```

## JOINs

### INNER JOIN

```python
# Basic join
stmt = (
    select(users, posts)
    .join(posts, users.c.id == posts.c.user_id)
)

# Using on_ clause explicitly
stmt = (
    select(users, posts)
    .join(posts, onclause=users.c.id == posts.c.user_id)
)

# Multiple joins
stmt = (
    select(users, posts, comments)
    .join(posts, users.c.id == posts.c.user_id)
    .join(comments, posts.c.id == comments.c.post_id)
)
```

### LEFT OUTER JOIN

```python
from sqlalchemy import outerjoin

# Left join
stmt = (
    select(users, posts)
    .outerjoin(posts, users.c.id == posts.c.user_id)
)

# Multiple left joins
stmt = (
    select(users, posts, comments)
    .outerjoin(posts, users.c.id == posts.c.user_id)
    .outerjoin(comments, posts.c.id == comments.c.post_id)
)
```

### JOIN with Conditions

```python
# Join with additional filter
stmt = (
    select(users, posts)
    .join(posts, users.c.id == posts.c.user_id)
    .where(posts.c.published == True)
)

# Full outer join (PostgreSQL)
from sqlalchemy import fullouterjoin
stmt = (
    select(left_table, right_table)
    .full_outer_join(right_table, left_table.c.id == right_table.c.left_id)
)
```

## Aggregations

### Basic Aggregates

```python
from sqlalchemy import func

# Count
stmt = select(func.count(users.c.id))

# Sum
stmt = select(func.sum(posts.c.view_count))

# Average
stmt = select(func.avg(products.c.price))

# Min/Max
stmt = select(func.min(users.c.age), func.max(users.c.age))
```

### GROUP BY

```python
# Simple group by
stmt = (
    select(users.c.department, func.count(users.c.id))
    .group_by(users.c.department)
)

# Multiple columns
stmt = (
    select(
        users.c.department,
        users.c.role,
        func.count(users.c.id)
    )
    .group_by(users.c.department, users.c.role)
)

# With aggregate filter (HAVING)
stmt = (
    select(users.c.department, func.count(users.c.id).label("count"))
    .group_by(users.c.department)
    .having(func.count(users.c.id) > 10)
)
```

### Window Functions

```python
from sqlalchemy import over, row_number, rank, dense_rank

# Row number
stmt = (
    select(
        users.c.username,
        users.c.salary,
        row_number().over(
            order_by=users.c.salary.desc()
        ).label("rank")
    )
    .select_from(users)
)

# Partitioned window
stmt = (
    select(
        users.c.department,
        users.c.username,
        row_number().over(
            partition_by=users.c.department,
            order_by=users.c.salary.desc()
        ).label("dept_rank")
    )
    .select_from(users)
)

# Running total
stmt = (
    select(
        users.c.username,
        func.sum(users.c.salary).over(
            order_by=users.c.username
        ).label("running_total")
    )
    .select_from(users)
)

# Lag/Lead
from sqlalchemy import lag, lead
stmt = (
    select(
        users.c.username,
        users.c.salary,
        lag(users.c.salary).over(order_by=users.c.username).label("prev_salary"),
        lead(users.c.salary).over(order_by=users.c.username).label("next_salary")
    )
    .select_from(users)
)
```

## Subqueries

### Scalar Subquery

```python
# Subquery in SELECT clause
avg_salary = (
    select(func.avg(users.c.salary))
    .where(users.c.department == "Engineering")
    .scalar_subquery()
)

stmt = select(
    users.c.username,
    users.c.salary,
    avg_salary.label("dept_avg")
).select_from(users)
```

### Correlated Subquery

```python
# Subquery in WHERE clause
subq = (
    select(func.max(posts.c.view_count))
    .where(posts.c.user_id == users.c.id)
    .scalar_subquery()
)

stmt = (
    select(users)
    .where(users.c.id.in_(
        select(posts.c.user_id).group_by(posts.c.user_id).having(
            func.count(posts.c.id) > 5
        )
    ))
)
```

### Lateral Join (PostgreSQL)

```python
from sqlalchemy import lateral

# Top posts per user
top_posts = (
    select(posts.c.user_id, posts.c.title, posts.c.view_count)
    .where(posts.c.user_id == users.c.id)
    .order_by(posts.c.view_count.desc())
    .limit(3)
    .lateral()
)

stmt = select(users, top_posts).select_from(users)
```

## UNION and Set Operations

```python
# UNION (distinct by default)
stmt1 = select(users.c.username).where(users.c.active == True)
stmt2 = select(admins.c.username).where(admins.c.active == True)

union_stmt = stmt1.union(stmt2)

# UNION ALL (no deduplication)
union_all_stmt = stmt1.union_all(stmt2)

# INTERSECT
intersect_stmt = stmt1.intersect(stmt2)

# EXCEPT
except_stmt = stmt1.except_(stmt2)
```

## INSERT Operations

### Single Insert

```python
from sqlalchemy import insert

# Basic insert
stmt = insert(users).values(
    username="alice",
    email="alice@example.com",
    age=30
)

result = session.execute(stmt)
session.commit()

# Get inserted ID
result = session.execute(
    insert(users).values(username="alice").returning(users.c.id)
)
new_id = result.scalar()
```

### Bulk Insert

```python
# Multiple rows at once
stmt = insert(users).values([
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"},
    {"username": "charlie", "email": "charlie@example.com"},
])

session.execute(stmt)
session.commit()

# Bulk insert (faster, no individual callbacks)
session.bulk_insert_mappings(users, [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
])
```

### Insert with Return

```python
# PostgreSQL/MySQL RETURNING
stmt = (
    insert(users)
    .values(username="alice", email="alice@example.com")
    .returning(users.c.id, users.c.username)
)

result = session.execute(stmt)
new_id, username = result.scalar_one()

# Return all columns
stmt = insert(users).values(...).returning(*users.columns)
```

### Upsert (INSERT ... ON CONFLICT)

```python
# PostgreSQL upsert
stmt = (
    insert(users)
    .values(username="alice", email="alice@example.com")
    .on_conflict_do_update(
        index_elements=[users.c.username],
        set_=dict(email="alice@example.com", updated_at=func.now())
    )
)

# MySQL upsert (ON DUPLICATE KEY UPDATE)
stmt = (
    insert(users)
    .values(username="alice", email="alice@example.com")
    .on_duplicate_key_update(
        email="alice@example.com",
        updated_at=func.now()
    )
)
```

## UPDATE Operations

### Basic Update

```python
from sqlalchemy import update

# Simple update
stmt = (
    update(users)
    .where(users.c.username == "alice")
    .values(email="newemail@example.com")
)

result = session.execute(stmt)
print(result.rowcount)  # Number of rows updated
session.commit()
```

### Update with Expressions

```python
# Increment value
stmt = (
    update(posts)
    .where(posts.c.id == 1)
    .values(view_count=posts.c.view_count + 1)
)

# Update with function
stmt = (
    update(users)
    .where(users.c.last_login.is_(None))
    .values(last_login=func.now())
)

# Conditional update using CASE
from sqlalchemy import case
stmt = (
    update(users)
    .values(
        status=case(
            (users.c.age >= 18, "adult"),
            (users.c.age >= 13, "teen"),
            else_="child")
    )
)
```

### Update from Select

```python
# Update values from another table
stmt = (
    update(users)
    .where(users.c.id == profiles.c.user_id)
    .values(full_name=profiles.c.full_name)
)
```

### Bulk Update

```python
# Using ORM query (2.0 style)
from sqlalchemy import update

stmt = (
    update(users)
    .where(users.c.age >= 18)
    .values(status="adult")
)

session.execute(stmt)
session.commit()

# Returns number of affected rows
result = session.execute(stmt)
print(f"Updated {result.rowcount} rows")
```

## DELETE Operations

### Basic Delete

```python
from sqlalchemy import delete

# Simple delete
stmt = delete(users).where(users.c.username == "alice")

result = session.execute(stmt)
print(result.rowcount)  # Number of rows deleted
session.commit()
```

### Delete with Conditions

```python
# Delete old records
from datetime import datetime, timedelta

cutoff_date = datetime.utcnow() - timedelta(days=365)
stmt = (
    delete(logs)
    .where(logs.c.created_at < cutoff_date)
)

# Delete based on subquery
subq = select(posts.c.user_id).group_by(posts.c.user_id).having(
    func.count(posts.c.id) > 100
).scalar_subquery()

stmt = delete(users).where(users.c.id.not_in(subq))
```

### DELETE ... RETURNING

```python
# PostgreSQL: Get deleted rows
stmt = (
    delete(users)
    .where(users.c.username == "alice")
    .returning(users.c.id, users.c.username)
)

result = session.execute(stmt)
for row in result:
    print(f"Deleted user: {row.username}")
```

### Truncate Table

```python
# Fast table truncation
stmt = users.delete()  # Clears all rows without WHERE clause

# Or use DDL
from sqlalchemy import text
session.execute(text("TRUNCATE TABLE users RESTART IDENTITY"))
```

## Executing Raw SQL

### Using text()

```python
from sqlalchemy import text

# Simple query
stmt = text("SELECT * FROM users WHERE username = :name")
result = session.execute(stmt, {"name": "alice"})

# With parameters
stmt = text("SELECT * FROM users WHERE age > :min_age AND active = :active")
result = session.execute(stmt, {"min_age": 18, "active": True})

# Multiple statements (PostgreSQL)
stmt = text("""
    CREATE TEMP TABLE temp_users AS
    SELECT * FROM users WHERE active = true;
    
    SELECT COUNT(*) FROM temp_users;
""")
result = session.execute(stmt)
```

### Executing DDL

```python
from sqlalchemy import text

# Create table
session.execute(text("""
    CREATE TABLE IF NOT EXISTS temp_data (
        id SERIAL PRIMARY KEY,
        value VARCHAR(100)
    )
"""))

# Execute stored procedure (PostgreSQL)
session.execute(text("CALL my_procedure(:param1, :param2)), {"param1": 1, "param2": 2}))
```

## Result Processing

### Accessing Results

```python
result = session.execute(select(users))

# First row
row = result.first()
print(row.username)

# Single scalar value
count = session.execute(select(func.count(users.id))).scalar()

# All rows as list
rows = session.execute(select(users)).all()

# Iterate efficiently (for large result sets)
for row in session.execute(select(users)):
    process(row)
```

### Row Access Patterns

```python
result = session.execute(select(users))
row = result.first()

# By attribute name
print(row.id, row.username)

# By index
print(row[0], row[1])

# By dictionary key
print(row["id"], row["username"])

# Unpack
user_id, username, email = row
```

### Mapped Results (Dict-like)

```python
from sqlalchemy import RowMapping

# Get results as mappings
result = session.execute(select(users)).mappings()

# Access as dict
for row in result:
    print(row["username"])

# Single mapping
user = session.execute(
    select(users).where(users.c.id == 1)
).mappings().one()
print(user["username"])

# As list of dicts
users_list = session.execute(select(users)).mappings().all()
```

## Advanced Techniques

### CTEs (Common Table Expressions)

```python
from sqlalchemy import cte

# Simple CTE
user_cte = cte(
    select(users.c.id, users.c.username)
    .where(users.c.active == True)
    .cte("active_users")
)

stmt = select(user_cte).where(user_cte.c.username.like("a%"))

# Recursive CTE (for hierarchical data)
from sqlalchemy import column

# Base case
manager_query = select(employees.c.id, employees.c.name, employees.c.manager_id).where(
    employees.c.manager_id.is_(None)
)

# Recursive case
employee_query = select(
    employees.c.id,
    employees.c.name,
    employees.c.manager_id
).where(employees.c.manager_id == cte("org").c.id)

recursive_cte = manager_query.union_all(employee_query).cte("org", recursive=True)

stmt = select(recursive_cte)
```

### With Options (PostgreSQL)

```python
# CTE with materialization hint
cte_obj = (
    select(users.c.id, users.c.username)
    .where(users.c.active == True)
    .cte("active_users", materialized=True)  # or materialized=False
)
```

## Performance Tips

1. **Use indexes** on frequently filtered columns
2. **Select only needed columns** instead of entire rows
3. **Use LIMIT** for large result sets
4. **Avoid N+1 queries** with proper joins
5. **Use bulk operations** for batch inserts/updates
6. **Consider connection pooling** for high-volume applications
7. **Use EXPLAIN** to analyze query plans

## Next Steps

- [ORM Mapping](05-orm-mapping.md) - Map Python classes to tables
- [ORM Querying](09-orm-querying.md) - ORM-specific query patterns
- [SQL Expressions](12-core-sql-expressions.md) - Advanced SQL construction
- [Best Practices](24-best-practices.md) - Performance optimization
