# Database Backends - Detailed Configuration

This reference covers complete configuration, optimization, and usage patterns for each database backend supported by NetworkXternal.

## SQLite Backend

### Classes

- `SQLiteMem` - In-memory SQLite (fastest, volatile)
- `SQLite` - File-based SQLite (persistent)

### Connection URLs

```python
# In-memory (lost when connection closes)
graph = SQLiteMem(url="sqlite:///:memory:")

# File-based persistent storage
graph = SQLite(url="sqlite:///path/to/graph.db")
graph = SQLite(url="sqlite:////absolute/path/to/graph.db")  # 4 slashes for absolute path
```

### Automatic Optimizations

SQLite backend automatically applies these pragmas on first launch:

```sql
PRAGMA page_size=4096;              -- Optimal page size for graph data
PRAGMA cache_size=10000;            -- 10MB cache for better performance
PRAGMA journal_mode=WAL;            -- Write-Ahead Logging for concurrency
PRAGMA locking_mode=EXCLUSIVE;      -- Reduced syscall overhead
PRAGMA synchronous=ON;              -- Balance of speed and safety
PRAGMA temp_store=MEMORY;           -- Temp tables in RAM
PRAGMA optimize(0xfffe);            -- Auto-analyze and optimize
PRAGMA threads=8;                   -- Worker thread limit
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch size | 1,000,000 edges | Optimal for bulk inserts |
| Write amplification | ~200x | 250MB graph → 200GB written |
| File size ratio | ~4x | 250MB graph → 1GB file |
| Best for | < 20 MB graphs | Performance degrades after |

### When to Use SQLite

✅ **Use when:**
- Graph fits under 20 MB in memory equivalent
- Single-process access pattern
- Quick prototyping or testing
- No database server available

❌ **Don't use when:**
- Multiple processes need concurrent access
- Graph exceeds 100 MB
- High write throughput required

## PostgreSQL Backend

### Connection URLs

```python
from networkxternal.postgres import PostgreSQL

# Basic connection
graph = PostgreSQL(
    url="postgresql://user:password@localhost:5432/graph_db"
)

# With SSL
graph = PostgreSQL(
    url="postgresql+psycopg2://user:password@localhost:5432/graph_db?sslmode=require"
)

# Connection pooling (use external pool)
from sqlalchemy import create_engine
engine = create_engine(
    "postgresql://user:password@localhost:5432/graph_db",
    pool_size=10,
    max_overflow=20
)
```

### Automatic Optimizations

PostgreSQL backend applies on first launch:

```sql
SET synchronous_commit=0;  -- Performance over reliability
```

**Note**: `shared_buffers` and `wal_buffers` must be set in postgresql.conf, not via session.

### Recommended postgresql.conf Settings

```conf
# For graph workloads
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
maintenance_work_mem = 1GB        # For VACUUM, CREATE INDEX
work_mem = 64MB                   # Per-query sort/hash memory
wal_buffers = 64MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1            # Lower if using SSD

# Connection limits
max_connections = 200

# For bulk imports
max_wal_size = 4GB
min_wal_size = 1GB
```

### Indexing Strategy

NetworkXternal creates these indexes automatically:

```sql
CREATE INDEX index_first ON main_edges(first);
CREATE INDEX index_second ON main_edges(second);
CREATE INDEX index_label ON main_edges(label);
CREATE INDEX index_directed ON main_edges(is_directed);
```

**Additional recommended indexes:**

```sql
-- Composite index for directed edge lookups
CREATE INDEX edges_directed_lookup ON main_edges(first, second, is_directed);

-- For undirected edge lookups (both directions)
CREATE INDEX edges_undirected_lookup ON main_edges(
    CASE WHEN first < second THEN first ELSE second END,
    CASE WHEN first < second THEN second ELSE first END
);

-- Partial index for only directed edges
CREATE INDEX edges_directed_only ON main_edges(first, second)
WHERE is_directed = true;
```

### JSON Payload Querying

PostgreSQL can query inside JSON payloads:

```python
# Install sqlalchemy-utils for JSON support
pip install sqlalchemy-utils

from sqlalchemy_utils.types.json import JSONType

# Query nodes by payload attribute
from sqlalchemy import select
from networkxternal.base_sql import NodeSQL

with graph.get_session() as s:
    # Find nodes with category='source'
    nodes = s.query(NodeSQL).filter(
        NodeSQL.payload_json['category'] == 'source'
    ).all()
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch size | 100,000 - 1,000,000 edges | Tune based on row size |
| Concurrent reads | Excellent | Multiple readers supported |
| Concurrent writes | Good | Row-level locking |
| Best for | Multi-process, large graphs | Production workloads |

### When to Use PostgreSQL

✅ **Use when:**
- Multiple processes need concurrent access
- Graph exceeds 1 GB
- Production environment with reliability requirements
- Need JSON payload querying

❌ **Don't use when:**
- Can't run a database server
- Simple single-process workload (use SQLite)

## MySQL Backend

### Connection URLs

```python
from networkxternal.mysql import MySQL

# Basic connection
graph = MySQL(
    url="mysql://user:password@localhost:3306/graph_db"
)

# With specific driver
graph = MySQL(
    url="mysql+pymysql://user:password@localhost:3306/graph_db"
)

# With connection pooling
graph = MySQL(
    url="mysql+mysqldb://user:password@localhost:3306/graph_db"
)
```

### Automatic Optimizations

MySQL backend applies on first launch:

```sql
SET GLOBAL local_infile=1;                    -- Allow CSV imports
SET GLOBAL innodb_file_per_table=1;           -- Flush temp tables after bulk
SET SESSION sql_mode=NO_AUTO_VALUE_ON_ZERO;   -- Don't auto-increment ID 0
SET GLOBAL tmp_table_size=16777216;           -- 16MB temp tables
SET GLOBAL max_heap_table_size=16777216;      -- 16MB heap tables
```

### Recommended my.cnf Settings

```ini
[mysqld]
# Memory
innodb_buffer_pool_size = 4G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2  # Performance over safety

# Connections
max_connections = 200
thread_cache_size = 50

# For graph workloads
innodb_flush_method = O_DIRECT        # Bypass OS cache (NVMe SSDs)
innodb_read_io_threads = 16
innodb_write_io_threads = 16

# Temp tables
tmp_table_size = 64M
max_heap_table_size = 64M

# Logging (disable for performance)
slow_query_log = 0
general_log = 0
```

### CSV Import Support

MySQL supports direct CSV loading (file must be on server):

```python
# This method is commented out in the library but can be enabled:
def add_from_csv(self, path: str) -> int:
    cnt = self.number_of_edges()
    pattern = '''
    LOAD DATA LOCAL INFILE '%s'
    INTO TABLE main_edges
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (first, second, weight);
    '''
    task = pattern % (path, "main_edges")
    with self.get_session() as s:
        s.execute(task)
        s.commit()
    # ... migration logic
    return self.number_of_edges() - cnt
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch size | 100,000 edges | Optimal for most workloads |
| CSV import speed | Fast | With local_infile enabled |
| Concurrent access | Good | InnoDB row-level locking |
| Best for | Existing MySQL infrastructure | Moderate-sized graphs |

### When to Use MySQL

✅ **Use when:**
- Already using MySQL in your stack
- Need familiar database administration
- Moderate graph sizes (100MB - 1GB)

❌ **Don't use when:**
- PostgreSQL is available (better for graphs)
- Very large graphs (> 5GB)

## MongoDB Backend

### Connection URLs

```python
from networkxternal.mongodb import MongoDB

# Basic connection
graph = MongoDB(
    url="mongodb://localhost:27017/graph"
)

# With authentication
graph = MongoDB(
    url="mongodb://user:password@localhost:27017/graph"
)

# Replica set
graph = MongoDB(
    url="mongodb://node1:27017,node2:27017,node3:27017/graph?replicaSet=rs0"
)

# With SSL
graph = MongoDB(
    url="mongodb://user:password@localhost:27017/graph?tls=true&tlsCAFile=/path/to/ca.pem"
)
```

### Collection Structure

MongoDB stores graph data in two collections:

**nodes collection:**
```json
{
  "_id": 123,
  "weight": 2.5,
  "label": 0,
  "payload": {
    "category": "source",
    "name": "node_123"
  }
}
```

**edges collection:**
```json
{
  "_id": 456,
  "first": 123,
  "second": 789,
  "is_directed": true,
  "weight": 3.5,
  "label": 0,
  "payload": {
    "relationship": "connects_to"
  }
}
```

### Index Creation

NetworkXternal creates indexes automatically:

```python
# Called in __init__
graph.create_index()

# Manually create additional indexes if needed
from pymongo import ASCENDING, DESCENDING

graph.edges_collection.create_index([("first", ASCENDING), ("second", ASCENDING)])
graph.edges_collection.create_index([("second", ASCENDING), ("first", ASCENDING)])
graph.edges_collection.create_index([("is_directed", ASCENDING), ("first", ASCENDING)])
```

### Aggregation Pipelines

MongoDB uses aggregation pipelines for complex queries:

```python
# Match edges by endpoint
def pipe_match_edge_members(self, u, v):
    if u is None and v is None:
        return None
    if u is None:
        return {"$match": {"second": v}}
    if v is None:
        return {"$match": {"first": u}}
    if u == v:
        return {
            "$match": {
                "$or": [
                    {"first": u, "second": u},
                    {"first": u, "second": u},
                ]
            }
        }
    return {
        "$match": {
            "$or": [
                {"first": u, "second": v},
                {"first": v, "second": u},
            ]
        }
    }

# Compute degree (count and weight sum)
def pipe_compute_degree(self):
    return {
        "$group": {
            "_id": None,
            "count": {"$sum": 1},
            "weight": {"$sum": "$weight"}
        }
    }

# Use in query
result = graph.edges_collection.aggregate([
    graph.pipe_match_edge_members(1, None),
    graph.pipe_compute_degree()
])
```

### Batch Size Limitations

MongoDB has hard limits on batch operations:

- **Maximum batch size**: 100,000 documents (was 1,000 before MongoDB 3.6)
- **Maximum BSON size**: 16 MB per document
- **Recommended batch**: 10,000 documents for stability

```python
# NetworkXternal respects this limit
MongoDB.__max_batch_size__ = 10000
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch size | 10,000 edges | Don't exceed 100,000 |
| Read performance | Good | Index lookups fast |
| Write performance | Moderate | Batch inserts help |
| Best for | Distributed deployments | Existing MongoDB infra |

### When to Use MongoDB

✅ **Use when:**
- Already using MongoDB in your stack
- Need distributed/deployed graph storage
- Flexible schema is beneficial
- Horizontal scaling required

❌ **Don't use when:**
- Graph has billions of edges (BSON size limits)
- Complex graph traversals needed
- ACID transactions across documents critical

## Neo4J Backend

### ⚠️ Important Warnings

**Neo4J is NOT recommended for large graphs due to:**

1. **High resource usage**: 10-20x CPU compared to other databases
2. **Memory issues**: Constant "Java heap space" crashes
3. **Edge indexing**: Only available in Enterprise edition
4. **Instability**: Frequent crashes with various error codes
5. **Space inefficiency**: Can't override native node IDs

### Connection URLs

```python
from networkxternal.neo4j import Neo4J

# Basic connection (Bolt protocol)
graph = Neo4J(
    url="bolt://localhost:7687/graph"
)

# With authentication
graph = Neo4J(
    url="bolt://neo4j:password@localhost:7687/graph"
)

# Enterprise edition features
graph = Neo4J(
    url="bolt://neo4j:password@localhost:7687/graph",
    enterprise_edition=True  # Enables edge constraints
)
```

### Label-Based Namespacing

Neo4J can't easily switch databases, so NetworkXternal uses labels:

```python
# Database name becomes label suffix
url = "bolt://localhost:7687/mygraph"
# Creates labels: vmygraph (vertices), emygraph (edges)

# All graphs share same physical storage but different labels
```

### Index vs Constraints

```python
# Using indexes (default, free edition compatible)
graph = Neo4J(
    url="bolt://localhost:7687/graph",
    use_indexes_over_constraints=True  # Default
)

# Creates: CREATE INDEX indexVERTEX FOR (v:VERTEX) ON (v._id)

# Using constraints (requires Enterprise for edges)
graph = Neo4J(
    url="bolt://localhost:7687/graph",
    use_indexes_over_constraints=False,
    enterprise_edition=True
)

# Creates: CREATE CONSTRAINT constraintVERTEX ON (v:VERTEX) ASSERT (v._id) IS UNIQUE
```

### Cypher Query Examples

NetworkXternal generates Cypher queries internally. Examples:

```python
# Find edges between nodes (generated by has_edge)
MATCH (u:`v{label}`)-[e:`e{label}`]->(v:`v{label}`)
WHERE u._id = $u_id AND v._id = $v_id
RETURN e

# Get neighbors (generated by neighbors)
MATCH (n:`v{label}`)-[]-(neighbor:`v{label}`)
WHERE n._id = $node_id
RETURN neighbor._id
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch size | 1,000 edges | Don't exceed 10,000 |
| CPU usage | Very high | 10-20x other DBs |
| Memory usage | High | Java heap management issues |
| Best for | Small graphs only | < 100K edges |

### Common Neo4J Errors

**Error**: `neobolt.exceptions.TransientError: There is not enough stack size`
- **Cause**: Query too complex or data too large
- **Solution**: Reduce batch size, simplify query

**Error**: `neobolt.exceptions.DatabaseError: Java heap space`
- **Cause**: Not enough memory allocated to Java VM
- **Solution**: Increase Neo4J heap size or use different backend

**Error**: Index not found on edges
- **Cause**: Edge indexing only in Enterprise edition
- **Solution**: Use Free edition with node indexes only, or upgrade

### When to Use Neo4J

✅ **Use when:**
- Graph is small (< 100K edges)
- Need native Cypher queries
- Already using Neo4J for other purposes
- Small team, simple deployment

❌ **Don't use when:**
- Graph exceeds 1M edges
- Production workload with reliability requirements
- Limited hardware resources
- Edge querying is critical (Free edition limitation)

## Backend Comparison Summary

| Feature | SQLite | PostgreSQL | MySQL | MongoDB | Neo4J |
|---------|--------|------------|-------|---------|-------|
| Max graph size | 20 MB | Unlimited | 5 GB | Unlimited | 100K edges |
| Concurrent access | No | Excellent | Good | Excellent | Moderate |
| Setup complexity | None | Medium | Medium | Medium | High |
| Write performance | Fast (small) | Fast | Fast | Moderate | Slow |
| Read performance | Fast (small) | Fast | Fast | Fast | Moderate |
| JSON querying | No | Yes | Limited | Native | N/A |
| ACID compliance | Yes | Yes | Yes | Yes (4.0+) | Yes |
| Horizontal scaling | No | Limited | Limited | Excellent | Limited |
| Best batch size | 1M | 100K-1M | 100K | 10K | 1K |

## Migration Between Backends

### Export/Import Pattern

```python
from networkxternal.sqlite import SQLite
from networkxternal.postgres import PostgreSQL

# Read from SQLite
source = SQLite(url="sqlite:///small_graph.db")

# Write to PostgreSQL
target = PostgreSQL(url="postgresql://user:pass@localhost/graph")

# Copy all edges
for edge in source.edges:
    target.add(edge)

# Copy all nodes
for node in source.nodes:
    target.add(node)
```

### CSV Intermediate Format

```python
# Export to CSV
with open("graph_export.csv", "w") as f:
    f.write("first,second,weight\n")
    for edge in source.edges:
        f.write(f"{edge.first},{edge.second},{edge.weight}\n")

# Import from CSV
from networkxternal.helpers.parsing import import_graph
import_graph(target, "graph_export.csv")
```
