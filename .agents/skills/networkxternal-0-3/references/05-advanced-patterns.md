# Advanced Patterns and Edge Cases

This reference covers advanced usage patterns, edge cases, and production-ready techniques for NetworkXternal.

## Bulk Operations

### Streaming CSV Import

For large CSV files that don't fit in memory:

```python
from networkxternal.postgres import PostgreSQL
from networkxternal.helpers.edge import Edge

def stream_csv_import(graph, csv_path, batch_size=10000):
    """Import CSV without loading entire file into memory"""
    import csv
    
    batch = []
    count = 0
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row in reader:
            first, second = int(row[0]), int(row[1])
            weight = float(row[2]) if len(row) > 2 else 1.0
            
            edge = Edge(first=first, second=second, weight=weight)
            batch.append(edge)
            
            if len(batch) >= batch_size:
                count += graph.add(batch)
                batch = []
                print(f"Imported {count} edges...")
        
        # Final batch
        if batch:
            count += graph.add(batch)
    
    # Register implied nodes
    graph.add_missing_nodes()
    print(f"Total imported: {count} edges")
    return count

# Usage
graph = PostgreSQL(url="postgresql://...")
stream_csv_import(graph, "large_graph.csv", batch_size=50000)
```

### Parallel Import from Multiple Files

Split large imports across multiple processes:

```python
from multiprocessing import Pool
from networkxternal.postgres import PostgreSQL

def import_chunk(args):
    """Single process imports one chunk"""
    csv_path, graph_url = args
    
    # Each process creates its own connection
    graph = PostgreSQL(url=graph_url)
    
    count = 0
    with open(csv_path, 'r') as f:
        for line in f:
            if line.startswith('first'):  # Skip header
                continue
            parts = line.strip().split(',')
            edge = Edge(first=int(parts[0]), second=int(parts[1]))
            graph.add(edge)
            count += 1
    
    return count

def parallel_import(csv_files, graph_url, num_processes=4):
    """Import multiple CSV files in parallel"""
    args = [(f, graph_url) for f in csv_files]
    
    with Pool(num_processes) as pool:
        results = pool.map(import_chunk, args)
    
    total = sum(results)
    print(f"Parallel import complete: {total} edges")
    
    # Final node registration (single process)
    graph = PostgreSQL(url=graph_url)
    graph.add_missing_nodes()
    
    return total

# Usage
csv_files = ["chunk_0.csv", "chunk_1.csv", "chunk_2.csv", "chunk_3.csv"]
parallel_import(csv_files, "postgresql://...", num_processes=4)
```

### Upsert vs Insert Performance

Understanding upsert behavior:

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///:memory:")

# First insert (fast - no lookup needed)
edge1 = Edge(_id=1, first=1, second=2, weight=3.5)
count1 = graph.add(edge1, upsert=True)  # Inserts new edge

# Second add with same ID (slower - checks existence)
edge2 = Edge(_id=1, first=1, second=2, weight=4.0)
count2 = graph.add(edge2, upsert=True)  # Updates existing edge

# With upsert=False (fails if exists)
edge3 = Edge(_id=1, first=1, second=2, weight=5.0)
count3 = graph.add(edge3, upsert=False)  # Returns 0, doesn't add
```

**Performance tip**: Use `upsert=False` when you know edges are unique:

```python
# Faster if you're sure edges don't exist
for edge in new_edges:
    graph.add(edge, upsert=False)  # Skips existence check
```

## Complex Queries

### Multi-Hop Traversal

Find nodes at exactly K hops from source:

```python
from collections import deque

def k_hop_neighbors(graph, source, k):
    """Find all nodes exactly K hops away"""
    if k == 0:
        return {source}
    
    current_level = {source}
    
    for hop in range(k):
        next_level = set()
        for node in current_level:
            for neighbor in graph.neighbors(node):
                next_level.add(neighbor)
        
        # Remove nodes from previous levels
        next_level -= current_level
        current_level = next_level
        
        if not current_level:
            break
    
    return current_level

# Usage
distance_3 = k_hop_neighbors(graph, source=42, k=3)
print(f"Nodes at exactly 3 hops: {len(distance_3)}")
```

### Subgraph Extraction

Extract subgraph induced by node set:

```python
from networkxternal.helpers.edge import Edge

def extract_subgraph(graph, node_ids):
    """Create new graph with only specified nodes and their edges"""
    from networkxternal.sqlite import SQLite
    
    node_set = set(node_ids)
    subgraph = SQLite(url="sqlite:///:memory:")
    
    # Add nodes
    for node_id in node_ids:
        node = graph.has_node(node_id)
        if node:
            subgraph.add(node)
    
    # Find edges where both endpoints are in subgraph
    count = 0
    for node_id in node_ids:
        for neighbor in graph.successors(node_id):
            if neighbor in node_set:
                edges = graph.has_edge(node_id, neighbor)
                if edges:
                    for edge in edges:
                        subgraph.add(edge)
                        count += 1
    
    print(f"Extracted subgraph: {len(node_ids)} nodes, {count} edges")
    return subgraph

# Usage
subgraph = extract_subgraph(graph, node_ids=[1, 2, 3, 4, 5])
```

### Edge Filtering by Attributes

Filter edges by payload attributes:

```python
def filter_edges_by_attribute(graph, attribute_key, attribute_value):
    """Stream edges and filter by payload attribute"""
    matching_edges = []
    
    for edge in graph.edges:
        if edge.payload.get(attribute_key) == attribute_value:
            matching_edges.append(edge)
    
    return matching_edges

# Usage
# Find all edges with type='friendship'
friendship_edges = filter_edges_by_attribute(graph, 'type', 'friendship')

# Find high-weight edges
high_weight_edges = [e for e in graph.edges if e.weight > 10.0]
```

### Aggregation Queries

Compute statistics over subsets:

```python
from networkxternal.helpers.graph_degree import GraphDegree

def node_statistics(graph, node_id):
    """Compute detailed statistics for a node"""
    # Incoming edges
    incoming = graph.reduce_edges(v=node_id)
    
    # Outgoing edges  
    outgoing = graph.reduce_edges(u=node_id)
    
    # All edges involving this node
    all_edges = graph.reduce_edges(node_id, node_id)
    
    # Neighbors
    neighbors = graph.neighbors(node_id)
    
    return {
        'node_id': node_id,
        'in_degree': incoming.count,
        'out_degree': outgoing.count,
        'total_degree': all_edges.count,
        'in_weight': incoming.weight,
        'out_weight': outgoing.weight,
        'neighbor_count': len(neighbors),
    }

# Usage
stats = node_statistics(graph, node_id=42)
print(f"Node 42: in_degree={stats['in_degree']}, out_degree={stats['out_degree']}")
```

## Transaction Management

### Explicit Transactions (SQL Backends)

Wrap operations in transactions:

```python
from contextlib import contextmanager

@contextmanager
def transaction(graph):
    """Context manager for database transactions"""
    session = graph.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

# Usage - all or nothing
try:
    with transaction(graph) as session:
        # All these operations commit together or rollback together
        graph.add(edge1)
        graph.add(edge2)
        graph.remove(node1)
        # If any fails, all are rolled back
except Exception as e:
    print(f"Transaction failed: {e}")
    # All changes reverted
```

### Batch with Checkpointing

For very large operations, checkpoint periodically:

```python
def bulk_import_with_checkpoints(graph, edges, checkpoint_interval=10000):
    """Import with periodic commits for crash recovery"""
    total = 0
    batch = []
    
    for i, edge in enumerate(edges):
        batch.append(edge)
        
        if len(batch) >= checkpoint_interval:
            with transaction(graph) as session:
                graph.add(batch)
            
            total += len(batch)
            print(f"Checkpoint: {total} edges imported")
            batch = []
    
    # Final batch
    if batch:
        with transaction(graph) as session:
            graph.add(batch)
        total += len(batch)
    
    print(f"Complete: {total} edges imported")
    return total
```

## Caching Strategies

### LRU Cache for Hot Data

Cache frequently accessed nodes/edges:

```python
from functools import lru_cache
from networkxternal.sqlite import SQLite

class CachedGraph:
    """Graph wrapper with automatic caching"""
    
    def __init__(self, graph, cache_size=10000):
        self.graph = graph
        self.cache_size = cache_size
    
    @lru_cache(maxsize=10000)
    def has_node_cached(self, node_id):
        """Cache node existence checks"""
        result = self.graph.has_node(node_id)
        return result._id if result else None
    
    @lru_cache(maxsize=10000)
    def neighbors_cached(self, node_id):
        """Cache neighbor lists (as tuple for hashability)"""
        return tuple(self.graph.neighbors(node_id))
    
    @lru_cache(maxsize=10000)
    def has_edge_cached(self, u, v):
        """Cache edge existence (returns count)"""
        result = self.graph.has_edge(u, v)
        return len(result) if result else 0
    
    def clear_cache(self):
        """Clear all caches"""
        self.has_node_cached.cache_clear()
        self.neighbors_cached.cache_clear()
        self.has_edge_cached.cache_clear()

# Usage
graph = SQLite(url="sqlite:///graph.db")
cached_graph = CachedGraph(graph, cache_size=50000)

# Subsequent calls use cache
neighbors1 = cached_graph.neighbors_cached(42)
neighbors2 = cached_graph.neighbors_cached(42)  # From cache!
```

### Time-Based Cache Expiration

For dynamic graphs, expire cache periodically:

```python
import time
from threading import Lock

class TimedCache:
    """Cache with TTL (time-to-live) expiration"""
    
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self.cache = {}
        self.lock = Lock()
    
    def get(self, key):
        """Get value if not expired"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
        return None
    
    def set(self, key, value):
        """Set value with current timestamp"""
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cached values"""
        with self.lock:
            self.cache.clear()

class DynamicGraph:
    """Graph wrapper with time-based caching"""
    
    def __init__(self, graph, cache_ttl=300):
        self.graph = graph
        self.neighbor_cache = TimedCache(ttl_seconds=cache_ttl)
    
    def neighbors(self, node_id):
        """Get neighbors with caching"""
        cached = self.neighbor_cache.get(node_id)
        if cached is not None:
            return cached
        
        # Cache miss - query database
        result = tuple(self.graph.neighbors(node_id))
        self.neighbor_cache.set(node_id, result)
        return result
    
    def invalidate_node_cache(self, node_id):
        """Invalidate cache for specific node (after modifications)"""
        self.neighbor_cache.cache.pop(node_id, None)

# Usage
graph = PostgreSQL(url="postgresql://...")
dynamic_graph = DynamicGraph(graph, cache_ttl=300)  # 5 minute cache

# Cached reads
neighbors = dynamic_graph.neighbors(42)

# After modifications, invalidate cache
graph.add_edge(42, 100)
dynamic_graph.invalidate_node_cache(42)  # Next read will refresh
```

## Error Handling

### Retry Logic for Transient Failures

Database operations can fail transiently:

```python
import time
from functools import wraps

def retry_on_failure(max_attempts=5, delay_seconds=1.0):
    """Decorator for retrying failed database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds * (2 ** attempt))  # Exponential backoff
            
            raise last_exception
        return wrapper
    return decorator

# Usage
class ResilientGraph:
    @retry_on_failure(max_attempts=5, delay_seconds=1.0)
    def add_edge_safe(self, u, v, **attrs):
        """Add edge with automatic retry on failure"""
        return self.add_edge(u, v, **attrs)
    
    @retry_on_failure(max_attempts=3, delay_seconds=0.5)
    def has_edge_safe(self, u, v):
        """Check edge with retry"""
        return self.has_edge(u, v)

# Or use manually
@retry_on_failure(max_attempts=5)
def bulk_import(graph, edges):
    for edge in edges:
        graph.add(edge)
```

### Connection Pool Exhaustion Handling

Handle "too many connections" errors:

```python
from sqlalchemy.exc import OperationalError
import queue

class ConnectionPoolManager:
    """Manage database connections with queue"""
    
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connection_queue = queue.Queue(maxsize=max_connections)
        self.graphs = []
    
    def get_graph(self):
        """Get graph from pool, wait if exhausted"""
        try:
            # Non-blocking get
            graph = self.connection_queue.get_nowait()
            return graph
        except queue.Empty:
            # Blocking get (wait for available connection)
            print("Waiting for available database connection...")
            graph = self.connection_queue.get()  # Blocks
            return graph
    
    def release_graph(self, graph):
        """Return graph to pool"""
        self.connection_queue.put(graph)
    
    @contextmanager
    def use_graph(self):
        """Context manager for safe connection usage"""
        graph = self.get_graph()
        try:
            yield graph
        finally:
            self.release_graph(graph)

# Usage
pool = ConnectionPoolManager(max_connections=10)

with pool.use_graph() as graph:
    # Use graph - automatically returned to pool when done
    result = graph.neighbors(42)
```

## Monitoring and Observability

### Operation Metrics

Track performance metrics:

```python
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List

@dataclass
class OperationMetric:
    operation: str
    duration_ms: float
    timestamp: float

class GraphMetrics:
    """Collect and report graph operation metrics"""
    
    def __init__(self):
        self.metrics: List[OperationMetric] = []
        self.operation_counts = defaultdict(int)
        self.operation_times = defaultdict(list)
    
    def record(self, operation: str, duration_ms: float):
        """Record an operation metric"""
        metric = OperationMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=time.time()
        )
        self.metrics.append(metric)
        self.operation_counts[operation] += 1
        self.operation_times[operation].append(duration_ms)
    
    def get_stats(self, operation: str = None):
        """Get statistics for operations"""
        if operation:
            times = self.operation_times[operation]
            count = self.operation_counts[operation]
        else:
            all_times = [t for times in self.operation_times.values() for t in times]
            count = sum(self.operation_counts.values())
        
        if not times:
            return None
        
        times.sort()
        return {
            'count': count,
            'min_ms': times[0],
            'max_ms': times[-1],
            'avg_ms': sum(times) / len(times),
            'p50_ms': times[len(times) // 2],
            'p95_ms': times[int(len(times) * 0.95)],
            'p99_ms': times[int(len(times) * 0.99)],
        }
    
    def report(self):
        """Print metrics report"""
        print("\n=== Graph Operation Metrics ===")
        for op in self.operation_counts:
            stats = self.get_stats(op)
            if stats:
                print(f"\n{op}:")
                print(f"  Count: {stats['count']}")
                print(f"  Avg: {stats['avg_ms']:.2f} ms")
                print(f"  P50: {stats['p50_ms']:.2f} ms")
                print(f"  P95: {stats['p95_ms']:.2f} ms")
                print(f"  P99: {stats['p99_ms']:.2f} ms")

# Usage with wrapper
class MonitoredGraph:
    def __init__(self, graph):
        self.graph = graph
        self.metrics = GraphMetrics()
    
    def _timed_operation(self, op_name, func, *args, **kwargs):
        """Wrap operation with timing"""
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.time() - start) * 1000
            self.metrics.record(op_name, duration_ms)
    
    def neighbors(self, node_id):
        return self._timed_operation(
            'neighbors', 
            self.graph.neighbors, 
            node_id
        )
    
    def has_edge(self, u, v):
        return self._timed_operation(
            'has_edge',
            self.graph.has_edge,
            u, v
        )
    
    def add_edge(self, u, v, **attrs):
        return self._timed_operation(
            'add_edge',
            self.graph.add_edge,
            u, v, **attrs
        )

# Usage
graph = PostgreSQL(url="postgresql://...")
monitored = MonitoredGraph(graph)

# Use monitored graph
monitored.neighbors(42)
monitored.has_edge(1, 2)

# Print report after operations
monitored.metrics.report()
```

## Memory Management

### Streaming Large Result Sets

Avoid loading all results into memory:

```python
def stream_nodes(graph, batch_size=1000):
    """Stream nodes in batches"""
    node_ids = graph.mentioned_nodes_ids  # Get all IDs first
    
    for i in range(0, len(node_ids), batch_size):
        batch = list(node_ids)[i:i+batch_size]
        
        for node_id in batch:
            node = graph.has_node(node_id)
            if node:
                yield node
        
        # Allow garbage collection
        del batch

# Usage
for node in stream_nodes(graph, batch_size=1000):
    process(node)  # Process one at a time
```

### Explicit Memory Cleanup

Force garbage collection during long operations:

```python
import gc

def process_with_cleanup(graph, processor, batch_size=10000):
    """Process edges with periodic GC"""
    count = 0
    
    for edge in graph.edges:
        processor(edge)
        count += 1
        
        if count % batch_size == 0:
            print(f"Processed {count} edges, running GC...")
            gc.collect()  # Force garbage collection
    
    print(f"Complete: {count} edges processed")
    return count
```

## Edge Cases

### Empty Graph Handling

Handle operations on empty graphs:

```python
def safe_operations_on_empty_graph(graph):
    """Operations that work correctly on empty graphs"""
    
    # These should all work without errors
    node_count = graph.number_of_nodes()  # Returns 0
    edge_count = graph.number_of_edges()  # Returns 0
    
    # Iterating over empty graph
    for node in graph.nodes:  # Never executes
        process(node)
    
    # Querying non-existent nodes
    node = graph.has_node(999)  # Returns None
    edges = graph.has_edge(1, 2)  # Returns None
    
    # Neighbors of non-existent node
    neighbors = graph.neighbors(999)  # Returns empty set
    
    # Statistics on empty graph
    stats = graph.reduce_nodes()  # Returns GraphDegree(0, 0)
```

### Self-Loops and Multi-Edges

Handle special edge cases:

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///:memory:", multigraph=True)

# Self-loop (edge from node to itself)
graph.add_edge(1, 1, weight=5.0)
self_loops = graph.has_edge(1, 1)  # Returns list with self-loop

# Multiple edges between same nodes (multigraph)
graph.add_edge(1, 2, weight=1.0, label="first")
graph.add_edge(1, 2, weight=2.0, label="second")
graph.add_edge(1, 2, weight=3.0, label="third")

all_edges = graph.has_edge(1, 2)  # Returns list of 3 edges
for edge in all_edges:
    print(f"Edge weight: {edge.weight}, label: {edge.payload.get('label')}")

# Neighbors deduplicates (returns unique node IDs)
neighbors = graph.neighbors(1)  # Returns {2} not {2, 2, 2}
```

### Disconnected Graphs

Handle graphs with multiple components:

```python
def find_connected_components(graph):
    """Find connected components using BFS"""
    visited = set()
    components = []
    
    for node in graph.nodes:
        if node._id not in visited:
            # Start new component
            component = set()
            queue = [node._id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                component.add(current)
                
                for neighbor in graph.neighbors(current):
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            components.append(component)
    
    return components

# Usage
components = find_connected_components(graph)
print(f"Found {len(components)} connected components")

largest_component = max(components, key=len)
print(f"Largest component has {len(largest_component)} nodes")
```

### Very Large Node IDs

Handle graphs with very large integer IDs:

```python
from networkxternal.sqlite import SQLite

graph = SQLite(url="sqlite:///:memory:")

# Works with very large IDs (uses BigInteger in SQL)
graph.add_node(2**63 - 1)  # Max 64-bit integer
graph.add_node(2**100)  # Arbitrarily large

# Edge ID generation uses Cantor pairing function
edge = Edge.identify_by_members(2**50, 2**50 + 1)
print(f"Generated edge ID: {edge}")
```

## Production Patterns

### Graph Versioning

Track graph versions for reproducibility:

```python
import hashlib
from datetime import datetime

class VersionedGraph:
    """Graph with version tracking"""
    
    def __init__(self, graph, version_table='graph_versions'):
        self.graph = graph
        self.version_table = version_table
        self._create_version_table()
    
    def _create_version_table(self):
        """Create table to track versions (SQL backends)"""
        if hasattr(self.graph, 'get_session'):
            with self.graph.get_session() as s:
                s.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.version_table} (
                        version_id TEXT PRIMARY KEY,
                        timestamp DATETIME,
                        node_count INTEGER,
                        edge_count INTEGER,
                        description TEXT
                    )
                """)
                s.commit()
    
    def record_version(self, description="Manual version"):
        """Record current graph state as version"""
        # Generate version ID from timestamp and hash
        timestamp = datetime.now().isoformat()
        node_count = self.graph.number_of_nodes()
        edge_count = self.graph.number_of_edges()
        
        version_id = f"v{timestamp}"
        
        if hasattr(self.graph, 'get_session'):
            with self.graph.get_session() as s:
                s.execute(f"""
                    INSERT INTO {self.version_table}
                    (version_id, timestamp, node_count, edge_count, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (version_id, timestamp, node_count, edge_count, description))
                s.commit()
        
        return version_id

# Usage
graph = PostgreSQL(url="postgresql://...")
versioned = VersionedGraph(graph)

# After bulk import
versioned.record_version("Initial import from dataset_v1.csv")

# After modifications
versioned.record_version("Added user connections for Q4 2024")
```

### Graph Backup and Restore

Create point-in-time backups:

```python
import json
from datetime import datetime

def backup_graph(graph, backup_path):
    """Export graph to JSON file"""
    print(f"Backing up {graph.number_of_nodes()} nodes...")
    nodes = [
        {
            '_id': node._id,
            'weight': node.weight,
            'label': node.label,
            'payload': node.payload
        }
        for node in graph.nodes
    ]
    
    print(f"Backing up {graph.number_of_edges()} edges...")
    edges = [
        {
            '_id': edge._id,
            'first': edge.first,
            'second': edge.second,
            'weight': edge.weight,
            'label': edge.label,
            'is_directed': edge.is_directed,
            'payload': edge.payload
        }
        for edge in graph.edges
    ]
    
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'node_count': len(nodes),
        'edge_count': len(edges),
        'nodes': nodes,
        'edges': edges
    }
    
    with open(backup_path, 'w') as f:
        json.dump(backup_data, f)
    
    print(f"Backup complete: {backup_path}")
    return backup_data

def restore_graph(graph, backup_path):
    """Restore graph from JSON backup"""
    with open(backup_path, 'r') as f:
        backup_data = json.load(f)
    
    print(f"Restoring {backup_data['node_count']} nodes...")
    for node_data in backup_data['nodes']:
        node = Node(**node_data)
        graph.add(node, upsert=True)
    
    print(f"Restoring {backup_data['edge_count']} edges...")
    for edge_data in backup_data['edges']:
        edge = Edge(**edge_data)
        graph.add(edge, upsert=True)
    
    print(f"Restore complete from {backup_data['timestamp']}")
    return backup_data
```
