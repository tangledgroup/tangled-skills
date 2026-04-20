# Shortest Path Algorithms

NetworkX provides comprehensive shortest path algorithms for both weighted and unweighted graphs, supporting directed and undirected networks.

## Problem Types

### Query Types

| Source | Target | Query Type |
|--------|--------|------------|
| None | None | All pairs shortest paths |
| Specified | None | From source to all reachable nodes |
| None | Specified | From all nodes that can reach target |
| Specified | Specified | Single source-target shortest path |

### Weight Handling

```python
# Unweighted (all edges weight = 1)
path = nx.shortest_path(G, "A", "B")

# Weighted using edge attribute
path = nx.shortest_path(G, "A", "B", weight="weight")

# Weighted using custom function
def weight_func(u, v, d):
    return d.get("cost", 1)
path = nx.shortest_path(G, "A", "B", weight=weight_func)
```

## Simplified Interface

NetworkX automatically selects the best algorithm based on your query:

```python
import networkx as nx

G = nx.Graph()
G.add_edge("A", "B", weight=4)
G.add_edge("B", "D", weight=2)
G.add_edge("A", "C", weight=3)
G.add_edge("C", "D", weight=4)

# Single-pair shortest path (auto-selects algorithm)
path = nx.shortest_path(G, "A", "D", weight="weight")
# Returns: ['A', 'B', 'D']

# All shortest paths between two nodes
all_paths = list(nx.all_shortest_paths(G, "A", "D", weight="weight"))

# Shortest path length
length = nx.shortest_path_length(G, "A", "D", weight="weight")
# Returns: 6

# Average shortest path length (for connected graphs)
avg_length = nx.average_shortest_path_length(G)

# Check if path exists
has_path = nx.has_path(G, "A", "D")
```

## Unweighted Algorithms

### Breadth-First Search (BFS)

Fastest for unweighted graphs. Finds shortest path in terms of number of edges.

```python
# Single-source BFS (paths from source to all nodes)
paths = nx.single_source_shortest_path(G, "source")
# Returns: {'source': ['source'], 'node1': ['source', 'node1'], ...}

# Single-source BFS (lengths only)
lengths = nx.single_source_shortest_path_length(G, "source")

# Single-target BFS (paths from all nodes to target)
paths = nx.single_target_shortest_path(G, "target")

# Bidirectional BFS (faster for single-pair)
path = nx.bidirectional_shortest_path(G, "source", "target")

# All pairs shortest paths
paths = dict(nx.all_pairs_shortest_path(G))

# Predecessor graph (for reconstructing paths)
pred = nx.predecessor(G, "source")
```

**Time complexity**: O(V + E) per source node

## Weighted Algorithms

### Dijkstra's Algorithm

Standard algorithm for non-negative edge weights.

```python
# Single-pair Dijkstra
path = nx.dijkstra_path(G, "source", "target", weight="weight")
length = nx.dijkstra_path_length(G, "source", "target", weight="weight")

# Single-source Dijkstra
paths = nx.single_source_dijkstra_path(G, "source", weight="weight")
lengths = nx.single_source_dijkstra_path_length(G, "source", weight="weight")

# Get both paths and lengths
lengths, paths = nx.single_source_dijkstra(G, "source", weight="weight")

# Multi-source Dijkstra (from multiple starting nodes)
lengths, paths = nx.multi_source_dijkstra(G, sources={"A", "B"}, weight="weight")

# All pairs Dijkstra
lengths, paths = nx.all_pairs_dijkstra(G, weight="weight")

# Bidirectional Dijkstra (faster for single-pair)
path = nx.bidirectional_dijkstra(G, "source", "target", weight="weight")

# Predecessor and distance
pred, dist = nx.dijkstra_predecessor_and_distance(G, "source", weight="weight")
```

**Time complexity**: O((V + E) log V) per source node

### Bellman-Ford Algorithm

Handles negative edge weights. Can detect negative cycles.

```python
# Single-pair Bellman-Ford
path = nx.bellman_ford_path(G, "source", "target", weight="weight")
length = nx.bellman_ford_path_length(G, "source", "target", weight="weight")

# Single-source Bellman-Ford
paths = nx.single_source_bellman_ford_path(G, "source", weight="weight")
lengths = nx.single_source_bellman_ford_path_length(G, "source", weight="weight")

# All pairs Bellman-Ford
paths = dict(nx.all_pairs_bellman_ford_path(G, weight="weight"))

# Predecessor and distance
pred, dist = nx.bellman_ford_predecessor_and_distance(G, "source", weight="weight")

# Detect negative cycles
has_negative_cycle = nx.negative_edge_cycle(G, weight="weight")

# Find a negative cycle
cycle = nx.find_negative_cycle(G, "source", weight="weight")
```

**Time complexity**: O(VE) per source node

### Johnson's Algorithm

Efficient for all-pairs shortest paths with negative weights.

```python
# All pairs shortest paths (handles negative weights)
lengths, paths = nx.johnson(G, weight="weight")
# Returns:
# lengths: {'A': {'A': 0, 'B': 5, ...}, ...}
# paths: {'A': {'A': ['A'], 'B': ['A', 'B'], ...}, ...}
```

**Time complexity**: O(V(V + E) log V)

## All-Pairs Algorithms

### Floyd-Warshall Algorithm

Best for dense graphs or when all-pairs distances are needed.

```python
# All pairs shortest path lengths
lengths = nx.floyd_warshall(G, weight="weight")

# All pairs shortest paths with predecessors
lengths, paths = nx.floyd_warshall_predecessor_and_distance(G, weight="weight")

# Reconstruct path from predecessor matrix
def reconstruct_path(pred, source, target):
    path = [target]
    current = target
    while current != source:
        current = pred[source][current]
        path.append(current)
    return path[::-1]

# All pairs shortest path lengths (unweighted)
lengths = nx.all_pairs_shortest_path_length(G)

# All pairs shortest paths (unweighted)
paths = dict(nx.all_pairs_shortest_path(G))
```

**Time complexity**: O(V³)

## Weighted vs Unweighted Comparison

```python
G = nx.Graph()
G.add_edge("A", "B", weight=10)
G.add_edge("B", "C", weight=10)
G.add_edge("A", "C", weight=25)

# Unweighted: A -> C is shortest (1 edge)
unweighted_path = nx.shortest_path(G, "A", "C")
# Returns: ['A', 'C']

# Weighted: A -> B -> C is shortest (weight 20 < 25)
weighted_path = nx.shortest_path(G, "A", "C", weight="weight")
# Returns: ['A', 'B', 'C']

# Path lengths differ
unweighted_length = nx.shortest_path_length(G, "A", "C")  # 1
weighted_length = nx.shortest_path_length(G, "A", "C", weight="weight")  # 20
```

## Directed Graphs

Shortest paths respect edge direction in directed graphs:

```python
DG = nx.DiGraph()
DG.add_edge("A", "B", weight=1)
DG.add_edge("B", "C", weight=1)
# No edge from C to B

# Path exists A -> C
path = nx.shortest_path(DG, "A", "C")  # ['A', 'B', 'C']

# No path from C to A (would need to reverse edges)
try:
    path = nx.shortest_path(DG, "C", "A")
except nx.NetworkXNoPath:
    print("No path exists")

# Reverse graph to find paths in opposite direction
DG_reverse = DG.reverse()
path = nx.shortest_path(DG_reverse, "C", "A")  # ['C', 'B', 'A']
```

## Common Patterns

### Find k Shortest Paths

```python
from networkx.algorithms.simple_paths import shortest_simple_paths

# Get k shortest simple paths (no repeated nodes)
paths = list(shortest_simple_paths(G, "source", "target", weight="weight"))
k_shortest = paths[:5]  # First 5 shortest paths
```

### Distance Matrix

```python
# Create distance matrix from all-pairs shortest paths
lengths = dict(nx.all_pairs_shortest_path_length(G))
nodes = list(G.nodes())
distance_matrix = [[lengths[n1][n2] for n2 in nodes] for n1 in nodes]
```

### Nearest Nodes

```python
# Find k nearest nodes to a source
lengths = nx.single_source_dijkstra_path_length(G, "source", weight="weight")
sorted_nodes = sorted(lengths.items(), key=lambda x: x[1])
k_nearest = sorted_nodes[:10]  # 10 nearest nodes with distances
```

### Eccentricity (Maximum Distance)

```python
# Maximum shortest path distance from each node
eccentricity = nx.eccentricity(G)

# Diameter (maximum eccentricity)
diameter = nx.diameter(G)

# Radius (minimum eccentricity)
radius = nx.radius(G)

# Center (nodes with minimum eccentricity)
center = nx.center(G)

# Periphery (nodes with maximum eccentricity)
periphery = nx.periphery(G)
print(f"Periphery nodes: {periphery}")

# Barycenter (node minimizing sum of distances to all others)
barycenter = nx.barycenter(G)
print(f"Barycenter: {barycenter}")
```

## Electrical Distance Measures

Measures based on modeling the graph as an electrical network.

```python
# Resistance distance (effective resistance between nodes)
# Models each edge as a 1-ohm resistor
res_dist = nx.resistance_distance(G)
print(res_dist[(1, 2)])  # Effective resistance between node 1 and 2

# Pairwise resistance distance
pair_res = nx.resistance_distance(G, 1, 2)
print(f"Resistance distance (1→2): {pair_res:.4f}")

# Effective graph resistance (Kirchhoff index)
eff_resistance = nx.effective_graph_resistance(G)
print(f"Effective graph resistance: {eff_resistance:.4f}")
# Sum of all pairwise resistance distances; relates to spanning tree count

# Harmonic diameter (based on harmonic mean of distances)
harmonic_diam = nx.harmonic_diameter(G)
print(f"Harmonic diameter: {harmonic_diam:.4f}")
# 1 / (1/n² × Σ 1/d(i,j)) — robust to disconnected components

# Kemeny constant (expected time for random walk to reach steady state)
kemeny = nx.kemeny_constant(G)
print(f"Kemeny constant: {kemeny:.4f}")
# Sum of reciprocals of non-zero Laplacian eigenvalues
# Lower = faster mixing, better connectivity
```

## A* Algorithm

Best when you have a heuristic function estimating distance to target. Faster than Dijkstra for large graphs.

```python
import math

def manhattan_heuristic(a, b):
    """Euclidean distance heuristic (admissible for geometric graphs)."""
    return math.sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

# Single-pair A* with heuristic
path = nx.astar_path(G, "source", "target", weight="weight", heuristic=manhattan_heuristic)
length = nx.astar_path_length(G, "source", "target", weight="weight", heuristic=manhattan_heuristic)
```

**Time complexity**: O((V + E) log V), often much faster with good heuristic

## Goldfarb-Radzik Algorithm

Alternative shortest path algorithm for weighted graphs. Handles negative weights (but not negative cycles).

```python
# Single-source shortest paths using Goldberg-Radzik
pred, dist = nx.goldberg_radzik(G, "source", weight="weight")
```

**Time complexity**: O(VE) worst case; faster in practice on many graphs

## Algorithm Selection Guide

| Scenario | Recommended Algorithm |
|----------|----------------------|
| Unweighted, single-pair | `bidirectional_shortest_path` |
| Unweighted, single-source | `single_source_shortest_path` (BFS) |
| Unweighted, single-target | `single_target_shortest_path` |
| Weighted (non-negative), single-pair | `bidirectional_dijkstra` or `astar_path` with heuristic |
| Weighted (non-negative), single-source | `single_source_dijkstra` |
| Weighted (non-negative), multi-source | `multi_source_dijkstra` |
| Weighted (negative edges), single-source | `single_source_bellman_ford` |
| All pairs, dense graph | `floyd_warshall` |
| All pairs, sparse graph | `all_pairs_dijkstra` |
| All pairs, negative weights | `johnson` or `all_pairs_bellman_ford_path` |
| Has heuristic to target | `astar_path` |
| Negative cycle detection | `negative_edge_cycle`, `find_negative_cycle` |
| Goldfarb-Radzik alternative | `goldberg_radzik` |

## Error Handling

```python
import networkx as nx

G = nx.Graph()
G.add_edge("A", "B")
G.add_edge("C", "D")  # Disconnected component

try:
    path = nx.shortest_path(G, "A", "C")
except nx.NetworkXNoPath:
    print("No path exists between nodes")

try:
    length = nx.shortest_path_length(G, "A", "A")
except nx.NetworkXError as e:
    print(f"Error: {e}")

# Check connectivity first
if nx.has_path(G, "A", "C"):
    path = nx.shortest_path(G, "A", "C")
else:
    print("Nodes are in different components")
```

## Performance Tips

1. **Use bidirectional search** for single-pair queries (2x faster typically)
2. **Cache all-pairs results** if querying multiple times
3. **Choose algorithm based on graph density**:
   - Dense graphs (E ≈ V²): Floyd-Warshall
   - Sparse graphs (E ≈ V): Dijkstra or Johnson
4. **Use unweighted algorithms** when weights don't matter (BFS is faster)
5. **For large graphs**, consider using backends (see [Backends and Performance](08-backends.md))
