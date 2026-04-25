# Advanced Features

Comprehensive guide to vector similarity search (KNN), geospatial queries, RedisVL integration, and other advanced features in Redis OM Python v1.1.0.

## Vector Similarity Search (KNN)

Redis OM supports k-nearest neighbors (KNN) vector similarity search for embedding-based applications like semantic search, recommendation systems, and AI applications.

### Vector Field Configuration

Use `VectorFieldOptions` to configure vector fields:

```python
from aredis_om import JsonModel, Field, VectorFieldOptions

DIMENSIONS = 768  # Must match your embedding model dimension

vector_options = VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,  # or FLOAT64
    dimension=DIMENSIONS,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,  # or EUCLIDEAN, IP
)

class Document(JsonModel):
    title: str = Field(index=True, full_text_search=True)
    content: str = Field(index=True, full_text_search=True)
    embeddings: list[float] = Field(
        default_factory=list,
        vector_options=vector_options
    )
    similarity_score: Optional[float] = None  # To store KNN score

# Distance metrics available:
# - COSINE: Cosine similarity (best for text embeddings)
# - EUCLIDEAN: Euclidean distance (L2)
# - IP: Inner product (dot product)
```

### Performing KNN Search

Use `KNNExpression` to perform vector similarity search:

```python
import struct
from aredis_om import KNNExpression

def pack_vector(vector: list[float]) -> bytes:
    """Pack float list to bytes for Redis storage."""
    return struct.pack(f"<{len(vector)}f", *vector)

# Your query embedding (must match dimension of indexed vectors)
query_embedding = [0.1] * DIMENSIONS  # Replace with actual embedding

# Create KNN expression
knn = KNNExpression(
    k=10,  # Number of results to return
    vector_field=Document.embeddings,
    score_field=Document.similarity_score,
    reference_vector=pack_vector(query_embedding),
)

# Execute search
similar_docs = await Document.find(knn=knn).all()

# Results are sorted by similarity (most similar first)
for doc in similar_docs:
    print(f"{doc.title}: score={doc.similarity_score}")
```

### KNN with Additional Filters

Combine vector search with other filters:

```python
# KNN with category filter
knn = KNNExpression(
    k=10,
    vector_field=Document.embeddings,
    score_field=Document.similarity_score,
    reference_vector=pack_vector(query_embedding),
)

# Add text filter
filtered_results = await Document.find(
    knn=knn,
    expr=Document.category == "technology"  # Additional filter
).all()

# KNN with full-text search (OR condition)
search_query = "machine learning"
combined = await Document.find(
    knn=knn
).copy(
    (Document.title % search_query) | (Document.content % search_query)
).all()
```

### Nested Vector Fields

Store vectors in nested structures:

```python
class Product(JsonModel):
    name: str = Field(index=True)
    features: dict = {
        "description_embedding": []  # Nested vector field
    }

# Configure vector options for nested field
vector_options = VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=DIMENSIONS,
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
)

class Product(JsonModel):
    name: str = Field(index=True)
    nested_embeddings: list[list[float]] = Field(
        default_factory=list,
        vector_options=vector_options
    )
    similarity_score: Optional[float] = None

# KNN on nested field
knn = KNNExpression(
    k=5,
    vector_field=Product.nested_embeddings,
    score_field=Product.similarity_score,
    reference_vector=pack_vector(query_embedding),
)

results = await Product.find(knn=knn).all()
```

### OR Expressions with KNN

Combine KNN with OR conditions:

```python
class Album(JsonModel):
    title: str = Field(primary_key=True)
    tags: str = Field(index=True)
    title_embeddings: list[float] = Field(
        default_factory=list,
        vector_options=vector_options
    )
    similarity_score: Optional[float] = None

# Create albums with embeddings
album1 = Album(title="rock-album", tags="rock", title_embeddings=embedding1)
await album1.save()

# KNN with OR expression
knn = KNNExpression(
    k=5,
    vector_field=Album.title_embeddings,
    score_field=Album.similarity_score,
    reference_vector=pack_vector(query_embedding),
)

# Find albums matching KNN OR specific tag
results = await Album.find(
    (Album.tags == "rock") | knn  # Note: KNN can be used in OR
).all()
```

## Geospatial Queries

Redis OM supports geospatial queries using the `GeoFilter` class and `Coordinates` type.

### Coordinate Fields

```python
from aredis_om import JsonModel, Field, Coordinates

class Location(JsonModel):
    name: str = Field(index=True, full_text_search=True)
    description: str = Field(index=True, full_text_search=True)
    coordinates: Coordinates = Field(index=True)  # Geo field
    city: str = Field(index=True)

# Create location with coordinates
from pydantic_extra_types.coordinate import Coordinate

nyc = Location(
    name="Central Park",
    description="Large public park in Manhattan",
    coordinates=Coordinate(latitude=40.78509, longitude=-73.96828),
    city="New York"
)
await nyc.save()
```

### Radius Search with GeoFilter

Find locations within a radius of a point:

```python
from aredis_om import GeoFilter

# Find all locations within 10 miles of Portland, OR
portland_filter = GeoFilter(
    longitude=-122.6765,
    latitude=45.5231,
    radius=10,
    unit="mi"  # Options: "m", "km", "mi", "ft"
)

nearby = await Location.find(
    Location.coordinates == portland_filter
).all()

# Find restaurants within 5 km of coordinates
restaurant_filter = GeoFilter(
    longitude=-0.1276,  # London
    latitude=51.5074,
    radius=5,
    unit="km"
)

london_eats = await Restaurant.find(
    Restaurant.location == restaurant_filter
).all()
```

### GeoFilter Units

Supported distance units:
- `"m"` - Meters
- `"km"` - Kilometers  
- `"mi"` - Miles
- `"ft"` - Feet

```python
# Various unit examples
meter_filter = GeoFilter(longitude=0, latitude=0, radius=1000, unit="m")
km_filter = GeoFilter(longitude=0, latitude=0, radius=1, unit="km")  # Same as above
mile_filter = GeoFilter(longitude=0, latitude=0, radius=0.62, unit="mi")
feet_filter = GeoFilter(longitude=0, latitude=0, radius=3281, unit="ft")
```

### GeoFilter from Coordinates

Create GeoFilter from existing Coordinate objects:

```python
from pydantic_extra_types.coordinate import Coordinate

# From Coordinate object
center_point = Coordinate(latitude=40.7128, longitude=-74.0060)
filter = GeoFilter.from_coordinates(
    center_point,
    radius=25,
    unit="mi"
)

results = await Location.find(Location.coordinates == filter).all()

# From tuple (longitude, latitude)
tuple_coords = (-74.0060, 40.7128)
filter = GeoFilter.from_coordinates(
    tuple_coords,
    radius=10,
    unit="km"
)
```

### Combining Geospatial with Other Filters

```python
# Find parks within 5 miles that have "playground" in description
geo_filter = GeoFilter(
    longitude=-122.4194,
    latitude=37.7749,
    radius=5,
    unit="mi"
)

parks = await Location.find(
    (Location.coordinates == geo_filter) & 
    (Location.name % "park") &
    (Location.description % "playground")
).all()

# Find locations in specific city within radius
sf_locations = await Location.find(
    (Location.coordinates == geo_filter) &
    (Location.city == "San Francisco")
).all()
```

## RedisVL Integration

Redis OM v1.1.0 includes RedisVL integration for advanced vector search capabilities:

```python
# RedisVL is included as a dependency
# pip install redis-om  # Includes redisvl>=0.16.0

from aredis_om import JsonModel, Field, VectorFieldOptions

# Use RedisVL-compatible vector configuration
vector_options = VectorFieldOptions.flat(
    type=VectorFieldOptions.TYPE.FLOAT32,
    dimension=1536,  # Common for text-embedding-ada-002
    distance_metric=VectorFieldOptions.DISTANCE_METRIC.COSINE,
)

class RAGDocument(JsonModel):
    """Document store for RAG (Retrieval Augmented Generation)."""
    content: str = Field(index=True, full_text_search=True)
    metadata: dict = Field(default_factory=dict)
    embedding: list[float] = Field(
        default_factory=list,
        vector_options=vector_options
    )
    similarity: Optional[float] = None

# Integration with external embedding services
import openai

async def create_document_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI API."""
    response = await openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Create indexed document
text = "Redis is an in-memory data structure store..."
embedding = await create_document_embedding(text)

doc = RAGDocument(
    content=text,
    metadata={"source": "documentation"},
    embedding=embedding
)
await doc.save()
```

## Partial Model Loading

Load only specific fields for better performance:

```python
from aredis_om import HashModel, Field

class User(HashModel):
    username: str = Field(index=True)
    email: str = Field(index=True)
    age: int = Field(index=True)
    bio: str = Field(index=True)
    preferences: dict

# Load only specific fields
partial_user = await User.find(User.age >= 18).only("username", "email").first()

print(partial_user.username)  # OK
print(partial_user.email)     # OK
# print(partial_user.age)     # AttributeError: Field not loaded

# Deep field loading for nested models
class Order(JsonModel):
    customer_name: str
    shipping_address: Address  # Embedded model
    total: float

# Load specific nested fields
partial_order = await Order.find().only(
    "customer_name",
    "shipping_address__city",
    "shipping_address__state"
).first()

print(partial_order.customer_name)           # OK
print(partial_order.shipping_address.city)   # OK
# print(partial_order.shipping_address.street)  # AttributeError
```

## Batch Operations

### Batch Save

```python
from aredis_om import HashModel, Field

class Product(HashModel):
    name: str = Field(index=True)
    price: float = Field(index=True)

products = [
    Product(name=f"Product {i}", price=i * 10.0)
    for i in range(100)
]

# Save multiple instances
for product in products:
    await product.save()

# Or use pipeline for better performance
async with redis.pipeline() as pipe:
    for product in products:
        # Manual pipeline operations
        pass
```

### Batch Delete

```python
# Delete multiple by primary keys
pks = ["pk1", "pk2", "pk3", "pk4", "pk5"]
for pk in pks:
    await Product.delete(pk)

# Delete all matching query (manual iteration)
to_delete = await Product.find(Product.price < 10).all()
for product in to_delete:
    await product.delete()
```

## Custom Redis Commands

Execute raw Redis commands when needed:

```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection()

# Execute custom command
result = await redis_client.execute_command("PING")

# Use Redis JSON commands directly
json_value = await redis_client.json().get("myapp:product:123")

# Raw hash commands
hash_field = await redis_client.hget("myapp:user:456", "username")
```

## Pipeline Operations

Use Redis pipelines for batch operations:

```python
from aredis_om import get_redis_connection

redis_client = get_redis_connection()

async with redis_client.pipeline() as pipe:
    # Multiple operations in one round-trip
    await pipe.set("key1", "value1")
    await pipe.set("key2", "value2")
    await pipe.hset("hash_key", field="field1", value="value1")
    results = await pipe.execute()

# Pipeline with Redis OM models
async def batch_save_users(users):
    async with redis_client.pipeline() as pipe:
        for user in users:
            # Serialize and save via pipeline
            key = f"user:{user.pk}"
            await pipe.hset(key, mapping=user.model_dump())
        await pipe.execute()
```

## Model Inheritance

Create base models for common functionality:

```python
import abc
from datetime import datetime
from aredis_om import JsonModel, Field

class TimestampedModel(JsonModel, abc.ABC):
    """Base model with automatic timestamps."""
    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
        sortable=True
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
        sortable=True
    )

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return await super().save(*args, **kwargs)

class Order(TimestampedModel):
    """Order inherits timestamps automatically."""
    customer_name: str = Field(index=True)
    total: float = Field(index=True, sortable=True)

# Usage
order = Order(customer_name="Alice", total=99.99)
await order.save()  # created_at and updated_at set automatically

await order.save()  # updated_at refreshed
```

## Global Key Prefixes

Organize models with namespace prefixes:

```python
class User(JsonModel):
    username: str = Field(index=True)

    class Meta:
        global_key_prefix = "myapp:v1"
        model_key_prefix = "user"

class Product(JsonModel):
    name: str = Field(index=True)

    class Meta:
        global_key_prefix = "myapp:v1"  # Same namespace
        model_key_prefix = "product"

class Session(HashModel):
    token: str = Field(index=True)

    class Meta:
        global_key_prefix = "myapp:sessions"  # Different namespace
        model_key_prefix = "session"

# Key formats:
# myapp:v1:user:<ulid>
# myapp:v1:product:<ulid>
# myapp:sessions:session:<ulid>
```

## Type Adapters and Serialization

Custom serialization for complex types:

```python
from pydantic import PlainSerializer, BeforeValidator
from typing import Annotated

def serialize_bytes(v: bytes) -> str:
    """Convert bytes to base64 string for Redis storage."""
    import base64
    return base64.b64encode(v).decode("ascii")

def deserialize_bytes(v: str) -> bytes:
    """Convert base64 string back to bytes."""
    import base64
    return base64.b64decode(v)

BytesType = Annotated[
    bytes,
    PlainSerializer(serialize_bytes, return_type=str),
    BeforeValidator(deserialize_bytes)
]

class File(JsonModel):
    name: str = Field(index=True)
    content: BytesType  # Automatically encoded/decoded
```

## Best Practices for Advanced Features

### Vector Search
1. **Match dimensions exactly:** Query vector must have same dimension as indexed vectors
2. **Use appropriate distance metric:** COSINE for text, EUCLIDEAN for spatial
3. **Store scores in separate field:** Use score_field to capture similarity scores
4. **Pack vectors correctly:** Use struct.pack with little-endian float32

### Geospatial Queries
1. **Validate coordinates:** Longitude (-180 to 180), Latitude (-90 to 90)
2. **Choose appropriate units:** Use "km" or "mi" for human-readable radii
3. **Index coordinate fields:** Must have index=True for geospatial queries
4. **Combine with text filters:** Filter by name/description for better results

### Performance
1. **Use partial loading:** Load only needed fields with .only()
2. **Batch operations:** Use pipelines for bulk saves/deletes
3. **Set appropriate TTLs:** Expire temporary data automatically
4. **Monitor index size:** Large indexes may need optimization
