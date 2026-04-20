# DAG Algorithms and Network Flow

NetworkX provides comprehensive algorithms for directed acyclic graphs (DAGs) and network flow optimization.

## DAG Algorithms

### Topological Sort

```python
import networkx as nx

DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])

# Basic topological sort
topo_order = list(nx.topological_sort(DG))
print(topo_order)  # e.g., [1, 2, 3, 4, 5]

# Lexicographic topological sort (stable, respects node ordering)
lex_topo = list(nx.lexicographical_topological_sort(DG, key=lambda n: -n))
print(lex_topo)  # Respects tie-breaking by node value

# Topological generations (layers)
generations = list(nx.topological_generations(DG))
print(generations)  # [[1], [2, 3], [4], [5]]
```

### DAG Properties and Analysis

```python
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (2, 3), (1, 3)])

# Check if directed acyclic
is_dag = nx.is_directed_acyclic_graph(DG)
print(is_dag)  # True

# Check if aperiodic
is_ap = nx.is_aperiodic(DG)
print(is_ap)  # True for DAGs

# Ancestors and descendants
ancestors_of_3 = nx.ancestors(DG, 3)
descendants_of_1 = nx.descendants(DG, 1)
print(ancestors_of_3)   # {1, 2}
print(descendants_of_1) # {2, 3}

# Colliders (nodes where two arrows meet: A -> C <- B)
colliders = list(nx.colliders(DG))

# V-structures (directed colliders with specified parents)
v_structures = list(nx.v_structures(DG))

# Antichains (sets of mutually unreachable nodes)
antichains = nx.antichains(DG)
print(list(antichains))  # e.g., [{1, 2}]

# Transitive closure
TC = nx.transitive_closure(DG)
# Every edge in TC represents a path in original DG

# Transitive reduction (remove redundant edges from TC)
TR = nx.transitive_reduction(DG)
# Minimal graph with same reachability as DG

# DAG to branching
branching = nx.dag_to_branching(DG)

# All topological sorts (not just one ordering)
all_sorts = list(nx.all_topological_sorts(DG))
print(f"Number of valid orderings: {len(all_sorts)}")
for sort in all_sorts[:5]:
    print(sort)

# Transitive closure DAG (optimized for DAGs only, faster than general TC)
TC_DAG = nx.transitive_closure_dag(DG)
# Returns a DiGraph where edge (u,v) exists iff v is reachable from u
```

### Longest Path in DAG

```python
DG = nx.DiGraph()
DG.add_edges_from([
    (1, 2, {"weight": 3}),
    (1, 3, {"weight": 2}),
    (2, 4, {"weight": 5}),
    (3, 4, {"weight": 10}),
])

# Longest path length
longest_len = nx.dag_longest_path_length(DG)
print(longest_len)  # Number of nodes in longest path

# Longest path with weights
longest_path = nx.dag_longest_path(DG, weight="weight")
print(longest_path)  # e.g., [1, 3, 4]
```

### DAG Visualization

```python
import matplotlib.pyplot as plt

DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])

# Topological sort for layout
topo_order = list(nx.topological_sort(DG))

# Create layered layout
layers = nx.topological_generations(DG)
pos = {}
for i, layer in enumerate(layers):
    for node in layer:
        pos[node] = (i, -list(layer).index(node))

nx.draw(DG, pos, with_labels=True, node_color="lightblue")
plt.show()
```

## Network Flow Algorithms

### Maximum Flow

```python
import networkx as nx

# Build a flow network
G = nx.DiGraph()
G.add_edges_from([
    ("s", "a", {"capacity": 15}),
    ("s", "b", {"capacity": 10}),
    ("a", "c", {"capacity": 10}),
    ("a", "d", {"capacity": 5}),
    ("b", "d", {"capacity": 10}),
    ("c", "t", {"capacity": 10}),
    ("d", "t", {"capacity": 20}),
])

# Edmonds-Karp algorithm (BFS-based, recommended)
flow_value, flow_dict = nx.maximum_flow(G, "s", "t", capacity="capacity")
print(f"Max flow: {flow_value}")

# Boykov-Kolmogorov (often faster for small graphs)
flow_value, flow_dict = nx.boykov_kolmogorov(G, "s", "t", capacity="capacity")

# Dinitz algorithm
flow_value, flow_dict = nx.dinitz(G, "s", "t", capacity="capacity")

# Build residual network
residual = nx.algorithms.flow.build_residual_network(G, capacity="capacity")
```

**Flow dict format:**
```python
print(flow_dict)
# {'s': {'a': 10, 'b': 5}, 'a': {'c': 10, 'd': 0}, ...}
```

### Min-Cut

```python
G = nx.DiGraph()
G.add_edges_from([
    ("s", "a", {"capacity": 3}),
    ("s", "b", {"capacity": 3}),
    ("a", "c", {"capacity": 1}),
    ("b", "c", {"capacity": 1}),
    ("a", "d", {"capacity": 2}),
    ("b", "d", {"capacity": 2}),
    ("c", "t", {"capacity": 4}),
    ("d", "t", {"capacity": 4}),
])

# Minimum cut value and partition
cut_value, partition = nx.minimum_cut(G, "s", "t", capacity="capacity")
source_set, target_set = partition
print(f"Min cut: {cut_value}, Partition: ({source_set}, {target_set})")

# Alternative: min-cut with residual network
flow_value, residual = nx.maximum_flow(G, "s", "t", capacity="capacity")
source_set, target_set = nx.minimum_cut_reachable_subgraph(residual, "s", "t", N=False)
```

### Min-Cost Flow

```python
G = nx.DiGraph()
G.add_edges_from([
    ("s", "a", {"capacity": 2, "weight": 1}),
    ("s", "b", {"capacity": 3, "weight": 2}),
    ("a", "t", {"capacity": 3, "weight": 3}),
    ("b", "t", {"capacity": 2, "weight": 1}),
])

# Supply/demand at nodes (positive = supply, negative = demand)
G.nodes["s"]["demand"] = -5
G.nodes["t"]["demand"] = 5

# Min-cost max-flow
flow_cost, flow_dict = nx.min_cost_flow(G)
print(f"Min cost: {flow_cost}")

# Min-cost flow with specific amount
flow_value = 3
cost, flow_dict = nx.min_cost_flow_cost(G)

# Capacity scaling algorithm (good for integer capacities)
flow_value, flow_dict, cost = nx.capacity_scaling(G)

# Maximum flow with minimum cost
flow_value, flow_dict = nx.max_flow_min_cost(G, "s", "t", capacity="capacity", weight="weight")
```

### Gomory-Hu Tree

```python
G = nx.Graph()
G.add_edges_from([
    (1, 2, {"capacity": 3}),
    (1, 3, {"capacity": 2}),
    (2, 4, {"capacity": 4}),
    (3, 4, {"capacity": 1}),
])

# Gomory-Hu tree: captures all-pairs min-cuts
GH = nx.gomory_hu_tree(G, capacity="capacity")
# GH is a tree where the minimum cut between any two nodes
# equals the minimum capacity edge on the path in GH
```

### Flow Decomposition

```python
G = nx.DiGraph()
G.add_edges_from([
    ("s", "a", {"flow": 2}),
    ("s", "b", {"flow": 1}),
    ("a", "t", {"flow": 2}),
    ("b", "t", {"flow": 1}),
])

# Decompose flow into path flows
for path, flow in nx.flow_cost(G, demand=-1):
    print(f"Path: {path}, Flow: {flow}")
```

### Flow on Graphs

```python
# Compute cost of a given flow
cost = nx.cost_of_flow(G, flow_dict)

# Balance check
balance = nx.balance(G, flow_dict)
# Returns dict of net flow into each node (should be 0 for internal nodes)
```

## Combined: Flow-Based Cuts and Connectivity

```python
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)])

# Edge connectivity via max-flow
edge_conn = nx.edge_connectivity(G)
local_edge_conn = nx.local_edge_connectivity(G, 1, 4)

# Node connectivity via max-flow
node_conn = nx.node_connectivity(G)
local_node_conn = nx.local_node_connectivity(G, 1, 4)

# Minimum edge cut
min_edge_cut = nx.minimum_edge_cut(G, 1, 4)
print(min_edge_cut)  # Set of edges whose removal disconnects nodes

# Minimum node cut
min_node_cut = nx.minimum_node_cut(G, 1, 4)
print(min_node_cut)  # Set of nodes whose removal disconnects nodes

# Edge-disjoint paths
edge_paths = nx.edge_disjoint_paths(G, "s", "t")
for path in edge_paths:
    print(path)

# Node-disjoint paths
node_paths = nx.node_disjoint_paths(G, "s", "t")
```

## Practical Flow Applications

### Bipartite Matching via Flow

```python
import networkx as nx

# Create bipartite graph
G = nx.Graph()
G.add_nodes_from(["u1", "u2", "u3"], bipartite=0)
G.add_nodes_from(["v1", "v2", "v3"], bipartite=1)
G.add_edges_from([
    ("u1", "v1"), ("u1", "v2"),
    ("u2", "v2"), ("u2", "v3"),
    ("u3", "v1"),
])

# Maximum matching via max flow
M = nx.bipartite.maximum_matching(G, top_nodes={"u1", "u2", "u3"})
print(M)
# e.g., {'u1': 'v2', 'u2': 'v3', 'u3': 'v1'}
# Note: M contains both directions, so len(M)/2 = matching size

# Maximum cardinality matching
matching = nx.max_weight_matching(G, maxcardinality=True)
print(matching)  # e.g., {('u1', 'v2'), ('u2', 'v3')}

# Minimum vertex cover (Konig's theorem for bipartite graphs)
vertex_cover = nx.bipartite.vertex_cover(G, top_nodes={"u1", "u2", "u3"})
print(vertex_cover)

# Maximum independent set
independent_set = nx.bipartite.independent_set(G, top_nodes={"u1", "u2", "u3"})
print(independent_set)
```

### Project Selection (Closure Problem)

```python
G = nx.DiGraph()
# Nodes with positive weight are profits, negative are costs
G.add_node("project_a", weight=50)
G.add_node("project_b", weight=-20)
G.add_node("tool_c", weight=-10)
# Dependencies: project_a requires tool_c
G.add_edge("project_a", "tool_c")
# project_b has no dependencies
G.add_edge("project_b", "tool_c")

# Maximum weight closure
closure = nx.algorithms.closure.maximum_weight_closure(G)
print(closure)  # Set of nodes to select for max profit
```

## Additional Flow Algorithms

### Network Simplex (for min-cost flow)

Fastest algorithm for min-cost flow on most networks.

```python
flow_cost, flow_dict = nx.network_simplex(G)
```

### Preflow-Push Algorithm

Alternative max-flow algorithm, often faster than Edmonds-Karp on dense graphs.

```python
flow_value, high_labels, flow_dict = nx.preflow_push(G, "s", "t", capacity="capacity")
```

### Shortest Augmenting Path

Generic shortest-augmenting-path based max flow.

```python
flow_value, flow_dict = nx.shortest_augmenting_path(G, "s", "t", capacity="capacity")
```

## Additional DAG Functions Reference

| Function | Description |
|----------|-------------|
| `topological_sort(DG)` | Linear ordering of DAG nodes |
| `all_topological_sorts(DG)` | All valid orderings |
| `lexicographical_topological_sort(DG, key=None)` | Stable sort with tie-breaking |
| `topological_generations(DG)` | Layer-by-layer generations |
| `is_directed_acyclic_graph(DG)` | Check for cycles |
| `is_aperiodic(DG)` | Check aperiodicity (DAGs always aperiodic) |
| `ancestors(DG, u)` | All nodes that can reach u |
| `descendants(DG, u)` | All nodes reachable from u |
| `antichains(DG)` | Sets of mutually unreachable nodes |
| `colliders(DG)` | Nodes with pattern A → C ← B |
| `v_structures(DG)` | Directed colliders (A→C←B where A,B not connected) |
| `transitive_closure(DG)` | Graph with all implied edges |
| `transitive_closure_dag(DG)` | Optimized TC for DAGs only |
| `transitive_reduction(DG)` | Minimal graph with same reachability |
| `dag_to_branching(DG)` | Convert to branching structure |
| `dag_longest_path(DG, weight=None)` | Longest path (by nodes) |
| `dag_longest_path_length(DG, weight=None)` | Length of longest path |

## Flow Algorithm Function Reference

| Function | Description | Notes |
|----------|-------------|-------|
| `maximum_flow(G, s, t, capacity="capacity")` | Max flow (Edmonds-Karp) | Default algorithm |
| `boykov_kolmogorov(G, s, t, capacity)` | Boykov-Kolmogorov | Often fastest |
| `dinitz(G, s, t, capacity)` | Dinitz algorithm | Good for dense graphs |
| `preflow_push(G, s, t, capacity)` | Preflow-push | Alternative to EK |
| `shortest_augmenting_path(G, s, t, capacity)` | Generic SAP | Slow but correct |
| `minimum_cut(G, s, t, capacity)` | Min cut value + partition | Returns (value, (S,T)) |
| `max_flow_min_cost(G, s, t, cap, weight)` | Min-cost max flow | With costs |
| `min_cost_flow(G)` | Min-cost flow | All demands satisfied |
| `min_cost_flow_cost(G)` | Min cost only | Returns (cost, flow_dict) |
| `capacity_scaling(G)` | Capacity scaling | Good for integer caps |
| `network_simplex(G)` | Network simplex | Fastest min-cost flow |
| `build_residual_network(G, capacity)` | Build residual graph | For manual manipulation |
| `cost_of_flow(G, flow_dict)` | Compute flow cost | Given flow dict |
| `flow_cost(G, demand)` | Flow decomposition | Path flows with costs |
| `gomory_hu_tree(G, capacity)` | All-pairs min-cuts | Tree representation |

## Summary

| Algorithm | Function | Complexity |
|-----------|----------|------------|
| Topological sort | `nx.topological_sort()` | O(V + E) |
| Lexicographic topological sort | `nx.lexicographical_topological_sort()` | O(V + E log V) |
| Longest path in DAG | `nx.dag_longest_path()` | O(V + E) |
| Transitive closure | `nx.transitive_closure()` | O(V × (V + E)) |
| Max flow (Edmonds-Karp) | `nx.maximum_flow()` | O(VE²) |
| Max flow (Boykov-Kolmogorov) | `nx.boykov_kolmogorov()` | Fast in practice |
| Max flow (Dinitz) | `nx.dinitz()` | O(V²E) |
| Min-cost flow | `nx.min_cost_flow()` | O(VE log V × f) |
| Gomory-Hu tree | `nx.gomory_hu_tree()` | (V-1) max-flow calls |
| Bipartite matching | `nx.bipartite.maximum_matching()` | Via max flow |
| Edge connectivity | `nx.edge_connectivity()` | Via max flow |
| Node connectivity | `nx.node_connectivity()` | Via max flow |
