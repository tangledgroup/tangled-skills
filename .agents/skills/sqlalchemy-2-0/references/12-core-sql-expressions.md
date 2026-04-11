# Core SQL Expression Language

## Overview of SQL Expressions

SQLAlchemy's Core provides a comprehensive SQL Expression Language for building SQL queries programmatically with type safety and composability.

```python
from sqlalchemy import select, insert, update, delete, table, column, literal

# Build complex queries using Python objects
stmt = (
    select(users.c.id, users.c.username)
    .where(users.c.age >= 18)
    .order_by(users.c.username)
    .limit(10)
)
```

## Column Expressions

### Basic Operations

```python
from sqlalchemy import Column, Integer, String

# Arithmetic
age_plus_one = users.c.age + 1
total_price = products.c.quantity * products.c.price
average = scores.c.total / scores.c.count

# Comparison
is_adult = users.c.age >= 18
in_range = users.c.age.between(18, 65)
equals = users.c.status == "active"

# String operations
full_name = users.c.first_name + " " + users.c.last_name
upper_name = func.upper(users.c.username)
substring = func.substr(users.c.email, 1, 5)

# Boolean logic
from sqlalchemy import and_, or_, not_

complex_condition = and_(
    users.c.age >= 18,
    users.c.active == True,
    or_(users.c.role == "admin", users.c.role == "moderator")
)
```

### Null Handling

```python
from sqlalchemy import null, true, false

# IS NULL / IS NOT NULL
is_null = users.c.middle_name.is_(None)
is_not_null = users.c.middle_name.isnot(None)

# COALESCE (NULL coalescing)
from sqlalchemy import func

display_name = func.coalesce(users.c.display_name, users.c.username)

# NULLIF (return NULL if equal)
from sqlalchemy import nullif

safe_divisor = nullif(scores.c.denominator, 0)
```

### Type Casting

```python
from sqlalchemy import cast, type_coerce
from sqlalchemy.types import String, Integer, DateTime

# Cast expression to different type
age_as_string = cast(users.c.age, String)
text_to_int = cast(products.c.code, Integer)

# Force type without SQL CAST
typed_literal = type_coerce("2024-01-01", DateTime)
```

## Table Expressions

### Table Aliases

```python
from sqlalchemy import alias

# Create alias for self-join
manager = users.alias("managers")
employee = users.alias("employees")

stmt = (
    select(employee.c.username, manager.c.username.label("manager_name"))
    .where(employee.c.manager_id == manager.c.id)
)

# Multiple aliases of same table
this_year = sales.alias("this_year")
last_year = sales.alias("last_year")

stmt = (
    select(
        this_year.c.product_id,
        this_year.c.total - last_year.c.total.label("growth")
    )
    .where(this_year.c.year == 2024)
    .join(last_year, and_(
        this_year.c.product_id == last_year.c.product_id,
        last_year.c.year == 2023
    ))
)
```

### Table Joins

```python
from sqlalchemy import join, outerjoin, fullouterjoin

# INNER JOIN
join_obj = users.join(posts, users.c.id == posts.c.author_id)
stmt = select(users, posts).select_from(join_obj)

# LEFT OUTER JOIN
left_join = users.outerjoin(posts, users.c.id == posts.c.author_id)
stmt = select(users, posts).select_from(left_join)

# Multiple joins
complex_join = (
    users
    .join(posts, users.c.id == posts.c.author_id)
    .join(comments, posts.c.id == comments.c.post_id)
)

# Full outer join (PostgreSQL)
full_join = left_table.full_outer_join(
    right_table, 
    left_table.c.id == right_table.c.left_id
)
```

### Table Operations

```python
from sqlalchemy import union, union_all, intersect, except_

# UNION (distinct)
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

## Function Expressions

### Built-in Functions

```python
from sqlalchemy import func

# Aggregate functions
user_count = func.count(users.c.id)
total_sales = func.sum(sales.c.amount)
avg_price = func.avg(products.c.price)
max_date = func.max(events.c.date)
min_date = func.min(events.c.date)

# String functions
upper_name = func.upper(users.c.username)
lower_email = func.lower(users.c.email)
length = func.length(posts.c.content)
concat = func.concat(users.c.first_name, " ", users.c.last_name)

# Date functions
current_date = func.current_date()
now = func.now()
extract_year = func.extract("year", events.c.created_at)
date_trunc = func.date_trunc("month", transactions.c.timestamp)

# Math functions
absolute = func.abs(scores.c.difficulty - scores.c.target)
sqrt = func.sqrt(numbers.c.value)
round_val = func.round(decimal.c.amount, 2)

# Conditional functions
coalesce = func.coalesce(users.c.display_name, users.c.username)
greatest = func.greatest(scores.c.score1, scores.c.score2, scores.c.score3)
least = func.least(prices.c.price1, prices.c.price2, prices.c.price3)
```

### Custom Functions

```python
from sqlalchemy import func, FunctionElement

# Use database-specific functions
# PostgreSQL array function
array_agg = func.array_agg(posts.c.id)

# PostgreSQL JSON functions
json_extract = func.json_extract(data.c.json_data, '$.field')

# MySQL specific
group_concat = func.group_concat(posts.c.title.separator(", "))

# Oracle specific
sysdate = func.sys_date()
```

### Aggregates with Filter

```python
from sqlalchemy import func

# PostgreSQL FILTER clause
active_count = (
    func.count(users.c.id)
    .filter(users.c.active == True)
)

# Count by category
sales_by_status = (
    select(
        orders.c.status,
        func.sum(orders.c.total).label("total_sales")
    )
    .group_by(orders.c.status)
)
```

## Case Expressions

### Simple CASE

```python
from sqlalchemy import case

# Column-based case
age_group = case(
    (users.c.age < 13, "child"),
    (users.c.age < 20, "teen"),
    (users.c.age < 65, "adult"),
    else_="senior"
)

stmt = select(users.c.username, age_group.label("age_group"))

# Search-list case
status_label = case(
    ((users.c.status == "P", "Pending"), (users.c.status == "C", "Completed")),
    else_=users.c.status
)
```

### SEARCHED CASE

```python
from sqlalchemy import case

# Expression-based case
discount = case(
    (orders.c.total > 1000, orders.c.total * 0.1),
    (orders.c.total > 500, orders.c.total * 0.05),
    else_=0
)

stmt = select(
    orders.c.id,
    orders.c.total,
    discount.label("discount"),
    (orders.c.total - discount).label("final_total")
)
```

### CASE in Updates

```python
from sqlalchemy import case, update

# Update with case expression
stmt = (
    update(users)
    .values(
        age_group=case(
            (users.c.age < 13, "child"),
            (users.c.age < 20, "teen"),
            else_="adult"
        )
    )
)
```

## Window Functions

### Basic Window Functions

```python
from sqlalchemy import over, row_number, rank, dense_rank

# Row number across all rows
stmt = (
    select(
        users.c.username,
        users.c.salary,
        row_number().over(order_by=users.c.salary.desc()).label("rank")
    )
)

# Rank with ties
stmt = (
    select(
        users.c.department,
        users.c.username,
        rank().over(
            partition_by=users.c.department,
            order_by=users.c.salary.desc()
        ).label("dept_rank")
    )
)

# Dense rank (no gaps)
stmt = (
    select(
        users.c.username,
        dense_rank().over(
            order_by=users.c.salary.desc()
        ).label("dense_rank")
    )
)
```

### Aggregate Window Functions

```python
from sqlalchemy import func, over

# Running total
stmt = (
    select(
        transactions.c.date,
        transactions.c.amount,
        func.sum(transactions.c.amount).over(
            order_by=transactions.c.date
        ).label("running_total")
    )
)

# Moving average (last 7 days)
stmt = (
    select(
        sales.c.date,
        sales.c.revenue,
        func.avg(sales.c.revenue).over(
            order_by=sales.c.date,
            rows_between=(7, 0)  # Last 7 rows including current
        ).label("moving_avg")
    )
)

# Compare to previous/next
from sqlalchemy import lag, lead

stmt = (
    select(
        sales.c.date,
        sales.c.revenue,
        lag(sales.c.revenue).over(order_by=sales.c.date).label("prev_revenue"),
        lead(sales.c.revenue).over(order_by=sales.c.date).label("next_revenue")
    )
)
```

### Window Frame Specifications

```python
from sqlalchemy import over, func

# Rows frame (default)
running_total = func.sum(sales.c.amount).over(
    order_by=sales.c.date,
    rows_between=(None, 0)  # From start to current row
)

# Range frame
range_sum = func.sum(sales.c.amount).over(
    order_by=sales.c.amount,
    range_between=(None, 0)  # All values <= current
)

# Fixed window (last 3 rows)
moving_avg = func.avg(sales.c.amount).over(
    order_by=sales.c.date,
    rows_between=(2, 0)  # Current and 2 preceding
)
```

## Subqueries

### Scalar Subquery

```python
from sqlalchemy import select, func

# Subquery returns single value
avg_salary = (
    select(func.avg(employees.c.salary))
    .where(employees.c.department == "Engineering")
    .scalar_subquery()
)

stmt = (
    select(
        employees.c.name,
        employees.c.salary,
        avg_salary.label("dept_avg")
    )
    .where(employees.c.salary > avg_salary)
)
```

### Correlated Subquery

```python
from sqlalchemy import select

# Subquery correlated to outer query
dept_avg = (
    select(func.avg(employees.c.salary))
    .where(employees.c.department == Employee.department)  # Correlation
    .correlate(Employee)  # Explicit correlation
    .scalar_subquery()
)

stmt = (
    select(
        Employee.name,
        Employee.salary,
        dept_avg.label("department_average")
    )
)
```

### EXISTS Subquery

```python
from sqlalchemy import exists

# Users who have at least one post
stmt = (
    select(users)
    .where(
        exists().where(posts.c.author_id == users.c.id)
    )
)

# Users without posts
stmt = (
    select(users)
    .where(
        ~exists().where(posts.c.author_id == users.c.id)
    )
)

# EXISTS with conditions
stmt = (
    select(users)
    .where(
        exists().where(
            and_(
                posts.c.author_id == users.c.id,
                posts.c.is_published == True
            )
        )
    )
)
```

### Lateral Join (PostgreSQL)

```python
from sqlalchemy import lateral

# Get top 3 posts per user
top_posts = (
    select(posts.c.author_id, posts.c.title, posts.c.view_count)
    .where(posts.c.author_id == users.c.id)
    .order_by(posts.c.view_count.desc())
    .limit(3)
    .lateral()
)

stmt = select(users, top_posts).select_from(users)
```

## Common Table Expressions (CTEs)

### Simple CTE

```python
from sqlalchemy import cte

# Define CTE
active_users = (
    select(users.c.id, users.c.username)
    .where(users.c.active == True)
    .cte("active_users")
)

# Use in main query
stmt = (
    select(active_users)
    .where(active_users.c.username.like("a%"))
)

# Or join with other tables
stmt = (
    select(active_users, posts)
    .join(posts, active_users.c.id == posts.c.author_id)
)
```

### Recursive CTE

```python
from sqlalchemy import cte, column

# Base case: root categories
root_categories = (
    select(
        categories.c.id,
        categories.c.name,
        categories.c.parent_id,
        literal(0).label("depth")
    )
    .where(categories.c.parent_id.is_(None))
)

# Recursive case: child categories
child_categories = (
    select(
        categories.c.id,
        categories.c.name,
        categories.c.parent_id,
        cte("category_tree").c.depth + 1
    )
    .where(categories.c.parent_id == cte("category_tree").c.id)
)

# Combine into recursive CTE
category_tree = root_categories.union_all(child_categories).cte(
    "category_tree",
    recursive=True
)

stmt = select(category_tree).order_by(category_tree.c.depth)
```

### Materialized CTEs

```python
from sqlalchemy import cte

# Force materialization (PostgreSQL)
user_stats = (
    select(
        users.c.id,
        func.count(posts.c.id).label("post_count")
    )
    .outerjoin(posts)
    .group_by(users.c.id)
    .cte("user_stats", materialized=True)  # Materialize
)

stmt = select(user_stats).where(user_stats.c.post_count > 10)
```

## Advanced Expression Techniques

### Inline Expressions

```python
from sqlalchemy import expression

# Create column expression inline
expr = column("username", String)

# Use in select
stmt = select(expr).select_from(users)
```

### Text Expressions

```python
from sqlalchemy import text

# Raw SQL fragment (use carefully!)
raw_filter = text("users.c.age >= :min_age")

# Or use text for dialect-specific syntax
pg_array = text("'{1,2,3}'::integer[]")
```

### Compound Expressions

```python
from sqlalchemy import and_, or_, not_

# Complex boolean logic
complex_filter = and_(
    users.c.age >= 18,
    or_(
        users.c.role == "admin",
        and_(
            users.c.active == True,
            users.c.verified == True
        )
    ),
    not_(users.c.banned == True)
)

stmt = select(users).where(complex_filter)
```

## Best Practices

### 1. Use Expressions for Type Safety

```python
# Good - type-safe, composable
stmt = select(users).where(users.c.age >= 18)

# Avoid - raw SQL strings (lose type safety)
stmt = text("SELECT * FROM users WHERE age >= 18")
```

### 2. Compose Expressions Reusably

```python
# Define reusable expression
is_adult = users.c.age >= 18
is_active = users.c.active == True

# Use in multiple queries
adults = select(users).where(is_adult)
active_adults = select(users).where(and_(is_adult, is_active))
```

### 3. Use Aliases for Complex Queries

```python
# Clear aliases improve readability
this_year = sales.alias("ty")
last_year = sales.alias("ly")

growth_query = (
    select(
        this_year.c.product_id,
        (this_year.c.total - last_year.c.total).label("growth")
    )
    .join(last_year, this_year.c.product_id == last_year.c.product_id)
)
```

## Next Steps

- [Core Querying](04-core-querying.md) - Complete query construction
- [Core Reflection](13-core-reflection.md) - Schema introspection
- [Custom Types](15-core-custom-types.md) - Type engineering
- [Dialects](16-dialects-overview.md) - Database-specific expressions
