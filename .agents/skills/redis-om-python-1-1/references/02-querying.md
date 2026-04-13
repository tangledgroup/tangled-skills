# Querying with Redis OM

Comprehensive guide to querying Redis OM models using the fluent FindQuery API, including filters, sorting, pagination, and aggregation.

## Basic Query Syntax

Redis OM uses a fluent API with Python operators for building queries:

```python
from aredis_om import HashModel, Field

class Product(HashModel):
    name: str = Field(index=True)
    category: str = Field(index=True)
    price: float = Field(index=True, sortable=True)
    rating: float = Field(index=True, sortable=True)
    is_available: bool = Field(default=True, index=True)

# Find all products
all_products = await Product.find().all()

# Single filter
expensive = await Product.find(Product.price > 100).all()

# Multiple filters (AND)
available_expensive = await Product.find(
    (Product.is_available == True) & (Product.price > 100)
).all()

# OR condition
electronics_or_books = await Product.find(
    (Product.category == "electronics") | (Product.category == "books")
).all()
```

## Comparison Operators

Redis OM maps Python operators to RediSearch query expressions:

| Operator | Usage | Description |
|----------|-------|-------------|
| `==` | `field == value` | Equality |
| `!=` | `field != value` | Not equal |
| `<` | `field < value` | Less than |
| `<=` | `field <= value` | Less than or equal |
| `>` | `field > value` | Greater than |
| `>=` | `field >= value` | Greater than or equal |
| `%` | `field % pattern` | Full-text search / LIKE |
| `<` (shift left) | `field << [values]` | IN operator |
| `>` (shift right) | `field >> [values]` | NOT IN operator |

### Equality and Inequality

```python
# Exact match
electronics = await Product.find(Product.category == "electronics").all()

# Not equal
not_sold_out = await Product.find(Product.is_available != False).all()

# Multiple equality (AND)
specific_product = await Product.find(
    (Product.category == "electronics") & 
    (Product.is_available == True)
).all()
```

### Range Queries

```python
# Greater than
expensive = await Product.find(Product.price > 100).all()

# Less than
cheap = await Product.find(Product.price < 50).all()

# Between (inclusive)
mid_range = await Product.find(
    (Product.price >= 50) & (Product.price <= 150)
).all()

# Multiple range conditions
good_deals = await Product.find(
    (Product.price < 100) & (Product.rating >= 4.0)
).all()
```

### IN and NOT IN Operators

```python
# IN operator (left shift <<)
categories = ["electronics", "books", "clothing"]
products = await Product.find(Product.category << categories).all()

# NOT IN operator (right shift >>)
exclude_categories = ["discontinued", "clearance"]
active = await Product.find(Product.category >> exclude_categories).all()

# Combine with other filters
results = await Product.find(
    (Product.category << ["electronics", "books"]) & 
    (Product.price > 25)
).all()
```

### String Methods

```python
# Startswith
names_a = await Product.find(Product.name.startswith("Alpha")).all()

# Endswith
ends_corp = await Product.find(Product.name.endswith("Corp")).all()

# Contains
has_pro = await Product.find(Product.name.contains("Pro")).all()
```

## Full-Text Search

Use the modulo operator `%` for full-text search on fields with `full_text_search=True`:

```python
class Article(HashModel):
    title: str = Field(index=True, full_text_search=True)
    content: str = Field(index=True, full_text_search=True)
    tags: str = Field(index=True)  # TAG field (exact match only)

# Full-text search in title
python_articles = await Article.find(Article.title % "Python").all()

# Search in multiple fields (OR)
search_results = await Article.find(
    (Article.title % "database") | (Article.content % "database")
).all()

# Complex full-text query
tech_articles = await Article.find(
    (Article.title % "Redis OR MongoDB") & 
    (Article.content % "performance")
).all()
```

**Full-text search features:**
- Stemming (e.g., "running" matches "run")
- Case-insensitive matching
- Phrase search with quotes in some cases
- Works best with natural language content

## Boolean Logic

Combine conditions with `&` (AND), `|` (OR), and `~` (NOT):

```python
# AND (also use parentheses)
condition1 & condition2
(condition1) & (condition2)  # Explicit grouping

# OR
condition1 | condition2

# NOT (negation)
~(Product.category == "discontinued")
(Product.category != "discontinued")  # Equivalent

# Complex expressions
query = await Product.find(
    ((Product.category == "electronics") | (Product.category == "accessories")) &
    (Product.price >= 50) &
    (Product.price <= 200) &
    ~(Product.is_available == False)
).all()

# Using NOT_IN for cleaner exclusion
exclude = ["discontinued", "clearance", "out-of-stock"]
available = await Product.find(
    (Product.status >> exclude) & (Product.price > 0)
).all()
```

## Sorting

Use `sort_by()` to order results:

```python
# Sort by single field (ascending default)
by_price_asc = await Product.find().sort_by("price").all()

# Sort descending (prefix with -)
by_price_desc = await Product.find().sort_by("-price").all()

# Sort by rating (highest first)
top_rated = await Product.find().sort_by("-rating").all()

# Sort by date
newest_first = await Product.find().sort_by("-created_at").all()

# Combine with filters
expensive_sorted = await Product.find(
    Product.price > 100
).sort_by("-price").all()
```

**Requirements:** Field must have `sortable=True` for numeric/date sorting.

## Pagination

Use `page()` or `copy()` with offset/limit:

```python
# Page method (0-indexed)
page_1 = await Product.find().page(0, 20).all()  # First 20
page_2 = await Product.find().page(1, 20).all()  # Next 20
page_3 = await Product.find().page(2, 20).all()  # Third page

# Copy with offset/limit
offset = (page_number - 1) * page_size
results = await Product.find().copy(offset=offset, limit=page_size).all()

# Combine with sorting
paginated = await Product.find(
    Product.category == "electronics"
).sort_by("-price").page(0, 10).all()
```

### Cursor-Based Pagination

For large datasets, use the last ID for cursor-based pagination:

```python
# Get first page
page_1 = await Product.find().sort_by("-created_at").page(0, 20).all()

# Use last item's timestamp for next page
if page_1:
    last_created = page_1[-1].created_at
    page_2 = await Product.find(
        Product.created_at < last_created
    ).sort_by("-created_at").page(0, 20).all()
```

## Single Result Methods

### first() - Get First Match

```python
# Returns None if no match found
oldest_user = await User.find().sort_by("created_at").first()

if oldest_user:
    print(f"Oldest user: {oldest_user.username}")
else:
    print("No users found")

# With filter
admin = await User.find(User.role == "admin").first()
```

### get() - Retrieve by Primary Key

```python
# Direct retrieval by PK
product = await Product.get("01H5K8X9Y2Z3A4B5C6D7E8F9G0")

# With error handling
from aredis_om import NotFoundError

try:
    product = await Product.get("non-existent-pk")
except NotFoundError:
    print("Product not found")

# Check existence first
if await Product.exists("pk-value"):
    product = await Product.get("pk-value")
```

## Count Results

```python
# Total count
total = await Product.find().count()

# Filtered count
expensive_count = await Product.find(Product.price > 100).count()

# Category counts
electronics_count = await Product.find(
    Product.category == "electronics"
).count()
```

## Querying Embedded Models

Query nested fields using double underscore (`__`) syntax:

```python
class Address(EmbeddedJsonModel):
    street: str
    city: str = Field(index=True)
    state: str = Field(index=True)
    zip_code: str = Field(index=True)

class Order(JsonModel):
    customer_name: str = Field(index=True)
    shipping_address: Address
    billing_address: Optional[Address] = None

# Query embedded field directly
boston_orders = await Order.find(
    Order.shipping_address.city == "Boston"
).all()

# Multiple embedded field conditions
ma_orders = await Order.find(
    (Order.shipping_address.state == "MA") &
    (Order.shipping_address.city.startswith("Bos"))
).all()

# Query optional embedded fields
ny_billing = await Order.find(
    Order.billing_address.city == "New York"
).all()
```

## List Field Queries

Query array fields in JsonModel:

```python
class Product(JsonModel):
    name: str = Field(index=True)
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

# Find products with specific tag
tagged_sale = await Product.find(
    Product.tags == "sale"
).all()

# Note: List queries match if the value exists anywhere in the array
```

## Negation and Exclusion

```python
# Using != operator
not_electronics = await Product.find(Product.category != "electronics").all()

# Using NOT (~) operator
not_discontinued = await Product.find(
    ~(Product.status == "discontinued")
).all()

# Using NOT_IN (>> operator)
exclude_statuses = ["discontinued", "clearance", "hold"]
active_products = await Product.find(
    Product.status >> exclude_statuses
).all()

# Complex negation
not_low_rated_unavailable = await Product.find(
    ~(Product.rating < 3.0) & (Product.is_available == True)
).all()
```

## Query Chaining and Reuse

Build and reuse query objects:

```python
# Build base query
base_query = Product.find(Product.is_available == True)

# Reuse with different filters
expensive = await base_query.copy(Product.price > 100).all()
cheap = await base_query.copy(Product.price < 50).all()

# Chain operations
results = await (
    Product.find(Product.category == "electronics")
    .sort_by("-rating")
    .page(0, 20)
    .all()
)

# Store query for later execution
query = User.find(
    (User.age >= 18) & (User.is_active == True)
).sort_by("-created_at")

# Execute later with pagination
page_1 = await query.page(0, 10).all()
page_2 = await query.page(1, 10).all()
```

## Performance Considerations

1. **Index fields you query:** Non-indexed fields cannot be filtered efficiently
2. **Use sortable=True for sorting:** Sorting non-indexed fields is slow
3. **Paginate large result sets:** Always use page() for potentially large queries
4. **Prefer specific filters over post-filtering:** Filter in Redis, not in Python
5. **Use count() before .all():** Check if results exist before fetching all
6. **First() for single results:** More efficient than .all()[0]

## Common Query Patterns

### Search with Filters and Pagination

```python
async def search_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search_term: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "price",
):
    filters = []
    
    if category:
        filters.append(Product.category == category)
    
    if min_price is not None:
        filters.append(Product.price >= min_price)
    
    if max_price is not None:
        filters.append(Product.price <= max_price)
    
    if search_term:
        filters.append(Product.name % search_term)
    
    query = Product.find(*filters) if filters else Product.find()
    
    # Apply sorting
    query = query.sort_by(sort_by)
    
    # Apply pagination
    offset = (page - 1) * page_size
    results = await query.copy(offset=offset, limit=page_size).all()
    
    # Get total count
    total = await Product.find(*filters if filters else []).count()
    
    return {
        "results": [p.model_dump() for p in results],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

### Filter by Date Range

```python
from datetime import datetime, timedelta

# Orders from last 7 days
seven_days_ago = datetime.now() - timedelta(days=7)
recent_orders = await Order.find(
    Order.created_at >= seven_days_ago
).sort_by("-created_at").all()

# Orders in specific month
start_of_month = datetime(2024, 1, 1)
end_of_month = datetime(2024, 1, 31)
january_orders = await Order.find(
    (Order.created_at >= start_of_month) & 
    (Order.created_at <= end_of_month)
).all()
```

### Dynamic Filter Building

```python
def build_user_query(**kwargs):
    filters = []
    
    if kwargs.get("min_age") is not None:
        filters.append(User.age >= kwargs["min_age"])
    
    if kwargs.get("max_age") is not None:
        filters.append(User.age <= kwargs["max_age"])
    
    if kwargs.get("username"):
        filters.append(User.username == kwargs["username"])
    
    if kwargs.get("is_active") is not None:
        filters.append(User.is_active == kwargs["is_active"])
    
    if kwargs.get("bio_search"):
        filters.append(User.bio % kwargs["bio_search"])
    
    return User.find(*filters) if filters else User.find()

# Usage
query = build_user_query(min_age=18, is_active=True, bio_search="developer")
results = await query.all()
```

## Error Handling in Queries

```python
from aredis_om import NotFoundError, QuerySyntaxError, QueryNotSupportedError

try:
    # Invalid field name
    results = await Product.find(Product.invalid_field == "value").all()
except QuerySyntaxError as e:
    print(f"Query syntax error: {e}")

try:
    # Get non-existent record
    product = await Product.get("invalid-pk")
except NotFoundError as e:
    print(f"Product not found: {e}")

try:
    # Unsupported query operation
    results = await Product.find(Product.tags.contains("sale")).all()
except QueryNotSupportedError as e:
    print(f"Query not supported: {e}")
```
