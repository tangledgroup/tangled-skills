# ORM Querying Guide

## Basic Query Patterns

### Select with SQLAlchemy 2.0 Style

```python
from sqlalchemy import select

# Get all objects
users = session.execute(select(User)).scalars().all()

# Filter objects
adults = session.execute(
    select(User).where(User.age >= 18)
).scalars().all()

# Get single object
user = session.execute(
    select(User).where(User.username == "alice")
).scalar_one_or_none()

# Get exactly one (raises if 0 or >1)
user = session.execute(
    select(User).where(User.id == 1)
).scalar_one()
```

### Using get() for Primary Key Lookup

```python
# Fast primary key lookup (no SQL query if in identity map)
user = session.get(User, 1)

# Get multiple by IDs (identity map aware)
users = session.get(User, 1)
users2 = session.get(User, 2)
```

### Filtering Queries

```python
from sqlalchemy import and_, or_, not_

# Simple filter
users = session.execute(
    select(User).where(User.active == True)
).scalars().all()

# Multiple conditions (AND)
users = session.execute(
    select(User).where(
        and_(User.age >= 18, User.active == True)
    )
).scalars().all()

# OR conditions
users = session.execute(
    select(User).where(
        or_(User.username == "alice", User.username == "bob")
    )
).scalars().all()

# NOT condition
users = session.execute(
    select(User).where(not_(User.banned == True))
).scalars().all()

# IN clause
users = session.execute(
    select(User).where(User.id.in_([1, 2, 3, 4, 5]))
).scalars().all()

# BETWEEN
users = session.execute(
    select(User).where(User.age.between(18, 65))
).scalars().all()

# LIKE patterns
users = session.execute(
    select(User).where(User.username.like("a%"))  # Starts with 'a'
).scalars().all()

users = session.execute(
    select(User).where(User.email.ilike("%@gmail.com"))  # Case-insensitive
).scalars().all()

# IS NULL / IS NOT NULL
incomplete = session.execute(
    select(User).where(User.middle_name.is_(None))
).scalars().all()

complete = session.execute(
    select(User).where(User.middle_name.isnot(None))
).scalars().all()
```

### Ordering and Limiting

```python
from sqlalchemy import desc, asc

# Order by single column
users = session.execute(
    select(User).order_by(User.username)
).scalars().all()

# Descending order
users = session.execute(
    select(User).order_by(desc(User.created_at))
).scalars().all()

# Multiple columns
users = session.execute(
    select(User).order_by(User.last_name, asc(User.first_name))
).scalars().all()

# Limit results
top_users = session.execute(
    select(User).order_by(User.score.desc()).limit(10)
).scalars().all()

# Pagination
page_size = 20
page_number = 2
users = session.execute(
    select(User)
    .order_by(User.id)
    .offset((page_number - 1) * page_size)
    .limit(page_size)
).scalars().all()
```

## Eager Loading Strategies

### The N+1 Problem

```python
# BAD: Causes N+1 queries
users = session.execute(select(User)).scalars().all()
for user in users:
    for post in user.posts:  # Query per user!
        print(post.title)

# GOOD: Use eager loading
from sqlalchemy.orm import selectinload

stmt = (
    select(User)
    .options(selectinload(User.posts))
)
users = session.execute(stmt).scalars().all()
for user in users:
    for post in user.posts:  # Posts already loaded!
        print(post.title)
```

### Selectin Load (Recommended)

Efficient IN query for relationships:

```python
from sqlalchemy.orm import selectinload

# Load single relationship
stmt = (
    select(User)
    .options(selectinload(User.posts))
)

# Load nested relationships
stmt = (
    select(User)
    .options(
        selectinload(User.posts).selectinload(Post.comments)
    )
)

# Multiple relationships
stmt = (
    select(User)
    .options(
        selectinload(User.posts),
        selectinload(User.profile)
    )
)

# With filter on relationship
stmt = (
    select(User)
    .options(
        selectinload(User.posts).where(Post.is_published == True)
    )
)

# With ordering and limit
stmt = (
    select(User)
    .options(
        selectinload(User.posts)
        .order_by(Post.created_at.desc())
        .limit(5)
    )
)
```

### Joined Load

JOIN with parent query:

```python
from sqlalchemy.orm import joinedload

# Simple joined load
stmt = (
    select(User)
    .options(joinedload(User.posts))
)

# Nested joined load
stmt = (
    select(User)
    .options(
        joinedload(User.posts).joinedload(Post.comments)
    )
)

# Warning: Can cause row duplication with multiple collections
# Use selectinload for multiple collection relationships
```

### Subquery Load

Similar to selectinload with correlated subquery:

```python
from sqlalchemy.orm import subqueryload

stmt = (
    select(User)
    .options(subqueryload(User.posts))
)
```

### Lazy Loading Options

Control per-query:

```python
from sqlalchemy.orm import lazyload, noload, raiseload

# Don't load specific relationship
stmt = (
    select(User)
    .options(noload(User.posts))
)

# Raise error if accessed when not loaded
stmt = (
    select(User)
    .options(raiseload(User.posts))
)

# Load lazily (separate query on access)
stmt = (
    select(User)
    .options(lazyload(User.profile))
)
```

## Querying with Joins

### Explicit Joins

```python
from sqlalchemy import select

# Join User and Post
stmt = (
    select(User, Post)
    .join(Post, User.id == Post.author_id)
)

result = session.execute(stmt)
for user, post in result:
    print(user.username, post.title)

# With filter on joined table
stmt = (
    select(User)
    .join(Post, User.id == Post.author_id)
    .where(Post.title.like("%SQL%"))
)

users = session.execute(stmt).scalars().unique().all()
```

### Join with Eager Loading

```python
from sqlalchemy.orm import selectinload

# Join and eager load other relationships
stmt = (
    select(User)
    .join(Post, User.id == Post.author_id)
    .where(Post.is_published == True)
    .options(selectinload(User.profile))
)

users = session.execute(stmt).scalars().unique().all()
```

## Aggregations and Grouping

### Aggregate Functions

```python
from sqlalchemy import func

# Count
user_count = session.execute(
    select(func.count(User.id))
).scalar()

# Sum
total_views = session.execute(
    select(func.sum(Post.view_count))
).scalar()

# Average
avg_age = session.execute(
    select(func.avg(User.age))
).scalar()

# Min/Max
oldest, youngest = session.execute(
    select(func.max(User.age), func.min(User.age))
).one()
```

### Group By

```python
from sqlalchemy import func

# Count users per department
stmt = (
    select(User.department, func.count(User.id).label("count"))
    .group_by(User.department)
)

result = session.execute(stmt)
for dept, count in result:
    print(f"{dept}: {count} users")

# Multiple columns
stmt = (
    select(
        User.department,
        User.role,
        func.count(User.id).label("count"),
        func.avg(User.age).label("avg_age")
    )
    .group_by(User.department, User.role)
)
```

### Having Clause

```python
from sqlalchemy import func

# Filter groups
stmt = (
    select(
        User.department,
        func.count(User.id).label("count")
    )
    .group_by(User.department)
    .having(func.count(User.id) > 10)
)

result = session.execute(stmt)
for dept, count in result:
    print(f"{dept}: {count} users")
```

## Subqueries and CTEs

### Scalar Subquery

```python
from sqlalchemy import select, func

# Subquery in WHERE clause
avg_salary = (
    select(func.avg(Employee.salary))
    .scalar_subquery()
)

stmt = (
    select(Employee)
    .where(Employee.salary > avg_salary)
)

above_avg = session.execute(stmt).scalars().all()

# Subquery in SELECT clause
dept_avg = (
    select(func.avg(Employee.salary))
    .where(Employee.department == Employee.department)  # Correlated
    .correlate(Employee)
    .scalar_subquery()
)

stmt = (
    select(
        Employee.name,
        Employee.salary,
        dept_avg.label("department_avg")
    )
)
```

### EXISTS Subquery

```python
from sqlalchemy import exists

# Users who have posts
stmt = (
    select(User)
    .where(
        exists().where(Post.author_id == User.id)
    )
)

active_users = session.execute(stmt).scalars().all()

# Users without posts
stmt = (
    select(User)
    .where(
        ~exists().where(Post.author_id == User.id)
    )
)

inactive_users = session.execute(stmt).scalars().all()
```

### Common Table Expressions (CTEs)

```python
from sqlalchemy import cte

# Simple CTE
user_cte = cte(
    select(User.id, User.username)
    .where(User.active == True)
    .cte("active_users")
)

stmt = (
    select(user_cte)
    .where(user_cte.c.username.like("a%"))
)

# Recursive CTE for hierarchical data
from sqlalchemy import column

# Base case: top-level categories
root_categories = (
    select(Category.id, Category.name, Category.parent_id, literal(0).label("depth"))
    .where(Category.parent_id.is_(None))
)

# Recursive case: child categories
child_categories = (
    select(
        Category.id,
        Category.name,
        Category.parent_id,
        cte("categories").c.depth + 1
    )
    .where(Category.parent_id == cte("categories").c.id)
)

# Combine into recursive CTE
category_cte = root_categories.union_all(child_categories).cte("categories", recursive=True)

stmt = select(category_cte)
```

## Advanced Query Patterns

### Union and Set Operations

```python
from sqlalchemy import select

# UNION (distinct)
stmt1 = select(User.username).where(User.active == True)
stmt2 = select(Admin.username).where(Admin.active == True)

union_stmt = stmt1.union(stmt2)

# UNION ALL (no deduplication)
union_all_stmt = stmt1.union_all(stmt2)

# INTERSECT
intersect_stmt = stmt1.intersect(stmt2)

# EXCEPT
except_stmt = stmt1.except_(stmt2)

result = session.execute(union_stmt)
```

### Case Expressions

```python
from sqlalchemy import case

# Simple case
age_group = case(
    (User.age < 13, "child"),
    (User.age < 20, "teen"),
    (User.age < 65, "adult"),
    else_="senior"
)

stmt = (
    select(User.username, age_group.label("age_group"))
)

# Case in WHERE clause
stmt = (
    select(User)
    .where(
        case(
            (User.age >= 18, User.age),
            else_=None
        ).isnot(None)
    )
)
```

### Window Functions

```python
from sqlalchemy import over, row_number, rank, dense_rank

# Row number
stmt = (
    select(
        User.username,
        User.salary,
        row_number().over(
            order_by=User.salary.desc()
        ).label("rank")
    )
)

# Partitioned window
stmt = (
    select(
        User.department,
        User.username,
        User.salary,
        row_number().over(
            partition_by=User.department,
            order_by=User.salary.desc()
        ).label("dept_rank")
    )
)

# Running total
stmt = (
    select(
        User.username,
        func.sum(User.salary).over(
            order_by=User.username
        ).label("running_total")
    )
)

# Lag/Lead
from sqlalchemy import lag, lead

stmt = (
    select(
        User.username,
        User.salary,
        lag(User.salary).over(order_by=User.username).label("prev_salary"),
        lead(User.salary).over(order_by=User.username).label("next_salary")
    )
)
```

## Polymorphic Queries

### Query Base Class

```python
# Get all employee types
employees = session.execute(
    select(Employee)
).scalars().all()

# Returns mix of Engineer, Manager, etc. instances
for emp in employees:
    print(type(emp).__name__, emp.name)
```

### Query Specific Subclass

```python
# Get only engineers
engineers = session.execute(
    select(Engineer)
).scalars().all()

# Get only managers
managers = session.execute(
    select(Manager)
).scalars().all()
```

### Polymorphic Loading

```python
from sqlalchemy.orm import polymorphic_load, EagerLoad

# Load all subclasses eagerly
stmt = (
    select(Employee)
    .options(polymorphic_load(EagerLoad))
)

employees = session.execute(stmt).scalars().all()

# Load specific subclasses
from sqlalchemy.orm import with_polymorphic

stmt = (
    select(Employee)
    .options(
        with_polymorphic(Engineer, "engineer").load_only(Engineer.programming_language)
    )
)
```

## Query Performance Tips

### 1. Use indexes on filtered columns

```python
# Add index for frequently filtered column
username = Column(String(50), index=True)
```

### 2. Select only needed columns

```python
from sqlalchemy import select

# Don't load unnecessary columns
stmt = (
    select(User.id, User.username)
    .where(User.active == True)
)
```

### 3. Use hints for database-specific optimizations

```python
# PostgreSQL index hint
stmt = (
    select(User)
    .index_hint(User, "ix_users_username")
)

# MySQL SQL_BUFFER_RESULT
stmt = (
    select(User)
    .prefix_with("SQL_BUFFER_RESULT", dialect="mysql")
)
```

### 4. Use streaming for large result sets

```python
# Don't load all at once
result = session.execute(
    select(User).yield_per(100)
)

for user in result.scalars():
    process(user)  # Process one at a time
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
        session.flush()
    
    return user
```

### Search with Multiple Terms

```python
from sqlalchemy import or_

def search_users(session, query):
    search_term = f"%{query}%"
    
    stmt = (
        select(User)
        .where(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
        .limit(50)
    )
    
    return session.execute(stmt).scalars().all()
```

### Count with Filter

```python
from sqlalchemy import func

def count_active_users(session):
    count = session.execute(
        select(func.count(User.id))
        .where(User.active == True)
    ).scalar()
    
    return count
```

## Next Steps

- [Hybrid Attributes](10-orm-hybrid-attributes.md) - Property expressions in queries
- [ORM Extensions](11-orm-extensions.md) - Advanced ORM features
- [Core Querying](04-core-querying.md) - Low-level query construction
- [Best Practices](24-best-practices.md) - Performance optimization
