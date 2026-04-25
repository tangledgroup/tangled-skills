# Hybrid Attributes in SQLAlchemy ORM

## Introduction to Hybrid Attributes

Hybrid attributes allow you to define Python properties that work both on instances and in class-level queries. This is particularly useful for computed fields, formatted values, or business logic that should be available in both contexts.

```python
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    
    @hybrid_property
    def full_name(self):
        """Instance-level: compute from attributes"""
        return f"{self.first_name} {self.last_name}"
    
    @full_name.expression
    @classmethod
    def full_name(cls):
        """Class-level: SQL expression for queries"""
        return cls.first_name + " " + cls.last_name

# Usage on instance
user = session.get(User, 1)
print(user.full_name)  # "John Doe"

# Usage in query
users = session.execute(
    select(User).where(User.full_name.like("John %"))
).scalars().all()
```

## Basic Hybrid Properties

### Simple Computed Fields

```python
from sqlalchemy.ext.hybrid import hybrid_property

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(10, 2))
    quantity = Column(Integer)
    tax_rate = Column(Numeric(3, 2), default=0.08)
    
    @hybrid_property
    def total_price(self):
        return self.unit_price * self.quantity
    
    @total_price.expression
    @classmethod
    def total_price(cls):
        return cls.unit_price * cls.quantity
    
    @hybrid_property
    def price_with_tax(self):
        return self.total_price * (1 + self.tax_rate)
    
    @price_with_tax.expression
    @classmethod
    def price_with_tax(cls):
        return (cls.unit_price * cls.quantity) * (1 + cls.tax_rate)

# Query by computed field
expensive = session.execute(
    select(Product).where(Product.total_price > 100)
).scalars().all()
```

### Conditional Logic

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(10, 2))
    status = Column(String(20))
    
    @hybrid_property
    def is_completed(self):
        return self.status == "completed"
    
    @is_completed.expression
    @classmethod
    def is_completed(cls):
        return cls.status == "completed"
    
    @hybrid_property
    def display_status(self):
        status_map = {
            "pending": "Pending Review",
            "processing": "Being Processed",
            "completed": "Completed",
            "cancelled": "Cancelled"
        }
        return status_map.get(self.status, self.status)
    
    @display_status.expression
    @classmethod
    def display_status(cls):
        return case(
            (cls.status == "pending", "Pending Review"),
            (cls.status == "processing", "Being Processed"),
            (cls.status == "completed", "Completed"),
            (cls.status == "cancelled", "Cancelled"),
            else_=cls.status
        )

# Query using hybrid property
completed = session.execute(
    select(Order).where(Order.is_completed == True)
).scalars().all()
```

## Hybrid Methods

Hybrid methods work similarly but for callable attributes:

```python
from sqlalchemy.ext.hybrid import hybrid_method

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    age = Column(Integer)
    
    @hybrid_method
    def is_adult(self):
        """Instance-level method"""
        return self.age >= 18
    
    @is_adult.expression
    @classmethod
    def is_adult(cls):
        """Class-level expression for queries"""
        return cls.age >= 18
    
    @hybrid_method
    def matches_age_range(self, min_age, max_age):
        """Instance-level with parameters"""
        return min_age <= self.age <= max_age
    
    @matches_age_range.expression
    @classmethod
    def matches_age_range(cls, min_age, max_age):
        """Class-level with parameters"""
        return (cls.age >= min_age) & (cls.age <= max_age)

# Usage on instance
user = session.get(User, 1)
if user.is_adult():
    print("Adult user")

if user.matches_age_range(18, 30):
    print("User is 18-30")

# Usage in queries
adults = session.execute(
    select(User).where(User.is_adult())
).scalars().all()

young_adults = session.execute(
    select(User).where(User.matches_age_range(18, 30))
).scalars().all()
```

## Advanced Hybrid Patterns

### JSON Field Helpers

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import JSON, cast, String

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferences = Column(JSON)  # {"theme": "dark", "lang": "en"}
    
    @hybrid_property
    def theme(self):
        return self.preferences.get("theme", "light") if self.preferences else "light"
    
    @theme.expression
    @classmethod
    def theme(cls):
        # PostgreSQL JSON access
        return cls.preferences["theme"].as_string()
    
    @hybrid_property
    def language(self):
        return self.preferences.get("lang", "en") if self.preferences else "en"
    
    @language.expression
    @classmethod
    def language(cls):
        return cls.preferences["lang"].as_string()

# Query by JSON field value
dark_theme = session.execute(
    select(Settings).where(Settings.theme == "dark")
).scalars().all()
```

### Date/Time Computations

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, extract
from datetime import datetime, timedelta

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    @hybrid_property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @duration_days.expression
    @classmethod
    def duration_days(cls):
        # PostgreSQL date arithmetic
        return extract(
            'epoch', 
            (cls.end_date - cls.start_date)
        ) / 86400
    
    @hybrid_property
    def is_upcoming(self):
        return self.start_date > datetime.utcnow()
    
    @is_upcoming.expression
    @classmethod
    def is_upcoming(cls):
        return cls.start_date > func.now()
    
    @hybrid_property
    def is_overdue(self):
        return self.end_date < datetime.utcnow()
    
    @is_overdue.expression
    @classmethod
    def is_overdue(cls):
        return cls.end_date < func.now()

# Query events by computed properties
upcoming = session.execute(
    select(Event).where(Event.is_upcoming == True)
).scalars().all()

long_events = session.execute(
    select(Event).where(Event.duration_days > 7)
).scalars().all()
```

### String Formatting and Parsing

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(50))  # "ELEC-LAPTOP-001"
    name = Column(String(200))
    
    @hybrid_property
    def category(self):
        """Parse category from SKU"""
        if self.sku:
            return self.sku.split("-")[0]
        return None
    
    @category.expression
    @classmethod
    def category(cls):
        # Extract first part before dash
        return func.split_part(cls.sku, '-', 1)
    
    @hybrid_property
    def sku_upper(self):
        return self.sku.upper() if self.sku else None
    
    @sku_upper.expression
    @classmethod
    def sku_upper(cls):
        return func.upper(cls.sku)
    
    @hybrid_property
    def display_name(self):
        """Format name for display"""
        return f"[{self.sku}] {self.name}" if self.sku else self.name
    
    @display_name.expression
    @classmethod
    def display_name(cls):
        return func.concat(
            "[", cls.sku, "] ", cls.name
        )

# Query by parsed field
electronics = session.execute(
    select(Product).where(Product.category == "ELEC")
).scalars().all()
```

## Hybrid with Relationships

### Computed Relationship Properties

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    
    posts = relationship("Post", back_populates="author")
    
    @hybrid_property
    def post_count(self):
        return len(self.posts) if self.posts else 0
    
    @post_count.expression
    @classmethod
    def post_count(cls):
        return (
            select(func.count(Post.id))
            .where(Post.author_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )
    
    @hybrid_property
    def total_views(self):
        return sum(p.view_count for p in self.posts) if self.posts else 0
    
    @total_views.expression
    @classmethod
    def total_views(cls):
        return (
            select(func.coalesce(func.sum(Post.view_count), 0))
            .where(Post.author_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )
    
    @hybrid_property
    def has_published_posts(self):
        return any(p.is_published for p in self.posts) if self.posts else False
    
    @has_published_posts.expression
    @classmethod
    def has_published_posts(cls):
        return (
            exists().where(
                and_(
                    Post.author_id == cls.id,
                    Post.is_published == True
                )
            )
        )

# Query users by relationship properties
active_authors = session.execute(
    select(User).where(User.post_count > 5)
).scalars().all()

popular_authors = session.execute(
    select(User).where(User.total_views > 1000)
).scalars().all()

published_authors = session.execute(
    select(User).where(User.has_published_posts == True)
).scalars().all()
```

## Best Practices

### 1. Keep Expressions Simple

```python
# Good - simple expression
@hybrid_property
def full_name(self):
    return f"{self.first_name} {self.last_name}"

@full_name.expression
@classmethod
def full_name(cls):
    return cls.first_name + " " + cls.last_name

# Avoid - complex logic that's hard to express in SQL
@hybrid_property  
def complex_score(self):
    # Complex Python logic
    base = self.base_score
    if self.is_premium:
        base *= 1.5
    if self.posts:
        base += len(self.posts) * 2
    # Hard to translate to SQL expression!
    return base
```

### 2. Handle None Values

```python
@hybrid_property
def formatted_name(self):
    if not self.first_name or not self.last_name:
        return None
    return f"{self.first_name} {self.last_name}"

@formatted_name.expression
@classmethod
def formatted_name(cls):
    from sqlalchemy import case
    return case(
        (cls.first_name.is_(None), None),
        (cls.last_name.is_(None), None),
        else_=cls.first_name + " " + cls.last_name
    )
```

### 3. Document Hybrid Properties

```python
@hybrid_property
def age_in_years(self):
    """
    Calculate age in years from birth_date.
    
    Instance: Returns integer age calculated in Python.
    Class: Returns approximate age using date arithmetic.
    
    Note: Class-level calculation may differ by 1 day near birthdays.
    """
    if not self.birth_date:
        return None
    today = datetime.utcnow().date()
    birth = self.birth_date.date()
    return today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

@age_in_years.expression
@classmethod
def age_in_years(cls):
    """Approximate age using PostgreSQL date arithmetic."""
    if cls.birth_date is None:
        return None
    return extract(
        'year', 
        func.age(func.now(), cls.birth_date)
    )
```

### 4. Use for Read-Only Computed Fields

Hybrid properties are typically read-only. For writable computed fields, consider alternative patterns.

## Troubleshooting

### Expression Not Working in Query

```python
# Problem: Forgot @expression decorator
@hybrid_property
def full_name(self):
    return f"{self.first_name} {self.last_name}"

# Missing:
# @full_name.expression
# @classmethod
# def full_name(cls):
#     return cls.first_name + " " + cls.last_name

# Error when using in query:
# select(User).where(User.full_name.like("John %"))  # Fails!
```

### Dialect-Specific Functions

```python
# Problem: Using PostgreSQL-specific function with MySQL
@category.expression
@classmethod
def category(cls):
    return func.split_part(cls.sku, '-', 1)  # PostgreSQL only!

# Solution: Use dialect-aware functions or conditionals
from sqlalchemy import case

@category.expression  
@classmethod
def category(cls):
    # More portable approach
    return func.left(cls.sku, func.instr(cls.sku, '-') - 1)
```

## Next Steps

- [ORM Extensions](11-orm-extensions.md) - Association proxy and other extensions
- [Core SQL Expressions](12-core-sql-expressions.md) - Advanced expression building
- [Best Practices](24-best-practices.md) - Performance considerations
- [Custom Types](15-core-custom-types.md) - Type-level computations
