# Centrality and Importance Measures

Centrality measures identify the most important nodes in a network. Different measures capture different notions of importance based on network structure.

## Degree-Based Centrality

### Degree Centrality

Measures the number of direct connections a node has. Simple but effective for identifying hubs.

```python
import networkx as nx

G = nx.karate_club_graph()

# Degree centrality (normalized by n-1)
dc = nx.degree_centrality(G)
# Returns: {'Node1': 0.35, 'Node2': 0.42, ...}

# For directed graphs
DG = nx.DiGraph()
DG.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 1)])

in_dc = nx.in_degree_centrality(DG)   # Incoming connections
out_dc = nx.out_degree_centrality(DG) # Outgoing connections

# Top k nodes by degree centrality
top_nodes = sorted(dc.items(), key=lambda x: x[1], reverse=True)[:10]
```

**Interpretation**: Higher values indicate more direct connections. Good for identifying hubs or popular nodes.

### Weighted Degree (Strength)

```python
# Sum of edge weights for each node
strength = dict(G.degree(weight="weight"))

# Normalized weighted degree
total_weight = sum(strength.values())
normalized_strength = {n: w / total_weight for n, w in strength.items()}
```

## Path-Based Centrality

### Betweenness Centrality

Measures how often a node lies on shortest paths between other nodes. Identifies brokers or bridges.

```python
# Node betweenness centrality
bc = nx.betweenness_centrality(G)

# Edge betweenness centrality
ebc = nx.edge_betweenness_centrality(G)

# Normalized (default True for graphs with > 2 nodes)
bc_normalized = nx.betweenness_centrality(G, normalized=True)

# Approximation for large graphs (k random samples per node)
bc_approx = nx.betweenness_centrality(G, k=10, weight=None)

# Betweenness for subset of nodes
source_nodes = [1, 2, 3]
target_nodes = [10, 11, 12]
bc_subset = nx.betweenness_centrality_subset(G, source_nodes, target_nodes)

# Top bridges (edges with highest betweenness)
top_edges = sorted(ebc.items(), key=lambda x: x[1], reverse=True)[:10]
```

**Time complexity**: O(VE) - expensive for large graphs. Use approximation for graphs with > 1000 nodes.

### Closeness Centrality

Measures how close a node is to all other nodes (average shortest path distance).

```python
# Standard closeness centrality
cc = nx.closeness_centrality(G)

# For disconnected graphs, use wf_improved=False to avoid zeroing
cc_all = nx.closeness_centrality(G, wf_improved=False)

# Closeness with edge weights
cc_weighted = nx.closeness_centrality(G, distance="weight")

# Incremental closeness (for dynamic graphs)
from networkx.algorithms.centrality import incremental_closeness_centrality
cc_inc = incremental_closeness_centrality(G)
```

**Interpretation**: Higher values indicate shorter average distances to all other nodes. Good for identifying efficient spreaders.

### Current Flow Betweenness

Random walk variant of betweenness centrality. Considers all paths, not just shortest paths.

```python
# Node current flow betweenness
cfbc = nx.current_flow_betweenness_centrality(G)

# Edge current flow betweenness
ecfbc = nx.edge_current_flow_betweenness_centrality(G)

# Approximation (faster for large graphs)
cfbc_approx = nx.approximate_current_flow_betweenness_centrality(G, niter=10)
```

## Eigenvector-Based Centrality

### Eigenvector Centrality

Nodes are important if they're connected to other important nodes. Used by Google's original PageRank.

```python
# Standard eigenvector centrality
ec = nx.eigenvector_centrality(G)

# With NumPy (faster for large graphs)
ec_numpy = nx.eigenvector_centrality_numpy(G)

# With edge weights
ec_weighted = nx.eigenvector_centrality(G, weight="weight")

# Maximum iterations and tolerance
ec = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)
```

**Convergence**: May not converge for disconnected graphs. Use `nx.eigenvector_centrality_numpy` for better stability.

### PageRank

Variant of eigenvector centrality with damping factor (random teleportation).

```python
# Standard PageRank (damping factor 0.85)
pr = nx.pagerank(G)

# Custom damping factor
pr_custom = nx.pagerank(G, alpha=0.9)

# With edge weights
pr_weighted = nx.pagerank(G, weight="weight")

# With personalized teleportation
personalization = {node: 1.0 for node in G.nodes()}
pr_personalized = nx.pagerank(G, personalization=personalization)

# Get both PageRank and iteration count
pr, num_iterations = nx.pagerank(G, return_iter=True)
```

**Parameters**:
- `alpha`: Damping factor (typically 0.85). Lower = more random jumps.
- `personalization`: Custom probability distribution for teleportation.

### Katz Centrality

Similar to eigenvector but counts all walks with attenuation by length.

```python
# Standard Katz centrality
kc = nx.katz_centrality(G)

# With attenuation factor (default 0.1)
kc_custom = nx.katz_centrality(G, alpha=0.2, beta=0.1)

# NumPy version (faster)
kc_numpy = nx.katz_centrality_numpy(G)

# With edge weights
kc_weighted = nx.katz_centrality(G, weight="weight")
```

**Parameters**:
- `alpha`: Attenuation factor (must be < 1/λ_max where λ_max is largest eigenvalue)
- `beta`: Weight for direct connections

## Information-Theoretic Centrality

### Harmonic Centrality

Like closeness but handles disconnected graphs better.

```python
hc = nx.harmonic_centrality(G)

# With edge weights
hc_weighted = nx.harmonic_centrality(G, distance="weight")
```

**Advantage**: Doesn't zero out nodes in disconnected components like closeness centrality.

### Information Centrality

Based on current flow closeness (random walks).

```python
ic = nx.information_centrality(G)

# For single node
ic_node = nx.information_centrality(G, nodes="node1")
```

## Load and Traffic Centrality

### Load Centrality

Measures how much "traffic" flows through a node (fraction of shortest paths).

```python
lc = nx.load_centrality(G)

# Edge load centrality
elc = nx.edge_load_centrality(G)

# With normalization
lc_normalized = nx.load_centrality(G, normalized=True)
```

## Subgraph-Based Centrality

### Subgraph Centrality

Counts closed walks of all lengths starting and ending at each node. Based on matrix exponential.

```python
sc = nx.subgraph_centrality(G)

# With edge weights
sc_weighted = nx.subgraph_centrality(G, attr="weight")

# Using explicit formula (more stable)
sc_exp = nx.subgraph_centrality_exp(G)

# Estrada index (sum of all subgraph centralities)
estrada = nx.estrada_index(G)
```

## Group Centrality

Measures importance of node groups rather than individual nodes.

```python
group = [1, 2, 3]  # Set of nodes

# Group degree centrality
gdc = nx.group_degree_centrality(G, group)

# Group betweenness centrality
gbc = nx.group_betweenness_centrality(G, group)

# Group closeness centrality
gcc = nx.group_closeness_centrality(G, group)

# For directed graphs
gin_dc = nx.group_in_degree_centrality(DG, group)
gout_dc = nx.group_out_degree_centrality(DG, group)

# Find most prominent group of size k
prominent = nx.prominent_group(G, k=5)
```

## Specialized Centrality Measures

### Dispersion

Measures how far a node's neighbors are from each other (structural holes).

```python
disp = nx.dispersion(G)

# With edge weights (distance-based)
disp_weighted = nx.dispersion(G, attr="weight")
```

### Local/Global Reaching Centrality

Based on reachability and network diameter.

```python
# Local reaching centrality
lrc = nx.local_reaching_centrality(G)

# Global reaching centrality
grc = nx.global_reaching_centrality(G)
```

### Percolation Centrality

Identifies nodes important for network percolation processes.

```python
# Requires node attributes 's' (source) and 't' (target)
for n in G.nodes():
    if n == "source_node":
        G.nodes[n]['s'] = 1.0
    elif n == "target_node":
        G.nodes[n]['t'] = 1.0
    else:
        G.nodes[n]['s'] = 0.0
        G.nodes[n]['t'] = 0.0

pc = nx.percolation_centrality(G)
```

### Trophic Levels

For directed networks (food webs, hierarchical systems).

```python
# Trophic levels (position in hierarchy)
levels = nx.trophic_levels(DG)

# Trophic differences (edges)
diffs = nx.trophic_differences(DG)

# Incoherence parameter (how well trophic levels fit)
incoherence = nx.trophic_incoherence_parameter(DG)
```

### VoteRank

Centrality based on voting mechanism with diminishing returns.

```python
vr = nx.voterank(G)

# For directed graphs
vr_directed = nx.voterank(DG)
```

### Laplacian Centrality

Based on graph Laplacian eigenvalues.

```python
lapc = nx.laplacian_centrality(G)
```

## Comparison and Selection

| Measure | Best For | Time Complexity |
|---------|----------|-----------------|
| Degree | Identifying hubs | O(V + E) |
| Betweenness | Finding bridges/brokers | O(VE) |
| Closeness | Efficient spreaders | O(V(V + E)) |
| Eigenvector | Influence propagation | O(k(V + E)) |
| PageRank | Web-like networks | O(kV) |
| Harmonic | Disconnected graphs | O(V(V + E)) |

## Practical Examples

### Identify Key Influencers

```python
G = nx.karate_club_graph()

# Combine multiple centrality measures
dc = nx.degree_centrality(G)
bc = nx.betweenness_centrality(G)
pr = nx.pagerank(G)

# Normalize and combine (equal weights)
combined = {n: 0.3*dc[n] + 0.3*bc[n] + 0.4*pr[n] for n in G.nodes()}

# Top 5 influencers
top_influencers = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:5]
print(top_influencers)
```

### Network Robustness Analysis

```python
# Attack by betweenness centrality (targeted attack)
bc = nx.betweenness_centrality(G)
sorted_nodes = sorted(bc.items(), key=lambda x: x[1], reverse=True)

# Remove nodes one by one and track largest component size
component_sizes = []
for i, (node, _) in enumerate(sorted_nodes):
    G.remove_node(node)
    if G.number_of_nodes() > 0:
        largest_component = max(c for c in nx.connected_components(G))
        component_sizes.append(len(largest_component))

# Compare with random removal
import random
G_random = nx.karate_club_graph()
random_nodes = list(G_random.nodes())
random.shuffle(random_nodes)

random_sizes = []
for node in random_nodes[:len(sorted_nodes)]:
    G_random.remove_node(node)
    if G_random.number_of_nodes() > 0:
        largest = max(c for c in nx.connected_components(G_random))
        random_sizes.append(len(largest))
```

### Cascade Simulation

```python
# Simple cascade model based on PageRank
pr = nx.pagerank(G)

# Initialize activation (seed nodes)
active = {"seed_node"}
threshold = 0.5

# Iterate until convergence
for iteration in range(100):
    newly_active = set()
    for node in G.nodes():
        if node not in active:
            # Activate if enough neighbors are active
            neighbor_pr = sum(pr[n] for n in G.neighbors(node) if n in active)
            total_neighbor_pr = sum(pr[n] for n in G.neighbors(node))
            if total_neighbor_pr > 0 and neighbor_pr / total_neighbor_pr > threshold:
                newly_active.add(node)
    
    if not newly_active:
        break
    active.update(newly_active)

print(f"Cascade reached {len(active)} nodes")
```

## Complete Centrality Function Reference

| Function | Module | Description |
|----------|--------|-------------|
| `degree_centrality(G)` | centrality | Normalized degree count |
| `in_degree_centrality(G)` | centrality | Incoming connections (directed) |
| `out_degree_centrality(G)` | centrality | Outgoing connections (directed) |
| `betweenness_centrality(G, k=None)` | centrality | Shortest-path betweenness |
| `betweenness_centrality_subset(G, s, t)` | centrality | Betweenness for node subsets |
| `edge_betweenness_centrality(G)` | centrality | Edge-level betweenness |
| `edge_betweenness_centrality_subset(G, s, t)` | centrality | Edge betweenness for subsets |
| `closeness_centrality(G, wf_improved=True)` | centrality | Inverse average distance |
| `eigenvector_centrality(G, max_iter=100)` | centrality | Neighbor-weighted importance |
| `eigenvector_centrality_numpy(G)` | centrality | NumPy-based (faster) |
| `pagerank(G, alpha=0.85)` | centrality | Damped random walk importance |
| `katz_centrality(G, alpha=0.1, beta=1.0)` | centrality | Walk-length attenuated importance |
| `katz_centrality_numpy(G)` | centrality | NumPy-based Katz |
| `current_flow_betweenness_centrality(G)` | centrality | Random walk betweenness |
| `current_flow_betweenness_centrality_subset(G, s, t)` | centrality | CF betweenness for subsets |
| `current_flow_closeness_centrality(G)` | centrality | Current flow closeness |
| `edge_current_flow_betweenness_centrality(G)` | centrality | Edge-level current flow betweenness |
| `edge_current_flow_betweenness_centrality_subset(G, s, t)` | centrality | Edge CF betweenness subsets |
| `approximate_current_flow_betweenness_centrality(G, niter=10)` | centrality | Approximated CF betweenness |
| `load_centrality(G)` | centrality | Fraction of shortest paths through node |
| `edge_load_centrality(G)` | centrality | Edge-level load |
| `harmonic_centrality(G, distance=None)` | centrality | Harmonic mean of distances |
| `subgraph_centrality(G, attr=None)` | centrality | Closed walk counts (matrix exp) |
| `subgraph_centrality_exp(G)` | centrality | Stable subgraph centrality |
| `estrada_index(G)` | centrality | Sum of all subgraph centralities |
| `information_centrality(G)` | centrality | Based on current flow closeness |
| `dispersion(G, attr=None)` | centrality | Neighbor dispersion (structural holes) |
| `local_reaching_centrality(G)` | centrality | Local reachability centrality |
| `global_reaching_centrality(G)` | centrality | Global reachability centrality |
| `percolation_centrality(G)` | centrality | Percolation process importance |
| `group_degree_centrality(G, group)` | centrality | Group-level degree importance |
| `group_betweenness_centrality(G, group)` | centrality | Group-level betweenness |
| `group_closeness_centrality(G, group)` | centrality | Group-level closeness |
| `group_in_degree_centrality(DG, group)` | centrality | Group in-degree (directed) |
| `group_out_degree_centrality(DG, group)` | centrality | Group out-degree (directed) |
| `prominent_group(G, k=5)` | centrality | Most prominent node group of size k |
| `incremental_closeness_centrality(G)` | centrality | Dynamic closeness for evolving graphs |
| `trophic_levels(DG)` | centrality | Hierarchical position (food webs) |
| `trophic_differences(DG)` | centrality | Edge-level trophic differences |
| `trophic_incoherence_parameter(DG)` | centrality | How well levels fit hierarchy |
| `voterank(G)` | centrality | Voting-based with diminishing returns |
| `laplacian_centrality(G)` | centrality | Laplacian eigenvalue-based |

## Performance Tips

1. **Use approximations for large graphs**: `k` parameter in betweenness centrality
2. **Cache results** when comparing multiple measures on same graph
3. **Parallelize** independent calculations (e.g., closeness for each node)
4. **Use NumPy versions** when available (`eigenvector_centrality_numpy`, `katz_centrality_numpy`)
5. **For very large graphs**, consider sampling or using backends
