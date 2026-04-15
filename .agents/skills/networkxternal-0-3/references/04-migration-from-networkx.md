# Migration from NetworkX to NetworkXternal

This guide covers step-by-step migration from NetworkX to NetworkXternal with minimal code changes.

## Compatibility Overview

NetworkXternal implements a subset of the NetworkX `MultiDiGraph` API:

| Feature | NetworkX | NetworkXternal | Migration Notes |
|---------|----------|----------------|-----------------|
| Directed graphs | ✅ | ✅ | Direct compatibility |
| Undirected graphs | ✅ | ✅ | Direct compatibility |
| Weighted edges | ✅ | ✅ | Use `weight` attribute |
| Multi-edges | ✅ | ✅ | Default behavior |
| Node attributes | ✅ | ✅ | Stored in `payload` dict |
| Edge attributes | ✅ | ✅ | Stored in `payload` dict |
| Integer node IDs | ✅ | ✅ | Direct compatibility |
| String node IDs | ✅ | ⚠️ | Auto-hashed to integers |
| Edge keys | ⚠️ Limited | ❌ | Use edge payloads instead |

## Basic Migration Pattern

### Step 1: Replace Import

```python
# Before (NetworkX)
import networkx as nx

# After (NetworkXternal)
from networkxternal.sqlite import SQLite
# or
from networkxternal.postgres import PostgreSQL
```

### Step 2: Replace Graph Creation

```python
# Before (NetworkX)
G = nx.MultiDiGraph()

# After (NetworkXternal)
G = SQLite(url="sqlite:///graph.db", directed=True, weighted=True)
```

### Step 3: Update Node/Edge Addition

Most NetworkX code works without changes:

```python
# Before (NetworkX)
G.add_node(1, weight=2.5, category="source")
G.add_edge(1, 2, weight=3.5, label="connects")

# After (NetworkXternal) - SAME CODE WORKS!
G.add_node(1, weight=2.5, category="source")
G.add_edge(1, 2, weight=3.5, label="connects")
```

### Step 4: Update Queries

Most queries work identically:

```python
# Before (NetworkX)
node_count = G.number_of_nodes()
edge_count = G.number_of_edges()
neighbors = list(G.neighbors(1))

# After (NetworkXternal) - SAME CODE WORKS!
node_count = G.number_of_nodes()
edge_count = G.number_of_edges()
neighbors = list(G.neighbors(1))
```

## API Differences and Workarounds

### String Node IDs

**NetworkX**: Supports arbitrary hashable node IDs

```python
# NetworkX
G.add_node("node_name")
G.add_edge("node_a", "node_b")
```

**NetworkXternal**: All nodes converted to integer hashes

```python
# NetworkXternal - same code, different behavior
G.add_node("node_name")  # Hashed to integer internally
G.add_edge("node_a", "node_b")  # Both hashed

# To get original string back:
node = G.has_node("node_name")
original_name = node.payload.get("_id")  # "node_name"
```

**Migration tip**: If you need string IDs, store them in payload:

```python
class StringIDGraph(NetworkXternal):
    def add_node(self, _id, **attrs):
        # Store original ID before hashing
        if not isinstance(_id, int):
            attrs["_original_id"] = _id
        super().add_node(_id, **attrs)
```

### Edge Data Access

**NetworkX**: Direct dictionary access

```python
# NetworkX
weight = G[1][2][0]['weight']
all_edge_data = G[1][2]  # Dict of key -> attributes
```

**NetworkXternal**: Use `has_edge()` and `get_edge_data()`

```python
# NetworkXternal
edges = G.has_edge(1, 2)  # Returns list of Edge objects
if edges:
    weight = edges[0].weight
    all_data = G.get_edge_data(1, 2)  # Dict like NetworkX
```

### has_edge() Return Value

**NetworkX**: Returns boolean

```python
# NetworkX
if G.has_edge(1, 2):
    print("Edge exists")
```

**NetworkXternal**: Returns list of edges or None

```python
# NetworkXternal
edges = G.has_edge(1, 2)
if edges is not None:
    print("Edge exists")
    for edge in edges:  # May be multiple in multigraph
        process(edge)
```

**Migration helper**: Create compatibility wrapper

```python
def nx_compatible_has_edge(G, u, v):
    """NetworkX-compatible has_edge that returns bool"""
    return G.has_edge(u, v) is not None
```

### Neighbor Iteration

**NetworkX**: Returns iterator

```python
# NetworkX
for neighbor in G.neighbors(1):
    process(neighbor)
```

**NetworkXternal**: Returns set of IDs

```python
# NetworkXternal - same code works!
for neighbor in G.neighbors(1):
    process(neighbor)
```

### Graph Algorithms

NetworkXternal does NOT include graph algorithms. For algorithms:

**Option 1**: Use NetworkX on subset

```python
import networkx as nx
from networkxternal.sqlite import SQLite

# Load small subgraph into NetworkX
G_persistent = SQLite(url="sqlite:///graph.db")
G_memory = nx.MultiDiGraph()

# Copy relevant portion
for node in G_persistent.nodes:
    G_memory.add_node(node._id, **node.payload)

for edge in G_persistent.edges:
    G_memory.add_edge(edge.first, edge.second, 
                     weight=edge.weight, **edge.payload)

# Run NetworkX algorithms
shortest_path = nx.shortest_path(G_memory, source=1, target=100)
```

**Option 2**: Implement algorithm with streaming

```python
def bfs_streaming(graph, start, max_depth=10):
    """BFS that doesn't load entire graph into memory"""
    from collections import deque
    
    visited = set()
    queue = deque([(start, 0)])
    visited.add(start)
    
    while queue:
        node, depth = queue.popleft()
        yield node, depth
        
        if depth < max_depth:
            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

# Use with NetworkXternal
for node, depth in bfs_streaming(G_persistent, start=1, max_depth=5):
    process(node, depth)
```

## Complete Migration Examples

### Example 1: Social Network Analysis

**Before (NetworkX)**:

```python
import networkx as nx

# Create graph
G = nx.MultiDiGraph()

# Load from CSV
import csv
with open('friends.csv') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    for row in reader:
        user_a, user_b = int(row[0]), int(row[1])
        G.add_edge(user_a, user_b)

# Analysis
print(f"Users: {G.number_of_nodes()}")
print(f"Friendships: {G.number_of_edges()}")

# Find popular users
degree_counts = [(n, d) for n, d in G.degree()]
degree_counts.sort(key=lambda x: x[1], reverse=True)
top_users = degree_counts[:10]

print("Top 10 most connected users:")
for user, degree in top_users:
    print(f"  User {user}: {degree} connections")
```

**After (NetworkXternal)**:

```python
from networkxternal.postgres import PostgreSQL
from networkxternal.helpers.parsing import import_graph

# Create persistent graph
G = PostgreSQL(url="postgresql://user:pass@localhost/social")

# Load from CSV (same format)
import_graph(G, 'friends.csv')

# Analysis (identical code!)
print(f"Users: {G.number_of_nodes()}")
print(f"Friendships: {G.number_of_edges()}")

# Find popular users (streaming to avoid memory issues)
degree_counts = []
for node in G.nodes:
    degree = len(G.neighbors(node._id))
    degree_counts.append((node._id, degree))

degree_counts.sort(key=lambda x: x[1], reverse=True)
top_users = degree_counts[:10]

print("Top 10 most connected users:")
for user, degree in top_users:
    print(f"  User {user}: {degree} connections")
```

### Example 2: Recommendation System

**Before (NetworkX)**:

```python
import networkx as nx

# Build user-item graph
G = nx.MultiDiGraph()

# Add user-item interactions
for user_id, item_id, rating in user_item_data:
    G.add_edge(user_id, item_id, weight=rating, type='rated')

# Find similar items (co-occurrence)
def find_similar_items(G, item_id, top_k=10):
    # Get users who rated this item
    users = list(G.predecessors(item_id))
    
    # Find other items these users rated
    item_scores = {}
    for user in users:
        for neighbor in G.successors(user):
            if neighbor != item_id:
                item_scores[neighbor] = item_scores.get(neighbor, 0) + 1
    
    # Return top K
    sorted_items = sorted(item_scores.items(), 
                         key=lambda x: x[1], reverse=True)
    return sorted_items[:top_k]

similar = find_similar_items(G, item_id=42)
```

**After (NetworkXternal)**:

```python
from networkxternal.postgres import PostgreSQL

# Build user-item graph (same code!)
G = PostgreSQL(url="postgresql://user:pass@localhost/recommendations")

for user_id, item_id, rating in user_item_data:
    G.add_edge(user_id, item_id, weight=rating, type='rated')

# Find similar items (adapted for streaming)
def find_similar_items(G, item_id, top_k=10):
    # Get users who rated this item
    users = list(G.predecessors(item_id))
    
    # Find other items these users rated
    item_scores = {}
    for user in users:
        for neighbor in G.successors(user):
            if neighbor != item_id:
                item_scores[neighbor] = item_scores.get(neighbor, 0) + 1
    
    # Return top K
    sorted_items = sorted(item_scores.items(), 
                         key=lambda x: x[1], reverse=True)
    return sorted_items[:top_k]

similar = find_similar_items(G, item_id=42)
```

### Example 3: Path Finding

**Before (NetworkX)**:

```python
import networkx as nx

G = nx.DiGraph()

# Add edges
for u, v, weight in edges:
    G.add_edge(u, v, weight=weight)

# Find shortest path
path = nx.shortest_path(G, source=1, target=100, weight='weight')
distance = nx.shortest_path_length(G, source=1, target=100, weight='weight')

print(f"Path: {path}")
print(f"Distance: {distance}")
```

**After (NetworkXternal with streaming Dijkstra)**:

```python
from networkxternal.postgres import PostgreSQL
import heapq

G = PostgreSQL(url="postgresql://user:pass@localhost/paths")

# Add edges (same code!)
for u, v, weight in edges:
    G.add_edge(u, v, weight=weight)

# Streaming Dijkstra (doesn't load full graph)
def dijkstra_streaming(G, source, target):
    """Dijkstra's algorithm that works with external storage"""
    distances = {source: 0}
    predecessors = {}
    queue = [(0, source)]
    
    while queue:
        dist, current = heapq.heappop(queue)
        
        if current == target:
            break
        
        if dist > distances.get(current, float('inf')):
            continue
        
        # Stream neighbors instead of loading all
        for neighbor_id in G.successors(current):
            # Get edge weight
            edges = G.has_edge(current, neighbor_id)
            if edges:
                weight = edges[0].weight
            else:
                weight = 1.0
            
            new_dist = dist + weight
            if new_dist < distances.get(neighbor_id, float('inf')):
                distances[neighbor_id] = new_dist
                predecessors[neighbor_id] = current
                heapq.heappush(queue, (new_dist, neighbor_id))
    
    # Reconstruct path
    if target not in predecessors and target != source:
        return None, float('inf')
    
    path = []
    current = target
    while current != source:
        path.append(current)
        current = predecessors[current]
    path.append(source)
    path.reverse()
    
    return path, distances[target]

path, distance = dijkstra_streaming(G, source=1, target=100)
print(f"Path: {path}")
print(f"Distance: {distance}")
```

## Performance Considerations During Migration

### 1. Expect Slower Operations

NetworkXternal is slower than in-memory NetworkX:

| Operation | NetworkX | NetworkXternal | Factor |
|-----------|----------|----------------|--------|
| Add edge | ~1 μs | ~100-500 μs | 100-500x |
| Find edge | ~1 μs | ~10-100 μs | 10-100x |
| Get neighbors | ~1 μs | ~100-1000 μs | 100-1000x |

**Migration strategy**: Profile first, optimize later

```python
# Add timing to understand impact
import time

start = time.time()
result = G.neighbors(42)
elapsed = time.time() - start

print(f"neighbors() took {elapsed*1000:.2f} ms")
```

### 2. Memory Usage Changes

**NetworkX**: All graph in RAM

```python
# NetworkX: 1M edges ≈ 100-500 MB RAM
G = nx.MultiDiGraph()
# ... load 1M edges
# RAM usage: high but constant
```

**NetworkXternal**: Graph on disk, minimal RAM

```python
# NetworkXternal: 1M edges ≈ 20-50 MB RAM
G = PostgreSQL(url="...")
# ... load 1M edges
# RAM usage: low, streaming operations
```

### 3. Batch Operations Are Critical

NetworkXternal benefits from batching:

```python
# ❌ Slow: Individual operations
for u, v, w in edges:
    G.add_edge(u, v, weight=w)

# ✅ Fast: Batch operation
edge_objects = [
    Edge(first=u, second=v, weight=w)
    for u, v, w in edges
]
G.add(edge_objects)
```

## Testing Your Migration

### Unit Test Compatibility

Create tests to verify behavior matches NetworkX:

```python
import unittest
from networkxternal.sqlite import SQLite

class TestNetworkXternalCompatibility(unittest.TestCase):
    def setUp(self):
        self.G = SQLite(url="sqlite:///:memory:")
    
    def test_add_node(self):
        self.G.add_node(1, weight=2.5)
        self.assertTrue(self.G.has_node(1) is not None)
    
    def test_add_edge(self):
        self.G.add_edge(1, 2, weight=3.5)
        self.assertTrue(self.G.has_edge(1, 2) is not None)
    
    def test_number_of_nodes(self):
        self.G.add_node(1)
        self.G.add_node(2)
        self.assertEqual(self.G.number_of_nodes(), 2)
    
    def test_neighbors(self):
        self.G.add_edge(1, 2)
        self.G.add_edge(1, 3)
        neighbors = set(self.G.neighbors(1))
        self.assertEqual(neighbors, {2, 3})
    
    def test_string_node_ids(self):
        self.G.add_node("name")
        node = self.G.has_node("name")
        self.assertIsNotNone(node)
        self.assertEqual(node.payload.get("_id"), "name")

if __name__ == '__main__':
    unittest.main()
```

### Performance Regression Tests

Compare performance before and after migration:

```python
import time
import networkx as nx
from networkxternal.sqlite import SQLite

def benchmark_networkx():
    G = nx.MultiDiGraph()
    
    start = time.time()
    for i in range(1000):
        G.add_edge(i, i+1, weight=float(i))
    add_time = time.time() - start
    
    start = time.time()
    for _ in range(100):
        _ = list(G.neighbors(500))
    query_time = time.time() - start
    
    return add_time, query_time

def benchmark_networkxternal():
    G = SQLite(url="sqlite:///:memory:")
    
    start = time.time()
    for i in range(1000):
        G.add_edge(i, i+1, weight=float(i))
    add_time = time.time() - start
    
    start = time.time()
    for _ in range(100):
        _ = list(G.neighbors(500))
    query_time = time.time() - start
    
    return add_time, query_time

nx_add, nx_query = benchmark_networkx()
ext_add, ext_query = benchmark_networkxternal()

print(f"NetworkX: add={nx_add:.3f}s, query={nx_query:.3f}s")
print(f"NetworkXternal: add={ext_add:.3f}s, query={ext_query:.3f}s")
print(f"Slowdown: add={ext_add/nx_add:.1f}x, query={ext_query/nx_query:.1f}x")
```

## Gradual Migration Strategy

### Phase 1: Dual Write

Write to both NetworkX and NetworkXternal:

```python
import networkx as nx
from networkxternal.postgres import PostgreSQL

G_memory = nx.MultiDiGraph()
G_persistent = PostgreSQL(url="postgresql://...")

def add_edge_dual(u, v, **attrs):
    G_memory.add_edge(u, v, **attrs)
    G_persistent.add_edge(u, v, **attrs)

# Use during transition period
for u, v, w in edges:
    add_edge_dual(u, v, weight=w)
```

### Phase 2: Read from Persistent

Gradually shift reads to persistent storage:

```python
def get_neighbors(node_id, use_persistent=True):
    if use_persistent:
        return G_persistent.neighbors(node_id)
    else:
        return G_memory.neighbors(node_id)

# Start with memory, gradually switch
use_persistent = False  # Phase 2a
# ...
use_persistent = True   # Phase 2b
```

### Phase 3: Full Migration

Remove NetworkX dependency:

```python
# Final code - only NetworkXternal
from networkxternal.postgres import PostgreSQL

G = PostgreSQL(url="postgresql://...")
# All operations use persistent storage
```

## Common Migration Issues

### Issue 1: String Node ID Hash Collisions

**Problem**: Different strings might hash to same integer

```python
G.add_node("node_a")
G.add_node("node_b")

# If hash("node_a") == hash("node_b"), collision!
```

**Solution**: Store original IDs and check for collisions

```python
def add_node_safe(G, node_id, **attrs):
    # Check if ID already exists
    if isinstance(node_id, str):
        existing = G.has_node(node_id)
        if existing and existing.payload.get("_id") != node_id:
            raise ValueError(f"Hash collision for '{node_id}'")
    G.add_node(node_id, **attrs)
```

### Issue 2: Missing Algorithms

**Problem**: NetworkX has 100+ algorithms, NetworkXternal has none

**Solution**: Use hybrid approach

```python
# For small subgraphs, use NetworkX
def analyze_subgraph(G_persistent, seed_node, max_nodes=1000):
    import networkx as nx
    
    # Extract subgraph
    G_memory = nx.MultiDiGraph()
    count = 0
    
    # BFS to collect nodes
    visited = set()
    queue = [seed_node]
    
    while queue and count < max_nodes:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        
        G_memory.add_node(node)
        count += 1
        
        for neighbor in G_persistent.neighbors(node):
            if neighbor not in visited:
                queue.append(neighbor)
    
    # Add edges
    for node in G_memory.nodes():
        for neighbor in G_persistent.successors(node):
            if neighbor in G_memory:
                edges = G_persistent.has_edge(node, neighbor)
                if edges:
                    G_memory.add_edge(node, neighbor, weight=edges[0].weight)
    
    # Run NetworkX algorithms
    return nx.page_rank(G_memory)
```

### Issue 3: Performance Regression

**Problem**: Application too slow after migration

**Solution**: Cache frequently accessed data

```python
from functools import lru_cache

class CachedGraph:
    def __init__(self, graph):
        self.graph = graph
    
    @lru_cache(maxsize=10000)
    def neighbors(self, node_id):
        """Cache neighbor lookups"""
        return tuple(self.graph.neighbors(node_id))
    
    @lru_cache(maxsize=10000)
    def has_edge(self, u, v):
        """Cache edge existence checks"""
        result = self.graph.has_edge(u, v)
        return tuple(result) if result else None

# Use wrapper for hot paths
G_cached = CachedGraph(G_persistent)
```

## Rollback Plan

If migration fails, have a rollback strategy:

```python
# Keep NetworkX working code in parallel
def run_analysis(use_networkxternal=False):
    if use_networkxternal:
        G = PostgreSQL(url="postgresql://...")
    else:
        import networkx as nx
        G = nx.MultiDiGraph()
    
    # Same analysis code for both
    result = analyze_graph(G)
    return result

# Gradual rollout
use_networkxternal = False  # Start with NetworkX
# Test thoroughly
# ...
use_networkxternal = True   # Switch when confident
```

## Summary

**Migration checklist:**

1. ✅ Replace imports (`nx` → `networkxternal`)
2. ✅ Replace graph creation (`nx.MultiDiGraph()` → `SQLite(...)`)
3. ✅ Test basic operations (add_node, add_edge, neighbors)
4. ✅ Handle string node IDs (auto-hashed to integers)
5. ✅ Adapt edge queries (`has_edge` returns list, not bool)
6. ✅ Implement streaming for large graphs
7. ✅ Add graph algorithms (hybrid approach or custom)
8. ✅ Profile performance and optimize batch sizes
9. ✅ Add caching for frequently accessed data
10. ✅ Test thoroughly before full deployment

**Key takeaways:**

- Most NetworkX code works without changes
- Expect 10-100x slower operations, plan accordingly
- Use streaming to avoid memory issues
- Batch operations for better performance
- Keep NetworkX for algorithms on small subgraphs
