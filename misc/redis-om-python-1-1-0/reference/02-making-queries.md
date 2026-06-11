# Making Queries

## Prerequisites

Before querying, ensure:

1. Model has `index=True` on the class declaration
2. Migrations have been run (`om migrate`) to create the RediSearch index

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

# Find with a filter expression
customers = await Customer.find(Customer.last_name == "Brookins").all()

# Multiple expressions (AND)
customers = await Customer.find(
    Customer.last_name == "Brookins",
    Customer.age > 30,
).all()
```

## Expression Operators

### Comparison Operators

- `==` — equal: `Customer.name == "John"`
- `!=` — not equal: `Customer.name != "John"`
- `<`, `<=`, `>`, `>=` — numeric comparisons

```python
young = await Customer.find(Customer.age < 30).all()
seniors = await Customer.find(Customer.age >= 65).all()
johns = await Customer.find(Customer.first_name == "John").all()
```

### String Operators

- `%` — LIKE pattern matching: `Customer.name % "John*"`
- `.startswith()` — starts with: `Customer.name.startswith("Jo")`
- `.endswith()` — ends with: `Customer.name.endswith("son")`
- `.contains()` — contains substring: `Customer.email.contains("@example.com")`

```python
customers = await Customer.find(Customer.last_name % "Brook*").all()
customers = await Customer.find(Customer.email.startswith("andrew")).all()
customers = await Customer.find(Customer.email.contains("@gmail")).all()
```

### Collection Operators

- `<<` — IN (value in list): `Customer.status << ["active", "pending"]`
- `>>` — NOT IN: `Customer.status >> ["banned", "deleted"]`

```python
active = await Customer.find(Customer.status << ["active", "pending"]).all()
good_standing = await Customer.find(Customer.status >> ["banned", "suspended"]).all()
```

### Combining Expressions

- `&` — AND
- `|` — OR
- `~` — NOT

```python
# AND
customers = await Customer.find(
    (Customer.first_name == "John") & (Customer.age < 30)
).all()

# OR
customers = await Customer.find(
    (Customer.age < 30) | (Customer.first_name == "John")
).all()

# NOT
customers = await Customer.find(
    ~(Customer.first_name == "John")
).all()

# Complex: NOT Andrew AND (Brookins OR Smith)
customers = await Customer.find(
    ~(Customer.first_name == "Andrew") & (
        (Customer.last_name == "Brookins") | (Customer.last_name == "Smith")
    )
).all()
```

### Visualizing Expression Trees

Use the `tree` property to see how Redis OM interprets a query:

```python
query = Customer.find(
    ~(Customer.first_name == "Andrew") & (
        (Customer.last_name == "Brookins") | (Customer.last_name == "Smith")
    )
)
print(query.expression.tree)
```

## Terminal Methods

### .all() — Get All Results

Returns all matching model instances:

```python
customers = await Customer.find(Customer.age > 30).all()
```

### .first() — Get First Result

Returns the first matching model or raises `NotFoundError`:

```python
from redis_om import NotFoundError

try:
    customer = await Customer.find(Customer.email == "john@example.com").first()
except NotFoundError:
    print("No customer found")
```

### .count() — Count Results

Returns the count without loading all results:

```python
count = await Customer.find(Customer.age > 30).count()
print(f"Found {count} customers over 30")
```

### .page() — Paginated Results

```python
first_page = await Customer.find().sort_by("age").page(offset=0, limit=10)
second_page = await Customer.find().sort_by("age").page(offset=10, limit=10)
```

Always use `.sort_by()` before `.page()` for stable pagination. Without explicit sorting, Redis does not guarantee consistent ordering between pages.

## Sorting Results

Use `.sort_by()`. Prefix with `-` for descending:

```python
# Ascending
customers = await Customer.find().sort_by("age").all()
# Descending
customers = await Customer.find().sort_by("-age").all()
# Multiple fields
customers = await Customer.find().sort_by("last_name", "-age").all()
```

Fields must be marked `sortable=True` in the model definition.

## Field Projection

### .values() — Dictionary Results

Returns results as dictionaries instead of model instances:

```python
# All fields as dicts
customers = await Customer.find().values().all()
# Specific fields only
customers = await Customer.find().values("first_name", "email").all()
```

### .only() — Partial Model Instances

Returns partial models with only specified fields. Accessing unloaded fields raises `AttributeError`:

```python
customers = await Customer.find().only("first_name", "email").all()
for c in customers:
    print(c.first_name)  # Works
    print(c.age)         # Raises AttributeError
```

### Deep Field Projection (JsonModel)

Access nested fields with double underscore syntax:

```python
customers = await Customer.find().values("name", "address__city").all()
# Returns: [{"name": "John", "address__city": "New York"}]
```

## Bulk Operations

### .update() — Update Multiple Records

```python
await Customer.find(Customer.tier == "premium").update(discount_percent=20)
```

### .delete() — Delete Multiple Records

```python
deleted_count = await Customer.find(Customer.status == "inactive").delete()
```

## Vector Similarity Search

Use `KNNExpression` for vector search:

```python
from redis_om import KNNExpression

query_embedding = get_embedding("search query")
results = await Document.find(
    KNNExpression(
        k=10,
        vector_field_name="embedding",
        reference_vector=query_embedding,
    )
).all()
```

### Hybrid Vector + Filter Queries

Combine vector search with traditional filters:

```python
results = await Document.find(
    (Document.category == "technology") & KNNExpression(
        k=10,
        vector_field_name="embedding",
        reference_vector=query_embedding,
    )
).all()
```

### Advanced Vector Search with RedisVL

For advanced vector capabilities, integrate with RedisVL:

```python
from aredis_om.redisvl import get_redisvl_index
from redisvl.query import VectorQuery

index = get_redisvl_index(Document)
results = await index.query(
    VectorQuery(
        vector=query_embedding,
        vector_field_name="embedding",
        num_results=10,
        return_fields=["title", "content"],
    )
)
```

RedisVL provides `VectorQuery` with hybrid policies (BATCHES, ADHOC_BF), `VectorRangeQuery` for epsilon-based searches, EF_RUNTIME tuning for HNSW indexes, and advanced filter expressions.

## Async Iteration

`FindQuery` objects support async iteration:

```python
async for customer in Customer.find(Customer.age > 30):
    print(customer.name)
```

## Index Access

Access specific results by index (0-indexed):

```python
query = Customer.find(Customer.age > 30)
fifth_customer = await query[4]
```

## Boolean Queries (JsonModel Only)

JsonModel supports querying boolean fields:

```python
class Product(JsonModel, index=True):
    name: str
    active: bool = Field(index=True)

active_products = await Product.find(Product.active == True).all()
```

Boolean queries are not supported with HashModel due to how Redis Hashes store data.

## Calling Raw Redis Commands

Use `.db()` on any model class or `get_redis_connection()`:

```python
from redis_om import HashModel, get_redis_connection

class Demo(HashModel):
    some_field: str

redis_conn = Demo.db()
redis_conn.sadd("myset", "a", "b", "c")
print(redis_conn.sismember("myset", "b"))  # True

# Or standalone:
redis_conn = get_redis_connection()
redis_conn.set("hello", "world")
```

## Query Debugging

### Getting the Raw Query

```python
query = Customer.find(Customer.age > 30)
print(query.query)  # Shows the RediSearch query string
```

### Getting Query Arguments

```python
args = await query.execute(return_query_args=True)
print(args)  # Shows all FT.SEARCH arguments
```

## Performance Tips

- Use field projection (`.values()` or `.only()`) when you don't need all fields
- Use `.count()` instead of `.all()` for counting
- Use pagination (`.page()`) for large result sets
- Mark fields as `sortable=True` only when needed — it increases memory usage
- Use TEXT fields for full-text search, TAG fields for exact matching

## Error Handling

### NotFoundError

Raised by `.first()` when no results match:

```python
from redis_om import NotFoundError

try:
    customer = await Customer.find(Customer.email == "x@y.com").first()
except NotFoundError:
    print("Not found")
```

### QueryNotSupportedError

Raised when a query expression is not supported by the current RediSearch version or module configuration.
