# Making Queries

## Prerequisites

Before querying models, you need:

1. An indexed model — add `index=True` to the model class
2. Run migrations — execute `om migrate` to create RediSearch indexes

```python
from redis_om import HashModel, Field


class Customer(HashModel, index=True):
    first_name: str
    last_name: str = Field(index=True)
    email: str
    age: int = Field(index=True, sortable=True)
```

```bash
om migrate
```

## The find() Method

`find()` is the entry point for all queries. It returns a `FindQuery` object that supports method chaining:

```python
# Find all customers
customers = await Customer.find().all()

# Find with a filter
customers = await Customer.find(Customer.last_name == "Brookins").all()

# Multiple conditions (AND)
customers = await Customer.find(
    Customer.last_name == "Brookins",
    Customer.age > 30
).all()
```

## Comparison Operators

```python
# Equal
Customer.find(Customer.name == "John").all()

# Not equal
Customer.find(Customer.name != "John").all()

# Less than / greater than (numeric fields)
Customer.find(Customer.age < 30).all()
Customer.find(Customer.age >= 65).all()

# Less than or equal / greater than or equal
Customer.find(Customer.age <= 30).all()
Customer.find(Customer.age > 30).all()
```

## String Operators

```python
# Pattern matching (LIKE) — use % operator
Customer.find(Customer.last_name % "Brook*").all()

# Starts with
Customer.find(Customer.email.startswith("andrew")).all()

# Ends with
Customer.find(Customer.name.endswith("son")).all()

# Contains substring
Customer.find(Customer.email.contains("@example.com")).all()
```

## Collection Operators

```python
# IN — value in list (use << operator)
active = await Customer.find(
    Customer.status << ["active", "pending"]
).all()

# NOT IN (use >> operator)
good_standing = await Customer.find(
    Customer.status >> ["banned", "suspended"]
).all()
```

Note: List/tuple fields can only contain strings when indexed.

## Combining Expressions

### AND (&)

```python
customers = await Customer.find(
    (Customer.first_name == "John") & (Customer.age < 30)
).all()
```

### OR (|)

```python
customers = await Customer.find(
    (Customer.age < 30) | (Customer.first_name == "John")
).all()
```

### NOT (~)

```python
customers = await Customer.find(
    ~(Customer.first_name == "John")
).all()
```

### Complex Expressions

Use parentheses to group:

```python
customers = await Customer.find(
    ~(Customer.first_name == "Andrew") &
    ((Customer.last_name == "Brookins") | (Customer.last_name == "Smith"))
).all()
```

### Visualizing Expression Trees

Use `expression.tree` to see how Redis OM interprets your query:

```python
query = Customer.find(
    ~(Customer.first_name == "Andrew") &
    ((Customer.last_name == "Brookins") | (Customer.last_name == "Smith"))
)
print(query.expression.tree)
"""
       ┌first_name
┌NOT EQ┤
|      └Andrew
 AND┤
    |     ┌last_name
    |  ┌EQ┤
    |  |  └Brookins
    └OR┤
       |  ┌last_name
       └EQ┤
          └Smith
"""
```

## Terminal Methods

### all() — Get All Results

```python
customers = await Customer.find(Customer.age > 30).all()
```

### first() — Get First Result

Returns the first match or raises `NotFoundError`:

```python
from redis_om import NotFoundError

try:
    customer = await Customer.find(
        Customer.email == "john@example.com"
    ).first()
except NotFoundError:
    print("No customer found")
```

### count() — Count Without Loading

```python
count = await Customer.find(Customer.age > 30).count()
```

### page() — Paginated Results

```python
# First 10 results
first_page = await Customer.find().sort_by("age").page(offset=0, limit=10)

# Next 10
second_page = await Customer.find().sort_by("age").page(offset=10, limit=10)
```

Always use `.sort_by()` before `.page()` for stable pagination. Without explicit sorting, Redis does not guarantee consistent ordering between pages.

## Sorting Results

Use `.sort_by()`. Prefix with `-` for descending:

```python
# Ascending
await Customer.find().sort_by("age").all()

# Descending
await Customer.find().sort_by("-age").all()

# Multiple fields
await Customer.find().sort_by("last_name", "-age").all()
```

Fields must be marked `sortable=True` in the model:

```python
class Customer(HashModel, index=True):
    name: str
    age: int = Field(sortable=True)
```

## Field Projection

### values() — Dictionary Results

Returns dictionaries instead of model instances:

```python
# All fields as dicts
customers = await Customer.find().values().all()
# [{"first_name": "John", "last_name": "Doe", ...}]

# Specific fields only
customers = await Customer.find().values("first_name", "email").all()
# [{"first_name": "John", "email": "john@example