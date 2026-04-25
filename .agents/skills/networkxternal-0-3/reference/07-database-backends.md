# Database Backends

### SQLite (Fastest for Small Graphs)

```python
from networkxternal.sqlite import SQLite, SQLiteMem

# In-memory (fastest, but volatile)
graph = SQLiteMem(directed=True)

# Persistent file-based storage
graph = SQLite(url="sqlite:///path/to/graph.db", directed=True)

# SQLite is optimized with pragmas:
# - page_size=4096
# - journal_mode=WAL
# - synchronous=ON
# - cache_size=10000
```

**Best for**: Graphs under 20 MB, single-process access, quick prototyping

### PostgreSQL (Feature-Rich)

```python
from networkxternal.postgres import PostgreSQL

graph = PostgreSQL(
    url="postgresql://user:password@localhost:5432/graph_db",
    directed=True
)

# PostgreSQL supports:
# - Concurrent reads/writes
# - JSON payload querying
# - Advanced indexing
```

**Best for**: Multi-process access, large graphs (GBs), production environments

### MySQL

```python
from networkxternal.mysql import MySQL

graph = MySQL(
    url="mysql://user:password@localhost:3306/graph_db",
    directed=True
)

# MySQL is optimized with:
# - local_infile=1 (for CSV imports)
# - innodb_file_per_table=1
# - tmp_table_size=16MB
```

**Best for**: Existing MySQL infrastructure, moderate-sized graphs

### MongoDB (Document-Based)

```python
from networkxternal.mongodb import MongoDB

graph = MongoDB(
    url="mongodb://localhost:27017/graph",
    directed=True
)

# MongoDB stores:
# - Nodes in 'nodes' collection
# - Edges in 'edges' collection
# - Uses aggregation pipelines for queries
```

**Best for**: Distributed deployments, existing MongoDB infrastructure, flexible schemas

### Neo4J (Native Graph DB)

```python
from networkxternal.neo4j import Neo4J

graph = Neo4J(
    url="bolt://user:password@localhost:7687/graph",
    directed=True,
    enterprise_edition=False  # Set True for edge uniqueness constraints
)

# Neo4J-specific methods:
path, weight = graph.shortest_path(first_node, second_node)  # Returns (node_ids, total_weight)
degree_count, degree_weight = graph.degree_neighbors(v)       # Count + total weight of edges
degree_count, degree_weight = graph.degree_successors(v)      # Out-degree stats
degree_count, degree_weight = graph.degree_predecessors(v)    # In-degree stats

# Neo4J uses Cypher queries with labels: v<name> for nodes, e<name> for edges
```

**⚠️ CRITICAL WARNING: Neo4J is the least stable backend:**
- **High CPU usage**: 10-20x higher than other backends
- **Java heap space crashes**: Frequently crashes on large imports (30 MB CSV → 1.4 GB RAM)
- **Edge indexing**: Only available in Enterprise edition; free version has poor edge lookup performance
- **Unstable**: Reports of stack overflow errors, inconsistent query profiler results
- **Small batch size recommended**: Max 1,000 edges per batch (vs 1M+ for SQL backends)
- **Not recommended for production** with large datasets

**Best for**: Small graphs (< 10K edges) where native Cypher graph queries are needed. Use other backends for anything larger.
